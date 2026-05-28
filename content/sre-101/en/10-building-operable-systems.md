---
series: sre-101
episode: 10
title: "SRE 101 (10/10): Building Operable Systems"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - SRE
  - Operability
  - Architecture
  - Reliability
  - Engineering
seo_description: A capstone guide to building operable systems covering observability, automation, safe change, resilience, and integrated operational design
last_reviewed: '2026-05-14'
---

# SRE 101 (10/10): Building Operable Systems

Many teams write detailed functional requirements but leave operational requirements as "later" problems. Logging gets added after the first blind-spot incident, rollback procedures appear after the first stuck deployment, and automation materializes only after repeating the same painful steps enough times. That delay is expensive because operability compounds—systems that are easy to observe, change safely, recover, and automate become progressively easier to improve, while systems that are not become progressively harder to trust.

Operable systems do not happen by accident. They require deliberate design: failures must be visible quickly, changes must be reversible safely, partial failures must not cascade into total outages, and repetitive procedures must live as code rather than tribal knowledge.

This is the final post in the SRE 101 series. It gathers the earlier ideas into one design lens: observability, safe change, resilience, and automation should be built into a system the same way functional behavior is.

![sre 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/10/10-01-concept-at-a-glance.en.png)
*sre 101 chapter 10 flow overview — how observability, automation, safe change, and resilience interlock within a single system*

## Questions to Keep in Mind

- Why is operability a design property instead of a post-launch enhancement?
- Why do observability, automation, safe change, and resilience need to be judged together?
- What should a team ask first when auditing whether a system is truly operable?

## Why This Topic Matters

A feature without operability returns as debt. The feature may ship successfully once, but every subsequent change, incident, and debugging session becomes more expensive than it needed to be. Logs are missing, metric names are inconsistent, rollback is manual, and incident response depends on one person's memory.

Strong teams design the operational path on purpose. They ask not only "does this feature work?" but also "can we understand it, roll it back, recover it, and automate it?" When those questions are answered at design time, operational cost stays flat as the system grows.

> Operability is not decoration bolted on after launch—it is a quality attribute designed alongside features from the start.

## Key Terms

| Term | Definition | Where it shows up |
| --- | --- | --- |
| operability | How easy it is to operate and troubleshoot the system | A quality property of the feature itself |
| observability | Ability to infer internal state from external signals | The starting point of all debugging |
| safe change | Small, reversible change practices (canary + rollback) | Reduces deployment risk |
| resilience | Ability to endure and recover from partial failure | Prevents cascade failures |
| runbook-as-code | Operational procedures expressed as executable code | Replaces human-dependent procedures |

## Why Operability Must Be Designed With Features

When teams try to bolt operational concerns onto a feature after development is done, compromise is inevitable. Logs are missing, metric names are inconsistent across services, rollback is manual, and incident response depends on one person's memory. In this state, every new feature increases operational complexity alongside it.

When operability is treated as a requirement from the start, the design questions change. What metrics should this feature emit? How does it degrade on failure? Can it deploy via canary? Can it roll back within minutes? Can repetitive operational steps be expressed as code? These questions enter the design phase early and prevent costly retrofits.

## Why the Four Axes Must Be Viewed Together

Without observability, you cannot read problems. Without safe change, small mistakes propagate widely. Without resilience, partial failure cascades into total outage. Without automation, team time stays trapped in repetitive manual work. Strength in one axis alone does not produce operability.

When running an operability audit, examine all axes simultaneously. This reveals where the system is weakest. Typically, weakness in one axis transfers burden to another—missing observability forces manual investigation, which consumes the time that could go toward automation.

## Operable System Characteristics

Operable systems share common traits. Turning these into a checklist makes them usable during design reviews and code reviews.

| Characteristic | Verification criterion | Example |
| --- | --- | --- |
| Observable | Metrics, logs, and traces all present? | Prometheus + Loki + Jaeger |
| Incremental deploy | Canary or blue-green possible? | canary 5 % → 100 % |
| Self-healing | Retry, timeout, circuit breaker exist? | retry 3×, timeout 5 s |
| Documented | Runbook, architecture diagram, API spec exist? | README + ADR + OpenAPI |

These characteristics should be reflected before adding a feature—retrofitting them after launch is far more expensive.

## Step-by-Step Operability Audit

### Step 1 — Observability check

```python
def has_obs(metrics, logs, traces):
    return all([metrics, logs, traces])
```

Metrics, logs, and traces each answer different questions. All three together let you infer internal state more accurately and accelerate debugging. Metrics tell you *what* is wrong, logs tell you *why*, and traces tell you *where* across services.

