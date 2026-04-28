# freakquery/ops/metrics.py

from collections import Counter
import time

from freakquery.registry.aliases import (
    norm,
    canonical_value,
    field_keys,
    same_value,
)

from freakquery.ops.grouping import (
    group_sum,
    group_duration,
    main_substance,
)

from freakquery.units import to_mg
from freakquery.config import get


# =====================================================
# HELPERS
# =====================================================

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
    if isinstance(n, int) and n >= 0:
        return items[:n]

    return items


def row_get(row, key):
    if not isinstance(row, dict):
        return None

    for wanted in field_keys(key):
        nw = norm(wanted)

        for real in row.keys():
            if norm(real) == nw:
                return row.get(real)

    return None


def row_substance(row):
    v = row_get(row, "substance")

    if v is None:
        return ""

    return canonical_value(
        "substance",
        v,
    )


def row_time_value(row):
    v = row_get(row, "time")

    try:
        return int(v)
    except:
        return 0


def clean_number(value):
    try:
        n = float(value)

        if n.is_integer():
            return str(int(n))

        s = str(n)

        if "." in s:
            s = s.rstrip("0").rstrip(".")

        return s
    except:
        return str(value)


def row_dose_text(row):
    dose = row_get(row, "dose")
    unit = row_get(row, "unit")

    if dose is None:
        return ""

    dose = clean_number(dose)

    if unit:
        unit = canonical_value(
            "unit",
            unit,
        )
        return f"{dose} {unit}"

    return str(dose)


def ordered_rows(rows):
    return sorted(
        rows,
        key=lambda r: row_time_value(r)
    )


def ordered_substances(rows):
    out = []

    for r in ordered_rows(rows):
        s = row_substance(r)

        if s:
            out.append(s)

    return out


def counter_rows(counter):
    return [
        {
            "value": k,
            "count": v,
        }
        for k, v in counter.most_common()
    ]


def compress_sequence(items):
    if not items:
        return []

    out = []

    cur = items[0]
    n = 1

    for x in items[1:]:
        if x == cur:
            n += 1
        else:
            if n > 1:
                out.append(
                    f"{cur} x{n}"
                )
            else:
                out.append(cur)

            cur = x
            n = 1

    if n > 1:
        out.append(
            f"{cur} x{n}"
        )
    else:
        out.append(cur)

    return out


def human_since(ms):
    seconds = ms // 1000

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


# =====================================================
# METRIC RESOLUTION
# =====================================================

def resolve_metric(plan):
    for m in plan.metrics:
        low = str(m).strip().lower()

        if low.startswith("ratio="):
            return m

        if low.startswith("sequence="):
            return m

        return low

    return None


# =====================================================
# MAIN
# =====================================================

