---
title: "Linux CLI 101 (10/10): SSH and Remote Access"
series: linux-cli-101
episode: 10
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
- SSH
- Remote
- scp
- Security
- Server
last_reviewed: '2026-05-15'
seo_description: SSH opens a remote terminal over an encrypted channel, and key-based
  authentication replaces passwords with a lock-and-key pair.
---

# Linux CLI 101 (10/10): SSH and Remote Access

The CLI becomes truly operational the moment you leave your own machine. Deploying code, checking logs on a server, copying build artifacts, and tunneling to a remote database all start with secure remote access.

This is the final post in the Linux CLI 101 series.


![Linux CLI 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/10/10-01-big-picture.en.png)
*Linux CLI 101 chapter 10 flow overview*

## Questions to Keep in Mind

- The basic SSH connection flow and key-based authentication setup?
- Generating a key pair with `ssh-keygen` and registering it on a server?
- Creating connection aliases with `~/.ssh/config`?

## Why it matters

Deploying code to a server, checking server logs, and connecting to a database all start with remote access. SSH is the foundation of every remote operation.

> You create an AWS EC2 instance and receive a public IP address. How do you connect and deploy your code? You cannot open a server terminal from a web browser.

One line — `ssh user@ip-address` — and the server's terminal appears on your screen.

## Mental Model

> SSH creates an encrypted tunnel between two computers. Key-based authentication uses a lock (public key) and a key (private key) instead of a password. You install the lock on the server and open it with the key on your computer — no password required.

```text
[My Computer]                       [Server]
 Private key (~/.ssh/id_ed25519) <-> Public key (~/.ssh/authorized_keys)
          |                              |
    "Open with this key"          "Lock matches — access granted"
          └──── Encrypted SSH tunnel ────┘
```

## Core Concepts

| Term | Description | Location |
|---|---|---|
| Public key | The lock you register on the server | `~/.ssh/id_ed25519.pub` |
| Private key | The key you keep on your computer | `~/.ssh/id_ed25519` |
| authorized_keys | List of public keys the server accepts | `~/.ssh/authorized_keys` |
| ssh-agent | Caches private keys in memory to avoid repeated passphrase entry | Process |
| known_hosts | Records server fingerprints of previously visited hosts | `~/.ssh/known_hosts` |

## Before / After

**Before (password authentication)**

```bash
ssh user@192.168.1.100
# Type password every time
# Vulnerable to brute-force attacks
# Cannot automate (putting passwords in scripts is a security incident)
```

**After (key-based authentication + config)**

```bash
ssh prod-server
# Instant login without a password
# Automatable (CI/CD deploys over SSH)
# Brute-force impossible
```

## Step-by-step practice

### Step 1. Generate an SSH key pair

```bash
ssh-keygen -t ed25519 -C "user@example.com"
# Enter file: (press Enter for default path)
# Enter passphrase: (recommended for security)

ls -la ~/.ssh/
# id_ed25519        <- Private key (never share)
# id_ed25519.pub    <- Public key (register on server)
```

### Step 2. Register the public key on a server

```bash
# Method 1: ssh-copy-id (easiest)
ssh-copy-id user@192.168.1.100

# Method 2: manual copy
cat ~/.ssh/id_ed25519.pub | ssh user@192.168.1.100 \
    'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys'

# Now you can connect without a password
ssh user@192.168.1.100
```

### Step 3. Configure SSH aliases

```bash
cat > ~/.ssh/config << 'EOF'
Host dev-server
    HostName 192.168.1.100
    User developer
    Port 22
    IdentityFile ~/.ssh/id_ed25519

Host prod-server
    HostName 10.0.1.50
    User deploy
    Port 2222
    IdentityFile ~/.ssh/id_ed25519
EOF

chmod 600 ~/.ssh/config

# Connect using aliases
ssh dev-server          # = ssh developer@192.168.1.100
ssh prod-server         # = ssh deploy@10.0.1.50 -p 2222
```

### Step 4. Transfer files (scp, rsync)

```bash
# scp: copy single files or directories
scp app.tar.gz dev-server:/opt/releases/          # Upload
scp dev-server:/var/log/app.log ./                 # Download
scp -r project/ dev-server:/home/developer/        # Copy directory

# rsync: incremental sync (transfers only changes)
rsync -avz project/ dev-server:/home/developer/project/
# -a: archive (preserves permissions, timestamps)
# -v: verbose
# -z: compressed transfer
```

### Step 5. Execute remote commands

```bash
# Run a command remotely without opening a session
ssh dev-server 'df -h'                        # Check disk usage
ssh dev-server 'tail -5 /var/log/app.log'     # Last 5 log lines

# Run multiple commands
ssh dev-server << 'EOF'
cd /opt/app
git pull
sudo systemctl restart app
echo "Deploy done"
EOF
```

## What to notice in this code

- `ssh-keygen -t ed25519` uses the ed25519 algorithm, currently recommended over RSA — shorter keys and faster operations
- Permissions on `~/.ssh/` and key files matter: if they are too loose, SSH refuses to use the key
- `rsync` transfers only the changed parts, making it far more efficient than `scp` for large directory syncs
- In SSH config, `Host` is an alias; `HostName` is the actual address

