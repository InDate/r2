import re
import math

from difflib import SequenceMatcher
from pathlib import Path

# from r2.dump import dump


def try_dotdotdots(whole, part, replace):
    """
    See if the edit block has ... lines.
    If not, return none.

    If yes, try and do a perfect edit with the ... chunks.
    If there's a mismatch or otherwise imperfect edit, raise ValueError.

    If perfect edit succeeds, return the updated whole.
    """

    dots_re = re.compile(r"(^\s*\.\.\.\n)", re.MULTILINE | re.DOTALL)

    part_pieces = re.split(dots_re, part)
    replace_pieces = re.split(dots_re, replace)

    if len(part_pieces) != len(replace_pieces):
        raise ValueError("Unpaired ... in edit block")

    if len(part_pieces) == 1:
        # no dots in this edit block, just return None
        return

    # Compare odd strings in part_pieces and replace_pieces
    all_dots_match = all(part_pieces[i] == replace_pieces[i]
                         for i in range(1, len(part_pieces), 2))

    if not all_dots_match:
        raise ValueError("Unmatched ... in edit block")

    part_pieces = [part_pieces[i] for i in range(0, len(part_pieces), 2)]
    replace_pieces = [replace_pieces[i]
                      for i in range(0, len(replace_pieces), 2)]

    pairs = zip(part_pieces, replace_pieces)
    for part, replace in pairs:
        if not part and not replace:
            continue

        if not part and replace:
            if not whole.endswith("\n"):
                whole += "\n"
            whole += replace
            continue

        if part not in whole:
            raise ValueError(
                "No perfect matching chunk in edit block with ...")

        whole = whole.replace(part, replace)

    return whole


def replace_most_similar_chunk(whole, part, replace):
    if part in whole:
        return whole.replace(part, replace)

    try:
        res = try_dotdotdots(whole, part, replace)
    except ValueError:
        return

    if res:
        return res

    similarity_thresh = 0.8

    max_similarity = 0
    most_similar_chunk_start = -1
    most_similar_chunk_end = -1

    whole_lines = whole.splitlines()
    part_lines = part.splitlines()

    scale = 0.1
    min_len = math.floor(len(part_lines) * (1 - scale))
    max_len = math.ceil(len(part_lines) * (1 + scale))

    for length in range(min_len, max_len):
        for i in range(len(whole_lines) - length + 1):
            chunk = whole_lines[i: i + length]
            chunk = "\n".join(chunk)

            similarity = SequenceMatcher(None, chunk, part).ratio()

            if similarity > max_similarity and similarity:
                max_similarity = similarity
                most_similar_chunk_start = i
                most_similar_chunk_end = i + length

    if max_similarity < similarity_thresh:
        return

    replace_lines = replace.splitlines()
    modified_whole = (
        whole_lines[:most_similar_chunk_start]
        + replace_lines
        + whole_lines[most_similar_chunk_end:]
    )
    modified_whole = "\n".join(modified_whole)

    if whole.endswith("\n"):
        modified_whole += "\n"

    return modified_whole


def quoted_file(fname, display_fname):
    prompt = "\n"
    prompt += display_fname
    prompt += "\n```\n"
    prompt += Path(fname).read_text()
    prompt += "\n```\n"
    return prompt


def strip_quoted_wrapping(res, fname=None):
    """
    Given an input string which may have extra "wrapping" around it, remove the wrapping.
    For example:

    filename.ext
    ```
    We just want this content
    Not the filename and triple quotes
    ```
    """
    if not res:
        return res

    res = res.splitlines()

    if fname and res[0].strip().endswith(Path(fname).name):
        res = res[1:]

    if res[0].startswith("```") and res[-1].startswith("```"):
        res = res[1:-1]

    res = "\n".join(res)
    if res and res[-1] != "\n":
        res += "\n"

    return res


def do_replace(fname, before_text, after_text, dry_run=False):
    before_text = strip_quoted_wrapping(before_text, fname)
    after_text = strip_quoted_wrapping(after_text, fname)
    fname = Path(fname)

    # does it want to make a new file?
    if not fname.exists() and not before_text.strip():
        fname.touch()

    content = fname.read_text()

    if not before_text.strip():
        if content:
            new_content = content + after_text
        else:
            # first populating an empty file
            new_content = after_text
    else:
        new_content = replace_most_similar_chunk(
            content, before_text, after_text)
        if not new_content:
            return

    if not dry_run:
        fname.write_text(new_content)

    return True


def show_messages(messages, title):
    print(title.upper(), "*" * 50)

    for msg in messages:
        print()
        print("-" * 50)
        role = msg["role"].upper()
        content = msg["content"].splitlines()
        for line in content:
            print(role, line)


ORIGINAL = "<<<<<<< ORIGINAL"
DIVIDER = "======="
UPDATED = ">>>>>>> UPDATED"

separators = "|".join([ORIGINAL, DIVIDER, UPDATED])

split_re = re.compile(
    r"^((?:" + separators + r")[ ]*\n)", re.MULTILINE | re.DOTALL)


def find_original_update_blocks(content):
    # make sure we end with a newline, otherwise the regex will miss <<UPD on the last line
    if not content.endswith("\n"):
        content = content + "\n"

    pieces = re.split(split_re, content)

    pieces.reverse()
    processed = []

    try:
        while pieces:
            cur = pieces.pop()

            if cur in (DIVIDER, UPDATED):
                processed.append(cur)
                raise ValueError(f"Unexpected {cur}")

            if cur.strip() != ORIGINAL:
                processed.append(cur)
                continue

            processed.append(cur)  # original_marker

            filename = processed[-2].splitlines()[-1].strip()
            if not len(filename) or "`" in filename:
                filename = processed[-2].splitlines()[-2].strip()
                if not len(filename) or "`" in filename:
                    raise ValueError(
                        f"Bad/missing filename. It should go right above {ORIGINAL}")

            original_text = pieces.pop()
            processed.append(original_text)

            divider_marker = pieces.pop()
            processed.append(divider_marker)
            if divider_marker.strip() != DIVIDER:
                raise ValueError(f"Expected {DIVIDER}")

            updated_text = pieces.pop()

            updated_marker = pieces.pop()
            if updated_marker.strip() != UPDATED:
                raise ValueError(f"Expected {UPDATED}")

            yield filename, original_text, updated_text
    except ValueError as e:
        processed = "".join(processed)
        err = e.args[0]
        raise ValueError(f"{processed}\n^^^ {err}")
    except IndexError:
        processed = "".join(processed)
        raise ValueError(
            f"{processed}\n^^^ Incomplete ORIGINAL/UPDATED block.")
    except Exception:
        processed = "".join(processed)
        raise ValueError(
            f"{processed}\n^^^ Error parsing ORIGINAL/UPDATED block.")


if __name__ == "__main__":
    edit = """
Here's the change:

```text
foo.txt
<<<<<<< ORIGINAL
Two
=======
Tooooo
>>>>>>> UPDATED
```

Hope you like it!
"""
    print(list(find_original_update_blocks(edit)))


def remove_unneeded_symbols(text: str) -> str:
    """Remove unneeded symbols from the given text."""
    text = text.replace('\\n', '')
    message = re.sub(r'[^a-zA-Z0-9 \/:_\.]+', ' ', text)
    cleaned_text = re.sub(r'([^\w\s])\1+', r'\1', message)
    return cleaned_text


def extract_last_running_cost(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    pattern = r'> Total running cost: \$([\d.]+)'
    matches = re.findall(pattern, content)
    if matches:
        return float(matches[-1])
    return None
