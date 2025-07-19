from psycopg2.extras import RealDictCursor
from utils.db import get_db_connection

def fetch_structured_ingredients(matches: list[dict]) -> list[dict]:
    if not matches:
        return []

    # Filter out unmatched
    matched_names = [m["matched_name"] for m in matches if m["matched_name"]]
    if not matched_names:
        return []

    placeholders = ', '.join(['%s'] * len(matched_names))
    query = f"""
        SELECT * FROM ingredientsdb
        WHERE name IN ({placeholders})
    """

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(query, matched_names)
        raw_results = cursor.fetchall()
        record_lookup = {rec["name"].lower(): rec for rec in raw_results}

        structured = []
        for m in matches:
            matched_name = m.get("matched_name")
            if not matched_name:
                continue
            rec = record_lookup.get(matched_name.lower())
            if rec:
                structured.append({
                    **m,
                    "record": rec
                })

        return structured

    finally:
        cursor.close()
        conn.close()
