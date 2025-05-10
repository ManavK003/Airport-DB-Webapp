from flask import Flask, jsonify, render_template
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

@app.route('/api/airports')
def get_airports():
    cur = conn.cursor()
    cur.execute("SELECT * FROM airports LIMIT 50;")
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    data = [dict(zip(colnames, row)) for row in rows]
    return jsonify(data)

@app.route('/api/delays/top')
def get_top_delays():
    cur = conn.cursor()
    cur.execute("SELECT * FROM delays ORDER BY delay_minutes DESC LIMIT 10;")
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    data = [dict(zip(colnames, row)) for row in rows]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
