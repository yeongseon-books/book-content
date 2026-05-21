---
episode: 3
language: en
last_reviewed: '2026-05-15'
series: git-github-101
status: publish-ready
tags:
- git-status
- git-diff
- git-log
- change-history
- working-tree-vs-index
- log-formatting
targets:
  ebook: true
  hashnode: true
  medium: true
  mkdocs: true
  tistory: false
title: "Git & GitHub 101 (3/10): Reading change history - status, diff, log"
seo_description: 'status, diff, and log are three read-only windows that answer three
  different questions: where am I right now, what is different and how, and how…'
---

# Git & GitHub 101 (3/10): Reading change history - status, diff, log

Most Git mistakes get cheaper the moment you learn to read before you act. `status`, `diff`, and `log` are the three commands that let you inspect the current state, the exact content of a change, and the history behind it.

This is the third post in the Git & GitHub 101 series. Here, we focus on reading change history accurately before branches and collaboration enter the picture.


![Git & GitHub 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/03/03-01-mental-model.en.png)
*Git & GitHub 101 chapter 3 flow overview*

## Questions to Keep in Mind

- How to read each line of `git status` output with confidence?
- How to scan the same state quickly with `git status -s`?
- Which area `git diff`, `git diff --cached`, and `git diff HEAD` each compare?

## Why it matters

The previous post walked through one full edit-to-commit cycle. From here on, real collaboration begins when you can answer not only "where does my change live?" but also "what exactly is in that change?"

The three commands play different roles.

- `git status` shows **which area** holds your changes.
- `git diff` shows the **content** of those changes line by line.
- `git log` shows the **order and intent** of changes that have already been committed.

Used together, they let you self-review what your next commit will contain. That habit leads directly to better commit messages and tighter pull requests.

## Mental model

> `status`, `diff`, and `log` are three read-only windows that answer three different questions: where am I right now, what is different and how, and how did I get here.
Each command compares a different pair of areas.

A one-line rule of thumb:

- `git diff` shows **changes not yet staged** (WD vs Staging).
- `--cached` (or the synonym `--staged`) shows **changes that are staged** (Staging vs HEAD).
- Adding `HEAD` shows **everything different from the last commit** (WD vs HEAD), staged or not.

## Core concepts

- **`git status` long form**: human-readable sections such as `On branch`, `Your branch is ...`, `Changes to be committed`, `Changes not staged for commit`, and `Untracked files`.
- **`git status -s` (short form)**: one line per file with a two-letter code. The left letter is staging; the right letter is the working directory.
- **`git diff`**: defaults to WD vs Staging. `+` lines are added, `-` lines are removed.
- **`git diff --cached`**: Staging vs HEAD. "What would land in the next commit."
- **`git diff HEAD`**: WD vs HEAD. The full diff against the last commit, regardless of staging.
- **`git log`**: walks back from HEAD, printing one commit at a time. Options shape both the form and the depth.
- **`--oneline`**: one line per commit (short hash + subject).
- **`--graph`**: ASCII branch graph alongside the commits (its value shows once branches diverge).
- **`--stat`**: per-file summary of inserted and deleted lines.
- **`-p` (or `--patch`)**: includes the actual diff for each commit.

## Before-after

Here is the same question - "what just changed?" - answered two ways.

