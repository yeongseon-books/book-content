---
title: "LangGraph 101 (4/6): 도구 호출 에이전트"
series: langgraph-101
episode: 4
language: ko
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/74"
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
seo_description: ToolNode와 tools_condition으로 도구 호출 루프를 명시적인 그래프로 표현합니다
---

# LangGraph 101 (4/6): 도구 호출 에이전트

도구를 쓰는 에이전트는 데모에서는 늘 똑똑해 보입니다. 계산이 필요하면 계산기를 부르고, 카운팅이 필요하면 텍스트 도구를 부르고, 그 결과를 바탕으로 답을 돌려주기 때문입니다. 하지만 운영으로 들어가면 질문이 곧바로 바뀝니다. 왜 이 요청만 도구를 세 번 호출했는지, 왜 존재하지도 않는 도구를 요청했는지, 왜 실패한 결과를 읽고도 같은 도구를 다시 부르는지가 중요해집니다.

이 글은 LangGraph 101 시리즈의 네 번째 글입니다. 여기서는 tool loop를 모델의 습관이 아니라, LLM 판단과 실제 도구 실행을 분리한 제어 루프로 읽습니다.

보통 핵심 문제는 모델이 도구를 사용할 수 있느냐가 아닙니다. 그 주위를 둘러싼 루프가 **명시적이고, 들여다볼 수 있고, 통제 가능한가**가 더 중요합니다. 도구 호출이 모델 내부의 불투명한 습관처럼 남아 있으면, 실패한 도구 재시도와 성공한 도구 후속 응답, 최종 답변 조립이 한 덩어리로 섞입니다. 그 순간 재현은 어려워지고, 로깅 경계는 약해지고, 비용이 어디서 커지는지도 읽기 힘들어집니다.

특히 side effect가 있는 도구가 붙는 순간 위험은 훨씬 커집니다. 읽기 전용 계산기나 카운터는 비교적 안전합니다. 하지만 외부 API를 호출하거나 파일을 수정하거나 티켓을 생성하는 도구라면, 한 번의 잘못된 루프가 중복 실행과 잘못된 상태 변경으로 이어질 수 있습니다.

여기서는 도구 호출 에이전트를 "모델이 알아서 도구를 쓰는 구조"가 아니라, **LLM 판단과 실제 도구 실행을 분리한 안전한 실행 환경**으로 이해해 보겠습니다. 핵심은 분명합니다. **Tool-calling agent는 LLM 노드, ToolNode, 그리고 명시적 종료 규칙이 결합된 제어 루프**입니다.

![agent와 tools 사이의 도구 루프](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/04/04-01-minimal-runnable-example.ko.png)
*agent와 tools 사이의 도구 루프*

> Tool-calling agent의 핵심은 모델이 도구를 안다는 사실이 아니라, 도구 실행이 검증 가능한 경계 안에서 반복된다는 사실입니다.

## 이 글에서 다룰 문제

- LangGraph tool-calling agent는 왜 LLM과 tool 실행 envelope를 분리해서 봐야 할까요?
- 도구 호출을 반복할 때 state에는 어떤 실행 흔적이 남아야 할까요?
- 안전한 dispatcher 없이 tool call을 실행하면 어떤 위험이 생길까요?
- 도구 실패 시 재시도 정책은 어떻게 설계해야 할까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 구조가 중요한가

도구 호출 에이전트를 배우는 이유를 "LLM이 계산도 하고 검색도 하게 만들 수 있으니까"라고만 설명하면 너무 약합니다. 더 현실적인 이유는 근거 있는 실행과 통제 가능한 루프입니다. 모델이 모르는 걸 외부 기능으로 보완하는 순간, 팀은 반드시 "왜 이 도구가 호출됐는가", "이 호출이 성공했는가", "언제 종료해야 하는가"를 설명할 수 있어야 합니다.

예를 들어 계산이 필요한 질문과 단순 설명 질문이 섞여 있다고 해 보겠습니다. 모델이 도구를 요청할 수도 있고, 그냥 답할 수도 있습니다. 이 흐름을 하나의 함수 안에 다 몰아넣으면 실행은 됩니다. 하지만 "왜 이 요청에서만 계산기를 두 번 불렀지?", "도구가 실패한 뒤 어떤 기준으로 다시 답변으로 돌아왔지?", "왜 여기서는 도구 없이 바로 끝났지?" 같은 질문에 답하기가 급격히 어려워집니다.

