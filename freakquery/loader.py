# src/loader.py

import json
from pathlib import Path

from freakquery.registry.aliases import (
    normalize_route,
)


def load_logs(path):
    path = Path(path)

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    rows = []

    for row in data:
        if not isinstance(
            row,
            dict,
        ):
            continue

        item = dict(row)

        if "route" in item:
            item["route"] = (
                normalize_route(
                    item["route"]
                )
            )

        rows.append(item)

    return rows