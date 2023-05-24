import sys
from r2 import prompts, utils
from r2.coder_classes.api_manager import TokensExceedsModel
from r2.coder_classes.git_manager import GitManager
from r2.commands import Commands

from rich.markdown import Markdown
from rich.live import Live


class CodeExecutor(GitManager):
    def __init__(self, io, api_manager, main_model="gpt-4"):
        super().__init__(io)
        self.io = io
        self.api_manager = api_manager
        self.commands = Commands(io, self)
        self.main_model = main_model
        self.pretty = True
        self.current_messages = []
        self.done_messages = []
        self.repo = None

    def send_to_llm(self, messages, model=None, temperature=0, silent=False):
        if not model:
            model = self.main_model

        # utils.reportTokens(str(messages), model)
        approx_tokens = self.api_manager.get_approx_prompt_tokens(messages, model)
        self.io.tool("Prompt Tokens: %s" % approx_tokens)

        self.resp = ""
        interrupted = False

        try:
            while True:
                completion = self.api_manager.create_chat_completion(
                    model=model,
                    messages=messages,
                    temperature=temperature
                )
                break
            self.show_send_output(completion, silent)
        except KeyboardInterrupt:
            interrupted = True
        except TokensExceedsModel as e:
            self.io.tool_error(f"Commit generation failed, file(s) too big. {e}")

        if not silent:
            self.io.ai_output(self.resp)

        return self.resp, interrupted

    def show_send_output(self, completion, silent):
        live = self.get_live(silent)
        try:
            if live:
                live.start()

            for chunk in completion:
                self.api_manager.update_completion_tokens(1)
                self.handle_chunk(chunk, silent, live)
        finally:
            if live:
                live.stop()
            self.io.tool(self.api_manager.get_total_cost())

    def get_live(self, silent):
        if self.pretty and not silent:
            return Live(vertical_overflow="scroll")
        return None

    def handle_chunk(self, chunk, silent, live):
        if chunk.choices[0].finish_reason not in (None, "stop"):
            assert False, "Exceeded context window!"

        try:
            text = chunk.choices[0].delta.content
            self.resp += text
        except AttributeError:
            return
        except Exception as err:
            self.io.tool_error("An exception occured with OpenAI: %s" % err)

        if not silent:
            self.output_text(text, live)

    def output_text(self, text, live):
        if self.pretty:
            md = Markdown(self.resp, style="blue", code_theme="default")
            live.update(md)
        else:
            sys.stdout.write(text)
            sys.stdout.flush()

    def get_message(self, role, content):
        return dict(role=role, content=content)

    def get_content_messages(self, user_input):
        """Prepare messages for sending to the AI model."""
        self.current_messages += [self.get_message("user", user_input)]

        messages = [
            self.get_message("system", prompts.main_system),
            self.get_message("system", prompts.system_reminder)
        ]

        # TODO: Not sure what done_messages is for.
        messages += self.done_messages
        messages += self.get_files_messages()
        messages += self.current_messages

        return messages

    def handle_interruption(self, content):
        """Handle KeyboardInterrupt during AI response"""
        self.io.tool_error("\n\n^C KeyboardInterrupt")
        content += "\n^C KeyboardInterrupt"
        return content

    def is_not_good_request(self, user_input):
        if len(user_input) < 10:
            self.io.tool_error("Not enough characters for meaningful response.")
            return True
        else:
            return False

    def send_new_user_message(self, user_input):
        if self.is_not_good_request(user_input):
            return

        messages = self.get_content_messages(user_input)
        content, interrupted = self.send_to_llm(messages)

        if interrupted:
            content = self.handle_interruption(content)

        self.current_messages += [dict(role="assistant", content=content)]
        self.io.tool()

        if interrupted:
            return

        edited, edit_error = self.apply_updates(content, user_input)
        if edit_error:
            return edit_error

        if edited and self.auto_commits:
            self.auto_commit()

        self.get_file_mentions(content)

    def get_file_mentions(self, content):
        files_mentions = self.check_for_file_mentions(content)

        if files_mentions and self.io.confirm_ask("Add these files to the chat?"):
            files_added = prompts.added_files.format(fnames=", ".join(files_mentions))
            message = [self.get_message("user", files_added)]
            self.io.queue.enqueue(('send_new_command_message', message, "New Files"), to_front=True)

            for files in files_mentions:
                self.io.queue.enqueue(('execute_command', '/add', files), to_front=True)

    def get_files_content(self, fnames=None):
        if not fnames:
            fnames = self.abs_fnames

        prompt = ""
        for fname in fnames:
            relative_fname = self.get_rel_fname(fname)
            prompt += utils.quoted_file(fname, relative_fname)
        return prompt

    def get_files_messages(self):
        files_content = prompts.files_content_prefix
        files_content += self.get_files_content()

        all_content = files_content

        if self.repo is not None:
            tracked_files = set(self.repo.git.ls_files().splitlines())
            files_listing = "\n".join(tracked_files)
            repo_content = prompts.repo_content_prefix
            repo_content += files_listing

            all_content = repo_content + "\n\n" + files_content

        files_messages = [
            dict(role="user", content=all_content),
            dict(role="assistant", content="Ok."),
            dict(
                role="system",
                content=prompts.files_content_suffix + prompts.system_reminder,
            ),
        ]

        return files_messages

    def send_new_command_message(self, messages, context, model='gpt-4', full_context=True):
        # sending message is newer. It will include everything.

        if full_context:
            all_messages = self.get_files_messages()
            all_messages += self.current_messages
            all_messages += messages
        else:
            all_messages = messages

        # TODO, this will over write all previous messages.
        self.current_messages = messages

        content, interrupted = self.send_to_llm(all_messages, model)

        if interrupted:
            content = self.handle_interruption(content)

        self.current_messages += [dict(role="assistant", content=content)]
        self.io.tool()

        if interrupted:
            return

        edited, edit_error = self.apply_updates(content, context)
        if edit_error:
            return edit_error

        if edited and self.auto_commits:
            self.auto_commit()

        self.get_file_mentions(content)

    def clear_chat(self):
        self.current_messages = []

    def run_loop(self):
        new_action = self.io.queue.dequeue()

        if new_action:
            return new_action

        user_input = self.io.get_input(self.abs_fnames, self.commands)

        self.num_control_c = 0

        if self.should_auto_commit(user_input):
            self.commit(ask=True, which="repo_files")

            # files changed, move cur messages back behind the files messages
            self.done_messages += self.current_messages
            self.done_messages += [
                dict(role="user", content=prompts.files_content_local_edits),
                dict(role="assistant", content="Ok."),
            ]
            self.clear_chat()

        if not user_input:
            return

        if user_input.startswith("/"):
            return self.commands.run(user_input)

    def process_action(self, action):
        kwargs = action[4] if len(action) > 4 else {}
        method = action[1] if len(action) > 1 else None
        args = action[2] if len(action) > 2 else None
        modifier = action[3] if len(action) > 3 else None

        if method.startswith("execute_command"):
            self.commands.execute_command(args, modifier, **kwargs)
        else:
            getattr(self, method)(args, modifier, **kwargs)

        return self.io.queue.dequeue()

    def run(self):
        self.done_messages = []
        self.clear_chat()

        self.num_control_c = 0

        while True:
            try:
                new_action = self.run_loop()
                while new_action:
                    new_action = self.process_action(new_action)

            except KeyboardInterrupt:
                self.num_control_c += 1
                if self.num_control_c >= 2:
                    break
                self.io.tool_error("^C again to quit")
            except EOFError:
                return
