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
아스트림(Astream)은 한국에서 제공하는 스트리밍 서비스로, 비디오 콘텐츠를 제공하는 서비스입니다. 아스트림에서는 영화, 드라마, TV 프로그램, 애니메이션 등 다양한 콘텐츠를 제공하고 있습니다. 아스트림은 사용자들에게 다양한 콘텐츠를 제공하고, 사용자들의 취향에 맞는 콘텐츠를 추천하는 등의 서비스를 제공합니다.
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
파이썬의 장점은 다음과 같습니다.

1. **간결하고 읽기 쉬운 코드**: 파이썬은 일련의 명령을 짧고 간결하게 표현할 수 있는 언어입니다. 이를 통해 개발자가 빠르게 코드를 작성하고 수정할 수 있습니다. 또한, 파이썬의 코드는 읽기 쉬워 개발자들이 서로의 코드를 이해하고 수정하는 것이 쉬워집니다.

2. **객체 지향 프로그래밍(OOP)**: 파이썬은 객체 지향 프로그래밍(OOP)을 지원하는 언어입니다. OOP은 시스템을 객체로 바라보는 프로그래밍 패러드입니다. 이는 코드를 더 구조화하고 유지보수가 용이한 코드를 작성할 수 있게 해줍니다.

3. **동적 타이핑**: 파이썬은 동적 타이핑을 지원하는 언어입니다. 동적 타이핑은 변수의 타입을 변수 선언 시에 정의하지 않고, 변수를 할당할 때 타입을 결정하는 프로그래밍 패러드입니다. 이로 인해 개발자가 더 자유롭게 코드를 작성할 수 있습니다.

4. **많은 라이브러리와 모듈**: 파이썬에는 많은 라이브러리와 모듈이 존재합니다. 이러한 라이브러리와 모듈은 개발자가 작업을 더 빠르게 진행할 수 있도록 돕습니다. 예를 들어, 파이썬의 NumPy와 pandas 라이브러리는 데이터 분석을 위한 도구입니다.

5. **크로스 플랫폼**: 파이썬은 크로스 플랫폼 언어입니다. 이는 파이썬 프로그램을 Windows, macOS, Linux, 등 다양한 운영체제에서 실행할 수 있게 해줍니다. 또한, 파이썬은 Java와 C++ 등의 다른 프로그래밍 언어와 호환성도 있습니다.

=== 체인 스트리밍 ===
벡터 검색(Vector Search)은 큰 데이터 집합에서 유사한 벡터를 찾는 데 사용되는 알고리즘입니다. 벡터 검색에서 데이터는 고차원 벡터로 표현되며, 각 벡터는 특정 특징을 나타냅니다. 예를 들어, 이미지 데이터를 처리하는 경우 벡터는 픽셀 색상 정보로 구성된 벡터입니다.

벡터 검색은 두 가지 종류로 구분됩니다. 하나는 내적(Inner Product) 기법을 사용하는 것인데, 이는 두 벡터 간의 내적 값을 계산하여 유사도를 측정합니다. 대표적인 예로 Cosine Similarity가 있습니다. 다른 하나는 거리기반 기법을 사용하는 것인데, 이는 두 벡터 간의 거리를 계산하여 유사도를 측정합니다. 대표적인 예로 Euclidean Distance 및 L2 거리이지만, 내적기반 기법보다 거리기반 기법의 복잡성과 계산속도가 더 좋습니다.

벡터 검색 알고리즘은 HNSW(Hierarchical Navigable Small World), ANNOY(Approximate Nearest Neighbors Oh Yeah!), Faiss(Facebook AI Similarity Search) 등이 있습니다. 이러한 알고리즘은 큰 데이터 집합에서 유사한 벡터를 효율적으로 찾는 데 사용됩니다. 벡터 검색은 컴퓨터 비전, 자연어 처리, 추천 시스템 등 다양한 분야에서 사용됩니다.
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
스트리밍: FAISS(Falconn Index Search Library for Spark and ScaLDA)란, 대규모 벡터 집합을 효율적으로 검색하기 위한 오픈 소스 라이브러리입니다. 벡터는 일반적으로 고차원 공간에서 특징을 표현하기 위한 데이터의 표현입니다. FAISS는 밀도 기반 인덱스와 퀀트리 기반 인덱스로 구성된 라이브러리이며, 이를 통해 벡터 집합을 빠르게 검색할 수 있습니다.

FAISS는 다음 특징을 가지고 있습니다.

1. **효율성**: FAISS는 벡터 집합을 빠르게 검색할 수 있는 인덱스를 생성하는 것을 목표로 합니다. 이를 통해 대규모 벡터 집합을 효율적으로 관리할 수 있습니다.
2. **flexibility**: FAISS는 다양한 인덱싱 알고리즘을 지원합니다. 사용자는 라이브러리를 사용하여 적합한 인덱싱 알고리즘을 선택할 수 있습니다.
3. **오픈 소스**: FAISS는 오픈 소스 라이브러리이므로 무료로 사용할 수 있습니다.

FAISS의 주요 기능에는 다음이 포함됩니다.

