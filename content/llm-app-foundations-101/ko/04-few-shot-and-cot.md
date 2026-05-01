---
title: Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기
series: llm-app-foundations-101
episode: 4
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

# Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기

> LLM 앱 기초 시리즈 (4/6)

예제 코드: [github.com/yeongseon-books/llm-app-foundations-101](https://github.com/yeongseon-books/llm-app-foundations-101/tree/main/ko/04-few-shot-and-cot)

이전 글에서는 `system`, `user`, `assistant` 역할을 분리해 프롬프트를 설계하는 기본 구조를 잡았습니다. 그다음 단계에서 바로 부딪히는 질문은 이것입니다. 같은 모델인데도 어떤 요청은 기대한 형식을 잘 따르고, 어떤 요청은 어딘가 비슷하지만 애매하게 빗나갑니다. 이 차이는 모델 자체보다도 모델을 어떻게 유도했는지에서 자주 갈립니다.

실무에서 가장 먼저 꺼내는 손잡이 두 개가 few-shot prompting과 chain-of-thought prompting입니다. few-shot은 원하는 답변 패턴을 예시로 먼저 보여 주는 방식이고, chain-of-thought는 문제를 한 번에 찍게 두지 않고 단계적으로 풀도록 유도하는 방식입니다. 둘 다 새 모델을 학습시키는 기법이 아닙니다. 이미 있는 모델의 행동을 더 안정적으로 끌어내는 입력 설계 기법입니다.

이번 글에서는 Groq의 `llama-3.1-8b-instant`를 기준으로 이 두 기법을 실제 코드로 다룹니다. 범위는 일곱 가지입니다.

- few-shot prompting이 무엇인지
- zero-shot과 few-shot이 어떻게 다른지
- 예시 품질이 왜 결과를 좌우하는지
- chain-of-thought가 왜 복합 문제에서 도움이 되는지
- zero-shot CoT와 few-shot CoT 패턴 차이
- few-shot과 CoT를 함께 쓰는 방법
- 이 기법들이 잘 안 먹히는 상황

포인트는 단순합니다. 좋은 프롬프트는 질문을 길게 쓰는 재주보다, 모델이 따라야 할 패턴을 얼마나 선명하게 보여 주느냐에 달려 있습니다.

---

## few-shot prompting은 예시로 패턴을 가르치는 일입니다

few-shot prompting은 모델에게 “이런 식으로 답하면 된다”는 예시를 먼저 보여 준 뒤, 마지막에 실제 질문을 넣는 방식입니다. 채팅 API에서는 이 예시를 별도 필드에 넣지 않습니다. 앞선 글에서 본 것처럼 같은 `messages` 배열 안에 `user`와 `assistant` 쌍으로 배치합니다.

구조는 대개 아래와 같습니다.

1. `system`에 전체 역할과 규칙을 둡니다.
2. `user` 예시 질문을 넣습니다.
3. 그에 대한 모범 `assistant` 답변을 넣습니다.
4. 이런 예시 쌍을 한두 개 더 넣습니다.
5. 마지막 `user` 메시지에 실제 요청을 넣습니다.

모델 관점에서는 이것이 작은 문맥 학습처럼 작동합니다. 가중치를 업데이트하지는 않지만, 현재 요청 안에서 “질문이 이렇게 생기면 답변은 이런 형식이어야 한다”는 패턴을 읽습니다. 형식 고정, 톤 유도, 라벨링 방식 통일, 짧은 변환 작업에서 특히 효과가 좋습니다.

아래 코드는 개념을 가장 작게 보여 주는 예제입니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": (
            "당신은 고객 문의를 분류하는 운영 도우미입니다. "
            "항상 아래 형식으로만 답하세요:\n"
            "category: <billing|technical|account>\n"
            "priority: <low|medium|high>\n"
            "reason: <한 문장>"
        ),
    },
    {"role": "user", "content": "결제는 됐는데 영수증 메일이 오지 않았어요."},
    {
        "role": "assistant",
        "content": (
            "category: billing\n"
            "priority: medium\n"
            "reason: 결제 이후 증빙 메일 누락 문제라 과금 영역으로 본다."
        ),
    },
    {"role": "user", "content": "비밀번호를 바꿨는데도 로그인에 계속 실패합니다."},
    {
        "role": "assistant",
        "content": (
            "category: account\n"
            "priority: high\n"
            "reason: 계정 접근 실패는 사용 불가 상태로 이어질 수 있다."
        ),
    },
    {"role": "user", "content": "CSV 업로드를 누르면 서버 오류가 납니다."},
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.2,
)

