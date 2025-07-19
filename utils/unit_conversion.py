import re
from fractions import Fraction

# Word-to-number mapping
WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "half": 0.5, "quarter": 0.25
}

# Normalized unit mapping
UNIT_MAP = {
    "cup": "cup", "cups": "cup", "c": "cup",
    "tablespoon": "tablespoon", "tablespoons": "tablespoon", "tbsp": "tablespoon", "tbs": "tablespoon", "tb": "tablespoon",
    "teaspoon": "teaspoon", "teaspoons": "teaspoon", "tsp": "teaspoon",
    "oz": "oz", "ounce": "oz", "ounces": "oz", "oz.": "oz",
    "lb": "lb", "lbs": "lb", "pound": "lb", "pounds": "lb",
    "fl oz": "fl oz", "fluid ounce": "fl oz",
    "stick": "stick",
    "pint": "pint", "pt": "pint",
    "quart": "quart", "qt": "quart",
    "gallon": "gallon", "gal": "gallon"
}

# Metric conversion factors
CONVERSIONS = {
    "cup": ("ml", 240),
    "tablespoon": ("ml", 15),
    "teaspoon": ("ml", 5),
    "fl oz": ("ml", 29.57),
    "oz": ("g", 28.35),
    "lb": ("g", 453.6),
    "stick": ("g", 113),
    "pint": ("ml", 473.18),
    "quart": ("ml", 946.35),
    "gallon": ("ml", 3785.41),
}

def parse_quantity(value):
    if isinstance(value, (int, float)):
        return float(value)

    val = str(value).strip().lower()

    # Handle whole + fraction (e.g. 2 1/2)
    if " " in val:
        parts = val.split()
        try:
            return float(parts[0]) + float(Fraction(parts[1]))
        except:
            pass

    # Handle pure fraction
    try:
        return float(Fraction(val))
    except:
        pass

    # Handle unicode fractions
    val = val.replace("½", "1/2").replace("¼", "1/4").replace("¾", "3/4")
    try:
        return float(Fraction(val))
    except:
        pass

    # Handle word numbers
    return WORD_NUMBERS.get(val, None)

def normalize_unit(unit_raw):
    unit = unit_raw.lower().strip().replace(".", "").rstrip("s")
    return UNIT_MAP.get(unit, None)

def split_quantity_from_unit(raw_unit):
    """
    Try to split numeric prefix from unit string, like '2 tablespoons' or '½ cup'
    """
    raw_unit = raw_unit.strip().lower()
    match = re.match(r"([\d\/\s¼½¾]+)\s*(.+)", raw_unit)
    if match:
        quantity_part = match.group(1).strip()
        unit_part = match.group(2).strip()
        parsed_qty = parse_quantity(quantity_part)
        normalized_unit = normalize_unit(unit_part)
        return parsed_qty, normalized_unit
    return None, None

def convert_units_to_metric(meal_plan: dict) -> dict:
    for meal in meal_plan.get("meals", []):
        for ing in meal.get("ingredients", []):
            raw_unit = ing.get("unit", "").strip()
            raw_qty = ing.get("quantity")

            # Case 1: normal quantity + unit
            norm_qty = parse_quantity(raw_qty)
            norm_unit = normalize_unit(raw_unit)

            # Case 2: GPT jammed both into unit (e.g. '2 tablespoons')
            if norm_unit not in CONVERSIONS or norm_qty is None:
                fallback_qty, fallback_unit = split_quantity_from_unit(raw_unit)
                if fallback_qty is not None and fallback_unit in CONVERSIONS:
                    norm_qty = fallback_qty
                    norm_unit = fallback_unit

            if norm_unit in CONVERSIONS and norm_qty is not None:
                metric_unit, factor = CONVERSIONS[norm_unit]
                ing["quantity"] = round(norm_qty * factor, 2)
                ing["unit"] = metric_unit
            else:
                print(f"⚠️ Skipped unit conversion for: {raw_qty} {raw_unit}")

    return meal_plan
