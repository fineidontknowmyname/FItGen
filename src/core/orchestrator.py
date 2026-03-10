from __future__ import annotations

import asyncio
import logging
from typing import List, Optional

from schemas.user import UserProfile, PhysicalActivity
from schemas.metrics import BodyMetrics
from schemas.plan import (
    FitnessPlan,
    GeneratePlanRequest,
    JobResponse,
    JobStatus,
    WeeklySchedule,
    WorkoutExercise,
    WorkoutSession,
    WorkoutSet,
)
from schemas.vision import BodyComposition
from schemas.common import ActivityLevel
from schemas.content import (
    ScheduledExercise,
    DailyWorkout,
    WeeklyPlan,
    PhaseGoal,
    TransformationRoadmap,
)

from integrations.ollama_client import ollama_client
from core.capacity import capacity_engine
from core.safety import safety_engine
from core.progression import progression_engine
from core.scheduler import scheduler
from services.intelligence.youtube import youtube_service

log = logging.getLogger(__name__)

# ── Video classification labels ───────────────────────────────────────────────
_WORKOUT_LABEL  = "workout"
_DIET_LABEL     = "diet"

# ── TDEE / macro constants ────────────────────────────────────────────────────
# Activity multipliers aligned with ActivityLevel enum
_PAL: dict[ActivityLevel, float] = {
    ActivityLevel.sedentary:          1.20,
    ActivityLevel.lightly_active:     1.375,
    ActivityLevel.moderately_active:  1.55,
    ActivityLevel.very_active:        1.725,
    ActivityLevel.extra_active:       1.90,
}

# Goal-based calorie adjustments (applied to TDEE)
_GOAL_DELTA: dict[str, float] = {
    "weight_loss":       -500.0,
    "muscle_gain":       +300.0,
    "strength_gain":     +200.0,
    "endurance_gain":      0.0,
    "flexibility_gain":    0.0,
    "general_fitness":     0.0,
}


# ── Orchestrator ──────────────────────────────────────────────────────────────

