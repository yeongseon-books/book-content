---
title: "바이브코딩을 위한 LLM 앱 기초 (2/6): 토큰 이해하기 — 비용, 한계, 컨텍스트 창"
series: llm-app-foundations-101
episode: 2
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM
- Tokens
- OpenAI
- Python
---

# 바이브코딩을 위한 LLM 앱 기초 (2/6): 토큰 이해하기 — 비용, 한계, 컨텍스트 창

이 글은 **바이브코딩을 위한 LLM 앱 기초** 시리즈의 두 번째 글입니다. 토큰이 무엇인지, 비용과 컨텍스트 창에 어떻게 영향을 주는지 이해합니다.

---

API를 호출했는데 비용이 예상보다 많이 나옵니다. 긴 문서를 넣었더니 "컨텍스트 창 초과" 오류가 납니다. 토큰이 무엇인지 이해하지 못하면 이런 상황을 예측하고 대응하기 어렵습니다.

바이브코딩으로 AI에게 "토큰 계산해줘"라고 하면 tiktoken 코드가 나옵니다. 토큰이 왜 문자와 다른지, 한국어 토큰이 영어보다 많이 나오는 이유, 컨텍스트 창이 전체 비용에 어떻게 영향을 주는지 모르면 최적화하기 어렵습니다.

> "토큰은 LLM의 비용과 한계를 결정하는 기본 단위입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 토큰이 문자, 단어, 바이트 중 어느 것에 가장 가까운가요?
2. 한국어 1글자가 몇 토큰인가요?
3. 컨텍스트 창이 초과하면 어떻게 되나요?
4. 입력 토큰과 출력 토큰의 비용이 다른가요?
5. 같은 내용을 더 적은 토큰으로 전달하는 방법이 있나요?

---

## tiktoken으로 토큰 측정

```python
import tiktoken

encoder = tiktoken.encoding_for_model("gpt-4o-mini")

text_en = "Hello, how are you?"
text_ko = "안녕하세요, 잘 지내세요?"

print(f"영어: {len(encoder.encode(text_en))} 토큰")
print(f"한국어: {len(encoder.encode(text_ko))} 토큰")
# 영어: 5 토큰, 한국어: 11 토큰 (대략 2배)
```

## 컨텍스트 창 계산

```python
MODEL_CONTEXT_WINDOWS = {
    "gpt-4o-mini": 128000,
    "gpt-4o": 128000,
    "gpt-3.5-turbo": 16385,
}

def count_messages_tokens(messages: list, model: str = "gpt-4o-mini") -> int:
    encoder = tiktoken.encoding_for_model(model)
    total = 0
    for msg in messages:
        total += len(encoder.encode(msg.get("content", ""))) + 4
    return total + 2

def check_context_limit(messages: list, model: str, max_response_tokens: int = 1000) -> dict:
    used = count_messages_tokens(messages, model)
    limit = MODEL_CONTEXT_WINDOWS.get(model, 128000)
    available = limit - used - max_response_tokens
    return {
        "used": used,
        "limit": limit,
        "available": available,
        "safe": available > 0,
    }
```

## 비용 계산

```python
# gpt-4o-mini 기준 (2024년 기준, 변동 가능)
PRICING = {
    "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
    "gpt-4o": {"input": 5.0 / 1_000_000, "output": 15.0 / 1_000_000},
}

def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    price = PRICING.get(model, PRICING["gpt-4o-mini"])
    return input_tokens * price["input"] + output_tokens * price["output"]
```

## 토큰 절약 팁

```python
def compress_messages(messages: list, max_tokens: int, model: str) -> list:
    """오래된 메시지부터 제거해서 토큰을 절약합니다."""
    while count_messages_tokens(messages, model) > max_tokens and len(messages) > 2:
        # system 메시지(index 0) 보존, 가장 오래된 user/assistant 쌍 제거
        messages.pop(1)
    return messages
```

---

## Before / After

| 항목 | Before (토큰 이해 없음) | After (토큰 관리) |
|------|----------------------|-----------------|
| 비용 예측 | 불가 | estimate_cost로 사전 계산 |
| 컨텍스트 초과 | 갑자기 오류 | check_context_limit |
| 한국어 토큰 | 과소평가 | 2배 예산 설정 |
| 대화 기록 | 무한 누적 | compress_messages |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 한국어=영어 토큰 가정 | 비용 초과 | tiktoken으로 직접 측정 |
| 컨텍스트 확인 없음 | 갑작스러운 오류 | check_context_limit |
| 대화 무제한 누적 | 컨텍스트 초과 | compress_messages |
| 출력 토큰 비용 무시 | 비용 과소평가 | input+output 합산 |

---

## AI 활용 팁

```
tiktoken으로 messages의 총 토큰 수를 계산하고, 컨텍스트 창 한도 내에 있는지 확인하는 함수를 만들어줘.
gpt-4o-mini의 입력/출력 토큰 비용으로 예상 비용을 계산해줘.
컨텍스트 초과 시 오래된 메시지부터 제거하는 compress_messages도 만들어줘.
```

---

## 체크리스트

- [ ] tiktoken 설치 및 인코더 설정
- [ ] count_messages_tokens 구현
- [ ] check_context_limit 구현
- [ ] 비용 계산 함수(input + output)
- [ ] compress_messages(오래된 메시지 제거)
- [ ] 한국어 토큰이 영어보다 많음 인지

---

## 처음 질문으로 돌아가기

"토큰이 그냥 단어랑 비슷한 거 아닌가요?" — 영어는 단어와 비슷하지만, 한국어는 1글자가 2~3 토큰입니다. "안녕하세요"는 5글자지만 10+ 토큰입니다. 한국어 서비스는 토큰 예산을 영어의 2배로 잡아야 합니다.

---

## 정리

- 한국어 토큰은 영어보다 약 2배 많으므로 예산을 여유 있게 설정한다
- tiktoken으로 API 호출 전 토큰을 사전 측정한다
- check_context_limit으로 컨텍스트 창 초과를 사전에 감지한다
- compress_messages로 오래된 대화를 정리해 컨텍스트를 절약한다

---

## 참고 자료

- [tiktoken GitHub](https://github.com/openai/tiktoken)
- [OpenAI 요금 페이지](https://openai.com/pricing)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- tiktoken으로 토큰 측정
- 컨텍스트 창 계산
- 비용 계산
- 토큰 절약 팁
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LLM, Tokens, OpenAI, Python
