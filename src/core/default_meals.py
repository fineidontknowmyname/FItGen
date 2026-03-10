
from __future__ import annotations

from typing import List

from core.meal_selector import MealItem, DietaryRestriction


# ── Tags shorthand ─────────────────────────────────────────────────────────────

_V   = DietaryRestriction.vegetarian
_VG  = DietaryRestriction.vegan
_GF  = DietaryRestriction.gluten_free
_DF  = DietaryRestriction.dairy_free
_LC  = DietaryRestriction.low_carb
_LS  = DietaryRestriction.low_sodium
_H   = DietaryRestriction.halal
_NF  = DietaryRestriction.nut_free


# ── Master Meal Library ────────────────────────────────────────────────────────
# 35 meals × (name, kcal, protein_g, carbs_g, fat_g, restriction_tags)
# All macros are per-serving estimates.

_LIBRARY: List[MealItem] = [

    # ── BREAKFAST ──────────────────────────────────────────────────────────────

    MealItem(
        name="Oatmeal with Banana and Honey",
        kcal=380,
        protein_g=12.0,
        carbs_g=68.0,
        fat_g=6.0,
        restriction_tags={_V, _VG, _GF, _DF, _NF, _H},
    ),
    MealItem(
        name="Scrambled Eggs on Whole-Wheat Toast",
        kcal=420,
        protein_g=26.0,
        carbs_g=38.0,
        fat_g=16.0,
        restriction_tags={_V, _NF, _H},
    ),
    MealItem(
        name="Greek Yoghurt with Berries and Granola",
        kcal=360,
        protein_g=22.0,
        carbs_g=48.0,
        fat_g=7.0,
        restriction_tags={_V, _NF, _H},
    ),
    MealItem(
        name="Protein Smoothie (Whey, Milk, Banana, Oats)",
        kcal=480,
        protein_g=36.0,
        carbs_g=55.0,
        fat_g=9.0,
        restriction_tags={_V, _NF, _H},
    ),
    MealItem(
        name="Veggie Omelette (Eggs, Spinach, Peppers, Feta)",
        kcal=350,
        protein_g=28.0,
        carbs_g=10.0,
        fat_g=22.0,
        restriction_tags={_V, _GF, _NF, _H, _LC},
    ),
    MealItem(
        name="Avocado Toast with Poached Eggs",
        kcal=440,
        protein_g=20.0,
        carbs_g=36.0,
        fat_g=24.0,
        restriction_tags={_V, _DF, _NF, _H},
    ),
    MealItem(
        name="Overnight Oats with Chia Seeds and Almond Milk",
        kcal=340,
        protein_g=11.0,
        carbs_g=52.0,
        fat_g=9.0,
        restriction_tags={_V, _VG, _DF, _NF, _H},
    ),

    # ── MORNING SNACK ──────────────────────────────────────────────────────────

    MealItem(
        name="Apple with Peanut Butter",
        kcal=220,
        protein_g=6.0,
        carbs_g=28.0,
        fat_g=10.0,
        restriction_tags={_V, _VG, _GF, _DF, _H},
    ),
    MealItem(
        name="Hard-Boiled Eggs (×2)",
        kcal=160,
        protein_g=13.0,
        carbs_g=1.0,
        fat_g=11.0,
        restriction_tags={_V, _GF, _DF, _LC, _NF, _H},
    ),
    MealItem(
        name="Rice Cake with Cottage Cheese",
        kcal=180,
        protein_g=14.0,
        carbs_g=22.0,
        fat_g=3.0,
        restriction_tags={_V, _GF, _NF, _H},
    ),
    MealItem(
        name="Mixed Nuts and Dried Fruit",
        kcal=240,
        protein_g=6.0,
        carbs_g=26.0,
        fat_g=14.0,
        restriction_tags={_V, _VG, _GF, _DF, _H},
    ),
    MealItem(
        name="Banana and Protein Bar",
        kcal=280,
        protein_g=20.0,
        carbs_g=38.0,
        fat_g=8.0,
        restriction_tags={_V, _H, _NF},
    ),

    # ── LUNCH ──────────────────────────────────────────────────────────────────

    MealItem(
        name="Grilled Chicken Breast with Brown Rice and Broccoli",
        kcal=520,
        protein_g=46.0,
        carbs_g=52.0,
        fat_g=10.0,
        restriction_tags={_GF, _DF, _NF, _H, _LC},
    ),
    MealItem(
        name="Tuna and Sweetcorn Whole-Wheat Wrap",
        kcal=490,
        protein_g=38.0,
        carbs_g=48.0,
        fat_g=12.0,
        restriction_tags={_DF, _NF, _H},
    ),
    MealItem(
        name="Beef and Vegetable Stir-Fry with Rice Noodles",
        kcal=560,
        protein_g=36.0,
        carbs_g=60.0,
        fat_g=14.0,
        restriction_tags={_DF, _NF, _H},
    ),
    MealItem(
        name="Lentil Soup with Whole-Grain Bread",
        kcal=420,
        protein_g=22.0,
        carbs_g=64.0,
        fat_g=6.0,
        restriction_tags={_V, _VG, _DF, _NF, _H},
    ),
    MealItem(
        name="Quinoa Salad with Chickpeas, Cucumber and Feta",
        kcal=460,
        protein_g=20.0,
        carbs_g=58.0,
        fat_g=14.0,
        restriction_tags={_V, _GF, _NF, _H},
    ),
    MealItem(
        name="Salmon Fillet with Sweet Potato and Asparagus",
        kcal=540,
        protein_g=44.0,
        carbs_g=42.0,
        fat_g=18.0,
        restriction_tags={_GF, _DF, _NF, _H},
    ),
    MealItem(
        name="Turkey and Avocado Salad Bowl (no dressing)",
        kcal=430,
        protein_g=40.0,
        carbs_g=18.0,
        fat_g=22.0,
        restriction_tags={_GF, _DF, _NF, _H, _LC},
    ),
    MealItem(
        name="Black Bean and Vegetable Burrito Bowl",
        kcal=500,
        protein_g=22.0,
        carbs_g=72.0,
        fat_g=10.0,
        restriction_tags={_V, _VG, _GF, _DF, _NF, _H},
    ),

    # ── AFTERNOON SNACK ────────────────────────────────────────────────────────

    MealItem(
        name="Cottage Cheese with Pineapple",
        kcal=190,
        protein_g=18.0,
        carbs_g=22.0,
        fat_g=3.0,
        restriction_tags={_V, _GF, _NF, _H},
    ),
    MealItem(
        name="Celery Sticks with Hummus",
        kcal=150,
        protein_g=5.0,
        carbs_g=16.0,
        fat_g=7.0,
        restriction_tags={_V, _VG, _GF, _DF, _NF, _H},
    ),
    MealItem(
        name="Protein Shake with Milk",
        kcal=220,
        protein_g=28.0,
        carbs_g=18.0,
        fat_g=4.0,
        restriction_tags={_V, _GF, _NF, _H},
    ),
    MealItem(
        name="Edamame (Steamed, Lightly Salted)",
        kcal=170,
        protein_g=14.0,
        carbs_g=14.0,
        fat_g=6.0,
        restriction_tags={_V, _VG, _GF, _DF, _NF, _H},
    ),
    MealItem(
        name="Dark Chocolate and Almonds",
        kcal=230,
        protein_g=5.0,
        carbs_g=20.0,
        fat_g=16.0,
        restriction_tags={_V, _VG, _GF, _DF, _H},
    ),

    # ── DINNER ─────────────────────────────────────────────────────────────────

    MealItem(
        name="Grilled Salmon with Roasted Vegetables and Quinoa",
        kcal=590,
        protein_g=46.0,
        carbs_g=48.0,
        fat_g=20.0,
        restriction_tags={_GF, _DF, _NF, _H},
    ),
    MealItem(
        name="Chicken Stir-Fry with Mixed Vegetables and Brown Rice",
        kcal=550,
        protein_g=44.0,
        carbs_g=56.0,
        fat_g=12.0,
        restriction_tags={_GF, _DF, _NF, _H},
    ),
    MealItem(
        name="Beef and Lentil Stew (Hearty Low-Sodium)",
        kcal=520,
        protein_g=40.0,
        carbs_g=50.0,
        fat_g=12.0,
        restriction_tags={_GF, _DF, _NF, _H, _LS},
    ),
    MealItem(
        name="Baked Cod with Garlic Green Beans and Sweet Potato",
        kcal=440,
        protein_g=38.0,
        carbs_g=44.0,
        fat_g=8.0,
        restriction_tags={_GF, _DF, _NF, _H, _LS},
    ),
    MealItem(
        name="Tofu and Vegetable Curry with Basmati Rice",
        kcal=510,
        protein_g=22.0,
        carbs_g=68.0,
        fat_g=14.0,
        restriction_tags={_V, _VG, _GF, _DF, _NF, _H},
    ),
    MealItem(
        name="Turkey Meatballs with Zucchini Noodles and Tomato Sauce",
        kcal=460,
        protein_g=42.0,
        carbs_g=24.0,
        fat_g=18.0,
        restriction_tags={_GF, _DF, _NF, _H, _LC},
    ),
    MealItem(
        name="Grilled Chicken with Cauliflower Rice and Salad",
        kcal=420,
        protein_g=46.0,
        carbs_g=22.0,
        fat_g=14.0,
        restriction_tags={_GF, _DF, _NF, _H, _LC},
    ),
    MealItem(
        name="Black Bean and Sweet Potato Bowl with Guacamole",
        kcal=530,
        protein_g=18.0,
        carbs_g=74.0,
        fat_g=16.0,
        restriction_tags={_V, _VG, _GF, _DF, _NF, _H},
    ),
    MealItem(
        name="Lamb Kofta with Tabbouleh and Greek Yoghurt",
        kcal=580,
        protein_g=38.0,
        carbs_g=44.0,
        fat_g=22.0,
        restriction_tags={_NF, _H},
    ),
]


# ── Public API ─────────────────────────────────────────────────────────────────

def get_default_meal_pool(
    calorie_target: float,
    restrictions: List[str] | None = None,
) -> List[MealItem]:
   
    import logging
    log = logging.getLogger(__name__)

    if not restrictions:
        log.debug("No dietary restrictions — returning full meal pool (%d meals)", len(_LIBRARY))
        return list(_LIBRARY)

    # Convert string restrictions to DietaryRestriction enum values (skip unknowns)
    parsed: list[DietaryRestriction] = []
    for r in restrictions:
        try:
            parsed.append(DietaryRestriction(r.lower().strip()))
        except ValueError:
            log.warning("Unknown dietary restriction ignored: %r", r)

    if not parsed:
        return list(_LIBRARY)

    filtered = [meal for meal in _LIBRARY if meal.is_eligible(parsed)]
    log.debug(
        "Meal pool filtered by %s: %d/%d meals remaining (target %.0f kcal)",
        [r.value for r in parsed], len(filtered), len(_LIBRARY), calorie_target,
    )
    return filtered
