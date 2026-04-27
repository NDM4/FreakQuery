# freakquery/query_plan.py

from dataclasses import dataclass, field


@dataclass
class QueryPlan:
    group: str | None = None
    selector: str | None = None

    filters: list = field(default_factory=list)
    metrics: list = field(default_factory=list)
    formats: list = field(default_factory=list)
    params: dict = field(default_factory=dict)

    # nuevo
    unknown: list = field(default_factory=list)

    display: dict = field(
        default_factory=lambda: {
            "dose": True,
            "unit": True,
            "route": False,
            "site": False,
            "parens": True,
            "time": False,
            "labels": True,
            "count": False,
            "percent": True,
            "compact": False,
            "sep": ", ",
        }
    )