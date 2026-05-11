import json
from pathlib import Path

class DataManager:
    """Handles all JSON file persistence logic."""
    @staticmethod
    def load(path, default):
        """Reads data from a JSON file or returns default if not found."""
        if Path(path).exists():
            with open(path, "r") as f:
                return json.load(f)
        return default

    @staticmethod
    def save(path, data):
        """Writes data to a JSON file with proper indentation."""
        with open(path, "w") as f:
            json.dump(data, f, indent=4)