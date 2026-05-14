---
title: Completing LangGraph
series: langgraph-101
episode: 6
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LangGraph
- Agent
- Python
- LLM
last_reviewed: '2026-05-12'
seo_description: A complete LangGraph agent is not one giant prompt. It is a state
  machine where supervisor logic, tool execution, and checkpointing cooperate…
---

# Completing LangGraph

By the time teams reach a “complete” agent example, they often expect one last trick. Maybe a better prompt. Maybe a smarter model. Maybe a more elaborate tool wrapper. In practice, the thing that usually makes the system feel complete is more structural than magical: state survives across turns, routing decisions stay explicit, and tool usage happens only when the request actually deserves it.

The failure cases are painfully repetitive. Without checkpoints, a second turn behaves like the first never happened. Without routing, every request gets shoved through the same expensive loop. Without tool boundaries, the model starts improvising arithmetic, counting, or extraction work that should have been delegated. I have seen prototypes look impressive in a demo and then fall apart the moment a real user asks a follow-up question that mixes memory, judgment, and tool use.

This is the final post in the LangGraph 101 series.

So this chapter is not about adding one more feature. It is about combining the ideas from the earlier posts into one operational skeleton. Checkpoints remember context. A supervisor decides whether the request needs a direct answer or a tool path. The tool loop stays isolated instead of infecting the whole graph. That combination is what starts to feel usable outside a tutorial.

## Questions this post answers

- How do you combine checkpoints, routing, and tool calling inside one LangGraph?
- When should a supervisor send a request to a direct-answer path instead of a tool loop?
- Why does a complete graph need state discipline even when the example looks small?
- What parts of the graph should stay simple if you want debugging to remain possible later?
- Which production mistakes show up when teams wire memory and tools together too casually?
- What should you verify first before calling a combined LangGraph example “ready” for serious prototyping?

## Why this matters

Individually, checkpoints, branching, and tools all look manageable. The operational trouble starts when they meet. Now you are no longer asking whether a node works in isolation. You are asking whether the whole graph still behaves predictably when one turn is conceptual, the next turn requires math, and the third turn depends on the earlier conversation still being present.

That is where many early agent systems get weaker than expected. One request should have been answered directly, but the graph routes it into a tool loop and adds avoidable latency. Another request should have used a tool, but the model improvises the answer from memory and returns something plausible but wrong. A third request should have resumed prior state, but the thread boundary was never treated as a real contract. The individual parts existed. The operating model did not.

## The best way to understand a complete LangGraph

The most useful mental model is this: **a complete LangGraph is a small operating system for request handling, not a large prompt with accessories attached.** State tells the graph what has happened so far. The supervisor decides what kind of work this turn requires. The tool loop performs narrow external work when necessary. Checkpointing makes the whole sequence resumable.

> A complete LangGraph agent is not one giant prompt. It is a state machine where supervisor logic, tool execution, and checkpointing cooperate through explicit transitions.

That framing matters because it stops you from treating completeness as feature count. I have seen teams say a graph is “complete” because it has memory, tools, and branching in the same repository. That is not enough. The question is whether those parts cooperate without blurring responsibility. Who decides the route? Which node is allowed to call tools? What state must survive? Where does the loop stop?

If you keep those questions visible, the combined graph becomes easier to understand than it first appears. It is just a direct-answer lane, a tool lane, and a persisted conversation history held together by explicit transitions.

