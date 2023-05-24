- Class Name: CodeExecutor
- Purpose: A class that manages the execution of code and communication with the AI model.

- Properties:
    - `io`: An instance of the IO class for input/output operations.
    - `api_manager`: An instance of the API manager class for managing API requests.
    - `commands`: An instance of the Commands class for handling user commands.
    - `main_model`: The name of the main AI model to use.
    - `pretty`: A boolean indicating whether to use pretty output or not.
    - `current_messages`: A list of current messages to send to the AI model.
    - `done_messages`: A list of completed messages.
    - `repo`: A reference to the Git repository.

- Methods:
    - `send_to_llm()`: Sends messages to the AI model and returns the response.
    - `show_send_output()`: Displays the output of the AI model.
    - `get_live()`: Returns a Live instance for pretty output.
    - `handle_chunk()`: Handles a chunk of the AI model's response.
    - `output_text()`: Outputs the text from the AI model.
    - `get_message()`: Returns a message dictionary with role and content.
    - `get_content_messages()`: Prepares messages for sending to the AI model.
    - `handle_interruption()`: Handles KeyboardInterrupt during AI response.
    - `is_not_good_request()`: Checks if the user input is not good for a meaningful response.
    - `send_new_user_message()`: Sends a new user message to the AI model.
    - `get_files_content()`: Returns the content of the specified files.
    - `get_files_messages()`: Returns messages related to the files.
    - `send_new_command_message()`: Sends a new command message to the AI model.
    - `run_loop()`: Runs the main loop for user input and AI interaction.
    - `run()`: Starts the CodeExecutor.

- Example Usage:
code_executor = CodeExecutor(io, api_manager)
code_executor.run()
