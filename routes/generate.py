from fastapi import APIRouter, Request
from models import InputPayload
from utils.parser import parse_meal_plan
from utils.macro_allocation import allocate_macros  # ⬅️ assuming you save the function in utils/macros.py

router = APIRouter()

@router.post("/generate")
async def generate_meal_plan(request: Request):
    try:
        data = await request.json()
        payload = InputPayload(**data)

        # ✅ Parse the meal_plan string into a Python dict
        meal_plan = parse_meal_plan(payload.meal_plan)
        print("Parsed meal plan:", meal_plan)

        # ✅ Allocate calories and macros
        allocate_macros(meal_plan, payload.calorie_target)
        print("Meal plan after macro allocation:", meal_plan)

        return {
            "status": "ok",
            "uuid": payload.uuid
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
