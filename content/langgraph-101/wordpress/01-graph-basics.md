---
title: "바이브코딩을 위한 LangGraph (1/6): LangGraph 소개와 그래프 기초"
series: langgraph-101
episode: 1
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LangGraph
- Agent
- Python
- LLM
---

# 바이브코딩을 위한 LangGraph (1/6): LangGraph 소개와 그래프 기초

이 글은 **바이브코딩을 위한 LangGraph** 시리즈의 첫 번째 글입니다. LangGraph의 핵심 개념인 StateGraph와 노드, 엣지 구조를 설명합니다.

---

LangChain으로 체인을 만들었습니다. 체인은 선형입니다. 항상 A → B → C로 흐릅니다. 그런데 "상황에 따라 B로 가거나 D로 가야" 한다면? "실패하면 다시 A로 돌아가야" 한다면? 선형 체인으로는 불가능합니다. LangGraph는 그래프 구조로 조건부 흐름과 루프를 가능하게 합니다.

바이브코딩으로 AI에게 "LangGraph로 에이전트 만들어줘"라고 하면 코드가 나옵니다. StateGraph가 무엇인지, 노드가 어떻게 상태를 변환하는지 이해 없이 사용하면 흐름을 수정하기 어렵습니다.

이 글에서는 StateGraph의 기본 구조를 간단한 예시로 설명합니다.

> "LangGraph는 LLM 워크플로를 그래프로 설계합니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. LangGraph와 LangChain LCEL의 차이가 무엇인가요?
2. StateGraph에서 "상태(State)"가 무엇을 의미하나요?
3. 노드(Node)와 엣지(Edge)의 역할이 각각 무엇인가요?
4. START와 END 노드가 왜 필요한가요?
5. 그래프를 컴파일(compile)해야 하는 이유가 무엇인가요?

---

## StateGraph 기본 구조

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
import operator

# 상태 정의
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]  # 메시지 누적
    step: int

# 노드 정의 (상태를 받아 변경된 상태를 반환)
def process_node(state: AgentState) -> AgentState:
    return {
        "messages": [{"role": "assistant", "content": "처리 완료"}],
        "step": state["step"] + 1,
    }

# 그래프 구성
graph = StateGraph(AgentState)
graph.add_node("process", process_node)
graph.add_edge(START, "process")
graph.add_edge("process", END)

app = graph.compile()
```

## 그래프 실행

```python
result = app.invoke({
    "messages": [{"role": "user", "content": "안녕"}],
    "step": 0,
})
print(result)
```

## 여러 노드 연결

```python
def analyze_node(state: AgentState) -> AgentState:
    return {"messages": [{"role": "assistant", "content": "분석 중"}], "step": state["step"] + 1}

def respond_node(state: AgentState) -> AgentState:
    return {"messages": [{"role": "assistant", "content": "응답 생성"}], "step": state["step"] + 1}

graph = StateGraph(AgentState)
graph.add_node("analyze", analyze_node)
graph.add_node("respond", respond_node)
graph.add_edge(START, "analyze")
graph.add_edge("analyze", "respond")
graph.add_edge("respond", END)

app = graph.compile()
```

## 상태 시각화

```python
# ASCII 시각화
print(app.get_graph().draw_ascii())
```

---

## Before / After

| 항목 | Before (LangChain 체인) | After (LangGraph) |
|------|------------------------|-------------------|
| 흐름 | 선형 A→B→C | 조건부 분기 가능 |
| 루프 | 불가 | 순환 엣지 지원 |
| 상태 관리 | 수동 | StateGraph 자동 |
| 시각화 | 없음 | draw_ascii() |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| compile() 없이 invoke | AttributeError | graph.compile() 필수 |
| 상태 반환 없음 | 상태 누락 | 노드에서 dict 반환 |
| START/END 연결 없음 | 그래프 실행 오류 | 시작과 끝 엣지 필수 |
| Annotated 없음 | 메시지 덮어쓰기 | operator.add로 누적 |

---

## AI 활용 팁

```
LangGraph StateGraph로 간단한 2단계 워크플로를 만들어줘.
AgentState는 messages(누적)와 step(카운터)을 포함해야 해.
analyze 노드와 respond 노드를 순서대로 연결하고 컴파일해줘.
draw_ascii()로 그래프 구조를 시각화해줘.
```

---

## 체크리스트

- [ ] langgraph 설치
- [ ] AgentState TypedDict 정의
- [ ] messages 필드에 Annotated[list, operator.add] 적용
- [ ] 노드 함수 작성(상태 → 상태)
- [ ] START → 노드 → END 엣지 연결
- [ ] graph.compile() 후 invoke 테스트

---

## 처음 질문으로 돌아가기

"LangChain이 있는데 LangGraph가 왜 필요한가요?" — LangChain 체인은 선형입니다. 조건에 따라 다른 경로를 가거나, 실패 시 되돌아가거나, 루프를 돌아야 하는 에이전트 워크플로에는 LangGraph의 그래프 구조가 필요합니다.

---

## 정리

- StateGraph는 상태(State)를 공유하는 노드들의 그래프다
- 노드는 상태를 받아 변경된 상태를 딕셔너리로 반환한다
- Annotated[list, operator.add]로 메시지를 덮어쓰지 않고 누적한다
- graph.compile() 후 invoke()로 실행한다

---

## 참고 자료

- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
- [LangGraph 튜토리얼](https://langchain-ai.github.io/langgraph/tutorials/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- StateGraph 기본 구조
- 그래프 실행
- 여러 노드 연결
- 상태 시각화
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LangGraph, Agent, Python, LLM
