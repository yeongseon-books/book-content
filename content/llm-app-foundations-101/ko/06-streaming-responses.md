---
title: 스트리밍 응답 처리 — 실시간으로 출력 받기
series: llm-app-foundations-101
episode: 6
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

# 스트리밍 응답 처리 — 실시간으로 출력 받기

> LLM 앱 기초 시리즈 (6/6)

예제 코드: [github.com/yeongseon-books/llm-app-foundations-101](https://github.com/yeongseon-books/llm-app-foundations-101/tree/main/ko/06-streaming-responses)

LLM 앱을 처음 붙이면 많은 입문자가 같은 실수를 합니다. 모델 호출을 일반적인 CRUD API처럼 다루는 것입니다. 요청을 보내고, 몇 초 기다린 뒤, 응답 본문 전체를 한 번에 받아 화면에 넣습니다. 기능만 보면 문제없어 보입니다. 실제로 데모도 돌아갑니다. 하지만 사용자가 체감하는 품질은 여기서 크게 갈립니다. 같은 5초라도 아무 변화 없이 멈춰 있는 5초와, 첫 글자가 300ms 안에 나타나고 그 뒤로 답이 계속 이어지는 5초는 완전히 다르게 느껴집니다.

이 차이는 겉보기 효과가 아닙니다. LLM은 원래 생성형 시스템입니다. 모델 내부에서는 토큰이 순차적으로 만들어지는데, 애플리케이션이 그 결과를 마지막까지 붙잡고 있다가 한 번에 내보내면 사용자는 모델이 실제로는 이미 일을 하고 있다는 사실을 볼 수 없습니다. 기다리는 동안 UI는 멈춰 있고, 네트워크는 조용하고, 사용자는 “느리다”는 인상만 받습니다. 긴 답변일수록 문제는 더 커집니다. 코드 설명, 문서 요약, 초안 작성처럼 출력이 길어지는 작업에서는 응답이 오고 있는지조차 모르면 사용자는 새로고침을 누르거나 같은 질문을 다시 보내기 쉽습니다.

그래서 스트리밍은 선택적 장식이 아니라 인터페이스 설계의 일부입니다. 서버가 생성 중인 조각을 바로 흘려보내면 사용자는 응답이 시작되었음을 즉시 확인하고, 프런트엔드는 그 조각을 받아 화면에 누적할 수 있습니다. 백엔드 관점에서도 장점이 있습니다. 긴 문자열이 완성될 때까지 메모리에만 붙잡아 둘 필요가 줄고, 생성 중간 결과를 파일·로그·다음 파이프라인 단계로 넘기기도 쉬워집니다.

이번 글에서는 Groq Python SDK를 기준으로 스트리밍 응답을 끝까지 다룹니다. 다룰 범위는 일곱 가지입니다.

- 왜 블로킹 호출이 UX를 나쁘게 만드는지
- `stream=True`와 `for chunk in stream:` 패턴
- 청크에서 `chunk.choices[0].delta.content`를 읽는 법
- 스트리밍과 동기·비동기 패턴의 차이
- 마지막 청크의 `x_groq` 또는 별도 집계로 사용량을 읽는 방법
- 스트림을 파일에 쓰거나 다음 단계로 파이프하는 방법
- 시리즈 전체를 마무리하고 다음 단계 학습 경로를 정리하는 방법

핵심은 단순합니다. **스트리밍은 모델을 더 빠르게 만들지 않지만, 사용자가 기다림을 이해할 수 있게 만듭니다.**

---

## 왜 스트리밍이 필요한가

블로킹 호출은 서버 관점에서는 단순합니다. `client.chat.completions.create()`를 호출하고, 함수가 반환될 때까지 기다린 뒤, 완성된 문자열을 한 번에 씁니다. 구현 난도도 낮습니다. 하지만 사용자는 호출이 끝나기 전까지 아무 정보도 받지 못합니다.

예를 들어 아래 두 흐름을 비교해 보겠습니다.

첫 번째는 비스트리밍입니다.

1. 사용자가 질문을 보냅니다.
2. 서버가 모델 호출을 시작합니다.
3. 모델은 내부적으로 토큰을 생성합니다.
4. 서버는 모든 토큰이 끝날 때까지 기다립니다.
5. 응답 전체를 한 번에 돌려줍니다.

두 번째는 스트리밍입니다.

1. 사용자가 질문을 보냅니다.
2. 서버가 모델 호출을 시작합니다.
3. 첫 번째 청크가 준비되는 즉시 서버가 클라이언트로 보냅니다.
4. 이후 청크가 도착할 때마다 화면에 이어 붙입니다.
5. 마지막 청크에서 종료와 사용량 정보를 읽습니다.

총 생성 시간이 같더라도, 사용자는 두 번째 방식을 훨씬 빠르게 느낍니다. 이유는 세 가지입니다.

- 첫 바이트가 빨리 도착해 작업이 시작되었음을 확인할 수 있습니다.
- 긴 답변도 읽으면서 기다릴 수 있어 체감 지연이 줄어듭니다.
- 중간 취소, 부분 저장, 진행 표시 같은 UX를 만들 수 있습니다.

실무에서는 특히 다음 경우에 스트리밍 가치가 큽니다.

- 답변 길이가 들쭉날쭉한 챗봇
- 문서 초안이나 요약처럼 긴 텍스트를 생성하는 앱
- 웹 UI에서 사용자가 즉시 반응을 기대하는 인터랙션
- 후속 파이프라인이 첫 문장부터 처리해도 되는 시스템

반대로 내부 배치 작업처럼 사람이 직접 기다리지 않는 경로에서는 비스트리밍으로도 충분할 수 있습니다. 중요한 것은 기술 유행을 따라가는 것이 아니라, 어떤 경로에서 사람이 기다리는지 먼저 보는 것입니다.

---

## Groq SDK에서 스트리밍을 여는 가장 작은 코드

Groq SDK에서 동기 스트리밍은 아주 작은 차이로 시작합니다. 기존 호출에 `stream=True`를 넣고, 반환값을 `for chunk in stream:`으로 순회하면 됩니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": "당신은 간결한 Python 튜터입니다.",
        },
        {
            "role": "user",
            "content": "파이썬 제너레이터를 5문장 안에서 설명해 주세요.",
        },
    ],
    temperature=0.3,
    stream=True,
)

