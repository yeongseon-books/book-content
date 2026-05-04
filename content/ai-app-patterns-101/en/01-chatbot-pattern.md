---
title: Chatbot pattern — managing conversation history and state
series: ai-app-patterns-101
episode: 1
language: en
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
seo_description: A chatbot is not a model with memory; it is an application loop that
  keeps replaying the accumulated messages list.
---

# Chatbot pattern — managing conversation history and state

## Questions this post answers

- Why does a chatbot application need to carry conversation history itself?
- What is the smallest working pattern for a multi-turn chatbot with accumulated messages?
- When should session history stay in memory, and when should it move to external storage?

> A chatbot is not a model with memory; it is an application loop that keeps replaying the accumulated messages list.

![Questions this post answers](../../../assets/ai-app-patterns-101/01/01-01-questions-this-post-answers.en.png)

*Questions this post answers*
> AI App Patterns 101 (1/6)

Example code: [github.com/yeongseon-books/ai-app-patterns-101](https://github.com/yeongseon-books/ai-app-patterns-101/tree/main/en/01-chatbot-pattern)

The LLM API is stateless. Each request is independent, so if you want the model to remember earlier turns, the application must manage history itself. The core questions of the chatbot pattern are: how to store the history, how much to keep, and when to compress it.

This post builds from the simplest possible chatbot to a windowed memory, a summary-based approach, and a session-keyed structure for multi-user apps.

Topics:

- a basic chatbot with manual history management
- memory window — keeping only the last N messages
- conversation summary to control context length
- session-based chatbot structure

---

## Basic chatbot: manual history

### Stateless call with replayed history

![Stateless call with replayed history](../../../assets/ai-app-patterns-101/01/01-01-stateless-call-with-replayed-history.en.png)

*Stateless call with replayed history*
The simplest approach: accumulate messages in a list and send the full list with every request.

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

As history accumulates, the context window fills up. `llama-3.1-8b-instant` has an 8,192 token limit. Long conversations hit the ceiling.

---

## Memory window — keeping the last N messages

### Sliding window message retention

![Sliding window message retention](../../../assets/ai-app-patterns-101/01/01-02-sliding-window-message-retention.en.png)

*Sliding window message retention*
Drop old messages and retain only the most recent N. This keeps context length predictable.

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

`deque(maxlen=window_size)` discards the oldest entry automatically when capacity is exceeded.

---

## Conversation summary to control context

### Summary memory with recent turns

![Summary memory with recent turns](../../../assets/ai-app-patterns-101/01/01-03-summary-memory-with-recent-turns.en.png)

*Summary memory with recent turns*
A window simply discards old messages. Summarization compresses them.

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

## Session-based chatbot

### Session-scoped conversation state

![Session-scoped conversation state](../../../assets/ai-app-patterns-101/01/01-04-session-scoped-conversation-state.en.png)

*Session-scoped conversation state*
Apps with multiple users need conversation state keyed by session ID.

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

## What to notice in this code

- `main.py` implements multi-turn behavior with nothing more than `SystemMessage` plus accumulated `HumanMessage` and `AIMessage` objects per session.
- The demo runs one continuing session and one separate session to show that “memory” lives in application state, not inside the model.
- In production, this in-memory `dict[str, list]` becomes Redis or a database-backed session store.

---

## Where engineers get confused

### Branching from full history to compression

![Branching from full history to compression](../../../assets/ai-app-patterns-101/01/01-05-branching-from-full-history-to-compressi.en.png)

*Branching from full history to compression*
- Persisting chat history does not give the model durable memory; it only replays prior turns on every request.
- Session identity and user identity are related but not identical. One user can have multiple concurrent sessions.
- As history grows, cost and latency often break first, long before the chatbot stops working.

---

## Checklist

- [ ] Conversation history is isolated per session ID
- [ ] The system prompt is included on every model call
- [ ] The AI reply is appended back into history after each response
- [ ] The storage layer can later move to Redis or a database without changing the calling pattern

---

## Conclusion

The chatbot pattern is fundamentally a question of history management. Simple accumulation, windowing, and summarization each make sense in different situations depending on conversation length, how much old context matters, and token cost.

The next post covers the RAG Q&A pattern: retrieving external documents to improve LLM answer accuracy.

<!-- toc:begin -->
## In this series

- **Chatbot pattern — managing conversation history and state (current)**
- RAG Q&A pattern — document-based question answering (upcoming)
- Document assistant — summarization, extraction, classification (upcoming)
- Agent and tool pattern — autonomous tool selection (upcoming)
- Workflow automation — designing multi-step chains (upcoming)
- Human-in-the-loop — designing for human intervention (upcoming)

<!-- toc:end -->

---

## References

- [LangChain message history](https://python.langchain.com/docs/expression_language/how_to/message_history/)
- [Groq chat API](https://console.groq.com/docs/text-chat)
- [LangChain chatbot use case](https://python.langchain.com/docs/use_cases/chatbots/)

Tags: LLM, RAG, Agent, Python
