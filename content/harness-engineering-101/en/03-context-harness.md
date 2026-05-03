---
title: Context Harness — Designing What the Agent Should Know and Not Know
series: harness-engineering-101
episode: 3
language: en
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Harness
- Context
- RAG
last_reviewed: '2026-05-03'
---

# Context Harness — Designing What the Agent Should Know and Not Know

> Harness Engineering 101 Series (3/10)

The context an agent receives shapes its output. Too little and it guesses. Too much and it loses focus. The Context Harness is about deciding what to give the agent and what to withhold.

---
## Context Is a Resource

An agent's context window is not infinite. GPT-4o has 128k tokens, Claude Sonnet 4 has 200k, Gemini 2.5 Pro has 1M. Big numbers, but in practice never enough. System prompt, conversation history, retrieved documents, tool schemas, and recent tool outputs all compete for the same space.

A bigger context also makes the model slower, more expensive, and less accurate. Information in the middle is easily ignored ("lost in the middle"), and irrelevant content perturbs reasoning. Context is a resource. Not something to pour in without limit, but something to design.

Context Harness is the explicit design of what information the agent receives, when, and what it does not receive. This article covers the components of context, selection strategies, and information you should deliberately hide.

---

## The Five Components of Context

The context an agent sees in a single inference splits into five parts.

1. **System prompt**: the agent's role, rules, and goals. Rarely changes.
2. **Task spec**: the current task's Goal, Inputs, and Completion criteria. Changes per task.
3. **Conversation history**: prior turns. Grows over time.
4. **Retrieved context**: information from RAG, memory, or external data. Should include only what is relevant to the task.
5. **Tool schemas and outputs**: definitions of available tools and the most recent call results.

Each component owns a token budget. In a 200k window you might pre-allocate 2k for system prompt, 1k for task spec, 5k for history, 10k for retrieved context, and 3k for tool schemas. Without allocation, history or retrieved content grows without bound and crowds out everything else.

```python
from dataclasses import dataclass


@dataclass
class ContextBudget:
    """Token budget allocation for the context window."""
    total_tokens: int = 200_000
    system_prompt: int = 2_000
    task_spec: int = 1_000
    conversation_history: int = 5_000
    retrieved_context: int = 10_000
    tool_schemas: int = 3_000
    response_buffer: int = 4_000  # Leave room for the response

    def remaining(self) -> int:
        used = (
            self.system_prompt
            + self.task_spec
            + self.conversation_history
            + self.retrieved_context
            + self.tool_schemas
            + self.response_buffer
        )
        return self.total_tokens - used


budget = ContextBudget()
assert budget.remaining() > 0, "Budget exceeds the window"
```

Once the budget is fixed, Context Harness is the work of compressing each component into its slot.

---

## Conversation History Strategies

History is the fastest-growing component. Three strategies, often combined.

**1. Sliding window**: keep only the last N turns. Simplest. Old information is lost.

**2. Summarization**: replace older turns with a summary. Information is preserved; detail is lost.

**3. Selective recall**: re-fetch past turns when needed via RAG.

```python
from typing import Literal
from dataclasses import dataclass


@dataclass
class Message:
    role: Literal["user", "assistant", "tool"]
    content: str
    tokens: int


class HistoryManager:
    """Manages conversation history within a token budget."""

    def __init__(self, max_tokens: int, strategy: str = "summarize"):
        self.max_tokens = max_tokens
        self.strategy = strategy
        self.messages: list[Message] = []
        self.summary: str = ""

    def add(self, msg: Message) -> None:
        self.messages.append(msg)
        self._compact()

    def _compact(self) -> None:
        total = sum(m.tokens for m in self.messages)
        if total <= self.max_tokens:
            return

        if self.strategy == "sliding":
            while sum(m.tokens for m in self.messages) > self.max_tokens:
                self.messages.pop(0)
        elif self.strategy == "summarize":
            old = self.messages[: len(self.messages) // 2]
            self.summary = self._summarize(old)
            self.messages = self.messages[len(self.messages) // 2 :]

    def _summarize(self, messages: list[Message]) -> str:
        # In practice, summarize with an LLM
        return f"[Summary: {len(messages)} turns]"

    def to_context(self) -> list[dict]:
        result = []
        if self.summary:
            result.append({"role": "system", "content": self.summary})
        result.extend({"role": m.role, "content": m.content} for m in self.messages)
        return result
```

The right strategy depends on the task. Short conversations need only sliding. Long collaborative tasks need summarization. Tasks that must reference past decisions exactly use selective recall.

---

## Precision in Retrieved Context

RAG-retrieved documents take up a large fraction of context. The precision of what you retrieve matters more than the volume.

Pasting in 10 raw documents leaves 90% of them irrelevant to the task. Irrelevant text is not a benign waste — it perturbs reasoning. The model assumes every input is "relevant" and lets unrelated text pull conclusions in the wrong direction.

Three stages improve precision.

**1. Retrieval**: fetch 20–50 candidates. Recall first.
**2. Reranking**: re-score candidates with a cross-encoder for task relevance and keep the top 5–10. Precision first.
**3. Compression**: extract only the sentences related to the task from each document, using an LLM or extractive summarizer.

```python
from typing import Protocol


class Retriever(Protocol):
    def search(self, query: str, top_k: int) -> list[dict]: ...


class Reranker(Protocol):
    def rerank(self, query: str, docs: list[dict]) -> list[dict]: ...


class Compressor(Protocol):
    def compress(self, query: str, doc: dict) -> str: ...


def build_retrieved_context(
    query: str,
    retriever: Retriever,
    reranker: Reranker,
    compressor: Compressor,
    final_k: int = 5,
) -> list[str]:
    """Three-stage precision pipeline."""
    candidates = retriever.search(query, top_k=30)
    reranked = reranker.rerank(query, candidates)[:final_k]
    compressed = [compressor.compress(query, doc) for doc in reranked]
    return compressed
```

