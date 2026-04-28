# freakquery/tag_registry.py

from freakquery.fq_types import *

REGISTRY = {

    # =====================================================
    # SELECTORS
    # =====================================================

    "first": {
        "accept": {LOG_ROWS, GROUP_ROWS, TEXT_ROWS},
        "returns": LOG_ROWS,
        "stage": "selector",
        "fn": "first_item",
    },

    "last": {
        "accept": {LOG_ROWS, GROUP_ROWS, TEXT_ROWS},
        "returns": LOG_ROWS,
        "stage": "selector",
        "fn": "last_item",
    },

    "random": {
        "accept": {LOG_ROWS, GROUP_ROWS, TEXT_ROWS},
        "returns": LOG_ROWS,
        "stage": "selector",
        "fn": "random_item",
    },

    # selected group => rows
    "largest": {
        "accept": {GROUP_ROWS},
        "returns": LOG_ROWS,
        "stage": "selector",
        "fn": "largest_group",
    },

    "longest": {
        "accept": {GROUP_ROWS},
        "returns": LOG_ROWS,
        "stage": "selector",
        "fn": "longest_group",
    },

    # =====================================================
    # GROUPING
    # =====================================================

    "binges": {
        "accept": {LOG_ROWS},
        "returns": GROUP_ROWS,
        "stage": "group",
        "fn": "make_binges",
    },

    "streaks": {
        "accept": {LOG_ROWS},
        "returns": GROUP_ROWS,
        "stage": "group",
        "fn": "make_streaks",
    },

    # =====================================================
    # CORE METRICS
    # =====================================================

    "count": {
        "accept": {
            LOG_ROWS,
            GROUP_ROWS,
            TEXT_ROWS,
            TOTAL_ROWS,
            TREND_ROWS,
        },
        "returns": SCALAR,
        "stage": "metric",
        "fn": "count_rows",
    },

    "dose": {
        "accept": {LOG_ROWS},
        "returns": SCALAR,
        "stage": "metric",
        "fn": "dose_value",
    },

    "substance": {
        "accept": {LOG_ROWS},
        "returns": SCALAR,
        "stage": "metric",
        "fn": "substance_value",
    },

    "since": {
        "accept": {LOG_ROWS},
        "returns": SCALAR,
        "stage": "metric",
        "fn": "since_value",
    },

    "sum_dose": {
        "accept": {LOG_ROWS},
        "returns": SCALAR,
        "stage": "metric",
        "fn": "sum_dose_value",
    },

    # =====================================================
    # LIST / RANKING METRICS
    # =====================================================

    "top_substances": {
        "accept": {LOG_ROWS},
        "returns": TEXT_ROWS,
        "stage": "metric",
        "fn": "top_substances_rows",
    },

    "top_routes": {
        "accept": {LOG_ROWS},
        "returns": TEXT_ROWS,
        "stage": "metric",
        "fn": "top_routes_rows",
    },

    "sites": {
        "accept": {LOG_ROWS},
        "returns": TEXT_ROWS,
        "stage": "metric",
        "fn": "sites_rows",
    },

    "substance_totals": {
        "accept": {LOG_ROWS},
        "returns": TOTAL_ROWS,
        "stage": "metric",
        "fn": "substance_totals_rows",
    },

    # =====================================================
    # TIMELINE / TEXT
    # =====================================================

    "timeline": {
        "accept": {LOG_ROWS},
        "returns": TEXT_ROWS,
        "stage": "metric",
        "fn": "timeline_rows",
    },

    "sequence": {
        "accept": {LOG_ROWS},
        "returns": TEXT_ROWS,
        "stage": "metric",
        "fn": "timeline_rows",
    },

    # =====================================================
    # GROUP METRICS
    # =====================================================

    "group_sum": {
        "accept": {LOG_ROWS, GROUP_ROWS},
        "returns": SCALAR,
        "stage": "metric",
        "fn": "group_sum_value",
    },

    "group_duration": {
        "accept": {LOG_ROWS, GROUP_ROWS},
        "returns": SCALAR,
        "stage": "metric",
        "fn": "group_duration_value",
    },

    "group_count": {
        "accept": {LOG_ROWS, GROUP_ROWS},
        "returns": SCALAR,
        "stage": "metric",
        "fn": "group_count_value",
    },

    "main_substance": {
        "accept": {LOG_ROWS, GROUP_ROWS},
        "returns": SCALAR,
        "stage": "metric",
        "fn": "main_substance_value",
    },

    # =====================================================
    # TRENDING
    # =====================================================

    "trend_month": {
        "accept": {LOG_ROWS},
        "returns": TREND_ROWS,
        "stage": "metric",
        "fn": "trend_month_rows",
    },

    "trend_year": {
        "accept": {LOG_ROWS},
        "returns": TREND_ROWS,
        "stage": "metric",
        "fn": "trend_year_rows",
    },
}