class PlanOrchestrator:

    # ── Public API ─────────────────────────────────────────────────────────────

    async def generate_plan(
        self,
        user_profile: UserProfile,
        youtube_urls: Optional[List[str]] = None,
        workout_youtube_urls: Optional[List[str]] = None,
        diet_youtube_urls: Optional[List[str]] = None,
        transcript_text: Optional[str] = None,
        body_composition: Optional[BodyComposition] = None,
    ) -> FitnessPlan:
        
        youtube_urls = youtube_urls or []
        workout_youtube_urls = workout_youtube_urls or []
        diet_youtube_urls = diet_youtube_urls or []
        mode = self._detect_mode(youtube_urls, transcript_text, body_composition)
        log.info("Plan generation starting  mode=%s  urls=%d", mode, len(youtube_urls))

        # ── Stages 0–3: Exercise pool (mode-dependent) ────────────────────────
        if mode == "A":
            # No YouTube content — use static exercise and meal libraries
            safe_exercises = self._default_exercise_pool(user_profile)
            diet_notes: Optional[str] = self._default_diet_notes(user_profile)
            log.info(
                "Mode A — using built-in exercise library (%d exercises after filter)",
                len(safe_exercises),
            )
        else:
            # MODE B or C — fetch and process YouTube transcripts
            # Stage 0: resolve transcripts
            url_transcript_map = await self._fetch_transcripts(youtube_urls)
            all_transcripts = list(url_transcript_map.values())
            if transcript_text:
                all_transcripts.append(transcript_text)

            workout_text = ""
            diet_transcripts = []

            # Stage 1: Fast-path context extraction if UI split them explicitly
            if workout_youtube_urls:
                workout_map = await self._fetch_transcripts(workout_youtube_urls)
                workout_text = " ".join(workout_map.values())
                
            if diet_youtube_urls:
                diet_map = await self._fetch_transcripts(diet_youtube_urls)
                diet_transcripts = list(diet_map.values())

            # Fallback for generic legacy URLs that weren't already categorised above
            if url_transcript_map:
                classifications = await self._classify_videos(url_transcript_map)
                log.info("Video classifications: %s", classifications)

                if not workout_text:
                    workout_text = self._collect_by_label(
                        url_transcript_map, classifications, _WORKOUT_LABEL,
                        fallback=transcript_text,
                    )
                if not diet_transcripts:
                    diet_transcripts = self._collect_by_label(
                        url_transcript_map, classifications, _DIET_LABEL,
                    )

            # Stage 2: extract exercises from transcripts
            if not workout_text:
                workout_text = " ".join(all_transcripts)

            exercise_lib = await ollama_client.extract_exercises(workout_text)
            log.info("Extracted %d exercises from transcripts", len(exercise_lib.exercises))

            # Stage 3: safety filter
            safe_exercises = safety_engine.filter_exercises(
                exercise_lib.exercises,
                user_profile.injuries,
                user_profile.equipment,
            )

            # Fallback to built-in library if LLM produced nothing usable
            if not safe_exercises:
                log.warning(
                    "LLM extraction yielded no safe exercises — "
                    "falling back to built-in library  mode=%s", mode
                )
                safe_exercises = self._default_exercise_pool(user_profile)

            # Stage 6-equivalent: diet notes from video
            diet_notes = None
            if diet_transcripts:
                diet_notes = await self._extract_diet_guidance(diet_transcripts)
                log.info("Diet notes extracted (%d chars)", len(diet_notes or ""))

        if not safe_exercises:
            raise ValueError(
                "No exercises available after filtering. "
                "Check the user's equipment list and injury flags."
            )

        # ── Stage 4: capacity score (all modes) ───────────────────────────────
        capacity_score = capacity_engine.calculate_score(
            user_metrics=user_profile.biometrics,
            strength_metrics=user_profile.metrics,
            physical_activity=user_profile.physical_activity,
            body_composition=body_composition,       # None in modes A & B
        )
        log.info("Capacity score: %.4f  mode=%s", capacity_score, mode)

        # ── Stage 5: BodyMetrics (TDEE / macros) — all modes ─────────────────
        body_metrics = self._compute_body_metrics(user_profile, capacity_score)

        # ── Stage 7: build base weekly template — all modes ───────────────────
        base_week = self._build_base_week(safe_exercises)

        # ── Stage 7b: build structured 7-day WeeklyPlan + TransformationRoadmap —
        roadmap = None
        try:
            structured_week = scheduler.build_weekly_plan(
                safe_exercises,
                user_profile.experience_level,
                capacity_score=capacity_score,
            )
            roadmap = self._build_roadmap(structured_week, user_profile)
        except Exception as exc:
            log.error(
                "Roadmap generation failed (plan will be returned without roadmap): %s",
                exc,
                exc_info=True,
            )

        # ── Stage 8: apply progression — all modes ────────────────────────────
        weeks = progression_engine.apply_progression(
            base_week, total_weeks=4, capacity_score=capacity_score
        )

        goal_label = user_profile.fitness_goal.value.replace("_", " ").title()
        return FitnessPlan(
            title=f"FitGen 4-Week Plan — {goal_label}  [{mode}]",
            weeks=weeks,
            body_metrics=body_metrics,
            diet_notes=diet_notes,
            body_composition=body_composition,   # echo back for the PDF renderer
            roadmap=roadmap,
        )

    async def generate_plan_async(self, request: GeneratePlanRequest) -> JobResponse:
       
        from workers.tasks import generate_plan_task  # deferred — Celery optional

        task = generate_plan_task.delay(request.model_dump())
        log.info("Dispatched plan generation task  job_id=%s", task.id)

        return JobResponse(
            job_id=task.id,
            status=JobStatus.pending,
            message=f"Plan generation queued. Poll /plans/job/{task.id} for status.",
        )

    # ── Stage helpers ──────────────────────────────────────────────────────────

    # ── Mode detection ─────────────────────────────────────────────────────────

    @staticmethod
    def _detect_mode(
        youtube_urls: List[str],
        transcript_text: Optional[str],
        body_composition: Optional[BodyComposition],
    ) -> str:
        
        has_content = bool(youtube_urls) or bool(transcript_text)
        if not has_content:
            return "A"
        if body_composition is not None:
            return "C"
        return "B"

    # ── Mode-A fallbacks ───────────────────────────────────────────────────────

    def _default_exercise_pool(self, user_profile: UserProfile) -> list:
       
        from core.default_exercises import get_default_exercises
        return get_default_exercises(
            goal=user_profile.fitness_goal,
            equipment=user_profile.equipment,
            experience_level=user_profile.experience_level,
            injuries=user_profile.injuries,
            top_n=25,
        )

    @staticmethod
    def _default_diet_notes(user_profile: UserProfile) -> str:
        
        _NOTES: dict[str, str] = {
            "weight_loss": (
                "• Aim for a 300–500 kcal daily deficit relative to your TDEE.\n"
                "• Prioritise protein (1.6–2.0 g/kg) to preserve muscle during a cut.\n"
                "• Fill half your plate with non-starchy vegetables at each main meal.\n"
                "• Limit liquid calories (sodas, juices, alcohol).\n"
                "• Eat slowly and stop at 80 % fullness to reduce overall intake naturally."
            ),
            "muscle_gain": (
                "• Eat in a 200–300 kcal surplus above your TDEE.\n"
                "• Target 1.8–2.2 g of protein per kg of bodyweight daily.\n"
                "• Time carbohydrates around workouts for performance and recovery.\n"
                "• Include calorie-dense whole foods: oats, rice, eggs, nuts, legumes.\n"
                "• Aim for 7–9 h of sleep — muscle is built during recovery, not training."
            ),
            "strength_gain": (
                "• Eat at or slightly above maintenance calories to fuel heavy lifting.\n"
                "• Protein target: 1.8–2.2 g/kg — critical for tendon and muscle repair.\n"
                "• Carbohydrates are your primary fuel for high-intensity strength work.\n"
                "• Hydration: drink at least 35 ml of water per kg of bodyweight daily.\n"
                "• Pre-workout meal: complex carbs + protein 1–2 h before training."
            ),
            "endurance_gain": (
                "• Carbohydrates are the primary fuel for sustained aerobic effort.\n"
                "• Aim for 5–7 g of carbs per kg on moderate training days.\n"
                "• Protein (1.4–1.6 g/kg) supports recovery and prevents muscle loss.\n"
                "• Electrolytes (sodium, potassium, magnesium) matter on long sessions.\n"
                "• Post-workout: a 3:1 carb-to-protein ratio aids glycogen restoration."
            ),
            "flexibility_gain": (
                "• Anti-inflammatory foods (fatty fish, berries, leafy greens) support joint health.\n"
                "• Stay consistently hydrated — dehydrated connective tissue is less pliable.\n"
                "• Collagen-supporting foods: vitamin C, bone broth, eggs.\n"
                "• Reduce processed foods and trans fats that promote systemic inflammation.\n"
                "• Magnesium-rich foods (spinach, almonds, dark chocolate) help muscle relaxation."
            ),
            "general_fitness": (
                "• Follow a balanced plate: ½ vegetables, ¼ lean protein, ¼ complex carbs.\n"
                "• Protein target: 1.4–1.8 g/kg to support recovery and body composition.\n"
                "• Drink water consistently — aim for 2–3 litres per day.\n"
                "• Minimise ultra-processed foods and added sugars.\n"
                "• Meal prep 2–3 days of food ahead to reduce reliance on convenience foods."
            ),
        }
        goal_key = user_profile.fitness_goal.value
        notes = _NOTES.get(goal_key, _NOTES["general_fitness"])
        return f"Standard {goal_key.replace('_', ' ').title()} Nutrition Guidelines\n\n{notes}"

    async def _fetch_transcripts(
        self, urls: List[str]
    ) -> dict[str, str]:
       
        return await youtube_service.fetch_many(urls, skip_failed=True)

    async def _classify_videos(
        self, url_transcript_map: dict[str, str]
    ) -> dict[str, str]:
       
        if not url_transcript_map:
            return {}

        async def _classify_one(url: str, text: str) -> tuple[str, str]:
            try:
                from services.intelligence.summarizer import summarizer_service
                category = await summarizer_service.classify_video(text)
                return url, category.value
            except Exception as exc:
                log.warning("Classification failed for %s: %s", url, exc)
                return url, "general"

        results = await asyncio.gather(
            *[_classify_one(u, t) for u, t in url_transcript_map.items()]
        )
        return dict(results)

    def _collect_by_label(
        self,
        url_transcript_map: dict[str, str],
        classifications: dict[str, str],
        label: str,
        fallback: Optional[str] = None,
    ) -> Optional[str]:
       
        parts = [
            url_transcript_map[url]
            for url, lbl in classifications.items()
            if lbl == label and url in url_transcript_map
        ]
        if parts:
            return " ".join(parts)
        return fallback

    def _compute_body_metrics(
        self, user_profile: UserProfile, capacity_score: float
    ) -> BodyMetrics:
       
        bio  = user_profile.biometrics
        goal = user_profile.fitness_goal.value

        # ── BMR (Mifflin-St Jeor) ──────────────────────────────────────────────
        if bio.gender.value == "male":
            bmr = (10.0 * bio.weight_kg) + (6.25 * bio.height_cm) - (5.0 * bio.age) + 5.0
        else:
            bmr = (10.0 * bio.weight_kg) + (6.25 * bio.height_cm) - (5.0 * bio.age) - 161.0

        # ── Activity multiplier ────────────────────────────────────────────────
        # physical_activity is Optional[PhysicalActivity]; fall back to defaults
        physical_activity = user_profile.physical_activity or PhysicalActivity()
        activity_multiplier = _PAL.get(
            physical_activity.activity_level,
            1.375,
        )
        tdee = bmr * activity_multiplier

        # ── Goal-based calorie target ──────────────────────────────────────────
        delta = _GOAL_DELTA.get(goal, 0.0)
        calorie_target = max(1200.0, tdee + delta)

        # ── Macros ─────────────────────────────────────────────────────────────
        # Protein: 1.6–2.2 g/kg based on goal; capacity score nudges the upper end
        protein_factor = 1.6 + (0.6 * (capacity_score - 0.5))   # 1.6 @ score=0.5 → 2.2 @ score=1.5
        protein_g = round(max(50.0, bio.weight_kg * protein_factor), 1)

        fat_g    = round(calorie_target * 0.25 / 9.0, 1)  # 25 % of calories from fat
        carbs_g  = round(
            (calorie_target - (protein_g * 4.0) - (fat_g * 9.0)) / 4.0, 1
        )
        carbs_g  = max(0.0, carbs_g)

        # ── Ideal weight (Devine formula) ──────────────────────────────────────
        height_over_152 = max(0.0, bio.height_cm - 152.4)
        if bio.gender.value == "male":
            ideal_weight_kg = 50.0 + 2.3 * (height_over_152 / 2.54)
        else:
            ideal_weight_kg = 45.5 + 2.3 * (height_over_152 / 2.54)

        # ── BMI ────────────────────────────────────────────────────────────────
        height_m = bio.height_cm / 100.0
        bmi = bio.weight_kg / (height_m ** 2)

        return BodyMetrics(
            bmi=round(bmi, 2),
            ideal_weight_kg=round(ideal_weight_kg, 2),
            bmr=round(bmr, 2),
            activity_multiplier=round(activity_multiplier, 3),
            tdee=round(tdee, 2),
            calorie_target=round(calorie_target, 2),
            protein_g=protein_g,
            carbs_g=carbs_g,
            fat_g=fat_g,
            notes=f"Goal: {goal.replace('_', ' ')}; calorie delta {delta:+.0f} kcal applied to TDEE.",
        )

    async def _extract_diet_guidance(self, diet_text: str) -> str:
        
        snippet = diet_text[:30000]
        prompt = (
            "You are a certified nutritionist reviewing a fitness video transcript.\n"
            "Extract the most specific, actionable diet recommendations from the text below.\n"
            "Format as a concise list of bullet-points (max 10 bullets).\n"
            "Do NOT include general advice — only content explicitly mentioned in the transcript.\n\n"
            f"Transcript:\n{snippet}"
        )
        try:
            return await ollama_client.generate_text(prompt)
        except Exception as exc:
            log.warning("Diet guidance extraction failed: %s", exc)
            return ""

    def _build_base_week(self, safe_exercises: list) -> WeeklySchedule:
        
        days = ["Monday", "Wednesday", "Friday"]
        chunk_size = max(1, len(safe_exercises) // 3)
        sessions: List[WorkoutSession] = []

        for i, day in enumerate(days):
            day_exercises = safe_exercises[i * chunk_size: (i + 1) * chunk_size]
            workout_exercises = [
                WorkoutExercise(
                    exercise=ex,
                    sets=[WorkoutSet(reps=10, weight_kg=10.0, rest_sec=60) for _ in range(3)],
                )
                for ex in day_exercises
            ]
            sessions.append(
                WorkoutSession(day_name=day, exercises=workout_exercises, duration_min=45)
            )

        return WeeklySchedule(week_number=1, sessions=sessions)

    # ── Transformation Roadmap ─────────────────────────────────────────────────

    @staticmethod
    def _build_roadmap(base_weekly_plan: WeeklyPlan, user_profile: UserProfile) -> TransformationRoadmap:
       
        from copy import deepcopy
        goal = user_profile.fitness_goal.value

        # ── Goal-aware expected outcomes ──────────────────────────────────────────
        _FAT_CHANGE = {
            "weight_loss":    "-1.5 to -2.5 kg body fat",
            "muscle_gain":    "+0.5% lean mass (fat neutral)",
            "strength_gain":  "Slight recomposition",
            "endurance_gain": "Minimal change (recomposition possible)",
            "general_fitness": "-0.5 to -1.0 kg",
            "flexibility_gain": "Minimal — focus is mobility",
        }
        _STRENGTH = {
            "weight_loss":    "+8-15% on all compound lifts",
            "muscle_gain":    "+15-25% on all compound lifts",
            "strength_gain":  "+20-30% on all compound lifts",
            "endurance_gain": "+5-10% on body-weight movements",
            "general_fitness": "+10-15% across all exercises",
            "flexibility_gain": "+5-8% on body-weight exercises",
        }

        fat = _FAT_CHANGE.get(goal, "Varies")
        strength = _STRENGTH.get(goal, "Varies")

        # ── Phase 1 — Foundation ─────────────────────────────────────────────────
        p1_plan = deepcopy(base_weekly_plan)
        p1_plan.repeat_for_weeks = 4

        phase1 = PhaseGoal(
            phase_name="Phase 1 — Foundation",
            duration_weeks=4,
            weeks_range="Weeks 1–4",
            primary_focus="Establish movement patterns, build base strength, form mastery",
            expected_fat_change=f"{fat} (across full 13 weeks)",
            expected_strength_gain="Technique improvements; +5% on key lifts by end of phase",
            expected_visible_changes="Improved posture, initial muscle fullness, reduced soreness",
            weekly_plan=p1_plan,
            cardio_protocol="1 LISS session/week, 30 min, target heart rate 120–140 bpm (Day 6)",
            progression_rule="Add 1 rep per exercise per session. When you hit the top of the rep range on ALL sets, add 2.5 kg.",
        )

        # ── Phase 2 — Development ────────────────────────────────────────────────
        p2_plan = deepcopy(base_weekly_plan)
        p2_plan.repeat_for_weeks = 4
        # Increase sets on compound exercises in training days
        for day in p2_plan.days:
            if not day.rest_day and day.exercises:
                for ex in day.exercises[:3]:   # first 3 = compound movements
                    ex.sets = min(ex.sets + 1, 5)

        phase2 = PhaseGoal(
            phase_name="Phase 2 — Development",
            duration_weeks=4,
            weeks_range="Weeks 5–8",
            primary_focus="Volume accumulation, hypertrophy emphasis, accessory work added",
            expected_fat_change="Progressive improvement continuing from Phase 1",
            expected_strength_gain=f"{strength} target across full 13 weeks",
            expected_visible_changes="Noticeable muscle definition, improved body composition",
            weekly_plan=p2_plan,
            cardio_protocol="1 LISS session/week, 35 min. Optional: add 15-min incline walk after lower days.",
            progression_rule="Add 1 set to compound lifts (bench, squat, row, deadlift). Keep rep ranges. Add 1 accessory movement per upper/lower day.",
        )

        # ── Phase 3 — Intensification ────────────────────────────────────────────
        p3_plan = deepcopy(base_weekly_plan)
        p3_plan.repeat_for_weeks = 4
        for day in p3_plan.days:
            if not day.rest_day and day.exercises:
                for ex in day.exercises:
                    ex.sets = min(ex.sets + 1, 5)

        phase3 = PhaseGoal(
            phase_name="Phase 3 — Intensification",
            duration_weeks=4,
            weeks_range="Weeks 9–12",
            primary_focus="Peak intensity — drop sets, mechanical tension, strength PR attempts",
            expected_fat_change="Rapid improvement — high intensity drives caloric burn",
            expected_strength_gain="PRs likely on all major compound lifts",
            expected_visible_changes="Significant muscle definition, vascularity in trained individuals",
            weekly_plan=p3_plan,
            cardio_protocol="2 LISS sessions/week — Day 3 (20 min) + Day 6 (40 min).",
            progression_rule="Final set of each exercise becomes a drop set: reduce weight 20%, perform AMRAP. Track and attempt new 1RM on last week of phase.",
        )

        # ── Phase 4 — Deload ─────────────────────────────────────────────────────
        p4_plan = deepcopy(base_weekly_plan)
        p4_plan.repeat_for_weeks = 1
        for day in p4_plan.days:
            if not day.rest_day:
                for ex in day.exercises:
                    ex.sets = max(1, ex.sets - 1)
                day.notes = "DELOAD — reduce all weights by 40%. Focus on form and joint health."

        phase4 = PhaseGoal(
            phase_name="Phase 4 — Deload",
            duration_weeks=1,
            weeks_range="Week 13",
            primary_focus="Active recovery, CNS reset, prepare for next training block",
            expected_fat_change="Maintenance — no significant change expected in 1 week",
            expected_strength_gain="Consolidation — strength is retained, fatigue dissipates",
            expected_visible_changes="Muscles appear fuller as glycogen restores",
            weekly_plan=p4_plan,
            cardio_protocol="1 easy 25-min walk. No high-intensity cardio.",
            progression_rule="Use 40% of your Phase 3 working weights. RPE should not exceed 5/10. Do not attempt PRs.",
        )

        # ── Final outcome string ──────────────────────────────────────────────────
        goal_label = goal.replace("_", " ").title()
        final_outcome = (
            f"After 13 weeks following the {goal_label} programme: "
            f"expected strength improvement of {strength.lower()}, "
            f"body composition change of {fat.lower()}, "
            "significantly improved movement quality and training capacity. "
            "Results depend on adherence, nutrition, and sleep quality."
        )

        return TransformationRoadmap(
            phases=[phase1, phase2, phase3, phase4],
            total_duration_weeks=13,
            final_expected_outcome=final_outcome,
        )


# Module-level singleton
plan_orchestrator = PlanOrchestrator()
