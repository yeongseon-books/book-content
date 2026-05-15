---
title: 'Downgrade strategy: when to write it for real and when to forbid it'
series: alembic-101
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
- Python
- Alembic
- downgrade
- expand-contract
- rollback
- SQLite
last_reviewed: '2026-05-03'
seo_description: 'Downgrade splits into two kinds. (1) Reversible changes: a precise
  inverse exists with no data loss (e.g., adding a nullable column).'
---

# Downgrade strategy: when to write it for real and when to forbid it

The existence of a `downgrade()` function does not make a change safe to reverse. Some revisions can be undone precisely, while others imply immediate data loss the moment you try.

This is post 8 in the Alembic 101 series. Here we will separate reversible from irreversible changes and show how to encode that policy honestly.

## What you will learn

- When a production downgrade is possible and when it is effectively impossible
- The kinds of irreversible changes and how to handle them
- How the expand-contract pattern restores the ability to downgrade
- How to express a "no downgrade" policy at the code level
- How to choose between forward-fix and downgrade when something goes wrong

## Why it matters

When you first learn alembic, downgrade looks like an obvious built-in feature. In real production, it is rarely used and frequently dangerous. But leaving it as an empty function is not the right answer either. "How do we handle downgrade" is an operational policy decision, and that policy should be expressed explicitly in code.

## Mental Model

> Downgrade splits into two kinds. **(1) Reversible changes: a precise inverse exists with no data loss (e.g., adding a nullable column). (2) Irreversible changes: the inverse implies data loss (e.g., dropping a column, a data migration).** Write the first kind for real and explicitly block the second.

The git analogy: type 1 is a commit that reverts cleanly; type 2 is a merged history you cannot undo without a force-push.

## Core concepts

### Reversible vs irreversible

| Change | Reversible? | Note |
| --- | --- | --- |
| Add nullable column | Yes | Drop reverts precisely |
| Add or drop index | Yes | Recreate to recover |
| Add table | Yes | Drop reverts |
| **Drop column** | No | Data loss |
| **Data migration** | No | Hard to restore pre-transform state |
| **Tighten to NOT NULL** | Effectively no | The default to use is ambiguous |
| Narrow column type (`String(100)` → `String(50)`) | No | Truncation risk |

For irreversible changes, you cannot honestly write a downgrade — blocking it is more honest.

### Declaring "no downgrade"

```python
def downgrade() -> None:
    raise NotImplementedError(
        "Irreversible: tier column drop loses data. "
        "If rollback needed, restore from backup."
    )
```

Leaving it as `pass` lets a stray `alembic downgrade -1` succeed silently — the graph rewinds while the schema stays the same, leaving you in a dangerous state. `raise NotImplementedError` prevents that.

### The expand-contract pattern

The strongest tool for turning irreversible changes into reversible ones.

```text
Phase 1 (expand):   add the new schema, keep the old
Phase 2 (migrate):  move data into the new schema
Phase 3 (deploy):   application starts using the new schema
Phase 4 (contract): remove the old schema
```

Each phase is **an individually reversible change**, so even if something fails at a given phase you can roll back one phase at a time. Take a column rename as an example:

```text
1. add display_name (nullable=True)         ← reversible
2. backfill display_name from name          ← data migration (irreversible)
3. app code uses display_name               ← code deploy
4. drop name                                ← irreversible, but with safety nets between phases
```

You only move to phase 4 once production has stabilized through phase 3. Until phase 4, you can rewind to phase 2 at any time.

### Forward-fix vs downgrade

When something breaks in production, you pick one:

- **forward-fix**: a new revision that corrects the problem (recommended in most cases)
- **downgrade**: rewind to the previous revision (risky when irreversible work is involved)

Why forward-fix should be the default: it keeps the `alembic_version` table, other instances' state, and application code consistency moving in a single direction, which is far easier to reason about.

## Before-After

```python
# Before: empty downgrade on an irreversible change
def upgrade() -> None:
    op.drop_column("users", "legacy_token")  # ← data lost forever

def downgrade() -> None:
    pass  # ← silently "succeeds" on accident
```

```python
# After: explicit block
def upgrade() -> None:
    op.drop_column("users", "legacy_token")

def downgrade() -> None:
    raise NotImplementedError(
        "drop column users.legacy_token is irreversible (data loss). "
        "Restore from backup or apply a new revision that re-adds the column."
    )
```

