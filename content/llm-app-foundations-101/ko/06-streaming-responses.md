---
title: "LLM App Foundations 101 (6/6): 스트리밍 응답 처리 — 실시간으로 출력 받기"
series: llm-app-foundations-101
episode: 6
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

# LLM App Foundations 101 (6/6): 스트리밍 응답 처리 — 실시간으로 출력 받기

LLM 애플리케이션을 느리게 만드는 가장 쉬운 방법 중 하나는 모델 호출을 일반적인 블로킹 API처럼 다루는 것입니다. 서버는 프롬프트를 보내고, 몇 초 동안 조용히 기다린 뒤, 답변 전체가 끝났을 때 한 번에 돌려줍니다. 기능은 동작하지만 사용자 경험은 필요 이상으로 답답해집니다.

문제는 총 생성 시간이 아니라 보이는 방식입니다. 사용자는 기다리는 동안 모델이 실제로 작업 중인지, 네트워크가 멈췄는지, 애플리케이션이 고장 났는지 알 수 없습니다. 반대로 몇백 밀리초 안에 첫 글자가 나타나고 뒤이어 텍스트가 이어지면, 같은 5초라도 체감은 완전히 달라집니다.

스트리밍의 가치는 바로 여기에 있습니다. 모델을 더 똑똑하게 만들지도, 총 생성 시간을 마법처럼 줄이지도 않습니다. 대신 기다림을 눈에 보이게 바꿉니다. 긴 답변일수록 이 차이는 더 커지고, 챗봇·초안 작성·브라우저 UI 같은 경로에서는 거의 제품 경험의 일부가 됩니다.

여기서는 스트리밍을 성능 트릭이 아니라 사용자에게 생성 과정을 드러내는 응답 전달 방식으로 보고, Groq SDK 기준의 기본 패턴을 정리하겠습니다.

![스트리밍 응답의 전체 이벤트 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/06/06-01-handling-streaming-responses-real-time-o.ko.png)
*스트리밍 응답의 전체 이벤트 흐름*

## 먼저 던지는 질문

- streaming은 응답을 더 빨리 끝내는 기술일까요, 생성 흐름을 먼저 보여주는 기술일까요?
- chunk에서 텍스트, 종료 신호, 사용량을 어떻게 읽어야 할까요?
- FastAPI 같은 서버는 모델 스트림을 사용자에게 어떻게 중계할까요?

## 왜 이 글이 중요한가

응답 품질이 충분해진 뒤 사용자가 가장 먼저 체감하는 문제는 종종 속도가 아니라 침묵입니다. 애플리케이션이 아무 반응 없이 몇 초를 보내면, 사용자는 모델이 답을 생성 중인지조차 확신할 수 없습니다. 이때 스트리밍은 실제 지연 시간을 숨기는 기능이 아니라, 진행 중인 작업을 사용자에게 노출하는 기능이 됩니다.

또한 스트리밍은 텍스트를 다루는 방식 자체를 바꿉니다. 비스트리밍에서는 응답이 하나의 완성 객체입니다. 스트리밍에서는 응답이 이벤트 시퀀스가 됩니다. 일부 청크는 텍스트를 담고, 일부 청크는 종료 신호나 메타데이터만 담습니다. UI를 만들기 시작하면 이 이벤트 중심 모델이 오히려 더 자연스럽습니다.

운영 관점에서도 의미가 큽니다. 시간당 처리량을 갑자기 올려 주지는 않더라도, time to first token, 사용자 취소율, 장문 응답 이탈률 같은 제품 지표를 개선할 수 있습니다. 즉, 스트리밍은 단순한 코드 패턴이 아니라 측정 가능한 UX 전략입니다.

## 스트리밍을 이해하는 가장 좋은 방법: 응답 본문 하나를 받는 것이 아니라 생성 이벤트의 흐름을 소비하는 것으로 보는 것입니다

`stream=True`를 켜는 순간 멘탈 모델이 바뀝니다. 이전에는 완료된 문자열 하나를 받았지만, 이제는 조각들이 순서대로 도착하는 흐름을 다뤄야 합니다. 따라서 소비자 코드는 세 가지를 동시에 신경 써야 합니다. 사용자에게 보일 부분 텍스트, 나중에 저장할 최종 텍스트, 마지막에만 나타날 수 있는 사용량 메타데이터입니다.

