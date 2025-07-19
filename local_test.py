import json
from models import InputPayload
from utils.parser import parse_meal_plan
from utils.macro_allocation import allocate_macros
from utils.normalize_ingredients import extract_normalized_ingredients

# Load payload from file
with open("tests/payload.json", "r") as f:
    raw = json.load(f)

payload = InputPayload(**raw)
meal_plan = parse_meal_plan(payload.meal_plan)

print("Parsed meal_plan:", meal_plan)
print("TYPE:", type(meal_plan))
print("KEYS:", list(meal_plan.keys()))

allocate_macros(meal_plan, payload.calorie_target)
print("After macro allocation:", meal_plan)

normalized = extract_normalized_ingredients(meal_plan)
print("Normalized ingredients:", normalized)
