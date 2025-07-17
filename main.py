# main.py
from fastapi import FastAPI
from routes.generate import router as generate_router

app = FastAPI()

@app.get("/")
def ping():
    return {"message": "Grub backend is alive!"}

app.include_router(generate_router)
