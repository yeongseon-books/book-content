---
title: "LangGraph 101 (6/6): LangGraph 완성"
series: langgraph-101
episode: 6
language: ko
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/76"
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
seo_description: routing, tool loop, checkpoint를 하나의 LangGraph로 묶어 운영 가능한 완성형 에이전트 구조를 정리합니다
---

# LangGraph 101 (6/6): LangGraph 완성

시리즈를 여기까지 따라오면 질문이 바뀝니다. 노드와 엣지를 그릴 수 있는가, 체크포인트를 붙일 수 있는가, 도구를 호출할 수 있는가를 각각 묻는 단계는 이미 지났습니다. 이제 더 중요한 질문은 이것입니다. 이 조각들을 한 그래프 안에 합쳤을 때도 여전히 설명 가능하고, 복구 가능하고, 운영 가능한가입니다.

이 글은 LangGraph 101 시리즈의 마지막 글입니다. 여기서는 direct path, tool loop, checkpoint를 한 운영 모델로 묶어 읽는 기준점을 정리합니다.

현업에서 "완성형" 에이전트가 무너지는 장면은 대개 비슷합니다. 단순한 질문도 불필요하게 tool loop로 보내서 지연과 비용이 커지고, checkpoint는 붙어 있는데 route 판단 근거가 흐려서 재개 뒤 동작을 설명하기 어려워지며, supervisor 비슷한 분기 로직이 실제 답변 생성까지 끌어안으면서 구조가 다시 거대한 단일 프롬프트로 돌아갑니다. 겉으로는 기능을 다 붙인 것처럼 보여도, 안쪽에서는 책임 분리가 사라진 상태입니다.

그래서 이 장은 기능을 하나 더 추가하는 글이 아닙니다. 앞선 글에서 본 개념들을 하나의 운영 골격으로 묶는 글입니다. 체크포인트는 문맥을 이어 붙이고, supervisor는 직접 답할지 도구 경로로 보낼지 결정하며, tool loop는 전체 그래프를 오염시키지 않고 필요한 요청에서만 열립니다. 이 조합이 잡혀야 비로소 튜토리얼 밖에서도 써 볼 만한 구조가 됩니다.

여기서는 **직접 답변 경로와 도구 경로를 분리하고, 그 전체 대화를 같은 상태 타임라인 위에 저장하는 구조**를 읽어 보겠습니다. 완성형 LangGraph를 볼 때 먼저 확인할 것은 세 가지입니다. 어떤 요청이 굳이 도구로 가는지, tool loop가 어디서 끝나는지, 그리고 다음 턴이 시작될 때 이전 판단과 결과가 어떤 상태로 되살아나는지입니다. 이 세 가지가 선명하면 그래프는 커져도 읽힙니다.

![supervisor와 tool loop가 결합된 통합 그래프](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/06/06-01-minimal-runnable-example.ko.png)
*supervisor와 tool loop가 결합된 통합 그래프*

> 완성형 에이전트의 기준은 기능을 모두 붙였는지가 아니라, 경로 선택과 도구 실행과 상태 복구를 각각 설명할 수 있는지입니다.

## 이 글에서 다룰 문제

- 완성형 LangGraph 앱은 왜 하나의 거대한 프롬프트가 아니라 협력하는 상태 기계로 봐야 할까요?
- 체크포인트, 분기, tool call, 멀티턴 이력을 붙여도 어떤 state 계약은 끝까지 유지해야 할까요?
- 운영에서 그래프 실행을 설명하려면 어떤 로그와 검증 지점을 남겨야 할까요?
- direct path와 tool path를 어떻게 분리해야 비용과 품질을 모두 지킬 수 있을까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 구조가 중요한가

완성형 예제가 중요한 이유를 "기능이 다 들어 있으니까" 정도로 설명하면 충분하지 않습니다. 더 현실적인 이유는 운영 경계가 여기서 한꺼번에 만난다는 사실입니다. routing이 잘못되면 필요 없는 tool loop가 열리고, tool loop가 과하면 비용과 지연이 늘고, checkpoint 설계가 약하면 다음 턴에서 왜 그런 판단이 나왔는지 재구성하기 어려워집니다. 각 요소를 따로 배울 때는 보이지 않던 문제가, 합치는 순간 드러납니다.

예를 들어 사용자가 먼저 LangGraph의 상태 모델을 물었다가, 다음 턴에서 `sqrt(81) + 5`를 계산해 달라고 요청한다고 해 보겠습니다. 이때 첫 번째 질문은 직접 설명 경로로 가는 편이 낫고, 두 번째 질문은 도구 경로로 가야 안전합니다. 그런데 분리가 약하면 두 질문이 모두 같은 프롬프트 안에서 처리되거나, 반대로 둘 다 도구를 거치게 됩니다. 전자는 통제 불가능한 답변을 만들고, 후자는 과한 실행 비용을 만듭니다.

