import os
from r2 import prompts
from r2.command_classes.base_command import BaseCommand
from prompt_toolkit.completion import Completion
from r2.utils import check_file_exists, get_file, is_file_type


class ExecuteTestsCommand(BaseCommand):
    def __init__(self, io, coder):
        super().__init__(io, coder)
        self.__doc__ = 'Used to execute unit tests for submitted file, will prompt to create if cannot be found'

    def run(self, args, **kwargs):
        if args.isspace() or args == '':
            self.io.tool_error("Add a file name to use this command")
            return

        create_unit_test = kwargs.get("create_unit_tests")

        if create_unit_test:
            test_file = kwargs.get("test_file")
            spec_file = kwargs.get("spec_file")
            self.create_unit_test(args, test_file, spec_file)
        elif args == ' all':
            self.io.tool_error('NOT IMPLEMENTED: Execute all unit tests')
        else:
            files = self.coder.get_all_relative_files()

            for word in args.split():
                matched_files = [file for file in files if word in file]

            if matched_files:
                self.execute_unit_test(matched_files)
            else: 
                self.io.tool_error('File not part of git repo')

    def create_unit_test(self, program_file, test_file, spec_file=None):
        new_message = prompts.professional_tester.format(
            program_file=program_file,
            unit_test_file=test_file,
        )

        messages = [
            self.coder.get_message("system", prompts.system_reminder),
            self.coder.get_message("user", new_message)
        ]
        self.io.queue.enqueue(('send_new_command_message', messages, "Unit Tester"), to_front=True)

    def completions_unit_test(self, partial):
        files = set(self.coder.get_all_relative_files())
        files = files - set(self.coder.get_inchat_relative_files())
        for fname in files:
            if partial.lower() in fname.lower():
                yield Completion(fname, start_position=-len(partial))

    def execute_unit_test(self, updated_files, auto_commit=False):
        # Implement the logic to run tests
        # Return True if tests pass, False otherwise
        to_front_of_queue = True if auto_commit else False

        for updated_file in updated_files:
            if is_file_type('spec', updated_file):
                return

            if is_file_type('tests', updated_file):
                return

            if not updated_file.endswith('.py') or not updated_file.endswith('.md'):
                return

            test_file_abs_path = get_file(updated_file, 'py', 'test', self.coder.test_dir)
            test_file = os.path.relpath(test_file_abs_path, self.coder.root)

            if not self.io.confirm_ask(
                    f"Test changes to {updated_file} [y/n]]?"):
                self.io.tool(f"Skipped: {test_file}")
                return

            if check_file_exists(test_file_abs_path):
                # TODO: Add further logic to extend unit_test if change are significant.
                self.io.queue.enqueue(('execute_command', '/execute_file',
                                      test_file), to_front=to_front_of_queue)

            elif self.io.confirm_ask(f"Test file: {test_file} not found, create test now?"):
                self.io.queue.enqueue(
                    ('execute_command', '/execute_file', test_file), to_front=True)
                self.io.queue.enqueue(('execute_command', '/unit_test', updated_file,
                                      {"create_unit_tests": True, "test_file": test_file}), to_front=True)
                self.io.queue.enqueue(('execute_command', '/add', updated_file), to_front=True)
