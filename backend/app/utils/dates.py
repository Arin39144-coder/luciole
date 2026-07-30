"""Utilitaires de dates."""
from datetime import date, datetime, timedelta


def today_start() -> datetime:
    now = datetime.utcnow()
    return datetime(now.year, now.month, now.day)


def today_end() -> datetime:
    return today_start() + timedelta(days=1)


def week_start() -> datetime:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return datetime(monday.year, monday.month, monday.day)


def format_duration_minutes(seconds: int | None) -> float:
    if not seconds:
        return 0.0
    return round(seconds / 60, 1)
