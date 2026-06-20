---
title: "바이브코딩을 위한 LangGraph (6/6): LangGraph 완성"
series: langgraph-101
episode: 6
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LangGraph
- Agent
- Production
- Python
---

# 바이브코딩을 위한 LangGraph (6/6): LangGraph 완성

이 글은 **바이브코딩을 위한 LangGraph** 시리즈의 마지막 글입니다. 그래프 기초, 체크포인트, 조건부 엣지, 도구 에이전트, 멀티 에이전트를 하나의 프로덕션 수준 시스템으로 통합합니다.

---

LangGraph의 모든 개념을 배웠습니다. StateGraph, 체크포인트, 조건부 엣지, ToolNode, 멀티 에이전트 — 이제 이것들을 실제로 운영할 수 있는 시스템으로 조립해야 합니다. "다 연결하면 되지 않나요?"라고 생각하지만, 프로덕션에서는 오류 복구, 타임아웃, 스트리밍, FastAPI 통합이 모두 필요합니다.

이 글에서는 체크포인트, 도구 에이전트, 스트리밍, FastAPI 통합이 모두 포함된 완전한 LangGraph 애플리케이션을 구성합니다.

> "프로덕션 LangGraph는 기능이 아니라 복구 가능성이 완성 기준입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 체크포인트와 FastAPI를 어떻게 통합하나요?
2. LangGraph 그래프를 FastAPI 엔드포인트로 노출하는 방법이 있나요?
3. 스트리밍과 체크포인트를 동시에 사용할 수 있나요?
4. 그래프 실행 중 타임아웃을 어떻게 설정하나요?
5. LangGraph Studio 없이 그래프를 시각화하는 방법이 있나요?

---

## 완전한 에이전트 구성

```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage
from typing import TypedDict, Annotated
import operator

@tool
def search(query: str) -> str:
    """정보를 검색합니다."""
    return f"검색 결과: {query}에 대한 정보를 찾았습니다."

tools = [search]
llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)
llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)

class State(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

def agent(state: State) -> State:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def should_continue(state: State):
    if state["messages"][-1].tool_calls:
        return "tools"
    return "__end__"

graph = StateGraph(State)
graph.add_node("agent", agent)
graph.add_node("tools", tool_node)
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)
```

## FastAPI 통합

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

fastapi_app = FastAPI()

class ChatRequest(BaseModel):
    session_id: str
    message: str

@fastapi_app.post("/agent/chat")
async def agent_chat(request: ChatRequest):
    config = {"configurable": {"thread_id": request.session_id}}

    async def generate():
        async for chunk in app.astream(
            {"messages": [HumanMessage(content=request.message)]},
            config=config,
            stream_mode="messages",
        ):
            if chunk[1].get("langgraph_node") == "agent":
                msg = chunk[0]
                if hasattr(msg, "content") and msg.content:
                    yield msg.content

    return StreamingResponse(generate(), media_type="text/plain")

@fastapi_app.get("/agent/history/{session_id}")
def get_history(session_id: str):
    config = {"configurable": {"thread_id": session_id}}
    state = app.get_state(config)
    return {"messages": [m.dict() for m in state.values.get("messages", [])]}
```

## 그래프 시각화

```python
# PNG로 저장 (graphviz 필요)
try:
    image_data = app.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(image_data)
except Exception:
    # Mermaid 텍스트로 대체
    print(app.get_graph().draw_mermaid())
```

---

## Before / After

| 항목 | Before (기본 에이전트) | After (프로덕션 에이전트) |
|------|----------------------|--------------------------|
| 세션 유지 | 없음 | thread_id 체크포인트 |
| API 노출 | 없음 | FastAPI 엔드포인트 |
| 스트리밍 | 없음 | astream + StreamingResponse |
| 히스토리 조회 | 없음 | get_state + /history |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 동기 app.stream in FastAPI | 블로킹 | app.astream 사용 |
| thread_id 없음 | 세션 혼합 | config에 thread_id 필수 |
| stream_mode 없음 | 전체 상태 반환 | "messages" 모드 지정 |
| 그래프 시각화 오류 | graphviz 미설치 | draw_mermaid() 대체 |

---

## AI 활용 팁

```
LangGraph 도구 에이전트를 FastAPI로 노출해줘.
체크포인트로 세션별 대화 기록을 유지하고, /chat 엔드포인트는 스트리밍으로 응답해줘.
/history/{session_id} 엔드포인트로 대화 기록을 조회할 수 있게 해줘.
그래프 구조를 Mermaid 텍스트로 출력하는 코드도 포함해줘.
```

---

## 체크리스트

- [ ] 완전한 도구 에이전트 그래프 구성
- [ ] MemorySaver 체크포인트 통합
- [ ] FastAPI /chat 스트리밍 엔드포인트
- [ ] FastAPI /history 조회 엔드포인트
- [ ] astream stream_mode="messages" 설정
- [ ] 그래프 Mermaid 시각화

---

## 처음 질문으로 돌아가기

"LangGraph 에이전트를 실제 서비스로 만들려면 무엇이 더 필요한가요?" — 체크포인트로 세션을 유지하고, FastAPI로 API를 노출하고, astream으로 스트리밍 응답을 제공하면 사용자가 체감하는 서비스가 됩니다. 그래프 시각화로 흐름을 확인하고 팀과 공유하세요.

---

## 정리

- MemorySaver + thread_id로 세션별 대화를 영속화한다
- FastAPI + astream으로 실시간 스트리밍 API를 제공한다
- get_state()로 대화 히스토리를 조회한다
- draw_mermaid()로 그래프 구조를 시각화해 팀과 공유한다

---

## 참고 자료

- [LangGraph FastAPI 통합](https://langchain-ai.github.io/langgraph/how-tos/streaming-from-final-node/)
- [LangGraph Studio](https://langchain-ai.github.io/langgraph/concepts/langgraph_studio/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 완전한 에이전트 구성
- FastAPI 통합
- 그래프 시각화
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LangGraph, Agent, Production, Python
