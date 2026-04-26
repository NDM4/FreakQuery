# src/ops/metrics.py

from collections import Counter

from freakquery.registry.aliases import (
    norm,
    canonical_value,
    field_keys,
)

from freakquery.config import get


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
    if not isinstance(
        n,
        int,
    ):
        return items

    if n <= 0:
        return items

    return items[:n]


def row_get(row, key):
    for wanted in field_keys(key):
        nw = norm(wanted)

        for real in row.keys():
            if norm(real) == nw:
                return row.get(real)

    return None


def apply_metrics(
    rows,
    plan,
    ctx,
):
    if not plan.metrics:
        return rows

    metric = norm(
        plan.metrics[-1]
    )

    total = len(rows)

    # ---------------------------------
    # count
    # ---------------------------------
    if metric == "count":
        return total

    # ---------------------------------
    # first / last fallback
    # ---------------------------------
    if metric == "first":
        return rows[0] if rows else {}

    if metric == "last":
        return rows[-1] if rows else {}

    # ---------------------------------
    # top_substances
    # ---------------------------------
    if metric == "top_substances":
        c = Counter()

        for r in rows:
            val = row_get(
                r,
                "substance",
            )

            if val:
                c[str(val)] += 1

        out = []

        for k, v in c.most_common():
            out.append(
                {
                    "substance": k,
                    "count": v,
                }
            )

        n = (
            plan.params.get("top")
            or plan.params.get(
                "limit"
            )
        )

        return top_n(out, n)

    # ---------------------------------
    # top_routes
    # ---------------------------------
    if metric == "top_routes":
        c = Counter()

        for r in rows:
            val = row_get(
                r,
                "route",
            )

            if val:
                val = canonical_value(
                    "route",
                    val,
                )

                c[str(val)] += 1

        out = []

        for k, v in c.most_common():
            out.append(
                {
                    "value": k,
                    "count": v,
                }
            )

        n = (
            plan.params.get("top")
            or plan.params.get(
                "limit"
            )
        )

        return top_n(out, n)

    # ---------------------------------
    # sites
    # ---------------------------------
    if metric == "sites":
        c = Counter()

        for r in rows:
            val = row_get(
                r,
                "site",
            )

            if val:
                val = canonical_value(
                    "site",
                    val,
                )

                c[str(val)] += 1

        out = []

        for k, v in c.most_common():
            out.append(
                {
                    "value": k,
                    "count": v,
                }
            )

        n = (
            plan.params.get("top")
            or plan.params.get(
                "limit"
            )
        )

        return top_n(out, n)

    # ---------------------------------
    # ratio=field
    # ---------------------------------
    if metric.startswith(
        "ratio="
    ):
        target = metric.split(
            "=",
            1,
        )[1]

        c = Counter()

        for r in rows:
            val = row_get(
                r,
                target,
            )

            if val is None:
                continue

            val = canonical_value(
                target,
                val,
            )

            c[str(val)] += 1

        denom = sum(
            c.values()
        )

        out = []

        for k, v in c.most_common():
            out.append(
                {
                    "value": k,
                    "count": v,
                    "label": pct(
                        v,
                        denom,
                    ),
                }
            )

        n = (
            plan.params.get("top")
            or plan.params.get(
                "limit"
            )
        )

        return top_n(out, n)

    # ---------------------------------
    # sum_dose
    # ---------------------------------
    if metric == "sum_dose":
        s = 0

        for r in rows:
            val = row_get(
                r,
                "dose",
            )

            try:
                s += float(val)
            except:
                pass

        return s

    # ---------------------------------
    # fallback
    # ---------------------------------
    return rows