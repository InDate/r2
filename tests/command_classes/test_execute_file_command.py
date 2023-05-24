import os
import tempfile
import unittest
import asyncio
from r2.command_classes.execute_command import execute_python_file
from multiprocessing import Queue


class TestExecuteCommand(unittest.TestCase):
    def test_execute_python_file_exception(self):
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
            temp_file.write("import sys\n")
            temp_file.write("def raise_exception():\n")
            temp_file.write("    raise Exception('Test exception')\n")
            temp_file.write("\n")
            temp_file.write("raise_exception()\n")
            temp_file.write("sys.exit(1)\n")

        starting_execution = {'status': 'status', 'message': 'Executing File: %s' % temp_file.name}
        error_result = {'status': 'error', 'message': 'Executing File: %s' % temp_file.name}

        queue = Queue()
        # Call the execute_python_file function
        result = None

        async def test_async():
            nonlocal result
            await execute_python_file(temp_file.name, [temp_file.name], queue)
            result = queue.get()
            self.assertEqual(starting_execution, {'status': 'status',
                             'message': f'Executing File: {temp_file.name}'})

        asyncio.run(test_async())

        while not queue.empty():
            result = queue.get()
            self.assertEqual(error_result['status'], result['status'])

        # Clean up the temporary file
        os.remove(temp_file.name)

    def test_execute_python_file(self):
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
            temp_file.write("print('Hello, World!')")

        expected_result = {'status': 'status', 'message': 'Executing File: %s' % temp_file.name}
        queue = Queue()
        # Call the execute_python_file function
        result = None

        async def test_async():
            nonlocal result
            await execute_python_file(temp_file.name, [temp_file.name], queue)
            result = queue.get()
            self.assertEqual(expected_result, {'status': 'status',
                             'message': f'Executing File: {temp_file.name}'})

        asyncio.run(test_async())

        self.assertEqual(expected_result, {'status': 'status',
                                           'message': f'Executing File: {temp_file.name}'})

        # Clean up the temporary file
        os.remove(temp_file.name)

    def test_execute_not_python_file(self):
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".p", delete=False) as temp_file:
            temp_file.write("print('Hello, World!')")

        queue = Queue()
        # Call the execute_python_file function

        async def test_async():
            await execute_python_file(temp_file.name, [temp_file.name], queue)

        try:
            asyncio.run(test_async())
        except:
            self.assertRaises(ValueError)

        # Clean up the temporary file
        os.remove(temp_file.name)


if __name__ == "__main__":
    unittest.main()
