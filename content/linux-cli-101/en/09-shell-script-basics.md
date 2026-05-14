---
title: Shell Script Basics
series: linux-cli-101
episode: 9
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
- Shell Script
- Bash
- Automation
- Scripting
- CLI
last_reviewed: '2026-05-04'
seo_description: A shell script is a recipe file of CLI commands. Write it once, and
  it runs repetitive tasks automatically every time.
---

# Shell Script Basics

> Linux CLI 101 series (9/10)

---

<!-- a-grade-intro:begin -->

## Key Questions

- What is a shell script and why use it instead of Python?
- Why is the shebang (`#!/bin/bash`) required?
- What is the basic syntax for variables, conditionals, and loops?
- How do you pass arguments and check exit codes?

> A shell script is a recipe file of CLI commands. Write it once, and it runs repetitive tasks automatically every time.

<!-- a-grade-intro:end -->

This is post 9 in the Linux CLI 101 series.

## What you will learn

- The basic flow of writing and running a shell script
- Bash syntax for variables, `if/else`, and `for` loops
- Script arguments (`$1`, `$2`, `$#`) and exit codes (`$?`)
- Common script patterns used in real-world workflows

## Why it matters

If you log into a server every morning and run the same five commands, you can write those five lines in a file and run them all at once. That is a shell script.

> Every time you deploy, you run five manual steps: run tests, build, back up the old version, copy the new version, restart the service. You skip one step and cause an outage.

Turn it into a script and steps can never be skipped. Anyone who runs it gets the same result.

## Mental Model

> A shell script is a recipe file of CLI commands. A chef who cooks from memory makes mistakes, but a written recipe lets anyone produce the same dish every time.

```text
Manual execution              Shell script
─────────────                 ──────────────
$ git pull                    #!/bin/bash
$ python -m pytest            git pull
$ docker build -t app .       python -m pytest
$ docker push app             docker build -t app .
                              docker push app
→ Type 4 lines every time     → ./deploy.sh once
```

## Core Concepts

| Term | Description | Example |
|---|---|---|
| shebang | Specifies the interpreter for the script | `#!/bin/bash` |
| `$1`, `$2` | Positional arguments passed to the script | `./script.sh hello` → `$1`=hello |
| `$#` | Number of arguments | 2 args → `$#`=2 |
| `$?` | Exit code of the last command | 0=success, non-zero=failure |
| `set -e` | Abort immediately on error | Recommended at the top of every script |

## Before / After

**Before (manual deploy)**

```text
1. SSH in
2. cd /opt/app
3. git pull
4. pip install -r requirements.txt
5. sudo systemctl restart app
# → Skipped step 3, old version keeps running
```

**After (scripted deploy)**

```bash
#!/bin/bash
set -e
cd /opt/app
git pull
pip install -r requirements.txt
sudo systemctl restart app
echo "Deploy complete at $(date)"
```

## Step-by-step practice

### Step 1. Create your first script

```bash
cd ~/practice/linux-cli
cat > hello.sh << 'EOF'
#!/bin/bash
echo "Hello, $(whoami)!"
echo "Today is $(date +%Y-%m-%d)"
echo "Current directory: $(pwd)"
EOF

chmod u+x hello.sh
./hello.sh
# Hello, user!
# Today is 2026-05-04
# Current directory: /home/user/practice/linux-cli
```

### Step 2. Variables and arguments

```bash
cat > greet.sh << 'EOF'
#!/bin/bash
NAME=${1:-"World"}          # First argument, default "World"
COUNT=${2:-1}               # Second argument, default 1

echo "Arguments count: $#"
for i in $(seq 1 "$COUNT"); do
    echo "[$i] Hello, $NAME!"
done
EOF

chmod u+x greet.sh
./greet.sh                  # Hello, World! (1 time)
./greet.sh Alice 3          # Hello, Alice! (3 times)
```

### Step 3. Conditionals

```bash
cat > check-file.sh << 'EOF'
#!/bin/bash
set -e

FILE=${1:?"Usage: $0 <filename>"}

if [ -f "$FILE" ]; then
    echo "File exists: $FILE"
    echo "Size: $(wc -c < "$FILE") bytes"
    echo "Lines: $(wc -l < "$FILE")"
elif [ -d "$FILE" ]; then
    echo "Directory exists: $FILE"
    echo "Contents: $(ls "$FILE" | wc -l) items"
else
    echo "Not found: $FILE"
    exit 1
fi
EOF

chmod u+x check-file.sh
./check-file.sh hello.sh         # File exists: hello.sh
./check-file.sh /tmp              # Directory exists: /tmp
./check-file.sh nonexistent       # Not found: nonexistent
```

### Step 4. Loops

```bash
cat > backup.sh << 'EOF'
#!/bin/bash
set -e

BACKUP_DIR="/tmp/backup-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

for file in *.sh; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
        echo "Backed up: $file"
    fi
done

echo "All scripts backed up to $BACKUP_DIR"
ls "$BACKUP_DIR"
EOF

chmod u+x backup.sh
./backup.sh
# Backed up: hello.sh
# Backed up: greet.sh
# ...
```

