from typing import Dict
from copy import deepcopy

PRIORITY_ORDER = ["protein", "carbs", "green"]

# ✅ Units like “medium”, “stick”, etc., should just be treated as “unit”
DUMB_UNITS = {
    "medium", "large", "small", "stick", "slice", "clove", "piece", "serving",
    "container", "package", "bag", "unit", "head", "cup", "bunch"
}

def normalize_unit(unit: str) -> str:
    unit = unit.lower().strip()
    if unit in DUMB_UNITS:
        return "unit"
    return unit

def scale_meal_plan(meal_plan: Dict) -> Dict:
    scaled = deepcopy(meal_plan)
    scaled["meals"] = []

    for meal in meal_plan.get("meals", []):
        scaled_meal = scale_single_meal(meal)
        scaled["meals"].append(scaled_meal)

    # ✅ Debug print to inspect snack macros
    print("\n=== SCALING SNACKS ===")
    for snack in meal_plan.get("snacks", []):
        print(f"- {snack.get('name', 'Unnamed snack')}, target: {snack.get('target_macros')}")

    # ✅ Handle snacks
    scaled["snacks"] = []
    for snack in meal_plan.get("snacks", []):
        scaled_snack = scale_single_meal(snack)
        scaled["snacks"].append(scaled_snack)

    return scaled


def scale_single_meal(meal: Dict) -> Dict:
    ingredients = meal.get("ingredients", [])
    target = meal.get("target_macros", {})
    total_p = total_c = total_f = total_kcal = 0
    
    for ing in ingredients:
        rec = ing.get("db_record")
        qty = ing.get("quantity")
        if not rec or qty is None:
            continue
        print(f"▶ INGREDIENT: {ing.get('name')}")
        print(f"   - quantity: {qty}")
        print(f"   - unit: {ing.get('unit')}")
        print(f"   - db_record unit: {rec.get('unit_of_measure')}")
        print(f"   - db qty: {rec.get('qty')}")
        print(f"   - protein: {rec.get('protein')}")
        print(f"   - fat: {rec.get('fat')}")
        print(f"   - carbs: {rec.get('carbs')}")
        print("---")

        # 🔥 Normalize weird units both from ingredient and db_record
        unit = normalize_unit(ing.get("unit", ""))
        db_unit = normalize_unit(rec.get("unit_of_measure", ""))
        if unit != db_unit:
            unit = db_unit  # force alignment with db if possible

        try:
            base_qty = float(rec["qty"])
            multiplier = qty / base_qty
        except (ValueError, TypeError, ZeroDivisionError):
            continue

        total_p += rec["protein"] * multiplier
        total_c += rec["carbs"] * multiplier
        total_f += rec["fat"] * multiplier
        total_kcal += rec["calories"] * multiplier

    meal["protein"] = round(total_p, 1)
    meal["carbs"] = round(total_c, 1)
    meal["fat"] = round(total_f, 1)
    meal["calories"] = round(total_kcal)

    return meal
