import unittest
from r2.coder_classes.code_parser import extract_function_definitions

class TestCodeParser(unittest.TestCase):

    def test_no_function_definitions(self):
        code = "a = 1\nb = 2\nprint(a + b)"
        expected_output = []
        self.assertEqual(extract_function_definitions(code), expected_output)

    def test_single_line_function_definitions(self):
        code = "def add(a, b): return a + b\ndef sub(a, b): return a - b"
        expected_output = ["def add(a, b): return a + b", "def sub(a, b): return a - b"]
        self.assertEqual(extract_function_definitions(code), expected_output)

    def test_multi_line_function_definitions(self):
        code = """
def add(a, b):
    return a + b

def sub(a, b):
    return a - b
"""
        expected_output = ["def add(a, b):\n    return a + b", "def sub(a, b):\n    return a - b"]
        self.assertEqual(extract_function_definitions(code), expected_output)

    def test_nested_function_definitions(self):
        code = """
def outer(a, b):
    def inner(x, y):
        return x * y
    return inner(a, b)
"""
        expected_output = ["def outer(a, b):\n    def inner(x, y):\n        return x * y\n    return inner(a, b)"]
        self.assertEqual(extract_function_definitions(code), expected_output)

def test_comments_and_docstrings(self):
    code = """
# This is a comment
def add(a, b):
    \"\"\"Add two numbers.\"\"\"
    return a + b

def sub(a, b):
    # This is another comment
    return a - b
"""
    expected_output = ["def add(a, b):\n    \"\"\"Add two numbers.\"\"\"\n    return a + b", "def sub(a, b):\n    # This is another comment\n    return a - b"]
    self.assertEqual(extract_function_definitions(code), expected_output)
if __name__ == "__main__":
    unittest.main()