이 시각이 중요한 이유는 스트리밍을 단순한 화면 출력 기능으로만 보면 나중에 저장, 로깅, 후속 파이프라인 연결, 중단 처리에서 다시 막히기 때문입니다. 스트림은 텍스트가 아니라 이벤트 흐름입니다. 그렇게 이해해야 UI와 서버 설계가 함께 정리됩니다.

> 스트리밍의 핵심은 모델을 더 빨리 끝내는 데 있지 않고, 생성 중인 답을 이벤트 흐름으로 드러내어 기다림을 읽을 수 있게 만드는 데 있습니다.

## 핵심 개념

비스트리밍과 스트리밍의 차이는 총 시간보다 관찰 가능성에 있습니다. 비스트리밍에서는 모든 토큰이 끝난 뒤 최종 payload 하나가 옵니다. 스트리밍에서는 첫 청크가 준비되는 즉시 전송이 시작됩니다.

가장 작은 Groq 스트리밍 호출은 아래와 같습니다.

![완성 전 청크가 먼저 도착하는 최소 예제](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/06/06-01-the-smallest-groq-streaming-example.ko.png)

*완성 전 청크가 먼저 도착하는 최소 예제*

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": "You are a concise Python tutor.",
        },
        {
            "role": "user",
            "content": "Explain Python generators in five sentences.",
        },
    ],
    temperature=0.3,
    stream=True,
)

for chunk in stream:
    print(chunk)
```

처음에는 이 출력이 장황해 보이지만, 일부 청크는 텍스트가 아니라 제어 정보만 담는다는 사실을 눈으로 확인하는 데 도움이 됩니다. 스트리밍을 디버깅할 때는 한 번쯤 raw chunk를 그대로 출력해 보는 편이 좋습니다.

이제 응답은 하나의 문자열이 아니라 청크들의 시퀀스입니다. 애플리케이션은 이 시퀀스에서 사용자에게 보여 줄 텍스트만 골라내야 합니다.

![청크 안에서 텍스트와 종료 정보를 읽는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/06/06-02-extracting-text-from-each-chunk.ko.png)

*청크 안에서 텍스트와 종료 정보를 읽는 구조*

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain the difference between FastAPI and Flask for beginners.",
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

<!-- injected-output:start -->
**출력 예시**

    FastAPI is a modern Python framework for building APIs, while Flask is a minimal web framework that gives you more manual control. FastAPI includes data validation and automatic docs by default, whereas Flask starts smaller and lets you assemble those pieces yourself. Beginners often find FastAPI faster for API-first projects and Flask easier to understand when learning core web concepts.
    ---
    FastAPI is a modern Python framework for building APIs, while Flask is a minimal web framework that gives you more manual control. FastAPI includes data validation and automatic docs by default, whereas Flask starts smaller and lets you assemble those pieces yourself. Beginners often find FastAPI faster for API-first projects and Flask easier to understand when learning core web concepts.

<!-- injected-output:end -->

여기서 중요한 습관은 `delta.content`가 비어 있을 수 있음을 정상으로 취급하는 것입니다. 일부 청크는 텍스트가 아니라 역할 정보나 종료 신호만 담을 수 있습니다.

스트리밍과 async는 같은 개념이 아닙니다.

![동기 스트리밍과 비동기 스트리밍의 구조 차이](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/06/06-03-streaming-versus-sync-and-async-patterns.ko.png)

*동기 스트리밍과 비동기 스트리밍의 구조 차이*

스트리밍은 응답이 조각으로 오는 방식이고, async는 애플리케이션이 그 조각을 기다리는 방식입니다. 따라서 동기 스트리밍도 가능하고 비동기 스트리밍도 가능합니다.

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
                "content": "Explain why asyncio helps in web servers.",
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

<!-- injected-output:start -->
**출력 예시**

    Asyncio helps web servers because one request can wait on network or database I/O without freezing the whole worker. While that request is waiting, the event loop can schedule other connections and keep throughput high. This matters most when your server spends more time waiting on external systems than using CPU.
    ---
    Asyncio helps web servers because one request can wait on network or database I/O without freezing the whole worker. While that request is waiting, the event loop can schedule other connections and keep throughput high. This matters most when your server spends more time waiting on external systems than using CPU.

<!-- injected-output:end -->

작은 CLI 도구라면 동기 스트리밍이 충분하고, FastAPI 같은 다중 사용자 서버라면 비동기 스트리밍이 더 자연스럽습니다.

스트리밍에서는 사용량 메타데이터를 언제 읽을지도 달라집니다.

![마지막 청크와 별도 집계로 사용량을 읽는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/06/06-04-reading-token-usage-during-or-after-stre.ko.png)

*마지막 청크와 별도 집계로 사용량을 읽는 구조*

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Explain Python decorators."}],
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

마지막 청크 메타데이터가 비어 있는 상황도 운영에서는 충분히 나올 수 있습니다. 프록시가 연결을 먼저 닫았거나, SDK 버전이 바뀌었거나, 중간에 클라이언트가 취소했을 수 있기 때문입니다. 그래서 usage는 가능하면 마지막 청크와 서버 로그 두 군데에서 함께 잡는 편이 안전합니다.

실전에서는 중단·타임아웃·부분 저장까지 한 번에 다루는 소비 함수를 두면 편합니다.

```python
import time

