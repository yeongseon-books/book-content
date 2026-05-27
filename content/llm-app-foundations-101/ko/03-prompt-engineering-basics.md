---
title: "LLM App Foundations 101 (3/6): 프롬프트 엔지니어링 기초 — System·User·Assistant 역할"
series: llm-app-foundations-101
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- LLM
- OpenAI
- Prompt Engineering
- Python
last_reviewed: '2026-05-15'
---

# LLM App Foundations 101 (3/6): 프롬프트 엔지니어링 기초 — System·User·Assistant 역할

프롬프트 엔지니어링은 흔히 말을 그럴듯하게 쓰는 요령처럼 소개됩니다. 하지만 애플리케이션 관점에서는 그 설명이 너무 약합니다. 실전에서 더 중요한 일은 지시를 역할별로 분리하고, 어떤 제약이 공통 정책인지, 어떤 내용이 이번 요청에만 해당하는지, 어떤 이력이 다음 턴으로 넘어가야 하는지를 구조로 고정하는 일입니다.

이 글은 LLM 앱 기초 시리즈의 3번째 글입니다.

이 차이는 초기에 바로 드러납니다. 입력을 문장 하나로 밀어 넣으면 톤이 흔들리고, 출력 형식이 매번 조금씩 달라지고, 이전 대화를 잊어버리고, 파라미터 조정도 감으로 하게 됩니다. 많은 입문자가 모델 불안정성으로 느끼는 문제 중 상당수는 사실 메시지 배열 구조가 흐린 데서 시작합니다.

특히 채팅 API에서는 `system`, `user`, `assistant`가 단순한 라벨이 아닙니다. 애플리케이션 정책, 현재 요청, 누적 이력을 분리하는 최소 단위입니다. 이 세 층을 분명히 구분하면 같은 모델이어도 훨씬 예측 가능한 동작을 끌어낼 수 있습니다.

여기서는 역할 기반 메시지 배열을 프롬프트의 기본 단위로 보고, 안정적인 입력 구조를 만드는 방법을 정리하겠습니다.

![역할 기반 프롬프트 구성의 전체 그림](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-01-prompt-engineering-basics-system-user-an.ko.png)
*역할 기반 프롬프트 구성의 전체 그림*

## 먼저 던지는 질문

- system, user, assistant 역할은 각각 어떤 책임을 맡을까요?
- system message는 왜 단순한 첫 문장보다 강한 기준이 될까요?
- temperature, top_p, few-shot은 답변 안정성에 어떤 영향을 줄까요?

## 왜 이 글이 중요한가

첫 API 호출이 성공한 뒤 곧바로 부딪히는 문제는 “같은 모델인데 왜 응답이 자꾸 달라지지?”입니다. 이 질문에 대한 첫 번째 답은 모델 교체가 아니라 입력 구조 점검입니다. 어떤 정책이 모든 요청에 공통인지, 어떤 제약이 현재 요청만의 것인지, 어떤 이력이 다음 턴에 남아야 하는지가 섞여 있으면 결과가 흔들리는 것이 자연스럽습니다.

또한 프롬프트 엔지니어링은 문장 표현보다 운영 가능성과 더 가깝습니다. 공통 정책을 `system`에 모아 두면 변경 지점이 한곳이 되고, 이력을 `assistant`로 명시하면 멀티턴 디버깅이 쉬워집니다. 출력 형식 요구를 구조적으로 적어 두면 테스트 가능한 계약이 생깁니다.

결국 좋은 프롬프트는 “모델에게 잘 부탁하는 문장”이 아니라 “애플리케이션이 반복적으로 재구성할 수 있는 입력 설계”입니다. 이 감각이 있어야 이후 few-shot, 대화 상태, 구조화 출력으로 자연스럽게 이어집니다.

## 역할 기반 프롬프트를 이해하는 가장 좋은 방법: 한 문장 프롬프트가 아니라 정책·현재 요청·이력의 세 층으로 보는 것입니다

