---
title: "AI Agent 101 (6/10): Multi-Agent Systems"
series: ai-agent-101
episode: 6
language: en
status: publish-ready
targets:
  tistory: false
  hashnode: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Multi-Agent
- Coordination
- Delegation
last_reviewed: '2026-05-15'
seo_description: Separate roles, define delegation protocols, and keep complex multi-agent workflows explainable and debuggable.
---

# AI Agent 101 (6/10): Multi-Agent Systems

Giving one agent search, writing, review, planning, and final response sounds simple at first. But as requests grow and roles multiply, problems appear quickly. Who plans, who verifies, and who takes final responsibility all become unclear.

This is the 6th post in the AI Agent 101 series.

The solution is multi-agent systems. The key point, however, is that adding agents is never the goal itself. Good multi-agent makes the system more explainable by splitting roles; bad multi-agent makes it more complex by splitting roles.

In practice, adopting multi-agent carelessly can increase token cost and handoff count while quality actually drops. So this topic should start not from "how to spin up multiple agents" but from "which tasks genuinely need a delegation structure."

This post frames multi-agent not as a model-count problem but as a role-separation and delegation-protocol problem.

![Multi-agent handoff graph](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/06/06-01-multi-agent-handoff-graph.en.png)
*Multi-agent handoff graph*
> You need multiple agents not when you want more agents, but when responsibilities conflict inside one agent.

## Questions to Keep in Mind

- Where is the line between a task that fits one agent and a task that needs multiple agents?
- What responsibilities should the supervisor, workers, and handoff contract each own?
- How do cost and failure points grow as you split work across more agents?

## Why This Post Matters

Multi-agent is often introduced as a performance tool, but in production it is closer to a tool for structured delegation. When which agent makes which kind of decision and leaves which artifacts is separated, the system stays readable as it grows.

Without role separation, adding agents only makes things worse. They pass the same questions to each other, duplicate searches, leave final-answer responsibility unclear, and make post-mortem tracing nearly impossible. The difficulty of multi-agent is not model count — it is protocol design.

This topic also connects directly to operations and evaluation. Route accuracy, handoff count, per-agent latency, shared state pollution, and unnecessary delegation ratio are metrics that only surface once a multi-agent structure exists. So if you introduce role separation, you must design observability alongside it.

## Core Perspective

Describing multi-agent as "multiple agents working together" is too abstract. A more practical description is a delegation graph where who owns which subtask and what results are left behind is defined. With this framing, the difference between supervisor and worker, reviewer and writer, manager and child agent becomes clear.

Three things matter in this structure. First, who decides the route. Second, which part of the shared state each agent can read and write. Third, who returns the final answer to the user. If these three are ambiguous, adding agents makes the system harder to read, not easier.

In practice, the reason to use multi-agent should be narrowing responsibility and shrinking failure blast radius — not looking sophisticated. That way the operational benefit justifies the extra cost.

> The core of multi-agent is not "there are multiple agents" — it is "roles and handoff rules are explicit in code and state."

## Core Concepts

### Drawing the delegation graph first lets you judge multi-agent necessity faster

![Delegation graph for judging multi-agent necessity](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/06/06-01-multi-agent-patterns.en.png)
*A multi-agent system is safer to view not as multiple models lined up, but as a delegation graph defining who owns which subtask and what state is shared.*

### The Orchestrator pattern is strong at central coordination

```python
from typing import List, Dict
from openai import OpenAI

class WorkerAgent:
    """A specialized worker agent."""

    def __init__(self, name: str, role: str, api_key: str):
        self.name = name
        self.role = role
        self.client = OpenAI(api_key=api_key)

    def execute(self, task: str) -> str:
        """Execute a task."""
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a {self.role}."},
                {"role": "user", "content": task}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content

class OrchestratorAgent:
    """An orchestrator agent that coordinates workers."""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.workers: Dict[str, WorkerAgent] = {}

    def register_worker(self, worker: WorkerAgent) -> None:
        """Register a worker."""
        self.workers[worker.name] = worker

    def plan(self, request: str) -> List[Dict]:
        """Decompose the request into subtasks."""
        worker_list = "\n".join([
            f"- {name}: {w.role}"
            for name, w in self.workers.items()
        ])
        prompt = f"""Break down the following request into subtasks and assign each to the appropriate worker.

Available workers:
{worker_list}

Request: {request}

Respond in JSON format:
[
  {{"worker": "worker_name", "task": "task description"}},
  ...
]
"""
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        import json
        return json.loads(response.choices[0].message.content)

    def handle(self, request: str) -> Dict:
        """Handle the request."""
        subtasks = self.plan(request)
        results = {}
        for subtask in subtasks:
            worker_name = subtask["worker"]
            task = subtask["task"]
            if worker_name in self.workers:
                results[worker_name] = self.workers[worker_name].execute(task)
        return results
```

