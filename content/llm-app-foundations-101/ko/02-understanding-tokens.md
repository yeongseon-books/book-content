---
title: "LLM App Foundations 101 (2/6): 토큰 이해하기 — 비용, 한계, 컨텍스트 창"
series: llm-app-foundations-101
episode: 2
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

# LLM App Foundations 101 (2/6): 토큰 이해하기 — 비용, 한계, 컨텍스트 창

LLM API를 처음 연결하면 대개 답변 품질에 먼저 눈이 갑니다. 하지만 실제 애플리케이션이 흔들리기 시작하는 지점은 품질보다 예산과 한계인 경우가 많습니다. 프롬프트가 조금 길어졌는데 응답이 느려지고, 이전 대화 몇 턴을 더 붙였더니 비용이 튀고, 참고 문서를 길게 넣자 답변이 중간에서 잘립니다.

이 글은 LLM 앱 기초 시리즈의 2번째 글입니다.

이 현상들은 각각 다른 문제처럼 보이지만, 공통된 단위 하나로 묶입니다. 토큰입니다. 모델은 문장이나 단어가 아니라 토큰 단위로 입력을 읽고 출력을 생성합니다. 따라서 사람 눈에 짧아 보이는 입력이 실제로는 비쌀 수 있고, 코드 블록이나 한국어 문장이 예상보다 빠르게 컨텍스트 창을 잡아먹을 수 있습니다.

운영 관점에서는 이 차이를 빨리 체득해야 합니다. 토큰은 단순한 이론 용어가 아니라 비용 계산 단위이고, 지연 시간의 첫 번째 설명 변수이며, 길이 제한의 경계선입니다. 이 감각이 생기면 “왜 이번 요청이 무거웠는가”를 감이 아니라 숫자로 설명할 수 있습니다.

여기서는 토큰을 문자열의 부속 개념이 아니라 비용·속도·한계를 함께 묶는 운영 단위로 보겠습니다.

![토큰이 비용과 한계로 이어지는 전체 그림](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/02/02-01-understanding-tokens-cost-limits-and-con.ko.png)
*토큰이 비용과 한계로 이어지는 전체 그림*

## 먼저 던지는 질문

- 토큰은 단어가 아니라 왜 예산 단위로 봐야 할까요?
- `prompt_tokens`, `completion_tokens`, `total_tokens`는 각각 어떤 비용을 보여 줄까요?
- context window와 `max_tokens`, `finish_reason`은 어디서 충돌할까요?

## 왜 이 글이 중요한가

LLM 애플리케이션은 문자열을 보내지만 실제로는 토큰 예산 위에서 동작합니다. 따라서 호출 비용을 설명할 때도, 응답 속도를 이해할 때도, 길이 제한을 설계할 때도 결국 토큰으로 되돌아가야 합니다. 이 기준점이 없으면 프롬프트가 길어졌을 때 왜 시스템이 갑자기 무거워졌는지 설명하기 어렵습니다.

또한 토큰 문제는 데모보다 운영에서 더 빨리 드러납니다. 한두 번의 단발 호출에서는 티가 잘 나지 않지만, 대화 이력이 쌓이고 문서 검색 결과가 붙고 응답 길이 제어가 느슨해지면 토큰이 비용과 지연을 함께 밀어 올립니다. 그래서 토큰을 일찍 이해하는 편이 나중의 비용 절감보다 더 큰 효과를 냅니다.

무엇보다 토큰은 문제를 숫자로 바꿔 줍니다. “프롬프트가 너무 긴 것 같다”가 아니라 `prompt_tokens=3050`이라고 말할 수 있고, “답이 잘린 것 같다”가 아니라 `finish_reason=length`라고 말할 수 있습니다. 이 차이가 바로 운영 감각입니다.

## 토큰을 이해하는 가장 좋은 방법: 텍스트 조각이 아니라 모델이 쓰는 예산 단위로 보는 것입니다

사람은 문장과 단어를 읽지만 모델은 그렇지 않습니다. 모델은 자신이 학습한 토크나이저 규칙에 따라 텍스트를 더 작은 조각으로 나누고, 그 조각 수를 기준으로 입력을 처리하고 출력을 생성합니다. 따라서 토큰은 “텍스트를 어떻게 쪼개는가”의 문제이면서 동시에 “얼마나 많은 예산을 쓰는가”의 문제이기도 합니다.

