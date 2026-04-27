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
        print(
            f"{__title__} {__version__}"
        )
        return

    if args[0] == "shell":
        if len(args) < 2:
            print("missing file")
            return

        run_shell(args[1])
        return

    if len(args) < 2:
        print("missing query")
        return

    path = args[0]
    query = args[1]

    data = load_logs(path)

    out = repl(
        query,
        data,
    )

    print(out)


if __name__ == "__main__":
    main()