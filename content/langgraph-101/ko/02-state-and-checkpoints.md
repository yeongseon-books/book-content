---
title: "LangGraph 101 (2/6): 상태 관리와 체크포인트"
series: langgraph-101
episode: 2
language: ko
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/72"
    published_at: '2026-05-12'
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- LangGraph
- Agent
- Python
- LLM
last_reviewed: '2026-05-14'
seo_description: 체크포인터로 그래프 상태를 저장하고 thread_id로 다시 이어 실행하는 방법을 정리합니다
---

# LangGraph 101 (2/6): 상태 관리와 체크포인트

에이전트가 한 번의 요청으로 끝날 때는 상태를 대충 넘겨도 크게 문제가 없을 수 있습니다. 하지만 워크플로가 두 번째 턴까지 살아남아야 하는 순간부터 상황이 완전히 달라집니다. 첫 번째 턴에서 사용자가 무엇을 말했는지, 어떤 도구 결과가 아직 유효한지, 지금이 몇 번째 응답인지가 모두 중요해지기 때문입니다.

이 글은 LangGraph 101 시리즈의 두 번째 글입니다. 여기서는 체크포인트를 대화형 편의 기능이 아니라, 같은 상태 타임라인을 다음 호출까지 이어 주는 저장 계층으로 읽습니다.

운영에서는 이 문제가 더 거칠게 드러납니다. 어떤 세션은 잘 이어지는데 프로세스가 한 번 재시작되자 맥락이 끊기고, 어떤 요청은 부분 실패 뒤 다시 돌렸더니 이미 비용을 낸 작업을 또 수행합니다. 체크포인트가 없는 장기 실행 에이전트는 실패 자체보다도, **실패 뒤에 질서 있게 복구할 수 없다는 점**이 더 위험한 경우가 많습니다.

특히 도구 호출과 멀티턴 대화가 붙기 시작하면 "마지막 사용자 메시지만 다시 보내면 되지 않을까?"라는 순진한 우회로가 얼마나 약한지 금방 드러납니다. 메시지 누적 규칙도 사라지고, turn counter도 사라지고, 요약 상태와 외부 도구 응답도 함께 사라집니다. 겉으로는 재시도처럼 보여도, 실제로는 이전 세션의 옷만 입은 새 실행이 되기 쉽습니다.

여기서는 체크포인트를 "대화를 기억하는 기능"이 아니라, **상태를 저장하고 같은 대화 타임라인 위에서 다시 실행을 잇게 만드는 런타임 계층**으로 이해해 보겠습니다. 핵심은 분명합니다. **State는 그래프의 단일 진실 공급원이고, Checkpoint는 그 진실을 호출 사이에 보존하는 장치**입니다.

이 관점이 잡히면 그래프의 모든 동작이 같은 언어로 설명됩니다. 조건부 엣지는 저장된 상태를 보고 다음 경로를 고르는 규칙이 되고, 도구 호출 루프는 같은 상태 타임라인 위에서 반복되는 전이 구조로 읽힙니다. 반대로 상태를 막연한 메모리 비유로만 이해하면, 왜 `thread_id`가 필요한지, 왜 병합 규칙을 필드마다 다르게 설계해야 하는지가 계속 흐릿하게 남습니다.

![thread_id를 통한 대화 재개 흐름](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/02/02-01-minimal-runnable-example.ko.png)
*thread_id를 통한 대화 재개 흐름*

> State는 현재 실행의 계약이고, checkpoint는 그 계약을 다음 호출에서 다시 이어 받게 만드는 저장 경계입니다.

## 이 글에서 다룰 문제

- LangGraph에서 state를 단일 진실 공급원으로 두면 어떤 버그를 줄일 수 있을까요?
- checkpoint는 메모리 저장과 무엇이 다르고, 언제 복구 경계가 될까요?
- MemorySaver 예제를 운영 코드로 착각하면 어떤 한계에 부딪힐까요?
- 메시지 누적 필드와 단순 갱신 필드를 같은 방식으로 다루면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 구조가 중요한가

체크포인트를 단순히 "대화형 기능을 위한 메모리"로만 이해하면 절반만 본 셈입니다. 더 중요한 이유는 실패 복구와 재현성입니다. 에이전트가 한 턴 안에서 끝나지 않고 다음 호출로 이어지는 순간, 상태 저장은 사용자 경험 문제이기도 하지만 동시에 **운영 안정성 문제**가 됩니다.

