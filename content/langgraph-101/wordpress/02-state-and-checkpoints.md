---
title: "바이브코딩을 위한 LangGraph (2/6): 상태 관리와 체크포인트"
series: langgraph-101
episode: 2
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LangGraph
- State
- Checkpoints
- Python
---

# 바이브코딩을 위한 LangGraph (2/6): 상태 관리와 체크포인트

이 글은 **바이브코딩을 위한 LangGraph** 시리즈의 두 번째 글입니다. LangGraph의 상태 관리와 체크포인트를 사용해 그래프 실행을 중단하고 재개하는 방법을 다룹니다.

---

그래프가 실행 중에 멈춰야 할 때가 있습니다. 사람의 승인을 기다리거나, 외부 이벤트를 기다리거나, 중간 결과를 저장해야 할 때입니다. LangGraph의 체크포인트는 그래프 상태를 스냅샷으로 저장하고 나중에 이어서 실행할 수 있게 합니다.

바이브코딩으로 AI에게 "LangGraph 체크포인트 써줘"라고 하면 코드가 나옵니다. MemorySaver와 SqliteSaver의 차이, thread_id가 왜 필요한지 모르면 재개 시 엉뚱한 상태에서 시작합니다.

> "체크포인트는 그래프의 타임머신입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 체크포인트 없이 그래프를 재개하면 어떻게 되나요?
2. MemorySaver와 SqliteSaver의 차이가 무엇인가요?
3. thread_id가 왜 필요한가요?
4. interrupt_before로 어떤 노드에서든 멈출 수 있나요?
5. 체크포인트에서 과거 상태를 조회하는 방법이 있나요?

---

## MemorySaver로 체크포인트

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    messages: list
    approved: bool

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)
```

## thread_id로 실행 재개

```python
config = {"configurable": {"thread_id": "session_001"}}

# 첫 실행
result1 = app.invoke({"messages": ["안녕"], "approved": False}, config=config)

# 같은 thread_id로 재개 (이전 상태에서 이어서)
result2 = app.invoke({"messages": ["계속해줘"], "approved": True}, config=config)
```

## 승인 대기(interrupt_before)

```python
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["approval_node"],  # 이 노드 실행 전 중단
)

# 1단계: 분석 실행 → approval_node 전에 중단
state = app.invoke(inputs, config=config)

# 2단계: 사람 검토 후 재개
state["approved"] = True
final = app.invoke(None, config=config)  # None = 현재 상태에서 재개
```

## SqliteSaver로 영속화

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# 재시작 후에도 상태 유지
with SqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
    app = graph.compile(checkpointer=checkpointer)
    result = app.invoke(inputs, config=config)
```

## 과거 상태 조회

```python
# 특정 thread의 체크포인트 히스토리
for state in app.get_state_history(config):
    print(state.values, state.created_at)
```

---

## Before / After

| 항목 | Before (체크포인트 없음) | After (체크포인트) |
|------|------------------------|------------------|
| 중간 저장 | 없음 | 노드별 자동 스냅샷 |
| 재개 | 처음부터 | thread_id로 이어서 |
| 사람 개입 | 불가 | interrupt_before |
| 과거 상태 | 없음 | get_state_history |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| thread_id 없음 | 상태 격리 실패 | config에 thread_id 필수 |
| MemorySaver in production | 재시작 시 소실 | SqliteSaver 또는 Redis |
| interrupt 후 재개 시 inputs | 상태 덮어쓰기 | None으로 재개 |
| 과거 상태 조회 없음 | 디버깅 어려움 | get_state_history 활용 |

---

## AI 활용 팁

```
LangGraph 그래프에 MemorySaver 체크포인트를 추가해줘.
approval_node 실행 전에 interrupt_before로 멈추고, 사람 확인 후 None으로 재개해줘.
thread_id를 config에 항상 포함하고, 프로덕션용으로 SqliteSaver도 설정해줘.
```

---

## 체크리스트

- [ ] MemorySaver 또는 SqliteSaver 선택
- [ ] graph.compile(checkpointer=checkpointer) 적용
- [ ] config에 thread_id 설정
- [ ] interrupt_before 노드 설정
- [ ] None 입력으로 재개 테스트
- [ ] get_state_history로 히스토리 확인

---

## 처음 질문으로 돌아가기

"그래프가 중간에 멈추면 처음부터 다시 해야 하나요?" — 체크포인트가 있으면 thread_id로 중단 지점부터 재개할 수 있습니다. 사람의 승인이 필요한 지점에 interrupt_before를 설정하고, 승인 후 None을 입력하면 이어서 실행됩니다.

---

## 정리

- checkpointer로 모든 노드 실행 후 상태를 자동 저장한다
- thread_id로 동일 세션의 상태를 격리하고 재개한다
- interrupt_before로 특정 노드 전에 그래프를 중단한다
- 프로덕션에서는 MemorySaver 대신 SqliteSaver를 사용한다

---

## 참고 자료

- [LangGraph 체크포인트 문서](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [Human-in-the-loop](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- MemorySaver로 체크포인트
- thread_id로 실행 재개
- 승인 대기
- SqliteSaver로 영속화
- 과거 상태 조회
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LangGraph, State, Checkpoints, Python
