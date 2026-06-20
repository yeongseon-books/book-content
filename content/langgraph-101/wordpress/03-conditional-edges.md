---
title: "바이브코딩을 위한 LangGraph (3/6): 조건부 엣지와 분기 흐름"
series: langgraph-101
episode: 3
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LangGraph
- Conditional Edges
- Agent
- Python
---

# 바이브코딩을 위한 LangGraph (3/6): 조건부 엣지와 분기 흐름

이 글은 **바이브코딩을 위한 LangGraph** 시리즈의 세 번째 글입니다. 상태에 따라 다른 노드로 분기하는 조건부 엣지를 설계합니다.

---

그래프에서 모든 경우가 같은 경로를 가지면 LangChain 체인과 다를 게 없습니다. LangGraph의 핵심은 조건부 엣지입니다. "도구 호출이 있으면 도구를 실행하고, 없으면 종료", "품질 점수가 낮으면 재생성, 높으면 반환" — 이런 분기가 에이전트 루프를 만듭니다.

바이브코딩으로 AI에게 "조건부 엣지 만들어줘"라고 하면 코드가 나옵니다. 라우팅 함수가 반환하는 값이 노드 이름이어야 한다는 것, END를 반환하면 그래프가 종료된다는 것을 모르면 오류가 나도 이유를 모릅니다.

> "조건부 엣지는 상태를 보고 다음 노드를 결정합니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. `add_conditional_edges`의 라우팅 함수가 반환해야 하는 값이 무엇인가요?
2. END를 반환하면 어떻게 되나요?
3. 여러 노드로 분기하는 라우팅 함수를 어떻게 작성하나요?
4. 도구 호출 여부를 상태로 감지하는 방법이 있나요?
5. 무한 루프를 조건부 엣지로 방지하는 방법이 있나요?

---

## 기본 조건부 엣지

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal

class State(TypedDict):
    quality_score: float
    content: str
    attempts: int

def route_by_quality(state: State) -> Literal["regenerate", "output"]:
    if state["quality_score"] < 0.7 and state["attempts"] < 3:
        return "regenerate"
    return "output"

graph = StateGraph(State)
graph.add_node("generate", generate_node)
graph.add_node("evaluate", evaluate_node)
graph.add_node("regenerate", regenerate_node)
graph.add_node("output", output_node)

graph.add_edge(START, "generate")
graph.add_edge("generate", "evaluate")
graph.add_conditional_edges(
    "evaluate",
    route_by_quality,
    {"regenerate": "regenerate", "output": "output"},
)
graph.add_edge("regenerate", "evaluate")  # 루프
graph.add_edge("output", END)
```

## 도구 호출 분기

```python
def should_use_tools(state: State) -> Literal["tools", "__end__"]:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "__end__"

graph.add_conditional_edges(
    "agent",
    should_use_tools,
    {"tools": "tool_executor", "__end__": END},
)
```

## 다중 분기

```python
def route_task(state: State) -> Literal["summarize", "translate", "analyze"]:
    task_type = state.get("task_type", "analyze")
    return task_type

graph.add_conditional_edges(
    "classify",
    route_task,
    {
        "summarize": "summarize_node",
        "translate": "translate_node",
        "analyze": "analyze_node",
    },
)
```

---

## Before / After

| 항목 | Before (선형 체인) | After (조건부 엣지) |
|------|------------------|--------------------|
| 품질 미달 처리 | 없음 | 재생성 루프 |
| 도구 호출 분기 | 불가 | should_use_tools |
| 작업 유형 분기 | if-else | add_conditional_edges |
| 무한 루프 방지 | 없음 | attempts 카운터 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 라우팅 함수가 None 반환 | 런타임 오류 | Literal 타입으로 반환값 강제 |
| 루프에 탈출 조건 없음 | 무한 루프 | attempts 카운터 + 최대값 |
| END 매핑 없음 | 종료 노드 연결 오류 | "__end__": END 매핑 |
| 매핑 딕셔너리 없음 | 자동 매핑 오작동 | 항상 명시적 매핑 |

---

## AI 활용 팁

```
LangGraph 그래프에 품질 기반 재생성 루프를 추가해줘.
evaluate 노드에서 quality_score가 0.7 미만이고 attempts가 3 미만이면 regenerate로 분기해줘.
조건이 맞지 않으면 output으로 가서 END에 연결해줘.
attempts 카운터로 무한 루프를 방지해줘.
```

---

## 체크리스트

- [ ] 라우팅 함수 반환값 Literal 타입 정의
- [ ] add_conditional_edges에 매핑 딕셔너리 명시
- [ ] END 매핑 포함("__end__": END)
- [ ] 루프 탈출 조건(attempts 카운터)
- [ ] 상태에 attempts 필드 추가
- [ ] 조건부 분기 시나리오 테스트

---

## 처음 질문으로 돌아가기

"LangGraph로 루프를 어떻게 만드나요?" — 조건부 엣지로 특정 노드에서 이전 노드로 돌아가는 엣지를 추가하면 루프가 됩니다. 중요한 것은 탈출 조건입니다. attempts 카운터나 품질 임계값으로 루프를 빠져나올 조건을 항상 설정하세요.

---

## 정리

- `add_conditional_edges`의 라우팅 함수는 노드 이름(문자열)을 반환한다
- END는 "__end__"로 매핑한다
- 루프에는 반드시 탈출 조건(attempts 카운터 등)을 설정한다
- 라우팅 함수의 반환값을 Literal 타입으로 명시하면 디버깅이 쉬워진다

---

## 참고 자료

- [LangGraph 조건부 엣지](https://langchain-ai.github.io/langgraph/concepts/low_level/#conditional-edges)
- [LangGraph 도구 호출 에이전트](https://langchain-ai.github.io/langgraph/tutorials/introduction/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 기본 조건부 엣지
- 도구 호출 분기
- 다중 분기
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LangGraph, Conditional Edges, Agent, Python
