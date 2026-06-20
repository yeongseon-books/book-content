---
title: "바이브코딩을 위한 LLM API 운영 (4/6): 캐싱 전략 — 비용과 지연 시간 줄이기"
series: llm-api-production-101
episode: 4
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM
- Caching
- Redis
- Python
---

# 바이브코딩을 위한 LLM API 운영 (4/6): 캐싱 전략 — 비용과 지연 시간 줄이기

이 글은 **바이브코딩을 위한 LLM API 운영** 시리즈의 네 번째 글입니다. LLM API 호출 비용을 줄이기 위한 의미 기반 캐싱과 정확 매칭 캐싱 전략을 다룹니다.

---

같은 질문이 하루에 100번 옵니다. 100번 모두 API를 호출하면 비용도 높고 지연 시간도 깁니다. "이전에 같은 질문이 있었으면 저장된 답을 주면 되지 않나요?" — 맞습니다. 그게 캐싱입니다.

바이브코딩으로 AI에게 "LLM 결과 캐싱해줘"라고 하면 dict 기반 캐시 코드가 나옵니다. "오늘 날씨는?"과 "오늘 날씨 어때?"는 다른 문자열이지만 같은 질문입니다. 의미 기반 캐싱 없이는 캐시 히트율이 낮습니다.

이 글에서는 정확 매칭 캐시와 의미 기반 캐시를 단계적으로 구현합니다.

> "캐싱은 같은 질문에 같은 답을 빠르게 주는 구조입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 정확 매칭 캐시와 의미 기반 캐시의 차이가 무엇인가요?
2. Redis를 LLM 캐시로 사용할 때 TTL을 어떻게 설정하나요?
3. 캐시 키를 어떻게 설계해야 충돌을 방지하나요?
4. 의미 기반 캐싱에서 유사도 임계값을 어떻게 설정하나요?
5. 캐시 히트율을 어떻게 측정하나요?

---

## 정확 매칭 캐시

```python
import hashlib
import json
import redis

class ExactMatchCache:
    def __init__(self, redis_client: redis.Redis, ttl: int = 3600):
        self.redis = redis_client
        self.ttl = ttl

    def _key(self, messages: list, model: str) -> str:
        payload = json.dumps({"messages": messages, "model": model}, sort_keys=True)
        return f"llm:exact:{hashlib.sha256(payload.encode()).hexdigest()}"

    def get(self, messages: list, model: str) -> str | None:
        return self.redis.get(self._key(messages, model))

    def set(self, messages: list, model: str, response: str):
        self.redis.setex(self._key(messages, model), self.ttl, response)
```

## 의미 기반 캐시

```python
import numpy as np
from sentence_transformers import SentenceTransformer

class SemanticCache:
    def __init__(self, embedder, threshold: float = 0.92):
        self.embedder = embedder
        self.threshold = threshold
        self.store: list[tuple[np.ndarray, str]] = []  # (embedding, response)

    def find(self, query: str) -> str | None:
        q_emb = self.embedder.encode([query], normalize_embeddings=True)[0]
        for stored_emb, response in self.store:
            score = float(np.dot(q_emb, stored_emb))
            if score >= self.threshold:
                return response
        return None

    def save(self, query: str, response: str):
        q_emb = self.embedder.encode([query], normalize_embeddings=True)[0]
        self.store.append((q_emb, response))
```

## 계층 캐시

정확 매칭 → 의미 기반 → API 호출 순서로 시도합니다.

```python
def cached_llm_call(query: str, exact_cache, semantic_cache, llm_client) -> dict:
    # 1. 정확 매칭
    if cached := exact_cache.get([{"role": "user", "content": query}], "gpt-4o-mini"):
        return {"response": cached, "source": "exact_cache"}

    # 2. 의미 기반 캐시
    if cached := semantic_cache.find(query):
        return {"response": cached, "source": "semantic_cache"}

    # 3. API 호출
    response = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}],
    )
    result = response.choices[0].message.content

    # 캐시 저장
    exact_cache.set([{"role": "user", "content": query}], "gpt-4o-mini", result)
    semantic_cache.save(query, result)

    return {"response": result, "source": "api"}
```

---

## Before / After

| 항목 | Before (캐시 없음) | After (계층 캐시) |
|------|------------------|-------------------|
| 동일 질문 비용 | 매번 API 호출 | 캐시 히트 시 무료 |
| 응답 속도 | API 대기 시간 | 즉시 반환 |
| 유사 질문 | 별도 API 호출 | 의미 캐시 히트 |
| 캐시 만료 | 없음 | TTL로 자동 정리 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 캐시 키에 model 미포함 | 다른 모델 응답 혼용 | model을 키에 포함 |
| TTL 없음 | 오래된 답변 반환 | 시간 민감 쿼리에 단기 TTL |
| 임계값 너무 낮음 | 관련 없는 캐시 히트 | 0.90~0.95 사용 |
| 히트율 미측정 | 캐시 효과 불명 | source 필드로 추적 |

---

## AI 활용 팁

```
LLM API 호출에 계층 캐시를 추가해줘.
ExactMatchCache는 Redis에 SHA-256 해시 키로 저장하고, TTL은 1시간으로 설정해줘.
SemanticCache는 임베딩 유사도 0.92 이상이면 히트로 처리해줘.
cached_llm_call은 exact → semantic → api 순서로 시도하고 source 필드로 히트 위치를 반환해줘.
```

---

## 체크리스트

- [ ] ExactMatchCache(Redis + SHA-256 키)
- [ ] SemanticCache(임베딩 + 임계값)
- [ ] 캐시 키에 model 포함
- [ ] TTL 설정(시간 민감 쿼리 단기)
- [ ] cached_llm_call 계층 순서
- [ ] source 필드로 히트율 추적

---

## 처음 질문으로 돌아가기

"같은 질문이 많은데 매번 API를 호출해야 하나요?" — 정확 매칭 캐시로 동일 질문을 잡고, 의미 기반 캐시로 유사 질문을 잡으면 API 호출을 크게 줄일 수 있습니다. source 필드로 히트율을 추적하고 임계값을 조정하세요.

---

## 정리

- 정확 매칭 캐시는 Redis + SHA-256 해시 키로 구현한다
- 의미 기반 캐시는 임베딩 유사도(0.92 이상)로 유사 질문을 매칭한다
- exact → semantic → api 순서로 계층 캐시를 시도한다
- source 필드로 캐시 히트율을 추적해 효과를 측정한다

---

## 참고 자료

- [Redis Python 클라이언트](https://redis-py.readthedocs.io/)
- [GPTCache 오픈소스](https://github.com/zilliztech/GPTCache)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 정확 매칭 캐시
- 의미 기반 캐시
- 계층 캐시
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LLM, Caching, Redis, Python
