import os
import unittest
from unittest.mock import MagicMock
from r2.command_classes.execute_tests_command import ExecuteTestsCommand
from r2.coder import Coder


class TestExecuteTestsCommand(unittest.TestCase):
    def setUp(self):
        self.io = MagicMock()
        self.coder = MagicMock()
        self.execute_tests_command = ExecuteTestsCommand(self.io, self.coder)

    def test_run(self):
        self.execute_tests_command.run("file1.py", create_unit_tests=True,
                                       test_file="test_file1.py", spec_file="spec_file1.md")
        self.execute_tests_command.run("file2.py", create_unit_tests=False)

    def test_create_unit_test(self):
        self.execute_tests_command.create_unit_test("file1.py", "test_file1.py", "spec_file1.md")
        self.execute_tests_command.create_unit_test("file2.py", "test_file2.py")

    def test_completions_unit_test(self):
        self.coder.get_all_relative_files = MagicMock(
            return_value=["file1.py", "file2.py", "file3.py"])
        self.coder.get_inchat_relative_files = MagicMock(return_value=["file3.py"])

        completions = sorted(
            list(self.execute_tests_command.completions_unit_test("file")), key=lambda x: x.text)
        self.assertEqual(len(completions), 2)
        self.assertEqual(completions[0].text, "file1.py")
        self.assertEqual(completions[1].text, "file2.py")


if __name__ == "__main__":
    unittest.main()
