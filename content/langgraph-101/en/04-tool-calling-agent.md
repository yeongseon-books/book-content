---
title: "LangGraph 101 (4/6): Tool-calling agents"
series: langgraph-101
episode: 4
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
seo_description: ToolNode and tools_condition make the tool loop explicit, so an LLM
  can request tools inside a controllable graph execution envelope.
---

# LangGraph 101 (4/6): Tool-calling agents

Tool-using agents always look smart in demos. If a question needs arithmetic, the model calls a calculator. If it needs counting, the model reaches for a text tool. The answer comes back with the glow of external grounding, and everyone feels better about the system. In production, though, the questions change quickly. Why did this request call the tool three times? Why did the model ask for a tool that does not even exist? Why did it read a failed tool result and then ask for the same tool again?

The real issue is usually not that the model can use tools. The issue is whether the loop around tool usage is explicit, inspectable, and controllable. Once tool invocation is left as an opaque inner habit of the model, failed tool retries, successful tool follow-up, and final answer synthesis blur together. Reproduction gets harder. Logging boundaries get weaker. The place where cost starts exploding gets harder to isolate.

This is the fourth article in the LangGraph 101 series. Here I want to frame a tool-calling agent not as “a model that knows how to use tools,” but as **a safe execution envelope that separates LLM judgment from actual tool execution**. That distinction matters. **A tool-calling agent is a control loop built from an LLM node, a ToolNode, and explicit termination rules.**

![Tool loop between agent and tools](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/04/04-01-minimal-runnable-example.en.png)
*Tool loop between agent and tools*
> The core of a tool-calling agent is not that the model knows tools; it is that tool execution repeats inside a boundary you can validate.

## Questions to Keep in Mind

- Why should a LangGraph tool-calling agent be read as an LLM plus a separate tool execution envelope?
- When tool calls repeat, what execution trace should remain in state?
- What risk appears when tool calls run without a safe dispatcher?

## Why this structure matters

It is too weak to say tool-calling agents matter because “an LLM can now do calculations or search.” The stronger reason is grounded execution with controllable loops. The moment a model starts outsourcing work to external capabilities, the team needs to answer practical questions: why was this tool called, did the tool succeed, and when should the loop stop?

Suppose some questions require arithmetic while others only need direct explanation. The model might request a tool, or it might answer immediately. You can absolutely bury that entire flow inside one function. It will run. But the moment somebody asks, “Why did this request call the calculator twice?”, “Why did the answer return to the model after the tool failed?”, or “Why did this question exit without any tool at all?”, the abstraction starts leaking fast.

So the goal of this post is not to help you memorize the `ToolNode` API. The more important goal is to show why an explicit tool loop improves both safety and debuggability.

---

## Reading a Tool-calling Agent as an Execution Boundary

The sentence worth anchoring on is this: **a tool-calling agent is an LLM inside a safe execution envelope.** I keep using that phrasing because it is operationally useful. The model decides whether a tool is needed. `ToolNode` performs the execution and creates the result message. A conditional edge decides whether the loop continues or stops.

Many first-time readers treat tool calling as “the option that lets an LLM reach outside itself.” That is only half the story. The more important half is that tool requests and tool execution become **separate layers**. Once those layers are separated, you can attach permission checks, logging, fallback behavior, and retry policy outside the prompt instead of trying to smuggle all of it into model instructions.

At the simplest level, the model looks like this.

| Component | Role | Why it matters in practice |
| --- | --- | --- |
| **LLM node** | Decides whether a tool is needed and emits tool calls | You centralize judgment and answer generation in one place |
| **ToolNode** | Executes the actual tool and emits `ToolMessage` output | You separate model judgment from side-effectful execution |
| **tools_condition** | Sends execution to `tools` if a tool call exists, otherwise ends the graph | You make loop and termination rules visible in structure |
| **Tool schema / docstring** | Tells the model how a tool should be used | You reduce tool-selection errors and bad argument assumptions |
| **Loop guard** | Covers recursion limit, timeout, fallback, and similar safety controls | You prevent runaway loops and runaway cost |

That table matters because these are the questions operators actually ask. Why did the model request this tool? Did the tool really succeed? Why did the system call it again after failure? When should execution stop instead of looping? Those questions become answerable only when tool calling is treated as an execution envelope rather than as an LLM party trick.

---

## Minimal runnable example

