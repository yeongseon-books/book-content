---
title: "LangChain 101 (5/6): Streaming — 실시간 출력 처리"
series: langchain-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- LangChain
- LCEL
- Python
- LLM
last_reviewed: '2026-05-12'
seo_description: LangChain의 stream과 astream으로 LLM 출력을 토큰 단위로 받아 처리하는 방법을 정리합니다
---

# LangChain 101 (5/6): Streaming — 실시간 출력 처리

이 글은 LangChain 101 시리즈의 다섯 번째 글입니다.

LLM 응답은 종종 몇 초씩 걸립니다. 총 처리 시간은 같더라도, 사용자가 아무 것도 보지 못한 채 기다리는 경험은 훨씬 더 느리게 느껴집니다. 그래서 스트리밍은 성능 최적화라기보다 먼저 **체감 지연을 줄이는 전달 방식**으로 이해하는 편이 정확합니다.

LangChain에서 좋은 점은 스트리밍이 별도 아키텍처를 요구하지 않는다는 것입니다. 대부분의 경우 체인 정의는 그대로 두고, `invoke()` 대신 `stream()`이나 `astream()`으로 결과를 소비하는 방식만 바꾸면 됩니다.

---

![전체 흐름 한눈에 보기](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/05/05-02-the-flow-at-a-glance.ko.png)
*전체 흐름 한눈에 보기*
> Streaming은 다른 체인을 만드는 기능이 아닙니다. 같은 체인을, 모델이 아직 생성 중일 때 부분 결과를 먼저 소비하는 실행 방식입니다.

## 먼저 던지는 질문

- `stream()`과 `astream()`은 사용자 경험과 서버 구조를 어떻게 다르게 만들까요?
- 청크를 다시 모을 때 빈 chunk와 중간 오류를 어떻게 다뤄야 할까요?
- FastAPI 스트리밍 엔드포인트에서는 어떤 경계에서 backpressure와 예외를 처리해야 할까요?

## 최소 실행 예제

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

chain = (
    ChatPromptTemplate.from_template("Explain {topic} in three sentences.")
    | ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"])
    | StrOutputParser()
)

for chunk in chain.stream({"topic": "astream"}):
    print(chunk, end="", flush=True)
```

이 예제에서 체인 정의는 전혀 특별하지 않습니다. 첫 글에서 본 것과 똑같은 `prompt | llm | parser` 구조입니다. 달라진 것은 최종 결과를 한 번에 받지 않고, 부분 문자열 청크를 순서대로 소비한다는 점뿐입니다.

## 기본 스트리밍

![모델 직접 스트리밍과 체인 스트리밍 비교](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/05/05-01-basic-streaming.ko.png)

*모델 직접 스트리밍과 체인 스트리밍 비교*

`stream()`은 generator를 반환합니다. 따라서 일반 `for` 루프로 순회하면서 청크를 바로 출력할 수 있습니다.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

# LLM에서 바로 스트리밍
print("=== LLM direct streaming ===")
for chunk in llm.stream("List five advantages of Python."):
    print(chunk.content, end="", flush=True)

print("\n\n=== chain streaming ===")
prompt = ChatPromptTemplate.from_messages([
    ("human", "Explain {topic} in three paragraphs."),
])

chain = prompt | llm | StrOutputParser()

for chunk in chain.stream({"topic": "vector search"}):
    print(chunk, end="", flush=True)

print()
```

`end=""`는 줄바꿈을 막고, `flush=True`는 버퍼링을 줄여 화면에 즉시 보이게 합니다. `StrOutputParser()`가 붙어 있으므로 체인 스트리밍에서는 `AIMessageChunk`가 아니라 문자열 조각을 받습니다.

운영 관점에서 보면 이 차이는 꽤 큽니다. 파서를 붙여 두면 이후 HTTP 응답이나 UI 이벤트로 넘길 때 훨씬 단순한 텍스트 파이프라인을 유지할 수 있기 때문입니다.

---

## 스트리밍 결과 다시 모으기

![청크를 다시 최종 텍스트로 조립하는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/05/05-02-collecting-streamed-output.ko.png)

*청크를 다시 최종 텍스트로 조립하는 흐름*

스트리밍 중간에는 화면에 바로 보여 주고, 끝난 뒤에는 로그 저장이나 캐시를 위해 전체 텍스트가 필요할 때가 많습니다. 이때는 청크를 리스트에 쌓아 두었다가 마지막에 합치면 됩니다.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = (
    ChatPromptTemplate.from_messages([("human", "{question}")])
    | llm
    | StrOutputParser()
)

