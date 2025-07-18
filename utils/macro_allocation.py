def allocate_macros(total_macros: dict) -> dict:
    """
    Distributes total macros between protein and carb ingredients.

    - 70% of protein → protein source
    - 30% of protein → carb source

    - 50% of fat → both
    - 20% of carbs → protein source
    - 80% of carbs → carb source
    """
    return {
        "protein_source": {
            "protein": round(total_macros["protein"] * 0.7, 1),
            "fat": round(total_macros["fat"] * 0.5, 1),
            "carbs": round(total_macros["carbs"] * 0.2, 1)
        },
        "carb_source": {
            "protein": round(total_macros["protein"] * 0.3, 1),
            "fat": round(total_macros["fat"] * 0.5, 1),
            "carbs": round(total_macros["carbs"] * 0.8, 1)
        }
    }
