from flask import Flask, request, jsonify, render_template
import psycopg2
from dotenv import load_dotenv
import os
import requests

import time



load_dotenv()
app = Flask(__name__)

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/airports/search')
def search_airports():
    query = request.args.get('city', '').strip()
    if not query:
        return jsonify([])

    cur = conn.cursor()
    try:
        cur.execute("ROLLBACK")  # reset if previous error occurred
        cur.execute("""
            SELECT * FROM airports
            WHERE city ILIKE %s OR country ILIKE %s OR iata ILIKE %s OR icao ILIKE %s
            LIMIT 50
        """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
        
        results = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return jsonify([dict(zip(columns, row)) for row in results])
    except Exception as e:
        print(" ERROR in /api/airports/search:", e)
        cur.execute("ROLLBACK")
        return jsonify({"error": str(e)}), 500




@app.route('/api/delays/top')
def top_delays():
    cur = conn.cursor()
    cur.execute("""
        SELECT f.flight_number, d.delay_minutes, f.departure_airport, f.arrival_airport
        FROM delays d
        JOIN flights f ON d.flight_id = f.id
        ORDER BY d.delay_minutes DESC
        LIMIT 10
    """)
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    return jsonify([dict(zip(columns, row)) for row in results])

@app.route('/api/planes/live')
def live_planes():
    r = requests.get("https://opensky-network.org/api/states/all")
    return jsonify(r.json())

@app.route('/api/airport_activity/<code>')
def airport_activity(code):
    
    cur = conn.cursor()
    cur.execute("""
        SELECT latitude, longitude
        FROM airports
        WHERE iata = %s OR icao = %s
        LIMIT 1
    """, (code.upper(), code.upper()))
    result = cur.fetchone()
    if result:
        lat, lon = result
    else:
        lat, lon = 20.0, 0.0  # fallback

    
    try:
        r = requests.get("https://opensky-network.org/api/states/all")
        states = r.json().get("states", [])
    except:
        return jsonify({
            "arrivals": [],
            "departures": [],
            "location": {"lat": lat, "lon": lon}
        })

    #  Filter planes near the airport
    def is_near(flight):
        try:
            return (
                flight[5] is not None and flight[6] is not None and  # lon, lat
                abs(flight[5] - lon) < 1.5 and
                abs(flight[6] - lat) < 1.5
            )
        except:
            return False

    nearby_flights = [f for f in states if is_near(f)]

    
    formatted = [
        {
            "icao24": f[0],
            "callsign": f[1].strip() if f[1] else None,
            "origin_country": f[2],
            "longitude": f[5],
            "latitude": f[6],
            "baro_altitude": f[7],
            "velocity": f[9],
        }
        for f in nearby_flights
    ]

    return jsonify({
        "arrivals": formatted,  
        "departures": [],
        "location": {"lat": lat, "lon": lon}
    })



@app.route('/api/track/<icao24>')
def track_flight(icao24):
    now = int(time.time())
    url = f"https://opensky-network.org/api/tracks/all?icao24={icao24.lower()}&time={now}"

    try:
        res = requests.get(url)
        res.raise_for_status()  
        return jsonify(res.json())
    except requests.exceptions.RequestException as e:
        print(f"OpenSky API error for {icao24}: {e}")
        return jsonify({"error": "Failed to retrieve flight data."}), 500
    except ValueError:
        print(f"Invalid JSON returned for {icao24}")
        return jsonify({"error": "No valid flight data returned."}), 500

@app.route('/api/lookup_icao24/<callsign>')
def lookup_icao24(callsign):
    try:
        r = requests.get("https://opensky-network.org/api/states/all")
        r.raise_for_status()
        states = r.json().get("states", [])
        for s in states:
            if s[1] and s[1].strip().lower() == callsign.lower():
                return jsonify({"icao24": s[0]})
        return jsonify({"error": "Callsign not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/landings/stats')
def landing_stats():
    cur = conn.cursor()
    cur.execute("""
        SELECT airport_code, runway, COUNT(*) as total_landings
        FROM landings
        GROUP BY airport_code, runway
        ORDER BY total_landings DESC
        LIMIT 10
    """)
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    return jsonify([dict(zip(columns, row)) for row in results])


@app.route('/api/weather/by-airport')
def weather_by_airport():
    code = request.args.get('code', '')
    cur = conn.cursor()
    cur.execute("SELECT * FROM weather_conditions WHERE airport_code = %s ORDER BY recorded_at DESC LIMIT 1", (code,))
    result = cur.fetchone()
    columns = [desc[0] for desc in cur.description]
    return jsonify(dict(zip(columns, result))) if result else jsonify({})


@app.route('/api/pilots/<pilot_id>')
def get_pilot(pilot_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM pilots WHERE id = %s", (pilot_id,))
    result = cur.fetchone()
    columns = [desc[0] for desc in cur.description]
    return jsonify(dict(zip(columns, result))) if result else jsonify({"error": "Pilot not found"})


if __name__ == '__main__':
    app.run(debug=True)