The Orchestrator manages route and fallback centrally. Stages are clear, approval checkpoints are easy to insert, and logs collect in one place. The downside is creating a single bottleneck and single point of failure.

### Peer-to-Peer is flexible but blurs quickly without protocol

```python
from typing import List, Optional

class PeerAgent:
    """A peer agent."""

    def __init__(self, name: str, role: str, api_key: str):
        self.name = name
        self.role = role
        self.client = OpenAI(api_key=api_key)
        self.peers: List["PeerAgent"] = []
        self.message_history: List[Dict] = []

    def add_peer(self, peer: "PeerAgent") -> None:
        """Add a peer."""
        if peer not in self.peers:
            self.peers.append(peer)

    def send_message(self, recipient: "PeerAgent", message: str) -> str:
        """Send a message to a peer."""
        msg = {
            "from": self.name,
            "to": recipient.name,
            "content": message
        }
        self.message_history.append(msg)
        return recipient.receive_message(self, message)

    def receive_message(self, sender: "PeerAgent", message: str) -> str:
        """Receive a message and respond."""
        prompt = f"""You are {self.name}, a {self.role}.\nMessage from {sender.name}: {message}\n\nRespond appropriately. If you need help from another peer, mention it."""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        reply = response.choices[0].message.content

        self.message_history.append({
            "from": sender.name,
            "to": self.name,
            "content": message,
            "reply": reply
        })
        return reply
```

This pattern is natural for creative collaboration or review-feedback flows. But without rules for who declares termination, when to escalate, or how to block duplicate requests, loops and redundancy appear quickly.

### Running a minimal handoff skeleton locally makes role boundaries visible

The example below lets an orchestrator call child agents and verify what each writes to shared state — without any API calls.

```python
from dataclasses import dataclass, field

@dataclass
class SharedState:
    topic: str
    research_notes: list[str] = field(default_factory=list)
    draft: str = ""
    review_comment: str = ""

def researcher(state: SharedState) -> None:
    state.research_notes = [
        f"{state.topic} is a structure that bundles multiple tool calls into automation.",
        "Without role separation, only handoff cost grows.",
    ]

def writer(state: SharedState) -> None:
    state.draft = " ".join(state.research_notes)

def reviewer(state: SharedState) -> None:
    if "handoff" not in state.draft:
        state.review_comment = "Handoff cost explanation is missing."
    else:
        state.review_comment = "Pass"

state = SharedState(topic="multi-agent systems")
researcher(state)
writer(state)
reviewer(state)
print(state)
```

**Expected output:**

```text
SharedState(topic='multi-agent systems', research_notes=['multi-agent systems is a structure that bundles multiple tool calls into automation.', 'Without role separation, only handoff cost grows.'], draft='multi-agent systems is a structure that bundles multiple tool calls into automation. Without role separation, only handoff cost grows.', review_comment='Pass')
```

Even this minimal skeleton immediately reveals whether each agent freely mutates the entire shared state or writes only to its own fields. Verifying these boundaries before attaching a real multi-agent framework is much safer.

### The Hierarchical pattern resembles a large org chart

A parent agent delegates to children, and children handle even smaller subtasks. Useful for decomposing large work hierarchically, but as depth increases, context loss and reporting cost grow together. Child output contracts must be designed very narrowly.

### Shared state should expose only the minimum contract

- Share only core fields like `route`, `current_owner`, `worker_result`.
- Do not expose each agent's private scratchpad to global shared state.
- Fix input and output schemas per handoff.
- Assign final assembly responsibility to one agent or a separate finalizer.
- Log delegation rationale so route quality can be evaluated.

