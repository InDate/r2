import os
import asyncio
from multiprocessing import Queue


def find_common_root(files):
    if files:
        common_prefix = os.path.commonpath(files)
        return os.path.dirname(common_prefix)
    else:
        return os.getcwd()


async def execute_python_file(args, files, queue: Queue):
    "Execute a Python file"
    root = find_common_root(files)
    matched_files = []

    for word in args.split():
        matched_files.extend([file for file in files if word in file])

    if not matched_files:
        raise FileNotFoundError("Error: No matching file found.")

    for matched_file in matched_files:
        filename = os.path.abspath(os.path.join(root, matched_file))
        break

    if not filename:
        raise FileNotFoundError("Error: No filename provided.")

    if not filename.endswith(".py"):
        raise ValueError("Invalid file type. Only .py files are allowed.")

    is_test_file = "test" in os.path.basename(filename)

    if not os.path.isfile(filename):
        raise FileNotFoundError(f"Error: File '{filename}' does not exist.")

    try:
        if is_test_file:
            queue.put(
                {f"status": "status", "message": "Performing Unit test: %s" % filename})
            process = await asyncio.create_subprocess_exec(
                "python3", "-m", "unittest", filename,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
        else:
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
