---
episode: 3
language: ko
last_reviewed: '2026-05-15'
series: llm-api-production-101
status: publish-ready
tags:
- LLM
- OpenAI
- Streaming
- Python
targets:
  ebook: true
  medium: false
  mkdocs: true
  tistory: true
title: "LLM API Production 101 (3/6): 스트리밍 심화 — 청크 처리와 오류 복구"
seo_description: 스트리밍 응답의 부분 상태, inactivity timeout, 부분 결과 보존을 운영 관점에서 정리합니다.
---

# LLM API Production 101 (3/6): 스트리밍 심화 — 청크 처리와 오류 복구

스트리밍은 데모에서는 즉시 체감되는 기능입니다. 첫 토큰이 빨리 보이면 사용자는 시스템이 살아 있다고 느끼고, 긴 답변에서도 이탈이 줄어듭니다. 하지만 운영에서는 스트리밍을 단순한 출력 효과로 보면 금방 한계를 만납니다. `stream=True`는 응답 방식을 바꾸는 동시에 실패 모델도 함께 바꾸기 때문입니다.

일반 응답은 대체로 성공 또는 예외로 끝납니다. 반면 스트리밍은 하나의 요청 안에서 진행과 실패가 동시에 존재할 수 있습니다. 청크가 일부까지는 잘 오다가 갑자기 멈출 수 있고, 텍스트 없는 이벤트가 섞일 수 있으며, 마지막 종료 신호 없이 연결이 끊길 수도 있습니다. 이때 사용자는 이미 화면에서 절반의 답을 읽었을 수 있습니다.

그래서 스트리밍 소비자는 최종 문자열만 바라보면 안 됩니다. 지금까지 누적한 텍스트, 마지막 유효 청크를 받은 시점, 정상 종료 신호를 봤는지 여부, 실패가 어디서 났는지를 함께 관리해야 합니다. 그렇지 않으면 “가끔 답이 중간에서 멈춘다”는 가장 다루기 어려운 버그 리포트를 만나게 됩니다.

이번 글에서는 Groq 스트리밍 경로를 기준으로, 기본 청크 루프를 시작점으로 삼아 비어 있는 델타 처리, 읽기 타임아웃 제어, 부분 결과 보존, 재시도 판단까지 운영 관점으로 정리하겠습니다.

이 글은 LLM API Production 101 시리즈의 세 번째 글입니다.

여기서는 부분 상태를 가진 스트리밍 응답을 안전하게 소비하고 복구하는 방법을 살펴보겠습니다.

## 먼저 던지는 질문

- 스트리밍은 최종 문자열 하나가 아니라 왜 부분 상태를 가진 세션으로 봐야 할까요?
- 텍스트가 없는 chunk와 중간 실패는 어떤 상태로 다뤄야 할까요?
- 스트리밍 실패 뒤 재시도할 때 무엇을 보존하고 무엇을 다시 만들어야 할까요?

## 왜 이 글이 중요한가

스트리밍은 UX 개선 기능처럼 보이지만, 실제로는 전송 프로토콜을 소비하는 코드입니다. 그 말은 곧 부분 응답, 연결 종료, 타임아웃, 마감 신호 누락 같은 문제를 애플리케이션이 직접 처리해야 한다는 뜻입니다. 이 책임을 무시하면 사용자 경험은 좋아지지 않고 오히려 더 혼란스러워집니다.

특히 생산 환경에서는 부분 응답 자체가 의미 있는 상태입니다. 사용자가 일부 답변을 봤다면 그것은 “빈 실패”가 아닙니다. 로그에도 남아야 하고, UI에도 반영되어야 하며, 재시도 정책도 그 사실을 전제로 설계되어야 합니다. 이미 보낸 토큰은 회수할 수 없기 때문입니다.

또한 스트리밍 경로는 관측 가능성이 중요합니다. 어느 시점까지 정상 진행이 있었는지, 종료 신호가 있었는지, transport timeout인지 provider-side interruption인지 구분할 수 있어야 장애 분석이 가능합니다. 이 차이가 있어야 스트리밍을 “멋있는 기능”이 아니라 “설명 가능한 운영 경로”로 다룰 수 있습니다.

