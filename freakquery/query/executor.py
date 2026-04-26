# src/query/executor.py

import json

from freakquery.constants import VERSION

from freakquery.query.parser import parse_tag
from freakquery.registry.aliases import apply_aliases
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


def execute_tag(
    tag,
    data,
    ctx,
):
    raw = str(tag).strip()
    low = raw.lower()

    # ----------------------------
    # META TAGS
    # ----------------------------
    if low == "version":
        return VERSION

    if low in (
        "version|json",
        "json|version",
    ):
        return json.dumps(
            {
                "version": VERSION
            },
            ensure_ascii=False,
            indent=2,
        )

    # ----------------------------
    # PARSE
    # ----------------------------
    parts = parse_tag(raw)

    # aliases
    parts = apply_aliases(parts)

    # precedence normalize
    parts = normalize_parts(parts)

    # validate
    ok, err = validate_parts(parts)

    if not ok:
        return f"[error:{err}]"

    # plan
    plan = build_plan(parts)

    # ----------------------------
    # EXECUTION PIPELINE
    # ----------------------------
    rows = list(data)

    rows = apply_filters(
        rows,
        plan,
        ctx,
    )

    rows = apply_grouping(
        rows,
        plan,
        ctx,
    )

    rows = apply_selectors(
        rows,
        plan,
        ctx,
    )

    rows = apply_metrics(
        rows,
        plan,
        ctx,
    )

    rows = apply_transforms(
        rows,
        plan,
        ctx,
    )

    # ----------------------------
    # OUTPUT FORMAT
    # ----------------------------
    if "json" in plan.formats:
        out = render_json(
            rows,
            plan,
            ctx,
        )
    else:
        out = render_text(
            rows,
            plan,
            ctx,
        )

    # ----------------------------
    # SAFE RETURN
    # ----------------------------
    if out is None:
        return ""

    return str(out).rstrip()