for chunk in stream:
    print(chunk)
```

여기서 반환되는 `stream`은 완성된 응답 객체가 아니라 청크 이터레이터에 가깝습니다. 각 청크에는 그 시점에 새로 생성된 조각과 메타데이터가 들어 있습니다. 입문 단계에서 가장 중요한 변화는 사고방식입니다. 이제 응답은 문자열 한 덩어리가 아니라 순차적으로 도착하는 이벤트 묶음입니다.

이벤트 스트림을 다룰 때는 보통 세 가지를 구분합니다.

- 텍스트 조각을 꺼내 화면이나 버퍼에 붙이는 일
- 종료 청크를 감지하고 루프를 닫는 일
- 마지막에 사용량이나 종료 이유 같은 메타데이터를 읽는 일

첫 번째가 가장 자주 쓰이고, 나머지 둘은 운영 품질을 위해 필요합니다.

---

## 청크에서 실제 텍스트를 꺼내는 법

채팅 스트림에서 바로 출력할 텍스트는 보통 `chunk.choices[0].delta.content`에 들어 있습니다. 다만 모든 청크에 텍스트가 들어오는 것은 아닙니다. 일부 청크는 역할 정보만 담거나, 종료 신호만 담거나, 사용량만 담을 수 있습니다. 그래서 `None` 체크를 넣는 습관이 필요합니다.

아래는 가장 실용적인 동기 예제입니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "FastAPI와 Flask의 차이를 입문자 관점에서 설명해 주세요.",
        }
    ],
    temperature=0.2,
    stream=True,
)

parts: list[str] = []

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
        parts.append(delta)

final_text = "".join(parts)
print("\n---")
print(final_text)
```

패턴은 간단합니다.

1. 루프 안에서 `delta.content`를 읽습니다.
2. 값이 있을 때만 즉시 출력합니다.
3. 동시에 리스트에 누적합니다.
4. 루프가 끝나면 `"".join(parts)`로 최종 문자열을 만듭니다.