예를 들어 첫 번째 호출에서 사용자가 프로젝트 주제를 말했고, 두 번째 호출에서 "아까 내가 뭐라고 했지?"라고 물었다고 해 보겠습니다. 상태가 남아 있지 않다면 답변 품질이 떨어지는 정도로 끝날 수 있습니다. 하지만 실제 프로덕션에서는 여기에 도구 호출, 누적 메시지, 검토 단계, 외부 시스템 부작용이 함께 얽힙니다. 그러면 단순한 맥락 손실이 아니라 중복 실행, 잘못된 회복, 비용 폭증으로 이어질 수 있습니다.

저는 팀들이 checkpoint가 없을 때 자주 같은 실수를 반복하는 걸 봤습니다. 실패한 요청을 복구하려고 마지막 사용자 입력만 다시 보내고, "왜 이번에는 응답이 다르지?"를 뒤늦게 묻습니다. 그때 이미 빠져 버린 것은 단순한 문장 한 줄이 아닙니다. 이전 턴의 메시지 누적, branch 결정 근거, turn count, 일부 도구 결과까지 함께 사라져 있습니다.

그래서 이 글의 목표는 `MemorySaver` 사용법을 보여 주는 데 있지 않습니다. 더 중요한 목표는 **체크포인트를 붙이는 순간 그래프가 왜 단발 함수 호출에서 이어 실행 가능한 시스템으로 바뀌는지**를 이해하는 데 있습니다.

---

## State와 checkpoint의 책임 분리

체크포인트 주제에서 가장 먼저 잡아야 할 문장은 이것입니다. **State는 그래프의 단일 진실 공급원이고, Checkpoint는 그 진실을 보존하는 저장 계층**입니다. 저는 이 문장이 LangGraph의 영속성 모델을 가장 정확하게 설명한다고 생각합니다.

많은 입문자가 체크포인터를 "메모리를 넣는 옵션" 정도로 이해합니다. 하지만 운영 관점에서는 그보다 더 구체적으로 읽어야 합니다. 체크포인터는 상태 스냅샷을 저장하고, 같은 세션 식별자(`thread_id`)가 들어왔을 때 그 스냅샷을 다시 그래프에 공급합니다. 즉, 기억을 흉내 내는 마법이 아니라 **재개 가능한 실행 컨텍스트**를 만드는 장치입니다.

가장 단순하게 정리하면 아래 표처럼 볼 수 있습니다.

| 구성 요소 | 역할 | 실무에서 왜 중요한가 |
| --- | --- | --- |
| **State** | 현재까지의 메시지, 카운터, 누적 결과 같은 공유 데이터 | 어느 시점에 무엇이 남아 있어야 하는지 검증할 수 있습니다 |
| **Checkpoint** | 특정 시점의 State 스냅샷 | 실패 후 재개와 재현 가능한 디버깅의 출발점이 됩니다 |
| **thread_id** | 같은 대화 타임라인을 식별하는 키 | 서로 다른 사용자 세션이 섞이지 않도록 막습니다 |
| **merge rule** | 새 상태와 저장된 상태를 어떤 방식으로 합칠지 정하는 규칙 | 메시지 누적과 카운터 갱신을 같은 방식으로 다루지 않게 해 줍니다 |
| **get_state()** | 현재 저장된 상태를 직접 확인하는 진단 진입점 | "정말 저장됐는가?"를 코드로 확인할 수 있습니다 |

이 표가 중요한 이유는 운영 질문이 늘 여기서 나오기 때문입니다. 메시지가 왜 사라졌지? 왜 다른 사용자의 세션이 섞였지? 왜 retry 이후 turn count가 이상하지? 왜 같은 질문을 다시 보냈는데 도구 호출 횟수가 달라졌지? 이런 질문들은 모델 품질이 아니라 state, checkpoint, merge rule, session identity 문제인 경우가 많습니다.

---

## 상태 필드 분류: 누적 필드 vs 갱신 필드

체크포인트를 설계하기 전에 먼저 해야 할 일이 있습니다. 상태 필드를 **누적 필드**와 **갱신 필드**로 분류하는 것입니다. 이 두 종류의 필드는 병합(merge) 방식이 달라야 하기 때문입니다.

**누적 필드**: 새 값이 기존 값 위에 쌓여야 하는 필드입니다.

- 대화 메시지 리스트 (`messages`)
- 도구 호출 기록 (`tool_calls_history`)
- 에러 로그 (`errors`)

