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

여기서는 AI에게 원하는 답을 더 안정적으로 얻기 위한 프롬프트 설계 원칙과 검증 루틴을 실무 감각으로 정리합니다.

![AI Web Development 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/02/prompt-role-layering.ko.png)
*AI Web Development 101 2장 흐름 개요*

## 먼저 던지는 질문

- 프롬프트는 단순한 질문과 무엇이 다를까요?
- `system`과 `user` 역할은 각각 어떤 책임을 가질까요?
- 좋은 프롬프트는 어떤 정보를 빠뜨리지 않을까요?

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

## 운영 기준선을 만드는 미니 평가표

프롬프트 품질을 팀으로 관리하려면 "좋아 보인다" 대신 공통 평가표가 필요합니다. 처음에는 거창할 필요 없이, 작업별로 최소한의 기준만 고정해도 효과가 큽니다.

| 작업 유형 | 필수 기준 | 실패 신호 |
| --- | --- | --- |
| 고객 문의 요약 | 2문장 이내, 사실만 유지 | 문장 수 초과, 추측성 문장 추가 |
| 정책 안내 | 불릿 3개, 금지 표현 제외 | 항목 누락, 금지 표현 포함 |
| 분류 작업 | 허용 라벨 집합 내 결과 | 라벨 오타, 집합 밖 값 |

여기서 중요한 점은 평가표가 프롬프트와 함께 버전 관리된다는 사실입니다. 프롬프트를 바꾸면 평가표도 같이 바꾸고, 테스트 결과를 PR에 남기면 이후 회귀를 빠르게 찾을 수 있습니다. 이 방식은 모델 변경, 파라미터 변경, 시스템 프롬프트 수정이 겹쳐도 "무엇 때문에 품질이 바뀌었는지"를 분리해서 보게 해 줍니다.

## 재사용 가능한 프롬프트 템플릿 설계

프롬프트 엔지니어링을 문장 센스로만 접근하면 팀 단위 협업에서 바로 막힙니다. 실무에서는 같은 기능을 여러 사람이 만지기 때문에, 템플릿을 명시적 계약으로 다뤄야 합니다. 특히 입력 변수, 출력 형식, 금지 규칙을 분리하면 리뷰 기준이 선명해집니다.

```python
PROMPT_TEMPLATE = """
역할: 당신은 한국어 기술 블로그 편집 도우미입니다.
목표: 사용자의 초안을 실무 문체로 정리합니다.
제약:
- 사실 확인이 안 된 내용은 추측하지 않습니다.
- 목록은 5개를 넘기지 않습니다.
출력 형식(JSON):
{{
  "summary": "한 문장 요약",
  "issues": ["문제점"],
  "rewrite": "개선된 본문"
}}
입력 본문:
{draft}
"""
```

이 템플릿처럼 역할, 목표, 제약, 출력 형식을 분리하면 모델 버전을 바꿔도 품질 편차를 줄일 수 있습니다. 또한 장애가 발생했을 때 어느 레이어가 깨졌는지 빠르게 역추적할 수 있습니다.

## 출력 계약을 강제하는 OpenAI API 예시

자연어 결과만 받는 방식은 빠르지만, 서비스 API와 연결할 때 파싱 불안정이 반복됩니다. 따라서 가능한 곳에서는 구조화 출력 또는 엄격한 JSON 계약을 두는 편이 좋습니다.

```python
from openai import OpenAI
import json

client = OpenAI()

def refine_draft(draft: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "항상 JSON 객체만 응답합니다."},
            {"role": "user", "content": PROMPT_TEMPLATE.format(draft=draft)},
        ],
    )
    raw = response.choices[0].message.content or "{}"
    parsed = json.loads(raw)
    return parsed
```

중요한 지점은 JSON 파싱 실패를 일반 예외로 덮지 않는 것입니다. 파싱 실패율을 별도 지표로 기록하면 프롬프트 퇴화를 조기에 감지할 수 있습니다.

## RAG와 결합할 때의 프롬프트 경계

많은 팀이 RAG를 붙인 뒤에도 답변 품질이 안정되지 않는 이유는 검색 결과를 무조건 길게 붙이기 때문입니다. 프롬프트에는 검색 결과를 넣되, 모델이 어떤 기준으로 문서를 선택해 인용할지 명시해야 합니다.

