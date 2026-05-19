---
title: 에러 처리와 안정성
series: ai-agent-101
episode: 8
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Error Handling
- Reliability
- Retry Logic
last_reviewed: '2026-05-12'
seo_description: retry, fallback, circuit breaker로 agent 신뢰성을 설계하는 법을 설명합니다.
---

# 에러 처리와 안정성

agent는 실패하기 쉽습니다. LLM 응답이 형식을 어길 수 있고, 외부 API가 느리거나 죽을 수 있고, 사용자가 잘못된 입력을 줄 수 있고, workflow가 잘못된 판단을 반복할 수도 있습니다. 즉, agent는 여러 불확실성이 겹친 시스템입니다.

그래서 신뢰성은 나중에 덧붙이는 옵션이 아닙니다. 처음부터 어떤 에러가 retry 가능하고 어떤 에러는 즉시 중단해야 하는지, 언제 fallback하고 언제 사람에게 넘길지, 사용자에게는 어떤 형태로 실패를 드러낼지 설계해야 합니다.

많은 팀이 reliability를 model accuracy의 하위 문제처럼 다루지만 실제 운영에서는 정반대입니다. 정확도가 조금 낮아도 예측 가능하게 실패하는 시스템이, 정확도가 높지만 가끔 무너지는 시스템보다 훨씬 다루기 쉽습니다.

이 글은 AI Agent 101 시리즈의 여덟 번째 글입니다.

이 글에서는 reliability를 "에러를 없애는 일"이 아니라 "에러를 분류하고 제어하는 일"로 정리하겠습니다.

## 이 글에서 다룰 문제

- agent에서 자주 발생하는 에러를 어떤 축으로 분류하면 좋을까요?
- retry와 fallback은 언제 서로를 대체하고 언제 함께 써야 할까요?
- recoverable error와 non-recoverable error를 어떻게 나눌 수 있을까요?
- circuit breaker와 timeout은 왜 tool use 계층에서 특히 중요할까요?
- 사용자에게 좋은 graceful degradation은 어떤 모습이어야 할까요?

## 왜 이 글이 중요한가

agent는 성공 경로만 설계해서는 배포할 수 없습니다. 외부 검색 API 하나만 붙어도 timeout, rate limit, malformed output, auth failure 같은 문제가 생기고, 여기에 LLM의 비결정성과 tool schema 오류까지 더해집니다. 에러를 기본값으로 받아들이지 않으면 운영 중 바로 흔들립니다.

또한 reliability 설계는 비용 절감과도 연결됩니다. retry를 무분별하게 걸면 시스템 부하와 토큰 비용이 함께 오르고, fallback이 없으면 사소한 장애가 사용자 체감 장애로 번집니다. 따라서 신뢰성은 안정성뿐 아니라 단가 문제이기도 합니다.

무엇보다 좋은 reliability 설계는 나중 평가와 관측성의 기초가 됩니다. 어떤 에러가 어디서 얼마나 발생했고, 어떤 fallback이 얼마나 자주 동작했고, 어떤 요청이 circuit breaker에 막혔는지 남겨야 개선이 가능합니다.

## 신뢰성을 이해하는 가장 좋은 방법: 실패를 제거하는 것이 아니라 제어하는 것으로 보는 것입니다

운영에서 중요한 것은 실패를 0으로 만드는 일이 아닙니다. 실제로는 불가능합니다. 더 중요한 것은 실패가 났을 때 시스템이 예측 가능한 형태로 멈추거나, 줄어든 기능으로라도 응답하거나, 안전하게 재시도하도록 만드는 것입니다.

이 관점이 있으면 에러 처리도 더 단순해집니다. 모든 예외를 뭉뚱그려 잡는 대신, 파싱 실패인지, 네트워크 실패인지, 사용자 입력 오류인지, 권한 문제인지 분리해서 생각하게 됩니다. 그래야 retry 가능 여부도 구체적으로 판단할 수 있습니다.

현업에서는 "실패했지만 왜 실패했는지 설명 가능하고, 다음 동작이 정의되어 있는가"가 reliability의 핵심 기준입니다.

