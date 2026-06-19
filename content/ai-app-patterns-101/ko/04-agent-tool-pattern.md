---
series: ai-app-patterns-101
episode: 4
title: "AI App Patterns 101 (4/6): Agent Tool 패턴"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Agent
  - ReAct
  - ToolCalling
  - LLM
  - Autonomous
seo_description: ReAct 패턴, @tool 데코레이터, 도구 레지스트리, 오류 핸들링을 에이전트 관찰로 처리하는 방법까지 Agent Tool 패턴 핵심을 정리합니다
last_reviewed: '2026-06-20'
---

# AI App Patterns 101 (4/6): Agent Tool 패턴

에이전트는 LLM이 어떤 도구를 언제 호출할지 스스로 결정하고, 도구 결과를 관찰해 다음 행동을 계획하는 패턴입니다. 단순한 챗봇이나 RAG와 달리, 에이전트는 여러 단계의 추론-행동-관찰 루프를 반복하며 목표를 달성합니다. 이 패턴의 핵심은 도구를 얼마나 안전하고 예측 가능하게 설계하느냐입니다.

에이전트를 "더 자율적인 AI"로만 보면 운영이 금방 흐려집니다. 에이전트의 자율성은 도구 경계 안에서만 안전합니다. 도구가 좁고 명확할수록 에이전트의 행동이 예측 가능하고 디버깅하기 쉬워집니다.

이 글은 AI App Patterns 101 시리즈의 4번째 글입니다.

![Agent Tool 패턴 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/04/04-01-concept-at-a-glance.ko.png)
*ReAct 루프와 도구 레지스트리가 결합된 에이전트 아키텍처*

## 이 글에서 다룰 문제

- ReAct 패턴에서 Thought, Action, Observation 각 단계의 역할은 무엇일까요?
- 도구를 안전하게 설계하려면 어떤 제약이 필요할까요?
- 도구 오류가 발생했을 때 에이전트가 복구하는 방법은 무엇일까요?
- 에이전트가 무한 루프에 빠지는 것을 어떻게 방지할 수 있을까요?
- 프로덕션 에이전트에서 반드시 로깅해야 할 정보는 무엇일까요?

## 핵심 개념 한 줄 정리

- **ReAct**: Reasoning + Acting의 약자로, LLM이 생각(Thought)하고 행동(Action)하고 결과를 관찰(Observation)하는 반복 루프입니다.
- **Tool**: 에이전트가 호출할 수 있는 함수로, 입력 스키마와 설명이 LLM에 제공됩니다.
- **Tool Registry**: 사용 가능한 도구 목록을 관리하고 이름으로 조회하는 시스템입니다.
- **Observation**: 도구 실행 결과로, 에이전트의 다음 추론에 입력됩니다.
- **Max Iterations**: 에이전트 루프의 최대 반복 횟수로, 무한 루프를 방지합니다.

## 에이전트 vs 체인 비교

| 특성 | 체인(Chain) | 에이전트(Agent) |
|---|---|---|
| 흐름 결정 | 사전 정의된 순서 | LLM이 동적으로 결정 |
| 도구 선택 | 고정 | 상황에 따라 유연하게 선택 |
| 예측 가능성 | 높음 | 낮음 |
| 적합 상황 | 반복적 작업 | 다양한 도구가 필요한 복잡한 작업 |
| 디버깅 난이도 | 낮음 | 높음 |

## 구체적인 시나리오: 데이터 분석 에이전트

**시나리오**: 비즈니스 분석가가 "지난달 매출 상위 5개 제품의 전월 대비 성장률을 계산하고, 그 결과를 Slack으로 보내 줘"라고 요청합니다. 이 작업은 (1) DB 쿼리, (2) 계산, (3) 메시지 전송 세 단계가 순서 없이 필요합니다. 체인으로 구현하면 단계가 고정되지만, 에이전트는 질문에 따라 필요한 도구만 선택해 실행합니다.

## 실습 1: 도구 정의와 레지스트리

도구를 함수로 정의하고, 레지스트리로 관리합니다. LLM에는 도구의 이름, 설명, 입력 스키마가 전달됩니다. 설명이 모호하면 LLM이 잘못된 도구를 선택합니다.

