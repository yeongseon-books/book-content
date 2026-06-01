---
title: "Harness Engineering 101 (9/10): Observability — Tracing and Replaying Agent Work"
series: harness-engineering-101
episode: 9
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Harness
- Observability
- Tracing
last_reviewed: '2026-05-14'
seo_description: If you cannot see what the agent did, you cannot debug it or improve
  it.
---

# Harness Engineering 101 (9/10): Observability — Tracing and Replaying Agent Work

Many agent systems still preserve only the final answer string. That is enough to impress someone in a demo and almost useless when an incident starts. Once a real run includes retrieval, tool calls, retries, reflection, approval, and cost controls, the final answer alone is not an explanation.

Operationally, the real requirement is stronger: after a bad run, you must be able to reconstruct what the agent saw, what it decided, what it called, how long each step took, and where the cost spiked.

This is the 9th post in the Harness Engineering 101 series. Here we treat observability as a replayable execution model, not as a collection of ad hoc logs.

![Observability - tracing and replaying agent work](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/09/09-01-observability-tracing-and-replaying-agen.en.png)
*Observability - tracing and replaying agent work*
> An observable agent can explain not only what it answered, but which input, context, tools, costs, and decisions produced that answer.

## Questions to Keep in Mind

- How should an Observability Harness let you reconstruct an agent run later?
- What operational questions do traces, replay, and cost-latency dashboards each answer?
- Which signals deserve alerts that wake a human?

## What Is Observability?

Observability is the ability to reconstruct, from the outside, what an agent did, why it did it, and how. It is not just "leave logs around" — when an incident happens, you must be able to trace and reproduce the decision made at that moment.

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid

@dataclass
class Span:
    span_id: str
    trace_id: str
    parent_id: str | None
    name: str
    started_at: datetime
    ended_at: datetime | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)
    status: str = "ok"
```

A `Span` is one unit of work in the agent. One tool call, one LLM call, one reflection step — each becomes its own span. Spans that share the same trace_id form one execution flow.

## What Should You Record?

![What should you Record](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/09/09-02-what-should-you-record.en.png)

*What should you Record*
You need three layers of information to make traces useful.

1. **What did the agent do?** tool name, input, output
2. **Why did it decide that?** prompt, model, temperature, retrieved context
3. **How long did it take and how much did it cost?** latency, token count, cost in dollars

```python
def record_llm_call(span: Span, prompt: str, model: str, response: str, usage: dict):
    span.attributes.update({
        "llm.model": model,
        "llm.prompt_tokens": usage["prompt_tokens"],
        "llm.completion_tokens": usage["completion_tokens"],
        "llm.cost_usd": _calculate_cost(model, usage),
    })
    span.events.append({
        "name": "llm.prompt",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "body": prompt,
    })
    span.events.append({
        "name": "llm.response",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "body": response,
    })
```

Note that prompt and response go into events, not attributes. Attributes are short metadata for search and filtering; events are payloads ordered by time.

## Trace Model — Following One Run End to End

![Trace model - following one run end to end](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/09/09-03-trace-model-following-one-run-end-to-end.en.png)

*Trace model - following one run end to end*
A single agent run produces a trace shaped like this tree:

```python
class Tracer:
    def __init__(self, exporter):
        self.exporter = exporter
        self._stack: list[Span] = []

    def start(self, name: str, **attrs) -> Span:
        parent_id = self._stack[-1].span_id if self._stack else None
        trace_id = self._stack[0].trace_id if self._stack else str(uuid.uuid4())
        span = Span(
            span_id=str(uuid.uuid4()),
            trace_id=trace_id,
            parent_id=parent_id,
            name=name,
            started_at=datetime.now(timezone.utc),
            attributes=dict(attrs),
        )
        self._stack.append(span)
        return span

    def end(self, status: str = "ok"):
        span = self._stack.pop()
        span.ended_at = datetime.now(timezone.utc)
        span.status = status
        self.exporter.export(span)
