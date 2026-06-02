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

This is the 3rd post in the Linux CLI 101 series.


![Linux CLI 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/03/03-01-big-picture.en.png)
*Linux CLI 101 chapter 3 flow overview*

## Questions to Keep in Mind

- The 3x3 structure of Linux file permissions (owner/group/others x read/write/execute)?
- How to read permission strings in `ls -l` output?
- Two ways to change permissions with `chmod` (numeric and symbolic)?

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

## Practical Scenario: Operational Standards for Preventing Permission Incidents

Permission issues do not stop at "the command did not work" — they escalate into service outages and security incidents. In practice, file access failures are often misdiagnosed as feature bugs. That is why operators verify the permission model before even looking at application logs.

```bash
namei -l /opt/my-app/current/conf/app.env

# Expected output
# f: /opt/my-app/current/conf/app.env
# drwxr-xr-x root   root   /
# drwxr-xr-x root   root   opt
# drwxr-xr-x deploy deploy my-app
# lrwxrwxrwx deploy deploy current -> /opt/my-app/releases/prod-20260521
# drwxr-xr-x deploy deploy conf
# -rw-r----- deploy deploy app.env
```

If even one path component lacks execute permission (`x`), the file is inaccessible. `namei -l` shows this breakdown step by step, making it extremely efficient for permission debugging.

### Connecting Numeric Permissions to Meaning

Rather than memorizing `chmod 640` or `750` mechanically, interpret as "who reads, who executes."

```bash
chmod 640 /opt/my-app/current/conf/app.env
chmod 750 /opt/my-app/current/bin/start.sh
ls -l /opt/my-app/current/conf/app.env /opt/my-app/current/bin/start.sh

# Expected output
# -rw-r----- 1 deploy deploy 512 May 21 13:22 /opt/my-app/current/conf/app.env
# -rwxr-x--- 1 deploy deploy 824 May 21 13:20 /opt/my-app/current/bin/start.sh
```

This setting gives the owner execute/read permission and grants only the minimum needed to the group. Closing `others` reduces accidental exposure of sensitive information.

### Understanding setuid/setgid/sticky Bit from an Operations Perspective

Special bits are not exam questions — they tie directly to operational policy.

```bash
# Fix file group in a shared directory
chmod 2775 /srv/shared

# Protect a public directory like /tmp
chmod 1777 /tmp

ls -ld /srv/shared /tmp
# drwxrwsr-x 2 deploy ops 4096 May 21 13:30 /srv/shared
# drwxrwxrwt 20 root root 4096 May 21 12:00 /tmp
```

The `2` in `2775` is setgid: files created in that directory inherit the directory's group. Useful for maintaining group consistency in team collaboration.

### Applying Least Privilege with ACLs

When basic permission bits are insufficient, use ACLs.

```bash
setfacl -m u:jenkins:rX /opt/my-app/current/conf
setfacl -m u:jenkins:r-- /opt/my-app/current/conf/app.env
getfacl /opt/my-app/current/conf/app.env

# Partial expected output
# user::rw-
# user:jenkins:r--
# group::r--
# mask::r--
# other::---
```

Granting the CI account only the read permission it needs maintains deployment automation while reducing security exposure.

### Permission Change Automation Script Example

```bash
#!/usr/bin/env bash
set -euo pipefail

target="/opt/my-app/releases/prod-20260521"

chown -R deploy:deploy "$target"
find "$target" -type d -exec chmod 755 {} \;
find "$target" -type f -name '*.sh' -exec chmod 750 {} \;
find "$target" -type f ! -name '*.sh' -exec chmod 640 {} \;

# Secrets get stricter permissions
chmod 600 "$target/conf/secrets.env"
```

The purpose of this script is not "setting permissions correctly" but **reproducing the same rules every time**. Reducing manual changes shrinks cross-environment drift and speeds up root-cause analysis.

### Aligning systemd Service Accounts with Permissions

If the user a service runs as does not match file permissions, it fails immediately after start.

```ini
# /etc/systemd/system/my-app.service
[Service]
User=deploy
Group=deploy
WorkingDirectory=/opt/my-app/current
ExecStart=/opt/my-app/current/bin/start.sh
EnvironmentFile=/opt/my-app/current/conf/app.env
```

After configuration, check logs:

```bash
systemctl daemon-reload
systemctl restart my-app
journalctl -u my-app -n 20 --no-pager
```

If `Permission denied` appears, check the permission model before looking at code.

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

### Operations Note: Post-Change Verification

After modifying permissions, files, or environment values, perform system-level verification alongside functional tests.

```bash
whoami
hostname
systemctl is-active my-api
journalctl -u my-api -n 20 --no-pager
```


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

- **How do `r`, `w`, `x` permissions behave differently on files vs directories?**
  - On files: `r` = read content, `w` = modify, `x` = execute. On directories: `r` = list entries, `w` = create/delete inside, `x` = enter (`cd`). Without `x` on a directory, you can't `cd` into it even if `r` shows the listing—so `namei -l` traces per-segment permissions to diagnose access failures.
- **Why does the owner/group/others distinction matter?**
  - `-rwxr-xr--` assigns different permissions to owner, group, and others, enabling policy separation over who can read, modify, or execute. The article set `app.env` to `640` and `start.sh` to `750` to open only what each role (service account vs team user) needs.
- **What does each of `chmod` and `chown` change?**
  - `chmod` changes permission bits (`644`, `755`, `u+x`); `chown` changes the file's owner and group (`deploy:deploy`). The deployment example ran `chown -R deploy:deploy` first, then applied different `chmod` values to directories and `*.sh` files—showing the role difference clearly.

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