chunks = []
print("streaming: ", end="")
for chunk in chain.stream({"question": "What is FAISS?"}):
    print(chunk, end="", flush=True)
    chunks.append(chunk)

full_text = "".join(chunks)
print(f"\n\ntotal characters: {len(full_text)}")
```

<!-- injected-output:start -->
**Output**

    streaming: FAISS (Facebook AI Similarity Search) is an open-source library for efficient similarity search and clustering of dense vectors. It was initially developed by Facebook to enable fast similarity search in large-scale vector spaces.

    FAISS is particularly useful in applications that involve searching for similar items in a high-dimensional space, such as:

    1. **Nearest Neighbor Search**: Finding the most similar items to a query vector in a large dataset.
    2. **Clustering**: Grouping similar vectors together to identify patterns or outliers.
    3. **Anomaly Detection**: Identifying vectors that are significantly different from the rest of the dataset.

    FAISS provides several benefits, including:

    1. **Speed**: FAISS is designed to be highly efficient, with performance improvements over traditional similarity search algorithms.
    2. **Scalability**: FAISS can handle large datasets and scale to thousands of nodes.
    3. **Flexibility**: FAISS supports various similarity metrics (e.g., inner product, L2 norm, cosine similarity) and clustering algorithms (e.g., k-means, hierarchical clustering).

    Some of the key features of FAISS include:

    1. **Indexing**: FAISS supports various indexing techniques, such as IVF (Inverted File) and PQ (Product Quantization).
    2. **Quantization**: FAISS provides efficient quantization methods to reduce the dimensionality of the data.
    3. **Clustering**: FAISS supports various clustering algorithms, including k-means and hierarchical clustering.

    FAISS is widely used in various applications, such as:

    1. **Recommendation Systems**: FAISS is used in recommendation systems to find similar items to suggest to users.
    2. **Computer Vision**: FAISS is used in computer vision applications, such as image and object recognition.
    3. **Natural Language Processing**: FAISS is used in NLP applications, such as text similarity search and clustering.

    Overall, FAISS is a powerful library for efficient similarity search and clustering of dense vectors, widely used in various applications across industries.

    total characters: 2039

<!-- injected-output:end -->

이 패턴은 실전에서 매우 자주 씁니다. 스트리밍은 사용자 경험을 위해 켜고, 마지막에는 전체 결과를 로깅·캐싱·후처리용으로 확보하는 방식입니다.

---

## `astream()` — 비동기 스트리밍

![async for 기반 스트리밍 실행 경로](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/05/05-03-astream-async-streaming.ko.png)

*async for 기반 스트리밍 실행 경로*

FastAPI 같은 비동기 프레임워크에서는 `stream()`보다 `astream()`이 더 자연스럽습니다. 이벤트 루프를 막지 않고 `async for`로 청크를 소비할 수 있기 때문입니다.

```python
import asyncio
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = (
    ChatPromptTemplate.from_messages([("human", "Explain {topic} briefly.")])
    | llm
    | StrOutputParser()
)

async def stream_response(topic: str) -> None:
    print(f"streaming: {topic}")
    async for chunk in chain.astream({"topic": topic}):
        print(chunk, end="", flush=True)
    print()

async def main() -> None:
    await stream_response("embedding vectors")
    await stream_response("FAISS indexes")

asyncio.run(main())
```

이렇게 생각하면 됩니다. 동기 CLI 스크립트라면 `stream()`, 비동기 웹 서버라면 `astream()`이 기본값입니다. 체인 구조는 같고 호출자 문맥만 달라집니다.

---

## FastAPI 스트리밍 엔드포인트

실서비스에서는 스트리밍 결과를 HTTP 응답으로 흘려보내야 합니다. FastAPI에서는 `StreamingResponse`가 가장 기본적인 형태입니다.

```python
import os

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

app = FastAPI()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = (
    ChatPromptTemplate.from_messages([("human", "{question}")])
    | llm
    | StrOutputParser()
)

@app.get("/stream")
async def stream_endpoint(question: str):
    async def generate():
        async for chunk in chain.astream({"question": question}):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
