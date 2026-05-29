---
series: distributed-systems-101
episode: 6
title: "Distributed Systems 101 (6/10): Consensus and Raft"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Distributed Systems
  - Consensus
  - Raft
  - Paxos
  - Replication
seo_description: Consensus is the hardest problem in distributed systems. We walk through Raft - terms, logs, commit, and quorums - in code-sized pieces.
last_reviewed: '2026-05-15'
---

# Distributed Systems 101 (6/10): Consensus and Raft

It is easy to say "the cluster should agree." It is much harder to make that sentence survive crashes, lost messages, and a leader that disappears in the middle of a write. Consensus is where distributed systems stop being intuitive and start being disciplined.

This is the 6th post in the Distributed Systems 101 series.

Here we use Raft to make the consensus problem concrete: terms, logs, quorums, and the exact point where a value becomes durable enough to trust.


![distributed systems 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/06/06-01-concept-at-a-glance.en.png)
*distributed systems 101 chapter 6 flow overview*

## Questions to Keep in Mind

- The definition of the consensus problem and its safety/liveness properties?
- The three roles in Raft (leader, follower, candidate)?
- The meaning of term, log, index, and commit?

## Why It Matters

A consensus algorithm sits at the heart of etcd, ZooKeeper, Consul, and CockroachDB. The Kubernetes control plane stands on top of etcd. Once you understand consensus, half of "why does this system behave this way?" answers itself.

> Consensus is the value of agreement in a distributed system.

A single leader receives the log and replicates it to followers. Only entries received by a majority count as committed.

## Key Terms

- **Consensus**: The problem of N nodes agreeing on a single value.
- **Term**: A monotonically increasing epoch. Each new leader gets a new term.
- **Log**: A sequence of entries, identified by index.
- **Commit**: An entry received by a majority becomes a permanent promise.
- **Quorum**: f+1 out of 2f+1, usually a majority.

## Before/After

**Before — leader decides alone**

```text
fast, but consistency breaks if the leader lies
```

**After — agreement of a majority**

```text
slightly slower, but safe even if a node dies or lies
```

A majority is the safety device of distributed systems.

## Hands-on: Raft's Core in Short Code

### Step 1 — define the state

```python
# 1_state.py
from dataclasses import dataclass, field
@dataclass
class Node:
    role: str = "follower"
    term: int = 0
    log: list = field(default_factory=list)
    commit_index: int = -1
    voted_for: int | None = None
```

term, log, commit_index — the variables on the first page of the Raft paper.

### Step 2 — election (simplified)

```python
# 2_election.py
def election_timeout(self, peers):
    self.term += 1
    self.role = "candidate"
    self.voted_for = self.id
    votes = 1
    for p in peers:
        if p.request_vote(self.term, self.id):
            votes += 1
    if votes > len(peers) // 2 + 1:
        self.role = "leader"
```

The first node to time out becomes a candidate and gathers votes. Win a majority and you become leader.

### Step 3 — log replication

```python
# 3_replicate.py
def append_entries(self, term, prev_index, entries):
    if term < self.term: return False
    if prev_index >= 0 and self.log[prev_index]["term"] != term:
        return False  # mismatch
    self.log = self.log[:prev_index+1] + entries
    return True
```

The leader sends its log to followers. Followers reject when entries do not match. Consistency is enforced via the previous index/term pair.

### Step 4 — commit

```python
# 4_commit.py
def maybe_commit(self, peers):
    for i in range(self.commit_index + 1, len(self.log)):
        acks = 1 + sum(1 for p in peers if p.match_index >= i)
        if acks > len(peers) // 2 + 1:
            self.commit_index = i
```

Once a majority has the entry, commit it. From that point on the entry never disappears.

### Step 5 — partition scenario

```python
# 5_partition.py (pseudocode)
# 5 nodes, only 2 (leader included) on one side of a partition
# - that side has no majority -> cannot elect a new leader -> cannot accept writes
# - the other side has 3 nodes -> majority -> elects a new leader -> keeps working
```

The side without a majority intentionally stops. This is the core design that prevents split-brain.

## What to Notice in This Code

- The term is monotonically increasing. Messages from old terms are always rejected.
- Order is essential to the log — matching is checked by the (index, term) pair.
- Commit is the promise that "a majority has it," not "everyone has it."
- The right answer for a partitioned side is to stop.

## Five Common Mistakes

