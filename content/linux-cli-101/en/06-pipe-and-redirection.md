---
title: "Linux CLI 101 (6/10): Pipes and Redirection"
series: linux-cli-101
episode: 6
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
- pipe
- redirection
- stdin
- stdout
- CLI
last_reviewed: '2026-05-15'
seo_description: A pipe connects commands like plumbing, and redirection changes the
  flow of data from the screen to a file.
---

# Linux CLI 101 (6/10): Pipes and Redirection

Single commands are useful, but real CLI work usually starts when you connect them. Filtering logs, saving build output, and separating failures from normal output all depend on understanding where stdin, stdout, and stderr are flowing.

This is the 6th post in the Linux CLI 101 series.


![Linux CLI 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/06/06-01-mental-model.en.png)
*Linux CLI 101 chapter 6 flow overview*

## Questions to Keep in Mind

- Passing the output of one command as input to the next with pipe (`|`)?
- Saving output to a file with `>` (overwrite) and `>>` (append)?
- The meaning of stdin (0), stdout (1), and stderr (2) file descriptors?

## Why it matters

The Linux philosophy is "build small tools that each do one thing well, and compose them to accomplish big tasks". `grep` only searches, `sort` only sorts, `wc` only counts. The glue that connects these tools is pipes and redirection.

> You want to find the top 5 IP addresses with the most requests in today's web server log. Counting tens of thousands of lines by eye in an editor is impossible.

```bash
cat access.log | grep "2026-05-04" | awk '{print $1}' | sort | uniq -c | sort -rn | head -5
```

This single line finishes in 3 seconds what would take an analyst 30 minutes in a spreadsheet.

## Mental Model

> Commands are faucets and pipe (`|`) is plumbing. Data flows from left to right. Redirection (`>`) diverts the flow from the pipe to a bucket (file) instead.

```text
[Command A] --stdout--|--stdin--> [Command B] --stdout--> screen
                                                          |
[Command A] --stdout--> file.txt    (overwrite)           |
[Command A] --stdout-->> file.txt   (append)              |
[Command A] <--stdin-- file.txt     (file as input)
```

## Core Concepts

| Symbol | Name | Role | Example |
|---|---|---|---|
| `\|` | pipe | Left stdout -> right stdin | `ls \| grep ".py"` |
| `>` | redirect (overwrite) | stdout -> file (existing contents deleted) | `echo "hi" > out.txt` |
| `>>` | redirect (append) | stdout -> file (existing contents preserved) | `echo "hi" >> out.txt` |
| `<` | input redirect | file -> stdin | `sort < names.txt` |
| `2>` | stderr redirect | Errors only to file | `cmd 2> error.log` |
| `2>&1` | stderr to stdout | Merge errors and output | `cmd > all.log 2>&1` |

## Before / After

**Before (manually creating intermediate files)**

```bash
grep "ERROR" app.log > errors.txt
sort errors.txt > sorted.txt
uniq -c sorted.txt > counted.txt
sort -rn counted.txt > result.txt
cat result.txt
# 4 files created, cleanup needed
```

**After (one pipe line)**

```bash
grep "ERROR" app.log | sort | uniq -c | sort -rn
# No intermediate files, result printed immediately
```

## Step-by-step practice

### Step 1. Create practice data

```bash
cd ~/practice/linux-cli
cat > access.log << 'EOF'
192.168.1.10 GET /index.html 200
10.0.0.5 GET /api/users 200
192.168.1.10 GET /style.css 200
10.0.0.5 POST /api/login 401
172.16.0.1 GET /index.html 200
192.168.1.10 GET /api/data 500
10.0.0.5 GET /index.html 200
172.16.0.1 GET /api/users 200
EOF
```

### Step 2. Connect commands with pipe

```bash
cat access.log | grep "200"             # Only successful requests
cat access.log | awk '{print $1}' | sort | uniq -c | sort -rn
# 3 192.168.1.10
# 3 10.0.0.5
# 2 172.16.0.1
```

### Step 3. Save to a file with redirection

```bash
grep "500" access.log > errors.txt      # Save only 500 errors
cat errors.txt
# 192.168.1.10 GET /api/data 500

echo "new error" >> errors.txt          # Append
cat errors.txt
# 192.168.1.10 GET /api/data 500
# new error
```

### Step 4. Separate stderr

```bash
ls /nonexistent 2> error.log            # Errors only to file
cat error.log
# ls: cannot access '/nonexistent': No such file or directory

ls /tmp /nonexistent > out.txt 2> err.txt  # Separate output and errors
ls /tmp /nonexistent > all.txt 2>&1        # Both to same file
```

### Step 5. Real-world pipelines