```

```text
trace 7a3f...
├── span: agent.run           (12.3s, $0.04)
│   ├── span: llm.plan        (1.2s, $0.01)
│   ├── span: tool.search     (0.8s)
│   ├── span: llm.synthesize  (2.1s, $0.02)
│   └── span: tool.send_email (0.3s)
```

With this tree alone you can answer "where was it slow?", "where did the cost spike?", and "which tool failed?" instantly.

## Replay — Reproducing a Run from Logs

![Replay - reproducing a run from logs](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/09/09-04-replay-reproducing-a-run-from-logs.en.png)

*Replay - reproducing a run from logs*
A good trace is reproducible. You should be able to run the same step with the same input again and verify the same output comes back.

```python
def replay_trace(trace_id: str, store) -> list[dict]:
    spans = store.load_spans(trace_id)
    results = []
    for span in spans:
        if span.name.startswith("tool."):
            tool_name = span.attributes["tool.name"]
            tool_input = span.attributes["tool.input"]
            actual = invoke_tool(tool_name, tool_input)
            expected = span.attributes["tool.output"]
            results.append({
                "span": span.name,
                "matches": actual == expected,
                "expected": expected,
                "actual": actual,
            })
    return results
```

For replay to work, every input — prompts, retrieved context, tool inputs — must be in the span. "Just record the result" makes replay impossible.

## Cost and Latency Dashboards

Production agents see sudden spikes in cost and response time. The dashboard should surface these four metrics in real time:

```python
@dataclass
class AgentMetrics:
    total_runs: int
    avg_latency_ms: float
    p95_latency_ms: float
    avg_cost_usd: float
    error_rate: float

def aggregate(spans: list[Span]) -> AgentMetrics:
    runs = [s for s in spans if s.name == "agent.run"]
    latencies = [(s.ended_at - s.started_at).total_seconds() * 1000 for s in runs]
    costs = [s.attributes.get("total.cost_usd", 0) for s in runs]
    errors = [s for s in runs if s.status != "ok"]
    latencies_sorted = sorted(latencies)
    p95_idx = int(len(latencies_sorted) * 0.95)
    return AgentMetrics(
        total_runs=len(runs),
        avg_latency_ms=sum(latencies) / len(latencies) if latencies else 0,
        p95_latency_ms=latencies_sorted[p95_idx] if latencies_sorted else 0,
        avg_cost_usd=sum(costs) / len(costs) if costs else 0,
        error_rate=len(errors) / len(runs) if runs else 0,
    )
```

P95 latency matters far more than the average. The average can look fine while five percent of users wait 30 seconds.

## Alerting — When to Wake Someone Up

Alert on every anomaly and you get alert fatigue. Wake people up only on these three conditions:

```python
def should_alert(metrics: AgentMetrics, baseline: AgentMetrics) -> str | None:
    if metrics.error_rate > baseline.error_rate * 2 and metrics.error_rate > 0.05:
        return f"Error rate spike: {metrics.error_rate:.1%}"
    if metrics.p95_latency_ms > baseline.p95_latency_ms * 3:
        return f"P95 latency spike: {metrics.p95_latency_ms:.0f}ms"
    if metrics.avg_cost_usd > baseline.avg_cost_usd * 5:
        return f"Cost spike: ${metrics.avg_cost_usd:.4f}/run"
    return None
```

1. **Error rate spike**: more than 2x baseline AND above 5% absolute
2. **P95 latency spike**: more than 3x baseline
3. **Per-run cost spike**: more than 5x baseline

---

## OpenTelemetry Attribute Standardization

The most common reason observability breaks across teams is inconsistent attribute keys. One service uses `model`, another `llm_name`, a third `provider_model`. Shared dashboards and queries break immediately. Standardize a minimum attribute set.

```yaml
# tracing_conventions.yaml
span_names:
  root: agent.run
  planning: llm.plan
  synthesis: llm.synthesize
  retrieval: rag.retrieve
  tool: tool.invoke

required_attributes:
  - agent.version
  - agent.task_id
  - llm.model
  - llm.prompt_tokens
  - llm.completion_tokens
  - cost.usd
  - latency.ms
  - user.request_id
  - safety.approval_required
```

```python
REQUIRED_ATTRS = {
    "agent.version",
    "agent.task_id",
    "llm.model",
    "llm.prompt_tokens",
    "llm.completion_tokens",
    "cost.usd",
    "latency.ms",
    "user.request_id",
    "safety.approval_required",
}

def validate_span_attributes(span) -> None:
    missing = sorted(REQUIRED_ATTRS - set(span.attributes.keys()))
    if missing:
        raise ValueError(
            f"span missing required attrs ({span.name}): {missing}"
        )
