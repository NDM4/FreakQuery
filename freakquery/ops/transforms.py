def apply_transforms(rows, plan, ctx):
    if not isinstance(rows, list):
        return rows

    limit = plan.params.get("limit")
    if isinstance(limit, int):
        rows = rows[:limit]

    top = plan.params.get("top")
    if isinstance(top, int):
        rows = rows[:top]

    return rows