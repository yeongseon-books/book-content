---
episode: 5
language: ko
last_reviewed: '2026-05-15'
series: llm-api-production-101
status: publish-ready
tags:
- LLM
- OpenAI
- Streaming
- Python
targets:
  ebook: true
  medium: false
  mkdocs: true
  tistory: true
title: "LLM API Production 101 (5/6): 재시도와 오류 처리 — 안정적인 API 호출 만들기"
seo_description: tenacity와 오류 분류로 LLM API 재시도 정책을 제한된 복구 전략으로 설계하는 방법을 다룹니다.
---

# LLM API Production 101 (5/6): 재시도와 오류 처리 — 안정적인 API 호출 만들기

LLM API가 실제 운영 경로에 들어가면 실패는 드문 예외가 아니라 런타임의 일부가 됩니다. 네트워크가 잠깐 멈출 수 있고, 공급자 API가 느려질 수 있으며, 요청이 제한 시간 안에 끝나지 않을 수 있습니다. 중요한 질문은 실패가 발생하느냐가 아니라, 애플리케이션이 그 실패에 얼마나 예측 가능하게 반응하느냐입니다.

이 지점에서 가장 흔한 실수는 모든 실패를 한데 묶어 재시도하는 것입니다. 예외를 넓게 잡고 잠깐 기다렸다가 다시 보내면 복원력이 생긴 것처럼 보입니다. 하지만 인증 오류, 잘못된 요청 본문, 애플리케이션 버그, 스키마 검증 실패는 기다린다고 나아지는 문제가 아닙니다.

그래서 재시도는 루프보다 분류가 먼저입니다. 무엇이 일시적 실패이고 무엇이 즉시 멈춰야 하는 실패인지 구분한 뒤, 재시도 가능한 것만 제한된 횟수와 백오프로 다시 시도해야 합니다. 그렇지 않으면 재시도는 안정성이 아니라 지연 시간과 비용만 늘리는 장치가 됩니다.

이번 글에서는 `tenacity`를 사용해 Groq 호출 주변에 분류 기반 재시도 정책을 두고, 일시적 오류와 영구 오류를 나누는 가장 실용적인 패턴을 정리하겠습니다.

이 글은 LLM API Production 101 시리즈의 다섯 번째 글입니다.

여기서는 오류 분류와 제한된 재시도로 안정적인 LLM 호출 경로를 만드는 방법을 봅니다.

![재시도와 오류 처리: 안정적인 API 호출 만들기](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/05/05-01-retry-and-error-handling-making-api-call.ko.png)
*재시도와 오류 처리: 안정적인 API 호출 만들기*
> 좋은 재시도 정책은 예외를 많이 잡는 코드가 아니라, 다시 시도할 가치가 있는 실패만 좁게 골라내는 코드입니다.

## 먼저 던지는 질문

- 왜 모든 API 실패를 같은 재시도 정책으로 다루면 안 될까요?
- 어떤 오류는 재시도하고, 어떤 오류는 바로 실패로 분류해야 할까요?
- 최종 실패 뒤 사용자 메시지와 내부 로그는 어떻게 나눠야 할까요?

## 왜 이 글이 중요한가

재시도는 단순한 안정성 옵션이 아닙니다. 실패를 어떤 종류로 보고 어느 지점까지 복구를 시도할지 결정하는 운영 정책입니다. 이 정책이 없으면 네트워크 일시 장애와 영구 설정 오류가 같은 흐름으로 섞이고, 결과적으로 시스템은 더 느려지고 더 시끄러워집니다.

특히 LLM 경로에서는 같은 요청을 다시 보내는 비용이 적지 않습니다. 지연 시간이 늘고 토큰 사용량도 다시 발생합니다. 그래서 재시도는 “조금 더 기다리면 나아질 가능성이 있는가”라는 질문을 먼저 통과해야 합니다. 이 분류 없이 재시도를 늘리는 것은 안정성이 아니라 낭비에 가깝습니다.

