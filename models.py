from pydantic import BaseModel
from typing import List, Optional


class Ingredient(BaseModel):
    name: str
    quantity: float
    unit: str


class Totals(BaseModel):
    calories: float
    protein: float
    fat: float
    carbs: float


class Meal(BaseModel):
    meal: str
    ingredients: List[Ingredient]
    totals: Totals


class OutputPayload(BaseModel):
    uuid: str
    daily_totals: Totals
    meals: List[Meal]

class InputPayload(BaseModel):
    uuid: str
    diet_type: str
    calorie_target: int
    calories_breakfast: int
    calories_lunch: int
    calories_dinner: int
    calories_snacks: int
    