Example code: [github.com/yeongseon-books/langgraph-101](https://github.com/yeongseon-books/langgraph-101/tree/main/en/06-langgraph-complete)

![Questions this post answers](../../../assets/langgraph-101/06/06-01-questions-this-post-answers.en.png)

*Questions this post answers*

## Minimal runnable example

Start with the smallest graph that still feels like a real agent skeleton. This example does four things that belong together: it persists conversation state with `MemorySaver`, classifies the latest request through a supervisor node, answers conceptual questions directly, and routes calculation or counting work into a tool-enabled loop. That is enough to demonstrate the shape of a serious prototype without hiding the important edges behind framework magic.

If you read the code with one goal in mind, make it this: notice how the graph does not treat all requests the same. That is where completeness starts to become operational rather than decorative.

![Combined graph with supervisor and tool loop](../../../assets/langgraph-101/06/06-01-minimal-runnable-example.en.png)

*Combined graph with supervisor and tool loop*

```python
import ast
import json
import math
import operator
from typing import Any, Callable, Literal, cast

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

ALLOWED_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
ALLOWED_FUNCTIONS: dict[str, Callable[..., Any]] = {
    name: value
    for name, value in math.__dict__.items()
    if not name.startswith("_") and callable(value)
}
ALLOWED_CONSTANTS = {"pi": math.pi, "e": math.e, "tau": math.tau}

def evaluate_math_expression(expression: str) -> float:
    def _evaluate(node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp):
            left = _evaluate(node.left)
            right = _evaluate(node.right)
            operation = ALLOWED_BINARY_OPERATORS.get(type(node.op))
            if operation is None:
                raise ValueError("unsupported operator")
            return float(operation(left, right))
        if isinstance(node, ast.UnaryOp):
            operand = _evaluate(node.operand)
            operation = ALLOWED_UNARY_OPERATORS.get(type(node.op))
            if operation is None:
                raise ValueError("unsupported unary operator")
            return float(operation(operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            function = ALLOWED_FUNCTIONS.get(node.func.id)
            if function is None or node.keywords:
                raise ValueError("unsupported function")
            arguments = [_evaluate(argument) for argument in node.args]
            return float(function(*arguments))
        if isinstance(node, ast.Name):
            value = ALLOWED_CONSTANTS.get(node.id)
            if value is not None:
                return float(value)
            raise ValueError("unsupported constant")
        raise ValueError("unsupported expression")

    parsed = ast.parse(expression, mode="eval")
    return _evaluate(parsed.body)

@tool
def calculator(expression: str) -> str:
    """Evaluate an arithmetic expression with safe math functions like sqrt(16) or pi * 2."""

    try:
        result = evaluate_math_expression(expression)
    except Exception as exc:
        return f"calculation error: {exc}"
    return str(result)

@tool
def word_stats(text: str) -> str:
    """Return word and character counts for a piece of text."""

    return json.dumps({"words": len(text.split()), "characters": len(text)})

TOOLS = [calculator, word_stats]

class CompleteState(MessagesState):
    route: str

def base_llm() -> ChatGroq:
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0, stop_sequences=None)

def supervisor(state: CompleteState) -> dict[str, str]:
    latest_question = str(state["messages"][-1].content).lower()
    if any(keyword in latest_question for keyword in ("count", "calculate", "math", "sqrt")):
        route = "tool_agent"
    else:
        route = "direct_answer"
    return {"route": route}

def route_after_supervisor(state: CompleteState) -> Literal["direct_answer", "tool_agent"]:
    return cast(Literal["direct_answer", "tool_agent"], state["route"])

def direct_answer(state: CompleteState) -> dict[str, object]:
    system = SystemMessage(
        content=(
            "You are explaining LangGraph from the LangChain ecosystem. "
            "Answer clearly using the full conversation history when it matters."
        )
    )
    response = base_llm().invoke([system, *state["messages"]])
    return {"messages": [response]}

def tool_agent(state: CompleteState) -> dict[str, object]:
    system = SystemMessage(
        content=(
            "You are a precise assistant. Use tools for calculations or counting tasks, "
            "then answer in one concise paragraph."
        )
    )
    response = base_llm().bind_tools(TOOLS).invoke([system, *state["messages"]])
    return {"messages": [response]}

def build_graph():
    graph = StateGraph(CompleteState)
    graph.add_node("supervisor", supervisor)
    graph.add_node("direct_answer", direct_answer)
    graph.add_node("tool_agent", tool_agent)
    graph.add_node("tools", ToolNode(TOOLS))

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {"direct_answer": "direct_answer", "tool_agent": "tool_agent"},
    )
    graph.add_edge("direct_answer", END)
    graph.add_conditional_edges("tool_agent", tools_condition, {"tools": "tools", "__end__": END})
    graph.add_edge("tools", "tool_agent")

    return graph.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    app = build_graph()
    config: RunnableConfig = {"configurable": {"thread_id": "complete-demo"}}

    first = app.invoke(
        {"messages": [HumanMessage(content="Explain what explicit state means in LangGraph.")], "route": ""},
        config=config,
    )
    print("First turn:")
    print(first["messages"][-1].content)

    second = app.invoke(
        {"messages": [HumanMessage(content="Now calculate sqrt(81) + 5 and use a tool.")]},
        config=config,
    )
    print("\nSecond turn:")
    print(second["messages"][-1].content)

    snapshot = app.get_state(config)
    print(f"\nCheckpoint message count: {len(snapshot.values['messages'])}")
```

Runnable file: `en/06-langgraph-complete/main.py`

```bash
export GROQ_API_KEY=... && python main.py
```

There are two layers worth noticing immediately after the code runs. The first layer is behavioral: a conceptual question lands on the direct-answer path, while a math-heavy follow-up reuses the same thread and moves into the tool path. The second layer is architectural: the tool loop is not global. It is activated only after the supervisor decides that the request belongs there.

That separation is what makes the example feel more mature than a basic demo. The graph preserves conversation history, but it does not confuse “having memory” with “always doing the same thing.” It can remember the conversation while still making a fresh structural choice each turn.

## What to notice in this code

Do not give every line equal weight. Three design decisions matter more than the rest.

![Checkpoint and route state structure](../../../assets/langgraph-101/06/06-02-what-to-notice-in-this-code.en.png)

*Checkpoint and route state structure*

- The supervisor decides whether the turn belongs to a direct-answer path or a tool-enabled path.
- The `tool_agent -> ToolNode -> tool_agent` loop stays isolated instead of becoming the default for every request.
- `compile(checkpointer=MemorySaver())` makes the graph resumable across turns with the same `thread_id`.

The first point is route ownership. The supervisor is not trying to answer the user and classify the task at the same time. It reads the latest request, makes a narrow routing decision, and hands off the rest. That discipline sounds simple, but I have seen many graphs lose clarity because the router slowly grew into a half-answering, half-delegating mess.

The second point is loop containment. Tool loops are useful, but they are easy to overgeneralize. Once every request goes through a tool-capable node, latency rises, tool-call reasoning becomes harder to inspect, and the graph starts paying a tax even on simple conceptual questions. This example avoids that by treating tools as a specialized lane.

The third point is persistence. Checkpointing is not just a convenience feature. It is the reason the second turn can build on the first without manually reconstructing history. In practice, thread identity becomes part of the system contract. If your team cannot explain how `thread_id` maps to a user, session, or workflow, memory behavior usually becomes confusing before the graph itself does.

## Where engineers get confused

The first confusion is calling any graph with memory and tools “production-like.” I understand the temptation. The example already feels richer than a single-node demo. But completeness is not the same as readiness. If routing rules are brittle, if tool selection is too naive, or if state observability is weak, the graph may still fail in exactly the places a real workload will expose first.

![Validation path with human review interrupt](../../../assets/langgraph-101/06/06-03-where-engineers-get-confused.en.png)

*Validation path with human review interrupt*

- Sending every request through the tool loop usually makes the agent slower and more expensive than necessary.
- Even with checkpointing, routing should stay simple enough to reason about from the latest message.
- Tool execution is not evaluation. You still need explicit regression cases, and the calculator tool should stay on a strict arithmetic parser rather than raw `eval()`.

The second confusion is assuming that checkpointing solves reasoning quality by itself. It does not. Checkpointing preserves history. It does not decide which part of history matters, whether the route was correct, or whether the tool output should be trusted. I have seen teams celebrate that “memory works” while users were still getting routed into the wrong branch half the time.

The third confusion is mixing safe tool execution with general autonomy. This example is careful for a reason. The calculator tool parses a restricted arithmetic expression instead of letting the model execute arbitrary Python. That kind of boundary tends to look fussy in tutorials and extremely wise after the first security review.

## First operations checklist

- [ ] Can you explain in one sentence why a request should go to `direct_answer` versus `tool_agent`
- [ ] Does the same `thread_id` reliably resume the intended conversation history
- [ ] Do conceptual prompts avoid unnecessary tool loops
- [ ] Do tool-heavy prompts actually trigger the tool path and terminate cleanly
- [ ] Are tool boundaries narrow enough that you could defend them in a code review

If one of those answers is vague, the graph is not ready to grow yet. The fastest way to make a complete example fragile is to stack more capability on top of unclear routing and unclear state behavior.

## How experienced practitioners think about this

Experienced teams usually stop talking about “the agent” as if it were one indivisible thing. They talk about routing quality, checkpoint semantics, tool safety, and observability as separate operating concerns. That shift sounds subtle, but it changes design decisions quickly. You stop asking only whether the answer looked smart and start asking whether the graph behaved predictably.

In practice, I evaluate a graph like this as a contract between lanes. The direct-answer lane should stay cheap and clear. The tool lane should be explicit, inspectable, and tightly bounded. The checkpoint layer should survive across turns without smearing unrelated sessions together. If those contracts hold, the graph can absorb more complexity later without losing its shape.

This is also where the whole series comes together. Graph basics gave us explicit structure. Checkpoints gave us persistence. Conditional edges gave us branching. Tool-calling gave us controlled external work. Multi-agent design gave us responsibility separation. A complete LangGraph is what happens when those concepts stop being separate lessons and start behaving like one system.

## Summary

The real lesson of this final chapter is that completeness comes from cooperation, not accumulation. A LangGraph feels complete when memory, routing, and tool usage reinforce each other instead of competing for control. The graph here is still small, but it already demonstrates the operating shape that matters: persist state, decide the lane, use tools only when needed, and stop the loop explicitly.

That is also the right way to close the series. LangGraph never needed to be mysterious. Across these six posts, the pattern stayed consistent: make state explicit, make transitions visible, and make responsibility boundaries narrow enough to reason about under pressure. Once those habits are in place, the framework starts feeling much less like agent magic and much more like engineering.

If you carry one idea forward, make it this: the best LangGraph systems are readable as graphs before they are impressive as demos. That is what makes them easier to extend, safer to review, and far more likely to survive contact with real users.

![Production agent flow across turns](../../../assets/langgraph-101/06/06-04-summary.en.png)

*Production agent flow across turns*

## Operations checklist

- [ ] Are routing rules documented well enough that another engineer can predict the branch choice
- [ ] Is checkpoint identity tied to a clear session or user contract
- [ ] Are tool nodes limited to narrowly scoped, reviewable capabilities
- [ ] Can you inspect why a given turn ended directly or entered the tool loop
- [ ] Do regression tests cover both remembered context and tool-routed follow-up turns

<!-- toc:begin -->
## In this series

- [LangGraph introduction and graph basics](./01-graph-basics.md)
- [State management and checkpoints](./02-state-and-checkpoints.md)
- [Conditional edges and branching](./03-conditional-edges.md)
- [Tool-calling agents](./04-tool-calling-agent.md)
- [Multi-agent systems](./05-multi-agent.md)
- **Completing LangGraph (current)**

<!-- toc:end -->

## References

- [LangGraph tutorials](https://langchain-ai.github.io/langgraph/tutorials/)
- [LangGraph persistence guide](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
- [LangGraph prebuilt components](https://langchain-ai.github.io/langgraph/reference/prebuilt/)

### Related posts
- [State management and checkpoints](./02-state-and-checkpoints.md)
- [Tool-calling agents](./04-tool-calling-agent.md)

Tags: LangGraph, Agent, Python, LLM
