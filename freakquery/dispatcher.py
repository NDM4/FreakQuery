from freakquery.tag_registry import REGISTRY
from freakquery.query_plan import QueryPlan

from freakquery.ops.grouping import apply_grouping
from freakquery.ops.selectors import apply_selectors
from freakquery.ops.metrics import apply_metrics


def dispatch(rows, part, ctx):
    meta = REGISTRY.get(part)

    if not meta:
        plan = QueryPlan()
        plan.metrics = [part]
        return apply_metrics(rows, plan, ctx)

    stage = meta["stage"]

    plan = QueryPlan()

    if stage == "group":
        plan.groups = [part]
        return apply_grouping(rows, plan, ctx)

    if stage == "selector":
        plan.selectors = [part]
        return apply_selectors(rows, plan, ctx)

    plan.metrics = [part]
    return apply_metrics(rows, plan, ctx)