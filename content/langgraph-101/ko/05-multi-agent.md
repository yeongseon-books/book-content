---
title: "LangGraph 101 (5/6): 멀티 에이전트 시스템"
series: langgraph-101
episode: 5
language: ko
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/75"
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
last_reviewed: '2026-05-11'
seo_description: supervisor와 worker 패턴으로 책임을 분리하는 멀티 에이전트 그래프 구성을 정리합니다
---

# LangGraph 101 (5/6): 멀티 에이전트 시스템

복잡한 요청을 하나의 에이전트에 계속 밀어 넣다 보면 처음에는 편해 보입니다. 프롬프트 하나, 모델 하나, 응답 하나면 되기 때문입니다. 그런데 요청이 길어지고 역할이 늘어나는 순간부터 문제가 드러납니다. 코드 작성도 해야 하고, 개념 설명도 해야 하고, 실패 분석도 해야 하는데, 이 모든 걸 한 프롬프트 안에 넣어 두면 역할 경계가 금방 흐려집니다.

운영에서는 이 혼선이 더 직접적으로 보입니다. 어떤 요청은 supervisor가 했어야 할 판단을 worker가 대신하고, 어떤 worker는 자신이 만든 결과를 다시 분류하기 시작하고, 어떤 시스템은 agent끼리 서로에게 넘기기만 하다가 비용만 쌓입니다. 현업에서 저는 이 상태를 "모델을 더 좋은 걸로 바꾸면 낫지 않을까?"라는 질문으로 덮는 팀을 자주 봤습니다. 하지만 실제 원인은 모델보다 **역할 분리와 위임 구조가 코드에 얼마나 명시적인가**에 있는 경우가 많습니다.

특히 supervisor가 없는 멀티 에이전트 구조는 생각보다 빨리 혼란스러워집니다. 누가 최종 결정을 하는지, 누가 어떤 worker를 호출하는지, 실패 시 어디서 멈춰야 하는지가 분명하지 않기 때문입니다. 겉으로는 여러 agent가 협력하는 것처럼 보여도, 안쪽에서는 하나의 거대한 프롬프트가 조각난 채 서로를 다시 호출하는 구조가 되기 쉽습니다.

이 글은 LangGraph 101 시리즈의 다섯 번째 글입니다. 여기서는 멀티 에이전트를 "LLM 호출을 여러 번 하는 패턴"이 아니라, **책임이 분리된 노드 클러스터를 supervisor가 조율하는 그래프 구조**로 이해해 보겠습니다. 한 가지 관점이 중요합니다. **Multi-agent는 모델 수의 문제가 아니라, 역할·위임·상태 계약을 어떻게 분리하느냐의 문제**라는 사실입니다.

![supervisor가 worker에게 위임하는 구조](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/05/05-01-minimal-runnable-example.ko.png)
*supervisor가 worker에게 위임하는 구조*

> Multi-agent의 품질은 에이전트 수가 아니라, 각 노드가 맡은 책임과 넘겨주는 state가 얼마나 분명한지에서 갈립니다.

## 이 글에서 다룰 문제

- 멀티 에이전트는 여러 모델을 붙이는 일이 아니라 어떤 책임 분리 구조일까요?
- 각 에이전트 노드가 공유 state를 읽고 쓸 때 무엇을 제한해야 할까요?
- handoff나 supervisor 경계가 흐리면 어떤 운영 문제가 생길까요?
- supervisor가 fallback 경로를 갖추어야 하는 이유는 무엇일까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 구조가 중요한가

멀티 에이전트를 배우는 이유를 "역할을 나눠서 더 똑똑하게 만들 수 있으니까"라고만 설명하면 너무 약합니다. 더 현실적인 이유는 설명 가능한 위임입니다. 요청이 복잡해질수록 팀은 반드시 "왜 이 요청이 이 worker에게 갔는가", "누가 최종 답을 책임지는가", "실패했을 때 어디서 멈추고 어디서 복구할 것인가"를 설명할 수 있어야 합니다.

