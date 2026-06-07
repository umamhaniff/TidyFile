import json
import logging
from pathlib import Path

logger = logging.getLogger("TidyFile")

DEFAULT_CONFIG = {
    "target_folders": [str(Path.home() / "Downloads")],
    "categories": {
        "Documents": [
            ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", 
            ".txt", ".rtf", ".odt", ".ods", ".odp", ".csv", ".md"
        ],
        "Images": [
            ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"
        ]
    },
    "default_category": "Others"
}

class ConfigManager:
    def __init__(self, config_path: Path):
        self.config_path = Path(config_path)
        self.target_folders = []
        self.categories = {}
        self.default_category = "Others"
        self.load_config()

    def load_config(self):
        if not self.config_path.exists():
            logger.warning(f"Config file {self.config_path} not found. Using defaults.")
            self._apply_dict(DEFAULT_CONFIG)
            return

        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
            self._apply_dict(data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to read config.json: Format JSON rusak. Menggunakan konfigurasi default. Detail: {e}")
            self._apply_dict(DEFAULT_CONFIG)

    def _apply_dict(self, data: dict):
        import os
        self.target_folders = []
        for p in data.get("target_folders", []):
            expanded_var = os.path.expandvars(str(p))
            expanded_path = Path(expanded_var).expanduser()
            self.target_folders.append(expanded_path)
        self.categories = data.get("categories", {})
        self.default_category = data.get("default_category", "Others")
