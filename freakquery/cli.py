import sys
from pathlib import Path

from freakquery.loader import load_logs
from freakquery.query.executor import execute_tag
from freakquery.engine import render


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Usage:")
        print('  freakquery <json_file> "{{count}}"')
        print("  freakquery <json_file> <template_file>")
        return

    if len(args) < 2:
        print("Error: missing arguments")
        return

    json_path = args[0]
    target = args[1]

    data = load_logs(json_path)

    # direct tag mode
    if "{{" in target and "}}" in target:
        tag = target.strip()

        if tag.startswith("{{") and tag.endswith("}}"):
            tag = tag[2:-2]

        print(
            execute_tag(
                tag.strip(),
                data,
                None,
            )
        )
        return

    # template mode
    path = Path(target)

    if not path.exists():
        print(f"Error: template file not found: {target}")
        return

    template = path.read_text(encoding="utf-8")

    print(render(template, data))