**갱신 필드**: 새 값이 기존 값을 교체해야 하는 필드입니다.

- 대화 턴 카운터 (`turn_count`)
- 현재 라우팅 결정 (`route`)
- 마지막 요약 (`last_summary`)

LangGraph에서 누적 필드는 `Annotated`와 병합 함수를 함께 지정해야 합니다. `add_messages`는 메시지 리스트를 위한 내장 병합 함수입니다.

```python
from typing import Annotated
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage

class ChatState(TypedDict):
    # 누적 필드: add_messages로 병합
    messages: Annotated[list[BaseMessage], add_messages]
    # 갱신 필드: 일반 TypedDict 필드
    turn_count: int
```

이 분류를 하지 않으면 어떤 일이 생길까요? 예를 들어 `messages`를 일반 필드로 선언하면, 두 번째 턴에서 새 메시지를 추가할 때 기존 메시지 전체가 덮어써집니다. 반대로 `turn_count`를 누적 필드로 선언하면 매번 카운터가 리스트로 쌓이는 이상한 동작이 생깁니다.

---

## 최소 실행 예제

가장 작은 재개 예제로 보겠습니다. 첫 번째 호출에서 사용자의 메시지를 저장하고, 두 번째 호출에서는 같은 `thread_id`를 사용해 이전 대화 상태를 이어 받습니다. 마지막에는 `get_state()`로 실제 저장값을 직접 확인합니다.

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


def assistant(state: ChatState) -> dict:
    """대화 이력을 참고해 응답을 생성하는 어시스턴트 노드"""
    human_messages = [
        msg.content
        for msg in state["messages"]
        if isinstance(msg, HumanMessage)
    ]
    latest = human_messages[-1]
    remembered = human_messages[:-1]

    if remembered:
        memory_line = f"이전 대화 내용: {', '.join(str(m) for m in remembered)}"
    else:
        memory_line = "이전 대화 기록이 없습니다."

    current_turn = state.get("turn_count", 0) + 1
    reply = AIMessage(
        content=(
            f"[턴 {current_turn}] 최신 요청: {latest}. {memory_line}"
        )
    )
    return {"messages": [reply], "turn_count": current_turn}


def build_graph():
    graph = StateGraph(ChatState)
    graph.add_node("assistant", assistant)
    graph.add_edge(START, "assistant")
    graph.add_edge("assistant", END)
    return graph.compile(checkpointer=MemorySaver())


if __name__ == "__main__":
    app = build_graph()
    config = {"configurable": {"thread_id": "session-001"}}

    # 첫 번째 턴
    first = app.invoke(
        {
            "messages": [HumanMessage(content="제 프로젝트는 LangGraph에 관한 것입니다.")],
            "turn_count": 0,
        },
        config=config,
    )
    print("=== 첫 번째 응답 ===")
    print(first["messages"][-1].content)

    # 두 번째 턴: thread_id 덕분에 이전 상태를 이어받음
    second = app.invoke(
        {"messages": [HumanMessage(content="제 프로젝트가 무엇에 관한 건지 기억하시나요?")]},
        config=config,
    )
    print("\n=== 두 번째 응답 (이전 상태 이어받음) ===")
    print(second["messages"][-1].content)

    # 저장된 상태 직접 확인
    snapshot = app.get_state(config)
    print(f"\n=== 체크포인트 검증 ===")
    print(f"저장된 메시지 수: {len(snapshot.values['messages'])}")
    print(f"저장된 turn_count: {snapshot.values['turn_count']}")
```

**예상 출력:**

```text
=== 첫 번째 응답 ===
[턴 1] 최신 요청: 제 프로젝트는 LangGraph에 관한 것입니다.. 이전 대화 기록이 없습니다.

=== 두 번째 응답 (이전 상태 이어받음) ===
[턴 2] 최신 요청: 제 프로젝트가 무엇에 관한 건지 기억하시나요?. 이전 대화 내용: 제 프로젝트는 LangGraph에 관한 것입니다.

