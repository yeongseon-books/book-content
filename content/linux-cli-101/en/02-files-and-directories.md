---
title: "Linux CLI 101 (2/10): Files and Directories"
series: linux-cli-101
episode: 2
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
- File System
- Directory
- ls
- cp
last_reviewed: '2026-05-15'
seo_description: The Linux file system is a giant tree that starts from a single root
  (/). Every file and directory is a branch of this tree.
---

# Linux CLI 101 (2/10): Files and Directories

Most server work is not glamorous. You move release bundles, back up config files, clean up logs, and figure out where a missing file actually lives. If your path sense is weak, even simple maintenance work slows down fast.

This is the 2nd post in the Linux CLI 101 series.


![Linux CLI 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/02/02-01-big-picture.en.png)
*Linux CLI 101 chapter 2 flow overview*

## Questions to Keep in Mind

- The Linux file system hierarchy (`/`, `/home`, `/etc`, `/var`)?
- Checking your current location and navigating with `pwd`, `cd`, `ls`?
- Manipulating files and directories with `mkdir`, `touch`, `cp`, `mv`, `rm`?

## Why it matters

A developer's daily routine is an endless cycle of creating, moving, copying, and deleting files. You organize code files, copy configuration files, and remove build artifacts. In a GUI you drag and drop, but on a server everything is done through commands.

> You receive a request to back up log files on a deployment server. There are 50 files inside `/var/log/app/` and you need to copy them to `/backup/2026-05-04/`. There is no mouse.

To finish this task in 3 seconds with `cp -r`, you need to understand the file system structure and basic commands.

## Mental Model

> The Linux file system is a giant tree that starts from a single root (`/`). Every file and directory is a branch of this tree.

Windows has multiple drive letters like `C:\` and `D:\`, but Linux always starts from a single `/` (root). Even when you plug in a USB drive or mount a network share, everything hangs somewhere on this tree.

```text
/                       <- root
├── home/               <- user home directories
│   └── user/           <- my workspace (~)
├── etc/                <- system configuration files
├── var/                <- logs, caches, variable data
├── tmp/                <- temporary files
└── usr/                <- user programs
    └── bin/            <- executables
```

## Core Concepts

| Term | Description | Example |
|---|---|---|
| Absolute path | Full path starting from `/` | `/home/user/project/main.py` |
| Relative path | Path relative to current location | `./src/main.py`, `../config.yaml` |
| `.` | Current directory | `./run.sh` (run.sh in the current folder) |
| `..` | Parent directory | `cd ..` (move one level up) |
| `~` | Home directory | `cd ~` = `cd /home/user` |

## Before / After

**Before (not knowing paths)**

```text
"The file is somewhere... where was it?"
-> Click through folders one by one in the GUI
-> 5 minutes spent
```

**After (a CLI user who knows paths)**

```bash
find /var/log -name "error*.log" -mtime -1
# Finds all error logs created since yesterday in 1 second
```

## Step-by-step practice

### Step 1. Check your current location

```bash
pwd
# Example output: /home/user
```

`pwd` (print working directory) shows where you currently are.

### Step 2. Navigate directories

```bash
cd /tmp           # Move using an absolute path
cd ~              # Move to home
mkdir -p ~/practice/linux-cli   # Create a practice directory
cd ~/practice/linux-cli         # Move into it
pwd
# Output: /home/user/practice/linux-cli
```

### Step 3. Create files and directories

```bash
touch hello.txt               # Create an empty file
mkdir src                     # Create a directory
mkdir -p src/utils/helpers    # Create nested directories at once
ls -la
# hello.txt, src/ are visible
```

### Step 4. Copy, move, and rename

```bash
cp hello.txt hello-backup.txt          # Copy a file
mv hello-backup.txt src/               # Move a file
mv src/hello-backup.txt src/backup.txt # Rename
ls src/
# backup.txt  utils/
```

### Step 5. Delete

```bash
rm src/backup.txt              # Delete a file
rmdir src/utils/helpers        # Delete an empty directory
rm -r src/utils                # Delete a directory and its contents
ls src/
# (empty)
```

## What to notice in this code

- `mkdir -p` creates intermediate directories at once. Without `-p`, it fails if the parent directory does not exist
- `mv` serves two roles: moving and renaming. Using `mv` within the same directory renames the file
- `rm -r` is recursive deletion. There is no recycle bin, so recovery is impossible
- To copy a directory with `cp`, the `-r` option is required

## Common mistakes

### Mistake 1. Running `rm -rf /`

Never do this. It deletes every file on the system. Modern systems refuse without `--no-preserve-root`, but you can still accidentally wipe `/home` or `/var`.

### Mistake 2. Using wildcard `*` without checking first

```bash
rm *.log        # Deletes only .log files — as intended
rm * .log       # Space causes deletion of ALL files, then tries to delete ".log" — disaster
```

Check targets with `ls *.log` before deleting.

### Mistake 3. Using filenames with spaces without quotes

```bash
cp My File.txt backup/     # Error: interpreted as two files "My" and "File.txt"
cp "My File.txt" backup/   # Correct
```

### Mistake 4. Confusing relative and absolute paths

`cd practice` only works when `practice` exists in the current directory. To work from anywhere, use an absolute path or `~` like `cd ~/practice`.

### Mistake 5. Forgetting `-r` when copying directories with `cp`

```bash
cp src/ backup/         # Error: "src/ is a directory"
cp -r src/ backup/      # Correct: recursive copy
```

## Practical applications

- **Project initialization**: Create a directory structure in one shot with `mkdir -p`
- **Log backup**: `cp -r /var/log/app/ /backup/$(date +%F)/` creates date-based backups
- **Build cleanup**: `rm -rf dist/ build/` clears previous build artifacts
- **Config backup**: `cp config.yaml config.yaml.bak` before making changes
- **Release preparation**: `mv app-v2.0.tar.gz /opt/releases/` moves release files

## How practitioners think about this

File manipulation commands look simple, but the key point is that **deletion is irreversible**. Code tracked by Git can be recovered, but log files or database dumps outside Git are gone once deleted.

Teams put safety guards on dangerous commands. Adding `alias rm='rm -i'` to `.bashrc` prompts for confirmation before every delete, or tools like `trash-cli` provide a recycle bin. On servers, a safer pattern is to `mv` files to a temporary folder instead of `rm`, then clean up after a set period.

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

## Practical Scenario: Safely Automating File Operations

File and directory commands look simple, but a significant portion of production incidents start here. For example, one wrong path in a log cleanup job can delete needed files. That is why in practice, the three-step habit of "confirm before acting → print affected scope → execute" is standard.

```bash
# 1) Confirm current location and target
pwd
ls -la ./releases