```python
import json
from typing import Any, Callable
from dataclasses import dataclass


@dataclass
class Tool:
    name: str
    description: str
    func: Callable
    parameters: dict


class ToolRegistry:
    """에이전트가 사용할 도구를 등록하고 조회합니다."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, name: str, description: str, parameters: dict):
        """함수를 도구로 등록하는 데코레이터입니다."""
        def decorator(func: Callable):
            self._tools[name] = Tool(
                name=name,
                description=description,
                func=func,
                parameters=parameters,
            )
            return func
        return decorator

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[dict]:
        """OpenAI function calling 형식으로 도구 목록을 반환합니다."""
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in self._tools.values()
        ]

    def tool_names(self) -> list[str]:
        return list(self._tools.keys())


# 도구 레지스트리 초기화
registry = ToolRegistry()


@registry.register(
    name="query_sales_data",
    description=(
        "데이터베이스에서 매출 데이터를 조회합니다. "
        "기간, 제품 카테고리, 상위 N개 제품을 필터링할 수 있습니다. "
        "실시간 재고나 배송 정보에는 사용하지 마세요."
    ),
    parameters={
        "type": "object",
        "properties": {
            "period": {
                "type": "string",
                "description": "조회 기간 (예: '2026-05', 'last_month', 'last_quarter')",
            },
            "top_n": {
                "type": "integer",
                "description": "상위 N개 제품 (기본값: 10)",
                "default": 10,
            },
        },
        "required": ["period"],
    },
)
def query_sales_data(period: str, top_n: int = 10) -> str:
    """실제 구현에서는 DB 쿼리를 실행합니다."""
    # 예시 데이터
    mock_data = [
        {"product": "Product A", "sales": 1500000, "units": 300},
        {"product": "Product B", "sales": 1200000, "units": 250},
        {"product": "Product C", "sales": 900000, "units": 180},
    ]
    return json.dumps({"period": period, "top_products": mock_data[:top_n]}, ensure_ascii=False)


@registry.register(
    name="calculate",
    description=(
        "수학 계산을 수행합니다. "
        "사칙연산, 백분율, 성장률 계산에 사용하세요. "
        "허용 연산자: +, -, *, /, %, ** (거듭제곱)"
    ),
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "계산할 수식 (예: '(1500 - 1200) / 1200 * 100')",
            },
        },
        "required": ["expression"],
    },
)
def calculate(expression: str) -> str:
    """안전한 수학 계산을 수행합니다."""
    allowed = set("0123456789+-*/.() %")
    if not all(c in allowed for c in expression):
        return f"오류: 허용되지 않은 문자가 포함되어 있습니다: {expression}"
    try:
        result = eval(expression, {"__builtins__": {}})
        return f"계산 결과: {result}"
    except Exception as e:
        return f"계산 오류: {str(e)}"


@registry.register(
    name="send_slack_message",
    description=(
        "Slack 채널에 메시지를 전송합니다. "
        "분석 결과 공유, 알림 전송에 사용하세요. "
        "개인 정보나 인증 데이터는 절대 포함하지 마세요."
    ),
    parameters={
        "type": "object",
        "properties": {
            "channel": {"type": "string", "description": "Slack 채널 이름 (예: '#sales-report')"},
            "message": {"type": "string", "description": "전송할 메시지 내용"},
        },
        "required": ["channel", "message"],
    },
)
def send_slack_message(channel: str, message: str) -> str:
    """실제 구현에서는 Slack API를 호출합니다."""
    # 프로덕션에서는 slack_sdk 사용
    print(f"[Slack → {channel}]\n{message}")
    return f"메시지가 {channel}에 전송되었습니다."
```

## 실습 2: ReAct 에이전트 루프

LLM이 도구를 선택하고, 실행하고, 결과를 관찰하며 목표를 달성하는 루프를 구현합니다.

```python
from openai import OpenAI
import json

client = OpenAI()

SYSTEM_PROMPT = """당신은 데이터 분석 에이전트입니다. 도구를 사용해 사용자의 요청을 처리하세요.
- 필요한 도구만 선택하고 불필요한 도구는 호출하지 마세요.
- 도구 결과를 보고 다음 행동을 결정하세요.
- 충분한 정보를 얻었으면 최종 답변을 제공하세요."""


def run_agent(
    user_query: str,
    max_iterations: int = 5,
    verbose: bool = True,
) -> dict:
    """ReAct 루프로 에이전트를 실행합니다."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]
    tools = registry.list_tools()
    tool_calls_log = []

    for iteration in range(max_iterations):
        if verbose:
            print(f"\n[Iteration {iteration + 1}/{max_iterations}]")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=1024,
        )

        message = response.choices[0].message
        messages.append(message)

        # 도구 호출이 없으면 최종 답변 반환
        if not message.tool_calls:
            if verbose:
                print(f"[Final Answer] {message.content}")
            return {
                "answer": message.content,
                "iterations": iteration + 1,
                "tool_calls": tool_calls_log,
                "stopped_reason": "final_answer",
            }

        # 도구 호출 실행
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            if verbose:
                print(f"[Action] {tool_name}({tool_args})")

            tool = registry.get(tool_name)
            if tool:
                try:
                    observation = tool.func(**tool_args)
                    status = "success"
                except Exception as e:
                    observation = f"도구 실행 오류: {str(e)}"
                    status = "error"
            else:
                observation = f"알 수 없는 도구: {tool_name}"
                status = "not_found"

            tool_calls_log.append({
                "tool": tool_name,
                "args": tool_args,
                "status": status,
            })

            if verbose:
                print(f"[Observation] {observation[:100]}")

            # 관찰 결과를 메시지에 추가
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": observation,
            })

    return {
        "answer": "최대 반복 횟수에 도달했습니다.",
        "iterations": max_iterations,
        "tool_calls": tool_calls_log,
        "stopped_reason": "max_iterations",
    }


# 사용 예시
result = run_agent(
    "지난달 매출 상위 3개 제품을 조회하고, 1위와 2위의 매출 차이를 계산해 주세요."
)
print(f"\n최종 결과: {result['answer']}")
print(f"사용한 도구: {[tc['tool'] for tc in result['tool_calls']]}")
```

