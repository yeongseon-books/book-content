---
episode: 2
language: en
last_reviewed: '2026-05-15'
series: git-github-101
status: publish-ready
tags:
- git-init
- git-status
- git-add
- git-commit
- staging-area
- first-repository
targets:
  ebook: true
  hashnode: true
  medium: true
  mkdocs: true
  tistory: false
title: "Git & GitHub 101 (2/10): Your first commit - init, status, add, commit"
seo_description: A first commit is the act of "gathering changes from the working
  directory into the staging area, then moving them into the repository as a single…
---

# Git & GitHub 101 (2/10): Your first commit - init, status, add, commit

The first commit is where Git stops being abstract. Once you walk one change all the way from an empty folder to a saved snapshot, later commands start to feel predictable instead of arbitrary.

This is the second post in the Git & GitHub 101 series. Here, we go through the full init -> add -> commit cycle by hand.

## Questions to Keep in Mind

- How to create an empty repository with `git init`?
- How to read your current state with `git status`?
- What `git add` actually means when it stages a change?

## Big Picture

![Git & GitHub 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/02/02-01-mental-model.en.png)

*Git & GitHub 101 chapter 2 flow overview*

This picture places Your first commit - init, status, add, commit inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Your first commit - init, status, add, commit is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Why it matters

Most Git commands make sense only when you can answer one question first: where does my change currently live? That is why the hard part of learning Git early on is not the command names but the mental picture of three areas.

Making your first commit by hand makes that picture sharp very quickly.

- You see how `git status` differs between "I edited the file" and "I edited and ran `git add`."
- You see status return to clean once a commit is made.
- You see what actually appears inside `.git/`.

After one full cycle, commands you meet later (`git diff`, `git log`, `git restore`, `git switch`) become much easier to predict because you can guess which area each one touches.

## Mental model

> A first commit is the act of "gathering changes from the working directory into the staging area, then moving them into the repository as a single snapshot". `add` and `commit` exist as separate commands precisely because those are two distinct steps.
A single edit-to-commit cycle looks like this.

Three verbs work together.

- **edit**: change or create files in your editor. Git does not know yet.
- **`add`**: tell Git "include this change in the next commit."
- **`commit`**: take what is in staging and save it as a snapshot.

`git status` is the guide that tells you "where things are right now," whichever step you are on. It is the safest first command when you are confused.

## Core concepts

- **Working Directory**: the files you see on disk. Edits in your editor change this area.
- **Staging Area (Index)**: the list of changes that will go into the next commit. `git add` fills it; `git commit` empties it.
- **`git init`**: creates the `.git/` directory inside the current folder, turning it into a Git repository. Run once.
- **Untracked / Modified / Staged**: the three states `git status` shows. A file Git has not yet seen, a tracked file that changed, and a change queued for the next commit.
- **Commit message**: a one-line summary of intent. Future readers (often you) thank past you for it during `git log`.
- **`HEAD`**: a nickname for the most recent commit on the current branch.

## Before-after

Compare the same task done with zip backups versus Git.

**Before (zip backups)**

```text
$ ls
notes_v1.txt
notes_v2.txt
notes_v2_FINAL.txt
```

- The "current" file is a guess based on the filename.
- Comparing two versions means firing up a separate diff tool.
- The intent behind a change lives nowhere on disk.

**After (Git)**

```text
$ git log --oneline
9b8c3e2 Add intro paragraph to notes
4f1a2c0 Initial commit
```

- The latest commit is whatever `HEAD` points to. Filename guesswork disappears.
- The diff between two commits is a single `git diff 9b8c3e2 4f1a2c0`.
- The intent of each change lives in its commit message.

## Step-by-step practice

Run the commands below in order. Lines starting with `$` are input; the lines below are output.

### 1. Start in an empty directory

```text
$ mkdir my-first-repo
$ cd my-first-repo
$ ls -A
```

If `ls -A` prints nothing, the directory is empty.

### 2. Create the repository with `git init`

```text
$ git init
Initialized empty Git repository in /Users/me/my-first-repo/.git/
```

Once `.git/` exists, this directory is a Git repository. Run this once per project.

```text
$ ls -A
.git
```

### 3. Create the first file and check status

```text
$ echo "# My First Repo" > README.md
$ git status
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        README.md

nothing added to commit but untracked files present (use "git add" to track)
```

The new `README.md` is `Untracked` because Git has not yet seen it. Notice that status also tells you the next likely command (`use "git add" to track`).

### 4. Stage the change with `git add`

```text
$ git add README.md
$ git status
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   README.md
```

The state moved from `Untracked` to `Changes to be committed`. That second state is staging.

### 5. Save the snapshot with `git commit -m`

```text
$ git commit -m "Initial commit"
[main (root-commit) 4f1a2c0] Initial commit
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

The first commit gets a `root-commit` label because it has no parent. Status returns to clean.

```text
$ git status
On branch main
nothing to commit, working tree clean
```

### 6. Run the cycle one more time

```text
$ echo "" >> README.md
$ echo "Some notes." >> README.md
$ git status
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   README.md