이렇게 두 경로를 함께 두는 이유가 있습니다. 사용자는 토큰이 흘러가는 모습을 보고, 애플리케이션은 나중에 저장·검사·후처리할 완성본도 갖게 됩니다. 화면 표시만 하고 누적하지 않으면 로그 저장이나 후속 체인으로 넘길 때 불편합니다. 반대로 누적만 하고 화면에 늦게 보여주면 스트리밍의 UX 이점을 잃습니다.

실무에서는 `print()` 대신 보통 다음 둘 중 하나를 씁니다.

- 웹소켓이나 SSE로 프런트엔드에 즉시 전달
- 내부 버퍼에 append한 뒤 주기적으로 flush

CLI에서는 `print(delta, end="", flush=True)`면 충분하지만, 서버에서는 소비자와의 프로토콜을 먼저 정해야 합니다.

---

## 동기 스트리밍과 비동기 스트리밍은 어디서 갈리나

동기 스트리밍은 학습과 스크립트 자동화에 잘 맞습니다. 한 요청을 보내고 한 스트림을 읽으면 끝나는 경로라면 코드가 짧고 디버깅도 쉽습니다. 반면 웹 서버나 여러 동시 연결을 다루는 서비스에서는 비동기 패턴이 더 자연스럽습니다. 한 연결이 토큰을 기다리는 동안 이벤트 루프가 다른 요청을 계속 처리할 수 있기 때문입니다.

비동기 버전은 `AsyncGroq`와 `async for`가 핵심입니다.

```python
import asyncio
import os

from groq import AsyncGroq

client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

async def main() -> None:
    stream = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": "asyncio가 웹 서버에서 왜 유리한지 설명해 주세요.",
            }
        ],
        temperature=0.2,
        stream=True,
    )

    parts: list[str] = []

    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
            parts.append(delta)

    final_text = "".join(parts)
    print("\n---")
    print(final_text)

asyncio.run(main())
```

구조는 동기 버전과 비슷하지만, 적용 위치는 다릅니다.

- 동기: CLI 도구, 짧은 배치 스크립트, 단일 호출 검증
- 비동기: FastAPI 서버, 동시 사용자 세션, 여러 네트워크 작업 결합

여기서 중요한 점은 스트리밍과 비동기가 같은 개념이 아니라는 사실입니다. 스트리밍은 **응답을 쪼개 받는 방식**이고, 비동기는 **기다리는 동안 다른 일을 할 수 있게 하는 실행 모델**입니다. 동기 스트리밍도 가능하고, 비스트리밍 비동기 호출도 가능합니다. 둘을 한 덩어리로 생각하면 설계 판단이 흐려집니다.

예를 들어 웹 서버에서 한 요청마다 모델 스트림 하나를 열고 그 결과를 브라우저에 넘기는 상황이라면, 비동기 서버 + 스트리밍 조합이 가장 자연스럽습니다. 반대로 야간 배치에서 생성 결과를 파일로 저장하는 스크립트라면, 동기 스트리밍만으로도 충분히 단순하고 좋습니다.

---

## 스트리밍 중 사용량은 어떻게 읽는가

비스트리밍 응답에서는 `completion.usage`를 바로 읽으면 끝납니다. 스트리밍에서는 타이밍이 조금 다릅니다. 중간 청크에는 사용량이 비어 있는 경우가 많고, 마지막 청크에 메타데이터가 붙는 경우가 일반적입니다. Groq에서는 최종 청크의 `x_groq` 아래에 사용량 정보가 포함될 수 있습니다. SDK 버전과 응답 형태에 따라 구체 필드 접근은 조금 달라질 수 있으므로, 마지막 청크를 잡아 안전하게 검사하는 편이 좋습니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "파이썬 데코레이터를 설명해 주세요."}],
    stream=True,
)

parts: list[str] = []
last_chunk = None

for chunk in stream:
    last_chunk = chunk
    delta = chunk.choices[0].delta.content
    if delta:
        parts.append(delta)

final_text = "".join(parts)
print(final_text)

usage = None
if last_chunk is not None:
    groq_meta = getattr(last_chunk, "x_groq", None)
    if groq_meta is not None:
        usage = getattr(groq_meta, "usage", None)

