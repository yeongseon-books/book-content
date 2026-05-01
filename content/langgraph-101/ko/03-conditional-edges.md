---
title: '조건부 엣지와 분기 흐름'
series: langgraph-101
episode: 3
language: ko
status: publish-ready
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

## 이 글에서 답할 질문

- `add_conditional_edges()`는 언제 써야 할까요?
- 상태를 보고 다음 노드를 고르는 함수는 어떤 역할만 맡아야 할까요?
- 분기 그래프를 만들 때 무한 루프를 어떻게 피할까요?

> 조건부 엣지는 상태를 계산한 뒤 다음 노드 이름을 반환해 그래프의 흐름을 런타임에 결정합니다.

예제 코드: [github.com/yeongseon-books/langgraph-101](https://github.com/yeongseon-books/langgraph-101/tree/main/ko/03-conditional-edges)

LLM 워크플로가 실제 서비스로 가면 모든 요청이 같은 경로를 타지 않습니다. 어떤 질문은 코드 생성으로, 어떤 질문은 개념 설명으로, 어떤 질문은 디버깅 흐름으로 보내야 합니다. LangGraph에서는 이 결정을 조건부 엣지 하나로 드러낼 수 있습니다.

![이 글에서 답할 질문](../../../assets/langgraph-101/03/03-01-questions-this-post-answers.ko.png)
## 최소 실행 예제

```python
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

class RouterState(TypedDict):
    question: str
    route: str
    answer: str

def classify_question(state: RouterState) -> RouterState:
    text = state["question"].lower()
    if any(word in text for word in ("bug", "error", "traceback")):
        route = "debug"
    elif any(word in text for word in ("code", "implement", "write")):
        route = "code"
    else:
        route = "concept"
    return {"route": route}

def route_question(state: RouterState) -> Literal["code", "concept", "debug"]:
    return state["route"]

def answer_code(_: RouterState) -> RouterState:
    return {"answer": "Route: code. Next node should generate or review code."}

def answer_concept(_: RouterState) -> RouterState:
    return {"answer": "Route: concept. Next node should explain the idea clearly."}

def answer_debug(_: RouterState) -> RouterState:
    return {"answer": "Route: debug. Next node should inspect failure details first."}

def build_graph():
    graph = StateGraph(RouterState)
    graph.add_node("classify", classify_question)
    graph.add_node("code", answer_code)
    graph.add_node("concept", answer_concept)
    graph.add_node("debug", answer_debug)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        route_question,
        {"code": "code", "concept": "concept", "debug": "debug"},
    )
    graph.add_edge("code", END)
    graph.add_edge("concept", END)
    graph.add_edge("debug", END)

    return graph.compile()

if __name__ == "__main__":
    app = build_graph()
    for question in [
        "Write Python code for quicksort.",
        "What is a checkpoint in LangGraph?",
        "I got a traceback while running my graph.",
    ]:
        result = app.invoke({"question": question, "route": "", "answer": ""})
        print(f"Question: {question}")
        print(f"Route: {result['route']}")
        print(f"Answer: {result['answer']}\n")
```

```
출력 결과
Question: Write Python code for quicksort.
Route: code
Answer: Route: code. Next node should generate or review code.

Question: What is a checkpoint in LangGraph?
Route: concept
Answer: Route: concept. Next node should explain the idea clearly.

Question: I got a traceback while running my graph.
Route: debug
Answer: Route: debug. Next node should inspect failure details first.
```

실행 파일: `/root/Github/langgraph-101/ko/03-conditional-edges/main.py`

## 이 코드에서 봐야 할 것

- `classify_question()`은 분기 판단에 필요한 값을 상태에 씁니다.
- `route_question()`은 부작용 없이 다음 노드 이름만 반환합니다.
- `path_map` 딕셔너리 덕분에 문자열 라벨과 실제 노드 이름 매핑이 명시적으로 남습니다.

## 실무에서 헷갈리는 지점

- 라우팅 함수 안에서 LLM 호출까지 같이 넣으면 디버깅이 어려워집니다. 분류와 라우팅은 분리하는 편이 낫습니다.
- 조건부 엣지는 if/else 한 번으로 끝나지 않습니다. 루프를 만들 수도 있으므로 종료 조건을 항상 같이 설계해야 합니다.
- 라우트 문자열이 오타 나면 런타임에 바로 깨집니다. `Literal[...]` 힌트를 두는 이유가 여기 있습니다.

## 체크리스트

- [ ] 분기 기준이 상태 필드로 분리되어 있는가
- [ ] 라우팅 함수가 외부 부작용 없이 순수하게 동작하는가
- [ ] 모든 분기 경로가 `END` 또는 다음 안정된 노드로 닫히는가

## 정리

조건부 엣지는 LangGraph가 "그래프답게" 느껴지는 첫 지점입니다. 다음 글에서는 이 분기 흐름 위에 실제 도구 호출 루프를 얹어 에이전트 형태로 발전시켜 보겠습니다.

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

- [LangGraph branching 가이드](https://langchain-ai.github.io/langgraph/how-tos/branching/)
- [LangGraph low-level concepts: edges](https://langchain-ai.github.io/langgraph/concepts/low_level/)
- [LangGraph recursion limit 가이드](https://langchain-ai.github.io/langgraph/how-tos/recursion-limit/)

Tags: LangGraph, Agent, Python, LLM
