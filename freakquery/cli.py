import json
import sys

from freakquery import (
    __title__,
    __version__,
)

from freakquery.loader import load_logs
from freakquery.engine import repl
from freakquery.shell import run_shell


def usage():
    name = __title__.lower()

    print("usage:")
    print(f"{name} <file.json> <query>")
    print(f"{name} shell <file.json>")
    print(f"{name} --version")


def main():
    args = sys.argv[1:]

    if not args:
        usage()
        return

    if args[0] in (
        "--version",
        "-V",
        "version",
    ):
        print(f"{__title__} {__version__}")
        return

    if args[0] in ("--help", "-h", "help"):
        usage()
        print()
        print("queries:")
        print("  count                        count all rows")
        print("  last                         show most recent row")
        print("  first                        show earliest row")
        print("  last|dose                    show most recent dose")
        print("  route=oral|count             count rows where route is oral")
        print("  ratio=route                  show route breakdown")
        print("  top_substances               rank substances by count")
        print("  sequence                     show substance sequence")
        print("  binges|largest|group_duration duration of largest binge")
        print()
        print("filters:  today, week, month, year, substance=..., route=...")
        print("groups:   binges, streaks")
        print("selectors: first, last, random, largest, longest")
        print("formats:  json")
        print()
        print("shell: freakquery shell <file.json>")
        return

    if args[0] == "shell":
        if len(args) < 2:
            print("error: missing file path")
            print("usage: freakquery shell <file.json>")
            return

        path = args[1]

        try:
            run_shell(path)
        except FileNotFoundError:
            print(f"error: file not found: {path}")
        except Exception as e:
            print(f"error: {e}")
        return

    if len(args) < 2:
        print("error: missing query")
        print("usage: freakquery <file.json> <query>")
        return

    path = args[0]
    query_str = args[1]

    try:
        data = load_logs(path)
    except FileNotFoundError:
        print(f"error: file not found: {path}")
        return
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON in {path}: {e}")
        return
    except Exception as e:
        print(f"error: {e}")
        return

    if not data:
        print("error: no data found in file")
        return

    try:
        out = repl(query_str, data)
        print(out)
    except Exception as e:
        print(f"error: {e}")


if __name__ == "__main__":
    main()