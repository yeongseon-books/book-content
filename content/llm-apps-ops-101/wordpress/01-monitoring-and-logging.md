---
title: "바이브코딩을 위한 LLM 앱 운영 (1/6): LLM 앱 모니터링과 로깅"
series: llm-apps-ops-101
episode: 1
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LLMOps
- Observability
- Python
- LLM
---

# 바이브코딩을 위한 LLM 앱 운영 (1/6): LLM 앱 모니터링과 로깅

이 글은 **바이브코딩을 위한 LLM 앱 운영** 시리즈의 첫 번째 글입니다. LLM 호출을 나중에 복원할 수 있는 로그 구조를 설계하고, 비용·지연 시간·장애를 하나의 기록으로 연결하는 방법을 다룹니다.

---

"LLM 앱에서 에러가 났습니다." 슬랙에 이 메시지가 올라왔을 때, 진짜 어려운 부분은 그 다음 질문입니다. "그때 프롬프트에 뭐가 들어갔지?", "토큰이 얼마나 나갔지?", "어제 같은 요청은 왜 정상이었지?" 이 질문들에 답할 수 없으면, 팀은 장애를 겪은 게 아니라 장애를 목격만 한 겁니다.

바이브코딩으로 AI에게 "LLM 로깅 만들어줘"라고 하면 print 문이나 기본 logging이 나올 수 있습니다. 호출 단위로 복원 가능한 로그 구조, 비용 추적, 지연 시간 측정이 없으면 장애 분석이 추측에 의존합니다.

> "LLM 호출 한 건을 나중에 복원할 수 있는 로그 구조가 먼저입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. LLM 호출 로그에 어떤 필드가 반드시 포함되어야 하나요?
2. 비용과 지연 시간을 어떻게 같은 로그에 기록하나요?
3. 로그를 나중에 재현하려면 어떤 정보가 필요한가요?
4. 장애 발생 시 로그에서 어떤 패턴을 찾아야 하나요?
5. 로그를 구조화해야 하는 이유가 무엇인가요?

---

## LLM 호출 로그 구조

```python
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class LLMCallLog:
    call_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    model: str = ""
    messages: list = field(default_factory=list)
    response: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    error: str | None = None
    metadata: dict = field(default_factory=dict)
```

## 로깅 래퍼

```python
import time
import json
import logging

logger = logging.getLogger(__name__)

COST_PER_TOKEN = {
    "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
}

def logged_llm_call(client, messages: list, model: str = "gpt-4o-mini", **kwargs) -> LLMCallLog:
    log = LLMCallLog(model=model, messages=messages)
    start = time.time()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )
        log.response = response.choices[0].message.content
        log.prompt_tokens = response.usage.prompt_tokens
        log.completion_tokens = response.usage.completion_tokens
        log.total_tokens = response.usage.total_tokens

        price = COST_PER_TOKEN.get(model, COST_PER_TOKEN["gpt-4o-mini"])
        log.cost_usd = (
            log.prompt_tokens * price["input"] +
            log.completion_tokens * price["output"]
        )

    except Exception as e:
        log.error = str(e)
        raise
    finally:
        log.latency_ms = (time.time() - start) * 1000
        logger.info(json.dumps({
            "call_id": log.call_id,
            "model": log.model,
            "total_tokens": log.total_tokens,
            "cost_usd": round(log.cost_usd, 6),
            "latency_ms": round(log.latency_ms, 1),
            "error": log.error,
        }))

    return log
```

## 로그 저장 및 조회

```python
import json
from pathlib import Path

class LLMLogStore:
    def __init__(self, log_file: str = "llm_calls.jsonl"):
        self.log_file = Path(log_file)

    def save(self, log: LLMCallLog):
        with open(self.log_file, "a") as f:
            f.write(json.dumps({
                "call_id": log.call_id,
                "timestamp": log.timestamp,
                "model": log.model,
                "messages": log.messages,
                "response": log.response,
                "tokens": log.total_tokens,
                "cost_usd": log.cost_usd,
                "latency_ms": log.latency_ms,
                "error": log.error,
            }) + "\n")

    def get_by_id(self, call_id: str) -> dict | None:
        with open(self.log_file) as f:
            for line in f:
                record = json.loads(line)
                if record["call_id"] == call_id:
                    return record
        return None
```

---

## Before / After

| 항목 | Before (로그 없음) | After (구조화 로그) |
|------|------------------|-------------------|
| 장애 분석 | 추측 | call_id로 재현 |
| 비용 추적 | 월 청구서 확인 | 호출별 실시간 기록 |
| 지연 시간 | 모름 | latency_ms 측정 |
| 에러 패턴 | 발생 후 발견 | error 필드 분석 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| print()로만 로그 | 구조화 불가 | JSON 로그 파일 |
| call_id 없음 | 특정 호출 추적 불가 | UUID call_id 필수 |
| messages 미기록 | 재현 불가 | 입력 messages 저장 |
| 비용 미기록 | 비용 분석 불가 | 호출별 cost_usd |

---

## AI 활용 팁

```
LLM API 호출을 logged_llm_call로 감싸줘.
LLMCallLog에 call_id, timestamp, messages, response, tokens, cost_usd, latency_ms를 기록해줘.
LLMLogStore로 JSONL 파일에 저장하고 call_id로 조회할 수 있게 해줘.
에러 발생 시에도 latency_ms와 error 필드를 기록해줘.
```

---

## 체크리스트

- [ ] LLMCallLog dataclass 정의
- [ ] logged_llm_call 래퍼 구현
- [ ] 토큰별 비용 계산
- [ ] latency_ms 측정(finally 블록)
- [ ] LLMLogStore JSONL 저장
- [ ] call_id로 로그 조회

---

## 처음 질문으로 돌아가기

"LLM 앱에서 에러가 났는데 어디서 뭐가 문제인지 어떻게 알아요?" — call_id가 있으면 그 호출의 입력 messages, 출력 response, 토큰 수, 비용, 지연 시간을 한 레코드로 조회할 수 있습니다. 재현과 분석이 가능해집니다.

---

## 정리

- LLMCallLog에 call_id, messages, response, tokens, cost, latency, error를 기록한다
- logged_llm_call이 모든 호출을 자동으로 감싸고 로그를 남긴다
- JSONL 형식으로 저장해 나중에 call_id로 조회하고 재현한다
- error 발생 시에도 finally 블록에서 latency와 error를 기록한다

---

## 참고 자료

- [Python logging 문서](https://docs.python.org/3/library/logging.html)
- [LangSmith 트레이싱](https://docs.smith.langchain.com/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- LLM 호출 로그 구조
- 로깅 래퍼
- 로그 저장 및 조회
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LLMOps, Observability, Python, LLM
