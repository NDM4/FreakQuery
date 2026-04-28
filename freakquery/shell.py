# freakquery/shell.py

import os
import sys
import shlex
import time

from freakquery import __version__
from freakquery.loader import load_logs
from freakquery.engine import repl
from freakquery.config import get


HAS_LINE_EDITING = False
readline = None

try:
    import readline
    HAS_LINE_EDITING = True
except Exception:
    try:
        import pyreadline3 as readline
        HAS_LINE_EDITING = True
    except Exception:
        readline = None


LAST_QUERY = None
LAST_RESULT = None


# =====================================================
# CONFIG
# =====================================================

def cfg(key, default=None):
    return get(f"shell.{key}", default)


# =====================================================
# UTILS
# =====================================================

def prompt():
    return str(
        cfg(
            "prompt",
            "fq> ",
        )
    )


def safe_print(*args):
    try:
        print(*args)
    except UnicodeEncodeError:
        txt = " ".join(
            str(x)
            for x in args
        )

        print(
            txt.encode(
                "utf-8",
                "replace",
            ).decode(
                "utf-8",
                "ignore",
            )
        )


def os_label():
    low = sys.platform.lower()

    if "android" in low:
        return "Android"

    if os.name == "nt":
        return "Windows"

    try:
        return os.uname().sysname
    except:
        return sys.platform


def clear_screen():
    mode = str(
        cfg(
            "clear_mode",
            "ansi",
        )
    ).lower()

    if mode == "system":
        os.system(
            "cls"
            if os.name == "nt"
            else "clear"
        )
        return

    print("\033c", end="")


# =====================================================
# HISTORY
# =====================================================

def history_file():
    return str(
        cfg(
            "history_file",
            os.path.expanduser(
                "~/.freakquery_history"
            ),
        )
    )


def setup_history():
    if not HAS_LINE_EDITING:
        return

    if not cfg(
        "history",
        True,
    ):
        return

    try:
        readline.read_history_file(
            history_file()
        )
    except:
        pass

    try:
        readline.set_history_length(
            int(
                cfg(
                    "history_size",
                    5000,
                )
            )
        )
    except:
        pass


def save_history():
    if not HAS_LINE_EDITING:
        return

    if not cfg(
        "history",
        True,
    ):
        return

    try:
        readline.write_history_file(
            history_file()
        )
    except:
        pass


# =====================================================
# AUTOCOMPLETE
# =====================================================

def setup_completion():
    if not HAS_LINE_EDITING:
        return

    if not cfg(
        "autocomplete",
        True,
    ):
        return

    words = [
        "count",
        "last",
        "first",
        "random",
        "largest",
        "longest",
        "binges",
        "streaks",
        "since",
        "dose",
        "substance",
        "top_substances",
        "top_routes",
        "sites",
        "sum_dose",
        "group_count",
        "group_duration",
        "group_sum",
        "main_substance",
        "avg_gap",
        "substances_count",
        "json",
        "reverse",
        "field=",
        "limit=",
        "ratio=",
        ".help",
        ".reload",
        ".clear",
        ".version",
        ".rows",
        ".path",
        ".pwd",
        ".cd",
        ".history",
        ".stats",
        ".time",
        ".last",
        ".watch",
        ".source",
        ".quit",
        ".exit",
    ]

    def complete(text, state):
        matches = [
            w for w in words
            if w.startswith(text)
        ]

        if state < len(matches):
            return matches[state]

        return None

    try:
        readline.set_completer(
            complete
        )
        readline.parse_and_bind(
            "tab: complete"
        )
    except:
        pass


# =====================================================
# BANNER
# =====================================================

def banner(rows, path):
    if not cfg(
        "banner",
        True,
    ):
        return

    safe_print()
    safe_print(
        f"FreakQuery Shell {__version__}"
    )
    safe_print(
        f"Rows: {rows}"
    )
    safe_print(
        f"File: {path}"
    )

    if cfg(
        "show_os",
        True,
    ):
        safe_print(
            f"OS: {os_label()}"
        )

    if cfg(
        "show_python",
        False,
    ):
        safe_print(
            f"Python: {sys.version.split()[0]}"
        )

    safe_print(
        "Type .help"
    )
    safe_print()


# =====================================================
# QUERY
# =====================================================

def normalize_query(q):
    q = str(q).strip()

    if not q:
        return ""

    if (
        len(q) >= 2
        and q[0] == q[-1]
        and q[0] in ("'", '"')
    ):
        q = q[1:-1].strip()

    if (
        q.startswith("{{")
        and q.endswith("}}")
    ):
        q = q[2:-2].strip()

    return q


