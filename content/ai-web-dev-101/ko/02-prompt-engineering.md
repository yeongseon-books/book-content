---
title: "AI Web Development 101 (2/7): 프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술"
series: ai-web-dev-101
episode: 2
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI
- LLM
- 웹 개발
- Python
- Tutorial
last_reviewed: '2026-05-14'
seo_description: 같은 모델로도 결과가 달라지는 이유를 역할, 맥락, 출력 계약, 검증 루틴 관점에서 정리합니다.
---

# AI Web Development 101 (2/7): 프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술

같은 모델을 써도 누구는 실무에 바로 쓰는 결과를 얻고, 누구는 몇 번 묻다가 창을 닫습니다. 차이는 대개 모델 자체보다 요청을 어떻게 구조화했는지에서 갈립니다. AI는 마음을 읽지 않으므로, 맥락과 출력 계약을 개발자가 먼저 정리해 줘야 합니다.

이 글은 AI 웹 개발 입문 시리즈의 2번째 글입니다.

여기서는 AI에게 원하는 답을 더 안정적으로 얻기 위한 프롬프트 설계 원칙과 검증 루틴을 실무 감각으로 정리합니다.

## 먼저 던지는 질문

- 프롬프트는 단순한 질문과 무엇이 다를까요?
- `system`과 `user` 역할은 각각 어떤 책임을 가질까요?
- 좋은 프롬프트는 어떤 정보를 빠뜨리지 않을까요?

## 큰 그림

![AI Web Development 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/02/prompt-role-layering.ko.png)

*AI Web Development 101 2장 흐름 개요*

이 그림에서는 프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 프롬프트를 따로 배워야 할까

지난 글에서는 API를 호출하는 법을 살펴봤습니다. 이제부터는 “어떻게 호출할 것인가”가 중요해집니다. 같은 모델이라도 요청이 모호하면 평균적인 답을 내놓고, 요청이 구체적이면 훨씬 목적에 맞는 답을 돌려줍니다.

프롬프트를 어렵게 생각할 필요는 없습니다. 새 팀원에게 업무를 맡긴다고 생각하면 됩니다. “보고서 좀 써줘”라고만 말하면 주제, 분량, 독자, 형식이 비어 있습니다. AI도 마찬가지입니다. 배경 지식과 기대 결과를 주지 않으면 가장 무난한 쪽으로 대답할 뿐입니다.

실무에서 중요한 차이는 여기서 생깁니다. 초안 생성은 대충 해도 되지만, 서비스 코드 안에서 재사용할 프롬프트는 실패할 때 원인을 좁힐 수 있어야 합니다. 즉, 프롬프트 엔지니어링은 글쓰기 감각만이 아니라 디버깅 감각과 검증 습관까지 포함합니다.

## `system`과 `user`를 나눠서 생각하기

OpenAI Chat Completions API에서는 `role` 필드로 메시지 성격을 구분합니다. 입문 단계에서 가장 중요한 것은 `system`과 `user` 두 가지입니다.

- `system`: 모델의 기본 역할, 태도, 전문성, 금지 사항
- `user`: 지금 수행해야 할 구체적인 작업과 입력값

예를 들어 `system`에는 “너는 보안과 성능을 중시하는 시니어 개발자다” 같은 기본 규칙을 두고, `user`에는 “이 함수를 리뷰해 달라”는 현재 작업을 넣습니다. 이렇게 나누면 모델의 장기 규칙과 개별 요청을 분리해서 관리할 수 있습니다.

## 나쁜 프롬프트와 개선된 프롬프트를 비교해 보기

