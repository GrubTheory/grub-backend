from psycopg2.extras import RealDictCursor
from utils.db import get_db_connection

def fetch_ingredients_by_name(names: list[str]) -> list[dict]:
    if not names:
        return []

    placeholders = ', '.join(['%s'] * len(names))
    query = f"""
        SELECT * FROM ingredientsdb
        WHERE name IN ({placeholders})
    """

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(query, names)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