=== 체크포인트 검증 ===
저장된 메시지 수: 4
저장된 turn_count: 2
```

이 예제는 단순하지만 운영에서 중요한 것을 세 가지 보여 줍니다. 첫째, `compile(checkpointer=MemorySaver())` 한 줄로 영속성 계층이 그래프 바깥이 아니라 그래프 구조 안에 붙습니다. 둘째, 두 번째 `invoke()`가 새 메시지만 받아도 같은 `thread_id` 덕분에 이전 상태를 이어서 실행할 수 있습니다. 셋째, `get_state()`를 통해 "정말 저장됐는가?"를 사람이 추측이 아니라 데이터로 확인할 수 있습니다.

---

## thread_id 설계 전략

`thread_id`는 가장 단순해 보이지만 운영에서 가장 많은 실수가 생기는 부분입니다. 잘못된 `thread_id` 전략이 만드는 문제는 크게 세 가지입니다.

**문제 1: 세션이 섞임**

여러 사용자가 동일한 `thread_id`를 공유하면 대화 내용이 뒤섞입니다.

```python
# 나쁜 예: 고정된 thread_id
config = {"configurable": {"thread_id": "chat"}}  # 모든 사용자가 같은 세션 공유

# 좋은 예: 사용자별 고유 thread_id
config = {"configurable": {"thread_id": f"user-{user_id}-session-{session_id}"}}
```

**문제 2: 대화가 연속되지 않음**

`thread_id`를 매 요청마다 새로 생성하면 체크포인트가 있어도 이전 대화를 이어받지 못합니다.

```python
# 나쁜 예: 매번 새로운 thread_id
import uuid
config = {"configurable": {"thread_id": str(uuid.uuid4())}}  # 요청마다 새 세션

# 좋은 예: 대화 단위로 일관된 thread_id 유지
# 대화 시작 시 ID를 생성하고, 같은 대화 동안 동일 ID 사용
conversation_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": conversation_id}}
```

**문제 3: TTL 없는 무제한 누적**

세션이 영구적으로 유지되면 오래된 메시지가 쌓여 토큰 비용이 증가합니다. 운영에서는 세션 만료 정책이 필요합니다.

```python
# thread_id에 타임스탬프를 포함해 자연스러운 만료 유도
from datetime import date
today = date.today().isoformat()  # "2026-05-14"
config = {"configurable": {"thread_id": f"user-{user_id}-{today}"}}
# 날짜가 바뀌면 자동으로 새 세션 시작
```

---

## 저장이 실제로 됐는지 로컬에서 검증하기

체크포인트 글에서 중요한 건 "코드가 실행됐다"가 아니라 "정말 저장됐는가"입니다. 그래서 두 번째 턴까지 실행한 뒤에는 답변 문장만 보지 말고, 저장된 상태가 기대한 필드를 포함하는지 바로 확인하는 편이 좋습니다.

```python
app = build_graph()
config = {"configurable": {"thread_id": "verification-test"}}

# 두 턴 실행
app.invoke(
    {
        "messages": [HumanMessage(content="제 프로젝트는 LangGraph에 관한 것입니다.")],
        "turn_count": 0,
    },
    config=config,
)
app.invoke(
    {"messages": [HumanMessage(content="제 프로젝트가 무엇에 관한 건지 기억하시나요?")]},
    config=config,
)

# 체크포인트 상태 검증
snapshot = app.get_state(config)

assert snapshot.values["turn_count"] == 2, \
    f"turn_count가 2여야 함, 실제: {snapshot.values['turn_count']}"

assert len(snapshot.values["messages"]) == 4, \
    f"메시지 4개여야 함 (HumanMessage 2 + AIMessage 2), 실제: {len(snapshot.values['messages'])}"

assert any(
    "LangGraph" in str(msg.content)
    for msg in snapshot.values["messages"]
), "LangGraph가 메시지에 포함되어 있어야 함"

print("모든 체크포인트 검증 통과")
print(f"저장된 상태: {snapshot.values}")
```

**예상 출력:**

```text
모든 체크포인트 검증 통과
저장된 상태: {
  'messages': [
    HumanMessage(content='제 프로젝트는 LangGraph에 관한 것입니다.'),
    AIMessage(content='[턴 1] 최신 요청: ...'),
    HumanMessage(content='제 프로젝트가 무엇에 관한 건지 기억하시나요?'),
    AIMessage(content='[턴 2] 최신 요청: ...')
  ],
  'turn_count': 2
}
```

이 검증이 중요한 이유는 checkpoint를 감성적 비유가 아니라 데이터 구조로 확인하게 해 주기 때문입니다. 저장된 메시지 수와 `turn_count`를 직접 보면, 무엇이 누적되고 무엇이 갱신되는지 곧바로 읽힙니다.

---

## 상태 타임라인 시각화

체크포인트가 어떻게 동작하는지 이해하기 위해 두 턴의 상태 타임라인을 텍스트로 그려 보겠습니다.

```text
=== 세션 시작 (thread_id: "session-001") ===

