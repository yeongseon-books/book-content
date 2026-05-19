---
episode: 10
language: en
last_reviewed: '2026-05-15'
series: git-github-101
status: publish-ready
tags:
- github-flow
- git-workflow
- conventional-commits
- semantic-versioning
- code-review
- release-tag
targets:
  ebook: true
  hashnode: true
  medium: true
  mkdocs: true
  tistory: false
title: 'Building a real-world Git workflow: from issue to release in one cycle'
seo_description: 'A realistic workflow is one repeating cycle: an issue defines the
  work, a branch carries the change, a Pull Request invites review, a merge brings…'
---

# Building a real-world Git workflow: from issue to release in one cycle

Knowing isolated Git commands is not the same as knowing how a team actually ships work. The last step is to connect those commands into one repeatable loop that starts with an issue and ends with a merge, a tag, and a clean main branch.

This is the final post in the Git & GitHub 101 series. Here, we stitch the earlier lessons into one practical workflow from issue to release.

## What you will learn

- How the commands from Episodes 1–9 fit together as one realistic workflow.
- How to walk a single change through issue, branch, commit, PR, review, merge, tag, and close.
- Which recovery commands to reach for when something goes wrong mid-flow.
- Which automated guardrails (branch protection, PR template, CI) keep the same flow stable across a team.

## Why it matters

Episodes 1 through 9 introduced commands one by one. Knowing a command and knowing a workflow are different. The same `git commit` carries a different meaning depending on which branch it lands on, which PR it belongs to, and which release it is heading toward. A workflow is a contract between teammates. Once everyone follows the same loop, a new hire can tell within a week where a change starts and where it ends.

GitHub Flow is the simplest version of that contract. Keep `main` deployable at all times. Do new work on a short feature branch, open a PR, get review, and squash merge. Tag a release when you need one. That single sentence is the whole post. Everything else is repetition — running the loop end to end so it sticks.

When the loop becomes muscle memory, accidents drop. Force-pushing over a teammate's commit, committing on the wrong branch, leaking a secret you cannot scrub from history — each comes from skipping a step in the flow. The last section maps those moments to the command that pulls you back.

## Mental model

> A realistic workflow is one repeating cycle: an issue defines the work, a branch carries the change, a Pull Request invites review, a merge brings it into the shared state, a tag marks the point, and the issue is closed.
A GitHub Flow cycle looks like this.

![Mental model](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/10/10-01-mental-model.en.png)

*Mental model*
The issue is the entrance, the tag and issue close are the exit. Every step in the middle is a command from earlier episodes. The job here is to make the diagram run as a single sentence in your head.

## Core concepts

| Concept | Description |
| --- | --- |
| GitHub Flow | `main` is always deployable, every change rides on a short feature branch, and PRs are the merge path. The simplicity fits small teams well. |
| Squash merge | Collapses the feature branch's commits into a single commit on `main`. The PR title becomes the commit message. |
| Semantic versioning | `MAJOR.MINOR.PATCH`. Break compatibility, bump MAJOR. Add a feature, bump MINOR. Fix a bug, bump PATCH. |
| Release tag | A name attached to a specific commit. Create with `git tag -a v0.3.0` and share with `git push --tags`. |
| `--force-with-lease` | A force push that refuses to overwrite remote work added since you last fetched. The safe form of force push. |
| Branch protection | A GitHub setting that blocks direct pushes to `main` and requires PR + review + CI to merge. |

## Step-by-step walkthrough

Run the loop end to end on the `vacation-notes` repository from Episode 9. The change for this round is "add a rate limit to the login endpoint".

### 1. Open an issue to define the work

Work begins at an issue. Two readers should be able to read the same short sentence and agree on what is being done and why.

```bash
$ gh issue create \
    --title "Add rate limit to login endpoint" \
    --body "Block password-guessing attempts by capping logins from a single IP at 5 per minute."

Creating issue in yeongseon/vacation-notes

https://github.com/yeongseon/vacation-notes/issues/42
```

Assume the new issue is `#42`. The body focuses on the "why". The "how" goes into the PR.

### 2. Work on a feature branch

Bring `main` up to date, then branch off it.

```bash
$ git switch main
Switched to branch 'main'
Your branch is up to date with 'origin/main'.
$ git pull
Already up to date.
$ git switch -c feat/login-rate-limit
Switched to a new branch 'feat/login-rate-limit'
```

The branch name follows `<type>/<short-slug>`. The type aligns with the Conventional Commits classification. One person, one issue, one branch — that pairing is the heart of the flow.

### 3. Stack two small commits

