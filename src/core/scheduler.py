
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Sequence

from schemas.content import (
    Exercise,
    ScheduledExercise,
    DailyWorkout,
    WeeklyPlan,
)
from schemas.plan import WeeklySchedule, WorkoutSession, WorkoutExercise, WorkoutSet
from schemas.common import ExperienceLevel

class SplitType(str, Enum):
    full_body       = "full_body"
    upper_lower     = "upper_lower"
    push_pull_legs  = "push_pull_legs"
    custom          = "custom"



@dataclass
class DayTemplate:
    
    day_name:      str
    muscle_focus:  List[str] = field(default_factory=list)
    max_exercises: int = 6
    is_rest:       bool = False


_FULL_BODY_DAYS: list[DayTemplate] = [
    DayTemplate("Monday",    muscle_focus=[], max_exercises=7),
    DayTemplate("Tuesday (Rest)",   is_rest=True),
    DayTemplate("Wednesday", muscle_focus=[], max_exercises=7),
    DayTemplate("Thursday (Rest)",  is_rest=True),
    DayTemplate("Friday",    muscle_focus=[], max_exercises=7),
    DayTemplate("Saturday (Rest)",  is_rest=True),
    DayTemplate("Sunday (Rest)",    is_rest=True),
]

_UPPER_LOWER_DAYS: list[DayTemplate] = [
    DayTemplate("Monday (Upper)",    muscle_focus=["chest", "back", "shoulder", "bicep", "tricep"], max_exercises=6),
    DayTemplate("Tuesday (Lower)",   muscle_focus=["quad", "hamstring", "glute", "calf", "leg"],    max_exercises=6),
    DayTemplate("Wednesday (Rest)",  is_rest=True),
    DayTemplate("Thursday (Upper)",  muscle_focus=["chest", "back", "shoulder", "bicep", "tricep"], max_exercises=6),
    DayTemplate("Friday (Lower)",    muscle_focus=["quad", "hamstring", "glute", "calf", "leg"],    max_exercises=6),
    DayTemplate("Saturday (Rest)",   is_rest=True),
    DayTemplate("Sunday (Rest)",     is_rest=True),
]

_PUSH_PULL_LEGS_DAYS: list[DayTemplate] = [
    DayTemplate("Monday (Push A)",    muscle_focus=["chest", "shoulder", "tricep"],              max_exercises=6),
    DayTemplate("Tuesday (Pull A)",   muscle_focus=["back", "bicep", "rear delt"],               max_exercises=6),
    DayTemplate("Wednesday (Legs A)", muscle_focus=["quad", "hamstring", "glute", "calf"],       max_exercises=6),
    DayTemplate("Thursday (Push B)",  muscle_focus=["chest", "shoulder", "tricep"],              max_exercises=6),
    DayTemplate("Friday (Pull B)",    muscle_focus=["back", "bicep", "rear delt"],               max_exercises=6),
    DayTemplate("Saturday (Legs B)",  muscle_focus=["quad", "hamstring", "glute", "calf"],       max_exercises=6),
    DayTemplate("Sunday (Rest)",      is_rest=True),
]

_SPLIT_TEMPLATES: dict[SplitType, list[DayTemplate]] = {
    SplitType.full_body:      _FULL_BODY_DAYS,
    SplitType.upper_lower:    _UPPER_LOWER_DAYS,
    SplitType.push_pull_legs: _PUSH_PULL_LEGS_DAYS,
}



_SECONDS_PER_SET = 45      # avg work time
_REST_PER_SET    = 60      # avg rest between sets
_TIME_PER_SET    = (_SECONDS_PER_SET + _REST_PER_SET) / 60   # â†’ 1.75 min/set

_MAX_SESSION_MIN = 90      # hard ceiling regardless of exercise count


_SETS_BY_LEVEL: dict[ExperienceLevel, int] = {
    ExperienceLevel.beginner:     2,
    ExperienceLevel.intermediate: 3,
    ExperienceLevel.advanced:     4,
}

