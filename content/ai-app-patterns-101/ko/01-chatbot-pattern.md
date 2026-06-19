---
series: ai-app-patterns-101
episode: 1
title: "AI App Patterns 101 (1/6): Chatbot 패턴"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Chatbot
  - LLM
  - ConversationMemory
  - FastAPI
  - Streaming
seo_description: 슬라이딩 윈도우·요약 메모리·세션 기반 대화 유지 방식과 FastAPI SSE 스트리밍까지 챗봇 구현 핵심 패턴을 정리합니다
last_reviewed: '2026-06-20'
---

# AI App Patterns 101 (1/6): Chatbot 패턴

챗봇은 가장 빠르게 프로토타입을 만들 수 있는 LLM 애플리케이션입니다. 하지만 "모델 API를 한 번 호출하면 된다"는 생각으로 시작한 프로젝트가 얼마 지나지 않아 대화 흐름이 끊기거나, 토큰 비용이 폭증하거나, 긴 대화에서 앞 내용을 잊어버리는 문제에 부딪힙니다. 챗봇을 프로덕션까지 가져가려면 메모리 전략, 토큰 예산 관리, 스트리밍 응답이라는 세 축을 함께 설계해야 합니다.

이 글은 AI App Patterns 101 시리즈의 1번째 글입니다.

![Chatbot 패턴 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/01/01-01-concept-at-a-glance.ko.png)
*대화 메모리와 스트리밍이 결합된 챗봇 패턴 전체 흐름*

## 이 글에서 다룰 문제

- 챗봇이 이전 대화를 기억하려면 어떤 메모리 전략이 필요할까요?
- 대화가 길어질수록 토큰 비용이 폭증하는 문제를 어떻게 막을 수 있을까요?
- 슬라이딩 윈도우와 요약 메모리는 각각 어떤 상황에 적합할까요?
- FastAPI에서 스트리밍 응답을 안전하게 구현하려면 어떻게 해야 할까요?
- 세션 기반 대화 관리를 프로덕션에서 운영할 때 무엇을 챙겨야 할까요?

## 핵심 개념 한 줄 정리

- **Sliding Window**: 최근 N개 메시지만 컨텍스트에 포함하는 가장 단순한 메모리 전략입니다.
- **Summary Memory**: 오래된 대화를 요약해 압축하고, 요약본과 최근 메시지를 합쳐 컨텍스트를 만드는 전략입니다.
- **Session**: 사용자별로 독립된 대화 이력을 격리하는 논리적 단위입니다.
- **Token Budget**: 프롬프트와 응답 합산 토큰에 상한선을 두는 설계 원칙입니다.
- **SSE(Server-Sent Events)**: 서버가 생성한 텍스트를 청크 단위로 클라이언트에 밀어 주는 HTTP 스트리밍 방식입니다.

## 메모리 전략 비교

대화 히스토리를 어떻게 다루느냐가 챗봇 품질과 비용을 동시에 결정합니다.

| 전략 | 토큰 비용 | 구현 복잡도 | 적합 상황 | 단점 |
|---|---|---|---|---|
| 전체 히스토리 | 매우 높음 | 낮음 | 짧은 데모 | 장기 대화에서 비용 폭발 |
| 슬라이딩 윈도우 | 고정 | 낮음 | 일반 챗봇 | 오래된 맥락 손실 |
| 요약 메모리 | 중간 | 중간 | 긴 대화 | 요약 품질에 의존 |
| 벡터 검색 메모리 | 낮음 | 높음 | 지식 기반 챗봇 | 검색 레이턴시 추가 |

슬라이딩 윈도우는 구현이 가장 쉽고, 대부분의 고객 지원 챗봇에서는 이 방식으로도 충분합니다. 요약 메모리는 1시간 넘는 세션이 발생하는 상담 서비스나 개인 비서 서비스에서 빛을 발합니다.

## 구체적인 시나리오: 어느 방식을 선택해야 할까?

**시나리오 A — 고객 지원 챗봇**: 사용자 한 명이 결제 문제로 챗봇과 10~15번 주고받습니다. 대부분의 대화가 현재 세션 주제에 집중되므로 슬라이딩 윈도우(window_size=10)로 충분합니다.

