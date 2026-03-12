from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from config import COLLECTION_INTERVAL_HOURS, RAIN_PRESENT_3H_MM
from services.weather_service import collect_and_store_weather
from services.aggregation_service import summarize_day, yesterday_utc
from services.risk_engine import run_risk_prediction
from services.email_service import send_flood_alert

scheduler = BackgroundScheduler(timezone="UTC")


def collection_job():

    weather = collect_and_store_weather()

    if not weather:
        return

    # Update summary continuously
    summarize_day(weather["recorded_at"][:10])


def daily_prediction_job():

    # Create summary for yesterday
    day = yesterday_utc()

    summarize_day(day)

    result = run_risk_prediction()

    if not result:
        print("Sliding window not ready")
        return

    probability, risk_level, reason = result

    if probability >= 0.5:

        send_flood_alert(
            day,
            probability,
            0,
            reason,
        )


def start_scheduler():

    if scheduler.running:
        return

    scheduler.add_job(
        collection_job,
        "interval",
        hours=COLLECTION_INTERVAL_HOURS,
        id="weather_collection",
        replace_existing=True,
    )

    scheduler.add_job(
        daily_prediction_job,
        "cron",
        hour=0,
        minute=5,
        id="daily_prediction",
        replace_existing=True,
    )

    scheduler.start()