턴 1 실행:
  입력: {"messages": [HumanMessage("LangGraph 프로젝트")], "turn_count": 0}
  assistant 노드 실행
  체크포인트 저장:
    messages: [HumanMessage, AIMessage]
    turn_count: 1

턴 2 실행:
  입력: {"messages": [HumanMessage("기억하시나요?")]}
  체크포인트 로드 (thread_id 일치):
    messages: [HumanMessage, AIMessage]  <- 이전 상태
    turn_count: 1                         <- 이전 상태
  새 입력 병합:
    messages: [HumanMessage, AIMessage, HumanMessage("기억하시나요?")]
    turn_count: 1
  assistant 노드 실행
  체크포인트 저장:
    messages: [HumanMessage, AIMessage, HumanMessage, AIMessage]
    turn_count: 2
```

이 타임라인이 보여주는 핵심은 두 가지입니다. 첫째, 두 번째 턴의 입력에 `turn_count`가 없어도 체크포인트에서 자동으로 불러옵니다. 둘째, `messages`는 누적 필드이기 때문에 기존 메시지 위에 새 메시지가 쌓입니다.

---

## MemorySaver 예제에서 반드시 짚고 넘어갈 한계

입문 예제는 `MemorySaver`로 충분합니다. 하지만 운영에서는 이 예제가 보여 주는 한계를 같이 이해해야 합니다.

**한계 1: 프로세스를 재시작하면 메모리 저장소는 비어 있습니다**

`MemorySaver`는 Python 프로세스 메모리에 상태를 저장합니다. 서버가 재시작되거나 컨테이너가 교체되면 모든 세션 데이터가 사라집니다. 재시작 뒤에도 복구돼야 하는 서비스라면 영속 저장소가 필요합니다.

```python
# 운영에서는 영속 저장소 사용
# (실제 연결 설정은 환경에 따라 다름)
# from langgraph.checkpoint.postgres import PostgresSaver
# from langgraph.checkpoint.sqlite import SqliteSaver

