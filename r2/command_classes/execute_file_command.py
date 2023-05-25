import asyncio
from multiprocessing import Process, Queue
from r2.command_classes.base_command import BaseCommand
from r2.command_classes import execute_command
from prompt_toolkit.completion import Completion


def run_async_function(func, *args, timeout=5):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(
            asyncio.wait_for(func(*args), timeout=timeout))
    except asyncio.TimeoutError:
        print(
            f"The function '{func}' with args '{args}' took too long to complete and was stopped after {timeout} seconds.")
        result = None  # You can set a default value or handle the situation differently
    finally:
        loop.close()

    return result


class ExecuteFileCommand(BaseCommand):
    def __init__(self, io, coder):
        super().__init__(io, coder)
        self.queue = Queue()
        self.__doc__ = 'Use to execute python file and commands, can override class ExecuteFileCommand to change functionality'

    def run(self, args, **kwargs):
        files = self.coder.get_all_relative_files()
        result = []

        if (isinstance(args, str)):
            args = self.parse_input(args, files)

        if kwargs.get("function_name"):
            files = self.coder.test_dir if 'all' in args else files
            execute_function = getattr(
                execute_command, kwargs.get("function_name"))
        elif len(args) == 0:
            self.io.tool_error(f'File not found in Git Repo: {args}')
            return
        else:
            execute_function = getattr(execute_command, 'execute_python_file')

        for file in args:
            process = Process(target=run_async_function, args=(
                execute_function, file, files, self.queue))
            process.start()
            process.join()

        try:
            while not self.queue.empty():
                result = self.queue.get()
                self.process_queue(result, args)
        finally:
            self.process_queue(result, args)

    def process_queue(self, result, file_name):
        # TODO: currently a hack to return last message on queue, need to put queue in IO class
        if result["status"] == "error":
            if self.io.confirm_ask(
                    'An error occured with "%s", would you like to debug now? [y/n]' % '", "'.join(file_name)):
                kwargs = {"debug": True, "error_message": result["message"]}
                next_command = ('execute_command', '/debug',
                                file_name, kwargs,)

                self.io.queue.enqueue(next_command, to_front=True)
        elif result["status"] == "update":
            self.io.tool(result['message'])

    def completions_execute_file(self, partial):
        files = self.coder.get_all_relative_files()
        python_files = [file for file in files if file.endswith(".py")]

        for fname in python_files:
            if partial.lower() in fname.lower():
                yield Completion(fname, start_position=-len(partial))
