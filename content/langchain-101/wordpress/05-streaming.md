---
title: "바이브코딩을 위한 LangChain (5/6): Streaming — 실시간 출력 처리"
series: langchain-101
episode: 5
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LangChain
- Streaming
- Python
- LLM
---

# 바이브코딩을 위한 LangChain (5/6): Streaming — 실시간 출력 처리

이 글은 **바이브코딩을 위한 LangChain** 시리즈의 다섯 번째 글입니다. LangChain 체인에서 스트리밍 출력을 처리하고 중간 단계 이벤트를 구독하는 방법을 다룹니다.

---

LLM 호출의 가장 큰 UX 문제는 대기 시간입니다. 5초짜리 응답을 기다리는 것과 첫 단어가 0.3초 만에 나오는 것은 체감이 완전히 다릅니다. `.stream()`이 그 차이를 만듭니다.

바이브코딩으로 AI에게 "스트리밍 구현해줘"라고 하면 기본 `.stream()` 코드가 나옵니다. 그런데 도구 호출 결과를 스트리밍하는 방법, 중간 단계 이벤트를 구독하는 방법을 모르면 복잡한 체인에서 스트리밍을 활용하기 어렵습니다.

> "스트리밍은 응답 시작 시간이 전체 대기 시간보다 중요할 때 씁니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. `.stream()`과 `.astream()`의 차이가 무엇인가요?
2. 스트리밍 청크가 문자 단위로 오나요, 토큰 단위로 오나요?
3. 중간 단계(Retriever 결과, 도구 실행)를 스트리밍으로 받을 수 있나요?
4. FastAPI에서 스트리밍 응답을 어떻게 구현하나요?
5. 스트리밍 중 오류가 나면 어떻게 처리하나요?

---

## 기본 스트리밍

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

chain = (
    ChatPromptTemplate.from_template("{question}")
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)

for chunk in chain.stream({"question": "Python의 역사를 설명해주세요"}):
    print(chunk, end="", flush=True)
```

## 비동기 스트리밍

FastAPI 같은 비동기 환경에서는 `.astream()`을 사용합니다.

```python
async def stream_response(question: str):
    async for chunk in chain.astream({"question": question}):
        yield chunk
```

## 중간 단계 이벤트 구독

```python
async def stream_with_events(question: str):
    async for event in rag_chain.astream_events(
        {"question": question},
        version="v2",
    ):
        event_type = event["event"]

        if event_type == "on_retriever_end":
            # Retriever 완료 시 검색된 문서 목록
            docs = event["data"]["output"]
            print(f"[검색됨] {len(docs)}개 문서")

        elif event_type == "on_chat_model_stream":
            # LLM 스트리밍 청크
            chunk = event["data"]["chunk"].content
            print(chunk, end="", flush=True)
```

## FastAPI 통합

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/stream")
async def stream_endpoint(question: str):
    async def generate():
        async for chunk in chain.astream({"question": question}):
            yield f"data: {chunk}\n\n"  # SSE 형식

    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

## Before / After

| 항목 | Before (.invoke()) | After (.stream()) |
|------|-------------------|-------------------|
| 첫 토큰까지 | 전체 대기 | 즉시 출력 시작 |
| UX | 로딩 스피너 | 타이핑 효과 |
| 중간 단계 확인 | 불가 | astream_events |
| FastAPI 통합 | JSONResponse | StreamingResponse |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 동기 .stream() in async | 블로킹 | .astream() 사용 |
| flush=True 없음 | 버퍼링으로 지연 출력 | `print(chunk, end="", flush=True)` |
| 이벤트 버전 없음 | astream_events 오류 | version="v2" 필수 |
| 스트리밍 중 오류 무처리 | 연결 끊김 | try-except로 감싸기 |

---

## AI 활용 팁

```
LangChain RAG 체인에 스트리밍을 추가해줘.
동기 환경은 .stream(), FastAPI 비동기 환경은 .astream()을 사용해줘.
astream_events로 Retriever 완료 이벤트와 LLM 스트리밍 청크를 분리해서 처리해줘.
FastAPI StreamingResponse로 SSE(Server-Sent Events) 형식으로 클라이언트에 전달해줘.
```

---

## 체크리스트

- [ ] 동기 .stream() 기본 구현
- [ ] 비동기 .astream() 구현
- [ ] astream_events로 중간 단계 이벤트 구독
- [ ] FastAPI StreamingResponse 통합
- [ ] 스트리밍 중 오류 처리
- [ ] flush=True 설정

---

## 처음 질문으로 돌아가기

"스트리밍이 꼭 필요한가요? invoke도 되는데요" — 5초 응답을 기다리는 사용자와 0.3초부터 타이핑이 나오는 사용자의 체감은 다릅니다. 챗봇, 긴 텍스트 생성, LLM API 응답 시간이 긴 서비스에서는 스트리밍이 UX의 핵심입니다.

---

## 정리

- `.stream()`은 동기, `.astream()`은 비동기 스트리밍이다
- `astream_events(version="v2")`로 Retriever 완료, LLM 청크 등 중간 이벤트를 구독한다
- FastAPI에서는 `StreamingResponse + SSE`로 클라이언트에 전달한다
- `flush=True`와 비동기 처리를 빠뜨리지 않는다

---

## 참고 자료

- [LangChain 스트리밍 문서](https://python.langchain.com/docs/concepts/streaming/)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 기본 스트리밍
- 비동기 스트리밍
- 중간 단계 이벤트 구독
- FastAPI 통합
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LangChain, Streaming, Python, LLM