# 로컬 개발용 SQLite 예시 (재시작 후에도 유지)
# checkpointer = SqliteSaver.from_conn_string("./checkpoints.db")
# app = graph.compile(checkpointer=checkpointer)
```

**한계 2: `thread_id`가 약하면 다른 세션이 섞입니다**

사용자 ID, 대화 ID, workflow ID 같은 경계를 어떻게 매핑할지 먼저 정하지 않으면 저장 계층이 있어도 복구가 불안정합니다. 특히 멀티 인스턴스 환경에서는 인스턴스별로 메모리가 분리되므로 `MemorySaver`는 동작 자체를 보장하지 못합니다.

**한계 3: 필드별 병합 전략이 같지 않습니다**

`messages`는 누적 필드지만 `turn_count`는 최신 값으로 갱신되는 필드입니다. 이 둘을 같은 방식으로 다루면 기억은 남는데 대화 규칙은 깨진 상태가 생깁니다.

그래서 checkpoint를 붙인 뒤에는 항상 두 가지를 같이 봐야 합니다. 첫째, 지금 저장된 값이 맞는가. 둘째, 이 저장 방식이 실제 운영 경계에서도 유지될 수 있는가. 전자는 `get_state()`로 바로 확인하고, 후자는 세션 키 설계와 저장소 선택에서 결정됩니다.

---

## 코드에서 먼저 볼 세 가지 포인트

처음부터 모든 라인을 해석하기보다, 아래 세 지점부터 잡는 편이 이해가 빠릅니다.

![메시지 누적과 turn_count 업데이트](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/02/02-02-what-to-notice-in-this-code.ko.png)
*메시지 누적과 turn_count 업데이트*

- `add_messages`는 새 메시지를 누적하고, 기존 대화 이력을 덮어쓰지 않도록 만듭니다.
- `graph.compile(checkpointer=MemorySaver())` 한 줄에서 지속성 계층을 붙입니다.
- 두 번째 `invoke()`는 새 메시지만 보내지만, 같은 `thread_id`가 이전 상태를 자동으로 복원합니다.

첫 번째 포인트는 메시지 병합 방식입니다. `messages`는 덮어쓰기보다 누적이 필요한 필드입니다. 그래서 `add_messages` 같은 병합 규칙이 중요합니다. 저는 현업에서 이런 필드를 일반 문자열처럼 다뤘다가, 재개는 되는데 이력은 사라지는 이상한 상태를 자주 봤습니다.

두 번째 포인트는 체크포인터 부착 위치입니다. `MemorySaver()`는 단순한 헬퍼가 아니라 그래프가 호출 사이에 상태를 유지하도록 만드는 런타임 계층입니다. 이 계층이 구조에 명시적으로 보이기 때문에, "이 그래프는 resumable한가?"라는 질문에 코드 수준에서 답할 수 있습니다.

세 번째 포인트는 세션 키입니다. 같은 `thread_id`를 주면 이전 상태가 이어집니다. 말은 단순하지만 운영에서는 이 키 설계가 아주 중요합니다. 키가 약하면 서로 다른 사용자 세션이 섞이고, 키가 너무 자주 바뀌면 아무 것도 이어지지 않습니다.

---

## 자주 하는 실수

체크포인트 입문에서 가장 많이 생기는 오해는 "저장된다면 다 해결됐다"는 기대입니다. 실제로는 저장 그 자체보다 **무엇이 어떻게 합쳐지고, 어떤 키 아래 보존되는가**가 더 중요합니다.

![체크포인터와 병합 규칙의 관계](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/02/02-03-where-engineers-get-confused.ko.png)
*체크포인터와 병합 규칙의 관계*

**실수 1: Stateless Replay 안티패턴**

체크포인트 없이 retry를 구현하면서 마지막 사용자 입력만 다시 보내는 방식입니다. 처음에는 단순하고 빠르게 보입니다. 하지만 실제로는 이전 메시지 누적, turn count, 도구 결과, branch 결정 근거가 모두 빠진 상태에서 "비슷한 요청"을 다시 돌리는 셈입니다. 겉으로는 복구처럼 보이지만, 실상은 전혀 다른 실행을 새로 시작하는 경우가 많습니다.

이 안티패턴이 production에서 왜 위험할까요? 첫째, 같은 세션처럼 보여도 실제로는 다른 상태 위에서 실행되므로 재현성이 무너집니다. 둘째, 외부 API 호출이나 도구 실행이 붙어 있으면 중복 작업과 비용이 생길 수 있습니다. 셋째, 부분 실패 뒤에 어디서부터 이어야 하는지 판단할 근거가 사라져서, 결국 "처음부터 다시"밖에 선택지가 남지 않습니다.

**실수 2: 누적 필드와 갱신 필드를 구분하지 않기**

메시지처럼 누적돼야 하는 필드는 상태 모델에서 명시적으로 설계해야 합니다. `messages`는 누적돼야 하지만 `turn_count`는 최신 값으로 갱신되면 됩니다. 둘을 같은 방식으로 처리하면 어떤 세션은 이력이 사라지고, 어떤 세션은 필요 없는 데이터가 과하게 쌓입니다.

**실수 3: MemorySaver를 운영 코드로 착각하기**

체크포인터가 있다고 해서 자동으로 모든 필드가 원하는 방식으로 합쳐지지는 않습니다. 또한 `thread_id` 전략이 약하면 서로 다른 사용자의 세션이 섞일 수 있습니다. 운영 환경에서는 영속 저장소와 명확한 세션 경계 정책이 반드시 필요합니다.

---

## 디버깅 전술: 체크포인트 상태 이력 조회

LangGraph는 `get_state_history()`를 통해 특정 스레드의 체크포인트 이력 전체를 조회할 수 있습니다. 이 기능은 "어느 턴에서 상태가 어떻게 바뀌었는가"를 추적하는 데 유용합니다.

```python
app = build_graph()
config = {"configurable": {"thread_id": "debug-session"}}

# 세 턴 실행
for i, message in enumerate([
    "첫 번째 메시지입니다.",
    "두 번째 메시지입니다.",
    "세 번째 메시지입니다.",
]):
    app.invoke(
        {"messages": [HumanMessage(content=message)], "turn_count": 0 if i == 0 else {}},
        config=config,
    )

# 체크포인트 이력 조회
print("=== 체크포인트 이력 ===")
for checkpoint in app.get_state_history(config):
    print(f"turn_count: {checkpoint.values.get('turn_count')}, "
          f"메시지 수: {len(checkpoint.values.get('messages', []))}")
