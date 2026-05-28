---
title: "Python 101 (3/10): Strings and formatting"
series: python-101
episode: 3
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- strings
- f-string
- format-spec
- unicode
- string-methods
- bytes-and-str
last_reviewed: '2026-05-03'
seo_description: In Python 3, str is an immutable sequence of Unicode code points
  and bytes is an immutable sequence of bytes.
---

# Python 101 (3/10): Strings and formatting

In Python 3, `str` is an immutable sequence of Unicode code points, while `bytes` is an immutable sequence of raw bytes. Keeping those two layers separate makes encoding and formatting issues much easier to reason about.

This is the 3rd post in the Python 101 series.

This post is the 3rd article in the Python 101 series. This is the part of the series where text, bytes, and representation stop being interchangeable.


![Python 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-101/03/03-01-mental-model.en.png)
*Python 101 chapter 3 flow overview*

## Questions to Keep in Mind

- Why Python 3's `str` is a Unicode string and how it differs from `bytes`?
- When to reach for single, double, triple, raw, or byte literals?
- The core methods `split`, `join`, `strip`, `replace`, `find`, `startswith`?

## Why this matters

Strings are the input and output of almost every program. User input, a line read from a file, an HTTP response, a log line, a JSON field — all of them are `str`. Mishandle strings and you walk into recurring accidents:

- Reading a file with Korean characters explodes with `UnicodeDecodeError`.
- A growing log built by `+=` wastes memory and time on every iteration.
- Trusted-looking user input goes straight into a SQL query and opens an injection.
- Without format specs, code degenerates into `round` plus `str.zfill` patchwork.

Handling strings precisely prevents these mistakes upfront, and the code becomes shorter and clearer. It also leads naturally into the next chapter on collections — most values inside lists and dicts end up being strings.

## Mental model

> In Python 3, `str` is an immutable sequence of Unicode code points and `bytes` is an immutable sequence of bytes. Keep those two layers separate and encoding, formatting, and regex questions all collapse into the same model.
Python's `str` is a sequence of code points. It is abstracted at the level humans read; it only becomes `bytes` when it leaves memory for disk or the network.

Three rules make most of the confusion disappear.

1. **`str` is a sequence of Unicode code points.** It carries no encoding information.
2. **`bytes` is a sequence of integers in `0..255`.** Which encoding produced them is something the programmer must remember.
3. **Encode and decode only at the boundary with the outside world.** Inside the program, work in `str`.

`str` is also **immutable**. `s = "hi"; s[0] = "H"` raises `TypeError`. Every "mutating" method actually returns a brand new `str`.

## Core concepts

### 1) String literals

Python accepts several quote styles. They mean the same thing; you pick whichever lets you avoid escaping the quotes inside.

```text
>>> 'hello'
'hello'
>>> "she said \"hi\""
'she said "hi"'
>>> 'she said "hi"'        # easier: wrap in single quotes
'she said "hi"'
>>> """multi
... line
... strings work too"""
'multi\nline\nstrings work too'
```

Raw strings keep backslashes as-is. Use them for Windows paths and regex.

```text
>>> path = r"C:\Users\name\file.txt"
>>> print(path)
C:\Users\name\file.txt
```

`b"..."` is a byte literal. ASCII characters can appear directly; other byte values must be written with escape sequences such as `\xFF`.

```text
>>> b"hello"
b'hello'
>>> b"안녕"
  File "<stdin>", line 1
SyntaxError: bytes can only contain ASCII literal characters
```

### 2) The boundary between str and bytes

At the OS and protocol boundary the data is bytes. Many Python text APIs (such as `open(..., "r")` or `requests.Response.text`) already decode it to `str` for you. When you do work with raw bytes, assume UTF-8 and call `decode` to get a `str`.

```text
>>> data = "hi".encode("utf-8")
>>> data
b'hi'
>>> data.decode("utf-8")
'hi'
>>> "안녕".encode("utf-8").decode("ascii")
Traceback (most recent call last):
  ...
UnicodeDecodeError: 'ascii' codec can't decode byte 0xec in position 0: ordinal not in range(128)
```