그래서 이 글의 목표는 `ToolNode` API를 외우는 데 있지 않습니다. 더 중요한 목표는 **도구 호출 루프를 명시적인 그래프로 만들면 왜 안전성과 디버깅 가능성이 함께 좋아지는지**를 이해하는 데 있습니다.

---

## tool loop 실행 흐름 다이어그램

코드를 보기 전에 tool loop가 어떻게 동작하는지 시퀀스로 이해하면 구조가 훨씬 명확해집니다.

```text
=== 도구가 필요한 요청 (예: 계산 요청) ===

HumanMessage("sqrt(81) + 5를 계산해 주세요.")
  |
  v
[agent 노드] - LLM 호출
  - 도구가 필요하다고 판단
  - AIMessage with tool_calls=[calculator("sqrt(81)+5")]
  |
  v (tools_condition: tool call 있음 -> tools로 이동)
  |
  v
[tools 노드] - ToolNode 실행
  - calculator("sqrt(81)+5") 실행 -> 결과: "14.0"
  - ToolMessage(content="14.0", tool_call_id="call_001")
  |
  v (tools -> agent: 항상)
  |
  v
[agent 노드] - LLM 호출 (도구 결과 포함)
  - 도구 결과를 보고 최종 답변 생성
  - AIMessage("sqrt(81) + 5 = 14.0입니다.")
  |
  v (tools_condition: tool call 없음 -> END)
  |
  v
END

=== 도구가 필요 없는 요청 (예: 개념 설명) ===

HumanMessage("LangGraph란 무엇인가요?")
  |
  v
[agent 노드] - LLM 호출
  - 도구 없이 직접 답변 가능
  - AIMessage("LangGraph는 ...")  # tool_calls 없음
  |
  v (tools_condition: tool call 없음 -> END)
  |
  v
END
```

이 다이어그램에서 핵심은 `tools_condition`의 역할입니다. 모델이 tool call을 포함한 응답을 했는지 여부에 따라 다음 노드를 결정합니다. 이 분기가 명시적이기 때문에 "왜 여기서 도구로 갔는가"와 "왜 여기서 바로 종료됐는가"를 구조로 설명할 수 있습니다.

---

## Tool-calling Agent를 실행 경계로 읽기

도구 호출 에이전트에서 가장 먼저 잡아야 할 문장은 이것입니다. **Tool-calling Agent는 LLM + 안전한 tool 실행 envelope**입니다. 모델은 도구 필요 여부를 판단하고, `ToolNode`는 실제 실행과 결과 메시지 생성을 담당하며, 조건부 엣지는 이 루프가 계속될지 종료될지를 결정합니다.

많은 입문자가 tool calling을 "LLM이 외부 기능을 부를 수 있게 만드는 옵션" 정도로 이해합니다. 절반은 맞지만, 절반은 놓칩니다. 중요한 차이는 도구 요청과 도구 실행이 **서로 다른 계층으로 분리된다**는 점입니다. 이 분리가 있어야 권한 검사, 로깅, 실패 복구, retry 정책을 모델 프롬프트 밖의 구조로 붙일 수 있습니다.

| 구성 요소 | 역할 | 실무에서 왜 중요한가 |
| --- | --- | --- |
| **LLM 노드** | 도구가 필요한지 판단하고 tool call을 생성 | 판단과 응답 생성 로직을 한곳에서 통제할 수 있습니다 |
| **ToolNode** | 실제 도구 실행과 `ToolMessage` 생성 | 모델 판단과 side-effect 실행을 분리할 수 있습니다 |
| **tools_condition** | tool call이 있으면 `tools`, 없으면 종료로 보냄 | 루프와 종료 규칙을 구조로 드러냅니다 |
| **Tool Schema / docstring** | 입력과 출력 계약을 모델에 설명 | 잘못된 도구 요청과 해석 오류를 줄이는 기준이 됩니다 |
| **Loop Guard** | recursion limit, fallback, timeout 같은 안전 장치 | 무한 루프와 runaway cost를 막습니다 |

---

## 최소 실행 예제

가장 작은 tool loop 예제로 보겠습니다. 모델이 질문을 읽고 필요한 경우 도구 호출을 요청하고, `ToolNode`가 실제 도구를 실행한 뒤, 그 결과를 다시 모델이 읽어 최종 답을 만듭니다.