> reliable agent는 실패하지 않는 agent가 아니라, 실패를 분류하고 제한하며 사용자와 운영자 모두에게 예측 가능한 방식으로 드러내는 agent입니다.

### 신뢰성 제어 루프

![신뢰성 제어 루프](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/08/08-01-reliability-control-loop.ko.png)
## 핵심 개념

### LLM 응답 에러는 가장 흔한 입력 실패입니다

```python
import json
from typing import Optional

class LLMResponseError(Exception):
    """LLM response error."""
    pass

def parse_llm_json(response_text: str) -> dict:
    """Safely parse JSON returned by an LLM."""
    # 1. Strip markdown code fences
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        # Remove ```json ... ``` or ``` ... ```
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    # 2. Try to parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise LLMResponseError(f"JSON parse failed: {e}\nraw: {response_text[:200]}")
```

structured output를 요구하는 agent에서는 파싱 실패가 곧 workflow 실패로 이어질 수 있습니다. 따라서 이 구간은 단순 try/except가 아니라 retry 분기와 telemetry가 함께 있어야 합니다.

### tool 에러는 recoverable 여부를 먼저 나눠야 합니다

```python
import requests
from typing import Any

class ToolExecutionError(Exception):
    """Tool execution failed."""
    def __init__(self, tool_name: str, reason: str, recoverable: bool = True):
        self.tool_name = tool_name
        self.reason = reason
        self.recoverable = recoverable
        super().__init__(f"{tool_name} failed: {reason}")

def execute_tool_safely(tool_name: str, tool_fn, **kwargs) -> Any:
    """Run a tool safely."""
    try:
        return tool_fn(**kwargs)
    except requests.Timeout:
        raise ToolExecutionError(tool_name, "timeout", recoverable=True)
    except requests.ConnectionError:
        raise ToolExecutionError(tool_name, "network connection failed", recoverable=True)
    except ValueError as e:
        # Bad arguments — same args won't succeed on retry
        raise ToolExecutionError(tool_name, f"bad argument: {e}", recoverable=False)
    except Exception as e:
        raise ToolExecutionError(tool_name, f"unexpected error: {e}", recoverable=False)
```

recoverable 구분이 중요한 이유는 retry 정책을 분기하기 위해서입니다. 잘못된 인자를 세 번 더 보내는 것은 복구가 아니라 부하 증가입니다. 반대로 일시적 timeout을 한 번의 실패로 끝내는 것도 아깝습니다.

### retry는 제한된 범위에서만 써야 합니다

```python
import time
import random
from collections.abc import Callable
from typing import Type, Tuple

def retry_with_backoff(
    fn: Callable,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Retry with exponential backoff."""
    last_exception = None

    for attempt in range(max_attempts):
        try:
            return fn()
        except retryable_exceptions as e:
            last_exception = e
            if attempt == max_attempts - 1:
                break

            delay = min(initial_delay * (exponential_base ** attempt), max_delay)
            if jitter:
                delay = delay * (0.5 + random.random())

            print(f"attempt {attempt + 1} failed: {e}. retrying in {delay:.1f}s")
            time.sleep(delay)

    raise last_exception
```

retry는 가장 쉬운 안정성 장치지만 가장 남용되기 쉬운 장치이기도 합니다. recovery 가능성이 없는 에러에 retry를 걸면 단지 더 느리고 더 비싼 실패를 만들 뿐입니다.

### fallback과 graceful degradation은 사용자 경험을 지킵니다

```python
class FallbackChain:
    """Try fallbacks sequentially."""

    def __init__(self):
        self.handlers = []

    def add(self, handler: Callable, name: str):
        self.handlers.append((name, handler))
        return self

    def execute(self, *args, **kwargs):
        errors = []
        for name, handler in self.handlers:
            try:
                result = handler(*args, **kwargs)
                return {"result": result, "source": name, "fallbacks_tried": errors}
            except Exception as e:
                errors.append({"handler": name, "error": str(e)})
        raise RuntimeError(f"all handlers failed: {errors}")
```

