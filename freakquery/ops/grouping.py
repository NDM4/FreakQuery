# freakquery/ops/grouping.py

from collections import Counter
from datetime import datetime, timedelta

from freakquery.constants import (
    GRP_BINGES,
    GRP_STREAKS,
)

from freakquery.units import to_mg
from freakquery.config import get


def group_duration(group):
    if not group:
        return 0

    return group[-1]["time"] - group[0]["time"]


def group_sum(group):
    total = 0.0

    for row in group:
        total += to_mg(
            row.get("dose"),
            row.get("unit"),
        )

    return total


def main_substance(group):
    c = Counter()

    for row in group:
        c[row.get("substance", "")] += 1

    if not c:
        return ""

    return c.most_common(1)[0][0]


# --------------------------------
# BINGES
# Needs at least one consecutive
# pair inside the configured gap.
# Isolated rows are ignored.
# --------------------------------
def build_binges(rows):
    if not rows:
        return []

    rows = sorted(
        rows,
        key=lambda r: r["time"],
    )

    gap_hours = get(
        "grouping.binge_gap_hours",
        8,
    )

    max_gap = int(
        gap_hours * 60 * 60 * 1000
    )

    groups = []
    cur = []

    for i in range(len(rows) - 1):
        a = rows[i]
        b = rows[i + 1]

        diff = b["time"] - a["time"]

        if diff <= max_gap:
            if not cur:
                cur = [a]

            cur.append(b)

        else:
            if cur:
                groups.append(cur)
                cur = []

    if cur:
        groups.append(cur)

    return groups


# --------------------------------
# STREAKS
# Consecutive calendar days
# --------------------------------
def build_streaks(rows):
    if not rows:
        return []

    rows = sorted(
        rows,
        key=lambda r: r["time"],
    )

    by_day = {}

    for row in rows:
        d = datetime.fromtimestamp(
            row["time"] / 1000
        ).date()

        by_day.setdefault(
            d,
            [],
        ).append(row)

    days = sorted(by_day.keys())

    groups = []
    cur = list(by_day[days[0]])
    prev = days[0]

    for d in days[1:]:
        if d - prev == timedelta(days=1):
            cur.extend(by_day[d])
        else:
            groups.append(cur)
            cur = list(by_day[d])

        prev = d

    groups.append(cur)

    return groups


def apply_grouping(rows, plan, ctx):
    mode = plan.group

    if mode == GRP_BINGES:
        return build_binges(rows)

    if mode == GRP_STREAKS:
        return build_streaks(rows)

    return rows