```python
import ast
import json
import math
import operator
from collections.abc import Callable
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

# 안전한 수식 평가기 (eval() 대신 AST 파서 사용)
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
    """AST 기반 안전한 수식 평가 (eval() 미사용)"""
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
                raise ValueError(f"지원하지 않는 단항 연산자: {type(node.op).__name__}")
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
        raise ValueError(f"지원하지 않는 표현식: {type(node).__name__}")

    parsed = ast.parse(expression, mode="eval")
    return _evaluate(parsed.body)


@tool
def calculator(expression: str) -> str:
    """수학 표현식을 안전하게 계산합니다. sqrt(16), pi * 2 같은 표현식도 지원합니다.

    Args:
        expression: 계산할 수학 표현식 (예: "sqrt(81) + 5", "pi * 2")

    Returns:
        계산 결과 또는 에러 메시지
    """
    try:
        result = evaluate_math_expression(expression)
    except Exception as exc:
        return f"계산 오류: {exc}"
    return str(result)


@tool
def word_stats(text: str) -> str:
    """텍스트의 단어 수와 문자 수를 반환합니다.

    Args:
        text: 분석할 텍스트

    Returns:
        JSON 형식의 단어 수와 문자 수
    """
    return json.dumps(
        {"words": len(text.split()), "characters": len(text)},
        ensure_ascii=False,
    )


TOOLS = [calculator, word_stats]


def call_model(state: MessagesState) -> dict:
    """LLM을 호출하고 도구 필요 여부를 판단합니다."""
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.0,
        stop_sequences=None,
    ).bind_tools(TOOLS)

    system = SystemMessage(
        content="정확한 답변을 제공하는 어시스턴트입니다. 계산이나 단어 수 세기 작업에는 반드시 도구를 사용하세요."
    )
    response = llm.invoke([system, *state["messages"]])
    return {"messages": [response]}


def build_graph():
    graph = StateGraph(MessagesState)

    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(TOOLS))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent",
        tools_condition,
        {"tools": "tools", "__end__": END},
    )
    graph.add_edge("tools", "agent")

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    # 계산 요청 - 도구 사용
    result = app.invoke({
        "messages": [HumanMessage(content="sqrt(81) + 5를 계산해 주세요.")]
    })
    print("=== 계산 요청 ===")
    print(result["messages"][-1].content)

    # 단어 수 요청 - 도구 사용
    result = app.invoke({
        "messages": [HumanMessage(content="'LangGraph는 강력한 그래프 프레임워크입니다' 텍스트의 단어 수를 세어 주세요.")]
    })
    print("\n=== 단어 수 요청 ===")
    print(result["messages"][-1].content)
```

이 예제는 단순해 보여도 운영에서 중요한 것을 세 가지 보여 줍니다. 첫째, 모델이 도구 필요 여부를 판단하고 실제 실행은 `ToolNode`가 맡기 때문에, 판단 실패와 실행 실패를 서로 다른 계층에서 볼 수 있습니다. 둘째, `tools_condition`이 종료와 루프를 구조로 드러내기 때문에 "왜 여기서 끝났지?" 또는 "왜 여기서 다시 tools로 갔지?"를 코드 수준에서 설명할 수 있습니다. 셋째, `calculator`처럼 안전한 도구 구현을 별도로 두면 side-effect와 권한 범위를 모델 프롬프트 바깥에서 통제할 수 있습니다.

---

## 왜 eval() 대신 AST 파서를 쓰는가

`calculator` 도구에서 Python의 내장 `eval()` 대신 AST 파서를 쓴 이유를 짚고 넘어가겠습니다. 이 선택은 보안과 예측 가능성 때문입니다.

```python
# 위험한 방식: eval() 사용
@tool
def calculator_unsafe(expression: str) -> str:
    """절대 사용하지 마세요!"""
    return str(eval(expression))  # 임의 코드 실행 가능!

# 안전한 방식: AST 파서로 제한된 연산만 허용
@tool
def calculator(expression: str) -> str:
    """허용된 연산만 실행합니다."""
    try:
        result = evaluate_math_expression(expression)  # AST 파서 사용
    except Exception as exc:
        return f"계산 오류: {exc}"
    return str(result)
```