def consume_stream(stream) -> tuple[str, float | None]:
    parts: list[str] = []
    first_token_at: float | None = None
    started_at = time.perf_counter()

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if not delta:
            continue

        if first_token_at is None:
            first_token_at = time.perf_counter() - started_at

        parts.append(delta)

    return "".join(parts), first_token_at
```

이 함수가 주는 핵심 값은 두 가지입니다. 첫째, 최종 본문을 안전하게 재구성합니다. 둘째, 사용자가 실제로 처음 글자를 본 시점인 time to first token을 측정합니다. 스트리밍 품질은 총 시간보다 이 지표에서 더 잘 드러나는 경우가 많습니다.

현업에서는 보통 마지막 청크 메타데이터와 서버 쪽 요청 단위 계측을 함께 둡니다. 이유는 스트리밍 경로가 중간 연결 종료, 프록시 동작, SDK 변경 같은 운영 변수에 더 민감하기 때문입니다.

스트리밍은 UI뿐 아니라 파일 저장과 파이프라인 연결에도 유용합니다. 긴 초안 생성 중간 결과를 바로 파일에 flush할 수도 있고, 문장 단위로 버퍼링해 다른 소비자에게 넘길 수도 있습니다. 핵심은 스트림을 “터미널 출력”이 아니라 “중간에 끼워 넣을 수 있는 데이터 흐름”으로 보는 것입니다. 이제 서버에서 브라우저로 릴레이하는 패턴까지 보면 스트리밍의 제품적 위치가 더 선명해집니다.

![FastAPI가 모델 스트림을 브라우저로 전달하는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/06/06-05-relaying-the-stream-through-fastapi.ko.png)

*FastAPI가 모델 스트림을 브라우저로 전달하는 구조*

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

여기서 자주 만나는 실패 모드도 미리 염두에 두는 편이 좋습니다. 브라우저가 중간에 연결을 끊으면 서버는 스트림 정리를 해야 하고, 역방향 프록시가 버퍼링을 켜 두면 청크가 한꺼번에 밀려올 수 있으며, 종료 이벤트가 빠지면 프런트엔드는 정상 완료와 네트워크 실패를 구분하기 어렵습니다. 따라서 SSE 릴레이는 단순 출력 코드처럼 보여도 실제로는 종료 신호와 취소 처리까지 포함한 전송 프로토콜에 가깝습니다.

이 패턴에서는 브라우저에 API 키를 노출하지 않고, 인증·프롬프트 정책·사용량 로깅을 서버에 유지할 수 있습니다. 또한 `[done]` 같은 명시적 종료 이벤트를 보내야 클라이언트가 정상 종료와 네트워크 실패를 구분하기 쉬워집니다.

## 흔히 헷갈리는 지점

- 스트리밍이 총 생성 시간을 크게 줄여 준다고 기대하기 쉽지만, 실제 가치는 체감 지연과 가시성 개선에 있습니다.
- 스트리밍과 async를 같은 개념으로 보지만, 하나는 응답 전달 방식이고 다른 하나는 대기 방식입니다.
- 모든 청크에 텍스트가 있다고 가정하면 소비 루프가 쉽게 깨집니다. 빈 `delta`는 정상입니다.
- 중간 렌더링만 신경 쓰고 최종 문자열 재구성을 빼먹기 쉽지만, 저장·캐시·후속 처리에는 전체 본문이 필요합니다.
- 마지막 종료 신호를 명시하지 않으면 브라우저 UI는 정상 완료와 연결 문제를 구분하기 어렵습니다.

## 스트리밍 운영 패턴: 중단, 재시도, 백프레셔

스트리밍이 실제 서비스에 들어가면 가장 먼저 필요한 것은 예쁜 출력보다 종료 제어입니다. 사용자 취소, 네트워크 단절, 서버 재시작이 모두 중간에 일어날 수 있기 때문입니다. 그래서 스트림 소비 루프는 "완주"만이 아니라 "중단"을 정상 경로로 다뤄야 합니다.

```python
class StreamCancelled(Exception):
    pass

