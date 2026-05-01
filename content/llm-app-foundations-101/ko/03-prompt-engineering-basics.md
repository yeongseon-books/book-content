---
title: 프롬프트 엔지니어링 기초 — System·User·Assistant 역할
series: llm-app-foundations-101
episode: 3
language: ko
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- OpenAI
- Prompt Engineering
- Python
last_reviewed: '2026-04-30'
---

# 프롬프트 엔지니어링 기초 — System·User·Assistant 역할

> LLM 앱 기초 시리즈 (3/6)

예제 코드: [github.com/yeongseon-books/llm-app-foundations-101](https://github.com/yeongseon-books/llm-app-foundations-101/tree/main/ko/03-prompt-engineering-basics)

프롬프트 엔지니어링을 처음 접하면 문장을 그럴듯하게 쓰는 기술처럼 보이기 쉽습니다. 실전에서는 조금 다릅니다. 핵심은 말을 예쁘게 다듬는 재주보다 **입력 구조를 분리하고, 모델이 따라야 할 우선순위를 설계하는 일**입니다. 같은 질문이라도 `system`에 무엇을 두는지, `user`에 어떤 맥락을 담는지, 이전 `assistant` 답변을 어떻게 이력으로 넘기는지에 따라 결과가 크게 달라집니다.

이 차이는 데모 단계에서는 가볍게 지나가지만, 애플리케이션으로 가면 바로 운영 문제로 바뀝니다. 톤이 흔들리고, 답변 형식이 들쭉날쭉해지고, 이전 대화를 잊어버리고, 길이 제어가 안 됩니다. 많은 입문자가 모델 품질 문제라고 느끼는 현상 가운데 상당수는 사실 프롬프트 구조 문제입니다.

이번 글에서는 Groq의 `llama-3.1-8b-instant`를 기준으로 채팅 프롬프트의 기본 뼈대를 잡겠습니다. 범위는 일곱 가지입니다.

- `system`, `user`, `assistant` 세 역할의 의미
- system 메시지가 전체 동작을 어떻게 바꾸는지
- assistant 메시지로 멀티턴 이력을 어떻게 구성하는지
- `temperature`, `top_p`가 창의성과 일관성에 어떤 영향을 주는지
- 효과적인 프롬프트 구조 패턴
- few-shot 예시를 `messages` 배열에 넣는 기본 방법
- 프롬프트 설계에서 자주 나오는 실수

포인트는 하나입니다. **좋은 프롬프트는 한 문장이 아니라 역할이 분리된 메시지 배열에서 시작합니다.**

---

## 왜 프롬프트를 문장 하나로만 보면 안 되는가

Post 01에서는 `messages=[{"role": "user", ...}]` 형태로 첫 호출을 만들었습니다. 그 단계에서는 충분합니다. 하지만 실제 앱은 대개 한 문장짜리 질문기로 끝나지 않습니다. 서비스는 특정 말투를 유지해야 하고, 답변 형식도 일정해야 하며, 이전 대화도 이어져야 합니다. 이 요구가 생기는 순간 `user` 메시지 하나만으로는 표현력이 부족해집니다.

채팅 기반 LLM API는 그래서 입력을 역할별 메시지 배열로 받습니다. 이 구조는 단순한 문법 장식이 아닙니다. 개발자가 모델에게 주는 지시를 계층으로 나누기 위한 장치입니다.

- `system`: 전체 행동 원칙과 경계
- `user`: 이번 턴의 실제 요청
- `assistant`: 이전 턴에서 모델이 이미 말한 내용

이 셋을 구분하면 프롬프트가 훨씬 운영 가능해집니다. 시스템 정책은 모든 요청에 공통으로 붙이고, 사용자의 질문은 매 턴 교체하고, 대화 이력은 필요한 범위만 누적하면 되기 때문입니다.

---

## system, user, assistant 역할 이해하기

세 역할을 짧게 정의하면 아래와 같습니다.

### `system`

`system`은 모델의 기본 동작을 잡는 상위 지시입니다. 답변 언어, 톤, 안전 경계, 포맷 원칙, 역할 정체성 같은 내용을 여기에 둡니다. 예를 들어 “당신은 Python 튜터다”, “항상 JSON으로 답하라”, “모르면 추측하지 말고 부족한 정보를 먼저 말하라” 같은 규칙이 들어갑니다.

중요한 점은 `system`이 “이번 질문의 내용”이 아니라 **모든 질문 위에 깔리는 운영 정책**이라는 사실입니다. 앱 차원에서 재사용되는 지시라면 대개 `system` 후보입니다.

### `user`

`user`는 현재 사용자의 요청입니다. 질문, 작업 지시, 추가 맥락, 제약 조건이 들어갑니다. 같은 앱이라도 사용자마다 내용이 달라지므로 매 요청마다 바뀌는 영역입니다.

예를 들어 “FastAPI와 Flask 차이를 표로 요약해 달라”, “답변은 초급자 눈높이로 설명해 달라”, “아래 로그를 보고 원인을 추정해 달라” 같은 입력은 `user`에 놓습니다.

### `assistant`

`assistant`는 모델이 이전 턴에서 했던 답변을 다시 입력으로 넘길 때 사용합니다. 많은 입문자가 “모델이 방금 한 답변을 왜 다시 보내야 하느냐”고 묻습니다. 이유는 간단합니다. API는 서버 쪽에 자동으로 대화 메모리를 오래 들고 있지 않는 경우가 많기 때문입니다. 매 턴마다 애플리케이션이 필요한 이력을 다시 보내야 같은 맥락이 이어집니다.

즉, 멀티턴 대화는 특별한 숨은 상태가 아니라 **`messages` 배열을 매번 다시 구성하는 애플리케이션 로직**입니다.

---

## system 메시지가 결과를 어떻게 바꾸는가

system 메시지의 영향은 추상적으로 설명하는 것보다 직접 비교해 보는 편이 빠릅니다. 아래 코드는 같은 사용자 질문을 두 번 보냅니다. 한 번은 system 없이, 한 번은 답변 스타일과 형식을 강하게 제한하는 system과 함께 보냅니다. 이 코드 블록은 독립 실행 가능합니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

question = "Python의 딕셔너리와 리스트 차이를 설명해 주세요."

without_system = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": question},
    ],
    temperature=0.2,
)

