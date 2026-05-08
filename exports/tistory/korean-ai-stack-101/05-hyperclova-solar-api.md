
# HyperCLOVA X와 Solar API 사용하기

## 이 글에서 배울 것

- HyperCLOVA X와 Solar API의 호출 방식과 응답 구조를 이해하고 Python으로 호출할 수 있습니다.
- 두 API의 가격 모델, 토큰 제한, 한국어 성능 차이를 비교합니다.
- OpenAI SDK 호환 인터페이스를 제공하는 모델의 장점과 제약을 파악합니다.
- 한국어 LLM API를 RAG 파이프라인의 generation 단계에 연결하는 방법을 설계합니다.

<!-- a-grade-intro:begin -->
## 핵심 질문

HyperCLOVA X와 Solar API를 어떻게 골라야 한국어 워크로드에 맞을까요?

이 글은 그 질문에 답하기 위해 HyperCLOVA·Solar API의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 답할 질문

- 한국어 생성 모델 API를 붙일 때 프롬프트보다 먼저 고정해야 할 호출 계약은 무엇일까요?
- HyperCLOVA X·Solar 같은 한국어 중심 API를 실전에 도입할 때 어떤 점을 먼저 검증해야 할까요?
- 왜 이 글의 실행 예제는 Groq `llama-3.1-8b-instant`를 대체 실습으로 쓰나요?
- 한국어 응답 품질과 검색 기반 문맥 제어는 어떤 식으로 분리해서 봐야 할까요?

> 생성 API를 바꾸는 일은 모델 이름만 바꾸는 일이 아니라, 인증·호출 형식·프롬프트 계약·후처리 규칙을 함께 바꾸는 일입니다.

> 한국어 AI 스택 101 시리즈 (5/6)

예제 코드: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/ko/05-hyperclova-solar-api)

## 왜 중요한가

이 글에서는 한국어 생성 LLM API를 안전하게 호출하는 패턴을 다룹니다. 앞 글들이 임베딩(KoSimCSE, BGE-M3)과 OCR(CLOVA)로 입력 데이터를 정리하는 단계였다면, 이번 글은 그 위에서 답을 만드는 단계입니다. HyperCLOVA X(NAVER)와 Solar(Upstage)는 한국어에 최적화돼 자연스러운 응답을 내놓지만, 운영 단계의 진짜 문제는 인증 방식, 응답 latency, 오류 코드, 토큰 한도, 프롬프트 캐시 같은 호출 계약 쪽에 있습니다.

별도 글로 다루는 이유도 분명합니다. 많은 팀이 모델만 한국어 특화 모델로 바꾸면 품질이 좋아질 거라 기대하지만, 시스템 메시지·temperature·출력 형식·timeout 같은 운영 변수가 그대로면 응답 흔들림은 그대로입니다. 또한 한국어 모델 키가 없는 독자도 실습할 수 있도록 Groq의 `llama-3.1-8b-instant`로 OpenAI 호환 인터페이스를 먼저 익힌 뒤, 마지막에 HyperCLOVA·Solar로 전환하는 두 단계 학습이 가장 현실적입니다.

## Mental Model

생성 API 호출은 4겹 계약으로 분해됩니다.

```
[호출 계약]   인증, endpoint, rate limit, timeout, retry
     |
     v
[메시지 계약] system / user / assistant 역할, 한국어 시스템 메시지
     |
     v
[샘플링 계약] temperature, top_p, max_tokens, stop sequences
     |
     v
[응답 계약]   choices[0].message.content 후처리, JSON validation, 안전 필터
```

핵심은 세 가지입니다.

- **모델 교체는 4겹 모두에 영향**: 모델 이름만 바꾼다고 운영이 끝나지 않습니다. 한 겹이라도 다르면 응답 분포가 달라집니다.
- **OpenAI 호환은 표준이 아님**: Groq, Solar, vLLM 모두 OpenAI 호환 인터페이스를 표방하지만 timeout 처리·rate limit 헤더·오류 코드는 다릅니다.
- **한국어 fluency ≠ 사실성**: HyperCLOVA·Solar의 자연스러운 한국어가 자동으로 정확성을 보장하지 않습니다. 검색(다음 글)이 그 빈자리를 채웁니다.

