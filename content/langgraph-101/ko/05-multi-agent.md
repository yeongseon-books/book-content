# 멀티 에이전트 시스템

> LangGraph 101 (5/6)

복잡한 작업은 여러 전문 에이전트가 협력해 처리합니다. 한 에이전트가 전체를 조율하고, 나머지는 각자의 역할에 집중합니다. 이 포스트에서는 감독자-작업자 패턴으로 멀티 에이전트 시스템을 구현합니다.

---

## 감독자-작업자 패턴

감독자(Supervisor)가 작업을 분석해 적절한 작업자(Worker) 에이전트에 위임하고, 결과를 통합해 최종 답변을 생성합니다.

```
사용자 → [감독자] → [연구 에이전트] → 결과
                  → [코드 에이전트] → 결과
                  → [요약 에이전트] → 최종 답변
```

---

## 에이전트 구현

```python
import os
from typing import TypedDict, Annotated, Literal

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq

# ── 공유 상태 ──────────────────────────────────────────────────────────────
class MultiAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    task_type: str          # 작업 유형: research, code, summary
    research_result: str    # 연구 에이전트 결과
    code_result: str        # 코드 에이전트 결과
    final_answer: str       # 최종 답변

def _llm(temperature: float = 0.0) -> ChatGroq:
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=temperature,
    )

# ── 감독자 에이전트 ────────────────────────────────────────────────────────
def supervisor_node(state: MultiAgentState) -> MultiAgentState:
    """사용자 요청을 분석해 작업 유형을 결정합니다."""
    last_msg = state["messages"][-1].content
    response = _llm().invoke([
        SystemMessage(content="""사용자 요청을 분석해 작업 유형을 결정하세요.

- research: 정보 수집, 개념 설명, 사실 확인이 필요한 경우
- code: 코드 작성, 디버깅, 코드 설명이 필요한 경우  
- summary: 정보를 요약하거나 정리가 필요한 경우

반드시 research, code, summary 중 하나만 반환하세요."""),
        HumanMessage(content=last_msg),
    ])
    task_type = response.content.strip().lower()
    if task_type not in ("research", "code", "summary"):
        task_type = "research"
    return {"task_type": task_type}

# ── 연구 에이전트 ──────────────────────────────────────────────────────────
def research_agent_node(state: MultiAgentState) -> MultiAgentState:
    """개념 설명과 정보 수집을 담당합니다."""
    last_msg = state["messages"][-1].content
    response = _llm().invoke([
        SystemMessage(content="""당신은 연구 전문가입니다.
다음 질문에 대해 정확하고 상세한 정보를 제공하세요.
출처와 핵심 포인트를 명확히 하세요."""),
        HumanMessage(content=last_msg),
    ])
    return {
        "research_result": response.content,
        "messages": [AIMessage(content=f"[연구 에이전트] {response.content}")],
    }

# ── 코드 에이전트 ──────────────────────────────────────────────────────────
def code_agent_node(state: MultiAgentState) -> MultiAgentState:
    """코드 작성과 설명을 담당합니다."""
    last_msg = state["messages"][-1].content
    response = _llm(temperature=0.0).invoke([
        SystemMessage(content="""당신은 시니어 파이썬 개발자입니다.
명확하고 실용적인 코드를 작성하세요.
코드 블록과 함께 설명을 제공하세요.
타입 힌트와 docstring을 포함하세요."""),
        HumanMessage(content=last_msg),
    ])
    return {
        "code_result": response.content,
        "messages": [AIMessage(content=f"[코드 에이전트] {response.content}")],
    }

# ── 요약 에이전트 ──────────────────────────────────────────────────────────
def summary_agent_node(state: MultiAgentState) -> MultiAgentState:
    """정보를 통합하고 최종 답변을 생성합니다."""
    context_parts = []
    if state.get("research_result"):
        context_parts.append(f"연구 결과:\n{state['research_result']}")
    if state.get("code_result"):
        context_parts.append(f"코드 결과:\n{state['code_result']}")

    context = "\n\n".join(context_parts) if context_parts else state["messages"][-1].content

    response = _llm().invoke([
        SystemMessage(content="""다음 정보를 바탕으로 사용자에게 최종 답변을 작성하세요.
명확하고 구조적으로 정리하세요."""),
        HumanMessage(content=f"원래 질문: {state['messages'][0].content}\n\n{context}"),
    ])
    return {
        "final_answer": response.content,
        "messages": [AIMessage(content=response.content)],
    }

# ── 라우팅 ────────────────────────────────────────────────────────────────
def route_by_task_type(state: MultiAgentState) -> Literal["research", "code", "summary"]:
    return state["task_type"]

def after_agent(state: MultiAgentState) -> Literal["summary", "end"]:
    """연구 또는 코드 에이전트 후 요약 에이전트로 이동."""
    return "summary"

# ── 그래프 조립 ───────────────────────────────────────────────────────────
def build_multi_agent_graph():
    graph = StateGraph(MultiAgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("research", research_agent_node)
    graph.add_node("code", code_agent_node)
    graph.add_node("summary", summary_agent_node)

    graph.set_entry_point("supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_by_task_type,
        {
            "research": "research",
            "code": "code",
            "summary": "summary",
        },
    )
    graph.add_edge("research", "summary")
    graph.add_edge("code", "summary")
    graph.add_edge("summary", END)

    return graph.compile()

if __name__ == "__main__":
    app = build_multi_agent_graph()

    initial_state: MultiAgentState = {
        "messages": [],
        "task_type": "",
        "research_result": "",
        "code_result": "",
        "final_answer": "",
    }

    questions = [
        "파이썬 비동기 프로그래밍이란 무엇인가요?",
        "파이썬으로 피보나치 수열을 구현해 주세요.",
    ]

    for q in questions:
        state = {**initial_state, "messages": [HumanMessage(content=q)]}
        result = app.invoke(state)
        print(f"\n질문: {q}")
        print(f"작업 유형: {result['task_type']}")
        print(f"최종 답변:\n{result['final_answer'][:300]}...")
```

---

## 에이전트 간 통신 패턴

멀티 에이전트 시스템에서 에이전트 간 통신은 공유 상태를 통해 이루어집니다. 각 에이전트가 상태에 결과를 쓰고, 다음 에이전트가 그 결과를 읽습니다.

이 패턴의 장점은 에이전트 간 결합도가 낮다는 것입니다. 코드 에이전트가 어떻게 구현됐는지 요약 에이전트는 알 필요가 없습니다. 공유 상태의 `code_result` 필드만 읽으면 됩니다. 에이전트 교체가 쉽고, 새 에이전트를 추가할 때 기존 에이전트를 수정할 필요가 없습니다.

<!-- toc:begin -->
## 시리즈 목차

- [LangGraph 소개와 그래프 기초](./01-graph-basics.md)
- [상태 관리와 체크포인트](./02-state-and-checkpoints.md)
- [조건부 엣지와 분기 흐름](./03-conditional-edges.md)
- [도구 호출 에이전트](./04-tool-calling-agent.md)
- **멀티 에이전트 시스템 (현재 글)**
- LangGraph 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangGraph 멀티 에이전트 문서](https://langchain-ai.github.io/langgraph/how-tos/multi-agent-network/)
- [LangGraph 감독자 패턴](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/)
- [LangGraph 에이전트 네트워크](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)

Tags: LangGraph, Agent, Python, LLM
