import os
from r2 import prompts
from r2.command_classes.base_command import BaseCommand
from prompt_toolkit.completion import Completion


class SpecFileCommand(BaseCommand):
    def __init__(self, io, coder):
        super().__init__(io, coder)

    def run(self, args, **kwargs):
        if args.isspace():
            self.io.tool_error("Add a file name to use this command")
            return

        create_spec_file = kwargs.get("create_spec_file")

        if create_spec_file:
            self.create_spec_file(args, kwargs.get("spec_file_git_path"))

        else:
            matched_files = []
            abs_file_path = []
            files = self.coder.get_all_relative_files()

            for word in args.split():
                matched_files = [file for file in files if word in file]

            for matched_file in matched_files:
                abs_file_path = os.path.abspath(os.path.join(self.coder.root, matched_file))

            self.io.tool_error(
                f"To implement /spec_file function from CLI - called for {abs_file_path}")

    def create_spec_file(self, program_file, spec_file):
        new_message = prompts.spec.format(
            spec_file_path=spec_file,
            file=program_file,
        )

        messages = [
            self.coder.get_message("system", prompts.system_reminder),
            self.coder.get_message("user", new_message)
        ]
        self.io.queue.enqueue(('send_new_command_message', messages, "Spec File"), to_front=True)
        self.io.queue.enqueue(('execute_command', '/add', program_file), to_front=True)

    def completions_spec_file(self, partial):
        files = set(self.coder.get_all_relative_files())
        files = files - set(self.coder.get_inchat_relative_files())
        for fname in files:
            if partial.lower() in fname.lower():
                yield Completion(fname, start_position=-len(partial))
