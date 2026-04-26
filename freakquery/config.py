from pathlib import Path
try:
    import tomllib
except Exception:
    import tomli as tomllib

DEFAULT_CONFIG = {
    "core": {
        "name": "freakquery",
        "version": "3.0.0",
        "default_format": "text",
    },
    "render": {
        "separator": ", ",
        "parens": True,
        "dose": True,
        "unit": True,
        "labels": True,
        "count": False,
        "percent": True,
        "compact": False,
        "time": False,
        "ratio_under_one": "<1%",
    },
    "fields": {},
    "aliases": {
        "route": {},
        "site": {},
    },
}

_CONFIG = None

def deep_merge(a, b):
    out = dict(a)
    for k, v in b.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out

def load_config(path="config.toml"):
    global _CONFIG
    if _CONFIG is not None:
        return _CONFIG
    cfg = dict(DEFAULT_CONFIG)
    p = Path(path)
    if p.exists():
        with p.open("rb") as f:
            user = tomllib.load(f)
        cfg = deep_merge(cfg, user)
    _CONFIG = cfg
    return cfg

def get(path, default=None):
    cfg = load_config()
    cur = cfg
    for part in path.split("."):
        if not isinstance(cur, dict):
            return default
        if part not in cur:
            return default
        cur = cur[part]
    return cur