print(completion.choices[0].message.content)
```

이 예시는 긴 설명보다 세 가지를 분명하게 보여 줍니다. 첫째, few-shot은 결국 메시지 배열 설계입니다. 둘째, 예시는 질문만이 아니라 원하는 답변 형식까지 포함해야 합니다. 셋째, 예시 수가 늘수록 토큰도 늘어나므로 대표성 있는 짧은 예시를 고르는 편이 낫습니다.

---

## zero-shot과 few-shot은 같은 질문도 다르게 끌고 갑니다

zero-shot은 예시 없이 바로 요청하는 방식입니다. 모델이 이미 학습한 일반 능력에 기대는 형태입니다. 단일 라벨 분류나 짧은 변환 작업에서는 zero-shot만으로도 꽤 잘 됩니다. 다만 출력 형식이 미묘하게 흔들리거나, 라벨 경계가 애매한 문제에서 일관성이 부족할 수 있습니다.

아래 코드는 같은 문의를 zero-shot과 few-shot으로 각각 보내 비교합니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

ticket = "팀 요금제인데 이번 달 청구 금액이 예상보다 두 배 가까이 높습니다."

system_prompt = (
    "당신은 SaaS 고객 문의를 분류하는 운영 도우미입니다. "
    "반드시 아래 형식으로만 답하세요:\n"
    "category: <billing|technical|account>\n"
    "priority: <low|medium|high>\n"
    "reason: <한 문장>"
)

zero_shot = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": ticket},
    ],
    temperature=0.2,
)

few_shot = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "환불이 아직 카드 명세서에 반영되지 않았어요."},
        {
            "role": "assistant",
            "content": (
                "category: billing\n"
                "priority: medium\n"
                "reason: 환불 반영 지연은 결제 후속 처리 문제다."
            ),
        },
        {"role": "user", "content": "2단계 인증 코드를 받아도 로그인이 되지 않습니다."},
        {
            "role": "assistant",
            "content": (
                "category: account\n"
                "priority: high\n"
                "reason: 계정 접근 실패는 사용자의 업무를 바로 막을 수 있다."
            ),
        },
        {"role": "user", "content": ticket},
    ],
    temperature=0.2,
)

print("[zero-shot]")
print(zero_shot.choices[0].message.content)
print()
print("[few-shot]")
print(few_shot.choices[0].message.content)
```

실행해 보면 zero-shot도 꽤 그럴듯하게 맞추는 경우가 많습니다. 그런데 few-shot 쪽이 보통 더 안정적으로 아래 요소를 맞춥니다.

- 라벨 이름
- 출력 줄 수와 순서
- 이유 설명 길이
- 애매한 문의를 해석하는 기준

이 차이가 중요한 이유는 애플리케이션에서는 한 번의 정답보다 수백 번의 재현성이 더 중요하기 때문입니다. 데모에서는 “대충 맞는다”가 충분하지만, 운영에서는 “항상 같은 스키마로 떨어진다”가 더 중요합니다.

---

## 예시 품질이 낮으면 few-shot은 오히려 독이 됩니다

few-shot은 예시를 보여 주는 기법이기 때문에, 예시 자체의 품질이 결과 품질을 강하게 끌고 갑니다. 이 점이 가장 자주 과소평가됩니다. 많은 입문자가 “예시를 넣었는데 왜 더 이상해졌지?”를 겪는데, 대부분 예시가 나쁘거나 서로 일관되지 않습니다.

나쁜 예시는 대개 네 부류입니다.

- 라벨이 일관되지 않은 예시
- 답변 형식이 매번 다른 예시
- 지나치게 장황해서 핵심 패턴이 흐려진 예시
- 실제 입력과 동떨어진 쉬운 예시

아래 코드는 같은 질문에 나쁜 예시와 좋은 예시를 각각 붙여 보내는 비교입니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

target_question = "비밀번호 재설정 메일이 오지 않아 로그인하지 못하고 있습니다."

bad_examples = [
    {"role": "user", "content": "청구서 금액이 이상합니다."},
    {
        "role": "assistant",
        "content": "이건 결제 문제 같기도 하고 계정 문제 같기도 합니다. 우선 고객에게 다시 물어보세요.",
    },
    {"role": "user", "content": "로그인이 안 됩니다."},
    {
        "role": "assistant",
        "content": "priority는 급할 수도 있고 아닐 수도 있습니다. 상황마다 다릅니다.",
    },
]

