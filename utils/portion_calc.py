def get_required_grams(target_protein: float, protein_per_100g: float) -> float:
    """
    Calculate how many grams of the ingredient are needed to hit target protein.
    """
    return round((target_protein / protein_per_100g) * 100, 1)

def get_actual_macros(grams: float, ingredient: dict) -> dict:
    """
    Based on required grams, calculate actual macros for that ingredient.
    """
    factor = grams / 100
    return {
        "protein": round(ingredient["protein"] * factor, 1),
        "fat": round(ingredient["fat"] * factor, 1),
        "carbs": round(ingredient["carbs"] * factor, 1),
        "calories": round(ingredient["calories"] * factor, 1)
    }
