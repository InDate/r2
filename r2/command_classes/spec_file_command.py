import os
from r2 import prompts
from r2.command_classes.base_command import BaseCommand
from prompt_toolkit.completion import Completion

from r2.utils import check_file_exists, get_file, is_file_type


class SpecFileCommand(BaseCommand):
    def __init__(self, io, coder):
        __doc__ == 'Generates a code2text specifications file for used with LLMs, this is used to for mapping the entire program'
        super().__init__(io, coder)

    def run(self, args, **kwargs):
        files = self.coder.get_all_relative_files()

        if (isinstance(args, str)):
            if args.isspace() or args == '':
                self.io.tool_error("Provide a file name to use this command")
                return

            for word in args.split():
                args = [file for file in files if word in file]

        if kwargs.get("create_spec_file"):
            self.create_spec_file(args, kwargs.get("spec_file_git_path"))
        else:
            self.get_spec_file(args, files)

    def create_spec_file(self, program_file, spec_file):
        new_message = prompts.spec.format(
            spec_file_path=spec_file,
            file=program_file,
        )

        messages = [
            self.coder.get_message("system", prompts.system_reminder),
            self.coder.get_message("user", new_message)
        ]
        self.io.queue.enqueue(
            ('send_new_command_message', messages, "Spec File"), to_front=True)
        self.io.queue.enqueue(
            ('execute_command', '/add', program_file), to_front=True)

    def completions_spec_file(self, partial):
        files = set(self.coder.get_all_relative_files())
        files = files - set(self.coder.get_inchat_relative_files())
        for fname in files:
            if partial.lower() in fname.lower():
                yield Completion(fname, start_position=-len(partial))

    def get_spec_file(self, updated_files, all_files):
        for updated_file in updated_files:
            if is_file_type('tests', updated_file):
                return

            if is_file_type('spec', updated_file):
                return

            if updated_file not in all_files:
                self.io.tool_error(
                    f'File Not found within git repo: {updated_file}')
                return

            spec_file = get_file(updated_file, 'md',
                                 'spec', self.coder.root + '/spec/')
            spec_file_git_path = os.path.relpath(spec_file, self.coder.root)

            if not check_file_exists(spec_file_git_path, all_files):
                if self.io.confirm_ask(
                        f"Spec file: {spec_file_git_path} not found, create before commit? [y/n]"):
                    self.io.queue.enqueue(('execute_command', '/spec_file', updated_file, {
                                          "create_spec_file": True, "spec_file_git_path": spec_file_git_path}), to_front=True)
            else:
                self.io.tool(f"Spec File Found: {spec_file_git_path}")

        return None
