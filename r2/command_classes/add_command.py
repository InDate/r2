from r2 import prompts
from .base_command import BaseCommand
import os
from rich.prompt import Confirm
from prompt_toolkit.completion import Completion


class AddCommand(BaseCommand):
    def __init__(self, io, coder):
        super().__init__(io, coder)

    def run(self, args):
        if args.isspace():
            self.io.tool_error("Add a file name to use this command")
            return

        added_file_names = self.add_files_command(args)

        if not added_file_names:
            self.io.tool_error(f"No files matched '{args}'")
        else:
            for fname in added_file_names:
                self.io.tool(f"Added {fname} to the chat")

            # only reply if there's been some chatting since the last edit
            if self.coder.current_messages:
                reply = prompts.added_files.format(fnames=", ".join(added_file_names))
                return reply

    def add_files_command(self, args):
        added_fnames = []
        matched_files = []
        files = self.coder.get_all_relative_files()

        for word in args.split():
            matched_files = [file for file in files if word in file]

        if not matched_files:

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
                matched_files = [word]
                if self.coder.repo is not None:
                    self.coder.repo.git.add(os.path.join(self.coder.root, word))
                    commit_message = f"r2: Created and added {word} to git."
                    self.coder.repo.git.commit("-m", commit_message, "--no-verify")
            else:
                return f"No files matched '{word}'"

        for matched_file in matched_files:
            abs_file_path = os.path.abspath(os.path.join(self.coder.root, matched_file))
            if abs_file_path not in self.coder.abs_fnames:
                self.coder.abs_fnames.add(abs_file_path)
                added_fnames.append(matched_file)
            else:
                return f"{matched_file} is already in the chat"

        return added_fnames

    def completions_add(self, partial):
        files = set(self.coder.get_all_relative_files())
        files = files - set(self.coder.get_inchat_relative_files())
        for fname in files:
            if partial.lower() in fname.lower():
                yield Completion(fname, start_position=-len(partial))
