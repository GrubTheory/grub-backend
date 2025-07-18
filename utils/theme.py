from utils.db import fetch_random_ingredient_by_category
import random

# --- Breakfast category pairs ---
ALLOWED_BREAKFAST_PAIRS = [
    ("breakfast_protein_egg", "breakfast_carb_toast"),
    ("breakfast_protein_dairy", "breakfast_carb_granola"),
    ("breakfast_protein_dairy", "breakfast_carb_berry"),
    ("breakfast_protein_nuts", "breakfast_carb_oats"),
    ("breakfast_protein_powder_animal", "breakfast_carb_fruit"),
]

# --- Main protein and carb categories ---
MAIN_PROTEINS = [
    "protein_poultry", "protein_red_meat", "protein_red_fish",
    "protein_white_fish", "protein_shellfish", "protein_plant_based"
]

MAIN_CARBS = [
    "carb_rice", "carb_quinoa", "carb_pasta",
    "carb_potato", "carb_sweet_potato", "carb_legume", "carb_grain_mix"
]

def generate_weekly_theme():
    breakfast_pairs = random.sample(ALLOWED_BREAKFAST_PAIRS, 5)
    breakfast_pairs += random.choices(breakfast_pairs, k=2)
    random.shuffle(breakfast_pairs)

    main_proteins = random.sample(MAIN_PROTEINS, 6)
    main_proteins += [random.choice(main_proteins)]
    random.shuffle(main_proteins)

    main_carbs = random.choices(MAIN_CARBS, k=7)

    week = []

    for i in range(7):
        b_cat_prot, b_cat_carb = breakfast_pairs[i]
        m_cat_prot = main_proteins[i]
        m_cat_carb = main_carbs[i]

        # Get ingredients from DB
        breakfast_protein = fetch_random_ingredient_by_category(b_cat_prot)
        breakfast_carb = fetch_random_ingredient_by_category(b_cat_carb)
        main_protein = fetch_random_ingredient_by_category(m_cat_prot)
        main_carb = fetch_random_ingredient_by_category(m_cat_carb)

        day_plan = {
            "day": i + 1,
            "breakfast": {
                "protein": breakfast_protein,
                "carb": breakfast_carb
            },
            "lunch": {
                "protein": main_protein,
                "carb": main_carb
            },
            "dinner": {
                "protein": main_protein,
                "carb": main_carb
            }
        }

        week.append(day_plan)

    return week
