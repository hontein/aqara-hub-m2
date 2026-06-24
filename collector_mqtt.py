import os
import sqlite3
import json
from datetime import datetime

import paho.mqtt.client as mqtt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sensors.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn


def ensure_schema():
    conn = get_db()
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
    conn.commit()
    conn.close()


def on_connect(client, userdata, flags, rc):
    print("MQTT connected with result code %s" % rc)
    # TODO: заменить топики на реальные после включения MQTT на Aqara Hub M2
    # Примеры:
    #   aqara/+/sensor
    #   zigbee/+/sensor
    client.subscribe("aqara/+/sensor")
    client.subscribe("zigbee/+/sensor")


def save_reading(temperature, humidity):
    ts = datetime.utcnow().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sensor_data (timestamp, temperature, humidity) VALUES (?, ?, ?)",
        (ts, temperature, humidity),
    )
    conn.commit()
    conn.close()
    print("Saved reading: %s °C, %s %%" % (temperature, humidity))


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print("MQTT message on %s: %s" % (msg.topic, payload))
    try:
        data = json.loads(payload)
    except ValueError:
        return

    # Ожидаем, что в JSON будут поля temperature / humidity.
    temperature = data.get("temperature")
    humidity = data.get("humidity")
    if temperature is None and humidity is None:
        return

    save_reading(temperature, humidity)


def main():
    ensure_schema()

    mqtt_host = os.environ.get("AQARA_MQTT_HOST", "192.168.0.131")
    mqtt_port = int(os.environ.get("AQARA_MQTT_PORT", "1883"))

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()

