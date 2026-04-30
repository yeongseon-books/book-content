# 상태 관리와 체크포인트

> LangGraph 101 (2/6)

대화형 에이전트는 이전 대화를 기억해야 합니다. LangGraph의 체크포인터는 각 스텝 후 상태를 저장해 대화 기록을 자동으로 관리합니다. 이 포스트에서는 메모리 체크포인터와 SQLite 체크포인터를 사용해 대화 지속성을 구현합니다.

---

## 체크포인트 작동 방식

체크포인터 없는 그래프는 매 호출이 독립적입니다. 체크포인터를 붙이면 `thread_id`로 구분된 대화 세션이 생기고, 같은 `thread_id`로 호출하면 이전 상태에서 이어집니다.

```
호출 1: [질문1] → 노드 실행 → 상태 저장 (thread_id="session_1")
호출 2: 상태 복원 (thread_id="session_1") → [질문1, 답변1, 질문2] → 노드 실행 → 상태 저장
```

---

## 메모리 체크포인터 (개발용)

```python
import os
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

class ConversationState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

SYSTEM_PROMPT = """당신은 파이썬 튜터입니다. 
이전 대화 내용을 기억하고 맥락에 맞게 답변하세요."""

def chat_node(state: ConversationState) -> ConversationState:
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.0,
    )
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

def build_chat_graph(checkpointer=None):
    graph = StateGraph(ConversationState)
    graph.add_node("chat", chat_node)
    graph.set_entry_point("chat")
    graph.add_edge("chat", END)
    return graph.compile(checkpointer=checkpointer)

def demo_memory_checkpointer():
    checkpointer = MemorySaver()
    app = build_chat_graph(checkpointer)
    config = {"configurable": {"thread_id": "session_1"}}

    turns = [
        "파이썬 데코레이터가 무엇인지 설명해 주세요.",
        "방금 설명한 개념을 실제 예시 코드로 보여 주세요.",
        "그 코드에서 functools.wraps는 왜 쓰나요?",
    ]

    for user_msg in turns:
        print(f"\n사용자: {user_msg}")
        result = app.invoke(
            {"messages": [HumanMessage(content=user_msg)]},
            config=config,
        )
        print(f"AI: {result['messages'][-1].content[:200]}...")

if __name__ == "__main__":
    demo_memory_checkpointer()
```

---

## SQLite 체크포인터 (프로덕션용)

메모리 체크포인터는 프로세스가 재시작되면 사라집니다. SQLite 체크포인터는 대화를 파일에 영구 저장합니다.

```python
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

def build_persistent_chat_app(db_path: str = "conversations.db"):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    return build_chat_graph(checkpointer)

def demo_sqlite_checkpointer():
    app = build_persistent_chat_app()
    config = {"configurable": {"thread_id": "persistent_session_1"}}

    # 첫 번째 호출
    result = app.invoke(
        {"messages": [HumanMessage(content="파이썬 GIL이란 무엇인가요?")]},
        config=config,
    )
    print(f"1차 답변: {result['messages'][-1].content[:200]}...")

    # 프로세스 재시작을 시뮬레이션: 같은 thread_id로 이어서 호출
    result = app.invoke(
        {"messages": [HumanMessage(content="방금 설명한 GIL이 멀티스레딩에 어떤 영향을 주나요?")]},
        config=config,
    )
    print(f"\n2차 답변 (이전 맥락 유지): {result['messages'][-1].content[:200]}...")

    # 상태 확인
    state = app.get_state(config)
    print(f"\n저장된 메시지 수: {len(state.values['messages'])}")
```

---

## 상태 검사와 수정

```python
def inspect_and_modify_state():
    checkpointer = MemorySaver()
    app = build_chat_graph(checkpointer)
    config = {"configurable": {"thread_id": "debug_session"}}

    # 초기 대화
    app.invoke(
        {"messages": [HumanMessage(content="안녕하세요!")]},
        config=config,
    )

    # 현재 상태 조회
    state = app.get_state(config)
    print("현재 메시지 수:", len(state.values["messages"]))
    for msg in state.values["messages"]:
        role = "사용자" if isinstance(msg, HumanMessage) else "AI"
        print(f"  [{role}]: {msg.content[:80]}...")

    # 상태 히스토리 조회
    print("\n상태 히스토리:")
    for snapshot in app.get_state_history(config):
        print(f"  스텝 {snapshot.config['configurable'].get('checkpoint_id', 'N/A')[:8]}: "
              f"메시지 {len(snapshot.values.get('messages', []))}개")

if __name__ == "__main__":
    demo_memory_checkpointer()
    demo_sqlite_checkpointer()
    inspect_and_modify_state()
```

---

## thread_id 설계 가이드

`thread_id`는 대화 세션의 식별자입니다. 실제 서비스에서는 사용자 ID와 세션 ID를 결합해 유일성을 보장합니다.

```python
def make_thread_id(user_id: str, session_id: str) -> str:
    return f"{user_id}:{session_id}"

# 같은 사용자의 새 대화 세션
import uuid
new_session = make_thread_id("user_123", str(uuid.uuid4()))
```

메모리 체크포인터는 개발과 테스트에만 씁니다. 프로덕션에서는 SQLite(단일 서버)나 Redis/PostgreSQL(분산 환경) 체크포인터를 사용합니다. 체크포인터를 바꿔도 그래프 코드는 전혀 수정할 필요가 없습니다.

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

- [LangGraph 체크포인터 문서](https://langchain-ai.github.io/langgraph/reference/checkpoints/)
- [LangGraph 퍼시스턴스 가이드](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
- [SqliteSaver API](https://langchain-ai.github.io/langgraph/reference/checkpoints/#langgraph.checkpoint.sqlite.SqliteSaver)

Tags: LangGraph, Agent, Python, LLM