```

**예상 출력:**

```text
=== 체크포인트 이력 ===
turn_count: 3, 메시지 수: 6
turn_count: 2, 메시지 수: 4
turn_count: 1, 메시지 수: 2
```

이 이력을 보면 각 턴에서 상태가 어떻게 변화했는지 시계열로 확인할 수 있습니다. 특정 시점의 상태로 돌아가서 다시 실행하는 "time travel" 기능도 이 이력을 기반으로 구현됩니다.

---

## 첫 번째 운영 체크리스트

체크포인트를 붙이는 순간부터 아래 항목은 기능 확인이 아니라 안정성 확인 항목이 됩니다.

- [ ] 세션 식별용 `thread_id` 규칙을 명확히 정했는가
- [ ] 누적 필드와 갱신 필드를 분리해서 모델링했는가
- [ ] 누적 필드에 `add_messages` 또는 커스텀 병합 함수를 지정했는가
- [ ] 재시도 시 어떤 상태를 재사용하고 어떤 값은 새로 계산할지 합의했는가
- [ ] 다음 턴 실행 뒤 `get_state()`로 실제 저장값을 확인했는가
- [ ] 프로세스 재시작 뒤에도 원하는 타임라인이 이어지는지 검증했는가
- [ ] `MemorySaver`를 영속 저장소로 교체할 시점과 기준을 팀에서 합의했는가

이 체크리스트의 핵심은 "기억되는가"가 아닙니다. "복구 가능한가, 설명 가능한가"입니다. 체크포인트는 편의 기능이 아니라 장애 대응 경계이기도 합니다.

---

## 실무에서는 이렇게 생각한다

체크포인터를 붙인 순간 그래프는 단발 호출 모음이 아니라 세션 시스템이 됩니다. 그래서 운영 질문도 달라집니다. "대답을 잘했나?"보다 먼저 "세션 키가 안정적인가?", "이 필드를 정말 저장해야 하나?", "time travel처럼 이전 상태를 다시 읽어야 할 때 어디를 기준점으로 삼을까?" 같은 질문이 붙기 시작합니다.

현업에서 저는 이 시점부터 checkpoint를 저장소 설계와 함께 봅니다. 메모리 기반 예제는 출발점으로 좋지만, 실제 서비스에서는 프로세스 재시작과 다중 인스턴스 환경을 고려해야 합니다. 결국 "상태를 어디에 두는가"는 성능과 비용 문제이기도 하지만, 동시에 어떤 수준의 복구를 약속할 수 있는가의 문제이기도 합니다.

또 하나 중요한 감각은 replay와 time travel을 구분하는 것입니다. replay는 같은 입력을 다시 돌리는 행위일 수 있지만, time travel은 저장된 특정 상태 지점에서 다시 시작하는 행위에 가깝습니다. 둘을 혼동하면 디버깅도, 실험도, 운영 복구도 모두 흐려집니다.

제가 본 강한 팀들은 프롬프트보다 상태 저장 전략을 먼저 리뷰했습니다. 이유는 단순합니다. 프롬프트는 바꾸기 쉬워도, 잘못 설계된 세션 경계와 병합 규칙은 나중에 전체 그래프를 흔들기 때문입니다. 이 글에서 꼭 가져가야 할 운영 감각도 여기 있습니다. **대화 품질 이전에 상태 복구 전략이 먼저 서야 장기 운영이 가능합니다.**

---

## 정리: 체크포인트는 기억 기능이 아니라, 재개 가능한 그래프를 만드는 계층이다

체크포인트를 처음 보면 "이전 대화를 기억하게 해 주는 기능"으로 이해하기 쉽습니다. 그 설명도 틀리진 않지만, 운영 관점에서는 너무 약합니다. 더 중요한 설명은 이렇습니다. 체크포인트는 그래프 상태를 저장하고, 같은 세션 식별자로 다시 불러와서, **실행을 이어 갈 수 있게 만드는 계층**입니다.

이 글에서 먼저 가져가야 할 핵심은 세 가지입니다. 첫째, State는 그래프의 단일 진실 공급원입니다. 둘째, Checkpoint는 그 State를 호출 사이에 보존합니다. 셋째, `thread_id`와 병합 규칙은 "기억이 된다/안 된다"를 넘어, 어떤 세션이 어떤 방식으로 복구되는지를 결정합니다.

이 관점이 중요한 이유는 다음 글의 조건부 엣지와 바로 이어지기 때문입니다. 분기는 결국 현재 상태를 보고 결정됩니다. 그런데 상태가 저장되지 않거나 잘못 합쳐진다면, 분기 품질도 함께 흔들릴 수밖에 없습니다. 체크포인트는 단순한 persistence 주제가 아니라 이후 라우팅 품질의 바탕이기도 합니다.

저는 checkpoint가 붙은 그래프를 볼 때 "이제 대화가 된다"보다 "이제 실패 후에도 설명 가능한가?"를 먼저 봅니다. 어느 턴에서 무엇이 저장됐는지, 어떤 키로 이어졌는지, 어떤 필드가 누적됐는지 말할 수 있다면 출발은 제대로 잡힌 셈입니다.

다음 글에서는 이렇게 저장된 상태를 바탕으로 어떤 노드가 다음에 실행될지 조건부 엣지로 결정해 보겠습니다. 이때 비로소 state와 checkpoint가 왜 분기 설계의 전제인지 더 선명하게 보일 것입니다.

---

## 운영 체크리스트

- [ ] `thread_id`를 사용자 세션 또는 대화 단위와 일관되게 매핑했다
- [ ] 저장이 필요한 필드와 저장하면 안 되는 필드를 구분했다
- [ ] replay와 time travel을 같은 개념으로 다루지 않도록 팀 용어를 정리했다
- [ ] 부분 실패 뒤 어디서부터 재개할지 기준점을 문서화했다
- [ ] `get_state()` 결과를 이용해 저장 상태를 실제로 점검하는 절차를 만들었다
- [ ] `get_state_history()`로 이력을 조회하는 디버깅 루틴을 갖추었다
- [ ] MemorySaver에서 영속 저장소로 마이그레이션할 시점과 방법을 계획했다

## 처음 질문으로 돌아가기

- **LangGraph에서 state를 단일 진실 공급원으로 두면 어떤 버그를 줄일 수 있을까요?**
  - 상태가 한곳에 모여 있으면 "이 값이 어디서 바뀌었는가"를 추적할 수 있습니다. 여러 곳에 상태가 흩어져 있으면 동기화 버그, 경쟁 조건, 예상치 못한 덮어쓰기가 생깁니다. 단일 진실 공급원은 이런 버그를 구조적으로 막아줍니다.

- **checkpoint는 메모리 저장과 무엇이 다르고, 언제 복구 경계가 될까요?**
  - 단순한 메모리 저장은 프로세스 생애 주기에 묶입니다. 체크포인트는 특정 시점의 전체 상태 스냅샷을 영속 저장소에 남겨서, 프로세스 재시작 후에도 같은 타임라인에서 재개할 수 있게 만듭니다. 복구 경계는 "마지막으로 성공한 체크포인트"가 됩니다.

- **MemorySaver 예제를 운영 코드로 착각하면 어떤 한계에 부딪힐까요?**
  - 프로세스가 재시작되면 모든 세션 데이터가 사라집니다. 멀티 인스턴스 환경에서는 같은 `thread_id`가 다른 인스턴스로 라우팅되면 이전 상태를 찾을 수 없습니다. 운영에서는 PostgreSQL, SQLite 같은 영속 저장소 기반 체크포인터가 필요합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LangGraph 101 (1/6): LangGraph 소개와 그래프 기초](./01-graph-basics.md)
- **LangGraph 101 (2/6): 상태 관리와 체크포인트 (현재 글)**
- [LangGraph 101 (3/6): 조건부 엣지와 분기 흐름](./03-conditional-edges.md)
- [LangGraph 101 (4/6): 도구 호출 에이전트](./04-tool-calling-agent.md)
- [LangGraph 101 (5/6): 멀티 에이전트 시스템](./05-multi-agent.md)
- [LangGraph 101 (6/6): LangGraph 완성](./06-langgraph-complete.md)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서
- [LangGraph persistence guide](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
- [MemorySaver reference](https://langchain-ai.github.io/langgraph/reference/checkpoints/)
- [Working with messages in graph state](https://langchain-ai.github.io/langgraph/concepts/low_level/#working-with-messages-in-graph-state)

### 소스 코드와 예제
- [LangGraph checkpoint package source](https://github.com/langchain-ai/langgraph/tree/main/libs/checkpoint)
- [LangGraph memory tutorial](https://langchain-ai.github.io/langgraph/tutorials/get-started/3-add-memory/)

### 관련 시리즈
- [LangGraph 소개와 그래프 기초](./01-graph-basics.md)
- [LangChain 101](../../langchain-101/ko/)

---

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/langgraph-101/ko/02-state-and-checkpoints)

Tags: LangGraph, Agent, Python, LLM