### Step 2 — Safe deploy check

```python
def safe_deploy(canary_pct, rollback_ready):
    return canary_pct <= 5 and rollback_ready
```

An operable system keeps changes small and reversible. Checking canary percentage and rollback readiness together ensures that even if something goes wrong, the blast radius is limited and recovery is immediate.

### Step 3 — Resilience patterns check

```python
def has_resilience(retry, timeout, breaker):
    return all([retry, timeout, breaker])
```

Retry, timeout, and circuit breaker are containment devices for partial failure. Without them, a slow external dependency can cascade and bring down the entire request path.

### Step 4 — Automation ratio

```python
def auto_ratio(auto_min, total_min):
    return auto_min / total_min
```

If humans keep performing repetitive procedures, operability is still weak. The automation ratio reveals whether team time flows toward structural improvements or stays trapped in manual repetition.

### Step 5 — Operability score

```python
def score(obs, deploy, resil, auto):
    return sum([obs, deploy, resil, auto >= 0.7]) / 4
```

Operability is abstract, but splitting it into per-axis checks makes prioritization easier. The goal is not a perfect score—it is surfacing the weakest axis quickly so you know where to invest next.

## Operability Maturity Model

Operable systems are built in stages. Understanding what capabilities each level adds helps you identify your current position and your next target.

### Level 1 — Reactive Operations

- Respond manually when incidents occur
- Monitoring exists but alert thresholds are vague
- Deployments are manual; rollbacks are also manual
- Documentation lives in one person's memory

### Level 2 — Structured Operations

- Monitoring metrics and alert thresholds are clearly defined
- Deployments run through CI/CD pipelines
- Runbooks exist and major procedures are documented
- Rollback is possible but manual

### Level 3 — Preventive Operations

- SLOs and error budgets are defined
- Canary deployment is the default; auto-rollback on failure
- Incident response is formalized; postmortems are standardized
- Toil ratio is measured and reduction work is scheduled

### Level 4 — Autonomous Operations

- Most incidents are detected and recovered automatically
- Capacity planning is data-driven
- Deployments are incremental with high test coverage
- Complex failure scenarios are periodically tested (chaos engineering)

Most teams sit between Level 2 and Level 3. What matters is acknowledging your current position and knowing what to improve to reach the next level.

## First SRE Adoption Roadmap

Teams introducing SRE principles for the first time often wonder where to start. Trying to change everything at once creates overwhelming resistance. A phased approach increases success probability.

### Phase 1 (Months 1–2) — Gain Visibility

- [ ] Select 3–5 core metrics (latency, error rate, throughput)
- [ ] Build monitoring dashboards
- [ ] Set alert thresholds for critical metrics
- [ ] Create incident communication channel (Slack/Teams)

### Phase 2 (Months 3–4) — Set Targets

- [ ] Define SLIs for core services
- [ ] Set SLO targets (99 %, 99.9 %, etc.)
- [ ] Introduce error budget concept
- [ ] Document incident severity classification

### Phase 3 (Months 5–6) — Formalize Processes

- [ ] Adopt postmortem template
- [ ] Define incident response roles (IC, ops lead, comms lead)
- [ ] Begin measuring toil
- [ ] Build automation candidate list

### Phase 4 (Months 7–12) — Engineering Execution

- [ ] Execute automation projects
- [ ] Build capacity planning model
- [ ] Improve CI/CD pipeline
- [ ] Introduce canary deployments

This roadmap adapts to a team's current state. The key is not doing everything at once but advancing each phase steadily.

## Runbook-as-Code: A Practical Example

Operational procedures stored only in a wiki drift from reality over time. Expressing them as code makes them both documentation and executable automation, ensuring they stay current through code review and CI.

```python
"""
Runbook: DB Connection Pool Exhaustion
Trigger: active_connections / max_connections > 0.9
Likely causes: batch job leaking connections, slow query spike
"""

import subprocess
import json
from datetime import datetime

def diagnose_connection_pool():
    """Step 1: Diagnose current state"""
    checks = {
        "active_connections": get_metric("active_db_connections"),
        "max_connections": get_metric("max_db_connections"),
        "waiting_queries": get_metric("db_queries_waiting"),
        "slow_queries_5min": get_metric("db_slow_queries_total", range="5m"),
    }

    utilization = checks["active_connections"] / checks["max_connections"]
    checks["utilization_pct"] = f"{utilization * 100:.1f}%"
    checks["severity"] = "critical" if utilization > 0.95 else "warning"

    return checks

def mitigate_connection_pool():
    """Step 2: Immediate mitigation"""
    actions = []

    # Force-release idle connections
    result = execute_db_command(
        "SELECT pg_terminate_backend(pid) "
        "FROM pg_stat_activity "
        "WHERE state = 'idle' "
        "AND state_change < now() - interval '5 minutes'"
    )
    actions.append(f"Released {result['terminated']} idle connections")

    # Pause batch jobs
    pause_batch_jobs()
    actions.append("Paused batch jobs")

    return actions

def verify_recovery():
    """Step 3: Verify recovery"""
    state = diagnose_connection_pool()
    utilization = float(state["utilization_pct"].replace("%", ""))

    if utilization < 70:
        return {"status": "recovered", "utilization": state["utilization_pct"]}
    else:
        return {"status": "not_recovered", "utilization": state["utilization_pct"]}
```

