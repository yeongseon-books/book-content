---
title: 'Completing LangGraph'
series: langgraph-101
episode: 6
language: en
status: draft
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

> LangGraph 101 (6/6)

Example code: [github.com/yeongseon-books/langgraph-101](https://github.com/yeongseon-books/langgraph-101/tree/main/en/06-langgraph-complete)

This post assembles graph basics, checkpoints, conditional edges, tool calling, and multi-agent coordination from across the series into one complete production agent: conversation memory, tool use, quality validation, and multi-turn dialogue.

---

## Complete production agent

```python
import json
import math
import os
import sqlite3
from typing import TypedDict, Annotated, Literal

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression. E.g.: '2 + 3 * 4', 'sqrt(16)', 'pi * 5**2'"""
    try:
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        return str(eval(expression, {"__builtins__": {}}, allowed))
    except Exception as e:
        return f"error: {e}"

@tool
def word_stats(text: str) -> str:
    """Return word count and character count for text."""
    return json.dumps({"words": len(text.split()), "chars": len(text)})

TOOLS = [calculator, word_stats]
TOOL_MAP = {t.name: t for t in TOOLS}

SYSTEM_PROMPT = """You are a helpful Python tutor agent.
Use tools to perform accurate calculations and analysis.
Remember the conversation history and respond in context.
Be honest when you don't know something."""

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    iterations: int

MAX_ITERATIONS = 10

def agent_node(state: AgentState) -> AgentState:
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.0,
    ).bind_tools(TOOLS)
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response], "iterations": state["iterations"] + 1}

def tool_node(state: AgentState) -> AgentState:
    last = state["messages"][-1]
    results = []
    for call in last.tool_calls:
        t = TOOL_MAP.get(call["name"])
        result = t.invoke(call["args"]) if t else f"unknown tool: {call['name']}"
        results.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
    return {"messages": results}

def route_agent(state: AgentState) -> Literal["tools", "end"]:
    if state["iterations"] >= MAX_ITERATIONS:
        return "end"
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "end"

def build_production_agent(persist: bool = False):
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", route_agent, {"tools": "tools", "end": END})
    graph.add_edge("tools", "agent")

    if persist:
        conn = sqlite3.connect("agent.db", check_same_thread=False)
        from langgraph.checkpoint.sqlite import SqliteSaver
        checkpointer = SqliteSaver(conn)
    else:
        checkpointer = MemorySaver()

    return graph.compile(checkpointer=checkpointer)
```

---

## Batch evaluation

Production agents need quality validation before deployment.

```python
def evaluate_agent(app, test_cases: list[dict]) -> dict:
    results = []
    for tc in test_cases:
        config = {"configurable": {"thread_id": f"eval_{tc['id']}"}}
        result = app.invoke(
            {"messages": [HumanMessage(content=tc["question"])], "iterations": 0},
            config=config,
        )
        answer = result["messages"][-1].content
        kw_hits = [kw for kw in tc["expected_keywords"] if kw.lower() in answer.lower()]
        results.append({
            "id": tc["id"],
            "passed": len(kw_hits) == len(tc["expected_keywords"]),
            "keyword_coverage": len(kw_hits) / len(tc["expected_keywords"]) if tc["expected_keywords"] else 1.0,
        })

    pass_rate = sum(1 for r in results if r["passed"]) / len(results) if results else 0.0
    return {"total": len(results), "pass_rate": round(pass_rate, 2), "details": results}

if __name__ == "__main__":
    app = build_production_agent()
    test_cases = [
        {"id": 1, "question": "What is sqrt(256)?", "expected_keywords": ["16"]},
        {"id": 2, "question": "What is a Python list comprehension?",
         "expected_keywords": ["list", "expression"]},
    ]
    print(json.dumps(evaluate_agent(app, test_cases), indent=2))
```

---

## Multi-turn conversation

```python
def run_conversation(thread_id: str = "demo"):
    app = build_production_agent()
    config = {"configurable": {"thread_id": thread_id}}
    print("Python tutor agent (type 'quit' to exit)")
    print("-" * 40)
    while True:
        user_input = input("\nuser: ").strip()
        if user_input.lower() in ("quit", "q", "exit"):
            break
        if not user_input:
            continue
        result = app.invoke(
            {"messages": [HumanMessage(content=user_input)], "iterations": 0},
            config=config,
        )
        print(f"\nagent: {result['messages'][-1].content}")
```

---

## Series summary

The agent built across this series has six layers.

1. **Graph basics**: StateGraph, nodes, and edges define the workflow explicitly
2. **Checkpointer**: conversation memory and session management
3. **Conditional edges**: dynamic flow control based on state
4. **Tool calling**: the agent loop that lets the LLM use external functions
5. **Multi-agent**: specialized agents coordinating through shared state
6. **Production integration**: all layers combined with quality validation

LangGraph's key insight is that complex workflows should be expressed as explicit graphs. When flow is visible in the graph definition rather than hidden in code, debugging, testing, and extension become straightforward.

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

- [LangGraph documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph tutorials](https://langchain-ai.github.io/langgraph/tutorials/)
- [LangGraph examples repository](https://github.com/langchain-ai/langgraph/tree/main/examples)

Tags: LangGraph, Agent, Python, LLM
