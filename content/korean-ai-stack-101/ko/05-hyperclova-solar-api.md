---
title: "Korean AI Stack 101 (5/6): HyperCLOVA X와 Solar API 사용하기"
series: korean-ai-stack-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- HyperCLOVA
- Solar
- LLM API
- Naver
- Upstage
last_reviewed: '2026-05-15'
seo_description: 공급자를 바꾸는 일은 모델 이름 교체가 아니라 인증, 메시지, 샘플링, 응답 계약을 함께 바꾸는 일입니다.
---

# Korean AI Stack 101 (5/6): HyperCLOVA X와 Solar API 사용하기

한국어 중심 생성 모델을 붙이기 시작하면 어려운 지점은 모델 이름이 아닙니다. 인증, 프롬프트, 출력 형식, 검증이 운영에서 흔들리지 않도록 호출 계약을 먼저 고정하는 일이 훨씬 중요합니다.

이 글은 Korean AI Stack 101 시리즈의 5번째 글입니다. 여기서는 HyperCLOVA X와 Solar 같은 한국어 LLM API를 안전하게 호출하는 패턴을 정리합니다.

![Korean AI Stack 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/05/05-01-core-flow.ko.png)
*Korean AI Stack 101 5장 흐름 개요*

## 먼저 던지는 질문

- 프롬프트 튜닝보다 먼저 고정해야 할 API 계약은 무엇일까요?
- HyperCLOVA X나 Solar 같은 한국어 생성 API를 도입할 때는 무엇부터 검증해야 할까요?
- 실행 예제가 왜 Groq `llama-3.1-8b-instant`를 대체 모델로 쓰는 걸까요?

## 왜 이 단계가 중요한가

이 글은 한국어 생성 API를 안전하게 호출하는 패턴을 다룹니다. 앞 글들은 임베딩(KoSimCSE, BGE-M3)과 OCR(CLOVA)로 입력 데이터를 정리했습니다. 이번 글은 그 위에서 답을 만드는 단계입니다. HyperCLOVA X(NAVER)와 Solar(Upstage)는 한국어 표현력이 좋지만, 실제 운영 문제는 인증 방식, 지연 시간, 에러 코드, 토큰 한도, 프롬프트 캐시처럼 호출 계약 쪽에서 더 자주 터집니다.

이 주제를 별도 글로 다루는 이유도 여기에 있습니다. 많은 팀이 한국어에 맞춘 모델만 쓰면 품질이 좋아질 것이라 기대하지만, system 메시지, temperature, 출력 형식, timeout이 기본값에 머물면 응답 흔들림도 그대로 남습니다. 현실적인 학습 경로는 두 단계입니다. 먼저 Groq의 OpenAI 호환 인터페이스로 감을 잡고, 마지막에 HyperCLOVA나 Solar로 교체합니다.

## 멘탈 모델

생성 API 호출은 네 겹의 계약으로 나뉩니다.

```text
[call contract]    auth, endpoint, rate limit, timeout, retry
     |
     v
[message contract] system / user / assistant roles, Korean system prompt
     |
     v
[sampling contract] temperature, top_p, max_tokens, stop sequences
     |
     v
[response contract] choices[0].message.content post-processing, JSON validation, safety filters
```

가장 중요한 것은 세 가지입니다.

- **모델 교체는 네 겹 모두를 건드립니다**: 모델 이름만 바꾸는 것으로 운영화가 끝나지 않습니다. 한 층만 달라져도 응답 분포가 달라집니다.
- **OpenAI 호환은 표준이 아닙니다**: Groq, Solar, vLLM은 모두 OpenAI 호환을 말하지만 timeout 처리, rate-limit 헤더, 에러 코드는 서로 다릅니다.
- **한국어 유창성은 사실 정확성과 다릅니다**: HyperCLOVA나 Solar가 자연스러운 한국어를 잘 내놓는다고 해서 자동으로 정확해지지는 않습니다. 그 간극은 다음 글의 검색 단계가 메웁니다.

추가로 두 가지를 더 기억하면 좋습니다.

- HyperCLOVA X는 NAVER Cloud Platform 인증을, Solar는 Upstage API 키를 사용합니다. OpenAI SDK는 HyperCLOVA를 직접 호출하지 못하지만, Solar는 `base_url` 교체로 대부분 동작합니다.
- Groq은 학습용 기준선으로 쓰기 좋은 OpenAI 호환 인터페이스에 가깝습니다.

