---
title: "Harness Engineering 101 (7/10): Feedback Loops — Building Structures That Let Agents Recover from Failure"
series: harness-engineering-101
episode: 7
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
- Feedback
- Reflection
last_reviewed: '2026-05-14'
seo_description: Agents rarely succeed on the first try. A Feedback Loop is the structure
  that hands failure back to the agent so it can fix its own work.
---

# Harness Engineering 101 (7/10): Feedback Loops — Building Structures That Let Agents Recover from Failure

Agents frequently fail on the first attempt. They choose the wrong tool, pass the wrong arguments, violate an output policy, or claim completion too early. The important distinction is not whether failure exists. It is whether the system can convert failure into a better next attempt.

Retrying blindly is usually just a cost amplifier. Returning the raw failure to the user is even worse. Productive feedback loops classify failure, choose the right recovery path, and stop before one task turns into an unbounded loop.

This is the 7th post in the Harness Engineering 101 series. Here we treat failure as structured input for the next attempt rather than as the end of the run.

![Feedback loops - building structures that let agents recover from failure](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/07/07-01-feedback-loops-building-structures-that.en.png)
*Feedback loops - building structures that let agents recover from failure*
> A good feedback loop does not merely try again; it makes the next attempt different because the system knows why the previous one failed.

## Questions to Keep in Mind

- What input should a Feedback Loop turn failure into instead of treating it as a stop signal?
- Where do simple retry and reflection diverge, and when should each be used?
- What limits and memory must remain inside the loop to prevent infinite retries?

## No Agent Succeeds on the First Try

Agents fail often on the first attempt. They call the wrong tool, pass wrong arguments, produce malformed output. How you handle that failure decides production quality.

The worst pattern is returning the failure to the user as is. The second worst is retrying the same call unchanged. The good pattern is feeding the failure cause back to the agent so the next attempt improves.

Feedback Loop is the structure that converts failure into a learning signal. This article covers retry vs reflect, the composition of feedback, and infinite-loop prevention.

---

## Retry vs Reflect

![Retry vs reflect](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/07/07-02-retry-vs-reflect.en.png)

*Retry vs reflect*
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

![Preventing infinite loops](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/07/07-03-preventing-infinite-loops.en.png)

*Preventing infinite loops*
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

![Failure memory](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/07/07-04-failure-memory.en.png)

*Failure memory*
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

## Operational checklist

- [ ] Classify failures into transient, reasoning, and deterministic buckets before recovery.
- [ ] Do not use identical logic for retry and reflect paths.
- [ ] Include What, Why, How, and a constraint in every reflect message.
- [ ] Cap attempts, cumulative cost, and repeated failure patterns together.
- [ ] Escalate unresolved loops to humans and record failure memory for the next run.

## Answering the Opening Questions

- **What input should a Feedback Loop turn failure into instead of treating it as a stop signal?**
  - It should become structured input: failure reason, observed evidence, constraints to change, and actions forbidden on the next attempt.
- **Where do simple retry and reflection diverge, and when should each be used?**
  - Retry fits transient errors where the same action may succeed. Reflection fits bad plans or judgments where the next action must change.
- **What limits and memory must remain inside the loop to prevent infinite retries?**
  - Keep max attempts, cost limits, failure memory, stop conditions, and human-escalation rules inside the loop.

<!-- toc:begin -->
## In this series

- [Harness Engineering 101 (1/10): What Is Harness Engineering?](./01-what-is-harness-engineering.md)
- [Harness Engineering 101 (2/10): Task Harness — Turning Vague Work into Executable Tasks](./02-task-harness.md)
- [Harness Engineering 101 (3/10): Context Harness — Designing What the Agent Should Know and Not Know](./03-context-harness.md)
- [Harness Engineering 101 (4/10): Constraint Harness — Defining Rules, Boundaries, and Forbidden Actions](./04-constraint-harness.md)
- [Harness Engineering 101 (5/10): Tool Harness — Designing Safe Tools for Agents](./05-tool-harness.md)
- [Harness Engineering 101 (6/10): Test Harness — Turning Completion Criteria into Tests](./06-test-harness.md)
- **Harness Engineering 101 (7/10): Feedback Loops — Building Structures That Let Agents Recover from Failure (current)**
- Harness Engineering 101 (8/10): Approval Gates — Designing Where Humans Must Approve (upcoming)
- Harness Engineering 101 (9/10): Observability — Tracing and Replaying Agent Work (upcoming)
- Harness Engineering 101 (10/10): Production Harness — Building Operational Environments for Agents (upcoming)

<!-- toc:end -->

---

## References

### Official docs and research

- [Shinn et al. — Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)
- [Madaan et al. — Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651)
- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [LangGraph — Reflection Patterns](https://langchain-ai.github.io/langgraph/tutorials/reflection/reflection/)

### Verification-friendly references

- [OpenAI Cookbook — Techniques to Improve Reliability](https://cookbook.openai.com/articles/techniques_to_improve_reliability)

Tags: AI Agent, Harness, Production, Reliability
