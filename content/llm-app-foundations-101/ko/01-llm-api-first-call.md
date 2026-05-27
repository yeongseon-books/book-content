---
title: "LLM App Foundations 101 (1/6): LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기"
series: llm-app-foundations-101
episode: 1
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

# LLM App Foundations 101 (1/6): LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기

LLM 애플리케이션을 처음 만들 때 가장 먼저 흐려지는 지점은 모델 성능이 아닙니다. 내 코드와 모델 서비스 사이에 어떤 계약이 있는지, 그 계약이 어디서 실패하는지, 응답에서 무엇을 읽어야 하는지가 더 먼저 헷갈립니다. 채팅 UI는 이 경계를 감추지만, 런타임에서는 결국 HTTP 요청 하나와 JSON 응답 하나가 전부입니다.

이 글은 LLM 앱 기초 시리즈의 첫 번째 글입니다.

이 구조를 초기에 정확히 잡아 두면 이후 주제들이 훨씬 또렷해집니다. 토큰 비용을 읽는 일도, 프롬프트 구조를 설계하는 일도, 스트리밍을 붙이는 일도 모두 첫 호출의 요청-응답 구조 위에 쌓입니다. 반대로 이 지점이 흐리면 이후의 기능은 전부 “뭔가 되긴 되는데 왜 그런지 모르겠다”는 상태로 남습니다.

특히 입문 단계에서는 프롬프트를 얼마나 영리하게 쓰느냐보다, 어떤 필드가 요청 본문에 들어가고 어떤 필드가 응답으로 돌아오는지부터 익히는 편이 좋습니다. 모델은 원격 서비스이고, 원격 서비스는 항상 명시적 계약과 실패 모드를 갖습니다. 이 감각이 있어야 이후 단계에서 문제를 추측이 아니라 로그와 구조로 설명할 수 있습니다.

여기서는 Groq Python SDK로 가장 작은 성공 경로를 만들고, 첫 호출을 운영 가능한 멘탈 모델로 바꾸겠습니다.

![첫 번째 LLM API 호출의 최소 왕복 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-01-llm-api-first-call-sending-your-first-re.ko.png)
*첫 번째 LLM API 호출의 최소 왕복 구조*

## 먼저 던지는 질문

- LLM API 호출은 SDK 아래에서 어떤 요청-응답 구조로 움직일까요?
- API 키와 모델 ID, 메시지 형식 중 첫 실패에서 어디부터 봐야 할까요?
- 응답에서 본문, 사용량, 모델명을 어떻게 읽어야 할까요?

## 왜 이 글이 중요한가

첫 호출은 단순한 입문 예제가 아닙니다. 이후 모든 기능의 기준점입니다. 토큰 사용량을 읽는 위치, 응답 본문을 꺼내는 위치, 모델명을 기록하는 위치가 여기서 정해집니다. 이 단계에서 구조를 대충 넘기면 나중에 비용 분석과 장애 분석도 함께 흐려집니다.

LLM을 “똑똑한 객체 하나”로 보면 문제를 잘못 찾기 쉽습니다. 실제로는 네트워크 요청, 인증 헤더, JSON 직렬화, 모델 선택, 응답 파싱이 얽힌 원격 호출입니다. 따라서 첫 호출을 이해하려면 모델 자체보다 서비스 경계를 먼저 봐야 합니다.

현업에서는 이 차이가 바로 드러납니다. `401`이면 프롬프트가 아니라 인증을 봐야 하고, `429`면 문장 표현보다 호출 빈도를 먼저 봐야 합니다. 첫 호출을 투명하게 보는 습관이 생기면, 이후의 LLM 개발은 훨씬 덜 신비롭고 훨씬 더 다루기 쉬워집니다.

## 첫 호출을 이해하는 가장 좋은 방법: SDK 메서드가 아니라 JSON 요청과 JSON 응답의 왕복으로 보는 것입니다

Groq SDK는 편리하지만, 실제 계약을 바꾸지는 않습니다. `client.chat.completions.create()`는 결국 JSON 요청을 만들고 JSON 응답을 Python 객체로 감싼 결과를 돌려줍니다. 그래서 첫 호출을 이해할 때는 “메서드를 어떻게 부르느냐”보다 “어떤 필드를 보내고 어떤 필드를 받느냐”를 먼저 보는 편이 정확합니다.

이 관점이 중요한 이유는 SDK 문법은 바뀌어도 기본 계약은 쉽게 바뀌지 않기 때문입니다. 모델 ID를 보내고, 메시지 배열을 보내고, 응답에서 생성 텍스트와 사용량과 메타데이터를 읽는 구조는 이후 스트리밍과 툴 호출로 가도 그대로 이어집니다.

