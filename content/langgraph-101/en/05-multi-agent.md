---
title: "LangGraph 101 (5/6): Multi-agent systems"
series: langgraph-101
episode: 5
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LangGraph
- Agent
- Python
- LLM
last_reviewed: '2026-05-01'
seo_description: A multi-agent graph is not just more LLM calls. It is a delegation
  structure where roles, handoffs, and state boundaries stay explicit.
---

# LangGraph 101 (5/6): Multi-agent systems

If you keep pushing every task into one agent, the setup often feels efficient at first. One prompt, one model, one answer. Then the request grows. Now the system needs to write code, explain concepts, inspect failures, and maybe coordinate tool output too. Once all of that lives inside one prompt, role boundaries blur fast, and the graph becomes much harder to reason about than it first appeared.

The operational version of that problem is even more obvious. One request gets routed by a worker when a supervisor should have made the decision. Another worker starts reinterpreting output that should have gone straight to final assembly. A third system keeps handing work from one agent to another until cost grows while clarity shrinks. I have seen teams try to solve that by upgrading the model, when the deeper issue was structural: delegation and responsibility were never made explicit enough in the graph.

Things get especially messy when no real supervisor exists. If nobody clearly owns routing, fallback, and stop conditions, the system can look collaborative from the outside while behaving like a broken prompt collage underneath. One worker calls another, that worker reframes the request again, and before long you have multiple agents participating without any clear answer to who was actually responsible for the decision.

This is the fifth article in the LangGraph 101 series. Here I want to frame multi-agent design not as “more LLM calls,” but as **a graph structure in which a supervisor coordinates a cluster of role-separated nodes**. That is the shift that matters. **Multi-agent quality is less about model count and more about how clearly role boundaries, handoffs, and state contracts are separated.**

Once that lens is in place, the final chapter becomes easier too. A complete LangGraph system is really just state, branching, tool use, and multi-agent orchestration combined into one operational graph. If multi-agent still feels like “a lot of agents doing things,” the supervisor design and shared-state boundaries stay vague much longer than they should.

## Questions to Keep in Mind

- What role-separation structure does multi-agent design require beyond connecting several models?
- What should be limited when each agent node reads and writes shared state?
- What operational problem appears when handoff or supervisor boundaries are blurry?

## Big Picture

![Supervisor worker delegation structure](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/05/05-01-minimal-runnable-example.en.png)

*Supervisor worker delegation structure*

This picture shows role-specific agent nodes cooperating through shared state while a supervisor or routing boundary chooses the next worker. Multi-agent design is less about parallelism than about clear responsibility and handoff.

> The quality of a multi-agent graph comes from clear responsibilities and handoff state, not from the number of agents.

## Why this structure matters

It is too weak to say multi-agent systems matter because “specialized roles can improve quality.” The stronger reason is explainable delegation. As requests become more complex, the team needs to answer practical questions: why did this request go to that worker, who owns the final response, and where should execution stop or recover when the system goes wrong?

Suppose one request should go to a research worker and another to a code-writing worker. If that decision stays buried inside one agent prompt, the system may still look like a division of labor. But once somebody asks, “Why did this go to code instead of research?”, “Why is the worker producing final-answer prose outside its role?”, or “Who actually validated the last message?”, the abstraction starts leaking quickly.

I have seen teams underestimate this and end up with multi-agent systems that are harder to debug than their original single-agent versions. The number of agents went up, but the clarity of responsibility went down. When supervisor, worker, and finalizer responsibilities are explicit, the opposite happens: the structure gets bigger while the reasoning path gets easier to follow.

So the goal of this post is not merely to show how to spawn multiple workers. The more important goal is to show why a visible delegation structure turns multi-agent design into something maintainable.

---

## Reading Multi-agent Design as Role Separation

The sentence worth anchoring on is this: **multi-agent is a cluster of role-separated graph nodes.** I keep using that phrasing because it keeps the focus where it belongs. A supervisor decides delegation. Workers execute within their role. A finalizer assembles the result. The important fact is not that multiple models exist, but that **responsibility boundaries are visible in the structure.**