**시나리오 B — 개인 학습 비서**: 사용자가 같은 주제를 여러 날에 걸쳐 공부하면서 "지난번에 배운 내용 이어서..."라는 표현을 자주 씁니다. 오래된 맥락을 요약해 보존하는 Summary Memory가 적합합니다.

**시나리오 C — 법률 문서 검토 보조**: "조항 3항과 7항의 충돌 가능성"처럼 문서 특정 부분을 자주 언급합니다. 벡터 검색 메모리로 필요한 절만 검색해서 컨텍스트에 주입하는 방식이 비용 효율적입니다.

## 실습: 슬라이딩 윈도우 메모리

가장 먼저 구현해야 할 기본 패턴입니다. 최근 K개 메시지만 LLM에 전달해 컨텍스트 크기를 일정하게 유지합니다.

```python
from openai import OpenAI

client = OpenAI()

def sliding_window_chat(
    history: list[dict],
    user_message: str,
    system_prompt: str = "You are a helpful assistant.",
    window_size: int = 10,
    max_tokens: int = 1024,
) -> str:
    """슬라이딩 윈도우 메모리로 대화를 유지합니다."""
    # 최근 window_size 개 메시지만 유지
    recent = history[-window_size:] if len(history) > window_size else history

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(recent)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


# 사용 예시: 고객 지원 시나리오
history: list[dict] = []
turns = [
    "안녕하세요, 파이썬 튜터링을 받고 싶어요.",
    "리스트 컴프리헨션을 설명해 주세요.",
    "방금 설명한 내용을 실제 예제로 보여 주세요.",
    "그러면 딕셔너리 컴프리헨션도 비슷한 방식인가요?",
    "네, 이해했어요. 그런데 처음에 말씀드린 튜터링 목표가 뭐였죠?",
]

for user_input in turns:
    reply = sliding_window_chat(history, user_input)
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": reply})
    print(f"User: {user_input}\nAssistant: {reply}\n{'='*50}")
```

window_size=10일 때 히스토리가 10개를 넘으면 오래된 메시지는 잘려 나갑니다. 위 예시의 마지막 질문("처음에 말씀드린 튜터링 목표")은 히스토리가 짧아서 잘 답하지만, 30번째 턴 이후에는 "첫 메시지"가 윈도우 밖으로 밀려납니다. 이것이 Summary Memory가 필요한 신호입니다.

## 실습: 요약 메모리

대화가 일정 길이를 초과하면 오래된 부분을 요약해 압축합니다. 이 방식은 맥락 손실을 최소화하면서 토큰을 아낍니다.

```python
from openai import OpenAI

client = OpenAI()


def summarize_history(messages: list[dict]) -> str:
    """오래된 대화 이력을 핵심만 남겨 요약합니다."""
    conversation_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in messages
    )
    summary_prompt = (
        "다음 대화를 핵심 정보만 남겨 3문장 이내로 요약하세요. "
        "사용자의 목적, 결정된 사항, 미결 사항을 포함하세요.\n\n"
        f"{conversation_text}"
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": summary_prompt}],
        max_tokens=256,
    )
    return resp.choices[0].message.content


def summary_memory_chat(
    history: list[dict],
    user_message: str,
    system_prompt: str = "You are a helpful assistant.",
    trigger_size: int = 20,
    keep_recent: int = 6,
) -> tuple[str, list[dict]]:
    """요약 메모리를 사용하는 챗봇입니다."""
    if len(history) > trigger_size:
        older = history[:-keep_recent]
        recent = history[-keep_recent:]
        summary = summarize_history(older)
        merged_system = f"{system_prompt}\n\n[이전 대화 요약]\n{summary}"
        history = recent
    else:
        merged_system = system_prompt

    messages = [{"role": "system", "content": merged_system}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=1024,
    )
    reply = response.choices[0].message.content
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    return reply, history


# 요약 메모리 시나리오: 긴 학습 세션
history: list[dict] = []
long_session = [
    "파이썬 학습을 시작하려고 해요. 기초부터 배우고 싶어요.",
    "변수와 자료형을 먼저 배우고 싶어요.",
    "리스트를 배웠는데, 튜플과 차이점이 뭔가요?",
    "딕셔너리는 어떻게 사용하나요?",
    "이제 제어문을 배우고 싶어요.",
    "for 루프 예제를 더 보여주세요.",
    "while 루프는 언제 쓰나요?",
    "함수를 만드는 법을 알려주세요.",
    "람다 함수가 뭔가요?",
    "클래스와 객체는 어떻게 다른가요?",
    # 히스토리가 trigger_size(20)를 넘으면 요약 트리거
]
for msg in long_session:
    reply, history = summary_memory_chat(history, msg)
    print(f"Q: {msg[:40]}...\nA: {reply[:80]}...\n")
```

