---
title: "Linux CLI 101 (8/10): Environment Variables and PATH"
series: linux-cli-101
episode: 8
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
- Environment Variable
- PATH
- bashrc
- Shell
- Configuration
last_reviewed: '2026-05-15'
seo_description: Environment variables are name tags attached to processes, and PATH
  is the map the Shell uses to find commands.
---

# Linux CLI 101 (8/10): Environment Variables and PATH

Environment variables sit behind a lot of everyday confusion: a command installs successfully but cannot be found, a script sees a variable in your shell but not in Python, or a setting works in one terminal and disappears in the next.

This is post 8 in the Linux CLI 101 series.

## Questions to Keep in Mind

- Viewing and setting environment variables with `echo`, `env`, `export`?
- How PATH drives command lookup?
- Adding permanent settings to `.bashrc` and `.bash_profile`?

## Big Picture

![Linux CLI 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/08/08-01-big-picture.en.png)

*Linux CLI 101 chapter 8 flow overview*

This picture places Environment Variables and PATH inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Environment Variables and PATH is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Why it matters

When you type `python`, the Shell finds and runs the Python executable. How does it find it? Not by searching every directory — it checks only the directories listed in PATH, in order. If the path is not in PATH, you get "command not found".

> You install a package with `pip install` but typing `mycommand` gives "command not found". The package is installed — so why won't it run? Because the installation path is not in PATH.

## Mental Model

> Environment variables are name tags attached to processes, and PATH is the map the Shell uses to find commands.

A delivery driver checks an address book (PATH) in order. Addresses not in the book are never visited. When a new shop opens, you must add it to the book for the driver to find it.

```text
$ python
Shell searches PATH in order:
  /usr/local/bin/python  -> not found
  /usr/bin/python         -> found! -> execute
```

## Core Concepts

| Term | Description | Example |
|---|---|---|
| Environment variable | key=value pair passed to a process | `HOME=/home/user` |
| PATH | List of command search directories (`:` separated) | `/usr/local/bin:/usr/bin:/bin` |
| export | Pass variable to child processes | `export API_KEY=abc123` |
| .bashrc | Runs when an interactive bash shell starts | `~/.bashrc` |
| .bash_profile | Runs when a login shell starts | `~/.bash_profile` |

## Before / After

**Before (not knowing PATH)**

```bash
pip install httpie
http GET https://api.example.com
# bash: http: command not found
# "Why doesn't it work? I just installed it..."
```

**After (understanding PATH)**

```bash
pip install httpie
which http || pip show httpie | grep Location
# Location: /home/user/.local/lib/python3.11/site-packages
# -> check if ~/.local/bin is in PATH
echo $PATH | tr ':' '\n' | grep local
# If /home/user/.local/bin is missing:
export PATH="$HOME/.local/bin:$PATH"
http GET https://api.example.com   # Works
```

## Step-by-step practice

### Step 1. Check environment variables

```bash
echo $HOME                    # Home directory
echo $USER                    # Current user
echo $SHELL                   # Current shell
echo $PATH                    # Command search paths

env                           # Print all environment variables
env | grep -i python          # Python-related variables only
```

### Step 2. Variable assignment and export

```bash
MY_VAR="hello"                # Shell variable (not passed to children)
echo $MY_VAR                  # hello

bash -c 'echo $MY_VAR'       # (empty) — not available in child process

export MY_VAR                 # export passes it to children
bash -c 'echo $MY_VAR'       # hello

export DB_HOST="localhost"    # Declare and export at once
```

### Step 3. Modify PATH

```bash
echo $PATH | tr ':' '\n'     # View PATH one entry per line

# Temporary addition (current session only)
export PATH="$HOME/mytools:$PATH"

# Check command location
which python
which ls
```

### Step 4. Add permanent settings to .bashrc

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
echo 'export EDITOR=vim' >> ~/.bashrc

source ~/.bashrc             # Apply immediately (or open a new terminal)
echo $EDITOR
# vim
```

### Step 5. The .env file pattern

```bash
cat > ~/practice/linux-cli/.env << 'EOF'
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
API_KEY=secret-key-123
EOF