> LLM 첫 호출의 핵심은 모델을 부르는 문법이 아니라, 원격 서비스와 맺는 입력·출력 계약을 눈에 보이는 구조로 이해하는 데 있습니다.

## 핵심 개념

가장 먼저 기억할 문장은 단순합니다. LLM API도 결국 API입니다. 애플리케이션은 모델과 직접 대화하는 것이 아니라, 모델 서비스를 호출합니다. 따라서 요청에는 모델과 입력 메시지가 들어가고, 응답에는 생성 텍스트와 사용량 같은 메타데이터가 들어옵니다.

![텍스트 입력과 JSON 응답으로 이어지는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-01-what-an-llm-api-is.ko.png)

*텍스트 입력과 JSON 응답으로 이어지는 흐름*

개념적으로 요청 본문은 아래처럼 생깁니다.

```json
{
  "model": "llama-3.1-8b-instant",
  "messages": [
    {
      "role": "user",
      "content": "Show me a small Python example that reads an environment variable."
    }
  ]
}
```

응답에서 처음 봐야 할 세 블록은 `model`, `choices`, `usage`입니다.

```json
{
  "model": "llama-3.1-8b-instant",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "import os\nprint(os.environ['HOME'])"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 24,
    "completion_tokens": 31,
    "total_tokens": 55
  }
}
```

실제 준비 단계는 길지 않습니다. 계정을 만들고, 키를 발급하고, 환경변수에 넣고, SDK를 설치하면 됩니다. 중요한 습관은 키를 코드에 박아 넣지 않는 것입니다.

```bash
export GROQ_API_KEY="your-issued-key"
```

```python
import os

api_key = os.environ["GROQ_API_KEY"]
print(f"API key loaded: {api_key[:6]}...")
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install groq
```

![클라이언트 생성부터 첫 호출까지 이어지는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-02-sending-your-first-request.ko.png)

*클라이언트 생성부터 첫 호출까지 이어지는 흐름*

가장 작은 성공 경로는 아래 코드입니다. 이 블록 하나로 “요청을 보냈고, 답이 돌아왔고, 본문을 읽었다”는 첫 번째 이정표를 확인할 수 있습니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain Python list comprehensions in one paragraph.",
        }
    ],
)

print(completion.choices[0].message.content)
```

이제 본문만 보지 말고 응답 객체 전체를 읽어야 합니다. 그래야 모델명, 토큰 사용량, 종료 이유까지 함께 추적할 수 있습니다.

![응답 객체에서 본문과 메타데이터를 읽는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-03-inspecting-the-response-object.ko.png)

*응답 객체에서 본문과 메타데이터를 읽는 구조*

```python
import json
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain the difference between an HTTP API and an SDK in three sentences.",
        }
    ],
)

print(json.dumps(completion.to_dict(), indent=2, ensure_ascii=False))
```

실전에서 최소한 기록할 값은 생성 텍스트, `usage`, 모델명, `finish_reason`입니다. 이 네 값만 있어도 비용과 잘림 문제를 설명할 재료가 생깁니다.

![인증 오류, 속도 제한, 재시도 분기로 이어지는 HTTP 경계](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-04-why-the-http-mental-model-still-matters.ko.png)

*인증 오류, 속도 제한, 재시도 분기로 이어지는 HTTP 경계*

SDK를 쓰더라도 네트워크 경계는 사라지지 않습니다. 느린 응답은 네트워크와 토큰 길이 문제일 수 있고, `401`은 인증 문제일 수 있으며, `429`는 속도 제한 문제일 수 있습니다. 그래서 첫 호출을 이해할 때는 프롬프트보다 경계 조건을 먼저 읽는 습관이 중요합니다.

![동기 대기와 비동기 병렬 실행의 차이](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-05-synchronous-and-asynchronous-patterns.ko.png)

*동기 대기와 비동기 병렬 실행의 차이*

동기 호출은 입문용으로 가장 단순합니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain asynchronous programming in one paragraph.",
        }
    ],
)

print(completion.choices[0].message.content)
```

애플리케이션이 이미 async 런타임 위에 있거나 여러 I/O 작업을 함께 다뤄야 하면 비동기 호출이 자연스럽습니다.

```python
import asyncio
import os

from groq import AsyncGroq

client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

async def main() -> None:
    completion = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": "Give me two situations where asyncio is useful.",
            }
        ],
    )

    print(completion.choices[0].message.content)

asyncio.run(main())
```

