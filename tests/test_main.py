import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.main import parse_args, main, get_organizer_by_mode, show_interactive_menu
from src.core import FileOrganizer, WorkstationOrganizer, MomentOrganizer

class TestMainCLI(unittest.TestCase):
    def test_parse_args_default(self):
        with patch.object(sys, 'argv', ['main.py']):
            args = parse_args()
            self.assertFalse(args.watch)
            self.assertIsNone(args.mode)

    def test_parse_args_subcommands(self):
        for m in ["tidy", "workstation", "moment", "1", "2", "3", "menu"]:
            with patch.object(sys, 'argv', ['main.py', m]):
                args = parse_args()
                self.assertEqual(args.mode, m)

    def test_parse_args_watch(self):
        with patch.object(sys, 'argv', ['main.py', '--watch']):
            args = parse_args()
            self.assertTrue(args.watch)

    def test_parse_args_path(self):
        with patch.object(sys, 'argv', ['main.py', '--path', 'some/dir']):
            args = parse_args()
            self.assertEqual(args.path, 'some/dir')

    def test_parse_args_version(self):
        with patch.object(sys, 'argv', ['main.py', '--version']):
            with self.assertRaises(SystemExit) as cm:
                parse_args()
            self.assertEqual(cm.exception.code, 0)

    def test_get_organizer_by_mode(self):
        cfg = MagicMock()
        m1, org1 = get_organizer_by_mode("tidy", cfg)
        self.assertEqual(m1, "tidy")
        self.assertIsInstance(org1, FileOrganizer)

        m2, org2 = get_organizer_by_mode("workstation", cfg)
        self.assertEqual(m2, "workstation")
        self.assertIsInstance(org2, WorkstationOrganizer)

        m3, org3 = get_organizer_by_mode("3", cfg)
        self.assertEqual(m3, "moment")
        self.assertIsInstance(org3, MomentOrganizer)

    @patch('builtins.input', side_effect=['1'])
    def test_show_interactive_menu_tidy(self, mock_input):
        mode = show_interactive_menu()
        self.assertEqual(mode, "tidy")

    @patch('builtins.input', side_effect=['2'])
    def test_show_interactive_menu_workstation(self, mock_input):
        mode = show_interactive_menu()
        self.assertEqual(mode, "workstation")

    @patch('builtins.input', side_effect=['3'])
    def test_show_interactive_menu_moment(self, mock_input):
        mode = show_interactive_menu()
        self.assertEqual(mode, "moment")

    @patch('builtins.input', side_effect=['4'])
    def test_show_interactive_menu_exit(self, mock_input):
        with self.assertRaises(SystemExit):
            show_interactive_menu()

    @patch('builtins.input', side_effect=['invalid'])
    def test_show_interactive_menu_invalid(self, mock_input):
        mode = show_interactive_menu()
        self.assertEqual(mode, "tidy")


class TestMainExecution(unittest.TestCase):
    @patch('src.main.ConfigManager')
    @patch('src.main.FileOrganizer')
    @patch('src.main.setup_logging')
    def test_main_with_path(self, mock_setup_logging, mock_file_organizer_cls, mock_config_manager_cls):
        mock_organizer = MagicMock()
        mock_file_organizer_cls.return_value = mock_organizer
        
        mock_config = MagicMock()
        mock_config.target_folders = [Path("default/dir")]
        mock_config_manager_cls.return_value = mock_config
        
        with patch.object(sys, 'argv', ['main.py', 'tidy', '--path', 'some/dir']):
            exit_code = main()
            self.assertEqual(exit_code, 0)
            resolved_path = Path('some/dir').resolve()
            mock_organizer.organize_folder.assert_called_once_with(resolved_path)

    @patch('src.main.ConfigManager')
    @patch('src.main.WorkstationOrganizer')
    @patch('src.main.setup_logging')
    def test_main_workstation_mode(self, mock_setup_logging, mock_ws_cls, mock_config_manager_cls):
        mock_organizer = MagicMock()
        mock_ws_cls.return_value = mock_organizer
        
        mock_config = MagicMock()
        mock_config.target_folders = [Path("default/dir")]
        mock_config_manager_cls.return_value = mock_config
        
        with patch.object(sys, 'argv', ['main.py', 'workstation']):
            exit_code = main()
            self.assertEqual(exit_code, 0)
            mock_organizer.organize_folder.assert_called_once_with(Path("default/dir"))

    @patch('src.main.ConfigManager')
    @patch('src.main.MomentOrganizer')
    @patch('src.main.setup_logging')
    def test_main_moment_mode(self, mock_setup_logging, mock_moment_cls, mock_config_manager_cls):
        mock_organizer = MagicMock()
        mock_moment_cls.return_value = mock_organizer
        
        mock_config = MagicMock()
        mock_config.target_folders = [Path("default/dir")]
        mock_config_manager_cls.return_value = mock_config
        
        with patch.object(sys, 'argv', ['main.py', 'moment']):
            exit_code = main()
            self.assertEqual(exit_code, 0)
            mock_organizer.organize_folder.assert_called_once_with(Path("default/dir"))

    @patch('src.main.ConfigManager')
    @patch('src.main.FileOrganizer')
    @patch('src.main.setup_logging')
    @patch('src.watcher.start_watcher')
    def test_main_watch_mode(self, mock_start_watcher, mock_setup_logging, mock_file_organizer_cls, mock_config_manager_cls):
        mock_organizer = MagicMock()
        mock_file_organizer_cls.return_value = mock_organizer
        
        mock_config = MagicMock()
        mock_config_manager_cls.return_value = mock_config
        
        with patch.object(sys, 'argv', ['main.py', 'tidy', '--watch']):
            exit_code = main()
            self.assertEqual(exit_code, 0)
            mock_start_watcher.assert_called_once_with(mock_config, mock_organizer)

    def test_setup_logging(self):
        from src.main import setup_logging
        import logging
        
        logger = setup_logging()
        self.assertEqual(logger.name, "TidyFile")
        self.assertEqual(logger.level, logging.INFO)
        self.assertTrue(any(isinstance(h, logging.FileHandler) for h in logger.handlers))
        self.assertTrue(any(isinstance(h, logging.StreamHandler) for h in logger.handlers))
        
        for h in list(logger.handlers):
            h.close()
            logger.removeHandler(h)

    @patch('src.config_manager.ConfigManager')
    @patch('src.core.FileOrganizer')
    def test_main_entry_point(self, mock_organizer_cls, mock_config_cls):
        import runpy
        mock_config = mock_config_cls.return_value
        mock_config.target_folders = []
        
        with patch.object(sys, 'argv', ['main.py', 'tidy']):
            runpy.run_module('src.main', run_name='__main__')
            
        mock_config_cls.assert_called_once()
        mock_organizer_cls.assert_called_once_with(mock_config)

if __name__ == "__main__":
    unittest.main()
