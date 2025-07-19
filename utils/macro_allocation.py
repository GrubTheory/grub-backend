def allocate_macros(meal_plan: dict, calorie_target: int) -> None:
    splits = {
        "breakfast": {"ratio": 0.20, "max": 600},
        "lunch": {"ratio": 0.35, "max": 1000},
        "dinner": {"ratio": 0.30, "max": 900},
    }

    allocated = {}
    total_allocated = 0

    # Step 1: Calculate capped allocations
    for meal, data in splits.items():
        raw = calorie_target * data["ratio"]
        capped = min(raw, data["max"])
        allocated[meal] = round(capped)
        total_allocated += capped

    # Step 2: Remaining goes to snacks
    allocated["snacks"] = round(calorie_target - total_allocated)

    # Step 3: Inject macros into meal_plan
    for meal, kcal in allocated.items():
        if meal == "snacks":
            snacks = meal_plan.get("snacks", [])
            if not snacks:
                continue
            per_snack_kcal = round(kcal / len(snacks), 1)
            for snack in snacks:
                protein = round((per_snack_kcal * 0.40) / 4, 1)
                fat = round((per_snack_kcal * 0.30) / 9, 1)
                carbs = round((per_snack_kcal * 0.30) / 4, 1)

                snack["calories"] = per_snack_kcal
                snack["protein"] = protein
                snack["fat"] = fat
                snack["carbs"] = carbs
                snack["target_macros"] = {
                    "calories": per_snack_kcal,
                    "protein": protein,
                    "fat": fat,
                    "carbs": carbs,
                }
        else:
            for m in meal_plan.get("meals", []):
                if m.get("time") == meal:
                    protein = round((kcal * 0.40) / 4, 1)
                    fat = round((kcal * 0.30) / 9, 1)
                    carbs = round((kcal * 0.30) / 4, 1)

                    m["calories"] = round(kcal)
                    m["protein"] = protein
                    m["fat"] = fat
                    m["carbs"] = carbs
                    m["target_macros"] = {
                        "calories": round(kcal),
                        "protein": protein,
                        "fat": fat,
                        "carbs": carbs,
                    }
