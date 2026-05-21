---
title: "Git & GitHub 101 (1/10): What is Git? Version control fundamentals"
series: git-github-101
episode: 1
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- git-basics
- version-control
- distributed-vcs
- snapshot-model
- git-install
- git-config
last_reviewed: '2026-05-15'
seo_description: 'Git''s core model is "a tool that keeps snapshots of your files
  in time order", and each snapshot is produced through three areas: the working…'
---

# Git & GitHub 101 (1/10): What is Git? Version control fundamentals

If version control still feels like a tool you are supposed to learn before real work begins, this is the place to reset that picture. Git becomes much easier once you see it less as a command list and more as a way to preserve and recover changes over time.

This is the first post in the Git & GitHub 101 series. Here, we build the mental model behind Git itself before moving on to the everyday commands.

## Questions to Keep in Mind

- The problem that a version control system (VCS) solves?
- Why Git is a distributed VCS?
- The "snapshot" model and how it differs from line-by-line tracking?

## Big Picture

![Git & GitHub 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/01/01-01-mental-model.en.png)

*Git & GitHub 101 chapter 1 flow overview*

This picture places What is Git? Version control fundamentals inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Why it matters

Even when you write code alone, given enough time you hit situations like these.

- "The code that worked yesterday no longer runs. What changed?"
- "I think this function looked different a month ago."
- "I edited multiple files at the same time and now everything is tangled."

Git lets you answer those questions. You can pull back any past version of your code and see who changed what and when. Add collaboration, and the value grows further: multiple people can edit the same file and only the conflicting spots need human attention.

Many teams and open-source projects treat Git as a standard tool. Learning it is less a "nice to have" and more a shared language for collaboration.

## Mental model

> Git's core model is "a tool that keeps snapshots of your files in time order", and each snapshot is produced through three areas: the working directory, the staging area, and the repository.
In one sentence, Git is "a tool that stores snapshots of your files in time order." Each commit is a photograph of the tracked files at that moment.

Git distinguishes three areas.

- **Working Directory**: where the files you are editing live.
- **Staging Area** (a.k.a. the index): a buffer where you collect the changes that will go into the next commit.
- **Repository**: the local store of commits over time. A remote repository is a separate repository you sync with; it sits outside these three local areas.

Once you internalize this model, the reason `add`, `commit`, and `push` are separate commands becomes natural.

## Core concepts

- **Version Control System (VCS)**: A tool that records and recovers changes to files over time.
- **Distributed VCS**: A model where a normal clone gives the local repository the full history. Git is the canonical example. Work continues even when the central server is briefly unreachable.
- **Snapshot model**: Git stores a snapshot of the tracked files at commit time, not just the changed lines (internally, identical files are reused to save space).
- **Commit**: The unit of change. It records a message, an author, a timestamp, and the parent commit.
- **Branch**: A movable pointer to a commit. Creating a branch does not copy files.
- **Remote**: An external repository (often on GitHub) linked to your local repository. It maintains its own commit graph.

## Before-after

Compare two ways a small team might share code.

**Before (without Git)**

```text
project_v1.zip
project_v2_FINAL.zip
project_v2_FINAL_real.zip
project_v2_FINAL_real_alice_edits.zip
```

This snippet has three problems.

- You guess which file is current from its filename alone.
- To see what changed, you unzip both archives and diff them by hand.
- Combining two people's edits means manual copy-paste.

**After (with Git)**

```text
$ git log --oneline
b3a1c0f Add login form (alice)
8e2f5d1 Refactor session helper (bob)
1a9b2c4 Initial commit (alice)
```

Three changes happened.

- Each change shows who made it and when, in one line.
- The diff between any two commits is one `git diff` away.
- Combining work runs through `git merge`, which auto-merges what it can and asks the human to resolve only the conflicting hunks.

## Step-by-step practice

This article assumes you are installing Git for the first time. The commands are shell examples; lines starting with `$` are input, the lines below are output.

### 1. Confirm Git is installed

```text
$ git --version
git version 2.43.0
```

If Git is missing, install it for your OS.

