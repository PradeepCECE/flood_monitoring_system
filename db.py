import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from config import DB_PATH


def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            '''
            CREATE TABLE IF NOT EXISTS hourly_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recorded_at TEXT NOT NULL,
                source_slot TEXT,
                rainfall_mm REAL NOT NULL,
                temperature_c REAL NOT NULL,
                humidity_pct REAL NOT NULL,
                pressure_hpa REAL NOT NULL,
                wind_speed_ms REAL NOT NULL,
                cloud_coverage_pct REAL NOT NULL,
                is_valid INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_hourly_records_time
            ON hourly_records(recorded_at);

            CREATE TABLE IF NOT EXISTS daily_summaries (
                day TEXT PRIMARY KEY,
                total_rainfall_mm REAL NOT NULL,
                avg_temperature_c REAL NOT NULL,
                avg_humidity_pct REAL NOT NULL,
                avg_pressure_hpa REAL NOT NULL,
                avg_wind_speed_ms REAL NOT NULL,
                reading_count INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS daily_predictions (
                day TEXT PRIMARY KEY,
                risk_probability REAL NOT NULL,
                risk_level TEXT NOT NULL,
                reason TEXT NOT NULL,
                window_ready INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                sent INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(day, alert_type)
            );

            CREATE INDEX IF NOT EXISTS idx_alerts_day
            ON alerts(day);
            '''
        )

    print("Database initialized successfully.")
def execute(query: str, params: tuple = ()) -> None:
    with get_connection() as conn:
        conn.execute(query, params)


def fetch_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        return conn.execute(query, params).fetchone()


def fetch_all(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        return conn.execute(query, params).fetchall()
