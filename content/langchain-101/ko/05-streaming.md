---
title: 'Streaming — 실시간 출력 처리'
series: langchain-101
episode: 5
language: ko
status: publish-ready
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

## 이 글에서 답할 질문

- `invoke()` 대신 `stream()`을 쓰면 호출 결과 타입이 어떻게 달라지는가
- 체인 스트리밍과 모델 직접 스트리밍은 어디서 차이가 생기는가
- `astream()`과 `astream_events()`는 언제 필요한가
- 스트리밍 응답을 UI나 API 응답으로 넘길 때 어떤 형태로 모아야 하는가

> Streaming은 응답이 끝난 뒤 받는 방식이 아니라 생성 중간 상태를 그대로 소비하는 실행 모드입니다.

![이 글에서 답할 질문](../../../assets/langchain-101/05/05-01-questions-this-post-answers.ko.png)
## 최소 실행 예제

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

chain = (
    ChatPromptTemplate.from_template("{topic}을 세 문장으로 설명해 주세요.")
    | ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"])
    | StrOutputParser()
)

for chunk in chain.stream({"topic": "astream"}):
    print(chunk, end="", flush=True)
```

~~~
출력 결과
스트림(stream)은 데이터를 연속적으로 전송하거나 수신하는 방법입니다. 스트림은 데이터를 메모리 내로 임시로 저장하는 대신, 데이터를 한 개의 단일 흐름으로 전송하거나 수신하여, 메모리를 효율적으로 사용할 수 있습니다.

스트림을 사용하면 데이터를 빠르게 전송하고 수신할 수 있습니다. 또한 스트림은 데이터를 패킷 단위로 전송하기 때문에, 네트워크 오류 또는 패킷 손실 시에도 데이터의 유효성을 검증할 수 있습니다.

스트림의 대표적인 예로는 TCP/IP의 전송 제어 프로토콜(TCP)과 UDP 프로토콜이 있습니다. TCP는 연결형 프로토콜로, 데이터가 제대로 전송될 때까지 재전송을 반복적으로 수행합니다. 반면 UDP는 비연결형 프로토콜로, 데이터를 빠르게 전송하는 것을優先시킵니다.
~~~

## 이 코드에서 봐야 할 것

- 체인 정의는 `invoke()` 때와 같고 소비 방식만 반복자로 바뀝니다.
- 파서를 붙인 스트리밍은 문자열 청크가 오고, 파서가 없으면 메시지 청크가 옵니다.
- 출력 청크를 바로 화면에 흘려보낼 수도 있고, 버퍼에 모아 최종 문자열로 만들 수도 있습니다.
- 스트리밍은 응답 속도를 줄이는 것이 아니라 첫 토큰 체감 시간을 줄입니다.

## 실무에서 헷갈리는 지점

- 스트리밍이 전체 실행 시간을 항상 줄여 주는 것은 아닙니다.
- 비동기 환경에서는 `stream()` 대신 `astream()`을 써야 이벤트 루프와 자연스럽게 붙습니다.
- 이벤트 단위 관찰이 필요할 때는 텍스트 청크보다 `astream_events()`가 더 유용합니다.

## 체크리스트

- [ ] `stream()` 결과를 반복자로 소비할 수 있다
- [ ] 문자열 청크와 메시지 청크 차이를 이해한다
- [ ] 비동기 환경에서 `astream()`을 언제 써야 하는지 설명할 수 있다

LangChain 101 시리즈 (5/6)

예제 코드: [github.com/yeongseon-books/langchain-101](https://github.com/yeongseon-books/langchain-101/tree/main/05-streaming)

## 이 글에서 답할 질문

- `invoke()` 대신 `stream()`으로 바꾸면 코드 구조가 얼마나 달라질까
- `astream()`과 `astream_events()`는 언제 구분해서 써야 할까
- 스트리밍 청크를 문자열로 다시 모을 때 어떤 패턴을 쓰면 될까
- FastAPI에서 스트리밍 결과를 HTTP 응답으로 보내려면 무엇이 필요할까

> Streaming은 체인을 다시 설계하는 기능이 아니라, 같은 체인의 출력을 한 번에 받지 않고 청크 단위로 소비하는 실행 방식입니다.

## 핵심 흐름 한눈에 보기

![핵심 흐름 한눈에 보기](../../../assets/langchain-101/05/05-02-the-flow-at-a-glance.ko.png)
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

~~~
출력 결과
=== LLM 직접 스트리밍 ===
파이썬은 프로그래밍 언어로 개발된 강력한 도구입니다. 파이썬의 장점은 다음과 같습니다.

1. **이해하기 쉬움**: 파이썬의 문법은 간결하고 쉬우며, 새로운 프로그래머로 하여금 쉽게 파이썬을 학습할 수 있도록 도와줍니다. 파이썬의 코드는 일반적으로 읽기 쉬우며, 다른 프로그래머가 쉽게 파이썬 코드를 이해할 수 있습니다.

2. **빠른 개발**: 파이썬은 빠른 개발을 가능하게 하는 데에 강점이 있습니다. 파이썬의 인터프리터는 코드를 바로 실행할 수 있으므로, 개발자들이 빠르게 코드를 테스트하고 수정할 수 있습니다.

3. **다양한 라이브러리와 모듈**: 파이썬은 다양한 라이브러리와 모듈을 제공합니다. 이들은 프로그래머들이 다양한 작업을 수행할 수 있도록 도와줍니다. 예를 들어, 데이터 분석에 사용되는 NumPy, pandas, matplotlib과 같은 라이브러리들이 있습니다.

4. **크롤링 및 데이터 분석**: 파이썬은 웹 크롤링 및 데이터 분석에 편리합니다. BeautifulSoup, Scrapy와 같은 크롤링 라이브러리와, pandas, NumPy, Matplotlib과 같은 데이터 분석 라이브러리들이 있습니다.

5. **Cross-Platform**: 파이썬은 다양한 플랫폼에서 작동할 수 있습니다. Windows, macOS, Linux와 같은 다양한 운영 체제에서 파이썬 코드를 실행할 수 있습니다.

=== 체인 스트리밍 ===
벡터 검색은 컴퓨터 과학에서 데이터베이스나 파일 시스템에서 벡터(벡터는 다차원 공간에서 선분을 의미)의 위치를 빠르게 찾는 기술입니다. 벡터 검색은 일반적으로 임베딩 기법을 사용하여 벡터를 고유한 정수 인덱스에 매핑하여 검색 속도를 높입니다.

벡터 검색 알고리즘은 다음과 같은 과정으로 진행됩니다. 첫째, 벡터를 임베딩 기법을 사용하여 고유한 정수 인덱스에 매핑합니다. 둘째, 검색할 벡터를 임베딩 기법을 사용하여 고유한 정수 인덱스에 매핑합니다. 셋째, 매핑된 인덱스를 사용하여 데이터베이스나 파일 시스템에서 벡터를 검색합니다. 벡터 검색은 많은 양의 데이터에 대해 빠르게 검색할 수 있는 강력한 도구로 사용됩니다.

벡터 검색의 예로는 아나콘다(Anaconda)와 같은 비슷한 벡터 색인기법을 사용한 서비스가 있습니다. 벡터 색인기법은 벡터를 정수 인덱스에 매핑하여 빠르게 검색할 수 있도록 합니다. 벡터 색인기법은 자연어 처리, 추천 시스템, 이미지 검색 등 많은 분야에서 사용됩니다.
~~~

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

~~~
출력 결과
스트리밍: FAISS(FALIA: Fast Approximate and Exact Nearest Neighbors Search Library in Scalable Space)란, 고밀도 데이터셋에 대한 빠르고 효율적인 근접점 검색 알고리즘을 제공하는 오픈 소스 라이브러리입니다. FAISS는 Google에서 개발한 알고리즘으로, 큰 데이터셋에서 효율적으로 거리 기반 탐색을 수행할 수 있도록 설계되었습니다.

FAISS는 다음의 주요 특징을 가지고 있습니다.

1. **빠른 검색 속도**: FAISS는 빠른 검색 속도를 제공합니다. 이는 큰 데이터셋에서 효율적으로 거리 기반 탐색을 수행하도록 설계되어 있습니다.
2. **거리 기반 탐색**: FAISS는 거리 기반 탐색을 지원합니다. 이는 데이터셋에서 유사한 데이터를 찾는 데 사용됩니다.
3. **고밀도 데이터셋**: FAISS는 고밀도 데이터셋을 처리할 수 있습니다. 이는 큰 데이터셋에서 효율적으로 탐색을 수행하도록 설계되어 있습니다.
4. **오픈 소스**: FAISS는 오픈 소스 라이브러리입니다. 이는 자유롭게 사용하고 확장할 수 있습니다.

FAISS는 다음의 알고리즘을 제공합니다.

1. **IVF (Inverted File)**: IVF는 고밀도 데이터셋을 처리하기 위해 설계된 알고리즘입니다. IVF는 데이터셋을 작은 클러스터로 분할하여 효율적으로 탐색을 수행합니다.
2. **HNSW (Hierarchical Navigable Small World)**: HNSW는 거리 기반 탐색을 수행하기 위해 설계된 알고리즘입니다. HNSW는 데이터셋을 계층적 구조로 분할하여 효율적으로 탐색을 수행합니다.
3. **SIFT (Scale-Invariant Feature Transform)**: SIFT는 이미지 프로세싱을 위해 설계된 알고리즘입니다. SIFT는 이미지에서 특징을 추출하고 비교하기 위해 사용됩니다.

FAISS는 다음의 언어로 제공됩니다.

1. **C++**: FAISS는 C++로 작성된 라이브러리입니다.
2. **Python**: FAISS는 Python으로 호출할 수 있습니다.

전체 글자 수: 1039자
~~~

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

~~~
출력 결과
스트리밍 시작: 임베딩 벡터
임베딩 벡터(Embedding Vector) 또는 임베딩 공간(Embedding Space)은 자연어 처리, 컴퓨터 비전, 추천 시스템 등 다양한 분야에서 사용되는 기초적인 개념입니다.

임베딩 벡터는 고차원 공간에 데이터를 embedding(배치)하여 표현하는 방법입니다. 예를 들어, 글자, 단어, 이미지, 혹은 유저 등에 대해 고차원 벡터를 할당하여, 유사성을 측정하거나, 정보를 처리하는 등의 목적으로 사용됩니다.

임베딩 벡터를 도입한 목적은, 고차원 데이터를 저차원 공간에서 처리하는 것이 더 용이하고, 데이터의 의미를 이해하는 것이 더 쉬워지도록 하기 위함입니다. 예를 들어, 단어 임베딩 벡터를 사용하면, "고양이"와 "고양이는"가 서로 유사한 벡터를 가질 수 있습니다. 이처럼, 임베딩 벡터는 데이터의 의미를 이해하는 도구로 사용됩니다.

임베딩 벡터의 예시로는 다음과 같습니다.

- 단어 임베딩 벡터: 각 단어에 고차원 벡터를 할당하여, 유사성을 측정하거나, 문장의 의미를 이해하는 등의 목적으로 사용됩니다.
- 이미지 임베딩 벡터: 각 이미지에 고차원 벡터를 할당하여, 이미지의 특징을 이해하거나, 이미지의 유사성을 측정하는 등의 목적으로 사용됩니다.
- 유저 임베딩 벡터: 각 유저에 고차원 벡터를 할당하여, 유저의 취향이나 취향에 대한 추천을 하는 등의 목적으로 사용됩니다.

임베딩 벡터의 장점으로는, 데이터의 의미를 이해하는 것이 쉬워지고, 데이터의 유사성을 측정하는 것이 용이하다는 점이 있습니다. 하지만, 임베딩 벡터를 구축하는 데에는 많은 데이터가 필요하고, 데이터의 품질이 중요하다는 단점이 있습니다.
스트리밍 시작: FAISS 인덱스
FAISS(Falconn Index for Similarity Search)란?

FAISS는 Facebook에서 개발한 벡터 인덱싱 라이브러리로, 벡터의 유사도를 빠르게 찾기 위한 기술입니다. FAISS는 유사도 검색, 클러스터링, 추천 시스템 등 다양한 응용 분야에서 사용됩니다.

FAISS의 주요 특징은 다음과 같습니다.

1. **고성능**: FAISS는 빠른 속도로 벡터의 유사도를 검색할 수 있습니다.
2. **효율성**: FAISS는 메모리 사용량이 적고, 디스크에 저장할 때도 효율적입니다.
3. **멀티 쓰레딩 지원**: FAISS는 멀티 쓰레딩을 지원하여 병렬 처리가 가능합니다.

FAISS의 구조는 다음과 같습니다.

1. **인덱싱**: 벡터를 인덱싱하는 과정입니다. 인덱싱은 벡터를 특정한 방식으로 재배열해서, 유사한 벡터가 인접하게 배치되도록 합니다.
2. **쿼리**: 사용자가 검색하고자 하는 벡터를 입력하는 과정입니다.
3. **검색**: 인덱싱된 벡터와 쿼리 벡터를 비교하여 유사도가 가장 높은 벡터를 찾는 과정입니다.

FAISS는 다양한 인덱싱 알고리즘을 제공합니다. 가장 일반적인 인덱싱 알고리즘은 다음과 같습니다.

1. **Flat Index**: 단순한 인덱싱 알고리즘으로, 벡터를 순서대로 저장합니다.
2. **IVF (Inverted File)**: 벡터를 인덱싱한 후, 유사한 벡터를 묶어 인덱싱합니다.
3. **HNSW (Hierarchical Navigable Small World Graph)**: 벡터를 인덱싱한 후, 유사한 벡터를 연결하는 그래프를 구성합니다.

FAISS는 다양한 응용 분야에서 사용됩니다. 예를 들어, 이미지 검색, 추천 시스템, 클러스터링 등 다양한 분야에서 FAISS를 사용할 수 있습니다.

FAISS를 사용하는 방법은 다음과 같습니다.

1. **인덱싱**: 벡터를 인덱싱하는 과정입니다.
2. **쿼리**: 사용자가 검색하고자 하는 벡터를 입력하는 과정입니다.
3. **검색**: 인덱싱된 벡터와 쿼리 벡터를 비교하여 유사도가 가장 높은 벡터를 찾는 과정입니다.

FAISS는 Python, C++, 
... (truncated)
~~~

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

## 이 코드에서 봐야 할 것

- 체인 정의는 `invoke()` 때와 거의 같습니다. 달라지는 부분은 호출 API와 청크를 소비하는 루프입니다.
- `stream()`은 동기 반복, `astream()`은 비동기 반복이라는 점만 이해해도 대부분의 서버 코드를 읽을 수 있습니다.
- 청크를 리스트에 모았다가 마지막에 `"".join(...)` 하는 패턴은 로그 저장이나 후처리에 자주 쓰입니다.
- `astream_events()`는 모델 출력만이 아니라 체인 전체 이벤트를 볼 수 있어 디버깅과 계측에 유리합니다.

## 실무에서 헷갈리는 지점

- 스트리밍을 쓰면 응답 형식 자체가 바뀐다고 생각하기 쉽지만, 최종 문자열은 그대로이고 전달 타이밍만 달라집니다.
- 비동기 스트리밍을 도입하면 상위 프레임워크도 async 흐름을 받아야 합니다.
- 이벤트 스트림은 디버깅에 좋지만, 단순 UI 출력만 필요하면 과한 선택일 수 있습니다.

## 체크리스트

- [ ] 같은 체인을 `invoke()`와 `stream()`으로 각각 실행해 볼 수 있다
- [ ] `astream()`과 `astream_events()`의 목적 차이를 설명할 수 있다
- [ ] FastAPI `StreamingResponse`로 스트리밍 청크를 넘기는 흐름을 이해했다

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
