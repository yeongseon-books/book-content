---
title: "AI App Patterns 101 (1/6): 챗봇 패턴 — 대화 이력과 상태 관리"
series: ai-app-patterns-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- LLM
- RAG
- Agent
- Python
last_reviewed: '2026-05-12'
seo_description: 챗봇은 모델이 기억하는 시스템이 아니라 누적 메시지 목록을 다시 보내는 앱 루프입니다.
---

# AI App Patterns 101 (1/6): 챗봇 패턴 — 대화 이력과 상태 관리

챗봇을 처음 설계할 때 가장 흔한 착각은 모델이 호출 사이의 대화를 어딘가에 기억해 둔다고 보는 일입니다. 실제로는 정반대입니다. 어떤 문맥을 다시 보낼지, 얼마나 오래 보관할지, 이력이 너무 길어졌을 때 무엇을 버리고 무엇을 압축할지는 모두 애플리케이션이 결정합니다.

이 차이를 빨리 잡아야 멀티턴 동작을 제대로 설명할 수 있습니다. 챗봇 품질 문제처럼 보이는 많은 현상은 사실 모델 지능의 문제가 아니라, 이력 재생 전략과 상태 저장 방식의 문제이기 때문입니다.

이 글은 AI App Patterns 101 시리즈의 첫 번째 글입니다. 여기서는 가장 작은 신뢰 가능한 챗봇 패턴과, 멀티턴 동작을 가능하게 만드는 상태 관리 결정을 함께 살펴봅니다.

## 먼저 던지는 질문

- 모델이 이전 대화를 기억하지 않는다면 챗봇의 “기억”은 어디에 있어야 할까요?
- 대화 이력을 계속 붙이면 언제 비용과 지연 시간이 먼저 문제가 될까요?
- 세션별 이력은 언제 메모리에 두고 언제 외부 저장소로 옮겨야 할까요?

## 큰 그림

![이력을 다시 보내는 무상태 호출](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/01/01-01-stateless-call-with-replayed-history.ko.png)

*이력을 다시 보내는 무상태 호출*

이 그림에서는 모델이 기억하는 것이 아니라 애플리케이션이 메시지 이력을 다시 보내 멀티턴 대화를 만드는 흐름을 봅니다. 챗봇 패턴의 핵심은 어떤 이력을 저장하고, 잘라 내고, 세션별로 분리할지 결정하는 것입니다.

> 챗봇은 모델이 기억하는 시스템이 아니라, 애플리케이션이 누적된 메시지 목록을 계속 다시 재생하는 루프입니다.

## 기본 챗봇: 수동 이력 관리

### 이력을 다시 보내는 무상태 호출

가장 단순한 접근은 메시지를 리스트에 계속 쌓고, 매 요청마다 그 전체 리스트를 다시 보내는 방식입니다.

```python
import os

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

system_message = SystemMessage(
    content="You are a helpful AI assistant. Keep your answers concise."
)
history = [system_message]

def chat(user_input: str) -> str:
    history.append(HumanMessage(content=user_input))
    response = llm.invoke(history)
    history.append(AIMessage(content=response.content))
    return response.content

print(chat("Hi! My name is Alice."))
print(chat("What are two advantages of Python?"))
print(chat("What is my name?"))  # must recall earlier turn
```

이력이 계속 쌓이면 결국 컨텍스트 창이 차기 시작합니다. `llama-3.1-8b-instant`의 한계는 8,192토큰이므로, 긴 대화는 언젠가 한계에 부딪힙니다.

---

## 메모리 윈도우 — 최근 N개 메시지만 유지

### 슬라이딩 윈도우 메시지 보존

![슬라이딩 윈도우 메시지 보존](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/01/01-02-sliding-window-message-retention.ko.png)

*슬라이딩 윈도우 메시지 보존*
오래된 메시지를 버리고 가장 최근 N개만 남기면 컨텍스트 길이를 예측 가능하게 유지할 수 있습니다.

```python
import os
from collections import deque

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

WINDOW_SIZE = 10  # last 10 messages (5 human-AI pairs)

class WindowedChatbot:
    def __init__(self, system_prompt: str, window_size: int = WINDOW_SIZE):
        self.system_message = SystemMessage(content=system_prompt)
        self.window: deque = deque(maxlen=window_size)

    def chat(self, user_input: str) -> str:
        self.window.append(HumanMessage(content=user_input))
        messages = [self.system_message] + list(self.window)
        response = llm.invoke(messages)
        ai_msg = AIMessage(content=response.content)
        self.window.append(ai_msg)
        return response.content

    @property
    def history_length(self) -> int:
        return len(self.window)

bot = WindowedChatbot(
    system_prompt="You are a Python tutor. Explain things clearly and concisely."
)

turns = [
    "What is the difference between a list and a tuple in Python?",
    "When is a dictionary the right choice?",
    "What are the main uses of a set?",
    "Summarize the three data structures you just explained in one line each.",
]

for turn in turns:
    print(f"\n[user] {turn}")
    answer = bot.chat(turn)
    print(f"[bot] {answer[:150]}...")
    print(f"history length: {bot.history_length} messages")
```

