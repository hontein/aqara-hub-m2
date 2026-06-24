import os
import sqlite3
from datetime import datetime, timedelta

from flask import Flask, jsonify, render_template, g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sensors.db")


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    @app.before_request
    def before_request():
        g.db = get_db()

    @app.teardown_request
    def teardown_request(exception):
        db = getattr(g, "db", None)
        if db is not None:
            db.close()

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/sensors")
    def api_sensors():
        """
        Возвращает последние показания датчика в виде временного ряда.
        Пока что данные берутся из локальной SQLite.
        """
        conn = g.db
        cursor = conn.cursor()
        cursor.execute(
            "SELECT timestamp, temperature, humidity FROM sensor_data ORDER BY timestamp ASC"
        )
        rows = cursor.fetchall()

        data = [
            {
                "timestamp": row[0],
                "temperature": row[1],
                "humidity": row[2],
            }
            for row in rows
        ]

        return jsonify({"data": data})

    return app


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(with_demo_data=True):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            temperature REAL,
            humidity REAL
        )
        """
    )

    if with_demo_data:
        cursor.execute("SELECT COUNT(*) FROM sensor_data")
        count = cursor.fetchone()[0]
        if count == 0:
            now = datetime.utcnow()
            for i in range(0, 24 * 6):
                t = now - timedelta(minutes=10 * (24 * 6 - i))
                temperature = 20.0 + 3.0 * (i % 10) / 10.0
                humidity = 40.0 + 10.0 * ((i * 3) % 10) / 10.0
                cursor.execute(
                    "INSERT INTO sensor_data (timestamp, temperature, humidity) VALUES (?, ?, ?)",
                    (t.isoformat(), temperature, humidity),
                )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db(with_demo_data=True)
    else:
        # На всякий случай убедимся, что таблица есть
        init_db(with_demo_data=False)

    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=False)

