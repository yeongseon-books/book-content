---
title: Task Harness — Turning Vague Work into Executable Tasks
series: harness-engineering-101
episode: 2
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
- Reliability
- Production
last_reviewed: '2026-05-14'
seo_description: Give an agent a vague instruction and you get a vague result. The
  Task Harness turns vague work into executable tasks with clear inputs, outputs…
---

# Task Harness — Turning Vague Work into Executable Tasks

The fastest way to make an agent expensive is to ask it to do a vague job. Humans respond to ambiguity by asking back. Agents usually respond by filling in the blanks on their own.

Those blanks quickly turn into concrete risk: the wrong data source, the wrong output format, the wrong completion bar, or the wrong scope of work. Once that ambiguity reaches tool calls, quality issues become cost incidents.

This is post 2 in the Harness Engineering 101 series. Here we turn business goals into executable TaskSpecs so later harnesses have something stable to operate on.

---

## Questions this chapter answers

- Why should you separate a business goal from an agent task?
- Which fields are the minimum for an executable TaskSpec?
- How do you decide that a task is too large and must be decomposed?
- How do natural-language completion conditions become machine-checkable criteria?
- Why should prompts, verifiers, and eval datasets derive from the same TaskSpec?

> Goals tell the business where to go. Tasks tell the agent what to do now. Task Harness is the layer that turns one into the other.

![Task harness - turning vague work into executable tasks](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/02/02-01-task-harness-turning-vague-work-into-exe.en.png)

*Task harness - turning vague work into executable tasks*
## Vague Work Cannot Be Executed

Hand "tidy up our team report" to an agent and the result is not guaranteed. Which report? Where do you fetch it from? Does "tidy up" mean summarize, restructure, or convert format? A human would ask back. An agent does not. It guesses. And it guesses wrong.

Task Harness is the design that converts vague work into an executable task with explicit inputs, outputs, and completion criteria. Without this conversion, every other harness loses its meaning. Context, Constraint, and Test all start from "what task is this for?"

This article covers the components of a Task, how to write a Task Spec, and how to decompose vague requests into executable tasks.

---

## The Four Components of a Task

![The four components of a task](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/02/02-02-the-four-components-of-a-task.en.png)

*The four components of a task*
An executable task has four parts.

1. **Goal**: What must be achieved. Write it in one sentence.
2. **Inputs**: Information and resources the agent may use. Data sources, parameters, preconditions.
3. **Outputs**: The format and location of the deliverable.
4. **Completion criteria**: How you decide the task is done. Must be automatically verifiable.

When all four are explicit, the task is executable. If any is missing, the agent guesses.

```python
from pydantic import BaseModel, Field
from typing import Any

class TaskSpec(BaseModel):
    """Specification for an executable task."""
    goal: str = Field(..., description="Goal to achieve (one sentence)")
    inputs: dict[str, Any] = Field(..., description="Input data and resources")
    outputs: dict[str, Any] = Field(..., description="Output format and location")
    completion_criteria: list[str] = Field(
        ...,
        description="Conditions to verify completion (automatable)",
    )

    def is_executable(self) -> bool:
        """Check whether the task is executable."""
        return bool(
            self.goal
            and self.inputs
            and self.outputs
            and self.completion_criteria
        )

# Example: a clear task
task = TaskSpec(
    goal="Generate a daily summary report from sales data for the past 7 days",
    inputs={
        "data_source": "postgres://reports/sales",
        "date_range": {"start": "2026-04-26", "end": "2026-05-02"},
        "filters": {"region": "APAC"},
    },
    outputs={
        "format": "markdown",
        "destination": "s3://reports/daily/2026-05-03.md",
        "schema": "ReportSchema",
    },
    completion_criteria=[
        "All required sections are present",
        "All numeric figures match the source data",
        "File is uploaded to the destination",
    ],
)

assert task.is_executable()
```

The four-part TaskSpec is the minimum. Without this structure, you cannot write a system prompt, a verification function, or a test for the task.

---

## Goal Versus Task

Goal and Task are different. Confusing them is the most common cause of harness failure.

A **Goal** is what the business wants. "Improve customer support quality." "Reduce onboarding friction." Goals are abstract, long-term, and not directly executable.

A **Task** is what the agent will execute right now. "Reply to the 12 unanswered tickets in the support inbox in Korean using template T-04." Tasks are concrete, short-term, and have completion criteria.

One Goal usually decomposes into many Tasks. The job of Task Harness is the decomposition.

```python
def decompose_goal(goal: str) -> list[TaskSpec]:
    """Decompose a Goal into executable Tasks."""
    # Goal: "Improve customer support quality"
    # → Tasks:
    return [
        TaskSpec(
            goal="Answer the 12 unanswered tickets from the past 24 hours",
            inputs={"queue": "support", "status": "unanswered", "max_age_hours": 24},
            outputs={"format": "ticket_reply", "destination": "zendesk"},
            completion_criteria=[
                "All 12 tickets have a reply",
                "Each reply uses an approved template",
                "Each reply links to a knowledge base article",
            ],
        ),
        TaskSpec(
            goal="Group last week's tickets by topic and produce statistics",
            inputs={"date_range": "last_week", "queue": "support"},
            outputs={"format": "json", "destination": "reports/topics.json"},
            completion_criteria=[
                "All tickets are assigned to a topic",
                "Each topic has count and percentage",
                "Top 5 topics include sample ticket IDs",
            ],
        ),
    ]
```

Give the agent the Task. The Goal is the human's job.

---

## Properties of a Good Task

Not every task is good. Three properties separate good tasks from bad.

**1. Single deliverable.** A task should produce one deliverable. "Reply to tickets and update the CRM" is two tasks. Split them. Single deliverable means single completion criteria, single retry unit, single rollback unit.

**2. Bounded tool calls.** A good task finishes in fewer than five tool calls. Beyond that, decompose. This is not a hard rule but a heuristic — long tool sequences amplify error compounding.

**3. Auto-verifiable completion criteria.** Criteria a human must read and judge cannot be tested, cannot be evaluated automatically, and cannot trigger retry decisions. Criteria must be expressible as code.

```python
from collections.abc import Callable

class VerifiableTask(TaskSpec):
    """Task with executable completion criteria."""
    verifier: Callable[[Any], bool] = Field(..., exclude=True)

    def verify(self, output: Any) -> bool:
        """Verify the output."""
        return self.verifier(output)

def verify_report(output: dict) -> bool:
    """Verifier for the daily summary report."""
    required_sections = ["summary", "metrics", "anomalies", "next_actions"]
    return (
        all(section in output for section in required_sections)
        and isinstance(output.get("metrics"), dict)
        and len(output.get("anomalies", [])) >= 0
    )

task = VerifiableTask(
    goal="Generate the daily summary report",
    inputs={"date": "2026-05-03"},
    outputs={"format": "json"},
    completion_criteria=[
        "Required sections are present",
        "metrics is a dict",
        "anomalies field exists",
    ],
    verifier=verify_report,
)

# Verify the agent's output
result = {"summary": "...", "metrics": {}, "anomalies": [], "next_actions": []}
assert task.verify(result)
```

Without `verify()`, you cannot decide whether to retry. Without that decision, the harness does not exist.

---

## Decomposing Vague Requests Into Tasks

![Decomposing vague requests into tasks](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/02/02-03-decomposing-vague-requests-into-tasks.en.png)

*Decomposing vague requests into tasks*
Real users do not deliver TaskSpecs. They say things like "do something about it." Task Harness must convert this into an executable task.

A three-step procedure works.

**Step 1: Restate the request as a Goal.**
"Do something about it" → "I want our team's productivity to improve."

**Step 2: Identify candidate Tasks for the Goal.**
- Send a weekly retrospective summary
- Visualize the meeting load
- Detect blockers and notify the manager

**Step 3: Convert each candidate into a TaskSpec.**
For each candidate, fill in Goal, Inputs, Outputs, and Completion criteria. Anything that cannot be filled in becomes a clarifying question for the human.

```python
class TaskCandidate(BaseModel):
    """Candidate task — incomplete spec."""
    description: str
    missing_fields: list[str] = []

    def to_spec(self, **filled) -> TaskSpec | None:
        """Convert to a TaskSpec. Returns None if fields are missing."""
        if self.missing_fields:
            return None
        return TaskSpec(**filled)

def request_to_tasks(request: str) -> list[TaskCandidate]:
    """Convert a vague request into task candidates."""
    # In production this is built with LLM + templates.
    return [
        TaskCandidate(
            description="Send a weekly retrospective summary",
            missing_fields=["recipient", "data_source"],
        ),
        TaskCandidate(
            description="Visualize the meeting load",
            missing_fields=["chart_type", "time_range"],
        ),
    ]

# Workflow
candidates = request_to_tasks("Do something about productivity")
for c in candidates:
    if c.missing_fields:
        print(f"Need clarification: {c.description}")
        print(f"  Missing fields: {c.missing_fields}")
```

Asking back is part of Task Harness. An agent that does not ask back is not collaborating — it is gambling.

---

## Task Spec As Single Source of Truth

![Task spec as single source of truth](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/02/02-04-task-spec-as-single-source-of-truth.en.png)

*Task spec as single source of truth*
Once a TaskSpec exists, everything else is derived from it.

- **System prompt**: generated from `goal` and `completion_criteria`
- **Allowed tools**: filtered from `inputs`
- **Verifier**: derived from `completion_criteria`
- **Retry policy**: derived from `completion_criteria` violation type
- **Eval dataset**: generated from variations of TaskSpec

```python
def task_to_system_prompt(task: TaskSpec) -> str:
    """Generate a system prompt from a TaskSpec."""
    criteria = "\n".join(f"- {c}" for c in task.completion_criteria)
    return f"""You are an AI agent.

Goal: {task.goal}

Completion criteria (all required):
{criteria}

Output format: {task.outputs.get('format')}
Output destination: {task.outputs.get('destination')}

Available inputs:
{task.inputs}

Verify each criterion before reporting completion.
"""

def task_to_eval_dataset(task: TaskSpec, n: int = 10) -> list[dict]:
    """Generate eval cases from a TaskSpec."""
    # Vary inputs to create test cases
    return [
        {"task": task.model_dump(), "variation": i, "expected_pass": True}
        for i in range(n)
    ]
```

When the TaskSpec is the single source of truth, prompt, verifier, and evals stay in sync. When they live in separate places, the prompt evolves and verifier and evals drift behind.

---

## Common Mistakes

**1. Using the Goal as the Task directly.**
Throwing "handle customer support well" straight at the agent. An undecomposed Goal is not executable. Convert to a clear TaskSpec first.

**2. Writing completion criteria only in natural language.**
"The report must be accurate" cannot be auto-verified. Rewrite into a code-expressible form.

**3. Making tasks too large.**
"Migrate the whole system" cannot be done in one agent run. Split into 5–10 smaller tasks.

**4. Not specifying inputs and letting the agent find its own.**
"Get the data you need and do the work" gives the agent free search. That leads to cost blowups and wrong sources. Specify the available inputs.

**5. Describing output format only in natural language without a schema.**
"Output as JSON" gives a different structure every time. Pin the format with a schema like Pydantic.

---

## Key Takeaways

- Task Harness converts vague work into executable tasks with explicit Goal, Inputs, Outputs, and Completion Criteria.
- A good task produces one deliverable, finishes in fewer than five tool calls, and has auto-verifiable completion criteria.
- Goal and Task are different. Goal is the business objective; Task is the execution unit. Give the agent the Task.
- Completion criteria must be objective, automatically verifiable, and measurable. Rewrite natural-language statements into code expressions.
- A single TaskSpec produces the system prompt, the verifier, and the eval dataset. The Task is the single source of truth.

## Operational checklist

- [ ] Require Goal, Inputs, Outputs, and Completion Criteria before the agent starts work.
- [ ] Keep each task scoped to one deliverable and one retry unit.
- [ ] Turn completion criteria into code-expressible checks, not review-only prose.
- [ ] Send missing fields back as clarifying questions instead of letting the agent guess.
- [ ] Generate prompts, verifiers, and eval cases from the same TaskSpec.

<!-- toc:begin -->
## In this series

- [What Is Harness Engineering?](./01-what-is-harness-engineering.md)
- **Task Harness — Turning Vague Work into Executable Tasks (current)**
- Context Harness — Designing What the Agent Should Know and Not Know (upcoming)
- Constraint Harness — Defining Rules, Boundaries, and Forbidden Actions (upcoming)
- Tool Harness — Designing Safe Tools for Agents (upcoming)
- Test Harness — Turning Completion Criteria into Tests (upcoming)
- Feedback Loops — Building Structures That Let Agents Recover from Failure (upcoming)
- Approval Gates — Designing Where Humans Must Approve (upcoming)
- Observability — Tracing and Replaying Agent Work (upcoming)
- Production Harness — Building Operational Environments for Agents (upcoming)

<!-- toc:end -->

---

## References

### Official docs and research

- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [OpenAI — A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
- [Pydantic Documentation — Models](https://docs.pydantic.dev/latest/concepts/models/)
- [Google Cloud — Agent Design Patterns](https://cloud.google.com/architecture/ai-agent-patterns)

Tags: AI Agent, Harness, Production, Reliability