모호함은 결과를 흔들게 만듭니다. 가장 빠른 학습법은 같은 작업을 두 가지 프롬프트로 돌려 보는 것입니다.

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def run_prompt(system_prompt: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content

bad = run_prompt(
    system_prompt="너는 친절한 도우미다.",
    user_prompt="상품 소개 문구를 써줘.",
)

better = run_prompt(
    system_prompt=(
        "너는 이커머스 카피라이터다. 과장 대신 실제 구매 맥락을 짧고 분명하게 설명한다."
    ),
    user_prompt=(
        "상품명: 무소음 기계식 키보드\n"
        "대상 독자: 재택근무 개발자\n"
        "강조점: 밤샘 작업, 부드러운 타건감, 파스텔 블루 컬러\n"
        "출력 형식: 불릿 3개, 각 1문장"
    ),
)

print("[bad]\n", bad)
print("\n[better]\n", better)
```

**Expected output:**

```text
[bad]
감성적이고 일반적인 광고 문구

[better]
- 밤늦게까지 일해도 키 소음 부담이 적습니다.
- 손끝 피로를 덜어 주는 부드러운 타건감이 긴 작업 시간에 잘 맞습니다.
- 파스텔 블루 컬러가 작업 공간 분위기를 과하지 않게 정리해 줍니다.
```

정확히 이 문장이 나오지는 않더라도, 개선된 프롬프트가 더 짧고 구조화된 결과를 내야 합니다. 여기서 핵심은 문학적 표현이 아니라 **입력 필드와 출력 계약을 명시했다**는 점입니다.

![모호한 프롬프트를 구체적으로 개선하는 과정](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/02/prompt-improvement-example.ko.png)

*모호한 프롬프트를 구체적으로 개선하는 과정*

## 좋은 프롬프트의 네 가지 기본 원칙

입문 단계에서는 아래 네 가지를 먼저 지키는 것만으로도 결과가 꽤 안정됩니다.

### 1. 역할을 분명히 둡니다

“도와줘”보다 “B2B SaaS 제품을 다루는 기술 문서 에디터다”가 더 낫습니다. 역할은 답변의 기본 관점을 결정합니다.

### 2. 맥락을 빠뜨리지 않습니다

독자, 도메인, 입력 데이터, 금지 사항이 빠지면 모델은 일반론으로 흘러갑니다. 서비스 안에서 재사용할 프롬프트일수록 이 맥락을 더 노출해야 합니다.

### 3. 출력 형식을 계약으로 만듭니다

“JSON으로 달라”, “불릿 3개로 정리해 달라”, “표 대신 문단으로 설명해 달라” 같은 제약은 후속 처리 비용을 크게 줄여 줍니다.

### 4. 제약 조건과 실패 기준을 함께 둡니다

“문서 근거가 없으면 모른다고 답하라”, “3문장을 넘기지 마라”, “개인정보를 추측하지 마라” 같은 조건은 실서비스에서 특히 중요합니다.

![좋은 결과를 이끄는 프롬프트 설계 원칙](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/02/four-prompt-principles.ko.png)

*좋은 결과를 이끄는 프롬프트 설계 원칙*

## 출력 형식을 진짜 계약으로 만드는 법

서비스 코드가 결과를 다시 읽어야 한다면, 자연어만 받기보다 구조화된 출력을 요구하는 편이 안전합니다. 입문 단계에서는 JSON 예제 하나만 제대로 잡아도 효과가 큽니다.

```python
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

response = client.chat.completions.create(
    model="gpt-4o-mini",
    temperature=0,
    messages=[
        {
            "role": "system",
            "content": (
                "너는 고객 지원 FAQ 생성기다."
                "반드시 JSON 객체 하나만 출력하고, 키는 title, summary, risk이다."
            ),
        },
        {
            "role": "user",
            "content": "비밀번호 재설정 정책을 2문장 이내 FAQ로 만들어줘.",
        },
    ],
)

payload = json.loads(response.choices[0].message.content)
print(payload)
```

**Expected output:**

```json
{
  "title": "비밀번호 재설정",
  "summary": "이메일 인증 후 새 비밀번호를 설정할 수 있습니다.",
  "risk": "본인 확인 없이 비밀번호를 바꾸게 두면 계정 탈취 위험이 있습니다."
}
```

이 방식이 중요한 이유는, 모델이 잘 썼는지 감으로 읽지 않고 코드가 직접 검증할 수 있기 때문입니다. 이후 평가 단계에서도 구조화된 출력은 훨씬 다루기 쉽습니다.

## `temperature`와 `max_tokens`는 언제 조절할까

프롬프트 문장만큼 중요한 것이 생성 파라미터입니다. 특히 `temperature`와 `max_tokens`는 결과의 성격을 크게 바꿉니다.

- `temperature`: 0에 가까울수록 더 일관되고 보수적인 답을 냅니다.
- `max_tokens`: 출력 길이의 상한입니다. 너무 짧게 잡으면 답이 중간에 끊길 수 있습니다.

작업별 감각은 대략 이렇습니다.

- 코드 생성, 분류, 추출: `temperature=0.0 ~ 0.3`
- 요약, 문서 초안: `temperature=0.2 ~ 0.5`
- 카피 초안, 브레인스토밍: `temperature=0.7` 이상도 가능

같은 질문을 두 온도로 비교하면 차이가 바로 드러납니다.

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
prompt = "재택근무 개발자를 위한 TODO 앱 소개 문구를 한 문장으로 써줘."

for temp in (0.1, 0.9):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=temp,
        max_tokens=80,
        messages=[{"role": "user", "content": prompt}],
    )
    print(f"temperature={temp}: {response.choices[0].message.content}")
```

![생성 다양성과 답변 길이를 조절하는 두 설정](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/02/temperature-max-tokens.ko.png)

*생성 다양성과 답변 길이를 조절하는 두 설정*

## 실패할 때는 프롬프트를 어떻게 디버깅할까

원하는 답이 나오지 않을 때는 모델을 탓하기 전에 입력을 먼저 점검하는 편이 좋습니다. 아래 순서는 실무에서도 그대로 통합니다.

1. **역할이 비어 있는가** — 누구처럼 답해야 하는지 모호하지 않은가
2. **맥락이 부족한가** — 도메인, 독자, 금지 사항이 빠지지 않았는가
3. **출력 형식이 약한가** — 불릿, JSON, 길이 제한이 없는가
4. **예시가 필요한가** — 기대 형식을 말로 설명하기보다 보여 주는 편이 낫지 않은가
5. **파라미터가 문제인가** — 프롬프트보다 `temperature`, `max_tokens`가 결과를 흔드는가

아래처럼 동일 작업에 대해 실패 사례를 묶어서 돌리면 어느 축이 흔들리는지 훨씬 빨리 보입니다.

```python
test_cases = [
    {
        "name": "길이 제한 확인",
        "user": "신규 가입 혜택을 2문장 이내로 설명해줘.",
    },
    {
        "name": "형식 확인",
        "user": "환불 정책을 불릿 3개로 정리해줘.",
    },
]

system_prompt = "너는 고객 지원 문서를 짧고 정확하게 요약하는 도우미다."

for case in test_cases:
    answer = run_prompt(system_prompt, case["user"])
    print(f"\n[{case['name']}]\n{answer}")
```

이런 테스트는 화려하지 않지만, 프롬프트를 “감”이 아니라 반복 가능한 입력으로 다루게 만들어 줍니다.

## 실서비스에서 자주 생기는 프롬프트 실패 모드

프롬프트는 잘 썼다고 생각했는데 실제 서비스에서는 다른 이유로 무너질 수 있습니다.

- **입력 데이터가 길어짐**: 대화 기록이 길어지면서 핵심 지시가 뒤로 밀릴 수 있습니다.
- **금지 조건이 약함**: “하지 마”만 있고 “대신 이렇게 해”가 없으면 결과가 흔들릴 수 있습니다.
- **출력 형식이 느슨함**: JSON을 요구하지 않아 후처리 코드가 깨질 수 있습니다.
- **도메인 용어가 부족함**: 모델이 일반적인 의미로 해석해 엉뚱한 답을 할 수 있습니다.

프롬프트는 한 번 완성해서 끝나는 문서가 아니라, 실패 패턴을 반영해 계속 정리되는 실행 계약입니다.

![프롬프트 개선 반복 과정](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/02/prompt-iteration-loop.ko.png)

*프롬프트 개선 반복 과정*

## 체크리스트

- [ ] `system`과 `user` 역할 차이를 설명할 수 있다.
- [ ] 출력 형식과 제약 조건을 프롬프트에 명시했다.
- [ ] 같은 작업을 두 프롬프트로 비교해 본 적이 있다.
- [ ] 작업 성격에 맞게 `temperature`와 `max_tokens`를 조절할 수 있다.
- [ ] 실패 사례를 반복 실행하며 프롬프트를 디버깅할 기준이 있다.

## 정리

프롬프트 엔지니어링은 AI에게 예쁘게 말하는 기술이 아니라, 모델이 따라야 할 작업 계약을 설계하고 검증하는 기술입니다.

- `system`은 장기 규칙, `user`는 현재 작업 지시라는 구분을 먼저 잡습니다.
- 좋은 프롬프트는 역할, 맥락, 출력 형식, 제약 조건을 빠뜨리지 않습니다.
- `temperature`와 `max_tokens`는 프롬프트의 일부처럼 함께 다뤄야 합니다.
- 실패할수록 프롬프트를 디버깅 대상과 테스트 입력으로 다루는 습관이 중요합니다.

다음 글에서는 이 원칙을 브라우저 UI와 연결해, 사용자가 실제로 대화할 수 있는 챗봇 형태로 구현해 보겠습니다.

## 처음 질문으로 돌아가기

- **프롬프트는 단순한 질문과 무엇이 다를까요?**
  - 본문의 기준은 프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`system`과 `user` 역할은 각각 어떤 책임을 가질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **좋은 프롬프트는 어떤 정보를 빠뜨리지 않을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Web Development 101 (1/7): AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기](./01-hello-ai-api.md)
- **프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술 (현재 글)**
- AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현 (예정)
- RAG 입문 — 내 데이터로 답하는 AI 만들기 (예정)
- AI 에이전트 첫걸음 — Tool Use로 똑똑한 AI 만들기 (예정)
- AI 웹 앱 배포하기: Vercel과 Azure에 올리고 운영하기 (예정)
- AI 앱의 평가와 개선, 품질을 측정하고 더 좋게 만드는 법 (예정)

<!-- toc:end -->

## 참고 자료

- [OpenAI Prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [OpenAI Prompt caching and prompt design guide](https://platform.openai.com/docs/guides/text)
- [Anthropic prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [OpenAI Cookbook prompt examples](https://cookbook.openai.com/)

Tags: AI, LLM, 웹 개발, Python, Tutorial
