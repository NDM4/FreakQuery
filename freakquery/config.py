from pathlib import Path

try:
    import tomllib
except Exception:
    import tomli as tomllib


_CONFIG = None


def config_path():
    return (
        Path(__file__)
        .resolve()
        .parent.parent
        / "config.toml"
    )


def load_config(force=False):
    global _CONFIG

    if _CONFIG is not None and not force:
        return _CONFIG

    path = config_path()

    if not path.exists():
        _CONFIG = {}
        return _CONFIG

    with path.open("rb") as f:
        _CONFIG = tomllib.load(f)

    return _CONFIG


def reload_config():
    return load_config(True)


def get(path, default=None):
    cur = load_config()

    for part in path.split("."):
        if not isinstance(cur, dict):
            return default

        if part not in cur:
            return default

        cur = cur[part]

    return cur