---
title: 'Streaming — 실시간 출력 처리'
series: langchain-101
episode: 5
language: ko
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LangChain
- LCEL
- Python
- LLM
last_reviewed: '2026-05-01'
---

# Streaming — 실시간 출력 처리

> LangChain 101 시리즈 (5/6)

예제 코드: [github.com/yeongseon-books/langchain-101](https://github.com/yeongseon-books/langchain-101/tree/main/ko/05-streaming)

LLM이 긴 응답을 생성할 때, 전체 텍스트가 완성될 때까지 기다리면 사용자 경험이 나빠집니다. 스트리밍은 토큰이 생성되는 즉시 화면에 출력하는 방식입니다. ChatGPT나 Claude에서 응답이 문자 단위로 흘러나오는 것이 바로 이 방식입니다.

LangChain에서 스트리밍은 `stream()` 메서드 하나로 시작합니다. 체인을 구성하는 방식은 `invoke()`와 동일하고, 호출 방법만 바뀝니다.

이번 글에서 다룰 내용은 다음과 같습니다.

- LLM과 체인에서 `stream()` 사용하기
- `astream()`으로 비동기 스트리밍
- 스트리밍 중 이벤트 유형 구분
- 스트리밍 출력을 문자열로 모으기
- 실용적인 FastAPI 스트리밍 엔드포인트

---

## 기본 스트리밍

`stream()`은 제너레이터를 반환합니다. `for` 루프로 청크를 받아 처리합니다.

```python
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

# LLM 직접 스트리밍
print("=== LLM 직접 스트리밍 ===")
for chunk in llm.stream("파이썬의 장점을 다섯 가지 설명해 주세요."):
    print(chunk.content, end="", flush=True)

print("\n\n=== 체인 스트리밍 ===")
prompt = ChatPromptTemplate.from_messages([
    ("human", "{topic}을 세 문단으로 설명해 주세요."),
])

chain = prompt | llm | StrOutputParser()

for chunk in chain.stream({"topic": "벡터 검색"}):
    print(chunk, end="", flush=True)

print()
```

`end=""`, `flush=True`는 줄바꿈 없이 실시간으로 출력하기 위한 설정입니다. `StrOutputParser()`는 스트리밍에서 `AIMessageChunk.content`를 문자열로 꺼내줍니다.

---

## 스트리밍 출력 수집

스트리밍 출력을 처리한 뒤 전체 텍스트도 필요할 때 청크를 리스트에 모읍니다.

```python
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
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
print("스트리밍: ", end="")
for chunk in chain.stream({"question": "FAISS가 무엇인지 설명해 주세요."}):
    print(chunk, end="", flush=True)
    chunks.append(chunk)

full_text = "".join(chunks)
print(f"\n\n전체 글자 수: {len(full_text)}자")
```

---

## astream() — 비동기 스트리밍

FastAPI 같은 비동기 프레임워크에서는 `astream()`을 씁니다. `async for`로 청크를 받습니다.

```python
import asyncio
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = (
    ChatPromptTemplate.from_messages([("human", "{topic}을 간단히 설명해 주세요.")])
    | llm
    | StrOutputParser()
)

async def stream_response(topic: str) -> None:
    print(f"스트리밍 시작: {topic}")
    async for chunk in chain.astream({"topic": topic}):
        print(chunk, end="", flush=True)
    print()

async def main() -> None:
    await stream_response("임베딩 벡터")
    await stream_response("FAISS 인덱스")

asyncio.run(main())
```

---

## FastAPI 스트리밍 엔드포인트

실제 앱에서는 HTTP SSE(Server-Sent Events)로 클라이언트에 스트리밍합니다.

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

실행 방법입니다.

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

```bash
curl "http://localhost:8000/stream?question=RAG%EB%9E%80+%EB%AC%B4%EC%97%87%EC%9D%B8%EA%B0%80%EC%9A%94"
```

---

## astream_events()로 이벤트 수준 제어

`astream_events()`는 체인 내부에서 발생하는 이벤트를 세밀하게 제어할 때 씁니다.

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
    ChatPromptTemplate.from_messages([("human", "{topic}을 설명해 주세요.")])
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

`astream_events()`는 여러 체인 컴포넌트에서 각각 발생하는 이벤트를 구분해서 처리할 때 유용합니다. 단순 출력이면 `astream()`이 더 간단합니다.

---

## 마무리

스트리밍은 API 호출 한 번에 `stream()` 또는 `astream()`으로 바꾸는 것으로 시작합니다. 체인 구성은 `invoke()`와 동일합니다. FastAPI와 연동하면 SSE로 클라이언트에 실시간 출력을 보낼 수 있습니다.

다음 글에서는 지금까지 배운 컴포넌트를 하나의 완전한 체인으로 조립합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LangChain 소개 — LCEL과 Runnable 기본](./01-lcel-runnable-basics.md)
- [Prompt와 LLM Chain — 체인 첫 번째 구성](./02-prompt-llm-chain.md)
- [Retriever — 문서 검색과 컨텍스트 주입](./03-retriever.md)
- [Tool Calling — 외부 도구 연결하기](./04-tool-calling.md)
- **Streaming — 실시간 출력 처리 (현재 글)**
- 실전 체인 조립 — 컴포넌트를 하나로 연결하기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain Streaming 가이드](https://python.langchain.com/docs/expression_language/streaming/)
- [astream_events 레퍼런스](https://python.langchain.com/docs/expression_language/interface/)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)

Tags: LangChain, LCEL, Python, LLM