> 멘탈 모델을 한 줄로 줄이면 이렇습니다. 생성 API 운영은 “모델 호출”이 아니라 “호출, 메시지, 샘플링, 응답을 한 세트로 고정하는 일”입니다.

## 핵심 개념

| 항목 | 의미 |
| --- | --- |
| HyperCLOVA X | NAVER의 한국어 중심 LLM. NCP를 통해 제공 |
| Solar | Upstage의 한국어/영어 LLM. Solar Pro/Mini 계열 포함 |
| Groq | LPU 기반 초저지연 추론 서비스. OpenAI 호환 |
| `temperature` | 샘플링 무작위성. 0.0은 결정적, 1.0+는 더 창의적 |
| `max_completion_tokens` | 응답 토큰 상한. 넘으면 잘림 |
| System prompt | 페르소나, 문체, 언어를 고정하는 첫 메시지 |
| Stop sequence | 생성을 멈추는 토큰 시퀀스. JSON 강제에 유용 |
| Output validation | JSON 스키마, 정규식, 길이 검사 같은 후처리 |

## 적용 전후 비교

**Before** — system 메시지 없이 영어 사용자 프롬프트로 호출하면 한국어 답변에 영어 단어가 섞이고, 기본 temperature(대개 1.0 전후) 때문에 같은 질문에도 매번 다른 답이 나옵니다.

**After** — 한국어 system 메시지와 `temperature=0.3`을 주면 동작이 이렇게 안정됩니다.

```python
# 같은 질문으로 세 번 호출합니다
'벡터 검색은 의미 유사도 기반, 키워드 검색은 문자 일치 기반입니다...'
'벡터 검색은 임베딩으로 의미를 비교하고, 키워드 검색은 토큰 매칭에 의존합니다...'
'벡터 검색은 의미를 벡터 공간에서 비교하고, 키워드 검색은 단어 단위 매칭입니다...'
```

중요한 점은 세 가지입니다. 첫째, “의미”, “임베딩”, “토큰” 같은 핵심 개념이 매번 유지됩니다. 둘째, 표현은 달라도 사실은 안정적으로 유지됩니다. 셋째, 응답 길이가 예측 가능해 후처리 비용을 통제할 수 있습니다.

## 핵심 흐름

## 왜 공급자 대체 실습도 충분히 도움이 될까

![최소 실행 예제](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/05/05-01-minimal-runnable-example.ko.png)

*최소 실행 예제*

독자가 항상 HyperCLOVA X나 Solar 키를 갖고 있는 것은 아닙니다. 예제가 실행되지 않으면 프롬프트 설계 교훈도 추상적으로 남습니다. 대체 공급자를 써도 오래 가는 부분은 충분히 배울 수 있습니다. 마지막 단계에서 endpoint와 인증 헤더만 바꾸면, 같은 system 메시지, 샘플링 설정, 응답 검증 로직을 그대로 재사용할 수 있기 때문입니다.

## 단계별 실습

### 단계 1 — 한국어 시스템 메시지로 기본 Groq 호출

```python
import os
from groq import Groq

client = Groq(api_key=os.environ['GROQ_API_KEY'])
response = client.chat.completions.create(
    model='llama-3.1-8b-instant',
    temperature=0.3,
    max_completion_tokens=300,
    messages=[
        {'role': 'system', 'content': '당신은 한국어 제품 문서를 설명하는 시니어 개발자입니다. 항상 한국어로, 3~5문장으로 답합니다.'},
        {'role': 'user', 'content': '벡터 검색과 키워드 검색의 차이를 한국어로 설명해 주세요.'},
    ],
)
print(response.choices[0].message.content)
```

중요한 점은 **언어, 역할, 길이**를 모두 시스템 메시지에 넣는 것입니다. 그러면 사용자 메시지는 훨씬 깔끔해집니다.

### 단계 2 — 출력 형식 제한 (JSON 강제)
![이 코드에서 주목할 점](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/05/05-02-what-to-notice-in-this-code.ko.png)

*이 코드에서 주목할 점*

```python
import json

response = client.chat.completions.create(
    model='llama-3.1-8b-instant',
    temperature=0.0,
    max_completion_tokens=200,
    response_format={'type': 'json_object'},
    messages=[
        {'role': 'system', 'content': '당신은 한국어 답변을 JSON으로 반환합니다. {"summary": str, "keywords": [str]} 형태만 사용합니다.'},
        {'role': 'user', 'content': '벡터 검색의 핵심을 한 줄 요약과 키워드 3개로 정리해 주세요.'},
    ],
)
data = json.loads(response.choices[0].message.content)
assert 'summary' in data and 'keywords' in data
print(data)
```