예를 들어 어떤 요청은 개념 조사 worker에게, 어떤 요청은 코드 작성 worker에게 보내야 한다고 해 보겠습니다. 이 판단을 한 에이전트의 프롬프트 안에만 숨겨 두면 겉으로는 분업처럼 보일 수 있습니다. 하지만 운영에서는 "왜 research가 아니라 code로 갔지?", "worker가 왜 자기 역할 밖의 답변까지 만들었지?", "누가 최종 문장을 검증했지?" 같은 질문에 답하기가 매우 어려워집니다.

저는 팀들이 이 지점을 과소평가해서, 멀티 에이전트 구조를 도입한 뒤 오히려 디버깅이 더 어려워진 장면을 자주 봤습니다. agent 수는 늘었는데 책임 경계는 더 흐려졌기 때문입니다. 반대로 supervisor, worker, finalizer가 각각 무엇을 맡는지 명시적으로 남겨 두면, 구조는 커져도 읽기는 오히려 쉬워집니다.

그래서 이 글의 목표는 worker를 여러 개 띄우는 방법을 보여 주는 데 있지 않습니다. 더 중요한 목표는 **위임 구조를 그래프 위에 드러내면 왜 멀티 에이전트가 유지보수 가능한 시스템이 되는지**를 이해하는 데 있습니다.

---

## 멀티 에이전트 구조 다이어그램

코드를 작성하기 전에 멀티 에이전트의 책임 분리를 텍스트로 그려 보겠습니다.

```text
START
  |
  v
[supervisor]
  - 읽는 필드: request
  - 쓰는 필드: route
  - 역할: 위임 결정 (직접 답변 X)
  |
  v (조건부 엣지: route 값에 따라 분기)
  |
  +-- route == "research" --> [research_worker]
  |                             - 읽는 필드: request
  |                             - 쓰는 필드: worker_result
  |                             - 역할: 개념 조사 및 설명
  |                             |
  |                             v --> [finalize]
  |
  +-- route == "code"     --> [code_worker]
  |                             - 읽는 필드: request
  |                             - 쓰는 필드: worker_result
  |                             - 역할: 코드 작성 및 설명
  |                             |
  |                             v --> [finalize]
  |
  +-- route == "fallback" --> [fallback_worker]
                                - 읽는 필드: request, route
                                - 쓰는 필드: worker_result
                                - 역할: 안전한 기본 처리
                                |
                                v --> [finalize]

[finalize]
  - 읽는 필드: route, worker_result
  - 쓰는 필드: final_answer
  - 역할: 최종 응답 조립 (형식 통일)
  |
  v
END
```

이 다이어그램에서 핵심 원칙은 세 가지입니다. 첫째, supervisor는 오직 `route`만 쓰고 `worker_result`는 건드리지 않습니다. 둘째, 각 worker는 오직 `worker_result`만 씁니다. 셋째, finalize가 최종 응답을 조립하는 유일한 책임자입니다. 이 경계가 명확할수록 어떤 노드가 문제를 일으켰는지 추적하기 쉬워집니다.

---

## Multi-agent를 책임 분리로 읽기

멀티 에이전트에서 가장 먼저 잡아야 할 문장은 이것입니다. **Multi-agent는 책임 분리된 그래프 노드 클러스터**입니다. supervisor는 위임을 결정하고, worker는 자기 역할만 수행하고, finalizer는 최종 응답을 조립합니다. 즉, 여러 모델이 있다는 사실보다 **누가 무엇을 책임지는가가 구조로 드러나는 것**이 더 중요합니다.

많은 입문자가 멀티 에이전트를 "한 agent보다 agent가 여러 개면 더 잘하겠지"라는 기대에서 시작합니다. 절반은 맞지만, 절반은 놓칩니다. 중요한 차이는 결과 품질보다 **책임 경계와 handoff가 명시적으로 남는가**에 있습니다. 이게 있어야 worker를 늘려도 구조가 무너지지 않고, 어떤 agent가 어떤 필드를 읽고 썼는지도 추적할 수 있습니다.