fallback은 항상 같은 품질을 보장하지는 않지만, 최소한 솔직한 부분 응답을 가능하게 합니다. 예를 들어 실시간 검색이 실패하면 캐시 결과를 주거나, 그것도 안 되면 제한된 안내 메시지를 줄 수 있습니다. 이 계층이 사용자 신뢰를 크게 좌우합니다.

### 반복 장애에는 circuit breaker가 필요합니다

```python
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"      # normal
    OPEN = "open"          # blocked
    HALF_OPEN = "half_open"  # trial calls
```

외부 서비스가 계속 실패할 때 계속 호출을 밀어 넣으면 전체 시스템이 함께 무너집니다. circuit breaker는 이 전염을 막는 장치입니다. 특히 search, browser, payment 같은 고비용 tool에는 거의 필수에 가깝습니다.

## 흔히 헷갈리는 지점

- 모든 에러에 retry를 거는 것이 안전하다고 생각하기 쉽지만, non-recoverable 에러에는 해롭습니다.
- fallback은 품질 저하라서 없어도 된다고 보기 쉽지만, production에서는 오히려 중요한 신뢰 장치입니다.
- structured output을 요구하면 형식 오류가 사라질 것 같지만, 실제로는 파싱 실패 대비가 여전히 필요합니다.
- timeout은 인프라 문제라고만 생각하기 쉽지만, agent 설계에서 stop condition의 일부입니다.
- 에러 메시지를 숨기는 것이 UX라고 보기 쉽지만, 솔직한 제한 안내가 잘못된 확신보다 낫습니다.

## 운영 체크리스트

- [ ] LLM 응답, tool 실행, 사용자 입력 에러를 별도 클래스로 분리했는가
- [ ] retry 가능 여부를 에러 수준에서 구분하는가
- [ ] fallback과 degraded response 경로가 정의되어 있는가
- [ ] timeout, circuit breaker, max step 제한이 존재하는가
- [ ] 실패 원인과 fallback 사용 여부를 로그와 메트릭으로 남기는가

## 정리

agent reliability는 실패를 없애는 기술이 아니라 실패를 제어하는 기술입니다. 어떤 에러는 다시 시도하고, 어떤 에러는 즉시 멈추고, 어떤 에러는 우회 경로로 처리하며, 어떤 경우에는 사용자에게 제한된 응답을 솔직하게 돌려줘야 합니다.

좋은 reliability 설계는 모델과 도구의 불확실성을 시스템 차원에서 흡수합니다. 그래야 실패가 있더라도 전체 서비스는 예측 가능한 형태를 유지하고, 운영자는 원인을 추적할 수 있습니다.

다음 글에서는 이렇게 설계한 agent를 실제 운영 환경에서 어떻게 관측하고 비용을 관리할지 다룹니다. 안정성 장치가 있어도 보이지 않으면 개선할 수 없기 때문입니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Agent란 무엇인가?](./01-what-is-an-ai-agent.md)
- [컨텍스트 엔지니어링](./02-context-engineering.md)
- [Tool Use 기초](./03-tool-use-fundamentals.md)
- [Agent Workflow 설계](./04-agent-workflow-design.md)
- [Memory와 State](./05-memory-and-state.md)
- [Multi-Agent 시스템](./06-multi-agent-systems.md)
- [Agent 평가](./07-agent-evaluation.md)
- **에러 처리와 안정성 (현재 글)**
- 운영 (예정)
- 첫 Agent 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Google SRE Book - Handling Overload](https://sre.google/sre-book/handling-overload/)
- [OpenAI Platform - Rate limits guide](https://platform.openai.com/docs/guides/rate-limits)
- [Anthropic - Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [Martin Fowler - Circuit Breaker](https://martinfowler.com/bliki/CircuitBreaker.html)

### 관련 시리즈

- [AI Evaluation 101 - 실패 분석과 회귀 검사](../../ai-evaluation-101/ko/08-regression-testing.md)
- [LangGraph 101 - 상태와 재시도](../../langgraph-101/ko/02-state-and-checkpoints.md)

Tags: AI Agent, LLM, Tool Use, Python