저는 팀들이 이 완성형 조합을 너무 늦게 검토해서, 개별 기능은 다 잘 동작하는데 전체 시스템은 설명하기 어려운 상태를 자주 봤습니다. checkpoint는 있는데 왜 맥락이 흐리지, tool calling은 있는데 왜 필요 없는 요청에도 도구를 부르지, route는 있는데 왜 supervisor가 실제 답까지 하려고 들지 같은 문제가 여기서 한꺼번에 튀어나옵니다.

---

## 완성형 그래프 전체 구조 다이어그램

완성형 그래프가 어떻게 동작하는지 전체 흐름을 먼저 그려 보겠습니다.

```text
=== 완성형 LangGraph 구조 ===

START
  |
  v
[supervisor]
  - 읽는 필드: messages (최신 HumanMessage)
  - 쓰는 필드: route
  - 역할: direct_answer vs tool_agent 분기
  |
  v (조건부 엣지: route 값에 따라)
  |
  +-- route == "direct_answer" --> [direct_answer]
  |                                  - LLM 직접 답변 (도구 없음)
  |                                  - messages에 AIMessage 추가
  |                                  |
  |                                  v --> END
  |
  +-- route == "tool_agent"   --> [tool_agent]
                                   - LLM + 도구 판단
                                   - tool_calls가 있으면 [tools]로
                                   |
                                   v (tools_condition)
                                   |
                                   +-- tool call 있음 --> [tools]
                                   |                        - ToolNode 실행
                                   |                        - ToolMessage 생성
                                   |                        |
                                   |                        v --> [tool_agent] (루프)
                                   |
                                   +-- tool call 없음 --> END

[모든 경로] -> checkpoint 저장 (thread_id로 세션 유지)
```

이 구조에서 핵심은 세 가지 경계입니다. 첫째, supervisor가 direct_answer와 tool_agent를 명확히 분리합니다. 둘째, tool loop는 tool_agent 내에서만 돌고 그래프 전체로 번지지 않습니다. 셋째, checkpoint가 두 경로 모두의 메시지를 같은 타임라인에 저장합니다.

---

## 완성형 그래프를 운영 모델로 읽기

마지막 글에서 가장 먼저 잡아야 할 문장은 이것입니다. **완성형 LangGraph 에이전트는 하나의 거대한 프롬프트가 아니라, supervisor 성격의 분기 로직, tool loop, checkpoint가 명시적 전이로 협력하는 상태 기계**입니다.

많은 입문자가 마지막 단계에서 다시 프롬프트 중심 사고로 돌아갑니다. "강한 모델 하나에 규칙을 다 넣으면 되지 않을까?"라는 생각입니다. 짧은 데모에서는 가능해 보일 수 있습니다. 하지만 운영에서는 직접 답변 경로, 계산·카운팅 같은 도구 경로, 다음 턴 재개를 위한 상태 저장이 서로 다른 책임을 가집니다. 이를 한곳에 뭉개면 어느 지점에서 비용이 생기고, 어느 경로에서 실패했는지, 왜 다음 턴이 이전 맥락을 그렇게 읽었는지가 흐려집니다.

완성형 그래프를 읽을 때는 네 가지만 먼저 붙잡으면 됩니다.

- supervisor route가 direct path와 tool path를 분리하는가
- `ToolNode` 루프가 필요한 요청에서만 열리는가
- checkpoint가 전체 메시지 타임라인을 붙잡는가
- 종료 규칙이 명시적인가

---

## 완성형 실행 예제

이제 시리즈에서 다룬 요소를 하나로 묶어 보겠습니다. 예제는 두 경로를 모두 보여 줍니다. 첫 번째 턴에서는 LangGraph 개념 질문에 직접 답하고, 두 번째 턴에서는 계산 요청을 tool loop로 보냅니다. 그리고 두 턴 모두 같은 `thread_id` 아래에서 저장해, 마지막에 checkpoint 상태를 확인합니다.