Guess the encoding wrong and you hit `UnicodeDecodeError`. When unsure, try UTF-8 first; if it fails, ask the sender what encoding they actually used.

### 3) Core methods

Every `str` method returns a new `str`. The original is left untouched.

```text
>>> "  hello, world  ".strip()
'hello, world'
>>> "user@example.com".split("@")
['user', 'example.com']
>>> ", ".join(["a", "b", "c"])
'a, b, c'
>>> "Python".lower()
'python'
>>> "Python".replace("P", "J")
'Jython'
>>> "image.png".endswith(".png")
True
>>> "report.txt".startswith(("draft", "report"))    # tuple is allowed
True
>>> "find me here".find("me")
5
>>> "needle" in "haystack with needle"
True
```

`split` with no argument splits on runs of whitespace (spaces, tabs, newlines). When you need a deterministic result, pass an explicit separator.

### 4) Slicing and immutability

`str` is a sequence, so indexing and slicing work as expected.

```text
>>> s = "Python"
>>> s[0], s[-1]
('P', 'n')
>>> s[0:3]
'Pyt'
>>> s[::-1]
'nohtyP'
```

To "change" part of a string, build a new one.

```text
>>> s = "hello"
>>> s = "H" + s[1:]
>>> s
'Hello'
```

### 5) f-strings and format specs

f-strings (PEP 498) are the clearest default for inline formatting. Variables and expressions go directly into braces.

```text
>>> name = "yeongseon"
>>> count = 3
>>> f"{name} has {count} books"
'yeongseon has 3 books'
>>> f"{count * 2}"
'6'
```

After a colon comes the format spec — alignment, width, precision, base, dates — all in one line.

```text
>>> import math
>>> f"{math.pi:.2f}"           # two decimal places
'3.14'
>>> f"{42:>6}"                 # width 6, right-aligned
'    42'
>>> f"{42:0>6}"                # width 6, left-padded with zeros
'000042'
>>> f"{255:#x}"                # hex with the 0x prefix
'0xff'
>>> from datetime import date
>>> today = date(2026, 5, 3)
>>> f"{today:%Y-%m-%d}"
'2026-05-03'
```

`!r` is great for debugging — it applies `repr()` so quotes show up.

```text
>>> name = "ada"
>>> f"name={name!r}"
"name='ada'"
```

Since Python 3.8, adding `=` prints both the variable name and its value. Debugging gets noticeably easier.

```text
>>> count = 3
>>> f"{count=}"
'count=3'
```

### 6) str.format and % formatting

Two older styles you will still meet in legacy code. New code prefers f-strings, but you should be able to read these.

```text
>>> "{} has {} books".format("yeongseon", 3)
'yeongseon has 3 books'
>>> "%s has %d books" % ("yeongseon", 3)
'yeongseon has 3 books'
```

`format` accepts keyword arguments. That is useful when a template comes from outside. f-strings capture variables at the spot where they are written, so they are awkward as templates.

```text
>>> template = "{name} owes {amount}"
>>> template.format(name="ada", amount=12000)
'ada owes 12000'
```

### 7) A first look at regular expressions

The `re` module manipulates strings via patterns. A full tour deserves its own chapter, but pulling email addresses out of a sentence fits in one line.

```text
>>> import re
>>> text = "Contact ada@example.com or bob@example.org"
>>> re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
['ada@example.com', 'bob@example.org']
```

Use raw strings (`r"..."`) so backslashes do not have to be doubled.

## Before / after

The same task in the old style versus modern f-string style. f-strings show intent at a glance and reduce the chances of a wrong conversion.

```python
# Before: % formatting + manual zfill
name = "ada"
count = 3
price = 1234.5
line = "%s | %s | %s" % (name.ljust(10), str(count).zfill(3), "%.2f" % price)
print(line)
# 'ada        | 003 | 1234.50'

# After: f-string + format spec
line = f"{name:<10} | {count:0>3} | {price:.2f}"
print(line)
# 'ada        | 003 | 1234.50'
```

Another common comparison is concatenation. Replace repeated `+` with `join`.

```python
# Before: repeated + concatenation
parts = ["alpha", "beta", "gamma", "delta"]
out = ""
for p in parts:
    out = out + p + ", "
out = out.rstrip(", ")
print(out)

# After: a single join
print(", ".join(parts))
```