Following Episode 9, keep one logical change per commit.

```bash
$ git add app/auth/rate_limit.py
$ git commit -m "feat(auth): add per-IP rate limiter"
[feat/login-rate-limit a1b2c3d] feat(auth): add per-IP rate limiter
 1 file changed, 28 insertions(+)
$ git add tests/auth/test_rate_limit.py
$ git commit -m "test(auth): cover rate-limit boundary cases"
[feat/login-rate-limit b2c3d4e] test(auth): cover rate-limit boundary cases
 1 file changed, 34 insertions(+)
```

Splitting production code from tests lets a reviewer read "how the feature works" and "which boundaries are tested" as two separate stories.

### 4. Push to origin

The first push uses `-u` to set the upstream. Later pushes are just `git push`.

```bash
$ git push -u origin feat/login-rate-limit
Enumerating objects: 12, done.
Counting objects: 100% (12/12), done.
Writing objects: 100% (8/8), 1.42 KiB | 1.42 MiB/s, done.
Total 8 (delta 4), reused 0 (delta 0)
remote:
remote: Create a pull request for 'feat/login-rate-limit' on GitHub by visiting:
remote:      https://github.com/yeongseon/vacation-notes/pull/new/feat/login-rate-limit
remote:
To github.com:yeongseon/vacation-notes.git
 * [new branch]      feat/login-rate-limit -> feat/login-rate-limit
Branch 'feat/login-rate-limit' set up to track 'origin/feat/login-rate-limit'.
```

The remote prints a PR-creation link. That link is the entry to the next step.

### 5. Open the PR and link the issue

Use `gh pr create` and include `Closes #42` in the body. That keyword closes the issue when the PR is merged into the default branch, `main`.

```bash
$ gh pr create \
    --base main \
    --title "feat(auth): add login rate limit" \
    --body "Closes #42

Returns 429 once the per-minute cap is hit. The limiter starts as an
in-memory dict and moves to a Redis backend in the next PR."

Creating pull request for feat/login-rate-limit into main in yeongseon/vacation-notes

https://github.com/yeongseon/vacation-notes/pull/17
```

The PR title is itself a Conventional Commits line. After squash merging, that title becomes the commit message on `main`.

### 6. Apply review feedback with `--amend` and `--force-with-lease`

Suppose a reviewer flags a test variable name. Even after the branch is pushed and the PR is open, a tiny fix that belongs only to the latest commit is a good case for `--amend`, followed by `--force-with-lease`.

```bash
$ # rename the test variable, then
$ git add tests/auth/test_rate_limit.py
$ git commit --amend --no-edit
[feat/login-rate-limit c3d4e5f] test(auth): cover rate-limit boundary cases
 Date: Tue May 5 14:08:11 2026 +0900
 1 file changed, 2 insertions(+), 2 deletions(-)
$ git push --force-with-lease
To github.com:yeongseon/vacation-notes.git
 + b2c3d4e...c3d4e5f feat/login-rate-limit -> feat/login-rate-limit (forced update)
```

`--force-with-lease` remembers the remote state from your last fetch. If a teammate has pushed to the same branch in the meantime, the push is refused. That is what makes it safer than plain `--force`. Use it on personal feature branches only.

### 7. Squash merge into main

Once review is finished, click "Squash and merge" on GitHub or run `gh`.

```bash
$ gh pr merge 17 --squash --delete-branch
✓ Squashed and merged pull request #17 (feat(auth): add login rate limit)
✓ Deleted branch feat/login-rate-limit and switched to branch main
$ git pull
Updating 9c8b7a6..d5e6f7a
Fast-forward
 app/auth/rate_limit.py        | 28 ++++++++++++++++
 tests/auth/test_rate_limit.py | 34 +++++++++++++++++++
 2 files changed, 62 insertions(+)
```

`--delete-branch` removes the feature branch on origin. Locally you land back on `main` automatically.

### 8. Tag a release

To pin this change to a release, add a tag. The previous release was `v0.2.0`, so the new feature bumps the MINOR digit to `v0.3.0`.

```bash
$ git tag -a v0.3.0 -m "Add per-IP login rate limit (#17)"
$ git push --tags
Enumerating objects: 1, done.
To github.com:yeongseon/vacation-notes.git
 * [new tag]         v0.3.0 -> v0.3.0
```

`-a` creates an annotated tag — tagger info and a message live alongside the hash. Release-note tooling pulls that message verbatim. A lightweight tag (`git tag v0.3.0`) only points at a hash, so `-a` is the default for release work.

### 9. Confirm the issue auto-closed