```python
import ast
import json
import math
import operator
from collections.abc import Callable
from typing import Any, Literal, cast

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

# 안전한 수식 평가기 (eval() 미사용)
ALLOWED_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
ALLOWED_FUNCTIONS: dict[str, Callable[..., Any]] = {
    name: value
    for name, value in math.__dict__.items()
    if not name.startswith("_") and callable(value)
}
ALLOWED_CONSTANTS = {"pi": math.pi, "e": math.e, "tau": math.tau}


def evaluate_math_expression(expression: str) -> float:
    """AST 기반 안전한 수식 평가"""
    def _evaluate(node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp):
            left = _evaluate(node.left)
            right = _evaluate(node.right)
            operation = ALLOWED_BINARY_OPERATORS.get(type(node.op))
            if operation is None:
                raise ValueError(f"지원하지 않는 연산자: {type(node.op).__name__}")
            return float(operation(left, right))
        if isinstance(node, ast.UnaryOp):
            operand = _evaluate(node.operand)
            operation = ALLOWED_UNARY_OPERATORS.get(type(node.op))
            if operation is None:
                raise ValueError(f"지원하지 않는 단항 연산자")
            return float(operation(operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            function = ALLOWED_FUNCTIONS.get(node.func.id)
            if function is None or node.keywords:
                raise ValueError(f"지원하지 않는 함수: {node.func.id}")
            arguments = [_evaluate(argument) for argument in node.args]
            return float(function(*arguments))
        if isinstance(node, ast.Name):
            value = ALLOWED_CONSTANTS.get(node.id)
            if value is not None:
                return float(value)
            raise ValueError(f"지원하지 않는 상수: {node.id}")
        raise ValueError(f"지원하지 않는 표현식 유형: {type(node).__name__}")

    parsed = ast.parse(expression, mode="eval")
    return _evaluate(parsed.body)


@tool
def calculator(expression: str) -> str:
    """수학 표현식을 안전하게 계산합니다. sqrt(16), pi * 2 같은 표현식도 지원합니다."""
    try:
        result = evaluate_math_expression(expression)
    except Exception as exc:
        return f"계산 오류: {exc}"
    return str(result)


@tool
def word_stats(text: str) -> str:
    """텍스트의 단어 수와 문자 수를 반환합니다."""
    return json.dumps(
        {"words": len(text.split()), "characters": len(text)},
        ensure_ascii=False,
    )


TOOLS = [calculator, word_stats]


class CompleteState(MessagesState):
    """완성형 그래프의 공유 상태.

    MessagesState에서 messages 필드(누적)를 상속받고,
    route 필드(갱신)를 추가합니다.
    """
    route: str


def get_llm() -> ChatGroq:
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0, stop_sequences=None)


def supervisor(state: CompleteState) -> dict:
    """최신 메시지를 보고 direct_answer vs tool_agent를 결정합니다.

    역할: 라우팅 결정만 합니다. 답변을 생성하지 않습니다.
    쓰는 필드: route
    """
    latest_question = str(state["messages"][-1].content).lower()

    # 계산/도구 관련 키워드 -> tool_agent 경로
    if any(kw in latest_question for kw in (
        "계산", "compute", "calculate", "math",
        "sqrt", "단어 수", "word count", "글자 수",
    )):
        return {"route": "tool_agent"}

    # 그 외 -> direct_answer 경로 (비용 효율적)
    return {"route": "direct_answer"}


def route_after_supervisor(
    state: CompleteState,
) -> Literal["direct_answer", "tool_agent"]:
    """route 값을 다음 노드로 변환합니다 (순수 함수)."""
    return cast(Literal["direct_answer", "tool_agent"], state.get("route", "direct_answer"))


def direct_answer(state: CompleteState) -> dict:
    """도구 없이 LLM으로 직접 답변합니다.

    역할: 개념 설명, 정보 제공 등 계산이 필요 없는 요청 처리
    """
    system = SystemMessage(
        content=(
            "LangGraph와 LangChain 생태계를 설명하는 어시스턴트입니다. "
            "대화 이력이 있으면 맥락을 활용해 일관성 있게 답변하세요."
        )
    )
    response = get_llm().invoke([system, *state["messages"]])
    return {"messages": [response]}


def tool_agent(state: CompleteState) -> dict:
    """도구를 사용해 계산 또는 분석 작업을 수행합니다.

    역할: 계산, 단어 수 세기 등 도구가 필요한 요청 처리
    """
    system = SystemMessage(
        content=(
            "정확한 계산과 분석을 위한 어시스턴트입니다. "
            "계산이나 단어 수 세기 작업에는 반드시 도구를 사용하세요. "
            "완료 후 결과를 한 단락으로 간결하게 요약하세요."
        )
    )
    response = get_llm().bind_tools(TOOLS).invoke([system, *state["messages"]])
    return {"messages": [response]}


def build_complete_graph():
    """완성형 그래프를 빌드합니다.

    구조:
    - supervisor: direct_answer vs tool_agent 분기
    - direct_answer: 도구 없이 직접 답변 -> END
    - tool_agent: 도구 호출 루프 -> END
    - tools: ToolNode (tool_agent와 루프)
    - checkpoint: MemorySaver (모든 경로의 메시지 저장)
    """
    graph = StateGraph(CompleteState)

    # 노드 등록
    graph.add_node("supervisor", supervisor)
    graph.add_node("direct_answer", direct_answer)
    graph.add_node("tool_agent", tool_agent)
    graph.add_node("tools", ToolNode(TOOLS))

    # 엣지 연결
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "direct_answer": "direct_answer",
            "tool_agent": "tool_agent",
        },
    )
    graph.add_edge("direct_answer", END)
    graph.add_conditional_edges(
        "tool_agent",
        tools_condition,
        {"tools": "tools", "__end__": END},
    )
    graph.add_edge("tools", "tool_agent")

    return graph.compile(checkpointer=MemorySaver())


if __name__ == "__main__":
    app = build_complete_graph()
    config: RunnableConfig = {"configurable": {"thread_id": "complete-demo-001"}}

    # 첫 번째 턴: 개념 설명 (direct_answer 경로)
    first = app.invoke(
        {
            "messages": [HumanMessage(content="LangGraph에서 명시적 상태란 무엇인가요?")],
            "route": "",
        },
        config=config,
    )
    print("=== 첫 번째 턴 (direct_answer 경로) ===")
    print(f"라우트: {first['route']}")
    print(f"답변: {str(first['messages'][-1].content)[:200]}...")

    # 두 번째 턴: 계산 요청 (tool_agent 경로)
    second = app.invoke(
        {"messages": [HumanMessage(content="sqrt(81) + 5를 계산하고 도구를 사용해 주세요.")]},
        config=config,
    )
    print("\n=== 두 번째 턴 (tool_agent 경로) ===")
    print(f"라우트: {second['route']}")
    print(f"답변: {str(second['messages'][-1].content)[:200]}...")

    # 체크포인트 검증
    snapshot = app.get_state(config)
    total_messages = len(snapshot.values["messages"])
    print(f"\n=== 체크포인트 검증 ===")
    print(f"저장된 총 메시지 수: {total_messages}")
    print(f"마지막 route: {snapshot.values['route']}")

    # 메시지 타임라인 출력
    from langchain_core.messages import AIMessage, ToolMessage
    print("\n=== 메시지 타임라인 ===")
    for i, msg in enumerate(snapshot.values["messages"]):
        msg_type = type(msg).__name__
        if isinstance(msg, AIMessage) and msg.tool_calls:
            calls = [tc["name"] for tc in msg.tool_calls]
            print(f"[{i}] {msg_type}: tool_calls={calls}")
        else:
            content_preview = str(msg.content)[:60]
            print(f"[{i}] {msg_type}: {content_preview}")
```

