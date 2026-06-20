---
title: "바이브코딩을 위한 LLM API 운영 (6/6): 속도 제한 관리 — Rate Limit 대응 패턴"
series: llm-api-production-101
episode: 6
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM
- OpenAI
- Rate Limit
- Python
---

# 바이브코딩을 위한 LLM API 운영 (6/6): 속도 제한 관리 — Rate Limit 대응 패턴

이 글은 **바이브코딩을 위한 LLM API 운영** 시리즈의 마지막 글입니다. 구조화 출력, 도구 호출, 스트리밍, 캐싱, 재시도를 통합하고 Rate Limit을 체계적으로 관리하는 방법을 다룹니다.

---

재시도 로직을 만들었습니다. 그런데 429 Rate Limit은 재시도보다 사전 예방이 중요합니다. 토큰을 너무 빠르게 소비하면 Rate Limit에 걸리고, 그러면 재시도가 많아지고, 재시도가 Rate Limit을 더 악화시킵니다.

바이브코딩으로 AI에게 "Rate Limit 처리해줘"라고 하면 재시도 코드가 나옵니다. 토큰 소비를 사전에 측정하고, 속도를 제어하고, 배치 처리로 효율을 높이는 방법까지 알아야 Rate Limit을 효과적으로 관리할 수 있습니다.

> "Rate Limit 관리는 사전 측정과 속도 제어에서 시작합니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. TPM(Tokens Per Minute)과 RPM(Requests Per Minute)의 차이가 무엇인가요?
2. 배치 처리가 Rate Limit 관리에 어떻게 도움이 되나요?
3. 토큰 사전 측정(pre-counting)이 왜 필요한가요?
4. 대기열(queue)로 요청 속도를 제어하는 방법이 있나요?
5. 여러 API 키를 로테이션하는 방법이 있나요?

---

## 토큰 사전 측정

```python
import tiktoken

def count_tokens(messages: list, model: str = "gpt-4o-mini") -> int:
    encoding = tiktoken.encoding_for_model(model)
    total = 0
    for msg in messages:
        total += len(encoding.encode(msg.get("content", ""))) + 4  # 메시지 오버헤드
    return total + 2  # 응답 프라이밍
```

## 속도 제한기

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, rpm: int = 60, tpm: int = 90000):
        self.rpm = rpm
        self.tpm = tpm
        self.request_times: deque = deque()
        self.token_times: deque = deque()

    def _clean_old(self, queue: deque, window: float = 60.0):
        now = time.time()
        while queue and queue[0][0] < now - window:
            queue.popleft()

    def wait_if_needed(self, tokens: int):
        self._clean_old(self.request_times)
        self._clean_old(self.token_times)

        current_rpm = len(self.request_times)
        current_tpm = sum(t for _, t in self.token_times)

        if current_rpm >= self.rpm or current_tpm + tokens >= self.tpm:
            wait = 60.0 - (time.time() - self.request_times[0][0]) if self.request_times else 1.0
            print(f"Rate limit 예방: {wait:.1f}초 대기")
            time.sleep(max(wait, 0.1))

    def record(self, tokens: int):
        now = time.time()
        self.request_times.append((now, 1))
        self.token_times.append((now, tokens))
```

## API 키 로테이션

```python
import itertools

class APIKeyRotator:
    def __init__(self, api_keys: list[str]):
        self._cycle = itertools.cycle(api_keys)
        self._failed: set[str] = set()

    def get_key(self) -> str:
        for _ in range(len(self._cycle.__length_hint__() if hasattr(self._cycle, '__length_hint__') else 10)):
            key = next(self._cycle)
            if key not in self._failed:
                return key
        raise RuntimeError("사용 가능한 API 키 없음")

    def mark_failed(self, key: str):
        self._failed.add(key)
```

## 통합 LLM 클라이언트

```python
from openai import OpenAI

class ProductionLLMClient:
    def __init__(self, api_keys: list[str], rpm: int = 60, tpm: int = 90000):
        self.rotator = APIKeyRotator(api_keys)
        self.limiter = RateLimiter(rpm=rpm, tpm=tpm)

    def call(self, messages: list) -> str:
        tokens = count_tokens(messages)
        self.limiter.wait_if_needed(tokens)

        api_key = self.rotator.get_key()
        client = OpenAI(api_key=api_key)

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
            )
            self.limiter.record(tokens)
            return response.choices[0].message.content
        except Exception as e:
            if "rate_limit" in str(e).lower():
                self.rotator.mark_failed(api_key)
            raise
```

---

## Before / After

| 항목 | Before (Rate Limit 없음) | After (Rate Limit 관리) |
|------|------------------------|------------------------|
| 429 발생 | 빈번하게 발생 | 사전 속도 제어로 예방 |
| 토큰 추적 | 없음 | tiktoken으로 사전 측정 |
| API 키 | 단일 키 | 로테이션으로 한도 분산 |
| 대기 | 재시도 대기 | 사전 예방적 대기 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 사전 측정 없음 | 한도 초과 후 재시도 | tiktoken 사전 계산 |
| 즉시 429 재시도 | 상황 악화 | wait_if_needed 선행 |
| API 키 고정 | 단일 키 한도 소진 | APIKeyRotator |
| 토큰/요청 분리 관리 | 불균형 | RPM + TPM 동시 추적 |

---

## AI 활용 팁

```
OpenAI API에 Rate Limit 관리를 추가해줘.
RateLimiter는 RPM과 TPM을 슬라이딩 윈도우로 추적하고, 한도 초과 시 대기해줘.
tiktoken으로 요청 전 토큰을 사전 측정해줘.
여러 API 키를 APIKeyRotator로 로테이션하고, 429 오류 발생 시 해당 키를 제외해줘.
```

---

## 체크리스트

- [ ] tiktoken으로 토큰 사전 측정
- [ ] RateLimiter(RPM + TPM 슬라이딩 윈도우)
- [ ] wait_if_needed 사전 예방 대기
- [ ] APIKeyRotator로 다중 키 관리
- [ ] 429 오류 시 키 비활성화
- [ ] ProductionLLMClient 통합 클래스

---

## 처음 질문으로 돌아가기

"Rate Limit이 걸리면 재시도하면 되지 않나요?" — 재시도는 마지막 수단입니다. 사전에 토큰을 측정하고 속도를 제어하면 Rate Limit 자체를 예방할 수 있습니다. 여러 API 키 로테이션으로 한도를 분산하면 처리량도 높아집니다.

---

## 정리

- tiktoken으로 API 호출 전 토큰을 사전 측정한다
- RateLimiter가 슬라이딩 윈도우로 RPM과 TPM을 추적하고 사전 대기한다
- APIKeyRotator로 다중 키를 로테이션해 한도를 분산한다
- 재시도보다 사전 예방이 Rate Limit 관리의 핵심이다

---

## 참고 자료

- [OpenAI Rate Limits](https://platform.openai.com/docs/guides/rate-limits)
- [tiktoken GitHub](https://github.com/openai/tiktoken)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 토큰 사전 측정
- 속도 제한기
- API 키 로테이션
- 통합 LLM 클라이언트
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LLM, OpenAI, Rate Limit, Python
