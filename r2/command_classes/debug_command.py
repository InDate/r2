from r2 import prompts
from r2 import utils
from r2.command_classes.base_command import BaseCommand
from prompt_toolkit.completion import Completion


class DebugCommand(BaseCommand):
    def __init__(self, io, coder):
        super().__init__(io, coder)

    def parse_input(self, args, files):
        if args.isspace() or args == '':
            self.io.tool_error("Provide a file name to use this command")
            return None
        elif args.split() != 1:
            self.io.tool_error("Provide an error message to use this command")
            return None

        file_path, error_message = args.split()

        if not [file for file in files if file_path in file]:
            file_path = self.create_files(file_path)

        return file_path, error_message

    def run(self, args, **kwargs):
        ''' 
            running debug command means adding files to the chat for the robot to debug with.
            running debug means passing debug messages in argument
        '''
        files = self.coder.get_all_relative_files()

        if (isinstance(args, str)):
            args, error_message = self.parse_input(args, files)

        if kwargs.get("debug"):
            debug_message = kwargs.get("error_message")
            self.get_help(args, debug_message)
        elif args and error_message:
            self.io.queue.enqueue(('execute_command', '/add', args))
            self.io.queue.enqueue(('send_new_command_message', error_message,
                                   "Expert Debugger"))

    def get_help(self, failing_file, error_message):
        # TODO; Pass exceptions from unit tests that do not contain formatting.
        cleaned_up_message = utils.remove_unneeded_symbols(error_message)
        self.io.tool_error(f"Error message: {cleaned_up_message}")

        messages = [
            self.coder.get_message("system", prompts.system_reminder),
            self.coder.get_message(
                "user", prompts.debug.format(message=cleaned_up_message))
        ]
        self.io.queue.enqueue(('send_new_command_message', messages,
                              "Expert Debugger"), to_front=True)
        self.io.queue.enqueue(
            ('execute_command', '/add', failing_file), to_front=True)

    def completions_debug(self, partial):
        files = set(self.coder.get_all_relative_files())
        files = files - set(self.coder.get_inchat_relative_files())
        for fname in files:
            if partial.lower() in fname.lower():
                yield Completion(fname, start_position=-len(partial))
