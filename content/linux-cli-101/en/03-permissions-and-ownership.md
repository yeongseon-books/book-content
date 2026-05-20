---
title: "Linux CLI 101 (3/10): Permissions and Ownership"
series: linux-cli-101
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
- Linux
- Permission
- chmod
- chown
- Security
- File System
last_reviewed: '2026-05-15'
seo_description: Linux file permissions are like a door with three locks. The owner,
  the group, and everyone else each get a different key.
---

# Linux CLI 101 (3/10): Permissions and Ownership

Permission problems often look misleading. A file is right there, but the script will not run. A config path exists, but the process still cannot read it. Until you can read `rwx` fluently, these errors feel arbitrary.

This is post 3 in the Linux CLI 101 series.

## Questions to Keep in Mind

- The 3x3 structure of Linux file permissions (owner/group/others x read/write/execute)?
- How to read permission strings in `ls -l` output?
- Two ways to change permissions with `chmod` (numeric and symbolic)?

## Big Picture

![Linux CLI 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/03/03-01-big-picture.en.png)

*Linux CLI 101 chapter 3 flow overview*

This picture places Permissions and Ownership inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Permissions and Ownership is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Why it matters

You try to run a script on a server with `./deploy.sh` and get "Permission denied". The file clearly exists — so why won't it run? Because the execute permission (x) is missing.

> A web server cannot read a configuration file and returns a 502 error. The file exists, but a "No such file"-like error appears. The cause is that the directory lacks execute permission (x), making it impossible to enter that path at all.

Permission issues are among the most common problems developers encounter on servers, and not understanding them leads to the dangerous habit of `chmod 777` for everything, creating security holes.

## Mental Model

> File permissions are like a door with three locks. One for the owner, one for the group, and one for others. Each lock has three keys: read (r), write (w), and execute (x).

```text
-rwxr-xr--
│└┬┘└┬┘└┬┘
│ │  │  └── others: r-- (read only)
│ │  └── group:  r-x (read+execute)
│ └── owner:  rwx (read+write+execute)
└── file type (-: regular file, d: directory)
```

## Core Concepts

| Symbol | Meaning | Number | File | Directory |
|---|---|---|---|---|
| r | read | 4 | read contents | list entries (ls) |
| w | write | 2 | modify contents | create/delete files |
| x | execute | 1 | run as program | enter directory (cd) |
| - | no permission | 0 | — | — |

## Before / After

**Before (not understanding permissions)**

```bash
./deploy.sh
# bash: ./deploy.sh: Permission denied
chmod 777 deploy.sh    # "Just 777 if it doesn't work" — security hole
```

**After (understanding permissions)**

```bash
ls -l deploy.sh
# -rw-r--r-- 1 user team 512 May 4 deploy.sh
# -> execute permission (x) is missing

chmod u+x deploy.sh   # Add execute permission for owner only
./deploy.sh            # Runs successfully
```

## Step-by-step practice

### Step 1. Check permissions

```bash
cd ~/practice/linux-cli
touch secret.txt
ls -l secret.txt
# -rw-r--r-- 1 user user 0 May  4 10:00 secret.txt
```

### Step 2. Change permissions with numeric mode

```bash
chmod 644 secret.txt     # owner: rw-, group: r--, others: r--
chmod 755 secret.txt     # owner: rwx, group: r-x, others: r-x
chmod 600 secret.txt     # owner: rw-, group: ---, others: ---
ls -l secret.txt
# -rw------- 1 user user 0 May  4 10:00 secret.txt
```

Numeric calculation: add r=4, w=2, x=1. `755` = `rwx`(7) + `r-x`(5) + `r-x`(5).

### Step 3. Change permissions with symbolic mode

```bash
chmod u+x secret.txt     # Add execute for owner
chmod g-r secret.txt     # Remove read from group
chmod o=r secret.txt     # Set others to read only
chmod a+r secret.txt     # Add read for all
ls -l secret.txt
```

### Step 4. Directory permissions

```bash
mkdir testdir
chmod 700 testdir        # Only owner can access
ls -ld testdir
# drwx------ 2 user user 4096 May  4 10:00 testdir
```

### Step 5. Change ownership

```bash
# Changing ownership requires root privileges
sudo chown root:root secret.txt
ls -l secret.txt
# -rwxr--r-- 1 root root 0 May  4 10:00 secret.txt

sudo chown user:user secret.txt   # Restore original
```

## What to notice in this code

- The first column of `ls -l` is the permission string — 10 characters (1 type + 9 permissions)
- Numeric mode sets everything at once; symbolic mode changes individual parts
- The `x` permission on a directory means "enter", not "execute"
- `chown` usually requires `sudo`

