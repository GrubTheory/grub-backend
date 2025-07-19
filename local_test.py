import json
import os
from models import InputPayload
from utils.parser import parse_meal_plan
from utils.unit_conversion import convert_units_to_metric
from utils.macro_allocation import allocate_macros
from utils.normalize_ingredients import extract_normalized_ingredients
from utils.fuzzy_match import fuzzy_match_ingredient, load_ingredient_names
from utils.db_lookup import fetch_structured_ingredients
from utils.scale_meal import scale_meal_plan
from utils.logger import log_final_output  # ⬅️ Use final log only

# ✅ Enable debug logs
os.environ["GRUB_DEBUG"] = "1"

# ✅ Load payload from file
with open("tests/payload.json", "r") as f:
    raw = json.load(f)

# ✅ Parse and hydrate payload
payload = InputPayload(**raw)
meal_plan = parse_meal_plan(payload.meal_plan)

# ✅ Convert imperial units to metric
meal_plan = convert_units_to_metric(meal_plan)

# ✅ Flatten meals into dict by time
meal_plan.update({m["time"]: m for m in meal_plan.get("meals", [])})

# ✅ Macro allocation
allocate_macros(meal_plan, payload.calorie_target)

# ✅ Ingredient normalization
normalized = extract_normalized_ingredients(meal_plan)

# ✅ Fuzzy match → build structured_matches list
load_ingredient_names()
structured_matches = []

for meal_time, ingredients in normalized.items():
    for idx, ing in enumerate(ingredients):
        match = fuzzy_match_ingredient(ing)
        if match["matched"]:
            structured_matches.append({
                "meal_time": meal_time,
                "ingredient_index": idx,
                "original": ing,
                "matched_name": match["matched"]
            })

# ✅ Fetch ingredient records using structured match data
ingredient_records = fetch_structured_ingredients(structured_matches)

# ✅ Create meal lookup by time (for reattachment)
meal_lookup = {meal["time"]: meal for meal in meal_plan["meals"]}

# ✅ Attach DB records back to correct ingredient in meal_plan
for item in ingredient_records:
    meal_time = item["meal_time"]
    idx = item["ingredient_index"]
    record = item["record"]

    meal = meal_lookup.get(meal_time)
    if not meal:
        continue

    ingredients = meal["ingredients"]
    if 0 <= idx < len(ingredients):
        ingredients[idx]["db_record"] = record

# ✅ Final step: scale
scale_meal_plan(meal_plan)

# ✅ Log final result only
log_final_output("Final scaled meal plan", {
    "uuid": payload.uuid,
    "calorie_target": payload.calorie_target,
    "meal_plan": meal_plan
})
