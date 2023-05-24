- Module Name: prompts
- Purpose: A module containing strings and messages used in the r2 application.

- Constants:
    - `main_system`: A string containing the main instructions for the r2 application.
    - `system_reminder`: A string containing a reminder about the proper format for code changes.
    - `files_content_gpt_edits`: A string used when the user has committed changes.
    - `files_content_gpt_no_edits`: A string used when no properly formatted edits are found in the user's reply.
    - `files_content_local_edits`: A string used when the user has made changes to the files themselves.
    - `repo_content_prefix`: A string used as a prefix when listing the files in the git repo.
    - `files_content_prefix`: A string used as a prefix when listing the files the user can propose changes to.
    - `files_content_suffix`: A string used as a suffix when listing the files the user can propose changes to.
    - `professional_tester`: A string used when requesting a unit test file.
    - `commit_system`: A string containing instructions for generating a commit message.
    - `spec`: A string containing instructions for creating a specification file.
    - `undo_command_reply`: A string used when the user wants to undo the last set of changes.
    - `added_files`: A string used when additional files have been shared.
    - `test_connection_message`: A string used to test the connection with the user.

- Example Usage:
from r2.prompts import main_system
print(main_system)  # Outputs the main instructions for the r2 application.