def run_query(q, data):
    global LAST_QUERY
    global LAST_RESULT

    q = normalize_query(q)

    if not q:
        return ""

    LAST_QUERY = q

    out = repl(q, data)

    if out is None:
        out = ""

    out = str(out)

    LAST_RESULT = out

    safe_print(out)

    return out


# =====================================================
# HELP
# =====================================================

def help_text():
    safe_print()
    safe_print("Commands:")
    safe_print(".help .reload .clear .version")
    safe_print(".rows .path .pwd .cd")
    safe_print(".history .stats .time")
    safe_print(".last .watch .source")
    safe_print(".quit .exit exit quit")
    safe_print()
    safe_print("Examples:")
    safe_print("binges|largest")
    safe_print("binges|longest|group_duration")
    safe_print("streaks|longest|group_duration")
    safe_print("route=oral|count")
    safe_print("top_substances")
    safe_print()


def shell_stats(data):
    for q in (
        "count",
        "last",
        "since",
        "top_substances",
        "top_routes",
    ):
        safe_print()
        safe_print(f"> {q}")
        run_query(q, data)


# =====================================================
# MAIN
# =====================================================

def run_shell(path):
    try:
        data = load_logs(path)
    except Exception as e:
        safe_print(
            "load error:",
            e,
        )
        return

    setup_history()
    setup_completion()

    banner(
        len(data),
        path,
    )

    while True:
        try:
            raw = input(prompt())
        except KeyboardInterrupt:
            safe_print()
            continue
        except EOFError:
            safe_print()
            break

        q = raw.strip()

        if not q:
            continue

        low = q.lower()

        # -----------------------------
        # exit
        # -----------------------------
        if low in (
            ".quit",
            ".exit",
            ":q",
            "quit",
            "exit",
        ):
            break

        # -----------------------------
        # meta
        # -----------------------------
        if low == ".help":
            help_text()
            continue

        if low in (
            ".clear",
            ".cls",
        ):
            clear_screen()
            continue

        if low == ".reload":
            try:
                data = load_logs(path)
                safe_print(
                    f"reloaded {len(data)} rows"
                )
            except Exception as e:
                safe_print(
                    "reload error:",
                    e,
                )
            continue

        if low == ".version":
            safe_print(
                f"FreakQuery {__version__}"
            )
            continue

        if low == ".rows":
            safe_print(len(data))
            continue

        if low == ".path":
            safe_print(path)
            continue

        if low == ".pwd":
            safe_print(os.getcwd())
            continue

        if low.startswith(".cd"):
            try:
                parts = shlex.split(q)

                target = (
                    parts[1]
                    if len(parts) > 1
                    else "~"
                )

                os.chdir(
                    os.path.expanduser(
                        target
                    )
                )

                safe_print(
                    os.getcwd()
                )

            except Exception as e:
                safe_print(
                    "cd error:",
                    e,
                )

            continue

        if low == ".history":
            if HAS_LINE_EDITING:
                try:
                    n = readline.get_current_history_length()

                    for i in range(
                        1,
                        n + 1,
                    ):
                        item = readline.get_history_item(i)

                        if item:
                            safe_print(
                                f"{i}: {item}"
                            )
                except:
                    pass
            continue

        if low == ".stats":
            shell_stats(data)
            continue

        if low == ".last":
            if LAST_QUERY:
                run_query(
                    LAST_QUERY,
                    data,
                )
            continue

        if low == ".source":
            try:
                st = os.stat(path)

                safe_print(path)
                safe_print(
                    f"{len(data)} rows"
                )
                safe_print(
                    time.ctime(
                        st.st_mtime
                    )
                )
            except:
                safe_print(path)

            continue

        if low.startswith(".time "):
            real = q[6:].strip()

            t0 = time.perf_counter()

            run_query(real, data)

            dt = round(
                time.perf_counter() - t0,
                int(
                    cfg(
                        "timing_precision",
                        3,
                    )
                ),
            )

            safe_print(
                f"({dt}s)"
            )

            continue

        if low.startswith(".watch "):
            arg = q[7:].strip()

            interval = float(
                cfg(
                    "watch_interval",
                    2,
                )
            )

            if " " in arg:
                a, b = arg.split(
                    " ",
                    1,
                )

                try:
                    interval = float(a)
                    arg = b.strip()
                except:
                    pass

            try:
                while True:
                    if cfg(
                        "watch_clear",
                        False,
                    ):
                        clear_screen()

                    run_query(
                        arg,
                        data,
                    )

                    time.sleep(
                        interval
                    )

            except KeyboardInterrupt:
                safe_print()

            continue

        # -----------------------------
        # query
        # -----------------------------
        try:
            run_query(q, data)
        except KeyboardInterrupt:
            safe_print()
        except Exception as e:
            safe_print(
                "error:",
                e,
            )

    save_history()
    safe_print("bye")