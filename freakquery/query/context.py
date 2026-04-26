# src/query/context.py

import time

from freakquery.cache import CACHE


class Context:
    def __init__(self, logs):
        self.logs = logs or []
        self.cache = CACHE

        self.now_ms = int(
            time.time() * 1000
        )

        # random consistente entre tags
        self.memory = {}

        # configuración futura
        self.settings = {
            "default_limit": None,
            "pretty_numbers": True,
        }

    def remember(self, key, value):
        self.memory[key] = value
        return value

    def recall(self, key, default=None):
        return self.memory.get(
            key,
            default
        )

    def has(self, key):
        return key in self.memory