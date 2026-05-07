---
series: database-systems-101
episode: 9
title: Replication and Backup
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Database
  - Replication
  - Backup
  - Recovery
  - HA
seo_description: Primary-replica replication, sync vs async, and PITR backups for availability and recovery.
last_reviewed: '2026-05-04'
---

# Replication and Backup

> Database Systems 101 series (9/10)

<!-- a-grade-intro:begin -->

**Core question**: When a single database dies or a disk vanishes entirely, what does it take to keep the service alive?

> Replication keeps live nodes in lock step on the same data; backups are insurance you can rewind to. Both solve availability and durability, but on different time axes. Neither is enough on its own.

<!-- a-grade-intro:end -->

## What You Will Learn

- How primary-replica replication works and what each role does
- The trade-offs between synchronous and asynchronous replication
- The kinds of backup — full, incremental, and WAL-based PITR
- How to define RPO and RTO

## Why It Matters

Failures happen. Disks die, someone runs the wrong DELETE, an entire region goes down. Replication and backup answer in advance: "when that happens, how much data do we lose, and how fast do we recover?"

> A backup whose restore procedure has never been exercised is not a backup.

## Concept at a Glance

```mermaid
flowchart LR
    A["Primary"] -- "WAL stream" --> B["Replica 1"]
    A --> C["Replica 2"]
    A -- "snapshot + WAL" --> D["Backup storage"]
    D -- "PITR" --> E["restored DB"]
```

Replication moves sideways (space), backup moves backward (time). Together they deliver availability, durability, and recovery.

## Key Terms

- **Primary/Replica**: the node that takes writes and the nodes that follow it.
- **Sync vs Async Replication**: whether a commit has to wait for a replica acknowledgment.
- **PITR (Point-in-Time Recovery)**: base backup plus WAL replay to a chosen instant.
- **RPO (Recovery Point Objective)**: acceptable amount of data loss (in time).
- **RTO (Recovery Time Objective)**: acceptable amount of downtime (in time).

## Before/After

**Before — single instance, backups only**

- A disk failure loses everything since last night's backup; recovery takes 30 minutes.

**After — replica plus regular PITR backups**

- Auto-failover restores writes within 30 seconds.
- A bad DELETE can be rolled back to a five-minute granularity via PITR.

The same data is now protected by two layers of defense.

## Hands-on: Imitating Replication and PITR

### Step 1 — Configure the primary (PostgreSQL)

```ini
# postgresql.conf
wal_level = replica
max_wal_senders = 10
archive_mode = on
archive_command = 'cp %p /var/lib/pgsql/wal_archive/%f'
```

This ships the WAL out to external storage, the foundation of PITR.

### Step 2 — Create a replica

```bash
pg_basebackup -h primary.host -D /var/lib/pgsql/replica -U replicator -P -X stream
```

Take a base backup and start streaming replication. The replica continuously follows the primary's WAL.

### Step 3 — Enable synchronous replication

```ini
# postgresql.conf
synchronous_commit = on
synchronous_standby_names = 'replica1'
```

Now the primary holds COMMIT until `replica1` confirms the WAL. Zero data loss, but writes slow down whenever the replica slows down.

### Step 4 — Base backup and WAL retention

```bash
pg_basebackup -D /backup/base/$(date +%F) -Ft -z -P
ls /var/lib/pgsql/wal_archive | tail
```

The base backup is the snapshot at time t0; the WAL archive is the change log after that.

### Step 5 — PITR to an arbitrary moment

```ini
# recovery.conf or postgresql.auto.conf
restore_command = 'cp /var/lib/pgsql/wal_archive/%f %p'
recovery_target_time = '2026-05-04 03:00:00'
```

Restore the base backup, then replay WAL up to the target time. You can rewind to right before the bad DELETE.

## What to Notice in This Code

- Replication is usually **WAL streaming**. The transaction log is the replication channel.
- Sync replication reduces data loss but slows everyone down when one node lags.
- PITR requires keeping **both** base backups and WAL.
- Restore time is a function of backup size, network speed, and WAL volume.

## Five Common Mistakes

1. **Treating a replica as a backup.** A bad DELETE is replicated immediately.
2. **Never restoring a backup.** "Restorable" is only proven by simulation.
3. **Setting RPO/RTO without consensus.** Business needs and infrastructure cost have to align.
4. **Using only synchronous replication.** One slow replica halts every write. Most teams mix sync + async.
5. **Storing backups only in the same region or account.** A region or account incident wipes them all.

## How This Shows Up in Production

Most OLTP services start with "1 primary + N async replicas + regular PITR backups." Read traffic is spread across replicas, but screens that need immediate consistency read from the primary.

Incident response is rehearsed, not invented in the moment. Failover drills and backup restoration drills run on a schedule. "We have a backup" is only true when "we restored it yesterday" is also true.

## How a Senior Engineer Thinks

- They agree on RPO/RTO as numbers ("RPO 5 min, RTO 30 min").
- They actually run the restore procedure once a quarter.
- Backups live in a different region and a different account.
- Sync replication targets get their own health monitoring.
- Failover is automated, but the manual procedure is also documented.

## Checklist

- [ ] Are RPO/RTO defined explicitly?
- [ ] Are both regular backups and WAL archives in place?
- [ ] Are backups stored in a separate location?
- [ ] Was the last restore drill within six months?
- [ ] Is the failover procedure documented and automated?

## Practice Problems

1. Write one sentence describing the biggest risk of synchronous replication and one for asynchronous.
2. A bad `DELETE FROM users` ran. With only replicas (no backups), what is possible and what is not?
3. In one paragraph, explain why RPO 0 is unrealistic for many systems.

## Wrap-up and Next Steps

Replication owns availability across space, backup owns durability across time. Together they make a system that survives failures. The next post compares the same data under two very different workloads — OLTP and OLAP — and explains why analytics gets its own system.

<!-- toc:begin -->
- [What Is a Database System?](./01-what-is-a-database.md)
- [The Relational Model](./02-relational-model.md)
- [SQL and Query Processing](./03-sql-and-query-processing.md)
- [Indexes](./04-indexes.md)
- [Transactions and ACID](./05-transactions-and-acid.md)
- [Isolation Levels](./06-isolation-levels.md)
- [Normalization and Modeling](./07-normalization-and-modeling.md)
- [Query Optimization](./08-query-optimization.md)
- **Replication and Backup (current)**
- OLTP and OLAP (upcoming)
<!-- toc:end -->

## References

- [PostgreSQL — High Availability, Replication](https://www.postgresql.org/docs/current/high-availability.html)
- [PostgreSQL — Continuous Archiving and PITR](https://www.postgresql.org/docs/current/continuous-archiving.html)
- [Designing Data-Intensive Applications — Chapter 5](https://dataintensive.net/)
- [Google SRE Book — Backup and Disaster Recovery](https://sre.google/sre-book/data-integrity/)

Tags: Computer Science, Database, Replication, Backup, Recovery, HA
