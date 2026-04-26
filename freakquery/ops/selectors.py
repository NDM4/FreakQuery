# src/ops/selectors.py

import random

from freakquery.constants import (
    SEL_FIRST,
    SEL_LAST,
    SEL_RANDOM,
    SEL_LARGEST,
    SEL_LONGEST,
)

from freakquery.ops.grouping import (
    group_duration,
    group_sum,
)


def norm(x):
    return str(x).strip().lower()


def row_time(row):
    try:
        return int(row.get("time", 0))
    except:
        return 0


def apply_selectors(rows, plan, ctx):
    mode = norm(plan.selector)

    if not mode:
        return rows

    rows = list(rows)

    if not rows:
        return rows

    sel_first = norm(SEL_FIRST)
    sel_last = norm(SEL_LAST)
    sel_random = norm(SEL_RANDOM)
    sel_largest = norm(SEL_LARGEST)
    sel_longest = norm(SEL_LONGEST)

    # chronological
    if mode == sel_last:
        return [max(rows, key=row_time)]

    if mode == sel_first:
        return [min(rows, key=row_time)]

    if mode == sel_random:
        return [random.choice(rows)]

    # grouped
    if mode in (
        sel_largest,
        sel_longest,
    ):
        groups = rows

        if not isinstance(groups[0], list):
            return rows

        if mode == sel_largest:
            return max(
                groups,
                key=group_sum,
            )

        if mode == sel_longest:
            return max(
                groups,
                key=group_duration,
            )

    return rows