## Step-by-step practice

Build a function that takes a CSV-like line and prints a tidy aligned row. We will exercise f-strings, format specs, and a handful of methods.

1. **Parse the input.** Split on commas, then strip each field.

   ```python
   raw = "ada, 30, 1700000.5"
   name, age_str, salary_str = [field.strip() for field in raw.split(",")]
   ```

2. **Convert types.** Cast numeric fields explicitly. Never trust that user input is already a number.

   ```python
   age = int(age_str)
   salary = float(salary_str)
   ```

3. **Format.** Pad widths and add thousands separators.

   ```python
   line = f"{name:<10} | {age:>3}y | {salary:>14,.2f} KRW"
   print(line)
   # 'ada        |  30y |   1,700,000.50 KRW'
   ```

4. **Apply to many rows.**

   ```python
   rows = [
       "ada, 30, 1700000.5",
       "bob, 28, 2300000",
       "charlie, 41, 5400000.25",
   ]
   for raw in rows:
       name, age_str, salary_str = [f.strip() for f in raw.split(",")]
       age = int(age_str)
       salary = float(salary_str)
       print(f"{name:<10} | {age:>3}y | {salary:>14,.2f} KRW")
   ```

5. **Extend.** When a new requirement arrives — say the salary may use other currencies — pull the symbol into a variable and interpolate it inside the f-string. Do not splice strings together with `+`; let the f-string do the work.

## Common mistakes

1. **Calling `str` "a UTF-8 string."**
   `str` is a sequence of Unicode code points. UTF-8 is one of several encodings used when converting to `bytes`.

2. **Mixing `bytes` and `str`.**
   `b"a" + "b"` raises `TypeError`. Decode `bytes` from the outside world as soon as you can, work in `str` internally, and encode once at the boundary on the way out.

3. **Building a big string with repeated `+`.**
   Each step allocates a new string, so the cost grows with the number of pieces. Collect into a list and finish with `"".join(...)`.

4. **Inserting user input into SQL via f-string.**
   `f"SELECT * FROM users WHERE name = '{name}'"` is the start of a SQL injection. Use the DB API placeholders (`?` or `%s`) instead. The database series goes deeper.

5. **Confusing `format` and f-strings.**
   f-strings capture variables at the moment they are defined. When the template needs to be filled in later, use `template.format(...)` or `string.Template`.

6. **Not noticing `split()` versus `split(" ")`.**
   `split()` with no argument collapses runs of whitespace. `split(" ")` keeps empty strings between consecutive spaces. Argument-less `split()` is usually the safer default for messy input.

## In practice

- **Log messages.** `logger.info(f"user={user_id} action={action}")` produces lines that are easy to grep and parse. Note that `logger.info("user=%s", user_id)` lets logging skip formatting when the level is disabled, which can matter in hot paths.
- **File paths.** For Windows paths prefer `pathlib.Path("C:/Users/name") / "file.txt"` over raw strings; the OS picks the right separator.
- **Email and URL validation.** Regex alone never validates them perfectly. Filter for shape, then confirm via an out-of-band signal such as sending a confirmation email.
- **Tabular output.** When you keep aligning console output by hand, switch to `tabulate` or `rich.table`. Hand-counted widths are fragile.
- **Internationalization.** Do not bake user-facing strings into the code. Use `gettext` or an i18n library. Translation extraction tools struggle with bare f-strings.

## Checklist

- [ ] I can explain that `str` is a Unicode sequence, distinct from `bytes`
- [ ] I do not get confused about the direction of `decode` (in) versus `encode` (out)
- [ ] I use `split`, `join`, `strip`, `replace`, `find`, `startswith`/`endswith` deliberately
- [ ] I can write `:.2f`, `:>10`, `:%Y-%m-%d`, `!r`, `{var=}` from memory
- [ ] I know `str` is immutable and that every method returns a new string
- [ ] I collect into a list and `join` instead of repeated `+` for big strings
- [ ] I never splice user input into SQL with an f-string
- [ ] I have used `re.findall` with a raw string at least once

## Exercises

