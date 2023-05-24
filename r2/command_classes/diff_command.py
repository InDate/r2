from .base_command import BaseCommand


class DiffCommand(BaseCommand):
    def __init__(self, io, coder):
        super().__init__(io, coder)

    def run(self, args):
        "Display the diff of the last r2 commit"
        if not self.coder.repo:
            self.io.tool_error("No git repository found.")
            return

        if not self.coder.last_r2_commit_hash:
            self.io.tool_error("No previous r2 commit found.")
            return

        commits = f"{self.coder.last_r2_commit_hash}~1"
        diff = self.coder.get_diffs(commits, self.coder.last_r2_commit_hash)

        # don't use io.tool() because we don't want to log or further colorize
        print(diff)
