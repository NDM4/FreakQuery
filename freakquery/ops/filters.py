# src/ops/filters.py

from freakquery.registry.aliases import (
    norm,
    field_keys,
    same_value,
)


def row_get(row, key):
    for wanted in field_keys(key):
        nw = norm(wanted)

        for real in row.keys():
            if norm(real) == nw:
                return row.get(real)

    return None


def apply_filters(rows, plan, ctx):
    if not plan.filters:
        return rows

    out = []

    for row in rows:
        ok = True

        for f in plan.filters:
            if "=" not in f:
                continue

            key, value = f.split("=", 1)

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

        if ok:
            out.append(row)

    return out