good_examples = [
    {"role": "user", "content": "결제 카드가 두 번 청구된 것 같습니다."},
    {
        "role": "assistant",
        "content": (
            "category: billing\n"
            "priority: high\n"
            "reason: 중복 청구는 금전 피해 가능성이 있어 우선 대응이 필요하다."
        ),
    },
    {"role": "user", "content": "프로필 사진 업로드 버튼을 누르면 500 오류가 납니다."},
    {
        "role": "assistant",
        "content": (
            "category: technical\n"
            "priority: medium\n"
            "reason: 기능 오류지만 계정 잠금만큼 즉시성이 높지는 않다."
        ),
    },
]

system_prompt = (
    "당신은 SaaS 고객 문의를 분류합니다. "
    "아래 형식으로만 답하세요:\n"
    "category: <billing|technical|account>\n"
    "priority: <low|medium|high>\n"
    "reason: <한 문장>"
)

bad_run = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "예시를 보고 같은 형식으로 분류해 주세요."},
        *bad_examples,
        {"role": "user", "content": target_question},
    ],
    temperature=0.2,
)

good_run = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": system_prompt},
        *good_examples,
        {"role": "user", "content": target_question},
    ],
    temperature=0.2,
)

print("[bad examples]")
print(bad_run.choices[0].message.content)
print()
print("[good examples]")
print(good_run.choices[0].message.content)
```

코드만 보면 차이가 작아 보일 수 있지만, 결과는 꽤 크게 갈립니다. 나쁜 예시는 모델에게 형식을 가르치지 못하고 애매함만 전달합니다. 좋은 예시는 라벨, 우선순위 판단 기준, 문장 길이를 함께 고정합니다. few-shot의 핵심은 예시 개수가 아니라 예시의 선명도입니다.

실무에서는 아래 기준으로 예시를 고르는 편이 안전합니다.

- 실제 입력과 비슷한 난이도일 것
- 서로 같은 형식을 유지할 것
- 경계가 애매한 사례를 포함할 것
- 답변이 짧고 패턴이 분명할 것

---

## chain-of-thought는 복합 문제를 단계로 쪼개게 만듭니다

few-shot이 답변 패턴을 보여 주는 기법이라면, chain-of-thought는 문제 풀이 과정을 단계로 나누게 하는 기법입니다. 가장 널리 알려진 형태는 프롬프트 끝에 “단계적으로 생각해 주세요” 혹은 영어로 “Let's think step by step”를 붙이는 방식입니다.

이 말이 왜 통할까요. 이유는 마법이 아니라 작업 구조입니다. 모델이 한 번에 최종 답만 내야 할 때보다, 중간 판단 단계를 거치도록 유도할 때 복합 제약을 놓칠 가능성이 줄어듭니다. 산술, 규칙 적용, 조건 비교, 여러 문장을 함께 읽는 추론에서 자주 도움이 됩니다.

물론 이 기법을 과장해서 보면 안 됩니다. 모델이 없던 지식을 갑자기 얻는 것은 아닙니다. 근거가 없는 분야 질문, 최신 정보가 필요한 질문, 애초에 모델이 잘 모르는 도메인에서는 step by step이라는 문구만으로 해결되지 않습니다. 그래도 이미 알고 있는 지식을 더 질서 있게 꺼내게 하는 데는 꽤 유용합니다.

아래는 zero-shot CoT의 가장 단순한 예제입니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

question = (
    "온라인 강의가 120000원입니다. 쿠폰 10%를 먼저 적용하고, "
    "그 결과에 부가세 10%를 붙이면 최종 결제 금액은 얼마인가요?"
)

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": "당신은 계산 과정을 차분히 설명하는 도우미입니다.",
        },
        {
            "role": "user",
            "content": (
                question
                + " 단계적으로 생각해 주세요. 마지막 줄에는 final_answer: <숫자>원 형식으로만 적어 주세요."
            ),
        },
    ],
    temperature=0.0,
)

print(completion.choices[0].message.content)
```

이 방식은 중간 추론 단계를 더 분명하게 끌어내는 경향이 있습니다. 그 결과 산술 순서나 조건 적용 순서를 덜 놓칩니다. 특히 “먼저 할인, 그다음 세금”처럼 순서가 중요한 문제에서 효과를 체감하기 쉽습니다.

---

## zero-shot CoT와 few-shot CoT는 쓰임새가 다릅니다

