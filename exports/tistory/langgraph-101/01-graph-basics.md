
# LangGraph 소개와 그래프 기초

> LangGraph 101 시리즈 (1/6)

<!-- a-grade-intro:begin -->

**핵심 질문**: *왜* *체인* 이 *아니라* *그래프* *인가요*?

> *분기*, *반복*, *상태 공유* 가 *생기면* *그래프* 가 *체인* 보다 *명료* 합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *그래프* 가 *필요* 한 *순간*
- *StateGraph* 의 *기본 구성*
- *node* 와 *edge*
- *START*, *END* *상수*
- *compile* 과 *invoke*

## 왜 중요한가

*LangChain* 의 *LCEL* 은 *직선 흐름* 에 *강합니다*. *조건 분기* 와 *루프* 가 *섞이면* *코드* 가 *복잡* 해집니다. *LangGraph* 는 *흐름* 을 *데이터* 로 *명시* 합니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    S[START] --> N1[node_a]
    N1 --> N2[node_b]
    N2 --> E[END]
```

## 핵심 용어 정리

- **StateGraph**: *상태 타입* 을 *공유* 하는 *그래프* *빌더*.
- **node**: *상태* 를 *입력* 받아 *부분 상태* 를 *돌려* *주는* *함수*.
- **edge**: *어느 노드* 다음에 *어느 노드* 가 *오는지* 의 *연결*.
- **START / END**: *그래프* 의 *시작* 과 *끝* 을 *나타내는* *상수*.
- **compile**: *그래프 정의* 를 *실행 가능* *객체* 로 *변환*.

## Before/After

**Before**: "`if`, `for` 가 *섞인* *체인 함수* 가 *길어지고* *디버깅* 이 *어려워* *집니다*."

**After**: "*노드* 와 *엣지* 로 *흐름* 이 *그림* 처럼 *드러* *납니다*."

## 실습: 첫 그래프 5단계

### 1단계 — 상태 타입 정의

```python
from typing import TypedDict

class State(TypedDict):
    counter: int
    log: list[str]
```

### 2단계 — 노드 두 개 작성

```python
def increment(state: State) -> dict:
    return {"counter": state["counter"] + 1, "log": ["incremented"]}

def double(state: State) -> dict:
    return {"counter": state["counter"] * 2, "log": ["doubled"]}
```

### 3단계 — 그래프 빌드

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(State)
builder.add_node("inc", increment)
builder.add_node("dbl", double)
builder.add_edge(START, "inc")
builder.add_edge("inc", "dbl")
builder.add_edge("dbl", END)
```

### 4단계 — compile

```python
graph = builder.compile()
```

### 5단계 — invoke

```python
result = graph.invoke({"counter": 1, "log": []})
print(result)
# {'counter': 4, 'log': ['doubled']}
```

## 이 코드에서 주목할 점

- *노드* 는 *부분 상태 dict* 만 *반환* 합니다. *나머지 키* 는 *건드리지* *않습니다*.
- *기본 reducer* 는 *덮어* *쓰기* 입니다. *log 리스트* 가 *마지막* *값* 으로 *바뀌는* *이유* 입니다.
- *2편* 에서 *Annotated* 와 *add_messages* 로 *누적 동작* 을 *바꿉니다*.

## 자주 하는 실수 5가지

1. ***START / END 누락*** — *컴파일* 시 *진입점/종점* 오류 가 *납니다*.
2. ***노드 이름 중복*** — *add_node* 가 *조용* 히 *기존 노드* 를 *덮어* *씁니다*.
3. ***전체 상태 반환*** — *부분 상태* 만 *반환* 해도 *충분* 합니다.
4. ***reducer 미지정*** — *list / set* 누적이 *깨집니다* (*2편* 참고).
5. ***compile 누락*** — *builder* 를 *직접* *invoke* 하면 *동작* *안* 합니다.

## 실무에서는 이렇게 쓰입니다

*프로덕션* 에서는 *분기 가 있는 에이전트*, *Human-in-the-loop* 워크플로, *멀티 에이전트* 시스템을 *그래프* 로 *그립니다*. *LangSmith* 가 *각 노드* *입출력* 을 *그대로* *시각화* 합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *흐름* 이 *직선* 이면 *LCEL*, *분기/루프* 가 *생기면* *LangGraph*.
- *노드* 는 *작고* *결정적* 으로 *유지* 합니다.
- *상태 타입* 이 *문서* 입니다.
- *그래프* 는 *그림* 이 *되는지* 부터 *그려* *봅니다*.
- *컴파일 결과* 는 *Runnable* 이라 *기존 LCEL* 과 *섞* *입니다*.

## 체크리스트

- [ ] *State* TypedDict *정의*.
- [ ] *모든 노드* 가 *부분 상태 dict* *반환*.
- [ ] *START → ... → END* *경로* *완성*.
- [ ] *compile* 후 *invoke*.

## 연습 문제

1. *세 번째* *노드* `subtract` 를 *추가* 하고 *순서* 를 *바꿔* *결과* 를 *비교* 하세요.
2. *log* 키의 *기본* *덮어* *쓰기* *동작* 을 *확인* 하기 위해 *각* *노드* 가 *다른* *문자열* 을 *기록* 하게 *하세요*.
3. `graph.get_graph().draw_ascii()` 로 *그래프* *구조* 를 *그려* *보세요*.

## 정리 및 다음 단계

다음 글은 *상태 관리와 체크포인트* 입니다.

## 시리즈 목차

- **LangGraph 소개와 그래프 기초 (현재 글)**
- 상태 관리와 체크포인트 (예정)
- 조건부 엣지와 분기 흐름 (예정)
- 도구 호출 에이전트 (예정)
- 멀티 에이전트 시스템 (예정)
- LangGraph 완성 (예정)

## 참고 자료

- [LangGraph quickstart](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
- [StateGraph reference](https://langchain-ai.github.io/langgraph/reference/graphs/)
- [LangGraph concepts](https://langchain-ai.github.io/langgraph/concepts/low_level/)
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)

Tags: LangGraph, Agent, Python, LLM

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