1. **Aligned table printer**
   Given a list like `[("ada", 30), ("bob", 28), ("charlie", 41)]`, write `print_table(rows)` that prints the name left-aligned to width 10 and the age right-aligned to width 3.
   - Success criterion: `print_table([("ada", 30)])` prints `'ada        |  30'`.

2. **CSV row parser**
   Write `parse_row(line: str)` that takes `"ada, 30, 1700000.5"` and returns `(name: str, age: int, salary: float)`. Strip whitespace; let `ValueError` propagate when a numeric field cannot parse.
   - Success criterion: `parse_row("ada, 30, 1700000.5")` returns `('ada', 30, 1700000.5)`.

3. **Email extractor**
   Write `extract_emails(text: str) -> list[str]` that returns every email address in the text. Use `re.findall` with a raw string.
   - Success criterion: `extract_emails("ada@example.com and bob@example.org")` returns `['ada@example.com', 'bob@example.org']`.

## Summary and next chapter

- Python 3's `str` is a sequence of Unicode code points; `bytes` is a sequence of integers in `0..255`.
- Encode and decode only at the boundary; inside the program, work exclusively in `str`.
- `str` is immutable; every method returns a new string.
- f-strings with format specs (`:.2f`, `:>10`, `:%Y-%m-%d`, `!r`, `{var=}`) cover almost every output need.
- For big strings, collect into a list and `join` once. Never splice user input into SQL via an f-string.

The next chapter compares the four core collections — list, tuple, set, dict — and explains when to reach for each one. Mutability, order, duplicates, and hashability fit on a single page.

## Answering the Opening Questions

- **Reading a file with Korean text fails with `UnicodeDecodeError`?**
  - The file's encoding isn't UTF-8 (e.g., a Windows file saved as CP949). Always pass `encoding="utf-8"` (or the actual encoding) to `open()`. For external files of uncertain origin, `errors="replace"` accepts partial corruption gracefully.
- **Repeating `+` concatenation in a loop wastes memory and time building a large log?**
  - Strings are immutable, so each `+` creates a new object—O(N²) cost for N fragments. Collect pieces in a list and `"".join(parts)` once, or write directly to a file handle for large outputs.
- **Trusting user input directly in SQL creates injection vulnerabilities?**
  - String formatting in queries lets payloads like `' OR 1=1 --` execute as SQL syntax. Always pass user input through the DB driver's parameter binding (`cursor.execute("... WHERE id=?", (uid,))`) to separate data from code.

<!-- toc:begin -->
## In this series

- [Python 101 (1/10): Why Python, and how to install and use venv](./01-why-python-and-install.md)
- [Python 101 (2/10): Variables, types, and operators](./02-variables-types-operators.md)
- **Strings and formatting (current)**
- list, tuple, set, dict (upcoming)
- Control flow: if, for, while, comprehension (upcoming)
- Functions and arguments: def, args, kwargs, default, lambda (upcoming)
- Modules and packages: import, __init__, __name__ (upcoming)
- File I/O and exception handling (upcoming)
- Classes and objects: bundling data with behavior (upcoming)
- Standard library tour: datetime, pathlib, json, collections, itertools (upcoming)

<!-- toc:end -->

## References

- [Python docs — Built-in Types](https://docs.python.org/3/library/stdtypes.html) — Canonical reference for `str`, `bytes`, immutability, and core text methods.
- [Unicode HOWTO](https://docs.python.org/3/howto/unicode.html) — Explains code points, encodings, and the `encode`/`decode` boundary model used throughout the chapter.
- [Python docs — `string`](https://docs.python.org/3/library/string.html) — Documents format string syntax and the format specification mini-language behind aligned output.
- [PEP 498 — Literal String Interpolation](https://peps.python.org/pep-0498/) — Defines f-strings, expression interpolation, and format specifier behavior.
- [Python docs — `re`](https://docs.python.org/3/library/re.html) — Relevant for the chapter’s raw-string and backslash guidance around regular expressions.
- [Python docs — Input and Output](https://docs.python.org/3/tutorial/inputoutput.html) — Adds official examples for `repr()`, `str()`, and text formatting in I/O contexts.

Tags: strings, f-string, format-spec, unicode, string-methods, bytes-and-str