또한 재시도는 사용자 경험과도 연결됩니다. 몇 번까지 자동 복구를 시도할지, 최종 실패 뒤 사용자에게 어떤 문구를 보여 줄지, 내부 로그에는 어떤 세부 정보를 남길지 미리 정해 두어야 시스템 동작이 일관됩니다.

## 핵심 개념

### 왜 모든 실패를 같은 정책으로 다루면 안 되는가

![재시도 가능 오류와 영구 오류의 분기 비교](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/05/05-01-why-all-failures-should-not-share-one-re.ko.png)

*재시도 가능 오류와 영구 오류의 분기 비교*

재시도가 유효한 경우는 실패가 잠시 후 사라질 가능성이 있을 때입니다. 짧은 네트워크 흔들림, transport timeout, 일부 5xx 응답, 때로는 429가 여기에 들어갑니다. 반면 인증 오류, 잘못된 요청 본문, 애플리케이션 파싱 버그, 잘못 설계된 구조화 출력 계약은 같은 요청을 다시 보내도 달라지지 않을 가능성이 큽니다.

이 둘을 분리하지 않으면 실패가 숨겨집니다. 영구 오류는 늦게 드러나고, 비용과 지연은 불필요하게 늘어납니다. 첫 단계는 언제나 재시도 가능성과 비재시도 가능성을 구분하는 것입니다.

### `tenacity`로 읽히는 재시도 정책 만들기

재시도 정책을 `while True`와 `sleep()`으로 직접 쓰면 읽기도 어렵고 조건이 흩어지기 쉽습니다. `tenacity`는 조건, 대기 간격, 중단 규칙을 정책처럼 선언하게 해 줍니다.

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
)
def flaky_operation() -> str:
    raise RuntimeError("temporary failure")
```

이 예제는 모양만 보여 줍니다. 실제 LLM 경로에서는 무엇이 재시도 대상인지 더 좁게 정해야 합니다.

### 오류 분류용 예외 계층 만들기

![공급자 예외를 앱 예외로 감싸는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/05/05-02-creating-an-error-hierarchy-for-retry-de.ko.png)

*공급자 예외를 앱 예외로 감싸는 구조*

가장 실용적인 패턴은 공급자 세부 예외를 애플리케이션 수준의 분류로 감싸는 것입니다.

```python
class RetryableLLMError(Exception):
    pass

class NonRetryableLLMError(Exception):
    pass
```

이 두 종류가 생기면 재시도 계층은 SDK 세부 사항을 몰라도 됩니다. 애플리케이션은 “다시 시도해도 되는 실패인가 아닌가”만 재시도 정책에 전달하면 됩니다.

### Groq 호출에 지수 백오프 붙이기

![지수 백오프가 반복되는 재시도 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/05/05-03-adding-exponential-backoff-to-a-groq-cal.ko.png)

*지수 백오프가 반복되는 재시도 흐름*

한 가지 운영 포인트가 먼저 있습니다. SDK 자체에 기본 재시도가 있다면 애플리케이션 재시도와 겹칠 수 있습니다. 예제에서는 이 중첩을 피하려고 SDK 재시도를 꺼 두었습니다.

```python
import logging
import os

from groq import APIConnectionError, APIStatusError, Groq, RateLimitError
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
client = Groq(api_key=os.environ["GROQ_API_KEY"], max_retries=0)

class RetryableLLMError(Exception):
    pass

class NonRetryableLLMError(Exception):
    pass

@retry(
    retry=retry_if_exception_type(RetryableLLMError),
    wait=wait_exponential_jitter(initial=1, max=8),
    stop=stop_after_attempt(3),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def call_llm(messages: list[dict]) -> str:
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0,
        )
        return completion.choices[0].message.content
    except RateLimitError as exc:
        raise RetryableLLMError("provider rate limit hit") from exc
    except APIConnectionError as exc:
        raise RetryableLLMError("provider connection failed") from exc
    except APIStatusError as exc:
        if exc.status_code >= 500:
            raise RetryableLLMError(f"provider server error: {exc.status_code}") from exc
        raise NonRetryableLLMError(f"provider request failed: {exc.status_code}") from exc

