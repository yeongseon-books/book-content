---
series: distributed-systems-101
episode: 2
title: "Distributed Systems 101 (2/10): Failure Models"
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
  - Failure Models
  - Crash
  - Byzantine
  - Reliability
seo_description: We classify the ways nodes and networks break in a distributed system using crash, omission, timing, and Byzantine models.
last_reviewed: '2026-05-15'
---

# Distributed Systems 101 (2/10): Failure Models

When an incident channel says "the service is down," that sentence hides several very different realities. A node may be dead, the network may be dropping packets, or the node may simply be so slow that every peer mistakes it for dead.

This is the 2nd post in the Distributed Systems 101 series.

Here we name those realities precisely so later topics such as consensus, leases, and CAP stop sounding like abstract theory and start reading like concrete design choices.


![distributed systems 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/02/02-01-concept-at-a-glance.en.png)
*distributed systems 101 chapter 2 flow overview*

## Questions to Keep in Mind

- What a failure model is and why we model failure?
- The differences between crash, omission, timing, and Byzantine?
- Why network partition deserves its own category?

## Why It Matters

If your algorithm does not state how nodes break, you cannot reason about its correctness or its cost. Raft, Paxos, and BFT algorithms differ because they assume different failure models. Without this vocabulary you cannot read papers or docs.

> A failure model is the price tag of an algorithm.

The further right you go, the harsher the world you assume. Harsher worlds force more expensive algorithms and more nodes.

## Key Terms

- **Crash (fail-stop)**: A node, once stopped, stays stopped.
- **Crash-recovery**: A node may crash and restart, but does not lie.
- **Omission**: A node may occasionally drop a message.
- **Timing**: A node's response may be arbitrarily slow.
- **Byzantine**: A node may lie or behave arbitrarily.
- **Network partition**: Only the links between nodes break, not the nodes themselves.
- **Fencing token**: A monotonically increasing token that invalidates stale leader writes.

## The Failure Model Spectrum

Failure models are best understood as a spectrum. The left side is the weakest assumption (nodes only stop), the right side is the strongest (nodes can lie).

```text
Crash (fail-stop)  ⊂  Crash-recovery  ⊂  Omission  ⊂  Timing  ⊂  Byzantine
────────────────────────────────────────────────────────────────────
Weak assumption (cheap)  ──────────────────────────→  Strong assumption (expensive)
```

Each level includes the previous. An algorithm that tolerates Byzantine failures naturally handles crashes too. But costs are so high that the practical principle is: choose the weakest assumption that suffices.

### Fault-Tolerance Requirements per Model

| Model | Min Nodes to Tolerate f Failures | Representative Algorithm | Operational Cost |
|---|---|---|---|
| Crash (fail-stop) | 2f + 1 | Raft, Paxos | Low |
| Crash-recovery | 2f + 1 | Raft (log replay) | Low–Medium |
| Omission | 2f + 1 | Retransmission protocols | Medium |
| Byzantine | 3f + 1 | PBFT, HotStuff | High |

A 5-node Raft cluster tolerates f=2 (two simultaneous crashes). To tolerate Byzantine with 5 nodes, f=1 is the maximum — you need more nodes for equivalent resilience.

## Before/After

**Before — "just assume it died"**

```text
treating every failure the same forces algorithms to over-pay
```

**After — explicit failure model**

```text
crash only -> Raft / Paxos
byzantine  -> BFT (an order of magnitude more expensive)
```

Different assumptions, different costs.

## Hands-on: Simulate Each Failure

### Step 1 — Simulate a crash

```python
# 1_crash.py
import os, sys
def handler():
    print("doing work")
    os._exit(1)  # cleanly dies
handler()
```

Under this model, other nodes assume "once dead, dead forever." The failure detector is simple.

### Step 2 — Simulate omission

```python
# 2_omission.py
import random
def send(msg):
    if random.random() < 0.1:
        return  # drop with 10% probability
    transport.send(msg)
```

From here on you need retries, sequence numbers, and acknowledgements.

### Step 3 — Simulate timing (slow)

```python
# 3_slow.py
import time, random
def handle(req):
    if random.random() < 0.05:
        time.sleep(10)  # 5% chance of being very slow
    return process(req)
```

A "slow node" and a "dead node" look identical from the outside. That is the limit of timeout-based failure detectors.

### Step 4 — Simulate Byzantine behavior

```python
# 4_byzantine.py
def vote(question):
    real_answer = compute(question)
    return not real_answer if is_malicious() else real_answer
```

Under this model majority voting is not enough; you need signed messages or 3f+1 nodes.

### Step 5 — Simulate a network partition

```bash
# 5_partition.sh (linux)
sudo iptables -A INPUT -s 10.0.0.5 -j DROP
sudo iptables -A OUTPUT -d 10.0.0.5 -j DROP
# restore
sudo iptables -F
```

