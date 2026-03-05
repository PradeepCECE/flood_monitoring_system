from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from config import COLLECTION_INTERVAL_HOURS, RAIN_PRESENT_3H_MM
from services.weather_service import collect_and_store_weather
from services.aggregation_service import summarize_day, yesterday_utc, get_recent_daily_summaries
from services.risk_engine import run_risk_prediction
from services.email_service import send_rain_update, send_flood_alert

scheduler = BackgroundScheduler(timezone="UTC")


def collection_job():
    weather = collect_and_store_weather()

    if not weather:
        return

    day = weather["recorded_at"][:10]

    # Send rain notification
    if weather["rainfall_mm"] >= RAIN_PRESENT_3H_MM:
        send_rain_update(day, weather["rainfall_mm"])

    # Update today's summary
    summarize_day(day)


def daily_prediction_job():
    target_day = yesterday_utc()

    summary = summarize_day(target_day)
    if not summary:
        return

    result = run_risk_prediction()

    if not result:
        return

    probability, risk_level, reason = result

    if risk_level in {"HIGH", "MODERATE"}:
        window = get_recent_daily_summaries(3)
        rolling_total = sum(day["total_rainfall_mm"] for day in window)

        send_flood_alert(
            target_day,
            probability,
            rolling_total,
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
        hour=23,
        minute=59,
        id="daily_prediction",
        replace_existing=True,
    )

    scheduler.start()