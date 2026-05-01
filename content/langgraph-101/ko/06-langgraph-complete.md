---
title: 'LangGraph 완성'
series: langgraph-101
episode: 6
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

# LangGraph 완성

> LangGraph 101 (6/6)

예제 코드: [github.com/yeongseon-books/langgraph-101](https://github.com/yeongseon-books/langgraph-101/tree/main/ko/06-langgraph-complete)

이 시리즈에서 다룬 그래프 기초, 체크포인트, 조건부 엣지, 도구 호출, 멀티 에이전트를 하나의 완전한 프로덕션 에이전트로 통합합니다. 대화 기억, 도구 사용, 품질 검증, 멀티턴 대화를 지원하는 에이전트를 만듭니다.

---

## 완전한 프로덕션 에이전트

```python
import json
import math
import os
import sqlite3
from typing import TypedDict, Annotated, Literal

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage, AIMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# ── 도구 ──────────────────────────────────────────────────────────────────
@tool
def calculator(expression: str) -> str:
    """수학 표현식을 계산합니다. 예: '2 + 3 * 4', 'sqrt(16)', 'pi * 5**2'"""
    try:
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        return str(eval(expression, {"__builtins__": {}}, allowed))
    except Exception as e:
        return f"오류: {e}"

@tool
def word_stats(text: str) -> str:
    """텍스트의 단어 수, 문자 수를 반환합니다."""
    return json.dumps({"words": len(text.split()), "chars": len(text)}, ensure_ascii=False)

TOOLS = [calculator, word_stats]
TOOL_MAP = {t.name: t for t in TOOLS}

SYSTEM_PROMPT = """당신은 유용한 파이썬 튜터 에이전트입니다.
도구를 활용해 정확한 계산과 분석을 수행하세요.
이전 대화 내용을 기억하고 맥락에 맞게 답변하세요.
모르는 것은 솔직하게 말하세요."""

# ── 상태 ──────────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    iterations: int

# ── 노드 ──────────────────────────────────────────────────────────────────
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
        result = t.invoke(call["args"]) if t else f"알 수 없는 도구: {call['name']}"
        results.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
    return {"messages": results}

# ── 라우팅 ────────────────────────────────────────────────────────────────
MAX_ITERATIONS = 10

def route_agent(state: AgentState) -> Literal["tools", "end"]:
    if state["iterations"] >= MAX_ITERATIONS:
        return "end"
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "end"

# ── 그래프 ────────────────────────────────────────────────────────────────
def build_production_agent(use_persistence: bool = False):
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", route_agent, {"tools": "tools", "end": END})
    graph.add_edge("tools", "agent")

    checkpointer = MemorySaver() if not use_persistence else _sqlite_checkpointer()
    return graph.compile(checkpointer=checkpointer)

def _sqlite_checkpointer():
    conn = sqlite3.connect("agent.db", check_same_thread=False)
    from langgraph.checkpoint.sqlite import SqliteSaver
    return SqliteSaver(conn)

# ── 대화 루프 ──────────────────────────────────────────────────────────────
def run_conversation(thread_id: str = "demo_session"):
    app = build_production_agent()
    config = {"configurable": {"thread_id": thread_id}}

    print("파이썬 튜터 에이전트 (종료: 'quit')")
    print("-" * 40)

    while True:
        user_input = input("\n사용자: ").strip()
        if user_input.lower() in ("quit", "q", "exit"):
            print("대화를 종료합니다.")
            break
        if not user_input:
            continue

        result = app.invoke(
            {"messages": [HumanMessage(content=user_input)], "iterations": 0},
            config=config,
        )
        last_msg = result["messages"][-1]
        print(f"\n에이전트: {last_msg.content}")
```

---

## 배치 평가 통합

프로덕션 에이전트는 배포 전 품질 검증이 필요합니다.

```python
def evaluate_agent(app, test_cases: list[dict]) -> dict:
    """에이전트 품질을 배치로 평가합니다."""
    results = []
    for tc in test_cases:
        config = {"configurable": {"thread_id": f"eval_{tc['id']}"}}
        result = app.invoke(
            {"messages": [HumanMessage(content=tc["question"])], "iterations": 0},
            config=config,
        )
        answer = result["messages"][-1].content
        keyword_hits = [kw for kw in tc["expected_keywords"] if kw.lower() in answer.lower()]
        results.append({
            "id": tc["id"],
            "passed": len(keyword_hits) == len(tc["expected_keywords"]),
            "keyword_coverage": len(keyword_hits) / len(tc["expected_keywords"]) if tc["expected_keywords"] else 1.0,
        })

    pass_rate = sum(1 for r in results if r["passed"]) / len(results) if results else 0.0
    return {"total": len(results), "pass_rate": round(pass_rate, 2), "details": results}

if __name__ == "__main__":
    # 배치 평가 실행
    app = build_production_agent()
    test_cases = [
        {"id": 1, "question": "sqrt(256)은 얼마인가요?", "expected_keywords": ["16"]},
        {"id": 2, "question": "파이썬 리스트 컴프리헨션이란?", "expected_keywords": ["리스트", "표현식"]},
    ]
    report = evaluate_agent(app, test_cases)
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # 대화 모드 실행
    # run_conversation()
```

---

## 시리즈 마무리

이 시리즈에서 구축한 에이전트는 여섯 가지 레이어로 구성됩니다.

1. **그래프 기초**: StateGraph, 노드, 엣지로 워크플로 정의
2. **체크포인터**: 대화 기억과 세션 관리
3. **조건부 엣지**: 상황에 따른 동적 흐름 제어
4. **도구 호출**: LLM이 외부 기능을 활용하는 에이전트 루프
5. **멀티 에이전트**: 전문 에이전트 협력 시스템
6. **프로덕션 통합**: 모든 레이어의 조합

LangGraph의 핵심은 복잡한 워크플로를 명시적 그래프로 표현한다는 것입니다. 흐름이 코드에 숨겨지지 않고 그래프 정의에 드러나기 때문에 디버깅, 테스트, 확장이 모두 쉬워집니다.

<!-- toc:begin -->
## 시리즈 목차

- [LangGraph 소개와 그래프 기초](./01-graph-basics.md)
- [상태 관리와 체크포인트](./02-state-and-checkpoints.md)
- [조건부 엣지와 분기 흐름](./03-conditional-edges.md)
- [도구 호출 에이전트](./04-tool-calling-agent.md)
- [멀티 에이전트 시스템](./05-multi-agent.md)
- **LangGraph 완성 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
- [LangGraph 튜토리얼](https://langchain-ai.github.io/langgraph/tutorials/)
- [LangGraph 예제 저장소](https://github.com/langchain-ai/langgraph/tree/main/examples)

Tags: LangGraph, Agent, Python, LLM
