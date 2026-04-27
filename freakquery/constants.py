# src/constants.py

# formats
FMT_JSON = "json"
FMT_PRETTY = "pretty"
FMT_BULLETS = "bullets"
FMT_NUMBERED = "numbered"

FORMATS = {
    FMT_JSON,
    FMT_PRETTY,
    FMT_BULLETS,
    FMT_NUMBERED,
}

# params
PARAM_LIMIT = "limit"
PARAM_TOP = "top"
PARAM_REVERSE = "reverse"

PARAMS = {
    PARAM_LIMIT,
    PARAM_TOP,
    PARAM_REVERSE,
}

# metric prefixes
PREFIX_RATIO = "ratio"

METRIC_PREFIXES = {
    PREFIX_RATIO,
}

# selectors
SEL_FIRST = "first"
SEL_LAST = "last"
SEL_RANDOM = "random"
SEL_LARGEST = "largest"
SEL_LONGEST = "longest"

# groups
GRP_BINGES = "binges"
GRP_STREAKS = "streaks"