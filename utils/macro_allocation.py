def allocate_macros(meal_plan: dict, calorie_target: int) -> None:
    # Define split ratios and max caps
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

    # Step 3: Macro split and injection
    for meal, kcal in allocated.items():
        meal_data = meal_plan.get(meal, {})
        meal_data["calories"] = round(kcal)
        meal_data["protein"] = round((kcal * 0.40) / 4, 1)
        meal_data["fat"] = round((kcal * 0.30) / 9, 1)
        meal_data["carbs"] = round((kcal * 0.30) / 4, 1)