이 시각으로 보면 비용, 지연, 길이 제한이 하나로 연결됩니다. 입력이 길면 읽을 토큰이 늘고, 출력이 길면 생성할 토큰이 늘며, 두 값을 합친 총량이 컨텍스트 창을 밀어붙입니다. 토큰은 내부 구현 디테일이 아니라 시스템 행동을 설명하는 공통 언어입니다.

> 토큰을 단어의 대체 개념으로 보면 계속 놀라고, 모델이 사용하는 예산 단위로 보면 비용과 한계가 한 번에 읽히기 시작합니다.

## 핵심 개념

토큰은 모델 관점의 텍스트 조각입니다. 이 조각은 단어와 일대일로 대응하지 않습니다. 흔한 영어 조합은 큰 덩어리로 묶일 수 있고, 드문 표현은 더 잘게 쪼개질 수 있습니다. 한국어, 코드, 숫자, 공백, 줄바꿈도 모두 토큰 계산에 들어갑니다.

![텍스트가 모델 토큰 조각으로 분해되는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/02/02-01-what-a-token-actually-is.ko.png)

*텍스트가 모델 토큰 조각으로 분해되는 흐름*

예를 들어 아래 세 입력은 사람 눈에는 비슷해 보여도 토큰 수는 크게 다를 수 있습니다.

- `hello world`
- `unbelievable`
- `print(user_profile[0]["email"])`

이 차이의 배경에는 BPE(Byte Pair Encoding) 같은 토크나이징 원리가 있습니다. 이론을 깊게 파고들 필요는 없지만, 실무적으로는 하나만 기억하면 충분합니다. 단어 수는 토큰 수의 좋은 대리 지표가 아닙니다.

![비슷해 보이지만 토큰 비용이 다른 입력들](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/02/02-02-why-tokens-matter-so-much.ko.png)

*비슷해 보이지만 토큰 비용이 다른 입력들*

토큰이 중요한 이유는 세 가지입니다. 첫째, 대부분의 LLM API는 입력 토큰과 출력 토큰 기준으로 과금합니다. 둘째, 모델은 토큰 단위로 읽고 생성하므로 입력과 출력이 길수록 지연이 늘기 쉽습니다. 셋째, 모델마다 한 번에 처리할 수 있는 최대 토큰 수, 즉 컨텍스트 창이 있습니다.

운영 규칙으로 줄이면 아래와 같습니다.

- 비용 문제는 대개 토큰 문제입니다.
- 느린 응답도 먼저 토큰 문제로 의심하는 편이 맞습니다.
- 길이 제한 오류는 거의 늘 토큰 예산 관리 실패입니다.

![입력, 출력, 총합을 나누는 usage 필드](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/02/02-03-revisiting-usage-prompt-tokens-completio.ko.png)

*입력, 출력, 총합을 나누는 usage 필드*

실제 호출에서는 `usage`를 숫자로 읽어야 합니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain Python decorators in no more than two paragraphs.",
        }
    ],
)

usage = completion.usage

print(completion.choices[0].message.content)
print()
print(f"finish_reason={completion.choices[0].finish_reason}")
print(f"prompt_tokens={usage.prompt_tokens}")
print(f"completion_tokens={usage.completion_tokens}")
print(f"total_tokens={usage.total_tokens}")
```

`prompt_tokens`는 요청 입력 전체 길이이고, `completion_tokens`는 모델이 생성한 출력 길이이며, `total_tokens`는 둘의 합입니다. 큰 입력에 짧은 출력이 붙으면 프롬프트 비대화 신호일 수 있고, 짧은 입력에 긴 출력이 붙으면 길이 제어가 느슨한 상황일 수 있습니다.

![호출 전에 토큰 길이를 가늠하는 사전 경로](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/02/02-04-estimating-token-count-with-tiktoken.ko.png)

*호출 전에 토큰 길이를 가늠하는 사전 경로*

실제 운영에서는 호출 후 관측만으로는 부족합니다. 보내기 전에 대략적인 크기를 재야 합니다.

```bash
pip install tiktoken
```

```python
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")

text = "Measuring token length before a request makes prompt handling safer."
tokens = encoding.encode(text)

print(tokens)
print(f"token_count={len(tokens)}")
```

메시지 묶음을 대략 추정할 때는 이렇게 볼 수 있습니다.

```python
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")

messages = [
    {"role": "system", "content": "You are a concise Python tutor."},
    {"role": "user", "content": "Explain the difference between a list and a tuple."},
    {"role": "assistant", "content": "Lists are mutable, while tuples are immutable."},
    {"role": "user", "content": "Add one short code example too."},
]

serialized = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
estimated_prompt_tokens = len(encoding.encode(serialized))

