from copy import deepcopy


def add_macros(record, grams):
    factor = grams / 100
    return {
        "calories": record["calories"] * factor,
        "protein": record["protein"] * factor,
        "fat": record["fat"] * factor,
        "carbs": record["carbs"] * factor
    }


def scale_group(group, current_macros, target_macros):
    for ing in group:
        record = ing["db_record"]
        if not record.get("scalable"):
            continue

        max_grams = float(record.get("max_per_meal", 100))
        unit_macros = add_macros(record, 100)

        for macro in ["calories", "protein", "fat", "carbs"]:
            needed = target_macros[macro] - current_macros[macro]
            if needed < 0:
                needed = 0
            unit_val = unit_macros[macro]
            grams = min((needed / unit_val) * 100 if unit_val else 0, max_grams)
            grams = round(grams, 1)
            ing["quantity"] = f"{grams}g"
            ing["unit"] = "g"
            added = add_macros(record, grams)
            for k in current_macros:
                current_macros[k] += added[k]
            break  # only scale one macro per ingredient


def scale_single_meal(meal: dict) -> dict:
    """
    Adjust ingredient quantities to meet the target macros for a single meal.
    This modifies the meal in-place and returns it.
    """
    if "ingredients" not in meal:
        return meal

    ingredients = deepcopy(meal["ingredients"])
    target_macros = {
        "calories": meal.get("calories", 0),
        "protein": meal.get("protein", 0),
        "fat": meal.get("fat", 0),
        "carbs": meal.get("carbs", 0)
    }
    current_macros = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}

    protein_ings = []
    carb_ings = []
    green_ings = []
    fixed_ings = []

    for ing in ingredients:
        record = ing.get("db_record")
        if not record:
            continue
        if record.get("cooking_ingredient"):
            fixed_ings.append(ing)
            continue

        category = record.get("category", "").lower()
        if "protein" in category:
            protein_ings.append(ing)
        elif "carb" in category:
            carb_ings.append(ing)
        else:
            green_ings.append(ing)

    # Apply scaling by priority
    scale_group(protein_ings, current_macros, target_macros)
    scale_group(carb_ings, current_macros, target_macros)
    scale_group(green_ings, current_macros, target_macros)

    # Final trim: round macros
    for k in target_macros:
        meal[k] = round(current_macros[k], 1)

    # Update ingredients
    meal["ingredients"] = protein_ings + carb_ings + green_ings + fixed_ings
    return meal


def scale_meal_plan(meal_plan: dict) -> dict:
    """
    Adjust all meals and snacks in the meal plan to match their target macros.
    """
    for meal in meal_plan.get("meals", []):
        scale_single_meal(meal)
    for snack in meal_plan.get("snacks", []):
        scale_single_meal(snack)
    return meal_plan
