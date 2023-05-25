import os
import re
from rich.prompt import Confirm


class BaseCommand:
    def __init__(self, io, coder):
        self.io = io
        self.coder = coder

    def run(self, args):
        raise NotImplementedError(
            "The run method must be implemented in the derived class.")

    def has_extension(self, string):
        _, file_extension = os.path.splitext(string)
        if file_extension is not None:
            return True
        else:
            return False

    def create_files(self, word):
        if not self.has_extension(word):
            self.io.tool_error(
                f"Expecting directory and file with extension, got: '{word}'")
            return

        if self.coder.repo is not None and word is not None:
            create_file = Confirm.ask(
                f"No files matched '{word}'. Do you want to create the file and add it to git?",
            )
        else:
            create_file = Confirm.ask(
                f"No files matched '{word}'. Do you want to create the file?"
            )

        if create_file:
            with open(os.path.join(self.coder.root, word), "w"):
                pass
            if self.coder.repo is not None:
                self.coder.repo.git.add(
                    os.path.join(self.coder.root, word))
                commit_message = f"r2: Created and added {word} to git."
                self.coder.repo.git.commit(
                    "-m", commit_message, "--no-verify")
            return word
        else:
            self.io.tool_error(f"No files matched '{word}'")
            return None

    def parse_input(self, args, files, add=False):
        if args.isspace() or args == '':
            self.io.tool_error("Provide a file name to use this command")
            return None
        elif args == ' all' or args == 'all':
            return ['all']
        elif add:
            args += self.create_files(args)

        for word in args.split():
            return [file for file in files if word in file]
