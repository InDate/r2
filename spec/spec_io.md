- Class Name: InputOutput
- Purpose: Handles input and output operations for the r2 tool, including user input, AI output, and chat history management.

- Properties:
    - `input`: The input stream for the PromptSession.
    - `output`: The output stream for the PromptSession.
    - `pretty`: A boolean indicating whether to use pretty formatting or not.
    - `yes`: A boolean indicating whether to automatically confirm prompts or not.
    - `input_history_file`: The file path for storing input history.
    - `chat_history_file`: The file path for storing chat history.
    - `queue`: A CustomQueue instance for managing the queue of messages.

- Methods:
    - `get_input(fnames, commands)`: Gets user input with autocompletion based on file content and command names.
    - `ai_output(content)`: Appends AI-generated content to the chat history.
    - `confirm_ask(question, default="y")`: Asks the user a yes/no question and returns a boolean based on the response.
    - `prompt_ask(question, default=None)`: Asks the user a question and returns the response.
    - `tool_error(message)`: Displays an error message to the user.
    - `tool(*messages, log_only=False)`: Displays messages to the user and logs them in the chat history.
    - `append_chat_history(text, linebreak=False, blockquote=False)`: Appends text to the chat history file.

- Example Usage:
io = InputOutput(pretty=True, yes=False, input_history_file="input_history.txt", chat_history_file="chat_history.txt")
user_input = io.get_input(["file1.py", "file2.py"], commands)
io.ai_output("AI-generated content")
confirmed = io.confirm_ask("Are you sure you want to proceed?")
response = io.prompt_ask("What is your favorite color?")
io.tool_error("An error occurred.")
io.tool("This is a message.")
io.append_chat_history("This is a chat history entry.")
