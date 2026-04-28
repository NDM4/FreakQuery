# src/query/contracts.py

from freakquery.fq_types import (
    LOG_ROWS,
    GROUP_ROWS,
    TEXT_ROWS,
    SCALAR,
    TREND_ROWS,
    TOTAL_ROWS,
    ANY,
    EMPTY,
)


OPERATORS = {

    # -----------------
    # FILTERS
    # -----------------

    "today": {
        "in": LOG_ROWS,
        "out": LOG_ROWS,
        "kind": "filter",
    },

    "week": {
        "in": LOG_ROWS,
        "out": LOG_ROWS,
        "kind": "filter",
    },

    "month": {
        "in": LOG_ROWS,
        "out": LOG_ROWS,
        "kind": "filter",
    },

    "year": {
        "in": LOG_ROWS,
        "out": LOG_ROWS,
        "kind": "filter",
    },

    # -----------------
    # GROUPING
    # -----------------

    "binges": {
        "in": LOG_ROWS,
        "out": GROUP_ROWS,
        "kind": "group",
    },

    "streaks": {
        "in": LOG_ROWS,
        "out": GROUP_ROWS,
        "kind": "group",
    },

    # -----------------
    # SELECTORS
    # -----------------

    "last": {
        "in": LOG_ROWS,
        "out": LOG_ROWS,
        "kind": "selector",
    },

    "first": {
        "in": LOG_ROWS,
        "out": LOG_ROWS,
        "kind": "selector",
    },

    "random": {
        "in": ANY,
        "out": ANY,
        "kind": "selector",
    },

    "largest": {
        "in": GROUP_ROWS,
        "out": LOG_ROWS,
        "kind": "selector",
    },

    "longest": {
        "in": GROUP_ROWS,
        "out": LOG_ROWS,
        "kind": "selector",
    },

    # -----------------
    # METRICS
    # -----------------

    "count": {
        "in": ANY,
        "out": SCALAR,
        "kind": "metric",
    },

    "timeline": {
        "in": LOG_ROWS,
        "out": TEXT_ROWS,
        "kind": "metric",
    },

    "sequence": {
        "in": LOG_ROWS,
        "out": TEXT_ROWS,
        "kind": "metric",
    },

    "dose": {
        "in": LOG_ROWS,
        "out": SCALAR,
        "kind": "metric",
    },

    "substance": {
        "in": LOG_ROWS,
        "out": SCALAR,
        "kind": "metric",
    },

    "since": {
        "in": LOG_ROWS,
        "out": SCALAR,
        "kind": "metric",
    },

    "group_sum": {
        "in": LOG_ROWS,
        "out": SCALAR,
        "kind": "metric",
    },

    "group_duration": {
        "in": LOG_ROWS,
        "out": SCALAR,
        "kind": "metric",
    },

    "main_substance": {
        "in": LOG_ROWS,
        "out": SCALAR,
        "kind": "metric",
    },

    "trend_month": {
        "in": LOG_ROWS,
        "out": TREND_ROWS,
        "kind": "metric",
    },

    "trend_year": {
        "in": LOG_ROWS,
        "out": TREND_ROWS,
        "kind": "metric",
    },

    "substance_totals": {
        "in": LOG_ROWS,
        "out": TOTAL_ROWS,
        "kind": "metric",
    },

    "top_substances": {
        "in": LOG_ROWS,
        "out": TEXT_ROWS,
        "kind": "metric",
    },
}