1. **Believing one leader is enough for safety.** Elections must be correct for safety.
2. **Treating "leader received it" as commit.** Commit is the moment a majority received it.
3. **Using identical timeouts on all nodes.** Split votes happen often (Raft uses randomized timeouts).
4. **Skipping the log-matching check.** Wrong entries get committed.
5. **Assuming the partitioned side can keep working.** Without a majority it must stop.

## How This Shows Up in Production

etcd (the Kubernetes data store), Consul, ZooKeeper (ZAB, a Paxos variant), CockroachDB, and TiKV all stand on top of consensus algorithms. Database leader election, distributed locks, and configuration storage are textbook use cases.

## How a Senior Engineer Thinks

- They do not call consensus often (it is expensive — only for metadata).
- They randomize timeouts based on measurement.
- They keep the node count odd (3, 5, 7).
- They design client retries that handle leader changes safely.
- They consciously decide whether reads are leader-only or use a lease.

## Making Raft Operationally Viable

The earlier sections covered Raft's core variables (term, log, commit). Now we shift to the operational layer. In production, knowing the algorithm is not the challenge — the challenge is making the same correct decisions during every failure. That requires connecting election, replication, safety, snapshots, membership changes, and observability into a single operational model.

### Detailed Raft Protocol Flow

Raft is a leader-centric protocol. All writes pass through the leader, followers replicate the leader's log, and the candidate role appears only briefly when the leader seems unhealthy.

```text
1) follower waits for AppendEntries (heartbeat)
2) if heartbeat is missing for election-timeout duration, transition to candidate
3) candidate increments term by 1, broadcasts RequestVote
4) win a majority of votes → become leader
5) leader appends client writes as log entries, replicates to followers
6) once majority replication is confirmed, advance commit index
7) apply committed entries to the state machine
```

The critical insight is the "write success response point." A write stored only in the leader's local memory is not a success. Success is when the entry is committed after majority replication. Without this distinction, a leader crash immediately causes data loss.

### Leader Election: Term Numbers, Voting Rules, and Split Vote Handling

In Raft, the term is the logical version of time. A node rejects messages from terms smaller than its own, and immediately steps down to follower upon receiving a message from a higher term. This simple rule resolves the "stale leader" problem.

The voting rule combines two constraints:

1. A node votes only once per term.
2. A node votes only if the candidate's log is sufficiently up-to-date.

The second rule is critical. If you simply vote for "whoever asks first," a candidate with a stale log could become leader. Raft compares `lastLogTerm` and `lastLogIndex` to verify the freshness condition.

Split vote occurs when multiple candidates appear simultaneously and none wins a majority. Two mechanisms mitigate this:

- Randomized election timeout (e.g., 150ms–300ms)
- Heartbeat interval kept well below election timeout (e.g., 50ms)

```yaml
raft_timing:
  heartbeat_interval_ms: 50
  election_timeout_min_ms: 150
  election_timeout_max_ms: 300
  pre_vote: true
```

`pre_vote` is useful for preventing a node that was temporarily partitioned from unnecessarily bumping the term when it rejoins.

### Log Replication Safety: Why the index+term Pair Matters

Raft's safety comes from comparing both the log position (index) and the creation time of that position (term). When a follower fails the `prevLogIndex`/`prevLogTerm` check, the leader backs up one entry at a time to find the matching point, then re-sends everything after it.

This process looks expensive but is effective:

- It cleans up divergent log branches.
- It preserves committed entries.
- It restores the log to a single linear history after leader changes.

The leader tracks a per-follower `next_index` to drive automatic re-synchronization:

```python
# raft_leader_sync.py
def replicate_to_follower(leader, follower_id):
    next_idx = leader.next_index[follower_id]
    prev_idx = next_idx - 1
    prev_term = leader.log[prev_idx]["term"] if prev_idx >= 0 else 0
    entries = leader.log[next_idx:]

    ok = send_append_entries(
        follower_id=follower_id,
        term=leader.current_term,
        prev_log_index=prev_idx,
        prev_log_term=prev_term,
        entries=entries,
        leader_commit=leader.commit_index,
    )

    if ok:
        leader.match_index[follower_id] = next_idx + len(entries) - 1
        leader.next_index[follower_id] = leader.match_index[follower_id] + 1
    else:
        leader.next_index[follower_id] = max(0, next_idx - 1)
```

### Commit Rules and Linearizability

Raft's "majority replication" alone is not sufficient — strictly speaking, only entries from the *current term* that achieve majority replication allow the commit index to advance safely. This condition prevents accidentally committing incomplete entries from a previous term.

The read path also requires design:

- Strong consistency reads: confirm leadership (read index, quorum check) before responding
- Relaxed reads: allow follower stale reads (with explicit staleness bounds)

