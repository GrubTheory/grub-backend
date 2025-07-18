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
    calorie_target: int
    diet_type: Optional[str]
    meal_plan: str  # Still a raw JSON string
    
