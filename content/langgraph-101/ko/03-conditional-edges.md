---
title: '조건부 엣지와 분기 흐름'
series: langgraph-101
episode: 3
language: ko
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

# 조건부 엣지와 분기 흐름

> LangGraph 101 (3/6)

선형 파이프라인은 항상 같은 경로로 흐릅니다. 에이전트는 상황에 따라 다른 경로를 선택해야 합니다. LangGraph의 조건부 엣지는 상태를 검사해 다음 노드를 동적으로 결정합니다. 이 포스트에서는 라우팅 패턴, 루프, 탈출 조건을 구현합니다.

---

## 조건부 엣지 기본

`add_conditional_edges`는 상태를 인자로 받아 다음 노드 이름을 반환하는 함수와 함께 씁니다.

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

# ── 라우터 노드 ───────────────────────────────────────────────────────────
def classify_question(state: RouterState) -> RouterState:
    """질문을 카테고리로 분류합니다."""
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)
    last_msg = state["messages"][-1].content
    response = llm.invoke([
        SystemMessage(content="""질문을 다음 중 하나로 분류하세요:
- code: 코드 작성, 디버깅, 프로그래밍 관련
- concept: 개념 설명, 이론, 원리 관련  
- other: 그 외

반드시 code, concept, other 중 하나만 반환하세요."""),
        HumanMessage(content=last_msg),
    ])
    category = response.content.strip().lower()
    if category not in ("code", "concept", "other"):
        category = "other"
    return {"category": category}

# ── 전문 노드들 ───────────────────────────────────────────────────────────
def handle_code_question(state: RouterState) -> RouterState:
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)
    response = llm.invoke([
        SystemMessage(content="코드 예시와 함께 명확하게 답변하세요. 코드 블록을 반드시 포함하세요."),
        *state["messages"],
    ])
    return {"messages": [response], "response": response.content}

def handle_concept_question(state: RouterState) -> RouterState:
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)
    response = llm.invoke([
        SystemMessage(content="개념을 단계별로 명확하게 설명하세요. 비유나 예시를 활용하세요."),
        *state["messages"],
    ])
    return {"messages": [response], "response": response.content}

def handle_other_question(state: RouterState) -> RouterState:
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)
    response = llm.invoke([
        SystemMessage(content="도움이 되는 방향으로 답변하세요."),
        *state["messages"],
    ])
    return {"messages": [response], "response": response.content}

# ── 라우팅 함수 ───────────────────────────────────────────────────────────
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
    graph.add_edge("code", END)
    graph.add_edge("concept", END)
    graph.add_edge("other", END)

    return graph.compile()

if __name__ == "__main__":
    app = build_router_graph()
    questions = [
        "파이썬에서 리스트를 정렬하는 코드를 작성해 주세요.",
        "재귀 함수가 무엇인지 설명해 주세요.",
        "파이썬은 왜 인기가 있나요?",
    ]
    for q in questions:
        result = app.invoke({"messages": [HumanMessage(content=q)], "category": "", "response": ""})
        print(f"\n질문: {q}")
        print(f"카테고리: {result['category']}")
        print(f"답변: {result['response'][:150]}...")
```

---

## 루프와 탈출 조건

에이전트 루프는 작업 완료 전까지 반복합니다. 무한 루프를 막기 위해 반드시 탈출 조건이 필요합니다.

```python
from typing import TypedDict, Annotated

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
        f"이전 답변: {state['draft']}\n\n비판: {state['critique']}\n\n위 비판을 반영해 개선하세요."
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"draft": response.content, "iteration": state["iteration"] + 1}

def critique_draft(state: ReflectionState) -> ReflectionState:
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)
    response = llm.invoke([
        SystemMessage(content="""다음 답변을 비판하세요.
답변이 충분히 좋으면 'APPROVED'를 반환하세요.
개선이 필요하면 구체적인 개선점을 한 문장으로 제시하세요."""),
        HumanMessage(content=state["draft"]),
    ])
    return {"critique": response.content}

def should_continue(state: ReflectionState) -> Literal["generate", "finish"]:
    if state["iteration"] >= state["max_iterations"]:
        return "finish"
    if "APPROVED" in state["critique"]:
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
    reflection_app = build_reflection_graph()
    result = reflection_app.invoke({
        "messages": [HumanMessage(content="파이썬 async/await를 설명해 주세요.")],
        "draft": "", "critique": "", "iteration": 0, "max_iterations": 3, "final": "",
    })
    print(f"반복 횟수: {result['iteration']}")
    print(f"최종 답변:\n{result['final']}")
```

---

## 라우팅 함수 설계 원칙

라우팅 함수는 상태만 받아 노드 이름을 반환합니다. 부작용이 없어야 합니다. LLM 호출이나 외부 API 호출은 라우팅 함수가 아닌 노드에서 수행합니다.

루프의 탈출 조건은 두 가지를 동시에 씁니다. 품질 기반 조건("APPROVED")과 횟수 기반 조건(`max_iterations`)을 모두 설정하면 품질이 충족될 때 빠르게 종료하고, 품질이 달성되지 않아도 무한 루프를 막을 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [LangGraph 소개와 그래프 기초](./01-graph-basics.md)
- [상태 관리와 체크포인트](./02-state-and-checkpoints.md)
- **조건부 엣지와 분기 흐름 (현재 글)**
- 도구 호출 에이전트 (예정)
- 멀티 에이전트 시스템 (예정)
- LangGraph 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangGraph 조건부 엣지 문서](https://langchain-ai.github.io/langgraph/how-tos/branching/)
- [LangGraph 루프 패턴](https://langchain-ai.github.io/langgraph/how-tos/recursion-limit/)
- [LangGraph 사이클 가이드](https://langchain-ai.github.io/langgraph/concepts/low_level/#cycles)

Tags: LangGraph, Agent, Python, LLM
