from fastapi import APIRouter, Request
from models import InputPayload
from utils.parser import parse_meal_plan
from utils.macro_allocation import allocate_macros
from utils.normalize_ingredients import extract_normalized_ingredients, normalize_ingredient_name
from utils.fuzzy_match import fuzzy_match_ingredient
from utils.db_lookup import fetch_structured_ingredients
from utils.scale_meal import scale_meal_plan
from utils.formatter import format_final_output
from utils.logger import log_final_output

router = APIRouter()

@router.post("/generate")
async def generate_meal_plan(request: Request):
    try:
        data = await request.json()
        payload = InputPayload(**data)

        # Step 1: Parse
        meal_plan = parse_meal_plan(payload.meal_plan)
        log_final_output("Parsed meal plan", meal_plan, "logs/01_parsed.json")

        # Step 2: Macro allocation
        allocate_macros(meal_plan, payload.calorie_target)
        log_final_output("Allocated macros", meal_plan, "logs/02_allocated_macros.json")

        # Step 3: Normalize
        normalized = extract_normalized_ingredients(meal_plan)
        log_final_output("Normalized ingredients", normalized, "logs/03_normalized.json")

        # Step 4: Fuzzy match
        matched = []
        for meal_time, group in normalized.items():
            for idx, raw_name in enumerate(group):
                match = fuzzy_match_ingredient(raw_name)
                if match["matched"]:
                    matched.append({
                        "meal_time": meal_time,
                        "ingredient_index": idx,
                        "original": raw_name,
                        "matched_name": match["matched"]
                    })
        log_final_output("Fuzzy matched names", matched, "logs/04_matched.json")

        # Step 5: DB fetch
        db_ingredients = fetch_structured_ingredients(matched)
        log_final_output("DB records attached", db_ingredients, "logs/05_attached.json")

        # Step 6: Attach db_records by meal_time + index
        meal_lookup = {m["time"]: m for m in meal_plan.get("meals", [])}
        snack_list = meal_plan.get("snacks", [])

        # Attach to regular meals
        for item in db_ingredients:
            time = item.get("meal_time")
            idx = item.get("ingredient_index")
            record = item.get("record")

            if time != "snacks":
                meal = meal_lookup.get(time)
                if meal and 0 <= idx < len(meal["ingredients"]):
                    meal["ingredients"][idx]["db_record"] = record

        # Attach to snacks using flat index
        flat_index = 0
        for item in db_ingredients:
            if item.get("meal_time") != "snacks":
                continue
            idx = item["ingredient_index"]
            record = item["record"]
            flat_index = 0
            found = False
            for snack in snack_list:
                for ing in snack.get("ingredients", []):
                    if flat_index == idx:
                        ing["db_record"] = record
                        found = True
                        break
                    flat_index += 1
                if found:
                    break

        # Step 7: Scale
        meal_plan = scale_meal_plan(meal_plan)
        log_final_output("Scaled meal plan", meal_plan, "logs/06_scaled.json")

        # Step 8: Format
        output = format_final_output(payload, meal_plan)
        log_final_output("Final output", output, "logs/07_final_output.json")

        return output

    except Exception as e:
        return {"status": "error", "message": str(e)}
