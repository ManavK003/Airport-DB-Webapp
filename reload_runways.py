import psycopg2
import csv
from dotenv import load_dotenv
import os

load_dotenv()

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

CSV_FILE = "Filtered_Runways_Matching_Real_Airports.csv"  

def load_runways():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        # Drop existing runways table
        cur.execute("DROP TABLE IF EXISTS runways CASCADE;")

        # Recreate runways table
        cur.execute("""
            CREATE TABLE runways (
                runway_id INTEGER PRIMARY KEY,
                airport_code VARCHAR(10),
                length_ft INTEGER,
                width_ft INTEGER,
                surface_type VARCHAR(100)
            );
        """)

        # Insert data from CSV
        with open(CSV_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cur.execute("""
                    INSERT INTO runways (runway_id, airport_code, length_ft, width_ft, surface_type)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    int(row['runway_id']),
                    row['airport_code'],
                    int(float(row['length_ft'])) if row['length_ft'] else None,
                    int(float(row['width_ft'])) if row['width_ft'] else None,
                    row['surface_type']
                ))

        conn.commit()
        print("✅ Runways table loaded successfully.")

    except Exception as e:
        print("❌ Error:", e)

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    load_runways()