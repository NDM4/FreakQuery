from freakquery.loader import load_logs
from freakquery.engine import render
from freakquery.query.executor import execute_tag


def render_template(template, source):
    """
    Render a template string containing {{tags}}.

    source can be:
    - path to json file
    - already loaded list of dict rows
    """
    if isinstance(source, str):
        data = load_logs(source)
    else:
        data = source

    return render(template, data)


def query(tag, source):
    """
    Execute a single tag/query.

    Example:
        query("count", "data.json")
        query("route=oral|count", rows)
    """
    if isinstance(source, str):
        data = load_logs(source)
    else:
        data = source

    tag = str(tag).strip()

    if tag.startswith("{{") and tag.endswith("}}"):
        tag = tag[2:-2].strip()

    return execute_tag(tag, data, None)