```text
시스템 지침:
- 제공된 문서 조각만 근거로 사용합니다.
- 근거 문서에 없는 내용은 "근거 없음"으로 답합니다.
- 답변 마지막에 source_ids를 배열로 출력합니다.

사용자 질문:
{question}

검색 문서:
{retrieved_chunks}
```

이 계약이 있으면 환각을 완전히 없애지는 못해도, 최소한 근거 추적 가능성을 확보할 수 있습니다.

## LangChain PromptTemplate 예시

프레임워크를 쓸 때도 원리는 같습니다. 템플릿과 체인을 분리해 두면 추후 실험 자동화가 쉬워집니다.

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 한국어 기술지원 도우미입니다. 근거 없는 추측을 금지합니다."),
    ("human", "질문: {question}\n\n문서:\n{context}\n\n형식: 요약 1문장 + 핵심 3개")
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
chain = prompt | llm

result = chain.invoke({
    "question": "토큰 비용이 갑자기 증가한 원인을 알려줘",
    "context": "지난주부터 프롬프트에 로그 전문이 통째로 들어가기 시작함"
})
```

LangChain을 쓰더라도 템플릿 품질 자체가 결과를 좌우한다는 사실은 변하지 않습니다.

## 프롬프트 품질 평가 지표

프롬프트를 개선할 때는 "좋아 보인다" 대신 측정 가능한 지표를 둬야 합니다.

- 정확성: 정답 데이터셋 대비 일치율
- 형식 준수율: JSON 파싱 성공률, 필수 필드 누락률
- 길이 적합성: 지정 토큰 범위를 벗어나는 비율
- 안전성: 금지 주제 응답 차단률
- 비용: 요청당 평균 total_tokens

아래처럼 간단한 회귀 테스트 스크립트만 있어도 프롬프트 변경의 품질 하락을 막을 수 있습니다.

```python
CASES = [
    {"q": "환불 정책 알려줘", "must_include": ["영업일"], "must_not_include": ["확실하지 않지만"]},
    {"q": "의료 진단해줘", "must_include": ["답변할 수 없습니다"], "must_not_include": ["복용량"]},
]
```

## 프롬프트 버전 관리 규칙

프롬프트를 코드처럼 다루려면 버전 규칙이 필요합니다. 예를 들어 `answer_v1`, `answer_v2`처럼 번호를 올리고, 변경 이유를 한 줄로 남기는 방식이 실무에서 가장 단순합니다.

- `v1 -> v2`: 출력 JSON 필드 `confidence` 추가
- `v2 -> v3`: 금지 주제 응답 문구를 정책 문구로 통일
- `v3 -> v4`: RAG 근거 인용 형식 `source_ids` 배열로 고정

이 변경 이력은 나중에 평가 점수 하락 원인을 찾을 때 매우 큰 도움을 줍니다. 특히 "모델 변경 없이 품질이 떨어진 사건"의 대부분은 프롬프트 변경에서 시작됩니다.

## 실험 로그를 남기는 A/B 프롬프트 비교

프롬프트 개선에서 가장 흔한 함정은 "이번 버전이 더 좋아 보인다"는 인상 평가입니다. 실무에서는 같은 입력셋으로 A/B를 돌리고, 형식 준수율과 사용자 피드백을 함께 비교해야 합니다.

```python
def run_prompt_ab(cases, prompt_a, prompt_b):
    report = []
    for case in cases:
        out_a = call_model(prompt_a, case["question"])
        out_b = call_model(prompt_b, case["question"])
        report.append({
            "id": case["id"],
            "a_json_ok": is_valid_json(out_a),
            "b_json_ok": is_valid_json(out_b),
            "a_len": len(out_a),
            "b_len": len(out_b),
        })
    return report
