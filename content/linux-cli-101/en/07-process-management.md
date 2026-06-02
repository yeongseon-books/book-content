---
title: "Linux CLI 101 (7/10): Process Management"
series: linux-cli-101
episode: 7
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
- Process
- ps
- kill
- Background
- CLI
last_reviewed: '2026-05-15'
seo_description: A process is a running instance of a program, each with a unique
  PID, acting as an independent worker.
---

# Linux CLI 101 (7/10): Process Management

Process problems show up in very practical ways: a port is already in use, CPU spikes to 100 percent, or a long-running job dies the moment your SSH session closes. If you cannot inspect and control processes, those problems stay mysterious longer than they should.

This is the 7th post in the Linux CLI 101 series.


![Linux CLI 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/07/07-01-mental-model.en.png)
*Linux CLI 101 chapter 7 flow overview*

## Questions to Keep in Mind

- Checking running processes with `ps` and `top`?
- Terminating processes with `kill` and `kill -9`?
- Switching between background and foreground with `&`, `bg`, `fg`, `jobs`?

## Why it matters

When a web server is consuming 100% CPU, a Python script is stuck in an infinite loop, or a port is already occupied by another process — you need to know how to check and manage processes to resolve any of these.

> You run your Flask dev server and get "Address already in use". A previous server process was never stopped and is still holding port 5000. You need to find and terminate that process.

## Mental Model

> A program is a recipe (code file), and a process is a cook actually cooking with that recipe (running instance). Just as 3 cooks can cook the same recipe simultaneously, 3 processes can run from the same program at the same time.

```text
Program (python)  ->  Process 1 (PID 1234)  <- check with ps
                 ->  Process 2 (PID 5678)  <- terminate with kill
                 ->  Process 3 (PID 9012)  <- keep with nohup
```

## Core Concepts

| Term | Meaning | Command |
|---|---|---|
| PID | Process ID, unique identifier | `echo $$` (current shell PID) |
| Foreground | Process that occupies the terminal | Default execution mode |
| Background | Process that does not occupy the terminal | `command &` |
| SIGTERM (15) | Graceful termination request | `kill PID` |
| SIGKILL (9) | Forced termination | `kill -9 PID` |

## Before / After

**Before (not knowing process management)**

```text
"The server is stuck and I don't know what's wrong"
-> Close and reopen the terminal
-> Previous process remains as a zombie, causing port conflicts
```

**After (understanding processes)**

```bash
lsof -i :5000                    # Find process holding port 5000
kill $(lsof -t -i :5000)         # Terminate it
python app.py                     # Start normally
```

## Step-by-step practice

### Step 1. Check processes

```bash
ps aux                           # All processes in detail
ps aux | grep python             # Only python-related processes
ps -ef --forest                  # Parent-child tree view
```

### Step 2. Real-time monitoring with top

```bash
top
# Controls:
# q: quit
# M: sort by memory
# P: sort by CPU
# k: kill process (enter PID)
```

### Step 3. Terminate a process

```bash
# Create a practice process
sleep 300 &
# [1] 12345

ps aux | grep sleep
# user  12345  ... sleep 300

kill 12345                       # SIGTERM: graceful termination request
# If it doesn't stop:
kill -9 12345                    # SIGKILL: forced termination
```

### Step 4. Background execution

```bash
sleep 100 &                      # Run in background
# [1] 23456
jobs                             # List background jobs
# [1]+  Running    sleep 100 &

fg %1                            # Bring to foreground
# Ctrl+Z to suspend
bg %1                            # Send back to background
```

### Step 5. Keep processes alive with nohup

```bash
nohup python long_task.py > task.log 2>&1 &
# [1] 34567
# Process continues even after SSH disconnection
# Output saved to task.log
```

## What to notice in this code

- In `ps aux`, `a`=all users, `u`=detailed info, `x`=include processes without a terminal
- `kill` sends SIGTERM (15) by default, giving the program a chance to clean up
- `kill -9` has the kernel kill the process directly — immediate termination with no cleanup
- `nohup` makes the process ignore the HUP (hangup) signal, surviving terminal closure

## Common mistakes

### Mistake 1. Reaching for kill -9 first

`kill -9` does not give the process a chance to close files or save temporary data. Always try `kill` (SIGTERM) first, wait 5-10 seconds, and only use `kill -9` if it still does not stop.

### Mistake 2. Killing the wrong PID

