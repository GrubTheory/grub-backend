# routes/generate.py
from fastapi import APIRouter
from models import InputPayload, OutputPayload

router = APIRouter()

@router.post("/test", response_model=OutputPayload)
def test_generate(payload: InputPayload):
    return {
        "uuid": payload.uuid,
        "daily_totals": {
            "calories": payload.calorie_target,
            "protein": 0,
            "fat": 0,
            "carbs": 0,
        },
        "meals": []
    }
