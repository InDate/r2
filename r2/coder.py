#!/usr/bin/env python
from rich.console import Console
import os
import openai
from r2.coder_classes.code_executor import CodeExecutor

from dotenv import load_dotenv


class Coder(CodeExecutor):
    def __init__(self, main_model, fnames, pretty, show_diffs, auto_commits, io, api_manager, dry_run):
        super().__init__(io, api_manager)
        self.io = io
        self.test_dir = None
        self.last_asked_for_commit_time = float()
        self.auto_commits = auto_commits
        self.dry_run = dry_run

        if pretty:
            self.console = Console()
        else:
            self.console = Console(force_terminal=True, no_color=True)

        self.main_model = main_model

        if main_model == "gpt-3.5-turbo":
            self.io.tool_error(
                f"r2 doesn't work well with {main_model}, use gpt-4 for best results."
            )

        self.set_repo(fnames)

        if not self.repo:
            self.io.tool_error("No suitable git repo, will not automatically commit edits.")
            self.find_common_root()

        self.pretty = pretty
        self.show_diffs = show_diffs
        self.find_test_directory()
