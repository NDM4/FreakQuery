# freakquery/query/planner.py

from freakquery.query_plan import QueryPlan
from freakquery.tag_registry import REGISTRY


def tag_norm(x):
    return str(x).strip().lower()


def parse_value(v):
    raw = str(v).strip()
    low = raw.lower()

    if low in ("true", "1", "yes", "on"):
        return True

    if low in ("false", "0", "no", "off"):
        return False

    try:
        if "." not in raw:
            return int(raw)
    except:
        pass

    try:
        return float(raw)
    except:
        pass

    return raw


DISPLAY_ONLY = {
    "parens",
    "time",
    "labels",
    "percent",
    "compact",
    "sep",
}

FIELD_EXTRACTORS = {
    "dose",
    "substance",
    "route",
    "unit",
    "site",
}


def build_plan(parts):
    plan = QueryPlan()

    for raw in parts:
        part = str(raw).strip()

        if not part:
            continue

        low = tag_norm(part)

        # -------------------------
        # key=value
        # -------------------------
        if "=" in part:
            key, value = part.split("=", 1)
            key_l = tag_norm(key)

            # metric params
            if key_l == "ratio":
                plan.metrics.append(
                    f"ratio={tag_norm(value)}"
                )
                continue

            if key_l in ("top", "limit"):
                plan.params[key_l] = parse_value(value)
                continue

            # display config
            if key_l in DISPLAY_ONLY:
                plan.display[key_l] = parse_value(value)
                continue

            # otherwise filter
            plan.filters.append(
                f"{key_l}={value.strip()}"
            )
            continue

        # -------------------------
        # direct field extractors
        # -------------------------
        if low in FIELD_EXTRACTORS:
            if plan.selector:
                plan.metrics.append(low)
            else:
                plan.display[low] = True
            continue

        # -------------------------
        # display flags
        # -------------------------
        if low in DISPLAY_ONLY:
            plan.display[low] = True
            continue

        # -------------------------
        # formats
        # -------------------------
        if low == "json":
            plan.formats.append(low)
            continue

        # -------------------------
        # registry tags
        # -------------------------
        meta = REGISTRY.get(low)

        if meta:
            stage = meta.get("stage")

            if stage == "selector":
                plan.selector = low
                continue

            if stage == "group":
                plan.group = low
                continue

            if stage == "metric":
                plan.metrics.append(low)
                continue

        # unknown tag ignored

    return plan