_DEFAULT_UPPER_STRENGTH = [
    ("Bench Press",          "Chest",     "Drive feet into floor and arch your upper back slightly."),
    ("Barbell Row",          "Back",      "Keep chest tall and pull the bar to your lower ribcage."),
    ("Overhead Press",       "Shoulders", "Brace your core and press the bar in a straight vertical line."),
    ("Pull-up / Lat Pulldown","Back",     "Retract scapula before pulling â€” avoid shrugging."),
    ("Tricep Dips",          "Triceps",   "Keep torso upright to emphasise triceps over chest."),
    ("Barbell Bicep Curl",   "Biceps",    "Pin elbows to sides and avoid swinging the torso."),
]

_DEFAULT_LOWER_STRENGTH = [
    ("Barbell Back Squat",    "Quadriceps", "Break at the hips first, keep knees tracking over toes."),
    ("Romanian Deadlift",     "Hamstrings", "Hinge at the hips, maintain a neutral spine throughout."),
    ("Leg Press",             "Quadriceps", "Place feet shoulder-width; don't lock knees at the top."),
    ("Bulgarian Split Squat", "Quadriceps", "Keep front shin vertical and torso upright."),
    ("Standing Calf Raise",   "Calves",     "Full range of motion â€” pause at the top and bottom."),
]

_DEFAULT_UPPER_HYPERTROPHY = [
    ("Incline Dumbbell Press","Chest",     "Control the eccentric â€” take 2-3 s to lower the dumbbells."),
    ("Cable Row",             "Back",      "Keep a slight forward lean and squeeze the shoulder blades."),
    ("Lateral Raise",         "Shoulders", "Lead with the elbows and pause at shoulder height."),
    ("Face Pull",             "Rear Delts","Pull to forehead height â€” externally rotate at the top."),
    ("Dumbbell Bicep Curl",   "Biceps",    "Supinate the wrist fully at the top of each rep."),
    ("Skull Crusher",         "Triceps",   "Keep upper arms perpendicular to floor; lower to forehead."),
]

_DEFAULT_LOWER_HYPERTROPHY = [
    ("Front Squat / Hack Squat","Quadriceps","Stay upright â€” let knees travel forward over toes."),
    ("Lying Leg Curl",          "Hamstrings","Flex ankles toward glutes; don't let hips rise off pad."),
    ("Walking Lunge",           "Quadriceps","Step long enough so front shin stays vertical."),
    ("Leg Extension",           "Quadriceps","Pause and squeeze at the top; don't use momentum."),
    ("Seated Calf Raise",       "Calves",    "Full range of motion â€” pause at the bottom for a stretch."),
]


