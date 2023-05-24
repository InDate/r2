- Class Name: DropCommand
- Purpose: A command class that removes specified files from the chat.

- Properties:
    - Inherits properties from `BaseCommand`.

- Methods:
    - `run(args, **kwargs)`: Removes specified files from the chat based on the given arguments.
    - `remove_files_from_chat(matched_files, notify=False)`: Removes the matched files from the chat and optionally notifies the user.
    - `completions_drop(partial)`: Provides file name completions based on the given partial input.

- Example Usage:
drop_command = DropCommand(io, coder)
drop_command.run("file_name")  # Removes the file with the name "file_name" from the chat.
drop_command.run("all")  # Removes all files from the chat.
