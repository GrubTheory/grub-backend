from utils.macro_split import get_macro_targets
from utils.macro_allocation import allocate_macros
from utils.portion_calc import get_required_grams, get_actual_macros
from utils.theme import generate_weekly_theme

# Simulate input from Make.com
calories_breakfast = 600
target_macros = get_macro_targets(calories_breakfast)
allocation = allocate_macros(target_macros)

# Get ingredients from theme
theme = generate_weekly_theme()
day1 = theme[0]
protein_ingredient = day1["breakfast"]["protein"]
carb_ingredient = day1["breakfast"]["carb"]

# Calculate required grams per ingredient
grams_prot = get_required_grams(allocation["protein_source"]["protein"], protein_ingredient["protein"])
grams_carb = get_required_grams(allocation["carb_source"]["carbs"], carb_ingredient["carbs"])

# Calculate actual macros from portion size
macros_prot = get_actual_macros(grams_prot, protein_ingredient)
macros_carb = get_actual_macros(grams_carb, carb_ingredient)

# Print result
import json
print(json.dumps({
    "breakfast": {
        "protein": {
            "name": protein_ingredient["name"],
            "portion": f"{grams_prot}g",
            "macros": macros_prot
        },
        "carb": {
            "name": carb_ingredient["name"],
            "portion": f"{grams_carb}g",
            "macros": macros_carb
        },
        "target_macros": target_macros
    }
}, indent=2))