| 구성 요소 | 역할 | 실무에서 왜 중요한가 |
| --- | --- | --- |
| **Supervisor** | 요청을 읽고 어떤 worker에게 보낼지 결정 | 위임 기준과 fallback을 한곳에서 관리할 수 있습니다 |
| **Worker Agent** | 자기 전문 영역의 결과를 생산 | 역할 경계가 분명해야 품질과 디버깅이 함께 좋아집니다 |
| **Shared State** | route, worker_result, final_answer 같은 최소 계약 | 어떤 agent가 무엇을 남겼는지 추적할 수 있습니다 |
| **Finalizer** | worker 결과를 사용자 응답으로 조립 | 출력 규칙을 한곳에 모아 확장 비용을 낮춥니다 |
| **Handoff Rule** | supervisor → worker → finalize 흐름 | agent 간 위임이 우연이 아니라 구조가 됩니다 |

---

## 최소 실행 예제

가장 작은 supervisor-worker 예제로 보겠습니다. supervisor가 요청을 읽고 `research` 또는 `code` worker 중 하나를 선택하고, worker는 자신의 전용 결과를 남기며, 마지막에 finalizer가 출력 형식을 정리합니다. fallback도 처음부터 포함했습니다.

```python
import os
from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph


class SupervisorState(TypedDict):
    request: str
    route: str
    worker_result: str
    final_answer: str


def get_llm() -> ChatGroq:
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.0,
        api_key=os.environ["GROQ_API_KEY"],
    )


def supervisor(state: SupervisorState) -> dict:
    """요청 유형을 분류하고 적절한 worker를 선택합니다.

    역할: 위임 결정만 합니다. 실제 답변을 생성하지 않습니다.
    쓰는 필드: route
    """
    request_lower = state["request"].lower()

    # 키워드 기반 빠른 분류 (LLM 비용 절약)
    if any(kw in request_lower for kw in ("코드", "python", "함수", "구현", "작성", "code", "implement")):
        return {"route": "code"}
    if any(kw in request_lower for kw in ("무엇", "왜", "설명", "개념", "what", "why", "explain")):
        return {"route": "research"}

    # 키워드로 분류 불가 -> LLM으로 판단
    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content=(
            "다음 요청을 'research' 또는 'code' 중 하나로 분류하세요. "
            "라벨만 반환하고 다른 텍스트는 포함하지 마세요."
        )),
        HumanMessage(content=state["request"]),
    ])
    route = response.content.strip().lower()

    # 알 수 없는 분류는 fallback으로 안전하게 처리
    if route not in {"research", "code"}:
        route = "fallback"

    return {"route": route}


def route_to_worker(
    state: SupervisorState,
) -> Literal["research_worker", "code_worker", "fallback_worker"]:
    """route 값에 따라 다음 worker를 결정합니다 (순수 함수)."""
    route = state.get("route", "fallback")
    if route == "code":
        return "code_worker"
    elif route == "research":
        return "research_worker"
    else:
        return "fallback_worker"


def research_worker(state: SupervisorState) -> dict:
    """LangGraph 개념을 조사하고 설명합니다.

    역할: 개념 설명 전용
    읽는 필드: request
    쓰는 필드: worker_result (다른 필드 건드리지 않음)
    """
    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content=(
            "LangGraph와 LangChain 생태계 전문 리서처입니다. "
            "개념을 간결한 불릿 포인트와 실용적인 엔지니어링 언어로 설명하세요."
        )),
        HumanMessage(content=state["request"]),
    ])
    return {"worker_result": response.content}


def code_worker(state: SupervisorState) -> dict:
    """LangGraph 관련 코드를 작성합니다.

    역할: 코드 작성 전용
    읽는 필드: request
    쓰는 필드: worker_result (다른 필드 건드리지 않음)
    """
    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content=(
            "LangGraph 튜토리얼 코딩 전문가입니다. "
            "짧고 실용적인 Python 코드 예제와 함께 답변하세요."
        )),
        HumanMessage(content=state["request"]),
    ])
    return {"worker_result": response.content}


def fallback_worker(state: SupervisorState) -> dict:
    """분류가 불가능한 요청을 안전하게 처리합니다.

    역할: fallback 처리 전용
    읽는 필드: request, route
    쓰는 필드: worker_result
    """
    return {
        "worker_result": (
            f"요청 분류에 실패했습니다 (route: {state.get('route', 'unknown')}). "
            f"원래 요청: '{state['request']}'. "
            "더 구체적인 질문으로 다시 시도해 주세요."
        )
    }


def finalize(state: SupervisorState) -> dict:
    """worker 결과를 최종 응답으로 조립합니다.

    역할: 출력 형식 통일 (응답 생성 전문)
    읽는 필드: route, worker_result
    쓰는 필드: final_answer
    """
    final_answer = (
        f"[{state['route'].upper()} 경로]\n\n"
        f"{state['worker_result']}"
    )
    return {"final_answer": final_answer}


def build_graph():
    graph = StateGraph(SupervisorState)

    # 노드 등록
    graph.add_node("supervisor", supervisor)
    graph.add_node("research_worker", research_worker)
    graph.add_node("code_worker", code_worker)
    graph.add_node("fallback_worker", fallback_worker)
    graph.add_node("finalize", finalize)

    # 엣지 연결
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_to_worker,
        {
            "research_worker": "research_worker",
            "code_worker": "code_worker",
            "fallback_worker": "fallback_worker",
        },
    )
    graph.add_edge("research_worker", "finalize")
    graph.add_edge("code_worker", "finalize")
    graph.add_edge("fallback_worker", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    test_requests = [
        "LangGraph의 체크포인트가 무엇인지 설명해 주세요.",
        "Python으로 간단한 StateGraph를 구현해 주세요.",
        "오늘 날씨가 어떤가요?",  # fallback 케이스
    ]

    for request in test_requests:
        result = app.invoke({
            "request": request,
            "route": "",
            "worker_result": "",
            "final_answer": "",
        })
        print(f"요청: {request}")
        print(f"라우트: {result['route']}")
        print(f"최종 답변:\n{result['final_answer'][:200]}...")
        print()
```

