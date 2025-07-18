from fastapi import APIRouter, Request
from models import InputPayload
from utils.parser import parse_meal_plan

router = APIRouter()

@router.post("/generate")
async def generate_meal_plan(request: Request):
    try:
        data = await request.json()
        payload = InputPayload(**data)

        # ✅ Parse the meal_plan string into a Python dict
        meal_plan = parse_meal_plan(payload.meal_plan)
        print("Parsed meal plan:", meal_plan)

        # Placeholder: future macro logic goes here

        return {
            "status": "ok",
            "uuid": payload.uuid
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
