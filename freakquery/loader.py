# freakquery/loader.py

import json

from freakquery.registry.aliases import (
    canonical_value,
)


def load_logs(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    # ---------------------------------
    # Standard logs.json
    # ---------------------------------
    if isinstance(data, list):
        return data

    # ---------------------------------
    # Journal export
    # ---------------------------------
    if isinstance(data, dict):
        if "experiences" in data:
            return load_journal(data)

    return []


def load_journal(data):
    rows = []

    for exp in data.get(
        "experiences",
        [],
    ):
        for ing in exp.get(
            "ingestions",
            [],
        ):
            tm = ing.get("time")

            try:
                row_id = int(tm)
            except:
                row_id = len(rows) + 1

            row = {
                "id": row_id,
                "time": tm,
                "substance": canonical_value(
                    "substance",
                    ing.get(
                        "substanceName",
                        "",
                    ),
                ),
                "route": canonical_value(
                    "route",
                    ing.get(
                        "administrationRoute",
                        "",
                    ),
                ),
                "dose": ing.get(
                    "dose"
                ),
                "unit": canonical_value(
                    "unit",
                    ing.get(
                        "units",
                        "",
                    ),
                ),
            }

            site = ing.get(
                "administrationSite"
            )

            if site:
                row["site"] = canonical_value(
                    "site",
                    site,
                )

            notes = ing.get(
                "notes"
            )

            if notes:
                row["notes"] = notes

            if ing.get(
                "isDoseAnEstimate"
            ):
                row["estimated"] = True

            rows.append(row)

    return rows