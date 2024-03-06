"""Simple caching classes, for storing and replaying API responses. This avoids
the need to keep sending requests to the API, which can help with avoiding API
quota limits.

This is intended for development only - it applies no caching logic and simply
stores everything sent to it until you delete the cache storage.
"""

import json
from pathlib import Path


class MemoryCache:
    """A simple in-memory cache (just a wrapper around a Python dict)."""

    def __init__(self):
        self.items = {}

    def get(self, key: str) -> str:
        return self.items[key]

    def set(self, key: str, value: str):
        self.items[key] = value

    def has(self, key: str) -> bool:
        return key in self.items

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, item, value):
        return self.set(item, value)

    def __contains__(self, item):
        return self.has(item)


class FileCache(MemoryCache):
    """A file-based cache that stores new information at the given file path in
    JSON format. If the file doesn't exist, or is corrupt JSON, a new file will
    be created in its place. To clear the cache, delete the file.
    """

    def __init__(self, file_path_str: str):
        self.file_path = Path(file_path_str)

        try:
            with self.file_path.open("r") as file:
                self.items = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            super().__init__()

    def set(self, key: str, value: str):
        super().set(key, value)

        with self.file_path.open("w") as file:
            json.dump(self.items, file)