```

여기서 JSON 준수율이 오르고 답변 길이 편차가 줄었다면, 실제 사용자 경험도 안정될 가능성이 높습니다. 반대로 점수는 올랐는데 토큰 사용량이 급증하면 운영 비용이 감당 가능한지 함께 판단해야 합니다.

## 프롬프트 실패 사례 기록 예시

아래처럼 실패 사례를 구체적으로 적어 두면 팀 학습 속도가 크게 빨라집니다.

- 사례 1: 금지 주제를 우회 표현으로 답변함 -> 금지 패턴 사전 강화
- 사례 2: JSON 형식 대신 마크다운으로 출력함 -> 시스템 지침에 "JSON 외 출력 금지" 재명시
- 사례 3: 길이 제한 초과 -> "최대 5문장" 제약 추가

이 기록은 단순 문서가 아니라 다음 실험의 입력 데이터가 됩니다.

## 운영에서 바로 쓰는 프롬프트 점검표

배포 직전에는 아래 점검표를 반드시 통과시키는 편이 좋습니다.

- 역할 문장이 한 줄로 명확한가
- 출력 형식이 파서 요구사항과 일치하는가
- 금지 규칙이 예외 없이 포함되어 있는가
- 길이 제한과 톤 제한이 함께 선언되어 있는가
- 실패 시 대체 문구가 정의되어 있는가

이 다섯 항목은 작아 보이지만, 운영 장애의 대부분을 사전에 줄여 줍니다.

### 실무 메모

이 절에서 다룬 원칙은 기능이 늘어날수록 더 중요해집니다. 특히 팀원이 늘어나면 개인 감각보다 문서화된 규칙이 더 큰 품질 차이를 만듭니다. 따라서 예제 코드를 복사해 쓰는 것에서 멈추지 말고, 현재 팀의 장애 패턴과 운영 제약에 맞춰 규칙을 재정의하는 작업이 필요합니다. 작은 체크리스트 하나가 장기적으로는 가장 큰 비용 절감으로 돌아옵니다.

## 정리

프롬프트 엔지니어링은 AI에게 예쁘게 말하는 기술이 아니라, 모델이 따라야 할 작업 계약을 설계하고 검증하는 기술입니다.

- `system`은 장기 규칙, `user`는 현재 작업 지시라는 구분을 먼저 잡습니다.
- 좋은 프롬프트는 역할, 맥락, 출력 형식, 제약 조건을 빠뜨리지 않습니다.
- `temperature`와 `max_tokens`는 프롬프트의 일부처럼 함께 다뤄야 합니다.
- 실패할수록 프롬프트를 디버깅 대상과 테스트 입력으로 다루는 습관이 중요합니다.

다음 글에서는 이 원칙을 브라우저 UI와 연결해, 사용자가 실제로 대화할 수 있는 챗봇 형태로 구현해 보겠습니다.

## 처음 질문으로 돌아가기

- **프롬프트는 단순한 질문과 무엇이 다를까요?**
  - 단순한 질문은 모델에게 빈칸을 남기지만, 프롬프트는 역할·맥락·출력 형식·제약 조건까지 포함한 작업 계약입니다. `bad` 예제의 "상품 소개 문구를 써줘"와 `better` 예제의 `대상 독자`, `강조점`, `출력 형식` 차이가 바로 그 계약의 차이였습니다. 그래서 이 글은 프롬프트를 문장 감각이 아니라 재현 가능한 입력 구조로 다뤘습니다.
- **`system`과 `user` 역할은 각각 어떤 책임을 가질까요?**
  - `system`은 "너는 고객 지원 FAQ 생성기다"처럼 장기 규칙과 금지 조건을 고정하고, `user`는 "비밀번호 재설정 정책을 2문장 이내 FAQ로 만들어줘"처럼 현재 작업을 전달합니다. `PROMPT_TEMPLATE` 예제에서도 역할, 목표, 제약, JSON 출력 형식을 시스템 성격으로 묶고 `draft`만 입력 변수로 주입했습니다. 이 분리가 있어야 프롬프트 버전이 바뀌었는지, 요청 데이터가 바뀌었는지 원인을 분리해 볼 수 있습니다.
- **좋은 프롬프트는 어떤 정보를 빠뜨리지 않을까요?**
  - 좋은 프롬프트는 최소한 역할, 도메인 맥락, 출력 계약, 금지 규칙을 빠뜨리지 않습니다. 본문에서 JSON 키를 `title`, `summary`, `risk`로 고정하고, RAG 예시에서는 `source_ids` 배열과 "근거가 없으면 근거 없음" 규칙을 명시한 이유가 여기에 있습니다. 배포 직전 점검표에서 역할 문장, 길이 제한, 금지 규칙, 대체 문구를 함께 확인하라고 한 것도 결국 같은 원칙을 운영용으로 압축한 것입니다.

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
- [AI Web Development 101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/ai-web-dev-101/ko)

- [OpenAI Prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [OpenAI Prompt caching and prompt design guide](https://platform.openai.com/docs/guides/text)
- [Anthropic prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [OpenAI Cookbook prompt examples](https://cookbook.openai.com/)

Tags: AI, LLM, 웹 개발, Python, Tutorial
