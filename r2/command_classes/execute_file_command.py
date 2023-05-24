import asyncio
from multiprocessing import Process, Queue
from r2.command_classes.base_command import BaseCommand
from r2.command_classes import execute_command
from prompt_toolkit.completion import Completion


def run_async_function(func, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(func(*args))
    loop.close()


class ExecuteFileCommand(BaseCommand):
    def __init__(self, io, coder):
        super().__init__(io, coder)
        self.__doc__ = 'Used to run python files, can override class ExecuteFileCommand to change functionality'

    def run(self, args, **kwargs):
        files = self.coder.get_all_relative_files()
        queue = Queue()
        internal_function_name = kwargs.get("function_name")

        if internal_function_name:
            execute_function = getattr(execute_command, internal_function_name)
        else:
            # Original execution logic
            execute_function = getattr(execute_command, 'execute_python_file')

        process = Process(target=run_async_function, args=(
            execute_function, args, files, queue))
        process.start()
        process.join()

        try:
            while not queue.empty():
                result = queue.get()
                return self.process_queue(result, args)
        finally:
            return self.process_queue(result, args)

    def process_queue(self, result, file_name):
        # TODO: currently a hack to return last message on queue, need to put queue in IO class
        if result["status"] == "error":
            message = "Test failed: Starting debugger"
            kwargs = {"debug": True, "error_message": result["message"]}
            next_command = ('execute_command', '/debug', file_name, kwargs,)

            self.io.queue.enqueue(next_command, to_front=True)

            return message

    def completions_execute_file(self, partial):
        files = self.coder.get_all_relative_files()
        python_files = [file for file in files if file.endswith(".py")]

        for fname in python_files:
            if partial.lower() in fname.lower():
                yield Completion(fname, start_position=-len(partial))