messages = [
    {"role": "system", "content": "You are a concise Python tutor."},
    {"role": "user", "content": "Explain Python context managers in three sentences."},
]

try:
    text = call_llm(messages)
    print(text)
except NonRetryableLLMError as exc:
    logger.error("request failed without retry: %s", exc)
except RetryableLLMError as exc:
    logger.error("request still failed after retries: %s", exc)
```

<!-- injected-output:start -->
**실행 결과**

    Python context managers are used to manage resources such as files, connections, or locks, ensuring they are properly cleaned up after use, even if exceptions occur. They are implemented using the `with` statement, which automatically calls the `__enter__` method when entering the block and the `__exit__` method when exiting, allowing for resource acquisition and release. This approach helps prevent resource leaks and makes code more readable and maintainable.

<!-- injected-output:end -->

여기서 세 가지가 중요합니다. `retry_if_exception_type(RetryableLLMError)`로 재시도 범위를 좁혔다는 점, `wait_exponential_jitter`로 점점 느려지는 백오프와 지터를 함께 적용했다는 점, `reraise=True`로 최종 실패를 숨기지 않는다는 점입니다.

### 어떤 실패가 재시도 대상인가

![오류 유형별 처리 정책 결정 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/05/05-04-which-failures-are-retryable.ko.png)

*오류 유형별 처리 정책 결정 흐름*

처음에는 단순한 기준으로도 충분합니다. 네트워크 단절, 연결 실패, transport timeout, 일시적인 5xx, 일부 429는 재시도 후보입니다. 반대로 인증 실패, 잘못된 요청 바디, 없는 모델명, 애플리케이션 버그, 구조화 출력 검증 실패는 보통 바로 멈추거나 별도 경로로 처리해야 합니다.

특히 Pydantic 검증 실패는 강조할 가치가 있습니다. 같은 요청을 즉시 다시 보내도 같은 종류의 실패가 반복될 가능성이 큽니다. 이 경우는 재시도보다 프롬프트 조정, 폴백 경로, 사용자에게 설명 가능한 오류 메시지가 더 정직한 대응입니다.

### 분류를 별도 함수로 빼기

`except` 분기가 늘어나면 분류 로직을 함수로 빼는 편이 낫습니다.

```python
def classify_exception(exc: Exception) -> Exception:
    if isinstance(exc, (RateLimitError, APIConnectionError)):
        return RetryableLLMError(str(exc))

    if isinstance(exc, APIStatusError):
        if exc.status_code >= 500:
            return RetryableLLMError(str(exc))
        return NonRetryableLLMError(str(exc))

    return NonRetryableLLMError(f"unexpected error: {exc}")
```

```python
try:
    completion = client.chat.completions.create(...)
except Exception as exc:
    raise classify_exception(exc) from exc
```

이렇게 해 두면 SDK 예외 종류가 늘어나도 재시도 정책 본문은 크게 흔들리지 않습니다.

### 실패를 의도적으로 재현해 백오프 로그 보기

재시도 코드는 실제 장애가 나기 전까지 체감하기 어렵습니다. 그래서 운영 전에는 공급자 호출 대신 의도적으로 실패하는 함수를 붙여, 시도 횟수와 로그가 기대대로 나오는지 확인하는 편이 좋습니다.

```python
import logging

from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("retry-demo")

class RetryableLLMError(Exception):
    pass

attempt_counter = {"count": 0}

