import psycopg2
import csv
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

CSV_FILE = "Airline_Delay_Cause.csv"

def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

def load_airline_delays():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        cur.execute("DROP TABLE IF EXISTS airline_statistics CASCADE;")
        cur.execute("""
            CREATE TABLE airline_statistics (
                carrier_code TEXT,
                carrier_name TEXT,
                airport_code TEXT,
                airport_name TEXT,
                total_flights INTEGER,
                on_time_flights INTEGER,
                delayed_flights INTEGER,
                cancelled_flights INTEGER,
                diverted_flights INTEGER,
                weather_delays INTEGER,
                carrier_delays INTEGER,
                nas_delays INTEGER,
                late_aircraft_delays INTEGER
            );
        """)

        with open(CSV_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total = safe_float(row['arr_flights'])
                delayed = safe_float(row['arr_del15'])
                cancelled = safe_float(row['arr_cancelled'])
                diverted = safe_float(row['arr_diverted'])
                on_time = total - delayed - cancelled - diverted

                cur.execute("""
                    INSERT INTO airline_statistics (
                        carrier_code, carrier_name, airport_code, airport_name,
                        total_flights, on_time_flights, delayed_flights,
                        cancelled_flights, diverted_flights, weather_delays,
                        carrier_delays, nas_delays, late_aircraft_delays
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    row['carrier'],
                    row['carrier_name'],
                    row['airport'],
                    row['airport_name'],
                    int(total),
                    int(on_time),
                    int(delayed),
                    int(cancelled),
                    int(diverted),
                    int(safe_float(row['weather_delay'])),
                    int(safe_float(row['carrier_delay'])),
                    int(safe_float(row['nas_delay'])),
                    int(safe_float(row['late_aircraft_delay']))
                ))

        conn.commit()
        print("✅ Airline statistics loaded successfully.")

    except Exception as e:
        print("❌ Error:", e)

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    load_airline_delays()