# Load .env file in Shell
set -a                        # Auto-export subsequent variables
source ~/practice/linux-cli/.env
set +a
echo $DB_HOST                 # localhost
```

## What to notice in this code

- Variables set without `export` are only valid in the current Shell and are not passed to child processes
- PATH uses `:` as a delimiter, and directories on the left take priority
- `source ~/.bashrc` runs the file in the current Shell. `.` is a synonym
- `.env` files must never be committed to Git (they contain sensitive data like API keys)

## Common mistakes

### Mistake 1. Overwriting PATH

```bash
export PATH="/my/new/path"              # Entire existing PATH is gone!
export PATH="/my/new/path:$PATH"        # Appends to existing PATH — safe
```

### Mistake 2. Confusing .bashrc and .bash_profile

Login shells (SSH connections) read `.bash_profile`; non-login interactive shells (terminal apps) read `.bashrc`. The common practice is to source `.bashrc` from `.bash_profile` for consistency.

### Mistake 3. Omitting braces in variable references

```bash
echo "$HOME_backup"           # Looks for a variable named HOME_backup
echo "${HOME}_backup"         # HOME variable + "_backup" string
```

### Mistake 4. Committing .env files to Git

If a `.env` file with API keys and passwords lands in a public repository, it is a security incident. Always add `.env` to `.gitignore`.

### Mistake 5. Forgetting export and wondering why "the variable doesn't work"

To read `os.environ["MY_VAR"]` in a Python script, the Shell must `export` the variable. `MY_VAR=hello` alone is invisible to the child process Python.

## Practical applications

- **12-Factor App**: Manage configuration through environment variables (DB credentials, API keys)
- **Virtual environment activation**: `source venv/bin/activate` prepends venv's bin/ to PATH
- **CI/CD variables**: `env:` in GitHub Actions sets environment variables
- **Docker**: `docker run -e DB_HOST=db` passes environment variables to a container
- **Debugging**: `env | sort` dumps the current environment for diagnosis

## How practitioners think about this

Environment variables are the standard method for managing "configuration outside of code". When running the same code across dev/staging/production, you change only the `DB_HOST` variable instead of the code. This is the core of the 12-Factor App methodology and the default way to inject configuration in Docker and Kubernetes.

On the other hand, too many environment variables become hard to manage. At that point, you move to per-environment `.env` files or secrets management tools like AWS Parameter Store and HashiCorp Vault. But the starting point for all of this is understanding `export` and `$PATH`.

## Checklist

- [ ] You can read the output of `echo $PATH` and explain the command search order
- [ ] You know the difference between `export` and plain variable assignment
- [ ] You can permanently add PATH entries to `.bashrc`
- [ ] You can create a `.env` file and load it with `source`
- [ ] You know why `.env` files should be added to `.gitignore`

## Exercises

1. Run `echo $PATH | tr ':' '\n' | nl` to see the PATH search order with numbering.
2. Set `MY_SECRET=hello` and `export MY_SECRET=hello` separately, then run `bash -c 'echo $MY_SECRET'` after each to observe the difference.
3. Add `alias ll='ls -la'` to `.bashrc`, run `source ~/.bashrc`, and verify that `ll` works.

## Summary and next

- Environment variables are key=value settings passed to processes, inherited by children via `export`.
- PATH is the list of directories the Shell searches for commands — `:` delimited, left-to-right priority.
- Adding settings to `.bashrc` applies them automatically to every new Shell.
- `.env` files are useful for application configuration but must never be committed to Git.
- Without `export`, child processes (Python, Docker, etc.) cannot see the variable.

The next post covers **shell scripting basics** — writing scripts to automate repetitive tasks.

## Answering the Opening Questions

- **Viewing and setting environment variables with `echo`, `env`, `export`?**
  - The article treats Environment Variables and PATH as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How PATH drives command lookup?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Adding permanent settings to `.bashrc` and `.bash_profile`?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Linux CLI 101 (1/10): What Is the CLI and Shell?](./01-what-is-cli-and-shell.md)
- [Linux CLI 101 (2/10): Files and Directories](./02-files-and-directories.md)
- [Linux CLI 101 (3/10): Permissions and Ownership](./03-permissions-and-ownership.md)
- [Linux CLI 101 (4/10): cat, less, head, tail — Viewing File Contents](./04-viewing-files.md)
- [Linux CLI 101 (5/10): grep, find, xargs — The Search Trio](./05-grep-find-xargs.md)
- [Linux CLI 101 (6/10): Pipes and Redirection](./06-pipe-and-redirection.md)
- [Linux CLI 101 (7/10): Process Management](./07-process-management.md)
- **Environment Variables and PATH (current)**
- Shell Script Basics (upcoming)
- SSH and Remote Access (upcoming)

<!-- toc:end -->

## References

- [GNU Bash Manual - Shell Variables](https://www.gnu.org/software/bash/manual/html_node/Shell-Variables.html)
- [The Twelve-Factor App - Config](https://12factor.net/config)
- [Linux man page - environ](https://man7.org/linux/man-pages/man7/environ.7.html)
- [dotenv pattern - Best practices](https://github.com/motdotla/dotenv)

Tags: Linux, Environment Variable, PATH, bashrc, Shell, Configuration