```bash
ps aux | grep python
# Multiple lines appear — verify which is your process
# The last line "grep python" is grep itself — ignore it
```

Use `pgrep -f "python app.py"` to find the exact PID.

### Mistake 3. Not knowing processes die when SSH disconnects

When an SSH session ends, all foreground processes launched in that session are terminated. For long-running tasks, always use `nohup` or `tmux`/`screen`.

### Mistake 4. Ignoring zombie processes

Processes in `Z` (zombie) state in `ps` have already terminated but their parent has not collected the exit status. A few are harmless, but too many can exhaust PIDs.

### Mistake 5. Rebooting to fix port conflicts

Rebooting a server because a port is occupied is an overreaction. Use `lsof -i :PORT` to find the occupying process and terminate it.

## Practical applications

- **Port conflict resolution**: `lsof -i :8080 | grep LISTEN` finds the occupying process
- **Memory leak monitoring**: Periodically check the RSS (memory) column in `top`
- **Batch job execution**: `nohup python etl.py > etl.log 2>&1 &` for long-running tasks
- **Dev server management**: `Ctrl+C` to stop; if that fails, use `kill`
- **Docker debugging**: `ps aux` inside a container to check running services

## How practitioners think about this

Process management is not just "run it and forget" — it includes "how to manage it after running". In production, process managers like `systemd`, `supervisor`, and `pm2` handle auto-restart on crash, log management, and resource limits.

Even during development, process awareness matters. Building the habit of asking "Will the server die if I close this terminal?" and "Is something still running in the background?" prevents production incidents down the road.

## When it breaks, check these first

- If a port conflict appears, do not reboot first. Run `lsof -i :PORT` and confirm which command is holding the port so you can tell whether it is your dev server, another service, or a stale background job.
- If `kill PID` does nothing, re-check the state with `ps -p PID -o pid,stat,cmd`. States like `D` or zombie cleanup issues behave differently from a normal running process.
- If `ps aux | grep python` gives too many lines, use `pgrep -af "python app.py"` or `ps -ef --forest` to narrow the search. Misidentifying the PID is more common than the process itself being weird.
- If jobs die after SSH disconnects, assume they were launched in the foreground until proven otherwise. For anything long-running, make `nohup`, `tmux`, or a process manager part of the default plan.

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

## Practical Scenario: Process Management and Service Recovery Procedures

Process management does not end at knowing the `kill` command. In practice, you must first understand "which process is consuming resources and why," then connect to a safe recovery procedure.

### Basic Status Check Routine

```bash
ps -eo pid,ppid,user,%cpu,%mem,etime,cmd --sort=-%cpu | head -n 15

# Partial expected output
#   PID  PPID USER   %CPU %MEM     ELAPSED CMD
# 18231     1 deploy 92.3 12.1     00:43:21 /usr/bin/python3 /opt/my-api/app.py
```

Viewing the top CPU/memory processes first lets you quickly form a bottleneck hypothesis.

### Precise Query for a Specific Process

```bash
pgrep -af 'my-api|gunicorn|uvicorn'

# Expected output
# 18231 /usr/bin/python3 /opt/my-api/app.py
# 18242 /usr/bin/python3 /opt/my-api/worker.py
```

`pgrep -af` shows PID and the full command line together, making it easy to distinguish similarly-named processes.

### Signal-Based Termination Strategy

```bash
# 1) Request graceful termination
kill -TERM 18231

# 2) Wait, then force kill
sleep 5
kill -KILL 18231
```

The production default is `TERM`. Using `KILL` immediately skips cleanup work (file flush, connection closure), which can cause data inconsistencies.

### Priority Adjustment (nice/renice)

```bash
nice -n 10 /opt/my-api/bin/heavy-batch.sh
renice -n 5 -p 18242
```

A common strategy: lower batch job priority to protect API responsiveness.

### Background Jobs and Session Detachment

```bash
nohup /opt/my-api/bin/report.sh > /tmp/report.out 2>&1 &
disown
jobs -l
```

Useful when a job must survive session disconnection. For long-term tasks, promoting to a systemd service/timer is more reliable.

### systemd-Centric Operations Pattern

```bash
systemctl status my-api --no-pager
systemctl restart my-api
systemctl is-failed my-api && journalctl -u my-api -n 80 --no-pager
```

Managing via systemd units rather than running processes directly gives consistent restart policies and log collection.