## 큰 그림

![스트리밍 심화: 청크 처리와 오류 복구](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/03/03-01-streaming-in-depth-chunk-handling-and-er.ko.png)

*스트리밍 심화: 청크 처리와 오류 복구*

이 그림에서는 스트리밍 응답을 완성된 문자열이 아니라 청크가 쌓이는 세션 상태로 봅니다. 중간 실패가 나도 어디까지 받았는지 남아 있어야 복구와 재시도 판단이 가능합니다.

> 스트리밍의 핵심은 빨리 보여 주는 데 있지 않습니다. 중간에 끊겨도 어디까지 왔는지 설명할 수 있는 세션 상태를 유지하는 데 있습니다.

## 핵심 개념

### 스트리밍에서는 무엇이 달라지는가

![스트리밍 세션이 부분 상태를 남기는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/03/03-01-what-changes-when-the-response-is-a-stre.ko.png)

*스트리밍 세션이 부분 상태를 남기는 흐름*

비스트리밍 호출은 성공이면 최종 객체를 받고, 실패면 예외를 받는 구조로 생각하기 쉽습니다. 스트리밍은 다릅니다. 30개 청크가 정상 도착한 뒤 12초 동안 멈추고, 그 뒤 연결이 끊어질 수 있습니다. 이 요청은 완전한 성공도, 빈 실패도 아닙니다.

따라서 최소한 다음 상태는 추적해야 합니다. 지금까지 누적한 텍스트, 마지막 의미 있는 청크를 본 시각, 종료 신호 확인 여부, 종료가 정상 완료인지 타임아웃인지 예외인지 같은 상태입니다. 이 정보가 있어야 스트림을 단순 예외가 아니라 관측 가능한 타임라인으로 다룰 수 있습니다.

### 가장 기본적인 청크 소비 루프

![기본 청크 소비 루프의 실행 경로](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/03/03-02-the-baseline-chunk-loop.ko.png)

*기본 청크 소비 루프의 실행 경로*

기준이 되는 최소 구현은 아래와 같습니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain FastAPI dependency injection for beginners.",
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

이 루프는 사용자에게 즉시 보이는 출력과 애플리케이션이 보존할 최종 문자열을 동시에 만듭니다. 하지만 아직 생산 환경에는 부족합니다. 빈 청크 처리, 무응답 감지, 예외 시 부분 결과 보존이 빠져 있기 때문입니다.

### 텍스트 없는 청크를 정상으로 다루기

텍스트가 없는 청크를 에러처럼 다루면 로그가 시끄러워집니다. 일부 청크는 역할 정보나 종료 메타데이터만 담고 있을 수 있기 때문입니다.

```python
for chunk in stream:
    choice = chunk.choices[0]
    delta = choice.delta.content

    if delta is not None and delta != "":
        print(delta, end="", flush=True)
        parts.append(delta)

    if choice.finish_reason is not None:
        print(f"\nfinish_reason={choice.finish_reason}")
```

중요한 점은 소비자가 당황하지 않는 것입니다. 빈 청크는 경고 신호가 아니라 프로토콜의 일부일 수 있습니다. 정상 이벤트를 비정상처럼 기록하면 실제 장애를 찾기 더 어려워집니다.

### 타임아웃은 루프 바깥에서 강제해야 한다

![동기 루프와 비동기 timeout 적용 비교](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/03/03-03-enforcing-timeouts-outside-the-loop.ko.png)

*동기 루프와 비동기 timeout 적용 비교*

동기 `for chunk in stream:` 루프는 다음 청크를 기다리는 동안 블로킹됩니다. 그래서 루프 내부에서 시계를 확인해도 진짜 청크 간 무응답을 감지할 수 없습니다. 무응답을 잡으려면 읽기 자체를 감싸야 합니다.

