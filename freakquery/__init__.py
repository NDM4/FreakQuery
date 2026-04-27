from freakquery.config import get
from freakquery.loader import load_logs
from freakquery.engine import render as _render
from freakquery.query.executor import execute_tag


__version__ = get(
    "core.version",
    "0.0.0",
)

__title__ = get(
    "core.name",
    "freakquery",
)


def _resolve_source(source):
    if isinstance(source, str):
        return load_logs(source)
    return source


def render(template, source):
    """
    Render template containing {{tags}}.

    source:
      - path to json
      - loaded rows
    """
    data = _resolve_source(source)
    return _render(template, data)


def query(tag, source):
    """
    Execute query/tag.
    """
    data = _resolve_source(source)

    tag = str(tag).strip()

    if tag.startswith("{{") and tag.endswith("}}"):
        tag = tag[2:-2].strip()

    return execute_tag(
        tag,
        data,
        None,
    )


__all__ = [
    "__title__",
    "__version__",
    "render",
    "query",
]