여러 요청을 동시에 다루는 구조는 이후 `asyncio.gather()` 같은 병렬 패턴으로 확장됩니다. 이 글에서는 첫 성공 경로와 구조 이해가 우선이므로, 마지막으로 기준점이 되는 완성 예제 하나만 남기겠습니다.

```python
import os

from groq import Groq

def main() -> None:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a concise Python tutor.",
            },
            {
                "role": "user",
                "content": (
                    "Explain the difference between a Python function and a method "
                    "in no more than five sentences, and add one short example line."
                ),
            },
        ],
    )

    content = completion.choices[0].message.content or ""
    usage = completion.usage

    print("=== answer ===")
    print(content)
    print()
    print("=== metadata ===")
    print(f"model: {completion.model}")
    print(f"prompt_tokens: {usage.prompt_tokens}")
    print(f"completion_tokens: {usage.completion_tokens}")
    print(f"total_tokens: {usage.total_tokens}")

if __name__ == "__main__":
    main()
```

## 흔히 헷갈리는 지점

- SDK를 쓰면 HTTP 경계가 사라진다고 생각하기 쉽지만, 인증·속도 제한·네트워크 지연은 그대로 남습니다.
- `choices[0].message.content`만 읽으면 충분하다고 느끼기 쉽지만, 실제 운영에서는 `usage`, `model`, `finish_reason`도 함께 봐야 합니다.
- 비동기 호출은 더 고급 기능처럼 보이지만, 본질은 여러 I/O를 동시에 기다리는 구조 선택입니다. 품질 자체를 올려 주는 기능은 아닙니다.
- 첫 호출 실패를 프롬프트 문제로 오해하기 쉽지만, 입문 단계에서는 인증 키 누락, 잘못된 모델 ID, 메시지 형식 오류가 더 흔합니다.

## 공급자별 첫 호출 비교와 실패 패턴

첫 호출 단계에서는 SDK 문법보다 요청 계약의 공통점과 차이를 같이 보는 편이 좋습니다. 같은 채팅 API라도 공급자마다 필드 이름과 응답 껍데기가 조금씩 다르기 때문입니다. 이 차이를 모르고 복사-붙여넣기하면 `400`이나 파싱 오류가 생깁니다.

OpenAI Python SDK 기준 최소 호출은 아래처럼 생깁니다.

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Python에서 list와 tuple 차이를 세 문장으로 설명하세요.",
)

print(response.output_text)
```

Anthropic Python SDK 기준 최소 호출은 아래처럼 생깁니다.

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-3-5-haiku-latest",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "Python list와 tuple 차이를 세 문장으로 설명하세요."}
    ],
)

print(message.content[0].text)
```

핵심은 모델을 바꾸는 일이 아니라, 응답 본문을 꺼내는 위치를 고정하는 일입니다. OpenAI는 `output_text` 또는 블록 기반 응답을, Anthropic은 `content` 배열을 자주 사용합니다. 팀 코드에서 `extract_text(response)` 같은 공통 함수를 먼저 두면 공급자를 바꿔도 상위 로직은 거의 바꾸지 않아도 됩니다.

```python
def extract_text(provider: str, payload) -> str:
    if provider == "groq":
        return payload.choices[0].message.content or ""
    if provider == "openai":
        return getattr(payload, "output_text", "") or ""
    if provider == "anthropic":
        blocks = getattr(payload, "content", [])
        return "".join(getattr(block, "text", "") for block in blocks)
    raise ValueError(f"Unsupported provider: {provider}")
```

### 첫 호출 단계에서 바로 넣어야 하는 로그 필드

입문 코드에서도 아래 필드는 즉시 남기는 편이 좋습니다. 이 값들이 있어야 토큰·비용·장애를 나중에 연결할 수 있습니다.

| 필드 | 의미 | 누락 시 문제 |
|---|---|---|
| `provider` | 호출한 공급자 식별 | 장애 구간 분리가 어려움 |
| `model` | 실제 응답 모델명 | 모델 교체 회귀 추적 불가 |
| `request_id` | 공급자 요청 식별자 | 지원 문의·추적이 어려움 |
| `latency_ms` | 응답 시간 | 느림 원인 추정만 하게 됨 |
| `prompt_tokens`/`completion_tokens` | 사용량 | 비용 분석이 불가능 |
| `finish_reason` | 종료 이유 | 길이 잘림 탐지가 늦어짐 |

아래처럼 최소 로깅 함수를 두면 충분합니다.