Many first-time readers start from the hope that “more agents must mean better results.” That is only half true. The more operationally useful question is whether handoffs and ownership stay explicit. Without that, adding workers often increases cost and ambiguity faster than it increases quality.

At the simplest level, the model looks like this.

| Component | Role | Why it matters in practice |
| --- | --- | --- |
| **Supervisor** | Reads the request and chooses which worker should handle it | You can centralize delegation criteria and fallback behavior |
| **Worker agent** | Produces a role-specific result | Clear role boundaries improve both quality and debugging |
| **Shared state** | Holds minimal contract fields such as `route`, `worker_result`, and `final_answer` | You can trace who produced what without exposing every field to every agent |
| **Finalizer** | Assembles worker output into the user-facing answer | Output formatting and completion rules stay in one place |
| **Handoff rule** | Defines the supervisor → worker → finalizer flow | Delegation becomes structure instead of accident |

That table matters because these are the questions operators actually ask. Why did the supervisor choose code instead of research? Why is a worker trying to write the final answer? Why is shared state growing without control? Could we remove the finalizer? Those questions make sense only if multi-agent is treated as a responsibility-separation problem, not just a call-count problem.

In practice, I look for three things first in a multi-agent graph: whether the supervisor really behaves like a supervisor, whether workers avoid mutating too much shared state, and whether the finalizer absorbs final-output responsibility. Once those three are clear, you can add workers without losing the shape of the system.

---

## Minimal runnable example

Start with the smallest supervisor-worker example that still resembles a real multi-agent skeleton. The supervisor reads the request and chooses either a `research` worker or a `code` worker. The worker writes only its dedicated result. A finalizer then assembles the response format. The example is deliberately small, but it already contains the structural bones that matter later.

```python
import os
from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph

class SupervisorState(TypedDict):
    request: str
    route: str
    worker_result: str
    final_answer: str

def llm() -> ChatGroq:
    return ChatGroq(model="llama-3.1-8b-instant", temperature=0.0, api_key=os.environ["GROQ_API_KEY"])

def supervisor(state: SupervisorState) -> SupervisorState:
    request_lower = state["request"].lower()
    if any(keyword in request_lower for keyword in ("code", "python", "function", "implement", "write")):
        return {"route": "code"}
    if any(keyword in request_lower for keyword in ("what", "why", "explain", "concept")):
        return {"route": "research"}

    response = llm().invoke(
        [
            SystemMessage(content="Classify the request as research or code. Return only one label: research or code."),
            HumanMessage(content=state["request"]),
        ]
    )
    route = response.content.strip().lower()
    if route not in {"research", "code"}:
        route = "research"
    return {"route": route}

def route_to_worker(state: SupervisorState) -> Literal["research_worker", "code_worker"]:
    return "code_worker" if state["route"] == "code" else "research_worker"

def research_worker(state: SupervisorState) -> SupervisorState:
    response = llm().invoke(
        [
            SystemMessage(content="You are a research worker for the LangGraph framework in the LangChain ecosystem. Explain concepts with crisp bullet points and practical engineering language."),
            HumanMessage(content=state["request"]),
        ]
    )
    return {"worker_result": response.content}

def code_worker(state: SupervisorState) -> SupervisorState:
    response = llm().invoke(
        [
            SystemMessage(content="You are a coding worker for LangGraph tutorials. Produce short Python-focused answers with one small example."),
            HumanMessage(content=state["request"]),
        ]
    )
    return {"worker_result": response.content}

def finalize(state: SupervisorState) -> SupervisorState:
    final_answer = (
        f"Supervisor route: {state['route']}\n"
        f"Worker output:\n{state['worker_result']}"
    )
    return {"final_answer": final_answer}

def build_graph():
    graph = StateGraph(SupervisorState)
    graph.add_node("supervisor", supervisor)
    graph.add_node("research_worker", research_worker)
    graph.add_node("code_worker", code_worker)
    graph.add_node("finalize", finalize)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_to_worker,
        {"research_worker": "research_worker", "code_worker": "code_worker"},
    )
    graph.add_edge("research_worker", "finalize")
    graph.add_edge("code_worker", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()
```

