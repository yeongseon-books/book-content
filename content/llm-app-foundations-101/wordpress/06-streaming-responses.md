---
title: "바이브코딩을 위한 LLM 앱 기초 (6/6): 스트리밍 응답 처리 — 실시간으로 출력 받기"
series: llm-app-foundations-101
episode: 6
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM
- Streaming
- FastAPI
- Python
---

# 바이브코딩을 위한 LLM 앱 기초 (6/6): 스트리밍 응답 처리 — 실시간으로 출력 받기

이 글은 **바이브코딩을 위한 LLM 앱 기초** 시리즈의 마지막 글입니다. API 호출, 토큰, 프롬프트, Few-shot, 대화 상태를 통합하고 스트리밍 응답으로 완성합니다.

---

API, 토큰, 프롬프트, 대화 상태를 모두 알았습니다. 이제 완성입니다. 하지만 사용자 경험 관점에서 한 가지가 더 있습니다. 5초 응답을 기다리는 것과 첫 단어가 0.3초 만에 나오는 것은 다릅니다. 스트리밍이 그 차이를 만듭니다.

바이브코딩에서 만드는 챗봇이 사용자에게 보이는 순간은 스트리밍이 중요합니다. API 호출부터 스트리밍까지 통합된 챗봇을 완성하는 것이 이 시리즈의 마무리입니다.

> "스트리밍은 기다리는 경험을 대화하는 경험으로 바꿉니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. stream=True로 응답이 어떻게 달라지나요?
2. 스트리밍 청크에서 텍스트를 어떻게 추출하나요?
3. 스트리밍 중 대화 기록은 어떻게 저장하나요?
4. FastAPI에서 스트리밍 응답을 어떻게 구현하나요?
5. 스트리밍 중 오류가 나면 어떻게 처리하나요?

---

## 기본 스트리밍

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def stream_chat(messages: list) -> str:
    full_response = ""
    with client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
    ) as stream:
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                print(delta.content, end="", flush=True)
                full_response += delta.content
    print()  # 줄바꿈
    return full_response
```

## 스트리밍 챗봇

```python
class StreamingChatbot:
    def __init__(self, system_prompt: str, max_tokens: int = 4000):
        self.messages = [{"role": "system", "content": system_prompt}]
        self.max_tokens = max_tokens

    def chat(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})

        full_response = ""
        try:
            with client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.messages,
                stream=True,
            ) as stream:
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        print(content, end="", flush=True)
                        full_response += content
        except Exception as e:
            full_response = f"오류: {e}"

        self.messages.append({"role": "assistant", "content": full_response})
        return full_response
```

## FastAPI 스트리밍 엔드포인트

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

app = FastAPI()

class ChatRequest(BaseModel):
    session_id: str
    message: str

sessions: dict = {}

@app.post("/chat/stream")
async def stream_endpoint(request: ChatRequest):
    session = sessions.setdefault(request.session_id, [
        {"role": "system", "content": "당신은 도움이 되는 AI 어시스턴트입니다."}
    ])
    session.append({"role": "user", "content": request.message})

    async def generate():
        full_response = ""
        with client.chat.completions.create(
            model="gpt-4o-mini",
            messages=session,
            stream=True,
        ) as stream:
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield f"data: {json.dumps({'content': content})}\n\n"

        session.append({"role": "assistant", "content": full_response})
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

## Before / After

| 항목 | Before (invoke) | After (stream) |
|------|----------------|----------------|
| 첫 토큰까지 | 전체 대기 | 즉시 시작 |
| 사용자 경험 | 로딩 스피너 | 타이핑 효과 |
| FastAPI 통합 | JSONResponse | StreamingResponse |
| 오류 처리 | 예외 그대로 | 오류 메시지 스트림 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| flush=True 없음 | 버퍼링 지연 | print(chunk, end="", flush=True) |
| 스트리밍 후 기록 없음 | 대화 기억 안 됨 | full_response를 messages에 추가 |
| 동기 in FastAPI | 블로킹 | async 스트리밍 사용 |
| 오류 미처리 | 연결 끊김 | try-except 포함 |

---

## AI 활용 팁

```
스트리밍을 지원하는 멀티턴 챗봇을 만들어줘.
stream=True로 청크를 실시간 출력하고, 스트리밍 완료 후 full_response를 messages에 추가해줘.
FastAPI에서 SSE(text/event-stream) 형식으로 클라이언트에 전달해줘.
오류 발생 시 오류 메시지를 스트림으로 전달해줘.
```

---

## 체크리스트

- [ ] stream=True 스트리밍 구현
- [ ] flush=True 설정
- [ ] full_response 누적 후 messages에 추가
- [ ] FastAPI StreamingResponse 통합
- [ ] SSE data: 형식 사용
- [ ] 스트리밍 중 오류 처리

---

## 처음 질문으로 돌아가기

"챗봇에 스트리밍이 꼭 필요한가요?" — 필수는 아닙니다. 하지만 응답이 1초 이상 걸리는 서비스에서 스트리밍은 사용자 체감 속도를 크게 개선합니다. 이 시리즈에서 배운 API 호출, 토큰 관리, 프롬프트, 대화 상태에 스트리밍이 더해지면 실제 서비스 수준의 챗봇이 됩니다.

---

## 정리

- stream=True로 응답을 청크 단위로 실시간 수신한다
- full_response에 청크를 누적한 뒤 messages에 추가해 대화 기록을 유지한다
- FastAPI StreamingResponse + SSE로 클라이언트에 실시간 전달한다
- 오류 발생 시 스트림에 오류 메시지를 포함해 연결을 안전하게 종료한다

---

## 참고 자료

- [OpenAI 스트리밍 문서](https://platform.openai.com/docs/api-reference/streaming)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 기본 스트리밍
- 스트리밍 챗봇
- FastAPI 스트리밍 엔드포인트
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LLM, Streaming, FastAPI, Python
