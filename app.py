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

FLIGHTAWARE_API_KEY = os.getenv("FLIGHTAWARE_API_KEY")

@app.route('/api/delays/by-airport')
def get_delays_by_airport():
    code = request.args.get("code", "").upper()
    if not code:
        return jsonify({"error": "Airport code is required"}), 400

    url = f"https://aeroapi.flightaware.com/aeroapi/airports/{code}/delays"
    headers = {
        "x-apikey": FLIGHTAWARE_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch delays: {str(e)}"}), 500

@app.route('/api/airportboards/<code>')
def get_airport_boards(code):
    flight_type = request.args.get("type", "arrivals")  # 'arrivals' or 'departures'
    how_many = request.args.get("howMany", 10)

    url = f"https://aeroapi.flightaware.com/aeroapi/airports/{code}/flights"
    params = {
        "type": flight_type,
        "howMany": how_many
    }
    headers = {
        "x-apikey": FLIGHTAWARE_API_KEY
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if flight_type == "arrivals":
            return jsonify({"flights": data.get("arrivals", [])})
        else:
            return jsonify({"flights": data.get("departures", [])})
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/flight_status/<flight_number>')
def get_flight_status(flight_number):
    headers = {
        "x-apikey": FLIGHTAWARE_API_KEY
    }
    url = f"https://aeroapi.flightaware.com/aeroapi/flights/{flight_number.upper()}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        flights = response.json().get("flights", [])
        if not flights:
            return jsonify({"error": "No data found for this flight."}), 404
        return jsonify(flights[0])  # return the most recent flight record
    except requests.RequestException as e:
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

@app.route('/api/airport_coords')
def get_airport_coords():
    code = request.args.get('code', '').upper()
    if not code:
        return jsonify({"error": "Missing airport code"}), 400

    cur = conn.cursor()
    cur.execute("""
        SELECT latitude, longitude FROM airports
        WHERE iata = %s OR icao = %s
        LIMIT 1
    """, (code, code))
    result = cur.fetchone()
    if result:
        return jsonify({"lat": result[0], "lon": result[1]})
    return jsonify({"error": "Airport not found"}), 404

@app.route('/api/airport_info/<code>')
def airport_info(code):
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT name, city, country, iata, icao, latitude, longitude
            FROM airports
            WHERE iata = %s OR icao = %s
            LIMIT 1
        """, (code.upper(), code.upper()))
        airport = cur.fetchone()

        if not airport:
            return jsonify({"error": "Airport not found"}), 404

        # Extract IATA and ICAO codes
        airport_keys = [desc[0] for desc in cur.description]
        airport_data = dict(zip(airport_keys, airport))
        iata_code = airport_data["iata"]
        icao_code = airport_data["icao"]

        # Fetch runways using both IATA and ICAO
        cur.execute("""
            SELECT runway_id, length_ft, width_ft, surface_type
            FROM runways
            WHERE airport_code = %s OR airport_code = %s
        """, (iata_code, icao_code))
        runways = cur.fetchall()
        runways_data = [
            dict(zip([desc[0] for desc in cur.description], row))
            for row in runways
        ]
        airport_data["runways"] = runways_data

        return jsonify(airport_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

@app.route('/api/airline_stats')
def airline_stats():
    airport_code = request.args.get('airport', '').upper()
    cur = conn.cursor()

    try:
        if airport_code:
            cur.execute("""
                SELECT carrier_name, airport_code,
                       total_flights,
                       on_time_flights,
                       ROUND((on_time_flights * 100.0) / NULLIF(total_flights, 0), 2) AS on_time_pct
                FROM airline_statistics
                WHERE airport_code = %s
                ORDER BY on_time_pct DESC
                LIMIT 10
            """, (airport_code,))
        else:
            cur.execute("""
                SELECT carrier_name, airport_code,
                       total_flights,
                       on_time_flights,
                       ROUND((on_time_flights * 100.0) / NULLIF(total_flights, 0), 2) AS on_time_pct
                FROM airline_statistics
                ORDER BY on_time_pct DESC
                LIMIT 10
            """)

        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return jsonify([dict(zip(columns, row)) for row in rows])
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