## Common mistakes

### Mistake 1. Solving everything with chmod 777

777 grants all permissions to every user. Setting 777 on web server files means anyone can modify them — a security vulnerability. Follow the principle of least privilege.

### Mistake 2. Overlooking the x permission on directories

On a directory, `x` means "permission to enter". With only `r` and no `x`, you can list entries with `ls` but cannot `cd` into it. To access a file, every directory in the path must have `x`.

### Mistake 3. Ignoring group permissions

When working alone, you only think about owner permissions. But on a team server, other developers in the same group need to read or modify files. Without proper group settings, colleagues cannot open files.

### Mistake 4. Not distinguishing files and directories in recursive permission changes

```bash
chmod -R 755 project/   # All files get execute permission — dangerous
# Correct approach:
find project/ -type d -exec chmod 755 {} \;   # Directories only
find project/ -type f -exec chmod 644 {} \;   # Files only
```

### Mistake 5. Creating files without knowing umask

The default permissions for new files are determined by `umask`. With `umask 022`, files are created as 644 and directories as 755. With `umask 077`, only the owner can access them.

## Practical applications

- **Deploy scripts**: Add execute permission with `chmod u+x deploy.sh`
- **SSH keys**: `chmod 600 ~/.ssh/id_rsa` is mandatory. SSH refuses keys with loose permissions
- **Web server**: HTML/CSS at 644, CGI/scripts at 755, config files at 600 is typical
- **Shared directories**: `chmod 2775 shared/` sets setgid so new files inherit the group
- **Docker**: Permission mismatches between container and host cause volume mount issues

## How practitioners think about this

The guiding principle for permissions is the **Principle of Least Privilege**. Grant only what is needed and close everything else. "Let's open 777 for now and tighten later" is dangerous because "later" never comes.

On the other hand, permissions that are too strict block team collaboration. A balanced approach is to open group permissions reasonably on dev servers while minimizing them on production. Tracking time lost to permission issues reveals which settings are appropriate.

## Checklist

- [ ] You can read `rwxr-xr--` and describe the owner/group/others permissions
- [ ] You can calculate what `chmod 755` grants
- [ ] You can make partial changes with symbolic mode (`u+x`, `g-w`)
- [ ] You know that `x` on a directory means "enter"
- [ ] You can explain why `chmod 777` should never be used

## Exercises

1. Create a `test.sh` file with `#!/bin/bash` and `echo "Hello"`, add execute permission, and run it with `./test.sh`.
2. Compare the permissions of `ls -l /etc/passwd` and `ls -l /etc/shadow`, and guess why they differ.
3. Run `umask` to check the current value, create a new file with `touch`, and explain how the default permissions relate to the umask.

## Summary and next

- Linux file permissions follow a 3x3 structure: owner/group/others x r/w/x.
- Numeric mode (644, 755) sets everything at once; symbolic mode (u+x) changes individual parts.
- The x permission on a directory means permission to enter, and every directory in the path needs it.
- Follow the principle of least privilege and never use 777.
- `chown` requires root privileges to change ownership.

The next post covers **viewing file contents** — `cat`, `less`, `head`, `tail`.

## Answering the Opening Questions

- **The 3x3 structure of Linux file permissions (owner/group/others x read/write/execute)?**
  - The article treats Permissions and Ownership as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How to read permission strings in `ls -l` output?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Two ways to change permissions with `chmod` (numeric and symbolic)?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Linux CLI 101 (1/10): What Is the CLI and Shell?](./01-what-is-cli-and-shell.md)
- [Linux CLI 101 (2/10): Files and Directories](./02-files-and-directories.md)
- **Permissions and Ownership (current)**
- cat, less, head, tail — Viewing File Contents (upcoming)
- grep, find, xargs — The Search Trio (upcoming)
- Pipes and Redirection (upcoming)
- Process Management (upcoming)
- Environment Variables and PATH (upcoming)
- Shell Script Basics (upcoming)
- SSH and Remote Access (upcoming)

<!-- toc:end -->

## References

- [Linux File Permissions Explained](https://www.redhat.com/sysadmin/linux-file-permissions-explained)
- [GNU Coreutils - chmod](https://www.gnu.org/software/coreutils/manual/html_node/chmod-invocation.html)
- [OWASP - Principle of Least Privilege](https://owasp.org/www-community/Access_Control)
- [Linux man page - chmod, chown](https://man7.org/linux/man-pages/)

Tags: Linux, Permission, chmod, chown, Security, File System
