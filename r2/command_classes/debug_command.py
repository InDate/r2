from r2 import prompts
from r2 import utils
from r2.command_classes.base_command import BaseCommand
from prompt_toolkit.completion import Completion


class DebugCommand(BaseCommand):
    def __init__(self, io, coder):
        super().__init__(io, coder)

    def run(self, args, **kwargs):
        ''' 
            running debug command means adding files to the chat for the robot to debug with.
            running debug means passing debug messages in argument
        '''

        if kwargs.get("debug"):
            debug_message = kwargs.get("error_message")
            self.get_help(args, debug_message)
        elif args.isspace():
            self.io.tool_error("Add a file name to use this command")
        else:
            matched_files = []
            files = self.coder.get_all_relative_files()

            for word in args.split():
                matched_files = [file for file in files if word in file]
                break

            for matched_file in matched_files:
                self.io.queue.enqueue(
                    ('execute_command', '/add', matched_file), to_front=True)

    def get_help(self, failing_file, error_message):
        # TODO; Pass exceptions from unit tests that do not contain formatting.
        cleaned_up_message = utils.remove_unneeded_symbols(error_message)
        self.io.tool_error(f"Error message: {cleaned_up_message}")

        messages = [
            self.coder.get_message("system", prompts.system_reminder),
            self.coder.get_message("user", prompts.debug.format(message=cleaned_up_message))
        ]
        self.io.queue.enqueue(('send_new_command_message', messages,
                              "Expert Debugger"), to_front=True)
        self.io.queue.enqueue(('execute_command', '/add', failing_file), to_front=True)

    def completions_debug(self, partial):
        files = set(self.coder.get_all_relative_files())
        files = files - set(self.coder.get_inchat_relative_files())
        for fname in files:
            if partial.lower() in fname.lower():
                yield Completion(fname, start_position=-len(partial))
