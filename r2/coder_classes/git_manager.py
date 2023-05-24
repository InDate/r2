import os
from pathlib import Path
from r2 import prompts
from r2.commands import Commands
from r2.coder_classes.file_manager import FileManager
import git


class GitManager(FileManager):
    def __init__(self, io):
        self.current_messages = []
        self.io = io
        self.commands = Commands(io, self)
        self.show_diffs = True
        self.abs_fnames = set()
        self.last_asked_for_commit_time = 0
        self.last_r2_commit_hash = None
        self.pretty = None

    def get_diffs(self, *args):
        if self.pretty:
            args = ["--color"] + list(args)

        diffs = self.repo.git.diff(*args)
        return diffs

    def get_diffs_file_names(self, *args):
        diff_output = self.repo.git.diff("--name-only", *args)
        file_names = diff_output.splitlines()
        return file_names

    def commit(self, history=None, prefix=None, ask=False, message=None, which="chat_files"):
        if not self._should_commit():
            return False

        relative_dirty_fnames, diffs = self._get_dirty_files_and_diffs(which)

        if self.show_diffs or ask:
            # print so it does not record in tool chat
            print(diffs)

        commit_message = self._get_commit_message(history, message, diffs)

        if ask:
            commit_message = self._ask_for_commit_message(commit_message, which)

        diff_file_names = self.get_diffs_file_names("HEAD", "--", relative_dirty_fnames)

        self._queue_test_changes(diff_file_names)
        self._queue_spec_file(diff_file_names)

        commit_hash, commit_message = self._perform_commit(
            relative_dirty_fnames, commit_message, prefix)
        self.last_asked_for_commit_time = self.get_last_modified()

        return commit_hash, commit_message

    def auto_commit(self):
        res = self.commit(history=self.current_messages, prefix="r2: ")
        if res:
            commit_hash, commit_message = res
            self.last_r2_commit_hash = commit_hash

            saved_message = prompts.files_content_gpt_edits.format(
                hash=commit_hash,
                message=commit_message,
            )
        else:
            # TODO: if not self.repo then the files_content_gpt_no_edits isn't appropriate
            self.io.tool_error("Warning: no changes found in tracked files.")
            saved_message = prompts.files_content_gpt_no_edits

        self.done_messages += self.current_messages
        self.done_messages += [
            dict(role="user", content=saved_message),
            dict(role="assistant", content="Ok."),
        ]
        self.current_messages = []

        return

    def _queue_spec_file(self, updated_files):
        # build spec for file
        for updated_file in updated_files:
            # test_file - do not spec
            if self.is_file_type('tests', updated_file):
                return

            if self.is_file_type('spec', updated_file):
                return

            spec_file = self.get_file(updated_file, 'md', 'spec', self.root + '/spec/')
            spec_file_git_path = os.path.relpath(spec_file, self.root)

            if not self.check_file_exists(spec_file):
                spec_file_git_path = os.path.relpath(spec_file, self.root)

                if self.io.confirm_ask(
                        f"Spec file: {spec_file_git_path} not found, create before commit [y/n]?"):
                    # TODO: Need to ensure that add file is only adding and removing for the task required, might be better to put add commands in execute_command process.
                    self.io.queue.enqueue(('execute_command', '/spec_file', updated_file, {
                                          "create_spec_file": True, "spec_file_git_path": spec_file_git_path}), to_front=True)
            # else:
                # TODO: Add further logic to extend unit_test if change are significant.
                # self.io.tool(f"Spec File Found: {spec_file_git_path}")

        return spec_file_git_path

    def _queue_test_changes(self, updated_files, auto_commit=False):
        # Implement the logic to run tests
        # Return True if tests pass, False otherwise
        to_front_of_queue = True if auto_commit else False

        if isinstance(updated_files, str):
            updated_files = [updated_files]

        for updated_file in updated_files:
            if self.is_file_type('spec', updated_file):
                return

            if self.is_file_type('tests', updated_file):
                return

            if not updated_file.endswith('.py') or not updated_file.endswith('.md'):
                return

            test_file_abs_path = self.get_file(updated_file, 'py', 'test', self.test_dir)
            test_file = os.path.relpath(test_file_abs_path, self.root)

            if not self.io.confirm_ask(
                    f"Test changes to {updated_file} [y/n]]?"):
                self.io.tool(f"Skipped: {test_file}")
                return

            if self.check_file_exists(test_file_abs_path):
                # TODO: Add further logic to extend unit_test if change are significant.
                self.io.queue.enqueue(('execute_command', '/execute_file',
                                      test_file), to_front=to_front_of_queue)

            elif self.io.confirm_ask(f"Test file: {test_file} not found, queue create test?"):
                # testing file does not exist. Need to create testing file here.
                self.io.queue.enqueue(
                    ('execute_command', '/execute_file', test_file), to_front=True)
                self.io.queue.enqueue(('execute_command', '/unit_test', updated_file,
                                      {"create_unit_tests": True, "test_file": test_file}), to_front=True)
                self.io.queue.enqueue(('execute_command', '/add', updated_file), to_front=True)

    def set_repo(self, cmd_line_fnames):
        if not cmd_line_fnames:
            cmd_line_fnames = ["."]

        repo_paths = []
        for fname in cmd_line_fnames:
            fname = Path(fname)
            if not fname.exists():
                self.io.tool(f"Creating empty file {fname}")
                fname.parent.mkdir(parents=True, exist_ok=True)
                fname.touch()

            try:
                repo_path = git.Repo(fname, search_parent_directories=True).git_dir
                repo_paths.append(repo_path)
            except git.exc.InvalidGitRepositoryError:
                pass

            if fname.is_dir():
                continue

            self.io.tool(f"Added {fname} to the chat")

            fname = fname.resolve()
            self.abs_fnames.add(str(fname))

        num_repos = len(set(repo_paths))

        if num_repos == 0:
            self.io.tool_error("Files are not in a git repo.")
            return
        if num_repos > 1:
            self.io.tool_error("Files are in different git repos.")
            return

        # https://github.com/gitpython-developers/GitPython/issues/427
        repo = git.Repo(repo_paths.pop(), odbt=git.GitDB)

        self.root = repo.working_tree_dir

        new_files = []
        for fname in self.abs_fnames:
            relative_fname = self.get_rel_fname(fname)
            tracked_files = set(repo.git.ls_files().splitlines())
            if relative_fname not in tracked_files:
                new_files.append(relative_fname)

        if new_files:
            rel_repo_dir = os.path.relpath(repo.git_dir, os.getcwd())

            self.io.tool(f"Files not tracked in {rel_repo_dir}:")
            for fn in new_files:
                self.io.tool(f" - {fn}")
            if self.io.confirm_ask("Add them?"):
                for relative_fname in new_files:
                    repo.git.add(relative_fname)
                    self.io.tool(f"Added {relative_fname} to the git repo.")
                show_files = ", ".join(new_files)
                commit_message = f"Added new files to the git repo: {show_files}"
                repo.git.commit("-m", commit_message, "--no-verify")
                commit_hash = repo.head.commit.hexsha[:7]
                self.io.tool(f"Commit {commit_hash} {commit_message}")
            else:
                self.io.tool_error("Skipped adding new files to the git repo.")
                return

        self.repo = repo

    def get_all_abs_files(self):
        files = self.get_all_relative_files()
        files = [os.path.abspath(os.path.join(self.root, path)) for path in files]
        return files

    def get_last_modified(self):
        files = self.get_all_abs_files()
        if not files:
            return 0
        return max(Path(path).stat().st_mtime for path in files)

    def should_auto_commit(self, inp):
        is_commit_command = inp and inp.startswith("/commit")

        if not self.auto_commits:
            return
        if not self.repo:
            return
        if not self.repo.is_dirty():
            return
        if is_commit_command:
            return
        if self.last_asked_for_commit_time >= self.get_last_modified():
            return
        return True

    def _generate_commit_message(self, diffs, context):
        diffs = "# Diffs:\n" + diffs

        messages = [
            dict(role="system", content=prompts.commit_system),
            dict(role="user", content=context + diffs),
        ]

        ###
        # Sending to API here!
        ###

        commit_message, interrupted = self.send_to_llm(
            messages,
            model="gpt-3.5-turbo",
            silent=True,
        )

        commit_message = commit_message.strip().strip('"').strip()

        if interrupted:
            self.io.tool_error(
                "Unable to get commit message from gpt-3.5-turbo. Use /commit to try again."
            )
            return

        return commit_message

    def _should_commit(self):
        """Check if the commit should be performed."""
        repo = self.repo
        if not repo:
            return False

        if not repo.is_dirty():
            return False

        return True

    def _get_dirty_files_and_diffs(self, which):
        """Get dirty files and their diffs based on the 'which' parameter."""
        if which == "repo_files":
            all_files = [os.path.join(self.root, f) for f in self.get_all_relative_files()]
            relative_dirty_fnames, diffs = self._get_dirty_files_and_diffs_helper(all_files)
        elif which == "chat_files":
            relative_dirty_fnames, diffs = self._get_dirty_files_and_diffs_helper(self.abs_fnames)
        else:
            raise ValueError(f"Invalid value for 'which': {which}")

        return relative_dirty_fnames, diffs

    def _get_dirty_files_and_diffs_helper(self, file_list):
        """Helper function to get dirty files and their diffs."""
        diffs = ""
        relative_dirty_files = []
        for fname in file_list:
            relative_fname = self.get_rel_fname(fname)
            relative_dirty_files.append(relative_fname)

            try:
                current_branch_commit_count = len(
                    list(self.repo.iter_commits(self.repo.active_branch))
                )
            except git.exc.GitCommandError:
                current_branch_commit_count = None

            if not current_branch_commit_count:
                continue

            these_diffs = self.get_diffs("HEAD", "--", relative_fname)

            if these_diffs:
                diffs += these_diffs + "\n"

        return relative_dirty_files, diffs

    def _get_commit_message(self, history, message, diffs):
        """Get the commit message."""
        context = self.get_context_from_history(history)
        if message:
            commit_message = message
        else:
            self.io.tool("No commit message found, generating...")
            commit_message = self._generate_commit_message(diffs, context)

        return commit_message

    def _ask_for_commit_message(self, commit_message, which):
        """Ask the user for a commit message."""
        if which == "repo_files":
            self.io.tool("Git repo has uncommitted changes.")
        else:
            self.io.tool("Files have uncommitted changes.")

        res = self.io.prompt_ask(
            "Suggested commit message [commit message]: ",
            default=commit_message,
        ).strip()

        self.io.tool()

        if res.lower() not in ["y", "yes"] and res:
            commit_message = res

        return commit_message

    def _perform_commit(self, relative_dirty_fnames, commit_message, prefix):
        """Perform the commit."""
        repo = self.repo
        repo.git.add(*relative_dirty_fnames)

        full_commit_message = commit_message + "\n\n" + \
            self.get_context_from_history(self.current_messages)
        if prefix:
            full_commit_message = prefix + full_commit_message

        repo.git.commit("-m", full_commit_message, "--no-verify")
        commit_hash = repo.head.commit.hexsha[:7]
        self.io.tool(f"Commit {commit_hash} {commit_message}")

        return commit_hash, commit_message
