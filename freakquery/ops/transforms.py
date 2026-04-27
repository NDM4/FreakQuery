from freakquery.config import get


def apply_transforms(rows, plan, ctx):
    if not isinstance(rows, list):
        return rows

    reverse = plan.params.get("reverse")

    if reverse is None:
        reverse = get(
            "query.reverse",
            True,
        )

    if reverse:
        rows = list(reversed(rows))

    limit = plan.params.get("limit")

    if isinstance(limit, int) and limit >= 0:
        rows = rows[:limit]

    return rows