이 예제는 단순해 보여도 운영에서 중요한 것을 세 가지 보여 줍니다. 첫째, supervisor가 route를 결정하고 worker는 실제 작업만 하기 때문에 위임 이유와 작업 결과를 분리해 볼 수 있습니다. 둘째, worker는 `worker_result` 같은 전용 공유 필드만 갱신해서 shared state 계약을 최소화합니다. 셋째, finalizer가 출력 조립을 한곳에서 맡기 때문에 worker가 늘어나도 응답 형식이 여기저기 흩어지지 않습니다.

---

## shared state 설계 원칙

멀티 에이전트에서 가장 흔히 망가지는 부분은 shared state입니다. 처음에는 모든 정보를 공유 상태에 넣는 것이 편리해 보입니다. 하지만 그러면 금방 "이 필드를 누가 바꿔도 되는가?"라는 혼란이 생깁니다.

**좋은 shared state 설계:**

```python
class SupervisorState(TypedDict):
    # 입력 (변경 불가): 모든 노드가 읽을 수 있지만 쓰지 않음
    request: str

    # supervisor 전용 출력: supervisor만 씀
    route: str

    # worker 전용 출력: 각 worker가 씀 (덮어씀)
    worker_result: str

    # finalizer 전용 출력: finalize만 씀
    final_answer: str
```

**피해야 할 shared state 패턴:**

```python
# 나쁜 예: 너무 많은 필드가 공유됨
class OversharedState(TypedDict):
    request: str
    route: str
    research_notes: str      # research_worker 전용인데 공유됨
    code_snippets: list      # code_worker 전용인데 공유됨
    supervisor_reasoning: str # supervisor 내부 정보인데 공유됨
    quality_score: float     # finalizer 내부 정보인데 공유됨
    worker_result: str
    final_answer: str
    # 필드가 많을수록 "누가 이 필드를 바꿔도 되는가"가 불분명해짐
```

원칙은 단순합니다. **각 에이전트는 자신의 출력 필드만 씁니다.** worker가 supervisor의 `route` 필드를 바꾸거나, supervisor가 `worker_result`를 건드리기 시작하면 책임 경계가 흐려집니다.

---

## worker 추가 시 확장성 패턴

멀티 에이전트 구조의 장점은 worker를 추가해도 supervisor와 finalize를 크게 바꾸지 않아도 된다는 것입니다. 새 worker 유형을 추가하는 패턴을 보겠습니다.

