"""Simple caching class, for storing and replaying API responses. This avoids
the need to keep sending requests to the API, which can help with avoiding API
quota limits.
"""

import json
from pathlib import Path


class FileCache:
    """A file-based cache that stores new information at the given file path in
    JSON format. If the file doesn't exist, or is corrupt JSON, a new file will
    be created in its place. To clear the cache, delete the file.
    """

    def __init__(self, file_path_str: str):
        self.file_path = Path(file_path_str)
        self.items = {}

        try:
            with self.file_path.open("r") as file:
                self.items = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            pass

    def get(self, key: str) -> str:
        return self.items[key]

    def set(self, key: str, value: str):
        self.items[key] = value

        with self.file_path.open("w") as file:
            json.dump(self.items, file)

    def has(self, key: str) -> bool:
        return key in self.items

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, item, value):
        return self.set(item, value)

    def __contains__(self, item):
        return self.has(item)
