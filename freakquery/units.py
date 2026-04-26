# src/units.py

MASS_UNITS = {
    "ug",
    "mcg",
    "μg",
    "µg",
    "mg",
    "g",
}


def clean_unit(unit):
    if unit is None:
        return ""

    return str(unit).strip().lower()


def is_mass_unit(unit):
    return clean_unit(unit) in MASS_UNITS


def to_mg(value, unit):
    u = clean_unit(unit)

    try:
        x = float(value)
    except:
        return 0.0

    if u in ("ug", "mcg", "μg", "µg"):
        return x / 1000

    if u == "mg":
        return x

    if u == "g":
        return x * 1000

    return x


def normalize_custom_unit(unit):
    u = clean_unit(unit)

    # naive singularization
    if u.endswith("s") and len(u) > 1:
        u = u[:-1]

    return u