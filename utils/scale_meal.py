from typing import Dict
from copy import deepcopy

PRIORITY_ORDER = ["protein", "carbs", "green"]

STEP_SIZES = {
    "cup": 0.5,
    "tbsp": 0.5,
    "tsp": 0.5,
    "oz": 1,
    "g": 1,
    "ml": 1,
    "unit": 1
}

def get_step_size(unit: str) -> float:
    unit = unit.lower()
    return STEP_SIZES.get(unit, 1)

CATEGORY_MACRO_MAP = {
    "protein": "protein",
    "carbs": "carbs",
    "green": "carbs"
}

def scale_meal_plan(meal_plan: Dict) -> Dict:
    scaled = deepcopy(meal_plan)
    scaled["meals"] = []

    total_leftover_p = total_leftover_c = total_leftover_f = total_leftover_kcal = 0

    for meal in meal_plan.get("meals", []):
        scaled_meal = scale_single_meal(meal)
        scaled["meals"].append(scaled_meal)

        # accumulate leftover macros if unfilled
        unfilled = scaled_meal.get("unfilled")
        if unfilled:
            total_leftover_p += unfilled.get("protein", 0)
            total_leftover_c += unfilled.get("carbs", 0)
            total_leftover_f += unfilled.get("fat", 0)
            total_leftover_kcal += unfilled.get("calories", 0)

    snacks = meal_plan.get("snacks", [])
    num_snacks = len(snacks)

    if total_leftover_kcal > 0 and num_snacks > 0:
        per_snack_p = total_leftover_p / num_snacks
        per_snack_c = total_leftover_c / num_snacks
        per_snack_f = total_leftover_f / num_snacks
        per_snack_kcal = total_leftover_kcal / num_snacks

        for snack in snacks:
            snack.setdefault("target_macros", {})
            snack["target_macros"]["calories"] = per_snack_kcal + snack["target_macros"].get("calories", 0)
            snack["target_macros"]["protein"] = per_snack_p + snack["target_macros"].get("protein", 0)
            snack["target_macros"]["carbs"] = per_snack_c + snack["target_macros"].get("carbs", 0)
            snack["target_macros"]["fat"] = per_snack_f + snack["target_macros"].get("fat", 0)

    scaled["snacks"] = []
    for snack in snacks:
        scaled_snack = scale_single_meal(snack)
        scaled["snacks"].append(scaled_snack)

    return scaled

def scale_single_meal(meal: Dict) -> Dict:
    ingredients = meal.get("ingredients", [])
    target = meal.get("target_macros", {})
    if not target:
        return meal

    for ing in ingredients:
        rec = ing.get("db_record", {})
        unit = rec.get("unit_of_measure", "unit").lower()
        ing["unit"] = unit
        ing["quantity"] = STEP_SIZES.get(unit, 1)

    def compute_totals():
        p = c = f = kcal = 0
        for ing in ingredients:
            rec = ing.get("db_record")
            qty = ing.get("quantity")
            if not rec or qty is None:
                continue
            try:
                multiplier = qty / rec["qty"]
            except:
                continue
            p += rec["protein"] * multiplier
            c += rec["carbs"] * multiplier
            f += rec["fat"] * multiplier
            kcal += rec["calories"] * multiplier
        return p, c, f, kcal

    def is_close(p, c, f, kcal):
        t_kcal = target.get("calories", 0)
        return abs(kcal - t_kcal) <= 0.02 * t_kcal

    target_kcal = target.get("calories", 0)

    for category in PRIORITY_ORDER:
        for ing in ingredients:
            rec = ing.get("db_record")
            if (
                not rec
                or rec.get("scalable") != True
                or rec.get("category") != category
                or rec.get("cooking_ingredient") == True
            ):
                continue

            base_qty = rec["qty"]
            max_units = rec.get("max_per_meal", 5)
            step = get_step_size(rec.get("unit_of_measure", "unit"))

            current_qty = ing.get("quantity", 0)
            current_units = round(current_qty / base_qty / step) * step

            while current_units + step <= max_units:
                tentative_units = current_units + step
                tentative_qty = round(tentative_units * base_qty, 2)

                ing["quantity"] = tentative_qty
                p, c, f, kcal = compute_totals()

                if is_close(p, c, f, kcal):
                    break
                if kcal > target_kcal * 1.02:
                    ing["quantity"] = round(current_units * base_qty, 2)
                    break

                current_units = tentative_units

        p, c, f, kcal = compute_totals()
        if is_close(p, c, f, kcal):
            break

    p, c, f, kcal = compute_totals()
    meal["protein"] = round(p, 1)
    meal["carbs"] = round(c, 1)
    meal["fat"] = round(f, 1)
    meal["calories"] = round(kcal)

    if not is_close(p, c, f, kcal):
        meal["unfilled"] = {
            "calories": round(target.get("calories", 0) - kcal, 1),
            "protein": round(target.get("protein", 0) - p, 1),
            "carbs": round(target.get("carbs", 0) - c, 1),
            "fat": round(target.get("fat", 0) - f, 1)
        }

    return meal
