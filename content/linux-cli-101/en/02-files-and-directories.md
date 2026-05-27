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

- **The Linux file system hierarchy (`/`, `/home`, `/etc`, `/var`)?**
  - The article treats Files and Directories as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Checking your current location and navigating with `pwd`, `cd`, `ls`?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Manipulating files and directories with `mkdir`, `touch`, `cp`, `mv`, `rm`?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
