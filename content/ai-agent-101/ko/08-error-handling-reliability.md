---
title: 에러 처리와 안정성
series: ai-agent-101
episode: 8
language: ko
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Error Handling
- Reliability
- Retry Logic
last_reviewed: '2026-05-02'
---

# 에러 처리와 안정성

> AI Agent 101 시리즈 (8/10)

Agent는 외부 도구를 호출하고, 네트워크를 거치고, 모델의 불확실한 판단에 의존하기 때문에 실패할 수 있습니다. API 타임아웃, 잘못된 도구 파라미터, 모델의 환각, 예상치 못한 응답 형식 등 다양한 실패 모드가 존재합니다.

신뢰할 수 있는 Agent를 만들려면 이런 실패를 예측하고 대응해야 합니다. Retry 전략, Fallback 패턴, Timeout 처리, Graceful Degradation이 핵심입니다.

이번 글에서는 Agent의 일반적인 실패 모드, Retry 전략, Fallback 패턴, Timeout 처리 방법, 그리고 Graceful Degradation을 다룹니다.

---

## Agent에서의 에러 유형

Agent는 LLM, 도구, 외부 API, 사용자 입력 등 여러 컴포넌트가 얽혀 있어 에러 유형이 다양합니다.

### LLM 응답 에러

LLM 자체의 비결정성, 형식 오류, 환각이 가장 흔한 에러원입니다.

```python
import json
from typing import Optional

class LLMResponseError(Exception):
    """LLM 응답 관련 에러."""
    pass

def parse_llm_json(response_text: str) -> dict:
    """LLM이 반환한 JSON을 안전하게 파싱."""
    # 1. 마크다운 코드 블록 제거
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        # ```json ... ``` 또는 ``` ... ``` 제거
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    # 2. JSON 파싱 시도
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise LLMResponseError(f"JSON 파싱 실패: {e}\n원본: {response_text[:200]}")

# 사용 예시
response = '```json\n{"action": "search", "query": "Python"}\n```'
try:
    parsed = parse_llm_json(response)
except LLMResponseError as e:
    # 재시도 로직으로 분기
    pass
```

LLM 응답을 항상 검증하고 파싱 실패에 대한 대응 경로를 마련해야 합니다.

### 도구 호출 에러

도구 자체의 실패, 타임아웃, 외부 API 장애 등이 포함됩니다.

```python
import requests
from typing import Any

class ToolExecutionError(Exception):
    """도구 실행 실패."""
    def __init__(self, tool_name: str, reason: str, recoverable: bool = True):
        self.tool_name = tool_name
        self.reason = reason
        self.recoverable = recoverable
        super().__init__(f"{tool_name} 실패: {reason}")

def execute_tool_safely(tool_name: str, tool_fn, **kwargs) -> Any:
    """도구를 안전하게 실행."""
    try:
        return tool_fn(**kwargs)
    except requests.Timeout:
        raise ToolExecutionError(tool_name, "타임아웃", recoverable=True)
    except requests.ConnectionError:
        raise ToolExecutionError(tool_name, "네트워크 연결 실패", recoverable=True)
    except ValueError as e:
        # 잘못된 인자 — 같은 인자로 재시도해도 실패
        raise ToolExecutionError(tool_name, f"잘못된 인자: {e}", recoverable=False)
    except Exception as e:
        raise ToolExecutionError(tool_name, f"예상치 못한 에러: {e}", recoverable=False)
```

`recoverable` 플래그로 재시도 가능 여부를 구분하면 상위에서 적절히 대응할 수 있습니다.

### 사용자 입력 에러

악의적 입력, 모호한 요청, 컨텍스트 윈도우 초과 등이 발생합니다.

```python
class UserInputError(Exception):
    pass

def validate_user_input(text: str, max_chars: int = 10000) -> str:
    """사용자 입력 검증."""
    if not text or not text.strip():
        raise UserInputError("빈 입력")
    if len(text) > max_chars:
        raise UserInputError(f"입력이 너무 깁니다 ({len(text)}자, 최대 {max_chars}자)")
    return text.strip()
```

검증되지 않은 입력은 LLM 비용 폭탄과 보안 사고로 이어집니다.

## Retry 패턴

가장 기본적인 안정성 메커니즘입니다. Exponential backoff가 표준입니다.

```python
import time
import random
from typing import Callable, Type, Tuple

def retry_with_backoff(
    fn: Callable,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Exponential backoff로 재시도."""
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

            print(f"시도 {attempt + 1} 실패: {e}. {delay:.1f}초 후 재시도")
            time.sleep(delay)

    raise last_exception

# 사용 예시
def call_flaky_api():
    response = requests.get("https://api.example.com/data", timeout=5)
    response.raise_for_status()
    return response.json()

result = retry_with_backoff(
    call_flaky_api,
    max_attempts=5,
    retryable_exceptions=(requests.Timeout, requests.ConnectionError)
)
```

주의: `recoverable=False` 에러까지 재시도하면 시스템 부하만 키우고 결과는 같습니다.

## Fallback과 Graceful Degradation

주 경로가 실패해도 부분적으로 응답하는 능력이 사용자 경험을 크게 좌우합니다.

```python
class FallbackChain:
    """순차적으로 fallback을 시도."""

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
        raise RuntimeError(f"모든 핸들러 실패: {errors}")

# 사용 예시
def primary_search(query):
    return external_search_api(query)

def cached_search(query):
    return cache.get(f"search:{query}") or []

def degraded_search(query):
    return [{"text": f"'{query}' 검색은 일시적으로 사용할 수 없습니다.", "fallback": True}]

chain = (FallbackChain()
    .add(primary_search, "primary")
    .add(cached_search, "cache")
    .add(degraded_search, "degraded"))

result = chain.execute("Python tutorial")
# 1차 실패 시 캐시, 캐시도 실패 시 안내 메시지 반환
```

