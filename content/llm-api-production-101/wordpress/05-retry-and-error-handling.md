---
title: "바이브코딩을 위한 LLM API 운영 (5/6): 재시도와 오류 처리 — 안정적인 API 호출 만들기"
series: llm-api-production-101
episode: 5
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM
- OpenAI
- Retry
- Python
---

# 바이브코딩을 위한 LLM API 운영 (5/6): 재시도와 오류 처리 — 안정적인 API 호출 만들기

이 글은 **바이브코딩을 위한 LLM API 운영** 시리즈의 다섯 번째 글입니다. 일시적 API 오류를 자동으로 복구하는 재시도 로직과 오류 유형별 처리 전략을 다룹니다.

---

LLM API는 가끔 실패합니다. 429 Rate Limit, 500 서버 오류, 네트워크 타임아웃 — 이런 오류가 나면 서비스가 멈춥니다. "다시 시도하면 되지 않나요?"라고 생각하지만, 무조건 즉시 재시도하면 오히려 문제가 커집니다.

바이브코딩으로 AI에게 "API 오류 처리해줘"라고 하면 기본 try-except가 나옵니다. 지수 백오프가 왜 필요한지, 어떤 오류는 재시도하고 어떤 오류는 바로 포기해야 하는지 모르면 재시도 로직이 오히려 서버에 부담을 줍니다.

> "오류 처리는 언제 재시도하고 언제 포기할지 결정하는 것입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 지수 백오프(exponential backoff)가 왜 필요한가요?
2. 재시도해야 하는 오류와 하면 안 되는 오류를 어떻게 구분하나요?
3. 429 오류의 Retry-After 헤더를 어떻게 사용하나요?
4. 최대 재시도 횟수를 초과하면 어떻게 처리해야 하나요?
5. 재시도 로직을 데코레이터로 구현하는 장점이 무엇인가요?

---

## 오류 분류

```python
from openai import RateLimitError, APIStatusError, APIConnectionError

RETRYABLE_ERRORS = (RateLimitError, APIConnectionError)
NON_RETRYABLE_STATUS = {400, 401, 403, 404}

def is_retryable(error: Exception) -> bool:
    if isinstance(error, RETRYABLE_ERRORS):
        return True
    if isinstance(error, APIStatusError):
        return error.status_code not in NON_RETRYABLE_STATUS
    return False
```

## 지수 백오프 재시도

```python
import time
import random

def retry_with_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
):
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries or not is_retryable(e):
                raise

            # 지수 백오프 + 지터
            delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)

            # Rate Limit 오류면 Retry-After 헤더 확인
            if isinstance(e, RateLimitError) and hasattr(e, "response"):
                retry_after = e.response.headers.get("Retry-After")
                if retry_after:
                    delay = float(retry_after)

            print(f"재시도 {attempt + 1}/{max_retries}, {delay:.1f}초 대기")
            time.sleep(delay)
```

## 재시도 데코레이터

```python
import functools

def with_retry(max_retries: int = 3, base_delay: float = 1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return retry_with_backoff(
                lambda: func(*args, **kwargs),
                max_retries=max_retries,
                base_delay=base_delay,
            )
        return wrapper
    return decorator

@with_retry(max_retries=3)
def call_llm(messages: list) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return response.choices[0].message.content
```

---

## Before / After

| 항목 | Before (재시도 없음) | After (지수 백오프) |
|------|--------------------|--------------------|
| API 오류 | 즉시 서비스 중단 | 자동 재시도 |
| Rate Limit | 즉시 실패 | Retry-After 대기 |
| 즉시 재시도 | 서버 부하 가중 | 백오프로 부하 분산 |
| 비재시도 오류 | 반복 시도 | 401/404 즉시 포기 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 모든 오류 재시도 | 401 오류 반복 | is_retryable로 구분 |
| 즉시 재시도 | 서버 부하 가중 | 지수 백오프 |
| 지터 없음 | 동시 요청 충돌 | random.uniform 추가 |
| Retry-After 무시 | Rate Limit 계속 | 헤더 값 사용 |

---

## AI 활용 팁

```
OpenAI API 호출에 지수 백오프 재시도 로직을 추가해줘.
RateLimitError와 APIConnectionError는 재시도하고, 400/401/403/404는 즉시 포기해줘.
지수 백오프에 랜덤 지터를 추가하고, RateLimitError의 Retry-After 헤더를 사용해줘.
@with_retry 데코레이터로 함수에 쉽게 적용할 수 있게 해줘.
```

---

## 체크리스트

- [ ] is_retryable로 오류 분류
- [ ] 지수 백오프(base_delay * 2^attempt)
- [ ] 랜덤 지터(random.uniform)
- [ ] Retry-After 헤더 활용
- [ ] max_delay 상한 설정
- [ ] @with_retry 데코레이터

---

## 처음 질문으로 돌아가기

"API 오류 나면 그냥 즉시 재시도하면 되지 않나요?" — 즉시 재시도는 서버 부하를 가중시키고 Rate Limit 상황을 악화시킵니다. 지수 백오프로 대기 시간을 늘리고, Retry-After 헤더를 존중해야 API 공급자와 공존할 수 있습니다.

---

## 정리

- 재시도 가능 오류(429, 5xx, 연결 오류)와 불가 오류(400, 401, 403, 404)를 구분한다
- 지수 백오프(base * 2^n)에 랜덤 지터를 추가해 동시 요청 충돌을 방지한다
- RateLimitError의 Retry-After 헤더를 우선적으로 사용한다
- @with_retry 데코레이터로 모든 API 호출에 쉽게 적용한다

---

## 참고 자료

- [OpenAI 오류 처리 가이드](https://platform.openai.com/docs/guides/error-codes)
- [지수 백오프 알고리즘](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 오류 분류
- 지수 백오프 재시도
- 재시도 데코레이터
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LLM, OpenAI, Retry, Python
