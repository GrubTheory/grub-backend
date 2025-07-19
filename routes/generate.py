from fastapi import APIRouter, Request
from models import InputPayload
from utils.parser import parse_meal_plan
from utils.macro_allocation import allocate_macros
from utils.normalize_ingredients import extract_normalized_ingredients
from utils.fuzzy_match import fuzzy_match_ingredient
from utils.db_lookup import fetch_structured_ingredients
from utils.unit_conversion import convert_units_to_metric 
from utils.logger import log_final_output  # ⬅️ Updated import

router = APIRouter()

@router.post("/generate")
async def generate_meal_plan(request: Request):
    try:
        data = await request.json()
        payload = InputPayload(**data)

        # Step 1: Parse meal_plan string to dict
        meal_plan = parse_meal_plan(payload.meal_plan)

        # Step 2: Convert imperial units to metric
        meal_plan = convert_units_to_metric(meal_plan)

        # Step 3: Flatten meals list into dict by meal time
        meal_plan.update({m["time"]: m for m in meal_plan.get("meals", [])})

        # Step 4: Allocate macros
        allocate_macros(meal_plan, payload.calorie_target)

        # Step 5: Normalize ingredient names
        normalized_ingredients = extract_normalized_ingredients(meal_plan)

        # Step 6: Fuzzy match + attach db_records
        matched_names = set()
        for meal_time, ingredients in normalized_ingredients.items():
            for idx, ing in enumerate(ingredients):
                match = fuzzy_match_ingredient(ing)
                if match["matched"]:
                    matched_names.add(match["matched"])
                    normalized_ingredients[meal_time][idx]["matched_name"] = match["matched"]

        ingredient_records = fetch_structured_ingredients(list(matched_names))

        # Step 7: Attach db_record to matched ingredients
        name_to_record = {r["name"]: r for r in ingredient_records}
        for meal_time, ingredients in normalized_ingredients.items():
            for ing in ingredients:
                matched_name = ing.get("matched_name")
                if matched_name and matched_name in name_to_record:
                    ing["db_record"] = name_to_record[matched_name]

        # 🔥 Final log only
        log_final_output("Final normalized meal plan", {
            "uuid": payload.uuid,
            "calorie_target": payload.calorie_target,
            "meal_plan": meal_plan,
            "normalized_ingredients": normalized_ingredients
        })

        return {
            "status": "ok",
            "uuid": payload.uuid
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
