---
title: "AI Agent 101 (8/10): 에러 처리와 안정성"
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

# AI Agent 101 (8/10): 에러 처리와 안정성

agent는 실패하기 쉽습니다. LLM 응답이 형식을 어길 수 있고, 외부 API가 느리거나 죽을 수 있고, 사용자가 잘못된 입력을 줄 수 있고, workflow가 잘못된 판단을 반복할 수도 있습니다. 즉, agent는 여러 불확실성이 겹친 시스템입니다.

이 글은 AI Agent 101 시리즈의 8번째 글입니다.

그래서 신뢰성은 나중에 덧붙이는 옵션이 아닙니다. 처음부터 어떤 에러가 retry 가능하고 어떤 에러는 즉시 중단해야 하는지, 언제 fallback하고 언제 사람에게 넘길지, 사용자에게는 어떤 형태로 실패를 드러낼지 설계해야 합니다.

많은 팀이 reliability를 model accuracy의 하위 문제처럼 다루지만 실제 운영에서는 정반대입니다. 정확도가 조금 낮아도 예측 가능하게 실패하는 시스템이, 정확도가 높지만 가끔 무너지는 시스템보다 훨씬 다루기 쉽습니다.

이 글에서는 reliability를 "에러를 없애는 일"이 아니라 "에러를 분류하고 제어하는 일"로 정리하겠습니다.

![신뢰성 제어 루프](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/08/08-01-reliability-control-loop.ko.png)
*신뢰성 제어 루프*
> Reliable agent는 실패하지 않는 agent가 아니라, 실패를 감지하고 제한하고 설명 가능한 방식으로 멈추는 agent입니다.

## 먼저 던지는 질문

- agent 신뢰성을 볼 때 실패를 없애는 대신 무엇을 제어해야 할까요?
- Retry, fallback, circuit breaker는 각각 어떤 종류의 실패에 맞을까요?
- tool 실행을 안전하게 만들려면 실패 전후에 어떤 guard가 필요할까요?

## 왜 이 글이 중요한가

agent는 성공 경로만 설계해서는 배포할 수 없습니다. 외부 검색 API 하나만 붙어도 timeout, rate limit, malformed output, auth failure 같은 문제가 생기고, 여기에 LLM의 비결정성과 tool schema 오류까지 더해집니다. 에러를 기본값으로 받아들이지 않으면 운영 중 바로 흔들립니다.

또한 reliability 설계는 비용 절감과도 연결됩니다. retry를 무분별하게 걸면 시스템 부하와 토큰 비용이 함께 오르고, fallback이 없으면 사소한 장애가 사용자 체감 장애로 번집니다. 따라서 신뢰성은 안정성뿐 아니라 단가 문제이기도 합니다.

무엇보다 좋은 reliability 설계는 나중 평가와 관측성의 기초가 됩니다. 어떤 에러가 어디서 얼마나 발생했고, 어떤 fallback이 얼마나 자주 동작했고, 어떤 요청이 circuit breaker에 막혔는지 남겨야 개선이 가능합니다.

## 핵심 관점

운영에서 중요한 것은 실패를 0으로 만드는 일이 아닙니다. 실제로는 불가능합니다. 더 중요한 것은 실패가 났을 때 시스템이 예측 가능한 형태로 멈추거나, 줄어든 기능으로라도 응답하거나, 안전하게 재시도하도록 만드는 것입니다.

이 관점이 있으면 에러 처리도 더 단순해집니다. 모든 예외를 뭉뚱그려 잡는 대신, 파싱 실패인지, 네트워크 실패인지, 사용자 입력 오류인지, 권한 문제인지 분리해서 생각하게 됩니다. 그래야 retry 가능 여부도 구체적으로 판단할 수 있습니다.

현업에서는 "실패했지만 왜 실패했는지 설명 가능하고, 다음 동작이 정의되어 있는가"가 reliability의 핵심 기준입니다.

> reliable agent는 실패하지 않는 agent가 아니라, 실패를 분류하고 제한하며 사용자와 운영자 모두에게 예측 가능한 방식으로 드러내는 agent입니다.

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
    # 1. 마크다운 코드 펜스 제거
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        # ```json ... ``` 또는 ``` ... ``` 제거
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    # 2. 파싱 시도
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
        # 인자가 잘못된 경우에는 같은 args로 재시도해도 성공하지 않습니다.
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

## 실전 설계 보강

### 오류를 예외 처리 문법이 아니라 분류 체계로 다룹니다

agent 신뢰성은 try/except 개수보다 오류 분류 체계에 달려 있습니다. 운영에서는 최소한 아래 네 범주를 분리해야 합니다.

