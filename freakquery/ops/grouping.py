# src/ops/grouping.py

from collections import Counter
from datetime import datetime

from freakquery.constants import (
    GRP_BINGES,
    GRP_STREAKS,
)


def group_duration(group):
    """
    Return duration in milliseconds between first and last row.
    """
    if not group:
        return 0

    return group[-1]["time"] - group[0]["time"]


def group_sum(group):
    """
    Sum numeric doses inside a group.
    """
    total = 0

    for row in group:
        total += row.get("dose", 0) or 0

    return total


def main_substance(group):
    """
    Most common substance inside a group.
    """
    counts = Counter()

    for row in group:
        counts[row.get("substance", "")] += 1

    if not counts:
        return ""

    return counts.most_common(1)[0][0]


def build_binges(rows):
    """
    Group rows by same calendar day.
    """
    if not rows:
        return []

    rows = sorted(rows, key=lambda row: row["time"])

    groups = []
    current = [rows[0]]

    for row in rows[1:]:
        a = datetime.fromtimestamp(
            current[-1]["time"] / 1000
        )
        b = datetime.fromtimestamp(
            row["time"] / 1000
        )

        same_day = (
            a.year == b.year and
            a.month == b.month and
            a.day == b.day
        )

        if same_day:
            current.append(row)
        else:
            groups.append(current)
            current = [row]

    groups.append(current)

    return groups


def build_streaks(rows):
    """
    Group consecutive active days into streaks.
    """
    if not rows:
        return []

    rows = sorted(rows, key=lambda row: row["time"])

    by_day = {}

    for row in rows:
        dt = datetime.fromtimestamp(
            row["time"] / 1000
        )

        key = (dt.year, dt.month, dt.day)

        by_day.setdefault(key, []).append(row)

    day_keys = sorted(by_day.keys())

    groups = []
    current = list(by_day[day_keys[0]])
    previous = datetime(*day_keys[0])

    for key in day_keys[1:]:
        now = datetime(*key)

        if (now - previous).days == 1:
            current.extend(by_day[key])
        else:
            groups.append(current)
            current = list(by_day[key])

        previous = now

    groups.append(current)

    return groups


def apply_grouping(rows, plan, ctx):
    """
    Apply grouping stage.
    """
    mode = plan.group

    if mode == GRP_BINGES:
        return build_binges(rows)

    if mode == GRP_STREAKS:
        return build_streaks(rows)

    return rows