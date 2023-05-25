import os
import unittest
from unittest.mock import MagicMock
from r2.command_classes.base_command import BaseCommand

class TestBaseCommand(unittest.TestCase):
import tempfile

class TestBaseCommand(unittest.TestCase):
    def setUp(self):
        self.io_mock = MagicMock()
        self.coder_mock = MagicMock()
        self.test_dir = tempfile.TemporaryDirectory()
        self.coder_mock.root = self.test_dir.name
        self.base_command = BaseCommand(self.io_mock, self.coder_mock)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_has_extension(self):
        self.assertTrue(self.base_command.has_extension("file.txt"))
        self.assertFalse(self.base_command.has_extension("file"))
        self.assertFalse(self.base_command.has_extension("file."))
        self.assertTrue(self.base_command.has_extension("file.py"))

    def test_create_files(self):
        self.io_mock.confirm_ask.return_value = True
        self.coder_mock.repo = None
        self.base_command.create_files("test_file.txt")
        self.io_mock.confirm_ask.assert_called_once()
        self.assertTrue(os.path.exists("test_file.txt"))
        os.remove("test_file.txt")

    def test_parse_input(self):
        files = ["file1.txt", "file2.txt", "file3.txt"]
        self.assertEqual(self.base_command.parse_input("file1.txt", files), ["file1.txt"])
        self.assertEqual(self.base_command.parse_input("file4.txt", files), None)
        self.assertEqual(self.base_command.parse_input("all", files), ["all"])

if __name__ == "__main__":
    unittest.main()