```bash
# Top 3 IPs by request count
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -3

# Extract only 500-error IPs
grep "500" access.log | awk '{print $1}' | sort -u

# Save to file AND print to screen (tee)
grep "200" access.log | tee success.log | wc -l
# 6 (screen output) + success.log also saved
```

## What to notice in this code

- Pipe flows data without intermediate files, saving disk space
- `>` overwrites the file, deleting existing contents. `>>` is safer
- In `2>&1`, the `&` means "file descriptor". Without `&`, `2>1` would write to a file literally named "1"
- `tee` sends data to both screen and file — like a T-shaped pipe

## Common mistakes

### Mistake 1. Confusing `>` and `>>` and losing data

```bash
echo "important" > data.txt    # Overwrites — existing contents deleted
echo "important" >> data.txt   # Appends — existing contents preserved
```

For important files, use `>>` or back up before using `>`.

### Mistake 2. Reading and writing the same file

```bash
sort file.txt > file.txt    # File becomes empty!
# Shell empties file.txt with > before sort reads it
sort file.txt > sorted.txt && mv sorted.txt file.txt  # Safe
```

### Mistake 3. Ignoring stderr

If a script does not capture errors, error messages mix into the screen output. Use `2>/dev/null` to discard or `2>error.log` to save separately.

### Mistake 4. Useless Use of Cat (UUOC)

```bash
cat file.txt | grep "pattern"    # Useless Use of Cat
grep "pattern" file.txt          # grep reads the file directly — more efficient
```

### Mistake 5. Getting the pipe order wrong

Filter first (grep), then sort. Sorting before filtering wastes time sorting lines that will be discarded.

## Practical applications

- **Log analysis**: `grep "ERROR" app.log | awk '{print $5}' | sort | uniq -c | sort -rn` for error frequency by type
- **Build logs**: `make 2>&1 | tee build.log` saves to screen and file simultaneously
- **Batch processing**: `find . -name "*.csv" | xargs -I {} sh -c 'process.py {} > {}.out'`
- **Cron jobs**: `script.sh > /var/log/cron.log 2>&1` logs scheduled tasks
- **Data preprocessing**: `cut -d',' -f2 data.csv | sort | uniq -c | sort -rn | head`

## How practitioners think about this

Pipes are the heart of the Unix philosophy. Composing small tools eliminates the need to write dedicated programs for most text processing tasks. Developing the habit of asking "Can I do this in one pipe line?" before writing a Python script is a hallmark of CLI proficiency.

On the other hand, when a pipe chain exceeds 5 stages, maintainability drops. At that point, it makes sense to move the logic to a Python or shell script. Pipes are optimal for "one-off analysis"; "logic that runs repeatedly" should be saved as a script for the sake of team collaboration.

## When it breaks, check these first

- If the pipeline output is empty, peel it apart from left to right. Check `grep "ERROR" app.log` first, then add `| sort`, then `| uniq -c`, so you can see exactly where data disappears.
- If a file suddenly becomes empty, look for commands like `sort file.txt > file.txt`. The shell truncates the file before the command reads it, so you need a temporary file or a safer pattern.
- If failure details never show up, verify whether stderr was redirected at all. For build and deploy logs, `2>&1 | tee build.log` is often the fastest way to keep both the screen view and the forensic record.
- If you are unsure whether to overwrite or append, write to a temporary file first. Production logs and report files are expensive to recreate once `>` wipes them out.

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

## Practical Scenario: Fixing Analysis Flows with Pipes and Redirection

Pipes and redirection are the core of CLI automation. The key is not making output pretty, but **transforming it into a form the next stage can consume**.

### Understand Standard Streams by Separating Them First

```bash
python3 app.py > /tmp/app.out 2> /tmp/app.err

# Expected result
# /tmp/app.out : normal output
# /tmp/app.err : error output
```

Separating stdout and stderr during problem analysis speeds up root cause tracing.

### Use tee to Display and Save Simultaneously

```bash
journalctl -u my-api --since '20 min ago' \
  | grep -E 'ERROR|CRITICAL|timeout' \
  | tee /tmp/my-api-errors.txt
```

`tee` satisfies "see it now" + "reuse it later" simultaneously.

### Pipe Chain Design Example: Access Log Summary

```bash
cat /var/log/nginx/access.log \
  | awk '{print $1, $7, $9}' \
  | grep -E ' 5[0-9]{2}$' \
  | sort \
  | uniq -c \
  | sort -nr \
  | head -n 20

# Expected output
#   87 10.10.1.2 /api/pay 502
#   41 10.10.1.5 /api/order 504
```

This flow is a typical pattern for turning "raw log" into a "priority action list."

### Generate Config Files with Here Documents and Redirection

```bash
cat > /tmp/my-api.env << 'EOF'
APP_ENV=production
LOG_LEVEL=INFO
WORKER_COUNT=4
EOF

cat /tmp/my-api.env
```

