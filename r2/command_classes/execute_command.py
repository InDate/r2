import os
import asyncio


def find_common_root(files):
    if files:
        common_prefix = os.path.commonpath(files)
        return os.path.dirname(common_prefix)
    else:
        return os.getcwd()


async def execute_python_test(file, files, queue):
    try:
        if file == 'all':
            queue.put(
                {f"status": "status", "update": "Performing unit test with all tests"})
            process = await asyncio.create_subprocess_exec(
                "python3", "-m", "unittest", "discover", "-s", files,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
        else:
            root = find_common_root(files)
            filename = os.path.abspath(os.path.join(root, file))

            if not filename.endswith(".py"):
                raise ValueError("Invalid file type. Only .py files.")

            if "test" not in os.path.basename(filename):
                raise ValueError("Invalid file type. Only test files.")

            queue.put(
                {"status": "update", "message": f"Unit testing '{file}'..."})
            process = await asyncio.create_subprocess_shell(
                "python3", "-m", "unittest", filename,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

        stdout, stderr = await process.communicate()
        returncode = process.returncode
    except Exception as e:
        queue.put({"status": "error", "message": str(e)})
        raise

    if returncode == 0:
        queue.put(
            {"status": "update", "message": f"Unit testing '{file}'...passed."})
        queue.put(
            {"status": "success", "message": f"Process complete with stdout message {stdout.decode()}"})
    else:
        queue.put({"status": "error", "message": stderr.decode()})


async def execute_python_file(file, files, queue):
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