This code is better than a wiki document in three ways. First, it is executable. Second, it is testable. Third, it stays current through code review.

## Resilience Patterns in Practice

Partial failures must not cascade into total outages. Retry, timeout, and circuit breaker form the three fundamental resilience patterns.

### Circuit Breaker Implementation

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Blocked (requests rejected)
    HALF_OPEN = "half_open"  # Tentatively allowing requests

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = 0

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError("Circuit is open, request rejected")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

class CircuitOpenError(Exception):
    pass
```

The circuit breaker protects system resources when external dependencies (databases, third-party APIs) stop responding. Once failures exceed the threshold, it blocks requests entirely rather than letting them queue up and exhaust threads or connection pools. After a recovery timeout, it tentatively allows one request to test whether the dependency has recovered.

### Retry with Exponential Backoff

```python
import time
import random

def retry_with_backoff(func, max_retries=3, base_delay=1.0, max_delay=30.0):
    """Retry with exponential backoff and jitter"""
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                raise e

            # Exponential backoff + jitter
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)

            print(f"Attempt {attempt + 1} failed, retrying in {delay + jitter:.1f}s")
            time.sleep(delay + jitter)
```

Jitter is added to prevent the "thundering herd" problem—when many clients retry simultaneously and concentrate load on a recovering server. Without jitter, synchronized retries can keep the server overwhelmed even after the original cause resolves.

## Operability Audit Checklist

Before deploying a new service to production—or when improving an existing service's operability—use this checklist as part of a Production Readiness Review (PRR).

### Observability

- [ ] Golden signals (latency, traffic, errors, saturation) collected?
- [ ] Structured logs include trace_id?
- [ ] Distributed tracing tracks cross-service requests?
- [ ] SLO dashboard configured?
- [ ] Error budget burn-rate alerts set?

### Safe Change

- [ ] Canary deployment possible? (5 % → 25 % → 100 %)
- [ ] Rollback within 1 minute possible?
- [ ] Feature flags can disable functionality?
- [ ] Database migrations are backward-compatible?
- [ ] Post-deploy smoke tests run automatically?

### Resilience

- [ ] Timeouts set on all external dependencies?
- [ ] Circuit breakers applied?
- [ ] Retries use exponential backoff with jitter?
- [ ] Graceful degradation on partial failure?
- [ ] Single points of failure (SPOF) eliminated?

### Automation

- [ ] 50 %+ of repetitive operational tasks automated?
- [ ] Runbooks managed as code?
- [ ] Recovery procedures executable via script?
- [ ] Certificate renewal, log rotation automated?
- [ ] Capacity scaling automatic or semi-automatic?

Any "no" answer represents operational risk. Using this checklist as part of PRR systematically secures operability before production deployment.

## Safe Deployment Pattern

Safe deployment means shipping changes in small, reversible increments rather than all-at-once rollouts. A staged pattern with metric gates at each phase significantly reduces risk.

```python
# Staged deployment pattern
deployment_stages = [
    {"name": "canary", "traffic_pct": 5, "duration_min": 10},
    {"name": "pilot", "traffic_pct": 25, "duration_min": 20},
    {"name": "full", "traffic_pct": 100, "duration_min": 0},
]

def should_proceed(stage, metrics):
    """Check if metrics are healthy before proceeding to next stage"""
    thresholds = {
        "error_rate": 0.01,       # 1%
        "latency_p99_ms": 1000,
        "cpu_pct": 80
    }

    return all(
        metrics[key] <= threshold
        for key, threshold in thresholds.items()
    )

# Example
current_metrics = {
    "error_rate": 0.005,
    "latency_p99_ms": 850,
    "cpu_pct": 65
}

if should_proceed("canary", current_metrics):
    print("Pass: Canary passed, proceeding to pilot stage")
else:
    print("Fail: Canary failed, rollback required")