# Expected output
# /opt/my-app
# drwxr-xr-x  8 deploy deploy 4096 May 21 13:00 .
# drwxr-xr-x  5 deploy deploy 4096 May 21 09:11 ..
# drwxr-xr-x  2 deploy deploy 4096 May 14 10:00 20260514
```

### Establish Naming Conventions Before Creating

Directory structure design matters most at the beginning. In operations, conventions that include dates and environment names make incident tracing easier.

```bash
env_name="prod"
release_date="$(date +%Y%m%d)"
base_dir="/opt/my-app/releases/${env_name}-${release_date}"

mkdir -p "$base_dir"/{bin,conf,logs,tmp}
find "$base_dir" -maxdepth 2 -type d | sort

# Expected output
# /opt/my-app/releases/prod-20260521
# /opt/my-app/releases/prod-20260521/bin
# /opt/my-app/releases/prod-20260521/conf
# /opt/my-app/releases/prod-20260521/logs
# /opt/my-app/releases/prod-20260521/tmp
```

### Copy and Move: Thinking in Terms of Atomicity

`cp` leaves the original; `mv` relocates. In deployments, preparing in a temporary directory and then swapping a symlink is the safe pattern.

```bash
cp -a ./build/. "$base_dir/bin/"
ln -sfn "$base_dir" /opt/my-app/current
ls -la /opt/my-app/current

# Expected output
# lrwxrwxrwx 1 deploy deploy 34 May 21 13:12 /opt/my-app/current -> /opt/my-app/releases/prod-20260521
```

`ln -sfn` overwrites an existing link to make the switch brief. However, executing without verifying the link target can switch to the wrong release, so it is good practice to check file count and checksums before the switch.

### Deletion Always Starts with Candidate Output

Without safeguards, deletion carries high recovery costs.

```bash
# Preview deletion candidates
find /opt/my-app/releases -maxdepth 1 -type d -name 'prod-*' -mtime +14 -print

# Actual deletion
find /opt/my-app/releases -maxdepth 1 -type d -name 'prod-*' -mtime +14 -print0 \
  | xargs -0 rm -rf
```

The `-print0` and `xargs -0` combination handles spaces and special characters. This pattern is a fundamental safety mechanism for file operation automation.

### Verifying Permissions and Ownership Together

A file can exist but the service still fails if permissions are wrong.

```bash
chown -R deploy:deploy "$base_dir"
find "$base_dir" -type d -exec chmod 755 {} \;
find "$base_dir" -type f -name '*.sh' -exec chmod 750 {} \;