```

서버 실행:

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

테스트:

```bash
curl "http://localhost:8000/stream?question=What+is+RAG"
```

운영에서 자주 만나는 문제는 코드보다 네트워크 쪽입니다. 프록시나 게이트웨이가 버퍼링하면, 애플리케이션은 스트리밍 중이어도 클라이언트는 한꺼번에 받는 것처럼 보일 수 있습니다. 그래서 "streaming이 안 된다"는 문제는 LangChain보다 배포 경로 설정에서 시작하는 경우가 많습니다.

---

## `astream_events()`로 세밀하게 제어하기

![체인 이벤트를 선택적으로 보는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/05/05-04-astream-events-for-fine-grained-control.ko.png)

*체인 이벤트를 선택적으로 보는 흐름*

단순히 텍스트 청크만 필요하다면 `astream()`이면 충분합니다. 하지만 체인 안에서 어느 컴포넌트가 어떤 이벤트를 내는지 보고 싶다면 `astream_events()`가 더 적합합니다.

```python
import asyncio
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = (
    ChatPromptTemplate.from_messages([("human", "Explain {topic}.")])
    | llm
    | StrOutputParser()
)

async def main() -> None:
    async for event in chain.astream_events({"topic": "FAISS"}, version="v2"):
        event_type = event["event"]
        if event_type == "on_llm_stream":
            chunk = event["data"].get("chunk", "")
            if hasattr(chunk, "content") and chunk.content:
                print(chunk.content, end="", flush=True)
    print()

asyncio.run(main())
```

`astream_events()`는 디버깅과 계측에 특히 유용합니다. 예를 들어 Prompt 단계, Retriever 단계, LLM 단계 중 어디서 시간이 많이 걸리는지 보거나, Tool Calling이 섞인 체인에서 어떤 이벤트가 중간에 나오는지 구분할 수 있습니다.

---

## Callback으로 스트리밍 로깅 붙이기

스트리밍을 운영에 붙일 때는 "보였다"보다 "무엇이 언제 보였는지"가 중요합니다. 콜백 핸들러를 사용하면 토큰 단위 이벤트를 일관된 형식으로 로그에 남길 수 있습니다.

```python
import os
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

class StreamLogHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        if token:
            print(f"[token] {token!r}")

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
    streaming=True,
    callbacks=[StreamLogHandler()],
)

chain = (
    ChatPromptTemplate.from_template("Explain {topic} in two paragraphs.")
    | llm
    | StrOutputParser()
)

for chunk in chain.stream({"topic": "callback handlers"}):
    print(chunk, end="", flush=True)
```

이 방식은 CLI 데모보다 서버 운영에서 더 유용합니다. token 이벤트를 request_id와 함께 저장하면 사용자 불만("응답이 멈췄다")을 재현할 때 큰 도움이 됩니다.

## stream vs astream 운영 선택 기준

| 항목 | `stream()` | `astream()` |
|---|---|---|
| 호출 문맥 | 동기 함수 | 비동기 함수 |
| 반복 형태 | `for chunk in ...` | `async for chunk in ...` |
| 적합한 환경 | CLI, 배치 스크립트 | FastAPI, WebSocket 서버 |
| 취소 처리 | 상대적으로 단순 | 연결 취소/타임아웃 분기 필요 |

팀 기준을 미리 정해 두면 코드 일관성이 좋아집니다. 예를 들어 "API 계층은 전부 `astream`만 사용"처럼 규칙을 두면 이벤트 루프 블로킹 문제를 줄일 수 있습니다.

## 빈 chunk와 중간 오류 처리 패턴

모델 공급자마다 스트리밍 이벤트 형식이 조금씩 다르므로, 빈 chunk를 오류로 오인하지 않는 코드가 필요합니다.

```python
def safe_stream(chain, payload: dict) -> str:
    chunks: list[str] = []
    try:
        for chunk in chain.stream(payload):
            if not chunk:
                continue
            print(chunk, end="", flush=True)
            chunks.append(chunk)
    except Exception as exc:
        print(f"\n[stream-error] {type(exc).__name__}: {exc}")
    finally:
        print()
    return "".join(chunks)
```

핵심은 실패하더라도 이미 전송한 부분 텍스트를 잃지 않는 것입니다. 사용자에게는 부분 결과를 보여 주고, 운영 로그에는 예외 유형과 마지막 chunk 시점을 함께 남겨야 합니다.

## FastAPI에서 SSE 형식으로 내보내기

단순 `text/plain`도 충분하지만, 프런트엔드가 이벤트 단위를 분리해야 한다면 SSE 형식이 더 안정적입니다.

```python
import json
import os

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

app = FastAPI()

chain = (
    ChatPromptTemplate.from_template("Answer briefly: {question}")
    | ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"])
    | StrOutputParser()
)