def apply_metrics(rows, plan, ctx):
    if not plan.metrics:
        return rows

    metric = resolve_metric(plan)

    if not metric:
        return rows

    total = len(rows)

    # BASIC

    if metric == "count":
        return total

    if metric == "first":
        return rows[0] if rows else {}

    if metric == "last":
        return rows[-1] if rows else {}

    if metric == "since":
        if not rows:
            return ""

        ts = row_time_value(rows[-1])

        now = int(
            time.time() * 1000
        )

        return human_since(
            max(0, now - ts)
        )

    if metric == "dose":
        if not rows:
            return ""

        return row_dose_text(
            rows[-1]
        )

    if metric == "substance":
        if not rows:
            return ""

        return row_substance(
            rows[-1]
        )

    # SUM

    if metric == "sum_dose":
        s = 0.0

        for r in rows:
            s += to_mg(
                row_get(r, "dose"),
                row_get(r, "unit"),
            )

        if s.is_integer():
            return int(s)

        return round(s, 2)

    # TOPS

    if metric == "top_substances":
        c = Counter()

        for r in rows:
            v = row_substance(r)

            if v:
                c[v] += 1

        out = [
            {
                "substance": k,
                "count": v,
            }
            for k, v in c.most_common()
        ]

        return top_n(
            out,
            plan.params.get("limit"),
        )

    if metric == "top_routes":
        c = Counter()

        for r in rows:
            v = row_get(
                r,
                "route",
            )

            if v:
                v = canonical_value(
                    "route",
                    v,
                )
                c[v] += 1

        return top_n(
            counter_rows(c),
            plan.params.get("limit"),
        )

    if metric == "sites":
        c = Counter()

        for r in rows:
            v = row_get(
                r,
                "site",
            )

            if v:
                v = canonical_value(
                    "site",
                    v,
                )
                c[v] += 1

        return top_n(
            counter_rows(c),
            plan.params.get("limit"),
        )

    # RATIO

    if metric.startswith("ratio="):
        field = metric.split(
            "=",
            1,
        )[1]

        c = Counter()

        for r in rows:
            v = row_get(r, field)

            if v in (
                None,
                "",
            ):
                continue

            v = canonical_value(
                field,
                v,
            )

            c[v] += 1

        denom = sum(c.values())

        out = [
            {
                "value": k,
                "count": v,
                "label": pct(
                    v,
                    denom,
                ),
            }
            for k, v in c.most_common()
        ]

        return top_n(
            out,
            plan.params.get("limit"),
        )

    # GROUP

    if metric == "group_sum":
        return group_sum(rows)

    if metric == "group_duration":
        return human_since(
            group_duration(rows)
        )

    if metric == "group_count":
        return len(rows)

    if metric == "main_substance":
        return main_substance(rows)

    if metric == "substances_count":
        return len(
            set(
                ordered_substances(rows)
            )
        )

    if metric == "avg_gap":
        if len(rows) < 2:
            return "0s"

        rs = ordered_rows(rows)
        gaps = []

        for i in range(
            1,
            len(rs),
        ):
            a = row_time_value(
                rs[i - 1]
            )

            b = row_time_value(
                rs[i]
            )

            if a and b:
                gaps.append(
                    b - a
                )

        if not gaps:
            return "0s"

        return human_since(
            int(
                sum(gaps)
                / len(gaps)
            )
        )

    # TIMELINE

    if metric == "timeline":
        return rows

    # SEQUENCE

    if metric == "sequence":
        rs = ordered_rows(rows)

        seq = [
            row_substance(r)
            for r in rs
            if row_substance(r)
        ]

        return " -> ".join(
            compress_sequence(seq)
        )

    if metric == "sequence=dose":
        rs = ordered_rows(rows)

        out = []

        for r in rs:
            sub = row_substance(r)

            if not sub:
                continue

            dose = row_dose_text(r)

            if dose:
                out.append(
                    f"{sub} ({dose})"
                )
            else:
                out.append(sub)

        return " -> ".join(out)

    if metric == "sequence=time":
        rs = ordered_rows(rows)

        if not rs:
            return ""

        out = []
        prev = None

        for r in rs:
            sub = row_substance(r)

            if not sub:
                continue

            now = row_time_value(r)

            if prev is not None:
                out.append(
                    f"+{human_since(now - prev)}"
                )

            out.append(sub)
            prev = now

        return " -> ".join(out)

    if metric == "sequence=patterns":
        seq = ordered_substances(rows)

        c = Counter()

        for i in range(
            len(seq) - 1
        ):
            c[
                f"{seq[i]} -> {seq[i+1]}"
            ] += 1

        return counter_rows(c)

    if metric.startswith(
        "sequence=after:"
    ):
        target = metric.split(
            ":",
            1,
        )[1]

        seq = ordered_substances(rows)
        c = Counter()

        for i in range(
            len(seq) - 1
        ):
            if same_value(
                "substance",
                seq[i],
                target,
            ):
                c[seq[i + 1]] += 1

        return counter_rows(c)

    if metric.startswith(
        "sequence=before:"
    ):
        target = metric.split(
            ":",
            1,
        )[1]

        seq = ordered_substances(rows)
        c = Counter()

        for i in range(
            1,
            len(seq),
        ):
            if same_value(
                "substance",
                seq[i],
                target,
            ):
                c[seq[i - 1]] += 1

        return counter_rows(c)

    return rows