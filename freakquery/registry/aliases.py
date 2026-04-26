# src/registry/aliases.py

import unicodedata

from freakquery.config import get


def norm(x):
    if x is None:
        return ""

    s = str(x).strip().lower()

    s = "".join(
        c for c in unicodedata.normalize(
            "NFKD",
            s,
        )
        if not unicodedata.combining(c)
    )

    for ch in (
        "_",
        "-",
        ".",
        ",",
        ";",
        ":",
        "/",
        "\\",
        "|",
        "(",
        ")",
        "[",
        "]",
        "{",
        "}",
    ):
        s = s.replace(ch, " ")

    return " ".join(s.split())


def field_keys(key):
    fields = get(
        "fields",
        {},
    )

    k = norm(key)

    for fk, vals in fields.items():
        if norm(fk) == k:
            return vals

    return [key]


def canonical_route(value):
    mp = get(
        "aliases.route",
        {},
    )

    v = norm(value)

    return mp.get(v, v)


def canonical_site(value):
    mp = get(
        "aliases.site",
        {},
    )

    v = norm(value)

    return mp.get(v, v)


def canonical_value(
    field,
    value,
):
    f = norm(field)

    if f == "route":
        return canonical_route(
            value
        )

    if f == "site":
        return canonical_site(
            value
        )

    return norm(value)


def display_value(
    field,
    value,
):
    return canonical_value(
        field,
        value,
    )


# backward compatibility
def normalize_route(v):
    return canonical_route(v)


def normalize_site(v):
    return canonical_site(v)


def apply_aliases(parts):
    return parts