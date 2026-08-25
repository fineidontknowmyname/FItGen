from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from schemas.user import UserMetrics, PhysicalActivity
from schemas.common import ActivityLevel, FitnessGoal, Gender


# ── Activity multipliers (PAL) ─────────────────────────────────────────────────
# Source: FAO/WHO/UNU Human Energy Requirements (2001), Table 5.2

PAL_MAP: dict[ActivityLevel, float] = {
    ActivityLevel.sedentary:          1.200,   # desk job, no exercise
    ActivityLevel.lightly_active:     1.375,   # light exercise 1–3 days/week
    ActivityLevel.moderately_active:  1.550,   # moderate exercise 3–5 days/week
    ActivityLevel.very_active:        1.725,   # hard exercise 6–7 days/week
    ActivityLevel.extra_active:       1.900,   # physical job + daily training
}

# ── Goal-based calorie deltas (kcal/day applied to TDEE) ──────────────────────

GOAL_DELTA: dict[FitnessGoal, float] = {
    FitnessGoal.weight_loss:       -500.0,
    FitnessGoal.muscle_gain:       +300.0,
    FitnessGoal.strength_gain:     +200.0,
    FitnessGoal.endurance_gain:      0.0,
    FitnessGoal.flexibility_gain:    0.0,
    FitnessGoal.general_fitness:     0.0,
}

# Safety floor — never recommend below this regardless of goal
_MIN_CALORIE_TARGET = 1200.0


# ── Result dataclass ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TDEEResult:
   
    bmr:                 float
    activity_multiplier: float
    tdee:                float
    calorie_target:      float
    goal_delta:          float
    notes:               Optional[str] = None

    # Convenience property
    @property
    def is_deficit(self) -> bool:
        return self.goal_delta < 0


# ── Engine ─────────────────────────────────────────────────────────────────────

class TDEEEngine:
    """
    Compute BMR → TDEE → goal-adjusted calorie target.
    """

    def compute(
        self,
        user_metrics: UserMetrics,
        physical_activity: PhysicalActivity,
        fitness_goal: FitnessGoal,
    ) -> TDEEResult:
        
        bmr = self._bmr(user_metrics)
        pal = self._pal(physical_activity, user_metrics)
        tdee = bmr * pal
        delta = GOAL_DELTA.get(fitness_goal, 0.0)
        target = max(_MIN_CALORIE_TARGET, tdee + delta)

        goal_str = fitness_goal.value.replace("_", " ")
        notes = (
            f"Goal: {goal_str}; calorie delta {delta:+.0f} kcal/day applied to TDEE. "
            f"Minimum floor of {_MIN_CALORIE_TARGET:.0f} kcal enforced."
        )

        return TDEEResult(
            bmr=round(bmr, 2),
            activity_multiplier=round(pal, 3),
            tdee=round(tdee, 2),
            calorie_target=round(target, 2),
            goal_delta=delta,
            notes=notes,
        )

    # ── Private helpers ────────────────────────────────────────────────────────

    def _bmr(self, m: UserMetrics) -> float:
        """
        Mifflin-St Jeor BMR.

        Male  : BMR = 10w + 6.25h − 5a + 5
        Female: BMR = 10w + 6.25h − 5a − 161

        where w = weight_kg, h = height_cm, a = age_years.
        """
        base = (10.0 * m.weight_kg) + (6.25 * m.height_cm) - (5.0 * m.age)
        return base + 5.0 if m.gender == Gender.male else base - 161.0

    def _pal(
        self,
        pa: PhysicalActivity,
        m: UserMetrics,
    ) -> float:
       
        base_pal = PAL_MAP.get(pa.activity_level, 1.375)

        # Extra exercise bonus: 0.025 per extra hour beyond 0.5 h/day, cap 0.10
        extra_hours = max(0.0, pa.physical_activity_hours_per_day - 0.5)
        bonus = min(0.10, extra_hours * 0.025)

        return min(1.90, base_pal + bonus)


# Module-level singleton
tdee_engine = TDEEEngine()