### Step 5. Exit codes in action

```bash
cat > deploy-check.sh << 'EOF'
#!/bin/bash
set -e

echo "Running tests..."
python -m pytest tests/ 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Tests passed. Proceeding with deploy."
else
    echo "Tests failed. Aborting deploy."
    exit 1
fi

echo "Building..."
echo "Deploying..."
echo "Done!"
EOF

chmod u+x deploy-check.sh
```

## What to notice in this code

- Without `#!/bin/bash`, the system's default shell runs the script, and syntax differences can cause errors
- `set -e` halts the script if any command fails — a safety net against silent errors
- `${1:-"default"}` provides a fallback when no argument is given; `${1:?"message"}` raises an error when a required argument is missing
- `$(command)` captures the output of a command as a string

## Common mistakes

### Mistake 1. Forgetting the shebang

```bash
# Without a shebang, sh may run instead of bash
# sh lacks bash features like arrays and [[ ]], causing errors
```

Always put `#!/bin/bash` on the first line.

### Mistake 2. Unquoted variables with spaces

```bash
FILE=my file.txt              # Error: tries to execute "my"
FILE="my file.txt"            # Correct

rm $FILE                      # Tries to delete "my" and "file.txt" separately
rm "$FILE"                    # Deletes "my file.txt" as one file
```

Always wrap variables in double quotes: `"$VAR"`.

### Mistake 3. Running without set -e and ignoring mid-script failures

Without `set -e`, the script continues even when a command fails. Tests fail but the deploy goes ahead — that is an outage.

### Mistake 4. Using relative paths without anchoring

If the script uses relative paths without `cd`, the result depends on where you run it from. Use absolute paths for critical locations, or use the `cd "$(dirname "$0")"` pattern.

### Mistake 5. Sending error messages to stdout

```bash
echo "Error: file not found" >&2   # stderr — correct
echo "Error: file not found"       # stdout — gets mixed in pipes
```

## Practical applications

- **Deploy scripts**: test, build, back up, deploy, health-check — all in one file
- **CI/CD**: the `run:` block in GitHub Actions is a shell script
- **Cron jobs**: automate regular backups and log rotation with scripts
- **Dev environment setup**: a new team member runs `./setup.sh` and everything is ready
- **Data pipelines**: simple ETL like CSV preprocessing and file movement

## How practitioners think about this

The strength of shell scripts is that you can use CLI commands directly. For gluing together tools like `git`, `docker`, and `kubectl`, a script is ideal. Writing `subprocess.run(["git", "pull"])` in Python is more verbose than a plain `git pull` one-liner.

On the other hand, complex logic — JSON parsing, API calls, error handling — is far better in Python. The rule of thumb is: "Will this script exceed 50 lines?" If so, write it in Python. Shell scripts shine as "sub-50-line command compositions".

## Checklist

- [ ] You understand the purpose of a shebang (`#!/bin/bash`) and always include it
- [ ] You can use `$1`, `$#`, and `$?` to handle arguments and exit codes
- [ ] You can write `if/else` and `for` loops in Bash syntax
- [ ] You can use `set -e` to halt a script on errors
- [ ] You habitually wrap variables in quotes (`"$VAR"`)

## Exercises

1. Write a script that takes a directory path as an argument and prints the number of `.py` files and `.md` files in that directory.
2. Write a script that copies all `.txt` files in the current directory to a `backup/` directory, creating `backup/` automatically if it does not exist.
3. Modify `check-file.sh` so that it prints "File is empty" if the file has zero bytes, "Large file" if it has 100 or more lines, and "Normal file" otherwise.

## Summary and next

- Shell scripts are the most direct way to automate CLI commands by writing them in a file.
- `#!/bin/bash` and `set -e` are the essential starting point for every script.
- `$1`, `$#`, and `$?` handle arguments and exit codes; `if/for` control flow.
- Always quote variables and send errors to stderr.
- Optimal for sub-50-line command compositions; switch to Python when complexity grows.

The next post covers **SSH and remote access** — key-based authentication, scp, and ssh config.

<!-- toc:begin -->
## Series Table of Contents

- [What Is the CLI and Shell?](./01-what-is-cli-and-shell.md)
- [Files and Directories](./02-files-and-directories.md)
- [Permissions and Ownership](./03-permissions-and-ownership.md)
- [cat, less, head, tail](./04-viewing-files.md)
- [grep, find, xargs](./05-grep-find-xargs.md)
- [Pipes and Redirection](./06-pipe-and-redirection.md)
- [Process Management](./07-process-management.md)
- [Environment Variables and PATH](./08-environment-variables.md)
- **Shell Script Basics (current)**
- SSH and Remote Access (upcoming)

<!-- toc:end -->

## References

- [GNU Bash Manual - Shell Scripts](https://www.gnu.org/software/bash/manual/html_node/Shell-Scripts.html)
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- [ShellCheck - Shell script linter](https://www.shellcheck.net/)
- [The Missing Semester - Shell Scripting](https://missing.csail.mit.edu/2020/shell-tools/)

Tags: Linux, Shell Script, Bash, Automation, Scripting, CLI