채팅 API의 메시지 배열은 단순한 나열이 아닙니다. `system`은 거의 모든 요청에 공통으로 적용될 정책을 담고, `user`는 이번 턴의 실제 요청을 담고, `assistant`는 이전 턴의 모델 답변을 다시 주입해 문맥을 복원합니다. 이 셋을 분리하면 모델이 어떤 지시를 얼마나 안정적으로 따라야 하는지 설명하기가 훨씬 쉬워집니다.

이 관점이 중요한 이유는 대화 품질 문제의 많은 부분이 역할 혼선에서 나오기 때문입니다. 공통 규칙을 매번 `user`에 반복하거나, 이력을 재전송하지 않거나, 창의적 샘플링을 높여 두고 엄격한 형식을 기대하면 결과가 흔들릴 수밖에 없습니다.

> 프롬프트 엔지니어링의 출발점은 멋진 문장이 아니라, 어떤 지시가 어느 역할에 속하는지 명시하는 메시지 구조입니다.

## 핵심 개념

채팅 프롬프트를 운영 가능한 형태로 만들려면 먼저 세 역할을 분리해야 합니다. `system`은 전체 정책, `user`는 현재 요청, `assistant`는 이전 답변입니다. 이 구조가 없으면 애플리케이션은 매 요청마다 같은 규칙을 중복해서 말하게 되고, 이력도 암묵적으로 기대하게 됩니다.

![세 역할이 하나의 messages 배열로 합쳐지는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-01-understanding-the-three-roles.ko.png)

*세 역할이 하나의 messages 배열로 합쳐지는 구조*

실무적으로는 아래처럼 정리하면 됩니다.

- `system`: 언어, 톤, 안전 경계, 출력 규칙 같은 공통 정책
- `user`: 현재 작업 지시, 질문, 첨부 맥락
- `assistant`: 다음 턴에서 다시 보여 줄 과거 답변

system 메시지의 효과는 직접 비교해 보는 편이 빠릅니다.

![system 메시지가 답변 구조를 바꾸는 방식](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-02-how-a-system-message-changes-the-answer.ko.png)

*system 메시지가 답변 구조를 바꾸는 방식*

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

question = "Explain the difference between a Python dictionary and a list."

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
                "You are a Python tutor for beginners. "
                "Always answer in English. "
                "Start with one short paragraph, then end with exactly three bullet points. "
                "Do not guess, and keep the explanation beginner-friendly."
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

이 비교에서 봐야 할 것은 “더 마음에 드는 답”이 아닙니다. system 메시지를 넣었을 때 언어, 분량, 불릿 수, 톤 같은 출력 계약이 얼마나 덜 흔들리는지입니다. 프롬프트를 운영 자산으로 보려면 바로 이 재현성이 중요합니다.

여기서 중요한 점은 system이 절대 명령은 아니지만 가장 강한 조향 입력이라는 사실입니다.

멀티턴 이력은 모델의 숨은 기억이 아니라 애플리케이션이 재구성한 메시지 배열입니다.

![이전 assistant 답변이 다음 턴에 재주입되는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-03-building-multi-turn-history-with-assista.ko.png)

*이전 assistant 답변이 다음 턴에 재주입되는 구조*

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": "You are a Python learning assistant. Be brief and precise.",
    },
    {
        "role": "user",
        "content": "Explain the difference between Python lists and tuples in one paragraph.",
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
        "content": "Add a short code example in no more than five lines.",
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

이 append 단계가 바로 챗봇 메모리의 핵심입니다. 다음 글에서 더 다루겠지만, 대화 상태는 모델 바깥의 자료구조입니다.

샘플링 파라미터도 프롬프트 설계의 일부입니다.

![낮은 temperature와 높은 temperature의 차이](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-04-temperature-and-top-p-consistency-versus.ko.png)

*낮은 temperature와 높은 temperature의 차이*

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

prompt = "Introduce FastAPI to a beginner in three sentences."

for temperature in (0.0, 0.9):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a technical editor. Keep answers concise.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )

    print(f"[temperature={temperature}]")
    print(completion.choices[0].message.content)
    print()
