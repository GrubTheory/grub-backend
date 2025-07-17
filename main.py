from models import InputPayload, OutputPayload
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def ping():
    return {"message": "Grub backend is alive!"}


@app.post("/test", response_model=OutputPayload)
def test_generate(payload: InputPayload):
    return {
        "uuid": payload.uuid,
        "daily_totals": {
            "calories": payload.calorie_target,
            "protein": 0,
            "fat": 0,
            "carbs": 0
        },
        "meals": []
    }
