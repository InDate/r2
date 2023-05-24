- Class Name: GitManager
- Purpose: A class to manage git operations such as diffs, commits, and file tracking.

- Properties:
    - `current_messages`: A list of current messages.
    - `io`: An instance of InputOutput class imported from 'aidan.io'.
    - `commands`: An instance of the Commands class.
    - `show_diffs`: A boolean indicating whether to show diffs.
    - `abs_fnames`: A set of absolute file names.
    - `last_asked_for_commit_time`: The last time the user was asked for a commit.

- Methods:
    - `get_diffs(*args)`: Returns the diffs for the given arguments.
    - `get_diffs_file_names(*args)`: Returns the file names of the diffs.
    - `commit(history=None, prefix=None, ask=False, message=None, which="chat_files")`: Commits changes with the given parameters.
    - `_spec_file_before_commit(updated_files)`: Handles spec file creation before committing.
    - `auto_test(updated_files)`: Automatically runs tests for the updated files.
    - `set_repo(cmd_line_fnames)`: Sets the git repository for the given file names.
    - `get_all_abs_files()`: Returns a list of all absolute file paths.
    - `get_last_modified()`: Returns the last modified time of the files.
    - `should_auto_commit(inp)`: Determines if an auto-commit should be performed.
    - `auto_commit()`: Performs an auto-commit if necessary.
    - `_generate_commit_message(diffs, context)`: Generates a commit message based on the diffs and context.
    - `_should_commit()`: Checks if a commit should be performed.
    - `_get_dirty_files_and_diffs(which)`: Gets dirty files and their diffs based on the 'which' parameter.
    - `_get_commit_message(history, message, diffs)`: Gets the commit message.
    - `_ask_for_commit_message(commit_message, which)`: Asks the user for a commit message.
    - `_test_changes_before_commit(diff_file_names)`: Tests changes before the commit proceeds.
    - `_perform_commit(relative_dirty_fnames, commit_message, prefix)`: Performs the commit.

- Example Usage:
git_manager = GitManager(io_instance)
git_manager.set_repo(["file1.py", "file2.py"])
git_manager.commit(message="Initial commit")
print(git_manager.get_diffs())  # Outputs: diffs between the current state and the last commit