with_system = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": (
                "당신은 Python 입문자를 돕는 기술 튜터입니다. "
                "항상 한국어로 답하고, 먼저 한 문단 요약을 쓴 뒤 "
                "마지막에 bullet 3개로 핵심 차이를 정리하세요. "
                "추측하지 말고 초급자 눈높이를 유지하세요."
            ),
        },
        {"role": "user", "content": question},
    ],
    temperature=0.2,
)

print("[without system]")
print(without_system.choices[0].message.content)
print()
print("[with system]")
print(with_system.choices[0].message.content)
```

실행해 보면 두 응답이 같은 사실을 설명하더라도 구조와 톤이 달라지는 경우가 많습니다. system이 없으면 모델은 일반적인 설명을 자유롭게 구성합니다. system이 있으면 아래 요소가 더 안정적으로 고정됩니다.

- 답변 언어
- 말투와 난이도
- 형식 순서
- 길이와 요약 방식
- 모를 때의 행동 원칙

여기서 중요한 운영 감각이 하나 있습니다. **system은 모델을 완전히 기계처럼 고정하는 스위치가 아니라, 일관성을 높이는 가장 강한 손잡이**입니다. 따라서 스타일이 흔들리는 앱이라면 user 문장을 계속 다듬기 전에 system 설계를 먼저 점검하는 편이 낫습니다.

---

## assistant 메시지로 멀티턴 이력 만들기

멀티턴 대화에서 자주 생기는 오해는 “API가 지난 대화를 기억할 것”이라는 기대입니다. 실제로는 애플리케이션이 기억을 전달해야 합니다. 현재 질문만 보내면 모델도 현재 질문만 봅니다. 이전 턴의 맥락이 필요하면 그 내용을 다시 `messages`에 넣어야 합니다.

아래 예제를 보겠습니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": "당신은 Python 학습 도우미입니다. 짧고 정확하게 설명하세요.",
    },
    {
        "role": "user",
        "content": "파이썬 리스트와 튜플 차이를 한 문단으로 설명해 주세요.",
    },
]

first = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.2,
)

assistant_text = first.choices[0].message.content
print("[assistant turn 1]")
print(assistant_text)
print()

messages.append({"role": "assistant", "content": assistant_text})
messages.append(
    {
        "role": "user",
        "content": "방금 설명에 5줄 이하 예제 코드를 덧붙여 주세요.",
    }
)

second = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.2,
)

print("[assistant turn 2]")
print(second.choices[0].message.content)
```

핵심은 `assistant_text`를 다시 배열에 넣는 부분입니다. 이렇게 해야 두 번째 요청이 “방금 설명”이 무엇이었는지 압니다. 이 패턴이 곧 챗봇의 기본 메모리입니다.

물론 이력을 무한정 쌓을 수는 없습니다. Post 02에서 본 것처럼 모든 이전 턴은 토큰 비용이 됩니다. 그래서 실전에서는 다음 셋 중 하나를 선택합니다.

- 최근 몇 턴만 유지하기
- 오래된 턴을 요약해 짧게 보존하기
- 중요한 사실만 별도 상태 저장소에 구조화해 두기