Because the PR body included `Closes #42`, merging this PR into the default branch, `main`, closed `#42` automatically. Verify once.

```bash
$ gh issue view 42
Add rate limit to login endpoint
Closed • yeongseon opened about 1 hour ago

  Block password-guessing attempts by capping logins from a single IP at 5 per minute.

  ...

  Closed by pull request #17 (Squashed and merged)
```

That is one full cycle. The next change starts at a new issue.

## The decision flow before you press merge

In practice, the risky part is rarely opening the PR. The risky part is deciding whether the branch is truly ready to merge. A simple decision flow makes that judgment repeatable.

![The decision flow before you press merge](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/10/10-01-the-decision-flow-before-you-press-merge.en.png)

*A GitHub Flow decision map from issue scope to merge method and release tagging*

This turns the merge button from a habit into the last step of a checklist.

## Verification loop just before merge

The most useful workflow guardrail is a fixed pre-merge review pass.

1. Run `git status` and confirm the working tree is clean.
2. Run `git log --oneline origin/main..HEAD` and read the exact commits entering the PR.
3. Run `git diff --stat origin/main...HEAD` and confirm the scope is still what the issue promised.
4. Re-read the PR body: `Closes #N`, verification steps, and release-tag intent should all be present.
5. Confirm CI and required reviews are green.
6. After the merge, pull `main`, create an annotated tag if needed, and delete the branch.

That sequence catches the most common workflow failures: oversized PRs, missing issue linkage, and merge-ready branches that were never actually verified.

## Choosing squash, merge commit, or rebase merge

Beginners should usually follow one team default, but it still helps to understand the trade-off.

| Method | Best fit | Main trade-off |
| --- | --- | --- |
| Squash merge | Keep `main` readable as one line per PR | Branch-level commit detail disappears from `main` |
| Merge commit | Preserve the branch structure and the exact landing point | The graph grows more complex faster |
| Rebase merge | Keep each commit while avoiding a merge bubble | Rewritten commit hashes can make tracing discussion harder |

For small teams and tutorial repositories, squash merge is usually the clearest default. If the branch structure itself matters, or if individual commits inside the PR are worth preserving on `main`, a merge commit can be the better fit.

## Recovery flows

Here are the mid-flow accidents teams run into most often, paired with the first command to type when they happen.

| Situation | Recovery command | Note |
| --- | --- | --- |
| Committed on the wrong branch (not yet pushed) | `git log -1 --format=%H` → `git switch <correct-branch>` → `git cherry-pick <hash>` → on the original branch run `git reset --hard HEAD~1` | `reset` is safe only before the push. |
| Want to rewrite only the previous message (not yet pushed) | `git commit --amend -m "..."` | The hash changes. Avoid amending after a push. |
| Need to undo a commit you already pushed | `git revert <hash>` → `git push` | Creates a new commit that reverses the change, so history stays linear. |
| Need to undo a squash-merged PR | `git revert <squash-commit-hash>` → `git push` | In this article's default flow, the PR lands as one squashed commit on `main`, so you usually revert that commit directly. |
| Lost local work by accident | `git reflog` → find the previous HEAD hash → `git switch -c rescue <hash>` | Reflog entries linger for roughly 90 days. |
| Pushed a secret to GitHub | Rotate the secret first → use `git filter-repo` (external tool) to scrub history → ask all collaborators to re-clone | Secret rotation comes before any history rewrite. |
| Force-pushed over a teammate's commit | Pull the lost hash from your reflog or theirs → branch off that hash → push back with `--force-with-lease` | The whole reason to default to `--force-with-lease` from day one. |

This table is not meant to be memorized. The goal is to remember it exists and reopen it when something breaks.

## Common mistakes

- Committing directly on `main`. Lock it down with branch protection so the flow cannot collapse silently.
- Opening PRs that are too big. Reviewers stop reading carefully past around 500 changed lines. Split the issue, then split the PR.
- Reaching for plain `--force`. Use `--force-with-lease` every time. Aliasing it as `git fpush` removes the temptation.
- Forgetting the tag right after a merge. Finding the release commit weeks later turns into archaeology. Add a "needs release tag?" checkbox to the PR template.
- Opening a PR without an issue. Capturing intent only inside the PR body means the next PR on the same topic has to repeat the context.

## In practice

To keep the same flow stable across a team, lean on four automated guardrails rather than memory.