# Inspect
find "$base_dir" -maxdepth 2 -printf '%M %u:%g %p\n' | head -n 8
```

The key here is separating permissions for executables (`*.sh`) from regular files. Granting `chmod 777` to everything looks convenient but immediately becomes a problem from security and audit perspectives.

### Combining Regex with File Pattern Extraction

Cleanup tasks frequently require filename pattern filtering.

```bash
ls -1 /var/log/my-app \
  | grep -E '^app-[0-9]{4}-[0-9]{2}-[0-9]{2}\.log(\.[0-9]+)?$' \
  | sort

# Expected output
# app-2026-05-19.log
# app-2026-05-20.log
# app-2026-05-20.log.1
```

Writing explicit regex reduces the chance of touching unintended files.

### Linking systemd Units to Directory Structure

Aligning paths referenced by the service with the unit file stabilizes operations.

```ini
# /etc/systemd/system/my-app.service
[Unit]
Description=My App Service
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/opt/my-app/current
ExecStart=/opt/my-app/current/bin/start.sh
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

The benefit of this structure is clear: after preparing a new release, you only swap the `current` link without touching the unit file. The result is smaller deployment diffs and faster rollbacks.

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

When a failure occurs, "check state → collect evidence → minimal action" is safer than "guess cause → restart immediately."

```bash
systemctl status my-api --no-pager | sed -n '1,12p'
journalctl -u my-api -n 50 --no-pager | grep -E 'ERROR|CRITICAL|timeout|Failed' || true
```

Capturing state and logs first means that even if evidence disappears after a restart, you can still proceed with the retrospective and recurrence prevention.


## Checklist

- [ ] You can check your location with `pwd` and navigate with `cd`
- [ ] You can explain the difference between absolute and relative paths
- [ ] You can create nested directories in one shot with `mkdir -p`
- [ ] You know the difference between `cp`, `mv`, `rm` and when `-r` is needed
- [ ] You have the habit of checking targets with `ls` before using wildcard `*`

## Exercises

1. Create the structure `project/src/`, `project/tests/`, `project/docs/` under your home directory using a single `mkdir -p` command.
2. Use `touch` to create `project/src/main.py` and `project/tests/test_main.py`, then rename `project/src/main.py` to `project/src/app.py`.
3. Copy the entire `project/` directory to `project-backup/`, then delete the original `project/`.

## Summary and next

- The Linux file system is a single tree structure starting from `/` (root).
- You determine your location and navigate with `pwd`, `cd`, `ls`.
- You manipulate files and directories with `mkdir`, `touch`, `cp`, `mv`, `rm`.
- Deletion is irreversible, so always verify your targets before executing.
- Absolute paths work from anywhere; relative paths depend on your current location.

The next post covers **permissions and ownership** — `chmod`, `chown`, and the meaning of `rwx`.

## Answering the Opening Questions

- **When do absolute and relative paths feel different?**
  - An absolute path like `/opt/my-app/releases/prod-20260521` points to the same target regardless of where you run it; a relative path changes meaning based on your current location. High-stakes operations (deployments, backups) favor absolute paths; working within the current directory uses `./src` or `../config.yaml` for convenience.
- **How do you read your current position with just `pwd`, `cd`, `ls`?**
  - `pwd` confirms the reference point; `cd ~/practice/linux-cli` moves there; `ls -la` shows what actually exists. The article's production scenario ran `pwd` and `ls -la ./releases` before touching anything—preventing accidental work in the wrong directory.
- **When is each of `cp`, `mv`, `rm` safe to use?**
  - `cp` when the original must remain; `mv` for moves or renames; `rm` only when deletion is truly intended. The article showed previewing candidates with `find ... -print` first, then running `-print0 | xargs -0 rm -rf` only after verifying the list.

<!-- toc:begin -->
## In this series

- [Linux CLI 101 (1/10): What Is the CLI and Shell?](./01-what-is-cli-and-shell.md)
- **Files and Directories (current)**
- Permissions and Ownership (upcoming)
- cat, less, head, tail — Viewing File Contents (upcoming)
- grep, find, xargs — The Search Trio (upcoming)
- Pipes and Redirection (upcoming)
- Process Management (upcoming)
- Environment Variables and PATH (upcoming)
- Shell Script Basics (upcoming)
- SSH and Remote Access (upcoming)

<!-- toc:end -->

## References

- [Linux Filesystem Hierarchy Standard](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html)
- [GNU Coreutils Manual](https://www.gnu.org/software/coreutils/manual/)
- [The Missing Semester - Navigating the Shell](https://missing.csail.mit.edu/2020/course-shell/)
- [Linux man page - cp, mv, rm](https://man7.org/linux/man-pages/)

Tags: Linux, CLI, File System, Directory, ls, cp
