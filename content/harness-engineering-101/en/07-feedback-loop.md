---
title: Feedback Loops — Building Structures That Let Agents Recover from Failure
series: harness-engineering-101
episode: 7
language: en
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Harness
- Feedback
- Reflection
last_reviewed: '2026-05-03'
---

# Feedback Loops — Building Structures That Let Agents Recover from Failure

> Harness Engineering 101 Series (7/10)

Agents rarely succeed on the first try. A Feedback Loop is the structure that hands failure back to the agent so it can fix its own work.

---
## No Agent Succeeds on the First Try

Agents fail often on the first attempt. They call the wrong tool, pass wrong arguments, produce malformed output. How you handle that failure decides production quality.

The worst pattern is returning the failure to the user as is. The second worst is retrying the same call unchanged. The good pattern is feeding the failure cause back to the agent so the next attempt improves.

Feedback Loop is the structure that converts failure into a learning signal. This article covers retry vs reflect, the composition of feedback, and infinite-loop prevention.

---

## Retry vs Reflect

Two responses to failure.

**Retry**: try the same input again. Suited to transient errors (network, timeout, rate limit).

**Reflect**: tell the agent why it failed and have it produce a new attempt. Suited to reasoning errors (wrong arguments, format violations).

The two are different tools. Reflecting on a problem that needed retry blows up cost. Retrying a problem that needs reflect fails forever.

```python
from dataclasses import dataclass
from enum import Enum


class FailureMode(Enum):
    TRANSIENT = "transient"
    DETERMINISTIC = "deterministic"
    REASONING = "reasoning"


@dataclass
class FailureClassification:
    mode: FailureMode
    feedback: str
    retry_after: float = 0.0


def classify_failure(error: Exception) -> FailureClassification:
    if isinstance(error, TimeoutError):
        return FailureClassification(FailureMode.TRANSIENT, "", retry_after=1.0)
    if isinstance(error, ToolError) and error.code == ErrorCode.RATE_LIMITED:
        return FailureClassification(FailureMode.TRANSIENT, "", retry_after=5.0)
    if isinstance(error, ToolError) and error.code == ErrorCode.INVALID_INPUT:
        return FailureClassification(FailureMode.REASONING, error.to_agent_message())
    if isinstance(error, PolicyViolation):
        return FailureClassification(FailureMode.REASONING, f"Policy violation: {error}. Try a different approach.")
    return FailureClassification(FailureMode.DETERMINISTIC, str(error))
```

Classification is the first step. Without it, every failure gets the same strategy.

---

## Composing Reflect Messages

More information in feedback is not better. Focus on three things: what was wrong, why, and how to try next.

```python
@dataclass
class ReflectMessage:
    """The bridge from failure to a new attempt."""
    attempt_number: int
    failed_action: str
    failure_reason: str
    suggested_change: str
    constraint: str

    def to_prompt(self) -> str:
        return f"""Attempt #{self.attempt_number} failed.

What you tried: {self.failed_action}
Why it failed: {self.failure_reason}
What to try next: {self.suggested_change}
Constraint for next attempt: {self.constraint}

Now produce a new attempt that satisfies the constraint."""


msg = ReflectMessage(
    attempt_number=2,
    failed_action="Called create_user with email='alice'",
    failure_reason="email field requires a valid address (must contain @)",
    suggested_change="Provide the full email like alice@example.com",
    constraint="email must match RFC 5322 format",
)
```

Feedback that says only "try again" makes the agent repeat the same mistake. Specific constraints change behavior.

---

## Preventing Infinite Loops

Reflect loops can run forever. The agent might repeat the same mistake or oscillate between two errors. Three safeties.

**1. Max attempts**: cap on attempts, typically 3–5.
**2. Cumulative cost limit**: cap on tokens/cost (reuse the ResourceMeter from Constraint Harness).
**3. Repetition detection**: stop if the same kind of failure repeats N times.

```python
from collections import Counter
from dataclasses import dataclass, field


@dataclass
class FeedbackLoop:
    """Manages the retry/reflect loop safely."""
    max_attempts: int = 5
    max_repetitions: int = 2
    attempts: int = 0
    failure_history: list[FailureClassification] = field(default_factory=list)

    def should_continue(self, latest: FailureClassification) -> bool:
        self.attempts += 1
        self.failure_history.append(latest)

        if self.attempts >= self.max_attempts:
            return False

        recent_modes = Counter(f.mode for f in self.failure_history[-3:])
        if any(count >= self.max_repetitions + 1 for count in recent_modes.values()):
            return False

        return True

    def escalate(self) -> dict:
        return {
            "status": "escalated",
            "attempts": self.attempts,
            "failure_history": [{"mode": f.mode.value, "feedback": f.feedback[:200]} for f in self.failure_history],
            "recommended_action": "human_review",
        }


def run_with_feedback(agent, task, loop: FeedbackLoop) -> dict:
    while True:
        try:
            return agent.run(task)
        except Exception as e:
            classification = classify_failure(e)
            if not loop.should_continue(classification):
                return loop.escalate()

            if classification.mode == FailureMode.TRANSIENT:
                import time
                time.sleep(classification.retry_after)
            elif classification.mode == FailureMode.REASONING:
                task = task.with_feedback(classification.feedback)
            else:
                return loop.escalate()
```