Both writes and reads should document "under which consistency contract was this response issued" in the API specification. This reduces confusion during failures.

The standard approach for linearizable reads is ReadIndex. The leader sends a heartbeat to a quorum to confirm it is still leader, then returns the read result from state applied up to the current commit index. This avoids adding a write log entry, keeping performance overhead low while guaranteeing linearizability.

```python
# read_index.py — ReadIndex-based linearizable read flow (pseudocode)
def linearizable_read(leader, peers, key):
    # 1) record current commit index
    read_index = leader.commit_index
    # 2) confirm leadership via quorum heartbeat
    acks = 1
    for p in peers:
        if p.confirm_leader(leader.current_term):
            acks += 1
    if acks <= len(peers) // 2:
        raise NotLeaderError("quorum confirmation failed")
    # 3) wait until state machine has applied up to read_index
    wait_until_applied(read_index)
    return state_machine.get(key)
```

Lease-based reads skip quorum confirmation within the heartbeat period to reduce latency, but they risk stale reads when clock skew is large. NTP synchronization quality must be established beforehand.

### Log Compaction and Snapshots

Raft logs grow indefinitely, making compaction essential. The standard strategy is to save a state-machine snapshot up to a certain commit index, then truncate all log entries before that point.

```yaml
snapshot:
  trigger:
    committed_entries: 10000
    wal_size_mb: 64
  retention:
    keep_last_snapshots: 3
  restore:
    verify_checksum: true
```

Three critical points about snapshots:

1. Always persist `last_included_index` and `last_included_term` alongside the snapshot.
2. New log replication from the leader must continue even while a snapshot transfer is in progress.
3. During recovery, the snapshot and subsequent incremental logs must be stitched together precisely.

For new nodes whose initial sync is slow, sending a snapshot first and then letting them catch up with tail logs is far faster than replaying the entire log from the beginning.

For systems with large snapshots, the InstallSnapshot RPC is split into chunks, each tagged with an offset and a done flag so the follower can reassemble them in order. During this process, the leader resets that follower's `next_index` to `last_included_index + 1`.

```python
# install_snapshot.py — snapshot transfer flow (pseudocode)
CHUNK_SIZE = 1024 * 1024  # 1 MB

def send_snapshot(leader, follower_id, snapshot_path):
    with open(snapshot_path, "rb") as f:
        offset = 0
        while True:
            chunk = f.read(CHUNK_SIZE)
            done = len(chunk) < CHUNK_SIZE
            send_install_snapshot(
                follower_id=follower_id,
                term=leader.current_term,
                last_included_index=leader.snapshot_index,
                last_included_term=leader.snapshot_term,
                offset=offset,
                data=chunk,
                done=done,
            )
            offset += len(chunk)
            if done:
                break
    leader.next_index[follower_id] = leader.snapshot_index + 1
```

### Raft vs Paxos

Both algorithms solve consensus, but from different design perspectives. For education and operational automation, Raft lowers the understanding and implementation barrier.

| Aspect | Raft | Paxos |
| --- | --- | --- |
| Core structure | Leader-centric log replication | Proposer/acceptor-based consensus |
| Understandability | Relatively straightforward | Relatively difficult |
| Log replication model | Built into the algorithm | Requires Multi-Paxos extension |
| Implementation docs | Roles and states are explicit | Many variants, implementations differ |
| Leader change visibility | Clear via term and election events | Tracking complexity varies by implementation |

The point is not "Raft is always superior" but rather choosing the model that lets your team make consistent decisions during failures. For most application metadata layers, Raft's operational simplicity is a significant advantage.

In practice, teams choose Paxos when optimizing for single-value consensus (e.g., a one-shot leader election), or when a stable Paxos implementation (Google Chubby, Spanner) is already running inside the organization. For new systems, embedding a Raft library (etcd/raft, hashicorp/raft) drastically reduces operational complexity compared to implementing Multi-Paxos from scratch.

### Cluster Sizing Guide

Node count is a tradeoff between fault tolerance and write latency.

| Nodes | Fault tolerance (f) | Quorum | Write latency characteristics |
| --- | --- | --- | --- |
| 3 | 1 | 2 | Fastest; tolerates only a single failure |
| 5 | 2 | 3 | Recommended for general production |
| 7 | 3 | 4 | Consider for geo-distributed deployments; higher latency |

