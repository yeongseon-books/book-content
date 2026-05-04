---
title: Streaming — 실시간 출력 처리
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
seo_description: Streaming은 응답이 끝난 뒤 받는 방식이 아니라 생성 중간 상태를 그대로 소비하는 실행 모드입니다.
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

<!-- injected-output:start -->
**출력 결과**

    스트림(stream)은 데이터를 연속적인 흐름으로 처리하는 기술입니다. 
    스트림을 사용하면 데이터를 한 번에 처리하기보다는 작은 크기의 블록으로 처리할 수 있어, 메모리 사용과 성능이 향상됩니다.
    스트림은 일반적으로 네트워크 통신에서 데이터를 전송할 때 사용되며, 로깅, 데이터 분석, 스트리밍 서비스 등 다양한 분야에서 활용됩니다.

<!-- injected-output:end -->

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

![모델 직접 스트리밍과 체인 스트리밍 비교](../../../assets/langchain-101/05/05-01-basic-streaming.ko.png)
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

<!-- injected-output:start -->
**출력 결과**

    === LLM 직접 스트리밍 ===
    파이썬의 장점은 다음과 같습니다.

    1. **간단하고 읽기 쉬운 코드**: 파이썬은 매우 간결하고 읽기 쉬운 코드를 작성할 수 있습니다. 이는 파이썬이 문법이 용이하고, 명령을 간결하게 표현할 수 있기 때문입니다.

    2. **빠른 개발**: 파이썬은 빠른 개발 속도를 제공합니다. 파이썬의 간결한 코드와 강력한 라이브러리를 사용하면, 개발 시간을 단축하고, 프로젝트의 속도를 높일 수 있습니다.

    3. **다양한 응용**: 파이썬은 다양한 응용을 위한 플랫폼으로 사용할 수 있습니다. 웹 개발, 데이터 분석, 인공지능, 게임 개발, 데이터 시각화 등 다양한 분야에서 사용할 수 있습니다.

    4. **동적 타이핑**: 파이썬은 동적 타이핑을 지원합니다. 이는 개발자가 변수의 타입을 미리 선언하지 않아도, 런타임에 타입을 결정할 수 있기 때문에, 코드의 가독성을 향상시킵니다.

    5. **대용량 라이브러리**: 파이썬에는 다양한 대용량 라이브러리와 프레임워크가 존재합니다. NumPy, pandas, TensorFlow, Keras 등이 이러한 라이브러리 중 일부입니다. 이러한 라이브러리를 사용하면, 개발자가 빠르게 프로젝트를 완성할 수 있습니다.

    === 체인 스트리밍 ===
    벡터 검색은 벡터 공간에서 특정 벡터를 찾는 검색 알고리즘입니다. 벡터는 정의된 공간 내에서 특정 위치를 표현하는 데 사용되는 수학적 개념입니다. 벡터 검색은 다음과 같은 문제를 해결하는데 사용됩니다.

    * **이진 벡터 검색** : 이진 벡터는 0과 1로만 구성된 벡터입니다. 이진 벡터를 사용하는 이유는 비트 연산이 쉽기 때문입니다. 이진 벡터 검색은 특정 이진 벡터를 찾는 문제를 해결하는데 사용됩니다. 예를 들어, 특정 이진 벡터가 파일 시스템의 파일을 나타내면, 이진 벡터를 사용하여 특정 파일을 찾는 문제를 해결할 수 있습니다.
    * **유니버설 벡터 검색** : 유니버설 벡터 검색은 모든 벡터를 검색할 수 있는 알고리즘입니다. 이 알고리즘은 벡터 공간의 모든 벡터를 검색할 수 있으므로, 유니버설 벡터 검색은 유연한 검색 알고리즘입니다. 유니버설 벡터 검색은 벡터의 유사성을 측정하는 벡터 유사도 계산을 사용합니다. 벡터 유사도 계산은 두 벡터 사이의 유사성을 측정하는 데 사용됩니다.
    * **벡터 검색 알고리즘** : 벡터 검색 알고리즘은 다양한 알고리즘을 포함합니다. 예를 들어, 이진 탐색 트리, 하이퍼스페이스 탐색, 계층적 탐색 등이 있습니다. 이 알고리즘들은 벡터 공간에서 특정 벡터를 찾는 데 사용됩니다. 벡터 검색 알고리즘은 벡터의 특징을 분석하여 특정 벡터를 찾는 문제를 해결합니다.

<!-- injected-output:end -->

`end=""`, `flush=True`는 줄바꿈 없이 실시간으로 출력하기 위한 설정입니다. `StrOutputParser()`는 스트리밍에서 `AIMessageChunk.content`를 문자열로 꺼내줍니다.

---

## 스트리밍 출력 수집

![청크 수집 후 전체 문자열 복원 흐름](../../../assets/langchain-101/05/05-02-collecting-streamed-output.ko.png)
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

