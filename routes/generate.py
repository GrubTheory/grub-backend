from fastapi import APIRouter, Request
from models import InputPayload
from utils.parser import parse_meal_plan
from utils.macro_allocation import allocate_macros
from utils.normalize_ingredients import extract_normalized_ingredients
from utils.fuzzy_match import fuzzy_match_ingredient
from utils.db_lookup import fetch_ingredients_by_name  # ✅ NEW IMPORT

router = APIRouter()

@router.post("/generate")
async def generate_meal_plan(request: Request):
    try:
        data = await request.json()
        payload = InputPayload(**data)

        # ✅ Parse the meal_plan string into a Python dict
        meal_plan = parse_meal_plan(payload.meal_plan)
        print("Parsed meal plan:", meal_plan)

        # ✅ Flatten meals list into dict by 'time' field
        meal_plan.update({m["time"]: m for m in meal_plan.get("meals", [])})

        # ✅ Allocate calories and macros
        allocate_macros(meal_plan, payload.calorie_target)
        print("Meal plan after macro allocation:", meal_plan)

        # ✅ Normalize ingredient names per meal
        normalized_ingredients = extract_normalized_ingredients(meal_plan)
        print("Normalized ingredients:", normalized_ingredients)

        # ✅ Fuzzy match each normalized ingredient
        fuzzy_matched_ingredients = {}
        for meal_time, ingredients in normalized_ingredients.items():
            fuzzy_matched_ingredients[meal_time] = [
                fuzzy_match_ingredient(ing) for ing in ingredients
            ]
        print("Fuzzy matched ingredients:", fuzzy_matched_ingredients)

        # ✅ Extract matched names
        matched_names = [
            item["matched"]
            for ingredients in fuzzy_matched_ingredients.values()
            for item in ingredients
            if item["matched"]
        ]
        print("Matched names:", matched_names)
        print("Matched name count:", len(matched_names))

        # ✅ Fetch full ingredient records from DB
        ingredient_records = fetch_ingredients_by_name(matched_names)
        print("Fetched ingredient records:", ingredient_records)

        return {
            "status": "ok",
            "uuid": payload.uuid
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