## 실습 3: 오류를 관찰로 처리하기

도구 실행 중 오류가 발생하면 에이전트에게 오류 내용을 알려 복구를 시도하게 합니다. 예외를 그냥 던지면 에이전트 루프가 중단됩니다.

```python
import time
from openai import OpenAI

client = OpenAI()


def safe_tool_call(
    tool: Tool,
    args: dict,
    max_retries: int = 2,
    timeout_sec: float = 10.0,
) -> str:
    """도구 호출에 재시도, 타임아웃, 오류 처리를 적용합니다."""
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            start = time.time()
            result = tool.func(**args)
            elapsed = time.time() - start

            if elapsed > timeout_sec:
                return (
                    f"경고: 도구 '{tool.name}'가 응답했지만 {elapsed:.1f}초 소요됨 "
                    f"(기준: {timeout_sec}초). 결과: {result}"
                )
            return result

        except Exception as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(0.5 * (attempt + 1))
            continue

    # 모든 재시도 실패 시 에이전트가 이해할 수 있는 관찰로 변환
    return (
        f"도구 '{tool.name}' 실행 실패 (시도 {max_retries + 1}회): "
        f"{type(last_error).__name__}: {str(last_error)}. "
        "다른 접근 방법을 시도하거나 사용자에게 알려주세요."
    )
```

## 실습 4: 도구 호출 추적과 재현

에이전트 디버깅을 위해 모든 도구 호출과 관찰 결과를 구조화 로그로 남깁니다.

```python
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class ToolCallRecord:
    iteration: int
    tool_name: str
    args: dict
    observation: str
    status: str
    elapsed_ms: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class AgentRunRecord:
    run_id: str
    user_query: str
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    final_answer: str = ""
    iterations_used: int = 0
    stopped_reason: str = ""
    total_elapsed_ms: float = 0.0

    def to_json(self) -> str:
        return json.dumps(
            {
                "run_id": self.run_id,
                "query": self.user_query,
                "tool_calls": [
                    {
                        "iter": tc.iteration,
                        "tool": tc.tool_name,
                        "status": tc.status,
                        "elapsed_ms": tc.elapsed_ms,
                    }
                    for tc in self.tool_calls
                ],
                "iterations": self.iterations_used,
                "stopped": self.stopped_reason,
            },
            ensure_ascii=False,
            indent=2,
        )


def run_agent_with_trace(user_query: str, max_iterations: int = 5) -> AgentRunRecord:
    """실행 추적이 포함된 에이전트를 실행합니다."""
    import uuid
    record = AgentRunRecord(
        run_id=str(uuid.uuid4())[:8],
        user_query=user_query,
    )
    start_total = time.time()

    # ... (run_agent 로직 통합)
    result = run_agent(user_query, max_iterations, verbose=False)

    for i, tc in enumerate(result.get("tool_calls", [])):
        record.tool_calls.append(
            ToolCallRecord(
                iteration=i + 1,
                tool_name=tc["tool"],
                args=tc["args"],
                observation="",  # 실제 구현에서는 observation 포함
                status=tc["status"],
                elapsed_ms=0,
            )
        )

    record.final_answer = result["answer"]
    record.iterations_used = result["iterations"]
    record.stopped_reason = result["stopped_reason"]
    record.total_elapsed_ms = (time.time() - start_total) * 1000

    return record
```

## 역할별 도구 권한 제어

프로덕션에서는 모든 사용자에게 모든 도구를 열어 주지 않습니다.

```python
ROLE_TOOL_POLICY = {
    "viewer": {"query_sales_data", "calculate"},
    "analyst": {"query_sales_data", "calculate", "send_slack_message"},
    "admin": {"query_sales_data", "calculate", "send_slack_message"},
}


def get_tools_for_role(role: str) -> list[dict]:
    """역할에 허용된 도구만 반환합니다."""
    allowed_names = ROLE_TOOL_POLICY.get(role, set())
    all_tools = registry.list_tools()
    return [t for t in all_tools if t["function"]["name"] in allowed_names]
```