추가로 알아야 할 것:

- HyperCLOVA X는 NAVER Cloud Platform 인증, Solar는 Upstage API 키 인증입니다. 둘 다 OpenAI SDK로는 직접 호출 안 되며 각자 SDK 또는 REST 호출이 필요합니다.
- Groq은 OpenAI 호환 API에 가까워 학습 목적의 stand-in으로 적합합니다.

## 핵심 개념

| 항목 | 의미 |
| --- | --- |
| HyperCLOVA X | NAVER에서 만든 한국어 중심 LLM. NCP를 통해 API 제공 |
| Solar | Upstage가 공개한 한국어/영어 LLM. Solar Pro/Mini 등 라인업 |
| Groq | LPU 기반 초저latency 추론 서비스. OpenAI 호환 인터페이스 |
| `temperature` | 샘플링 무작위성. 0.0(결정적) ~ 1.0+(창의적) |
| `max_completion_tokens` | 응답 토큰 상한. 한도 초과 시 잘림 |
| System prompt | 모델 페르소나·문체·언어를 고정하는 첫 메시지 |
| Stop sequence | 응답을 자르는 토큰 시퀀스. JSON 강제 시 유용 |
| Output validation | JSON 스키마, 정규식, 길이 검사 등 응답 후처리 |

## Before vs. After

**Before** — system 메시지 없이 영어 프롬프트로 호출하면 한국어 답이 영어 단어를 섞고, temperature를 기본값(보통 1.0)으로 두면 같은 질문에 매번 다른 답이 나옵니다.

**After** — 시스템 메시지를 한국어로 명시하고 temperature를 0.3으로 고정하면 다음과 같이 안정됩니다.

```python
# 같은 질문 3회 호출
'벡터 검색은 의미 유사도 기반, 키워드 검색은 문자 일치 기반입니다...'
'벡터 검색은 임베딩으로 의미를 비교하고, 키워드 검색은 토큰 매칭에 의존합니다...'
'벡터 검색은 의미를 벡터 공간에서 비교하고, 키워드 검색은 단어 단위 매칭입니다...'
```

핵심은 (1) 핵심 단어("의미", "임베딩", "토큰")가 매번 등장한다, (2) 표현은 다르지만 사실 관계가 일관된다, (3) 길이가 비슷하게 유지돼 후처리(요약·번역) 비용이 예측 가능하다는 것입니다.

## 핵심 흐름

![핵심 흐름](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/05/05-01-core-flow.ko.png)

*핵심 흐름*

## 왜 공급자 대체 실습이 유효한가

![공급자 대체 실습의 코드 재사용 구조](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/05/05-01-diagram.ko.png)

*공급자 대체 실습의 코드 재사용 구조*

독자가 항상 HyperCLOVA X나 Solar 키를 가지고 있지는 않습니다. 예제가 실행되지 않으면 프롬프트 설계와 후처리 포인트를 체감하기 어렵습니다. 호출 인터페이스와 운영 감각을 먼저 잡는 데는 Groq 예제로도 충분합니다. 마지막 단계에서 endpoint와 인증 헤더만 교체하면 동일한 system 메시지·샘플링·응답 처리 코드가 재사용됩니다.

## 단계별 실습

### 1단계 — Groq 기본 호출 (한국어 system 메시지)

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

핵심은 system 메시지에 **언어, 역할, 길이 제약**을 한꺼번에 넣는다는 점입니다. user 메시지에 같은 제약을 또 넣을 필요가 없습니다.

### 2단계 — 출력 형식 제약 (JSON 강제)

![최소 실행 예제](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/05/05-02-diagram-2.ko.png)

*최소 실행 예제*

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

`response_format='json_object'`와 system 메시지의 명시적 스키마가 짝입니다. 둘 중 하나라도 빠지면 JSON이 아닌 답이 섞여 옵니다.

### 3단계 — Timeout과 retry

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

지수 백오프와 timeout은 한 쌍입니다. timeout 없이 retry만 두면 hang된 호출을 영원히 기다립니다.

### 4단계 — 응답 검증과 마스킹