| 범주 | 예시 | 기본 정책 |
| --- | --- | --- |
| 입력 오류 | 필수 필드 누락, 잘못된 타입 | 즉시 실패, 사용자 수정 요청 |
| 일시 오류 | 네트워크 타임아웃, 429 | backoff 재시도 |
| 영구 오류 | 권한 없음, 미등록 도구 | 즉시 중단 |
| 정책 오류 | 안전 규칙 위반 | 차단 + 감사 로그 |

### 재시도 래퍼 예시

```python
import time

def with_retry(fn, max_attempts=3, base_sleep=0.4):
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except TimeoutError:
            if attempt == max_attempts:
                raise
            time.sleep(base_sleep * (2 ** (attempt - 1)))
```

재시도는 만능이 아닙니다. 영구 오류에 재시도를 걸면 지연만 늘어나고, 정책 오류에 재시도를 걸면 사고 가능성이 커집니다. 오류 타입별로 재시도 가능 여부를 분리해야 합니다.

### Circuit Breaker 상태 머신

```text
closed -> (오류율 초과) -> open
open   -> (cooldown 경과) -> half_open
half_open -> (성공) -> closed
half_open -> (실패) -> open
```

외부 도구가 불안정할 때 circuit breaker가 없으면 agent 전체가 연쇄 지연에 빠집니다. 특히 멀티 도구 환경에서 필수입니다.

### 신뢰성 SLI/SLO 예시

| SLI | 정의 | SLO |
| --- | --- | --- |
| run_success | goal_achieved 비율 | 99% |
| timeout_rate | 런타임 타임아웃 비율 | 1% 이하 |
| safe_abort_rate | 안전 중단 후 복구 가능 비율 | 95% 이상 |

신뢰성은 기능의 부가 요소가 아니라 제품의 기본 품질입니다. SLO를 숫자로 두지 않으면 운영 판단이 감각에 의존하게 됩니다.

## 심화 운영 노트

### 운영 관점 실패 분류 템플릿

실전에서는 실패를 "모델이 틀렸다" 한 문장으로 닫지 않습니다. 다음 템플릿처럼 실패 축을 분리하면 개선 우선순위가 명확해집니다.

| 분류 축 | 질문 | 예시 |
| --- | --- | --- |
| 계획 실패 | 목표를 잘못 분해했는가 | 불필요한 step 6회 반복 |
| 실행 실패 | 도구 호출이 실패했는가 | timeout, 429, schema mismatch |
| 검증 실패 | 결과 확인이 부족했는가 | 잘못된 observation 채택 |
| 정책 실패 | 안전 경계를 넘었는가 | 민감 데이터 외부 전송 시도 |

이 표를 runbook에 고정해 두면 온콜 엔지니어가 같은 기준으로 사고를 분류할 수 있습니다.

### 프롬프트/도구 버전 고정 전략

변경 추적이 어려운 팀은 대부분 프롬프트와 도구 스키마를 코드 릴리스와 분리해 관리합니다. 안정적인 팀은 아래처럼 버전 필드를 요청 컨텍스트에 명시합니다.

```json
{
  "run_id": "run_2026_05_21_001",
  "model": "gpt-4.1-mini",
  "prompt_version": "agent-101-ko-v3",
  "tool_schema_version": "tools-v5",
  "policy_version": "policy-2026-05"
}
```

버전 필드만 있어도 회귀 분석 속도가 크게 빨라집니다. 특정 시점의 품질 저하가 모델 변경인지, 프롬프트 변경인지, 도구 변경인지 즉시 좁힐 수 있기 때문입니다.

### 관측성 이벤트 예시

```python
import json
from datetime import datetime

def emit_event(event_type: str, payload: dict):
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "payload": payload,
    }
    print(json.dumps(record, ensure_ascii=False))

emit_event("agent.step", {"step": 2, "tool": "search_docs", "latency_ms": 412})
```

구조화 로그를 먼저 도입하면 추후 OpenTelemetry, ELK, Grafana 같은 스택으로 확장할 때 마이그레이션 비용이 낮아집니다.

### 배포 체크 항목

- 모델 API 키를 환경 변수와 Secret Manager로 분리했는지 확인합니다.
- `max_steps`, `timeout_ms`, `retry_budget` 기본값이 운영 프로필에 맞는지 검증합니다.
- 장애 시 fallback 응답 문구가 사용자에게 과장된 확신을 주지 않는지 점검합니다.
- 알람 임계치(`error_rate`, `p95_latency`, `policy_violation_rate`)를 문서와 코드에서 동일하게 유지합니다.