`eval("__import__('os').system('rm -rf /')")`처럼 위험한 표현식도 실행해 버립니다. AST 파서는 허용된 연산자와 함수만 실행하도록 엄격하게 제한합니다.

모델이 잘못된 표현식을 생성하더라도 AST 파서는 명확한 에러 메시지를 반환합니다. `eval()`은 예측하기 어려운 동작을 할 수 있습니다.

이 원칙은 도구 설계 전반에 적용됩니다. **도구는 가능한 한 결정론적(deterministic)이어야 하며, 허용 범위가 명확해야 합니다.** 모델이 잘못된 입력을 보내도 도구가 안전하게 실패할 수 있어야 합니다.

---

## ToolMessage를 상태 계약으로 다루기

tool loop를 운영에서 재현하려면 `ToolMessage`를 단순한 중간 산출물로 넘기면 안 됩니다. `ToolMessage`는 "어떤 tool call이 실제로 실행됐고, 그 결과가 무엇이었는지"를 state에 남기는 핵심 계약입니다.

```python
from langchain_core.messages import ToolMessage


def normalize_tool_result(
    name: str,
    tool_call_id: str,
    payload: str,
    is_error: bool = False,
) -> ToolMessage:
    """도구 실행 결과를 표준화된 ToolMessage로 변환합니다."""
    # 너무 긴 결과는 잘라서 저장
    MAX_CONTENT_LENGTH = 2_000
    if len(payload) > MAX_CONTENT_LENGTH:
        content = payload[:MAX_CONTENT_LENGTH] + "...<잘림>"
    else:
        content = payload

    status = "오류" if is_error else "성공"
    return ToolMessage(
        content=f"[{status}] {content}",
        name=name,
        tool_call_id=tool_call_id,
    )
```

이렇게 남겨 두면 다음과 같은 운영 질문에 즉시 답할 수 있습니다.

- 왜 같은 도구가 두 번 호출됐는가?
- 첫 호출과 두 번째 호출의 입력은 같았는가?
- 첫 호출은 실패였는가?
- 실패였다면 모델이 어떤 에러 메시지를 읽고 다시 시도했는가?

반대로 결과를 free-form 텍스트로만 이어 붙이면 호출 단위 재현이 거의 불가능해집니다.

---

## agent loop를 시퀀스로 시각화하기

LangGraph 코드만 보면 루프는 짧아 보이지만, 디버깅은 보통 "한 턴 안에서 몇 번 왕복했는지"를 보는 순간 쉬워집니다.

```text
=== 단일 도구 호출 (정상 경로) ===
HumanMessage
  -> agent(LLM): tool_calls=[calculator("sqrt(81)+5")]
  -> tools(ToolNode): ToolMessage(tool_call_id=call_1, content="[성공] 14.0")
  -> agent(LLM): AIMessage("sqrt(81) + 5 = 14.0입니다.")
  -> END
왕복 횟수: 1

=== 도구 실패 후 재시도 경로 ===
HumanMessage
  -> agent(LLM): tool_calls=[calculator("sqrt(-1)")]
  -> tools(ToolNode): ToolMessage(content="[오류] 계산 오류: 음수의 제곱근")
  -> agent(LLM): tool_calls=[calculator("sqrt(1)")]  # 다른 입력으로 재시도
  -> tools(ToolNode): ToolMessage(content="[성공] 1.0")
  -> agent(LLM): AIMessage("음수의 제곱근은 실수로 계산할 수 없어 sqrt(1)로 대신 계산했습니다.")
  -> END
왕복 횟수: 2

=== 도구 불필요 경로 ===
HumanMessage
  -> agent(LLM): AIMessage("LangGraph는 ...")  # tool_calls 없음
  -> END
왕복 횟수: 0
```

이 표현은 단순하지만 효과가 큽니다. 첫째, 종료 판단이 언제 일어나는지 보입니다. 둘째, 도구 실패 시 재시도가 몇 번까지 허용되는지 policy를 붙이기 쉽습니다. 셋째, 관측 지표를 어디서 수집할지 명확해집니다.

---

## 도구 실패 시 재시도 정책 설계

tool-calling agent를 production에 올릴 때 가장 큰 차이는 성공 경로가 아니라 실패 경로에서 드러납니다. 도구가 실패했을 때 모델에게 "알아서 다시 해 봐"라고 맡기는 방식은 재현성과 비용 통제를 동시에 잃기 쉽습니다.

