# src/query_plan.py

from dataclasses import dataclass, field


@dataclass
class QueryPlan:
    # query semantics
    group: str | None = None
    selector: str | None = None

    filters: list = field(default_factory=list)
    metrics: list = field(default_factory=list)
    formats: list = field(default_factory=list)
    params: dict = field(default_factory=dict)

    # presentation semantics
    display: dict = field(
        default_factory=lambda: {
            "dose": True,
            "unit": True,
            "route": False,
            "parens": True,
            "time": False,
        }
    )