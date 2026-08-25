from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from schemas.common import Gender


# ── WHO category enum ─────────────────────────────────────────────────────────

class BMICategory(str, Enum):
    severe_thinness    = "Severe thinness"
    moderate_thinness  = "Moderate thinness"
    mild_thinness      = "Mild thinness"
    normal             = "Normal weight"
    pre_obesity        = "Pre-obesity"
    obese_class_i      = "Obese class I"
    obese_class_ii     = "Obese class II"
    obese_class_iii    = "Obese class III"


# ── Plan signal enum ──────────────────────────────────────────────────────────

class PlanSignal(str, Enum):
  
    green   = "green"
    caution = "caution"
    warning = "warning"


# ── Category → PlanSignal map ─────────────────────────────────────────────────

_SIGNAL_MAP: dict[BMICategory, PlanSignal] = {
    BMICategory.severe_thinness:   PlanSignal.warning,
    BMICategory.moderate_thinness: PlanSignal.warning,
    BMICategory.mild_thinness:     PlanSignal.caution,
    BMICategory.normal:            PlanSignal.green,
    BMICategory.pre_obesity:       PlanSignal.caution,
    BMICategory.obese_class_i:     PlanSignal.caution,
    BMICategory.obese_class_ii:    PlanSignal.warning,
    BMICategory.obese_class_iii:   PlanSignal.warning,
}

# ── Advisory notes per signal ─────────────────────────────────────────────────

_SIGNAL_NOTES: dict[PlanSignal, str] = {
    PlanSignal.green: (
        "BMI is within the healthy range. No adjustments required."
    ),
    PlanSignal.caution: (
        "BMI is outside the optimal range. Starting loads have been kept "
        "conservative. Monitor progress and consult a healthcare professional "
        "if unsure."
    ),
    PlanSignal.warning: (
        "BMI indicates a significant health deviation. It is strongly recommended "
        "to seek medical clearance before beginning this training programme."
    ),
}


# ── WHo category thresholds ───────────────────────────────────────────────────
# Stored as (upper_exclusive_bound, BMICategory) sorted ascending.

_THRESHOLDS: list[tuple[float, BMICategory]] = [
    (16.00, BMICategory.severe_thinness),
    (17.00, BMICategory.moderate_thinness),
    (18.50, BMICategory.mild_thinness),
    (25.00, BMICategory.normal),
    (30.00, BMICategory.pre_obesity),
    (35.00, BMICategory.obese_class_i),
    (40.00, BMICategory.obese_class_ii),
    (float("inf"), BMICategory.obese_class_iii),
]


# ── Result dataclass ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class BMIResult:
   
    bmi:              float
    category:         BMICategory
    ideal_weight_kg:  float
    weight_delta_kg:  float      # current_weight − ideal (positive = above ideal)
    plan_signal:      PlanSignal
    advisory:         str


# ── Engine ─────────────────────────────────────────────────────────────────────

class BMIEngine:
   
    def compute(
        self,
        weight_kg: float,
        height_cm: float,
        gender: Gender,
    ) -> BMIResult:
        
        bmi = self._bmi(weight_kg, height_cm)
        category = self._category(bmi)
        ideal = self._ideal_weight(height_cm, gender)
        delta = round(weight_kg - ideal, 2)
        signal = _SIGNAL_MAP[category]
        advisory = _SIGNAL_NOTES[signal]

        return BMIResult(
            bmi=round(bmi, 2),
            category=category,
            ideal_weight_kg=round(ideal, 2),
            weight_delta_kg=delta,
            plan_signal=signal,
            advisory=advisory,
        )

    # ── Private helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _bmi(weight_kg: float, height_cm: float) -> float:
        """BMI = weight_kg / height_m²."""
        height_m = height_cm / 100.0
        if height_m <= 0:
            raise ValueError(f"height_cm must be positive, got {height_cm}")
        return weight_kg / (height_m ** 2)

    @staticmethod
    def _category(bmi: float) -> BMICategory:
        """Map a BMI value to the corresponding WHO category."""
        for upper_bound, cat in _THRESHOLDS:
            if bmi < upper_bound:
                return cat
        return BMICategory.obese_class_iii  # unreachable but satisfies type checker

    @staticmethod
    def _ideal_weight(height_cm: float, gender: Gender) -> float:
        
        base_height_cm = 152.4   # 5 feet in cm
        inches_over    = max(0.0, height_cm - base_height_cm) / 2.54

        if gender == Gender.male:
            ideal = 50.0 + 2.3 * inches_over
        else:
            ideal = 45.5 + 2.3 * inches_over

        return max(30.0, ideal)


# Module-level singleton
bmi_engine = BMIEngine()