**예상 출력:**

```text
=== 첫 번째 턴 (direct_answer 경로) ===
라우트: direct_answer
답변: LangGraph에서 명시적 상태(explicit state)란 그래프의 모든 노드가 공유하는 데이터 계약입니다...

=== 두 번째 턴 (tool_agent 경로) ===
라우트: tool_agent
답변: sqrt(81) + 5 = 9 + 5 = 14.0입니다. 계산기 도구를 사용해 검증했습니다...

=== 체크포인트 검증 ===
저장된 총 메시지 수: 6
마지막 route: tool_agent

=== 메시지 타임라인 ===
[0] HumanMessage: LangGraph에서 명시적 상태란 무엇인가요?
[1] AIMessage: LangGraph에서 명시적 상태(explicit state)란 그래프의
[2] HumanMessage: sqrt(81) + 5를 계산하고 도구를 사용해 주세요.
[3] AIMessage: tool_calls=['calculator']
[4] ToolMessage: [성공] 14.0
[5] AIMessage: sqrt(81) + 5 = 9 + 5 = 14.0입니다.
```

이 예제는 시리즈 마지막 예제로서 의도적으로 과하지 않게 구성돼 있습니다. direct path, tool path, checkpoint만 넣고도 이미 운영에 필요한 핵심 골격이 모두 보입니다.

---

## 각 경로의 비용과 성능 특성 비교

완성형 그래프를 운영하면서 가장 먼저 측정해야 할 것은 경로별 특성입니다.

```text
=== 경로별 비용과 성능 비교 ===

direct_answer 경로:
  - LLM 호출 횟수: 1회
  - 외부 도구 실행: 없음
  - 평균 지연: 낮음 (LLM 응답 시간만)
  - 토큰 비용: 낮음 (도구 스키마 없음)
  - 적합한 요청: 개념 설명, 정보 제공, 대화

tool_agent 경로:
  - LLM 호출 횟수: 2회 이상 (판단 + 결과 해석)
  - 외부 도구 실행: 1회 이상
  - 평균 지연: 높음 (LLM + 도구 실행 + LLM)
  - 토큰 비용: 높음 (도구 스키마 + 결과 포함)
  - 적합한 요청: 계산, 데이터 분석, 외부 정보 조회
```

