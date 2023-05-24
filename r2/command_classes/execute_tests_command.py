from r2 import prompts
from r2.command_classes.base_command import BaseCommand
from prompt_toolkit.completion import Completion


class ExecuteTestsCommand(BaseCommand):
    def __init__(self, io, coder):
        super().__init__(io, coder)

    def run(self, args, **kwargs):
        ''' 
            use to extract information from code file.
            output of program: provides a list of functions with descriptions
        '''
        if args.isspace():
            self.io.tool_error("Add a file name to use this command")
            return

        create_unit_test = kwargs.get("create_unit_tests")

        if create_unit_test:
            test_file = kwargs.get("test_file")
            spec_file = kwargs.get("spec_file")
            self.create_unit_test(args, test_file, spec_file)

        else:
            file = args.split()[0]
            files = self.coder.get_all_relative_files()

            for word in args.split():
                matched_files = [file for file in files if word in file]

            if file in files:
                # TODO: This is referencing coding class, better to add to queue.
                self.coder._test_changes_before_commit(file)

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
