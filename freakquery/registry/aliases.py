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
    fields = get("fields", {})

    wanted = norm(key)

    # recorrer grupos
    for canonical, vals in fields.items():

        names = [canonical]

        if isinstance(vals, list):
            names.extend(vals)
        else:
            names.append(vals)

        # si coincide cualquiera
        for x in names:
            if norm(x) == wanted:
                return names

    return [key]


def alias_map(field):
    aliases = get(
        "aliases",
        {},
    )

    return aliases.get(
        norm(field),
        {},
    )


def canonical_field(field, value):
    mp = alias_map(field)

    raw = "" if value is None else str(value).strip()
    v = norm(raw)

    return mp.get(v, raw)


def canonical_route(value):
    return canonical_field(
        "route",
        value,
    )


def canonical_site(value):
    return canonical_field(
        "site",
        value,
    )


def canonical_value(
    field,
    value,
):
    return canonical_field(
        field,
        value,
    )


def same_value(
    field,
    a,
    b,
):
    return (
        canonical_value(field, a)
        ==
        canonical_value(field, b)
    )


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