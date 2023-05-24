import unittest
from unittest.mock import MagicMock
from r2.commands import Commands


class TestCommands(unittest.TestCase):
    def setUp(self):
        self.io_mock = MagicMock()
        self.coder_mock = MagicMock()
        self.commands = Commands(self.io_mock, self.coder_mock)

    def test_help(self):
        self.commands.help()
        self.io_mock.tool.assert_called()

    def test_get_commands(self):
        commands = self.commands.get_commands()
        self.assertIn("/help", commands)
        self.assertIn("/execute_file", commands)
        self.assertIn("/add", commands)
        self.assertIn("/commit", commands)
        self.assertIn("/ls", commands)
        self.assertIn("/undo", commands)
        self.assertIn("/diff", commands)
        self.assertIn("/drop", commands)

    def test_get_command_completions(self):
        self.commands.command_methods["/execute_file"].completions_execute_file = MagicMock(return_value=[
                                                                                            "example"])
        completions = list(self.commands.get_command_completions("execute_file", "ex"))
        self.commands.command_methods["/execute_file"].completions_execute_file.assert_called_with(
            "ex")
        self.assertEqual(completions, ["example"])


if __name__ == "__main__":
    unittest.main()
