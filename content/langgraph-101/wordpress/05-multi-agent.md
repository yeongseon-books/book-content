---
title: "바이브코딩을 위한 LangGraph (5/6): 멀티 에이전트 시스템"
series: langgraph-101
episode: 5
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LangGraph
- Multi-Agent
- Agent
- Python
---

# 바이브코딩을 위한 LangGraph (5/6): 멀티 에이전트 시스템

이 글은 **바이브코딩을 위한 LangGraph** 시리즈의 다섯 번째 글입니다. 여러 에이전트가 협력하는 멀티 에이전트 시스템을 LangGraph로 구현합니다.

---

단일 에이전트로 모든 것을 처리하려고 하면, 에이전트가 너무 많은 것을 알아야 하고, 프롬프트가 길어지고, 실패 지점이 많아집니다. "검색 전문 에이전트", "코드 작성 에이전트", "검토 에이전트"처럼 역할을 나누면 각 에이전트가 집중할 수 있습니다.

바이브코딩으로 AI에게 "멀티 에이전트 만들어줘"라고 하면 코드가 나옵니다. Supervisor 패턴과 직접 통신 패턴의 차이, 에이전트 간 상태 공유 방법을 모르면 시스템을 확장하기 어렵습니다.

> "멀티 에이전트는 역할을 나눠 각자 집중하게 합니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. Supervisor 패턴과 직접 통신 패턴의 차이가 무엇인가요?
2. 에이전트 간 상태를 어떻게 공유하나요?
3. 하위 에이전트의 실패가 전체 시스템에 어떻게 전파되나요?
4. 에이전트 수가 늘어날 때 어떻게 확장하나요?
5. 멀티 에이전트 시스템의 성능을 어떻게 측정하나요?

---

## Supervisor 패턴

Supervisor가 작업을 적절한 하위 에이전트에게 라우팅합니다.

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
from langchain_openai import ChatOpenAI

class TeamState(TypedDict):
    task: str
    result: str
    assigned_to: str

llm = ChatOpenAI(model="gpt-4o-mini")

def supervisor_node(state: TeamState) -> TeamState:
    # Supervisor가 작업을 분석해서 담당자 결정
    response = llm.invoke([
        {"role": "system", "content": "작업을 분석해서 researcher, coder, reviewer 중 하나를 선택하세요."},
        {"role": "user", "content": state["task"]},
    ])
    assigned = response.content.strip().lower()
    if assigned not in ["researcher", "coder", "reviewer"]:
        assigned = "researcher"
    return {"assigned_to": assigned}

def researcher_node(state: TeamState) -> TeamState:
    result = llm.invoke([{"role": "user", "content": f"다음을 조사해주세요: {state['task']}"}])
    return {"result": result.content}

def coder_node(state: TeamState) -> TeamState:
    result = llm.invoke([{"role": "user", "content": f"코드를 작성해주세요: {state['task']}"}])
    return {"result": result.content}

def reviewer_node(state: TeamState) -> TeamState:
    result = llm.invoke([{"role": "user", "content": f"다음을 검토해주세요: {state['result']}"}])
    return {"result": result.content}
```

## 그래프 구성

```python
def route_to_agent(state: TeamState) -> Literal["researcher", "coder", "reviewer"]:
    return state["assigned_to"]

graph = StateGraph(TeamState)
graph.add_node("supervisor", supervisor_node)
graph.add_node("researcher", researcher_node)
graph.add_node("coder", coder_node)
graph.add_node("reviewer", reviewer_node)

graph.add_edge(START, "supervisor")
graph.add_conditional_edges(
    "supervisor",
    route_to_agent,
    {"researcher": "researcher", "coder": "coder", "reviewer": "reviewer"},
)
graph.add_edge("researcher", END)
graph.add_edge("coder", END)
graph.add_edge("reviewer", END)

app = graph.compile()
```

## 실행

```python
result = app.invoke({"task": "Python으로 피보나치 수열을 구현해줘", "result": "", "assigned_to": ""})
print(result["result"])
```

---

## Before / After

| 항목 | Before (단일 에이전트) | After (멀티 에이전트) |
|------|----------------------|---------------------|
| 역할 분리 | 없음(모든 것 처리) | Supervisor가 라우팅 |
| 프롬프트 크기 | 점점 커짐 | 에이전트별 집중 |
| 실패 격리 | 전체 실패 | 에이전트별 독립 |
| 확장 | 어려움 | 노드 추가로 확장 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| Supervisor 무한 루프 | 계속 라우팅 | 각 에이전트에서 END로 연결 |
| 상태 필드 누락 | KeyError | TypedDict에 모든 필드 정의 |
| 에이전트 간 의존성 | 순서 의존 | Supervisor가 의존성 관리 |
| 에이전트 수 너무 많음 | 관리 복잡 | 3~5개로 시작 |

---

## AI 활용 팁

```
LangGraph Supervisor 패턴으로 researcher, coder, reviewer 에이전트를 조율하는 시스템을 만들어줘.
Supervisor는 LLM으로 작업을 분석하고 적절한 에이전트에게 라우팅해야 해.
각 에이전트는 자신의 역할에 집중하고 결과를 state["result"]에 저장해줘.
```

---

## 체크리스트

- [ ] TeamState TypedDict 정의
- [ ] Supervisor 라우팅 노드 구현
- [ ] 역할별 에이전트 노드 구현
- [ ] add_conditional_edges로 Supervisor → 에이전트 라우팅
- [ ] 각 에이전트에서 END 연결
- [ ] 엣지 케이스(알 수 없는 에이전트) 처리

---

## 처음 질문으로 돌아가기

"에이전트 하나로 다 처리하면 안 되나요?" — 처음엔 됩니다. 작업이 복잡해지면 단일 에이전트의 프롬프트가 길어지고 실패 지점이 많아집니다. 역할을 나눠 Supervisor가 라우팅하면 각 에이전트가 집중할 수 있고 시스템 확장이 쉬워집니다.

---

## 정리

- Supervisor 패턴은 중앙 에이전트가 작업을 적절한 하위 에이전트에게 라우팅한다
- 각 에이전트는 역할에 집중하고 결과를 공유 상태에 저장한다
- add_conditional_edges로 Supervisor의 라우팅 결정을 그래프 흐름으로 표현한다
- 3~5개 에이전트로 시작해 필요에 따라 노드를 추가한다

---

## 참고 자료

- [LangGraph 멀티 에이전트](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
- [Supervisor 패턴 튜토리얼](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- Supervisor 패턴
- 그래프 구성
- 실행
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LangGraph, Multi-Agent, Agent, Python
