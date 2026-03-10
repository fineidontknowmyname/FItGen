from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Sequence


# ── Dietary restriction tags ───────────────────────────────────────────────────

class DietaryRestriction(str, Enum):
    vegan          = "vegan"
    vegetarian     = "vegetarian"
    gluten_free    = "gluten_free"
    dairy_free     = "dairy_free"
    nut_free       = "nut_free"
    low_sodium     = "low_sodium"
    low_carb       = "low_carb"
    halal          = "halal"
    kosher         = "kosher"


# ── Meal slot definition ───────────────────────────────────────────────────────

@dataclass(frozen=True)
class MealSlot:
    
    name:             str
    calorie_fraction: float
    is_snack:         bool = False


# ── Default daily slot schedule ───────────────────────────────────────────────

DEFAULT_SLOTS: list[MealSlot] = [
    MealSlot("Breakfast",       calorie_fraction=0.25),
    MealSlot("Morning Snack",   calorie_fraction=0.10, is_snack=True),
    MealSlot("Lunch",           calorie_fraction=0.30),
    MealSlot("Afternoon Snack", calorie_fraction=0.10, is_snack=True),
    MealSlot("Dinner",          calorie_fraction=0.25),
]


# ── Meal item ─────────────────────────────────────────────────────────────────

@dataclass
class MealItem:
   
    name:             str
    kcal:             float
    protein_g:        float = 0.0
    carbs_g:          float = 0.0
    fat_g:            float = 0.0
    restriction_tags: set[DietaryRestriction] = field(default_factory=set)

    def is_eligible(self, restrictions: Sequence[DietaryRestriction]) -> bool:
       
        if not restrictions:
            return True
        return all(r in self.restriction_tags for r in restrictions)


# ── Selected slot entry ────────────────────────────────────────────────────────

@dataclass
class SelectedMeal:
    slot:    MealSlot
    meal:    MealItem
    kcal:    float      # actual serving kcal (may be scaled)
    scaling: float      # portion scaling factor applied (1.0 = full serving)


# ── Daily plan output ─────────────────────────────────────────────────────────

@dataclass
class DailyPlan:
    """
    The full day's meal selections.

    Attributes
    ----------
    meals           Ordered list of (slot → meal) selections.
    total_kcal      Sum of kcal across all selected meals.
    target_kcal     The calorie target this plan was built for.
    is_within_tolerance
                    True iff |total - target| / target ≤ tolerance.
    unfilled_slots  Slot names for which no eligible meal was found.
    """
    meals:                List[SelectedMeal]
    total_kcal:           float
    target_kcal:          float
    is_within_tolerance:  bool
    unfilled_slots:       List[str] = field(default_factory=list)

    @property
    def calorie_delta(self) -> float:
        """Signed difference: total − target (negative = under target)."""
        return round(self.total_kcal - self.target_kcal, 2)


# ── Engine ─────────────────────────────────────────────────────────────────────

class MealSelectorEngine:
    

    def select(
        self,
        meal_pool: List[MealItem],
        restrictions: Sequence[DietaryRestriction],
        calorie_target: float,
        slots: Optional[List[MealSlot]] = None,
        tolerance: float = 0.05,
        shuffle_pool: bool = True,
        seed: Optional[int] = None,
    ) -> DailyPlan:
       
        if slots is None:
            slots = DEFAULT_SLOTS

        if not meal_pool:
            return DailyPlan(
                meals=[], total_kcal=0.0, target_kcal=calorie_target,
                is_within_tolerance=False,
                unfilled_slots=[s.name for s in slots],
            )

        rng = random.Random(seed)
        pool = list(meal_pool)
        if shuffle_pool:
            rng.shuffle(pool)

        # Eligible pool (restriction filter applied once, not per-slot)
        eligible_pool = [m for m in pool if m.is_eligible(restrictions)]

        # Sort slots by budget descending for greedy fill
        ordered_slots = sorted(slots, key=lambda s: s.calorie_fraction, reverse=True)

        selections: List[SelectedMeal] = []
        unfilled: List[str] = []
        used_names: set[str] = set()   # avoid exact duplicate meals on same day

        for slot in ordered_slots:
            budget = calorie_target * slot.calorie_fraction
            chosen = self._pick(eligible_pool, budget, tolerance, used_names)

            if chosen is None:
                unfilled.append(slot.name)
                continue

            # Scale portion to match budget
            scaling = budget / chosen.kcal if chosen.kcal > 0 else 1.0
            actual_kcal = chosen.kcal * scaling

            selections.append(SelectedMeal(
                slot=slot,
                meal=chosen,
                kcal=round(actual_kcal, 1),
                scaling=round(scaling, 3),
            ))
            used_names.add(chosen.name)

        # Re-sort selections back to natural slot order
        slot_order = {s.name: i for i, s in enumerate(slots)}
        selections.sort(key=lambda sm: slot_order.get(sm.slot.name, 999))

        total_kcal = round(sum(sm.kcal for sm in selections), 1)
        deviation = abs(total_kcal - calorie_target) / max(calorie_target, 1.0)

        return DailyPlan(
            meals=selections,
            total_kcal=total_kcal,
            target_kcal=round(calorie_target, 1),
            is_within_tolerance=deviation <= tolerance,
            unfilled_slots=unfilled,
        )

    # ── Selection helpers ──────────────────────────────────────────────────────

    def _pick(
        self,
        pool: List[MealItem],
        budget: float,
        tolerance: float,
        used_names: set[str],
    ) -> Optional[MealItem]:
        
        unused = [m for m in pool if m.name not in used_names]
        within_tol = [
            m for m in unused
            if abs(m.kcal - budget) / max(budget, 1.0) <= tolerance
        ]

        if within_tol:
            # Closest to budget among in-tolerance options
            return min(within_tol, key=lambda m: abs(m.kcal - budget))

        if unused:
            # Closest to budget among all unused (will be scaled)
            return min(unused, key=lambda m: abs(m.kcal - budget))

        if pool:
            # Last resort — allow repeats rather than leave slot empty
            return min(pool, key=lambda m: abs(m.kcal - budget))

        return None


# Module-level singleton
meal_selector = MealSelectorEngine()
