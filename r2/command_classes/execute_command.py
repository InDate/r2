import os
import asyncio
from multiprocessing import Queue


def find_common_root(files):
    if files:
        common_prefix = os.path.commonpath(files)
        return os.path.dirname(common_prefix)
    else:
        return os.getcwd()


async def execute_python_test(file, files, queue: Queue):
    "Execute a Python test"
    root = find_common_root(files)
    filename = os.path.abspath(os.path.join(root, file))

    if not filename.endswith(".py"):
        raise ValueError("Invalid file type. Only .py files.")

    if "test" not in os.path.basename(filename):
        raise ValueError("Invalid file type. Only test files.")

    try:
        if file == 'all':
            queue.put(
                {f"status": "status", "message": "Performing unit test with all tests"})
            process = await asyncio.create_subprocess_exec(
                "python3", "-m", "unittest", "discover", "-s", files,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
        else:
            queue.put(
                {f"status": "status", "message": "Performing Unit test: %s" % filename})
            process = await asyncio.create_subprocess_exec(
                "python3", "-m", "unittest", filename,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
        stdout, stderr = await process.communicate()
        returncode = process.returncode
    except Exception as e:
        queue.put({"status": "error", "message": str(e)})
        raise

    if returncode != 0:
        queue.put({"status": "error", "message": str(stderr)})
    elif len(stdout) > 0:
        queue.put({"status": "success", "message": str(stdout)})

    return


async def execute_python_file(file, files, queue: Queue):
    "Execute a Python file"
    root = find_common_root(files)
    filename = os.path.abspath(os.path.join(root, file))

    if not filename.endswith(".py"):
        raise ValueError("Invalid file type. Only .py files.")

    try:
        queue.put(
            {"status": "status", "message": "Executing File: %s" % filename})
        process = await asyncio.create_subprocess_exec(
            "python3", filename,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()
        returncode = process.returncode
    except Exception as e:
        queue.put({"status": "error", "message": str(e)})
        raise

    if returncode != 0:
        queue.put({"status": "error", "message": str(stderr)})
    elif len(stdout) > 0:
        queue.put({"status": "success", "message": str(stdout)})

    return