Post 05에서 대화 상태 관리를 더 깊게 다룰 예정이지만, 지금 단계에서는 “멀티턴은 assistant 메시지를 포함한 배열 재구성”이라고 이해하면 충분합니다.

---

## temperature와 top_p: 창의성 vs 일관성

프롬프트를 아무리 잘 써도 샘플링 파라미터를 무시하면 결과가 흔들릴 수 있습니다. 입문 단계에서 먼저 알아둘 값은 `temperature`와 `top_p`입니다.

### `temperature`

`temperature`는 다음 토큰을 얼마나 넓게 고를지에 영향을 줍니다. 보통 낮을수록 보수적이고, 높을수록 다양한 표현이 나옵니다.

- `0.0`에 가까울수록 더 일관된 답변
- `0.7` 이상으로 갈수록 표현 다양성 증가
- 분류, 추출, 요약처럼 형식 안정성이 중요한 작업은 낮게
- 카피 초안, 아이디어 브레인스토밍은 상대적으로 높게

아래 코드는 같은 질문을 `temperature=0.0`과 `0.9`로 비교합니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

prompt = "FastAPI를 처음 배우는 개발자에게 3문장으로 소개해 주세요."

for temperature in (0.0, 0.9):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "당신은 한국어 기술 블로그 편집자입니다. 간결하게 답하세요.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )

    print(f"[temperature={temperature}]")
    print(completion.choices[0].message.content)
    print()
```

### `top_p`

`top_p`는 확률이 높은 후보 집합을 얼마나 넓게 열어둘지 정합니다. 개념적으로는 “상위 누적 확률 질량 안에서만 뽑기”에 가깝습니다. 낮추면 더 보수적이고, 높이면 더 다양한 후보를 허용합니다.

입문 단계에서는 보통 두 원칙이면 충분합니다.

- 먼저 `temperature` 하나만 조절해 봅니다.
- 특별한 이유가 없다면 `temperature`와 `top_p`를 동시에 크게 흔들지 않습니다.

둘 다 다양성에 영향을 주기 때문에, 초반부터 함께 크게 바꾸면 왜 결과가 달라졌는지 설명하기 어려워집니다. 운영 기준을 세울 때는 한 번에 한 손잡이씩 움직이는 편이 좋습니다.

---

## 효과적인 프롬프트 구조 패턴

입문자에게 가장 재현성이 높은 패턴은 **지시 + 컨텍스트 + 출력 형식**입니다. 한 문장으로 퉁치지 말고 세 덩어리로 나누면 읽기도 쉽고 유지보수도 쉬워집니다.

예를 들어 아래처럼 구성할 수 있습니다.

```text
지시: 무엇을 해라
컨텍스트: 어떤 독자/상황/입력인가
출력 형식: 어떤 구조로 답하라
```

이 패턴을 messages로 옮기면 더 명확해집니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": (
                "당신은 백엔드 입문자를 돕는 Python 튜터입니다. "
                "설명은 한국어로 하고, 추측하지 마세요."
            ),
        },
        {
            "role": "user",
            "content": (
                "지시: dataclass가 무엇인지 설명해 주세요.\n"
                "컨텍스트: 독자는 Python 문법은 알지만 dataclass는 처음입니다.\n"
                "출력 형식: 1) 두 문장 설명 2) 6줄 이하 코드 예제 3) 언제 쓰면 좋은지 한 줄"
            ),
        },
    ],
    temperature=0.2,
)

print(completion.choices[0].message.content)
```

이 구조가 좋은 이유는 세 가지입니다. 지시가 분명해지고, 배경 정보가 묻히지 않으며, 출력 검증 기준이 생깁니다. 나중에 응답 품질이 흔들릴 때도 “지시가 약한가”, “컨텍스트가 부족한가”, “형식 조건이 모호한가”를 분리해서 볼 수 있습니다.

---

## few-shot 예시를 messages 배열에 넣는 기본 방법

few-shot은 모델에게 원하는 패턴의 예시를 먼저 보여주고 같은 스타일로 답하게 유도하는 방식입니다. Post 04에서 더 깊게 다루겠지만, 입문 단계에서는 **예시도 결국 messages 배열 안에 넣는다**는 점만 확실히 잡으면 됩니다.

