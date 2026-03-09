from __future__ import annotations

from flask import Flask, jsonify, render_template

from config import DASHBOARD_REFRESH_MS, RAIN_PRESENT_3H_MM
from db import init_db
from scheduler_jobs import collection_job, daily_prediction_job, start_scheduler
from services.aggregation_service import (
    get_latest_hourly_record,
    get_latest_prediction,
    get_recent_alerts,
    get_recent_daily_summaries,
)

app = Flask(__name__)

# START DATABASE + SCHEDULER WHEN APP LOADS
init_db()
start_scheduler()


def build_dashboard_payload():
    latest = get_latest_hourly_record()
    prediction = get_latest_prediction()
    daily_summaries = list(reversed(get_recent_daily_summaries(3)))
    alerts = get_recent_alerts(5)

    rain_detected = bool(latest and latest['rainfall_mm'] >= RAIN_PRESENT_3H_MM)
    flood_alert_sent = any(
        alert['alert_type'] == 'FLOOD_ALERT' and alert['sent'] == 1 for alert in alerts
    )

    return {
        'latest_weather': latest,
        'prediction': prediction,
        'daily_summaries': daily_summaries,
        'alerts': alerts,
        'flags': {
            'rain_detected': rain_detected,
            'flood_alert_sent': flood_alert_sent,
        },
        'ui': {
            'refresh_ms': DASHBOARD_REFRESH_MS,
        },
    }


@app.route('/')
def index():
    return render_template('index.html', refresh_ms=DASHBOARD_REFRESH_MS)


@app.route('/api/status')
def api_status():
    return jsonify(build_dashboard_payload())


@app.route('/api/manual/collect', methods=['POST'])
def manual_collect():
    collection_job()
    return jsonify({'ok': True})


@app.route('/api/manual/predict', methods=['POST'])
def manual_predict():
    daily_prediction_job()
    return jsonify({'ok': True})

from services.weather_service import fetch_weather_snapshot

@app.route("/api/weather")
def api_weather():
    weather = fetch_weather_snapshot()
    return jsonify(weather)