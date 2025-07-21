import csv
import time
import requests
import os

API_KEY = "p21qHgLnWOtCs31jNZLfhgJC34GDXi5c7ZPY3qj2"
CSV_PATH = os.path.join(os.path.dirname(__file__), "ingredients.csv")

INGREDIENTS = [
     "scallion", "shallot", "parsnip", "turnip", "rutabaga", "bok choy", "chard", "endive",
    "watercress", "fennel", "artichoke", "okra", "horseradish", "jalapeno", "habanero",
    "chili pepper", "bell pepper", "green chili", "chili flakes", "pickles", "capers",
    "olives", "sun-dried tomato", "tomato paste", "tomato sauce", "anchovy paste",
    "cream cheese", "ricotta", "brie", "feta", "blue cheese", "goat cheese",
    "almond", "walnut", "pecan", "cashew", "hazelnut", "pistachio", "pine nut",
    "chia seeds", "flaxseeds", "hemp seeds", "pumpkin seeds", "sunflower seeds",
    "coconut", "coconut milk", "coconut cream", "coconut oil", "evaporated milk", "condensed milk",
    "molasses", "agave syrup", "maple syrup", "date syrup",
    "nutmeg", "cinnamon", "clove", "cardamom", "cumin", "coriander", "turmeric", "paprika",
    "smoked paprika", "oregano", "thyme", "rosemary", "sage", "dill", "basil", "parsley", "mint",
    "bay leaf", "curry powder", "five spice", "za'atar", "tahini",
    "miso", "mirin", "sake", "wasabi", "nori", "kimchi", "sauerkraut",
    "anchovy", "octopus", "scallop", "eel", "lobster",
    "duck egg", "quail egg",
    "gluten-free flour", "almond flour", "coconut flour", "spelt flour", "buckwheat flour",
    "polenta", "grits", "millet", "freekeh", "teff", "amaranth",
    "rice paper", "wonton wrapper", "phyllo dough", "puff pastry",
    "stock", "broth", "bouillon", "gelato", "sorbet", "egg"

]

# Use accurate USDA nutrient IDs
NUTRIENT_IDS = {
    1003: "protein",    # Protein
    1004: "fat",        # Total lipid (fat)
    1005: "carbs",      # Carbohydrate, by difference
    2048: "calories"    # Energy (Atwater Specific Factors)
}

def get_fdc_ids(ingredient_name):
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "query": ingredient_name,
        "dataType": "Foundation",
        "api_key": API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    results = response.json().get("foods", [])
    return [(r["fdcId"], r["description"]) for r in results]

def get_macros(fdc_id):
    url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}?api_key={API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    macros = {"protein": None, "fat": None, "carbs": None, "calories": None}
    for nutrient in data.get("foodNutrients", []):
        nutrient_info = nutrient.get("nutrient", {})
        n_id = nutrient_info.get("id")
        n_name = nutrient_info.get("name", "").lower()
        amount = nutrient.get("amount")

        if amount is None:
            continue  # Skip if no value

        # Match by ID (preferred)
        if n_id in NUTRIENT_IDS:
            key = NUTRIENT_IDS[n_id]
            macros[key] = round(amount, 1)

        # Fallback to name-based match
        elif "protein" in n_name and macros["protein"] is None:
            macros["protein"] = round(amount, 1)
        elif "fat" in n_name and macros["fat"] is None:
            macros["fat"] = round(amount, 1)
        elif "carbohydrate" in n_name and macros["carbs"] is None:
            macros["carbs"] = round(amount, 1)
        elif "energy" in n_name and macros["calories"] is None and n_id == 2048:
            macros["calories"] = round(amount, 1)

    if None in macros.values():
        raise ValueError("Missing macro data")
    return macros

def generate_csv():
    file_exists = os.path.isfile(CSV_PATH)
    
    with open(CSV_PATH, mode="a", encoding="utf-8", newline="") as f:
        fieldnames = ["name", "calories", "protein", "fat", "carbs", "unit_of_measure", "qty"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()

        for ingredient in INGREDIENTS:
            try:
                print(f"\n🔍 Searching: {ingredient}")
                fdc_list = get_fdc_ids(ingredient)
                if not fdc_list:
                    print("❌ No results")
                    continue

                for fdc_id, name in fdc_list:
                    try:
                        macros = get_macros(fdc_id)
                        row = {
                            "name": name,
                            "calories": macros["calories"],
                            "protein": macros["protein"],
                            "fat": macros["fat"],
                            "carbs": macros["carbs"],
                            "unit_of_measure": "oz",
                            "qty": 3.5
                        }
                        writer.writerow(row)
                        print(f"✅ Saved: {name}")
                    except Exception as e:
                        print(f"⚠️ Skipped '{name}': {e}")
                    time.sleep(1)
            except Exception as e:
                print(f"🔥 Total fail on '{ingredient}': {e}")
                continue

    print("\n✅ All done. Entries appended to CSV.")

if __name__ == "__main__":
    generate_csv()