```ini
# /etc/systemd/system/my-api.service
[Unit]
Description=My API Service
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/opt/my-api/current
ExecStart=/opt/my-api/current/bin/start.sh
Restart=on-failure
RestartSec=2
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

### Regex Filter for Detecting Process Leaks

```bash
ps -ef \
  | grep -E 'python3 .*my-api|gunicorn .*my-api' \
  | grep -v grep
```

Useful for checking whether previous-version processes remain after deployment.

### Recovery Automation Bash Script

```bash
#!/usr/bin/env bash
set -euo pipefail

svc="my-api"

if ! systemctl is-active --quiet "$svc"; then
  echo "[WARN] $svc inactive, restarting"
  systemctl restart "$svc"
  sleep 2
fi

systemctl status "$svc" --no-pager | sed -n '1,12p'
journalctl -u "$svc" -n 40 --no-pager | grep -E 'ERROR|CRITICAL|Failed' || true
```

The key is performing "automatic recovery + evidence output" together. Restarting alone makes recurrence analysis difficult.

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

- [ ] You can check all system processes with `ps aux`
- [ ] You can explain the difference between `kill` and `kill -9`
- [ ] You can run commands in the background with `&` and switch with `fg`/`bg`
- [ ] You can keep processes alive after SSH disconnection with `nohup`
- [ ] You can find processes holding a port with `lsof -i :PORT`

## Exercises

1. Create 3 background processes with `sleep 600 &`, check them with `jobs`, bring one to the foreground with `fg`, and stop it with `Ctrl+C`.
2. Run `ps aux | head -1` to see the column header, then explain the meaning of the PID, CPU%, MEM%, and COMMAND columns.
3. Run `lsof -i :22` to find the PID of the SSH daemon.

## Summary and next

- A process is a running instance of a program with a unique PID.
- Check process status with `ps` and `top`; terminate with `kill`.
- Always follow the order: `kill` (SIGTERM) -> wait -> `kill -9` (SIGKILL).
- Switch between background and foreground with `&`, `bg`, `fg`.
- Use `nohup` or `tmux` to keep processes alive after SSH disconnection.

The next post covers **environment variables and PATH** — how the Shell finds commands and manages configuration.

## Answering the Opening Questions

- **What distinguishes a process from a program?**
  - A program is code or an executable on disk; a process is a running instance of it in memory. The same Python app can exist as multiple processes with different PIDs, as `pgrep -af 'my-api|gunicorn|uvicorn'` reveals.
- **In what order should you use `ps`, `top`, `pgrep`, `kill`?**
  - First survey top resource consumers with `ps -eo ... --sort=-%cpu` or `top`; then pinpoint the exact process with `pgrep -af`; finally attempt graceful shutdown with `kill -TERM`. If it persists, wait briefly then escalate to `kill -KILL`.
- **Why are background jobs and job control frequently needed in server operations?**
  - Long-running batches and maintenance scripts must survive SSH disconnects. Mastering `sleep 100 &`, `jobs`, `fg`, `bg`, plus the `nohup ... > task.log 2>&1 &` and `disown` patterns lets you decouple work from the session for stable operations.

<!-- toc:begin -->
## In this series

- [Linux CLI 101 (1/10): What Is the CLI and Shell?](./01-what-is-cli-and-shell.md)
- [Linux CLI 101 (2/10): Files and Directories](./02-files-and-directories.md)
- [Linux CLI 101 (3/10): Permissions and Ownership](./03-permissions-and-ownership.md)
- [Linux CLI 101 (4/10): cat, less, head, tail — Viewing File Contents](./04-viewing-files.md)
- [Linux CLI 101 (5/10): grep, find, xargs — The Search Trio](./05-grep-find-xargs.md)
- [Linux CLI 101 (6/10): Pipes and Redirection](./06-pipe-and-redirection.md)
- **Process Management (current)**
- Environment Variables and PATH (upcoming)
- Shell Script Basics (upcoming)
- SSH and Remote Access (upcoming)

<!-- toc:end -->

## References

- [Linux man page - ps](https://man7.org/linux/man-pages/man1/ps.1.html)
- [Linux man page - kill, signal](https://man7.org/linux/man-pages/man1/kill.1.html)
- [The Missing Semester - Job Control](https://missing.csail.mit.edu/2020/command-line/)
- [systemd for Developers](https://www.freedesktop.org/software/systemd/man/systemd.html)

Tags: Linux, Process, ps, kill, Background, CLI
