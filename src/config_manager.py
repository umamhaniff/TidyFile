import json
import logging
from pathlib import Path

logger = logging.getLogger("TidyFile")

DEFAULT_CONFIG = {
    "target_folders": [str(Path.home() / "Downloads")],
    "categories": {
        "Documents": [
            ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", 
            ".txt", ".rtf", ".odt", ".ods", ".odp", ".csv", ".md", 
            ".pages", ".numbers", ".key", ".epub", ".mobi", ".azw", ".azw3", 
            ".gdoc", ".gsheet", ".gslides", ".wps", ".wpt", ".dps"
        ],
        "Data_and_Models": [
            ".json", ".parquet", ".pkl", ".sqlite", ".db", ".db3", 
            ".tsv", ".yaml", ".yml", ".xml", ".h5", ".feather", 
            ".pb", ".onnx", ".tflite", ".bin", ".hdf5", ".mat"
        ],
        "Code_and_Projects": [
            ".py", ".ipynb", ".sql", ".js", ".ts", ".html", ".css", 
            ".c", ".cpp", ".h", ".cs", ".java", ".kt", ".swift", 
            ".dart", ".sh", ".bat", ".ps1", ".go", ".rs", ".php", ".rb"
        ],
        "BI_and_Design_Links": [
            ".twbx", ".twb", ".pbix", ".pbit", ".fig", ".xd", ".sketch", ".cdr"
        ],
        "Images": [
            ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp", 
            ".heic", ".heif", ".psd", ".ai", ".svg", ".raw", ".cr2", ".nef"
        ],
        "Audio_and_Video": [
            ".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv", ".3gp", 
            ".mpeg", ".mpg", ".m4v", ".mp3", ".wav", ".m4a", ".flac", ".aac", 
            ".ogg", ".wma", ".opus", ".mid", ".midi", ".amr"
        ],
        "Compressed_and_Packages": [
            ".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".cab", ".img",
            ".dmg", ".pkg", ".apk", ".aab", ".ipa", ".exe", ".msi"
        ],
        "Fonts": [
            ".ttf", ".otf", ".woff", ".woff2", ".eot"
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
