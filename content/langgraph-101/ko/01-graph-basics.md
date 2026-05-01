---
title: 'LangGraph 소개와 그래프 기초'
series: langgraph-101
episode: 1
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

# LangGraph 소개와 그래프 기초

## 이 글에서 답할 질문

- LangGraph에서 `StateGraph`는 정확히 무엇을 정의할까요?
- 노드와 엣지를 어떻게 연결해야 흐름이 읽히는 그래프가 될까요?
- `invoke()`를 호출하면 상태가 어떤 순서로 흘러갈까요?

> StateGraph는 노드 함수들을 상태 전이 규칙으로 엮어 실행 가능한 워크플로로 바꾸는 설계도입니다.

예제 코드: [github.com/yeongseon-books/langgraph-101](https://github.com/yeongseon-books/langgraph-101/tree/main/ko/01-graph-basics)

LangGraph를 처음 볼 때 가장 중요한 감각은 "체인 여러 개"가 아니라 "상태가 흐르는 그래프"라는 점입니다. 이 글에서는 가장 작은 그래프를 직접 만들면서 노드 추가, 엣지 연결, `invoke()` 실행까지 한 번에 정리합니다.

![이 글에서 답할 질문](../../../assets/langgraph-101/01/01-01-questions-this-post-answers.ko.png)
## 최소 실행 예제

```python
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

class ArticleState(TypedDict):
    user_request: str
    topic: str
    outline: list[str]
    answer: str

def choose_topic(state: ArticleState) -> ArticleState:
    request = state["user_request"].lower()
    if "checkpoint" in request:
        topic = "checkpoints"
    elif "tool" in request:
        topic = "tool calling"
    else:
        topic = "graph basics"
    return {"topic": topic}

def build_outline(state: ArticleState) -> ArticleState:
    outline = [
        f"Define {state['topic']}",
        "Show the nodes in the graph",
        "Explain how invoke() runs the graph",
    ]
    return {"outline": outline}

def write_answer(state: ArticleState) -> ArticleState:
    bullet_lines = "\n".join(f"- {item}" for item in state["outline"])
    answer = (
        f"Request: {state['user_request']}\n"
        f"Chosen topic: {state['topic']}\n"
        "Teaching outline:\n"
        f"{bullet_lines}"
    )
    return {"answer": answer}

def build_graph():
    graph = StateGraph(ArticleState)
    graph.add_node("choose_topic", choose_topic)
    graph.add_node("build_outline", build_outline)
    graph.add_node("write_answer", write_answer)

    graph.add_edge(START, "choose_topic")
    graph.add_edge("choose_topic", "build_outline")
    graph.add_edge("build_outline", "write_answer")
    graph.add_edge("write_answer", END)

    return graph.compile()

if __name__ == "__main__":
    app = build_graph()
    result = app.invoke(
        {
            "user_request": "Explain how a LangGraph StateGraph works.",
            "topic": "",
            "outline": [],
            "answer": "",
        }
    )
    print(result["answer"])
```

```
출력 결과
Request: Explain how a LangGraph StateGraph works.
Chosen topic: graph basics
Teaching outline:
- Define graph basics
- Show the nodes in the graph
- Explain how invoke() runs the graph
```

실행 파일: `/root/Github/langgraph-101/ko/01-graph-basics/main.py`

## 이 코드에서 봐야 할 것

- `StateGraph(ArticleState)`가 그래프 전체에서 공유할 상태 스키마를 정합니다.
- 각 노드는 상태 전체를 받아 필요한 필드만 업데이트해서 반환합니다.
- `START → choose_topic → build_outline → write_answer → END` 순서가 코드에 그대로 드러납니다.

## 실무에서 헷갈리는 지점

- 노드가 상태 전체를 다시 만들어야 하는 것은 아닙니다. 바뀐 필드만 반환해도 됩니다.
- `StateGraph`는 DAG만 만드는 도구가 아닙니다. 뒤 글에서 보겠지만 루프와 조건 분기도 자연스럽게 표현합니다.
- `invoke()`의 반환값은 마지막 노드 출력이 아니라 최종 상태 전체입니다.

## 체크리스트

- [ ] 상태 필드가 다음 노드에 정말 필요한 값만 담고 있는가
- [ ] 노드 이름만 봐도 흐름이 읽히는가
- [ ] `START`와 `END` 사이 경로가 불필요하게 우회하지 않는가

## 정리

이 단계에서는 "그래프를 만든다"보다 "상태가 어떤 순서로 변하는지 드러낸다"는 감각을 잡는 것이 중요합니다. 다음 글에서는 이 상태를 메모리에 저장하고 같은 `thread_id`로 다시 이어 붙이는 방법을 봅니다.

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

- [LangGraph 개념 문서](https://langchain-ai.github.io/langgraph/concepts/low_level/)
- [StateGraph API 레퍼런스](https://langchain-ai.github.io/langgraph/reference/graphs/)
- [LangGraph 시작 가이드](https://langchain-ai.github.io/langgraph/tutorials/introduction/)

Tags: LangGraph, Agent, Python, LLM