```python
# 기존: research, code, fallback
# 추가: debug (디버깅 전문 worker)

def debug_worker(state: SupervisorState) -> dict:
    """에러와 디버깅 요청을 처리합니다."""
    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content=(
            "LangGraph 디버깅 전문가입니다. "
            "에러 메시지를 분석하고 해결 방법을 단계별로 설명하세요."
        )),
        HumanMessage(content=state["request"]),
    ])
    return {"worker_result": response.content}


def supervisor_extended(state: SupervisorState) -> dict:
    """debug 케이스를 추가한 확장된 supervisor."""
    request_lower = state["request"].lower()

    if any(kw in request_lower for kw in ("버그", "에러", "오류", "traceback", "bug", "error")):
        return {"route": "debug"}  # 새 라우트 추가
    if any(kw in request_lower for kw in ("코드", "python", "구현", "code", "implement")):
        return {"route": "code"}
    if any(kw in request_lower for kw in ("무엇", "설명", "개념", "what", "explain")):
        return {"route": "research"}
    return {"route": "fallback"}


def route_to_worker_extended(
    state: SupervisorState,
) -> Literal["research_worker", "code_worker", "debug_worker", "fallback_worker"]:
    """debug 라우트를 추가한 확장된 라우터."""
    route = state.get("route", "fallback")
    mapping = {
        "research": "research_worker",
        "code": "code_worker",
        "debug": "debug_worker",
    }
    return mapping.get(route, "fallback_worker")  # type: ignore[return-value]


def build_extended_graph():
    graph = StateGraph(SupervisorState)

    graph.add_node("supervisor", supervisor_extended)
    graph.add_node("research_worker", research_worker)
    graph.add_node("code_worker", code_worker)
    graph.add_node("debug_worker", debug_worker)       # 새 노드
    graph.add_node("fallback_worker", fallback_worker)
    graph.add_node("finalize", finalize)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_to_worker_extended,
        {
            "research_worker": "research_worker",
            "code_worker": "code_worker",
            "debug_worker": "debug_worker",       # 새 경로
            "fallback_worker": "fallback_worker",
        },
    )
    # finalize 연결은 모두 동일
    for worker in ["research_worker", "code_worker", "debug_worker", "fallback_worker"]:
        graph.add_edge(worker, "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()
```

이 패턴의 핵심은 worker를 추가할 때 `finalize` 노드를 바꾸지 않아도 된다는 사실입니다. finalize는 `worker_result`를 읽어서 최종 응답을 조립하므로, 어떤 worker가 결과를 만들었는지 상관없이 같은 방식으로 처리합니다. 이것이 finalizer 패턴의 확장성 이점입니다.

---

## 코드에서 먼저 볼 세 가지 포인트

코드 전체를 한 번에 읽기보다, 아래 세 지점부터 잡는 편이 좋습니다.

![route와 worker_result가 상태를 따라 흐르는 구조](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/05/05-02-what-to-notice-in-this-code.ko.png)
*route와 worker_result가 상태를 따라 흐르는 구조*

- supervisor는 경로를 결정하지만, 요청 자체에 답하려고 들지 않습니다.
- worker는 `worker_result` 같은 전용 공유 필드에만 결과를 기록합니다.
- `finalize`가 답변 조립을 한곳에서 맡기 때문에, 나중에 worker가 늘어나도 구조가 흔들리지 않습니다.

첫 번째 포인트는 supervisor의 역할 절제입니다. supervisor는 경로를 정해야지, 실제 답을 끝까지 만들려고 들면 안 됩니다. 저는 현업에서 supervisor가 분류도 하고, 중간 답도 쓰고, fallback 답변까지 만들기 시작하면서 구조가 다시 단일 agent처럼 무너지는 경우를 자주 봤습니다.

두 번째 포인트는 shared state 최소화입니다. worker가 모든 필드를 읽고 쓰기 시작하면 멀티 에이전트의 장점이 빠르게 사라집니다. 작은 전용 필드에 결과를 남기면 어떤 worker가 무엇을 책임졌는지 추적하기 쉽고, 나중에 worker를 교체하거나 추가할 때도 영향 범위를 줄일 수 있습니다.

세 번째 포인트는 finalizer입니다. finalizer가 없으면 worker마다 출력 스타일과 종료 규칙이 흩어지기 쉽습니다. 반대로 최종 조립을 한 노드에 모아 두면, 응답 형식은 중앙에서 통제하고 worker는 전문 작업에만 집중하게 만들 수 있습니다.

---

## 자주 하는 실수