`response_format='json_object'`와 system 메시지 안의 명시적 스키마는 한 쌍입니다. 둘 중 하나라도 빠지면 JSON이 아닌 응답이 새어 나옵니다.

### 단계 3 — 타임아웃과 재시도

```python
import time
from groq import Groq, APIConnectionError, RateLimitError

def call_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model='llama-3.1-8b-instant',
                temperature=0.3,
                max_completion_tokens=300,
                messages=messages,
                timeout=10.0,
            )
        except (APIConnectionError, RateLimitError) as e:
            wait = 2 ** attempt
            print(f"retry {attempt+1}/{max_retries} after {wait}s: {e}")
            time.sleep(wait)
    raise RuntimeError('all retries failed')
```

지수 백오프와 timeout은 항상 같이 가야 합니다. timeout이 없으면 hang된 호출 앞에서 재시도도 영원히 기다릴 수 있습니다.

### 단계 4 — 응답 검증과 마스킹

```python
import re

def sanitize(text):
    text = re.sub(r'\b\d{2,3}-\d{3,4}-\d{4}\b', '[PHONE]', text)
    text = re.sub(r'\b\d{6}-\d{7}\b', '[RRN]', text)  # Korean resident number pattern
    return text

def validate(text, min_len=20, max_len=2000):
    if not (min_len <= len(text) <= max_len):
        raise ValueError(f'length out of range: {len(text)}')
    if any(bad in text for bad in ['죄송합니다, 제가', 'I cannot', 'As an AI']):
        raise ValueError('refusal-like response')
    return text

raw = response.choices[0].message.content
clean = sanitize(validate(raw))
```

검증은 생성 직후, 사용자에게 보여 주기 전에 바로 돌려야 합니다. 마스킹은 로그나 캐시에 넣기 직전에 한 번 더 거치면 됩니다.

### 단계 5 — HyperCLOVA / Solar 전환 (개념)

![엔지니어가 헷갈리는 지점](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/05/05-03-where-engineers-get-confused.ko.png)

*엔지니어가 헷갈리는 지점*

```python
# Solar(Upstage) 통화 — OpenAI SDK 호환
from openai import OpenAI

solar = OpenAI(
    api_key=os.environ['UPSTAGE_API_KEY'],
    base_url='https://api.upstage.ai/v1/solar',
)
response = solar.chat.completions.create(
    model='solar-mini',
    temperature=0.3,
    max_tokens=300,
    messages=[
        {'role': 'system', 'content': '당신은 한국어 제품 문서를 설명하는 시니어 개발자입니다.'},
        {'role': 'user', 'content': '벡터 검색과 키워드 검색의 차이를 설명해 주세요.'},
    ],
)
```

Solar는 `base_url`만 바꾸면 Groq 예제 대부분이 그대로 옮겨집니다. HyperCLOVA X는 NCP 전용 SDK나 REST 호출이 필요하지만, 메시지, 샘플링, 검증 층은 동일합니다.

## 이 코드에서 먼저 봐야 할 점

- system 메시지 한 줄에 **언어, 역할, 길이**를 모두 담으면 user 메시지는 최소한으로 유지됩니다.
- `temperature=0.3`은 설명형 한국어 답변에 좋은 출발점입니다. 창의적 글쓰기는 0.7 이상이 어울립니다.
- JSON 강제는 `response_format`과 명시적 schema system 메시지 **둘 다** 필요합니다.
- timeout 없는 retry는 위험합니다. 반드시 짝으로 두세요.
- 공급자를 교체할 때 바뀌는 것은 endpoint와 인증이고, 유지되는 것은 메시지, 검증, 마스킹입니다.

## 자주 하는 실수

- **system 메시지를 두지 않는 것** — 낮은 temperature에서도 페르소나가 흔들립니다. 한 줄짜리 system 메시지가 가장 큰 효과를 냅니다.
- **기본 temperature를 믿는 것** — 공급자마다 기본값이 다릅니다. 환경 간 재현성을 원하면 직접 고정해야 합니다.
- **`max_tokens` 상한을 두지 않는 것** — 한국어는 영어보다 토큰 비용이 더 들 수 있습니다. 상한이 없으면 비용이 빠르게 커집니다.
- **OpenAI SDK가 모든 한국어 모델에 닿는다고 생각하는 것** — Solar는 대체로 그렇지만 HyperCLOVA X는 아닙니다. 통합 전에 먼저 확인해야 합니다.
- **raw 응답을 그대로 노출하는 것** — refusal 문구나 개인정보가 그대로 새어 나올 수 있습니다. 항상 검증과 마스킹을 거치세요.
- **유창함을 정확함으로 오해하는 것** — 자연스러운 답변이 사실 기반 답변을 보장하지는 않습니다. 정확성은 다음 글의 RAG가 보강합니다.

