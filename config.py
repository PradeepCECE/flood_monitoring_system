import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "flood_monitor.db"

# --------------------------------------------------
# OpenWeather API Configuration
# --------------------------------------------------

OPENWEATHER_API_KEY = os.getenv(
    "OPENWEATHER_API_KEY",
    "5f2d430cfee00a6563cc4d4671df0e63"
)

OPENWEATHER_LAT = float(os.getenv("OPENWEATHER_LAT", "13.0827"))
OPENWEATHER_LON = float(os.getenv("OPENWEATHER_LON", "80.2707"))

OPENWEATHER_UNITS = os.getenv("OPENWEATHER_UNITS", "metric")


# --------------------------------------------------
# Email / SMTP Configuration
# --------------------------------------------------

MAIL_ENABLED = True

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

SMTP_USERNAME = "Flood"

# ⚠️ Put your Gmail App Password here
SMTP_PASSWORD = "uyxlvyhzyuyaryec"

MAIL_FROM = "floodmonitoringapp@gmail.com"

MAIL_TO = "pradeepchandran.dev@gmail.com"


# --------------------------------------------------
# Scheduler Settings
# --------------------------------------------------

COLLECTION_INTERVAL_HOURS = 3
DASHBOARD_REFRESH_MS = COLLECTION_INTERVAL_HOURS * 60 * 60 * 1000


# --------------------------------------------------
# Environmental Thresholds
# --------------------------------------------------

HEAVY_RAIN_DAILY_MM = 64.5
VERY_HEAVY_RAIN_DAILY_MM = 115.6
EXTREME_RAIN_DAILY_MM = 204.5

RAIN_PRESENT_3H_MM = 0.1

HIGH_HUMIDITY_PERCENT = 85.0
LOW_PRESSURE_HPA = 1000.0
STRONG_WIND_MS = 10.0


# --------------------------------------------------
# Sliding Window Configuration
# --------------------------------------------------

ROLLING_WINDOW_DAYS = 3


# --------------------------------------------------
# Alert Decision Thresholds
# --------------------------------------------------

FLOOD_ALERT_PROBABILITY = 0.70
MONITOR_PROBABILITY = 0.45