Using an even number of nodes (4 or 6) does not increase fault tolerance compared to the next-lower odd number, while increasing quorum cost. For example, a 4-node cluster tolerates only 1 failure (same as 3 nodes), but requires a quorum of 3 — meaning every write waits on one extra node. Odd-numbered clusters are more cost-effective.

In geo-distributed deployments, quorum response latency is determined not by the farthest node but by the "farthest node within the majority." A 5-node cluster placed as Seoul 2, Tokyo 2, Singapore 1 means the quorum of 3 is bounded by Seoul-to-Tokyo latency; the Singapore node does not affect the write path.

### etcd/Raft Operational Patterns

The fact that the Kubernetes control plane depends on etcd means "a Raft failure is a control-plane failure." Operating etcd therefore requires managing the cluster lifecycle and Raft parameters together.

```yaml
name: infra-etcd-1
data-dir: /var/lib/etcd
listen-client-urls: https://0.0.0.0:2379
advertise-client-urls: https://10.0.0.11:2379
listen-peer-urls: https://0.0.0.0:2380
initial-advertise-peer-urls: https://10.0.0.11:2380
initial-cluster: infra-etcd-1=https://10.0.0.11:2380,infra-etcd-2=https://10.0.0.12:2380,infra-etcd-3=https://10.0.0.13:2380
initial-cluster-state: existing
initial-cluster-token: infra-etcd-prod
heartbeat-interval: 100
election-timeout: 1000
snapshot-count: 10000
auto-compaction-mode: revision
auto-compaction-retention: "5000"
```

Recommended operational patterns:

1. Maintain odd-numbered nodes (3 or 5); avoid distributing them too far geographically.
2. Prioritize disk latency and fsync performance management.
3. Run regular snapshot backups and recovery rehearsals as separate procedures.
4. Design client retries with idempotency keys.

### Membership Changes: Why Joint Consensus Is Necessary

Adding or removing nodes from a Raft cluster is not a simple list edit. The moment the majority set changes, safety can be violated. Joint Consensus prevents this.

The core idea is to temporarily require "a majority from both the old configuration C_old and the new configuration C_new" during the transition:

```text
Step 1) C_old -> C_old,new (joint configuration)
Step 2) Commit log entries under C_old,new
Step 3) Final transition to C_new
```

This approach prevents split-brain where two different majority sets independently recognize a leader during the transition. Operationally, runbooks should restrict configuration changes to "one node at a time" for safety.

### Raft Health Monitoring: Prometheus Metrics

Raft's explicit internal state makes metric-based operations a natural fit. The following metrics are the minimum baseline for most etcd/raft-family systems.

```text
Leader stability: leader_changes_seen_total
Proposal throughput: proposals_committed_total, proposals_failed_total
Latency: peer_round_trip_time_seconds
Backpressure: backend_commit_duration_seconds, wal_fsync_duration_seconds
State: has_leader (0/1), is_learner (0/1)
```

A starter Prometheus alerting rule set:

```yaml
groups:
  - name: raft-health
    rules:
      - alert: RaftLeaderFlapping
        expr: increase(etcd_server_leader_changes_seen_total[10m]) > 3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Excessive leader changes detected"

      - alert: RaftNoLeader
        expr: max(etcd_server_has_leader) == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Cluster has lost its leader"

      - alert: RaftProposalFailures
        expr: rate(etcd_server_proposals_failed_total[5m]) > 0
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Consensus proposal failures are sustained"
```

An important operational habit: do not fix alert thresholds at static values. Re-calibrate them periodically based on steady-state distributions (p95/p99).

### Failure Response Sequence

Raft failure response is far safer when following a fixed sequence rather than improvising.

1. Check election stability via `has_leader` and leader-change count.
2. Verify write-path damage via `proposals_failed_total` increase.
3. Separate the cause into election issues vs. I/O issues by examining disk/network latency metrics.
4. On majority loss, explicitly enforce a write-rejection policy.
5. After recovery, hold off traffic re-admission until backlog application completes.

```shell
# etcd cluster health check commands
etcdctl endpoint status --cluster -w table
etcdctl endpoint health --cluster
etcdctl alarm list
```

Fixing this sequence into a runbook ensures the same decision quality regardless of who is on-call. The real-world stability of a consensus system depends more on operational consistency than on the algorithm itself.

### Client Retries and Idempotency

When a leader changes, clients temporarily receive no response. Naive retries cause duplicate writes, so idempotency keys must be part of the design.

