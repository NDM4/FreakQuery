# src/engine.py

import re
import traceback

from freakquery.query.context import Context
from freakquery.query.executor import execute_tag


TAG_RE = re.compile(
    r"\{\{(.*?)\}\}",
    re.DOTALL,
)


def render(
    template,
    data,
):
    ctx = Context(data)

    def repl(match):
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

            return (
                f"[error:{tag}]"
            )

    return TAG_RE.sub(
        repl,
        template,
    )