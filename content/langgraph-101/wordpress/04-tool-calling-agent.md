---
title: "바이브코딩을 위한 LangGraph (4/6): 도구 호출 에이전트"
series: langgraph-101
episode: 4
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LangGraph
- Tool Calling
- Agent
- Python
---

# 바이브코딩을 위한 LangGraph (4/6): 도구 호출 에이전트

이 글은 **바이브코딩을 위한 LangGraph** 시리즈의 네 번째 글입니다. LangGraph로 LLM이 도구를 호출하고 결과를 처리하는 ReAct 스타일 에이전트를 구현합니다.

---

조건부 엣지로 분기 흐름을 만들었습니다. 이제 에이전트의 핵심인 도구 호출 루프를 구현해야 합니다. LLM이 "이 도구를 써야겠다"고 판단하면 도구를 실행하고, 결과를 다시 LLM에 전달해 다음 행동을 결정하는 사이클입니다.

바이브코딩으로 AI에게 "LangGraph 도구 에이전트 만들어줘"라고 하면 코드가 나옵니다. ToolNode가 무엇을 하는지, 도구 실행 결과가 어떻게 상태에 추가되는지 모르면 도구를 바꾸거나 추가하기 어렵습니다.

> "도구 호출 에이전트는 LLM이 언제 멈출지 스스로 결정합니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. ToolNode가 무엇을 하나요?
2. 도구 실행 결과가 메시지 상태에 어떻게 추가되나요?
3. 에이전트가 도구 호출 없이 응답하면 어떻게 되나요?
4. 여러 도구가 동시에 호출될 수 있나요?
5. 도구 실행 중 오류가 나면 에이전트에게 어떻게 전달하나요?

---

## ToolNode로 도구 실행

```python
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

@tool
def search_web(query: str) -> str:
    """웹에서 정보를 검색합니다."""
    return f"'{query}' 검색 결과: 관련 정보를 찾았습니다."

@tool
def calculate(expression: str) -> str:
    """수학 계산을 수행합니다."""
    return str(eval(expression))

tools = [search_web, calculate]
tool_node = ToolNode(tools)

llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)
```

## 에이전트 그래프

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

def agent_node(state: AgentState) -> AgentState:
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return "__end__"

graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")  # 도구 실행 후 에이전트로 복귀

app = graph.compile()
```

## 에이전트 실행

```python
from langchain_core.messages import HumanMessage

result = app.invoke({
    "messages": [HumanMessage(content="서울 날씨를 검색하고, 화씨로 변환해줘")]
})

for msg in result["messages"]:
    print(f"[{msg.type}]: {msg.content}")
```

---

## Before / After

| 항목 | Before (수동 루프) | After (LangGraph) |
|------|------------------|--------------------|
| 도구 실행 | 직접 if-else 분기 | ToolNode 자동 처리 |
| 루프 관리 | 수동 while 루프 | 그래프 조건부 엣지 |
| 다중 도구 | 순차 실행 | 동시 실행 지원 |
| 상태 추적 | 수동 | messages 자동 누적 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| tools → agent 엣지 없음 | 도구 실행 후 종료 | tools에서 agent로 복귀 엣지 |
| 메시지 누적 없음 | 도구 결과 유실 | Annotated[list, operator.add] |
| tool_node에 도구 미전달 | KeyError | ToolNode(tools) 생성 |
| should_continue 오류 | 무한 루프 | tool_calls 존재 여부 확인 |

---

## AI 활용 팁

```
LangGraph로 도구 호출 에이전트를 만들어줘.
agent 노드는 llm_with_tools로 LLM을 호출하고, tool_calls가 있으면 tools 노드로, 없으면 END로 분기해줘.
tools 노드는 ToolNode(tools)를 사용하고, 실행 후 agent 노드로 복귀해줘.
메시지는 Annotated[list, operator.add]로 누적해줘.
```

---

## 체크리스트

- [ ] @tool 데코레이터로 도구 정의
- [ ] ToolNode(tools) 생성
- [ ] llm.bind_tools(tools) 바인딩
- [ ] should_continue 라우팅 함수
- [ ] tools → agent 복귀 엣지
- [ ] messages Annotated 누적 설정

---

## 처음 질문으로 돌아가기

"LangGraph 도구 에이전트가 LangChain Tool Calling과 뭐가 다른가요?" — LangChain Tool Calling은 수동 루프를 직접 구현합니다. LangGraph는 그래프 구조로 루프를 선언적으로 정의하고, 체크포인트와 조건부 엣지가 자동으로 작동합니다. 복잡한 에이전트 로직을 그래프로 시각화할 수 있다는 것이 차이입니다.

---

## 정리

- ToolNode가 tool_calls를 읽어 자동으로 도구를 실행하고 ToolMessage를 추가한다
- tools → agent 엣지로 도구 실행 후 에이전트로 복귀한다
- should_continue가 tool_calls 존재 여부로 루프 지속/종료를 결정한다
- messages를 Annotated[list, operator.add]로 설정해야 누적된다

---

## 참고 자료

- [LangGraph 도구 에이전트 튜토리얼](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
- [ToolNode 문서](https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.tool_node.ToolNode)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- ToolNode로 도구 실행
- 에이전트 그래프
- 에이전트 실행
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LangGraph, Tool Calling, Agent, Python
