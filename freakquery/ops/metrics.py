# freakquery/ops/metrics.py

from collections import Counter
import time

from freakquery.registry.aliases import (
    norm,
    canonical_value,
    field_keys,
)

from freakquery.config import get


def tag_norm(x):
    return str(x).strip().lower()


def pct(part, total):
    if total <= 0:
        return "0%"

    real = (part / total) * 100

    if real < 1:
        return get(
            "render.ratio_under_one",
            "<1%",
        )

    return f"{round(real)}%"


def top_n(items, n):
    if not isinstance(n, int):
        return items

    if n <= 0:
        return items

    return items[:n]


def row_get(row, key):
    if not isinstance(row, dict):
        return None

    for wanted in field_keys(key):
        nw = norm(wanted)

        for real in row.keys():
            if norm(real) == nw:
                return row.get(real)

    return None


def human_since(ms):
    seconds = ms // 1000

    if seconds < 60:
        return f"{seconds}s"

    minutes = seconds // 60

    if minutes < 60:
        return f"{minutes}m {seconds % 60}s"

    hours = minutes // 60

    if hours < 24:
        return f"{hours}h {minutes % 60}m"

    days = hours // 24

    if days < 30:
        return f"{days}d {hours % 24}h"

    months = days // 30

    if months < 12:
        return f"{months}mo {days % 30}d"

    years = days // 365
    return f"{years}y {(days % 365)//30}mo"


def resolve_metric(plan):
    known = {
        "count",
        "first",
        "last",
        "since",
        "dose",
        "substance",
        "top_substances",
        "top_routes",
        "sites",
        "sum_dose",
    }

    for m in plan.metrics:
        low = tag_norm(m)

        if low in known:
            return low

        if low.startswith("ratio="):
            return low

    return None


def apply_metrics(rows, plan, ctx):
    if not plan.metrics:
        return rows

    metric = resolve_metric(plan)

    if not metric:
        return rows

    total = len(rows)

    # count
    if metric == "count":
        return total

    # first
    if metric == "first":
        return rows[0] if rows else {}

    # last
    if metric == "last":
        return rows[-1] if rows else {}

    # since
    if metric == "since":
        if not rows:
            return ""

        row = rows[-1]

        try:
            ts = int(row_get(row, "time"))
        except:
            return ""

        now = int(time.time() * 1000)
        return human_since(max(0, now - ts))

    # dose
    if metric == "dose":
        if not rows:
            return ""

        val = row_get(rows[-1], "dose")
        unit = row_get(rows[-1], "unit")

        if val is None:
            return ""

        return f"{val} {unit}".strip()

    # substance
    if metric == "substance":
        if not rows:
            return ""

        return str(
            row_get(rows[-1], "substance") or ""
        )

    # top_substances
    if metric == "top_substances":
        c = Counter()

        for r in rows:
            v = row_get(r, "substance")
            if v:
                c[str(v)] += 1

        out = [
            {
                "substance": k,
                "count": v,
            }
            for k, v in c.most_common()
        ]

        n = (
            plan.params.get("top")
            or plan.params.get("limit")
        )

        return top_n(out, n)

    # top_routes
    if metric == "top_routes":
        c = Counter()

        for r in rows:
            v = row_get(r, "route")
            if v:
                v = canonical_value("route", v)
                c[str(v)] += 1

        out = [
            {
                "value": k,
                "count": v,
            }
            for k, v in c.most_common()
        ]

        n = (
            plan.params.get("top")
            or plan.params.get("limit")
        )

        return top_n(out, n)

    # sites
    if metric == "sites":
        c = Counter()

        for r in rows:
            v = row_get(r, "site")
            if v:
                v = canonical_value("site", v)
                c[str(v)] += 1

        out = [
            {
                "value": k,
                "count": v,
            }
            for k, v in c.most_common()
        ]

        n = (
            plan.params.get("top")
            or plan.params.get("limit")
        )

        return top_n(out, n)

    # ratio=field
    if metric.startswith("ratio="):
        field = metric.split("=", 1)[1]

        c = Counter()

        for r in rows:
            v = row_get(r, field)
            if v is None:
                continue

            v = canonical_value(field, v)
            c[str(v)] += 1

        denom = sum(c.values())

        out = [
            {
                "value": k,
                "count": v,
                "label": pct(v, denom),
            }
            for k, v in c.most_common()
        ]

        n = (
            plan.params.get("top")
            or plan.params.get("limit")
        )

        return top_n(out, n)

    # sum_dose
    if metric == "sum_dose":
        s = 0.0

        for r in rows:
            val = row_get(r, "dose")

            try:
                s += float(val)
            except:
                pass

        if s.is_integer():
            return int(s)

        return round(s, 2)

    return rows