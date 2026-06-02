---
title: "Linux CLI 101 (4/10): cat, less, head, tail — Viewing File Contents"
series: linux-cli-101
episode: 4
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
- CLI
- cat
- less
- tail
- Log
last_reviewed: '2026-05-15'
seo_description: cat dumps a file all at once like pouring a bucket, and less lets
  you flip through it one page at a time like reading a book.
---

# Linux CLI 101 (4/10): cat, less, head, tail — Viewing File Contents

When you work on servers, reading files efficiently matters almost as much as editing them. Logs, config files, CSVs, and generated output all need different reading habits, and using the wrong command can waste time or flood your terminal.

This is the 4th post in the Linux CLI 101 series.


![Linux CLI 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/04/04-01-big-picture.en.png)
*Linux CLI 101 chapter 4 flow overview*

## Questions to Keep in Mind

- Using `cat` to quickly view short files?
- Using `less` to browse long files page by page?
- Using `head` and `tail` to slice the beginning or end of a file?

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

## Shell Checkpoints for Automation Quality

### Input Validation and Exit Code Contracts
For a shell script to become a team tool, its failure modes must be predictable. Declaring argument validation and exit code contracts allows CI and operational scripts to integrate safely.

```bash
#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: $0 <log_dir> <keyword>"
}

if [ "$#" -ne 2 ]; then
  usage
  exit 64
fi

log_dir="$1"
keyword="$2"

if [ ! -d "$log_dir" ]; then
  echo "directory not found: $log_dir"
  exit 66
fi

if grep -R --line-number "$keyword" "$log_dir" >/tmp/match.out; then
  echo "match found"
  exit 0
else
  echo "no match"
  exit 1
fi
```

Exit codes like `64` and `66` classify the failure cause for the caller. When human-readable messages and machine-readable codes are separated, branching logic in automation pipelines becomes straightforward.

### Finding Pipeline Bottlenecks
Complex pipelines are hard to diagnose by feel alone. Stamp timestamps before and after each stage, or split into temporary files to identify which stage is slow.

```bash
time grep -R "ERROR" /var/log/myapp > /tmp/step1.txt
time cut -d' ' -f1-8 /tmp/step1.txt > /tmp/step2.txt
time sort /tmp/step2.txt | uniq -c | sort -nr > /tmp/step3.txt
```

This approach is simple but effective. You can quickly tell whether a stage is CPU-bound or I/O-bound, and then decide on optimizations such as `awk` replacement, parallelization, or input reduction.

### Reusable Function Snippets
Even in long scripts, splitting functionality into functions makes testing and maintenance easier.

```bash
collect_pids() {
  pgrep -f "$1" || true
}

kill_gracefully() {
  local pid="$1"
  kill -TERM "$pid"
  sleep 2
  kill -0 "$pid" 2>/dev/null && kill -KILL "$pid" || true
}
```

Function-level decomposition enables scenario-by-scenario verification: whether the termination signal is handled correctly, whether zombie processes remain, whether restart logic runs twice.

## Practical Scenario: Turning File Viewing into an Analysis Routine

File viewing commands are not simply about reading content. In operations, they are the starting point of an analysis routine: "find the problem segment quickly, preserve evidence, and connect to the next action." That is why building a habit of combining the right viewing tools for the purpose is more valuable than repeating `cat` for everything.

### Check Metadata Before Viewing the Full File

```bash
ls -lh /var/log/my-app/app.log
stat /var/log/my-app/app.log

# Partial expected output
# -rw-r----- 1 deploy deploy 142M May 21 14:10 /var/log/my-app/app.log
# Size: 148944001  Blocks: ...  Access: ...  Modify: 2026-05-21 14:10:03
```

Checking file size and modification time first lets you quickly judge "is the log I am looking at actually current?" This prevents the mistake of analyzing a stale file.

### Save Time with Range-Based Viewing

```bash
# First 40 lines: check format, headers, initialization logs
head -n 40 /var/log/my-app/app.log

# Last 80 lines: check current failure symptoms
tail -n 80 /var/log/my-app/app.log

# Real-time tracking
tail -f /var/log/my-app/app.log
```

For real-time tracking, the efficient approach is to reproduce requests in a separate terminal while keeping the log terminal focused on evidence collection.

### Compress Failure Patterns with grep Regex

```bash
grep -E 'ERROR|CRITICAL|Exception|timeout|5[0-9]{2}' /var/log/my-app/app.log \
  | tail -n 40

# Expected output
# 2026-05-21T14:12:03 ERROR Payment timeout after 3000ms
# 2026-05-21T14:12:04 CRITICAL Worker crashed pid=18312
```

A pattern like `5[0-9]{2}` broadly catches HTTP 5xx responses. The habit of viewing text through patterns rather than reading line by line speeds up analysis.

### Trace Root Causes with Context-Inclusive Viewing

```bash
grep -n -C 3 'Database connection pool exhausted' /var/log/my-app/app.log

# Partial expected output
# 12931-... INFO checkout connection
# 12932-... WARN retrying request
# 12933:... ERROR Database connection pool exhausted
# 12934-... INFO queue depth=87
```

Including surrounding context with `-C 3` makes it easier to understand the causal flow than looking at a single error line.

### Use less as an Analysis Tool