```python
import time

def call_and_log(client, model: str, messages: list[dict[str, str]]) -> str:
    started = time.perf_counter()
    completion = client.chat.completions.create(model=model, messages=messages)
    latency_ms = (time.perf_counter() - started) * 1000

    choice = completion.choices[0]
    usage = completion.usage
    print(
        {
            "provider": "groq",
            "model": completion.model,
            "latency_ms": round(latency_ms, 1),
            "finish_reason": choice.finish_reason,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
        }
    )
    return choice.message.content or ""
```

### 401, 429, 5xx를 다루는 기본 재시도 틀

첫 호출 예제에서 가장 빠르게 운영 감각을 얻는 방법은 오류 분기를 명시하는 것입니다. `401`은 재시도로 해결되지 않고, `429`와 일부 `5xx`는 backoff 재시도가 유효합니다.

```python
import random
import time

def call_with_retry(create_fn, max_attempts: int = 4):
    for attempt in range(1, max_attempts + 1):
        try:
            return create_fn()
        except Exception as exc:  # SDK별 예외 타입으로 좁히면 더 좋습니다.
            msg = str(exc)
            if "401" in msg or "403" in msg:
                raise
            if ("429" in msg or "500" in msg or "503" in msg) and attempt < max_attempts:
                sleep_s = (2 ** (attempt - 1)) + random.random() * 0.2
                time.sleep(sleep_s)
                continue
            raise
```

이 단계에서 중요한 것은 완벽한 에러 프레임워크가 아닙니다. 어떤 오류는 즉시 실패해야 하고, 어떤 오류는 천천히 다시 시도해야 하는지 경계를 분명히 두는 것입니다.

### 호출 단가를 처음부터 숫자로 보는 습관

요청 하나의 비용을 대략 계산해 보는 습관을 초기에 들이면, 이후 프롬프트 설계가 훨씬 현실적으로 바뀝니다.

| 시나리오 | prompt_tokens | completion_tokens | 단가 가정(USD / 1M) | 1회 호출 추정 비용 |
|---|---:|---:|---|---:|
| 짧은 Q&A | 180 | 120 | 입력 0.20 / 출력 0.60 | 0.000108 |
| 중간 설명 | 850 | 400 | 입력 0.20 / 출력 0.60 | 0.000410 |
| 긴 분석 | 2200 | 900 | 입력 0.20 / 출력 0.60 | 0.000980 |

```python
def estimate_cost_usd(
    prompt_tokens: int,
    completion_tokens: int,
    in_price_per_m: float,
    out_price_per_m: float,
) -> float:
    return (prompt_tokens / 1_000_000) * in_price_per_m + (
        completion_tokens / 1_000_000
    ) * out_price_per_m
```

요금은 공급자와 모델 버전에 따라 바뀌므로, 숫자 자체보다 계산 습관이 더 중요합니다. 한 번 이 함수를 연결해 두면 “좋은 답”과 “지속 가능한 답”을 같은 화면에서 볼 수 있습니다.

## 운영 체크리스트

- [ ] 첫 호출 성공 직후 OpenAI/Anthropic 보조 호출을 한 번 더 실행해 응답 파싱 위치 차이를 확인했습니다.
- [ ] `401`, `429`, `5xx`를 같은 오류로 취급하지 않고 분기별 대응(즉시 실패/재시도)을 코드에 명시했습니다.
- [ ] 호출 로그에 `model`, `finish_reason`, `latency_ms`, `total_tokens`를 공통 필드로 남깁니다.
- [ ] 요청 단가 계산 함수를 넣고, 최소 3개 시나리오(짧은/중간/긴 요청) 비용을 숫자로 검증했습니다.
- [ ] `GROQ_API_KEY`를 환경변수로 주입했고 소스코드에 키 문자열을 넣지 않았습니다.
- [ ] `pip install groq` 이후 `import groq`가 정상 동작합니다.
- [ ] `client.chat.completions.create(model=..., messages=[...])` 호출이 정상 응답을 반환합니다.
- [ ] 응답에서 `choices[0].message.content`, `usage.total_tokens`, `model`을 함께 기록합니다.
- [ ] 같은 호출을 동기와 비동기 방식으로 각각 한 번씩 실행해 차이를 확인했습니다.

## 첫 호출 이후 바로 붙일 실전 안전장치

첫 호출이 성공하면 많은 팀이 곧바로 프롬프트 실험으로 넘어갑니다. 그런데 운영 관점에서는 이 시점에 안전장치를 먼저 넣는 편이 더 이득입니다. 특히 요청 ID 추적, 멱등 키, 타임아웃 상한은 초기에 넣을수록 나중 비용이 크게 줄어듭니다.