@app.get("/sse")
async def sse(question: str):
    async def generate():
        async for chunk in chain.astream({"question": question}):
            if not chunk:
                continue
            payload = json.dumps({"type": "token", "text": chunk}, ensure_ascii=False)
            yield f"data: {payload}\n\n"
        yield "data: {\"type\":\"done\"}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

이 구조를 쓰면 클라이언트가 `done` 이벤트를 기준으로 렌더링 완료를 명확히 판단할 수 있습니다. 운영에서 타임아웃 정책을 넣을 때도 이벤트 단위가 있으면 훨씬 다루기 쉽습니다.

## LangSmith 추적으로 첫 토큰 지연 측정하기

스트리밍 품질은 총 latency보다 first token latency에 더 크게 좌우됩니다. 추적 로그에서 두 값을 분리해 관리하는 것이 좋습니다.

```text
trace_id=trc_05_stream_001
model=llama-3.1-8b-instant
latency_total_ms=1820
latency_first_token_ms=410
tokens_out=278
status=success
```

동일한 총 지연이라도 첫 토큰이 빠르면 체감은 크게 좋아집니다. 그래서 튜닝 순서도 보통 `first_token -> tokens/sec -> total_latency` 순으로 잡는 편이 효율적입니다.

## 스트리밍 운영 체크리스트

- `취소 처리`: 클라이언트 연결이 끊기면 생성 루프를 즉시 중단하는가
- `부분 결과 정책`: 중간 오류 시 부분 텍스트를 사용자에게 유지하는가
- `관측`: first token latency, total latency, output token 수를 저장하는가
- `버퍼링 경로`: 프록시/게이트웨이에서 chunk buffering이 꺼져 있는가
- `재시도`: 스트리밍 중 재시도는 새 요청으로 분리하는가

이 체크리스트를 배포 전 점검 항목으로 넣어 두면, 기능 데모는 되는데 프로덕션에서 체감이 나빠지는 상황을 크게 줄일 수 있습니다.

## Tool Calling과 스트리밍을 함께 쓰는 패턴

실전 챗 인터페이스에서는 도구 호출과 최종 답변 스트리밍이 같이 등장합니다. 이때 사용자에게는 다음 두 단계를 구분해 보여 주는 편이 좋습니다.

1. **도구 실행 단계**: "계산 중", "조회 중" 같은 상태 이벤트
2. **최종 응답 생성 단계**: 토큰 스트리밍

```python
from langchain_core.messages import HumanMessage, ToolMessage

async def run_tool_then_stream(question: str):
    messages = [HumanMessage(content=question)]

    # 1) 첫 라운드: tool 요청 확인
    first = llm_with_tools.invoke(messages)
    messages.append(first)

    for tc in first.tool_calls:
        result = tool_map[tc["name"]].invoke(tc["args"])
        print(f"[tool] {tc['name']} -> {result}")
        messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

    # 2) 둘째 라운드: 최종 답변 스트리밍
    async for chunk in llm_with_tools.astream(messages):
        if hasattr(chunk, "content") and chunk.content:
            print(chunk.content, end="", flush=True)
    print()
```

이 패턴을 쓰면 사용자는 "지금 멈춘 것이 아니라 도구 실행 중"이라는 상태를 이해할 수 있고, 체감 품질이 좋아집니다.

## backpressure를 고려한 전송 제어

느린 클라이언트가 연결된 상태에서 무제한으로 토큰을 밀어내면 서버 메모리와 큐가 빠르게 커질 수 있습니다. 그래서 전송 계층에서 최소한의 흐름 제어가 필요합니다.

```python
import asyncio

async def throttled_generate(chain, payload: dict, delay_sec: float = 0.0):
    async for chunk in chain.astream(payload):
        if not chunk:
            continue
        yield chunk
        if delay_sec > 0:
            await asyncio.sleep(delay_sec)
```

실제로는 인위적 지연보다 네트워크 버퍼 정책, SSE 프레임 크기, 게이트웨이 타임아웃을 함께 조정해야 합니다. 핵심은 애플리케이션 레벨에서도 backpressure를 전혀 무시하지 않는다는 점입니다.

## 스트리밍 이벤트 설계 예시

클라이언트와 합의한 이벤트 스키마를 두면 화면 로직이 단순해집니다.

