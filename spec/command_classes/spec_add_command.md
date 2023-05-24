- Class Name: AddCommand
- Purpose: Adds files into the chat. Once a file is added, the contents are shared with the LLM.

- Properties:
    - `__doc__`: A brief description of the class.

- Methods:
    - `run(args)`: Executes the add command with the given arguments.
    - `add_files_command(args)`: Adds files to the chat based on the given arguments.
    - `completions_add(partial)`: Provides file name completions based on the given partial input.

- Example Usage:
add_command = AddCommand(io, coder)
add_command.run("file_name")
print(add_command.add_files_command("file_name"))  # Outputs: ['file_name']