가장 단순한 형태는 사용자 질문과 모범 assistant 답변을 한 쌍 이상 앞에 두는 것입니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": "당신은 Python 개념을 한 줄 정의와 한 줄 비유로 설명하는 튜터입니다.",
    },
    {"role": "user", "content": "클래스가 무엇인가요?"},
    {
        "role": "assistant",
        "content": "정의: 클래스는 객체를 만들기 위한 설계도입니다.\n비유: 같은 모양의 붕어빵을 찍어내는 틀과 비슷합니다.",
    },
    {"role": "user", "content": "상속이 무엇인가요?"},
    {
        "role": "assistant",
        "content": "정의: 상속은 기존 클래스의 속성과 동작을 이어받아 새 클래스를 만드는 방식입니다.\n비유: 기본 템플릿을 복사해 필요한 부분만 덧붙이는 것과 비슷합니다.",
    },
    {"role": "user", "content": "데코레이터가 무엇인가요?"},
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.2,
)

print(completion.choices[0].message.content)
```

이 방식은 강력하지만 공짜는 아닙니다. 예시가 늘수록 토큰도 늘어납니다. 따라서 무작정 많이 넣기보다, 원하는 패턴을 가장 잘 보여주는 짧고 대표적인 예시를 고르는 편이 낫습니다.

---

## 프롬프트 설계에서 흔한 실수

입문 단계에서 가장 자주 보이는 실수는 아래 일곱 가지입니다.

### 1. system에 둘 정책을 user에만 우겨 넣는 실수

매 요청마다 “항상 한국어로 답해라”, “초급자 눈높이로 설명해라”, “JSON으로만 답해라”를 user 메시지에 반복해서 넣으면 관리가 어렵습니다. 앱 공통 정책은 system으로 올리는 편이 낫습니다.

### 2. 지시와 데이터가 섞여 모호해지는 실수

질문, 배경 설명, 원문 데이터, 원하는 출력 형식이 한 문단에 뒤섞이면 모델도 우선순위를 해석해야 합니다. 구조를 나누면 품질보다 먼저 재현성이 좋아집니다.

### 3. 멀티턴 이력을 안 보내고 기억하길 기대하는 실수

API 호출이 상태를 자동 보존한다고 가정하면 후속 질문 품질이 급격히 흔들립니다. 필요한 assistant/user 이력을 다시 넣어야 합니다.

### 4. `temperature`를 높여 놓고 형식 일관성을 기대하는 실수

창의성이 필요한 작업과 형식 고정 작업을 같은 파라미터로 다루면 결과가 불안정해집니다. 추출, 분류, 요약은 보통 낮은 temperature에서 시작하는 편이 안전합니다.

### 5. few-shot 예시를 길게 넣어 토큰을 낭비하는 실수

예시는 짧고 선명해야 합니다. 장황한 예시 여러 개보다 패턴이 분명한 짧은 예시 두 개가 더 낫습니다.

### 6. “좋게”, “자세히”, “적당히” 같은 모호한 표현을 쓰는 실수

모호한 형용사는 검증 기준이 되지 못합니다. 문단 수, bullet 수, 코드 길이, JSON 키처럼 측정 가능한 요구가 더 낫습니다.

### 7. 한 번 잘 나온 결과를 일반화하는 실수

프롬프트 평가는 샘플 하나로 끝내면 안 됩니다. 질문 종류를 바꿔 여러 번 돌려 보고, 파라미터까지 함께 기록해야 운영 기준이 생깁니다.

---

## 마무리

프롬프트 엔지니어링의 출발점은 멋진 문장을 짓는 능력이 아닙니다. system으로 정책을 분리하고, user로 현재 요청을 표현하고, assistant로 필요한 이력을 다시 연결하는 구조 감각입니다. 여기에 `temperature`와 `top_p`를 조심스럽게 조절하면, 같은 모델이라도 훨씬 예측 가능한 애플리케이션을 만들 수 있습니다.

다음 글에서는 few-shot과 chain-of-thought를 조금 더 체계적으로 다룹니다. 이번 글에서 본 역할 분리 위에 예시 설계까지 얹으면, “질문을 던진다” 수준을 넘어 “원하는 답변 패턴을 유도한다”는 감각이 생기기 시작합니다.

<!-- blog-only:start -->
다음 글: [Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기](./04-few-shot-and-cot.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기](./01-llm-api-first-call.md)
- [토큰 이해하기 — 비용, 한계, 컨텍스트 창](./02-understanding-tokens.md)
- **프롬프트 엔지니어링 기초 — System·User·Assistant 역할 (현재 글)**
- Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기 (예정)
- 대화 상태 관리 — 멀티턴 챗봇 만들기 (예정)
- 스트리밍 응답 처리 — 실시간으로 출력 받기 (예정)

<!-- toc:end -->

---

## 참고 자료

- Groq Docs, "Text chat"
- Groq Python Library: <https://github.com/groq/groq-python>
- OpenAI Platform Docs, "Messages and roles": <https://platform.openai.com/docs/guides/text>
- Anthropic Docs, "Prompt engineering overview": <https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview>

Tags: LLM, OpenAI, Prompt Engineering, Python
