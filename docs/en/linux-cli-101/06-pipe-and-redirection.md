---
title: Pipes and Redirection
series: linux-cli-101
episode: 6
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
- pipe
- redirection
- stdin
- stdout
- CLI
last_reviewed: '2026-05-04'
seo_description: A pipe connects commands like plumbing, and redirection changes the
  flow of data from the screen to a file.
---

# Pipes and Redirection

> Linux CLI 101 series (6/10)

---

<!-- a-grade-intro:begin -->

## Key Questions

- How does `|` (pipe) connect two commands?
- What is the difference between `>`, `>>`, and `<`?
- Why are stdout and stderr separated?
- How do you save only error messages to a file?

> A pipe connects commands like plumbing, and redirection changes the flow of data from the screen to a file.

<!-- a-grade-intro:end -->

## What you will learn

- Passing the output of one command as input to the next with pipe (`|`)
- Saving output to a file with `>` (overwrite) and `>>` (append)
- The meaning of stdin (0), stdout (1), and stderr (2) file descriptors
- Merging or separating error and normal output with `2>&1`

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

<!-- toc:begin -->
## Series Table of Contents

- [What Is the CLI and Shell?](./01-what-is-cli-and-shell.md)
- [Files and Directories](./02-files-and-directories.md)
- [Permissions and Ownership](./03-permissions-and-ownership.md)
- [cat, less, head, tail](./04-viewing-files.md)
- [grep, find, xargs](./05-grep-find-xargs.md)
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
