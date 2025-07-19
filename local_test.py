import json
import os
from models import InputPayload
from utils.parser import parse_meal_plan
from utils.macro_allocation import allocate_macros
from utils.normalize_ingredients import extract_normalized_ingredients, normalize_ingredient_name
from utils.fuzzy_match import fuzzy_match_ingredient, load_ingredient_names
from utils.db_lookup import fetch_structured_ingredients
from utils.scale_meal import scale_meal_plan
from utils.formatter import format_final_output
from utils.logger import log_final_output

os.environ["GRUB_DEBUG"] = "1"
os.makedirs("logs", exist_ok=True)

# Load payload
with open("tests/payload.json", "r") as f:
    raw = json.load(f)
payload = InputPayload(**raw)

# Step 1: Parse
meal_plan = parse_meal_plan(payload.meal_plan)
log_final_output("Parsed meal plan", meal_plan, "logs/01_parsed.json")

# Step 2: Allocate macros
allocate_macros(meal_plan, payload.calorie_target)
log_final_output("Allocated macros", meal_plan, "logs/02_allocated_macros.json")

# Step 3: Normalize
normalized = extract_normalized_ingredients(meal_plan)
log_final_output("Normalized ingredients", normalized, "logs/03_normalized.json")

# Step 4: Fuzzy match
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
log_final_output("Fuzzy matched names", structured_matches, "logs/04_matched.json")

# Step 5: Fetch from DB
ingredient_records = fetch_structured_ingredients(structured_matches)
log_final_output("DB records attached", ingredient_records, "logs/05_attached.json")

# Step 6: Attach db_record
meal_lookup = {meal["time"]: meal for meal in meal_plan.get("meals", [])}
snack_list = meal_plan.get("snacks", [])

# Attach to regular meals
for item in ingredient_records:
    time = item.get("meal_time")
    idx = item.get("ingredient_index")
    record = item.get("record")

    if time != "snacks":
        meal = meal_lookup.get(time)
        if meal and 0 <= idx < len(meal["ingredients"]):
            meal["ingredients"][idx]["db_record"] = record

# Attach to snacks using flat index
flat_index = 0
for item in ingredient_records:
    if item.get("meal_time") != "snacks":
        continue
    idx = item["ingredient_index"]
    record = item["record"]
    flat_index = 0
    found = False
    for snack in snack_list:
        for ing in snack.get("ingredients", []):
            if flat_index == idx:
                ing["db_record"] = record
                found = True
                break
            flat_index += 1
        if found:
            break

# Step 7: Scale
meal_plan = scale_meal_plan(meal_plan)
log_final_output("Scaled meals", meal_plan, "logs/06_scaled.json")

# Step 8: Final output
final_output = format_final_output(payload, meal_plan)
log_final_output("Final output", final_output, "logs/07_final_output.json")

# Save to tests dir
with open("tests/final_output.json", "w") as f:
    json.dump(final_output, f, indent=2)
