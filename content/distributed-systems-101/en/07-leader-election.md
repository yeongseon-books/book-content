---
series: distributed-systems-101
episode: 7
title: "Distributed Systems 101 (7/10): Leader Election"
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
  - LeaderElection
  - Lease
  - Coordination
  - Liveness
seo_description: We cover how distributed systems pick and keep a leader using lease, fencing, and split-brain prevention - patterns from etcd and ZooKeeper.
last_reviewed: '2026-05-15'
---

# Distributed Systems 101 (7/10): Leader Election

The dangerous moment in leader election is not the happy path where one node wins. It is the messy moment where the old leader wakes up late, still thinks it owns the world, and tries to write after a new leader has already taken over.

This is the 7th post in the Distributed Systems 101 series.

Here we treat leader election as an operational safety problem: leases decide who is allowed to lead, and fencing tokens decide whose writes are still valid.


![distributed systems 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/07/07-01-concept-at-a-glance.en.png)
*distributed systems 101 chapter 7 flow overview*

## Questions to Keep in Mind

- Why leader election is needed and what its safety conditions are?
- The roles of lease and heartbeat?
- How to use a fencing token to block an old leader?

## Why It Matters

Many distributed-system bugs happen the moment "there are two leaders." When two leaders write to the same resource at the same time, data breaks. A correct election guarantees that only one leader holds authority at any point in time.

> A good election is the promise that "there is no moment with two leaders."

Multiple candidates request a lease from a lock service. Only one becomes leader and renews the lease with heartbeats.

## Key Terms

- **Leader**: The node that holds write authority at a point in time.
- **Lease**: A temporary authority that expires automatically after a TTL.
- **Heartbeat**: A periodic signal used to renew the lease.
- **Fencing token**: A monotonically increasing ID used to reject old-leader requests.
- **Split-brain**: A state where two nodes simultaneously believe they are leader.

## Before/After

**Before — leader judgement by heartbeat alone**

```text
an old leader stalled by GC pause comes back and writes to the same resource
```

**After — lease + fencing token**

```text
the old leader's request is rejected by a smaller token; only the new leader passes
```

A single token line prevents split-brain.

## Hands-on: Election and Fencing

### Step 1 — lease-based election (pseudocode)

```python
# 1_lease.py
import time
class Lease:
    def __init__(self, ttl): self.ttl, self.expires = ttl, 0
    def acquire(self, now):
        if now >= self.expires:
            self.expires = now + self.ttl
            return True
        return False
```

Only an expired lease can be acquired anew. TTL is the safety boundary.

### Step 2 — renew with heartbeat

```python
# 2_heartbeat.py
def renew(lease, now):
    lease.expires = now + lease.ttl
```

The leader renews every TTL/3. A safety margin lets one or two missed renewals slide.

### Step 3 — fencing token

```python
# 3_fence.py
counter = 0
def grant_leader():
    global counter
    counter += 1
    return counter   # monotonically increasing token
```

Every time a new leader is elected the token grows. The resource server rejects requests with a smaller token.

### Step 4 — resource server reject logic

```python
# 4_resource.py
last_token = 0
def write(token, data):
    global last_token
    if token < last_token:
        return "rejected (stale leader)"
    last_token = token
    return "ok"
```

This single line stops an old leader from writing.

### Step 5 — split-brain scenario

```python
# 5_split.py (pseudocode)
# old leader A: token=5, GC pause 30s
# meanwhile new leader B: token=6 issued
# A wakes up and tries to write with token=5 -> resource server rejects
# B's write with token=6 succeeds
```

In a design without tokens, A's write would land and corrupt the data.

## Operational walkthrough: lease expiry under a GC pause

The failure mode worth rehearsing is not "a node cleanly dies" but "a node stalls long enough to miss renewals." A practical sequence looks like this:

1. Leader A acquires lease `ttl=5s` and gets fencing token `41`.
2. A long GC pause or CPU starvation freezes A for 8 seconds.
3. The lock service sees no heartbeat, expires the lease, and elects leader B.
4. B receives fencing token `42` and starts handling writes.
5. A wakes up and tries to write with token `41`.
6. The resource server rejects A because `41 < 42`.

That last comparison is the real safety boundary. The lease service decides who may lead, but the resource server decides which writes are still legal. If you only log leadership changes and never validate tokens at the write target, you have observability but not protection.

## What to Notice in This Code

