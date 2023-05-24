from .base_command import BaseCommand
import os
from rich.prompt import Confirm
from prompt_toolkit.completion import Completion


class LSCommand(BaseCommand):
    def __init__(self, io, coder):
        super().__init__(io, coder)

    def run(self, args):
        "List all known files and those included in the chat session"
        chat_files, other_files = self.list_files_command()

        if chat_files:
            self.io.tool("Files in chat:\n")
        for file in chat_files:
            self.io.tool(f"  {file}")

        if other_files:
            self.io.tool("\nRepo files not in the chat:\n")
        for file in other_files:
            self.io.tool(f"  {file}")

    def list_files_command(self):
        files = self.coder.get_all_relative_files()

        other_files = []
        chat_files = []
        for file in files:
            abs_file_path = os.path.abspath(os.path.join(self.coder.root, file))
            if abs_file_path in self.coder.abs_fnames:
                chat_files.append(file)
            else:
                other_files.append(file)

        return chat_files, other_files
