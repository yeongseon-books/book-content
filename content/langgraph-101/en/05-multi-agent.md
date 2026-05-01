---
title: 'Multi-agent systems'
series: langgraph-101
episode: 5
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

# Multi-agent systems

> LangGraph 101 (5/6)

Example code: [github.com/yeongseon-books/langgraph-101](https://github.com/yeongseon-books/langgraph-101/tree/main/en/05-multi-agent)

Complex tasks benefit from multiple specialized agents working together. One agent orchestrates the work; the others focus on their specific roles. This post implements the supervisor-worker pattern as a multi-agent system in LangGraph.

---

## Supervisor-worker pattern

The supervisor analyzes the request, delegates to the appropriate worker agent, and integrates the results into a final answer.

```
user → [supervisor] → [research agent] → result
                    → [code agent]     → result
                    → [summary agent]  → final answer
```

---

## Agent implementation

```python
import os
from typing import TypedDict, Annotated, Literal

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_groq import ChatGroq

class MultiAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    task_type: str
    research_result: str
    code_result: str
    final_answer: str

def _llm(temperature: float = 0.0) -> ChatGroq:
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=temperature,
    )

def supervisor_node(state: MultiAgentState) -> MultiAgentState:
    last_msg = state["messages"][-1].content
    response = _llm().invoke([
        SystemMessage(content="""Analyze the user request and determine the task type.

- research: information gathering, concept explanation, fact checking
- code: code writing, debugging, code explanation
- summary: summarizing or organizing information

Return only one of: research, code, summary."""),
        HumanMessage(content=last_msg),
    ])
    task_type = response.content.strip().lower()
    return {"task_type": task_type if task_type in ("research", "code", "summary") else "research"}

def research_agent_node(state: MultiAgentState) -> MultiAgentState:
    last_msg = state["messages"][-1].content
    response = _llm().invoke([
        SystemMessage(content="You are a research expert. Provide accurate and detailed information with clear key points."),
        HumanMessage(content=last_msg),
    ])
    return {
        "research_result": response.content,
        "messages": [AIMessage(content=f"[research agent] {response.content}")],
    }

def code_agent_node(state: MultiAgentState) -> MultiAgentState:
    last_msg = state["messages"][-1].content
    response = _llm().invoke([
        SystemMessage(content="You are a senior Python developer. Write clear, practical code with type hints, docstrings, and explanations."),
        HumanMessage(content=last_msg),
    ])
    return {
        "code_result": response.content,
        "messages": [AIMessage(content=f"[code agent] {response.content}")],
    }

def summary_agent_node(state: MultiAgentState) -> MultiAgentState:
    parts = []
    if state.get("research_result"):
        parts.append(f"Research:\n{state['research_result']}")
    if state.get("code_result"):
        parts.append(f"Code:\n{state['code_result']}")
    context = "\n\n".join(parts) if parts else state["messages"][-1].content

    response = _llm().invoke([
        SystemMessage(content="Synthesize the following information into a clear, structured final answer."),
        HumanMessage(content=f"Original question: {state['messages'][0].content}\n\n{context}"),
    ])
    return {
        "final_answer": response.content,
        "messages": [AIMessage(content=response.content)],
    }

def route_by_task_type(state: MultiAgentState) -> Literal["research", "code", "summary"]:
    return state["task_type"]

def build_multi_agent_graph():
    graph = StateGraph(MultiAgentState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("research", research_agent_node)
    graph.add_node("code", code_agent_node)
    graph.add_node("summary", summary_agent_node)

    graph.set_entry_point("supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_by_task_type,
        {"research": "research", "code": "code", "summary": "summary"},
    )
    graph.add_edge("research", "summary")
    graph.add_edge("code", "summary")
    graph.add_edge("summary", END)
    return graph.compile()

if __name__ == "__main__":
    app = build_multi_agent_graph()
    initial: MultiAgentState = {
        "messages": [], "task_type": "",
        "research_result": "", "code_result": "", "final_answer": "",
    }
    questions = [
        "What is Python asynchronous programming?",
        "Implement a Fibonacci sequence generator in Python.",
    ]
    for q in questions:
        result = app.invoke({**initial, "messages": [HumanMessage(content=q)]})
        print(f"\nQ: {q}")
        print(f"task type: {result['task_type']}")
        print(f"answer:\n{result['final_answer'][:300]}...")
```

---

## Inter-agent communication

Agents communicate through shared state. Each agent writes its result to a dedicated state field; the next agent reads from it.

This keeps coupling low. The summary agent does not need to know how the code agent is implemented — it only reads `code_result`. Adding a new agent type requires no changes to existing agents, only a new node and routing entry.

<!-- blog-only:start -->
Next: [Completing LangGraph](./06-langgraph-complete.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- [LangGraph introduction and graph basics](./01-graph-basics.md)
- [State management and checkpoints](./02-state-and-checkpoints.md)
- [Conditional edges and branching](./03-conditional-edges.md)
- [Tool-calling agents](./04-tool-calling-agent.md)
- **Multi-agent systems (current)**
- Completing LangGraph (upcoming)

<!-- toc:end -->

---

## References

- [LangGraph multi-agent documentation](https://langchain-ai.github.io/langgraph/how-tos/multi-agent-network/)
- [LangGraph supervisor pattern](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/)
- [LangGraph agent network concepts](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)

Tags: LangGraph, Agent, Python, LLM
