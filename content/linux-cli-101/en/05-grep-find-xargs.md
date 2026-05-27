---
title: "Linux CLI 101 (5/10): grep, find, xargs — The Search Trio"
series: linux-cli-101
episode: 5
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Linux
- grep
- find
- xargs
- Search
- CLI
last_reviewed: '2026-05-15'
seo_description: grep is a detective that finds text inside file contents, and find
  is a search party that locates files by name and attributes.
---

# Linux CLI 101 (5/10): grep, find, xargs — The Search Trio

Once a project stops fitting in your head, search becomes a workflow, not a convenience. You need to answer questions like "Where is this called?", "Which logs changed today?", and "Which matching files should I delete?" without opening everything one by one.

This is the 5th post in the Linux CLI 101 series.


![Linux CLI 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/05/05-01-mental-model.en.png)
*Linux CLI 101 chapter 5 flow overview*

## Questions to Keep in Mind

- Searching for strings inside files with `grep`?
- Finding files by name, size, and modification time with `find`?
- Passing search results as arguments to other commands with `xargs`?

## Why it matters

As projects grow, file counts climb into the hundreds. "Where is this function called?", "Which files were modified yesterday?", "Show me only the log lines containing ERROR" — `grep` and `find` answer all of these questions.

> A "database connection timeout" error hits your production server. There are 30 log files, each tens of thousands of lines long. You need to find which file and which line.

Instead of opening files one by one in an editor, `grep -rn "connection timeout" /var/log/app/` returns every result in under 1 second.

## Mental Model

> `grep` is a specialist librarian who searches book contents, `find` is a search party that locates books by title or size on the shelves, and `xargs` is the courier who hands the found books to someone else.

```text
grep: "Find pages containing this word"     -> content search
find: "Find the red 200-page book"          -> file search
xargs: "Take the found books to the copier" -> results -> command
```

## Core Concepts

| Command | Search target | Key options | Example |
|---|---|---|---|
| `grep` | File contents (text) | `-r`, `-n`, `-i`, `-l` | `grep -rn "TODO" src/` |
| `find` | Files/directories (metadata) | `-name`, `-type`, `-mtime`, `-size` | `find . -name "*.py"` |
| `xargs` | Converts stdin to arguments | `-I {}`, `-P` | `find . -name "*.log" \| xargs rm` |

## Before / After

**Before (manual search)**

```text
1. Open files one by one in an editor
2. Ctrl+F to search
3. Open next file
4. Repeat for 30 files -> 20 minutes
```

**After (one grep command)**

```bash
grep -rn "connection timeout" /var/log/app/
# /var/log/app/web.log:1523: 2026-05-04 ERROR database connection timeout
# /var/log/app/worker.log:89: 2026-05-04 ERROR database connection timeout
# All locations found in 1 second
```

## Step-by-step practice

### Step 1. Set up practice environment

```bash
cd ~/practice/linux-cli
mkdir -p project/src project/tests project/docs
echo 'def hello():
    # TODO: add logging
    print("hello")' > project/src/app.py
echo 'def test_hello():
    # TODO: fix assertion
    assert hello() is None' > project/tests/test_app.py
echo '# Project README
TODO: write documentation' > project/docs/README.md
```

### Step 2. Search contents with grep

```bash
grep "TODO" project/src/app.py           # Single file
# TODO: add logging

grep -rn "TODO" project/                  # Recursive + line numbers
# project/src/app.py:2:    # TODO: add logging
# project/tests/test_app.py:2:    # TODO: fix assertion
# project/docs/README.md:2:TODO: write documentation

grep -ri "todo" project/                  # Case insensitive
grep -rl "TODO" project/                  # File paths only
# project/src/app.py
# project/tests/test_app.py
# project/docs/README.md
```

### Step 3. Find files with find

```bash
find project/ -name "*.py"               # Find by name
# project/src/app.py
# project/tests/test_app.py

find project/ -type d                     # Directories only
find project/ -name "*.py" -newer project/docs/README.md   # Newer than a specific file
find /tmp -size +1M -mtime -7            # Over 1MB, modified within 7 days
```

### Step 4. Pass results to commands with xargs

```bash
find project/ -name "*.py" | xargs wc -l
#  3 project/src/app.py
#  3 project/tests/test_app.py
#  6 total

grep -rl "TODO" project/ | xargs -I {} echo "Fix needed: {}"
# Fix needed: project/src/app.py
# Fix needed: project/tests/test_app.py
# Fix needed: project/docs/README.md
```

### Step 5. Real-world combinations

```bash
# Find "print" calls in all Python files
find project/ -name "*.py" | xargs grep -n "print"
# project/src/app.py:3:    print("hello")

# Delete log files older than 30 days
find /tmp -name "*.log" -mtime +30 -print | xargs rm -v
```

## What to notice in this code

- The `-r` in `grep -r` stands for recursive — it searches subdirectories
- `grep -l` outputs file paths instead of matching lines, making it useful for pipelines
- The `-name` pattern in `find` must be quoted so the Shell does not expand the wildcard first
- `xargs -I {}` substitutes `{}` with each found item

## Common mistakes

### Mistake 1. Forgetting quotes on find patterns

