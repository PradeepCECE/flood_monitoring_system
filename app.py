from __future__ import annotations
from db import init_db
from scheduler_jobs import start_scheduler
from flask import Flask, jsonify, render_template
from services.weather_service import fetch_weather_snapshot
from config import DASHBOARD_REFRESH_MS, RAIN_PRESENT_3H_MM

app = Flask(__name__)

def build_dashboard_payload():
# Fetch live weather data from OpenWeather
    latest = fetch_weather_snapshot()

    prediction = None
    daily_summaries = []
    alerts = []

    rain_detected = bool(latest and latest["rainfall_mm"] >= RAIN_PRESENT_3H_MM)

    return {
    "latest_weather": latest,
    "prediction": prediction,
    "daily_summaries": daily_summaries,
    "alerts": alerts,
    "flags": {
        "rain_detected": rain_detected,
        "flood_alert_sent": False
    },
    "ui": {
        "refresh_ms": DASHBOARD_REFRESH_MS
    }
}

@app.route("/")
def index():
    return render_template("index.html", refresh_ms=DASHBOARD_REFRESH_MS)

@app.route("/api/status")
def api_status():
    return jsonify(build_dashboard_payload())

@app.route("/api/weather")
def api_weather():
    weather = fetch_weather_snapshot()
    return jsonify(weather)

if __name__ == "__main__":
    init_db()
    start_scheduler()
    port =int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)