```

This pattern verifies metrics at each stage and advances only when everything looks healthy. When a problem is detected, it rolls back immediately to minimize blast radius.

## Design Principles for Operable Systems

Building operable systems from scratch requires keeping a few design principles in mind. These principles apply alongside feature development.

### Principle 1 — Failure Always Happens

Every component will eventually fail. Networks disconnect, disks fill up, external APIs time out. Design failure as part of normal operation, not as an exception.

### Principle 2 — If Not Observable, Not Debuggable

When an incident occurs and you cannot tell what went wrong, fast recovery is impossible. Metrics, logs, and traces are not post-hoc tools—they are interfaces that must be decided at design time.

### Principle 3 — Small Changes, Often

Large changes carry large risk and wide blast radius when something goes wrong. Small, frequent deployments let you quickly identify the cause of any regression and roll back with minimal impact.

### Principle 4 — Automate Repetitive Work First

You cannot automate everything at once. Start with tasks that are high-frequency, low-risk, and well-defined. Automation is an investment that protects team time.

### Principle 5 — Document Incident Procedures as Code

Runbooks in a wiki go stale quickly. Procedures expressed as scripts serve as both documentation and executable automation. Code is more honest than prose.

Applying these principles to every new feature keeps operational burden from growing linearly with system size.

## Series Summary

The ten topics covered in the SRE 101 series are not isolated concepts—they are components of a unified operational framework.

| Post | Core question | Practical deliverable |
| --- | --- | --- |
| 1. What is SRE | How do you engineer operations? | SRE adoption criteria |
| 2. Reliability | What dimensions make up reliability? | Per-dimension measurement |
| 3. SLI/SLO/SLA | What to measure, how far to promise? | SLO document, SLA contract |
| 4. Error Budget | How much failure is acceptable? | Budget policy, release rules |
| 5. Monitoring | Which signals to watch? | Dashboard + alert design |
| 6. Incident Response | Who moves how during incidents? | Role matrix, comms template |
| 7. Postmortem | What do you learn from incidents? | Postmortem template, action tracker |
| 8. Reducing Toil | Which repetitive tasks to automate? | Toil tracker, automation roadmap |
| 9. Capacity Planning | When to scale resources? | Capacity model, forecast sheet |
| 10. Building Operable Systems | How to design operability from the start? | PRR checklist, maturity model |

When these components interlock well, incidents decrease, changes become faster and safer, and teams spend time on system improvements instead of repetitive tasks. The ultimate goal of SRE is not to take on more operational work—it is to reduce the human time required for operations while increasing reliability.

## Answering the Opening Questions

- **Why is operability a design property instead of a post-launch enhancement?**
  Operability cannot be achieved by inserting monitoring and alerts after code is written. Decisions about which signals to expose, which changes are safe, and how to recover from failure must happen at the interface, data-model, and deployment-structure stages. Only then can the system be operated without accumulating ongoing manual cost.

- **Why do observability, automation, safe change, and resilience need to be judged together?**
  The four axes complement each other. Without observability, automation does not know what to act on. Without safe change (canary/rollback), automation spreads incidents faster. Without resilience, observing problems does not help if you cannot respond. One strong axis means nothing when another axis's weakness determines total operational cost.

- **What should a team ask first when auditing whether a system is truly operable?**
  Ask: "Where does failure happen, what signal reveals it, who notices, and how quickly?" "Can changes be applied and rolled back incrementally?" "How far does automatic recovery extend without waking someone at 3 AM?" Parts that cannot answer these questions clearly are next quarter's operational burden—considering operations at design time dramatically reduces future manual work.

<!-- toc:begin -->
## In this series

- [SRE 101 (1/10): What is SRE?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- [SRE 101 (4/10): Error Budget](./04-error-budget.md)
- [SRE 101 (5/10): Monitoring](./05-monitoring.md)
- [SRE 101 (6/10): Incident Response](./06-incident-response.md)
- [SRE 101 (7/10): Postmortem](./07-postmortem.md)
- [SRE 101 (8/10): Reducing Toil](./08-reducing-toil.md)
- [SRE 101 (9/10): Capacity Planning](./09-capacity-planning.md)
- **Building Operable Systems (current)**

<!-- toc:end -->

## References

- [Building Secure and Reliable Systems - Google](https://sre.google/books/building-secure-reliable-systems/)
- [Release It! - Michael Nygard](https://pragprog.com/titles/mnee2/release-it-second-edition/)
- [Resilience Engineering - Wikipedia](https://en.wikipedia.org/wiki/Resilience_engineering)
- [Observability Engineering - O'Reilly](https://www.oreilly.com/library/view/observability-engineering/9781492076438/)

Tags: SRE, Operability, Architecture, Reliability, Engineering
