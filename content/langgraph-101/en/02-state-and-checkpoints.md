---
title: 'State management and checkpoints'
series: langgraph-101
episode: 2
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

# State management and checkpoints

> LangGraph 101 (2/6)

Example code: [github.com/yeongseon-books/langgraph-101](https://github.com/yeongseon-books/langgraph-101/tree/main/en/02-state-and-checkpoints)

Conversational agents need to remember previous turns. LangGraph's checkpointer saves state after each step and automatically maintains conversation history. This post implements conversation persistence using both an in-memory checkpointer for development and a SQLite checkpointer for production.

---

## How checkpoints work

Without a checkpointer, every graph invocation is independent. With a checkpointer, a `thread_id` identifies a conversation session — invoking with the same `thread_id` resumes from where the last invocation left off.

```
invoke 1: [Q1] → run nodes → save state (thread_id="session_1")
invoke 2: restore state (thread_id="session_1") → [Q1, A1, Q2] → run nodes → save state
```

---

## Memory checkpointer (development)

```python
import os
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

class ConversationState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

SYSTEM_PROMPT = "You are a Python tutor. Remember the conversation history and respond in context."

def chat_node(state: ConversationState) -> ConversationState:
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.0,
    )
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT)] + state["messages"])
    return {"messages": [response]}

def build_chat_graph(checkpointer=None):
    graph = StateGraph(ConversationState)
    graph.add_node("chat", chat_node)
    graph.set_entry_point("chat")
    graph.add_edge("chat", END)
    return graph.compile(checkpointer=checkpointer)

def demo_memory_checkpointer():
    checkpointer = MemorySaver()
    app = build_chat_graph(checkpointer)
    config = {"configurable": {"thread_id": "session_1"}}

    turns = [
        "What is a Python decorator?",
        "Show me an example of the concept you just explained.",
        "Why is functools.wraps used in that example?",
    ]
    for msg in turns:
        print(f"\nuser: {msg}")
        result = app.invoke({"messages": [HumanMessage(content=msg)]}, config=config)
        print(f"AI: {result['messages'][-1].content[:200]}...")

if __name__ == "__main__":
    demo_memory_checkpointer()
```

---

## SQLite checkpointer (production)

The memory checkpointer is lost when the process restarts. SQLite persists conversations to disk.

```python
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

def build_persistent_chat_app(db_path: str = "conversations.db"):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    return build_chat_graph(checkpointer)

def demo_sqlite_checkpointer():
    app = build_persistent_chat_app()
    config = {"configurable": {"thread_id": "persistent_session_1"}}

    result = app.invoke(
        {"messages": [HumanMessage(content="What is Python's GIL?")]},
        config=config,
    )
    print(f"turn 1: {result['messages'][-1].content[:200]}...")

    result = app.invoke(
        {"messages": [HumanMessage(content="How does the GIL affect multithreading?")]},
        config=config,
    )
    print(f"\nturn 2 (with prior context): {result['messages'][-1].content[:200]}...")

    state = app.get_state(config)
    print(f"\nsaved message count: {len(state.values['messages'])}")
```

---

## State inspection

```python
def inspect_state():
    checkpointer = MemorySaver()
    app = build_chat_graph(checkpointer)
    config = {"configurable": {"thread_id": "debug"}}

    app.invoke({"messages": [HumanMessage(content="Hello!")]}, config=config)

    state = app.get_state(config)
    print("message count:", len(state.values["messages"]))
    for msg in state.values["messages"]:
        role = "user" if isinstance(msg, HumanMessage) else "AI"
        print(f"  [{role}]: {msg.content[:80]}...")

    print("\nstate history:")
    for snap in app.get_state_history(config):
        cid = snap.config["configurable"].get("checkpoint_id", "N/A")[:8]
        print(f"  step {cid}: {len(snap.values.get('messages', []))} messages")
```

---

## Thread ID design

`thread_id` identifies a conversation session. In production, combine user ID and session ID for uniqueness.

```python
import uuid

def make_thread_id(user_id: str, session_id: str) -> str:
    return f"{user_id}:{session_id}"

new_session = make_thread_id("user_123", str(uuid.uuid4()))
```

Use the memory checkpointer only in development and tests. In production, use SQLite (single server) or Redis/PostgreSQL (distributed). Swapping the checkpointer requires no changes to the graph code.

<!-- toc:begin -->
## In this series

- [LangGraph introduction and graph basics](./01-graph-basics.md)
- **State management and checkpoints (current)**
- Conditional edges and branching (upcoming)
- Tool-calling agents (upcoming)
- Multi-agent systems (upcoming)
- Completing LangGraph (upcoming)

<!-- toc:end -->

---

## References

- [LangGraph checkpoints documentation](https://langchain-ai.github.io/langgraph/reference/checkpoints/)
- [LangGraph persistence guide](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
- [SqliteSaver API](https://langchain-ai.github.io/langgraph/reference/checkpoints/#langgraph.checkpoint.sqlite.SqliteSaver)

Tags: LangGraph, Agent, Python, LLM
