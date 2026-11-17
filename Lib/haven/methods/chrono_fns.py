"""
Haven Standard Library - Chrono & Temporal Continuity Methods
Standard: Open Digital Continuity Standard (ODCS) & Monotonic Time Spec
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import time
import calendar
from datetime import datetime, timezone, timedelta
from typing import Optional, Union


def now_utc() -> datetime:
    """Returns current UTC datetime with timezone awareness."""
    return datetime.now(timezone.utc)


def now_iso() -> str:
    """Returns current UTC ISO-8601 timestamp string."""
    return datetime.now(timezone.utc).isoformat()


def now_ms() -> int:
    """Returns current epoch timestamp in milliseconds."""
    return int(time.time() * 1000)


def now_micros() -> int:
    """Returns current epoch timestamp in microseconds."""
    return int(time.time() * 1_000_000)


def now_timestamp() -> float:
    """Returns current epoch timestamp in seconds."""
    return time.time()


def parse_iso(iso_str: str) -> datetime:
    """Parses an ISO-8601 formatted string into datetime."""
    return datetime.fromisoformat(iso_str)


def format_iso(dt: datetime) -> str:
    """Formats datetime to ISO-8601 string."""
    return dt.isoformat()


def add_seconds(dt: datetime, s: float) -> datetime:
    """Adds seconds to datetime."""
    return dt + timedelta(seconds=s)


def add_minutes(dt: datetime, m: float) -> datetime:
    """Adds minutes to datetime."""
    return dt + timedelta(minutes=m)


def add_hours(dt: datetime, h: float) -> datetime:
    """Adds hours to datetime."""
    return dt + timedelta(hours=h)


def add_days(dt: datetime, d: float) -> datetime:
    """Adds days to datetime."""
    return dt + timedelta(days=d)


def diff_seconds(dt1: datetime, dt2: datetime) -> float:
    """Returns difference in seconds (dt1 - dt2)."""
    return (dt1 - dt2).total_seconds()


def diff_days(dt1: datetime, dt2: datetime) -> float:
    """Returns difference in days (dt1 - dt2)."""
    return (dt1 - dt2).total_seconds() / 86400.0


def is_leap_year(year: int) -> bool:
    """Checks if year is a leap year."""
    return calendar.isleap(year)


def days_in_month(year: int, month: int) -> int:
    """Returns total days in the given month of year."""
    return calendar.monthrange(year, month)[1]


def start_of_day(dt: datetime) -> datetime:
    """Returns datetime set to 00:00:00 of the same day."""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(dt: datetime) -> datetime:
    """Returns datetime set to 23:59:59.999999 of the same day."""
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def start_of_month(dt: datetime) -> datetime:
    """Returns datetime set to first day of the month at 00:00:00."""
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def end_of_month(dt: datetime) -> datetime:
    """Returns datetime set to last day of the month at 23:59:59.999999."""
    last_day = days_in_month(dt.year, dt.month)
    return dt.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)


def start_of_year(dt: datetime) -> datetime:
    """Returns datetime set to Jan 1 at 00:00:00."""
    return dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)


def end_of_year(dt: datetime) -> datetime:
    """Returns datetime set to Dec 31 at 23:59:59.999999."""
    return dt.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)


def is_weekend(dt: datetime) -> bool:
    """Checks if datetime falls on Saturday or Sunday."""
    return dt.weekday() >= 5


def humanize_duration(seconds: float) -> str:
    """Converts duration in seconds to human-readable string (e.g. '2h 15m 30s')."""
    s = int(seconds)
    if s < 60:
        return f"{s}s"
    m, s = divmod(s, 60)
    if m < 60:
        return f"{m}m {s}s"
    h, m = divmod(m, 60)
    if h < 24:
        return f"{h}h {m}m"
    d, h = divmod(h, 24)
    return f"{d}d {h}h {m}m"


def sleep_ms(ms: int) -> None:
    """High-precision sleep for specified milliseconds."""
    time.sleep(ms / 1000.0)


def monotonic_ms() -> int:
    """Returns monotonic clock time in milliseconds."""
    return int(time.monotonic() * 1000)