@retry(
    retry=retry_if_exception_type(RetryableLLMError),
    wait=wait_exponential_jitter(initial=1, max=2),
    stop=stop_after_attempt(3),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def flaky_lookup() -> str:
    attempt_counter["count"] += 1
    logger.info("attempt=%s", attempt_counter["count"])
    if attempt_counter["count"] < 3:
        raise RetryableLLMError("temporary upstream timeout")
    return "recovered on third attempt"

print(flaky_lookup())
```

<!-- injected-output:start -->
**실행 결과**

    INFO:retry-demo:attempt=1
    WARNING:retry-demo:Retrying __main__.flaky_lookup in 1.0 seconds as it raised RetryableLLMError: temporary upstream timeout.
    INFO:retry-demo:attempt=2
    WARNING:retry-demo:Retrying __main__.flaky_lookup in 2.0 seconds as it raised RetryableLLMError: temporary upstream timeout.
    INFO:retry-demo:attempt=3
    recovered on third attempt

<!-- injected-output:end -->

이 예제는 장애 재현이 아니라 정책 검증에 가깝습니다. 로그에 시도 횟수, 대기 간격, 최종 성공 여부가 남기 때문에 운영 전에 “정말 세 번만 시도하는가”, “백오프가 겹치지 않는가”, “성공 뒤 불필요한 추가 시도가 없는가”를 바로 확인할 수 있습니다.

### 최종 실패를 사용자 메시지와 내부 로그로 분리하기

재시도 정책이 끝나면 이제 실패를 어디에 어떻게 전달할지 결정해야 합니다. 사용자에게는 짧고 안정적인 문구를 주고, 내부에는 디버깅 가능한 필드를 남기는 편이 좋습니다.

```python
def build_failure_response(exc: Exception, attempt_count: int) -> tuple[dict, dict]:
    user_payload = {
        "message": "잠시 후 다시 시도해 주세요. 요청을 끝까지 처리하지 못했습니다.",
        "retryable": isinstance(exc, RetryableLLMError),
    }
    log_payload = {
        "retryable": isinstance(exc, RetryableLLMError),
        "attempt_count": attempt_count,
        "final_error_type": type(exc).__name__,
        "final_error_message": str(exc),
    }
    return user_payload, log_payload

user_payload, log_payload = build_failure_response(RetryableLLMError("timeout"), attempt_count=3)
print(user_payload)
print(log_payload)
```

<!-- injected-output:start -->
**실행 결과**

    {'message': '잠시 후 다시 시도해 주세요. 요청을 끝까지 처리하지 못했습니다.', 'retryable': True}
    {'retryable': True, 'attempt_count': 3, 'final_error_type': 'RetryableLLMError', 'final_error_message': 'timeout'}

<!-- injected-output:end -->

이렇게 분리해 두면 사용자 경험은 안정적으로 유지되고, 운영자는 내부 로그에서 재시도 성격과 최종 실패 이유를 바로 볼 수 있습니다. 구조화 출력 검증 실패처럼 비재시도 오류가 들어오면 같은 함수로도 전혀 다른 후속 처리 정책을 붙일 수 있습니다.

### 최종 실패 뒤 무엇을 남길 것인가

![최종 실패 뒤 사용자와 로그로 나뉘는 경로](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/05/05-05-what-the-user-should-see-after-final-fai.ko.png)

*최종 실패 뒤 사용자와 로그로 나뉘는 경로*

재시도는 실패를 없애지 않습니다. 실패를 더 나은 형태로 드러내게 할 뿐입니다. 마지막 시도까지 모두 끝났다면 사용자 메시지, 내부 로그, 자동 복구 중단 지점이 분명해야 합니다. 내부에는 `retryable`, `attempt_count`, `final_error_type` 같은 정보를 남기고, 사용자에게는 짧고 일관된 문구를 주는 편이 좋습니다.

공급자 예외 원문을 그대로 보여 주면 노이즈가 많고 때로는 과도한 정보를 노출할 수 있습니다. 사용자 경험과 내부 디버깅 정보는 의도적으로 분리하는 것이 좋습니다.

### 재시도 예산을 두어 장애 폭주를 막기

재시도 정책이 있어도 트래픽 전체가 동시에 실패하면 문제가 다시 커집니다. 각 요청이 3회 재시도하면, 원래 100 RPS 경로가 순간적으로 300회 이상의 추가 호출을 만들 수 있습니다. 이때는 요청 단위 재시도 외에 시스템 단위 재시도 예산을 두는 편이 안전합니다.

```python
import time
from collections import deque

class RetryBudget:
    def __init__(self, window_seconds: int, max_retries_in_window: int) -> None:
        self.window_seconds = window_seconds
        self.max_retries_in_window = max_retries_in_window
        self.events: deque[float] = deque()

    def allow_retry(self) -> bool:
        now = time.monotonic()
        while self.events and now - self.events[0] >= self.window_seconds:
            self.events.popleft()

        if len(self.events) >= self.max_retries_in_window:
            return False

        self.events.append(now)
        return True

budget = RetryBudget(window_seconds=60, max_retries_in_window=120)
print(budget.allow_retry())
```

이 예산은 회로 차단기보다 단순하지만 효과적입니다. 장애가 확산되는 시점에 재시도 호출량을 제한해 공급자와 애플리케이션 양쪽의 압력을 줄여 줍니다. 특히 다중 워커 환경에서는 이 카운터를 Redis로 공유하는 것이 좋습니다.

### 429와 5xx를 같은 백오프로 다루지 않기

운영 로그를 보면 429와 5xx는 의미가 다릅니다. 429는 정책 충돌이고 5xx는 공급자 불안정일 가능성이 큽니다. 둘을 같은 대기 정책으로 묶으면 회복 속도가 늦거나, 반대로 너무 공격적인 재시도로 다시 실패를 키울 수 있습니다.

```python
import random

def compute_backoff_seconds(error_type: str, attempt: int) -> float:
    if error_type == "rate_limit":
        # 429는 더 보수적으로 대기
        return min(2 ** (attempt + 1), 16) + random.uniform(0, 0.5)

    if error_type == "server_error":
        # 5xx는 상대적으로 짧은 초기 백오프로 빠른 회복 시도
        return min(2**attempt, 8) + random.uniform(0, 0.3)

    return 0.0

for i in range(3):
    print("429 backoff", i, compute_backoff_seconds("rate_limit", i))
    print("5xx backoff", i, compute_backoff_seconds("server_error", i))
```

백오프 수치 자체보다 중요한 것은 정책을 분리해 표현하는 것입니다. 분리가 되어 있으면 후속 튜닝에서 지표와 설정이 일대일로 연결됩니다. 예를 들어 429가 집중되는 시간대에는 rate-limit 경로만 조정하면 되고, 5xx가 증가하면 공급자 전환이나 timeout 재설계를 먼저 검토할 수 있습니다.

### 재시도 시도 정보를 요청 컨텍스트에 남기기

재시도 정책을 붙였는데도 디버깅이 어려운 경우는, 최종 실패 로그에 마지막 예외만 남고 중간 시도 정보가 사라졌기 때문인 경우가 많습니다. 각 시도의 오류 유형과 대기 시간을 남기면 장애 원인 분리가 훨씬 쉬워집니다.

```python
from dataclasses import dataclass, field

@dataclass
class RetryAttempt:
    attempt: int
    error_type: str
    planned_sleep_seconds: float

@dataclass
class RetryTrace:
    request_id: str
    attempts: list[RetryAttempt] = field(default_factory=list)

    def add(self, attempt: int, error_type: str, planned_sleep_seconds: float) -> None:
        self.attempts.append(
            RetryAttempt(
                attempt=attempt,
                error_type=error_type,
                planned_sleep_seconds=planned_sleep_seconds,
            )
        )

trace = RetryTrace(request_id="req-2026-05-15-001")
trace.add(attempt=1, error_type="RateLimitError", planned_sleep_seconds=1.2)
trace.add(attempt=2, error_type="RateLimitError", planned_sleep_seconds=2.1)
print(trace)
```

이 필드는 APM이나 구조화 로그로 그대로 보내기 좋습니다. 운영자는 “몇 번째 시도에서 어떤 오류가 반복되는지”를 즉시 볼 수 있고, 재시도 예산 조정이나 백오프 튜닝을 감에 의존하지 않게 됩니다.

## 흔히 헷갈리는 지점

- 재시도 횟수를 늘리면 안정성이 높아진다고 생각하기 쉽지만, 분류가 먼저입니다.
- 지수 백오프에서 지터를 빼면 여러 요청이 같은 타이밍에 다시 몰릴 수 있습니다.
- SDK 기본 재시도와 애플리케이션 재시도를 겹치면 실제 시도 횟수가 의도보다 커질 수 있습니다.
- 구조화 출력 검증 실패는 대개 같은 요청 재시도로 해결되지 않습니다.
- 최종 실패 처리에서 사용자 메시지와 내부 로그를 같은 수준으로 노출하면 둘 다 품질이 떨어집니다.

## 운영 체크리스트

- [ ] 재시도 가능 오류와 비재시도 오류를 문서와 코드에서 같은 기준으로 나눴다
- [ ] SDK 재시도와 애플리케이션 재시도 중첩 여부를 확인했다
- [ ] 지수 백오프와 지터, 최대 시도 횟수를 명시적으로 설정했다
- [ ] 구조화 출력·스트리밍 실패를 별도 정책으로 분리했다
- [ ] 최종 실패 시 사용자 메시지와 내부 로그 필드를 따로 설계했다

## 정리

이번 글에서는 재시도를 무조건적인 반복이 아니라 오류 분류 위에 세운 제한된 복구 전략으로 정리했습니다. `tenacity`는 이 정책을 코드로 읽기 쉽게 만들어 주고, 애플리케이션 수준의 예외 계층은 공급자 세부 예외를 더 안정적인 운영 분류로 바꿔 줍니다.

먼저 정해야 할 것은 무엇을 다시 시도할지입니다. 일시적 실패만 좁게 골라 재시도하고, 영구 오류는 빨리 멈춰야 시스템이 덜 시끄럽고 덜 비싸게 동작합니다. 이 차이가 있어야 재시도가 안정성 도구가 됩니다.

다음 글에서는 개별 요청의 복구를 넘어 트래픽 전체의 흐름을 다룹니다. 재시도가 실패 후 복구였다면, 속도 제한 관리는 429가 오기 전에 요청 흐름을 제어하는 문제입니다.

## 처음 질문으로 돌아가기

- **왜 모든 API 실패를 같은 재시도 정책으로 다루면 안 될까요?**
  인증 오류, 입력 오류, 속도 제한, 일시적 네트워크 오류는 원인과 회복 가능성이 다르므로 같은 정책으로 묶으면 비용과 장애 시간이 커집니다.

- **어떤 오류는 재시도하고, 어떤 오류는 바로 실패로 분류해야 할까요?**
  일시적 네트워크 오류와 일부 429/5xx는 재시도 후보이고, 잘못된 키·모델 ID·요청 스키마 오류는 보통 수정 없이 재시도해도 해결되지 않습니다.

- **최종 실패 뒤 사용자 메시지와 내부 로그는 어떻게 나눠야 할까요?**
  사용자에게는 행동 가능한 짧은 메시지를 주고, 내부 로그에는 오류 분류, provider 응답, 시도 횟수, correlation id를 남겨야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM API Production 101 (1/6): 구조화 출력 — JSON 모드와 응답 스키마](./01-structured-output.md)
- [LLM API Production 101 (2/6): 툴 호출 — 함수를 모델에 연결하기](./02-tool-calling.md)
- [LLM API Production 101 (3/6): 스트리밍 심화 — 청크 처리와 오류 복구](./03-streaming-in-depth.md)
- [LLM API Production 101 (4/6): 캐싱 전략 — 비용과 지연 시간 줄이기](./04-caching-strategies.md)
- **LLM API Production 101 (5/6): 재시도와 오류 처리 — 안정적인 API 호출 만들기 (현재 글)**
- LLM API Production 101 (6/6): 속도 제한 관리 — Rate Limit 대응 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Tenacity documentation](https://tenacity.readthedocs.io/en/latest/)
- [Groq Text Chat docs](https://console.groq.com/docs/text-chat)

### 검증 보조 자료
- [HTTP Semantics — 429 Too Many Requests](https://www.rfc-editor.org/rfc/rfc9110.html#name-429-too-many-requests)

### 관련 시리즈
- [캐싱 전략 — 비용과 지연 시간 줄이기](./04-caching-strategies.md)
- [속도 제한 관리 — Rate Limit 대응 패턴](./06-rate-limit-management.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-api-production-101/ko/05-retry-and-error-handling)

Tags: LLM, OpenAI, Streaming, Python