A partition is the special state where "nodes are alive but cannot see each other." Episode 4 (CAP) lives right here.

## Crash-Recovery: The Most Common Model in Practice

Pure fail-stop (once dead, dead forever) is a theoretical model. Real servers crash and come back. An OOM kill followed by a systemd restart, or a VM resurrected on another host. The node must remember how far it progressed.

```python
# Safe state restoration under crash-recovery
import json
from pathlib import Path

WAL_PATH = Path("/var/lib/myapp/wal.jsonl")

def append_wal(entry: dict) -> None:
    """Write to disk before applying to memory."""
    with open(WAL_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
        f.flush()
        import os; os.fsync(f.fileno())  # guarantee disk persistence

def recover_from_wal() -> list[dict]:
    """On restart, read WAL to restore last state."""
    entries = []
    if WAL_PATH.exists():
        for line in WAL_PATH.read_text().splitlines():
            entries.append(json.loads(line))
    return entries
```

WAL (Write-Ahead Log) is the fundamental tool of the crash-recovery model: write to disk first, apply to memory, replay WAL on restart. PostgreSQL, etcd, and Kafka all use this pattern.

## Failure Detector Limits and Trade-offs

In asynchronous systems, a perfect failure detector is impossible — proven by FLP impossibility (1985). In practice you trade off between two types of errors:

| Error Type | Meaning | Consequence |
|---|---|---|
| False positive | Mark a live node as dead | Unnecessary failover, re-election, traffic redistribution |
| False negative | Mark a dead node as alive | Lost requests, timeout accumulation, user errors |

Shorter timeouts increase false positives; longer timeouts increase false negatives. This relationship cannot be eliminated — only managed.

### Adaptive Timeout Implementation

```python
# adaptive_timeout.py
import time
from collections import deque

class AdaptiveTimeout:
    """Dynamically adjusts timeout based on measured RTT samples."""
    def __init__(self, initial_ms: float = 500, safety_factor: float = 4.0):
        self._samples: deque[float] = deque(maxlen=100)
        self._timeout_ms = initial_ms
        self._safety_factor = safety_factor

    def record_rtt(self, rtt_ms: float) -> None:
        self._samples.append(rtt_ms)
        if len(self._samples) >= 10:
            avg = sum(self._samples) / len(self._samples)
            std = (sum((x - avg) ** 2 for x in self._samples) / len(self._samples)) ** 0.5
            self._timeout_ms = avg + self._safety_factor * std

    @property
    def timeout_ms(self) -> float:
        return self._timeout_ms
```

This follows the same principle as TCP RTO calculation. Using mean RTT + 4×stddev as the timeout absorbs normal latency variance while still detecting real failures quickly.

## The Reality of Network Partitions

A network partition means "all nodes are alive but cannot see each other." Unlike node failure, partitions can be asymmetric:

```text
Symmetric partition:   A <-> B communication blocked both ways
Asymmetric partition:  A -> B works, B -> A blocked

Example: 3 nodes {A, B, C}
    A <-> B normal
    A <-> C normal
    B <-> C severed  <- B and C may each conclude the other is dead
```

In such partial partitions, if each node independently decides "the other is dead," split-brain follows. B declares itself leader without C, and C declares itself leader without B. Result: two leaders, two truths.

### Design Choices During Partition

| Choice | Description | Representative Systems |
|---|---|---|
| CP — reject writes | Refuse writes during partition, maintain consistency | etcd, ZooKeeper, Spanner |
| AP — accept writes | Accept writes during partition, resolve conflicts later | Cassandra, DynamoDB |
| Hybrid | Apply CP or AP per API | Most production systems |

In practice, entire systems are rarely purely CP or AP. Payment APIs use CP while product-catalog reads use AP — hybrids are the norm. Episode 4 (CAP) covers this in detail.

## Failure Models and Testing: Chaos Engineering Foundations

Once you name the failure model, you can systematically build tests for it:

| Failure Model | Injection Method | Verification Target |
|---|---|---|
| Crash | `kill -9`, pod delete | Leader re-election time, request error rate |
| Omission | `tc netem loss 10%` | Retransmission success rate, duplicate handling |
| Timing | `tc netem delay 500ms 200ms` | P99 response, timeout ratio |
| Byzantine | Response-tampering proxy | Data integrity, audit log |
| Partition | `iptables DROP` | Split-brain occurrence, recovery time |

```bash
# Fault injection with tc (Linux)
# Inject 10% packet loss + 200ms delay
sudo tc qdisc add dev eth0 root netem delay 200ms loss 10%

# Run tests
python3 -m pytest tests/integration/test_under_failure.py -v

# Clean up
sudo tc qdisc del dev eth0 root
```