요약이 실제로 언제 발동했는지 확인하려면 `len(history) > trigger_size` 분기를 로그로 남기는 것이 좋습니다. 요약 품질이 나쁘면 초반 대화의 맥락이 왜곡될 수 있으므로, 요약 결과를 별도로 저장하고 검토하는 루틴을 운영 초기에 두는 것을 권장합니다.

## 실습: FastAPI SSE 스트리밍

사용자가 첫 글자가 나오기까지 기다리는 시간이 길면 챗봇 경험이 크게 나빠집니다. SSE 스트리밍으로 토큰이 생성되는 즉시 클라이언트에 전달합니다.

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import OpenAI
import json

app = FastAPI()
client = OpenAI()

# 세션별 대화 이력 저장소 (프로덕션에서는 Redis 사용 권장)
sessions: dict[str, list[dict]] = {}


def stream_chat_response(session_id: str, user_message: str):
    """스트리밍 응답을 SSE 형식으로 생성합니다."""
    history = sessions.get(session_id, [])
    window = history[-10:]

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        *window,
        {"role": "user", "content": user_message},
    ]

    full_reply = []
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
        max_tokens=1024,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            full_reply.append(delta.content)
            yield f"data: {json.dumps({'text': delta.content})}\n\n"

    # 완료 후 히스토리 업데이트 (스트림 완료 후에만 저장)
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": "".join(full_reply)})
    sessions[session_id] = history
    yield "data: [DONE]\n\n"


@app.post("/chat/{session_id}")
async def chat_endpoint(session_id: str, body: dict):
    user_message = body.get("message", "")
    return StreamingResponse(
        stream_chat_response(session_id, user_message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Nginx 역방향 프록시 버퍼링 비활성화
        },
    )


@app.delete("/chat/{session_id}")
async def clear_session(session_id: str):
    sessions.pop(session_id, None)
    return {"status": "cleared"}


@app.get("/chat/{session_id}/history")
async def get_history(session_id: str):
    """세션 히스토리 조회 (디버깅용)."""
    history = sessions.get(session_id, [])
    return {"session_id": session_id, "message_count": len(history), "history": history}
