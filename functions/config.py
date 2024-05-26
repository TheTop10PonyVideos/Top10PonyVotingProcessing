"""Functions for managing application configuration."""

import json
from pathlib import Path


def load_config_json(config_file_path_str: str) -> dict:
    """Load the given JSON file and return the resulting object."""
    config_file_path = Path(config_file_path_str)

    with config_file_path.open() as config_file:
        config = json.load(config_file)

    return config