멀티 에이전트 입문에서 가장 흔한 오해는 "agent를 여러 개 쓰면 자동으로 더 좋아진다"는 기대입니다. 실제로는 agent 수보다 **누가 위임을 결정하고, 누가 작업하고, 누가 최종 책임을 지는가**가 더 중요할 때가 많습니다.

![supervisor와 worker 사이의 역할 경계](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/05/05-03-where-engineers-get-confused.ko.png)
*supervisor와 worker 사이의 역할 경계*

**실수 1: Supervisor-less Multi-agent 안티패턴**

여러 worker가 있지만 누가 위임을 결정하는지 분명하지 않은 구조입니다. 처음에는 agent들이 유연하게 협력하는 것처럼 보일 수 있습니다. 하지만 실제로는 어떤 worker가 다른 worker를 다시 호출하고, 그 결과를 또 다른 worker가 다시 해석하면서, 역할 경계와 책임 소재가 빠르게 흐려집니다.

이 안티패턴이 production에서 왜 위험할까요? 첫째, 실패했을 때 어느 agent의 판단이 잘못됐는지 추적하기 어렵습니다. 둘째, handoff가 중첩되면서 token 비용과 지연이 예상보다 크게 늘어납니다. 셋째, supervisor가 없으면 fallback과 종료 규칙도 중앙에서 관리되지 않아, agent loop가 길어지거나 같은 요청을 여러 worker가 중복 처리하기 쉬워집니다.

**실수 2: supervisor가 작업까지 하는 패턴**

supervisor의 가장 흔한 역할 혼선입니다. supervisor가 분류도 하고 일부 답변도 작성하기 시작하면, 구조는 점점 단일 agent로 돌아갑니다.

```python
# 나쁜 예: supervisor가 작업까지 수행
def supervisor_bad(state: SupervisorState) -> dict:
    request_lower = state["request"].lower()
    if "코드" in request_lower:
        # supervisor가 직접 코드도 생성 -> worker가 필요 없어짐
        code = generate_code(state["request"])
        return {"route": "code", "worker_result": code}  # 역할 침범!
    return {"route": "research"}

# 좋은 예: supervisor는 라우팅만
def supervisor_good(state: SupervisorState) -> dict:
    request_lower = state["request"].lower()
    if "코드" in request_lower:
        return {"route": "code"}  # 라우팅만
    return {"route": "research"}  # 라우팅만
```

**실수 3: shared state를 지나치게 넓히기**

모든 worker가 모든 필드를 읽고 쓸 수 있게 열어 두면 처음에는 유연해 보입니다. 그러나 곧 "이 필드를 누가 바꿨지?", "왜 research worker가 code worker용 메타데이터를 건드렸지?" 같은 질문이 생깁니다. 저는 팀들이 여기서 모델 선택보다 상태 인터페이스 설계가 더 중요하다는 사실을 뒤늦게 체감하는 장면을 자주 봤습니다.

---

## 디버깅 전술: 위임 추적

멀티 에이전트 그래프에서 "어떤 worker가 이 요청을 처리했는가"를 추적하려면 `stream()`으로 노드별 상태 변화를 확인하는 것이 효과적입니다.

```python
app = build_graph()

request = "LangGraph의 체크포인트가 무엇인지 설명해 주세요."
print(f"요청: {request}\n")

for event in app.stream(
    {"request": request, "route": "", "worker_result": "", "final_answer": ""},
    stream_mode="updates",
):
    for node_name, state_update in event.items():
        print(f"[{node_name}] 업데이트:")
        for field, value in state_update.items():
            preview = str(value)[:80] + "..." if len(str(value)) > 80 else str(value)
            print(f"  {field}: {preview}")
```

**예상 출력:**

```text
요청: LangGraph의 체크포인트가 무엇인지 설명해 주세요.

[supervisor] 업데이트:
  route: research

[research_worker] 업데이트:
  worker_result: LangGraph 체크포인트는 그래프 실행 상태를 특정 시점에 저장하는...

[finalize] 업데이트:
  final_answer: [RESEARCH 경로]

LangGraph 체크포인트는 ...
```