zero-shot CoT는 예시 없이 “단계적으로 생각하라”고만 지시하는 패턴입니다. 장점은 간단하고 토큰이 적게 든다는 점입니다. 이미 꽤 잘 학습된 일반 추론 문제라면 이 한 줄만으로도 성능이 좋아지는 경우가 많습니다.

few-shot CoT는 여기에 한 단계 더 나갑니다. 답만 보여 주는 few-shot이 아니라, 예시 답변 안에 추론 순서까지 포함합니다. 그러면 모델은 최종 형식뿐 아니라 풀이 리듬까지 따라 하게 됩니다.

아래 코드는 few-shot CoT의 기본 형태입니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": (
            "당신은 주문 금액을 계산하는 도우미입니다. "
            "항상 1) 계산 단계 2) final_answer 형식으로 답하세요."
        ),
    },
    {
        "role": "user",
        "content": "가격이 50000원이고 20% 할인 후 배송비 3000원을 더하면 얼마인가요?",
    },
    {
        "role": "assistant",
        "content": (
            "1) 50000원의 20%는 10000원입니다.\n"
            "2) 할인 적용 후 금액은 40000원입니다.\n"
            "3) 배송비 3000원을 더하면 43000원입니다.\n"
            "final_answer: 43000원"
        ),
    },
    {
        "role": "user",
        "content": "가격이 80000원이고 25% 할인 후 배송비 5000원을 더하면 얼마인가요?",
    },
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.0,
)

print(completion.choices[0].message.content)
```

둘의 차이는 이런 식으로 보면 됩니다.

- zero-shot CoT: 추론하라고만 지시
- few-shot CoT: 추론 예시까지 먼저 제공

입문 단계에서는 zero-shot CoT부터 시도하고, 출력 형식이나 추론 순서가 계속 흔들릴 때 few-shot CoT로 넘어가는 편이 비용 대비 효율이 좋습니다.

---

## few-shot과 CoT를 함께 쓰면 답변 패턴과 풀이 절차를 동시에 고정할 수 있습니다

실무에서는 두 기법을 분리해서만 쓰지 않습니다. 답변 형식도 고정하고 싶고, 중간 추론 절차도 놓치게 하고 싶지 않을 때 둘을 함께 씁니다. 특히 규칙 기반 분류, 운영 의사결정, 정책 판정처럼 “조건을 단계로 확인한 뒤 최종 레이블을 내야 하는 작업”에서 유용합니다.

아래 예제는 고객 환불 요청을 정책 기준에 따라 판정하는 few-shot CoT 패턴입니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

policy = (
    "환불 정책:\n"
    "- 결제 후 7일 이내이고 시청률 20% 미만이면 전액 환불\n"
    "- 결제 후 7일 이내이고 시청률 20% 이상이면 환불 불가\n"
    "- 결제 후 7일 초과면 시청률과 무관하게 환불 불가"
)

messages = [
    {
        "role": "system",
        "content": (
            "당신은 온라인 강의 서비스의 환불 심사 도우미입니다. "
            "항상 1) policy_check 2) decision 3) reason 형식으로 답하세요."
        ),
    },
    {"role": "user", "content": policy},
    {
        "role": "user",
        "content": "결제 후 3일 지났고 시청률은 10%입니다. 환불 가능 여부를 판단해 주세요.",
    },
    {
        "role": "assistant",
        "content": (
            "policy_check:\n"
            "1) 결제 후 7일 이내입니다.\n"
            "2) 시청률이 20% 미만입니다.\n"
            "decision: approved\n"
            "reason: 기간과 시청률 조건을 모두 충족해 전액 환불 대상입니다."
        ),
    },
    {
        "role": "user",
        "content": "결제 후 5일 지났고 시청률은 35%입니다. 환불 가능 여부를 판단해 주세요.",
    },
    {
        "role": "assistant",
        "content": (
            "policy_check:\n"
            "1) 결제 후 7일 이내입니다.\n"
            "2) 시청률이 20% 이상입니다.\n"
            "decision: denied\n"
            "reason: 기간 조건은 맞지만 시청률 기준을 넘어 환불할 수 없습니다."
        ),
    },
    {
        "role": "user",
        "content": "결제 후 10일 지났고 시청률은 0%입니다. 환불 가능 여부를 판단해 주세요.",
    },
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.0,
)

print(completion.choices[0].message.content)
```

이 패턴의 장점은 둘입니다. 먼저 예시가 답변 껍데기를 고정합니다. 이어서 `policy_check` 단계가 판단 순서를 고정합니다. 단순히 `approved`나 `denied`만 받는 것보다 디버깅도 쉬워집니다. 잘못 분류되면 어느 단계에서 판단이 틀어졌는지 확인할 수 있기 때문입니다.