```python
MAX_TOOL_RETRY = 2

# 재시도 가능한 에러 코드 분류
TRANSIENT_ERRORS = {"timeout", "rate_limit", "upstream_5xx"}
PERMANENT_ERRORS = {"invalid_args", "permission_denied", "not_found"}


def should_retry_tool(error_message: str, attempt: int) -> bool:
    """도구 재시도 여부를 결정합니다."""
    # 최대 재시도 횟수 초과
    if attempt >= MAX_TOOL_RETRY:
        return False

    # 일시적 에러만 재시도
    for error_code in TRANSIENT_ERRORS:
        if error_code in error_message.lower():
            return True

    return False


def format_tool_error_for_model(
    tool_name: str,
    error_message: str,
    attempt: int,
) -> str:
    """모델이 이해할 수 있는 에러 메시지를 생성합니다."""
    if attempt < MAX_TOOL_RETRY and any(
        code in error_message.lower() for code in TRANSIENT_ERRORS
    ):
        return (
            f"[일시적 오류] {tool_name} 실행 실패 (시도 {attempt + 1}/{MAX_TOOL_RETRY}): "
            f"{error_message}. 다른 방법으로 시도하거나 잠시 후 재시도 가능합니다."
        )
    else:
        return (
            f"[영구 오류] {tool_name} 실행 실패: {error_message}. "
            f"이 입력으로는 더 이상 시도할 수 없습니다. 다른 접근 방법을 사용해 주세요."
        )
```

이 정책의 핵심은 재시도 판단을 프롬프트가 아니라 실행 계층에 둔다는 사실입니다. 예를 들어 입력 검증 실패(`invalid_args`)는 즉시 중단하고, 일시적 오류만 제한적으로 재시도합니다. 그리고 최종 실패 시에는 무조건 같은 포맷의 에러 `ToolMessage`를 만들어 agent로 돌려보내 "왜 실패했고 다음에 무엇을 해야 하는지"를 모델이 읽을 수 있게 합니다.

---

## side-effect 도구의 idempotency 설계

side-effect가 있는 도구를 붙일 때는 idempotency(멱등성)를 반드시 고려해야 합니다. 예를 들어 티켓 생성 도구는 같은 요청을 여러 번 실행해도 결과가 동일해야 합니다.

```python
import hashlib
from datetime import datetime


@tool
def create_ticket(
    title: str,
    description: str,
    request_id: str,
) -> str:
    """티켓을 생성합니다. 같은 request_id로 중복 호출하면 기존 티켓을 반환합니다.

    Args:
        title: 티켓 제목
        description: 티켓 설명
        request_id: 중복 방지를 위한 요청 ID (호출자가 생성)

    Returns:
        생성된 또는 기존 티켓 정보
    """
    # 실제 구현에서는 DB 조회로 중복 확인
    ticket_key = hashlib.sha256(request_id.encode()).hexdigest()[:8]

    # 시뮬레이션: 이미 존재하는 티켓 처리
    # if ticket_already_exists(ticket_key):
    #     return f"[기존] 티켓 #{ticket_key}: {title}"

    return f"[신규] 티켓 #{ticket_key} 생성됨: {title} - {description}"
```

이 장치가 없으면 loop 재시도 한 번이 곧 중복 티켓, 중복 결제, 중복 상태 변경으로 이어질 수 있습니다. side-effect 도구는 반드시 "같은 요청을 두 번 보내도 안전한가?"를 먼저 확인해야 합니다.

---

## 코드에서 먼저 볼 세 가지 포인트

코드 전체를 한 번에 읽기보다, 아래 세 지점부터 잡는 편이 좋습니다.

![도구 호출과 ToolMessage 흐름](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/04/04-02-what-to-notice-in-this-code.ko.png)
*도구 호출과 ToolMessage 흐름*

- 도구의 docstring이 모델이 실제로 보는 사용 설명서가 됩니다.
- `ToolNode(TOOLS)`는 실행과 `ToolMessage` 생성 책임을 함께 맡습니다.
- `tools_condition`은 마지막 AI 메시지에 tool call이 있을 때만 `tools`로 보내고, 없으면 그래프를 종료합니다.

