---
title: 'LangGraph 소개와 그래프 기초'
series: langgraph-101
episode: 1
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

# LangGraph 소개와 그래프 기초

> LangGraph 101 (1/6)

LangChain은 선형 체인을 잘 다룹니다. 그러나 실제 에이전트는 루프를 돕니다. 도구를 쓰고, 결과를 보고, 다음 단계를 결정하고, 또 도구를 씁니다. 이 반복 흐름을 표현하는 것이 LangGraph의 핵심입니다. 이 포스트에서는 LangGraph의 기본 개념인 StateGraph, 노드, 엣지를 소개하고 첫 번째 그래프를 만듭니다.

---

## LangGraph의 핵심 개념

LangGraph는 LLM 워크플로를 **방향성 그래프(directed graph)**로 표현합니다.

- **노드(Node)**: 작업 단위. LLM 호출, 도구 실행, 데이터 변환 등 모든 처리 단계입니다.
- **엣지(Edge)**: 노드 간 흐름. 조건 없이 항상 이동하거나, 조건에 따라 다른 노드로 분기합니다.
- **상태(State)**: 그래프 전체를 흐르는 데이터. 각 노드는 상태를 받아 수정하고 반환합니다.
- **체크포인트**: 상태 스냅샷. 중단과 재개, 메모리 구현의 기반입니다.

---

## 첫 번째 그래프: 에코 봇

가장 단순한 그래프부터 시작합니다. 사용자 입력을 받아 LLM으로 처리하고 반환합니다.

```python
import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq

# ── 상태 스키마 ───────────────────────────────────────────────────────────
class BasicState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# ── 노드 ──────────────────────────────────────────────────────────────────
def call_llm(state: BasicState) -> BasicState:
    """LLM을 호출하고 응답을 상태에 추가합니다."""
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.0,
    )
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# ── 그래프 구성 ───────────────────────────────────────────────────────────
def build_basic_graph() -> StateGraph:
    graph = StateGraph(BasicState)
    graph.add_node("llm", call_llm)

    graph.set_entry_point("llm")
    graph.add_edge("llm", END)

    return graph.compile()

# ── 실행 ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = build_basic_graph()

    result = app.invoke({"messages": [HumanMessage(content="파이썬 리스트 컴프리헨션을 설명해 주세요.")]})
    print(result["messages"][-1].content)
```

---

## 다중 노드 그래프

노드를 추가하고 순서를 정의하면 파이프라인을 만들 수 있습니다.

```python
from langchain_core.messages import SystemMessage

class PipelineState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    topic: str
    summary: str

def extract_topic(state: PipelineState) -> PipelineState:
    """사용자 메시지에서 주제를 추출합니다."""
    last_msg = state["messages"][-1].content
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)
    response = llm.invoke([
        SystemMessage(content="사용자 메시지의 핵심 주제를 한 단어로 추출하세요. 단어만 반환하세요."),
        HumanMessage(content=last_msg),
    ])
    return {"topic": response.content.strip()}

def generate_answer(state: PipelineState) -> PipelineState:
    """주제를 바탕으로 상세한 답변을 생성합니다."""
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)
    response = llm.invoke([
        SystemMessage(content=f"당신은 {state['topic']} 전문가입니다. 명확하고 실용적으로 설명하세요."),
        *state["messages"],
    ])
    return {"messages": [response]}

def summarize_answer(state: PipelineState) -> PipelineState:
    """답변을 한 문장으로 요약합니다."""
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)
    last_answer = state["messages"][-1].content
    response = llm.invoke([
        SystemMessage(content="주어진 내용을 한 문장으로 요약하세요."),
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
        "messages": [HumanMessage(content="제너레이터와 이터레이터의 차이를 설명해 주세요.")],
        "topic": "",
        "summary": "",
    })
    print(f"주제: {result['topic']}")
    print(f"요약: {result['summary']}")
    print(f"\n전체 답변:\n{result['messages'][-1].content}")
```

---

## 상태 설계 원칙

상태는 그래프를 흐르는 공유 메모리입니다. 설계 시 두 가지를 결정해야 합니다.

**필드 타입**: `Annotated[list, add_messages]`는 리스트를 덮어쓰지 않고 추가합니다. 메시지 히스토리처럼 누적이 필요한 필드에 씁니다. 나머지 필드는 일반 타입으로 선언하면 덮어씁니다.

**필드 범위**: 노드가 필요한 정보만 상태에 담습니다. 임시 계산 결과는 노드 로컬 변수로 유지하고, 다음 노드에 전달할 데이터만 상태에 씁니다.

<!-- toc:begin -->
## 시리즈 목차

- **LangGraph 소개와 그래프 기초 (현재 글)**
- 상태 관리와 체크포인트 (예정)
- 조건부 엣지와 분기 흐름 (예정)
- 도구 호출 에이전트 (예정)
- 멀티 에이전트 시스템 (예정)
- LangGraph 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
- [LangGraph 개념 가이드](https://langchain-ai.github.io/langgraph/concepts/)
- [StateGraph API](https://langchain-ai.github.io/langgraph/reference/graphs/)

Tags: LangGraph, Agent, Python, LLM
