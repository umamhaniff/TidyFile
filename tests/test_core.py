import unittest
import tempfile
import shutil
from pathlib import Path
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