```bash
less /var/log/my-app/app.log
# /ERROR      -> search
# n / N       -> next/previous result
# g / G       -> file beginning/end
# q           -> quit
```

When dealing with large logs, `less` is not just a viewer but a navigator. It is especially powerful when comparing patterns by jumping back and forth between search results.

### Build Daily Aggregates with Pipe Chains

```bash
grep -E 'ERROR|CRITICAL' /var/log/my-app/app.log \
  | awk '{print $1}' \
  | cut -d'T' -f1 \
  | sort \
  | uniq -c

# Expected output
#   18 2026-05-19
#   24 2026-05-20
#   41 2026-05-21
```

Quickly grasping error-count trends lets you immediately determine "is today an anomaly?"

### Cross-Reference systemd Logs with File Logs

```bash
journalctl -u my-app --since '30 min ago' --no-pager \
  | grep -E 'Started|Stopped|Failed|OOM|ERROR'
```

Viewing application file logs and system logs together gives a more accurate picture of restart timing, OOM occurrences, and service failure reasons.

### Bash Snippet for Automating Inspection

```bash
#!/usr/bin/env bash
set -euo pipefail

log_file="/var/log/my-app/app.log"

printf '[INFO] file=%s size=%s\n' "$log_file" "$(stat -c '%s' "$log_file")"

grep -E 'ERROR|CRITICAL|timeout|5[0-9]{2}' "$log_file" \
  | tail -n 60 \
  | tee /tmp/my-app-errors-latest.txt

printf '[INFO] saved=/tmp/my-app-errors-latest.txt\n'
```

The key is saving results to a file. Being able to reuse the same evidence in meetings or incident reports reduces communication overhead.

## Practical Inspection Log Example

The example below is an abbreviated version of inspection output frequently seen in real operations. What matters is not copying specific commands verbatim, but building the habit of connecting output to the next judgment.

```bash
# Collect service status + recent errors in one pass
systemctl is-active my-api
journalctl -u my-api --since '5 min ago' --no-pager \
  | grep -E 'ERROR|CRITICAL|timeout|Failed' \
  | tail -n 20

# Expected output
# active
# 2026-05-21 15:31:10 ERROR timeout while calling payment API
# 2026-05-21 15:31:12 CRITICAL worker exited unexpectedly
```

```bash
# Process / port / file handle inspection
ps -ef | grep -E 'my-api|gunicorn' | grep -v grep
ss -lntp | grep -E ':8080|:80|:443'
lsof -p "$(pgrep -f my-api | head -n 1)" | wc -l

# Expected output example
# deploy 18231 1  ... /opt/my-api/current/bin/start.sh
# LISTEN 0 4096 0.0.0.0:8080 ... users:(("python3",pid=18231,fd=12))
# 412
```

Saving these outputs as a time series makes comparison easy when issues recur, and quickly explains "how the current state differs from normal." Ultimately, practical CLI competence is the ability to reliably repeat an **evidence-based judgment routine**, not the commands themselves.

### Operations Note: Recovery Order After Failure

When a failure occurs, the sequence "check status → collect evidence → minimal action" is safer than "guess the cause → restart immediately."

```bash
systemctl status my-api --no-pager | sed -n '1,12p'
journalctl -u my-api -n 50 --no-pager | grep -E 'ERROR|CRITICAL|timeout|Failed' || true
```

Preserving status and logs first means that even after a restart erases evidence, you can still proceed with retrospectives and prevention work.

### Operations Note: Post-Change Verification Check

After changing permissions, viewing settings, or environment values, perform system-level verification alongside functional tests.

```bash
whoami
hostname
systemctl is-active my-api
journalctl -u my-api -n 20 --no-pager
```

Even a short verification routine, if recorded every time, allows fast reconstruction of "what was changed and when" during incidents.

Storing these verification logs alongside issue numbers accelerates future incident response.

This habit is what builds long-term operational quality.

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

## Answering the Opening Questions

- **When should you view a file whole vs viewing only part of it?**
  - Short files (dozens of lines like `data.csv`) suit `cat` or `cat -n`; large log files call for `less`, `head -n 40` for the beginning, or `tail -n 80` for the recent window. The article checked `ls -lh` and `stat` before opening a 142 MB log—same judgment principle.
- **Why is `less` safer than raw output?**
  - `less` doesn't load the entire file into memory; it navigates page by page, so opening a large file won't flood the terminal buffer. `/ERROR`, `n`, `g`, `G`, `q` give controlled search and movement—far safer for analysis than `cat access.log` dumping everything at once.
- **How do `head` and `tail` serve different log-checking roles?**
  - `head` checks file format, headers, or initialization logs at the start; `tail` shows recent errors and current state. `tail -f /var/log/my-app/app.log` in particular lets you reproduce a request while watching new log lines appear—a fundamental incident-response routine.

<!-- toc:begin -->
## In this series

- [Linux CLI 101 (1/10): What Is the CLI and Shell?](./01-what-is-cli-and-shell.md)
- [Linux CLI 101 (2/10): Files and Directories](./02-files-and-directories.md)
- [Linux CLI 101 (3/10): Permissions and Ownership](./03-permissions-and-ownership.md)
- **cat, less, head, tail — Viewing File Contents (current)**
- grep, find, xargs — The Search Trio (upcoming)
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
