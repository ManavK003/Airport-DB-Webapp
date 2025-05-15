import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

cur = conn.cursor()
cur.execute("SELECT DISTINCT airport_code FROM airline_statistics WHERE airport_code ILIKE 'JFK';")
rows = cur.fetchall()

if rows:
    print("JFK found:", rows)
else:
    print("JFK not found in airline_statistics.")

cur.close()
conn.close()