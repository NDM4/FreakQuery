# src/outputs/text.py

from datetime import datetime

from freakquery.registry.aliases import (
    display_value,
    norm,
    field_keys,
)

from freakquery.config import get


def clean_number(value):
    try:
        n = float(value)

        if n.is_integer():
            return str(int(n))

        s = str(n)

        if "." in s:
            s = s.rstrip("0").rstrip(".")

        return s
    except:
        return str(value)


def row_get(row, key):
    for wanted in field_keys(key):
        nw = norm(wanted)

        for real in row.keys():
            if norm(real) == nw:
                return row.get(real)

    return None


def format_time(ms, mode):
    try:
        dt = datetime.fromtimestamp(
            int(ms) / 1000
        )
    except:
        return str(ms)

    mode = str(mode).lower()

    if mode == "iso":
        return dt.isoformat(
            timespec="seconds"
        )

    if mode == "date":
        return dt.strftime(
            "%Y-%m-%d"
        )

    return dt.strftime(
        "%H:%M"
    )


def truthy(v, default=True):
    if v is None:
        return default

    if isinstance(v, bool):
        return v

    s = str(v).strip().lower()

    if s in (
        "false",
        "0",
        "no",
        "off",
    ):
        return False

    if s in (
        "true",
        "1",
        "yes",
        "on",
    ):
        return True

    return default


def getd(plan, key, default):
    return plan.display.get(
        key,
        default,
    )


def wrap_count(v, parens):
    if parens:
        return f"({v})"

    return str(v)


def render_ratio_row(
    item,
    labels,
    count,
    percent,
):
    parts = []

    if labels:
        parts.append(
            str(item["value"])
        )

    if percent:
        parts.append(
            str(item["label"])
        )

    if count:
        parts.append(
            str(item["count"])
        )

    return " ".join(
        p for p in parts if p
    ).strip()


def render_text(
    data,
    plan,
    ctx,
):
    if isinstance(
        data,
        (
            str,
            int,
            float,
        ),
    ):
        return str(data)

    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list):
        return str(data)

    if not data:
        return ""

    show_dose = truthy(
        getd(
            plan,
            "dose",
            get(
                "render.dose",
                True,
            ),
        )
    )

    show_unit = truthy(
        getd(
            plan,
            "unit",
            get(
                "render.unit",
                True,
            ),
        )
    )

    show_route = truthy(
        getd(
            plan,
            "route",
            False,
        )
    )

    show_site = truthy(
        getd(
            plan,
            "site",
            False,
        )
    )

    use_parens = truthy(
        getd(
            plan,
            "parens",
            get(
                "render.parens",
                True,
            ),
        )
    )

    show_labels = truthy(
        getd(
            plan,
            "labels",
            get(
                "render.labels",
                True,
            ),
        )
    )

    show_count = truthy(
        getd(
            plan,
            "count",
            get(
                "render.count",
                False,
            ),
        )
    )

    show_percent = truthy(
        getd(
            plan,
            "percent",
            get(
                "render.percent",
                True,
            ),
        )
    )

    compact = truthy(
        getd(
            plan,
            "compact",
            get(
                "render.compact",
                False,
            ),
        )
    )

    sep = str(
        getd(
            plan,
            "sep",
            get(
                "render.separator",
                ", ",
            ),
        )
    )

    time_mode = getd(
        plan,
        "time",
        get(
            "render.time",
            False,
        ),
    )

    lines = []

    for item in data:

        if not isinstance(
            item,
            dict,
        ):
            lines.append(
                str(item)
            )
            continue

        # ratio rows
        if (
            "value" in item
            and "label" in item
        ):
            lines.append(
                render_ratio_row(
                    item,
                    show_labels,
                    show_count,
                    show_percent,
                )
            )
            continue

        # generic value/count rows
        if (
            "value" in item
            and "count" in item
            and "label"
            not in item
        ):
            parts = []

            if show_labels:
                parts.append(
                    display_value(
                        "value",
                        item["value"],
                    )
                )

            if show_count:
                parts.append(
                    str(
                        item["count"]
                    )
                )
            else:
                parts.append(
                    wrap_count(
                        item["count"],
                        use_parens,
                    )
                )

            lines.append(
                " ".join(parts).strip()
            )
            continue

        # top_substances
        if (
            "substance"
            in item
            and "count"
            in item
            and len(item) <= 2
        ):
            left = (
                display_value(
                    "substance",
                    item["substance"],
                )
                if show_labels
                else ""
            )

            right = (
                str(
                    item["count"]
                )
                if show_count
                else wrap_count(
                    item["count"],
                    use_parens,
                )
            )

            lines.append(
                " ".join(
                    x
                    for x in (
                        left,
                        right,
                    )
                    if x
                ).strip()
            )
            continue

        # normal rows
        parts = []

        tm = row_get(
            item,
            "time",
        )

        if (
            time_mode
            and tm
        ):
            parts.append(
                format_time(
                    tm,
                    time_mode,
                )
            )

        sub = row_get(
            item,
            "substance",
        )

        if (
            show_labels
            and sub
        ):
            parts.append(
                display_value(
                    "substance",
                    sub,
                )
            )

        extras = []

        dose = row_get(
            item,
            "dose",
        )

        if (
            show_dose
            and dose is not None
        ):
            d = clean_number(
                dose
            )

            unit = row_get(
                item,
                "unit",
            )

            if (
                show_unit
                and unit
            ):
                d += (
                    " "
                    + display_value(
                        "unit",
                        unit,
                    )
                )

            extras.append(d)

        route = row_get(
            item,
            "route",
        )

        if (
            show_route
            and route
        ):
            extras.append(
                display_value(
                    "route",
                    route,
                )
            )

        site = row_get(
            item,
            "site",
        )

        if (
            show_site
            and site
        ):
            extras.append(
                display_value(
                    "site",
                    site,
                )
            )

        if extras:
            txt = sep.join(
                extras
            )

            if use_parens:
                parts.append(
                    "("
                    + txt
                    + ")"
                )
            else:
                parts.append(
                    txt
                )

        if not parts:
            parts.append(
                str(item)
            )

        if compact:
            lines.append(
                sep.join(parts)
            )
        else:
            lines.append(
                " ".join(parts)
            )

    return "\n".join(lines)