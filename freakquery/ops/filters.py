# freakquery/ops/filters.py

from datetime import datetime

from freakquery.registry.aliases import (
    norm,
    field_keys,
    same_value,
)


# =====================================================
# HELPERS
# =====================================================

def row_get(row, key):
    for wanted in field_keys(key):
        nw = norm(wanted)

        for real in row.keys():
            if norm(real) == nw:
                return row.get(real)

    return None


def row_time(row):
    try:
        return int(row_get(row, "time"))
    except:
        return 0


def row_dt(row):
    ts = row_time(row)

    if not ts:
        return None

    try:
        return datetime.fromtimestamp(ts / 1000)
    except:
        return None


def now_dt(ctx):
    if ctx and getattr(ctx, "now_ms", None):
        try:
            return datetime.fromtimestamp(
                int(ctx.now_ms) / 1000
            )
        except:
            pass

    return datetime.now()


def same_day(a, b):
    return (
        a.year == b.year and
        a.month == b.month and
        a.day == b.day
    )


def same_week(a, b):
    ia = a.isocalendar()
    ib = b.isocalendar()

    return (
        ia[0] == ib[0] and
        ia[1] == ib[1]
    )


def same_month(a, b):
    return (
        a.year == b.year and
        a.month == b.month
    )


def same_year(a, b):
    return a.year == b.year


# =====================================================
# MAIN
# =====================================================

def apply_filters(rows, plan, ctx):
    if not plan.filters:
        return rows

    out = []
    now = now_dt(ctx)

    for row in rows:
        ok = True
        dt = row_dt(row)

        for f in plan.filters:
            fl = str(f).strip().lower()

            # ---------------------------------
            # TIME FILTERS
            # ---------------------------------

            if fl in (
                "day",
                "today",
            ):
                if not dt or not same_day(dt, now):
                    ok = False
                    break
                continue

            if fl == "week":
                if not dt or not same_week(dt, now):
                    ok = False
                    break
                continue

            if fl == "month":
                if not dt or not same_month(dt, now):
                    ok = False
                    break
                continue

            if fl == "year":
                if not dt or not same_year(dt, now):
                    ok = False
                    break
                continue

            # ---------------------------------
            # key=value filters
            # ---------------------------------

            if "=" in fl:
                key, value = fl.split("=", 1)

                rv = row_get(
                    row,
                    key,
                )

                if rv is None:
                    ok = False
                    break

                if not same_value(
                    key,
                    rv,
                    value,
                ):
                    ok = False
                    break

                continue

        if ok:
            out.append(row)

    return out