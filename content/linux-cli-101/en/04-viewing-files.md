---
title: "cat, less, head, tail — Viewing File Contents"
series: linux-cli-101
episode: 4
language: en
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Linux
- CLI
- cat
- less
- tail
- Log
last_reviewed: '2026-05-04'
seo_description: cat dumps a file all at once like pouring a bucket, and less lets
  you flip through it one page at a time like reading a book.
---

# cat, less, head, tail — Viewing File Contents

> Linux CLI 101 series (4/10)

---

<!-- a-grade-intro:begin -->

## Key Questions

- Why do we need multiple commands just to view file contents?
- What happens if you run `cat` on a 1GB log file?
- When would you use `tail -f`?
- How do you view only the first 10 lines or the last 20 lines of a file?

> cat dumps a file all at once like pouring a bucket, and less lets you flip through it one page at a time like reading a book.

<!-- a-grade-intro:end -->

## What you will learn

- Using `cat` to quickly view short files
- Using `less` to browse long files page by page
- Using `head` and `tail` to slice the beginning or end of a file
- Using `tail -f` to monitor logs in real time

## Why it matters

Viewing file contents comes up constantly during development. You check config values, hunt for errors in logs, and inspect CSV headers. Opening an editor is slow for large files, and edit mode risks accidental changes.

> You need to check the last error in a 1GB log file on a server. Opening it in vim consumes all memory, and running cat scrolls the terminal for minutes.

Using the right read-only command for the right job solves this cleanly.

## Mental Model

> `cat` is pouring a bucket all at once, `less` is flipping through a book one page at a time. `head` is tearing out the first few pages, and `tail` is reading only the last few pages.

```text
Small file     --> cat (print at once)
Large file     --> less (page navigation)
Need beginning --> head -n 20
Need end       --> tail -n 20
Real-time      --> tail -f
```

## Core Concepts

| Command | Purpose | Key trait |
|---|---|---|
| `cat` | Print entire file | Best for short files, also used as pipe input |
| `less` | Page-by-page navigation | Searchable, navigable, memory efficient |
| `head` | Print beginning of file | Default 10 lines, adjust with `-n` |
| `tail` | Print end of file | Default 10 lines, `-f` for real-time tracking |
| `wc` | Count lines/words/bytes | `wc -l` for line count only |

## Before / After

**Before (opening every file in an editor)**

```text
vim /var/log/app/app.log    # 1GB file -> 30 seconds to load
# Accidentally press i -> edit mode -> risk of changing contents
# :q! to exit
```

**After (read-only commands)**

```bash
tail -n 50 /var/log/app/app.log    # Last 50 lines printed instantly
tail -f /var/log/app/app.log       # New log lines appear in real time
```

## Step-by-step practice

### Step 1. Create practice files

```bash
cd ~/practice/linux-cli
seq 1 100 > numbers.txt          # Numbers 1 through 100
echo -e "name,age\nAlice,30\nBob,25\nCharlie,35" > data.csv
cat /etc/passwd > users.txt      # Copy system user list
```

### Step 2. View short files with cat

```bash
cat data.csv
# name,age
# Alice,30
# Bob,25
# Charlie,35

cat -n data.csv          # With line numbers
# 1  name,age
# 2  Alice,30
# 3  Bob,25
# 4  Charlie,35
```

### Step 3. head and tail

```bash
head numbers.txt          # First 10 lines
head -n 5 numbers.txt     # First 5 lines

tail numbers.txt          # Last 10 lines
tail -n 3 numbers.txt     # Last 3 lines
# 98
# 99
# 100
```

### Step 4. Browse long files with less

```bash
less users.txt
# Controls:
# Space or f: next page
# b: previous page
# /keyword: search (n for next result)
# g: go to beginning
# G: go to end
# q: quit
```

### Step 5. Real-time log monitoring with tail -f

```bash
# Terminal 1: monitor logs in real time
tail -f /tmp/test.log &

# Add log entries
echo "$(date) INFO: app started" >> /tmp/test.log
echo "$(date) ERROR: connection failed" >> /tmp/test.log

# tail -f prints new lines immediately
# Ctrl+C to stop
kill %1 2>/dev/null
```

## What to notice in this code

