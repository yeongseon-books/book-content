---
episode: 4
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
title: "LLM API Production 101 (4/6): 캐싱 전략 — 비용과 지연 시간 줄이기"
seo_description: 요청 해시와 TTL을 기준으로 LLM 캐시 키를 설계하고 오래된 응답을 안전하게 무효화하는 방법을 다룹니다.
---

# LLM API Production 101 (4/6): 캐싱 전략 — 비용과 지연 시간 줄이기

LLM 기능이 실제 트래픽을 받기 시작하면 비용 문제는 생각보다 빨리 눈에 들어옵니다. 같은 질문이 반복되고, 같은 시스템 프롬프트가 다시 전송되고, 같은 컨텍스트가 다시 직렬화되고, 결국 같은 답을 또 생성하는 일이 많기 때문입니다. 이때 많은 팀이 먼저 모델 교체나 프롬프트 축소를 고민하지만, 더 앞단에 있는 해법이 있습니다. 이미 계산한 일을 다시 하지 않는 것입니다.

이 글은 LLM API 프로덕션 101 시리즈의 4번째 글입니다.

캐시는 새로운 개념이 아닙니다. 웹 서버, 데이터베이스, CDN, 검색 시스템이 모두 오래전부터 풀어 온 문제입니다. 다만 LLM 경로에서는 “무엇을 같은 요청으로 볼 것인가”가 더 까다롭습니다. 겉으로 보이는 사용자 질문이 같아도 모델, 시스템 프롬프트, temperature, 구조화 출력 옵션이 다르면 사실상 다른 작업일 수 있습니다.

그래서 LLM 캐시는 단순히 응답 문자열을 저장하는 상자가 아닙니다. 어떤 입력 조합이 동일한 작업을 의미하는지 정의하는 계약입니다. 이 계약이 느슨하면 잘못된 재사용이 생기고, 너무 엄격하면 적중률이 떨어집니다. 결국 캐시 설계의 핵심은 저장 방식보다 동일성의 정의에 있습니다.

이번 글에서는 가장 작은 운영형 캐시부터 출발하겠습니다. 요청 payload를 정규화해 해시 키를 만들고, TTL 기반 인메모리 캐시를 붙여 비용과 지연 시간을 줄이는 패턴을 정리합니다.

여기서는 요청 해시와 TTL을 기반으로 같은 작업의 재계산을 피하는 캐싱 전략을 봅니다.

![캐싱 전략: 비용과 지연 시간 줄이기](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/04/04-01-caching-strategies-reducing-cost-and-lat.ko.png)
*캐싱 전략: 비용과 지연 시간 줄이기*
> LLM 캐시의 핵심은 응답을 저장하는 기술이 아니라, 어떤 요청이 정말 같은 작업인지 엄격하게 정의하는 일입니다.

## 먼저 던지는 질문

- LLM 캐시는 응답 저장소가 아니라 왜 요청 동일성 계약으로 봐야 할까요?
- 캐시 키에는 프롬프트 외에 어떤 값이 들어가야 할까요?
- 어떤 경로는 비용이 커도 캐시하지 않는 편이 안전할까요?

## 왜 이 글이 중요한가

캐시는 비용 절감 수단이면서 동시에 정확성 경계입니다. 같은 작업을 다시 계산하지 않으면 지연 시간과 토큰 사용량을 동시에 줄일 수 있습니다. 하지만 잘못된 캐시 키는 다른 작업에 대해 이전 결과를 재사용하게 만들고, 그 순간 캐시는 성능 최적화가 아니라 품질 저하 장치가 됩니다.

LLM 경로에서는 특히 시스템 프롬프트와 생성 옵션이 중요합니다. 사용자가 같은 질문을 했더라도 요약기 프롬프트와 분류기 프롬프트는 같은 작업이 아닙니다. temperature가 0인지 0.8인지도 결과 의미에 영향을 줄 수 있습니다. 그래서 캐시는 “보이는 질문”이 아니라 “실행 계약 전체”를 기준으로 설계해야 합니다.

또한 캐시는 만료와 무효화까지 포함해 생각해야 합니다. 오래된 응답을 영원히 재사용하면 비용은 줄어들지 몰라도 정확성과 신뢰가 무너집니다. TTL과 버전 필드는 캐시를 정직하게 유지하는 최소 장치입니다.

## 핵심 개념

### 왜 LLM 호출 앞에 캐시가 필요한가

