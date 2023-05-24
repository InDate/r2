- Module Name: utils
- Purpose: Utility functions for the r2 project.

- Functions:
    - `try_dotdotdots(whole, part, replace)`: Tries to perform a perfect edit with the ... chunks.
    - `replace_most_similar_chunk(whole, part, replace)`: Replaces the most similar chunk in the whole text with the given replace text.
    - `quoted_file(fname, display_fname)`: Returns a quoted file content with the given display file name.
    - `strip_quoted_wrapping(res, fname=None)`: Removes the wrapping around the input string.
    - `do_replace(fname, before_text, after_text, dry_run=False)`: Replaces the content of a file with the given before and after text.
    - `show_messages(messages, title)`: Displays messages with the given title.
    - `find_original_update_blocks(content)`: Finds the original and updated blocks in the given content.
    - `remove_unneeded_symbols(text: str) -> str`: Removes unneeded symbols from the given text.

- Example Usage:
```python
from r2.utils import do_replace

file_name = "example.txt"
before_text = "This is the original text."
after_text = "This is the updated text."
do_replace(file_name, before_text, after_text)
```
