# Flood Monitor (Rule-Based, No Frontend Libraries)

This project replaces the ML model with a simple rule-based decision engine while keeping the same staged flow:
- collect 3-hour OpenWeather data
- aggregate into daily summaries
- evaluate a 3-day sliding window
- email alerts when flood probability crosses the configured threshold
- show the latest state on a plain HTML/CSS/JS dashboard

## Project Structure

- `app.py` - Flask entrypoint and API routes
- `config.py` - thresholds, API settings, mail settings
- `db.py` - SQLite schema and helpers
- `scheduler_jobs.py` - 3-hour collection job + daily prediction job
- `services/weather_service.py` - OpenWeather fetch + validation + storage
- `services/aggregation_service.py` - daily summary building and read helpers
- `services/risk_engine.py` - rule-based flood scoring and 3-day sliding decision
- `services/email_service.py` - rain update email and flood alert email
- `templates/index.html` - plain dashboard markup
- `static/styles.css` - dashboard styling
- `static/app.js` - automatic front-end polling and color changes

## How the Algorithm Works

Each completed day gets a score using:
- daily rainfall total
- average humidity
- average pressure
- average wind speed

The latest 3 completed days are evaluated together.

### Rule Highlights
- heavier rainfall increases the score the most
- high humidity increases saturation risk
- low pressure increases storm risk
- stronger wind adds a smaller extra weight
- if 2 or more of the last 3 days are heavy-rain days, probability increases
- if humidity stayed high for all 3 days, probability increases
- if pressure stayed lower than normal for 2 or more days, probability increases
- if rainfall is rising across the 3-day window, probability increases

If the final probability is:
- `< 45%` -> Low Risk
- `45% to 69%` -> Moderate Risk
- `>= 70%` -> High Risk and flood alert is sent

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables:
   ```bash
   export OPENWEATHER_API_KEY="your_key"
   export OPENWEATHER_LAT="17.3850"
   export OPENWEATHER_LON="78.4867"

   export MAIL_ENABLED="true"
   export SMTP_HOST="smtp.gmail.com"
   export SMTP_PORT="587"
   export SMTP_USERNAME="your_email@example.com"
   export SMTP_PASSWORD="your_app_password"
   export MAIL_FROM="your_email@example.com"
   export MAIL_TO="authority@example.com"
   ```
4. Run the app:
   ```bash
   python app.py
   ```
5. Open `http://127.0.0.1:5000`

## Dashboard Behavior

- Default body color: sky blue
- If current 3-hour rainfall is detected: body turns yellow
- If a flood alert email is successfully sent: body turns red
- Weather parameter cards remain separate white boxes and do not inherit alert colors
- Frontend reloads `/api/status` automatically every 3 hours

## Useful Test Endpoints

- `POST /api/manual/collect` -> run a weather collection immediately
- `POST /api/manual/predict` -> run the daily prediction immediately

These help you test without waiting for the scheduler.
