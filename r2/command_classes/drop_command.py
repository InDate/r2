from .base_command import BaseCommand
import os
from rich.prompt import Confirm
from prompt_toolkit.completion import Completion


class DropCommand(BaseCommand):
    def __init__(self, io, coder):
        super().__init__(io, coder)

    def run(self, args, **kwargs):
        notify = kwargs.get('notify')

        for word in args.split():
            matched_files = [
                file
                for file in self.coder.abs_fnames
                if word.lower() in os.path.relpath(file, self.coder.root).lower()
            ]
            if word == 'all':
                matched_files = self.coder.abs_fnames
            elif not matched_files:
                self.io.tool_error(f"No files matched '{word}'")

            self.remove_files_from_chat(matched_files, notify)

    def remove_files_from_chat(self, matched_files, notify=False):
        for matched_file in matched_files:
            relative_fname = os.path.relpath(matched_file, self.coder.root)
            self.coder.abs_fnames.remove(matched_file)

            if notify:
                self.io.tool(f"Removed {relative_fname} from the chat")

    def completions_drop(self, partial):
        files = self.coder.get_inchat_relative_files()

        for fname in files:
            if partial.lower() in fname.lower():
                yield Completion(fname, start_position=-len(partial))
