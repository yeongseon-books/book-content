---
title: 'branches and merges: combining revisions made in parallel'
series: alembic-101
episode: 5
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Python
- Alembic
- branch
- merge
- depends_on
- SQLite
last_reviewed: '2026-05-03'
seo_description: An alembic revision graph is a directed acyclic graph (DAG), just
  like git.
---

# branches and merges: combining revisions made in parallel

When teammates generate revisions in parallel, the graph naturally forks into multiple heads. If you do not recognize that as a normal state, the first `Multiple head revisions are present` error feels much worse than it is.

This is post 5 in the Alembic 101 series. Here we will cover why branches appear and how `alembic merge` brings the graph back to a single head.

## What you will learn

- When the alembic revision graph forks into branches
- The exact role of `branch_labels` and `depends_on`
- How to consolidate two heads with `alembic merge`
- How `upgrade` and `downgrade` behave in a multi-head state
- Operational rules to reduce branch incidents on a team

## Why it matters

On any team where several people open PRs in parallel, alembic branches happen almost every week. A branch on its own is normal, but the first time you hit `Multiple head revisions are present` and a deploy stops, panic sets in. This post is the calm-merge guide for that moment.

## Mental Model

> An alembic revision graph is **a directed acyclic graph (DAG)**, just like git. When two people generate a revision from the same head, you get two new heads. `alembic merge` creates a new revision whose parents are both heads, returning the graph to a single head.

Borrowing from git: `alembic merge` is `git merge`. The difference is that the merge revision does not introduce new schema changes — it only stitches the graph back together.

## Core concepts

### When a branch appears

```text
A → B → C  (head: C)
        ↑
      Alice generates D, Bob generates E concurrently
        ↓
A → B → C → D  (head: D)
            ↘
              E  (head: E)
```

Run `alembic heads` and you see two heads:

```bash
$ alembic heads
d1e2f3a4b5c6 (head)
e7f8a9b0c1d2 (head)
```

In this state, `alembic upgrade head` raises an ambiguity error.

### `branch_labels` and `depends_on`

```python
revision = "d1e2f3a4b5c6"
down_revision = "c1234567890a"
branch_labels = ("billing",)        # name of the branch this revision belongs to
depends_on = ("e7f8a9b0c1d2",)      # this revision depends on a specific revision in another branch
```

- `branch_labels`: used when you intentionally maintain a separate branch (for example, isolating migrations for a different domain on the same DB). You can call `alembic upgrade billing@head`.
- `depends_on`: used when a revision in one branch needs a revision from another branch to be applied first. It encodes a cross-branch dependency.

In most teams, neither is used routinely; branches are merged as soon as they appear.

### `alembic merge`

```bash
alembic merge -m "merge billing and audit branches" d1e2f3a4b5c6 e7f8a9b0c1d2
```

This generates a merge revision like:

```python
"""merge billing and audit branches

Revision ID: f9a8b7c6d5e4
Revises: d1e2f3a4b5c6, e7f8a9b0c1d2
Create Date: 2026-05-03 12:00:00.000000
"""
revision = "f9a8b7c6d5e4"
down_revision = ("d1e2f3a4b5c6", "e7f8a9b0c1d2")
branch_labels = None
depends_on = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
```

The key points: `down_revision` is a **tuple** and both `upgrade` and `downgrade` are **empty**. A merge only consolidates the graph.

### Commands in a multi-head state

```bash
alembic heads                      # list current heads
alembic upgrade heads              # apply every head all the way (note the s)
alembic upgrade <revision_id>      # only up to a specific revision
alembic upgrade billing@head       # target by branch_labels
```

Remember the `head` (singular) vs `heads` (plural) distinction. Before merging, you need `heads`.

## Before-After

```text
# Before: pushed without merging, deploy is stuck
$ alembic upgrade head
ERROR: Multiple head revisions are present for given argument 'head';
please specify a specific target revision...
```

```bash
# After: confirm heads, merge, return to single head
$ alembic heads
d1e2f3a4b5c6 (head)
e7f8a9b0c1d2 (head)

$ alembic merge -m "merge feature-billing into trunk" d1e2f3a4b5c6 e7f8a9b0c1d2
Generating versions/f9a8b7c6d5e4_merge_feature_billing_into_trunk.py ... done

$ alembic heads
f9a8b7c6d5e4 (head)

$ alembic upgrade head
INFO  Running upgrade ... -> f9a8b7c6d5e4, merge feature-billing into trunk
```