---

## 언제는 잘 먹히고, 언제는 기대만큼 안 먹힙니다

few-shot과 CoT는 강력하지만 만능은 아닙니다. 아래 상황에서는 효과가 제한되거나 오히려 비용만 늘 수 있습니다.

### 모델이 원래 모르는 지식을 물을 때

few-shot도 CoT도 없는 사실을 만들어 내는 해결책은 아닙니다. 최신 법규, 비공개 사내 정책, 공급자 장애 현황처럼 모델이 학습하지 않았거나 볼 수 없는 정보는 별도 검색이나 도구 호출이 필요합니다.

### 입력 컨텍스트가 이미 너무 길 때

few-shot 예시는 토큰을 더 먹습니다. 대화 이력이나 RAG 문서가 이미 길다면, 예시 몇 개를 얹는 순간 컨텍스트 예산이 빠르게 줄어듭니다. 이런 경우에는 예시보다 입력 정리가 먼저입니다.

### 출력 형식이 아주 엄격할 때

CoT는 종종 설명을 길게 만듭니다. 그런데 여러분이 원하는 것이 엄격한 JSON, CSV, SQL 한 줄이라면 추론 문장이 오히려 방해가 됩니다. 이때는 chain-of-thought를 노출하기보다 형식 제약을 더 강하게 두는 편이 낫습니다.

### 예시가 실제 문제를 대표하지 못할 때

쉬운 예시 두 개를 넣고 어려운 경계 사례를 맞히길 기대하면 성능이 흔들립니다. few-shot은 데이터셋 전체를 대체하는 학습이 아닙니다. 현재 요청 근처의 패턴을 짧게 힌트하는 정도로 보는 편이 정확합니다.

### 모델이 이미 충분히 잘하는 단순 작업일 때

짧은 요약, 간단한 재작성, 명확한 분류처럼 zero-shot만으로도 충분한 작업은 많습니다. 이때 few-shot과 CoT를 습관적으로 붙이면 지연 시간과 비용만 올라갑니다. 프롬프트는 언제나 최소한에서 시작하는 편이 좋습니다.

---

## 마무리

few-shot은 예시로 행동 패턴을 보여 주는 기술이고, chain-of-thought는 문제를 단계로 풀게 하는 기술입니다. 전자는 형식과 스타일을 안정시키는 데 강하고, 후자는 복합 조건 추론을 덜 놓치게 하는 데 강합니다. 둘을 함께 쓰면 답변 껍데기와 판단 절차를 동시에 고정할 수 있습니다.

다만 실전 감각은 언제나 같은 결론으로 돌아옵니다. 예시를 많이 넣는다고 무조건 좋아지지 않습니다. step by step 한 줄을 붙인다고 없는 지식이 생기지도 않습니다. 좋은 결과는 대개 짧고 선명한 예시, 분명한 출력 형식, 낮은 temperature, 그리고 토큰 예산 관리에서 나옵니다.

다음 글에서는 멀티턴 대화에서 이력을 어떻게 관리할지 다룹니다. few-shot이 정적인 예시라면, 대화 상태 관리는 시간에 따라 바뀌는 동적 문맥 문제입니다. 그 지점부터 챗봇다운 설계가 본격적으로 시작됩니다.

<!-- blog-only:start -->
다음 글: [대화 상태 관리 — 멀티턴 챗봇 만들기](./05-conversation-state.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기](./01-llm-api-first-call.md)
- [토큰 이해하기 — 비용, 한계, 컨텍스트 창](./02-understanding-tokens.md)
- [프롬프트 엔지니어링 기초 — System·User·Assistant 역할](./03-prompt-engineering-basics.md)
- **Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기 (현재 글)**
- 대화 상태 관리 — 멀티턴 챗봇 만들기 (예정)
- 스트리밍 응답 처리 — 실시간으로 출력 받기 (예정)

<!-- toc:end -->

---

## 참고 자료

- Groq Docs, "Text chat": <https://console.groq.com/docs/text-chat>
- Groq Python Library: <https://github.com/groq/groq-python>
- OpenAI, "Prompt engineering": <https://platform.openai.com/docs/guides/prompt-engineering>
- Anthropic Docs, "Prompt engineering overview": <https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview>
- Jason Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models": <https://arxiv.org/abs/2201.11903>

Tags: LLM, OpenAI, Prompt Engineering, Python
