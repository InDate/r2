import unittest
from unittest.mock import MagicMock, patch
from r2.command_classes.debug_command import DebugCommand
from prompt_toolkit.document import Document
from prompt_toolkit import PromptSession


class TestDebugCommand(unittest.TestCase):
    def setUp(self):
        self.io = MagicMock()
        self.coder = MagicMock()
        self.io.queue = MagicMock()
        self.io.tool_error = MagicMock()
        self.debug_command = DebugCommand(self.io, self.coder)

    def mocked_prompt(prompt, mock_inputs):
        return MagicMock(spec=Document, text=mock_inputs.pop(0))
    
    def test_run_valid_file_from_chat(self):
        self.coder.get_all_relative_files.return_value = ["file1.py"]
        self.debug_command.run("file1.py Error: division by zero")
        self.assertEqual(self.io.queue.enqueue.call_count, 2)
        
    def test_run_create_file_if_not_found(self):
        mock_inputs = ['n', 'n']
        self.coder.get_all_relative_files.return_value = []
        
        with patch.object(PromptSession, 'prompt', side_effect=self.mocked_prompt(mock_inputs)):
            with patch("builtins.open", MagicMock()):
                self.debug_command.run("invalid_file.py Error: division by zero")
        
        self.assertEqual(self.io.queue.enqueue.call_count, 0)
        self.io.tool_error.assert_called()
        
    def test_run_not_create_invalid_file(self):
        self.coder.get_all_relative_files.return_value = []
        
        self.debug_command.run("new_file Error: division by zero")
        self.assertEqual(self.io.queue.enqueue.call_count, 0)
        self.io.tool_error.assert_called()
        
    def test_run_debug_message(self):
        self.debug_command.run("file1.py", debug=True, error_message="Error: division by zero")
        self.assertEqual(self.io.queue.enqueue.call_count, 2)

    def test_get_help_valid_error_message(self):
        self.debug_command.get_help("Error: division by zero", "file1.py")
        self.io.tool.assert_called()
        self.assertEqual(self.io.queue.enqueue.call_count, 2)

    def test_completions(self):
        self.coder.get_all_relative_files.return_value = ["file1.py", "file2.py"]
        completions = list(self.debug_command.completions_debug("file"))
        self.assertEqual(len(completions), 2)

    def test_completions_debug_invalid_partial_file_name(self):
        self.coder.get_all_relative_files.return_value = ["file1.py", "file2.py"]
        completions = list(self.debug_command.completions_debug("invalid"))
        self.assertEqual(len(completions), 0)


if __name__ == '__main__':
    unittest.main()