<!-- injected-output:start -->
**출력 결과**

    스트리밍: FAISS(Falconn Approximate Nearest Neighbor Search in Sublinear time)란, 유사한 벡터를 찾아내는 빠른 알고리즘입니다. FAISS는 Google의 연구원이 개발한 오픈 소스 라이브러리입니다.

    FAISS는 다음과 같은 특징을 가지고 있습니다:

    1. **빠른 검색**: FAISS는 벡터 검색을 위한 빠른 알고리즘입니다. 벡터 간의 유사성을 측정하여 가장 유사한 벡터를 찾을 수 있습니다.
    2. **유사성 측정**: FAISS는 다양한 유사성 측정 방법을 제공합니다. 유사성 측정 방법은 벡터 간의 유사성을 측정하여 유사한 벡터를 찾을 수 있습니다.
    3. **인덱스 생성**: FAISS는 인덱스를 생성하여 빠르게 검색할 수 있도록 합니다. 인덱스는 벡터를 빠르게 검색할 수 있도록 해 주는 데이터 구조입니다.
    4. **멀티 스레딩**: FAISS는 멀티 스레딩을 지원하여 병렬 처리를 하여 검색 속도를 빠르게 할 수 있습니다.

    FAISS는 다음과 같은 사용 사례를 가지고 있습니다:

    1. **이미지 검색**: FAISS는 이미지 검색에서 유용합니다. 이미지 간의 유사성을 측정하여 가장 유사한 이미지를 찾을 수 있습니다.
    2. **음악 검색**: FAISS는 음악 검색에서 유용합니다. 음악 간의 유사성을 측정하여 가장 유사한 음악을 찾을 수 있습니다.
    3. **데이터 분석**: FAISS는 데이터 분석에서 유용합니다. 벡터 간의 유사성을 측정하여 관련된 데이터를 찾을 수 있습니다.

    FAISS는 다음과 같은 장점을 가지고 있습니다:

    1. **빠른 검색 속도**: FAISS는 빠른 검색 속도를 제공하여 데이터 검색에 유용합니다.
    2. **유연한 인덱싱**: FAISS는 다양한 인덱싱 알고리즘을 제공하여 사용자에게 유연성을 제공합니다.
    3. **멀티 스레딩**: FAISS는 멀티 스레딩을 지원하여 병렬 처리를 하여 검색 속도를 빠르게 할 수 있습니다.

    FAISS는 다음과 같은 결함을 가지고 있습니다:

    1. **초기 셋업**: FAISS를 사용하기 전에 초기 셋업이 필요합니다. 초기 셋업을 하게 되면 FAISS를 사용하기에 더 쉬워집니다.
    2. **인덱싱 시간**: FAISS를 사용하기 전에 인덱싱 시간이 필요합니다. 인덱싱 시간이 길면 FAISS를 사용하기에 시간이 걸립니다.

    FAISS는 다음과 같은 대안을 가지고 있습니다:

    1. **Annoy**: Annoy는 FAISS와 유사한 오픈 소스 라이브러리입니다. Annoy는 FAISS보다 더 빠른 검색 속도를 제공합니다.
    2. **Hnswlib**: Hnswlib는 FAISS와 유사한 오픈 소스 라이브러리입니다. Hnswlib는 FAISS보다 더 유연한 인덱싱 알고리즘을 제공합니다.

    FAISS는 다음과 같은 사용 방법을 가지고 있습니다:

    1. **인덱싱**: 인덱싱은 벡터를 인덱싱하는 과정입니다. 인덱싱은 FAISS를 사용하기 전에 필요합니다.
    2. **검색**: 검색은 인덱싱된 벡터를 검색하는 과정입니다. 검색은 FAISS를 사용하는 과정입니다.
    3. **유사성 측정**: 유사성 측정은 벡터 간의 유사성을 측정하는 과정입니다. 유사성 측정은 FAISS를 사용하는 과정입니다.

    FAISS는 다음과 같은 코드 예시를 가지고 있습니다:

    ```cpp
    #include <faiss/IndexFlat.h>
    #include <faiss/IndexIVFFlat.h>
    #include <faiss/index.h>

    int main() {
      // 인덱싱
      faiss::IndexFlat L(128);

      // 벡터 생성
      std::vector<float> vecs(10 * 128);

      // 인덱싱
      L.add(vecs.data(), vecs.size() / 128);

      // 검색
      faiss::IndexIVFFlat IVF(L, 128, 10);
      IVF.train(vecs.data(), vecs.size() / 128);

      // 벡터 생성
      std::vector<float> query(128);
    ... (truncated)

<!-- injected-output:end -->

---

## astream() — 비동기 스트리밍

![async for 기반 비동기 스트리밍 흐름](../../../assets/langchain-101/05/05-03-astream-async-streaming.ko.png)
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

![체인 이벤트를 골라 처리하는 흐름](../../../assets/langchain-101/05/05-04-astream-events-for-fine-grained-control.ko.png)
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