![반복 요청에서 비용이 다시 쌓이는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/04/04-01-why-an-llm-path-needs-caching.ko.png)

*반복 요청에서 비용이 다시 쌓이는 흐름*

운영 로그를 보면 반복은 생각보다 많습니다. FAQ형 챗봇, 비슷한 문장 교정을 반복하는 내부 도구, 같은 리포트를 여러 사용자가 보는 대시보드, 같은 질문을 조금씩 바꿔 재질문하는 대화 세션이 모두 그렇습니다. 이런 경로에서는 매번 전체 호출 비용을 다시 내는 것이 비효율적입니다.

문제는 “같은 요청”을 눈으로 판단하면 안 된다는 데 있습니다. 사람이 보기에는 같아 보여도 모델, 시스템 프롬프트, 생성 옵션이 달라지면 사실상 다른 작업입니다. 캐시는 바로 이 경계를 명확히 해 줘야 합니다.

### 캐시 키에는 무엇이 들어가야 하는가

![캐시 키를 이루는 요청 구성 요소 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/04/04-02-what-belongs-in-the-cache-key.ko.png)

*캐시 키를 이루는 요청 구성 요소 구조*

가장 흔한 실수는 사용자 질문 문자열만 키로 쓰는 것입니다.

```python
cache[user_prompt] = response_text
```

이 방식은 너무 느슨합니다. 같은 사용자 질문이라도 모델이 다를 수 있고, 시스템 프롬프트가 다를 수 있으며, `temperature=0`인지 `temperature=0.8`인지도 다를 수 있습니다. JSON 응답을 기대하는 요청과 자유 텍스트를 기대하는 요청도 같은 작업이 아닙니다.

안전한 기본값은 `model`, `messages`, `temperature`, `response_format`, 그리고 필요할 때 `tools`, `max_tokens` 같은 생성 옵션까지 포함하는 것입니다. 즉, 캐시 키는 사람이 읽는 질문이 아니라 정규화된 요청 구조를 대표해야 합니다.

### 요청 해시 만들기

아래 함수는 요청 payload를 canonical JSON으로 만든 뒤 SHA-256 해시로 바꿉니다.

```python
import hashlib
import json
from typing import Any

def build_cache_key(payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

request_payload = {
    "model": "llama-3.1-8b-instant",
    "messages": [
        {"role": "system", "content": "You are a concise summarizer."},
        {"role": "user", "content": "Summarize the difference between FastAPI and Flask in three sentences."},
    ],
    "temperature": 0,
}

print(build_cache_key(request_payload))
```

<!-- injected-output:start -->
**실행 결과**

    6b8029d33b678c483174d55c429edd51a4ab075fab3943a4069fbc89476a6d8f

<!-- injected-output:end -->

`sort_keys=True`는 딕셔너리 키 순서 차이로 같은 요청이 다른 키가 되는 일을 막아 줍니다. `separators`는 불필요한 공백 차이를 없앱니다. 결국 이 해시는 요청 계약 전체를 고정 길이 키로 압축한 결과입니다.

### TTL이 왜 필요한가

![캐시 항목의 생성 만료 갱신 단계](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/04/04-03-why-ttl-matters.ko.png)

*캐시 항목의 생성 만료 갱신 단계*

해시 키만 있으면 캐시는 만들 수 있습니다. 하지만 TTL이 없으면 응답이 영원히 남습니다. 모델 버전이 바뀌거나 프롬프트 정책이 바뀌어도 예전 답을 계속 재사용할 수 있고, 메모리도 계속 증가합니다. TTL은 캐시가 진실의 원본이 아니라 일정 시간 동안만 유효한 복사본이라는 사실을 코드로 표현합니다.

정적 FAQ는 긴 TTL이 가능하지만, 실시간성이 높은 요약은 더 짧아야 합니다. 외부 상태에 의존하는 툴 호출 결과는 TTL을 아주 짧게 두거나 아예 캐시하지 않는 편이 낫습니다. 숫자 하나를 고르는 일보다 TTL을 명시적으로 설계하는 습관이 더 중요합니다.

### 인메모리 TTL 캐시 구현

단일 프로세스 기준의 최소 구현은 아래와 같습니다.

```python
import time
from dataclasses import dataclass
from typing import Any

@dataclass
class CacheEntry:
    value: Any
    expires_at: float

class TTLCache:
    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None

        if time.time() >= entry.expires_at:
            del self._store[key]
            return None

        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = CacheEntry(
            value=value,
            expires_at=time.time() + ttl_seconds,
        )

    def delete(self, key: str) -> None:
        self._store.pop(key, None)
```