```

Add this validation to both CI and runtime sampling, so you can test observability quality itself.

---

## PII Minimization and Retention Policy

The more detailed your traces, the higher the security risk. Storing raw prompts and tool inputs easily leaks personal information. An Observability Harness must pair increased recording with explicit retention policy.

```python
import re

def redact_pii(text: str) -> str:
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[REDACTED_EMAIL]", text)
    text = re.sub(r"\b\d{2,3}-\d{3,4}-\d{4}\b", "[REDACTED_PHONE]", text)
    return text

def sanitize_event_payload(event: dict) -> dict:
    body = event.get("body")
    if isinstance(body, str):
        event["body"] = redact_pii(body)
    return event
```

```yaml
# retention_policy.yaml
retention:
  hot_trace_days: 14
  warm_trace_days: 90
  cold_archive_days: 365
  delete_after_days: 365

sampling:
  default_rate: 0.2
  error_rate: 1.0
  high_risk_action_rate: 1.0
```

Without an explicit retention policy, cost and compliance problems surface simultaneously. Deleting too aggressively makes replay impossible. The practical default: sample normal traffic, retain 100% of failures and high-risk events.

---

## Auto-Generating Execution Replay Reports

Storing traces and producing human-readable reports are separate problems. To accelerate incident response, auto-generate a summary from each trace.

```python
def build_incident_report(trace_id: str, store) -> dict:
    spans = store.load_spans(trace_id)
    root = next(s for s in spans if s.parent_id is None)
    failed = [s for s in spans if s.status != "ok"]

    return {
        "trace_id": trace_id,
        "agent_version": root.attributes.get("agent.version"),
        "task_id": root.attributes.get("agent.task_id"),
        "total_latency_ms": root.attributes.get("latency.ms"),
        "total_cost_usd": root.attributes.get("cost.usd"),
        "failed_spans": [
            {
                "name": s.name,
                "status": s.status,
                "error": s.attributes.get("error.message", ""),
            }
            for s in failed
        ],
    }
```

This report is the first thing on-call reads in the opening five minutes. Teams that debug well are not teams that read more logs—they are teams that structure their first screen so the next action is obvious.

---

## Trace ID Propagation in Distributed Execution

When the agent runtime splits across queues, workers, and external tool services, traces break easily. Force trace_id propagation at the protocol level to maintain end-to-end replay.

```python
def inject_trace_headers(
    headers: dict, trace_id: str, span_id: str
) -> dict:
    h = dict(headers)
    h["x-trace-id"] = trace_id
    h["x-parent-span-id"] = span_id
    return h

def extract_trace_headers(headers: dict) -> tuple[str | None, str | None]:
    return headers.get("x-trace-id"), headers.get("x-parent-span-id")

def enqueue_with_trace(
    queue, message: dict, trace_id: str, span_id: str
) -> None:
    message = dict(message)
    message["_trace"] = {"trace_id": trace_id, "parent_span_id": span_id}
    queue.publish(message)
```

Without this rule, when tool-call latency spikes, you cannot link back to the root trace and root-cause analysis time grows significantly.

---

## Operational Dashboard Example Queries

Collected data is useless if you cannot ask questions. These are the queries on-call engineers reach for most often.

```text
Q1. Which task_ids have the highest failure rate in the last 30 minutes?
Q2. Were there approval bypass attempts on requests with approval_required=true?
Q3. How much has cost.usd/run increased since the model version switch?
Q4. Are policy_violations concentrated in a specific tool?
Q5. What are the top 10 repeated_failure_signatures?
```

```python
import collections

def top_failed_tasks(spans, window_minutes: int = 30) -> list[tuple[str, int]]:
    failures = collections.Counter()
    for s in spans:
        if s.name == "agent.run" and s.status != "ok":
            task_id = s.attributes.get("agent.task_id", "unknown")
            failures[task_id] += 1
    return failures.most_common(10)

def approval_bypass_attempts(spans) -> int:
    return sum(
        1 for s in spans
        if s.attributes.get("safety.approval_bypass") is True
    )
