from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Tuple

from config import (
    MAIL_ENABLED,
    MAIL_FROM,
    MAIL_TO,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USERNAME,
)
from db import execute


def _send_message(subject: str, body: str) -> Tuple[bool, str]:
    if not MAIL_ENABLED:
        return False, 'MAIL_ENABLED is false; email not sent.'

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = MAIL_FROM
    msg['To'] = MAIL_TO
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True, 'Email sent successfully.'
    except Exception as exc:  # pragma: no cover
        return False, f'Email send failed: {exc}'


def log_alert(day: str, alert_type: str, message: str, sent: bool) -> None:
    execute(
        '''
        INSERT INTO alerts (day, alert_type, message, sent)
        VALUES (?, ?, ?, ?)
        ''',
        (day, alert_type, message, int(sent)),
    )


def send_rain_update(day: str, rainfall_mm: float) -> Tuple[bool, str, str]:
    subject = f'Rain Update - {day}'
    body = (
    f'Rainfall update detected.\n\n'
    f'Date: {day}\n'
    f'Rainfall (latest 3-hour block): {rainfall_mm:.2f} mm\n\n'
    f'This notification is generated automatically by the flood monitoring system.'
)
    sent, detail = _send_message(subject, body)
    log_alert(day, 'RAIN_UPDATE', f'{body}\n\nStatus: {detail}', sent)
    return sent, detail, body


def send_flood_alert(day: str, probability: float, rolling_rain_mm: float, reason: str) -> Tuple[bool, str, str]:
    subject = f'Flood Alert - {day}'
    body = (
        f'Potential flood conditions detected.\n\n'
        f'Flood probability from rule-based algorithm: {probability * 100:.0f}%\n'
        f'Total rainfall across current 3-day sliding window: {rolling_rain_mm:.2f} mm\n'
        f'Why this was triggered: {reason}\n\n'
        f'Please inspect vulnerable areas and issue field verification if required.'
    )
    sent, detail = _send_message(subject, body)
    log_alert(day, 'FLOOD_ALERT', f'{body}\n\nStatus: {detail}', sent)
    return sent, detail, body