Start with the smallest tool loop that still resembles a real tool-using agent. The model reads a question, requests a tool when necessary, `ToolNode` performs the execution, and the model reads the result before producing the final answer. The example is intentionally small, but it already contains the whole control loop.

```python
import ast
import json
import math
import operator
from collections.abc import Callable
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
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

def call_model(state: MessagesState):
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0, stop_sequences=None).bind_tools(TOOLS)
    system = SystemMessage(
        content="You are a precise assistant. Use tools for calculations or counting tasks."
    )
    response = llm.invoke([system, *state["messages"]])
    return {"messages": [response]}

def build_graph():
    graph = StateGraph(MessagesState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition, {"tools": "tools", "__end__": END})
    graph.add_edge("tools", "agent")
    return graph.compile()
```

This example is small, but it already proves three operationally important things. First, the model decides whether a tool is needed while `ToolNode` owns real execution, so model-judgment failures and tool-execution failures can be inspected at different layers. Second, `tools_condition` makes loop continuation and loop termination visible in structure, so “why did this stop here?” and “why did it return to tools again?” become code-level questions instead of mysteries. Third, a deliberately safe tool implementation such as `calculator` keeps side effects and permission scope outside the prompt.

---

## What to notice in this code

Do not try to assign equal weight to every line on a first pass. Three details matter first.

![Tool call and ToolMessage flow](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/04/04-02-what-to-notice-in-this-code.en.png)

*Tool call and ToolMessage flow*

- Tool docstrings are effectively the usage manual the model sees.
- `ToolNode(TOOLS)` owns execution and the resulting `ToolMessage` objects.
- `tools_condition` routes to `tools` only when the last AI message includes tool calls; otherwise it ends the graph.

The first point is the tool contract. The model does not understand your Python implementation directly. It learns from the tool schema and description. When the input and output contract is vague, bad tool selection and bad argument formation become much more common. In practice, I have seen teams keep tuning prompts when the real problem was weak tool descriptions.

The second point is role separation inside `ToolNode`. A model requesting a tool is not the same thing as a model executing a tool. Because `ToolNode` owns real execution and `ToolMessage` creation, permission checks, logging, and failure handling can attach to that layer cleanly. That separation is what keeps side-effect tools manageable at all.

The third point is termination. `tools_condition` looks small, but it matters a lot. No tool call means the graph can end. A tool call means execution moves into the tool node. That rule has to stay explicit so questions that do not need tools do not loop unnecessarily, while questions that do need tools stay in the cycle only as long as required.

---

## Where engineers get confused

The most common mistake in tool-calling agents is assuming that “more tools” automatically means “more accuracy.” In practice, loop control and side-effect safety matter at least as much as raw answer quality.

![Branching from the last AI message](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/04/04-03-where-engineers-get-confused.en.png)

*Branching from the last AI message*

- If you inline tool execution inside the model loop, retries, logging, and testing become harder than they need to be.
- `bind_tools()` teaches the model how to request tools, but it does not execute them.
- Deterministic tools are easier to debug. Keep the calculator on a strict arithmetic parser instead of raw `eval()`.

The failure mode I see most often is **The Unbounded Tool Loop Anti-pattern**. The model requests a tool once, and then—without sufficiently strong failure and stop controls—keeps asking the same question and calling the same tool again. At first that can feel like self-correction. In practice, it often turns into repeated tool invocation, rising token cost, rising external-call cost, and final answers that arrive late or never arrive at all.

Why is that dangerous in production? First, if the tool has side effects, duplicate execution can become duplicate state mutation. Second, it gets much harder to tell whether the failure came from the model’s judgment or from the tool itself. Third, if the loop guard is weak, timeouts and recursion limits get handled as emergency cleanup instead of design, which makes the whole system feel brittle.

Teams I have worked with tend to stabilize tool-calling agents once they document three things clearly: which tools are read-only, which tools have side effects, and where the loop must stop. Without those three, a tool-calling agent stops behaving like a grounded assistant and starts behaving like an under-controlled execution engine.

---

## First operating checklist

Once a tool loop enters the graph, these stop being implementation details and become execution-stability checks.

- [ ] Do tool descriptions clearly define the input and output contract
- [ ] Is the `agent -> tools -> agent` loop explicit in the graph
- [ ] Are side-effect tools separated from read-only tools conceptually and operationally
- [ ] Do non-tool answers exit directly to `END`
- [ ] Are timeout, recursion limit, fallback, and similar loop guards designed outside the prompt

