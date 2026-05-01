---
title: 'Agent + Tool 패턴 — 자율 도구 선택'
series: ai-app-patterns-101
episode: 4
language: ko
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- RAG
- Agent
- Python
last_reviewed: '2026-05-01'
---

# Agent + Tool 패턴 — 자율 도구 선택

> AI 앱 패턴 101 시리즈 (4/6)

예제 코드: [github.com/yeongseon-books/ai-app-patterns-101](https://github.com/yeongseon-books/ai-app-patterns-101/tree/main/ko/04-agent-tool-pattern)

지금까지는 LLM이 고정된 체인 안에서만 동작했습니다. 입력이 들어오면 정해진 순서로 처리하고 결과를 반환했습니다. Agent 패턴은 다릅니다. LLM이 스스로 판단해서 어떤 도구를 쓸지, 도구 결과를 보고 다음에 무엇을 할지 결정합니다.

이번 글에서는 Agent 패턴의 핵심 개념과 완전한 구현을 다룹니다.

- Agent와 Chain의 차이
- 도구(Tool) 정의와 등록
- ReAct 방식 Agent 구현
- 다중 도구 조합

---

## Agent vs Chain

**Chain**: 입력 → 단계 A → 단계 B → 출력. 실행 경로가 고정됩니다.

**Agent**: 입력 → LLM이 판단 → 도구 선택 → 도구 실행 → 결과 확인 → 필요하면 반복 → 최종 답변. 실행 경로가 동적입니다.

Agent는 "생각(Thought) → 행동(Action) → 관찰(Observation)"을 반복하는 ReAct(Reason + Act) 루프로 동작합니다. LLM이 현재 상황을 추론하고, 도구를 선택해 실행하고, 그 결과를 보고 다음 행동을 결정합니다.

---

## 도구 정의

LangChain에서 도구는 `@tool` 데코레이터로 만듭니다. 함수의 독스트링이 LLM이 도구를 선택할 때 참고하는 설명이 되므로, 정확하게 써야 합니다.

```python
import math
import os
from datetime import datetime

from langchain_core.tools import tool

@tool
def calculate(expression: str) -> str:
    """
    수학 식을 계산합니다.
    예: '2 + 3 * 4', 'sqrt(16)', 'pow(2, 10)'
    파이썬 수식 문법을 사용합니다.
    """
    try:
        # 안전한 수학 함수만 허용
        allowed = {
            "sqrt": math.sqrt,
            "pow": math.pow,
            "abs": abs,
            "round": round,
            "pi": math.pi,
            "e": math.e,
        }
        result = eval(expression, {"__builtins__": {}}, allowed)
        return str(result)
    except Exception as exc:
        return f"계산 오류: {exc}"

@tool
def get_current_time(timezone: str = "Asia/Seoul") -> str:
    """
    현재 날짜와 시간을 반환합니다.
    timezone 파라미터로 시간대를 지정할 수 있습니다 (기본값: Asia/Seoul).
    """
    now = datetime.now()
    return f"현재 시각: {now.strftime('%Y년 %m월 %d일 %H시 %M분')} ({timezone})"

@tool
def word_count(text: str) -> str:
    """
    텍스트의 단어 수와 글자 수를 반환합니다.
    """
    words = len(text.split())
    chars = len(text)
    chars_no_space = len(text.replace(" ", ""))
    return f"단어 수: {words}, 글자 수: {chars} (공백 제외: {chars_no_space})"

@tool
def unit_convert(value: float, from_unit: str, to_unit: str) -> str:
    """
    단위를 변환합니다.
    지원 변환: km↔mile, kg↔lb, celsius↔fahrenheit, m↔ft
    예: value=100, from_unit='km', to_unit='mile'
    """
    conversions = {
        ("km", "mile"): lambda x: x * 0.621371,
        ("mile", "km"): lambda x: x * 1.60934,
        ("kg", "lb"): lambda x: x * 2.20462,
        ("lb", "kg"): lambda x: x * 0.453592,
        ("celsius", "fahrenheit"): lambda x: x * 9 / 5 + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5 / 9,
        ("m", "ft"): lambda x: x * 3.28084,
        ("ft", "m"): lambda x: x * 0.3048,
    }
    key = (from_unit.lower(), to_unit.lower())
    if key not in conversions:
        return f"지원하지 않는 변환: {from_unit} → {to_unit}"
    result = conversions[key](value)
    return f"{value} {from_unit} = {result:.4f} {to_unit}"
```

---

## ReAct Agent 구현

```python
import os

from langchain_groq import ChatGroq
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

tools = [calculate, get_current_time, word_count, unit_convert]

# ReAct 프롬프트 — Thought/Action/Observation 루프 유도
react_prompt = PromptTemplate.from_template("""
당신은 주어진 도구를 사용해 질문에 답하는 AI 어시스턴트입니다.

사용 가능한 도구:
{tools}

도구 이름 목록: {tool_names}

다음 형식을 반드시 따르세요:

Question: 답해야 할 질문
Thought: 어떻게 접근할지 생각
Action: 사용할 도구 이름 (도구 이름 목록 중 하나)
Action Input: 도구에 전달할 입력
Observation: 도구 실행 결과
... (Thought/Action/Action Input/Observation 반복)
Thought: 이제 최종 답변을 알고 있습니다
Final Answer: 최종 답변

시작!

Question: {input}
Thought: {agent_scratchpad}
""")

agent = create_react_agent(llm=llm, tools=tools, prompt=react_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True,
)

# 테스트
questions = [
    "2의 10승은 얼마인가요?",
    "지금 몇 시인가요?",
    "100킬로미터는 몇 마일인가요?",
    "다음 텍스트의 단어 수를 세고 2를 곱하세요: 'The quick brown fox jumps over the lazy dog'",
]

for question in questions:
    print(f"\n{'='*60}")
    print(f"질문: {question}")
    result = agent_executor.invoke({"input": question})
    print(f"최종 답변: {result['output']}")
```

---

## 도구 사용 결과 관찰

`verbose=True`로 실행하면 Agent의 사고 과정이 출력됩니다. Thought → Action → Observation → Thought 순서로 반복되는 것을 볼 수 있습니다. 복잡한 질문일수록 반복 횟수가 늘어납니다.

`max_iterations`는 무한 루프 방지를 위해 항상 설정합니다. 일반적인 작업에는 5~10이 적당합니다.

---

## 도구 오류 처리

도구가 예외를 던지면 Agent가 멈춥니다. 도구 함수 내부에서 예외를 잡아 문자열로 반환하면 Agent가 오류 메시지를 Observation으로 받아 다음 행동을 결정할 수 있습니다.

```python
@tool
def safe_divide(a: float, b: float) -> str:
    """두 수를 나눕니다. 0으로 나누기 오류를 안전하게 처리합니다."""
    if b == 0:
        return "오류: 0으로 나눌 수 없습니다."
    return str(a / b)
```

---

## 마무리

Agent 패턴은 LLM이 단순 체인을 넘어 동적으로 문제를 해결하도록 합니다. 도구의 독스트링이 LLM이 도구를 선택하는 유일한 단서이므로, 구체적이고 명확하게 작성해야 합니다. 모호한 독스트링은 잘못된 도구 선택으로 이어집니다.

다음 글에서는 워크플로 자동화 패턴을 다룹니다. 여러 단계를 체계적으로 연결하는 다단계 체인 설계입니다.

<!-- blog-only:start -->
다음 글: [워크플로 자동화 — 다단계 체인 설계](./05-workflow-automation.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [챗봇 패턴 — 대화 이력 관리와 상태](./01-chatbot-pattern.md)
- [RAG Q&A 패턴 — 문서 기반 질의응답](./02-rag-qa-pattern.md)
- [문서 어시스턴트 — 요약, 추출, 분류](./03-document-assistant.md)
- **Agent + Tool 패턴 — 자율 도구 선택 (현재 글)**
- 워크플로 자동화 — 다단계 체인 설계 (예정)
- Human-in-the-loop — 사람 개입 설계 패턴 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain Agents 개요](https://python.langchain.com/docs/modules/agents/)
- [ReAct 논문 (Yao et al., 2022)](https://arxiv.org/abs/2210.03629)
- [LangChain Tool 정의](https://python.langchain.com/docs/modules/tools/)

Tags: LLM, RAG, Agent, Python
