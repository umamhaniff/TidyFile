import unittest
import sys
from unittest.mock import patch
from src.main import parse_args

class TestMainCLI(unittest.TestCase):
    def test_parse_args_default(self):
        with patch.object(sys, 'argv', ['main.py']):
            args = parse_args()
            self.assertFalse(args.watch)

    def test_parse_args_watch(self):
        with patch.object(sys, 'argv', ['main.py', '--watch']):
            args = parse_args()
            self.assertTrue(args.watch)

    def test_parse_args_path(self):
        with patch.object(sys, 'argv', ['main.py', '--path', 'C:\\some\\dir']):
            args = parse_args()
            self.assertEqual(args.path, 'C:\\some\\dir')


from pathlib import Path
from unittest.mock import MagicMock
from src.main import main

class TestMainExecution(unittest.TestCase):
    @patch('src.main.ConfigManager')
    @patch('src.main.FileOrganizer')
    @patch('src.main.setup_logging')
    def test_main_with_path(self, mock_setup_logging, mock_file_organizer_cls, mock_config_manager_cls):
        mock_organizer = MagicMock()
        mock_file_organizer_cls.return_value = mock_organizer
        
        mock_config = MagicMock()
        mock_config.target_folders = [Path("C:\\default\\dir")]
        mock_config_manager_cls.return_value = mock_config
        
        with patch.object(sys, 'argv', ['main.py', '--path', 'C:\\some\\dir']):
            exit_code = main()
            self.assertEqual(exit_code, 0)
            # Should resolve the path
            resolved_path = Path('C:\\some\\dir').resolve()
            mock_organizer.organize_folder.assert_called_once_with(resolved_path)

    @patch('src.main.ConfigManager')
    @patch('src.main.FileOrganizer')
    @patch('src.main.setup_logging')
    def test_main_default_flow(self, mock_setup_logging, mock_file_organizer_cls, mock_config_manager_cls):
        mock_organizer = MagicMock()
        mock_file_organizer_cls.return_value = mock_organizer
        
        mock_config = MagicMock()
        mock_config.target_folders = [Path("C:\\default\\dir1"), Path("C:\\default\\dir2")]
        mock_config_manager_cls.return_value = mock_config
        
        with patch.object(sys, 'argv', ['main.py']):
            exit_code = main()
            self.assertEqual(exit_code, 0)
            mock_organizer.organize_folder.assert_any_call(Path("C:\\default\\dir1"))
            mock_organizer.organize_folder.assert_any_call(Path("C:\\default\\dir2"))
            self.assertEqual(mock_organizer.organize_folder.call_count, 2)