이 비교가 중요한 이유는 "모든 요청을 tool_agent로 보내면 안 된다"는 사실을 수치로 보여주기 때문입니다. 개념 설명 요청을 tool_agent로 보내면 불필요한 도구 스키마 토큰이 추가되고, 도구 판단 LLM 호출이 발생하며, 전체 지연이 2배 이상 늘어납니다. supervisor가 두 경로를 잘 분리할수록 비용 효율이 올라갑니다.

---

## 코드에서 먼저 볼 세 가지 포인트

![checkpoint와 route 상태 구조](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/06/06-02-what-to-notice-in-this-code.ko.png)
*checkpoint와 route 상태 구조*

- supervisor는 최신 질문만 보고 `direct_answer`와 `tool_agent`를 분리합니다.
- `tool_agent -> ToolNode -> tool_agent` 루프는 도구가 필요한 경우에만 열립니다.
- `compile(checkpointer=MemorySaver())`가 턴 전체를 같은 대화 타임라인으로 묶어 줍니다.

첫 번째 포인트는 route의 절제입니다. supervisor는 복잡한 답변을 만들지 않고, 지금 요청이 어떤 종류인지 판단하는 데 집중합니다. route를 고르던 노드가 "어차피 내가 답도 조금 써 줄게"라고 역할을 넓히기 시작하면 direct path와 tool path가 다시 프롬프트 한 덩어리로 섞입니다.

두 번째 포인트는 loop의 격리입니다. `ToolNode`를 거치는 왕복은 tool_agent 내부에서만 돌아야 합니다. tool loop가 supervisor나 direct_answer를 다시 거치기 시작하면 각 경로의 비용과 실패 양상이 뒤섞여서 추적이 어려워집니다.

세 번째 포인트는 checkpoint의 범위입니다. 여기서는 tool 결과만이 아니라 전체 메시지 타임라인을 저장합니다. 그래서 첫 번째 턴의 개념 설명 뒤에 두 번째 턴이 들어와도 같은 대화 위에서 계속 읽힙니다. 완성형 그래프에서 checkpoint는 옵션이 아니라 여러 실행 경로를 하나의 세션으로 묶는 접착제에 가깝습니다.

---

## 자주 하는 실수

완성형 예제에서 가장 흔한 오해는 "이제 기능이 다 들어갔으니 거의 끝났다"는 기대입니다. 실제로는 이 단계부터 안티패턴도 더 선명하게 드러납니다. direct path, tool path, checkpoint 중 하나라도 경계가 약하면 나머지 둘이 멀쩡해 보여도 전체 시스템은 금방 흔들립니다.

![human review interrupt가 포함된 검증 경로](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/06/06-03-where-engineers-get-confused.ko.png)
*human review interrupt가 포함된 검증 경로*

**실수 1: Everything-is-a-Tool 안티패턴**

계산이든 개념 질문이든 전부 도구 경로로 보내는 방식입니다. 처음에는 구현이 단순해 보일 수 있습니다. 하지만 실제로는 도구가 필요 없는 질문까지 `bind_tools()` 호출과 loop 판단을 거치면서 지연과 비용이 누적됩니다. 더 나쁜 경우에는 모델이 굳이 도구를 써야 한다고 착각해 불필요한 호출을 반복합니다.

```python
# 나쁜 예: 모든 요청을 tool_agent로
def supervisor_bad(state: CompleteState) -> dict:
    return {"route": "tool_agent"}  # 항상 tool_agent - 비용 낭비!

# 좋은 예: 키워드 기반 경로 분리
def supervisor_good(state: CompleteState) -> dict:
    latest = str(state["messages"][-1].content).lower()
    if any(kw in latest for kw in ("계산", "sqrt", "단어 수")):
        return {"route": "tool_agent"}
    return {"route": "direct_answer"}  # 기본값은 직접 답변
```

**실수 2: Checkpoint가 있으니 route가 복잡해도 된다는 생각**

저장된다는 사실과 설명 가능하다는 사실은 다릅니다. checkpoint가 있어도 route 결정 이유가 흐리면 "왜 이 요청이 tool_agent로 갔는가"를 다음 턴에서 재구성하기 어렵습니다.

**실수 3: 도구 실행 성공을 정답으로 착각하기**

`calculator`가 14.0을 반환했다고 해서 그것이 사용자 질문에 대한 올바른 답이라고 가정하면 안 됩니다. 도구는 실행 도구이지 품질 보증 장치가 아닙니다. production에서는 회귀 케이스와 필요 시 human-review interrupt 경로를 별도로 두어야 합니다.

---

## 체크포인트 영속화와 배포 설계