Including these tests in CI lets you repeatedly verify "under failure model X, does the system recover within Y seconds?" Netflix's Chaos Monkey, AWS FIS, and Gremlin are all built on this principle.

## Failure Detection Pattern Comparison

The way a system detects failure also varies by failure model:

| Pattern | Behavior | Advantage | Disadvantage |
|---|---|---|---|
| Heartbeat | Periodic signal; failure assumed on miss | Simple to implement | False positive risk |
| Lease | Auto-release on expiry | Time-based safety guarantee | Requires clock synchronization |
| Gossip | Nodes propagate each other's status | No single point of failure | Slow convergence |
| Accrual (φ) | Outputs suspicion as a continuous value | Tunable threshold | Complex implementation |

Cassandra uses Gossip + Accrual φ. etcd/Raft uses Heartbeat + Lease. Regardless of the combination, the false positive/negative trade-off remains.

## Operational Scenario: Incidents from Misidentified Failure Models

A common production sequence:

1. Network latency spikes temporarily (timing failure).
2. Timeout-based failure detector declares the leader "dead" (false positive).
3. A new leader is elected; the old leader recovers.
4. Momentarily two leaders accept writes simultaneously (split-brain).
5. Some client requests reach the old leader, producing conflicting data.

Root cause: "slow" was misidentified as "dead." Preventive measures:

- **Fencing token**: a monotonically increasing token that invalidates stale-leader writes.
- **Adaptive timeout**: measurement-based dynamic timeout instead of a fixed value.
- **Term verification**: every write request includes the current term number; writes from a prior term are rejected.

```python
# Fencing token verification
def write_with_fence(key: str, value: str, fence_token: int) -> bool:
    current_fence = db.get_fence_token(key)
    if fence_token < current_fence:
        return False  # stale leader write — reject
    db.put(key, value, fence_token=fence_token)
    return True
```

## Real-System Failure Model Choices

| System | Failure Model Assumed | Fault Tolerance | Design Consequence |
|---|---|---|---|
| etcd / Raft | Crash-recovery | 2f+1 (typically 3 or 5) | WAL + snapshot restore, leader election |
| Cassandra | Crash + Partition | QUORUM setting | Gossip-based detection, hinted handoff |
| ZooKeeper | Crash-recovery | 2f+1 | Sessions + ephemeral nodes for failure propagation |
| Bitcoin | Byzantine | 50% hash power | PoW, longest-chain rule |
| Spanner | Crash + Timing | 2f+1 | TrueTime makes clock uncertainty explicit |
| Kafka | Crash-recovery | ISR-based | Writes allowed only while min ISR maintained |

Notable: only Bitcoin assumes Byzantine. The rest all assume "nodes do not lie" — because inside a datacenter, operators control the nodes. Only systems with external participants pay Byzantine costs.

### Kafka ISR: Crash-Recovery in Practice

Kafka implements crash-recovery through the ISR (In-Sync Replicas) concept:

```text
Topic: orders, Partition 0
Leader: broker-1
ISR: [broker-1, broker-2, broker-3]

1. broker-3 falls behind replication for 10 seconds
2. Leader removes broker-3 from ISR
   ISR: [broker-1, broker-2]
3. min.insync.replicas=2, so writes continue
4. broker-3 recovers → catches up log → rejoins ISR
   ISR: [broker-1, broker-2, broker-3]
```

If ISR drops below `min.insync.replicas`, producers receive `NotEnoughReplicasException`. This is how Kafka prevents data loss during crash-recovery scenarios.

## Failure Model Documentation Template

Explicitly documenting the failure model ensures the entire team reasons from the same assumptions:

```yaml
# failure-model.yaml
service: payment-gateway
failure_model:
  node: crash-recovery
  network: partition-possible
  byzantine: not-assumed
  rationale: >
    Internal datacenter operation — no malicious nodes assumed.
    Nodes may crash and restart (OOM / deploy), hence crash-recovery.

detection:
  method: heartbeat
  interval_ms: 500
  timeout_ms: 2000
  false_positive_action: fencing_token_check

partition_policy:
  write: reject_without_quorum
  read: allow_stale_with_header
  recovery: log_replay_then_reconcile
```

When this document exists, new engineers can immediately find answers to "why 3 nodes?", "why 2-second timeout?", and "why reject writes during partition?"

## Monitoring Metrics for Failure Model Validation

Once the failure model is set, you must continuously verify that it matches reality:

| Category | Metric | Meaning |
|---|---|---|
| Crash detection | Leader re-election count/time | More frequent than expected → adjust timeout |
| Omission | Retransmission rate, ACK miss rate | Network quality degradation signal |
| Timing | P99/P99.9 response time | Tail latency approaching timeout → danger zone |
| Partition | Node-to-node connectivity matrix | Early detection of asymmetric partitions |
| Recovery | WAL restore time, ISR rejoin time | Meeting recovery SLO |