def consume_with_cancel(stream, is_cancelled) -> str:
    parts: list[str] = []
    for chunk in stream:
        if is_cancelled():
            raise StreamCancelled("User requested cancellation")

        delta = chunk.choices[0].delta.content
        if delta:
            parts.append(delta)

    return "".join(parts)
```

이 패턴을 두면 "취소했는데도 모델 호출이 끝까지 돈다" 같은 낭비를 줄일 수 있습니다.

### 스트리밍 전용 오류 분기

비스트리밍과 달리 스트리밍은 "시작 전 실패"와 "중간 실패"를 구분해야 합니다.

| 실패 시점 | 예시 | 권장 대응 |
|---|---|---|
| 시작 전 | 인증 실패, 모델 ID 오류 | 즉시 실패 응답 |
| 중간 | 네트워크 단절, 클라이언트 종료 | 부분 결과 저장 + 중단 상태 기록 |
| 종료 직전 | done 이벤트 누락 | 타임아웃 후 강제 종료 처리 |

중간 실패를 500으로만 뭉개면 사용자 입장에서는 "아무것도 안 나왔다"로 느껴집니다. 부분 텍스트를 남기고 재시도 가이드를 주는 쪽이 훨씬 낫습니다.

### FastAPI SSE에서 백프레셔 완화

브라우저 소비 속도가 느리면 서버 버퍼가 밀릴 수 있습니다. 이때는 청크를 너무 잘게 쪼개지 않고, 문장 단위 버퍼링을 넣는 편이 안정적입니다.

```python
async def sentence_buffered_sse(stream):
    buffer = ""
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if not delta:
            continue

        buffer += delta
        if buffer.endswith((".", "!", "?", "\n")):
            yield f"data: {buffer}\n\n"
            buffer = ""

    if buffer:
        yield f"data: {buffer}\n\n"
    yield "data: [done]\n\n"