이 항목은 기능 개발보다 눈에 덜 띄지만, 실제 장애 빈도를 줄이는 데 직접적으로 기여합니다.

### 비용 통제 포인트

| 항목 | 설명 | 권장 기본값 |
| --- | --- | --- |
| max_steps | 1회 실행당 최대 루프 | 4~8 |
| max_tool_calls | 도구 호출 상한 | 3~6 |
| input_token_budget | 입력 토큰 예산 | 서비스별 정책 |
| output_token_budget | 출력 토큰 예산 | 서비스별 정책 |

비용 통제는 성능 최적화 이후에 붙이는 부가기능이 아닙니다. 처음부터 실행 예산을 고정해야 사용량 급증 시 서비스가 안정적으로 유지됩니다.

### 품질 회귀를 막는 CI 게이트 예시

```bash
python3 scripts/eval_agent.py --dataset eval/agent_core_ko.jsonl --min-success 0.82
python3 scripts/check_tool_schema.py --strict
python3 scripts/check_prompt_version.py --require-changelog
```

배포 파이프라인에서 최소 품질 게이트를 자동화하면 "우연히 좋아 보이는 빌드"가 운영으로 유입되는 일을 줄일 수 있습니다.

### 운영 관점 실패 분류 템플릿

실전에서는 실패를 "모델이 틀렸다" 한 문장으로 닫지 않습니다. 다음 템플릿처럼 실패 축을 분리하면 개선 우선순위가 명확해집니다.

| 분류 축 | 질문 | 예시 |
| --- | --- | --- |
| 계획 실패 | 목표를 잘못 분해했는가 | 불필요한 step 6회 반복 |
| 실행 실패 | 도구 호출이 실패했는가 | timeout, 429, schema mismatch |
| 검증 실패 | 결과 확인이 부족했는가 | 잘못된 observation 채택 |
| 정책 실패 | 안전 경계를 넘었는가 | 민감 데이터 외부 전송 시도 |

이 표를 runbook에 고정해 두면 온콜 엔지니어가 같은 기준으로 사고를 분류할 수 있습니다.

### 프롬프트/도구 버전 고정 전략

변경 추적이 어려운 팀은 대부분 프롬프트와 도구 스키마를 코드 릴리스와 분리해 관리합니다. 안정적인 팀은 아래처럼 버전 필드를 요청 컨텍스트에 명시합니다.

```json
{
  "run_id": "run_2026_05_21_001",
  "model": "gpt-4.1-mini",
  "prompt_version": "agent-101-ko-v3",
  "tool_schema_version": "tools-v5",
  "policy_version": "policy-2026-05"
}
```

버전 필드만 있어도 회귀 분석 속도가 크게 빨라집니다. 특정 시점의 품질 저하가 모델 변경인지, 프롬프트 변경인지, 도구 변경인지 즉시 좁힐 수 있기 때문입니다.

### 관측성 이벤트 예시

```python
import json
from datetime import datetime

def emit_event(event_type: str, payload: dict):
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "payload": payload,
    }
    print(json.dumps(record, ensure_ascii=False))

emit_event("agent.step", {"step": 2, "tool": "search_docs", "latency_ms": 412})
```

구조화 로그를 먼저 도입하면 추후 OpenTelemetry, ELK, Grafana 같은 스택으로 확장할 때 마이그레이션 비용이 낮아집니다.

### 배포 체크 항목

- 모델 API 키를 환경 변수와 Secret Manager로 분리했는지 확인합니다.
- `max_steps`, `timeout_ms`, `retry_budget` 기본값이 운영 프로필에 맞는지 검증합니다.
- 장애 시 fallback 응답 문구가 사용자에게 과장된 확신을 주지 않는지 점검합니다.
- 알람 임계치(`error_rate`, `p95_latency`, `policy_violation_rate`)를 문서와 코드에서 동일하게 유지합니다.

이 항목은 기능 개발보다 눈에 덜 띄지만, 실제 장애 빈도를 줄이는 데 직접적으로 기여합니다.

### 비용 통제 포인트

| 항목 | 설명 | 권장 기본값 |
| --- | --- | --- |
| max_steps | 1회 실행당 최대 루프 | 4~8 |
| max_tool_calls | 도구 호출 상한 | 3~6 |
| input_token_budget | 입력 토큰 예산 | 서비스별 정책 |
| output_token_budget | 출력 토큰 예산 | 서비스별 정책 |

비용 통제는 성능 최적화 이후에 붙이는 부가기능이 아닙니다. 처음부터 실행 예산을 고정해야 사용량 급증 시 서비스가 안정적으로 유지됩니다.

