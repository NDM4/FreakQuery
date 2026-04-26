import sys

from freakquery.loader import load_logs
from freakquery.query.executor import execute_tag


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Usage:")
        print("  freakquery <json_file> <tag>")
        print('  freakquery data/New.json "{{count}}"')
        return

    if len(args) < 2:
        print("Error: missing arguments")
        return

    path = args[0]
    tag = args[1]

    data = load_logs(path)

    out = execute_tag(
        tag.strip("{}"),
        data,
        None,
    )

    print(out)