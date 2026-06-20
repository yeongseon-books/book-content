---
title: "바이브코딩을 위한 LangChain (6/6): 실전 체인 조립 — 컴포넌트를 하나로 연결하기"
series: langchain-101
episode: 6
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LangChain
- RAG
- Agent
- Python
---

# 바이브코딩을 위한 LangChain (6/6): 실전 체인 조립 — 컴포넌트를 하나로 연결하기

이 글은 **바이브코딩을 위한 LangChain** 시리즈의 마지막 글입니다. LCEL, Prompt, Retriever, Tool Calling, Streaming을 하나의 실전 체인으로 통합합니다.

---

LCEL, Prompt, Retriever, Tool, Streaming — 각각을 만들었습니다. 이제 하나의 체인으로 조립해야 합니다. "그냥 파이프로 연결하면 되지 않나요?"라고 생각하지만, 실제 서비스에서는 메모리(대화 기록), 에러 처리, 스트리밍, 로깅이 모두 통합되어야 합니다.

바이브코딩으로 AI에게 "다 연결해줘"라고 하면 연결이 됩니다. 하지만 대화 기록이 어떻게 관리되는지, 체인이 실패했을 때 어떤 에러가 나는지, 어떻게 로그를 남기는지 — 이해 없이는 유지보수가 어렵습니다.

이 글에서는 대화 기록 관리, 에러 처리, 로깅이 포함된 프로덕션 수준 체인을 구성합니다.

> "체인 조립의 완성은 기능이 아니라 운영 가능성입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 대화 기록을 체인에 포함하는 방법이 있나요?
2. 체인 실행 중 오류가 나면 어디서 잡아야 하나요?
3. LangSmith 없이 체인 실행을 로깅하는 방법이 있나요?
4. 체인을 FastAPI 엔드포인트로 노출하는 방법이 있나요?
5. 체인 응답 시간을 측정하는 방법이 있나요?

---

## 대화 기록 관리

```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

store = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

chain_with_history = RunnableWithMessageHistory(
    base_chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)

# 세션 ID로 대화 유지
response = chain_with_history.invoke(
    {"question": "안녕하세요"},
    config={"configurable": {"session_id": "user_123"}},
)
```

## 에러 처리

```python
from langchain_core.runnables import RunnableLambda

def safe_chain_invoke(chain, inputs: dict) -> dict:
    try:
        result = chain.invoke(inputs)
        return {"success": True, "result": result}
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }
```

## 실행 시간 로깅

```python
import time
import logging

logger = logging.getLogger(__name__)

def timed_invoke(chain, inputs: dict) -> dict:
    start = time.time()
    result = chain.invoke(inputs)
    elapsed = time.time() - start
    logger.info(f"체인 실행 시간: {elapsed:.2f}초")
    return result
```

## FastAPI 통합 체인

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    session_id: str
    question: str

@app.post("/chat")
async def chat(request: ChatRequest):
    async def generate():
        async for chunk in chain_with_history.astream(
            {"question": request.question},
            config={"configurable": {"session_id": request.session_id}},
        ):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
```

---

## Before / After

| 항목 | Before (기본 체인) | After (프로덕션 체인) |
|------|------------------|-----------------------|
| 대화 기록 | 없음 | InMemoryChatMessageHistory |
| 에러 처리 | 예외 그대로 | safe_chain_invoke |
| 실행 시간 | 모름 | 로깅으로 측정 |
| API 노출 | 없음 | FastAPI + 스트리밍 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| session_id 미설정 | 모든 대화 혼합 | configurable session_id |
| 에러 미처리 | 500 오류 | safe_chain_invoke |
| 메모리 무한 증가 | OOM | 대화 기록 최대 길이 설정 |
| 동기 in FastAPI async | 블로킹 | .astream() 사용 |

---

## AI 활용 팁

```
LangChain RAG 체인에 대화 기록, 에러 처리, 스트리밍을 통합해줘.
RunnableWithMessageHistory로 session_id 기반 대화 기록을 관리해줘.
FastAPI 엔드포인트로 노출하고, StreamingResponse로 응답해줘.
실행 시간을 로깅하고, 에러 시 success/error 딕셔너리를 반환해줘.
```

---

## 체크리스트

- [ ] RunnableWithMessageHistory로 대화 기록 관리
- [ ] session_id 기반 세션 분리
- [ ] safe_chain_invoke로 에러 처리
- [ ] 실행 시간 로깅
- [ ] FastAPI POST /chat 엔드포인트
- [ ] 비동기 스트리밍 응답

---

## 처음 질문으로 돌아가기

"LangChain 컴포넌트를 다 배웠는데 실제 서비스를 어떻게 만드나요?" — 대화 기록, 에러 처리, 로깅, FastAPI 통합이 추가되면 프로덕션 수준이 됩니다. RunnableWithMessageHistory로 세션 기반 대화를 관리하고, StreamingResponse로 실시간 응답을 제공하면 사용자가 체감하는 서비스가 완성됩니다.

---

## 정리

- RunnableWithMessageHistory로 session_id 기반 대화 기록을 관리한다
- safe_chain_invoke로 체인 오류를 구조화된 형태로 반환한다
- 실행 시간을 로깅해 성능 병목을 파악한다
- FastAPI + StreamingResponse로 실시간 스트리밍 API를 노출한다

---

## 참고 자료

- [RunnableWithMessageHistory 문서](https://python.langchain.com/docs/how_to/message_history/)
- [LangChain FastAPI 통합](https://python.langchain.com/docs/how_to/streaming/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 대화 기록 관리
- 에러 처리
- 실행 시간 로깅
- FastAPI 통합 체인
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LangChain, RAG, Agent, Python
