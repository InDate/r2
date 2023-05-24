import os
import unittest
import asyncio
from multiprocessing import Queue
from r2.command_classes.execute_command import execute_python_file


class TestExecuteCommand(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.queue = Queue()

    def test_execute_simple_file(self):
        async def run_test():
            await execute_python_file("simple_file", ["simple_file.py"], self.queue)
            result = self.queue.get()
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["message"], "Hello, World!")

        self.loop.run_until_complete(run_test())

    def test_execute_file_with_error(self):
        async def run_test():
            with self.assertRaises(Exception):
                await execute_python_file("file_with_error", ["file_with_error.py"], self.queue)
            result = self.queue.get()
            self.assertEqual(result["status"], "error")

        self.loop.run_until_complete(run_test())

    def test_execute_test_file(self):
        async def run_test():
            await execute_python_file("test_file", ["test_file.py"], self.queue)
            result = self.queue.get()
            self.assertEqual(result["status"], "success")

        self.loop.run_until_complete(run_test())

    def test_execute_test_file_with_failing_test(self):
        async def run_test():
            with self.assertRaises(Exception):
                await execute_python_file("test_file_with_failing_test", ["test_file_with_failing_test.py"], self.queue)
            result = self.queue.get()
            self.assertEqual(result["status"], "error")

        self.loop.run_until_complete(run_test())

    def test_no_matching_file(self):
        async def run_test():
            with self.assertRaises(FileNotFoundError):
                await execute_python_file("non_existent_file", [], self.queue)

        self.loop.run_until_complete(run_test())

    def test_invalid_file_type(self):
        async def run_test():
            with self.assertRaises(ValueError):
                await execute_python_file("invalid_file_type", ["invalid_file_type.txt"], self.queue)

        self.loop.run_until_complete(run_test())


if __name__ == "__main__":
    unittest.main()