`deque(maxlen=window_size)`는 용량을 넘기는 순간 가장 오래된 항목을 자동으로 버립니다.

---

## 대화 요약으로 컨텍스트 제어

### 최근 대화와 함께 쓰는 요약 메모리

![최근 대화와 함께 쓰는 요약 메모리](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/01/01-03-summary-memory-with-recent-turns.ko.png)

*최근 대화와 함께 쓰는 요약 메모리*
윈도우 방식은 오래된 메시지를 그냥 버립니다. 요약 방식은 오래된 메시지를 압축해서 남깁니다.

> 멘탈 모델은 단순합니다. 최근 대화는 원문으로 유지하고, 오래된 대화는 요약본으로 접어 두는 것입니다. 챗봇은 장기 기억을 갖는 것이 아니라, 긴 이력을 짧은 설명문으로 다시 들고 다니는 셈입니다.

```python
import os

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

summarize_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Summarize this conversation in 3-5 sentences. "
        "Preserve who the user is, what they asked, and any key facts.",
    ),
    ("human", "Conversation:\n{history}"),
])

summarize_chain = summarize_prompt | llm | StrOutputParser()

class SummaryChatbot:
    def __init__(self, system_prompt: str, max_turns: int = 6):
        self.system_prompt = system_prompt
        self.max_turns = max_turns
        self.summary = ""
        self.recent: list = []

    def _summarize(self) -> None:
        history_text = "\n".join(
            f"{'user' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
            for m in self.recent
        )
        self.summary = summarize_chain.invoke({"history": history_text})
        self.recent = []
        print(f"  [summary generated: {len(self.summary)} chars]")

    def chat(self, user_input: str) -> str:
        if len(self.recent) >= self.max_turns * 2:
            self._summarize()

        system_content = self.system_prompt
        if self.summary:
            system_content += f"\n\nPrevious conversation summary:\n{self.summary}"

        messages = (
            [SystemMessage(content=system_content)]
            + self.recent
            + [HumanMessage(content=user_input)]
        )

        response = llm.invoke(messages)
        self.recent.append(HumanMessage(content=user_input))
        self.recent.append(AIMessage(content=response.content))
        return response.content

bot = SummaryChatbot(
    system_prompt="You are a helpful travel assistant.",
    max_turns=3,
)

conversations = [
    "I am planning a trip to Jeju Island. When is the best time to go?",
    "Is a rental car necessary?",
    "Where is a good area to stay?",
    "Recommend a good itinerary for a family trip.",  # triggers summarization
    "What activities do children typically enjoy there?",
]

for msg in conversations:
    print(f"\n[user] {msg}")
    answer = bot.chat(msg)
    print(f"[bot] {answer[:200]}...")
```

---

## 세션 기반 챗봇

### 세션 범위로 분리된 대화 상태

![세션 범위로 분리된 대화 상태](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/01/01-04-session-scoped-conversation-state.ko.png)

*세션 범위로 분리된 대화 상태*
여러 사용자가 있는 앱에서는 세션 ID를 기준으로 대화 상태를 분리해야 합니다.

```python
import os
import uuid
from collections import deque

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

# session store — use Redis or a database in production
sessions: dict[str, deque] = {}
WINDOW_SIZE = 10
SYSTEM_PROMPT = "You are a helpful AI assistant."

def get_or_create_session(session_id: str | None = None) -> str:
    if session_id is None or session_id not in sessions:
        session_id = session_id or str(uuid.uuid4())
        sessions[session_id] = deque(maxlen=WINDOW_SIZE)
    return session_id

def chat(user_input: str, session_id: str | None = None) -> tuple[str, str]:
    session_id = get_or_create_session(session_id)
    window = sessions[session_id]

    window.append(HumanMessage(content=user_input))
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(window)
    response = llm.invoke(messages)
    window.append(AIMessage(content=response.content))

    return response.content, session_id

# two users with independent sessions
session_a = None
session_b = None

response_a, session_a = chat("Hi, my name is Alice.", session_a)
print(f"[Alice] {response_a[:100]}...\n")

response_b, session_b = chat("Hi, my name is Bob.", session_b)
print(f"[Bob] {response_b[:100]}...\n")

response_a, session_a = chat("What is my name?", session_a)
print(f"[Alice continued] {response_a[:100]}...")

print(f"\nsession A: {session_a}")
print(f"session B: {session_b}")
print(f"session A history length: {len(sessions[session_a])}")
```

