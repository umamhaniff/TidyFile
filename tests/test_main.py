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
