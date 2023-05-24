- Class Name: ExecuteTestsCommand
- Purpose: A command class to execute tests and create unit tests for specified files.

- Properties:
    - `io`: An instance of the IO class for input/output operations.
    - `coder`: An instance of the Coder class for managing code files and operations.

- Methods:
    - `run(args, **kwargs)`: Executes tests or creates unit tests based on the provided arguments and kwargs.
    - `create_unit_test(program_file, test_file, spec_file=None)`: Creates a unit test for the specified program_file, test_file, and optional spec_file.
    - `completions_unit_test(partial)`: Provides autocompletion suggestions for unit test files based on the partial input.

- Example Usage:
io = IO()
coder = Coder(io)
execute_tests_command = ExecuteTestsCommand(io, coder)
execute_tests_command.run("file1.py", create_unit_tests=True, test_file="test_file1.py", spec_file="spec_file1.md")
execute_tests_command.run("file2.py", create_unit_tests=False)
execute_tests_command.create_unit_test("file1.py", "test_file1.py", "spec_file1.md")
execute_tests_command.create_unit_test("file2.py", "test_file2.py")
completions = list(execute_tests_command.completions_unit_test("file"))