```

The point is not building a flashy dashboard—it is having queries ready that answer incident-response questions immediately.

As operational cycles lengthen, metric definitions need versioning too. If the `cost.usd` formula changes due to model pricing updates, past and present comparisons become invalid. Recording a metric-definition version alongside the data lets you separate "the metric got worse" from "the formula changed."

Track the top-20 most expensive traces weekly. Most cost comes not from the model itself but from unnecessary reflect iterations or excessive retrieval document counts.

---

## Five Common Mistakes

1. **Logging only outputs, not inputs.** Replay becomes impossible and you cannot trace incident causes. Always record prompts and retrieved context.
2. **Logging PII verbatim.** User emails, card numbers and similar end up raw in spans. Mask or hash before recording.
3. **Losing trace_id across boundaries.** Async calls drop the context and the trace breaks. Use an async-aware tracer or pass it explicitly.
4. **Watching averages and ignoring P95.** The mean looks fine while 5% wait 30s. Always look at percentiles.
5. **Alerting on every anomaly.** Alert fatigue makes you miss real alerts. Combine baseline-relative ratios with absolute thresholds.

## Key Takeaways

- Observability lets you trace and reproduce decisions after the fact.
- Spans are units of work; traces are the tree of one run.
- Record all three layers: What, Why, and Cost.
- Replay only works if prompts and retrieved context are stored.
- Watch p95 (not average) latency and alert on baseline-relative spikes.

## Operational checklist

- [ ] Record every agent run as a trace with nested spans.
- [ ] Store What, Why, and Cost metadata together for each critical step.
- [ ] Preserve prompts, retrieved context, and tool inputs needed for replay.
- [ ] Track error rate, p95 latency, and average cost per run in dashboards.
- [ ] Page only on material baseline-relative spikes to avoid alert fatigue.

The next post is Production Harness — combining the nine harnesses into a deployment pattern for real production environments.

## Answering the Opening Questions

- **How should an Observability Harness let you reconstruct an agent run later?**
  - Tie request id, input, context snapshot, tool calls, intermediate decisions, cost, latency, errors, and final result into one trace.
- **What operational questions do traces, replay, and cost-latency dashboards each answer?**
  - Traces answer path questions, replay answers reproducibility questions, and dashboards expose trends and bottlenecks in cost, latency, and errors.
- **Which signals deserve alerts that wake a human?**
  - Alerts should fire for user-impacting failure spikes, runaway cost, repeated tool failures, approval bypass attempts, and rollback failures.

<!-- toc:begin -->
## In this series

- [Harness Engineering 101 (1/10): What Is Harness Engineering?](./01-what-is-harness-engineering.md)
- [Harness Engineering 101 (2/10): Task Harness — Turning Vague Work into Executable Tasks](./02-task-harness.md)
- [Harness Engineering 101 (3/10): Context Harness — Designing What the Agent Should Know and Not Know](./03-context-harness.md)
- [Harness Engineering 101 (4/10): Constraint Harness — Defining Rules, Boundaries, and Forbidden Actions](./04-constraint-harness.md)
- [Harness Engineering 101 (5/10): Tool Harness — Designing Safe Tools for Agents](./05-tool-harness.md)
- [Harness Engineering 101 (6/10): Test Harness — Turning Completion Criteria into Tests](./06-test-harness.md)
- [Harness Engineering 101 (7/10): Feedback Loops — Building Structures That Let Agents Recover from Failure](./07-feedback-loop.md)
- [Harness Engineering 101 (8/10): Approval Gates — Designing Where Humans Must Approve](./08-approval-gate.md)
- **Harness Engineering 101 (9/10): Observability — Tracing and Replaying Agent Work (current)**
- Harness Engineering 101 (10/10): Production Harness — Building Operational Environments for Agents (upcoming)

<!-- toc:end -->

---

## References

### Official docs and references

- [OpenTelemetry — Tracing Concepts](https://opentelemetry.io/docs/concepts/signals/traces/)
- [Google SRE — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [LangSmith — Tracing for LLM Applications](https://docs.smith.langchain.com/observability)

### Verification-friendly observability references

- [Honeycomb — What Is Observability Engineering?](https://www.honeycomb.io/blog/what-is-observability)
- [OpenAI Agents SDK — Tracing](https://openai.github.io/openai-agents-python/tracing/)

Tags: AI Agent, Harness, Production, Reliability
