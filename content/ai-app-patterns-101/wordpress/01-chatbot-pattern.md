---
title: "바이브코딩을 위한 AI 앱 패턴 (1/6): 챗봇 패턴"
series: ai-app-patterns-101
episode: 1
language: ko
tags:
- Chatbot Pattern
- Sliding Window Memory
- SSE Streaming
- 바이브코딩
- Vibe Coding
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI 앱 패턴 (1/6): 챗봇 패턴

이 글은 **바이브코딩을 위한 AI 앱 패턴** 시리즈의 첫 번째 글입니다. 총 6편으로 구성되며, 실제 AI 앱을 만들 때 반복적으로 쓰이는 패턴들을 바이브코딩 관점에서 다룹니다.

---

바이브코딩으로 AI 앱을 만들 때 가장 먼저 만들게 되는 것이 챗봇입니다. "ChatGPT처럼 대화하는 것"이 목표인데, 막상 구현하면 "왜 이전 대화를 기억 못 하지?", "왜 긴 대화에서 느려지지?", "스트리밍은 어떻게 하지?" 같은 질문에 부딪힙니다.

챗봇 패턴의 핵심은 두 가지입니다. **메모리 전략**(대화 히스토리를 어떻게 관리하는가)과 **스트리밍**(답변을 어떻게 실시간으로 보여주는가). 이 두 가지를 제대로 설계하지 않으면 대화가 길어질수록 느려지고, 사용자가 답변을 기다리는 동안 아무 피드백이 없는 나쁜 UX가 됩니다.

> "챗봇의 메모리 전략은 사용자 경험과 비용을 동시에 결정합니다. 모든 것을 기억하려고 하면 비용이, 너무 빨리 잊으면 품질이 떨어집니다."

## 이 글에서 다룰 질문

1. 슬라이딩 윈도우 메모리와 요약 메모리는 어떻게 다른가요?
2. SSE(Server-Sent Events)로 스트리밍을 구현하는 방법은?
3. Redis 세션으로 여러 서버 간 대화를 공유하는 방법은?
4. 토큰 수를 효율적으로 추정하는 방법은?
5. 메모리 전략 선택 기준은 무엇인가요?

---

## 메모리 전략 비교

| 전략 | 특징 | 적합한 상황 | 단점 |
|------|------|------------|------|
| 슬라이딩 윈도우 | 최근 N개 메시지만 유지 | 대부분의 챗봇 | 오래된 대화 손실 |
| 요약 메모리 | 오래된 대화를 요약으로 압축 | 긴 대화가 필요한 경우 | 요약 API 호출 비용 |
| 전체 히스토리 | 모든 대화 유지 | 짧은 대화 전용 | 토큰 초과, 비용 폭발 |
| Redis 세션 | 외부 저장소에 보관 | 멀티 서버 환경 | 인프라 필요 |

## Before / After: 메모리 관리

**Before (모든 대화 누적)**
```python
messages = []
while True:
    user_input = input("You: ")
    messages.append({"role": "user", "content": user_input})
    response = llm.chat(messages)  # 대화가 길어질수록 비용 폭증
    messages.append({"role": "assistant", "content": response})
```

**After (슬라이딩 윈도우)**
```python
def build_windowed_messages(history: list[dict], system: str, max_tokens: int = 4000) -> list[dict]:
    """토큰 한도 안에서 최근 대화만 선택합니다."""
    result = [{"role": "system", "content": system}]
    current_tokens = estimate_tokens(system)

    # 최신 메시지부터 역순으로 추가
    for msg in reversed(history):
        msg_tokens = estimate_tokens(msg["content"])
        if current_tokens + msg_tokens > max_tokens:
            break
        result.insert(1, msg)
        current_tokens += msg_tokens

    return result
```

## SSE 스트리밍 구현

스트리밍은 사용자가 답변이 생성되는 것을 실시간으로 볼 수 있게 합니다.

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

async def stream_chat_response(messages: list[dict]):
    """SSE 형식으로 응답을 스트리밍합니다."""
    client = OpenAI()
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True
    )

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            data = json.dumps({"text": delta.content}, ensure_ascii=False)
            yield f"data: {data}\n\n"

    yield "data: [DONE]\n\n"

@app.post("/chat/stream")
async def chat_stream(request: dict):
    messages = request["messages"]
    return StreamingResponse(
        stream_chat_response(messages),
        media_type="text/event-stream"
    )
```

## Redis 세션으로 멀티 서버 지원

```python
import redis
import json

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

def save_session(session_id: str, messages: list[dict], ttl: int = 3600):
    """대화 히스토리를 Redis에 저장합니다."""
    redis_client.setex(
        f"chat:{session_id}",
        ttl,
        json.dumps(messages, ensure_ascii=False)
    )

