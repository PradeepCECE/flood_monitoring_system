from typing import Dict, List
from services.aggregation_service import get_recent_daily_summaries
from db import execute


def run_risk_prediction():

    # Get latest 3 days
    days = get_recent_daily_summaries(3)

    if len(days) < 3:
        return None

    total_rain = sum(d["total_rainfall_mm"] for d in days)

    # If no rain in last 3 days → probability 0
    if total_rain == 0:
        probability = 0
        risk_level = "LOW"
        reason = "No rainfall detected in last 3 days"

    else:

        avg_humidity = sum(d["avg_humidity_pct"] for d in days) / 3
        avg_pressure = sum(d["avg_pressure_hpa"] for d in days) / 3

        rain_score = min(total_rain / 200, 1)
        humidity_score = avg_humidity / 100
        pressure_score = (1013 - avg_pressure) / 50

        probability = (rain_score * 0.6) + (humidity_score * 0.25) + (pressure_score * 0.15)

        probability = max(0, min(probability, 1))

        if probability >= 0.5:
            risk_level = "HIGH"
        elif probability >= 0.3:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"

        reason = (
            f"Rainfall={total_rain:.1f}mm, "
            f"Humidity={avg_humidity:.1f}%, "
            f"Pressure={avg_pressure:.1f}hPa"
        )

    latest_day = days[0]["day"]

    execute(
        """
        INSERT INTO daily_predictions
        (day, risk_probability, risk_level, reason, window_ready)
        VALUES (?, ?, ?, ?, 1)
        ON CONFLICT(day) DO UPDATE SET
            risk_probability=excluded.risk_probability,
            risk_level=excluded.risk_level,
            reason=excluded.reason,
            window_ready=1
        """,
        (latest_day, probability, risk_level, reason),
    )

    return probability, risk_level, reason