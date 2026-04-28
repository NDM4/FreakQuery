import json
import difflib

from freakquery.config import get
from freakquery.tag_registry import REGISTRY

from freakquery.query.parser import parse_tag
from freakquery.registry.aliases import (
    apply_aliases,
    field_keys,
    norm,
)
from freakquery.query.precedence import normalize_parts
from freakquery.query.validator import validate_parts
from freakquery.query.planner import build_plan

from freakquery.ops.filters import apply_filters
from freakquery.ops.grouping import apply_grouping
from freakquery.ops.selectors import apply_selectors
from freakquery.ops.metrics import apply_metrics
from freakquery.ops.transforms import apply_transforms

from freakquery.outputs.text import render_text
from freakquery.outputs.json import render_json


VERSION = get("core.version", "0.0.0")


# =====================================================
# HELPERS
# =====================================================

def unknown_error(raw):
    guess = difflib.get_close_matches(
        raw.lower(),
        REGISTRY.keys(),
        n=1,
        cutoff=0.65,
    )

    if guess:
        return (
            f"[error: unknown query '{raw}' "
            f"(did you mean '{guess[0]}'?)]"
        )

    return f"[error: unknown query '{raw}']"


def empty_plan(plan):
    return not any([
        plan.filters,
        plan.group,
        plan.selector,
        plan.metrics,
        plan.formats,
    ])


def clean_number(value):
    try:
        n = float(value)

        if n.is_integer():
            return str(int(n))

        s = str(n).rstrip("0").rstrip(".")
        return s
    except:
        return str(value)


def row_get(row, key):
    if not isinstance(row, dict):
        return None

    for wanted in field_keys(key):
        nw = norm(wanted)

        for real in row.keys():
            if norm(real) == nw:
                return row.get(real)

    return None


# =====================================================
# MAIN
# =====================================================

def execute_tag(tag, data, ctx):
    raw = str(tag).strip()

    if not raw:
        return ""

    low = raw.lower()

    # meta
    if low == "version":
        return VERSION

    if low in ("version|json", "json|version"):
        return json.dumps(
            {"version": VERSION},
            ensure_ascii=False,
            indent=2,
        )

    # parse
    parts = parse_tag(raw)
    parts = apply_aliases(parts)
    parts = normalize_parts(parts)

    ok, err = validate_parts(parts)

    if not ok:
        return f"[error:{err}]"

    plan = build_plan(parts)

    if empty_plan(plan):
        return unknown_error(raw)

    # detect field=
    wanted_field = None

    for p in parts:
        if p.lower().startswith("field="):
            wanted_field = p.split("=", 1)[1].strip()
            break

    # pipeline
    rows = list(data)

    rows = apply_filters(rows, plan, ctx)
    rows = apply_grouping(rows, plan, ctx)
    rows = apply_selectors(rows, plan, ctx)

    # =====================================
    # UNIVERSAL field=
    # after selectors
    # before metrics
    # =====================================

    if wanted_field is not None:
        if not rows:
            return ""

        row = rows[0]

        val = row_get(row, wanted_field)

        if val is None:
            return ""

        return clean_number(val)

    # continue normal flow
    rows = apply_metrics(rows, plan, ctx)
    rows = apply_transforms(rows, plan, ctx)

    # output
    if "json" in plan.formats:
        out = render_json(rows, plan, ctx)
    else:
        out = render_text(rows, plan, ctx)

    return str(out).rstrip()