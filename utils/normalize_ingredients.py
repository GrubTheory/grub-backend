import re
from typing import Dict, List

TRASH_WORDS = {
    "fresh", "plain", "chopped", "grilled", "boiled", "raw", "sliced",
    "extra virgin", "unsalted", "whole", "low fat", "fat free" , "chopped", "minced", "low sodium", "low sugar", "low-fat", 
    "organic", "reduced", "sodium", "jullienned", "sticks", "pieces", "diced", "cubed", "shredded", "crushed",
    "ground", "powdered", "cooked", "baked", "steamed", "roasted", "flowerets", "halved", "quartered", "mixed", "chopped"
}

def normalize_ingredient_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r"\([^)]*\)", "", name)
    name = name.replace(",", " ")
    for word in TRASH_WORDS:
        name = name.replace(word, "")
    name = re.sub(r"\s+", " ", name).strip()
    return name


def extract_normalized_ingredients(meal_plan: dict) -> Dict[str, List[str]]:
    result = {}

    for key in ("breakfast", "lunch", "dinner"):
        for meal in meal_plan.get("meals", []):
            if meal.get("time") == key:
                cleaned = []
                for item in meal.get("ingredients", []):
                    raw = item.get("name")
                    if raw:
                        cleaned.append(normalize_ingredient_name(raw))
                result[key] = cleaned

    # Handle snacks (list of snack dicts)
    snack_ingredients = []
    for snack in meal_plan.get("snacks", []):
        for item in snack.get("ingredients", []):
            raw = item.get("name")
            if raw:
                snack_ingredients.append(normalize_ingredient_name(raw))
    result["snacks"] = snack_ingredients

    return result