```

입문 단계에서는 두 가지 원칙이면 충분합니다. 형식 안정성이 중요하면 `temperature`를 낮게 시작하고, `temperature`와 `top_p`를 동시에 크게 흔들지 않는 것입니다.

실무적으로 가장 재사용하기 쉬운 구조는 instruction + context + output format 패턴입니다.

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
                "You are a Python tutor for backend beginners. "
                "Answer in English and do not guess."
            ),
        },
        {
            "role": "user",
            "content": (
                "Instruction: explain what a dataclass is.\n"
                "Context: the reader knows basic Python syntax but has never used dataclasses.\n"
                "Output format: 1) two-sentence explanation 2) code example in six lines or less 3) one-line use case"
            ),
        },
    ],
    temperature=0.2,
)

print(completion.choices[0].message.content)
```

역할 분리를 코드에서 반복 가능하게 만들려면 메시지 조립 함수를 두는 편이 좋습니다.

```python
from typing import Iterable

def build_messages(
    system_prompt: str,
    user_prompt: str,
    history: Iterable[dict[str, str]],
) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})
    return messages

history = [
    {"role": "assistant", "content": "Lists are mutable, while tuples are immutable."},
]

messages = build_messages(
    system_prompt="You are a concise Python tutor.",
    user_prompt="Add one short example that shows when a tuple is safer.",
    history=history,
)

for message in messages:
    print(message)
```

이렇게 구조를 고정해 두면 실패 모드도 더 빨리 읽힙니다. 예를 들어 공통 정책이 흔들리면 `system`을 보고, 이전 턴을 잊으면 `assistant` 재주입 로직을 보고, 출력 형식이 들쭉날쭉하면 `user` 안의 출력 규칙과 `temperature`를 함께 보면 됩니다. 역할을 분리하지 않은 프롬프트는 문제 원인도 함께 섞어 버립니다.

few-shot 예시도 같은 `messages` 배열 안에 들어갑니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": "You explain Python concepts as a one-line definition followed by a one-line analogy.",
    },
    {"role": "user", "content": "What is a class?"},
    {
        "role": "assistant",
        "content": "Definition: A class is a blueprint for creating objects.\nAnalogy: It is like a mold used to produce many objects with the same shape.",
    },
    {"role": "user", "content": "What is inheritance?"},
    {
        "role": "assistant",
        "content": "Definition: Inheritance lets a new class reuse attributes and behavior from an existing class.\nAnalogy: It is like starting from a base template and extending it instead of rebuilding from scratch.",
    },
    {"role": "user", "content": "What is a decorator?"},
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.2,
)

print(completion.choices[0].message.content)
```

마지막으로, 흔한 실수는 대부분 입력 구조를 흐리게 만드는 방향에서 나옵니다.

![출력을 흔들리게 만드는 프롬프트 설계 실수들](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-05-common-prompt-design-mistakes.ko.png)

*출력을 흔들리게 만드는 프롬프트 설계 실수들*

## 흔히 헷갈리는 지점

- 공통 정책을 매번 `user` 메시지에 반복해도 된다고 생각하기 쉽지만, 변경 지점이 늘고 안정성이 떨어집니다.
- 멀티턴 대화가 모델 내부 메모리라고 오해하기 쉽지만, 실제로는 `assistant` 메시지를 다시 넣는 애플리케이션 로직입니다.
- 높은 `temperature`와 엄격한 형식을 동시에 기대하면 충돌이 생깁니다.
- few-shot 예시를 많이 넣을수록 좋다고 생각하기 쉽지만, 긴 예시는 토큰만 쓰고 패턴은 흐릴 수 있습니다.
- “더 좋게”, “자세히”, “알아서” 같은 모호한 표현이 충분한 제어라고 믿기 쉽지만, 실제로는 문단 수·불릿 수·키 이름 같은 구체적 제약이 더 강합니다.

## 재사용 가능한 프롬프트 템플릿 패턴

프롬프트를 문장 덩어리로만 관리하면 변경 이력이 금방 꼬입니다. 실무에서는 템플릿과 슬롯을 분리해 정책·컨텍스트·출력 계약을 별도 변수로 다루는 편이 안전합니다.

```python
from dataclasses import dataclass