print(serialized)
print()
print(f"estimated_prompt_tokens={estimated_prompt_tokens}")
```

여기서 중요한 주의점이 하나 있습니다. `cl100k_base`는 실용적인 추정 도구이지, Groq 청구 기준의 절대 진실은 아닙니다. 최종 회계 값은 공급자가 돌려주는 `usage`가 권위 있는 값입니다.

컨텍스트 창은 입력 한계가 아니라 입력과 출력이 공유하는 예산으로 이해해야 합니다. 실전 식은 아래 한 줄입니다.

`input tokens + output tokens <= context window`

따라서 긴 시스템 프롬프트, 긴 대화 이력, 검색 결과 문서, 긴 답변 요구는 모두 같은 창을 경쟁합니다. 이 때문에 이론상 최대치 바로 아래까지 밀어붙이는 설계는 쉽게 깨집니다. 항상 여유를 남겨야 합니다.

![컨텍스트 초과와 출력 길이 제한을 가르는 분기](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/02/02-05-detecting-long-prompt-problems-with-fini.ko.png)

*컨텍스트 초과와 출력 길이 제한을 가르는 분기*

출력 길이는 `max_tokens`로 제한할 수 있고, 잘림 여부는 `finish_reason`으로 감지합니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain the difference between a Python generator and a list with examples.",
        }
    ],
    max_tokens=80,
)

print(completion.choices[0].message.content)
print()
print(f"completion_tokens={completion.usage.completion_tokens}")
print(f"finish_reason={completion.choices[0].finish_reason}")
```

긴 입력과 작은 출력 상한을 함께 다루는 감시 패턴은 아래처럼 잡을 수 있습니다.

```python
import os

import tiktoken
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])
encoding = tiktoken.get_encoding("cl100k_base")

long_text = " ".join(
    [
        "Explain why a Python web application should keep both request logs and exception logs."
    ]
    * 200
)

instruction = "Read the following text and summarize the key points as 10 bullets."
user_content = instruction + "\n\n" + long_text
estimated_prompt_tokens = len(encoding.encode(user_content))
print(f"estimated_prompt_tokens={estimated_prompt_tokens}")

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": user_content,
        }
    ],
    max_tokens=60,
)

choice = completion.choices[0]

print(choice.message.content)
print()
print(f"prompt_tokens={completion.usage.prompt_tokens}")
print(f"completion_tokens={completion.usage.completion_tokens}")
print(f"total_tokens={completion.usage.total_tokens}")
print(f"finish_reason={choice.finish_reason}")

if choice.finish_reason == "length":
    print("Warning: the response stopped because it hit a length limit.")
```

실무에서는 이 정도 정보만 찍어도 바로 행동 기준이 생깁니다. `estimated_prompt_tokens`와 실제 `prompt_tokens`가 크게 벌어지면 추정 방식이 거칠다는 뜻이고, `finish_reason=length`가 반복되면 입력 축약이나 `max_tokens` 재설계가 먼저입니다. 반대로 입력이 짧은데 `completion_tokens`만 계속 치솟으면 출력 형식 요구가 너무 느슨한 경우가 많습니다.

긴 입력을 다룰 때는 호출 직전 가드 함수를 두는 편이 안전합니다.

```python
def should_compress_prompt(
    estimated_prompt_tokens: int,
    reserved_output_tokens: int,
    context_window: int,
    safety_margin: int = 500,
) -> bool:
    usable_budget = context_window - reserved_output_tokens - safety_margin
    return estimated_prompt_tokens > usable_budget

context_window = 128_000
reserved_output_tokens = 1_000

if should_compress_prompt(
    estimated_prompt_tokens=3_050,
    reserved_output_tokens=reserved_output_tokens,
    context_window=context_window,
):
    print("Compress or trim the prompt before sending it.")
else:
    print("Prompt budget looks safe.")
```

이런 사전 가드는 실패를 막는 데도 유용하지만, 더 중요한 역할은 정책을 고정하는 데 있습니다. 검색 결과를 몇 개까지 붙일지, 대화 이력을 몇 턴까지 유지할지, 출력에 얼마만큼의 여유를 남길지 같은 결정을 코드로 남길 수 있기 때문입니다.

## 흔히 헷갈리는 지점

