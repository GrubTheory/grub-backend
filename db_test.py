import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT version();")
    db_version = cur.fetchone()
    print("Connected. PostgreSQL version:", db_version)

    cur.close()
    conn.close()
except Exception as e:
    print("Connection failed:", e)