**Before (the editor's undo history)**

```text
- You scroll back through Ctrl+Z one keystroke at a time
- Changes in other files are invisible
- Yesterday's edits are likely gone
```

**After (Git's status / diff / log)**

```text
$ git status -s
 M README.md
?? draft.md

$ git diff README.md
diff --git a/README.md b/README.md
index 6e85ca6..b7f5a1e 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,4 @@
 # My First Repo

 Some notes.
+Author: me
```

In one place you see which file changed, which area it lives in (`status -s`), exactly which line was added (`diff`), and the entire history since the last commit (`log`).

## Step-by-step practice

We continue from the `my-first-repo` directory built in the previous post. Start with `git log --oneline` showing both commits.

```text
$ git log --oneline
9b8c3e2 Add intro paragraph to notes
4f1a2c0 Initial commit
```

### 1. Read status in two forms

Edit `README.md` by one line and create a new file.

```text
$ echo "Author: me" >> README.md
$ echo "draft" > draft.md
```

The long form names both the area and the next likely command.

```text
$ git status
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   README.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        draft.md

no changes added to commit (use "git add" and/or "git commit -a")
```

The short form fits the same state on two lines.

```text
$ git status -s
 M README.md
?? draft.md
```

How to read those two letters:

- Left letter: **staging** state (`M`=modified, `A`=added, `D`=deleted, blank=unchanged).
- Right letter: **working directory** state (same letters, plus `?` for untracked).
- `??` means neither side knows the file yet - it is brand new.

### 2. `git diff` for unstaged changes

`README.md` is modified but not yet staged.

```text
$ git diff
diff --git a/README.md b/README.md
index 6e85ca6..b7f5a1e 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,4 @@
 # My First Repo

 Some notes.
+Author: me
```

Read it top down:

- `diff --git a/README.md b/README.md`: which file is being compared.
- `index 6e85ca6..b7f5a1e 100644`: blob hashes before and after, plus file mode.
- `--- a/...` / `+++ b/...`: the two sides. `a` is staging (or HEAD); `b` is the working directory.
- `@@ -1,3 +1,4 @@`: the hunk header. "Three lines starting at line 1 in the original; four lines starting at line 1 in the new version."
- Lines starting with `+` are added, `-` are removed, and a leading space marks unchanged context.

### 3. `git diff --cached` for staged changes

Stage README and compare both commands.

```text
$ git add README.md
$ git diff
$ git diff --cached
diff --git a/README.md b/README.md
index 6e85ca6..b7f5a1e 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,4 @@
 # My First Repo

 Some notes.
+Author: me
```

`git diff` is empty because the change has moved into staging. `--cached` shows "what would land in the next commit." Running it once before each `commit` is a cheap habit that catches surprises.

The long-form `git status` at this point also makes the staging-area hint visible.

```text
$ git status
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   README.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        draft.md

```

The line `(use "git restore --staged <file>..." to unstage)` under `Changes to be committed:` is Git telling you exactly which command moves the change back out of staging.

### 4. `git diff HEAD` to combine both areas

`draft.md` is still untracked while README is staged. `git diff HEAD` collapses both areas into a single comparison against the last commit.

```text
$ git diff HEAD
diff --git a/README.md b/README.md
index 6e85ca6..b7f5a1e 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,4 @@
 # My First Repo

 Some notes.
+Author: me
```

`draft.md` is missing from this output. `git diff` shows changes to **tracked files**; an untracked file is not one. To include it, run `git status` or `git add -N draft.md` (intent-to-add) first.

### 5. Compare two commits

Pass two hashes to compare specific commits.

```text
$ git diff 4f1a2c0 9b8c3e2
diff --git a/README.md b/README.md
index a1b2c3d..6e85ca6 100644
--- a/README.md
+++ b/README.md
@@ -1 +1,3 @@
 # My First Repo
+
+Some notes.
```

The order is "older then newer." Swap the order and `+` and `-` flip. To see the change introduced by a single commit, `git show <hash>` is shorter.

### 6. Shape `git log` output

Commit the staged README change and then read the resulting log in different shapes.

```text
$ git commit -m "Add author line to README"
[main e7d2c1a] Add author line to README
 1 file changed, 1 insertion(+)
```

Compare the same history through different options.

```text
$ git log --oneline
e7d2c1a Add author line to README
9b8c3e2 Add intro paragraph to notes
4f1a2c0 Initial commit
```

```text
$ git log --oneline --graph
* e7d2c1a Add author line to README
* 9b8c3e2 Add intro paragraph to notes
* 4f1a2c0 Initial commit
```

The graph is a straight line today because there are no branches yet. Once branches start to merge, the shape becomes the most useful part of the output.

```text
$ git log --stat
commit e7d2c1a4b9f0c5d2e1a8b7c6d5e4f3a2b1c0d9e8
Author: Me <me@example.com>
Date:   Mon May 4 10:30:00 2026 +0900

    Add author line to README

 README.md | 1 +
 1 file changed, 1 insertion(+)
```

`--stat` summarises which files changed and by how much. It is the line you most often borrow when writing a PR description.

```text
$ git log -p -1
commit e7d2c1a4b9f0c5d2e1a8b7c6d5e4f3a2b1c0d9e8
Author: Me <me@example.com>
Date:   Mon May 4 10:30:00 2026 +0900

    Add author line to README

diff --git a/README.md b/README.md
index 6e85ca6..b7f5a1e 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,4 @@
 # My First Repo

 Some notes.
+Author: me
```

`-p` (or `--patch`) expands each commit with its full diff. `-1` limits the output to a single commit.

## Common mistakes

- **Reading "no diff" as "no change"** - changes already staged do not appear in plain `git diff`. Use `git diff --cached` or `git diff HEAD`.
- **Swapping the two arguments to `git diff <a> <b>`** - `<a>` is older, `<b>` is newer. Reverse them and `+/-` flip too.
- **Trusting `git log` subjects alone** - if the subject is vague, `--stat` or `-p` gives you the truth.
- **Reading the two letters of `git status -s` as one** - left is staging, right is working directory. `MM` is a different state ("staged change with further edits on top of it") from `M`.
- **Thinking an untracked file vanished from `git diff`** - it does not appear there. Use `git status` or `git add -N`.
- **Stuck inside `git log` output** - the pager (`less`) is open. Press `q` to exit.

## In practice

- **Pre-commit self-check**: scan with `git status -s`, then read `git diff --cached` once. If something unexpected is staged, drop it with `git restore --staged <file>`.
- **Drafting a PR description**: list the commits with `git log --oneline origin/main..HEAD`, then review the contents with `git log -p origin/main..HEAD`.
- **Bug hunting**: trace a file's history with `git log -p <file>`, or for harder cases reach for `git bisect` (covered later in the series).
- **Aliases that stick**: a single line such as `git config --global alias.lg "log --oneline --graph --decorate"` saves a lot of typing.
- **Colour output**: most environments enable it by default. If yours does not, run `git config --global color.ui auto`.

## Checklist

- [ ] You read both the long form and the `-s` short form of `git status`.
- [ ] You can describe what `git diff`, `git diff --cached`, and `git diff HEAD` each compare in one sentence.
- [ ] You can explain what the hunk header `@@ -1,3 +1,4 @@` means.
- [ ] You compared `git log --oneline`, `--graph`, `--stat`, and `-p` outputs side by side.
- [ ] You can describe what the order of `git diff <a> <b>` arguments means.
- [ ] Your fingers know that `q` exits the pager.

## Exercises

1. Edit one line of `README.md` and capture the output of both `git diff` and `git diff --cached` for comparison.
2. Stage the change, confirm that `git diff` is empty, and confirm that `git diff HEAD` still shows it.
3. Compare your first two commits with `git diff 4f1a2c0 9b8c3e2` (substitute your real hashes), then run `git show 9b8c3e2` for the same information.
4. Run `git log --oneline --graph --stat` once and write a sentence about which option produces which line.
5. Create a fresh file, observe the `??` in `git status -s`, then `git add` it and watch the marker change.

## Wrap-up and next post

- `git status` tells you where changes live, `git diff` tells you what is in them, and `git log` tells you the shape of the history already saved.
- `git diff` defaults to WD vs Staging, `--cached` to Staging vs HEAD, and `HEAD` to a combined comparison against the last commit.
- `git log` shows the same history at different depths depending on which options you combine. `--oneline --graph` is great for scanning; `--stat` and `-p` are great for review.
- The cheapest habit before any commit is `status -s` followed by `diff --cached`.

The next post moves into branches: how to start a parallel line of work in the same folder and switch between them safely.

## Answering the Opening Questions

- **How to read each line of `git status` output with confidence?**
  - The article treats Reading change history - status, diff, log as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How to scan the same state quickly with `git status -s`?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Which area `git diff`, `git diff --cached`, and `git diff HEAD` each compare?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Git & GitHub 101 (1/10): What is Git? Version control fundamentals](./01-what-is-git.md)
- [Git & GitHub 101 (2/10): Your first commit - init, status, add, commit](./02-first-commit.md)
- **Reading change history - status, diff, log (current)**
- Branch basics - create, switch, and compare (upcoming)
- Merge and Conflict Resolution - Bringing Two Lines Back Together (upcoming)
- Creating a GitHub repository - remote, push, and pull in one go (upcoming)
- Collaborating with Pull Requests - From Branch to Review to Main (upcoming)
- Tracking Work with Issues and Projects - How GitHub Records What's Next (upcoming)
- Writing Good Commit Messages: Conventional Commits and Useful Bodies (upcoming)
- Building a real-world Git workflow: from issue to release in one cycle (upcoming)

<!-- toc:end -->

## References

- [Pro Git — Viewing the Commit History](https://git-scm.com/book/en/v2/Git-Basics-Viewing-the-Commit-History) — Provides the bigger picture behind `git log --oneline`, `--graph`, `--stat`, and `-p` in this chapter.
- [git-status manual](https://git-scm.com/docs/git-status) — The canonical explanation of long-form status output and the `-s` short format.
- [git-diff manual](https://git-scm.com/docs/git-diff) — The source of truth for what `git diff`, `git diff --cached`, and `git diff HEAD` compare.
- [git-log manual](https://git-scm.com/docs/git-log) — Backs up the different log shapes and option combinations shown in the walkthrough.
- [git-show manual](https://git-scm.com/docs/git-show) — Covers the single-commit inspection shortcut the article suggests as an alternative.
- [gitrevisions manual](https://git-scm.com/docs/gitrevisions) — Defines revision and range notation such as `HEAD` and two-commit comparisons like `<old> <new>`.
Tags: git-status, git-diff, git-log, change-history, working-tree-vs-index, log-formatting