```bash
find . -name *.py          # Shell expands *.py first -> unexpected results
find . -name "*.py"        # Correct: find processes the pattern directly
```

### Mistake 2. Using regex in grep without realizing it

In `grep "error.log"`, the `.` means "any character". It matches `errorXlog` as well as `error.log`. For a literal match, use `grep -F "error.log"` or `grep "error\.log"`.

### Mistake 3. Passing filenames with spaces through xargs

```bash
find . -name "*.txt" | xargs rm          # "My File.txt" splits into "My" and "File.txt"
find . -name "*.txt" -print0 | xargs -0 rm  # Null delimiter handles spaces safely
```

### Mistake 4. Processing find results with a for loop

```bash
# Slow and unsafe
for f in $(find . -name "*.log"); do rm "$f"; done

# Fast and safe
find . -name "*.log" -exec rm {} \;
# or
find . -name "*.log" -print0 | xargs -0 rm
```

### Mistake 5. Running grep on binary files

Running grep on images or executables produces garbled output. Restrict file types with `grep --include="*.py" -r "pattern" .`.

## Practical applications

- **Code search**: `grep -rn "deprecated" src/` finds deprecated API calls
- **Log analysis**: `grep -c "ERROR" app.log` counts error occurrences
- **Disk cleanup**: `find /tmp -mtime +30 -delete` removes old temporary files
- **Build cleanup**: `find . -name "__pycache__" -type d | xargs rm -rf`
- **Code review prep**: `find . -name "*.py" -newer last-review.txt` finds files changed since the last review

## How practitioners think about this

`grep` and `find` are the most frequently used commands in CLI workflows. The "search entire project" feature in your IDE is doing `grep -r` internally, and the "file explorer" is doing `find`. Using them directly in the CLI gives you more flexible options and lets you automate follow-up tasks through pipelines.

In practice, many teams use `ripgrep (rg)` which is faster than `grep`, and `fd` which is faster than `find`. But learning the standard commands first is necessary to appreciate the alternatives, and the standard commands have one undeniable advantage — they are installed on every server.

## When it breaks, check these first

- If you get no matches at all, shrink the scope first. Run `grep -n "TODO" one-file.txt` before going recursive so you can tell whether the pattern is wrong or the path is wrong.
- If `find` behaves strangely, check your quoting. `find . -name *.py` lets the shell expand `*.py` too early; `find . -name "*.py"` keeps the pattern where it belongs.
- If filenames with spaces break downstream commands, switch to `-print0` and `xargs -0` before doing anything destructive. This matters most when the next step is `rm`, `mv`, or `chmod`.
- If grep output is noisy or slow, limit the target set with options like `--include="*.py"` or `--exclude-dir=.git`. In real codebases, controlling scope is usually the first optimization.

## Checklist

- [ ] You can search for strings across a project with `grep -rn`
- [ ] You can find files by condition with `find -name -type -mtime`
- [ ] You can pass search results to other commands with `xargs`
- [ ] You can safely handle filenames with spaces using `-print0` and `-0`
- [ ] You can explain the `-i`, `-l`, `-c`, `-F` options of `grep`

## Exercises

1. Find all files with the `.py` extension under your home directory.
2. Run `grep -rn "import" project/` and then check the per-file import count with `grep -rc`.
3. Combine `find` and `grep` to find files modified within 7 days that contain `TODO`.

## Summary and next

- `grep` searches file contents for strings, with `-r` for recursive and `-n` for line numbers.
- `find` locates files by name, type, size, modification time, and other metadata.
- `xargs` converts standard input into command arguments, with `-0` to prevent whitespace issues.
- Combining the three commands is a core CLI pattern for automating manual tasks.
- Learn the standard commands first, then move on to alternatives like `ripgrep` and `fd`.

The next post covers **pipes and redirection** — connecting commands and redirecting input/output.

## Answering the Opening Questions

- **Searching for strings inside files with `grep`?**
  - The article treats grep, find, xargs — The Search Trio as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Finding files by name, size, and modification time with `find`?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Passing search results as arguments to other commands with `xargs`?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Linux CLI 101 (1/10): What Is the CLI and Shell?](./01-what-is-cli-and-shell.md)
- [Linux CLI 101 (2/10): Files and Directories](./02-files-and-directories.md)
- [Linux CLI 101 (3/10): Permissions and Ownership](./03-permissions-and-ownership.md)
- [Linux CLI 101 (4/10): cat, less, head, tail — Viewing File Contents](./04-viewing-files.md)
- **grep, find, xargs — The Search Trio (current)**
- Pipes and Redirection (upcoming)
- Process Management (upcoming)
- Environment Variables and PATH (upcoming)
- Shell Script Basics (upcoming)
- SSH and Remote Access (upcoming)

<!-- toc:end -->

## References

- [GNU grep Manual](https://www.gnu.org/software/grep/manual/)
- [GNU find Manual](https://www.gnu.org/software/findutils/manual/html_node/find_html/)
- [The Missing Semester - Data Wrangling](https://missing.csail.mit.edu/2020/data-wrangling/)
- [ripgrep - a faster grep alternative](https://github.com/BurntSushi/ripgrep)

Tags: Linux, grep, find, xargs, Search, CLI