## 실무 적용

- **이중 공급자 운영**: Solar를 기본으로 두고 HyperCLOVA X를 fallback으로 둘 수 있습니다. 메시지 코드는 공유하고 endpoint만 바꾸면 됩니다.
- **프롬프트 캐시**: 긴 system 메시지가 반복되면 OpenAI 호환 캐시로 지연과 비용을 꽤 줄일 수 있습니다.
- **스트리밍**: 200토큰을 넘는 응답은 `stream=True`로 흘려 보내는 편이 체감 지연을 크게 줄입니다.
- **로그 마스킹**: production 로그에는 raw prompt를 그대로 저장하지 말고 `sanitize()` 결과만 남겨야 합니다.
- **온도/길이 A/B 테스트**: 0.3 vs 0.5, max_tokens 200 vs 400을 사용자 만족도와 함께 비교하면 한국어 응답의 변동 폭을 더 빨리 읽을 수 있습니다.
- **모니터링 지표**: TTFT, 종단 지연, refusal 비율, JSON 파싱 실패율, 평균 입력/출력 토큰은 기본 대시보드 항목입니다.

## 체크리스트

- [ ] system 메시지에 대상 독자, 문체, 언어를 명시했습니다.
- [ ] `temperature`와 토큰 한도를 출력 비교 전에 먼저 고정했습니다.
- [ ] 출력 형식을 bullet, JSON, 또는 다른 명시적 형태로 제한했습니다.
- [ ] `timeout`과 `retry`를 같이 두었습니다.
- [ ] 생성 직후 검증과 마스킹을 한 번 실행합니다.
- [ ] 공급자를 바꿀 때 인증, 오류 처리, 지연 시간을 다시 점검합니다.

## 연습 문제

1. 같은 system 메시지로 `temperature` 0.0, 0.3, 0.7을 각각 다섯 번 호출해 보세요. 응답 길이와 핵심 용어 빈도가 어떻게 달라지는지 비교해 보세요.
2. JSON 강제 호출에서 system 메시지의 스키마를 빼고 `response_format`만 남겨 보세요. 얼마나 안정적으로 JSON이 유지되는지 확인해 보세요.
3. Solar 또는 HyperCLOVA 키가 있다면 같은 메시지를 보내고, Groq와의 지연 시간, refusal 비율, 응답 길이를 작은 표로 비교해 보세요.

## HyperCLOVA X REST 호출 예시

OpenAI 호환 인터페이스는 Solar나 일부 공급자에서는 편리하지만, HyperCLOVA X는 NCP 전용 REST 계약을 이해해야 운영이 안정적입니다. 실제 운영에서는 SDK wrapper를 쓰더라도 원시 요청/응답 형식을 한 번은 확인해 두는 편이 좋습니다.

```python
import os
import requests

def call_hyperclova_x(prompt: str) -> str:
    host = os.environ['NCP_APIGW_HOST']
    endpoint = '/testapp/v1/chat-completions/HCX-005'
    url = f'https://{host}{endpoint}'

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'X-NCP-CLOVASTUDIO-API-KEY': os.environ['NCP_CLOVA_API_KEY'],
        'X-NCP-APIGW-API-KEY': os.environ['NCP_APIGW_API_KEY'],
        'X-NCP-CLOVASTUDIO-REQUEST-ID': 'korean-ai-stack-101-ep05',
    }

    payload = {
        'messages': [
            {'role': 'system', 'content': '당신은 한국어 기술 문서를 설명하는 시니어 개발자입니다.'},
            {'role': 'user', 'content': prompt},
        ],
        'topP': 0.8,
        'topK': 0,
        'temperature': 0.3,
        'maxTokens': 320,
        'repeatPenalty': 1.1,
        'includeAiFilters': True,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=12)
    resp.raise_for_status()
    data = resp.json()
    return data['result']['message']['content']
```

핵심은 모델 이름이 아니라 헤더 계약입니다. 운영 이슈의 상당수는 키 이름 오타, request id 누락, timeout 미설정에서 시작합니다.

