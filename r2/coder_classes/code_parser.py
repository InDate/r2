import re

def extract_function_definitions(code):
    """Extracts function definitions from the given Python code."""
    function_definitions = []
    pattern = re.compile(r"(def\s+\w+\s*\(.*?\):(?:\n(?:\s*#.*\n)*\s*(?:[^#\n].*?(?:\n|$))+)+)", re.DOTALL)
    matches = pattern.finditer(code)
    for match in matches:
        function_definitions.append(match.group(1))
    return function_definitions
