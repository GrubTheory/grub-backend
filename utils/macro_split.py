def get_macro_targets(calories: float, protein_pct=0.4, fat_pct=0.3, carb_pct=0.3) -> dict:
    """
    Splits a calorie value into grams of protein, fat, and carbs based on ratios.

    - Protein: 4 kcal/g
    - Carbs: 4 kcal/g
    - Fat: 9 kcal/g
    """
    protein = round((calories * protein_pct) / 4, 1)
    fat = round((calories * fat_pct) / 9, 1)
    carbs = round((calories * carb_pct) / 4, 1)

    return {
        "protein": protein,
        "fat": fat,
        "carbs": carbs,
        "calories": calories
    }