### Handoff failures usually start from missing protocol

- If the orchestrator does not log the routing reason, post-hoc analysis of why a particular worker was chosen becomes impossible.
- If workers return only free-form text, the next agent can read it but cannot validate it.
- If the reviewer and writer overwrite the same shared state field concurrently, only the last write survives and root-cause tracing breaks.
- If no termination condition exists, peer-to-peer structures easily send the same request bouncing between agents.

Before adding agents, fix four things: `input schema`, `output schema`, `max handoff count`, and `final responsible agent`. Only with these four does delegation remain an explainable structure.

## Production Design Details

### The separation criterion for roles is responsibility boundary, not model performance

The common question when reviewing multi-agent composition is "does splitting models make it smarter?" The actually important criterion is responsibility boundary. If planner, executor, and reviewer responsibilities conflict, debugging becomes harder than with a single agent.

| Role | Input | Output | Failure Mode |
| --- | --- | --- | --- |
| Planner | Goal, policy | Execution plan | Over-decomposition |
| Executor | Single task instruction | Tool result | Wrong tool selection |
| Reviewer | Plan + result | Approve/revise instruction | Excessive rejection |

### Message bus schema example

```json
{
  "message_id": "uuid",
  "trace_id": "uuid",
  "from": "planner",
  "to": "executor",
  "intent": "run_tool",
  "payload": {"tool": "search_docs", "args": {"q": "..."}},
  "deadline_ms": 4000,
  "retry": 0
}
```

Leaving inter-agent communication as free text repeats parsing errors and responsibility shifting. Enforcing a structured envelope is what creates operational viability.

### Supervisor pattern minimal implementation

```python
def supervisor(goal: str):
    plan = planner_agent(goal)
    for task in plan["tasks"]:
        result = executor_agent(task)
        verdict = reviewer_agent(task=task, result=result)
        if verdict["status"] == "retry":
            result = executor_agent({**task, "hint": verdict.get("hint")})
        if verdict["status"] == "fail":
            return {"ok": False, "reason": "review_failed", "task": task}
    return {"ok": True}
```

The key is that the supervisor owns a retry budget and termination condition. Without a higher-level controller, each agent could spin in an infinite loop.

### Multi-agent observability metrics

| Metric | Meaning |
| --- | --- |
| cross_agent_hops | Hops between agents per goal |
| reviewer_reject_rate | Reviewer rejection ratio |
| arbitration_latency | Supervisor mediation delay |
| dead_letter_count | Messages that failed processing |

Multi-agent has division-of-labor benefits but high communication and synchronization costs. Operating without metrics produces a system slower and more expensive than a single agent.

## Operations Notes

### Failure classification template

In production you never close a failure with "the model got it wrong." Splitting failure axes makes improvement priorities clear.

| Axis | Question | Example |
| --- | --- | --- |
| Planning failure | Was the goal decomposed wrong? | Unnecessary step repeated 6 times |
| Execution failure | Did a tool call fail? | Timeout, 429, schema mismatch |
| Verification failure | Was result checking insufficient? | Wrong observation adopted |
| Policy failure | Was a safety boundary crossed? | Sensitive data sent externally |

### Prompt and tool version pinning

```json
{
  "run_id": "run_2026_05_21_001",
  "model": "gpt-4.1-mini",
  "prompt_version": "agent-101-en-v3",
  "tool_schema_version": "tools-v5",
  "policy_version": "policy-2026-05"
}
```

Version fields alone dramatically speed up regression analysis — immediately narrowing whether a drop came from a model, prompt, or tool change.

### Observability event example

```python
import json
from datetime import datetime

def emit_event(event_type: str, payload: dict):
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "payload": payload,
    }
    print(json.dumps(record, ensure_ascii=False))

emit_event("agent.step", {"step": 2, "tool": "search_docs", "latency_ms": 412})
```

Structured logs first, then expand to OpenTelemetry/ELK/Grafana later at low migration cost.

### Deployment checklist