1. **Branch protection.** Under Settings → Branches on GitHub, require all of these for `main`: PRs only (no direct push), at least one approving review, passing CI, and no force pushes.
2. **PR template.** A `.github/pull_request_template.md` with sections for "Summary / Linked issue / How to test / Needs release tag" prefills every new PR with the same shape.
3. **CODEOWNERS.** A `.github/CODEOWNERS` file maps directories to reviewers. PRs that touch those paths get the owners auto-requested.
4. **Required CI.** Run lint, type check, tests, and build on every PR. Block the merge button until they pass.

Add the `commit-msg` hook and `commitlint` from Episode 9 on top, and the format holds at every step of the flow.

Defaulting to squash merge keeps the history readable too. Small commits inside a feature branch collapse into one commit per PR, so `git log --oneline` on `main` reads as one line per PR.

The recovery table belongs in team documentation too. If a branch gets force-pushed incorrectly or a secret leaks into history, the team should not be inventing the response live during the incident. A small runbook linked from the repository makes the workflow much calmer under pressure.

## Checklist

- [ ] Did an issue come first, with its number landing in the PR body as `Closes #N`?
- [ ] Does the feature branch name follow `<type>/<slug>`?
- [ ] Are commits atomic, with each message in Conventional Commits form?
- [ ] Is the PR title in Conventional Commits form, with the body explaining the "why"?
- [ ] When force pushing was needed, was it `--force-with-lease`?
- [ ] Is squash merge the team default, with the feature branch deleted after merge?
- [ ] At release time, did you create an annotated tag (`-a`) and push it with `--tags`?

## Practice questions

1. On a personal repository, create a `feat/<slug>` branch, split the change into two commits, and open a PR. Add `Closes #N` to the body and confirm the issue closes after the squash merge.
2. Register a git config alias that prefers the safer push: `git config --global alias.fpush "push --force-with-lease"`. Use `git fpush` from now on.
3. Squash-merge a small PR, then tag the release with `git tag -a v0.0.1 -m "first tagged release"` and push it via `git push --tags`. Verify it appears in the GitHub Releases tab.
4. Add a `.github/pull_request_template.md` to your repository with four sections: "Summary / Linked issue / How to test / Needs release tag".
5. Pretend a commit was pushed to `main` by mistake and walk through `git revert <hash>`. Confirm a new revert commit appears in `git log --oneline`.

## Wrap-up

Every command from Episodes 1 through 9 was a step inside this single cycle. Define the work in an issue, stack atomic commits on a short feature branch, get review through a PR, squash-merge into `main`, and tag a release when one is needed. When something breaks, reopen the recovery table. At team scale, lean on branch protection, the PR template, CODEOWNERS, and required CI to make the flow self-enforcing.

This post closes the Git & GitHub 101 series. The natural next step is automation. Wiring GitHub Actions into the same repository so that every PR runs lint and tests, and pushing a tag triggers an auto-generated release note, is the topic of the next series. Until then, the most useful thing you can do is run this loop once on a project of your own. A command becomes your tool only when your fingers can type it without thinking.

<!-- toc:begin -->
## Series TOC

- [What is Git? Version Control Fundamentals](./01-what-is-git.md)
- [Your First Commit: init, add, commit](./02-first-commit.md)
- [Inspecting Changes: status, diff, log](./03-status-diff-log.md)
- [Understanding Branches: Diverging and Switching](./04-branch-basics.md)
- [Merging Branches and Resolving Conflicts](./05-merge-and-conflict.md)
- [Creating a GitHub Repository: remote, push, pull](./06-github-repository.md)
- [Collaborating with Pull Requests](./07-pull-request.md)
- [Tracking Work with Issues and Projects](./08-issue-and-project.md)
- [Writing Good Commit Messages](./09-good-commit-message.md)
- **Building a Real-World Git Workflow (current)**
<!-- toc:end -->

## References

- [GitHub Docs — GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow) — The official end-to-end description of the issue → branch → PR → merge → branch cleanup loop this chapter teaches.
- [GitHub Docs — About merge methods on GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github) — The direct reference for choosing between squash, merge-commit, and rebase-merge workflows.
- [git-push manual](https://git-scm.com/docs/git-push#Documentation/git-push.txt---force-with-lease) — Explains why `--force-with-lease` is safer than plain `--force` in the recovery section.
- [git-tag manual](https://git-scm.com/docs/git-tag) — The canonical reference for creating and publishing annotated release tags.
- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) — Defines the `MAJOR.MINOR.PATCH` rules the release-tag examples rely on.
- [GitHub Docs — About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches) — Covers the branch-protection guardrails behind no-direct-push, review, and status-check requirements.
Tags: github-flow, git-workflow, conventional-commits, semantic-versioning, code-review, release-tag
