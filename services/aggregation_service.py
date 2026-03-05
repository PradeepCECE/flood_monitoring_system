from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from db import execute, fetch_all, fetch_one


def get_latest_hourly_record() -> Optional[Dict]:
    return fetch_one(
        '''
        SELECT * FROM hourly_records
        ORDER BY datetime(recorded_at) DESC, id DESC
        LIMIT 1
        '''
    )


def get_day_records(day: str) -> List[Dict]:
    return fetch_all(
        '''
        SELECT * FROM hourly_records
        WHERE date(recorded_at) = ?
        ORDER BY datetime(recorded_at) ASC
        ''',
        (day,),
    )


def summarize_day(day: Optional[str] = None) -> Optional[Dict]:
    target_day = day or datetime.utcnow().date().isoformat()
    rows = get_day_records(target_day)
    if not rows:
        return None

    reading_count = len(rows)
    summary = {
        'day': target_day,
        'total_rainfall_mm': round(sum(r['rainfall_mm'] for r in rows), 2),
        'avg_temperature_c': round(sum(r['temperature_c'] for r in rows) / reading_count, 2),
        'avg_humidity_pct': round(sum(r['humidity_pct'] for r in rows) / reading_count, 2),
        'avg_pressure_hpa': round(sum(r['pressure_hpa'] for r in rows) / reading_count, 2),
        'avg_wind_speed_ms': round(sum(r['wind_speed_ms'] for r in rows) / reading_count, 2),
        'reading_count': reading_count,
    }

    execute(
        '''
        INSERT INTO daily_summaries (
            day, total_rainfall_mm, avg_temperature_c, avg_humidity_pct,
            avg_pressure_hpa, avg_wind_speed_ms, reading_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(day) DO UPDATE SET
            total_rainfall_mm = excluded.total_rainfall_mm,
            avg_temperature_c = excluded.avg_temperature_c,
            avg_humidity_pct = excluded.avg_humidity_pct,
            avg_pressure_hpa = excluded.avg_pressure_hpa,
            avg_wind_speed_ms = excluded.avg_wind_speed_ms,
            reading_count = excluded.reading_count,
            created_at = CURRENT_TIMESTAMP
        ''',
        (
            summary['day'],
            summary['total_rainfall_mm'],
            summary['avg_temperature_c'],
            summary['avg_humidity_pct'],
            summary['avg_pressure_hpa'],
            summary['avg_wind_speed_ms'],
            summary['reading_count'],
        ),
    )
    return summary


def get_recent_daily_summaries(days: int = 3) -> List[Dict]:
    return fetch_all(
        '''
        SELECT * FROM daily_summaries
        ORDER BY day DESC
        LIMIT ?
        ''',
        (days,),
    )


def get_latest_prediction() -> Optional[Dict]:
    return fetch_one(
        '''
        SELECT * FROM daily_predictions
        ORDER BY day DESC
        LIMIT 1
        '''
    )


def get_recent_alerts(limit: int = 5) -> List[Dict]:
    return fetch_all(
        '''
        SELECT * FROM alerts
        ORDER BY created_at DESC, id DESC
        LIMIT ?
        ''',
        (limit,),
    )


def yesterday_utc() -> str:
    return (datetime.utcnow().date() - timedelta(days=1)).isoformat()