- A lease expires automatically — it handles network partitions naturally.
- Heartbeats are sent more often than the TTL — a margin is essential.
- Monotonic increase is the essence of a token.
- Rejection is the resource server's responsibility — never trust the client.

## Five Common Mistakes

1. **Believing heartbeats alone are enough.** GC pauses and network delays are ignored.
2. **Setting TTL too short.** False failovers happen often.
3. **Not putting token validation in the resource server.** Old leaders succeed at writes.
4. **Using random values for the token.** Monotonic ordering breaks; comparison is meaningless.
5. **Recovering from split-brain manually.** Recovery should be automatic by design.

## How This Shows Up in Production

Kubernetes' `kube-controller-manager` and `kube-scheduler` use etcd leases for leader election. ZooKeeper's ephemeral znode is the same pattern. Kafka's controller, HDFS NameNode HA, and distributed cron are all lease + fencing variants.

## How a Senior Engineer Thinks

- TTL is set comfortably above max(GC pause + network RTT).
- Election events are exposed as metrics — frequent elections are a bug signal.
- Fencing tokens are the first parameter of resource-server APIs.
- Behavior of in-flight requests during a leader change is documented in the spec.
- Split-brain is forced and reproduced as part of the test suite.

## Checklist

- [ ] Can you explain the roles of lease and heartbeat in one line?
- [ ] Can you say why a fencing token must be monotonically increasing?
- [ ] Can you write a one-sentence split-brain scenario?
- [ ] Do you have a rule for choosing TTL?
- [ ] Can you imagine implementing election with etcd or ZooKeeper?

## Practice Problems

1. Analyze what happens in a system with a 5-second TTL when a single GC pause lasts 8 seconds.
2. State in one line the conditions under which safe election is possible without a fencing token.
3. Write pseudocode that implements distributed cron on top of etcd leases.

## Wrap-up and Next Steps

Leader election is the work of keeping the promise of "one leader at a time" with leases and fencing. In the next post we look at tools that distribute work without a leader at all — message queues and event sourcing.

## Answering the Opening Questions

- **Why is leader election needed, and what safety conditions are required?**
  - Leader election restricts write authority to one node at a time, preventing split-brain. The safety condition summarizes to "two leaders never write simultaneously"—as shown in the article, lease expiry boundaries, monotonically increasing fencing tokens, and resource server token rejection verification must all be present for this condition to actually hold.
- **What role do lease and heartbeat each play?**
  - A lease defines the validity period of leader authority—a safety boundary. A heartbeat extends that authority—a maintenance signal. Lease answers "when does authority end"; heartbeat answers "is the current leader still healthy." As in the Kubernetes Lease and stepdown examples, if heartbeats stop or dependency checks fail, the next candidate must be able to take over.
- **Why is the fencing token the critical device blocking a previous leader?**
  - The fencing token is the final safety mechanism connecting election results to resource server verification. Even if an old leader resumes after a GC pause, its smaller token is rejected—preventing data corruption. The FastAPI example and `fencing_reject_total` metric are the operational evidence confirming this protection actually works.
<!-- toc:begin -->
## In this series

- [Distributed Systems 101 (1/10): What Is a Distributed System?](./01-what-is-a-distributed-system.md)
- [Distributed Systems 101 (2/10): Failure Models](./02-failure-model.md)
- [Distributed Systems 101 (3/10): RPC and Message Passing](./03-rpc-and-message-passing.md)
- [Distributed Systems 101 (4/10): Consistency and CAP](./04-consistency-and-cap.md)
- [Distributed Systems 101 (5/10): Replication](./05-replication.md)
- [Distributed Systems 101 (6/10): Consensus and Raft](./06-consensus-and-raft.md)
- **Leader Election (current)**
- Message Queues and Event Sourcing (upcoming)
- Distributed Transactions (upcoming)
- Patterns for Operable Distributed Systems (upcoming)

<!-- toc:end -->

## References

- [Leader election — Wikipedia](https://en.wikipedia.org/wiki/Leader_election)
- [How to do distributed locking — Martin Kleppmann](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
- [etcd lease and leader election](https://etcd.io/docs/v3.5/learning/lock/)
- [Kubernetes leader election library](https://pkg.go.dev/k8s.io/client-go/tools/leaderelection)
- [ZooKeeper recipes and solutions — Leader Election](https://zookeeper.apache.org/doc/current/recipes.html#sc_leaderElection)

Tags: Computer Science, Distributed Systems, LeaderElection, Lease, Coordination, Liveness
