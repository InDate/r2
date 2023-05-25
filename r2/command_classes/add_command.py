from r2 import prompts
from .base_command import BaseCommand
import os
from prompt_toolkit.completion import Completion


class AddCommand(BaseCommand):
    def __init__(self, io, coder):
        self.__doc__ = 'Adds files into the chat. Once a file is added, the contents are shared with the LLM'
        super().__init__(io, coder)

    def run(self, args):
        files = self.coder.get_all_relative_files()

        if (isinstance(args, str)):
            ask = False
            args = self.parse_input(args, files, add=True)

        added_file_names = self.add_files_command(args, ask=True)

        if not added_file_names:
            self.io.tool_error(f"No files matched '{args}'")
        else:
            for fname in added_file_names:
                self.io.tool(f"Added {fname} to the chat")

            # add prompt backed to LLM, if responding to add files
            if self.coder.current_messages:
                reply = prompts.added_files.format(
                    fnames=", ".join(added_file_names))
                return reply

    def add_files_command(self, matched_files, ask=True):
        added_fnames = []

        for matched_file in matched_files:
            abs_file_path = os.path.abspath(
                os.path.join(self.coder.root, matched_file))
            if abs_file_path not in self.coder.abs_fnames:
                ask = self.io.confirm_ask(
                    f"File '{matched_file}' is required in the chat, add now? [y/n]") if ask else True
                if ask:
                    self.coder.abs_fnames.add(abs_file_path)
                    added_fnames.append(matched_file)
            else:
                self.io.tool(f"'{matched_file}' was previously added.")

        return added_fnames

    def completions_add(self, partial):
        files = set(self.coder.get_all_relative_files())
        files = files - set(self.coder.get_inchat_relative_files())
        for fname in files:
            if partial.lower() in fname.lower():
                yield Completion(fname, start_position=-len(partial))