## Common mistakes

### Mistake 1. Sharing or committing the private key

The private key (`id_ed25519`) must never be sent to anyone or committed to Git. The only key you share is the public key (`.pub`).

### Mistake 2. Loose permissions on SSH key files

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
chmod 600 ~/.ssh/config
# Looser permissions cause SSH to reject the key
```

### Mistake 3. Ignoring the known_hosts warning

When you see "WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED", the server may have been reinstalled or it could be a man-in-the-middle attack. Verify the server, then run `ssh-keygen -R hostname` to remove the old fingerprint.

### Mistake 4. Not disabling password authentication

Even after setting up key-based authentication, leaving password authentication enabled exposes the server to brute-force attacks. Set `PasswordAuthentication no` in `/etc/ssh/sshd_config`.

### Mistake 5. Not using SSH config

Typing `ssh -i ~/.ssh/mykey -p 2222 user@long-hostname.example.com` every time is inefficient and error-prone. Create an alias in config.

## Practical applications

- **Server deploys**: `ssh prod 'cd /opt/app && git pull && sudo systemctl restart app'`
- **CI/CD**: GitHub Actions deploys to servers using SSH keys
- **Port forwarding**: `ssh -L 5432:localhost:5432 db-server` accesses a remote DB as if it were local
- **File sync**: `rsync -avz dist/ prod:/var/www/html/` deploys a web frontend
- **Jump hosts**: `ssh -J bastion internal-server` reaches servers behind firewalls

## How practitioners think about this

SSH is fundamental to server management, but the fewer times you SSH into a server manually, the more mature your infrastructure is. Good teams deploy through CI/CD pipelines, view logs through monitoring tools, and manage servers with Infrastructure as Code.

That said, you still need to know SSH. When CI/CD fails, when monitoring misses a problem, the last resort is always "SSH in and check directly". SSH is the skill you rarely use day-to-day but absolutely must have for emergencies.

## When it breaks, check these first

- If you get `Permission denied (publickey)`, check key paths and permissions before blaming the network. `chmod 700 ~/.ssh`, `chmod 600 ~/.ssh/id_ed25519`, and `ssh -v host` usually surface the real cause.
- If you see `REMOTE HOST IDENTIFICATION HAS CHANGED`, do not blindly delete the warning. First verify whether the server was rebuilt or replaced, then remove the old fingerprint with `ssh-keygen -R host`.
- If `scp` or `rsync` fails, confirm the SSH user and port first. Many production hosts do not use port 22, and that often gets mistaken for a bad remote path.
- If a remote command only half-runs, check whether shell init files or a `sudo` prompt interrupted non-interactive execution. In automation, break the flow into smaller remote steps until the failure point is obvious.

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

## Practical Scenario: SSH Operations Standards and Automation Integration

If you understand SSH only as a "remote connection command," operations automation and security policy become disconnected. In practice, SSH must be viewed together as authentication, access control, file transfer, remote execution, and an auditable record system.

### Pre-Connection Basic Checks

```bash
ssh -V
ls -ld ~/.ssh
ls -l ~/.ssh

# Partial expected output
# OpenSSH_9.6p1, OpenSSL 3.0.13
# drwx------ 2 user user 4096 May 21 12:01 /home/user/.ssh
# -rw------- 1 user user  411 May 21 12:01 id_ed25519
```

If permissions are loose, SSH refuses to use the key. Check file permissions before blaming the network for connection problems.

### Connection Debugging: Using Verbose Logs

```bash
ssh -v prod-server

# Points to check in output
# debug1: Offering public key: /home/user/.ssh/id_ed25519
# debug1: Server accepts key: /home/user/.ssh/id_ed25519
# debug1: Authentication succeeded (publickey).
```

The fastest diagnostic method for `Permission denied (publickey)` situations.

### Use ~/.ssh/config Like a Policy Document

```sshconfig
Host prod-server
    HostName 10.0.1.50
    User deploy
    Port 2222
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 3

Host bastion
    HostName 203.0.113.10
    User jump

Host internal-api
    HostName 10.10.2.15
    User deploy
    ProxyJump bastion
```

The config file goes beyond convenience — it serves as a document standardizing the team's connection methods.

### Remote Commands and Pipe Chains

```bash
ssh prod-server "journalctl -u my-api --since '10 min ago' --no-pager" \
  | grep -E 'ERROR|CRITICAL|timeout|5[0-9]{2}' \
  | tee /tmp/prod-api-errors.txt
```

Remote output can be combined with local pipelines, making it easy to build centralized analysis scripts.

### File Synchronization Strategy: scp vs rsync

```bash
# Single file transfer
scp dist/app.tar.gz prod-server:/opt/releases/