## 한국어 응답 품질을 측정하는 작은 벤치마크

유창함과 정확도를 분리해 보려면 평가 세트를 아주 작게라도 만들어야 합니다. 다음은 한국어 기술 Q&A 기준선에서 자주 쓰는 최소 지표입니다.

| 지표 | 정의 | 초기 기준값 예시 |
| --- | --- | --- |
| Format pass rate | JSON 응답 강제 시 파싱 성공 비율 | 0.98 이상 |
| Refusal precision | 답할 수 없는 질문에서 거절 규칙 준수 비율 | 0.95 이상 |
| Citation presence rate | 답변에 출처 라인 포함 비율 | 0.99 이상 |
| Korean consistency | 영어 혼입 없는 한국어 문체 유지 비율 | 0.97 이상 |

아래처럼 간단한 자동 점검 함수를 두면 배포 전 회귀를 빠르게 걸러낼 수 있습니다.

```python
import json
import re

def check_generation_contract(raw_text: str):
    result = {
        'len_ok': 20 <= len(raw_text) <= 2000,
        'has_sources': '[sources:' in raw_text,
        'no_ai_slop': not any(
            bad in raw_text for bad in ['As an AI', 'I cannot', '저는 AI']
        ),
        'mostly_korean': bool(re.search(r'[가-힣]', raw_text)),
    }
    return result

sample = '결제 동기화 지연을 먼저 확인하세요. [sources: 0,1]'
print(json.dumps(check_generation_contract(sample), ensure_ascii=False))
```

## 생산 환경 구성 예시: 이중 공급자 라우팅

한국어 서비스에서는 하나의 공급자만 고정하기보다 기본/대체 경로를 미리 준비해 두는 편이 안전합니다. 지연 급증이나 일시 장애에서 빠르게 우회할 수 있기 때문입니다.

```yaml
llm_router:
  primary: solar-mini
  fallback: hyperclova-x
  timeout_ms: 10000
  max_retries: 2

providers:
  solar:
    base_url: https://api.upstage.ai/v1/solar
    model: solar-mini
    temperature: 0.3
    max_tokens: 320

  hyperclova:
    host_env: NCP_APIGW_HOST
    endpoint: /testapp/v1/chat-completions/HCX-005
    temperature: 0.3
    max_tokens: 320

guardrails:
  require_citation: true
  reject_if_no_json_when_required: true
  pii_mask_before_log: true
```

이 설정을 코드와 분리해 두면 공급자 전환을 PR 한 건으로 끝낼 수 있고, 온도/길이 조정 이력도 명확하게 남습니다.

## 오류 코드 분류와 재시도 정책

API 호출 실패는 무조건 재시도하면 오히려 상황을 악화시킬 수 있습니다. 상태 코드별 대응을 먼저 정의해 두는 편이 좋습니다.

| 상태 코드 | 의미 | 권장 대응 |
| --- | --- | --- |
| 400 | 요청 형식 오류 | 재시도하지 않고 즉시 실패 처리 |
| 401/403 | 인증/권한 문제 | 키 회전 알람, 재시도 금지 |
| 429 | 속도 제한 | 지수 백오프 후 제한 횟수 재시도 |
| 500/502/503 | 일시 서버 오류 | 짧은 백오프 재시도 후 fallback 전환 |
| timeout | 네트워크/지연 | timeout 증가보다 요청 축소와 fallback 우선 |

```python
def should_retry(status_code: int) -> bool:
    return status_code in (429, 500, 502, 503)
```

이 규칙을 라우터 레벨에 넣어 두면 모델별 SDK가 달라도 운영 정책은 일관되게 유지됩니다.

## 한국어 시스템 프롬프트 템플릿 예시

프롬프트 품질은 길이보다 계약이 중요합니다. 한국어 기술 문서 답변용으로 자주 쓰는 템플릿은 아래 정도면 충분합니다.

```text
당신은 한국어 기술 문서를 설명하는 시니어 개발자입니다.
규칙:
1) 반드시 한국어로 답합니다.
2) 제공된 문맥에 없는 내용은 추측하지 말고 '문맥에서 확인하지 못했습니다.'라고 답합니다.
3) 답변 마지막 줄에 [sources: ...] 형식으로 출처 번호를 적습니다.
4) 불필요한 사과문, 자기소개, 모델 언급을 하지 않습니다.
```

이 템플릿을 고정하면 모델을 바꿔도 문체와 안전 규칙이 유지되어, 사용자 입장에서 제품이 덜 흔들립니다.

