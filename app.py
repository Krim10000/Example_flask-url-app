import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")

frontend_url = os.getenv("FRONTEND_URL", "*")
allowed_origins = [origin.strip() for origin in frontend_url.split(",") if origin.strip()]
CORS(app, resources={r"/*": {"origins": allowed_origins}})


def init_db():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is not set")

    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS urls (
                    id SERIAL PRIMARY KEY,
                    url TEXT NOT NULL
                )
                """
            )
            conn.commit()
    finally:
        conn.close()


init_db()


def get_db():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is not set")

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    return conn


@app.get("/")
def index():
    return send_from_directory(os.path.dirname(__file__), "index.html")


@app.post("/submit")
def submit_url():
    url = request.form.get("url", "").strip()
    if not url:
        return jsonify({"status": "error", "message": "La URL no puede estar vacía."}), 400

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO urls (url) VALUES (%s)", (url,))
            conn.commit()
            cur.execute("SELECT url FROM urls ORDER BY id DESC")
            rows = cur.fetchall()
    finally:
        conn.close()

    return jsonify({"status": "ok", "urls": [row[0] for row in rows]})


@app.get("/urls")
def get_urls():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT url FROM urls ORDER BY id DESC")
            rows = cur.fetchall()
    finally:
        conn.close()
    return jsonify([row[0] for row in rows])


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(debug=True, host="0.0.0.0", port=port)
