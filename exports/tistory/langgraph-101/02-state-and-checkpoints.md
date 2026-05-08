
# 상태 관리와 체크포인트

> LangGraph 101 시리즈 (2/6)

<!-- a-grade-intro:begin -->

**핵심 질문**: *왜* *invoke* *한 번* 으로 *끝나면* *안* *되나요*?

> *대화* *시스템* 은 *이어서* *써야* *하기* *때문* 입니다. *체크포인터* 가 *상태* 를 *저장* 하고 *thread_id* 로 *복원* 합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *체크포인터* 가 *저장* 하는 *것*
- *MemorySaver* 와 *thread_id* *조합*
- *Annotated* 와 *add_messages* *누적*
- *get_state* 로 *스냅샷* *확인*
- *재개* 시 *입력* *최소화*

## 왜 중요한가

*에이전트* 를 *실서비스* 로 *옮기면* *한 턴* 으로 *끝나는* *호출* 은 *없습니다*. *멀티턴* *대화*, *human-in-the-loop*, *재시도* *모두* *상태* 를 *어딘가* 에 *저장* 해야 *합니다*. *LangGraph* 는 *이* *역할* 을 *체크포인터* 로 *분리* 합니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    U1["1st invoke"] --> G1[Graph]
    G1 --> CP[(MemorySaver)]
    U2["2nd invoke (same thread_id)"] --> G2[Graph]
    CP --> G2
    G2 --> R[Resumed reply]
```

## 핵심 용어 정리

- **checkpointer**: *각 노드* *실행* *후* *상태* 를 *스냅샷* 으로 *저장* 하는 *어댑터*.
- **MemorySaver**: *메모리* *기반* *체크포인터*. *프로토타입* 용.
- **thread_id**: *동일* *대화* *세션* 을 *식별* 하는 *키*.
- **add_messages**: *메시지 리스트* 를 *덮어쓰지* *않고* *누적* 하는 *reducer*.
- **get_state**: *현재* *thread* 의 *최신* *스냅샷* 을 *반환* 합니다.

## Before/After

**Before**: "*매 호출* 마다 *전체* *대화 히스토리* 를 *직접* *넘겨야* *합니다*."

**After**: "*같은* *thread_id* 만 *주면* *이전* *상태* 가 *자동* 으로 *복원* 됩니다."

## 실습: 대화 상태 저장 5단계

### 1단계 — 상태 타입 정의

```python
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    turn_count: int
```

### 2단계 — 어시스턴트 노드

```python
from langchain_core.messages import AIMessage, HumanMessage

def assistant(state: ChatState) -> dict:
    user_turns = [m.content for m in state["messages"] if isinstance(m, HumanMessage)]
    latest = user_turns[-1]
    earlier = ", ".join(user_turns[:-1]) or "none"
    reply = AIMessage(
        content=f"Turn {state.get('turn_count', 0) + 1}. Latest: {latest}. Earlier: {earlier}"
    )
    return {"messages": [reply], "turn_count": state.get("turn_count", 0) + 1}
```

### 3단계 — 체크포인터 붙여 컴파일

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

builder = StateGraph(ChatState)
builder.add_node("assistant", assistant)
builder.add_edge(START, "assistant")
builder.add_edge("assistant", END)

app = builder.compile(checkpointer=MemorySaver())
```

### 4단계 — 첫 invoke

```python
config = {"configurable": {"thread_id": "demo-1"}}

first = app.invoke(
    {"messages": [HumanMessage(content="My project is about LangGraph.")], "turn_count": 0},
    config=config,
)
print(first["messages"][-1].content)
```

### 5단계 — 재개 invoke와 스냅샷

```python
second = app.invoke(
    {"messages": [HumanMessage(content="What did I say my project was about?")]},
    config=config,
)
print(second["messages"][-1].content)

snapshot = app.get_state(config)
print(len(snapshot.values["messages"]), snapshot.values["turn_count"])
```

## 이 코드에서 주목할 점

- *두 번째* *invoke* 는 *과거* *메시지* 를 *다시* *넘기지* *않습니다*. *체크포인터* 가 *복원* 합니다.
- *add_messages* 가 *없었다면* *messages* *리스트* 가 *덮어써* *집니다*.
- *config* 의 *thread_id* 가 *세션* *경계* 입니다. *바꾸면* *대화* 가 *완전* 히 *분리* 됩니다.

## 자주 하는 실수 5가지

1. ***Annotated 누락*** — *messages* 가 *매번* *덮어써* *지면서* *대화* 가 *사라* *집니다*.
2. ***thread_id 공유*** — *서로* *다른* *사용자* 의 *상태* 가 *섞입니다*.
3. ***체크포인터 미지정*** — *compile()* 만 *하면* *상태* 가 *세션* *밖* 으로 *나가지* *못합니다*.
4. ***전체 히스토리 재전송*** — *재개* 시 *과거* *메시지* 를 *다시* *넣으면* *중복* 누적 됩니다.
5. ***MemorySaver 프로덕션 사용*** — *프로세스* *종료* 시 *전부* *소실* 됩니다. *DB* *기반* *체크포인터* 로 *교체* 합니다.

## 실무에서는 이렇게 쓰입니다

*프로덕션* 에서는 *MemorySaver* 대신 *PostgresSaver*, *RedisSaver* 같은 *영속* *체크포인터* 를 *씁니다*. *thread_id* 는 *대화 ID*, *세션 ID*, *사용자 ID + 채널* *조합* 등으로 *설계* 합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *체크포인터* 는 *기억 기능* 이 *아니라* *상태 저장소* 입니다.
- *thread_id* *설계* 가 *멀티테넌시* 의 *경계* 입니다.
- *누적* *필드* 와 *덮어쓰기* *필드* 를 *반드시* *구분* 합니다.
- *get_state* 는 *디버깅* *시* *가장* *먼저* *쓰는* *툴* 입니다.
- *영속 백엔드* 선택은 *처음* 부터 *고려* 합니다. *나중* 교체는 *마이그레이션* 이 *필요* 합니다.

## 체크리스트

- [ ] *Annotated[..., add_messages]* 적용.
- [ ] *compile(checkpointer=...)* 호출.
- [ ] *config* 에 *thread_id* 전달.
- [ ] *get_state* 로 *스냅샷* 확인.

## 연습 문제

1. *thread_id* 를 *바꿔* *invoke* 했을 때 *대화* 가 *분리* 되는지 *확인* 하세요.
2. *Annotated* 를 *제거* 하고 *messages* 가 *어떻게* *바뀌는지* *비교* 하세요.
3. *get_state_history* 로 *과거* *스냅샷* *목록* 을 *조회* 해 보세요.

## 정리 및 다음 단계

다음 글은 *조건부 엣지와 분기 흐름* 입니다.

## 시리즈 목차

- [LangGraph 소개와 그래프 기초](./01-graph-basics.md)
- **상태 관리와 체크포인트 (현재 글)**
- 조건부 엣지와 분기 흐름 (예정)
- 도구 호출 에이전트 (예정)
- 멀티 에이전트 시스템 (예정)
- LangGraph 완성 (예정)

## 참고 자료

- [LangGraph persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [Checkpointer reference](https://langchain-ai.github.io/langgraph/reference/checkpoints/)
- [MessagesState concepts](https://langchain-ai.github.io/langgraph/concepts/low_level/#messagesstate)
- [LangGraph how-tos](https://langchain-ai.github.io/langgraph/how-tos/)

Tags: LangGraph, Agent, Python, LLM

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
