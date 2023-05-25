from r2 import prompts
from r2 import utils
from r2.command_classes.base_command import BaseCommand
from prompt_toolkit.completion import Completion


class DebugCommand(BaseCommand):
    def __init__(self, io, coder):
        super().__init__(io, coder)

    def parse_input(self, args):
        if args.isspace() or args == '':
            self.io.tool_error("Provide a file name to use this command")
            return None, None

        file_path = args.split()[0]
        existing_git_files = self.coder.get_all_relative_files()
        if not [file for file in existing_git_files if file_path in file]:
            file_path = self.create_files(file_path)

        if not file_path:
            self.io.tool_error(
                "A file contained within the Git Repo is required")
            return None, None

        debug_message = args.split(file_path)

        if len(debug_message) != 2:
            self.io.tool_error(
                "Provide debug instructions after file name")
            return None, None
        else:
            debug_message = debug_message[1]

        return file_path, debug_message

    def run(self, args, **kwargs):
        if kwargs.get("debug"):
            debug_message = kwargs.get("error_message")
        elif (isinstance(args, str)):
            args, debug_message = self.parse_input(args)

        if args and debug_message:
            self.get_help(args, debug_message)

    def get_help(self, failing_file, error_message):
        # TODO; Pass exceptions from unit tests that do not contain formatting.
        cleaned_up_message = utils.remove_unneeded_symbols(error_message)
        self.io.tool("")
        self.io.tool_error(f"Error message: {error_message}")

        if not self.io.confirm_ask(
                'An error occured with "%s", would you like to debug now? [y/n]' % '", "'.join(failing_file)):
            return

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
