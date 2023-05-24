# built from aider and auto-gpt.

# Prompt based development. 
Built upon the code from of Aider[https://github.com/paul-gauthier/aider] / Auto-GPT[https://github.com/Significant-Gravitas/Auto-GPT] and GPT4, `r2` is for the new era of prompt-based developers. 

R2 can be prompted to modify or create new code, it can develop it's own test's, execute the tests and debug/repair mistakes as they arise. When the changes are testing successfully, `r2` will prompt you to commit to the repo, complete with message.

With the tool, you can ask for features, improvements, or bug fixes and `r2` will apply the suggested changes to source files.

Note: this version has been a self-referencing tool, used to develop itself. My intention is to add ReAct based logic, method by method editing and a jupyter style GUI. Sending an entire file to GPT-4 is expensive and quickly limited by context size. 

To use r2, you will require your own GPT-4 API key. 
'r2' will prompt to execute .py files through unit tests and commands. This could result in bad things happening to the operating system and it's files if not carefully monitored. 

Happy to chat, available on - Discord[https://discord.gg/YaqMe653] or Twitter.

## Features

* Chat with GPT-4 about your code by launching `r2` from the command line with set of source files to discuss and edit together.
* Request new features, changes, improvements, or bug fixes to your code. Ask for new test cases, updated documentation or code refactors.
* `r2` will apply the edits suggested by GPT-4 directly to your source files.
* `r2` will automatically commit each changeset to your local git repo with a descriptive commit message. These frequent, automatic commits provide a safety net. It's easy to undo `r2` changes or use standard git workflows to manage longer sequences of changes.
* `r2` can review multiple source files at once and make coordinated code changes across all of them in a single changeset/commit.
* `r2` knows about all the files in your repo, so it can ask for permission to review whichever files seem relevant to your requests.
* You can also edit the files in your editor while chatting with `r2`.
  * `r2` will notice if you edit the files outside the chat.
  * It will help you commit these out-of-band changes, if you'd like.
  * It will bring the updated file contents into the chat.
  * You can bounce back and forth between the `r2` chat and your editor, to fluidly collaborate.
* Live, colorized, human friendly output.
* Readline style chat input history, with autocompletion of code tokens found in the source files being discussed (via `prompt_toolkit` and `pygments` lexers)

## Installation

1. Install the package: `pip install git+https://github.com/InDate/r2.git`
2. Set up your OpenAI API key as an environment variable `OPENAI_API_KEY` or by including it in a `.env` file.

## Usage

Run the `r2` tool by executing the following command:

```
r2
```

You can launch `r2` anywhere in a git repo without naming files on the command line.
It will discover all the files in the repo.
You can then add and remove individual files in the chat session with the `/add` and `/drop` chat commands described below.

You can also use additional command-line options to customize the behavior of the tool. The following options are available, along with their corresponding environment variable overrides:

- `--input-history-file INPUT_HISTORY_FILE`: Specify the chat input history file (default: .r2.input.history). Override the default with the environment variable `r2_INPUT_HISTORY_FILE`.
- `--chat-history-file CHAT_HISTORY_FILE`: Specify the chat history file (default: .r2.chat.history.md). Override the default with the environment variable `r2_CHAT_HISTORY_FILE`.
- `--no-pretty`: Disable pretty, colorized output. Override the default with the environment variable `r2_PRETTY` (default: 1 for enabled, 0 for disabled).
- `--no-auto-commits`: Disable auto commit of changes. Override the default with the environment variable `r2_AUTO_COMMITS` (default: 1 for enabled, 0 for disabled).
- `--show-diffs`: Show diffs when committing changes (default: False). Override the default with the environment variable `r2_SHOW_DIFFS` (default: 0 for False, 1 for True).
- `--yes`: Always say yes to every confirmation (default: False).

For more information, run `r2 --help`.

## Chat commands

`r2` supports the following commands from within the chat:

* `/add <file>`: Add matching files to the chat session.
* `/drop <file>`: Remove matching files from the chat session.
* `/ls`: List all known files and those included in the chat session.
* `/commit [message]`: Commit outstanding changes to the chat session files. Use this to commit edits you made outside the chat, with your editor or git commands. r2 will provide a commit message if you don't.
* `/undo`: Undo the last git commit if it was done by r2.
* `/diff`: Display the diff of the last r2 commit.
* `/debug`: Display the diff of the last r2 commit.
* `/unit_test`: Display the diff of the last r2 commit.
* `/spec_file`: Display the diff of the last r2 commit.
* `/test_connection`: Display the diff of the last r2 commit.
* `/execute_file`: Display the diff of the last r2 commit.


To use a command, simply type it in the chat input followed by any required arguments.

## Tips

* Large changes are best performed as a sequence of bite sized steps. Same as if you were undertaking them by yourself.
* Use Control-C to safely interrupt `r2` if it isn't providing a useful response. The partial response remains in the conversation, so you can refer to it when you reply with more information or direction.
* Enter a multiline chat message by entering `{` alone on the first line. End the multiline message with `}` alone on the last line.
* If your code is throwing an error, paste the error message and stack trace into `r2` as a multiline `{}` message and let `r2` fix the bug.
* GPT-4 knows about a lot of standard tools and libraries, but may get some of the fine details wrong about APIs and function arguments. You can paste doc snippets into the chat with the  multiline `{}` syntax.
* `r2` will notice if you launch it on a git repo with uncommitted changes and offer to commit them before proceeding.
* `r2` can only see the content of the files you specify, but it also gets a list of all the files in the repo. It may ask to see additional files if it feels that's needed for your requests.

## Limitations

You probably need GPT-4 api access to use `r2`.
You can invoke it with `r2 -3` to try using gpt-3.5-turbo, but it will almost certainly fail to function correctly.
GPT-3.5 is unable to consistently follow directions to generate concise code edits in a stable, parsable format.

You can only use `r2` to edit code that fits in the GPT context window.
For GPT-4 that is 8k tokens.
It helps to be selective about how many source files you discuss with `r2` at one time.
You might consider refactoring your code into more, smaller files (which is usually a good idea anyway).
You can use `r2` to help perform such refactorings, if you start before the files get too large.

If you have access to gpt-4-32k, I would be curious to hear how it works with r2.