## 호출 비용과 지연을 함께 관리하는 운영 표

LLM API 운영에서는 품질만큼 비용과 지연이 중요합니다. 아래처럼 요청당 입력/출력 토큰과 p95 지연을 한 표에 묶어 추적하면 의사결정이 빨라집니다.

| 프로필 | temperature | max_tokens | 평균 입력 토큰 | 평균 출력 토큰 | p95 지연(ms) | 요청당 비용(상대) |
| --- | --- | --- | --- | --- | --- | --- |
| concise-support | 0.2 | 180 | 420 | 120 | 820 | 1.0x |
| default-explain | 0.3 | 320 | 530 | 210 | 1210 | 1.6x |
| long-report | 0.4 | 700 | 760 | 520 | 2480 | 3.1x |

운영팀은 이 표를 기준으로 제품 기능별 프로필을 나눠야 합니다. 모든 기능에 같은 토큰 상한을 주면 비용과 지연이 빠르게 불안정해집니다.

## production 코드 예시: 공급자 추상화 인터페이스

공급자 교체를 안전하게 하려면 호출 코드를 인터페이스로 감싸 두는 편이 좋습니다.

```python
from dataclasses import dataclass

@dataclass
class LLMRequest:
    system: str
    user: str
    temperature: float = 0.3
    max_tokens: int = 320

class LLMProvider:
    def generate(self, req: LLMRequest) -> str:
        raise NotImplementedError

class SolarProvider(LLMProvider):
    def __init__(self, client, model='solar-mini'):
        self.client = client
        self.model = model

    def generate(self, req: LLMRequest) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            messages=[
                {'role': 'system', 'content': req.system},
                {'role': 'user', 'content': req.user},
            ],
        )
        return resp.choices[0].message.content
```

이 구조를 쓰면 실험 단계에서는 Solar를, 규제나 계약 요건이 필요한 환경에서는 HyperCLOVA를 같은 인터페이스로 교체할 수 있습니다.

## 정리

이 글에서 남길 포인트는 한국어 생성 API를 네 겹의 계약, 즉 호출·메시지·샘플링·응답으로 나누어 운영하는 감각입니다. 시스템 메시지, temperature, 출력 형식, timeout만 한 번 제대로 고정해 두면 공급자 교체나 모델 업그레이드는 한두 줄 수정으로 끝나는 경우가 많습니다. 한국어 유창함은 쉽게 얻을 수 있지만, 사실 제어는 다음 글의 검색 단계가 책임집니다.

다음 글에서는 6편이자 마지막 글인 한국어 RAG 파이프라인을 조합합니다. BGE-M3 검색, CLOVA OCR 텍스트, 이 글의 LLM 호출을 하나의 흐름으로 묶어 사실 기반 한국어 응답을 만드는 최소 RAG를 코드로 완성합니다.

## 처음 질문으로 돌아가기

- **프롬프트 튜닝보다 먼저 고정해야 할 API 계약은 무엇일까요?**
  - 본문의 기준은 HyperCLOVA X와 Solar API 사용하기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **HyperCLOVA X나 Solar 같은 한국어 생성 API를 도입할 때는 무엇부터 검증해야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **실행 예제가 왜 Groq `llama-3.1-8b-instant`를 대체 모델로 쓰는 걸까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Korean AI Stack 101 (1/6): 한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [Korean AI Stack 101 (2/6): KoSimCSE로 문장 유사도 구현하기](./02-kosimcse-similarity.md)
- [Korean AI Stack 101 (3/6): BGE-M3 다국어 임베딩 실전](./03-bge-m3-multilingual.md)
- [Korean AI Stack 101 (4/6): CLOVA OCR API로 문서 텍스트 추출](./04-clova-ocr.md)
- **Korean AI Stack 101 (5/6): HyperCLOVA X와 Solar API 사용하기 (현재 글)**
- Korean AI Stack 101 (6/6): 한국어 RAG 파이프라인 조합하기 (예정)

<!-- toc:end -->

## 참고 자료

- [Groq Python library](https://github.com/groq/groq-python)
- [Groq API reference](https://console.groq.com/docs/api-reference)
- [Upstage Solar documentation](https://developers.upstage.ai/docs/getting-started/overview)
- [NAVER Cloud HyperCLOVA X overview](https://www.ncloud.com/product/aiService/clovaStudio)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/korean-ai-stack-101/ko/05-hyperclova-solar-api)

Tags: Korean NLP, LLM, Embeddings, OCR
