---
title: 'Conditional edges and branching'
series: langgraph-101
episode: 3
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

# Conditional edges and branching

> LangGraph 101 (3/6)

Example code: [github.com/yeongseon-books/langgraph-101](https://github.com/yeongseon-books/langgraph-101/tree/main/en/03-conditional-edges)

Linear pipelines always take the same path. Agents need to choose different paths depending on what they encounter. LangGraph's conditional edges inspect state and dynamically select the next node. This post implements routing patterns, loops, and escape conditions.

---

## Conditional edge basics

`add_conditional_edges` takes a routing function that receives state and returns the next node name.

```python
import os
from typing import TypedDict, Annotated, Literal

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

class RouterState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    category: str
    response: str

def classify_question(state: RouterState) -> RouterState:
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)
    last_msg = state["messages"][-1].content
    response = llm.invoke([
        SystemMessage(content="""Classify the question as one of:
- code: code writing, debugging, programming
- concept: explanations, theory, principles
- other: everything else

Return only the label: code, concept, or other."""),
        HumanMessage(content=last_msg),
    ])
    category = response.content.strip().lower()
    return {"category": category if category in ("code", "concept", "other") else "other"}

def handle_code_question(state: RouterState) -> RouterState:
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)
    response = llm.invoke([
        SystemMessage(content="Answer with code examples. Always include a code block."),
        *state["messages"],
    ])
    return {"messages": [response], "response": response.content}

def handle_concept_question(state: RouterState) -> RouterState:
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)
    response = llm.invoke([
        SystemMessage(content="Explain step by step with analogies and examples."),
        *state["messages"],
    ])
    return {"messages": [response], "response": response.content}

def handle_other_question(state: RouterState) -> RouterState:
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)
    response = llm.invoke([SystemMessage(content="Be helpful."), *state["messages"]])
    return {"messages": [response], "response": response.content}

def route_by_category(state: RouterState) -> Literal["code", "concept", "other"]:
    return state["category"]

def build_router_graph():
    graph = StateGraph(RouterState)
    graph.add_node("classify", classify_question)
    graph.add_node("code", handle_code_question)
    graph.add_node("concept", handle_concept_question)
    graph.add_node("other", handle_other_question)

    graph.set_entry_point("classify")
    graph.add_conditional_edges(
        "classify",
        route_by_category,
        {"code": "code", "concept": "concept", "other": "other"},
    )
    for node in ("code", "concept", "other"):
        graph.add_edge(node, END)

    return graph.compile()

if __name__ == "__main__":
    app = build_router_graph()
    questions = [
        "Write code to sort a list in Python.",
        "What is recursion?",
        "Why is Python popular?",
    ]
    for q in questions:
        result = app.invoke({"messages": [HumanMessage(content=q)], "category": "", "response": ""})
        print(f"\nQ: {q}\ncategory: {result['category']}\nanswer: {result['response'][:150]}...")
```

---

## Loops and escape conditions

Agent loops repeat until a task is done. Always include an escape condition to prevent infinite loops.

```python
class ReflectionState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    draft: str
    critique: str
    iteration: int
    max_iterations: int
    final: str

def generate_draft(state: ReflectionState) -> ReflectionState:
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.7)
    prompt = state["messages"][-1].content if not state["draft"] else \
        f"Previous answer: {state['draft']}\n\nCritique: {state['critique']}\n\nRevise based on the critique."
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"draft": response.content, "iteration": state["iteration"] + 1}

def critique_draft(state: ReflectionState) -> ReflectionState:
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)
    response = llm.invoke([
        SystemMessage(content="""Critique the following answer.
If it is good enough, return 'APPROVED'.
Otherwise, give one specific improvement in a single sentence."""),
        HumanMessage(content=state["draft"]),
    ])
    return {"critique": response.content}

def should_continue(state: ReflectionState) -> Literal["generate", "finish"]:
    if state["iteration"] >= state["max_iterations"] or "APPROVED" in state["critique"]:
        return "finish"
    return "generate"

def finish(state: ReflectionState) -> ReflectionState:
    return {"final": state["draft"]}

def build_reflection_graph():
    graph = StateGraph(ReflectionState)
    graph.add_node("generate", generate_draft)
    graph.add_node("critique", critique_draft)
    graph.add_node("finish", finish)

    graph.set_entry_point("generate")
    graph.add_edge("generate", "critique")
    graph.add_conditional_edges("critique", should_continue, {"generate": "generate", "finish": "finish"})
    graph.add_edge("finish", END)
    return graph.compile()

if __name__ == "__main__":
    app = build_reflection_graph()
    result = app.invoke({
        "messages": [HumanMessage(content="Explain Python async/await.")],
        "draft": "", "critique": "", "iteration": 0, "max_iterations": 3, "final": "",
    })
    print(f"iterations: {result['iteration']}")
    print(f"final answer:\n{result['final']}")
```

---

## Routing function design

Routing functions must be pure: they receive state and return a node name, with no side effects. LLM calls and API requests belong in nodes, not routing functions.

Always combine a quality-based escape (`"APPROVED"`) with an iteration cap (`max_iterations`). The quality check exits early when the result is good; the cap guarantees termination when it is not.

<!-- blog-only:start -->
Next: [Tool-calling agents](./04-tool-calling-agent.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- [LangGraph introduction and graph basics](./01-graph-basics.md)
- [State management and checkpoints](./02-state-and-checkpoints.md)
- **Conditional edges and branching (current)**
- Tool-calling agents (upcoming)
- Multi-agent systems (upcoming)
- Completing LangGraph (upcoming)

<!-- toc:end -->

---

## References

- [LangGraph conditional edges](https://langchain-ai.github.io/langgraph/how-tos/branching/)
- [LangGraph recursion limit](https://langchain-ai.github.io/langgraph/how-tos/recursion-limit/)
- [LangGraph cycles guide](https://langchain-ai.github.io/langgraph/concepts/low_level/#cycles)

Tags: LangGraph, Agent, Python, LLM
