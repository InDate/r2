import traceback
from r2 import prompts, utils
from pathlib import Path
import os


class FileManager:
    def __init__(self, io):
        print('init FileM')
        self.io = io
        self.repo = None

    def get_context_from_history(self, history):
        context = ""
        if history:
            context += "# Context:\n"
            for msg in history:
                context += msg["role"].upper() + ": " + msg["content"] + "\n"
        return context

    def get_rel_fname(self, fname):
        return os.path.relpath(fname, self.root)

    def get_inchat_relative_files(self):
        files = [self.get_rel_fname(fname) for fname in self.abs_fnames]
        return sorted(set(files))

    def get_all_relative_files(self):
        if self.repo:
            files = self.repo.git.ls_files().splitlines()
        else:
            files = self.get_inchat_relative_files()

        return sorted(set(files))

    def find_common_root(self):
        if self.abs_fnames:
            common_prefix = os.path.commonpath(list(self.abs_fnames))
            self.root = os.path.dirname(common_prefix)
        else:
            self.root = os.getcwd()

        self.io.tool(f"Common root directory: {self.root}")

    def check_for_file_mentions(self, content):
        words = set(word for word in content.split())

        # drop sentence punctuation from the end
        words = set(word.rstrip(",.!;") for word in words)

        # strip away all kinds of quotes
        quotes = "".join(['"', "'", "`"])
        words = set(word.strip(quotes) for word in words)

        addable_rel_fnames = set(self.get_all_relative_files()) - set(
            self.get_inchat_relative_files()
        )

        mentioned_rel_fnames = set()
        for word in words:
            if word in addable_rel_fnames:
                mentioned_rel_fnames.add(word)

        if not mentioned_rel_fnames:
            return

        for rel_fname in mentioned_rel_fnames:
            self.io.tool(rel_fname)

        return mentioned_rel_fnames

    def update_files(self, content, inp):
        # might raise ValueError for malformed ORIG/UPD blocks
        edits = list(utils.find_original_update_blocks(content))

        edited = set()
        for path, original, updated in edits:
            full_path = os.path.abspath(os.path.join(self.root, path))

            if full_path not in self.abs_fnames:
                if not Path(full_path).exists():
                    question = f"Allow creation of new file {path}?"  # noqa: E501
                else:
                    question = (
                        f"Allow edits to {path} which was not previously provided?"  # noqa: E501
                    )
                if not self.io.confirm_ask(question):
                    self.io.tool_error(f"Skipping edit to {path}")
                    continue

                if not Path(full_path).exists():
                    Path(full_path).parent.mkdir(parents=True, exist_ok=True)
                    Path(full_path).touch()

                self.abs_fnames.add(full_path)

                # Check if the file is already in the repo
                if self.repo:
                    tracked_files = set(self.repo.git.ls_files().splitlines())
                    relative_fname = self.get_rel_fname(full_path)
                    if relative_fname not in tracked_files and self.io.confirm_ask(
                        f"Add {path} to git?"
                    ):
                        self.repo.git.add(full_path)

            edited.add(path)
            if utils.do_replace(full_path, original, updated, self.dry_run):
                if self.dry_run:
                    self.io.tool(f"Dry run, did not apply edit to {path}")
                else:
                    self.io.tool(f"Applied edit to {path}")
            else:
                self.io.tool_error(f"Failed to apply edit to {path}")

        return edited

    def get_test_file(self, file_path):
        """Returns the equiv test file in the testing folder."""
        file_dir, file_name = os.path.split(file_path)
        test_file_name = f"test_{file_name}"
        if file_dir.isspace():
            common_path = os.path.commonpath([self.test_dir, file_dir])
        else:
            common_path = self.test_dir

        relative_path = os.path.relpath(file_dir, common_path)
        path_parts = relative_path.split(os.sep)
        removed_app_name = os.sep.join(path_parts[2:])
        test_file = os.path.join(
            self.test_dir, removed_app_name, test_file_name)
        return test_file

    def apply_updates(self, content, inp):
        try:
            edited = self.update_files(content, inp)
            return edited, None
        except ValueError as err:
            err = err.args[0]
            self.io.tool_error("Malformed ORIGINAL/UPDATE blocks, retrying...")
            self.io.tool_error(str(err))
            return None, err

        except Exception as err:
            print(err)
            print()
            traceback.print_exc()
            return None, err

    def find_test_directory(self):
        all_files = self.get_all_relative_files()
        test_dirs = [f for f in all_files if f.startswith(
            "tests/") or f.startswith("test/")]

        if not test_dirs:
            self.io.tool_error("No test directory found.")
            return

        test_dir = os.path.commonprefix(test_dirs)
        if not test_dir.endswith("/"):
            test_dir += "/"

        self.test_dir = self.root + "/" + test_dir
        self.io.tool(f"Test directory found: {self.test_dir}")