---

## 이 코드에서 먼저 볼 점

- `main.py`는 세션마다 `SystemMessage`, `HumanMessage`, `AIMessage`를 누적하는 것만으로 멀티턴 동작을 구현합니다.
- 예제는 이어지는 세션 하나와 별도 세션 하나를 함께 실행해, “기억”이 모델 내부가 아니라 애플리케이션 상태에 있다는 점을 보여 줍니다.
- 운영 환경에서는 이 메모리 기반 `dict[str, list]`를 Redis나 데이터베이스 기반 세션 저장소로 바꾸게 됩니다.

---

## 어디서 자주 헷갈릴까요?

### 전체 이력에서 압축 전략으로 갈라지는 분기

![전체 이력에서 압축 전략으로 갈라지는 분기](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/01/01-05-branching-from-full-history-to-compressi.ko.png)

*전체 이력에서 압축 전략으로 갈라지는 분기*
- 채팅 이력을 저장한다고 해서 모델이 지속적인 기억을 얻는 것은 아닙니다. 단지 이전 턴을 매 요청마다 다시 재생할 뿐입니다.
- 세션 정체성과 사용자 정체성은 연결되지만 같은 개념은 아닙니다. 한 사용자가 동시에 여러 세션을 가질 수도 있습니다.
- 이력이 길어질수록 챗봇이 멈추기 전에 먼저 깨지는 것은 대개 비용과 지연 시간입니다.

---

## 체크리스트

- [ ] 대화 이력이 세션 ID별로 분리되어 있다
- [ ] system prompt가 모든 모델 호출에 포함된다
- [ ] AI 응답이 매 턴 이후 다시 이력에 추가된다
- [ ] 저장 계층을 나중에 Redis나 데이터베이스로 바꿔도 호출 패턴이 유지된다

---

## 정리

챗봇 패턴의 본질은 대화 이력 관리입니다. 단순 누적, 윈도잉, 요약은 대화 길이와 오래된 문맥의 중요도, 토큰 비용에 따라 각각 다른 상황에서 타당합니다.

다음 글에서는 RAG Q&A 패턴을 다룹니다. 외부 문서를 검색해 LLM 답변 정확도를 높이는 구조입니다.

## 처음 질문으로 돌아가기

- **모델이 이전 대화를 기억하지 않는다면 챗봇의 “기억”은 어디에 있어야 할까요?**
  챗봇의 기억은 모델 내부가 아니라 애플리케이션이 관리하는 메시지 이력과 세션 저장소에 있습니다.

- **대화 이력을 계속 붙이면 언제 비용과 지연 시간이 먼저 문제가 될까요?**
  전체 이력을 매번 다시 보내면 토큰 비용과 응답 지연이 빠르게 커집니다. 이때 메모리 윈도우나 요약 전략이 필요합니다.

- **세션별 이력은 언제 메모리에 두고 언제 외부 저장소로 옮겨야 할까요?**
  단일 프로세스 데모는 메모리 dict로 충분하지만, 다중 사용자·재시작·수평 확장이 필요하면 Redis나 데이터베이스 같은 외부 저장소로 옮겨야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **AI App Patterns 101 (1/6): 챗봇 패턴 — 대화 이력과 상태 관리 (현재 글)**
- AI App Patterns 101 (2/6): RAG Q&A 패턴 — 문서 기반 질의응답 (예정)
- AI App Patterns 101 (3/6): 문서 어시스턴트 — 요약, 추출, 분류 (예정)
- AI App Patterns 101 (4/6): 에이전트와 도구 패턴 — 자율적 도구 선택 (예정)
- AI App Patterns 101 (5/6): 워크플로 자동화 — 다단계 체인 설계 (예정)
- AI App Patterns 101 (6/6): Human-in-the-loop — 사람 개입 설계 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain message history](https://python.langchain.com/docs/expression_language/how_to/message_history/)
- [Groq chat API](https://console.groq.com/docs/text-chat)
- [LangChain chatbot use case](https://python.langchain.com/docs/use_cases/chatbots/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-app-patterns-101/ko/01-chatbot-pattern)

Tags: LLM, RAG, Agent, Python