- macOS: `brew install git` (with Homebrew) or use the git bundled with Xcode Command Line Tools.
- Ubuntu/Debian: `sudo apt update && sudo apt install git`
- Windows: install [Git for Windows](https://git-scm.com/download/win).

After installing, open a fresh shell and re-run `git --version` to confirm the version prints.

### 2. Set your identity

Each commit records the author's name and email. You set this once.

```text
$ git config --global user.name "Ada Lovelace"
$ git config --global user.email "ada@example.com"
```

The `--global` flag stores the values in the `.gitconfig` file in your home directory. To use a different email in one specific repository, run the same command inside that repository without `--global`.

### 3. Set the default branch name

Choose the default name for the branch a fresh repository starts on. `main` is the common modern choice.

```text
$ git config --global init.defaultBranch main
```

### 4. Inspect your settings

You can see the values you have set in one place.

```text
$ git config --global --list
user.name=Ada Lovelace
user.email=ada@example.com
init.defaultBranch=main
```

### 5. Use the help system

When you forget how a command works, three patterns cover most cases.

```text
$ git help                # list of common Git commands
$ git help commit         # full manual (browser or man page)
$ git commit --help       # same manual as `git help commit`
$ git commit -h           # one-screen option summary (short usage)
```

`git help <cmd>` and `git <cmd> --help` open the same full manual. The lower-case `-h` flag is the short usage summary, handy when an option name is on the tip of your tongue.

## Common mistakes

- **Leaving a work email on personal repositories** — A `--global` setting applies user-wide, so other repositories pick up the same email. To split per-repository identities, re-run the command inside that repository without `--global`.
- **Skipping `user.name` and `user.email` after install** — Your first commit greets you with `Please tell me who you are`.
- **Avoiding the command line and using only a GUI** — GUIs are quick, but troubleshooting is faster on the CLI. Knowing both is the safer setup.
- **Running an outdated git binary** — Some features (such as `git switch`, `git restore`, and the newer `git sparse-checkout`) require a recent release. Prefer the official installer or current Homebrew/apt over very old OS packages.
- **Backing up the project as a zip** — If `.git/` is excluded, the history disappears. To back things up, push to a remote.
- **Confusing `git` with `GitHub`** — Git is the tool; GitHub is one hosting service for Git repositories. GitLab and Bitbucket are other hosts.

## In practice

Git shows up in real development environments in several recurring places.

- **A safety net for solo work**: rolling back yesterday's changes with one command provides large psychological comfort.
- **A shared language for teams**: the Pull Request flow assumes Git underneath. Without a model of Git, PR review turns into guesswork.
- **A trigger for CI/CD**: most CI systems (GitHub Actions, GitLab CI, and so on) start jobs from commit or PR events.
- **Incident archaeology**: `git bisect` and `git blame` answer "when did this bug appear?" quickly, provided the history is well kept.
- **Infrastructure code**: Terraform plans and Kubernetes manifests are still text files, so they live in Git too.

When you are first learning Git, the most useful exercise is not memorizing commands but picturing where each change currently sits — working directory, staging area, or repository.

## Checklist

- [ ] `git --version` prints a version.
- [ ] `git config --global user.name` and `user.email` are set.
- [ ] `git config --global init.defaultBranch` is set (e.g. to `main`).
- [ ] You can describe Working Directory, Staging Area, and Repository in one sentence each.
- [ ] You can describe the relationship between `git` and GitHub in one sentence.
- [ ] You know the difference between `git help <command>`, `git <command> --help`, and `git <command> -h`.

## Exercises

1. Install Git on your OS and write down what `git --version` prints.
2. Set `git config --global user.name` and `user.email`, then confirm with `git config --global --list`.
3. Set `git config --global init.defaultBranch main`, then run `git init` in a fresh directory and verify the default branch is `main`.
4. Run `git help commit`, `git commit --help`, and `git commit -h` and compare how the three outputs differ.
5. Define "Working Directory", "Staging Area", and "Repository" in your own words, one sentence each.

## Wrap-up and next post

- Git is a distributed version control tool that stores snapshots of files in time order so you can track and recover changes.
- Changes flow Working Directory → Staging Area → Repository.
- Before first use, set `user.name`, `user.email`, and `init.defaultBranch` once.
- Git is the tool; GitHub is one hosting service for Git repositories. Keep them mentally separate.
- When you forget syntax, reach for `git help <command>` or `git <command> -h`.

In the next post we start from an empty directory and build the first commit. `git init`, `git status`, `git add`, and `git commit` come in, in that order.

## Answering the Opening Questions

- **The problem that a version control system (VCS) solves?**
  - The article treats What is Git? Version control fundamentals as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why Git is a distributed VCS?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **The "snapshot" model and how it differs from line-by-line tracking?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- **What is Git? Version control fundamentals (current)**
- Your first commit - init, status, add, commit (upcoming)
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

- [Pro Git — About Version Control](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control) — Grounds the chapter's opening problem statement by explaining what version control solves and how centralized and distributed models differ.
- [Pro Git — What is Git?](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F) — Maps directly to the snapshot model and distributed-repository mental model used throughout the article.
- [Pro Git — First-Time Git Setup](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup) — Backs up the first-run configuration flow for `user.name` and `user.email` with the canonical walkthrough.
- [git-config manual](https://git-scm.com/docs/git-config) — The precise reference for `git config --global` syntax and `init.defaultBranch` settings.
- [Git downloads](https://git-scm.com/downloads) — The official installation entry point for each operating system.
- [GitHub Docs — Set up Git](https://docs.github.com/en/get-started/quickstart/set-up-git) — Summarizes the first-time Git setup steps in a GitHub-oriented workflow.
Tags: git-basics, version-control, distributed-vcs, snapshot-model, git-install, git-config
