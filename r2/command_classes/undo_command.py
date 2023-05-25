import git

from .base_command import BaseCommand
import os
from r2 import prompts
from rich.prompt import Confirm
from prompt_toolkit.completion import Completion


class UndoCommand(BaseCommand):
    def __init__(self, io, coder):
        super().__init__(io, coder)
        self.__doc__ = 'Will undo the last git commit if it was performed by r2'

    def run(self, args):
        result = self.undo_command(prompts)
        if result == prompts.undo_command_reply:
            last_commit = self.coder.repo.head.commit
            self.io.tool(
                f"{last_commit.message.strip()}\n"
                f"The above commit {self.coder.last_r2_commit_hash} "
                "was reset and removed from git.\n"
            )

    def undo_command(self, prompts):
        if not self.coder.repo:
            self.io.tool_error("No git repository found.")
            return

        if self.coder.repo.is_dirty():
            self.io.tool_error(
                "The repository has uncommitted changes. Please commit or stash them before undoing.")
            return

        local_head = self.coder.repo.git.rev_parse("HEAD")
        has_origin = any(
            remote.name == "origin" for remote in self.coder.repo.remotes)

        if has_origin:
            current_branch = self.coder.repo.active_branch.name
            try:
                remote_head = self.coder.repo.git.rev_parse(
                    f"origin/{current_branch}")
            except git.exc.GitCommandError:
                self.io.tool_error(
                    f"Error: Unable to get the remote 'origin/{current_branch}'.")
                return

            if local_head == remote_head:
                self.io.tool_error(
                    "The last commit has already been pushed to the origin. Undoing is not possible.")
                return

        last_commit = self.coder.repo.head.commit
        if (
            not last_commit.message.startswith("r2:")
            or last_commit.hexsha[:7] != self.coder.last_r2_commit_hash
        ):
            self.io.tool_error(
                "The last commit was not made by r2 in this chat session.")
            return

        self.coder.repo.git.reset("--hard", "HEAD~1")
        return prompts.undo_command_reply
