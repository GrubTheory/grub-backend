import json

def parse_meal_plan(meal_plan_str: str) -> dict:
    try:
        return json.loads(meal_plan_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid meal_plan JSON: {e}")