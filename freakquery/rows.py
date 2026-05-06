from __future__ import annotations

import time
from datetime import datetime
from typing import Any

from freakquery.registry.aliases import field_keys, norm


def row_get(row, key, default=None) -> Any:
    if not isinstance(row, dict):
        return default

    for wanted in field_keys(key):
        wanted_norm = norm(wanted)

        for real, value in row.items():
            if norm(real) == wanted_norm:
                return value

    return default


def row_time(row) -> int:
    try:
        return int(row_get(row, "time", 0))
    except (TypeError, ValueError):
        return 0


def row_datetime(row) -> datetime | None:
    ts = row_time(row)

    if not ts:
        return None

    try:
        return datetime.fromtimestamp(ts / 1000)
    except (OverflowError, OSError, ValueError):
        return None


def clean_number(value) -> str:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return str(value)

    if n.is_integer():
        return str(int(n))

    return str(n).rstrip("0").rstrip(".")


def human_since(ms) -> str:
    seconds = int(ms) // 1000

    mins, sec = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)
    days, hrs = divmod(hrs, 24)
    years, days = divmod(days, 365)
    months, days = divmod(days, 30)

    if years:
        return f"{years}y {months}mo"

    if months:
        return f"{months}mo {days}d"

    if days:
        return f"{days}d {hrs}h"

    if hrs:
        return f"{hrs}h {mins}m"

    if mins:
        return f"{mins}m {sec}s"

    return f"{sec}s"


def now_ms() -> int:
    return int(time.time() * 1000)


def ordered_rows(rows) -> list:
    return sorted(rows, key=row_time)
