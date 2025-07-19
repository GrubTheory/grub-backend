# main.py
from fastapi import FastAPI
from routes.generate import router as generate_router
from utils.fuzzy_match import load_ingredient_names

app = FastAPI()

@app.get("/")
def ping():
    return {"message": "Grub backend is alive!"}

app.include_router(generate_router)

load_ingredient_names()  # Load ingredient names at startup