첫 번째 포인트는 도구 계약입니다. 모델은 Python 함수 본문을 이해하는 게 아니라, tool schema와 설명을 통해 도구를 배웁니다. 그래서 입력과 출력 계약이 흐릿하면 잘못된 tool call이 늘어나기 쉽습니다. docstring에 Args와 Returns를 명확하게 쓰는 것이 모델 품질 개선의 가장 빠른 방법입니다.

두 번째 포인트는 `ToolNode`의 역할 분리입니다. 모델이 도구를 요청했다고 해서 실행까지 모델이 하는 건 아닙니다. `ToolNode`가 실제 실행과 `ToolMessage` 생성을 맡기 때문에, 권한 검사와 로깅, 실패 처리 경계를 이 계층에 붙일 수 있습니다.

세 번째 포인트는 종료 규칙입니다. `tools_condition`은 단순해 보여도 아주 중요합니다. tool call이 없으면 종료하고, 있으면 실행 노드로 보냅니다. 이 구조가 명시적이어야 도구가 필요 없는 질문을 괜히 loop로 돌리지 않고, 반대로 도구가 필요한 질문에서만 loop를 유지할 수 있습니다.

---

## 자주 하는 실수

도구 호출 에이전트 입문에서 가장 흔한 오해는 "도구를 붙이면 모델이 더 정확해진다"는 기대입니다. 실제로는 정확성보다 **루프 제어와 side-effect 안전성**이 더 중요한 경우가 많습니다.

![마지막 AI 메시지에서 갈라지는 분기](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/04/04-03-where-engineers-get-confused.ko.png)
*마지막 AI 메시지에서 갈라지는 분기*

**실수 1: Unbounded Tool Loop 안티패턴**

모델이 도구를 한 번 요청하면, 실패 여부와 종료 조건을 충분히 통제하지 않은 채 다시 같은 질문을 던지고, 또 같은 도구를 부르는 구조입니다. 처음에는 "모델이 스스로 고쳐 보겠지"처럼 보일 수 있습니다. 하지만 실제로는 같은 도구 호출이 반복되면서 token 비용과 외부 호출 비용만 커지고, 최종 답은 오히려 늦게 나오거나 아예 안 나오는 경우가 많습니다.

이 안티패턴이 production에서 왜 위험할까요? 첫째, side-effect 도구라면 중복 실행이 곧 잘못된 상태 변경으로 이어질 수 있습니다. 둘째, 실패 원인이 모델 판단인지 도구 예외인지 구분하기 어려워집니다. 셋째, loop guard가 약하면 timeout과 recursion limit까지 운영 중 임기응변으로 다뤄야 해서 시스템 전체가 불안정해집니다.

**실수 2: docstring을 소홀히 하기**

`bind_tools()`는 모델이 도구를 요청하는 법만 알게 해 줄 뿐, 실행까지 해 주지는 않습니다. 모델이 도구를 어떻게 사용할지는 docstring에서 배웁니다. docstring이 부실하면 모델이 잘못된 인수를 보내거나, 적합하지 않은 상황에서 도구를 호출합니다.

**실수 3: eval()로 계산기 만들기**

결정적인 도구일수록 디버깅이 쉽습니다. 계산기는 `eval()` 대신 엄격한 산술 파서를 쓰는 편이 안전합니다. `eval()`은 보안 취약점이고, 예측하기 어려운 동작을 할 수 있습니다.

제가 본 강한 팀들은 tool-calling agent를 설계할 때 먼저 세 가지를 문서화했습니다. 어떤 도구가 read-only인지, 어떤 도구가 side-effect를 일으키는지, loop를 어디서 끊을지입니다. 이 세 가지가 명시되지 않으면 도구 호출 agent는 똑똑한 assistant가 아니라 통제 어려운 실행기처럼 변하기 쉽습니다.

---

## 디버깅 전술: tool loop 추적

도구 호출 루프를 디버깅할 때는 메시지 타입과 tool call 정보를 함께 확인하는 것이 효과적입니다.

```python
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

app = build_graph()
result = app.invoke({
    "messages": [HumanMessage(content="sqrt(144) + sqrt(25)를 계산해 주세요.")]
})

print("=== 메시지 타임라인 ===")
for i, msg in enumerate(result["messages"]):
    msg_type = type(msg).__name__
    if isinstance(msg, AIMessage) and msg.tool_calls:
        calls = [f"{tc['name']}({tc['args']})" for tc in msg.tool_calls]
        print(f"[{i}] {msg_type}: tool_calls={calls}")
    elif isinstance(msg, ToolMessage):
        print(f"[{i}] {msg_type}(name={msg.name}): {msg.content[:50]}")
    else:
        content_preview = str(msg.content)[:50]
        print(f"[{i}] {msg_type}: {content_preview}")
```

