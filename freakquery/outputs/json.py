# src/outputs/json.py

import json

from freakquery.registry.aliases import (
    display_value,
)
from freakquery.rows import row_get


def normalize_obj(obj):
    if not isinstance(
        obj,
        dict,
    ):
        return obj

    out = dict(obj)

    for field in (
        "substance",
        "route",
        "site",
        "unit",
    ):
        val = row_get(
            out,
            field,
        )

        if val is not None:
            out[field] = display_value(
                field,
                val,
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
