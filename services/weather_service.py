from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional
import requests

from config import (
    OPENWEATHER_API_KEY,
    OPENWEATHER_LAT,
    OPENWEATHER_LON,
    OPENWEATHER_UNITS,
    RAIN_PRESENT_3H_MM,
)

from db import execute

FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def fetch_weather_snapshot() -> Optional[Dict]:

    params = {
        "lat": OPENWEATHER_LAT,
        "lon": OPENWEATHER_LON,
        "appid": OPENWEATHER_API_KEY,
        "units": OPENWEATHER_UNITS,
        "cnt": 1,
    }

    try:
        response = requests.get(FORECAST_URL, params=params, timeout=20)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        print(f"Weather API error: {exc}")
        return None

    return _extract_fields(payload)


def _extract_fields(payload: Dict) -> Optional[Dict]:

    entries = payload.get("list", [])
    if not entries:
        return None

    first = entries[0]

    main = first.get("main", {})
    wind = first.get("wind", {})
    clouds = first.get("clouds", {})
    rain = first.get("rain", {})

    rainfall_mm = float(rain.get("3h", 0.0))

    timestamp = datetime.fromtimestamp(first["dt"], tz=timezone.utc).isoformat()

    return {
        "recorded_at": timestamp,
        "source_slot": first.get("dt_txt", timestamp),
        "rainfall_mm": rainfall_mm,
        "temperature_c": float(main.get("temp", 0)),
        "humidity_pct": float(main.get("humidity", 0)),
        "pressure_hpa": float(main.get("pressure", 0)),
        "wind_speed_ms": float(wind.get("speed", 0)),
        "cloud_coverage_pct": float(clouds.get("all", 0)),
        "rain_present": int(rainfall_mm >= RAIN_PRESENT_3H_MM),
        "is_valid": 1,
    }


def store_hourly_record(weather: Dict):

    execute(
        """
        INSERT INTO hourly_records (
            recorded_at,
            source_slot,
            rainfall_mm,
            temperature_c,
            humidity_pct,
            pressure_hpa,
            wind_speed_ms,
            cloud_coverage_pct,
            is_valid
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            weather["recorded_at"],
            weather["source_slot"],
            weather["rainfall_mm"],
            weather["temperature_c"],
            weather["humidity_pct"],
            weather["pressure_hpa"],
            weather["wind_speed_ms"],
            weather["cloud_coverage_pct"],
            weather["is_valid"],
        ),
    )


def collect_and_store_weather() -> Optional[Dict]:

    weather = fetch_weather_snapshot()

    if not weather:
        return None

    store_hourly_record(weather)

    print(
        f"Weather stored | Rain: {weather['rainfall_mm']} mm | Temp: {weather['temperature_c']}°C"
    )

    return weather