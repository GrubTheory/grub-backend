import json

def format_final_output(payload, meal_plan):
    # ✅ Load original meal_plan from string
    original = json.loads(payload.meal_plan)

    # ✅ Flatten meals by time for lookup
    meal_lookup = {m.get("time"): m for m in meal_plan.get("meals", [])}

    # ✅ Update meals with calculated macros
    for meal in original["meals"]:
        time = meal.get("time")
        updated = meal_lookup.get(time)
        if updated:
            meal["ingredients"] = updated.get("ingredients", [])
            meal["calories"] = updated.get("calories")
            meal["protein"] = updated.get("protein")
            meal["fat"] = updated.get("fat")
            meal["carbs"] = updated.get("carbs")

    # ✅ Update snacks by index
    updated_snacks = meal_plan.get("snacks", [])
    original_snacks = original.get("snacks", [])

    for i, snack in enumerate(original_snacks):
        if i < len(updated_snacks):
            updated = updated_snacks[i]
            snack["ingredients"] = updated.get("ingredients", [])
            snack["calories"] = updated.get("calories")
            snack["protein"] = updated.get("protein")
            snack["fat"] = updated.get("fat")
            snack["carbs"] = updated.get("carbs")

    # ✅ Remove db_record from all ingredients
    for meal in original.get("meals", []):
        for ing in meal.get("ingredients", []):
            ing.pop("db_record", None)

    for snack in original.get("snacks", []):
        for ing in snack.get("ingredients", []):
            ing.pop("db_record", None)

    # ✅ Calculate new totals
    all_items = original["meals"] + original.get("snacks", [])
    total_calories = sum(item.get("calories") or 0 for item in all_items)
    total_protein = sum(item.get("protein") or 0 for item in all_items)
    total_fat = sum(item.get("fat") or 0 for item in all_items)
    total_carbs = sum(item.get("carbs") or 0 for item in all_items)

    original["totals"] = {
        "calories": round(total_calories, 1),
        "protein": round(total_protein, 1),
        "fat": round(total_fat, 1),
        "carbs": round(total_carbs, 1)
    }

    return {
        "uuid": payload.uuid,
        "calorie_target": payload.calorie_target,
        "meal_plan": original
    }