```python
import asyncio
import os

from groq import AsyncGroq

INACTIVITY_TIMEOUT_SECONDS = 8.0

client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

async def consume_stream(prompt: str) -> dict:
    stream = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    parts: list[str] = []

    while True:
        try:
            chunk = await asyncio.wait_for(
                anext(stream),
                timeout=INACTIVITY_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError as exc:
            return {"status": "timeout", "text": "".join(parts), "error": str(exc)}
        except StopAsyncIteration:
            return {"status": "completed", "text": "".join(parts)}

        delta = chunk.choices[0].delta.content
        if delta:
            parts.append(delta)
            print(delta, end="", flush=True)

asyncio.run(consume_stream("Explain why Python context managers are useful."))
```

여기서 봐야 할 것은 총 요청 시간이 아니라 “진전이 계속 있는가”입니다. 동기 경로를 유지해야 한다면 transport timeout을 두는 편이 낫지만, 진짜 청크 간 무응답 감지는 읽기 자체를 감싸는 방식에서만 정확해집니다.

```python
import os

from groq import Groq

client = Groq(
    api_key=os.environ["GROQ_API_KEY"],
    timeout=8.0,
)

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Explain Python generators."}],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
```

### 실패해도 부분 결과를 버리지 않기

![스트리밍 결과 객체에 남기는 상태 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/03/03-04-keeping-partial-output-on-failure.ko.png)

*스트리밍 결과 객체에 남기는 상태 구조*

부분 결과를 항상 포함하는 결과 객체를 반환하면 복구와 UI 처리가 쉬워집니다.

```python
import os

from groq import Groq

def stream_text(prompt: str) -> dict:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        stream=True,
    )

    parts: list[str] = []
    finish_reason = None

    try:
        for chunk in stream:
            choice = chunk.choices[0]
            delta = choice.delta.content
            if delta:
                parts.append(delta)
                print(delta, end="", flush=True)

            if choice.finish_reason is not None:
                finish_reason = choice.finish_reason

        return {
            "status": "completed",
            "text": "".join(parts),
            "finish_reason": finish_reason,
            "saw_finish_reason": finish_reason is not None,
        }
    except Exception as exc:
        return {
            "status": "failed",
            "text": "".join(parts),
            "error": str(exc),
            "finish_reason": finish_reason,
            "saw_finish_reason": finish_reason is not None,
        }
```

이 래퍼가 주는 가치는 단순합니다. 호출자는 완료와 실패를 구분하면서도, 실패 전에 생성된 텍스트를 그대로 받을 수 있습니다. 웹 UI에서는 이 부분 텍스트를 남기고 “응답이 중단되었습니다”라는 안내를 덧붙이는 식으로 처리할 수 있습니다.

### 어떤 신호가 불완전한 스트림을 암시하는가

![스트리밍 중단 뒤 재시도 판단 경로](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/03/03-05-retrying-after-a-streaming-failure.ko.png)

*스트리밍 중단 뒤 재시도 판단 경로*

스트림이 불완전했는지 100% 증명하기는 어렵지만, 의심할 만한 신호는 있습니다. 문장이 중간에서 끝난 경우, 코드 블록이 닫히지 않은 경우, `finish_reason` 없이 연결이 끊긴 경우, 사용량 메타데이터가 끝까지 오지 않은 경우가 그렇습니다. 이 검사는 답변 품질을 재단하려는 것이 아니라 전송 완전성을 가늠하려는 것입니다.

재시도 판단은 사용자에게 이미 출력이 보였는지에 따라 달라집니다. 내부 파이프라인이라면 전체 재시도가 쉬울 수 있습니다. 반면 대화형 UI에서는 이미 보여 준 부분 응답을 유지한 채, 다음 시도를 새 블록으로 이어 붙이는 편이 더 정직합니다.

```python
result = stream_text("Explain the difference between FastAPI and Flask.")

print("partial_text=")
print(result["text"])

if result["status"] == "completed":
    print("stream completed normally")
else:
    print("stream interrupted")
    print("show retry button to the user")
```

## 흔히 헷갈리는 지점

