---
title: '챗봇 패턴 — 대화 이력 관리와 상태'
series: ai-app-patterns-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- RAG
- Agent
- Python
last_reviewed: '2026-05-01'
---

# 챗봇 패턴 — 대화 이력 관리와 상태

## 이 글에서 답할 질문

- 왜 LLM 챗봇은 대화 이력을 앱이 직접 들고 있어야 할까요?
- 메시지 리스트를 누적하는 가장 단순한 멀티턴 패턴은 어떻게 구현할까요?
- 세션별 이력을 분리할 때 어디까지 메모리에 두고 언제 외부 저장소로 빼야 할까요?

> 챗봇은 모델이 기억하는 시스템이 아니라, 앱이 messages 리스트를 계속 다시 보내는 재생 루프입니다.

![이 글에서 답할 질문](../../../assets/ai-app-patterns-101/01/01-01-questions-this-post-answers.ko.png)
> AI 앱 패턴 101 시리즈 (1/6)

예제 코드: [github.com/yeongseon-books/ai-app-patterns-101](https://github.com/yeongseon-books/ai-app-patterns-101/tree/main/ko/01-chatbot-pattern)

LLM API는 무상태(stateless)입니다. 요청마다 독립적으로 처리하므로, 이전 대화를 기억하려면 앱이 직접 이력을 관리해야 합니다. 챗봇 패턴의 핵심은 대화 이력을 어떻게 관리하고, 얼마나 보존하고, 언제 요약할 것인가입니다.

이번 글에서는 가장 기본적인 챗봇부터 메모리 윈도우, 대화 요약, 세션 관리까지 단계적으로 만들어 봅니다.

다룰 내용은 다음과 같습니다.

- 대화 이력을 직접 관리하는 기본 챗봇
- 메모리 윈도우 — 최근 N개만 유지하기
- 대화 요약으로 컨텍스트 길이 제어
- 세션 기반 챗봇 구조

---

## 기본 챗봇: 대화 이력 직접 관리

가장 단순한 챗봇입니다. 메시지 리스트에 대화를 쌓고, 매 요청마다 전체를 LLM에 보냅니다.

```python
import os

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

system_message = SystemMessage(
    content="당신은 친절한 AI 어시스턴트입니다. 간결하게 답변합니다."
)
history = [system_message]

def chat(user_input: str) -> str:
    history.append(HumanMessage(content=user_input))
    response = llm.invoke(history)
    history.append(AIMessage(content=response.content))
    return response.content

# 대화 시뮬레이션
print(chat("안녕하세요! 제 이름은 김철수입니다."))
print(chat("파이썬의 장점을 두 가지만 알려주세요."))
print(chat("제 이름이 뭐라고 했죠?"))  # 이전 대화를 기억해야 함
```

~~~
출력 결과
안녕하세요! 김철수 님 반갑습니다. 무슨 여쭤보시려는지 혹시 궁금한 건 있으세요?
파이썬의 장점은 다음과 같습니다.

1. **쉬운 학습**: 파이썬은 배우기 쉬운 언어로, 많은 프로그래머가 쉽게 학습할 수 있습니다.
2. **재사용성**: 파이썬은 모듈화와 패키지를 지원하여, 코드를 재사용하기 쉽게 해줍니다.
김철수 님이라고 했습니다.
~~~

대화 이력이 쌓이면 컨텍스트 창이 가득 찰 수 있습니다. `llama-3.1-8b-instant`는 최대 8,192 토큰입니다. 긴 대화에서는 제한에 걸립니다.

---

## 메모리 윈도우 — 최근 N개만 유지

오래된 대화를 버리고 최근 N개만 유지합니다. 구현이 간단하고 컨텍스트 길이를 예측 가능하게 유지합니다.

```python
import os
from collections import deque

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

WINDOW_SIZE = 10  # 최근 10개 메시지 유지 (human + ai 쌍 기준 5턴)

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
    system_prompt="당신은 파이썬 튜터입니다. 명확하고 간결하게 설명합니다."
)

turns = [
    "파이썬에서 리스트와 튜플의 차이는 무엇인가요?",
    "딕셔너리는 언제 쓰는 게 좋은가요?",
    "집합(set)의 주요 용도는 무엇인가요?",
    "방금 설명한 세 가지 자료구조를 한 줄씩 정리해 주세요.",
]

for turn in turns:
    print(f"\n[사용자] {turn}")
    answer = bot.chat(turn)
    print(f"[봇] {answer[:150]}...")
    print(f"현재 이력 길이: {bot.history_length}개 메시지")
```

~~~
출력 결과

[사용자] 파이썬에서 리스트와 튜플의 차이는 무엇인가요?
[봇] 리스트와 튜플은 모두 파이썬에서 사용하는 컬렉션 데이터 타입입니다. 그러나 두 타입 사이에는 몇 가지 중요한 차이가 있습니다.

### 1. 변경 가능성

리스트는 변경 가능하며, 요소를 추가, 삭제, 수정할 수 있습니다. 반면에 튜플은 변경 불가능하며, 요소를 추가,...
현재 이력 길이: 2개 메시지

[사용자] 딕셔너리는 언제 쓰는 게 좋은가요?
[봇] 딕셔너리는 키-값 쌍을 저장할 수 있는 데이터 구조입니다. 딕셔너리를 사용하는 경우는 다음과 같습니다.

### 1. 키-값 쌍을 저장하는 경우

딕셔너리는 키-값 쌍을 저장할 수 있습니다. 키는 중복을 허용하지 않으며, 값은 중복을 허용합니다.

```python
#...
현재 이력 길이: 4개 메시지

[사용자] 집합(set)의 주요 용도는 무엇인가요?
[봇] 집합(set)은 중복된 원소를 허용하지 않는 무결성 데이터 구조입니다. 집합의 주요 용도는 다음과 같습니다.

### 1. 중복된 원소를 제거하는 경우

집합은 중복된 원소를 제거할 수 있습니다. 집합은 중복된 원소를 허용하지 않기 때문에, 중복된 원소를 제거하는 데 ...
현재 이력 길이: 6개 메시지

[사용자] 방금 설명한 세 가지 자료구조를 한 줄씩 정리해 주세요.
[봇] 다음은 세 가지 자료구조를 한 줄씩 정리한 내용입니다.

### 리스트(List)

* 변경 가능, 할당 가능, 데이터의 변경이 빈번한 경우에 사용
* 요소를 추가, 삭제, 수정할 수 있음
* 효율적인 데이터 관리를 지원

### 튜플(Tuple)

* 변경 불가능, ...
현재 이력 길이: 8개 메시지
~~~python
stu...
현재 이력 길이: 4개 메시지

[사용자] 집합(set)의 주요 용도는 무엇인가요?
[봇] 집합(set)의 주요 용도는 다음과 같습니다.

### 1. 중복 제거

집합은 중복된 값을 자동으로 제거합니다. 예를 들어, 다음과 같은 리스트가 있으면, 집합을 사용하면 중복된 값을 자동으로 제거할 수 있습니다.

```python
numbers = [1, 2, 2...
현재 이력 길이: 6개 메시지

[사용자] 방금 설명한 세 가지 자료구조를 한 줄씩 정리해 주세요.
[봇] 다음은 세 가지 자료구조를 한 줄씩 정리한 것입니다.

### 1. 리스트

- 내용을 변경할 수 있는 순서가 있는 컬렉션

### 2. 튜플

- 내용을 변경할 수 없는 순서가 있는 컬렉션

### 3. 집합

- 중복된 값을 자동으로 제거하고 멤버십 테스트를 빠르게...
현재 이력 길이: 8개 메시지
```

`deque(maxlen=window_size)`는 최대 길이 제한이 있는 큐입니다. 꽉 차면 오래된 항목이 자동으로 제거됩니다.

---

## 대화 요약으로 컨텍스트 제어

메모리 윈도우는 오래된 대화를 잘라버립니다. 대화 요약은 오래된 내용을 압축해서 보존합니다.

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
        "대화 이력을 3~5문장으로 요약하세요. "
        "사용자가 누구인지, 무엇을 물어봤는지, 핵심 정보를 보존합니다.",
    ),
    ("human", "대화 이력:\n{history}"),
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
            f"{'사용자' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
            for m in self.recent
        )
        self.summary = summarize_chain.invoke({"history": history_text})
        self.recent = []
        print(f"  [요약 생성됨: {len(self.summary)}자]")

    def chat(self, user_input: str) -> str:
        if len(self.recent) >= self.max_turns * 2:
            self._summarize()

        system_content = self.system_prompt
        if self.summary:
            system_content += f"\n\n이전 대화 요약:\n{self.summary}"

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
    system_prompt="당신은 친절한 여행 어시스턴트입니다.",
    max_turns=3,
)

conversations = [
    "제주도 여행을 계획 중입니다. 언제가 가장 좋은가요?",
    "렌터카가 꼭 필요한가요?",
    "숙소는 어디가 좋을까요?",
    "가족 여행에 좋은 코스를 추천해 주세요.",  # 요약 후 진행
    "아이들이 좋아할 만한 체험 활동은?",
]

for msg in conversations:
    print(f"\n[사용자] {msg}")
    answer = bot.chat(msg)
    print(f"[봇] {answer[:200]}...")
```

---

## 세션 기반 챗봇

여러 사용자를 지원하는 앱에서는 세션 ID로 대화를 구분합니다.

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

# 세션 저장소 (실제 앱에서는 Redis나 DB 사용)
sessions: dict[str, deque] = {}
WINDOW_SIZE = 10
SYSTEM_PROMPT = "당신은 친절한 AI 어시스턴트입니다."

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

# 두 사용자가 독립적으로 대화
session_a = None
session_b = None

response_a, session_a = chat("안녕하세요! 저는 앨리스입니다.", session_a)
print(f"[앨리스] {response_a[:100]}...\n")

response_b, session_b = chat("안녕하세요! 저는 밥입니다.", session_b)
print(f"[밥] {response_b[:100]}...\n")

response_a, session_a = chat("제 이름이 뭐라고 했나요?", session_a)
print(f"[앨리스 계속] {response_a[:100]}...")

print(f"\n세션 A: {session_a}")
print(f"세션 B: {session_b}")
print(f"세션 A 이력 길이: {len(sessions[session_a])}")
```

~~~
출력 결과
[앨리스] 안녕하세요! 앨리스님! 반갑습니다. 제가 도와드릴 수 있는ใด든지 알려주세요!...

[밥] 안녕하세요 밥! 만나서 반갑습니다. 어떻게 지내는지 궁금합니다. 무엇을 도와드릴까요?...

[앨리스 계속] 앨리스입니다! 저는 이전에 당신이 앨리스라고 이름을 밝히셨던 것을 기억하고 있습니다....

세션 A: f81f0696-b438-4f90-9023-4a7c14708705
세션 B: f8417c21-03bc-45be-b3f6-d2f9227c8af9
세션 A 이력 길이: 4
~~~

---

## 이 코드에서 봐야 할 것

- `main.py`는 `SystemMessage` + 세션별 `HumanMessage`/`AIMessage` 누적 구조만으로 멀티턴을 구현합니다.
- 실행 예제는 같은 세션과 다른 세션을 함께 돌려서 "기억"이 모델이 아니라 앱 상태에 있다는 점을 보여줍니다.
- 운영 단계에서는 이 `dict[str, list]` 저장소를 Redis나 DB로 바꾸면 됩니다.

---

## 실무에서 헷갈리는 지점

- 대화 이력을 저장한다고 해서 모델이 장기 기억을 갖는 것은 아닙니다. 매 요청마다 다시 보내는 것뿐입니다.
- 세션 분리와 사용자 인증은 다른 문제입니다. 같은 사용자라도 여러 세션을 가질 수 있습니다.
- 이력이 길어질수록 품질보다 먼저 비용과 지연 시간이 문제 되므로 요약이나 윈도잉 전략이 필요합니다.

---

## 체크리스트

- [ ] 세션 ID별로 messages 리스트가 분리되어 있다
- [ ] system prompt가 매 호출마다 항상 포함된다
- [ ] 응답 후 AIMessage도 다시 이력에 append된다
- [ ] 장기 저장소로 바꿔도 인터페이스가 유지된다

---

## 마무리

챗봇 패턴의 핵심은 대화 이력 관리입니다. 단순 누적, 윈도우, 요약 중 어떤 방식을 고를지는 대화 길이, 중요 정보 보존 필요성, 컨텍스트 비용에 따라 결정합니다.

다음 글에서는 RAG Q&A 패턴을 다룹니다. 외부 문서를 검색해서 LLM의 답변 정확도를 높이는 방법입니다.

<!-- toc:begin -->
## 시리즈 목차

- **챗봇 패턴 — 대화 이력 관리와 상태 (현재 글)**
- RAG Q&A 패턴 — 문서 기반 질의응답 (예정)
- 문서 어시스턴트 — 요약, 추출, 분류 (예정)
- Agent + Tool 패턴 — 자율 도구 선택 (예정)
- 워크플로 자동화 — 다단계 체인 설계 (예정)
- Human-in-the-loop — 사람 개입 설계 패턴 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain 대화 이력 관리](https://python.langchain.com/docs/expression_language/how_to/message_history/)
- [Groq 대화 API](https://console.groq.com/docs/text-chat)
- [ChatGPT 스타일 메모리 패턴](https://python.langchain.com/docs/use_cases/chatbots/)

Tags: LLM, RAG, Agent, Python
