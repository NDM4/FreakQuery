import random

from freakquery.rows import row_time
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


def is_groups(rows):
    return bool(rows) and isinstance(rows[0], list)


def apply_selectors(rows, plan, ctx):
    mode = norm(plan.selector)

    if not mode:
        return rows

    rows = list(rows)

    if not rows:
        return rows

    grouped = is_groups(rows)

    # -------------------
    # GROUP MODE
    # -------------------
    if grouped:

        if mode == SEL_FIRST:
            return rows[0]

        if mode == SEL_LAST:
            return rows[-1]

        if mode == SEL_RANDOM:
            return random.choice(rows)

        if mode == SEL_LARGEST:
            return max(rows, key=group_sum)

        if mode == SEL_LONGEST:
            return max(rows, key=group_duration)

        return rows

    # -------------------
    # NORMAL ROW MODE
    # -------------------
    if mode == SEL_FIRST:
        return [min(rows, key=row_time)]

    if mode == SEL_LAST:
        return [max(rows, key=row_time)]

    if mode == SEL_RANDOM:
        return [random.choice(rows)]

    return rows