Systems that stop at retrieval waste context. Reranking and compression are the heart of Context Harness.

---

## What to Deliberately Hide

Some information must not enter context. Context Harness designs what to hide as carefully as what to show.

**1. Secrets**: API keys, user passwords, PII, medical records. They can leak through agent outputs or logs. Mask or tokenize before they enter context.

**2. Irrelevant tool schemas**: Tools not needed for this task should be removed. Too many tools encourages the model to "use them all."

**3. Contradictory instructions**: When the system prompt and a user message contradict, the model cannot decide which to follow. Define a clear priority or remove the contradiction.

**4. Old tool outputs**: A tool result from five calls ago is usually unrelated to the current task. Keep only the most recent N tool outputs.

**5. Detailed records of failed attempts**: Keep only "this approach failed" so the agent does not repeat it; compress the details.

```python
import re


def mask_secrets(text: str) -> str:
    """Mask API keys and PII."""
    text = re.sub(r"sk-[a-zA-Z0-9]{20,}", "[REDACTED_API_KEY]", text)
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[REDACTED_EMAIL]", text)
    text = re.sub(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[REDACTED_CARD]", text)
    text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]", text)
    return text


def filter_tools_for_task(all_tools: list[dict], task_tags: set[str]) -> list[dict]:
    """Expose only tools whose tags match the task."""
    return [t for t in all_tools if set(t.get("tags", [])) & task_tags]


def trim_tool_history(history: list[dict], keep_last: int = 3) -> list[dict]:
    """Keep only the most recent N tool outputs."""
    tool_msgs = [i for i, m in enumerate(history) if m.get("role") == "tool"]
    if len(tool_msgs) <= keep_last:
        return history
    keep = set(tool_msgs[-keep_last:])
    return [m for i, m in enumerate(history) if m.get("role") != "tool" or i in keep]
```

Hiding is as much a design decision as showing.

---

## Context Snapshots for Reproducibility

A production agent must produce the same output for the same input. But context is assembled through many stages, which makes reproduction hard. Context snapshots solve this.

Save the final context exactly as it goes into each inference. Feeding the same context back to the model later (with temperature 0) produces the same output. This is the foundation of debugging and reproduction tests.

```python
import hashlib
import json
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class ContextSnapshot:
    """Complete snapshot of context just before inference."""
    timestamp: str
    task_id: str
    messages: list[dict]
    tools: list[dict]
    model: str
    temperature: float
    snapshot_hash: str = ""

    def __post_init__(self) -> None:
        payload = json.dumps(
            {"messages": self.messages, "tools": self.tools, "model": self.model},
            sort_keys=True,
        )
        self.snapshot_hash = hashlib.sha256(payload.encode()).hexdigest()[:16]


def capture_snapshot(task_id: str, messages: list[dict], tools: list[dict], model: str) -> ContextSnapshot:
    return ContextSnapshot(
        timestamp=datetime.utcnow().isoformat(),
        task_id=task_id,
        messages=messages,
        tools=tools,
        model=model,
        temperature=0.0,
    )
```

With snapshots you can analyze "why did this output happen?" after the fact. Without them, the answer is "that's just how it was."

---

## Common Mistakes

**1. Filling the entire context window.**
"The window is 200k, so put it all in" is wrong intuition. Models do not process all inputs equally. Set a token budget and compress within it.

**2. Letting conversation history grow without bound.**
Without sliding window or summarization, after 100 turns the context collapses. Decide a history strategy from day one.

**3. Pasting RAG results raw.**
Attaching the top-20 documents unprocessed leaves 90% noise. Run reranking and compression.

**4. Always exposing every tool schema.**
With 30 tools always shown, the model is more likely to choose the wrong one. Filter per task.

**5. Not masking secrets.**
API keys, PII, and medical data placed straight into context leak via logs and outputs. Mask at ingest time.

---

## Key Takeaways

- Context is a resource. Even a large window has all components competing for the same space, so allocate a token budget upfront.
- Choose conversation-history strategy by task: sliding window, summarization, or selective recall.
- RAG does not stop at retrieval. Reranking and compression raise precision.
- Context Harness designs what to hide as carefully as what to show. Deliberately remove secrets, irrelevant tools, and stale outputs.
- Context snapshots are the foundation of reproducibility and debugging in production agents.

---

<!-- toc:begin -->
## Harness Engineering 101 Series

- [What Is Harness Engineering?](./01-what-is-harness-engineering.md)
- [Task Harness — Turning Vague Work into Executable Tasks](./02-task-harness.md)
- **Context Harness — Designing What to Show and Hide from the Agent (current)**
- Constraint Harness — Defining Rules, Boundaries, and Forbidden Actions (upcoming)
- Tool Harness — Designing Safe Tools for Agents (upcoming)
- Test Harness — Pinning Completion Criteria with Tests (upcoming)
- Feedback Loop — A Repeating Structure That Forces Failures to Be Fixed (upcoming)
- Approval Gate — Designing Where Human Approval Is Required (upcoming)
- Observability — Tracing and Reproducing Agent Work (upcoming)
- Production Harness — Building an Operable Agent Work Environment (upcoming)
<!-- toc:end -->

## References

- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [Liu et al. — Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)
- [LangChain — Contextual Compression Retriever](https://python.langchain.com/docs/how_to/contextual_compression/)
- [OpenAI — Retrieval-Augmented Generation Best Practices](https://cookbook.openai.com/examples/question_answering_using_embeddings)

Tags: AI Agent, Harness, Context, RAG
