from psycopg2.extras import RealDictCursor
from utils.db import get_db_connection

def fetch_structured_ingredients(matches: list[dict]) -> list[dict]:
    if not matches:
        return []

    names = list({m["matched_name"] for m in matches})
    placeholders = ', '.join(['%s'] * len(names))
    query = f"""
        SELECT * FROM ingredientsdb
        WHERE name IN ({placeholders})
    """

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(query, names)
        raw_results = cursor.fetchall()
        record_lookup = {rec["name"].lower(): rec for rec in raw_results}

        structured = []
        for m in matches:
            rec = record_lookup.get(m["matched_name"].lower())
            if rec:
                structured.append({
                    **m,
                    "record": rec
                })

        return structured

    finally:
        cursor.close()
        conn.close()