The real question here is not “can the model use a tool?” It is “can the system use a tool safely and stop cleanly?” Tool calling is a feature, but it is also an execution boundary.

---

## How senior teams think about this in practice

The moment a tool-calling loop appears, the graph stops being just an answer generator and starts looking more like an execution system. That changes the operating questions. Instead of asking only whether the answer was good, you start asking why this tool was selected, who decides when to stop after failure, and whether it is safe to retry the tool at all.

Another useful distinction is not collapsing tool loops and multi-agent handoffs into one mental bucket. A tool loop is usually one agent invoking an external capability. A multi-agent graph is usually multiple role owners handing work to each other. They can coexist, but they are not the same shape. Once that distinction gets blurry, supervisors start calling tools, behaving like workers, and taking on termination logic too.

I have seen strong teams review the tool-execution contract before they review raw model quality. The reason is practical. A model can wobble a little while the system still holds together if the tool contract and loop guards are solid. A strong model on top of weak execution boundaries still produces a fragile system.

---

## Summary: a tool-calling agent is not a model feature, but a graph control loop that keeps execution safe

At first glance, a tool-calling agent can look like “a model that learned to use external capabilities.” That is not wrong, but it is too weak for production thinking. The stronger definition is this: the model decides whether a tool is needed, `ToolNode` performs the actual execution, and explicit termination rules keep the loop safe.

The core lessons from this post are simple. First, tool request and tool execution should stay separated. Second, side-effect tools demand stricter schemas and loop guards than read-only helpers. Third, termination rules and fallback behavior are not decorative flourishes. They are production safety mechanisms.

That matters immediately for the next post on multi-agent systems. A supervisor handing work to a worker and an agent handing work to a tool are different patterns, but both depend on the same deeper principle: separate judgment from execution. Once tool calling reads as a safe execution envelope here, multi-agent delegation becomes easier to reason about later.

In the next post, we will extend the series from branching into supervisor-worker cooperation. That is where the tool loop stops looking like a small feature extension and starts looking like the structural precondition for stable multi-agent design.

---

## Operating checklist

- [ ] Are tool permission levels and side-effect characteristics documented per tool
- [ ] Is there a fallback or human-review path for failed tool calls
- [ ] Are recursion limit, timeout, and retry rules controlled outside the loop itself
- [ ] Can `ToolNode` execution logs and model tool-call requests be traced separately
- [ ] Is there a validation process that keeps schema quality and stop rules consistent as more tools are added

## Answering the Opening Questions

- **Why should a LangGraph tool-calling agent be read as an LLM plus a separate tool execution envelope?**
  - The LLM proposes intent; the envelope controls names, arguments, allowed scope, and how results return to state. Keeping them separate makes responsibility and failure points visible.
- **When tool calls repeat, what execution trace should remain in state?**
  - State should retain model messages, tool calls, tool results, and the accumulated messages used for the next decision so the loop can be replayed.
- **What risk appears when tool calls run without a safe dispatcher?**
  - Without a dispatcher, unapproved tools or invalid arguments can run directly, increasing security, cost, and data-integrity risk.

<!-- toc:begin -->
## In this series

- [LangGraph 101 (1/6): LangGraph introduction and graph basics](./01-graph-basics.md)
- [LangGraph 101 (2/6): State management and checkpoints](./02-state-and-checkpoints.md)
- [LangGraph 101 (3/6): Conditional edges and branching](./03-conditional-edges.md)
- **LangGraph 101 (4/6): Tool-calling agents (current)**
- LangGraph 101 (5/6): Multi-agent systems (upcoming)
- LangGraph 101 (6/6): Completing LangGraph (upcoming)

<!-- toc:end -->

---

## References

### Official Documentation
- [LangGraph tool-calling how-to](https://langchain-ai.github.io/langgraph/how-tos/tool-calling/)
- [ToolNode API reference](https://langchain-ai.github.io/langgraph/reference/prebuilt/#toolnode)
- [LangChain tool concepts](https://python.langchain.com/docs/concepts/tools/)

### Related Series
- [Conditional edges and branching](./03-conditional-edges.md)
- [Multi-agent systems](./05-multi-agent.md)

---

Tags: LangGraph, Agent, Python, LLM
