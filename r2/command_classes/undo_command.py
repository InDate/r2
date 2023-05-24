import git

from .base_command import BaseCommand
import os
from r2 import prompts
from rich.prompt import Confirm
from prompt_toolkit.completion import Completion


class UndoCommand(BaseCommand):
    def __init__(self, io, coder):
        super().__init__(io, coder)

    def run(self, args):
        "Undo the last git commit if it was done by r2"
        result = self.undo_command(prompts)
        if result.startswith("Error"):
            self.io.tool_error(result)
        elif result == prompts.undo_command_reply:
            last_commit = self.coder.repo.head.commit
            self.io.tool(
                f"{last_commit.message.strip()}\n"
                f"The above commit {self.coder.last_r2_commit_hash} "
                "was reset and removed from git.\n"
            )
            return result
        else:
            self.io.tool(result)

    def undo_command(self, prompts):
        if not self.coder.repo:
            return "No git repository found."

        if self.coder.repo.is_dirty():
            return "The repository has uncommitted changes. Please commit or stash them before undoing."

        local_head = self.coder.repo.git.rev_parse("HEAD")
        has_origin = any(remote.name == "origin" for remote in self.coder.repo.remotes)

        if has_origin:
            current_branch = self.coder.repo.active_branch.name
            try:
                remote_head = self.coder.repo.git.rev_parse(f"origin/{current_branch}")
            except git.exc.GitCommandError:
                return f"Error: Unable to get the remote 'origin/{current_branch}'."

            if local_head == remote_head:
                return "The last commit has already been pushed to the origin. Undoing is not possible."

        last_commit = self.coder.repo.head.commit
        if (
            not last_commit.message.startswith("r2:")
            or last_commit.hexsha[:7] != self.coder.last_r2_commit_hash
        ):
            return "The last commit was not made by r2 in this chat session."

        self.coder.repo.git.reset("--hard", "HEAD~1")
        return prompts.undo_command_reply
