# src/cache.py

import hashlib
import json


class Cache:
    def __init__(self):
        self.store = {}

    def _key(self, *parts):
        raw = json.dumps(
            parts,
            sort_keys=True,
            default=str,
        )

        return hashlib.md5(
            raw.encode("utf-8")
        ).hexdigest()

    def get(self, *parts):
        key = self._key(*parts)
        return self.store.get(key)

    def set(self, value, *parts):
        key = self._key(*parts)
        self.store[key] = value
        return value

    def remember(self, fn, *parts):
        cached = self.get(*parts)

        if cached is not None:
            return cached

        value = fn()
        return self.set(value, *parts)

    def clear(self):
        self.store.clear()


CACHE = Cache()