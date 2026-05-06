# src/cache.py

import json
from typing import Any


class Cache:
    def __init__(self):
        self.store = {}

    def _key(self, *parts):
        raw = json.dumps(
            parts,
            sort_keys=True,
            default=str,
        )

        return str(hash(raw))

    def get(self, *parts) -> Any:
        key = self._key(*parts)
        return self.store.get(key)

    def set(self, value, *parts) -> Any:
        key = self._key(*parts)
        self.store[key] = value
        return value

    def remember(self, fn, *parts) -> Any:
        cached = self.get(*parts)

        if cached is not None:
            return cached

        value = fn()
        return self.set(value, *parts)

    def clear(self):
        self.store.clear()


CACHE = Cache()