```python
# Prometheus metric examples
from prometheus_client import Counter, Histogram

leader_elections = Counter(
    "leader_elections_total",
    "Number of leader elections triggered",
)

detection_latency = Histogram(
    "failure_detection_seconds",
    "Time from actual failure to detection",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
)

false_positives = Counter(
    "false_positive_detections_total",
    "Nodes incorrectly marked as failed",
)
```

A spike in false-positive count means the timeout should increase. Frequent leader elections signal a network-quality investigation. Validating failure-model assumptions against real data is a core sign of operational maturity.

## What to Notice in This Code

- The same "error" comes in different flavors with different responses.
- Omission and timing can only be distinguished by timeout (and not exactly).
- Byzantine costs an order of magnitude more.
- Partition is a link-level event, not a node-level one.

## Five Common Mistakes

1. **Assuming every failure is a crash.** Algorithms converge incorrectly when the network breaks partially.
2. **Setting timeouts too short.** You will mark live nodes dead (false suspicion).
3. **Reaching for Byzantine everywhere.** Costs explode.
4. **Ignoring partition.** It is a daily event in cloud environments.
5. **Assuming the failure detector is perfect.** A perfect detector is impossible in an asynchronous model.

## How This Shows Up in Production

Most internet services assume crash + partition (CFT). Finance and blockchain assume Byzantine (BFT, PBFT, Tendermint). The algorithm choices in Kubernetes, Spanner, and Cassandra all explicitly state which failure model they target. For example, Kubernetes' etcd uses Raft (crash-recovery assumption), while Cassandra uses gossip-based failure detection to maintain availability even during partitions. Systems that do not name their failure model implicitly assume crash-stop — and behave unpredictably when partitions occur.

## How a Senior Engineer Thinks

- They pick the algorithm that needs the weakest assumption that suffices (no needless BFT).
- They are aware that failure detectors are always approximate.
- They treat partition as a daily occurrence.
- They derive timeout values from network measurements.
- They trust only docs and RFCs that name the failure model explicitly.

## Checklist

- [ ] Can you state the difference between crash and omission in one line?
- [ ] Can you explain why Byzantine is more expensive?
- [ ] Can you say how partition differs from node failure?
- [ ] Do you know why timeout-based detectors are imperfect?
- [ ] Can you say which model your system assumes?
- [ ] Do you have a failure-model documentation for your service?

## Practice Problems

1. Write down which model your service assumes: crash, omission, or Byzantine.
2. List two metrics you must measure to choose a timeout (e.g., p99 latency).
3. Research one mechanism that prevents split-brain when a partition occurs.

## Wrap-up and Next Steps

The failure model is the first design decision; it sets the algorithm and the operational cost. Next we look at how nodes exchange messages on top of these models — RPC and message passing.

## Answering the Opening Questions

- **What is a failure model and why must failures be modeled?**
  - A failure model is a contract specifying "how nodes can break." Without this contract, neither algorithm correctness nor cost can be discussed. Assuming only crashes requires 2f+1 nodes; assuming Byzantine requires 3f+1.
- **How do crash, omission, timing, and Byzantine differ?**
  - On the spectrum from left to right: crash only stops, omission drops messages, timing becomes arbitrarily slow, and Byzantine can lie. Each level includes the previous and costs escalate sharply.
- **Why should network partitions be treated as a separate category?**
  - A partition is a link failure, not a node failure. All nodes can be healthy yet unable to see each other, and independent decisions in this state lead to split-brain. This is exactly the core situation CAP theorem addresses.
<!-- toc:begin -->
## In this series

- [Distributed Systems 101 (1/10): What Is a Distributed System?](./01-what-is-a-distributed-system.md)
- **Failure Models (current)**
- RPC and Message Passing (upcoming)
- Consistency and CAP (upcoming)
- Replication (upcoming)
- Consensus and Raft (upcoming)
- Leader Election (upcoming)
- Message Queues and Event Sourcing (upcoming)
- Distributed Transactions (upcoming)
- Patterns for Operable Distributed Systems (upcoming)

<!-- toc:end -->

## References

- [Failure semantics (Wikipedia)](https://en.wikipedia.org/wiki/Failure_semantics)
- [Byzantine fault (Wikipedia)](https://en.wikipedia.org/wiki/Byzantine_fault)
- [Network partition (Wikipedia)](https://en.wikipedia.org/wiki/Network_partition)
- [Designing Data-Intensive Applications — chapter 8](https://dataintensive.net/)
- [FLP Impossibility — Fischer, Lynch, Paterson (1985)](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf)

Tags: Computer Science, Distributed Systems, Failure Models, Crash, Byzantine, Reliability