```

이 방식은 토큰 단위 실시간성은 조금 낮아지지만, 전송량과 렌더링 부하를 줄여 실제 UX가 더 안정적으로 보일 때가 많습니다.

### 스트리밍 지표를 분리해서 보기

스트리밍 도입 효과는 평균 응답 시간 하나로 잘 보이지 않습니다. 아래 지표를 분리해 보는 편이 정확합니다.

| 지표 | 의미 | 목표 |
|---|---|---|
| TTFT(time to first token) | 첫 글자 도착 시간 | 가능한 낮게 |
| Stream completion rate | `[done]`까지 정상 완료 비율 | 가능한 높게 |
| Mid-stream abort rate | 중간 취소/단절 비율 | 원인별 추적 |
| Avg tokens streamed | 평균 스트리밍 토큰 수 | use case별 기준화 |

스트리밍은 "빠르다/느리다"보다 "얼마나 빨리 보이기 시작하는가"가 핵심입니다. 그래서 TTFT를 별도로 측정하지 않으면 개선 여부를 놓치기 쉽습니다.

## 운영 체크리스트

- [ ] `stream=True` 호출이 기본 응답 객체와 다른 소비 패턴을 만든다는 점을 확인했습니다.
- [ ] 청크 처리 루프에서 `chunk.choices[0].delta.content`가 `None`일 수 있음을 정상 처리합니다.
- [ ] 누적한 스트림 결과가 비스트리밍 최종 본문과 같은지 검증했습니다.
- [ ] 동기 `for`와 비동기 `async for` 소비 패턴을 각각 한 번씩 구현했습니다.
- [ ] FastAPI 스트리밍 경로에서 `StreamingResponse`, 올바른 `media_type`, 명시적 종료 이벤트를 사용합니다.

## 정리

스트리밍은 모델을 더 빠르게 끝내는 기능이 아니라, 생성 중인 답을 사용자와 시스템에 더 일찍 보여 주는 기능입니다. 이 한 가지 차이만으로도 체감 속도, 장문 응답 경험, 취소 가능성, 후속 파이프라인 연결 방식이 모두 달라집니다.

이 글에서 기억해야 할 핵심은 세 가지입니다. 응답은 이제 문자열 하나가 아니라 이벤트 시퀀스이고, 소비자는 부분 렌더링과 최종 재구성과 메타데이터 수집을 함께 해야 하며, 서버는 스트림을 브라우저로 안전하게 릴레이하는 중간 계층이 되어야 합니다.

이 시리즈는 여기서 기초를 마칩니다. 첫 호출, 토큰, 역할 기반 프롬프트, few-shot 유도, 대화 상태, 스트리밍까지 이해했다면 이제 작은 LLM 앱을 설계하고 설명할 수 있는 기반이 생긴 것입니다. 다음 단계는 구조화 출력, 툴 호출, 더 깊은 스트리밍 운영 패턴, 캐싱과 재시도처럼 프로덕션 쪽 관심사로 넘어가는 일입니다.

## 처음 질문으로 돌아가기

- streaming은 응답을 더 빨리 끝내는 기술일까요, 생성 흐름을 먼저 보여주는 기술일까요?
  - streaming은 생성을 더 빨리 끝내기보다, 생성 중인 조각을 먼저 전달해 사용자가 진행 상황을 볼 수 있게 만드는 기술입니다.

- chunk에서 텍스트, 종료 신호, 사용량을 어떻게 읽어야 할까요?
  - 각 chunk에서 delta 텍스트를 누적하고, 종료 신호와 사용량은 provider가 제공하는 마지막 chunk나 별도 집계 경로에서 확인합니다.

- FastAPI 같은 서버는 모델 스트림을 사용자에게 어떻게 중계할까요?
  - FastAPI는 모델에서 받은 chunk를 `StreamingResponse` 같은 서버 스트림으로 감싸 브라우저나 클라이언트에 다시 흘려보냅니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM App Foundations 101 (1/6): LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기](./01-llm-api-first-call.md)
- [LLM App Foundations 101 (2/6): 토큰 이해하기 — 비용, 한계, 컨텍스트 창](./02-understanding-tokens.md)
- [LLM App Foundations 101 (3/6): 프롬프트 엔지니어링 기초 — System·User·Assistant 역할](./03-prompt-engineering-basics.md)
- [LLM App Foundations 101 (4/6): Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기](./04-few-shot-and-cot.md)
- [LLM App Foundations 101 (5/6): 대화 상태 관리 — 멀티턴 챗봇 만들기](./05-conversation-state.md)
- **LLM App Foundations 101 (6/6): 스트리밍 응답 처리 — 실시간으로 출력 받기 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Groq text generation docs](https://console.groq.com/docs/text-chat)
- [Groq Python SDK repository](https://github.com/groq/groq-python)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [MDN Server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

### 관련 시리즈

- [대화 상태 관리 — 멀티턴 챗봇 만들기](./05-conversation-state.md)
- [스트리밍 심화 — 청크 처리와 오류 복구](../../llm-api-production-101/ko/03-streaming-in-depth.md)
- [챗봇 패턴 — 대화 이력 관리와 상태](../../ai-app-patterns-101/ko/01-chatbot-pattern.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-app-foundations-101/ko/06-streaming-responses)

Tags: LLM, OpenAI, Prompt Engineering, Python