The After version makes intent explicit. If someone runs `alembic downgrade -1` by accident, it fails immediately and prevents a real incident.

## Step-by-step walkthrough

### Step 1: write a reversible revision

```python
def upgrade() -> None:
    op.add_column("users", sa.Column("nickname", sa.String(50), nullable=True))

def downgrade() -> None:
    op.drop_column("users", "nickname")
```

Adding with `nullable=True` is schema-only and there is no data, so the drop is safe. Write the downgrade for real.

### Step 2: block an irreversible revision

```python
def upgrade() -> None:
    op.drop_column("users", "old_field")

def downgrade() -> None:
    raise NotImplementedError("drop is irreversible (data loss)")
```

### Step 3: handle a rename via expand-contract

revision 1 (expand):
```python
def upgrade() -> None:
    op.add_column("users", sa.Column("display_name", sa.String(100), nullable=True))

def downgrade() -> None:
    op.drop_column("users", "display_name")
```

revision 2 (data backfill, irreversible):
```python
def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(text("UPDATE users SET display_name = name WHERE display_name IS NULL"))

def downgrade() -> None:
    raise NotImplementedError("data migration is irreversible")
```

revision 3 (contract):
```python
def upgrade() -> None:
    op.drop_column("users", "name")

def downgrade() -> None:
    raise NotImplementedError("drop name is irreversible")
```

Before applying 3, you can move freely between 1 and 2. Incidents after 3 are handled with forward-fix.

### Step 4: document the policy

Add one line to `alembic.ini` or the README.

```text
Downgrade policy:
- Reversible revisions: real downgrade()
- Irreversible (drop, data migration): raise NotImplementedError
- Production rollback: forward-fix only; restore from backup if necessary
```

## Common mistakes

- **`pass` on an irreversible change.** Silent success is the most dangerous outcome. Use `NotImplementedError` to be explicit.
- **Aggressively using downgrade in production.** Sync with other instances and data state breaks easily. Forward-fix is the default.
- **Big changes without expand-contract.** Renames and tightening to NOT NULL handled in one revision are effectively irreversible.
- **Not testing downgrade.** Run `downgrade -1 && upgrade head` once on the PR to verify reversibility.
- **Assuming downgrade is actually reversible.** Schema may rewind while data has changed and the application assumes the new schema — that situation is common.

## Practical patterns

- **Three-phase split (expand-contract).** Apply this pattern to renames, NOT NULL tightening, and column drops.
- **Disable production downgrade at the deploy script level.** Make sure no human can accidentally invoke `alembic downgrade` in operations.
- **Add "is this reversible?" to the PR checklist.** Make the decision explicit during code review.
- **Backup-and-restore is the real rollback tool.** Do not treat alembic downgrade as a backup substitute.
- **Forward-fix revision template.** Express intent with a `"fix <old_revision>"` style message.

## Checklist

- [ ] Every revision is classified as reversible or irreversible
- [ ] Irreversible revisions have `NotImplementedError` in `downgrade`
- [ ] Big changes (rename, NOT NULL, drop) are split into three expand-contract phases
- [ ] Reversible revisions pass a `downgrade -1 && upgrade head` cycle on the PR
- [ ] Production downgrade policy is documented in the README
- [ ] Backup-and-restore is verified as a real rollback path

## Exercises

1. Create a column-drop revision with `NotImplementedError` in `downgrade`, then confirm `alembic downgrade -1` fails.
2. Implement the `name` → `display_name` rename as a three-phase expand-contract sequence.
3. After application code starts using the new column, attempt a downgrade and observe what error occurs.

## Wrap up, next post

Downgrade is not a "feature on by default" — it is a feature decided by policy. Classifying changes into reversible and irreversible and explicitly blocking the latter is honest operations. The expand-contract pattern is the strongest tool for turning irreversible changes back into reversible ones.

The next post covers deploy ordering between application code and schema changes, and the blue/green safety rules.

## References

- Alembic: Operation Reference — https://alembic.sqlalchemy.org/en/latest/ops.html
- Martin Fowler: Evolutionary Database Design — https://martinfowler.com/articles/evodb.html
- "Refactoring Databases" by Scott Ambler & Pramod Sadalage (expand-contract origin)
- PostgreSQL Wiki: Don't Do This — https://wiki.postgresql.org/wiki/Don%27t_Do_This

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, Alembic, downgrade, expand-contract, rollback, SQLite