If the merge revision lands in a PR right before deploy, the same incident never happens.

## Step-by-step walkthrough

### Step 1: reproduce a branch

Build a branch locally to internalize how it feels.

```bash
# Alice's work
git checkout -b feature-a
alembic revision -m "add billing column"

# Bob's work (from the same base)
git checkout master
git checkout -b feature-b
alembic revision -m "add audit column"

# After both PRs land on master
git checkout master
git merge feature-a
git merge feature-b
alembic heads
```

You see two heads.

### Step 2: create the merge revision

```bash
alembic merge -m "merge billing and audit" <id1> <id2>
```

Commit the generated file. Both `upgrade` and `downgrade` stay empty.

### Step 3: apply

```bash
alembic upgrade head
```

Now that there is a single head again, things proceed as usual.

### Step 4: when there is a cross-branch dependency

If `feature-b` uses a column added in `feature-a`, declare it with `depends_on`.

```python
# feature-b's revision
revision = "e7f8a9b0c1d2"
down_revision = "c1234567890a"
depends_on = ("d1e2f3a4b5c6",)  # feature-a's revision
```

`alembic upgrade head` reads the dependency and applies things in the correct order.

### Step 5: an intentional long-running branch

Use `branch_labels` only when you genuinely run a separate domain.

```python
revision = "abc123"
down_revision = None
branch_labels = ("audit",)
```

You can then run `alembic upgrade audit@head` to apply only the audit branch. Most teams never need this.

## Common mistakes

- **Confusing `heads` (plural) with `head` (singular).** Pre-merge, `head` raises an ambiguity error.
- **Putting schema changes inside a merge revision's `upgrade`.** Mixing new changes into the merge step makes history hard to follow. Keep merges purely structural.
- **Overusing `branch_labels`.** Day-to-day branches on a normal team are cleaner if you close them with a merge immediately.
- **Failing to detect migration conflicts in PR.** Add a CI step that fails if `alembic heads` returns more than one entry.
- **Hand-reordering `down_revision` tuples after a merge.** It does not change semantics, but it confuses reviewers. Keep the autogenerated order.

## Practical patterns

- **CI: head count must be 1.** A guard such as `python -c "from alembic.config import Config; from alembic.script import ScriptDirectory; cfg=Config('alembic.ini'); s=ScriptDirectory.from_config(cfg); assert len(list(s.get_heads()))==1"` catches multi-head PRs.
- **Late-merger workflow on PR conflicts.** Of two conflicting PRs, the one that lands second includes the merge revision in its own PR.
- **Convention for merge messages.** Standardize on `merge <branchA> and <branchB>`.
- **`depends_on` only when you must.** It is usually simpler to put the two revisions in one PR and treat them as a single branch.
- **`alembic history --verbose` for graph visualization.** This is the fastest way to understand the situation when something breaks.

## Checklist

- [ ] After merging, `alembic heads` returns a single head
- [ ] The merge revision's `upgrade` and `downgrade` are empty
- [ ] CI detects a multi-head state
- [ ] `depends_on` is declared if there is a cross-branch dependency
- [ ] `branch_labels` is used only for genuinely separate domains
- [ ] Merge messages follow the `merge <X> and <Y>` convention

## Exercises

1. Create two heads in a local SQLite environment and consolidate them with `alembic merge`.
2. Open the merge revision and confirm that `down_revision` is a tuple.
3. Add a script to CI that checks the head count and verify it blocks a multi-head PR.

## Wrap up, next post

An alembic branch follows the same model as a git branch. There is nothing to fear — `alembic merge` only consolidates the graph. A single line in CI that enforces "exactly one head" prevents most team-level incidents.

The next post covers data migrations: changes that update the data itself rather than the schema.

## References

- Alembic: Working with Branches — https://alembic.sqlalchemy.org/en/latest/branches.html
- Alembic: Merging Branches — https://alembic.sqlalchemy.org/en/latest/branches.html#merging-branches
- Alembic: depends_on — https://alembic.sqlalchemy.org/en/latest/branches.html#referencing-dependencies
- Alembic: ScriptDirectory API — https://alembic.sqlalchemy.org/en/latest/api/script.html

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, Alembic, branch, merge, depends_on, SQLite