**예상 출력:**

```text
=== 메시지 타임라인 ===
[0] HumanMessage: sqrt(144) + sqrt(25)를 계산해 주세요.
[1] AIMessage: tool_calls=["calculator({'expression': 'sqrt(144)'})", "calculator({'expression': 'sqrt(25)'})"]
[2] ToolMessage(name=calculator): [성공] 12.0
[3] ToolMessage(name=calculator): [성공] 5.0
[4] AIMessage: sqrt(144) + sqrt(25) = 12 + 5 = 17입니다.
```

이 타임라인에서 모델이 두 개의 도구 호출을 동시에 요청했고 (병렬 tool call), 각각 성공했으며, 최종 답변을 생성한 것을 확인할 수 있습니다. 이 추적이 없으면 "왜 결과가 이렇게 나왔는가"를 역추적하기 어렵습니다.

---

## 첫 번째 운영 체크리스트

도구 호출 루프를 붙이는 순간부터 아래 항목은 단순한 구현 점검이 아니라 실행 안정성 점검 항목이 됩니다.

- [ ] 도구 설명(docstring)이 입력과 출력 계약을 분명하게 담고 있는가
- [ ] `agent -> tools -> agent` 루프가 그래프에서 명시적으로 보이는가
- [ ] side-effect 도구와 read-only 도구를 구분했는가
- [ ] 도구가 필요 없는 답변은 바로 `END`로 종료되는가
- [ ] timeout, recursion limit, fallback 같은 loop guard를 별도로 설계했는가
- [ ] side-effect 도구에 idempotency 키가 있는가
- [ ] 도구 실패 시 명확한 에러 메시지가 모델에게 전달되는가
- [ ] 메시지 타임라인으로 tool loop 왕복 횟수를 추적할 수 있는가

이 체크리스트의 핵심은 "도구를 쓰느냐"가 아닙니다. "도구를 안전하게 쓰고 멈출 수 있느냐"입니다. tool calling은 기능이 아니라 실행 경계이기도 합니다.

---

## 실무에서는 이렇게 생각한다

도구 호출 에이전트를 붙인 순간 그래프는 단순한 답변 생성기를 넘어서 실행 시스템이 됩니다. 그래서 운영 질문도 달라집니다. "답이 좋았나?"보다 먼저 "왜 이 도구가 선택됐지?", "실패했을 때 누가 종료를 결정하지?", "이 도구는 재시도해도 안전한가?" 같은 질문이 붙기 시작합니다.

또 하나 중요한 감각은 tool loop와 multi-agent handoff를 섞어 생각하지 않는 것입니다. tool loop는 한 agent가 외부 기능을 호출하는 구조에 가깝고, multi-agent는 역할이 다른 주체들이 handoff하는 구조에 가깝습니다. 둘은 함께 쓰일 수 있지만, 역할이 다릅니다. 이 구분이 흐려지면 supervisor가 도구도 직접 부르고, worker처럼 응답도 만들고, 종료 규칙까지 동시에 떠안는 구조가 되기 쉽습니다.

제가 본 강한 팀들은 모델 품질보다 도구 실행 계약을 먼저 리뷰했습니다. 모델이 조금 흔들려도 loop guard와 tool contract가 분명하면 시스템은 버팁니다.

---

## 정리: Tool-calling Agent는 모델 기능이 아니라, 실행을 안전하게 감싸는 그래프 제어 루프다

도구 호출 에이전트를 처음 보면 "모델이 외부 기능도 쓸 수 있게 된 구조"처럼 보일 수 있습니다. 그 설명도 틀리진 않지만, 운영 관점에서는 너무 약합니다. 더 중요한 설명은 이렇습니다. tool-calling agent는 모델이 도구 필요 여부를 판단하고, `ToolNode`가 실제 실행을 맡고, 종료 규칙이 loop를 안전하게 멈추게 만드는 **그래프 제어 루프**입니다.

