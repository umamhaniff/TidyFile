import unittest
import json
import tempfile
from pathlib import Path
from src.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "config.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_valid_config(self):
        config_data = {
            "target_folders": ["C:/TestDownloads"],
            "categories": {"Docs": [".pdf"]},
            "default_category": "Misc"
        }
        with open(self.config_path, "w") as f:
            json.dump(config_data, f)
        
        cm = ConfigManager(self.config_path)
        self.assertEqual(cm.target_folders, [Path("C:/TestDownloads")])
        self.assertEqual(cm.categories, {"Docs": [".pdf"]})
        self.assertEqual(cm.default_category, "Misc")

    def test_load_missing_or_invalid_config_fallback(self):
        # No file created, should fallback to defaults
        cm = ConfigManager(self.config_path)
        self.assertTrue(len(cm.target_folders) >= 0)
        self.assertEqual(cm.default_category, "Others")

    def test_load_invalid_json_fallback(self):
        # Corrupt JSON file, should fallback to defaults
        with open(self.config_path, "w") as f:
            f.write("{invalid_json: true")
        
        cm = ConfigManager(self.config_path)
        self.assertTrue(len(cm.target_folders) >= 0)
        self.assertEqual(cm.default_category, "Others")