`MemorySaver()`는 구조를 이해하기 좋은 출발점이지만, 프로세스 재시작 뒤에도 대화를 복구해야 하는 환경에서는 영속 체크포인트가 필요합니다.

```python
# 운영 환경에서의 영속 체크포인트 선택

# 옵션 1: SQLite (단일 서버, 경량 영속성)
# from langgraph.checkpoint.sqlite import SqliteSaver
# checkpointer = SqliteSaver.from_conn_string("./checkpoints.db")

# 옵션 2: PostgreSQL (다중 인스턴스, 고가용성)
# from langgraph.checkpoint.postgres import PostgresSaver
# checkpointer = PostgresSaver.from_conn_string(os.environ["DATABASE_URL"])

# 운영 설정 예시 (환경 변수로 관리)
def get_checkpointer():
    backend = os.environ.get("LANGGRAPH_CHECKPOINT_BACKEND", "memory")
    if backend == "sqlite":
        from langgraph.checkpoint.sqlite import SqliteSaver
        return SqliteSaver.from_conn_string(os.environ.get("SQLITE_PATH", "./checkpoints.db"))
    # elif backend == "postgres":
    #     from langgraph.checkpoint.postgres import PostgresSaver
    #     return PostgresSaver.from_conn_string(os.environ["DATABASE_URL"])
    else:
        from langgraph.checkpoint.memory import MemorySaver
        return MemorySaver()
```

배포 관점에서 중요한 설계 원칙은 세 가지입니다. 첫째, 인스턴스는 stateless하게 유지합니다. 상태는 외부 저장소에 두고 인스턴스는 아무 요청이나 처리할 수 있게 만듭니다. 둘째, `thread_id` 규칙을 환경 변수가 아니라 코드로 명시합니다. 셋째, 세션 TTL을 정의해서 오래된 세션이 무제한으로 쌓이지 않게 합니다.

```yaml
# 배포 설정 예시 (플랫폼 독립적 의도)
service:
  name: langgraph-complete
  replicas: 3
  env:
    - name: LANGGRAPH_CHECKPOINT_BACKEND
      value: sqlite  # 또는 postgres
    - name: LANGGRAPH_THREAD_TTL_MINUTES
      value: "1440"  # 24시간
    - name: LANGGRAPH_MAX_RECURSION
      value: "20"    # tool loop 최대 반복
  health:
    readiness: /healthz/ready
    liveness: /healthz/live
```

---

## 장애 복구 시나리오별 전략

완성형 그래프 운영에서는 "노드 예외 하나"보다 "경로 단위 실패"를 다루는 편이 효과적입니다.

```text
=== 장애 유형별 복구 전략 ===

1. direct_answer 경로 LLM 실패:
   - 원인: LLM API timeout, 서비스 불가
   - 전략: 짧은 재시도 (1-2회) 후 graceful 에러 메시지
   - 메시지: "답변 생성에 일시적 문제가 발생했습니다. 다시 시도해 주세요."

2. tool_agent 경로 도구 실패:
   - 원인: 계산 오류, 잘못된 입력
   - 전략: 에러 ToolMessage를 모델에 전달 -> 모델이 다른 방법 시도
   - 최대 재시도: 2회 (MAX_TOOL_RETRY)

3. tool_agent 경로 LLM 실패 (도구 결과 해석 중):
   - 원인: 도구 결과 후 LLM 호출 실패
   - 전략: 도구 결과 원본 + 에러 메시지 반환
   - 체크포인트 복구: 이전 성공 상태에서 재개

4. 체크포인트 저장소 실패:
   - 원인: DB 연결 불가
   - 전략: 폴백으로 in-memory 사용 + 알림
   - 중요: 세션이 재시작되면 이전 대화 손실 가능성 고지
```

이 시나리오를 팀 문서로 남겨 두면 야간 장애에서 우선순위를 빠르게 정할 수 있습니다. "어느 경로의 어떤 단계가 실패했는가"가 분리되기 때문입니다.

---

## 완성형 그래프 통합 검증

완성형 그래프를 배포하기 전에 두 경로를 모두 검증하는 통합 테스트를 작성하는 것이 중요합니다.

