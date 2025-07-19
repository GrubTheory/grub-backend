import json
from models import InputPayload
from utils.parser import parse_meal_plan
from utils.macro_allocation import allocate_macros
from utils.normalize_ingredients import extract_normalized_ingredients
from utils.fuzzy_match import fuzzy_match_ingredient, load_ingredient_names
from utils.db_lookup import fetch_ingredients_by_name  # ✅ DB fetch import

# ✅ Load payload from file
with open("tests/payload.json", "r") as f:
    raw = json.load(f)

# ✅ Parse and hydrate payload
payload = InputPayload(**raw)
meal_plan = parse_meal_plan(payload.meal_plan)

print("Parsed meal_plan:", meal_plan)
print("TYPE:", type(meal_plan))
print("KEYS:", list(meal_plan.keys()))

# ✅ Macro allocation
allocate_macros(meal_plan, payload.calorie_target)
print("After macro allocation:", meal_plan)

# ✅ Ingredient normalization
normalized = extract_normalized_ingredients(meal_plan)
print("Normalized ingredients:", normalized)

# ✅ Fuzzy matching
load_ingredient_names()
fuzzy_matched = {
    meal: [fuzzy_match_ingredient(ing) for ing in ingredients]
    for meal, ingredients in normalized.items()
}
print("Fuzzy matched ingredients:", fuzzy_matched)

# ✅ Extract matched names
matched_names = [
    item["matched"]
    for group in fuzzy_matched.values()
    for item in group
    if item["matched"]
]
print("Matched names:", matched_names)

# ✅ DB fetch based on matched names
ingredient_records = fetch_ingredients_by_name(matched_names)
print("Fetched ingredient records from DB:", ingredient_records)
