# src/query/precedence.py

TERMINAL_METRICS = {
    "count",
    "dose",
    "substance",
    "since",
    "group_sum",
    "group_duration",
    "main_substance",
}

FORMAT_PRIORITY = [
    "json",
    "pretty",
    "numbered",
    "bullets",
    "lines",
]


def normalize_parts(parts):
    filters = []
    params = {}
    group = None
    selector = None
    metrics = []
    formats = []

    for part in parts:

        if "=" in part:
            k, v = part.split("=", 1)
            params[k] = v
            continue

        if part in (
            "today",
            "week",
            "month",
            "year",
        ):
            filters.append(part)
            continue

        if part in (
            "binges",
            "streaks",
        ):
            group = part
            continue

        if part in (
            "last",
            "first",
            "random",
            "largest",
            "longest",
        ):
            selector = part
            continue

        if part in FORMAT_PRIORITY:
            formats.append(part)
            continue

        metrics.append(part)

    # terminal metric corta cadena
    final_metrics = []

    for m in metrics:
        final_metrics.append(m)
        if m in TERMINAL_METRICS:
            break

    out = []

    # 1 filters
    out.extend(filters)

    # 2 params
    for k, v in params.items():
        out.append(f"{k}={v}")

    # 3 group
    if group:
        out.append(group)

    # 4 selector
    if selector:
        out.append(selector)

    # 5 metrics
    out.extend(final_metrics)

    # 6 format winner
    for fmt in FORMAT_PRIORITY:
        if fmt in formats:
            out.append(fmt)
            break

    return out