- 스트리밍은 일반 완료 응답을 빨리 출력하는 기능일 뿐이라고 생각하면 부분 실패 처리를 놓치기 쉽습니다.
- 텍스트가 없는 청크를 모두 이상 신호로 기록하면 정상 프로토콜 이벤트가 노이즈가 됩니다.
- 동기 이터레이터 내부 시계 확인만으로는 진짜 청크 간 무응답을 감지할 수 없습니다.
- 스트림 실패 시 지금까지 받은 텍스트를 버리면 복구와 디버깅이 더 어려워집니다.
- 이미 사용자에게 일부 응답을 보여 준 뒤의 재시도는 API 정책이면서 동시에 UX 정책입니다.

## 운영 체크리스트

- [ ] 사용자 출력과 내부 누적 문자열을 동시에 유지하는 소비 루프를 만들었다
- [ ] 빈 델타와 종료 메타데이터를 정상 이벤트로 처리했다
- [ ] 읽기 자체를 감싸는 timeout 또는 transport timeout을 적용했다
- [ ] 실패 시 부분 텍스트와 종료 신호 여부를 함께 반환했다
- [ ] UI와 내부 파이프라인에 대해 서로 다른 재시도 정책을 정의했다

## 정리

이번 글에서는 스트리밍을 화려한 출력 모드가 아니라 부분 상태를 가진 응답 세션으로 다뤘습니다. 기본 청크 루프는 출발점일 뿐이고, 실제 운영에서는 빈 청크 처리, 읽기 타임아웃 제어, 부분 결과 보존, 정상 종료 여부 확인이 함께 있어야 합니다.

중요한 점은 스트림이 끊겨도 무슨 일이 일어났는지 설명할 수 있어야 한다는 데 있습니다. 어디까지 출력이 왔는지, 왜 멈췄는지, 다시 시도할 때 무엇을 유지할지를 상태로 남겨야 스트리밍 경로가 신뢰할 수 있는 시스템 구성 요소가 됩니다.

다음 글에서는 같은 운영 관점을 비용과 지연 시간에 적용합니다. 스트리밍이 부분 응답을 다루는 문제였다면, 캐싱은 반복되는 동일 작업을 다시 계산하지 않도록 만드는 문제입니다.

## 처음 질문으로 돌아가기

- **스트리밍은 최종 문자열 하나가 아니라 왜 부분 상태를 가진 세션으로 봐야 할까요?**
  스트리밍은 여러 chunk가 누적되어 하나의 응답이 되므로, 지금까지 받은 텍스트와 종료 신호를 가진 세션 상태로 관리해야 합니다.

- **텍스트가 없는 chunk와 중간 실패는 어떤 상태로 다뤄야 할까요?**
  텍스트 없는 chunk는 정상 신호일 수 있으므로 버리지 말고, 중간 실패는 부분 결과와 오류 원인을 함께 남기는 상태로 처리해야 합니다.

- **스트리밍 실패 뒤 재시도할 때 무엇을 보존하고 무엇을 다시 만들어야 할까요?**
  이미 받은 부분 결과와 요청 식별자는 보존하고, 새 요청에서는 중복 출력·사용자 표시·로그 상관관계를 다시 설계해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM API Production 101 (1/6): 구조화 출력 — JSON 모드와 응답 스키마](./01-structured-output.md)
- [LLM API Production 101 (2/6): 툴 호출 — 함수를 모델에 연결하기](./02-tool-calling.md)
- **LLM API Production 101 (3/6): 스트리밍 심화 — 청크 처리와 오류 복구 (현재 글)**
- LLM API Production 101 (4/6): 캐싱 전략 — 비용과 지연 시간 줄이기 (예정)
- LLM API Production 101 (5/6): 재시도와 오류 처리 — 안정적인 API 호출 만들기 (예정)
- LLM API Production 101 (6/6): 속도 제한 관리 — Rate Limit 대응 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Groq Text Chat docs](https://console.groq.com/docs/text-chat)
- [MDN Server-sent events guide](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

### 검증 보조 자료
- [Python asyncio.wait_for documentation](https://docs.python.org/3/library/asyncio-task.html#asyncio.wait_for)

### 관련 시리즈
- [툴 호출 — 함수를 모델에 연결하기](./02-tool-calling.md)
- [캐싱 전략 — 비용과 지연 시간 줄이기](./04-caching-strategies.md)

Tags: LLM, OpenAI, Streaming, Python
