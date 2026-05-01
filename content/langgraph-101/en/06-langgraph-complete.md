---
title: 'Completing LangGraph'
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
last_reviewed: '2026-05-01'
---

# Completing LangGraph

## Questions this post answers

- How do you combine checkpoints, routing, and tool calling in one graph?
- How do you separate direct answers from tool-heavy requests without losing conversation state?
- What should you verify before calling a combined example production-ready?

> A complete LangGraph agent is not one giant prompt. It is a state machine where supervisor logic, tool execution, and checkpointing cooperate through explicit transitions.

Example code: [github.com/yeongseon-books/langgraph-101](https://github.com/yeongseon-books/langgraph-101/tree/main/en/06-langgraph-complete)

This final example pulls the series together. It classifies the incoming question, answers simple conceptual prompts directly, routes calculation-heavy prompts into a tool loop, and stores the whole conversation with `MemorySaver`. That is already enough structure for a serious prototype.

![Questions this post answers](../../../assets/langgraph-101/06/06-01-questions-this-post-answers.en.png)
## Minimal runnable example

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

```
Output
First turn:
In the context of LangGraph, a component of the LangChain ecosystem, "explicit state" refers to the idea of making the state of a conversation or application explicit and manageable.

In traditional conversational AI systems, the state of the conversation is often implicit, meaning it's buried within the conversation history or the internal workings of the model. This can make it difficult to manage, debug, and scale the system.

In contrast, LangGraph uses an explicit state management approach, where the state of the conversation is represented as a graph data structure. This graph contains nodes and edges that represent the different entities, concepts, and relationships within the conversation.

By making the state explicit, LangGraph enables developers to:

1. **Visualize** the conversation state: The graph provides a clear and visual representation of the conversation state, making it easier to understand and debug.
2. **Manage** the conversation state: Developers can explicitly update, modify, and manipulate the graph to manage the conversation state.
3. **Scale** the system: Explicit state management allows LangGraph to handle complex conversations and scale to larger applications.

In summary, explicit state in LangGraph means representing the conversation state as a manageable, visual, and scalable graph data structure, making it easier to develop, debug, and maintain conversational AI applications.

Second turn:
The result of the calculation sqrt(81) + 5 is 14.0.

Checkpoint message count: 6
```

Runnable file: `/root/Github/langgraph-101/en/06-langgraph-complete/main.py`

Run it with:

```bash
export GROQ_API_KEY=... && python main.py
```

## What to notice in this code

- The supervisor keeps graph complexity under control by splitting direct answers from tool-driven requests.
- The `tool_agent -> ToolNode -> tool_agent` loop is isolated to the cases that need tools.
- `compile(checkpointer=MemorySaver())` makes the entire conversation resumable across turns.

## Where engineers get confused

- Sending every request through the tool loop usually makes the agent slower and more expensive than necessary.
- Even with checkpointing, routing should stay simple enough to reason about from the latest message.
- Tool execution is not evaluation. You still need explicit regression cases, and the calculator tool should stay on a strict arithmetic parser rather than raw `eval()`.

## Checklist

- [ ] Are direct-answer and tool paths separated clearly
- [ ] Does the same `thread_id` resume the conversation as expected
- [ ] Do tool questions and non-tool questions route to the intended path
- [ ] Is loop termination explicit before the final answer

## Summary

The real goal of this series was never memorizing LangGraph APIs. It was learning how to design state, edges, checkpoints, and tool loops as one coherent system. Once that mental model is in place, building a usable agent skeleton becomes much more straightforward.

<!-- toc:begin -->
## In this series

- [LangGraph introduction and graph basics](./01-graph-basics.md)
- [State management and checkpoints](./02-state-and-checkpoints.md)
- [Conditional edges and branching](./03-conditional-edges.md)
- [Tool-calling agents](./04-tool-calling-agent.md)
- [Multi-agent systems](./05-multi-agent.md)
- **Completing LangGraph (current)**

<!-- toc:end -->

---

## References

- [LangGraph tutorials](https://langchain-ai.github.io/langgraph/tutorials/)
- [LangGraph persistence guide](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
- [LangGraph prebuilt components](https://langchain-ai.github.io/langgraph/reference/prebuilt/)

Tags: LangGraph, Agent, Python, LLM