- 토큰을 단어 수와 비슷하다고 보면 한국어, 코드, 기호가 많은 입력에서 계속 오차가 납니다.
- `tiktoken` 추정치를 청구 기준의 정확한 값으로 오해하기 쉽지만, 최종 기준은 공급자의 `usage`입니다.
- 컨텍스트 창을 입력 전용 한계로 보면 안 됩니다. 출력도 같은 창을 함께 씁니다.
- `max_tokens`를 크게 잡으면 충분하다고 생각하기 쉽지만, 입력이 이미 커지면 실제로 남은 출력 공간은 훨씬 작을 수 있습니다.
- `finish_reason=length`를 가벼운 경고로 넘기기 쉽지만, 실제로는 문장 중간 잘림이나 코드 블록 손실로 이어질 수 있습니다.

## 토큰 예산을 운영 정책으로 바꾸는 방법

토큰을 이해했다면 다음 단계는 수치를 정책으로 고정하는 일입니다. 가장 실용적인 출발점은 요청 타입별 예산표를 만드는 것입니다. “대충 짧게”가 아니라 입력·출력 상한을 명시하면, 팀 내에서 같은 기준으로 프롬프트를 설계할 수 있습니다.

| 요청 타입 | 입력 상한 | 출력 상한 | 안전 마진 | 비고 |
|---|---:|---:|---:|---|
| 일반 Q&A | 2,000 | 600 | 300 | 응답 속도 우선 |
| 문서 요약 | 5,000 | 900 | 500 | 긴 본문 허용 |
| 정책 판정 | 3,500 | 500 | 400 | 형식 안정성 우선 |
| 코드 설명 | 4,500 | 1,000 | 500 | 코드 블록 여유 필요 |

이 표를 코드로 옮기면 호출 전 검증이 쉬워집니다.

```python
from dataclasses import dataclass

@dataclass
class TokenBudget:
    max_prompt: int
    max_output: int
    safety_margin: int

BUDGETS = {
    "qa": TokenBudget(max_prompt=2000, max_output=600, safety_margin=300),
    "summary": TokenBudget(max_prompt=5000, max_output=900, safety_margin=500),
    "policy": TokenBudget(max_prompt=3500, max_output=500, safety_margin=400),
    "code": TokenBudget(max_prompt=4500, max_output=1000, safety_margin=500),
}

def assert_budget_ok(estimated_prompt_tokens: int, use_case: str, context_window: int) -> None:
    budget = BUDGETS[use_case]
    allowed_prompt = context_window - budget.max_output - budget.safety_margin
    if estimated_prompt_tokens > allowed_prompt:
        raise ValueError(
            f"Prompt too long: estimated={estimated_prompt_tokens}, allowed={allowed_prompt}, use_case={use_case}"
        )
```

### 토큰 기반 rate limit 방어

rate limit은 요청 횟수만의 문제가 아닙니다. 많은 공급자가 토큰 속도 제한도 함께 둡니다. 따라서 초당 요청 수(RPS)만 보고 설계하면, 긴 프롬프트 구간에서 `429`가 반복될 수 있습니다.

```python
import time

class TokenRateLimiter:
    def __init__(self, tokens_per_minute: int):
        self.tokens_per_minute = tokens_per_minute
        self.window_started = time.time()
        self.used_tokens = 0

    def consume(self, estimated_tokens: int) -> None:
        now = time.time()
        if now - self.window_started >= 60:
            self.window_started = now
            self.used_tokens = 0

        if self.used_tokens + estimated_tokens > self.tokens_per_minute:
            sleep_s = 60 - (now - self.window_started)
            if sleep_s > 0:
                time.sleep(sleep_s)
            self.window_started = time.time()
            self.used_tokens = 0

        self.used_tokens += estimated_tokens
```

이 제한기는 거칠지만 효과가 분명합니다. 토큰이 큰 요청이 몰릴 때도 공급자 제한보다 먼저 속도를 줄이므로 `429` 폭주를 줄일 수 있습니다.

### 월 비용을 빠르게 추정하는 테이블

운영 의사결정에서는 호출 단가보다 월 총량이 중요합니다. 아래처럼 보수적으로 계산해 두면, 기능 추가 전에 예산 충격을 빠르게 확인할 수 있습니다.

| 일 호출 수 | 평균 총 토큰 | 월 총 토큰(30일) | 단가 가정(USD / 1M) | 월 비용 추정 |
|---:|---:|---:|---|---:|
| 5,000 | 900 | 135,000,000 | 0.35 | 47.25 |
| 20,000 | 1,200 | 720,000,000 | 0.35 | 252.00 |
| 50,000 | 1,600 | 2,400,000,000 | 0.35 | 840.00 |

토큰 비용은 모델 교체와 프롬프트 길이 변화에 민감합니다. 그래서 비용 회고를 할 때는 “요금표가 바뀌었다”보다 “평균 `prompt_tokens`가 얼마나 늘었는가”를 먼저 보는 편이 정확합니다.