```python
import re

def sanitize(text):
    text = re.sub(r'\b\d{2,3}-\d{3,4}-\d{4}\b', '[PHONE]', text)
    text = re.sub(r'\b\d{6}-\d{7}\b', '[RRN]', text)  # 주민번호 패턴
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

응답 검증은 generation 직후, 사용자에게 노출되기 전 한 번 거치는 것이 원칙입니다. 마스킹은 로그·캐시 저장 직전에 한 번 더.

### 5단계 — HyperCLOVA / Solar로 전환 (개념)

```python
# Solar (Upstage) 호출 예시 — OpenAI SDK 호환
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

Solar는 OpenAI SDK의 `base_url`만 바꾸면 Groq 예제 코드 대부분이 그대로 동작합니다. HyperCLOVA X는 NCP 전용 SDK 또는 REST 호출이 필요하지만, 메시지·샘플링·검증 코드는 동일하게 재사용됩니다.

## 이 코드에서 봐야 할 것

![이 코드에서 봐야 할 것](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/05/05-03-diagram-3.ko.png)

*이 코드에서 봐야 할 것*

- 시스템 메시지 한 줄에 **언어·역할·길이**를 모두 박아 두면 user 메시지가 단순해집니다.
- `temperature=0.3`은 설명형 한국어에 잘 맞는 출발점입니다. 창의적 글쓰기는 0.7 이상.
- JSON 강제는 `response_format` + 명시적 스키마 system 메시지 **둘 다** 필요합니다.
- timeout 없는 retry는 위험합니다. 둘은 항상 짝.
- 공급자 교체 시 변하는 것은 endpoint와 인증, 변하지 않는 것은 메시지·검증·마스킹 코드입니다.

## 자주 하는 실수

![실무에서 헷갈리는 지점](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/05/05-04-diagram-4.ko.png)

*실무에서 헷갈리는 지점*

- **System 메시지 없이 호출** — temperature가 낮아도 페르소나가 흔들립니다. 한 줄짜리 system 메시지가 가장 비용 대비 효과가 큽니다.
- **temperature 기본값 사용** — 공급자별로 기본값이 다릅니다(0.7~1.0). 명시적으로 지정해야 환경 간 재현성이 생깁니다.
- **max token 한도 미설정** — 한국어는 영어보다 토큰 수가 많아 비용이 1.3-1.5배 듭니다. 한도를 두지 않으면 청구서가 폭증합니다.
- **OpenAI SDK가 모든 한국어 모델에 통한다는 가정** — Solar는 OK, HyperCLOVA X는 별도 SDK. 사전에 검증.
- **응답을 그대로 사용자에게 노출** — refusal 응답("죄송합니다, 제가 답할 수 없습니다")이나 PII 누출 가능성이 있습니다. 검증과 마스킹을 거칩니다.
- **한국어 fluency를 사실성으로 착각** — 자연스럽게 답한다고 정확하지는 않습니다. 사실성은 다음 글의 RAG로 보강합니다.

## 실무 적용

- **이중 공급자 운영**: 평상시는 Solar, 장애 시 HyperCLOVA X로 fallback. 메시지 코드는 공유, endpoint만 교체.
- **프롬프트 캐시**: 시스템 메시지가 길고 자주 반복된다면 OpenAI 호환 캐시를 사용해 latency·비용을 30% 이상 절감 가능합니다.
- **Streaming**: 200토큰 이상 응답은 streaming으로 받아 사용자 체감 latency를 절반으로 줄입니다. `stream=True`.
- **로그 마스킹**: production 로그에는 raw prompt를 그대로 남기지 않습니다. `sanitize()`를 통과한 버전만 저장.
- **온도/길이 A/B**: temperature 0.3 vs 0.5, max_tokens 200 vs 400을 user satisfaction 지표로 비교. 한국어는 길이 변동이 영어보다 큽니다.
- **모니터링 지표**: TTFT(Time To First Token), end-to-end latency, refusal rate, JSON parsing 실패율, 평균 입력/출력 토큰 — 이 5개가 LLM 운영의 기본 대시보드입니다.

## 실무에서는 이렇게 생각한다