### 품질 회귀를 막는 CI 게이트 예시

```bash
python3 scripts/eval_agent.py --dataset eval/agent_core_ko.jsonl --min-success 0.82
python3 scripts/check_tool_schema.py --strict
python3 scripts/check_prompt_version.py --require-changelog
```

배포 파이프라인에서 최소 품질 게이트를 자동화하면 "우연히 좋아 보이는 빌드"가 운영으로 유입되는 일을 줄일 수 있습니다.

### 운영 관점 실패 분류 템플릿

실전에서는 실패를 "모델이 틀렸다" 한 문장으로 닫지 않습니다. 다음 템플릿처럼 실패 축을 분리하면 개선 우선순위가 명확해집니다.

| 분류 축 | 질문 | 예시 |
| --- | --- | --- |
| 계획 실패 | 목표를 잘못 분해했는가 | 불필요한 step 6회 반복 |
| 실행 실패 | 도구 호출이 실패했는가 | timeout, 429, schema mismatch |
| 검증 실패 | 결과 확인이 부족했는가 | 잘못된 observation 채택 |
| 정책 실패 | 안전 경계를 넘었는가 | 민감 데이터 외부 전송 시도 |

이 표를 runbook에 고정해 두면 온콜 엔지니어가 같은 기준으로 사고를 분류할 수 있습니다.

### 프롬프트/도구 버전 고정 전략

변경 추적이 어려운 팀은 대부분 프롬프트와 도구 스키마를 코드 릴리스와 분리해 관리합니다. 안정적인 팀은 아래처럼 버전 필드를 요청 컨텍스트에 명시합니다.

```json
{
  "run_id": "run_2026_05_21_001",
  "model": "gpt-4.1-mini",
  "prompt_version": "agent-101-ko-v3",
  "tool_schema_version": "tools-v5",
  "policy_version": "policy-2026-05"
}
```

버전 필드만 있어도 회귀 분석 속도가 크게 빨라집니다. 특정 시점의 품질 저하가 모델 변경인지, 프롬프트 변경인지, 도구 변경인지 즉시 좁힐 수 있기 때문입니다.

### 관측성 이벤트 예시

```python
import json
from datetime import datetime

def emit_event(event_type: str, payload: dict):
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "payload": payload,
    }
    print(json.dumps(record, ensure_ascii=False))

emit_event("agent.step", {"step": 2, "tool": "search_docs", "latency_ms": 412})
```

구조화 로그를 먼저 도입하면 추후 OpenTelemetry, ELK, Grafana 같은 스택으로 확장할 때 마이그레이션 비용이 낮아집니다.

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

## 처음 질문으로 돌아가기

- **agent 신뢰성을 볼 때 실패를 없애는 대신 무엇을 제어해야 할까요?**
  - 네트워크, tool, 모델 판단, 출력 형식 실패를 감지하고 확산 범위, 재시도 횟수, 사용자에게 보여 줄 상태를 제어해야 합니다.
- **Retry, fallback, circuit breaker는 각각 어떤 종류의 실패에 맞을까요?**
  - Retry는 일시적 실패, fallback은 품질을 낮춰도 계속해야 하는 실패, circuit breaker는 반복 실패나 위험한 외부 호출을 막아야 하는 상황에 맞습니다.
- **tool 실행을 안전하게 만들려면 실패 전후에 어떤 guard가 필요할까요?**
  - 실행 전에는 허용 도구, 인자, 권한, timeout을 검증하고 실행 후에는 에러 형식, partial result, 재시도 여부, 사용자 안내를 정해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Agent 101 (1/10): AI Agent란 무엇인가?](./01-what-is-an-ai-agent.md)
- [AI Agent 101 (2/10): 컨텍스트 엔지니어링](./02-context-engineering.md)
- [AI Agent 101 (3/10): Tool Use 기초](./03-tool-use-fundamentals.md)
- [AI Agent 101 (4/10): Agent Workflow 설계](./04-agent-workflow-design.md)
- [AI Agent 101 (5/10): Memory와 State](./05-memory-and-state.md)
- [AI Agent 101 (6/10): Multi-Agent 시스템](./06-multi-agent-systems.md)
- [AI Agent 101 (7/10): Agent 평가](./07-agent-evaluation.md)
- **AI Agent 101 (8/10): 에러 처리와 안정성 (현재 글)**
- AI Agent 101 (9/10): 운영 (예정)
- AI Agent 101 (10/10): 첫 Agent 만들기 (예정)

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

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-agent-101/ko/08-error-handling-reliability)

Tags: AI Agent, LLM, Tool Use, Python
