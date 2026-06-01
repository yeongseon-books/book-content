---
title: "LLM App Foundations 101 (5/6): Managing conversation state — building a multi-turn chatbot"
series: llm-app-foundations-101
episode: 5
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- OpenAI
- Prompt Engineering
- Python
last_reviewed: '2026-05-01'
seo_description: Build stateful LLM chatbots by managing conversation history through full-replay, sliding-window, and summary-based compression strategies.
---

# LLM App Foundations 101 (5/6): Managing conversation state — building a multi-turn chatbot

One of the first surprises in chatbot development is how quickly the illusion breaks. The first answer looks fine. The second user message refers to the previous turn, and the model suddenly behaves as if the conversation started from zero. That is not a provider bug. It is the default API contract.

This is the fifth post in the LLM App Foundations 101 series.

An LLM does not carry your application's conversation state for free. A chat product feels stateful because the application keeps rebuilding context and resending it on every request. The memory is not hidden in the model. It is a data structure you own.

Understanding this difference early makes multi-turn design easier. If you think of memory as a mysterious model capability, debugging becomes hard and policy becomes vague. If you think of memory as application state you manage directly, the design points become clear: what to keep, what to drop, when to summarize, and where to cut cost.

![Managing conversation state: building a multi-turn chatbot](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/05/05-01-managing-conversation-state-building-a-m.en.png)
*Managing conversation state: building a multi-turn chatbot*

## Questions to Keep in Mind

- Does multi-turn memory live inside the model or inside the request?
- When do full history, sliding windows, and summary compression split apart?
- How can you detect context overflow before the request fails?

## Why this post matters

If prompt design was about static input structure, conversation state management is about input structure that changes over time. A multi-turn system sends a fresh request each time, yet it must also preserve prior decisions, user preferences, and unresolved questions. Getting that balance right is the core of chatbot quality.

State management is also cost management. Keeping the full history makes context strong but drives token cost up every turn. Trimming too aggressively is cheap but loses important facts. Summarization extends session life but risks corrupting memory if done poorly. Memory policy is not a convenience feature — it is a system design decision.

Most multi-turn quality problems resolve at the state strategy level, not by switching models. "Why did it forget this fact?" is almost always answered by inspecting the message reconstruction logic, not the model parameters. Once you understand conversation state, chatbot development shifts from prompt experimentation to application engineering.

## The best way to think about multi-turn memory: not a hidden model ability but state reassembled on every request

Each chat call is independent. The model sees only the messages array in the current request. Multi-turn conversation is therefore not the result of a "remembering model" but the result of an "application that retransmits prior context." Accepting this premise makes state management an ordinary engineering problem: what data to store, what rules to use for reassembly, and when to compress.

This perspective matters because memory policy directly becomes cost policy and quality policy. Full history is simple but expensive; sliding windows are budget-predictable but lose old facts; summary compression handles long sessions but carries information-loss risk.

> Multi-turn chatbot memory is not a hidden ability inside the model. It is a state contract that the application reassembles into each request.

## Why LLM calls are stateless

![Stateless calls with and without replayed history](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/05/05-01-why-llm-calls-are-stateless.en.png)

*Stateless calls with and without replayed history*

At the API boundary, each chat completion request is independent. The model sees only the payload you send. If you do not include earlier turns, those turns do not exist from the model's point of view.

```python
messages = [
    {"role": "user", "content": "My name is Mina. Please remember that."}
]
```

```python
messages = [
    {"role": "user", "content": "What is my name?"}
]
```

This statelessness is not purely a limitation. Request replay is easy, sent context is inspectable via logs, and retention policy stays under application control.

## Multi-turn chat comes from replaying history in messages

![History append loop across user turns](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/05/05-02-multi-turn-chat-comes-from-replaying-his.en.png)

*History append loop across user turns*

