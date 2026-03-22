import os
import psycopg
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from config import DATABASE_URL


@contextmanager
def get_connection():
    conn = psycopg.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:

    with get_connection() as conn:
        with conn.cursor() as cur:

            # Hourly weather records
            cur.execute("""
            CREATE TABLE IF NOT EXISTS hourly_records (
                id SERIAL PRIMARY KEY,
                recorded_at TIMESTAMP NOT NULL,
                source_slot TEXT,
                rainfall_mm FLOAT NOT NULL,
                temperature_c FLOAT NOT NULL,
                humidity_pct FLOAT NOT NULL,
                pressure_hpa FLOAT NOT NULL,
                wind_speed_ms FLOAT NOT NULL,
                cloud_coverage_pct FLOAT NOT NULL,
                is_valid INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_hourly_records_time
            ON hourly_records(recorded_at);
            """)

            # Daily summaries
            cur.execute("""
            CREATE TABLE IF NOT EXISTS daily_summaries (
                day DATE PRIMARY KEY,
                total_rainfall_mm FLOAT NOT NULL,
                avg_temperature_c FLOAT NOT NULL,
                avg_humidity_pct FLOAT NOT NULL,
                avg_pressure_hpa FLOAT NOT NULL,
                avg_wind_speed_ms FLOAT NOT NULL,
                reading_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Prediction table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS daily_predictions (
                day DATE PRIMARY KEY,
                risk_probability FLOAT NOT NULL,
                risk_level TEXT NOT NULL,
                reason TEXT NOT NULL,
                window_ready INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Alert table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                day DATE NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                sent INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(day, alert_type)
            );
            """)

            cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_day
            ON alerts(day);
            """)

    print("Database initialized successfully.")


def execute(query: str, params: tuple = ()) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)


def fetch_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            row = cur.fetchone()

            if not row:
                return None

            columns = [desc[0] for desc in cur.description]
            return dict(zip(columns, row))


def fetch_all(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, r)) for r in rows]