```python
import os
import uuid
from typing import Any

from groq import Groq

def create_completion_with_request_context(client: Groq, messages: list[dict[str, str]]) -> Any:
    request_id = str(uuid.uuid4())
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        timeout=20.0,
    )
    print({"request_id": request_id, "model": completion.model})
    return completion

client = Groq(api_key=os.environ["GROQ_API_KEY"])
result = create_completion_with_request_context(
    client,
    [{"role": "user", "content": "Python 예외 처리의 핵심 원칙을 세 문장으로 정리하세요."}],
)
print(result.choices[0].message.content)
```

핵심은 복잡한 프레임워크가 아닙니다. "이 호출을 나중에 다시 찾아올 수 있는가"를 보장하는 최소 장치를 지금 넣는 것입니다. 이 한 단계만으로도 장애 대응 속도가 크게 달라집니다.

## 정리

첫 번째 LLM API 호출은 작아 보여도 이미 핵심 구조를 다 담고 있습니다. 환경변수에서 키를 읽고, 클라이언트를 만들고, 모델과 메시지를 보내고, 응답에서 본문과 메타데이터를 읽습니다. 이후의 모든 기능은 이 루프를 더 정교하게 다루는 과정에 가깝습니다.

이 글에서 꼭 가져가야 할 감각은 세 가지입니다. 첫째, SDK는 편의 계층일 뿐이고 기본 계약은 여전히 JSON 요청과 JSON 응답입니다. 둘째, 본문만 보지 말고 토큰 사용량과 모델명과 종료 이유까지 함께 읽어야 운영 감각이 생깁니다. 셋째, 동기와 비동기는 품질 문제가 아니라 애플리케이션 구조 문제입니다.

다음 글에서는 같은 호출을 유지한 채 토큰을 중심에 놓고 보겠습니다. 길이 제한, 비용, 지연 시간은 결국 토큰 예산 문제로 수렴합니다. 첫 호출의 구조를 이해했다면, 이제 그 구조를 숫자로 읽을 차례입니다.

## 처음 질문으로 돌아가기

- LLM API 호출은 SDK 아래에서 어떤 요청-응답 구조로 움직일까요?
  - SDK 메서드처럼 보이지만 실제로는 모델 ID와 메시지 배열을 담은 JSON 요청을 보내고, 생성 텍스트와 사용량이 담긴 JSON 응답을 받는 구조입니다.

- API 키와 모델 ID, 메시지 형식 중 첫 실패에서 어디부터 봐야 할까요?
  - 먼저 인증과 API 키 위치를 확인하고, 그다음 모델 ID와 메시지 배열 형식을 좁혀 가는 편이 안전합니다.

- 응답에서 본문, 사용량, 모델명을 어떻게 읽어야 할까요?
  - `choices[0].message.content`에서 본문을 읽고, `usage`에서 토큰 사용량을 읽고, `model`에서 실제 응답 모델을 기록합니다.

<!-- toc:begin -->
## 시리즈 목차

- **LLM App Foundations 101 (1/6): LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기 (현재 글)**
- LLM App Foundations 101 (2/6): 토큰 이해하기 — 비용, 한계, 컨텍스트 창 (예정)
- LLM App Foundations 101 (3/6): 프롬프트 엔지니어링 기초 — System·User·Assistant 역할 (예정)
- LLM App Foundations 101 (4/6): Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기 (예정)
- LLM App Foundations 101 (5/6): 대화 상태 관리 — 멀티턴 챗봇 만들기 (예정)
- LLM App Foundations 101 (6/6): 스트리밍 응답 처리 — 실시간으로 출력 받기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Groq quickstart](https://console.groq.com/docs/quickstart)
- [Groq Python SDK](https://github.com/groq/groq-python)
- [Groq API reference](https://console.groq.com/docs/api-reference)
- [Groq models](https://console.groq.com/docs/models)

### 관련 시리즈

- [토큰 이해하기 — 비용, 한계, 컨텍스트 창](./02-understanding-tokens.md)
- [프롬프트 엔지니어링 기초 — System·User·Assistant 역할](./03-prompt-engineering-basics.md)
- [LLM API Production 101](../../llm-api-production-101/ko/01-structured-output.md) — 이 시리즈가 끝나는 지점, 즉 첫 호출·토큰·기본 프롬프트 다음 단계를 다룹니다. 구조화 출력, 툴 호출, 스트리밍, 재시도처럼 production 환경에서 부딪히는 문제로 넘어갈 때 권장합니다.

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-app-foundations-101/ko/01-llm-api-first-call)

Tags: LLM, OpenAI, Prompt Engineering, Python