## 운영 체크리스트

- [ ] 실제 호출에서 `prompt_tokens`, `completion_tokens`, `total_tokens`를 모두 기록합니다.
- [ ] 호출 전에 `tiktoken` 또는 동등한 방식으로 입력 길이를 대략 추정합니다.
- [ ] 사용 중인 모델의 컨텍스트 창 한계를 공식 문서에서 확인했습니다.
- [ ] `max_tokens`를 기본값으로 방치하지 않고 출력 길이 정책으로 명시합니다.
- [ ] `finish_reason`를 로그에 남기고 `length` 발생 시 후속 조치를 정의했습니다.

## 정리

토큰은 LLM 시스템에서 문장보다 더 중요한 단위입니다. 모델은 토큰으로 읽고, 토큰으로 생성하고, 공급자는 토큰으로 과금하며, 컨텍스트 창도 토큰으로 제한됩니다. 따라서 비용과 속도와 한계를 하나의 언어로 설명하려면 토큰 중심의 멘탈 모델이 필요합니다.

이 글에서 가져가야 할 실전 감각은 분명합니다. 호출 후에는 `usage`를 읽고, 호출 전에는 `tiktoken`으로 대략적 길이를 추정하고, 출력 길이는 `max_tokens`, 잘림 여부는 `finish_reason`로 감시해야 합니다. 이 네 축이 모이면 길이 관련 문제는 훨씬 덜 신비로워집니다.

추가로 기억할 점이 하나 더 있습니다. 토큰 최적화는 모델 품질을 낮추는 절약 기술이 아니라, 같은 예산에서 더 안정적인 결과를 얻기 위한 설계 기술입니다. 불필요한 반복 문장을 줄이고, 이력을 선택적으로 압축하고, 출력 형식을 명시하면 품질과 비용을 동시에 개선할 수 있습니다.

다음 글에서는 같은 채팅 API 위에서 역할 기반 프롬프트 설계를 다룹니다. 토큰 예산을 읽을 수 있게 되었다면, 이제 같은 모델에서 더 안정적인 행동을 끌어내는 입력 구조를 설계할 차례입니다.

## 처음 질문으로 돌아가기

- 토큰은 단어가 아니라 왜 예산 단위로 봐야 할까요?
  - 모델은 글자나 단어가 아니라 토큰 단위로 입력과 출력을 처리하고, 대부분의 비용과 한계도 이 단위로 계산되기 때문입니다.

- `prompt_tokens`, `completion_tokens`, `total_tokens`는 각각 어떤 비용을 보여 줄까요?
  - `prompt_tokens`는 보낸 입력 비용, `completion_tokens`는 생성된 출력 비용, `total_tokens`는 한 호출의 전체 예산을 보여 줍니다.

- context window와 `max_tokens`, `finish_reason`은 어디서 충돌할까요?
  - 입력과 출력이 함께 context window를 차지합니다. `max_tokens`를 크게 잡아도 남은 창이 부족하면 `finish_reason`으로 길이 문제를 확인해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM App Foundations 101 (1/6): LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기](./01-llm-api-first-call.md)
- **LLM App Foundations 101 (2/6): 토큰 이해하기 — 비용, 한계, 컨텍스트 창 (현재 글)**
- LLM App Foundations 101 (3/6): 프롬프트 엔지니어링 기초 — System·User·Assistant 역할 (예정)
- LLM App Foundations 101 (4/6): Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기 (예정)
- LLM App Foundations 101 (5/6): 대화 상태 관리 — 멀티턴 챗봇 만들기 (예정)
- LLM App Foundations 101 (6/6): 스트리밍 응답 처리 — 실시간으로 출력 받기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Groq API reference](https://console.groq.com/docs/api-reference)
- [Groq models](https://console.groq.com/docs/models)
- [Groq Python SDK](https://github.com/groq/groq-python)
- [tiktoken GitHub repository](https://github.com/openai/tiktoken)
- [OpenAI tokenizer](https://platform.openai.com/tokenizer)

### 관련 시리즈

- [LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기](./01-llm-api-first-call.md)
- [프롬프트 엔지니어링 기초 — System·User·Assistant 역할](./03-prompt-engineering-basics.md)
- [캐싱 전략 — 비용과 지연 시간 줄이기](../../llm-api-production-101/ko/04-caching-strategies.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-app-foundations-101/ko/02-understanding-tokens)

Tags: LLM, OpenAI, Prompt Engineering, Python
