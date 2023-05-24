import os
import unittest
from unittest.mock import MagicMock
from r2.command_classes.spec_file_command import SpecFileCommand


class TestSpecFileCommand(unittest.TestCase):
    def setUp(self):
        self.io = MagicMock()
        self.coder = MagicMock()
        self.spec_file_command = SpecFileCommand(self.io, self.coder)

    def test_run_empty_args(self):
        self.spec_file_command.run("  ", create_spec_file=False)
        self.io.tool_error.assert_called_with("Add a file name to use this command")

    def test_run_valid_file(self):
        self.coder.get_all_relative_files.return_value = ["file1.py", "file2.py"]
        self.spec_file_command.run("file1", create_spec_file=False)
        self.io.tool_error.assert_called()

    def test_run_invalid_file(self):
        self.coder.get_all_relative_files.return_value = ["file1.py", "file2.py"]
        self.spec_file_command.run("non_existent_file", create_spec_file=False)
        self.io.tool_error.assert_called()

    def test_run_create_spec_file(self):
        self.spec_file_command.create_spec_file = MagicMock()
        self.spec_file_command.run("file1", create_spec_file=True)
        self.spec_file_command.create_spec_file.assert_called()

    def test_create_spec_file(self):
        self.spec_file_command.create_spec_file("file1.py", "spec_file1.md")
        self.io.queue.enqueue.assert_called()

    def test_completions_spec_file(self):
        self.coder.get_all_relative_files.return_value = ["file1.py", "file2.py"]
        self.coder.get_inchat_relative_files.return_value = ["file2.py"]
        completions = list(self.spec_file_command.completions_spec_file("file"))
        self.assertEqual(len(completions), 1)
        self.assertEqual(completions[0].text, "file1.py")

    def test_completions_spec_file_no_match(self):
        self.coder.get_all_relative_files.return_value = ["file1.py", "file2.py"]
        self.coder.get_inchat_relative_files.return_value = ["file2.py"]
        completions = list(self.spec_file_command.completions_spec_file("non_existent_file"))
        self.assertEqual(len(completions), 0)


if __name__ == "__main__":
    unittest.main()
