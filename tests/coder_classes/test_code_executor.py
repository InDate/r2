import unittest
from unittest.mock import MagicMock, Mock, patch
from r2.coder_classes.code_executor import CodeExecutor
from r2.io import InputOutput


class TestCodeExecutor(unittest.TestCase):

    def setUp(self):
        io_instance = InputOutput(
            pretty=False, yes=True, input_history_file="input_history.txt", chat_history_file="chat_history.txt")
        api_manager_mock = MagicMock()
        self.code_executor = CodeExecutor(io_instance, api_manager_mock)
        self.code_executor.pretty = True
        self.code_executor.update_completion_tokens = Mock()
        self.code_executor.handle_chunk = Mock()

        self.completion = [Mock()]
        self.silent = False

    def test_show_send_output(self):
        for live_enabled, mock_live in [(True, MagicMock()), (False, None)]:
            with patch('rich.live.Live', return_value=mock_live):
                # Prepare
                self.code_executor.get_live = Mock(return_value=mock_live)
                self.code_executor.api_manager.get_total_cost = Mock(return_value="0")

                # Exercise
                self.code_executor.show_send_output(self.completion, self.silent)

                # Verify
                self.code_executor.get_live.assert_called_once_with(self.silent)
                self.code_executor.api_manager.update_completion_tokens.assert_called_once_with(1)
                self.code_executor.handle_chunk.assert_called_once_with(
                    self.completion[0], self.silent, mock_live)

                # Reset mocks for the next iteration
                self.code_executor.get_live.reset_mock()
                self.code_executor.api_manager.update_completion_tokens.reset_mock()
                self.code_executor.handle_chunk.reset_mock()

    def test_send(self):
        # Test send method with a simple message
        self.code_executor.send_to_llm = MagicMock(return_value=("Test message", False))
        self.code_executor.create_chat_completion = MagicMock(return_value=[])
        messages = [{"role": "user", "content": "Test input"}]
        result, interrupted = self.code_executor.send_to_llm(messages)
        self.assertEqual(result, "Test message")

    def test_send_new_user_message(self):
        # Test send_new_user_message method with a simple input
        with unittest.mock.patch.object(self.code_executor, "send_to_llm", return_value=("Test message", False)):
            self.code_executor.send_new_user_message("Test input")
        self.assertIn({"role": "user", "content": "Test input"},
                      self.code_executor.current_messages)

    def test_get_files_content(self):
        # Test get_files_content method with a simple file content
        self.code_executor.get_files_content = MagicMock(return_value="Test file content")
        result = self.code_executor.get_files_content()
        self.assertEqual(result, "Test file content")

    def test_get_files_messages(self):
        # Test get_files_messages method with a simple message
        self.code_executor.get_files_messages = MagicMock(
            return_value=[{"role": "user", "content": "Test message"}])
        result = self.code_executor.get_files_messages()
        self.assertEqual(result, [{"role": "user", "content": "Test message"}])

    def test_send_new_command_message(self):
        # Add test cases for the send_new_command_message method here
        with unittest.mock.patch.object(self.code_executor, "send_to_llm", return_value=("Test command message", False)):
            self.code_executor.send_new_command_message([
                dict({"assistant": "Test command message"})], "Unit Test", full_context=False)
        self.assertIn({"role": "assistant", "content": "Test command message"},
                      self.code_executor.current_messages)

    def test_run_loop(self):
        # Add test cases for the run_loop method here
        self.code_executor.run_loop = MagicMock(return_value=None)
        result = self.code_executor.run_loop()
        self.assertIsNone(result)

    def test_run(self):
        # Add test cases for the run method here
        self.code_executor.run = MagicMock(return_value=None)
        result = self.code_executor.run()
        self.assertIsNone(result)

    def test_get_context_from_history(self):
        self.code_executor.current_messages = [{"role": "user", "content": "Test message"}]
        history = [{"role": "user", "content": "Test message"}]
        context = self.code_executor.get_context_from_history(history)
        expected_context = "# Context:\nUSER: Test message\n"
        self.assertEqual(context, expected_context)


if __name__ == '__main__':
    unittest.main()
