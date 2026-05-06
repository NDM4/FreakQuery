# src/query/validator.py

from freakquery.fq_types import LOG_ROWS, ANY
from freakquery.tag_registry import REGISTRY


def validate_parts(parts):
    current = LOG_ROWS

    for part in parts:
        if "=" in part:
            continue

        meta = REGISTRY.get(part)

        if not meta:
            continue

        allowed = meta["accept"]

        if ANY not in allowed and current not in allowed:
            return (
                False,
                f"{part} requires "
                f"{'/'.join(sorted(allowed))}, "
                f"got {current}"
            )

        current = meta["returns"]

    return True, None