이 구현은 lazy eviction을 사용합니다. 읽을 때 만료 여부를 확인하고 지난 항목을 제거합니다. 단순하지만 핵심 동작을 이해하기에는 충분합니다. 다만 이 캐시는 현재 프로세스 안에서만 공유되므로, 여러 워커나 여러 서버가 있는 환경에서는 서비스 전체 공유 캐시가 아닙니다.

### Groq 호출 앞에 캐시 붙이기

![캐시 적중과 미스가 갈리는 실행 경로](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/04/04-04-putting-the-cache-in-front-of-groq-calls.ko.png)

*캐시 적중과 미스가 갈리는 실행 경로*

이제 실제 호출 앞에 캐시를 둡니다.

```python
import hashlib
import json
import os
import time
from dataclasses import dataclass
from typing import Any

from groq import Groq

@dataclass
class CacheEntry:
    value: Any
    expires_at: float

class TTLCache:
    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.time() >= entry.expires_at:
            del self._store[key]
            return None
        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = CacheEntry(value=value, expires_at=time.time() + ttl_seconds)

def build_cache_key(payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

cache = TTLCache()
client = Groq(api_key=os.environ["GROQ_API_KEY"])

def cached_completion(payload: dict[str, Any], ttl_seconds: int = 300) -> dict[str, Any]:
    key = build_cache_key(payload)
    cached = cache.get(key)
    if cached is not None:
        return {"source": "cache", "content": cached}

    completion = client.chat.completions.create(**payload)
    content = completion.choices[0].message.content
    cache.set(key, content, ttl_seconds=ttl_seconds)
    return {"source": "model", "content": content}

payload = {
    "model": "llama-3.1-8b-instant",
    "messages": [
        {"role": "system", "content": "You are a concise Python tutor."},
        {"role": "user", "content": "Explain Python dataclasses in three sentences."},
    ],
    "temperature": 0,
}

print(cached_completion(payload))
print(cached_completion(payload))
```

<!-- injected-output:start -->
**실행 결과**

    {'source': 'model', 'content': 'Python dataclasses are a feature introduced in Python 3.7 that allows you to create classes with minimal boilerplate code, making it easier to define simple data structures. They automatically generate special methods like `__init__`, `__repr__`, and `__eq__` for you, reducing the amount of code you need to write. Dataclasses can be used to create immutable or mutable data structures, and they support features like type hints and fields with default values.'}
    {'source': 'cache', 'content': 'Python dataclasses are a feature introduced in Python 3.7 that allows you to create classes with minimal boilerplate code, making it easier to define simple data structures. They automatically generate special methods like `__init__`, `__repr__`, and `__eq__` for you, reducing the amount of code you need to write. Dataclasses can be used to create immutable or mutable data structures, and they support features like type hints and fields with default values.'}

<!-- injected-output:end -->

첫 번째 요청은 모델로 가고, 두 번째는 같은 payload이므로 캐시를 적중합니다. 여기서 `source`를 함께 반환하는 이유는 캐시 동작을 로그와 메트릭에서 관측 가능하게 만들기 위해서입니다.

### 어떤 경로는 캐시하지 말아야 한다

![캐시 가능 경로와 우회 경로의 판단 비교](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/04/04-05-when-not-to-cache.ko.png)

*캐시 가능 경로와 우회 경로의 판단 비교*

모든 응답이 캐시 대상은 아닙니다. 빠르게 바뀌는 외부 데이터에 의존하는 응답, 사용자별 권한이 다른 응답, 민감한 개인정보를 포함하는 응답, 높은 temperature에서 다양성이 중요한 생성 작업은 특히 조심해야 합니다. 같은 질문이라도 정답이 실제로 달라질 수 있기 때문입니다.

무효화는 TTL만으로 끝나지 않습니다. 프롬프트 정책, 모델, 출력 형식, 비즈니스 규칙이 바뀌었다면 캐시 버전도 함께 바꾸는 편이 안전합니다.

```python
messages = [
    {"role": "system", "content": "You are a concise summarizer."},
    {"role": "user", "content": "Summarize the FastAPI and Flask difference."},
]

payload = {
    "cache_version": "v2",
    "model": "llama-3.1-8b-instant",
    "messages": messages,
    "temperature": 0,
}
```