if usage is not None:
    print("prompt_tokens:", usage.prompt_tokens)
    print("completion_tokens:", usage.completion_tokens)
    print("total_tokens:", usage.total_tokens)
else:
    print("usage metadata was not present in the final chunk")
```

운영 코드에서는 한 단계 더 보수적으로 접근하는 편이 좋습니다. 이유는 두 가지입니다.

- SDK 버전이 바뀌면 메타데이터 객체 형태가 달라질 수 있습니다.
- 프록시나 중간 계층을 끼우면 마지막 청크의 메타데이터가 그대로 전달되지 않을 수 있습니다.

그래서 서비스 설계에서는 보통 아래 둘 중 하나를 선택합니다.

1. 마지막 청크의 `x_groq`를 읽어 서버 로그와 과금 지표에 남깁니다.
2. 스트리밍 경로와 별개로 요청 단위 메타데이터를 서버 쪽에서 별도 집계합니다.

두 번째 방식은 프런트엔드에 토큰을 흘려보내더라도 서버가 세션 단위 사용량을 안정적으로 기록할 수 있다는 장점이 있습니다. 예를 들어 요청 시작 시각, 첫 토큰 시각, 마지막 토큰 시각, 총 바이트 수, 총 토큰 수를 함께 적재하면 나중에 UX와 비용을 함께 분석할 수 있습니다.

---

## 스트림을 파일에 쓰거나 다음 단계로 파이프하기

스트리밍의 장점은 화면 표시만이 아닙니다. 토큰이 생기는 즉시 다른 소비자에게 넘길 수 있다는 점도 중요합니다. 가장 쉬운 형태는 파일 저장입니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Redis 입문자를 위한 10줄 요약을 작성해 주세요.",
        }
    ],
    stream=True,
)

with open("summary.txt", "w", encoding="utf-8") as file:
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            file.write(delta)
            file.flush()
            print(delta, end="", flush=True)
```

이 코드는 생성되는 즉시 파일과 표준 출력에 동시에 기록합니다. 생성이 길어지더라도 중간 결과가 디스크에 남기 때문에, 운영 중간에 프로세스가 끊겼을 때도 일부 결과를 복구하기 쉽습니다.

조금 더 흥미로운 패턴은 다음 단계로 파이프하는 방식입니다. 예를 들어 모델 응답을 한 문장씩 받아 금칙어 검사나 요약기, 번역기, TTS 엔진에 순차적으로 넘길 수 있습니다. 이때는 “토큰마다 바로 후처리”보다 “작은 버퍼를 모았다가 의미 있는 경계에서 넘기기”가 실용적입니다.

```python
def sentence_chunks(stream):
    buffer = ""

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if not delta:
            continue

        buffer += delta

        while ". " in buffer:
            sentence, buffer = buffer.split(". ", 1)
            yield sentence + "."

    if buffer.strip():
        yield buffer

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "벡터 데이터베이스를 쉽게 설명해 주세요."}],
    stream=True,
)

for sentence in sentence_chunks(stream):
    print("[consumer]", sentence)
```

이 구조는 다음 시리즈에서 다룰 캐싱, 후처리, 스트리밍 심화 패턴의 출발점이 됩니다. 중요한 것은 스트림을 단순 출력이 아니라 **연결 가능한 데이터 흐름**으로 보는 관점입니다.

---

## FastAPI에서 브라우저로 스트림을 그대로 전달하기

웹 앱에서는 서버가 받은 청크를 다시 브라우저에 흘려보내야 합니다. FastAPI에서는 `StreamingResponse`가 가장 단순한 출발점입니다. 아래 예시는 서버가 Groq 스트림을 받아 브라우저 쪽으로 SSE 형태로 전달하는 패턴입니다.

```python
import os

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from groq import AsyncGroq

app = FastAPI()
client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

@app.get("/chat/stream")
async def chat_stream(prompt: str) -> StreamingResponse:
    async def event_gen():
        stream = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            stream=True,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield f"data: {delta}\n\n"

        yield "data: [done]\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")
```

브라우저에서는 `EventSource`나 `fetch()` 스트림으로 이 데이터를 읽어 화면에 붙이면 됩니다. 서버가 모델 공급자와 직접 붙고, 브라우저는 우리 서버만 보게 만드는 이유도 분명합니다.