| event.type | payload 예시 | 프런트엔드 동작 |
|---|---|---|
| `status` | `{ "phase": "tool_calling" }` | 상태 배지 표시 |
| `token` | `{ "text": "FAISS" }` | 본문 누적 렌더링 |
| `usage` | `{ "tokens_out": 180 }` | 비용/통계 갱신 |
| `done` | `{}` | 입력창 재활성화 |
| `error` | `{ "message": "provider timeout" }` | 오류 토스트 표시 |

이 합의가 없으면 프런트엔드가 공급자별 예외 형식을 직접 해석해야 하고, 유지보수 비용이 빠르게 올라갑니다.

---

## 이 코드에서 주목할 점

- 체인 정의는 `invoke()` 버전에서 거의 바뀌지 않습니다. 진짜 차이는 출력을 소비하는 방식입니다.
- `stream()`은 동기 반복이고, `astream()`은 같은 논리 응답에 대한 비동기 반복입니다.
- 청크를 리스트에 모아 나중에 합치는 패턴은 로깅, 캐싱, 후처리에 자주 쓰입니다.
- `astream_events()`는 단순 토큰 표시를 넘어, 체인 수준의 디버깅과 계측에 유용합니다.

## 엔지니어가 자주 헷갈리는 지점

- 스트리밍은 최종 답변 형식을 바꾸지 않습니다. 애플리케이션이 각 조각을 받는 시점만 바꿉니다.
- 비동기 스트리밍은 호출자 코드도 함께 바꾸므로, 프레임워크와 엔드포인트가 async 흐름을 지원해야 합니다.
- 이벤트 스트림은 강력하지만, 단지 텍스트를 점진적으로 보여 주려는 목적이라면 오버헤드가 될 수 있습니다.

## 체크리스트

- [ ] 같은 체인을 `invoke()`와 `stream()`으로 모두 실행할 수 있다
- [ ] `astream()`과 `astream_events()`의 차이를 설명할 수 있다
- [ ] FastAPI의 `StreamingResponse`가 스트리밍 청크를 어떻게 감싸는지 이해했다

## 정리

LangChain 스트리밍은 한 가지 변화로 시작합니다. `invoke()`를 `stream()`이나 `astream()`으로 바꾸는 것입니다. 체인 구조는 그대로 두고, 출력 소비 방식만 바꾸면 됩니다. FastAPI에서는 `StreamingResponse`를 감싸 실시간으로 청크를 사용자에게 전달할 수 있습니다.

다음 글에서는 지금까지 다룬 LCEL, 프롬프트, Retriever, Streaming을 한 파일 안에서 조합해, 실제로 돌아가는 완전한 RAG 체인으로 묶어 보겠습니다.

## 처음 질문으로 돌아가기

- **`stream()`과 `astream()`은 사용자 경험과 서버 구조를 어떻게 다르게 만들까요?**
  `stream()`은 동기 반복자로 부분 결과를 주고, `astream()`은 비동기 서버에서 await 가능한 흐름을 제공합니다. 둘 다 첫 토큰 지연을 줄여 사용자 경험을 바꿉니다.

- **청크를 다시 모을 때 빈 chunk와 중간 오류를 어떻게 다뤄야 할까요?**
  빈 chunk는 정상 이벤트일 수 있으므로 상태로 처리하고, 중간 오류는 지금까지 받은 부분 결과와 함께 로그에 남겨야 합니다.

- **FastAPI 스트리밍 엔드포인트에서는 어떤 경계에서 backpressure와 예외를 처리해야 할까요?**
  FastAPI에서는 generator 또는 async generator 경계에서 취소, 느린 클라이언트, provider 예외를 잡아 연결 종료와 로그를 분리해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LangChain 101 (1/6): LangChain 소개 — LCEL과 Runnable 기본](./01-lcel-runnable-basics.md)
- [LangChain 101 (2/6): Prompt와 LLM Chain — 체인 첫 번째 구성](./02-prompt-llm-chain.md)
- [LangChain 101 (3/6): Retriever — 문서 검색과 컨텍스트 주입](./03-retriever.md)
- [LangChain 101 (4/6): Tool Calling — 외부 도구 연결하기](./04-tool-calling.md)
- **LangChain 101 (5/6): Streaming — 실시간 출력 처리 (현재 글)**
- LangChain 101 (6/6): 실전 체인 조립 — 컴포넌트를 하나로 연결하기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain streaming guide](https://python.langchain.com/docs/expression_language/streaming/)
- [astream_events reference](https://python.langchain.com/docs/expression_language/interface/)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/langchain-101/ko/05-streaming)

Tags: LangChain, LCEL, Python, LLM