Every new request includes prior turns alongside the latest user input. The model reads the whole array and continues from there.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": "You are a concise Python tutor.",
    },
    {"role": "user", "content": "Explain the difference between a list and a tuple."},
    {
        "role": "assistant",
        "content": "A list is mutable, while a tuple is immutable.",
    },
    {"role": "user", "content": "Which one is better as a dictionary key then?"},
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.3,
)

print(completion.choices[0].message.content)
```

The important part is not just the last question. It is the replayed context before it. Terms like "which one" and "then" become meaningful only because the earlier turns are present in the same request.

## Keeping the full history is the simplest memory pattern

![Full history payload growth and token cost](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/05/05-03-keeping-the-full-history-is-the-simplest.en.png)

*Full history payload growth and token cost*

The first implementation most teams write is the easiest to understand: keep the entire conversation and resend it every time.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

history = [
    {
        "role": "system",
        "content": "You are a concise technical support assistant.",
    }
]

def ask(user_text: str) -> str:
    history.append({"role": "user", "content": user_text})

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=history,
        temperature=0.2,
    )

    answer = completion.choices[0].message.content or ""
    history.append({"role": "assistant", "content": answer})
    return answer

print(ask("My product is a monthly SaaS service. Please remember that."))
print(ask("Now write a one-line refund policy statement."))
```

This approach is easiest to understand and debug, but cost and latency grow with every turn until the request hits the model's context window.

## Sliding windows retain only the last N turns

![Full history window and summary comparison](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/05/05-04-sliding-windows-retain-only-the-last-n-t.en.png)

*Full history window and summary comparison*

Sliding-window memory keeps the fixed `system` message and preserves only the most recent N user and assistant turns.

```python
import os
from collections import deque

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

system_message = {
    "role": "system",
    "content": "You are a chatbot that helps users learn Python.",
}
recent_turns = deque(maxlen=6)  # last 3 user/assistant pairs

def ask(user_text: str) -> str:
    recent_turns.append({"role": "user", "content": user_text})

    messages = [system_message, *recent_turns]
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.3,
    )

    answer = completion.choices[0].message.content or ""
    recent_turns.append({"role": "assistant", "content": answer})
    return answer
```

Token usage becomes easy to bound, but once a fact falls out of the window the model loses it. Facts that must survive the whole session belong in `system` or a persistent summary, not in rolling history.

## Summary-based compression handles longer conversations

Sometimes discarding old turns is too aggressive, but keeping everything is too expensive. Summary compression sits in the middle.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

system_message = {
    "role": "system",
    "content": "You are a project-planning chatbot.",
}
summary_text = ""
recent_turns = []

def summarize_history(history_chunk: list[dict[str, str]], current_summary: str) -> str:
    prompt = [
        {
            "role": "system",
            "content": (
                "Compress the conversation. Preserve user goals, confirmed facts, "
                "preferences, and unresolved questions."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Current summary:\n{current_summary or '(none)'}\n\n"
                f"New history chunk:\n{history_chunk}"
            ),
        },
    ]

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=prompt,
        temperature=0.1,
    )
    return completion.choices[0].message.content or ""

def build_messages(user_text: str) -> list[dict[str, str]]:
    messages = [system_message]
    if summary_text:
        messages.append(
            {
                "role": "system",
                "content": f"Conversation summary:\n{summary_text}",
            }
        )
    messages.extend(recent_turns)
    messages.append({"role": "user", "content": user_text})
    return messages