이 패턴은 오래된 항목이 자연 만료되기를 기다리는 것보다 훨씬 예측 가능합니다. 새 계약에는 새 버전을 쓰면 됩니다.

### 적중률과 오래된 응답을 함께 측정하기

캐시를 붙였다고 끝이 아닙니다. 운영에서는 적중률이 얼마나 나오는지, 오래된 응답이 너무 오래 남지 않는지, 어떤 경로가 계속 미스가 나는지 함께 봐야 합니다. 아래처럼 최소 메트릭 카운터를 붙여 두면 캐시가 실제로 비용을 줄이는지 확인하기 쉽습니다.

```python
import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any

@dataclass
class CacheEntry:
    value: Any
    expires_at: float

class TTLCache:
    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}
        self.metrics = {"hits": 0, "misses": 0, "expired": 0}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            self.metrics["misses"] += 1
            return None

        if time.time() >= entry.expires_at:
            self.metrics["expired"] += 1
            self.metrics["misses"] += 1
            del self._store[key]
            return None

        self.metrics["hits"] += 1
        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = CacheEntry(value=value, expires_at=time.time() + ttl_seconds)

def build_cache_key(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

cache = TTLCache()
payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "hi"}]}
key = build_cache_key(payload)

print(cache.get(key))
cache.set(key, "cached-response", ttl_seconds=1)
print(cache.get(key))
time.sleep(1.1)
print(cache.get(key))
print(cache.metrics)
```

<!-- injected-output:start -->
**실행 결과**

    None
    cached-response
    None
    {'hits': 1, 'misses': 2, 'expired': 1}

<!-- injected-output:end -->

이 정도만 있어도 운영 판단이 쉬워집니다. 적중률은 낮은데 만료가 거의 없다면 키가 너무 엄격할 수 있고, 만료가 자주 나는데도 오래된 응답 이슈가 생긴다면 TTL이 여전히 길 수 있습니다. 캐시는 성능 기능이면서 동시에 정확성 기능이기 때문에, hit/miss/expired를 함께 보는 습관이 필요합니다.

### Redis로 확장: 프로세스를 넘어 공유 캐시 만들기

인메모리 캐시는 로직 학습용으로는 좋지만, 워커가 여러 개인 실제 배포에서는 적중률이 분산됩니다. 같은 요청이 워커마다 한 번씩 모델로 나가면 비용 절감 효과가 급격히 떨어집니다. 이때는 Redis 같은 공유 저장소를 앞단에 두는 편이 실용적입니다.

```python
import hashlib
import json
from typing import Any

import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def build_cache_key(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"llm:completion:v1:{digest}"

def get_cached_text(payload: dict[str, Any]) -> str | None:
    key = build_cache_key(payload)
    return r.get(key)

def set_cached_text(payload: dict[str, Any], text: str, ttl_seconds: int) -> None:
    key = build_cache_key(payload)
    r.setex(key, ttl_seconds, text)
```

여기서 중요한 실무 포인트는 네임스페이스입니다. `llm:completion:v1:` 같은 prefix를 두면 운영 중 삭제 범위를 제어하기 쉬워집니다. 긴급 무효화가 필요하면 버전 prefix를 올리거나, 특정 prefix를 기준으로 정리 작업을 수행할 수 있습니다.

### Semantic 캐시: 문장이 조금 달라도 같은 의미면 재사용하기

정확 일치 키만 쓰면 안전하지만 적중률이 낮을 수 있습니다. 질문이 단어만 조금 다른 경우에는 매번 새 호출이 발생합니다. 이때는 임베딩 유사도를 이용한 semantic 캐시를 보조 계층으로 붙일 수 있습니다.

```python
from dataclasses import dataclass

@dataclass
class SemanticEntry:
    query: str
    embedding: list[float]
    answer: str

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def find_semantic_hit(
    query_embedding: list[float],
    entries: list[SemanticEntry],
    threshold: float = 0.92,
) -> SemanticEntry | None:
    best: SemanticEntry | None = None
    best_score = 0.0
    for entry in entries:
        score = cosine_similarity(query_embedding, entry.embedding)
        if score > best_score:
            best_score = score
            best = entry

    if best is not None and best_score >= threshold:
        return best
    return None
```

이 접근은 비용 절감에 강하지만 오적중 위험이 있습니다. 따라서 기본값은 `exact-key cache -> semantic cache -> model call` 순서가 안전합니다. 또 semantic 캐시를 통과한 응답은 로그에 `cache_source=semantic`과 `similarity_score`를 남겨 품질 회귀를 감시해야 합니다.

