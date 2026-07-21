import os
import sqlite3
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "urls.db")

frontend_url = os.getenv("FRONTEND_URL", "*")
allowed_origins = [origin.strip() for origin in frontend_url.split(",") if origin.strip()]
CORS(app, resources={r"/*": {"origins": allowed_origins}})


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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
    conn.execute("INSERT INTO urls (url) VALUES (?)", (url,))
    conn.commit()
    rows = conn.execute("SELECT url FROM urls ORDER BY id DESC").fetchall()
    conn.close()

    return jsonify({"status": "ok", "urls": [row["url"] for row in rows]})


@app.get("/urls")
def get_urls():
    conn = get_db()
    rows = conn.execute("SELECT url FROM urls ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([row["url"] for row in rows])


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(debug=True, host="0.0.0.0", port=port)
