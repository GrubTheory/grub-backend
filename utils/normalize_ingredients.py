import re
from typing import Dict, List

# Words that add noise but don't affect core ingredient identity
TRASH_WORDS = {
    "fresh", "plain", "chopped", "grilled", "boiled", "raw", "sliced",
    "extra virgin", "unsalted", "whole", "low fat", "fat free"
}

def normalize_ingredient_name(name: str) -> str:
    # Lowercase
    name = name.lower()

    # Remove parentheses content
    name = re.sub(r"\([^)]*\)", "", name)

    # Remove commas
    name = name.replace(",", " ")

    # Remove trash words
    for word in TRASH_WORDS:
        name = name.replace(word, "")

    # Collapse multiple spaces
    name = re.sub(r"\s+", " ", name).strip()

    return name


def extract_normalized_ingredients(meal_plan: dict) -> Dict[str, List[str]]:
    result = {}
    for meal_name, meal_data in meal_plan.items():
        ingredients = meal_data.get("ingredients", [])
        cleaned = []
        for item in ingredients:
            raw = item.get("name")
            if raw:
                cleaned.append(normalize_ingredient_name(raw))
        result[meal_name] = cleaned
    return result
