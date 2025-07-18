import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import random
from typing import Dict

# Load DB URL
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def fetch_random_ingredient_by_category(category: str) -> Dict:
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            "SELECT * FROM ingredientsDB WHERE category = %s;",
            (category,)
        )
        results = cursor.fetchall()
        if not results:
            raise ValueError(f"No ingredients found for category: {category}")
        return random.choice(results)
    finally:
        cursor.close()
        conn.close()
