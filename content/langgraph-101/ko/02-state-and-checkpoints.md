---
title: 상태 관리와 체크포인트
series: langgraph-101
episode: 2
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
last_reviewed: '2026-05-11'
seo_description: 체크포인터로 그래프 상태를 저장하고 thread_id로 다시 이어 실행하는 방법을 정리합니다
---

# 상태 관리와 체크포인트

에이전트가 대화형으로 바뀌는 순간, 단발 호출만으로는 부족해집니다. 턴 사이에 상태를 저장해야 하고, 같은 세션 키로 다시 불러와야 하며, 실제로 무엇이 남았는지 검증도 해야 합니다. LangGraph에서는 이 역할을 체크포인터가 맡습니다.

이 글은 LangGraph 101 시리즈의 2번째 글입니다.

## 이 글에서 다룰 문제

- LangGraph의 체크포인터는 실제로 무엇을 저장할까요?
- `MemorySaver`와 `thread_id`를 쓰면 그래프는 어떻게 이전 대화를 이어 갈까요?
- 다음 턴이 끝난 뒤 복원된 상태를 어떻게 확인할 수 있을까요?

> 체크포인터는 그래프 상태의 스냅샷을 저장해 두었다가, 다음 호출이 같은 대화 타임라인에서 다시 시작하도록 만들어 주는 저장 계층입니다.

예제 코드: [github.com/yeongseon-books/langgraph-101](https://github.com/yeongseon-books/langgraph-101/tree/main/en/02-state-and-checkpoints)

![이 글에서 답할 질문](../../../assets/langgraph-101/02/02-01-questions-this-post-answers.ko.png)

이 글에서 답할 질문

## 최소 실행 예제

![thread_id를 통한 대화 재개 흐름](../../../assets/langgraph-101/02/02-01-minimal-runnable-example.ko.png)

thread_id를 통한 대화 재개 흐름

```python
from typing import Annotated

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    turn_count: int

def assistant(state: ChatState) -> ChatState:
    human_messages = [msg.content for msg in state["messages"] if isinstance(msg, HumanMessage)]
    latest = human_messages[-1]
    remembered = human_messages[:-1]
    memory_line = "No earlier user turns saved yet."
    if remembered:
        memory_line = f"Earlier user turns: {', '.join(remembered)}"
    reply = AIMessage(
        content=(
            f"Turn {state.get('turn_count', 0) + 1}. "
            f"Latest user message: {latest}. {memory_line}"
        )
    )
    return {"messages": [reply], "turn_count": state.get("turn_count", 0) + 1}

def build_graph():
    graph = StateGraph(ChatState)
    graph.add_node("assistant", assistant)
    graph.add_edge(START, "assistant")
    graph.add_edge("assistant", END)
    return graph.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    app = build_graph()
    config = {"configurable": {"thread_id": "memory-demo"}}

    first = app.invoke(
        {"messages": [HumanMessage(content="My project is about LangGraph.")], "turn_count": 0},
        config=config,
    )
    print("First reply:")
    print(first["messages"][-1].content)

    second = app.invoke(
        {"messages": [HumanMessage(content="What did I say my project was about?")]},
        config=config,
    )
    print("\nSecond reply after resume:")
    print(second["messages"][-1].content)

    snapshot = app.get_state(config)
    print(f"\nSaved message count: {len(snapshot.values['messages'])}")
    print(f"Saved turn count: {snapshot.values['turn_count']}")
```

실행 파일: `/root/Github/langgraph-101/en/02-state-and-checkpoints/main.py`

## 이 코드에서 먼저 봐야 할 점

![메시지 누적과 turn_count 업데이트](../../../assets/langgraph-101/02/02-02-what-to-notice-in-this-code.ko.png)

메시지 누적과 turn_count 업데이트

- `add_messages`는 새 메시지를 누적하고, 기존 대화 이력을 덮어쓰지 않도록 만듭니다.
- `graph.compile(checkpointer=MemorySaver())` 한 줄에서 지속성 계층을 붙입니다.
- 두 번째 `invoke()`는 새 메시지만 보내지만, 같은 `thread_id`가 이전 상태를 자동으로 복원합니다.

여기서 체크포인터를 단순한 메모리 기능으로 이해하면 나중에 운영에서 혼동이 생깁니다. 체크포인터는 기억처럼 보이는 동작을 만들어 주는 저장소입니다. 따라서 무엇을 누적할지, 무엇을 덮어쓸지, 어떤 키로 세션을 구분할지는 개발자가 설계해야 합니다.

## 어디서 자주 헷갈릴까요?

![체크포인터와 병합 규칙의 관계](../../../assets/langgraph-101/02/02-03-where-engineers-get-confused.ko.png)

체크포인터와 병합 규칙의 관계

- 체크포인터가 있다고 해서 자동으로 모든 필드가 원하는 방식으로 합쳐지지는 않습니다.
- `thread_id` 전략이 약하면 서로 다른 사용자의 세션이 섞일 수 있습니다.
- 메시지처럼 누적돼야 하는 필드는 상태 모델에서 명시적으로 설계해야 합니다.

실무에서는 이 지점이 특히 중요합니다. 예를 들어 `turn_count`는 덮어써도 되지만 `messages`는 누적돼야 합니다. 둘을 같은 방식으로 다루면 재개는 되는데 대화 이력이 사라지거나, 반대로 불필요한 데이터가 계속 쌓일 수 있습니다. 상태 필드마다 병합 규칙을 다르게 생각해야 하는 이유입니다.

## 체크리스트

- [ ] 세션 식별용 `thread_id` 규칙을 명확히 정했는가
- [ ] 누적 필드와 덮어쓰기 필드를 분리해서 모델링했는가
- [ ] 다음 턴 실행 뒤 `get_state()`로 실제 저장값을 확인했는가

## 정리

![여러 턴에 걸친 대화 재개 타임라인](../../../assets/langgraph-101/02/02-04-summary.ko.png)

여러 턴에 걸친 대화 재개 타임라인

체크포인터를 붙이는 순간 그래프는 일회성 함수 호출을 넘어서, 이어서 실행할 수 있는 대화 시스템이 됩니다. 다음 글에서는 이렇게 저장된 상태를 바탕으로 어떤 노드가 다음에 실행될지 조건부 엣지로 결정해 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [LangGraph 소개와 그래프 기초](./01-graph-basics.md)
- **상태 관리와 체크포인트 (현재 글)**
- 조건부 엣지와 분기 흐름 (예정)
- 도구 호출 에이전트 (예정)
- 멀티 에이전트 시스템 (예정)
- LangGraph 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangGraph persistence guide](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
- [MemorySaver reference](https://langchain-ai.github.io/langgraph/reference/checkpoints/)
- [Working with messages in graph state](https://langchain-ai.github.io/langgraph/concepts/low_level/#working-with-messages-in-graph-state)

Tags: LangGraph, Agent, Python, LLM
