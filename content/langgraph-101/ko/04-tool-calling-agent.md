---
title: '도구 호출 에이전트'
series: langgraph-101
episode: 4
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

# 도구 호출 에이전트

> LangGraph 101 (4/6)

예제 코드: [github.com/yeongseon-books/langgraph-101](https://github.com/yeongseon-books/langgraph-101/tree/main/ko/04-tool-calling-agent)

LLM이 스스로 도구를 선택하고 결과를 보고 다음 행동을 결정하는 것이 에이전트의 핵심입니다. 이 포스트에서는 LangGraph로 도구 호출 에이전트를 만듭니다. 도구 정의, 도구 실행 노드, 에이전트 루프를 구현하고 계산기와 검색 도구를 붙입니다.

---

<!-- ebook-only:start -->

이 장의 핵심: **Tool Calling Agent는 Thought → Action → Observation 루프다.** LangGraph에서는 이 루프가 노드와 엣지로 명시적으로 보인다.

## 이 장의 위치

이 글은 시리즈 6편 중 4번째 장입니다.
앞 장에서는 **조건부 엣지와 분기 흐름**을 다뤘습니다.
이 장을 마치면 다음 장에서 **멀티 에이전트 시스템**으로 이어집니다.
<!-- ebook-only:end -->

## 도구 정의

LangChain의 `@tool` 데코레이터로 도구를 정의합니다. docstring이 LLM에 전달되는 도구 설명이 됩니다.

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
    """수학 표현식을 계산합니다.
    
    Args:
        expression: 계산할 수식 (예: '2 + 3 * 4', 'sqrt(16)', 'pi * r**2')
    
    Returns:
        계산 결과 문자열
    """
    try:
        # 안전한 수식 평가 (math 모듈만 허용)
        allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"계산 오류: {e}"

@tool
def word_counter(text: str) -> str:
    """텍스트의 단어 수, 문자 수, 문장 수를 반환합니다.
    
    Args:
        text: 분석할 텍스트
    
    Returns:
        단어 수, 문자 수, 문장 수 정보
    """
    words = len(text.split())
    chars = len(text)
    sentences = text.count(".") + text.count("!") + text.count("?")
    return json.dumps({"words": words, "chars": chars, "sentences": sentences}, ensure_ascii=False)

@tool
def unit_converter(value: float, from_unit: str, to_unit: str) -> str:
    """단위를 변환합니다. 지원 단위: km/mile, kg/lb, celsius/fahrenheit.
    
    Args:
        value: 변환할 값
        from_unit: 원래 단위
        to_unit: 목표 단위
    
    Returns:
        변환된 값과 단위
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
    converter = conversions.get(key)
    if not converter:
        return f"지원하지 않는 단위 변환: {from_unit} → {to_unit}"
    result = converter(value)
    return f"{value} {from_unit} = {result:.4f} {to_unit}"
```

---

## 도구 호출 에이전트 그래프

```python
TOOLS = [calculator, word_counter, unit_converter]
TOOL_MAP = {t.name: t for t in TOOLS}

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def agent_node(state: AgentState) -> AgentState:
    """LLM이 도구 호출 여부를 결정합니다."""
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.0,
    ).bind_tools(TOOLS)
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def tool_node(state: AgentState) -> AgentState:
    """도구 호출을 실행하고 결과를 상태에 추가합니다."""
    last_message = state["messages"][-1]
    tool_results = []

    for tool_call in last_message.tool_calls:
        tool = TOOL_MAP.get(tool_call["name"])
        if tool:
            result = tool.invoke(tool_call["args"])
            tool_results.append(
                ToolMessage(content=str(result), tool_call_id=tool_call["id"])
            )
        else:
            tool_results.append(
                ToolMessage(
                    content=f"알 수 없는 도구: {tool_call['name']}",
                    tool_call_id=tool_call["id"],
                )
            )
    return {"messages": tool_results}

def should_use_tool(state: AgentState) -> str:
    """마지막 메시지에 도구 호출이 있으면 도구 노드로, 없으면 종료."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"

def build_tool_agent():
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")
    graph.add_conditional_edges(
        "agent",
        should_use_tool,
        {"tools": "tools", "end": END},
    )
    graph.add_edge("tools", "agent")  # 도구 실행 후 에이전트로 복귀

    return graph.compile()

if __name__ == "__main__":
    app = build_tool_agent()

    questions = [
        "sqrt(144) + 5^2는 얼마인가요?",
        "100km는 몇 마일인가요?",
        "파이썬 에이전트는 LLM이 도구를 선택해 실행하는 시스템입니다. 이 문장의 단어 수를 세어 주세요.",
    ]

    for q in questions:
        print(f"\n질문: {q}")
        result = app.invoke({"messages": [HumanMessage(content=q)]})
        print(f"답변: {result['messages'][-1].content}")
```

---

## 도구 설계 원칙

**단일 책임**: 도구 하나는 한 가지 일만 합니다. 계산과 검색을 하나의 도구에 넣지 않습니다.

**명확한 docstring**: LLM은 docstring만 보고 도구를 선택합니다. 입력 형식, 반환 형식, 지원하는 범위를 명확히 적어야 합니다.

**실패 처리**: 도구가 예외를 올리면 에이전트 루프가 중단됩니다. 내부에서 예외를 잡아 오류 메시지 문자열을 반환합니다.

**재현 가능성**: 도구는 같은 입력에 항상 같은 출력을 내야 합니다. 랜덤이나 시간 의존적 도구는 에이전트 디버깅을 어렵게 만듭니다.

<!-- blog-only:start -->
다음 글: [멀티 에이전트 시스템](./05-multi-agent.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [LangGraph 소개와 그래프 기초](./01-graph-basics.md)
- [상태 관리와 체크포인트](./02-state-and-checkpoints.md)
- [조건부 엣지와 분기 흐름](./03-conditional-edges.md)
- **도구 호출 에이전트 (현재 글)**
- 멀티 에이전트 시스템 (예정)
- LangGraph 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangGraph 도구 노드 문서](https://langchain-ai.github.io/langgraph/how-tos/tool-calling/)
- [LangChain 도구 정의](https://python.langchain.com/docs/modules/tools/)
- [LangGraph 에이전트 패턴](https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/)

Tags: LangGraph, Agent, Python, LLM
