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
        # Create TidyFile scripts and project config files in source dir
        script_file = self.src_dir / "run_once.bat"
        script_file.write_text("echo run once")
        
        tidy_here_file = self.src_dir / "tidy_here.bat"
        tidy_here_file.write_text("echo tidy here")
        
        config_file = self.src_dir / "config.json"
        config_file.write_text("{}")
        
        req_file = self.src_dir / "requirements.txt"
        req_file.write_text("watchdog")
        
        gitignore_file = self.src_dir / ".gitignore"
        gitignore_file.write_text(".venv")
        
        self.organizer.organize_folder(self.src_dir)
        
        # They should NOT be moved
        self.assertTrue(script_file.exists())
        self.assertTrue(tidy_here_file.exists())
        self.assertTrue(config_file.exists())
        self.assertTrue(req_file.exists())
        self.assertTrue(gitignore_file.exists())
        
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

    def test_calculate_hash_exception(self):
        # Pass a non-existent path to trigger an Exception in calculate_hash
        h = self.organizer.calculate_hash(self.src_dir / "non_existent.txt")
        self.assertEqual(h, "")

    def test_process_file_with_directory(self):
        # Creating a directory inside Downloads
        subdir = self.src_dir / "Subfolder"
        subdir.mkdir()
        
        # Calling process_file on a directory should return immediately
        self.organizer.process_file(subdir)
        self.assertTrue(subdir.exists())
        self.assertFalse((self.src_dir / "Others" / "Subfolder").exists())

    def test_process_file_temp_extensions(self):
        # Temp file
        temp_file = self.src_dir / "download.crdownload"
        temp_file.write_text("partial data")
        
        self.organizer.process_file(temp_file)
        self.assertTrue(temp_file.exists())
        self.assertFalse((self.src_dir / "Others" / "download.crdownload").exists())

    def test_process_file_unlink_permission_error(self):
        # Target file exists
        dest_dir = self.src_dir / "Documents"
        dest_dir.mkdir()
        dest_file = dest_dir / "tugas.pdf"
        dest_file.write_text("same content")
        
        # Source file (duplicate)
        src_file = self.src_dir / "tugas.pdf"
        src_file.write_text("same content")
        
        # Mock unlink to throw PermissionError
        with patch.object(Path, 'unlink', side_effect=PermissionError("Permission denied")):
            with patch('src.core.logger') as mock_logger:
                self.organizer.process_file(src_file)
                mock_logger.warning.assert_called_once_with(
                    f'Gagal menghapus duplikat "{src_file.name}": File sedang dibuka oleh program lain.'
                )
        self.assertTrue(src_file.exists())

    def test_process_file_move_permission_error(self):
        src_file = self.src_dir / "tugas.pdf"
        src_file.write_text("some content")
        
        with patch('shutil.move', side_effect=PermissionError("File locked")):
            with patch('src.core.logger') as mock_logger:
                self.organizer.process_file(src_file)
                mock_logger.warning.assert_called_once_with(
                    f'Gagal memindahkan "{src_file.name}": File sedang dibuka oleh program lain atau sedang di-download.'
                )
        self.assertTrue(src_file.exists())

    def test_process_file_move_general_exception(self):
        src_file = self.src_dir / "tugas.pdf"
        src_file.write_text("some content")
        
        with patch('shutil.move', side_effect=RuntimeError("Disk failure")):
            with patch('src.core.logger') as mock_logger:
                self.organizer.process_file(src_file)
                mock_logger.error.assert_called_once_with(
                    f'Gagal memproses file "{src_file.name}": Disk failure'
                )
        self.assertTrue(src_file.exists())

    def test_organize_folder_not_exist(self):
        non_existent_folder = self.root / "MissingFolder"
        with patch('src.core.logger') as mock_logger:
            self.organizer.organize_folder(non_existent_folder)
            mock_logger.error.assert_called_once_with(
                f'Folder target "{non_existent_folder}" tidak ditemukan.'
            )

    def test_organize_folder_empty(self):
        # Empty source directory
        empty_dir = self.root / "EmptyFolder"
        empty_dir.mkdir()
        
        with patch('src.core.logger') as mock_logger:
            self.organizer.organize_folder(empty_dir)
            mock_logger.info.assert_any_call(
                f'Folder "{empty_dir.name}" sudah bersih. Tidak ada file untuk dirapikan.'
            )