class SchedulerEngine:

    def build_base_week(
        self,
        scored_exercises: Sequence,   # List[ScoredExercise] or List[Exercise]
        experience_level: ExperienceLevel,
        split: SplitType = SplitType.full_body,
        capacity_score: float = 1.0,
        custom_days: Optional[List[DayTemplate]] = None,
    ) -> WeeklySchedule:
        
        exercises = self._unwrap(scored_exercises)

        if split == SplitType.custom or custom_days is not None:
            templates = custom_days or []
        else:
            templates = _SPLIT_TEMPLATES.get(split, _FULL_BODY_DAYS)

        training_days = [t for t in templates if not t.is_rest]
        sets_per_ex   = self._sets_count(experience_level, capacity_score)

        # Route exercises to days
        day_exercise_map: dict[str, List[Exercise]] = {
            t.day_name: [] for t in training_days
        }
        unrouted: List[Exercise] = []

        for ex in exercises:
            routed = False
            for tmpl in training_days:
                if not tmpl.muscle_focus:
                    continue   # full-body days handled in round-robin below
                if self._matches_focus(ex, tmpl.muscle_focus):
                    bucket = day_exercise_map[tmpl.day_name]
                    if len(bucket) < tmpl.max_exercises:
                        bucket.append(ex)
                        routed = True
                        break
            if not routed:
                unrouted.append(ex)

        # Round-robin unrouted (or all, for full-body) exercises across days
        full_body_days = [t for t in training_days if not t.muscle_focus]
        target_days    = full_body_days or training_days   # fallback

        for idx, ex in enumerate(unrouted):
            tmpl  = target_days[idx % len(target_days)]
            bucket = day_exercise_map[tmpl.day_name]
            if len(bucket) < tmpl.max_exercises:
                bucket.append(ex)

        # Build WorkoutSession objects
        sessions: List[WorkoutSession] = []
        for tmpl in training_days:
            day_exercises = day_exercise_map.get(tmpl.day_name, [])
            if not day_exercises:
                continue   # skip empty training days

            workout_exercises = [
                WorkoutExercise(
                    exercise=ex,
                    sets=[
                        WorkoutSet(reps=10, weight_kg=0.0, rest_sec=60)
                        for _ in range(sets_per_ex)
                    ],
                )
                for ex in day_exercises
            ]

            duration = self._estimate_duration(len(day_exercises), sets_per_ex)

            sessions.append(WorkoutSession(
                day_name=tmpl.day_name,
                exercises=workout_exercises,
                duration_min=duration,
            ))

        if not sessions:
            raise ValueError(
                f"Scheduler produced zero sessions for split={split.value}. "
                "Ensure exercises are available after scoring and safety filtering."
            )

        return WeeklySchedule(week_number=1, sessions=sessions)

    # â”€â”€ Structured 7-day plan (new) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def build_weekly_plan(
        self,
        scored_exercises: Sequence,
        experience_level: ExperienceLevel,
        capacity_score: float = 1.0,
    ) -> WeeklyPlan:
        
        exercises = self._unwrap(scored_exercises)

        # Capacity nudge: advanced users get 4 sets on hypertrophy days
        hyp_sets = 4 if capacity_score >= 1.20 else 3

        upper_muscles = {"chest", "back", "shoulder", "bicep", "tricep", "lat", "deltoid"}
        lower_muscles = {"quad", "hamstring", "glute", "calf", "hip flexor", "adductor", "abductor"}

        upper_ex = self._filter_by_focus(exercises, upper_muscles)
        lower_ex = self._filter_by_focus(exercises, lower_muscles)

        # Day 1 â€” Upper Strength
        day1_exs = self._build_scheduled(
            library=upper_ex,
            defaults=_DEFAULT_UPPER_STRENGTH,
            count=6,
            sets=4,
            reps="4-6",
            rest=180,
            rationale="Selected for upper-body strength development in Phase 1.",
        )

        # Day 2 â€” Lower Strength
        day2_exs = self._build_scheduled(
            library=lower_ex,
            defaults=_DEFAULT_LOWER_STRENGTH,
            count=5,
            sets=4,
            reps="4-6",
            rest=180,
            rationale="Selected for lower-body strength development in Phase 1.",
        )

        # Day 4 â€” Upper Hypertrophy
        day4_exs = self._build_scheduled(
            library=upper_ex,
            defaults=_DEFAULT_UPPER_HYPERTROPHY,
            count=6,
            sets=hyp_sets,
            reps="8-12",
            rest=90,
            rationale="Hypertrophy focus â€” moderate load, higher volume.",
        )

        # Day 5 â€” Lower Hypertrophy
        day5_exs = self._build_scheduled(
            library=lower_ex,
            defaults=_DEFAULT_LOWER_HYPERTROPHY,
            count=5,
            sets=hyp_sets,
            reps="8-12",
            rest=90,
            rationale="Hypertrophy focus â€” moderate load, higher volume.",
        )

        days = [
            DailyWorkout(
                day_number=1,
                day_name="Day 1: Upper Body â€” Strength",
                focus="Chest, Back, Shoulders, Arms",
                exercises=day1_exs,
                notes="Heavy compound movements. Focus on progressive overload.",
            ),
            DailyWorkout(
                day_number=2,
                day_name="Day 2: Lower Body â€” Strength",
                focus="Quadriceps, Hamstrings, Glutes, Calves",
                exercises=day2_exs,
                notes="Heavy compound movements. Drive through the heels.",
            ),
            DailyWorkout(
                day_number=3,
                day_name="Day 3: Rest / Active Recovery",
                focus="Recovery",
                exercises=[],
                rest_day=True,
                notes="20-30 min light walking. Foam roll and stretch hips, hamstrings, lats.",
            ),
            DailyWorkout(
                day_number=4,
                day_name="Day 4: Upper Body â€” Hypertrophy",
                focus="Chest, Back, Shoulders, Arms",
                exercises=day4_exs,
                notes="Moderate weight, higher reps. Slow eccentric on each rep.",
            ),
            DailyWorkout(
                day_number=5,
                day_name="Day 5: Lower Body â€” Hypertrophy",
                focus="Quadriceps, Hamstrings, Glutes, Calves",
                exercises=day5_exs,
                notes="Moderate weight, higher reps. Full range of motion on every rep.",
            ),
            DailyWorkout(
                day_number=6,
                day_name="Day 6: Cardio",
                focus="Cardiovascular",
                exercises=[],
                rest_day=False,
                notes="30-40 min LISS cardio (brisk walk, cycling, or elliptical). "
                      "Target heart rate: 120-140 bpm. Do not exceed Zone 2.",
            ),
            DailyWorkout(
                day_number=7,
                day_name="Day 7: Full Rest",
                focus="Recovery",
                exercises=[],
                rest_day=True,
                notes="Complete rest. Prioritise 7-9 hours of sleep.",
            ),
        ]

        return WeeklyPlan(days=days, repeat_for_weeks=4)

    @staticmethod
    def _unwrap(scored_exercises: Sequence) -> List[Exercise]:
        result = []
        for item in scored_exercises:
            if hasattr(item, "exercise"):
                result.append(item.exercise)
            else:
                result.append(item)
        return result

    @staticmethod
    def _filter_by_focus(exercises: List[Exercise], focus: set) -> List[Exercise]:
        """Return exercises that target at least one muscle in focus set."""
        out = []
        for ex in exercises:
            muscles = {m.lower() for m in getattr(ex, "muscles_worked", [])}
            if muscles & focus:
                out.append(ex)
        return out

    @staticmethod
    def _build_scheduled(
        library: List[Exercise],
        defaults: list,
        count: int,
        sets: int,
        reps: str,
        rest: int,
        rationale: str,
    ) -> List[ScheduledExercise]:
        
        result: List[ScheduledExercise] = []
        used_names: set = set()

        # 1. Cherry-pick from scored library
        for ex in library:
            if len(result) >= count:
                break
            nm = ex.name.lower()
            if nm in used_names:
                continue
            muscle = ex.muscles_worked[0] if ex.muscles_worked else "General"
            cue    = ex.instructions[0] if ex.instructions else ""
            result.append(ScheduledExercise(
                name=ex.name,
                sets=sets,
                reps=reps,
                rest_seconds=rest,
                primary_muscle=muscle.title(),
                why_selected=rationale,
                form_cue=cue[:120] if cue else "",
            ))
            used_names.add(nm)

        # 2. Fill gaps with defaults
        for name, muscle, cue in defaults:
            if len(result) >= count:
                break
            if name.lower() in used_names:
                continue
            result.append(ScheduledExercise(
                name=name,
                sets=sets,
                reps=reps,
                rest_seconds=rest,
                primary_muscle=muscle,
                why_selected=rationale,
                form_cue=cue[:120],
            ))
            used_names.add(name.lower())

        return result

    @staticmethod
    def _sets_count(level: ExperienceLevel, capacity_score: float) -> int:
        """
        Base sets from experience level + a +1 bonus for high capacity.
        Capped at 5 to keep sessions manageable.
        """
        base = _SETS_BY_LEVEL.get(level, 3)
        bonus = 1 if capacity_score >= 1.30 else 0
        return min(5, base + bonus)

    @staticmethod
    def _matches_focus(ex: Exercise, focus_tags: List[str]) -> bool:
        muscles = [m.lower() for m in getattr(ex, "muscles_worked", [])]
        for tag in focus_tags:
            tag_lower = tag.lower()
            if any(tag_lower in m for m in muscles):
                return True
        return False

    @staticmethod
    def _estimate_duration(n_exercises: int, sets_per_ex: int) -> int:
        total_sets = n_exercises * sets_per_ex
        raw_min    = total_sets * _TIME_PER_SET + 10   # 10 min buffer
        return max(5, min(_MAX_SESSION_MIN, int(raw_min)))


# Module-level singleton
scheduler = SchedulerEngine()
