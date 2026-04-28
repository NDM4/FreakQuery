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

    for raw in parts:
        part = str(raw).strip()
        low = part.lower()

        if "=" in part:
            k, v = part.split("=", 1)
            params[k.strip().lower()] = v.strip()
            continue

        if low in ("today", "week", "month", "year"):
            filters.append(low)
            continue

        if low in ("binges", "streaks"):
            group = low
            continue

        if low in (
            "last",
            "first",
            "random",
            "largest",
            "longest",
        ):
            selector = low
            continue

        if low in FORMAT_PRIORITY:
            formats.append(low)
            continue

        metrics.append(low)

    final_metrics = []

    for m in metrics:
        final_metrics.append(m)
        if m in TERMINAL_METRICS:
            break

    out = []

    out.extend(filters)

    for k, v in params.items():
        out.append(f"{k}={v}")

    if group:
        out.append(group)

    if selector:
        out.append(selector)

    out.extend(final_metrics)

    for fmt in FORMAT_PRIORITY:
        if fmt in formats:
            out.append(fmt)
            break

    return out