```python
def test_complete_graph():
    """완성형 그래프의 두 경로와 체크포인트를 통합 검증합니다."""
    app = build_complete_graph()
    config = {"configurable": {"thread_id": "integration-test-001"}}

    # 테스트 1: direct_answer 경로
    result_direct = app.invoke(
        {
            "messages": [HumanMessage(content="LangGraph의 상태 기계란 무엇인가요?")],
            "route": "",
        },
        config=config,
    )
    assert result_direct["route"] == "direct_answer", \
        f"개념 질문은 direct_answer여야 함, 실제: {result_direct['route']}"
    assert len(result_direct["messages"]) >= 2, \
        "HumanMessage + AIMessage 최소 2개여야 함"

    # 테스트 2: tool_agent 경로
    result_tool = app.invoke(
        {"messages": [HumanMessage(content="sqrt(144)를 계산해 주세요.")]},
        config=config,
    )
    assert result_tool["route"] == "tool_agent", \
        f"계산 요청은 tool_agent여야 함, 실제: {result_tool['route']}"

    # 테스트 3: 체크포인트 검증
    snapshot = app.get_state(config)
    assert len(snapshot.values["messages"]) >= 4, \
        "두 턴의 메시지가 모두 저장되어야 함"

    from langchain_core.messages import ToolMessage
    has_tool_message = any(
        isinstance(msg, ToolMessage)
        for msg in snapshot.values["messages"]
    )
    assert has_tool_message, "tool_agent 경로에서 ToolMessage가 생성되어야 함"

    print("모든 통합 테스트 통과")
    print(f"총 저장 메시지: {len(snapshot.values['messages'])}")
    return True


if __name__ == "__main__":
    test_complete_graph()
```

이 검증을 CI/CD 파이프라인에 포함하면 코드 변경 시마다 두 경로가 모두 정상 동작하는지 자동으로 확인할 수 있습니다.

---

## 첫 번째 운영 체크리스트

완성형 그래프를 처음 묶는 순간부터 아래 항목은 기능 확인이 아니라 운영 가능성 점검 항목이 됩니다.

- [ ] 직접 응답 경로와 도구 경로가 명확하게 분리되어 있는가
- [ ] 같은 `thread_id`로 두 턴 이상 실행했을 때 대화가 예상대로 이어지는가
- [ ] 도구가 필요한 질문과 필요 없는 질문이 의도한 경로로 라우팅되는가
- [ ] tool loop 종료 조건이 명시적으로 드러나는가
- [ ] 계산기 같은 도구가 안전한 파서와 제한된 권한 범위를 유지하는가
- [ ] 두 경로의 비용과 지연을 별도로 관측할 수 있는가
- [ ] 장애 시나리오별 복구 전략이 문서화되어 있는가
- [ ] 통합 테스트가 두 경로를 모두 검증하는가

이 체크리스트의 핵심은 기능 유무가 아닙니다. 구조가 설명 가능한가, 비용과 실패가 통제 가능한가입니다.

---

## 실무에서는 이렇게 생각한다

실무에서 완성형 LangGraph를 본다는 것은 "멋진 데모"를 본다는 뜻이 아닙니다. 저는 먼저 direct path가 얼마나 많이 살아남는지 봅니다. production 요청의 상당수는 사실 도구를 필요로 하지 않습니다. 이 경로를 살려 두어야 평균 지연과 비용이 내려가고, tool path는 정말 필요한 요청에만 집중할 수 있습니다.

또 하나 중요한 감각은 checkpoint를 단순한 메모리 기능으로 다루지 않는 것입니다. 완성형 그래프에서는 route 결정, tool 결과, 최종 응답이 모두 같은 세션 타임라인에서 읽혀야 합니다. 그래서 observability도 세션 기준으로 봐야 합니다. 어떤 요청이 어느 path를 탔는지, tool이 몇 번 호출됐는지, 마지막 응답이 어떤 상태 스냅샷 위에서 생성됐는지가 남아야 디버깅이 가능합니다.

현업에서 저는 여기서 평가 경계를 분리합니다. tool 호출 성공률, route 정확도, 최종 답변 품질은 서로 다른 지표입니다. calculator가 정상 동작해도 route가 잘못되면 쓸데없는 계산이 늘고, route가 좋아도 checkpoint가 약하면 다음 턴 품질이 흔들립니다. 완성형 그래프를 잘 운영하는 팀은 모델 하나의 품질보다 경로별 책임과 지표를 먼저 나눕니다.

---

## 정리: LangGraph 완성은 기능 나열이 아니라, 상태·분기·도구·체크포인트를 하나의 운영 모델로 묶는 일이다

![턴 전반의 production 에이전트 흐름](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/06/06-04-summary.ko.png)
*턴 전반의 production 에이전트 흐름*

마지막 글에서 가져가야 할 핵심은 분명합니다. 완성형 LangGraph는 거대한 만능 프롬프트가 아닙니다. supervisor 성격의 route 판단이 direct path와 tool path를 나누고, 필요한 경우에만 `ToolNode` 루프가 열리며, 그 전체 대화가 checkpoint를 통해 같은 세션 타임라인에 저장되는 구조입니다.

이 시리즈에서 앞서 본 조각들도 여기서 모두 다시 제자리를 찾습니다.