This example is small, but it proves three operationally important things. First, the supervisor owns route selection while workers own actual execution, so delegation logic and work output can be inspected separately. Second, workers update a dedicated field like `worker_result`, which keeps the shared-state contract narrow. Third, the finalizer holds output assembly in one place, so adding workers later does not scatter answer-shaping logic across the graph.

That is why I like examples in this shape. They make multi-agent design read like a handoff graph instead of a pile of model calls. If you start with too many workers and too many loops, the phenomenon looks richer but the structure gets harder to see. Here the supervisor, worker, and finalizer layers are visible enough to make delegation boundaries intuitive first.

There is another useful contrast here. This code shows the difference between “one agent trying to do everything” and “a graph whose delegation can be explained.” Once that difference is clear, shared-state discipline and handoff safety stop looking optional.

---

## What to notice in this code

Do not try to absorb the whole file with equal attention. Three things matter first.

![Route and worker_result state flow](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/05/05-02-what-to-notice-in-this-code.en.png)

*Route and worker_result state flow*

- The supervisor decides the route but does not try to answer the request itself.
- Workers write only to dedicated shared fields such as `worker_result`.
- `finalize` keeps answer assembly in one place, which makes future expansion easier.

The first point is supervisor discipline. A supervisor should decide the path, not try to perform the substantive work too. In practice, I have seen supervisors slowly absorb classification, partial answering, and even fallback response writing, until the structure collapsed back into a disguised single-agent system.

The second point is minimal shared state. Once every worker can read and write every field, the advantages of multi-agent separation disappear quickly. Narrow output fields make it easier to trace responsibility and reduce the blast radius when one worker is replaced or added.

The third point is the finalizer. Without one, output style and completion rules start drifting across workers. With one, the response contract stays centralized while workers stay focused on specialized work.

---

## Where engineers get confused

The most common mistake in multi-agent design is believing that “more agents” automatically means “better results.” In practice, agent count usually matters less than **who controls delegation, who performs work, and who owns the final response.**

![Role boundaries across supervisor and workers](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/05/05-03-where-engineers-get-confused.en.png)

*Role boundaries across supervisor and workers*

- “Multi-agent” does not automatically mean “better.” Weak role boundaries often produce worse results than one well-designed agent.
- If the supervisor also does substantive work, the structure drifts back toward a monolith.
- Oversharing state increases coupling. Most workers need a small, explicit contract instead.

The failure mode I see most often is **The Supervisor-less Multi-agent Anti-pattern**. Multiple workers exist, but nobody clearly owns delegation. At first the system can look flexible, even collaborative. In practice, one worker starts calling another, that second worker reinterprets the task again, and before long role boundaries and accountability blur at the exact point where the team most needs clarity.

Why is that dangerous in production? First, when the system fails, it becomes much harder to identify which agent made the wrong decision. Second, repeated handoffs increase both token cost and latency faster than expected. Third, without a real supervisor, fallback and stop rules stop being centrally managed, so agent loops can run longer than intended or cause the same request to be handled redundantly by multiple workers.

Another trap is oversharing state. Let every worker read and write every field, and the design initially feels flexible. Then the questions arrive: who changed this field, and why is the research worker mutating code-oriented metadata? I have seen teams discover too late that state-interface design mattered more than model choice all along.

Teams I have worked with tend to stabilize multi-agent design once they document three things clearly: the supervisor’s delegation criteria, the dedicated output field for each worker, and the finalizer’s responsibility. Without those three, the system looks collaborative but behaves more like a prompt pile with blurred ownership.

---

## First operating checklist

Once multi-agent structure enters the graph, these stop being architecture preferences and become delegation-stability checks.

- [ ] Can you explain the supervisor and worker responsibilities in one sentence each
- [ ] Are worker outputs stored in meaningful dedicated fields
- [ ] Does the supervisor centrally own fallback and handoff rules
- [ ] Is shared state restricted to a minimal contract
- [ ] Is there a dedicated finalizer node for debugging and extension

The real question here is not “do we have multiple agents?” It is “is the delegation structure explainable and safe?” Multi-agent design is a feature, but it is also an operational boundary.

---

## How senior teams think about this in practice

