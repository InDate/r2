from r2 import prompts
from r2.command_classes.execute_tests_command import ExecuteTestsCommand


class Commands:
    def __init__(self, io, coder):
        self.io = io
        self.coder = coder
        self.command_methods = {}
        self.register_commands()

    def help(self):
        "Show help about all commands"
        commands = self.get_commands()
        for cmd in commands:
            cmd_method_name = f"cmd_{cmd[1:]}"
            cmd_method = getattr(self, cmd_method_name, None)
            if cmd_method:
                description = cmd_method.__doc__
                self.io.tool(f"{cmd} {description}")
            else:
                self.io.tool(f"{cmd} No description available.")

    def get_commands(self):
        commands = ["/help"]
        for cmd_name in self.command_methods:
            commands.append(cmd_name)

        return commands

    def get_command_completions(self, cmd_name, partial):
        command_instance = self.command_methods.get(f"/{cmd_name}", None)
        if command_instance:
            cmd_completions_method_name = f"completions_{cmd_name}"
            cmd_completions_method = getattr(command_instance, cmd_completions_method_name, None)
            if cmd_completions_method:
                for completion in cmd_completions_method(partial):
                    yield completion

    def register_commands(self):
        from .command_classes.execute_file_command import ExecuteFileCommand
        from .command_classes.spec_file_command import SpecFileCommand
        from .command_classes.add_command import AddCommand  # Import the AddCommand class
        from .command_classes.commit_command import CommitCommand  # Import the AddCommand class
        from .command_classes.list_files_command import LSCommand
        from .command_classes.undo_command import UndoCommand
        from .command_classes.diff_command import DiffCommand
        from .command_classes.drop_command import DropCommand
        from .command_classes.debug_command import DebugCommand
        # Import other command classes here

        self.command_methods = {
            "/execute_file": ExecuteFileCommand(self.io, self.coder),
            "/add": AddCommand(self.io, self.coder),  # Create an instance of AddCommand
            "/commit": CommitCommand(self.io, self.coder),
            "/ls": LSCommand(self.io, self.coder),
            "/undo": UndoCommand(self.io, self.coder),
            "/diff": DiffCommand(self.io, self.coder),
            "/drop": DropCommand(self.io, self.coder),
            "/unit_test": ExecuteTestsCommand(self.io, self.coder),
            "/debug": DebugCommand(self.io, self.coder),
            "/spec_file": SpecFileCommand(self.io, self.coder),
            "/help": None,
            "/clear": None,
            "/test_connection": None,
            # Add other command instances here
        }

    def execute_command(self, command, args, **kwargs):
        if command in self.command_methods:
            return self.command_methods[command].run(args, **kwargs)
        else:
            self.io.tool_error(f"Error: {command} is not a valid command.")

    def test_connection(self):
        connection_message = [self.coder.get_message("user", prompts.test_connection_message)]
        self.coder.clear_chat()
        self.coder.send_to_llm(connection_message, temperature=0.7, model='gpt-3.5-turbo')

    def run(self, input):
        words = input.strip().split()
        if not words:
            return

        first_word = words[0]
        rest_input = input[len(words[0]):]

        if first_word in self.command_methods:
            if first_word == "/help":
                self.help()
            elif first_word == "/clear":
                self.clear_chat()
            elif first_word == "/test_connection":
                self.test_connection()
            else:
                return self.command_methods[first_word].run(rest_input)
        else:
            self.io.tool_error(f"Error: {first_word} is not a valid command.")
