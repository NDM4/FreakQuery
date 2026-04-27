# freakquery/query/planner.py

from freakquery.query_plan import QueryPlan
from freakquery.tag_registry import REGISTRY
from freakquery.config import get


def tag_norm(x):
    return str(x).strip().lower()


def parse_value(v):
    raw = str(v).strip()
    low = raw.lower()

    if low in (
        "true",
        "1",
        "yes",
        "on",
    ):
        return True

    if low in (
        "false",
        "0",
        "no",
        "off",
    ):
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


# -------------------------------------------------
# runtime display flags
# -------------------------------------------------

DISPLAY_ONLY = {
    "parens",
    "time",
    "labels",
    "percent",
    "compact",
    "sep",
    "dose",
    "unit",
    "route",
    "site",
}


# -------------------------------------------------
# direct row fields
# -------------------------------------------------

FIELD_EXTRACTORS = {
    "dose",
    "substance",
    "route",
    "unit",
    "site",
}


# -------------------------------------------------
# limits logic
# -------------------------------------------------

def apply_default_limits(plan):
    """
    Smart default limits.

    Priority:
    1. explicit limit=
    2. selected groups => unlimited
    3. metric specific config
    4. group specific config
    5. rows/default config
    """

    # explicit user limit wins
    if "limit" in plan.params:
        return

    # grouped selector results => no auto limit
    if (
        plan.group
        and plan.selector
    ):
        return

    # metric specific limits
    for metric in plan.metrics:
        val = get(
            f"limits.{metric}",
            None,
        )

        if isinstance(val, int):
            plan.params["limit"] = val
            return

    # group specific limits
    if plan.group:
        val = get(
            f"limits.{plan.group}",
            None,
        )

        if isinstance(val, int):
            plan.params["limit"] = val
            return

    # rows fallback
    val = get(
        "limits.rows",
        get(
            "limits.default",
            None,
        ),
    )

    if isinstance(val, int):
        plan.params["limit"] = val


# -------------------------------------------------
# planner
# -------------------------------------------------

def build_plan(parts):
    plan = QueryPlan()

    for raw in parts:
        part = str(raw).strip()

        if not part:
            continue

        low = tag_norm(part)

        # =====================================
        # key=value
        # =====================================
        if "=" in part:
            key, value = part.split(
                "=",
                1,
            )

            key_l = tag_norm(key)
            val = value.strip()

            # -------------------------
            # dynamic metrics
            # -------------------------
            if key_l == "ratio":
                plan.metrics.append(
                    f"ratio={tag_norm(val)}"
                )
                continue

            if key_l == "sequence":
                plan.metrics.append(
                    f"sequence={val}"
                )
                continue

            # -------------------------
            # universal params
            # -------------------------
            if key_l in (
                "limit",
                "top",
            ):
                plan.params["limit"] = parse_value(
                    val
                )
                continue

            if key_l == "reverse":
                plan.params["reverse"] = parse_value(
                    val
                )
                continue

            # -------------------------
            # display config
            # -------------------------
            if key_l in DISPLAY_ONLY:
                plan.display[key_l] = parse_value(
                    val
                )
                continue

            # -------------------------
            # normal filters
            # -------------------------
            plan.filters.append(
                f"{key_l}={val}"
            )
            continue

        # =====================================
        # transforms
        # =====================================
        if low == "reverse":
            plan.params["reverse"] = True
            continue

        # =====================================
        # field toggles
        # =====================================
        if low in FIELD_EXTRACTORS:
            if plan.selector:
                plan.metrics.append(low)
            else:
                plan.display[low] = True
            continue

        # =====================================
        # display flags
        # =====================================
        if low in DISPLAY_ONLY:
            plan.display[low] = True
            continue

        # =====================================
        # formats
        # =====================================
        if low == "json":
            plan.formats.append(
                "json"
            )
            continue

        # =====================================
        # registry tags
        # =====================================
        meta = REGISTRY.get(low)

        if meta:
            stage = meta.get("stage")

            if stage == "group":
                plan.group = low
                continue

            if stage == "selector":
                plan.selector = low
                continue

            if stage == "metric":
                plan.metrics.append(low)
                continue

        # unknown tags ignored here
        # executor reports errors

    apply_default_limits(plan)

    return plan