@dataclass
class PromptTemplate:
    system_policy: str
    instruction: str
    output_contract: str

BASE_TEMPLATE = PromptTemplate(
    system_policy=(
        "You are a backend Python tutor. "
        "Do not guess unknown facts. "
        "If information is missing, say what is missing explicitly."
    ),
    instruction="",
    output_contract=(
        "Return exactly this structure:\n"
        "summary: <2 sentences>\n"
        "example: <code block>\n"
        "pitfall: <1 sentence>"
    ),
)

def build_user_prompt(task: str, context: str) -> str:
    return (
        f"Instruction: {task}\n"
        f"Context: {context}\n"
        f"Output format: {BASE_TEMPLATE.output_contract}"
    )
```

이 구조의 장점은 정책 업데이트가 중앙 집중된다는 사실입니다. 예를 들어 “근거 없는 추측 금지” 규칙을 강화할 때 `system_policy` 한 곳만 바꾸면 전체 경로가 동시에 정리됩니다.

### 프롬프트 회귀 테스트 패턴

프롬프트 변경은 코드 변경과 동일하게 회귀를 만듭니다. 최소한의 스냅샷 테스트를 두면 출력 형식이 깨지는 순간을 빠르게 찾을 수 있습니다.

```python
EXPECTED_KEYS = ["summary:", "example:", "pitfall:"]

def assert_output_contract(text: str) -> None:
    for key in EXPECTED_KEYS:
        if key not in text:
            raise AssertionError(f"Missing contract key: {key}")

def assert_no_forbidden_phrase(text: str) -> None:
    forbidden = ["I guess", "maybe", "not sure"]
    lowered = text.lower()
    for phrase in forbidden:
        if phrase in lowered:
            raise AssertionError(f"Forbidden uncertainty phrase found: {phrase}")
```

프롬프트 엔지니어링이 감각의 영역으로만 남지 않으려면, 이런 작고 단단한 계약 검증이 필요합니다.

### OpenAI/Anthropic에서 역할 맵핑할 때의 주의점

역할 이름은 비슷하지만 SDK 표면이 다릅니다. OpenAI는 `responses`/`chat.completions` 경로가 공존하고, Anthropic은 `messages` 경로가 중심입니다. 따라서 팀 공통 인터페이스를 두고 역할을 내부 표준으로 먼저 고정하는 편이 좋습니다.

```python
def normalize_messages(system_text: str, history: list[dict[str, str]], user_text: str):
    return [{"role": "system", "content": system_text}, *history, {"role": "user", "content": user_text}]
