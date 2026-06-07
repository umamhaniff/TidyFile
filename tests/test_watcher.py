import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from watchdog.events import FileCreatedEvent, FileMovedEvent
from src.watcher import FolderHandler, start_watcher

class TestWatcher(unittest.TestCase):
    def setUp(self):
        self.mock_organizer = MagicMock()
        self.handler = FolderHandler(self.mock_organizer)

    def test_on_created_file(self):
        event = FileCreatedEvent("/path/to/file.txt")
        with patch("time.sleep") as mock_sleep:
            self.handler.on_created(event)
            mock_sleep.assert_called_once_with(1.5)
            self.mock_organizer.process_file.assert_called_once_with(Path("/path/to/file.txt"))

    def test_on_created_directory(self):
        # Directories should be ignored
        event = MagicMock()
        event.is_directory = True
        event.src_path = "/path/to/dir"
        self.handler.on_created(event)
        self.mock_organizer.process_file.assert_not_called()

    def test_on_moved_file(self):
        event = FileMovedEvent("/path/to/old.txt", "/path/to/new.txt")
        with patch("time.sleep") as mock_sleep:
            self.handler.on_moved(event)
            mock_sleep.assert_called_once_with(1.5)
            self.mock_organizer.process_file.assert_called_once_with(Path("/path/to/new.txt"))

    def test_on_moved_directory(self):
        # Directories should be ignored
        event = MagicMock()
        event.is_directory = True
        event.dest_path = "/path/to/dir"
        self.handler.on_moved(event)
        self.mock_organizer.process_file.assert_not_called()

    def test_process_with_cooldown_ignores_temp_extensions(self):
        for ext in [".crdownload", ".part", ".tmp"]:
            with self.subTest(ext=ext):
                self.mock_organizer.reset_mock()
                file_path = Path(f"/path/to/file{ext}")
                self.handler.process_with_cooldown(file_path)
                self.mock_organizer.process_file.assert_not_called()

    @patch("src.watcher.Observer")
    def test_start_watcher_valid_folders(self, mock_observer_cls):
        mock_observer = MagicMock()
        mock_observer_cls.return_value = mock_observer

        mock_config = MagicMock()
        mock_folder1 = MagicMock(spec=Path)
        mock_folder1.exists.return_value = True
        mock_folder1.__str__.return_value = "/path/folder1"
        
        mock_folder2 = MagicMock(spec=Path)
        mock_folder2.exists.return_value = False
        mock_folder2.__str__.return_value = "/path/folder2"

        mock_config.target_folders = [mock_folder1, mock_folder2]

        # We raise KeyboardInterrupt to break the infinite loop in start_watcher
        with patch("time.sleep", side_effect=KeyboardInterrupt):
            start_watcher(mock_config, self.mock_organizer)

        mock_observer.schedule.assert_called_once()
        mock_observer.start.assert_called_once()
        mock_observer.stop.assert_called_once()
        mock_observer.join.assert_called_once()

    @patch("src.watcher.Observer")
    def test_start_watcher_no_valid_folders(self, mock_observer_cls):
        mock_observer = MagicMock()
        mock_observer_cls.return_value = mock_observer

        mock_config = MagicMock()
        mock_folder = MagicMock(spec=Path)
        mock_folder.exists.return_value = False
        mock_folder.__str__.return_value = "/path/folder"

        mock_config.target_folders = [mock_folder]

        start_watcher(mock_config, self.mock_organizer)

        mock_observer.schedule.assert_not_called()
        mock_observer.start.assert_not_called()