이 추적에서 supervisor가 `research`를 선택하고, `research_worker`가 결과를 생성하고, `finalize`가 조립했다는 전체 위임 흐름이 보입니다. 이 흐름이 보이지 않으면 "왜 이 worker가 선택됐는가"를 나중에 설명하기 어렵습니다.

---

## 첫 번째 운영 체크리스트

멀티 에이전트를 붙이는 순간부터 아래 항목은 단순한 구조 리뷰가 아니라 위임 안정성 점검 항목이 됩니다.

- [ ] supervisor와 worker의 책임을 각각 한 문장으로 설명할 수 있는가
- [ ] supervisor가 `route`만 쓰고 `worker_result`는 건드리지 않는가
- [ ] worker 출력이 의미 있는 전용 필드에 저장되는가
- [ ] supervisor가 fallback과 handoff 규칙을 중앙에서 관리하는가
- [ ] shared state가 최소 계약만 노출하도록 설계됐는가
- [ ] 디버깅과 확장을 위한 전용 finalizer 노드가 있는가
- [ ] fallback_worker가 있어서 알 수 없는 route도 안전하게 처리되는가
- [ ] worker를 추가할 때 finalize를 바꾸지 않아도 되는 구조인가

이 체크리스트의 핵심은 "agent가 여러 개인가"가 아닙니다. "위임 구조가 설명 가능하고 안전한가"입니다. 멀티 에이전트는 기능이 아니라 운영 경계이기도 합니다.

---

## 실무에서는 이렇게 생각한다

멀티 에이전트를 붙인 순간 그래프는 단순한 라우팅 시스템을 넘어서 조직 구조를 닮기 시작합니다. 그래서 운영 질문도 달라집니다. "답이 좋았나?"보다 먼저 "누가 이 작업을 맡았지?", "handoff는 왜 여기서 일어났지?", "최종 책임은 어느 노드가 지지?" 같은 질문이 붙기 시작합니다.

현업에서 저는 멀티 에이전트 설계를 observability 설계와 함께 봅니다. supervisor가 어떤 route를 골랐는지, worker가 어떤 필드만 건드렸는지, finalizer가 어떤 출력 규칙을 적용했는지가 로그와 상태에 남아야 합니다. agent가 많아질수록 더 많은 모델보다 더 좋은 추적 경계가 먼저 필요해집니다.

또 하나 중요한 감각은 tool-calling agent와 multi-agent를 섞어 생각하지 않는 것입니다. tool-calling은 한 agent가 외부 기능을 호출하는 구조에 가깝고, multi-agent는 책임이 다른 주체들이 handoff하는 구조에 가깝습니다. 둘은 함께 쓰일 수 있지만, 역할이 다릅니다. 이 구분이 흐려지면 supervisor가 도구도 부르고 worker 역할도 하며 finalizer 역할까지 떠안는 이상한 구조가 되기 쉽습니다.

제가 본 강한 팀들은 모델 성능보다 handoff 계약을 먼저 리뷰했습니다. 이유는 단순합니다. worker 품질이 조금 흔들려도 supervisor와 finalizer가 경계를 지키면 시스템은 버팁니다. 반대로 위임 계약이 약하면 좋은 모델도 곧 역할 혼선 속에서 불안정한 시스템이 됩니다.

---

## 정리: Multi-agent는 모델 수가 아니라, 위임 구조를 설명 가능하게 만드는 그래프 설계다

멀티 에이전트를 처음 보면 "전문 agent를 여러 개 두는 구조"처럼 보일 수 있습니다. 그 설명도 틀리진 않지만, 운영 관점에서는 너무 약합니다. 더 중요한 설명은 이렇습니다. multi-agent는 supervisor가 위임을 결정하고, worker가 역할에 맞는 결과를 만들고, finalizer가 최종 응답을 정리하는 **책임 분리된 그래프 설계**입니다.

이 글에서 먼저 가져가야 할 핵심은 세 가지입니다. 첫째, supervisor는 판단과 위임에 집중해야 합니다. 둘째, worker는 shared state를 최소 계약 안에서만 다뤄야 합니다. 셋째, finalizer와 fallback 규칙은 optional 장식이 아니라 구조 안정성을 지키는 안전장치입니다.