## 흔히 헷갈리는 지점

- 사용자 질문만 같으면 같은 캐시 키로 봐도 된다고 생각하기 쉽지만 대부분은 너무 느슨합니다.
- TTL은 성능 옵션이 아니라 정확성 유지 장치입니다.
- 인메모리 캐시는 단일 프로세스 예제일 뿐 서비스 전체 공유 캐시가 아닙니다.
- 외부 상태나 사용자 권한이 반영된 응답은 캐시 키에 범위를 넣거나 아예 캐시하지 않아야 합니다.
- 캐시 적중률만 높이면 된다고 생각하면 오래된 응답 재사용이라는 더 큰 문제를 놓치기 쉽습니다.

## 운영 체크리스트

- [ ] 모델, 메시지, temperature, 응답 형식을 캐시 키에 포함했다
- [ ] canonical JSON 직렬화와 해시로 안정적인 요청 키를 만들었다
- [ ] TTL을 workload별로 명시하고 기본값을 코드에 고정했다
- [ ] 사용자별·민감 정보 응답의 캐시 정책을 별도로 정했다
- [ ] 모델/프롬프트 변경 시 `cache_version`으로 명시적 무효화를 지원했다

## 정리

이번 글에서는 요청 해시와 TTL을 기반으로 한 가장 작은 LLM 캐시를 만들었습니다. 핵심은 응답 문자열을 저장하는 행위보다, 어떤 요청이 정말 같은 작업인지 정확하게 정의하는 데 있습니다. 이 경계가 명확해야 캐시는 비용과 지연 시간을 줄이면서도 품질을 해치지 않습니다.

또한 캐시는 유효 기간과 무효화까지 포함해 생각해야 합니다. TTL과 버전 필드가 없으면 캐시는 금방 오래된 응답 저장소가 됩니다. 반대로 이 두 장치가 있으면 캐시는 단순한 최적화가 아니라 운영 계약의 일부가 됩니다.

다음 글에서는 반복 비용이 아니라 실패 경로를 다룹니다. 캐시로 해결되지 않는 일시적 장애를 언제, 무엇만, 얼마나 재시도해야 안정성이 올라가는지 다룹니다.

## 처음 질문으로 돌아가기

- **LLM 캐시는 응답 저장소가 아니라 왜 요청 동일성 계약으로 봐야 할까요?**
  캐시는 단순히 답을 저장하는 것이 아니라, 두 요청이 같은 작업인지 판정하는 계약이기 때문에 요청 동일성 정의가 먼저입니다.

- **캐시 키에는 프롬프트 외에 어떤 값이 들어가야 할까요?**
  프롬프트, 모델, 주요 옵션, 시스템 지침, 스키마 버전처럼 출력 의미를 바꾸는 값을 캐시 키에 포함해야 합니다.

- **어떤 경로는 비용이 커도 캐시하지 않는 편이 안전할까요?**
  사용자별 권한, 최신성이 중요한 데이터, 안전 검토 결과처럼 오래된 응답이 위험한 경로는 캐시하지 않는 편이 안전합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM API Production 101 (1/6): 구조화 출력 — JSON 모드와 응답 스키마](./01-structured-output.md)
- [LLM API Production 101 (2/6): 툴 호출 — 함수를 모델에 연결하기](./02-tool-calling.md)
- [LLM API Production 101 (3/6): 스트리밍 심화 — 청크 처리와 오류 복구](./03-streaming-in-depth.md)
- **LLM API Production 101 (4/6): 캐싱 전략 — 비용과 지연 시간 줄이기 (현재 글)**
- LLM API Production 101 (5/6): 재시도와 오류 처리 — 안정적인 API 호출 만들기 (예정)
- LLM API Production 101 (6/6): 속도 제한 관리 — Rate Limit 대응 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Groq Text Chat docs](https://console.groq.com/docs/text-chat)
- [Python hashlib documentation](https://docs.python.org/3/library/hashlib.html)

### 검증 보조 자료
- [Python json.dumps documentation](https://docs.python.org/3/library/json.html#json.dumps)

### 관련 시리즈
- [스트리밍 심화 — 청크 처리와 오류 복구](./03-streaming-in-depth.md)
- [재시도와 오류 처리 — 안정적인 API 호출 만들기](./05-retry-and-error-handling.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-api-production-101/ko/04-caching-strategies)

Tags: LLM, OpenAI, Streaming, Python