Graceful degradation은 "나쁜 응답" 대신 "정직한 한정 응답"을 제공합니다.

## Circuit Breaker 패턴

특정 서비스가 계속 실패할 때 일시적으로 차단해 시스템 전체 부하를 막습니다.

```python
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"      # 정상
    OPEN = "open"          # 차단
    HALF_OPEN = "half_open"  # 시험 호출

class CircuitBreaker:
    """Circuit Breaker."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0

    def call(self, fn: Callable, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise RuntimeError("Circuit breaker OPEN")

        try:
            result = fn(*args, **kwargs)
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# 사용 예시
breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

try:
    result = breaker.call(external_api_call, "param")
except RuntimeError as e:
    # Circuit이 열렸으므로 fallback 사용
    result = cached_value
```

Circuit breaker는 외부 API 의존성이 많은 Agent에 필수적입니다.

## 안전한 도구 실행

도구 실행 시 시간/리소스 제한을 두지 않으면 한 번의 실패가 전체 시스템을 마비시킬 수 있습니다.

```python
import signal
from contextlib import contextmanager

class TimeoutError(Exception):
    pass

@contextmanager
def time_limit(seconds: int):
    """함수 실행 시간 제한."""
    def signal_handler(signum, frame):
        raise TimeoutError(f"실행이 {seconds}초를 초과")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

def run_tool_with_limits(tool_fn, *args, timeout: int = 30, **kwargs):
    """타임아웃과 예외 처리를 포함한 도구 실행."""
    try:
        with time_limit(timeout):
            return tool_fn(*args, **kwargs)
    except TimeoutError as e:
        raise ToolExecutionError("tool", str(e), recoverable=True)
    except Exception as e:
        raise ToolExecutionError("tool", str(e), recoverable=False)
```

도구별로 적절한 타임아웃을 설정해야 합니다.

## 흔한 실수 5가지

### 실수 1: 모든 에러를 재시도

```python
# 나쁜 예
for _ in range(5):
    try:
        return call_api(invalid_args)  # 잘못된 인자는 재시도해도 실패
    except Exception:
        time.sleep(1)

# 좋은 예
try:
    return call_api(args)
except (Timeout, ConnectionError):
    return retry_with_backoff(lambda: call_api(args))
except ValueError:
    raise  # 재시도 불가
```

복구 불가능한 에러는 빠르게 실패시켜야 합니다.

### 실수 2: 무한 재시도

```python
# 나쁜 예
while True:
    try:
        return call_api()
    except Exception:
        time.sleep(1)  # 영원히 반복

# 좋은 예
return retry_with_backoff(call_api, max_attempts=5)
```

반드시 최대 시도 횟수와 시간 제한을 둡니다.

### 실수 3: Fallback 없이 단일 경로 의존

```python
# 나쁜 예
def search(query):
    return external_api.search(query)  # API 죽으면 전체 다운

# 좋은 예
def search(query):
    try:
        return external_api.search(query)
    except Exception:
        return cache.get(query) or []  # 최소한 캐시라도
```

핵심 기능에는 항상 fallback을 제공합니다.

### 실수 4: 에러를 조용히 삼키기

```python
# 나쁜 예
try:
    result = risky_operation()
except Exception:
    pass  # 무시 — 디버깅 불가능

# 좋은 예
try:
    result = risky_operation()
except Exception as e:
    logger.error(f"risky_operation 실패: {e}", exc_info=True)
    metrics.increment("risky_operation.failures")
    raise
```

에러는 항상 로그와 메트릭에 기록합니다.

### 실수 5: 사용자에게 raw 에러 노출

```python
# 나쁜 예
return {"error": str(exception)}  # 내부 구조, 스택 트레이스 노출

# 좋은 예
return {
    "error": "요청을 처리할 수 없습니다",
    "request_id": req_id,  # 내부 추적용
}
# 상세 정보는 서버 로그에만
```

사용자에게는 친화적 메시지, 내부 추적 ID는 별도로 관리합니다.

## 핵심 요약

- Agent 에러는 LLM 응답, 도구 호출, 사용자 입력 등 여러 층에서 발생합니다
- Retry는 exponential backoff와 jitter를 함께 사용하고, 복구 가능 여부를 구분합니다
- Fallback과 graceful degradation으로 부분 응답이라도 제공합니다
- Circuit breaker는 반복 실패하는 외부 의존성으로부터 시스템을 보호합니다
- 도구 실행에는 항상 타임아웃과 리소스 제한을 둡니다
- 에러는 조용히 삼키지 말고 로그·메트릭으로 가시화합니다

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

1. **Release It! Design and Deploy Production-Ready Software** - Michael Nygard - https://pragprog.com/titles/mnee2/release-it-second-edition/  
   Circuit breaker, bulkhead, timeout 등 안정성 패턴의 고전. Agent 시스템에도 그대로 적용됩니다.

2. **AWS Builders' Library: Timeouts, retries, and backoff with jitter** - https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/  
   AWS의 재시도/백오프 모범 사례. Jitter의 필요성과 구체적인 알고리즘을 설명합니다.

3. **OpenAI: Production Best Practices** - https://platform.openai.com/docs/guides/production-best-practices  
   OpenAI 공식 운영 가이드. Rate limit, 에러 코드, 재시도 정책을 다룹니다.

4. **Hystrix: Latency and Fault Tolerance** - https://github.com/Netflix/Hystrix/wiki  
   Netflix의 circuit breaker 라이브러리 문서. 패턴의 핵심 개념과 운영 사례를 제공합니다.

Tags: AI Agent, LLM, Tool Use, Python
