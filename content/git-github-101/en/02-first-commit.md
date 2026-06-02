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


![Git & GitHub 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/02/02-01-mental-model.en.png)
*Git & GitHub 101 chapter 2 flow overview*

## Questions to Keep in Mind

- How to create an empty repository with `git init`?
- How to read your current state with `git status`?
- What `git add` actually means when it stages a change?

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

## Practical CLI Scenario

The following example shows the most common workflow: work on a feature branch, then merge into main. The key operating principle is "keep work units small, check status frequently, and resolve conflicts quickly."

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/auth-session
git status
git add app/auth.py tests/test_auth.py
git commit -m "feat(auth): add session refresh flow"
git push -u origin feature/auth-session
```

Placing `git pull --ff-only` at the beginning prevents branching off a stale local main that has diverged from the remote. Repeating `git status` just before committing catches unwanted files before they enter history.

Connecting this back to the first-commit lesson: this scenario follows the same principle. Regardless of which branch you are on, the `edit → add → commit` structure is identical, and `status` tells you your current coordinates. The only difference is whether you are working locally alone or collaborating with a remote.

Below is a "30-second pre-commit check" template frequently used in practice:

```bash
git status
git diff --staged
git log --oneline -5
```

These three lines let you quickly verify "current state," "what this commit contains," and "how it connects to recent history." A small routine, but it directly impacts PR quality.

## Choosing a Branch Strategy

In practice the strategy itself matters less than "what release cadence does the team follow?" The table below compares three strategies that entry-level teams most often evaluate.

| Strategy | Characteristics | Best Fit | Watch Out |
|---|---|---|---|
| Trunk-based | Short-lived branches, fast merge | Teams with frequent deploys and strong test automation | Without a small-PR discipline, main becomes unstable |
| GitHub Flow | main + feature branch + PR | SaaS / web services with continuous deployment | You must define environment-specific deploy policies separately |
| Git Flow | Multiple long-lived branches (develop/release/hotfix) | Product organizations with fixed release windows | Many branches raise operational complexity |

For beginners, starting with GitHub Flow is the safest choice. The rules are simple and it pairs well with Pull-Request-centric collaboration tools. When release requirements grow more complex later, you can extend by adding release branches.

The reason this topic appears in a first-commit article is simple: a commit is a personal record, but the branch strategy determines how that record is consumed by the team. Even with the same commit quality, a different strategy changes review speed and deploy rhythm.

For entry-level teams, fixing just two rules first delivers outsized results:

- Never push directly to main; always go through a PR.
- Each PR carries a single intent, and the commit message preserves that intent.

When these two are maintained, "first-commit quality" naturally translates into "collaboration quality."

## Standardizing Conflict Resolution

A conflict is not a failure — it is a natural signal of concurrent work. What matters is aligning the resolution sequence and verification procedure as a shared team standard.

1. Identify the conflicting files and decide which change is correct according to domain rules.
2. Remove the markers (`<<<<<<<`, `=======`, `>>>>>>>`) while leaving only the intended final code.
3. Run unit tests and static analysis to verify no syntax or behavioral regression.
4. Record the conflict resolution in a dedicated commit so reviewers can read the reasoning.

```bash
git fetch origin
git switch feature/auth-session
git merge origin/main
# After resolving conflicts
git add app/auth.py tests/test_auth.py
git commit -m "merge: resolve auth-session conflicts with main"
pytest -q
git push
```

If your team uses `rebase` instead of `merge`, only the final history shape differs — the principle of resolving and verifying conflicts remains the same. Skipping tests right after a conflict resolution creates a state where "the merge succeeded but the behavior is broken," so always attach automated verification.

## Raising Review Quality with Operational Tips

- In a PR description, write "why this choice was made" before "what changed."
- If the file count is large, split commits by functional unit so the reviewer can follow the logical flow.
- Use `git range-diff` to clearly compare commits before and after review feedback is applied.
- For urgent fixes (hotfixes), use a small PR instead of pushing directly to main to preserve history and approval records.

Following these four points improves collaboration stability far more quickly than knowing many Git commands.


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

- **What does `git init` create in the current directory?**
  - It creates a `.git/` folder containing `HEAD`, `objects/`, `refs/`, `config`, and other repository metadata. From that moment the folder is no longer a plain directory—it's a Git database.
- **What words does `git status` use to show file state?**
  - Key phrases: `Untracked files`, `Changes not staged for commit`, `Changes to be committed`. The same file can appear in two areas simultaneously depending on whether it was staged and then modified again—and that difference determines what enters the commit.
- **Does `git add` simply "add a file," or is there a more precise meaning?**
  - The precise meaning is "record the next snapshot candidate in the index." It's not a file-creation command but a commit-boundary design command. `git add -p` lets you select only the needed hunks from a single file, raising record quality.

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
