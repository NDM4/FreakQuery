# src/outputs/json.py

import json

from freakquery.registry.aliases import (
    display_value,
    norm,
    field_keys,
)


def row_get(row, key):
    for wanted in field_keys(key):
        nw = norm(wanted)

        for real in row.keys():
            if norm(real) == nw:
                return row.get(real)

    return None


def normalize_obj(obj):
    if not isinstance(
        obj,
        dict,
    ):
        return obj

    out = dict(obj)

    route = row_get(
        out,
        "route",
    )

    if route is not None:
        out["route"] = display_value(
            "route",
            route,
        )

    site = row_get(
        out,
        "site",
    )

    if site is not None:
        out["site"] = display_value(
            "site",
            site,
        )

    return out


def normalize_data(data):
    if isinstance(data, list):
        return [
            normalize_obj(x)
            for x in data
        ]

    if isinstance(
        data,
        dict,
    ):
        return normalize_obj(
            data
        )

    return data


def render_json(
    data,
    plan,
    ctx,
):
    data = normalize_data(
        data
    )

    return json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )