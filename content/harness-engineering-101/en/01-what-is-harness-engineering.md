---
title: What Is Harness Engineering?
series: harness-engineering-101
episode: 1
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
seo_description: Good agents are not made by good models alone. You must design the
  environment, constraints, tools, and verification loops the model works inside.
---

# What Is Harness Engineering?

Every frontier-model release triggers the same hope: maybe this is the one that finally makes agents production-ready. In practice, teams using the same model still land in very different places. One team gets a stable operator. Another gets an expensive demo that keeps guessing.

The difference is usually not the model. It is the work environment around the model: what task it receives, what context it sees, what tools it may touch, how completion is verified, and where risky actions stop.

This is the first post in the Harness Engineering 101 series. It establishes the operating model for the rest of the series, so Task, Context, Constraint, Tool, Test, Feedback, Approval, and Observability read as one system rather than eight isolated tips.

---

## Questions this chapter answers

- Why do agents still behave unpredictably even when the underlying model is strong?
- What does the word harness mean when you apply it to an agent system?
- How does an agent without a harness differ from one with a harness in code and in operations?
- What questions do the eight harnesses answer across the rest of the series?
- Why is Harness Engineering a different decision layer from framework choice?

> A reliable agent is decided more by the system around the model than by the model alone. Harness Engineering is the work of designing that surrounding system.

![What is harness Engineering](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/01/01-01-what-is-harness-engineering.en.png)

*What is harness Engineering*

## Why this chapter matters

If you miss this frame, every later decision starts to look like prompt tuning or framework preference. Teams keep swapping models, adding tools, and lengthening instructions without being able to explain why the system still drifts, loops, or performs risky actions at the wrong time.

Once you look at the problem through the harness lens, the order of questions changes. You ask what the agent must do, what it should see, what it must never do, which tools it may call, how completion is proven, how failure is recovered, where a human must stop it, and how a run can be replayed later. That is the shift from demo thinking to operating-system thinking.

## A Good Model Alone Is Not Enough

Every time a new frontier model lands — GPT-4, Claude 3.5, Gemini 1.5 — the same hope follows: "now real agents are finally possible." But with the same model, one team builds a reliable automation system and another team gets different results on every run. The difference is rarely the model. It is **the environment around the model**.

Even a skilled person produces poor work at a messy desk with broken tools. Agents work the same way. Without a clear task definition, clean context, safe tools, explicit completion criteria, a loop that recovers from failure, an approval flow for risky actions, and observability into what was done, even a capable model looks incompetent.

Harness Engineering is the practice of designing that environment. Building a good agent is not about picking a good model. It is about constructing a system the model can work inside.

## The simplest mental model: design the workbench outside the model

Harness Engineering is easiest to understand if you picture the model as a capable worker and the harness as the workbench around that worker. A stronger worker helps, but a messy bench, unclear instructions, unsafe tools, and missing verification still produce bad work.

That is why production failures should not default to “the model is weak.” More often the agent had to infer too much, saw too much irrelevant context, had access to the wrong tool surface, or claimed completion without an external check. The harness tells you where to debug first.

---

## What Is a Harness?

The English word "harness" originally describes the equipment fitted onto a horse or working animal. It is not a restraint. It is the device that channels the animal's strength in a useful direction. Without a harness, a horse's power scatters and stays uncontrolled. With a harness, the same horse pulls a carriage, plows a field, or carries a rider safely.

The harness in Harness Engineering means the same thing. It is the device that channels an AI model's capability in the direction you want. You do not change the model itself. You design the environment, inputs, constraints, tools, and verification around the model so that it works reliably.

The word is already familiar in software engineering. A test harness provides the environment a function runs inside (setup, teardown, fixtures). A cable harness in embedded systems connects multiple parts in a fixed pattern. An AI agent harness follows the same idea. You set up the environment in advance, and the model works within it.

---

## Agents Without and With a Harness

![Agents without and with a harness](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/01/01-02-agents-without-and-with-a-harness.en.png)

*Agents without and with a harness*
Without a harness, an agent often looks like this:

```python
from openai import OpenAI

client = OpenAI()

def run_agent(user_message: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_message}],
    )
    return response.choices[0].message.content or ""

# Usage
answer = run_agent("Build a sales report for our company")
print(answer)
```

This agent answers once and stops. There are no tools, no memory, and no verification. There is no way to judge whether the result is good, and the same question yields different answers on different runs. It cannot ship to production.

With a harness applied, the same task becomes:

```python
from typing import Any
from pydantic import BaseModel

class TaskSpec(BaseModel):
    """Task Harness: clear inputs and completion criteria."""
    goal: str
    inputs: dict[str, Any]
    completion_criteria: list[str]

class AgentContext(BaseModel):
    """Context Harness: what to show and what to hide."""
    system_prompt: str
    allowed_data_sources: list[str]
    forbidden_topics: list[str]

class ToolPolicy(BaseModel):
    """Constraint + Tool Harness: allowed and forbidden actions."""
    allowed_tools: list[str]
    require_approval: list[str]
    max_iterations: int = 5

def run_agent_with_harness(task: TaskSpec, ctx: AgentContext, policy: ToolPolicy) -> dict[str, Any]:
    """Agent execution with harnesses applied."""
    trace = []  # Observability Harness: record every step

    for iteration in range(policy.max_iterations):
        decision = think_with_context(task, ctx, trace)
        trace.append({"iteration": iteration, "decision": decision})

        if decision["action"] in policy.require_approval:
            if not request_human_approval(decision):
                trace.append({"approval": "denied"})
                break

        result = execute_tool(decision, policy.allowed_tools)
        trace.append({"result": result})

        if check_completion(result, task.completion_criteria):
            return {"status": "success", "trace": trace, "result": result}

    return {"status": "incomplete", "trace": trace}
```

The code is longer, but the agent now guarantees:

- The task is well defined (Task Harness).
- The information it sees is scoped (Context Harness).
- Allowed tools and approval-required actions are explicit (Constraint Harness).
- Loops cannot run forever (Tool Harness).
- Every decision is recorded (Observability).

Same model, completely different system.

One practical difference is that the harnessed version gives the rest of the system something concrete to verify. The task has a schema, approvals can be intercepted, and the trace can be inspected after the run. That turns “the model said it is done” into something a verifier, an approver, and an on-call engineer can all reason about.

```text
Harness-free run
- Input: "Build a sales report"
- Output: free-form answer
- Verification: none
- Replay path: none

Harnessed run
- Input: TaskSpec + scoped context + tool policy
- Output: typed result + trace
- Verification: completion criteria checked
- Replay path: trace and tool history available
```

**Expected output:** the harnessed path produces artifacts the rest of your system can inspect, reject, retry, or replay. The unharnessed path produces only text.

---

## The Eight Harnesses

![The eight harnesses](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/01/01-03-the-eight-harnesses.en.png)

*The eight harnesses*
This series covers eight harnesses. Each one designs a different aspect of the agent.

| Harness | Question it answers | Episode |
| --- | --- | --- |
| Task | "What should the agent do?" | 2 |
| Context | "What should the agent see?" | 3 |
| Constraint | "What must the agent not do?" | 4 |
| Tool | "What can the agent use?" | 5 |
| Test | "How do we know it is done?" | 6 |
| Feedback | "How does it recover from failure?" | 7 |
| Approval | "Where must a human stop it?" | 8 |
| Observability | "How do we trace what it did?" | 9 |

Episode 10 integrates all of them into a Production Harness.

These harnesses are not independent. The Tool Harness is defined inside the Constraint Harness. The Approval Gate intercepts specific actions inside the Tool Harness. Observability records the state of every other harness. They have to be designed together to form a coherent system.

---

## Harness vs Framework

People often ask how Harness Engineering relates to frameworks like LangChain, LangGraph, or CrewAI. They live at different layers.

| Aspect | Framework | Harness Engineering |
| --- | --- | --- |
| What it is | A code library | A set of design principles and patterns |
| What it provides | APIs, abstractions, utilities | Decisions about what environment to build |
| Example | A LangGraph node and edge | A Task Harness definition |
| When you choose it | Picked once | Designed for every agent |

Frameworks are tools. Harness Engineering is how you think about what to build with those tools. You can build an agent without a harness using LangGraph, and you can build a well-harnessed agent using only the standard library.

In practice the two combine. Use Harness Engineering first to decide what task, context, constraint, tool, test, feedback, approval, and observability your agent needs. Then use a framework like LangGraph or CrewAI to express that design in code. Design first, framework second.

---

## When You Need Harness Engineering

Not every LLM use needs a full harness. Look for these signals.

**1. The same input produces different results.**
Non-deterministic behavior signals weak Task and Context Harnesses. Your inputs and the scope of context are not pinned down.

**2. You cannot explain what the agent did.**
When a user asks "why did it answer that way?" and you cannot answer, you have no Observability Harness. Every decision and tool call must be recorded.

**3. The agent performs risky actions automatically.**
If the agent deletes data, sends emails, or makes payments without human confirmation, you need an Approval Gate.

**4. Tool call costs explode.**
If the agent repeats the same search 100 times or loops forever, your Constraint and Tool Harnesses are missing.

**5. You cannot tell when the agent is done.**
Without a Test Harness, "I am done" from the agent means nothing.

If you see any one of these, switching models will not save you. You need to design harnesses.

## A minimal verification loop for a harnessed agent

The key difference between a demo agent and a production candidate is not how clever the answer sounds. It is whether the rest of the system can reject an incomplete answer automatically.

```python
from pydantic import BaseModel, ValidationError

class ReportResult(BaseModel):
    title: str
    summary: str
    next_actions: list[str]

def verify_report_result(payload: dict) -> tuple[bool, str]:
    try:
        result = ReportResult.model_validate(payload)
    except ValidationError as exc:
        return False, f"schema validation failed: {exc.errors()}"

    if len(result.next_actions) < 2:
        return False, "need at least two follow-up actions"

    return True, "pass"
```

This is a tiny example, but it captures the real point. Once outputs are pinned down, the rest of the harness can do useful work: Test Harness can fail the run, Feedback Loop can retry with guidance, Approval Gate can hold risky actions, and Observability can record which check failed.

---

## A Small Example: Email Classification Agent

![A small Example: email classification agent](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/01/01-04-a-small-example-email-classification-age.en.png)

*A small Example: email classification agent*
Enough abstraction. Consider a small task: "classify incoming emails by priority." Without a harness:

```python
def classify_email(email_body: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Classify the email as high, medium, or low."},
            {"role": "user", "content": email_body},
        ],
    )
    return response.choices[0].message.content or ""
```

There are many problems. Output format is not guaranteed. The same email yields different labels. Classification criteria are vague. There is no way to detect a wrong label.

With a harness applied:

```python
from enum import Enum
from pydantic import BaseModel, Field

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ClassificationResult(BaseModel):
    """Test Harness: schema pins down completion criteria."""
    priority: Priority
    reason: str = Field(..., min_length=10)
    confidence: float = Field(..., ge=0.0, le=1.0)

SYSTEM_PROMPT = """You are an email priority classifier.

Classification criteria (Context Harness):
- high: response required within 24 hours. Customer complaints, payment failures, security issues.
- medium: response required within 3 business days. General inquiries, feature requests.
- low: response optional. Marketing, notifications, automated emails.

Rules (Constraint Harness):
- Use only one of the three categories above.
- Reason must be a single sentence explaining the basis for the label.
- Confidence must be a number between 0.0 and 1.0.
- Do not infer information not present in the email body."""

def classify_email_with_harness(email_body: str) -> ClassificationResult:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": email_body},
        ],
        response_format=ClassificationResult,  # Test Harness
    )
    return ClassificationResult.model_validate_json(response.choices[0].message.content)
```

The function now guarantees:

- Output always follows `ClassificationResult` schema (Test Harness).
- Classification criteria are spelled out in the system prompt (Context Harness).
- Disallowed categories cannot appear (Constraint Harness).
- Low `confidence` can be detected and routed for human review (Approval link).

Same model, same task, but the harnessed version is something you can actually run in production.

---

## Common Mistakes

**1. Believing a model swap will fix everything.**
Teams expect that switching to GPT-4o makes things accurate, or to Claude 3.5 makes them smarter. Models do differ, but without a harness no model becomes a reliable system.

**2. Trying to build all eight harnesses at once.**
Attempting to design every harness up front blocks you from starting. Begin with Task and Context Harnesses, then add the others where pain appears.

**3. Confusing harnesses with frameworks.**
Adopting LangGraph does not give you harnesses for free. Frameworks are tools. Harnesses are designs. You can have one without the other.

**4. Adding observability last.**
"First make it work, then add logs" is a common postponement. Without observability you cannot debug, so you end up rewriting from scratch. Record every decision and tool call from day one.

**5. Automating risky actions without an Approval Gate.**
"It is just a test environment" leads to automated deletes, sends, and payments that eventually hit production data. Risky actions must pass an Approval Gate from the start, regardless of environment.

---

## Key Takeaways

- A good agent is not built from a good model alone. The environment (the harness) the model works inside must be designed too.
- A harness channels model capability in the direction you want. You design the surroundings, not the model itself.
- This series covers eight harnesses: Task, Context, Constraint, Tool, Test, Feedback, Approval, and Observability.
- Harness Engineering is a design discipline, not a framework. Use frameworks like LangGraph as tools to implement your harness design.
- Non-deterministic behavior, undebuggable runs, automated risky actions, runaway costs, and "is it done?" ambiguity are signals that you need to start designing harnesses.

## Operational checklist

- [ ] Before changing models, check whether Task, Context, Tool, Test, or Approval gaps explain the failure first.
- [ ] Treat harness design as a system problem, not as a prompt-writing problem.
- [ ] Require every serious agent to expose completion criteria and a replay path.
- [ ] Keep framework choice separate from harness design documents and reviews.
- [ ] Use the eight harnesses as a diagnostic map when production behavior drifts.

<!-- toc:begin -->
## In this series

- **What Is Harness Engineering? (current)**
- Task Harness — Turning Vague Work into Executable Tasks (upcoming)
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

- [Building Effective Agents — Anthropic](https://www.anthropic.com/research/building-effective-agents)
- [LLM Powered Autonomous Agents — Lilian Weng](https://lilianweng.github.io/posts/2023-06-23-agent/)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)

### Related series

- [LangGraph 101 — Multi-Agent Systems](../../langgraph-101/en/05-multi-agent.md)
- [AI Safety & Guardrails 101 — Building Production Guardrail Systems](../../ai-safety-guardrails-101/en/10-production-guardrail-system.md)

Tags: AI Agent, Harness, Production, Reliability