이 글에서 먼저 가져가야 할 핵심은 세 가지입니다. 첫째, 도구 요청과 실제 실행은 분리돼 있어야 합니다. 둘째, side-effect 도구일수록 schema와 loop guard를 더 엄격하게 가져가야 합니다. 셋째, 종료 규칙과 fallback은 optional 장식이 아니라 production 안전장치입니다.

이 관점이 중요한 이유는 다음 글의 멀티 에이전트와 바로 이어지기 때문입니다. supervisor가 worker를 호출하는 handoff와, agent가 tool을 호출하는 loop는 서로 다른 주제지만 모두 "판단과 실행을 분리하는 구조"라는 공통점을 가집니다.

다음 글에서는 이 시리즈의 분기 구조를 supervisor-worker 협업으로 확장해 보겠습니다. 그때 tool loop가 왜 단순한 기능 확장이 아니라 멀티 에이전트 설계의 전 단계였는지가 더 선명하게 드러날 것입니다.

---

## 운영 체크리스트

- [ ] 도구별 권한 수준과 side-effect 여부를 문서화했다
- [ ] 실패한 tool call에 대한 fallback 또는 human-review 경로를 정했다
- [ ] recursion limit, timeout, retry 기준을 loop 밖에서 통제하도록 설계했다
- [ ] `ToolNode` 실행 로그와 모델 tool call 요청을 분리해 추적할 수 있게 만들었다
- [ ] 도구가 늘어나도 schema 품질과 종료 규칙을 유지할 검증 절차를 만들었다
- [ ] eval() 대신 안전한 파서로 계산 도구를 구현했다

## 처음 질문으로 돌아가기

- **LangGraph tool-calling agent는 왜 LLM과 tool 실행 envelope를 분리해서 봐야 할까요?**
  - 분리하지 않으면 "모델이 잘못 판단했는가"와 "도구 실행이 실패했는가"를 구분할 수 없습니다. 분리된 구조에서는 LLM 노드의 로그와 ToolNode의 로그를 독립적으로 확인할 수 있고, 각 계층에 다른 재시도 정책과 로깅을 붙일 수 있습니다.

- **도구 호출을 반복할 때 state에는 어떤 실행 흔적이 남아야 할까요?**
  - 각 tool call의 ID, 입력 인수, 실행 결과, 성공/실패 여부가 `ToolMessage`로 메시지 타임라인에 남아야 합니다. 특히 `tool_call_id`는 AIMessage의 tool call 요청과 ToolMessage의 결과를 연결하는 핵심 링크입니다. 이 흔적이 없으면 "왜 두 번 호출됐는가"를 추적할 수 없습니다.

- **안전한 dispatcher 없이 tool call을 실행하면 어떤 위험이 생길까요?**
  - 첫째, 권한 검사 없이 모든 도구가 실행됩니다. 둘째, side-effect 도구가 중복 실행되어 중복 결제나 중복 티켓 같은 문제가 생길 수 있습니다. 셋째, 실패 시 에러 메시지 포맷이 일관되지 않아 모델이 어떻게 대응해야 할지 알 수 없게 됩니다. `ToolNode`를 통해 실행하면 이런 문제를 한 계층에서 처리할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [LangGraph 101 (1/6): LangGraph 소개와 그래프 기초](./01-graph-basics.md)
- [LangGraph 101 (2/6): 상태 관리와 체크포인트](./02-state-and-checkpoints.md)
- [LangGraph 101 (3/6): 조건부 엣지와 분기 흐름](./03-conditional-edges.md)
- **LangGraph 101 (4/6): 도구 호출 에이전트 (현재 글)**
- [LangGraph 101 (5/6): 멀티 에이전트 시스템](./05-multi-agent.md)
- [LangGraph 101 (6/6): LangGraph 완성](./06-langgraph-complete.md)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서
- [LangGraph tool-calling how-to](https://langchain-ai.github.io/langgraph/how-tos/tool-calling/)
- [ToolNode API reference](https://langchain-ai.github.io/langgraph/reference/prebuilt/#toolnode)
- [LangChain tool concepts](https://python.langchain.com/docs/concepts/tools/)

### 관련 시리즈
- [조건부 엣지와 분기 흐름](./03-conditional-edges.md)
- [멀티 에이전트 시스템](./05-multi-agent.md)

---

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/langgraph-101/ko/04-tool-calling-agent)

Tags: LangGraph, Agent, Python, LLM