```

### 클라이언트 측 SSE 수신 예시

```javascript
// 브라우저에서 SSE를 수신하는 최소 코드
async function streamChat(sessionId, message) {
    const response = await fetch(`/chat/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const lines = text.split('\n');
        for (const line of lines) {
            if (line.startsWith('data: ') && line !== 'data: [DONE]') {
                const data = JSON.parse(line.slice(6));
                document.getElementById('output').textContent += data.text;
            }
        }
    }
}
```

## 토큰 예산 계산기

스트리밍 전에 토큰이 예산을 초과할지 미리 확인하면 예상치 못한 비용을 막을 수 있습니다.

```python
import tiktoken


def estimate_tokens(messages: list[dict], model: str = "gpt-4o-mini") -> int:
    """메시지 리스트의 예상 토큰 수를 계산합니다."""
    enc = tiktoken.encoding_for_model(model)
    total = 0
    for msg in messages:
        total += 4  # 역할과 구분자 토큰
        total += len(enc.encode(msg.get("content", "")))
    total += 2  # 응답 프라이밍 토큰
    return total


def build_windowed_messages(
    history: list[dict],
    user_message: str,
    system_prompt: str,
    token_budget: int = 3000,
    model: str = "gpt-4o-mini",
) -> list[dict]:
    """토큰 예산 내에서 최대한 많은 히스토리를 포함합니다."""
    base = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    base_tokens = estimate_tokens(base, model)
    available = token_budget - base_tokens

    selected = []
    for msg in reversed(history):
        msg_tokens = estimate_tokens([msg], model)
        if available - msg_tokens < 0:
            break
        selected.insert(0, msg)
        available -= msg_tokens

    return (
        [{"role": "system", "content": system_prompt}]
        + selected
        + [{"role": "user", "content": user_message}]
    )


# 실제 사용 예시
system_prompt = "당신은 파이썬 튜터입니다."
user_message = "재귀 함수에 대해 설명해주세요."

messages = build_windowed_messages(
    history=history,
    user_message=user_message,
    system_prompt=system_prompt,
    token_budget=3000,
)
estimated = estimate_tokens(messages)
print(f"예상 토큰 사용량: {estimated} / 3000")
print(f"포함된 히스토리 메시지 수: {len(messages) - 2}")  # system + user 제외
```

## Redis를 활용한 세션 영속화

인메모리 `dict`는 서버 재시작 시 모든 세션이 사라집니다. 프로덕션에서는 Redis를 사용해야 합니다.

```python
import json
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

SESSION_TTL = 3600  # 세션 만료 시간: 1시간


def get_session(session_id: str) -> list[dict]:
    """Redis에서 세션 히스토리를 조회합니다."""
    raw = r.get(f"chat:session:{session_id}")
    if raw is None:
        return []
    return json.loads(raw)


def save_session(session_id: str, history: list[dict]) -> None:
    """Redis에 세션 히스토리를 저장하고 TTL을 갱신합니다."""
    r.set(
        f"chat:session:{session_id}",
        json.dumps(history, ensure_ascii=False),
        ex=SESSION_TTL,
    )


def append_messages(session_id: str, user_msg: str, assistant_msg: str) -> None:
    """세션에 새 메시지 쌍을 추가합니다."""
    history = get_session(session_id)
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": assistant_msg})
    # 최대 50개 메시지만 보존 (오래된 것부터 제거)
    if len(history) > 50:
        history = history[-50:]
    save_session(session_id, history)
```

## 멀티턴 대화 디버깅 패턴

대화가 예상대로 흐르지 않을 때 어느 지점에서 맥락이 깨졌는지 빠르게 찾으려면 구조화된 로그가 필요합니다.

```python
import logging
from datetime import datetime

logger = logging.getLogger("chatbot")

def debug_chat_turn(
    session_id: str,
    user_message: str,
    reply: str,
    history_len: int,
    tokens_used: int,
) -> None:
    """각 턴의 핵심 메타데이터를 구조화 로그로 남깁니다."""
    logger.info(
        "chat_turn",
        extra={
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "history_len": history_len,
            "user_message_len": len(user_message),
            "reply_len": len(reply),
            "tokens_used": tokens_used,
        },
    )
```

이 로그를 ELK 스택이나 CloudWatch에 보내면 "어느 세션에서 토큰이 급증했는지", "평균 몇 번째 턴에서 맥락 관련 불만이 들어오는지"를 데이터로 분석할 수 있습니다.

## 운영 체크리스트

- [ ] 슬라이딩 윈도우 크기가 평균 세션 길이보다 충분히 큰지 확인했습니다.
- [ ] 세션 이력이 Redis 또는 DB에 영속화됩니다.
- [ ] 스트리밍 완료 후에만 히스토리를 업데이트하는 로직을 확인했습니다.
- [ ] 토큰 예산 초과 시 사용자에게 안내 메시지를 반환합니다.
- [ ] 세션 간 히스토리 격리를 단위 테스트로 검증했습니다.
- [ ] Redis TTL이 설정되어 비활성 세션이 자동으로 만료됩니다.
- [ ] `X-Accel-Buffering: no` 헤더가 Nginx 환경에서 스트리밍을 방해하지 않습니다.

## 자주 하는 실수

| 실수 | 증상 | 해결 방법 |
|---|---|---|
| 전체 히스토리를 무조건 전달 | 장기 대화에서 비용 폭발, 컨텍스트 초과 오류 | 슬라이딩 윈도우 또는 요약 메모리 적용 |
| 세션을 인메모리에만 저장 | 서버 재시작 시 대화 이력 소멸 | Redis 또는 DB에 세션 영속화 |
| 스트리밍 없이 전체 응답 대기 | 긴 응답에서 UX 저하, 타임아웃 발생 | SSE 스트리밍 구현 |
| system 프롬프트를 messages에 중복 포함 | 불필요한 토큰 낭비 | system은 첫 번째 메시지로 1회만 포함 |
| 동시 세션 간 히스토리 공유 | 사용자 간 대화 내용 노출 | 세션 ID로 격리, 프로덕션은 Redis Hash 사용 |
| 스트림 중간에 히스토리 저장 | 응답이 잘린 채로 히스토리에 저장됨 | 스트림 완료 후 `[DONE]` 이벤트 기점으로 저장 |
| 요약 메모리 요약 결과 검증 안 함 | 중요 맥락이 요약에서 누락되어 후속 응답 품질 저하 | 요약 결과를 별도 저장하고 주기적으로 샘플 검토 |
| window_size가 너무 작음 | 3~4턴 전 내용도 기억 못하는 챗봇 | 평균 세션 길이의 1.5배 이상으로 설정 |

## 처음 질문으로 돌아가기

- **챗봇이 이전 대화를 기억하려면 어떤 메모리 전략이 필요할까요?**
  슬라이딩 윈도우(최근 N개 메시지)로 시작하고, 대화가 20턴 이상으로 길어지면 요약 메모리로 전환합니다. 오래된 부분은 요약하고 최근 K개는 원문을 유지하는 하이브리드 방식이 가장 실용적입니다.

- **토큰 비용이 폭증하는 문제를 어떻게 막을 수 있을까요?**
  토큰 예산 계산기를 프롬프트 구성 전에 실행해 초과 여부를 미리 확인하고, 예산 내에서 역순으로 히스토리를 채웁니다. 슬라이딩 윈도우 크기와 토큰 한도를 동시에 적용하면 비용을 예측 가능하게 유지할 수 있습니다.

- **슬라이딩 윈도우와 요약 메모리는 각각 어떤 상황에 적합할까요?**
  슬라이딩 윈도우는 대화가 10~20턴 이하이고 최근 맥락이 전부인 고객 지원, 단순 Q&A에 적합합니다. 요약 메모리는 학습 세션, 개인 비서처럼 누적 맥락이 중요한 장기 대화에 적합합니다.

- **FastAPI에서 스트리밍을 안전하게 구현하려면 어떻게 해야 할까요?**
  `StreamingResponse`에 `text/event-stream` 미디어 타입을 사용하고, Nginx 환경에서는 `X-Accel-Buffering: no` 헤더를 추가합니다. 스트림 완료 후에 히스토리를 업데이트해야 일부만 저장되는 오류를 방지할 수 있습니다.

- **세션 기반 대화 관리를 프로덕션에서 운영할 때 무엇을 챙겨야 할까요?**
  Redis TTL로 비활성 세션을 자동 만료시키고, 세션 ID를 JWT 토큰에 포함해 인증된 사용자만 자신의 세션에 접근하도록 합니다. 세션 히스토리 최대 길이를 코드로 고정해 단일 세션의 메모리 과점유를 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **AI App Patterns 101 (1/6): Chatbot 패턴 (현재 글)**
- [AI App Patterns 101 (2/6): RAG QA 패턴](./02-rag-qa-pattern.md)
- [AI App Patterns 101 (3/6): Document Assistant 패턴](./03-document-assistant.md)
- [AI App Patterns 101 (4/6): Agent Tool 패턴](./04-agent-tool-pattern.md)
- [AI App Patterns 101 (5/6): Workflow Automation 패턴](./05-workflow-automation.md)
- [AI App Patterns 101 (6/6): Human-in-the-Loop 패턴](./06-human-in-the-loop.md)

<!-- toc:end -->

## 참고 자료

- [OpenAI — Chat Completions API](https://platform.openai.com/docs/guides/chat)
- [LangChain — Conversation Memory](https://python.langchain.com/docs/modules/memory/)
- [FastAPI — StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [tiktoken — Token counting](https://github.com/openai/tiktoken)
- [Redis — Python client](https://redis-py.readthedocs.io/)
- [book-examples — ai-app-patterns-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/ai-app-patterns-101/ko)

Tags: Chatbot, LLM, ConversationMemory, FastAPI, Streaming
