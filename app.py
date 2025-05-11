from flask import Flask, request, jsonify, render_template
import psycopg2
from dotenv import load_dotenv
import os



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
    city = request.args.get('city', '').strip()


    if not city:
        # If city is empty, don't query the DB – return empty list or message
        return jsonify([])

    cur = conn.cursor()
    try:
        cur.execute("ROLLBACK")
        cur.execute("SELECT * FROM airports WHERE country ILIKE %s LIMIT 50", (f"%{city}%",))
        results = cur.fetchall()
        print("RESULTS:", results)
        columns = [desc[0] for desc in cur.description]
        return jsonify([dict(zip(columns, row)) for row in results])
    except Exception as e:
        print("ERROR in /api/airports/search:", e)
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