이 관점이 중요한 이유는 다음 글의 완성형 LangGraph와 바로 이어지기 때문입니다. 마지막 글에서는 상태, 체크포인트, 분기, tool 호출, 멀티 에이전트를 하나의 그래프로 합치게 됩니다. 멀티 에이전트를 위임 구조로 이해하고 있어야 그 조합이 기능 나열이 아니라 하나의 운영 모델로 읽힙니다.

저는 멀티 에이전트 그래프를 볼 때 "agent가 많다"보다 "누가 무엇을 책임지는지 설명된다"를 먼저 봅니다. supervisor가 왜 이 worker를 골랐는지, worker가 어떤 필드만 갱신했는지, finalizer가 어디서 최종 책임을 지는지 말할 수 있다면 출발은 제대로 잡힌 셈입니다.

다음 글에서는 이 시리즈의 요소들을 하나의 완성형 LangGraph 예제로 묶어 보겠습니다. 그때 멀티 에이전트가 왜 별도의 트릭이 아니라 전체 그래프 설계를 안정시키는 마지막 조각인지 더 선명하게 드러날 것입니다.

---

## 운영 체크리스트

- [ ] supervisor의 위임 기준과 worker의 책임 경계를 ADR 또는 문서로 남겼다
- [ ] worker별 출력 필드와 shared state 최소 계약을 정의했다
- [ ] handoff 실패 시 fallback 또는 human-review 경로를 정했다
- [ ] finalizer가 응답 형식과 종료 책임을 흡수하도록 설계했다
- [ ] worker가 늘어나도 추적 가능한 로그/상태 경계를 유지할 수 있게 만들었다
- [ ] supervisor가 라우팅만 하고 작업은 worker에게 위임하는지 확인했다
- [ ] `stream()`으로 위임 흐름을 추적하는 디버깅 루틴을 갖추었다

## 처음 질문으로 돌아가기

- **멀티 에이전트는 여러 모델을 붙이는 일이 아니라 어떤 책임 분리 구조일까요?**
  - supervisor가 위임을 결정하고, worker가 전문 영역의 결과를 만들고, finalizer가 최종 응답을 조립하는 구조입니다. 모델 수가 아니라 각 노드가 어떤 필드를 읽고 쓰는지의 경계가 멀티 에이전트의 핵심입니다.

- **각 에이전트 노드가 공유 state를 읽고 쓸 때 무엇을 제한해야 할까요?**
  - 각 노드는 자신의 출력 필드만 써야 합니다. supervisor는 `route`만 쓰고, worker는 `worker_result`만 쓰고, finalizer는 `final_answer`만 씁니다. 다른 노드의 전용 필드를 건드리기 시작하면 책임 경계가 흐려지고 디버깅이 어려워집니다.

- **handoff나 supervisor 경계가 흐리면 어떤 운영 문제가 생길까요?**
  - 실패했을 때 어느 노드의 판단이 잘못됐는지 추적하기 어려워집니다. supervisor가 작업까지 하면 worker의 존재 이유가 없어지고, worker가 다른 worker를 직접 호출하기 시작하면 비용과 지연이 예측 불가능하게 늘어납니다.

<!-- toc:begin -->
## 시리즈 목차

- [LangGraph 101 (1/6): LangGraph 소개와 그래프 기초](./01-graph-basics.md)
- [LangGraph 101 (2/6): 상태 관리와 체크포인트](./02-state-and-checkpoints.md)
- [LangGraph 101 (3/6): 조건부 엣지와 분기 흐름](./03-conditional-edges.md)
- [LangGraph 101 (4/6): 도구 호출 에이전트](./04-tool-calling-agent.md)
- **LangGraph 101 (5/6): 멀티 에이전트 시스템 (현재 글)**
- [LangGraph 101 (6/6): LangGraph 완성](./06-langgraph-complete.md)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서
- [LangGraph multi-agent concepts](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
- [LangGraph supervisor tutorial](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/)
- [LangGraph multi-agent network guide](https://langchain-ai.github.io/langgraph/how-tos/multi-agent-network/)

### 관련 시리즈
- [조건부 엣지와 분기 흐름](./03-conditional-edges.md)
- [LangGraph 소개와 그래프 기초](./01-graph-basics.md)

---

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/langgraph-101/ko/05-multi-agent)

Tags: LangGraph, Agent, Python, LLM