```python
# idempotent_write.py
from fastapi import FastAPI, HTTPException

app = FastAPI()
applied_requests: dict[str, dict] = {}

@app.post("/write")
async def write(idempotency_key: str, payload: dict):
    if idempotency_key in applied_requests:
        return {"status": "already_applied", "result": applied_requests[idempotency_key]}
    result = await submit_to_raft_leader(idempotency_key, payload)
    if result is None:
        raise HTTPException(status_code=503, detail="leader unavailable")
    applied_requests[idempotency_key] = result
    return {"status": "committed", "result": result}
```

The key principle: if the same key arrives twice, the second request does not apply the operation — it simply returns the prior result. Keys are generated client-side, and applied entries expire via TTL to prevent unbounded memory growth.

### Implementation Selection and Testing Strategy

Implementing Raft from scratch is rare, but when choosing a library these criteria help:

| Criterion | What to verify |
| --- | --- |
| Log storage | Are WAL and snapshots separated? |
| Membership changes | Joint Consensus or single-server approach support |
| Pre-vote | Prevention of term explosion after partition recovery |
| Learner role | Read-only nodes that replicate logs without voting |
| Benchmarks | Write throughput and p99 latency including fsync |

Testing strategy should focus on failure paths rather than happy paths:

```python
# raft_chaos_test.py (pseudocode)
import random

def test_leader_crash_during_commit():
    """If the leader dies just before majority replication,
    the new leader must NOT commit that entry."""
    cluster = create_cluster(nodes=5)
    leader = cluster.get_leader()
    # write one entry to leader only, crash before replication
    leader.append_local_only(entry={"cmd": "set x=1"})
    cluster.kill(leader)
    new_leader = cluster.wait_for_election()
    # the new leader's commit index must not include that entry
    assert not new_leader.has_committed({"cmd": "set x=1"})
```

Choosing a consensus implementation without such failure-scenario tests risks data loss from unexpected edge cases in production. This is exactly why tools like Jepsen exist.

## Checklist

- [ ] Can you state the definition of consensus in one line?
- [ ] Can you explain the relationship between term, log, and commit?
- [ ] Can you say how many nodes can fail in a 5-node cluster?
- [ ] Do you know how split votes are prevented?
- [ ] Do you let "etcd is on top of consensus" inform your system design?

## Practice Problems

1. Compare the fault tolerance of a 3-node and a 5-node cluster.
2. Explain how Raft's randomized election timeout reduces split votes.
3. Write one paragraph on how you would build a distributed lock with etcd.

## Wrap-up and Next Steps

Consensus is the hardest problem in distributed systems, and Raft is its human-friendly form. In the next post we cover the larger picture of choosing a leader on top of consensus — leader election.

## Answering the Opening Questions

- **What is the consensus problem, and what safety and liveness properties does it have?**
  - Consensus is the problem of making multiple nodes share decisions in the same order despite partial failures and latency. Safety means committed logs never disappear and two leaders never simultaneously confirm writes. Liveness means if a majority is alive, a new leader is eventually elected and writes progress.
- **How are Raft's three roles—leader, follower, candidate—distinguished?**
  - Follower is the default state receiving heartbeats. When heartbeats stop, it transitions to candidate and starts an election. The candidate winning majority votes becomes leader, accepting and replicating all writes.
- **What do term, log, index, and commit each mean?**
  - Term is the leadership generation number; log is the ordered list of state-change entries; index is the log position number. Commit is the promise that majority replication has made an entry "undeletable"—only committed entries are applied to the state machine.
<!-- toc:begin -->
## In this series

- [Distributed Systems 101 (1/10): What Is a Distributed System?](./01-what-is-a-distributed-system.md)
- [Distributed Systems 101 (2/10): Failure Models](./02-failure-model.md)
- [Distributed Systems 101 (3/10): RPC and Message Passing](./03-rpc-and-message-passing.md)
- [Distributed Systems 101 (4/10): Consistency and CAP](./04-consistency-and-cap.md)
- [Distributed Systems 101 (5/10): Replication](./05-replication.md)
- **Consensus and Raft (current)**
- Leader Election (upcoming)
- Message Queues and Event Sourcing (upcoming)
- Distributed Transactions (upcoming)
- Patterns for Operable Distributed Systems (upcoming)

<!-- toc:end -->

## References

- [Raft consensus algorithm](https://raft.github.io/)
- [In Search of an Understandable Consensus Algorithm (Raft paper)](https://raft.github.io/raft.pdf)
- [Paxos (Wikipedia)](https://en.wikipedia.org/wiki/Paxos_(computer_science))
- [etcd documentation](https://etcd.io/docs/)

Tags: Computer Science, Distributed Systems, Consensus, Raft, Paxos, Replication