API 선택에서 가장 중요한 것은 한국어 성능이 아니라 안정성과 운영 편의성입니다. HyperCLOVA X가 한국어에서 더 자연스러운 응답을 낼 수 있지만, SLA, 업타임, SDK 성숙도, 에러 처리 문서화 수준도 함께 비교해야 합니다.

vendor lock-in을 줄이려면 OpenAI SDK 호환 인터페이스를 제공하는 모델을 우선하는 것이 실용적입니다. Solar는 OpenAI SDK로 바로 호출할 수 있어 기존 코드를 거의 바꾸지 않고 교체할 수 있습니다. 프로덕션에서는 여러 모델을 fallback chain으로 엶는 패턴이 흔합니다. 메인 모델이 응답하지 않으면 대체 모델로 자동 전환하는 구조를 미리 마련해두는 것이 좋습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **한국어 성능과 글로벌 모델을 비교** — 범용 GPT 대비 가치 제안을 측정합니다.
- **API 안정성·SLA를 평가** — 신생 API는 운영 변수가 많습니다.
- **비용 모델을 use case에 맞춘다** — 토큰 단가·기본 요금이 다릅니다.
- **data residency가 결정적** — 국내 처리 요구가 있으면 선택지가 좁아집니다.
- **multi-vendor 전략을 의식** — 단일 의존은 운영 위험입니다.

## 체크리스트

- [ ] 시스템 메시지에 대상 독자·문체·언어를 명시한다.
- [ ] temperature와 max token 값을 고정하고 비교한다.
- [ ] 출력 형식을 bullet, JSON, 요약문 중 하나로 제한한다.
- [ ] timeout과 retry를 짝으로 둔다.
- [ ] 응답 검증과 마스킹을 generation 직후 한 번 거친다.
- [ ] 공급자를 바꿀 때 인증·오류 처리·latency 차이를 점검한다.

## 연습 문제

1. 같은 system 메시지로 temperature 0.0, 0.3, 0.7 세 가지 호출을 5회씩 반복하고, 응답 길이와 핵심 단어 등장 빈도를 비교해 보세요.
2. JSON 강제 호출에서 일부러 system 메시지의 스키마를 빼고 호출해 보세요. `response_format`만으로 얼마나 안정적인지 관찰하세요.
3. Solar(또는 HyperCLOVA) 키가 있다면 같은 메시지를 보내고 latency·refusal rate·길이를 Groq 결과와 비교해 표로 정리하세요.

## 정리 · 다음 글

이 글의 핵심은 한국어 생성 API의 호출 계약을 4겹(호출·메시지·샘플링·응답)으로 나눠 운영하는 감각입니다. 어떤 모델을 쓰든 system 메시지·temperature·출력 형식·timeout 네 가지만 고정해 두면, 공급자 교체와 모델 업그레이드가 코드 한두 줄 수정으로 끝납니다. 한국어 fluency는 무료로 얻지만 사실성은 다음 글에서 검색으로 보강합니다.

다음 글(6편, 마지막)에서는 한국어 RAG 파이프라인을 조합합니다. 이전 글들의 BGE-M3 검색 + CLOVA OCR + 이번 글의 LLM 호출을 하나의 흐름으로 묶어, 사실 기반 한국어 응답을 만들어 내는 minimum viable RAG를 코드로 구축합니다.

## 시리즈 목차

- [한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [KoSimCSE로 문장 유사도 구현하기](./02-kosimcse-similarity.md)
- [BGE-M3 다국어 임베딩 실전](./03-bge-m3-multilingual.md)
- [CLOVA OCR API로 문서 텍스트 추출](./04-clova-ocr.md)
- **HyperCLOVA X와 Solar API 사용하기 (현재 글)**
- 한국어 RAG 파이프라인 조합하기 (예정)

---

## 참고 자료

- [Groq Python library](https://github.com/groq/groq-python)
- [Groq API reference](https://console.groq.com/docs/api-reference)
- [Upstage Solar documentation](https://developers.upstage.ai/docs/getting-started/overview)
- [NAVER Cloud HyperCLOVA X overview](https://www.ncloud.com/product/aiService/clovaStudio)

Tags: Korean NLP, LLM, Embeddings, OCR

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
