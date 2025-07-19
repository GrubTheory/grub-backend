from rapidfuzz import process, fuzz
from .db import get_db_connection

_ingredient_cache = []

def load_ingredient_names():
    global _ingredient_cache
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT name FROM ingredientsdb")
        rows = cur.fetchall()
        _ingredient_cache = [row[0] for row in rows]
    conn.close()

def fuzzy_match_ingredient(ingredient: str, threshold: int = 80) -> dict:
    if not _ingredient_cache:
        raise ValueError("Ingredient cache not loaded")

    result = process.extractOne(
        ingredient,
        _ingredient_cache,
        scorer=fuzz.token_sort_ratio
    )

    if result and result[1] >= threshold:
        return {
            "original": ingredient,
            "matched": result[0],
            "score": result[1]
        }
    else:
        return {
            "original": ingredient,
            "matched": None,
            "score": result[1] if result else 0
        }