- Confirm model API keys are separated into environment variables and Secret Manager.
- Verify `max_steps`, `timeout_ms`, `retry_budget` defaults fit the production profile.
- Check that fallback response wording does not give overconfident assurances during outages.
- Keep alarm thresholds (`error_rate`, `p95_latency`, `policy_violation_rate`) identical in docs and code.

### Cost control points

| Item | Description | Recommended Default |
| --- | --- | --- |
| max_steps | Max loops per execution | 4–8 |
| max_tool_calls | Tool call ceiling | 3–6 |
| input_token_budget | Input token budget | Per-service policy |
| output_token_budget | Output token budget | Per-service policy |

### CI gate example

```bash
python3 scripts/eval_agent.py --dataset eval/agent_core_en.jsonl --min-success 0.82
python3 scripts/check_tool_schema.py --strict
python3 scripts/check_prompt_version.py --require-changelog
```

## Common Misconceptions

- Adding more agents does not automatically improve quality — role boundaries come first.
- Making the orchestrator handle every detail makes it indistinguishable from a single agent.
- Opening shared state wide seems flexible but quickly explodes coupling and debug difficulty.
- Peer-to-peer looks free but without termination rules, infinite handoff loops emerge easily.
- Multi-agent looks expert-level but many problems are better solved with single-agent + better tools.

## Operations Checklist

- [ ] Compared multi-agent necessity against a single-agent alternative
- [ ] Stated who decides the route and who owns the final answer
- [ ] Defined handoff input/output schemas and termination conditions
- [ ] Limited shared state to minimum fields
- [ ] Measuring per-agent latency, route accuracy, and handoff count

## Wrap-Up

Multi-agent is not a technique for bundling multiple models impressively. It is a method for separating roles, clarifying delegation boundaries, and fixing final responsibility location to create a more explainable automation structure. The core is protocol quality, not agent count.

Good multi-agent design makes each agent smaller, shared state narrower, and the final assembly point sharper. Bad design makes it harder to tell who did what as agents increase.

The next post covers how to evaluate these systems. Unless you measure whether routes were appropriate, trajectories were efficient, and final success rate holds, you cannot justify multi-agent cost.

## Answering the Opening Questions

- **Where is the line between a task that fits one agent and a task that needs multiple agents?**
  - Consider multiple agents when domains, tools, success criteria, or task ownership are distinct enough that one prompt and state contract become overloaded.
- **What responsibilities should the supervisor, workers, and handoff contract each own?**
  - The supervisor owns routing and stopping decisions, workers own assigned execution, and the handoff contract owns the input/output shape passed between them.
- **How do cost and failure points grow as you split work across more agents?**
  - More agents add LLM calls, handoff gaps, state mismatches, and supervisor bottlenecks. Split only when role separation pays for that overhead.

<!-- toc:begin -->
## In this series

- [AI Agent 101 (1/10): What Is an AI Agent?](./01-what-is-an-ai-agent.md)
- [AI Agent 101 (2/10): Context Engineering](./02-context-engineering.md)
- [AI Agent 101 (3/10): Tool Use Fundamentals](./03-tool-use-fundamentals.md)
- [AI Agent 101 (4/10): Agent Workflow Design](./04-agent-workflow-design.md)
- [AI Agent 101 (5/10): Memory and State](./05-memory-and-state.md)
- **AI Agent 101 (6/10): Multi-Agent Systems (current)**
- AI Agent 101 (7/10): Agent Evaluation (upcoming)
- AI Agent 101 (8/10): Error Handling and Reliability (upcoming)
- AI Agent 101 (9/10): Production Operations (upcoming)
- AI Agent 101 (10/10): Building Your First Agent (upcoming)

<!-- toc:end -->

## References

### Official Documentation

- [Anthropic - Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [LangGraph - Multi-agent workflows](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)
- [OpenAI Platform - Agents guide](https://platform.openai.com/docs/guides/agents)
- [CrewAI Documentation](https://docs.crewai.com/)

### Related Series

- [LangGraph 101 - Multi-agent systems](../../langgraph-101/ko/05-multi-agent.md)
- [AI Evaluation 101 - System evaluation perspective](../../ai-evaluation-101/ko/01-why-evaluate-llm-apps.md)

- [Example code for this post (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-agent-101/en/06-multi-agent-systems)

Tags: AI Agent, LLM, Tool Use, Python
