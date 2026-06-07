import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
from src.core import FileOrganizer
from src.config_manager import ConfigManager

class TestFileOrganizer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        
        # Target directories setup
        self.src_dir = self.root / "Downloads"
        self.src_dir.mkdir()
        
        # Mock ConfigManager properties
        class MockConfig:
            target_folders = [self.src_dir]
            categories = {
                "Documents": [".pdf"],
                "Images": [".jpg"]
            }
            default_category = "Others"
            
        self.config = MockConfig()
        self.organizer = FileOrganizer(self.config)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_category(self):
        self.assertEqual(self.organizer.get_category(Path("test.pdf")), "Documents")
        self.assertEqual(self.organizer.get_category(Path("test.txt")), "Others")

    def test_hash_calculation(self):
        file1 = self.src_dir / "f1.txt"
        file1.write_text("Hello World")
        h1 = self.organizer.calculate_hash(file1)
        self.assertEqual(len(h1), 64)  # SHA-256 length

    def test_organize_simple_move(self):
        file = self.src_dir / "tugas.pdf"
        file.write_text("content")
        
        self.organizer.organize_folder(self.src_dir)
        
        dest = self.src_dir / "Documents" / "tugas.pdf"
        self.assertTrue(dest.exists())
        self.assertFalse(file.exists())

    def test_organize_duplicate_deletion(self):
        # Target file exists
        dest_dir = self.src_dir / "Documents"
        dest_dir.mkdir()
        dest_file = dest_dir / "tugas.pdf"
        dest_file.write_text("same content")
        
        # Source file (duplicate)
        src_file = self.src_dir / "tugas.pdf"
        src_file.write_text("same content")
        
        self.organizer.organize_folder(self.src_dir)
        
        self.assertTrue(dest_file.exists())
        self.assertFalse(src_file.exists())  # Duplicate deleted

    def test_organize_version_renaming(self):
        dest_dir = self.src_dir / "Documents"
        dest_dir.mkdir()
        dest_file = dest_dir / "tugas.pdf"
        dest_file.write_text("version 1")
        
        src_file = self.src_dir / "tugas.pdf"
        src_file.write_text("version 2")
        
        self.organizer.organize_folder(self.src_dir)
        
        self.assertTrue(dest_file.exists())
        self.assertFalse(src_file.exists())
        
        renamed_file = dest_dir / "tugas_1.pdf"
        self.assertTrue(renamed_file.exists())
        self.assertEqual(renamed_file.read_text(), "version 2")

    def test_organize_ignores_tidyfile_scripts(self):
        # Create TidyFile scripts in source dir
        script_file = self.src_dir / "run_once.bat"
        script_file.write_text("echo run once")
        
        config_file = self.src_dir / "config.json"
        config_file.write_text("{}")
        
        self.organizer.organize_folder(self.src_dir)
        
        # They should NOT be moved
        self.assertTrue(script_file.exists())
        self.assertTrue(config_file.exists())
        
        # Verify no "Code_and_Projects" or "Others" subdirectories were created
        self.assertFalse((self.src_dir / "Code_and_Projects").exists())
        self.assertFalse((self.src_dir / "Others").exists())

    def test_organize_non_directory(self):
        # Create a file instead of a directory
        file_path = self.src_dir / "not_a_dir.txt"
        file_path.write_text("just a file")
        
        with patch('src.core.logger') as mock_logger:
            self.organizer.organize_folder(file_path)
            mock_logger.error.assert_called_once_with(
                f'Folder target "{file_path}" bukan merupakan direktori.'
            )
            
        self.assertTrue(file_path.exists())