no changes added to commit (use "git add" and/or "git commit -a")
```

This time the file is `modified`, not `Untracked`, because Git already tracks it.

```text
$ git add README.md
$ git commit -m "Add intro paragraph to notes"
[main 9b8c3e2] Add intro paragraph to notes
 1 file changed, 2 insertions(+)
```

Confirm with `git log --oneline`.

```text
$ git log --oneline
9b8c3e2 Add intro paragraph to notes
4f1a2c0 Initial commit
```

## Common mistakes

- **Running `git init` in your home directory** — your whole home becomes a repository, and `git status` becomes painfully slow. Run it inside the project directory only.
- **Trying to commit without `add`** — empty staging triggers "nothing to commit." A change must be staged before it can be saved.
- **`git add .` sweeping in unintended files** — build artefacts and secret files can slip in. When in doubt, list filenames explicitly or set up `.gitignore` first.
- **Empty commit messages** — `git commit -m ""` is rejected. A single line about intent is enough.
- **Hand-editing `.git/`** — touching internal files can corrupt the repository. Change it only through commands.
- **Editing a tracked file and forgetting to `add` before committing** — you may see "nothing to commit" or quietly include only part of your work. Checking with `git status` first is the safer habit.

## In practice

This same cycle shows up in real work in several recurring ways.

- **Starting a new project**: `git init` -> add a README and `.gitignore` -> first commit. The first commit is conventionally a short "Initial commit."
- **One-intent commits**: keep one purpose per commit. Mixing "add login form" with "refactor session helper" makes review and rollback harder.
- **Run `git status` often**: there is no penalty for running it. Aligning your mental picture with reality is the biggest time saver.
- **Smaller commits make collaboration easier**: a giant single commit is hard to review and increases the size of merge conflicts. Small, frequent commits are safer.

## Checklist

- [ ] You looked inside the `.git/` directory created by `git init`.
- [ ] You saw `Untracked`, `modified`, and `Changes to be committed` in `git status`.
- [ ] You can describe how `git status` changes before and after `git add`.
- [ ] You created a commit with `git commit -m "..."` and confirmed it with `git log --oneline`.
- [ ] You watched `git status` return to `working tree clean` after committing.
- [ ] You can explain what `root-commit` means in one sentence.

## Exercises

1. Run `git init` in an empty directory and look one level into `.git/` to see what was created.
2. Create a `README.md`, view status while it is `Untracked`, run `git add`, and compare status again.
3. After your first commit, append a line to `README.md` and commit. Confirm that `git log --oneline` now shows two lines.
4. Try `git commit -m ""` and write down the message Git prints back.
5. Create two new files, `git add` only one of them, commit, and use `git status` to see what state the other file is in.

## Wrap-up and next post

- `git init` adds a `.git/` directory and turns the current folder into a Git repository.
- `git status` is the guide that tells you whether each change sits in Working Directory, Staging, or Repository.
- `git add` moves changes into staging; `git commit` saves staged changes as a snapshot.
- Walking through one full edit -> add -> commit cycle by hand makes later commands much easier to reason about.

The next post takes a closer look at `git status` output and uses `git diff` and `git log` to read change history in detail.

## Answering the Opening Questions

- **How to create an empty repository with `git init`?**
  - The article treats Your first commit - init, status, add, commit as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How to read your current state with `git status`?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What `git add` actually means when it stages a change?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Git & GitHub 101 (1/10): What is Git? Version control fundamentals](./01-what-is-git.md)
- **Your first commit - init, status, add, commit (current)**
- Reading change history - status, diff, log (upcoming)
- Branch basics - create, switch, and compare (upcoming)
- Merge and Conflict Resolution - Bringing Two Lines Back Together (upcoming)
- Creating a GitHub repository - remote, push, and pull in one go (upcoming)
- Collaborating with Pull Requests - From Branch to Review to Main (upcoming)
- Tracking Work with Issues and Projects - How GitHub Records What's Next (upcoming)
- Writing Good Commit Messages: Conventional Commits and Useful Bodies (upcoming)
- Building a real-world Git workflow: from issue to release in one cycle (upcoming)

<!-- toc:end -->

## References

- [Pro Git — Recording Changes to the Repository](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository) — The clearest canonical walkthrough of moving a change from working directory to staging and into a commit.
- [git-init manual](https://git-scm.com/docs/git-init) — Documents exactly how `git init` creates a repository and which defaults it uses.
- [git-status manual](https://git-scm.com/docs/git-status) — The source for status terms like `Untracked`, `modified`, and `Changes to be committed` used in the examples.
- [git-add manual](https://git-scm.com/docs/git-add) — Explains why `git add` means “stage this change” rather than merely “add a file.”
- [git-commit manual](https://git-scm.com/docs/git-commit) — The authoritative reference for `git commit -m` and the act of recording a snapshot.
- [git-log manual](https://git-scm.com/docs/git-log) — Connects to the final verification step where the article confirms the first two commits with `git log --oneline`.
Tags: git-init, git-status, git-add, git-commit, staging-area, first-repository
