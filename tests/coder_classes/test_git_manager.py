import os
import tempfile
import shutil
import unittest
from unittest.mock import MagicMock
from git import Repo
from r2.coder_classes.git_manager import GitManager


class TestGitManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.repo = Repo.init(self.temp_dir)
        self.io = MagicMock()
        self.git_manager = GitManager(self.io)
        self.git_manager.repo = self.repo
        self.git_manager.root = self.temp_dir

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_get_diffs(self):
        # Test the get_diffs method by creating a new file, adding it to the repo, and checking the diffs
        file_path = os.path.join(self.temp_dir, "test_file.txt")
        with open(file_path, "w") as f:
            f.write("This is a test file.")

        self.repo.index.add([file_path])
        self.repo.index.commit("Initial commit")

        with open(file_path, "a") as f:
            f.write("\nAdding a new line.")

        diffs = self.git_manager.get_diffs()
        self.assertIn("test_file.txt", diffs)

    # Add more test methods for other GitManager methods


if __name__ == "__main__":
    unittest.main()
