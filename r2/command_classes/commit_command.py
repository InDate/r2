from .base_command import BaseCommand


class CommitCommand(BaseCommand):
    def __init__(self, io, coder):
        super().__init__(io, coder)

    def run(self, args):
        result = self.commit_command(args)

        if result:
            self.io.tool_error(result)
        else:
            self.io.tool("Commit successful.")

    def commit_command(self, args):
        "Commit edits to chat session files made outside the chat (commit message optional)"

        if not self.coder.repo:
            self.io.tool_error("No git repository found.")
            return

        if not self.coder.repo.is_dirty():
            self.io.tool_error("No more changes to commit.")
            return

        self.coder.auto_commit()