# Sync only changes
rsync -avz --delete dist/ prod-server:/opt/my-api/current/
```

`--delete` cleans up unnecessary files on the remote to keep state aligned, but running it from the wrong path causes major accidents. Verify with dry-run (`--dry-run`) first.

### Access Internal Services via SSH Tunnels

```bash
# Forward remote DB to local port 5432
ssh -L 5432:127.0.0.1:5432 prod-server

# Connect from another terminal
psql -h 127.0.0.1 -p 5432 -U appuser appdb
```

Safely inspect production databases without exposing them directly.

### Server-Side sshd Configuration Essentials

```text
# /etc/ssh/sshd_config key examples
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin no
AllowUsers deploy ops
```

After changing configuration, a service restart and log check are mandatory.

```bash
sudo systemctl restart sshd
sudo systemctl status sshd --no-pager
sudo journalctl -u sshd -n 40 --no-pager
```

### Remote Operations Script Example

```bash
#!/usr/bin/env bash
set -euo pipefail

host="prod-server"
svc="my-api"

ssh "$host" "systemctl is-active --quiet $svc"
ssh "$host" "systemctl status $svc --no-pager | sed -n '1,10p'"
ssh "$host" "journalctl -u $svc -n 50 --no-pager | grep -E 'ERROR|CRITICAL|Failed' || true"
```

This approach reduces the time spent manually SSH-ing in for checks and standardizes inspection result formats.

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

## Checklist

- [ ] You can generate an SSH key pair and register the public key on a server
- [ ] You can create aliases in `~/.ssh/config` to simplify connections
- [ ] You can upload and download files with `scp`
- [ ] You can incrementally sync directories with `rsync`
- [ ] You know the correct permissions (600, 700) for SSH key files

## Exercises

1. Generate a key pair with `ssh-keygen -t ed25519` and inspect the contents of the public key (`~/.ssh/id_ed25519.pub`).
2. Write a sample `~/.ssh/config` entry for a hypothetical server (you do not need to actually connect). Include all five fields: `Host`, `HostName`, `User`, `Port`, `IdentityFile`.
3. Write an `scp` command that copies a local file to `/tmp/` using localhost as the remote host.

## Summary and next

- SSH is an encrypted remote access protocol; key-based authentication is more secure than passwords.
- `ssh-keygen` creates keys; `ssh-copy-id` registers the public key on a server.
- `~/.ssh/config` manages connection details with aliases, boosting productivity.
- `scp` handles one-off copies; `rsync` handles incremental syncs.
- Proper key file permissions and disabling password authentication are security essentials.

This concludes the Linux CLI 101 series. You now have the CLI fundamentals to connect to servers, analyze logs, and automate deployments with confidence.

## Answering the Opening Questions

- **Why did SSH replace Telnet as the default remote-access method?**
  - SSH encrypts remote commands and file transfers inside a tunnel, making it far safer than Telnet's plaintext traffic. Server deployments, quick checks like `ssh prod-server 'df -h'`, and file transfers via `scp`/`rsync` all share the same secure channel—establishing it as the operational baseline.
- **What difference does key-based vs password authentication make?**
  - Password auth requires manual input each time and resists automation; key-based auth (`ssh-keygen -t ed25519` → `authorized_keys`) connects securely without a password. When `Permission denied (publickey)` appears, check `chmod 700 ~/.ssh`, `chmod 600 ~/.ssh/id_ed25519`, and `ssh -v prod-server` first.
- **How does `~/.ssh/config` simplify connection workflows?**
  - Pre-filling `Host`, `HostName`, `User`, `Port`, `IdentityFile` lets you type `ssh prod-server` instead of memorizing long connection strings. The article's `ProxyJump bastion` and `ServerAliveInterval 30` examples showed how team access policies and jump-host routes can be standardized in one config file.

<!-- toc:begin -->
## In this series

- [Linux CLI 101 (1/10): What Is the CLI and Shell?](./01-what-is-cli-and-shell.md)
- [Linux CLI 101 (2/10): Files and Directories](./02-files-and-directories.md)
- [Linux CLI 101 (3/10): Permissions and Ownership](./03-permissions-and-ownership.md)
- [Linux CLI 101 (4/10): cat, less, head, tail — Viewing File Contents](./04-viewing-files.md)
- [Linux CLI 101 (5/10): grep, find, xargs — The Search Trio](./05-grep-find-xargs.md)
- [Linux CLI 101 (6/10): Pipes and Redirection](./06-pipe-and-redirection.md)
- [Linux CLI 101 (7/10): Process Management](./07-process-management.md)
- [Linux CLI 101 (8/10): Environment Variables and PATH](./08-environment-variables.md)
- [Linux CLI 101 (9/10): Shell Script Basics](./09-shell-script-basics.md)
- **SSH and Remote Access (current)**

<!-- toc:end -->

## References

- [OpenSSH Manual Pages](https://www.openssh.com/manual.html)
- [SSH Academy - SSH Key Management](https://www.ssh.com/academy/ssh/keygen)
- [GitHub - Connecting with SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [rsync man page](https://man7.org/linux/man-pages/man1/rsync.1.html)

Tags: Linux, SSH, Remote, scp, Security, Server
