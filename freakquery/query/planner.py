# src/query/planner.py

from freakquery.query_plan import QueryPlan
from freakquery.constants import (
    FORMATS,
    PARAMS,
    METRIC_PREFIXES,
    SEL_FIRST,
    SEL_LAST,
    SEL_RANDOM,
    SEL_LARGEST,
    SEL_LONGEST,
    GRP_BINGES,
    GRP_STREAKS,
)


def norm(x):
    return str(x).strip().lower()


# -------------------------------------------------
# PRESENTATION FLAGS (bare tokens only)
# route / site without "=" are display flags
# -------------------------------------------------
DISPLAY_KEYS = {
    "dose",
    "unit",
    "route",
    "site",
    "parens",
    "time",
    "labels",
    "percent",
    "compact",
    "sep",
}


# key=value display only
DISPLAY_KV_ONLY = {
    "count",
}


# safe key=value display params
DISPLAY_ASSIGN_KEYS = {
    "dose",
    "unit",
    "parens",
    "time",
    "labels",
    "percent",
    "compact",
    "sep",
}


# -------------------------------------------------
# SELECTORS
# -------------------------------------------------
SELECTORS = {
    norm(SEL_FIRST),
    norm(SEL_LAST),
    norm(SEL_RANDOM),
    norm(SEL_LARGEST),
    norm(SEL_LONGEST),
}


# -------------------------------------------------
# GROUPS
# -------------------------------------------------
GROUPS = {
    norm(GRP_BINGES),
    norm(GRP_STREAKS),
}


# -------------------------------------------------
# NORMALIZED SETS
# -------------------------------------------------
FORMAT_SET = {
    norm(x) for x in FORMATS
}

PARAM_SET = {
    norm(x) for x in PARAMS
}

PREFIX_SET = {
    norm(x) for x in METRIC_PREFIXES
}


# -------------------------------------------------
# VALUE PARSER
# -------------------------------------------------
def parse_value(v):
    raw = str(v).strip()
    low = raw.lower()

    if low in (
        "true",
        "1",
        "yes",
        "on",
        "enabled",
    ):
        return True

    if low in (
        "false",
        "0",
        "no",
        "off",
        "disabled",
    ):
        return False

    if low in (
        "none",
        "null",
        "nil",
    ):
        return None

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
# MAIN
# -------------------------------------------------
def build_plan(parts):
    plan = QueryPlan()

    for raw in parts:
        part = str(raw).strip()

        if not part:
            continue

        low = norm(part)

        # -----------------------------------------
        # key=value
        # IMPORTANT:
        # route=oral / site=left nostril are FILTERS
        # route / site (without =) are DISPLAY FLAGS
        # -----------------------------------------
        if "=" in part:
            key, value = part.split(
                "=",
                1,
            )

            key_l = norm(key)
            parsed = parse_value(value)

            # safe display assignments only
            if key_l in DISPLAY_ASSIGN_KEYS:
                plan.display[key_l] = parsed
                continue

            # kv-only display flags
            if key_l in DISPLAY_KV_ONLY:
                plan.display[key_l] = parsed
                continue

            # metric prefixes
            # ratio=route
            if key_l in PREFIX_SET:
                plan.metrics.append(
                    key_l
                    + "="
                    + norm(value)
                )
                continue

            # params
            if key_l in PARAM_SET:
                plan.params[key_l] = parsed
                continue

            # default = filter
            plan.filters.append(
                key_l
                + "="
                + str(value).strip()
            )
            continue

        # -----------------------------------------
        # bare display flags
        # -----------------------------------------
        if low in DISPLAY_KEYS:
            plan.display[low] = True
            continue

        # -----------------------------------------
        # formats
        # -----------------------------------------
        if low in FORMAT_SET:
            plan.formats.append(low)
            continue

        # -----------------------------------------
        # selectors
        # -----------------------------------------
        if low in SELECTORS:
            plan.selector = low
            continue

        # -----------------------------------------
        # groups
        # -----------------------------------------
        if low in GROUPS:
            plan.group = low
            continue

        # -----------------------------------------
        # fallback = metric
        # -----------------------------------------
        plan.metrics.append(low)

    return plan