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
            for snack in meal_plan.get("snacks", []):
                snack["calories"] = round(kcal / len(meal_plan["snacks"]), 1)
                snack["protein"] = round((snack["calories"] * 0.40) / 4, 1)
                snack["fat"] = round((snack["calories"] * 0.30) / 9, 1)
                snack["carbs"] = round((snack["calories"] * 0.30) / 4, 1)
        else:
            for m in meal_plan.get("meals", []):
                if m.get("time") == meal:
                    m["calories"] = round(kcal)
                    m["protein"] = round((kcal * 0.40) / 4, 1)
                    m["fat"] = round((kcal * 0.30) / 9, 1)
                    m["carbs"] = round((kcal * 0.30) / 4, 1)