1. **밀도 기반 인덱싱**: FAISS는 밀도 기반 인덱싱 알고리즘을 지원합니다. 이 알고리즘은 벡터 집합을 밀도 기반으로 인덱싱하여 벡터를 검색하는 것을 목표로 합니다.
2. **퀀트리 기반 인덱싱**: FAISS는 퀀트리 기반 인덱싱 알고리즘을 지원합니다. 이 알고리즘은 벡터 집합을 퀀트리 기반으로 인덱싱하여 벡터를 검색하는 것을 목표로 합니다.
3. **인덱스 생성**: FAISS는 인덱스를 생성하는 기능을 제공합니다. 사용자는 라이브러리를 사용하여 인덱스를 생성할 수 있습니다.
4. **벡터 검색**: FAISS는 벡터를 검색하는 기능을 제공합니다. 사용자는 라이브러리를 사용하여 벡터를 검색할 수 있습니다.

FAISS는 다양한 산업 분야에서 사용됩니다. 예를 들어, 이미지 검색, 추천 시스템, 자연어 처리 등에서 FAISS를 사용할 수 있습니다.

전체 글자 수: 937자
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
임베딩 벡터는 자연어 처리에서 사용되는 기술 중 하나입니다. 임베딩 벡터는 단어나 문장과 같은 텍스트 데이터를 숫자 벡터로 변환하여 컴퓨터가 이해할 수 있도록 합니다.

임베딩 벡터의 목표는 텍스트 데이터를 숫자로 변환하여 다음과 같은 tasks에서 사용할 수 있도록 하는 것입니다.

* 유사도 계산: 두 단어가 얼마나 유사한지 계산할 수 있습니다.
* 문장 분류: 문장의 내용을 분류할 수 있습니다. (예: 긍정적 문장 vs. 부정적 문장)
* 자연어 처리任务: 자연어 처리 tasks, chẳng hạn như Language Model, Question Answering, etc.

임베딩 벡터는 다음과 같은 방법으로 생성할 수 있습니다.

1. Word2Vec: 단어 간의 유사도를 기반으로 임베딩 벡터를 생성하는 방법입니다.
2. GloVe: 단어 간의 유사도를 기반으로 임베딩 벡터를 생성하는 방법입니다.
3. FastText: 단어의 서브워드 임베딩을 기반으로 임베딩 벡터를 생성하는 방법입니다.

임베딩 벡터의 예시는 다음과 같습니다.

* 단어 'king'과 'queen'의 임베딩 벡터는 유사한 벡터를 가질 수 있습니다.
* 단어 'dog'과 'cat'의 임베딩 벡터는 유사한 벡터를 가질 수 없습니다.

임베딩 벡터의 장점은 다음과 같습니다.

* 텍스트 데이터를 숫자로 변환하여 컴퓨터가 이해할 수 있도록 합니다.
* 자연어 처리 tasks에서 사용할 수 있습니다.
* 데이터의 크기를 줄일 수 있습니다.

임베딩 벡터의 단점은 다음과 같습니다.

* 텍스트 데이터의 의미를 완전히 캡처하지 못할 수 있습니다.
* 데이터의 크기를 줄일 수 있지만, 데이터의 의미를 잃을 수 있습니다.
스트리밍 시작: FAISS 인덱스
FAISS(Falicon Index for Similar Search)는 Facebook에서 개발한 고성능 인덱싱 기술입니다. FAISS는 이진 트리 인덱싱과 같은 기존 인덱싱 기술의 한계를 극복하기 위해 설계되었습니다. 

FAISS는 다음 기능을 제공합니다:

1. **고성능**: FAISS는 매우 빠른 검색 속도를 제공합니다. 
2. **대용량**: FAISS는 대용량 데이터 집합을 처리할 수 있습니다.
3. **고밀도**: FAISS는 밀도가 높은 데이터 집합을 처리할 수 있습니다.

FAISS의 작동 원리는 다음과 같습니다:

1. **인덱싱**: FAISS는 데이터를 인덱싱하는 과정에서, 데이터를 유사한 벡터로 군집화합니다. 각 군집은 고유한 인덱스 값을 가집니다.
2. **트리 구축**: 인덱싱이 끝나면, FAISS는 트리 구조를 구축합니다. 트리는 각 군집과 그에 속한 데이터를 연결합니다.
3. **검색**: 사용자는 검색 키를 제공하면, FAISS는 트리 구조를 탐색하여 가장 가까운 데이터를 찾습니다.

FAISS를 사용하면, 다음과 같은 이점이 있습니다:

* **빠른 검색 속도**: FAISS는 매우 빠른 검색 속도를 제공합니다.
* **대용량 처리**: FAISS는 대용량 데이터 집합을 처리할 수 있습니다.
* **고밀도 처리**: FAISS는 밀도가 높은 데이터 집합을 처리할 수 있습니다.

FAISS는 다음과 같은 분야에서 사용될 수 있습니다:

* **이미지 검색**: FAISS는 이미지 검색에 사용될 수 있습니다. 이미지 검색은 대용량 이미지 데이터를 처리해야 하기 때문에 FAISS의 대용량 처리 능력은 매우 유용합니다.
* **음성 검색**: FAISS는 음성 검색에 사용될 수 있습니다. 음성 검색은 대용량 음성 데이터를 처리해야 하기 때문에 FAISS의 대용량 처리 능력은 매우 유용합니다.
* **자연 언어 처리**: FAISS는 자연 언어 처리에 사용될 수 있습니다. 자연 언어 처리는 대용량 텍스트 데이터를 처리해야 하기 때문에 FAISS의 대용량 처리 능력은 매우 유용합니다.
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