```

Summaries are lossy compression. The summary prompt must be explicit about what to preserve: user goals, confirmed facts, preferences, and unresolved questions.

## Detecting context overflow before the request fails

![Budget check before context overflow](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/05/05-05-detecting-context-overflow-before-the-re.en.png)

*Budget check before context overflow*

Long session failures usually start with context budget overflow. Pre-flight detection matters.

```python
def rough_token_count(messages: list[dict[str, str]]) -> int:
    total_chars = sum(len(message["content"]) for message in messages)
    overhead = len(messages) * 12
    return (total_chars // 4) + overhead

def enforce_budget(messages: list[dict[str, str]], max_input_tokens: int = 6000) -> list[dict[str, str]]:
    if rough_token_count(messages) <= max_input_tokens:
        return messages

    trimmed = messages[:1] + messages[-8:]
    if rough_token_count(trimmed) <= max_input_tokens:
        return trimmed

    raise ValueError("Conversation is too long. A more aggressive summary is required.")
```

Even this crude estimate triggers useful actions: summarize older turns, shrink the sliding window, or ask the user to reset.

## Session storage and lifetime policy

Tutorial examples use an in-process list, but real services handle multiple concurrent user sessions. The critical question is not which memory strategy to use but what storage contract to define: what key identifies a session, when does it expire, and how do you recover after a crash.

| Storage | Strengths | Weaknesses | Recommended use |
|---|---|---|---|
| Process memory | Simplest implementation | Lost on restart, no multi-instance | Local development |
| Redis | Fast read/write, TTL built-in | Adds operational complexity | Default for real-time chatbots |
| RDBMS | Audit/analytics friendly | Higher latency | Regulated/audit-required environments |

A minimal Redis-based pattern:

```python
import json
from redis import Redis

redis = Redis(host="localhost", port=6379, decode_responses=True)
SESSION_TTL_SECONDS = 60 * 60 * 24

def load_session_messages(session_id: str) -> list[dict[str, str]]:
    raw = redis.get(f"chat:session:{session_id}")
    if not raw:
        return []
    return json.loads(raw)

def save_session_messages(session_id: str, messages: list[dict[str, str]]) -> None:
    redis.set(
        f"chat:session:{session_id}",
        json.dumps(messages, ensure_ascii=False),
        ex=SESSION_TTL_SECONDS,
    )
```

Without an explicit TTL, stale sessions accumulate and create both cost and security risk. State management is not about extending memory — it is about designing memory lifetime.

## Reducing summary distortion with dual retention

Summaries shrink length but introduce meaning loss. For longer sessions, keeping "some raw turns + a summary" together reduces distortion.

```python
def build_context_for_request(
    system_message: dict[str, str],
    summary_message: dict[str, str] | None,
    recent_turns: list[dict[str, str]],
    user_message: dict[str, str],
) -> list[dict[str, str]]:
    context = [system_message]
    if summary_message:
        context.append(summary_message)
    context.extend(recent_turns[-6:])
    context.append(user_message)
    return context
```

The goal is not perfect memory. It is keeping long-term context from being destroyed by cheap summarization while bounding the budget.

## Error classification for state management debugging

When conversation quality drops, classifying the failure mode accelerates debugging.

| Symptom | Primary cause candidate | Check point |
|---|---|---|
| Forgets user preference | Recent window too narrow | Window size, summary preservation rules |
| Answer drifts mid-context | Summary distortion | Summary prompt, summarization frequency |
| 429 / rising latency | History bloat | Average `prompt_tokens`, compression trigger |
| Cross-session info leakage | session_id collision | Session key generation, multi-tenant boundary |

## Tracking multi-turn cost per session

Single-call usage alone hides the effect of your state strategy. Recording cumulative session tokens reveals which policy is actually cheaper.

```python
from dataclasses import dataclass

@dataclass
class SessionUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

def accumulate_usage(usage_tracker: SessionUsage, usage) -> None:
    usage_tracker.prompt_tokens += int(getattr(usage, "prompt_tokens", 0))
    usage_tracker.completion_tokens += int(getattr(usage, "completion_tokens", 0))
```

On an operations dashboard, watching `session_total_tokens`, `avg_tokens_per_turn`, and `summary_trigger_count` together makes policy effectiveness visible.

## Cross-provider principles for state reconstruction

The state management principles hold regardless of whether you use OpenAI, Anthropic, or Groq:

- Previous assistant output must be explicitly re-injected into the next request.
- System policy must be repeated in every request.
- Summary text should live in a separate slot and be logged independently.
- Sensitive conversations must be deleted or de-identified at session end.

Many issues that look like model quality problems are actually one of these four principles breaking down.

## Privacy and state deletion policy

Conversation state is both a quality asset and a security asset. In customer support, healthcare, and finance domains, PII enters sessions easily. Multi-turn design needs a deletion policy as strong as its retention policy.

```python
import re

PII_PATTERNS = [
    re.compile(r"\b\d{2,3}-\d{3,4}-\d{4}\b"),  # phone numbers
    re.compile(r"\b[\w.-]+@[\w.-]+\.[A-Za-z]{2,}\b"),  # email addresses
]

def redact_pii(text: str) -> str:
    redacted = text
    for pattern in PII_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted

def sanitize_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {"role": m["role"], "content": redact_pii(m["content"])}
        for m in messages
    ]