- **1편: 그래프 기초** — 흐름을 읽는 눈과 상태 기계 멘탈 모델
- **2편: 상태와 체크포인트** — 세션 타임라인과 복구 가능한 실행
- **3편: 조건부 엣지** — 경로 선택을 명시적으로 드러내는 라우팅 계층
- **4편: 도구 호출** — 안전한 실행 루프와 tool envelope 분리
- **5편: 멀티 에이전트** — 책임 분리와 supervisor-worker-finalizer 패턴
- **6편: 완성** — 이 모든 것을 하나의 운영 가능한 그래프로 통합

마지막 예제는 그 요소들을 한 문장으로 묶습니다. **무엇을 직접 답하고, 무엇을 도구로 보내며, 그 전 과정을 어떻게 저장할 것인가.**

이 글로 LangGraph 101 시리즈를 마무리합니다. 시리즈 전체에서 계속 강조한 것도 결국 하나였습니다. 좋은 에이전트는 한 번의 멋진 응답보다, 상태와 전이를 숨기지 않는 구조에서 나옵니다. 그 구조를 손에 잡히는 코드로 바꾸는 것이 LangGraph의 진짜 가치입니다.

---

## 운영 체크리스트

- [ ] route 판단, direct answer, tool loop, checkpoint 책임을 각각 한 문장으로 설명할 수 있다
- [ ] direct path와 tool path의 비용·지연·실패 양상을 별도로 관측할 수 있다
- [ ] 같은 `thread_id` 재개 시 이전 메시지와 새 요청이 하나의 대화로 자연스럽게 이어진다
- [ ] 도구는 안전한 입력 파서와 회귀 테스트 케이스를 갖추고 있다
- [ ] human review 또는 fallback 경로를 포함한 종료 전략을 운영 문서에 남겼다
- [ ] 장애 시나리오별 복구 전략이 경로 단위로 문서화되어 있다
- [ ] 통합 테스트가 두 경로와 체크포인트를 모두 검증한다
- [ ] MemorySaver에서 영속 저장소로 마이그레이션 계획이 있다

## 처음 질문으로 돌아가기

- **완성형 LangGraph 앱은 왜 하나의 거대한 프롬프트가 아니라 협력하는 상태 기계로 봐야 할까요?**
  - 거대한 프롬프트는 "왜 이 요청이 도구를 사용했는가", "어느 단계에서 비용이 생겼는가", "다음 턴에서 왜 이전 맥락을 이렇게 읽었는가"를 설명할 수 없습니다. 상태 기계 구조에서는 supervisor 결정, tool 실행, checkpoint 저장이 각각 분리된 계층으로 드러나기 때문에 이 질문들에 코드 수준에서 답할 수 있습니다.

- **체크포인트, 분기, tool call, 멀티턴 이력을 붙여도 어떤 state 계약은 끝까지 유지해야 할까요?**
  - `messages` 필드는 두 경로 모두에서 누적되어야 합니다. `route` 필드는 각 턴의 라우팅 결정을 기록해야 합니다. 이 두 필드가 안정적으로 유지되어야 "어떤 경로를 탔는가"와 "이전 대화가 무엇이었는가"를 항상 읽을 수 있습니다.

- **운영에서 그래프 실행을 설명하려면 어떤 로그와 검증 지점을 남겨야 할까요?**
  - 각 turn에서 route 결정 이유, 사용된 도구 이름과 결과, LLM 호출 횟수, 체크포인트 저장 성공 여부를 남겨야 합니다. `stream()`으로 노드별 상태 변화를 추적하고, `get_state()`로 저장 상태를 검증하는 루틴을 팀 표준으로 정하면 디버깅 시간이 크게 줄어듭니다.

<!-- toc:begin -->
## 시리즈 목차

- [LangGraph 101 (1/6): LangGraph 소개와 그래프 기초](./01-graph-basics.md)
- [LangGraph 101 (2/6): 상태 관리와 체크포인트](./02-state-and-checkpoints.md)
- [LangGraph 101 (3/6): 조건부 엣지와 분기 흐름](./03-conditional-edges.md)
- [LangGraph 101 (4/6): 도구 호출 에이전트](./04-tool-calling-agent.md)
- [LangGraph 101 (5/6): 멀티 에이전트 시스템](./05-multi-agent.md)
- **LangGraph 101 (6/6): LangGraph 완성 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [LangGraph tutorials](https://langchain-ai.github.io/langgraph/tutorials/)
- [LangGraph persistence guide](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
- [LangGraph prebuilt components](https://langchain-ai.github.io/langgraph/reference/prebuilt/)

### 관련 시리즈
- [상태 관리와 체크포인트](./02-state-and-checkpoints.md)
- [도구 호출 에이전트](./04-tool-calling-agent.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/langgraph-101/ko/06-langgraph-complete)

Tags: LangGraph, Agent, Python, LLM
