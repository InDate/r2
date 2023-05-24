import os
import subprocess
import sys
import tempfile
import unittest
import venv


class TestSetup(unittest.TestCase):
    def test_package_installation(self):
        # Create a temporary directory for the virtual environment
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a virtual environment
            venv.create(temp_dir, with_pip=True)

            # Install the package using setup.py
            subprocess.run(
                [sys.executable, "setup.py", "install"],
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                env={**os.environ, "VIRTUAL_ENV": temp_dir,
                     "PATH": f"{temp_dir}/bin:{os.environ['PATH']}"}
            )

            # Verify that the entry point script is created and can be executed
            try:
                subprocess.check_call(["r2", "--help"])
            except subprocess.CalledProcessError:
                self.fail("Entry point script execution failed")


if __name__ == "__main__":
    unittest.main()