- In `seq 1 100 > numbers.txt`, `>` is redirection that sends output to a file (covered in detail in Ep6)
- `cat -n` is useful when you need line numbers for debugging
- `less` does not load the entire file into memory, so it opens huge files instantly
- The `f` in `tail -f` stands for "follow" — it keeps tracking the end of the file

## Common mistakes

### Mistake 1. Using cat on large files

```bash
cat access.log    # 1GB file -> terminal scrolls for minutes
# Ctrl+C stops it, but the terminal buffer is already flooded
```

Use `less` or `tail -n 100` to view only what you need.

### Mistake 2. Not knowing how to exit less

Press `q`. `Ctrl+C` does not work inside `less`. Unlike vim, it is `q` alone — not `:q`.

### Mistake 3. Leaving tail -f running without stopping it

`tail -f` is a never-ending command. You must explicitly stop it with `Ctrl+C`. Leaving it in the background consumes resources.

### Mistake 4. Not knowing the default (10 lines) for head/tail

`head file.txt` prints 10 lines by default. To see only 5 lines, you must specify `-n 5`.

### Mistake 5. Not knowing cat's original purpose — concatenation

`cat` stands for concatenate. Its original purpose is joining multiple files together.

```bash
cat header.csv data1.csv data2.csv > combined.csv
```

## Practical applications

- **Log monitoring**: `tail -f /var/log/nginx/error.log` for real-time errors
- **CSV header check**: `head -n 1 data.csv` to quickly see column names
- **Config check**: `cat config.yaml` for short configuration files
- **Line counting**: `wc -l access.log` to quickly gauge request volume
- **Log filtering**: `tail -n 1000 app.log | grep ERROR` to extract recent errors

## How practitioners think about this

The decision criterion for "which command to view a file with" is **file size and purpose**. A few dozen lines means `cat`, hundreds of lines or more means `less`, and only the beginning or end means `head`/`tail`. Once this selection becomes automatic, your CLI speed improves noticeably.

The most-used combination in production is `tail -f` + `grep`. Running `tail -f app.log | grep --line-buffered ERROR` shows errors the instant they occur. Without this combination during incident response, you fall into the inefficiency of "opening the log file in an editor and refreshing".

## Checklist

- [ ] You can distinguish the purposes of `cat`, `less`, `head`, and `tail`
- [ ] You can search (`/`) and quit (`q`) in `less`
- [ ] You can view a specific number of lines with `head -n N` and `tail -n N`
- [ ] You can monitor logs in real time with `tail -f`
- [ ] You can choose the appropriate command based on file size

## Exercises

1. Check the line count of `/etc/passwd` with `wc -l`, then print the first 5 and last 5 lines separately.
2. Create a file with `seq 1 10000 > big.txt`, open it in `less`, and search for `/5000` to jump to that line.
3. Run `tail -f /tmp/live.log`, then from another terminal run `echo "test" >> /tmp/live.log` and observe the real-time output.

## Summary and next

- `cat` prints short files at once or concatenates multiple files.
- `less` browses large files page by page with memory efficiency.
- `head`/`tail` quickly show only the beginning or end of a file.
- `tail -f` is the essential tool for real-time log monitoring.
- Choosing the appropriate command based on file size and purpose is a mark of CLI proficiency.

The next post covers **text search and file finding** — `grep`, `find`, `xargs`.

<!-- toc:begin -->
## Series Table of Contents

- [What Is the CLI and Shell?](./01-what-is-cli-and-shell.md)
- [Files and Directories](./02-files-and-directories.md)
- [Permissions and Ownership](./03-permissions-and-ownership.md)
- **cat, less, head, tail (current)**
- grep, find, xargs (upcoming)
- Pipes and Redirection (upcoming)
- Process Management (upcoming)
- Environment Variables and PATH (upcoming)
- Shell Script Basics (upcoming)
- SSH and Remote Access (upcoming)

<!-- toc:end -->

## References

- [GNU Coreutils - cat, head, tail](https://www.gnu.org/software/coreutils/manual/)
- [less man page](https://man7.org/linux/man-pages/man1/less.1.html)
- [The Missing Semester - Data Wrangling](https://missing.csail.mit.edu/2020/data-wrangling/)
- [Linux Journal - tail -f and friends](https://www.linuxjournal.com/content/tail-f-and-friends)

Tags: Linux, CLI, cat, less, tail, Log
