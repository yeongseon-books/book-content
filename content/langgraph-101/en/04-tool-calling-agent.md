---
title: 'Tool-calling agents'
series: langgraph-101
episode: 4
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

# Tool-calling agents

> LangGraph 101 (4/6)

The defining capability of an agent is choosing tools, observing results, and deciding what to do next. This post builds a tool-calling agent with LangGraph: tool definitions, a tool execution node, and the agent loop that ties them together.

---

## Tool definitions

LangChain's `@tool` decorator turns functions into tools. The docstring becomes the tool description passed to the LLM.

```python
import json
import math
import os
from typing import TypedDict, Annotated

from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression.
    
    Args:
        expression: math expression to evaluate (e.g., '2 + 3 * 4', 'sqrt(16)')
    
    Returns:
        result as a string
    """
    try:
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        result = eval(expression, {"__builtins__": {}}, allowed)
        return str(result)
    except Exception as e:
        return f"calculation error: {e}"

@tool
def word_counter(text: str) -> str:
    """Count words, characters, and sentences in text.
    
    Args:
        text: text to analyze
    
    Returns:
        JSON with word, char, and sentence counts
    """
    return json.dumps({
        "words": len(text.split()),
        "chars": len(text),
        "sentences": text.count(".") + text.count("!") + text.count("?"),
    })

@tool
def unit_converter(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between units. Supported: km/mile, kg/lb, celsius/fahrenheit.
    
    Args:
        value: numeric value to convert
        from_unit: source unit
        to_unit: target unit
    
    Returns:
        converted value with units
    """
    conversions = {
        ("km", "mile"): lambda x: x * 0.621371,
        ("mile", "km"): lambda x: x * 1.60934,
        ("kg", "lb"): lambda x: x * 2.20462,
        ("lb", "kg"): lambda x: x / 2.20462,
        ("celsius", "fahrenheit"): lambda x: x * 9/5 + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
    }
    key = (from_unit.lower(), to_unit.lower())
    fn = conversions.get(key)
    if not fn:
        return f"unsupported conversion: {from_unit} -> {to_unit}"
    return f"{value} {from_unit} = {fn(value):.4f} {to_unit}"
```

---

## Tool-calling agent graph

```python
TOOLS = [calculator, word_counter, unit_converter]
TOOL_MAP = {t.name: t for t in TOOLS}

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def agent_node(state: AgentState) -> AgentState:
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.0,
    ).bind_tools(TOOLS)
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def tool_node(state: AgentState) -> AgentState:
    last_message = state["messages"][-1]
    results = []
    for call in last_message.tool_calls:
        tool = TOOL_MAP.get(call["name"])
        result = tool.invoke(call["args"]) if tool else f"unknown tool: {call['name']}"
        results.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
    return {"messages": results}

def should_use_tool(state: AgentState) -> str:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "end"

def build_tool_agent():
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_use_tool, {"tools": "tools", "end": END})
    graph.add_edge("tools", "agent")

    return graph.compile()

if __name__ == "__main__":
    app = build_tool_agent()
    questions = [
        "What is sqrt(144) + 5^2?",
        "How many miles is 100 km?",
        "Count the words in: An agent is a system where an LLM chooses and executes tools.",
    ]
    for q in questions:
        print(f"\nQ: {q}")
        result = app.invoke({"messages": [HumanMessage(content=q)]})
        print(f"A: {result['messages'][-1].content}")
```

---

## Tool design principles

**Single responsibility**: one tool does one thing. Don't bundle calculation and search into the same tool.

**Clear docstrings**: the LLM selects tools based on docstrings alone. Specify input format, return format, and supported range explicitly.

**Fail gracefully**: if a tool raises an exception, the agent loop halts. Catch exceptions internally and return an error string instead.

**Determinism**: tools should return the same output for the same input. Random or time-dependent tools make agent debugging unnecessarily hard.

<!-- toc:begin -->
## In this series

- [LangGraph introduction and graph basics](./01-graph-basics.md)
- [State management and checkpoints](./02-state-and-checkpoints.md)
- [Conditional edges and branching](./03-conditional-edges.md)
- **Tool-calling agents (current)**
- Multi-agent systems (upcoming)
- Completing LangGraph (upcoming)

<!-- toc:end -->

---

## References

- [LangGraph tool node documentation](https://langchain-ai.github.io/langgraph/how-tos/tool-calling/)
- [LangChain tool definitions](https://python.langchain.com/docs/modules/tools/)
- [LangGraph agent patterns](https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/)

Tags: LangGraph, Agent, Python, LLM
