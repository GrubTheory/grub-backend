from fastapi import APIRouter, Request
from models import InputPayload
from utils.parser import parse_meal_plan
from utils.macro_allocation import allocate_macros
from utils.normalize_ingredients import extract_normalized_ingredients

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

        return {
            "status": "ok",
            "uuid": payload.uuid
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