```

This step does not conflict with quality. The longer you keep conversation logs, the more important de-identification becomes. Conversation state is complete only when "how long to remember" and "how safely to forget" are designed together.

## Common misconceptions

- Multi-turn memory looks like a model feature but is actually message-array reconstruction logic.
- Keeping the full history unconditionally seems ideal but quickly drives up cost and latency in long sessions.
- A sliding window alone seems sufficient, but facts that must persist across the entire session need a separate preservation strategy.
- Summarization is compression and always carries information-loss risk. The summary prompt must be explicit about what to preserve.
- Detecting context overflow only after failure is too late. Length estimation and pre-emptive compression must come first.

## Operational checklist

- [ ] Session storage (with TTL) is defined and expired state is auto-deleted
- [ ] Summary memory and recent-turn memory are separated so recovery is possible when distortion occurs
- [ ] Cumulative session tokens (`session_total_tokens`) are logged to compare memory policy effectiveness
- [ ] Session key includes user and workspace boundaries to prevent collision
- [ ] Each turn's assistant reply is appended back into messages for the next call
- [ ] Both full-history mode and sliding-window mode have been compared for trade-offs
- [ ] Summary prompt specifies preservation rules for user goals, confirmed facts, preferences, and unresolved questions
- [ ] Cumulative input length is estimated before each request; warning or compression fires near the limit
- [ ] Session management commands (`/reset`, `/summary`, `/quit`) are provided

## Answering the Opening Questions

- Does multi-turn memory live inside the model or inside the request?
  - Memory does not stay inside the model automatically. The app creates the multi-turn effect by replaying prior messages in the next request.

- When do full history, sliding windows, and summary compression split apart?
  - Full history is simplest for short conversations; sliding windows and summary compression become necessary as cost and context pressure grow.

- How can you detect context overflow before the request fails?
  - Estimate the message budget before sending the request, including expected output, so overflow is caught before the API rejects or truncates the call.

<!-- toc:begin -->
## In this series

- [LLM App Foundations 101 (1/6): LLM API first call — sending your first request](./01-llm-api-first-call.md)
- [LLM App Foundations 101 (2/6): Understanding tokens — cost, limits, and context windows](./02-understanding-tokens.md)
- [LLM App Foundations 101 (3/6): Prompt engineering basics — system, user, and assistant roles](./03-prompt-engineering-basics.md)
- [LLM App Foundations 101 (4/6): Few-shot and chain-of-thought — steering better answers](./04-few-shot-and-cot.md)
- **LLM App Foundations 101 (5/6): Managing conversation state — building a multi-turn chatbot (current)**
- LLM App Foundations 101 (6/6): Handling streaming responses — real-time output (upcoming)

<!-- toc:end -->

---

## References

### Official docs

- [Groq quickstart](https://console.groq.com/docs/quickstart)
- [Groq API reference](https://console.groq.com/docs/api-reference)
- [Groq models](https://console.groq.com/docs/models)
- [OpenAI prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering)

### Related series

- [Handling streaming responses — real-time output](./06-streaming-responses.md)
- [Prompt engineering basics — system, user, and assistant roles](./03-prompt-engineering-basics.md)
- [Chatbot pattern — conversation history and state](../../ai-app-patterns-101/en/01-chatbot-pattern.md)

Tags: LLM, OpenAI, Prompt Engineering, Python
