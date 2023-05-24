import os
import mimetypes
from r2.command_classes.base_command import BaseCommand

from r2.command_classes.execute_file_command import ExecuteFileCommand


class FileTypeCommand(BaseCommand):
    def __init__(self, io, coder):
        super().__init__(io, coder)

    def run(self, args):
        ''' 
            use to extract information from code file.
            output of program: provides a list of functions with descriptions
        '''
        program_path = args[0]
        function_path = args[1] if len(args) > 1 else None

        if not program_path or not function_path:
            self.io.tool_error(
                f"first argument: program that will extract functions, second argument: file that contains functions")
            return

        if not os.path.isfile(program_path):
            self.io.tool_error(f"{program_path} is not a valid file.")
            return

        if not os.path.isfile(function_path):
            self.io.tool_error(f"{function_path} is not a valid file.")
            return

        mime_type, _ = mimetypes.guess_type(function_path)
        if mime_type and "text" in mime_type:
            code_type = mime_type.split("/")[-1]
            self.io.print(f"{function_path} is a {code_type} code file.")
            execute_file_command = ExecuteFileCommand(self.io, self.coder)
            execute_file_command.run([program_path, function_path], "extract_methods")
        else:
            self.io.print(f"{function_path} is not a code file.")
