# routes/generate.py
from fastapi import APIRouter
from models import InputPayload, OutputPayload

router = APIRouter()

@router.post("/generate")
async def generate_meal_plan(request: Request):
    try:
        data = await request.json()
        payload = InputPayload(**data)

        # Debug log (optional)
        print("Received:", payload.dict())

        return {"status": "ok", "uuid": payload.uuid}

    except Exception as e:
        return {"status": "error", "message": str(e)}