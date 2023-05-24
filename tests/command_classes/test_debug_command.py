import unittest
from unittest.mock import MagicMock
from r2.command_classes.debug_command import DebugCommand


class TestDebugCommand(unittest.TestCase):
    def setUp(self):
        self.io = MagicMock()
        self.coder = MagicMock()
        self.io.queue = MagicMock()
        self.io.tool_error = MagicMock()
        self.debug_command = DebugCommand(self.io, self.coder)

    def test_run_valid_file(self):
        self.coder.get_all_relative_files.return_value = ["file1.py"]
        self.debug_command.run("file1.py")
        self.io.queue.enqueue.assert_called_once()

    def test_run_invalid_file(self):
        self.coder.get_all_relative_files.return_value = []
        self.debug_command.run("invalid_file.py")
        self.io.tool_error.assert_called_once()

    def test_run_debug_message(self):
        self.debug_command.run("file1.py", debug=True, error_message="Error: division by zero")
        self.io.queue.enqueue.call_count == 2

    def test_get_help_valid_error_message(self):
        self.debug_command.get_help("Error: division by zero", "file1.py")
        self.io.tool_error.assert_called()
        self.io.queue.enqueue.assert_called()

    def test_run_invalid_file(self):
        self.coder.get_all_relative_files.return_value = []
        self.debug_command.run("invalid_file.py")
        self.coder.get_all_relative_files.return_value = ["file1.py", "file2.py"]
        completions = list(self.debug_command.completions_debug("file"))
        self.io.queue.enqueue.assert_not_called()
        self.assertEqual(len(completions), 2)

    def test_completions_debug_invalid_partial_file_name(self):
        self.coder.get_all_relative_files.return_value = ["file1.py", "file2.py"]
        completions = list(self.debug_command.completions_debug("invalid"))
        self.assertEqual(len(completions), 0)


if __name__ == '__main__':
    unittest.main()