The moment multi-agent structure appears, the graph starts resembling an organizational chart rather than a simple routing system. That changes the operating questions. Instead of asking only whether the answer was good, you start asking who owned the task, why the handoff happened there, and which node carried final responsibility.

In practice, I evaluate multi-agent design together with observability. The supervisor’s route choice, the worker’s field updates, and the finalizer’s output rules all need to survive in logs or state. As agent count grows, stronger trace boundaries matter more than additional model variety.

Another useful distinction is not confusing tool-calling with multi-agent design. A tool-calling agent usually means one agent invoking external capabilities. Multi-agent design means different role owners handing work to each other. They can coexist, but they are not the same thing. Once that difference blurs, supervisors start calling tools, behaving like workers, and absorbing finalization too.

I have seen strong teams review handoff contracts before they review raw model quality. The reason is practical. Worker performance can wobble a little while the system still holds together if the supervisor and finalizer preserve boundaries. A strong model on top of a weak delegation contract still produces a brittle graph.

---

## Summary: multi-agent is not about model count, but about graph design that makes delegation explainable

At first glance, multi-agent design can look like “put several specialists in the same workflow.” That is not wrong, but it is too weak for operating real systems. The stronger definition is that multi-agent graphs let a supervisor decide delegation, workers produce role-specific output, and a finalizer assemble the final answer inside a responsibility-separated structure.

The core lessons from this post are simple. First, supervisors should focus on judgment and handoff. Second, workers should operate within a minimal shared-state contract. Third, finalizers and fallback rules are not decorative extras. They are stability controls that keep delegation understandable.

That matters immediately for the final chapter. The complete LangGraph example will combine state, checkpoints, branching, tool usage, and multi-agent orchestration into one graph. If multi-agent already reads as delegation structure here, the final system will feel like one operating model rather than a pile of features.

When I look at a multi-agent graph, I care less about how many agents exist and more about whether ownership can be explained. Why did the supervisor choose that worker? Which field did the worker actually own? Where did final responsibility land? If the graph answers those clearly, the structure is in good shape.

In the next post, we will assemble the series into one complete LangGraph example. That is where multi-agent structure stops looking like a separate trick and starts looking like the final piece that stabilizes the whole graph.

---

## Operating checklist

- [ ] Are the supervisor’s delegation rules and each worker’s responsibility captured in an ADR or equivalent document
- [ ] Are dedicated worker output fields and the minimal shared-state contract defined clearly
- [ ] Is there a fallback or human-review path for failed handoffs
- [ ] Does the finalizer absorb response-format and completion responsibility
- [ ] Can trace boundaries stay readable even as more workers are added

## Answering the Opening Questions

- **What role-separation structure does multi-agent design require beyond connecting several models?**
  - Multi-agent design splits responsibilities such as planner, researcher, and writer, then records the handoff contract in shared state.
- **What should be limited when each agent node reads and writes shared state?**
  - Each node should update only the fields and result shapes it owns. Otherwise agents overwrite the evidence needed by other stages.
- **What operational problem appears when handoff or supervisor boundaries are blurry?**
  - Blurry boundaries let supervisors do worker jobs or agents overwrite each other, making failure points and cost drivers hard to trace.

<!-- toc:begin -->
## In this series

- [LangGraph 101 (1/6): LangGraph introduction and graph basics](./01-graph-basics.md)
- [LangGraph 101 (2/6): State management and checkpoints](./02-state-and-checkpoints.md)
- [LangGraph 101 (3/6): Conditional edges and branching](./03-conditional-edges.md)
- [LangGraph 101 (4/6): Tool-calling agents](./04-tool-calling-agent.md)
- **LangGraph 101 (5/6): Multi-agent systems (current)**
- LangGraph 101 (6/6): Completing LangGraph (upcoming)

<!-- toc:end -->

---

## References

### Official Documentation
- [LangGraph multi-agent concepts](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
- [LangGraph supervisor tutorial](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/)
- [LangGraph multi-agent network guide](https://langchain-ai.github.io/langgraph/how-tos/multi-agent-network/)

### Related Series
- [Conditional edges and branching](./03-conditional-edges.md)
- [LangGraph introduction and graph basics](./01-graph-basics.md)

---

Tags: LangGraph, Agent, Python, LLM
