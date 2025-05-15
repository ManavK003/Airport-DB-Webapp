import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

cur = conn.cursor()
cur.execute("""
    SELECT * FROM runways
    WHERE airport_code ILIKE '%JFK%'
""")
rows = cur.fetchall()

print(f"🔍 Found {len(rows)} runways for JFK variants:\n")
for row in rows:
    print(row)

conn.close()