```

공급자 교체 시 가장 자주 깨지는 부분은 모델 성능이 아니라 메시지 직렬화 계층입니다. 시작 단계에서 이 계층을 분리해 두면 이후 확장이 훨씬 단순해집니다.

## 운영 체크리스트

- [ ] `system`에는 공통 정책, `user`에는 현재 요청, `assistant`에는 재주입할 이력을 둡니다.
- [ ] 같은 질문을 system 유무로 비교해 출력 차이를 직접 확인했습니다.
- [ ] 재사용되는 system 프롬프트는 상수나 설정 파일로 분리했습니다.
- [ ] 멀티턴 테스트에서 `assistant` 메시지를 명시적으로 다시 넣는지 검증합니다.
- [ ] 형식 요구사항은 모호한 형용사 대신 문단 수, 불릿 수, 키 구조로 적습니다.

## 정리

프롬프트 엔지니어링의 출발점은 화려한 문장이 아닙니다. 역할이 분리된 메시지 배열입니다. `system`은 정책을 고정하고, `user`는 현재 요청을 담고, `assistant`는 다음 턴에 필요한 이력을 되살립니다. 이 기본 구조를 잡아야 같은 모델에서도 더 예측 가능한 동작을 만들 수 있습니다.

이 글에서 기억할 핵심은 세 가지입니다. 공통 규칙은 `system`으로 올리고, 멀티턴 기억은 애플리케이션이 재구성하고, 파라미터 조정은 프롬프트 구조와 함께 읽어야 합니다. 이 세 가지가 분리되면 “왜 답이 흔들렸는가”를 훨씬 쉽게 설명할 수 있습니다.

실무에서는 여기에 한 가지를 더 붙이면 안정성이 크게 좋아집니다. 프롬프트를 코드와 같은 변경 자산으로 취급하고, 템플릿 버전과 회귀 테스트를 운영 절차에 포함하는 것입니다. 같은 모델에서도 결과가 달라지는 이유를 추적할 수 있어야 시스템이 장기적으로 유지됩니다.

프롬프트가 길어질수록 품질이 좋아진다는 보장은 없습니다. 길이보다 구조와 계약이 명확한 프롬프트가 결과를 더 안정적으로 만듭니다.

운영에서는 이 원칙이 비용 절감과 장애 감소로 바로 연결됩니다.
짧고 선명한 구조가 유리합니다.

다음 글에서는 few-shot과 chain-of-thought를 다룹니다. 이번 글이 역할의 분리였다면, 다음 글은 그 위에 예시와 단계적 추론을 얹어 응답 패턴을 더 강하게 유도하는 단계입니다.

## 처음 질문으로 돌아가기

- system, user, assistant 역할은 각각 어떤 책임을 맡을까요?
  - `system`은 공통 정책과 역할, `user`는 현재 요청, `assistant`는 이전 응답 이력을 맡습니다.

- system message는 왜 단순한 첫 문장보다 강한 기준이 될까요?
  - system message는 매 요청에서 모델이 먼저 따라야 할 상위 지침으로 들어가므로, user message 안의 일반 문장보다 안정적인 기준이 됩니다.

- temperature, top_p, few-shot은 답변 안정성에 어떤 영향을 줄까요?
  - temperature와 top_p는 샘플링의 흔들림을 조절하고, few-shot은 원하는 답변 모양을 예시로 고정해 안정성을 높입니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM App Foundations 101 (1/6): LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기](./01-llm-api-first-call.md)
- [LLM App Foundations 101 (2/6): 토큰 이해하기 — 비용, 한계, 컨텍스트 창](./02-understanding-tokens.md)
- **LLM App Foundations 101 (3/6): 프롬프트 엔지니어링 기초 — System·User·Assistant 역할 (현재 글)**
- LLM App Foundations 101 (4/6): Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기 (예정)
- LLM App Foundations 101 (5/6): 대화 상태 관리 — 멀티턴 챗봇 만들기 (예정)
- LLM App Foundations 101 (6/6): 스트리밍 응답 처리 — 실시간으로 출력 받기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Groq Docs: Text chat](https://console.groq.com/docs/text-chat)
- [Groq Python SDK](https://github.com/groq/groq-python)
- [OpenAI Platform Docs: Messages and roles](https://platform.openai.com/docs/guides/text)
- [Anthropic Docs: Prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)

### 관련 시리즈

- [Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기](./04-few-shot-and-cot.md)
- [대화 상태 관리 — 멀티턴 챗봇 만들기](./05-conversation-state.md)
- [툴 호출 — 함수를 모델에 연결하기](../../llm-api-production-101/ko/02-tool-calling.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-app-foundations-101/ko/03-prompt-engineering-basics)

Tags: LLM, OpenAI, Prompt Engineering, Python