Useful for creating config files in automation scripts, but secrets should never remain in plain text — use a dedicated secret management system.

### stderr Merging and Separation Strategies

```bash
# stdout + stderr both to file
./deploy.sh > /tmp/deploy.log 2>&1

# stderr only to separate file
./deploy.sh 2> /tmp/deploy.err
```

In operations, "viewing only failure logs" is important, so stderr file separation is used frequently.

### Bulk Execution with xargs and Pipes

```bash
printf '%s\n' api worker scheduler \
  | xargs -n 1 -I {} sh -c 'systemctl status my-{} --no-pager | sed -n "1,5p"'
```

Effective for quickly inspecting multiple services.

### Combine systemd Logs with Redirection

```bash
journalctl -u my-api --since '1 hour ago' --no-pager \
  > /tmp/my-api-journal.txt

grep -E 'ERROR|CRITICAL|timeout|OOM' /tmp/my-api-journal.txt
```

Saving to a file instead of only viewing in real time enables team review and retrospective reuse.

### Bash Pipeline Script Example

```bash
#!/usr/bin/env bash
set -euo pipefail

service="my-api"
out="/tmp/${service}-incident-$(date +%Y%m%d-%H%M%S).log"

journalctl -u "$service" --since '30 min ago' --no-pager \
  | grep -E 'ERROR|CRITICAL|timeout|OOM' \
  | tee "$out"

printf '[INFO] saved=%s\n' "$out"
```

Scripts like this produce "the same result no matter who runs them" during incidents, stabilizing operational quality.

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

## Checklist

- [ ] You can connect two commands' output/input with `|`
- [ ] You know the difference between `>` (overwrite) and `>>` (append)
- [ ] You can explain why stdout (1) and stderr (2) are separate
- [ ] You can merge errors and output with `2>&1`
- [ ] You can output to both screen and file simultaneously with `tee`

## Exercises

1. Count the number of users with `/bin/bash` in `/etc/passwd` using a single pipe line.
2. Extract only the file sizes (5th column) from `ls -la /etc`, sort by size, and print the top 5.
3. Run `find / -name "*.conf" 2>/dev/null | head -10` and explain why `2>/dev/null` is needed.

## Summary and next

- Pipe (`|`) connects the stdout of one command to the stdin of the next.
- `>` overwrites, `>>` appends when saving output to a file.
- stdout (1) and stderr (2) are independent and can be merged with `2>&1`.
- `tee` outputs to both screen and file simultaneously.
- When pipe chains get complex, moving to a script improves maintainability.

The next post covers **process management** — `ps`, `top`, `kill`, and background execution.

## Answering the Opening Questions

- **Why are stdin, stdout, and stderr separated?**
  - Keeping normal output and errors apart lets the next command consume only the data it needs reliably. Splitting with `python3 app.py > /tmp/app.out 2> /tmp/app.err` eases analysis and automation; merging back with `2>&1 | tee build.log` becomes an explicit choice.
- **What flow does each of `|`, `>`, `>>`, `2>` create?**
  - `|` passes left-side stdout to right-side stdin; `>` overwrites a file; `>>` appends; `2>` redirects only stderr. `awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -3` and `ls /tmp /nonexistent > out.txt 2> err.txt` are canonical pipe and redirection examples.
- **What improves when you chain commands without intermediate files?**
  - Immediate results without disk waste or cleanup cost. A pipe chain that compresses access logs into a 5xx list lets each stage consume the previous stage's output directly in transformed form.

<!-- toc:begin -->
## In this series

- [Linux CLI 101 (1/10): What Is the CLI and Shell?](./01-what-is-cli-and-shell.md)
- [Linux CLI 101 (2/10): Files and Directories](./02-files-and-directories.md)
- [Linux CLI 101 (3/10): Permissions and Ownership](./03-permissions-and-ownership.md)
- [Linux CLI 101 (4/10): cat, less, head, tail — Viewing File Contents](./04-viewing-files.md)
- [Linux CLI 101 (5/10): grep, find, xargs — The Search Trio](./05-grep-find-xargs.md)
- **Pipes and Redirection (current)**
- Process Management (upcoming)
- Environment Variables and PATH (upcoming)
- Shell Script Basics (upcoming)
- SSH and Remote Access (upcoming)

<!-- toc:end -->

## References

- [GNU Bash Manual - Redirections](https://www.gnu.org/software/bash/manual/html_node/Redirections.html)
- [The Missing Semester - Data Wrangling](https://missing.csail.mit.edu/2020/data-wrangling/)
- [Linux Documentation - I/O Redirection](https://tldp.org/LDP/abs/html/io-redirection.html)
- [Useless Use of Cat Award](https://porkmail.org/era/unix/award)

Tags: Linux, pipe, redirection, stdin, stdout, CLI
