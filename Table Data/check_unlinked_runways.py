import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

def find_unlinked_runways():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        query = """
            SELECT r.*
            FROM runways r
            LEFT JOIN airports a
              ON r.airport_code = a.iata OR r.airport_code = a.icao
            WHERE a.iata IS NULL AND a.icao IS NULL;
        """
        cur.execute(query)
        unlinked = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

        if not unlinked:
            print("✅ All runways are linked to valid airports.")
        else:
            print(f"❌ {len(unlinked)} runways are NOT linked to any airport:")
            for row in unlinked:
                print(dict(zip(columns, row)))

    except Exception as e:
        print("Error:", e)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    find_unlinked_runways()