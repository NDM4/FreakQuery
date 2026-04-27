import re
import traceback

from freakquery.query.context import Context
from freakquery.query.executor import execute_tag


TAG_RE = re.compile(
    r"\{\{(.*?)\}\}",
    re.DOTALL,
)


def repl(query, data):
    ctx = Context(data)

    return execute_tag(
        str(query).strip(),
        data,
        ctx,
    )


def render(
    template,
    data,
):
    ctx = Context(data)

    def replace(match):
        tag = match.group(1).strip()

        try:
            return str(
                execute_tag(
                    tag,
                    data,
                    ctx,
                )
            )

        except Exception:
            print(
                f"\n--- ERROR IN TAG: {tag} ---"
            )
            traceback.print_exc()

            return f"[error:{tag}]"

    return TAG_RE.sub(
        replace,
        template,
    )