- API 키를 브라우저에 노출하지 않습니다.
- 공통 로깅과 인증을 서버에서 처리할 수 있습니다.
- 실패 재시도, 사용량 집계, 프롬프트 정책을 중앙에서 통제할 수 있습니다.

실무에서 자주 놓치는 부분은 종료 신호입니다. 사용자가 끊겼는지, 모델이 끝났는지, 중간 오류가 났는지 프런트엔드가 구분할 수 있어야 합니다. 그래서 실제 서비스에서는 `[done]`, `[error]` 같은 제어 이벤트를 함께 보내는 편이 좋습니다.

---

## 무엇을 기준으로 동기와 비동기를 고를까

입문 단계에서는 문법보다 배치 맥락을 기준으로 판단하면 됩니다.

- 로컬 실험, CLI, 운영 보조 스크립트라면 동기 스트리밍이 가장 단순합니다.
- FastAPI 서버, 다중 사용자 채팅, 여러 외부 I/O를 묶는 앱이라면 비동기 스트리밍이 자연스럽습니다.
- 사용자가 완성본만 필요하고 부분 출력 가치가 없다면 비스트리밍도 여전히 유효합니다.

이 셋을 섞어 생각하지 않는 것이 중요합니다. “비동기이니까 스트리밍”도 아니고, “스트리밍이면 무조건 더 낫다”도 아닙니다. 사용자가 기다리는지, 기다리는 동안 중간 결과를 봐야 하는지, 서버가 같은 시간에 다른 연결도 처리해야 하는지에 따라 답이 달라집니다.

운영 지표도 함께 보아야 합니다. 스트리밍을 넣은 뒤에는 보통 아래 값을 따로 측정합니다.

- 요청 시작부터 첫 토큰까지 시간
- 첫 토큰부터 마지막 토큰까지 시간
- 전체 토큰 수와 응답 길이
- 사용자 중도 취소 비율

이 지표를 보면 “총 응답 시간은 비슷하지만 첫 토큰 시간이 크게 줄어 만족도가 올랐다” 같은 판단이 가능해집니다. 스트리밍은 감각의 문제가 아니라 측정 가능한 UX 개선 수단입니다.

---

## 마무리

이번 글에서는 블로킹 호출이 왜 답답하게 느껴지는지부터 시작해, Groq SDK의 `stream=True` 패턴, `chunk.choices[0].delta.content`로 텍스트를 꺼내는 방법, 동기와 비동기 스트리밍의 역할 차이, 마지막 청크의 `x_groq` 또는 서버 쪽 별도 집계로 사용량을 읽는 방법, 그리고 파일 저장·파이프·FastAPI `StreamingResponse`까지 한 흐름으로 정리했습니다. 이 시리즈 전체를 돌아보면 우리는 첫 API 호출에서 출발해 토큰과 비용, 메시지 구조, 프롬프트 역할, few-shot과 추론 유도, 대화 상태 관리, 그리고 실시간 출력까지 LLM 앱의 가장 바깥쪽 뼈대를 한 바퀴 훑었습니다. 다음 단계에서는 같은 기초 위에 더 운영다운 문제를 올릴 차례입니다. 이어지는 `llm-api-production-101` 시리즈에서는 Structured Output, Tool Calling, 스트리밍 심화, Caching 같은 주제를 다루며, “모델을 한 번 불러보는 앱”에서 “예측 가능하게 운영되는 앱”으로 넘어가는 기준선을 함께 정리하겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기](./01-llm-api-first-call.md)
- [토큰 이해하기 — 비용, 한계, 컨텍스트 창](./02-understanding-tokens.md)
- [프롬프트 엔지니어링 기초 — System·User·Assistant 역할](./03-prompt-engineering-basics.md)
- [Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기](./04-few-shot-and-cot.md)
- [대화 상태 관리 — 멀티턴 챗봇 만들기](./05-conversation-state.md)
- **스트리밍 응답 처리 — 실시간으로 출력 받기 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [Groq text generation docs](https://console.groq.com/docs/text-chat)
- [Groq Python SDK repository](https://github.com/groq/groq-python)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [MDN Server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

Tags: LLM, OpenAI, Prompt Engineering, Python