def load_session(session_id: str) -> list[dict]:
    """Redis에서 대화 히스토리를 불러옵니다."""
    data = redis_client.get(f"chat:{session_id}")
    return json.loads(data) if data else []
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 모든 대화 히스토리 전송 | 토큰 초과, 비용 폭증 | 슬라이딩 윈도우 또는 요약 적용 |
| 스트리밍 없이 긴 응답 | 사용자가 긴 시간 기다림 | SSE 스트리밍 구현 |
| 메모리를 서버에만 저장 | 서버 재시작 시 대화 소멸 | Redis 등 외부 저장소 사용 |
| 토큰 추정 없이 메시지 추가 | 예상치 못한 컨텍스트 초과 | estimate_tokens로 사전 확인 |

## AI 팁

요약 메모리 전략을 쓸 때는 LLM에게 대화를 요약하게 하되, 반드시 "사용자의 핵심 정보(이름, 목적, 선호도)"를 보존하도록 요약 프롬프트를 작성하세요.

```python
def summarize_history(messages: list[dict]) -> str:
    summary_prompt = """다음 대화를 요약하세요.
    반드시 포함할 내용:
    - 사용자가 언급한 핵심 정보 (이름, 목적, 선호도)
    - 해결된 문제와 미해결 문제
    - 다음 대화에서 참고해야 할 중요 사항

    대화:
    """ + "\n".join([f"{m['role']}: {m['content']}" for m in messages])

    return llm.chat([{"role": "user", "content": summary_prompt}])
```

## 체크리스트

- [ ] 메모리 전략을 선택하고 토큰 한도를 설정했다
- [ ] SSE 스트리밍으로 실시간 답변을 구현했다
- [ ] 세션 ID로 사용자별 대화를 분리했다
- [ ] 서버 재시작 후에도 대화가 유지된다
- [ ] 토큰 사용량을 모니터링하고 있다

## 처음 질문으로 돌아가기

**슬라이딩 윈도우 vs 요약 메모리?** 슬라이딩 윈도우는 단순하고 빠르지만 오래된 대화를 잃습니다. 요약 메모리는 더 많은 맥락을 보존하지만 추가 API 호출이 필요합니다. 대부분의 챗봇에는 슬라이딩 윈도우로 시작하는 것을 권장합니다.

**SSE 스트리밍 구현은?** OpenAI `stream=True` 옵션으로 청크를 받고, 각 청크를 `data: {...}\n\n` 형식으로 클라이언트에 전송합니다.

**Redis 세션은 언제 필요한가요?** 여러 서버 인스턴스가 동일한 사용자 대화에 접근해야 하거나, 서버 재시작 후에도 대화를 유지해야 할 때.

**토큰 수 추정 방법은?** `tiktoken` 라이브러리로 정확하게 계산하거나, 영어 기준 `글자수 / 4`로 빠르게 추정합니다.

**메모리 전략 선택 기준은?** 대화 길이, 비용 예산, 사용자 경험 요구사항에 따라 다릅니다. 짧은 대화는 전체 유지, 중간은 슬라이딩 윈도우, 긴 대화는 요약 메모리.

## 정리

챗봇 패턴의 핵심은 메모리 전략과 스트리밍입니다. 대화가 길어질수록 모든 히스토리를 전송하면 비용이 폭증하므로 슬라이딩 윈도우나 요약 메모리로 관리해야 합니다. SSE 스트리밍은 답변이 생성되는 동안 사용자에게 진행 상황을 보여줘 UX를 크게 개선합니다.

다음 글에서는 문서 기반 질문 답변 시스템인 **RAG QA 패턴**을 다룹니다.

## 참고 자료

- [AI 앱 패턴 원문: 챗봇 패턴](../ko/01-chatbot-pattern.md)
- [OpenAI Streaming Guide](https://platform.openai.com/docs/api-reference/streaming)

---

<!-- toc:begin -->
## 시리즈 목차

1. **바이브코딩을 위한 AI 앱 패턴 (1/6): 챗봇 패턴 (현재 글)**
2. [바이브코딩을 위한 AI 앱 패턴 (2/6): RAG QA 패턴](./02-rag-qa-pattern.md)
3. [바이브코딩을 위한 AI 앱 패턴 (3/6): 문서 어시스턴트](./03-document-assistant.md)
4. [바이브코딩을 위한 AI 앱 패턴 (4/6): 에이전트 도구 패턴](./04-agent-tool-pattern.md)
5. [바이브코딩을 위한 AI 앱 패턴 (5/6): 워크플로우 자동화](./05-workflow-automation.md)
6. [바이브코딩을 위한 AI 앱 패턴 (6/6): Human-in-the-Loop](./06-human-in-the-loop.md)
<!-- toc:end -->

Tags: Chatbot Pattern, Sliding Window Memory, SSE Streaming, 바이브코딩, Vibe Coding