## 운영 체크리스트

- [ ] 모든 도구에 입력 유효성 검사가 있습니다.
- [ ] max_iterations로 무한 루프를 방지합니다.
- [ ] 도구 호출 이력이 구조화 로그로 남습니다.
- [ ] 위험한 도구(외부 전송, 데이터 수정)에 사전 승인 단계가 있습니다.
- [ ] 도구 실행 타임아웃이 설정되어 있습니다.
- [ ] 역할별 도구 접근 제어가 구현되어 있습니다.
- [ ] 에이전트 실행 결과가 재현 가능한 형태로 저장됩니다.

## 자주 하는 실수

| 실수 | 증상 | 해결 방법 |
|---|---|---|
| max_iterations 설정 없음 | 에이전트가 무한 루프에 빠짐 | 5-10회 제한 설정 필수 |
| 도구 설명이 모호함 | 에이전트가 잘못된 도구를 선택 | "언제 쓰는가"와 "언제 쓰지 않는가"를 모두 설명 |
| 오류를 exception으로만 처리 | 에이전트가 복구 불가, 루프 중단 | 오류를 observation 문자열로 반환해 재시도 유도 |
| 도구 사이드 이펙트 미공개 | Slack 전송, DB 수정 등 예상치 못한 동작 | 설명에 사이드 이펙트 명시 |
| 도구 인자 검증 없음 | 잘못된 인자로 외부 API 호출 | Pydantic으로 입력 스키마 검증 |
| 모든 사용자에게 모든 도구 허용 | 권한 없는 사용자가 민감 도구 호출 | 역할별 도구 허용 목록 구현 |
| 도구 타임아웃 없음 | 외부 API 지연이 에이전트 루프 전체를 블록 | 도구별 timeout 설정 및 safe_tool_call 래퍼 사용 |
| 실행 추적 없음 | 에이전트 실패 시 어느 단계에서 무엇이 잘못됐는지 불명 | tool_calls_log와 AgentRunRecord 저장 필수 |

## 처음 질문으로 돌아가기

- **ReAct 패턴에서 각 단계의 역할은 무엇일까요?**
  Thought(생각) 단계에서 LLM이 상황을 분석하고 계획을 세웁니다. Action 단계에서 도구를 선택하고 호출합니다. Observation 단계에서 도구 결과를 받아 다음 Thought에 반영합니다. 이 루프가 반복되면서 목표에 점진적으로 접근합니다.

- **도구 오류가 발생했을 때 에이전트가 복구하는 방법은 무엇일까요?**
  오류를 exception으로 처리하지 말고, 에이전트가 이해할 수 있는 observation 문자열로 변환합니다. 에이전트는 오류 메시지를 보고 다른 도구를 시도하거나 사용자에게 문제를 안내할 수 있습니다.

- **에이전트가 무한 루프에 빠지는 것을 어떻게 방지할 수 있을까요?**
  max_iterations로 루프 횟수를 제한하고, 반복 횟수 초과 시 현재까지의 결과로 답변을 완성합니다. 같은 도구를 동일한 인자로 연속 호출하는 패턴을 감지해 루프를 강제 종료하는 로직도 추가할 수 있습니다.

- **프로덕션 에이전트에서 반드시 로깅해야 할 정보는 무엇일까요?**
  run_id, 사용자 쿼리, 각 도구 호출(이름/인자/결과/상태), iteration 수, 종료 이유, 총 실행 시간을 구조화 로그로 남겨야 합니다. 이 데이터로 실패를 재현하고 도구 선택 오류를 분석할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI App Patterns 101 (1/6): Chatbot 패턴](./01-chatbot-pattern.md)
- [AI App Patterns 101 (2/6): RAG QA 패턴](./02-rag-qa-pattern.md)
- [AI App Patterns 101 (3/6): Document Assistant 패턴](./03-document-assistant.md)
- **AI App Patterns 101 (4/6): Agent Tool 패턴 (현재 글)**
- [AI App Patterns 101 (5/6): Workflow Automation 패턴](./05-workflow-automation.md)
- [AI App Patterns 101 (6/6): Human-in-the-Loop 패턴](./06-human-in-the-loop.md)

<!-- toc:end -->

## 참고 자료

- [OpenAI — Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [ReAct — Synergizing Reasoning and Acting in LLMs](https://arxiv.org/abs/2210.03629)
- [LangChain — Agents](https://python.langchain.com/docs/modules/agents/)
- [Anthropic — Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [book-examples — ai-app-patterns-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/ai-app-patterns-101/ko)

Tags: Agent, ReAct, ToolCalling, LLM, Autonomous