`escalate` is the human exit. Problems the loop cannot solve must go to a human (covered next in Approval Gate).

---

## Self-Critique Pattern

Have the agent critique its own output. Weaker than external validation, but useful when no validator is available.

```python
def self_critique(agent, draft: str, criteria: list[str]) -> tuple[bool, str]:
    """Have the agent review its own draft."""
    critique_prompt = f"""Review the following draft against these criteria.

Criteria:
{chr(10).join(f'- {c}' for c in criteria)}

Draft:
{draft}

Respond in JSON:
{{
  "passes_all": true/false,
  "violations": ["criterion that failed: reason"],
  "suggested_fix": "concrete change to make"
}}"""
    response = agent.complete(critique_prompt)
    parsed = parse_json(response)
    return parsed["passes_all"], parsed.get("suggested_fix", "")


def generate_with_critique(agent, prompt: str, criteria: list[str], max_rounds: int = 3) -> str:
    draft = agent.complete(prompt)
    for _ in range(max_rounds):
        passes, fix = self_critique(agent, draft, criteria)
        if passes:
            return draft
        draft = agent.complete(f"{prompt}\n\nPrevious draft:\n{draft}\n\nApply this fix: {fix}")
    return draft
```

Self-critique has two risks. (1) The agent misses its own mistakes (false positive). (2) Cost roughly doubles per turn. Where external validation is possible, prefer external validation.

---

## Failure Memory

When the same task type runs many times, remembering past failures cuts repeated mistakes. Failure memory accumulates which approaches failed per task.

```python
from datetime import datetime
import json
from pathlib import Path


@dataclass
class FailureRecord:
    task_type: str
    failed_approach: str
    failure_reason: str
    timestamp: str
    fixed_in_next_attempt: bool


class FailureMemory:
    """Accumulates failure records per task type."""

    def __init__(self, store_path: Path):
        self.store_path = store_path
        self.records: list[FailureRecord] = self._load()

    def _load(self) -> list[FailureRecord]:
        if not self.store_path.exists():
            return []
        data = json.loads(self.store_path.read_text())
        return [FailureRecord(**r) for r in data]

    def add(self, record: FailureRecord) -> None:
        self.records.append(record)
        self.store_path.write_text(json.dumps([r.__dict__ for r in self.records], indent=2))

    def warnings_for(self, task_type: str, recent: int = 5) -> list[str]:
        relevant = [r for r in self.records if r.task_type == task_type][-recent:]
        return [f"Previously failed: {r.failed_approach} (reason: {r.failure_reason})" for r in relevant]
```

Inject failure memory warnings into the agent's first-attempt prompt and it starts away from past mistakes. Without learning, the system improves over time.

---

## Common Mistakes

**1. Solving every failure with retry.**
Reasoning errors do not yield to retry. Classify, then reflect.

**2. Reflect messages too generic.**
"Try again" carries zero information. Include What/Why/How and a specific constraint.

**3. No infinite-loop prevention.**
Without max attempts, cost limit, and repetition detection, one task can blow up cost.

**4. No escalation path.**
Problems the loop cannot solve must reach a human. Auto-retry without escalate sends failures straight to users.

**5. No failure memory.**
An agent that meets the same mistakes fresh every time does not improve. Failure logs are nearly free learning signal.

---

## Key Takeaways

- No agent succeeds on the first try. Feedback Loop turns failure into a learning signal for the next attempt.
- Classify failure as transient, reasoning, or deterministic, then choose retry or reflect.
- Reflect messages must include What/Why/How and a concrete constraint to change behavior.
- Prevent infinite loops with max attempts, cost limit, and repetition detection.
- Failure memory injected into the first-attempt prompt makes the system improve over time.

---

<!-- toc:begin -->
## Harness Engineering 101 Series

- [What Is Harness Engineering?](./01-what-is-harness-engineering.md)
- [Task Harness — Turning Vague Work into Executable Tasks](./02-task-harness.md)
- [Context Harness — Designing What to Show and Hide from the Agent](./03-context-harness.md)
- [Constraint Harness — Defining Rules, Boundaries, and Forbidden Actions](./04-constraint-harness.md)
- [Tool Harness — Designing Safe Tools for Agents](./05-tool-harness.md)
- [Test Harness — Pinning Completion Criteria with Tests](./06-test-harness.md)
- **Feedback Loop — A Repeating Structure That Forces Failures to Be Fixed (current)**
- Approval Gate — Designing Where Human Approval Is Required (upcoming)
- Observability — Tracing and Reproducing Agent Work (upcoming)
- Production Harness — Building an Operable Agent Work Environment (upcoming)
<!-- toc:end -->

## References

- [Shinn et al. — Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)
- [Madaan et al. — Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651)
- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [LangGraph — Reflection Patterns](https://langchain-ai.github.io/langgraph/tutorials/reflection/reflection/)

Tags: AI Agent, Harness, Feedback, Reflection
