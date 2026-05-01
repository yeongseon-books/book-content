---
title: 'LangGraph introduction and graph basics'
series: langgraph-101
episode: 1
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

# LangGraph introduction and graph basics

> LangGraph 101 (1/6)

Example code: [github.com/yeongseon-books/langgraph-101](https://github.com/yeongseon-books/langgraph-101/tree/main/en/01-graph-basics)

LangChain handles linear chains well. Real agents are different — they use a tool, look at the result, decide what to do next, and use another tool. This loop is what LangGraph is built to express. This post introduces the core concepts: StateGraph, nodes, and edges, and builds the first graph.

---

## Core concepts

LangGraph represents LLM workflows as **directed graphs**.

- **Node**: a unit of work. Any processing step — LLM call, tool execution, data transformation.
- **Edge**: flow between nodes. Unconditional (always go there) or conditional (branch based on state).
- **State**: data that flows through the entire graph. Each node receives state, optionally modifies it, and returns the update.
- **Checkpoint**: a state snapshot. The foundation for pause/resume and memory.

---

## First graph: echo bot

Start with the simplest possible graph — receive user input, process with LLM, return.

```python
import os
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq

class BasicState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def call_llm(state: BasicState) -> BasicState:
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.0,
    )
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def build_basic_graph():
    graph = StateGraph(BasicState)
    graph.add_node("llm", call_llm)
    graph.set_entry_point("llm")
    graph.add_edge("llm", END)
    return graph.compile()

if __name__ == "__main__":
    app = build_basic_graph()
    result = app.invoke({"messages": [HumanMessage(content="Explain Python list comprehensions.")]})
    print(result["messages"][-1].content)
```

---

## Multi-node pipeline

Add nodes and define order to build a pipeline.

```python
from langchain_core.messages import SystemMessage

class PipelineState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    topic: str
    summary: str

def extract_topic(state: PipelineState) -> PipelineState:
    last_msg = state["messages"][-1].content
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)
    response = llm.invoke([
        SystemMessage(content="Extract the core topic of the user message as a single word. Return only the word."),
        HumanMessage(content=last_msg),
    ])
    return {"topic": response.content.strip()}

def generate_answer(state: PipelineState) -> PipelineState:
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)
    response = llm.invoke([
        SystemMessage(content=f"You are an expert in {state['topic']}. Explain clearly and practically."),
        *state["messages"],
    ])
    return {"messages": [response]}

def summarize_answer(state: PipelineState) -> PipelineState:
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)
    last_answer = state["messages"][-1].content
    response = llm.invoke([
        SystemMessage(content="Summarize the following in exactly one sentence."),
        HumanMessage(content=last_answer),
    ])
    return {"summary": response.content}

def build_pipeline_graph():
    graph = StateGraph(PipelineState)
    graph.add_node("extract_topic", extract_topic)
    graph.add_node("generate_answer", generate_answer)
    graph.add_node("summarize", summarize_answer)

    graph.set_entry_point("extract_topic")
    graph.add_edge("extract_topic", "generate_answer")
    graph.add_edge("generate_answer", "summarize")
    graph.add_edge("summarize", END)
    return graph.compile()

if __name__ == "__main__":
    pipeline = build_pipeline_graph()
    result = pipeline.invoke({
        "messages": [HumanMessage(content="Explain the difference between generators and iterators.")],
        "topic": "",
        "summary": "",
    })
    print(f"topic: {result['topic']}")
    print(f"summary: {result['summary']}")
    print(f"\nfull answer:\n{result['messages'][-1].content}")
```

---

## State design principles

State is the shared memory flowing through the graph. Two decisions matter at design time.

**Field type**: `Annotated[list, add_messages]` appends rather than overwrites. Use it for cumulative data like message history. Plain typed fields are overwritten by each update.

**Field scope**: only put data in state that another node needs. Keep intermediate results as local variables; write to state only what the next node must see.

<!-- blog-only:start -->
Next: [State management and checkpoints](./02-state-and-checkpoints.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- **LangGraph introduction and graph basics (current)**
- State management and checkpoints (upcoming)
- Conditional edges and branching (upcoming)
- Tool-calling agents (upcoming)
- Multi-agent systems (upcoming)
- Completing LangGraph (upcoming)

<!-- toc:end -->

---

## References

- [LangGraph documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph concepts guide](https://langchain-ai.github.io/langgraph/concepts/)
- [StateGraph API reference](https://langchain-ai.github.io/langgraph/reference/graphs/)

Tags: LangGraph, Agent, Python, LLM
