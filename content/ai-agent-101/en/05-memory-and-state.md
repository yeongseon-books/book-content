---
title: "AI Agent 101 (5/10): Memory and State"
series: ai-agent-101
episode: 5
language: en
status: publish-ready
targets:
  tistory: false
  hashnode: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Memory
- State Management
- Context Window
last_reviewed: '2026-05-15'
seo_description: Short-term memory, long-term memory, execution state, and context window — how to keep agents reliable across long workflows.
---

# AI Agent 101 (5/10): Memory and State

An agent that handles one or two tool calls rarely reveals memory problems. But once conversations grow, multi-step workflows accumulate, and users ask follow-up questions, new issues surface: how much context to keep, what to discard, and what to store as structured state.

This is the 5th post in the AI Agent 101 series.

Many beginners treat memory and state as the same thing, but in production separating them is far safer. Memory is about preserving past information; state is a structured record of the current execution position.

Stuffing everything into the prompt also does not scale. The context window is finite, token cost grows super-linearly in perceived impact, and stale history can blur current decisions.

This post separates short-term memory, long-term memory, and state, then establishes criteria for deciding where each piece of information belongs.

![Memory and state split](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/05/05-01-memory-and-state-split.en.png)
*Memory and state split*
> Memory preserves useful past information; state tells the workflow where the current execution stands.

## Questions to Keep in Mind

- What design problem appears when agent memory and state are treated as the same store?
- When do short-term memory, long-term memory, and execution state each matter?
- When the context window is tight, what should be summarized and what must remain exact?

## Why This Post Matters

Memory design determines perceived agent quality. It keeps users from repeating themselves, prevents the agent from forgetting mid-task, and makes follow-up questions feel natural. At the same time, poor design is the fastest path to cost and error explosions.

In production, separating state is especially important. If you only carry history, recovering the current workflow position after a restart is hard. If you only carry state, you lose user preferences and prior decision rationale. Splitting the two layers makes restart, checkpoint, and retry all easier.

Memory also connects to evaluation. Unless you measure what was stored, when it was retrieved, and whether retrieval actually helped, you are left with a vague impression that "adding memory improved things" and optimization stalls.

## Core Perspective

If you think of memory as a single "remember everything" blob, the design tangles fast. I usually split with two questions. First, **what should be kept long-term**. Second, **where are we right now**. The first is memory; the second is state.

With this separation, storage choices become simpler. User preferences, past summaries, and knowledge snippets are long-term memory candidates. Current step, completed tasks, and remaining work are state candidates. Mixing them in one structure makes reads harder and change conflicts more frequent.

In practice, "put only the minimum context the current turn needs plus the current position" outlasts "put everything in" by a wide margin.

> Good memory design is not about remembering more — it is about separating long-lived information from current execution state and retrieving each only when needed.

## Core Concepts

### A single flow diagram makes the design boundary between memory and state obvious

![Short-term memory vs long-term memory](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/05/05-01-short-term-memory-vs-long-term-memory.en.png)
*Short-term memory is the working set for the current conversation, state is the current execution position, and long-term memory is information worth keeping for the next session. Fixing this distinction first keeps the design stable.*

### Short-term memory is the working context within the current session

```python
from typing import List, Dict

class ShortTermMemory:
    """Short-term memory: retained only during current session"""

    def __init__(self, system_prompt: str):
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]

    def add_user_message(self, content: str):
        """Add user message"""
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        """Add agent response"""
        self.messages.append({"role": "assistant", "content": content})

    def get_context(self) -> List[Dict[str, str]]:
        """Return current context"""
        return self.messages

    def clear(self):
        """Clear memory on session end"""
        system_msg = self.messages[0]
        self.messages = [system_msg]

# Usage example
memory = ShortTermMemory(system_prompt="You are a helpful assistant.")

memory.add_user_message("What's the weather today?")
memory.add_assistant_message("Today's weather in Seoul is sunny.")

memory.add_user_message("How about tomorrow?")
# Agent remembers previous conversation and understands "tomorrow" refers to weather

print(f"Message count: {len(memory.get_context())}")  # 4 (system + user + assistant + user)
```

Short-term memory is the easiest to implement but the quickest to bloat. As conversation lengthens, sending it raw to the LLM gets expensive, and old messages can distort current decisions. That is why sliding window or summary compaction must follow.

### Long-term memory is information extracted outside the session

```python
import json
from datetime import datetime
from typing import List, Dict, Optional

class LongTermMemory:
    """Long-term memory: permanently stored in external storage"""

    def __init__(self, storage_path: str = "memory.json"):
        self.storage_path = storage_path
        self.memories: Dict[str, List[Dict]] = self._load()

    def _load(self) -> Dict[str, List[Dict]]:
        """Load memory from storage"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save(self):
        """Save memory to storage"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)

    def add_memory(self, user_id: str, key: str, value: str):
        """Add information to user's memory"""
        if user_id not in self.memories:
            self.memories[user_id] = []

        self.memories[user_id].append({
            "key": key,
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def retrieve_memory(self, user_id: str, key: Optional[str] = None) -> List[Dict]:
        """Retrieve user's memory"""
        if user_id not in self.memories:
            return []

        memories = self.memories[user_id]

        if key:
            return [m for m in memories if m["key"] == key]

        return memories
```

The key to long-term memory is not injecting all of it every turn. Store generously, but retrieve narrowly. Only information that retains value outside the session — user preferences, past work summaries, repeatedly used facts — belongs here.

### Real systems combine both but keep state separate

```python
class HybridMemory:
    """Short-term memory + long-term memory combined"""

    def __init__(self, user_id: str, system_prompt: str):
        self.user_id = user_id
        self.short_term = ShortTermMemory(system_prompt)
        self.long_term = LongTermMemory()

    def start_session(self):
        """Load relevant information from long-term memory on session start"""
        memories = self.long_term.retrieve_memory(self.user_id)

        if memories:
            context = "Previous user preferences:\n"
            for mem in memories:
                context += f"- {mem['key']}: {mem['value']}\n"

            self.short_term.messages[0]["content"] += f"\n\n{context}"

    def add_user_message(self, content: str):
        """Add user message"""
        self.short_term.add_user_message(content)

    def add_assistant_message(self, content: str):
        """Add agent response"""
        self.short_term.add_assistant_message(content)

    def save_important_info(self, key: str, value: str):
        """Save important information to long-term memory"""
        self.long_term.add_memory(self.user_id, key, value)

    def get_context(self) -> List[Dict[str, str]]:
        """Return current context"""
        return self.short_term.get_context()

    def end_session(self):
        """Session end: clear short-term memory"""
        self.short_term.clear()
```

This example shows only memory combination, but production systems keep a separate `state` object alongside it. Fields like `current_step`, `completed_steps`, `pending_actions`, and `retry_count` belong in state rather than history. That way resumption and recovery are straightforward.

### Verifying restart recovery first clarifies the role of state

The example below is the smallest form that restores where to resume even when a long-running workflow breaks mid-way, using only `state.json`.

```python
import json
from pathlib import Path

STATE_PATH = Path("state.json")

def save_state(step: str, completed: list[str]) -> None:
    STATE_PATH.write_text(
        json.dumps({"current_step": step, "completed": completed}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"current_step": "collect", "completed": []}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))

state = load_state()
print("before:", state)

if state["current_step"] == "collect":
    state["completed"].append("collect")
    state["current_step"] = "summarize"
    save_state(state["current_step"], state["completed"])

reloaded = load_state()
print("after:", reloaded)
```

**Expected output:**

```text
before: {'current_step': 'collect', 'completed': []}
after: {'current_step': 'summarize', 'completed': ['collect']}
```

Simple as it is, this shows that what a workflow needs for recovery is often not the full conversation text but the current position and completed list. Separating state from history makes the recovery path much shorter.

### The context window is a working set, not a storage layer

- Include only what the current turn's decision directly needs.
- Compress old conversation into summaries.
- Move frequently reused facts to long-term memory.
- Maintain the current execution position in a separate state structure.
- Prioritize retrieval precision over volume when injecting memory.

### Viewing failure modes from the state perspective first hardens the memory design

- If you pile up history without separately saving the current step, recovery after a restart cannot determine which stage was active.
- If you store every trivial exchange in long-term memory, retrieval precision drops and current decisions get blurred by noise.
- If you compress summaries too aggressively, user constraints and prior decision rationale disappear.
- If you apply no compression at all, the context window and cost hit limits first.

In practice, two questions work well for deciding where to store information: "Is this needed for the next step decision?" and "Will this be needed again in a future session?" If only the first applies, it goes to short-term or state. If the second also applies, it goes to long-term memory.

## Production Design Details

### Separating memory layers reduces both forgetting and leakage

Dumping memory into one store is simple initially but soon creates quality and security problems. Production separates short-term execution state, session memory, and long-term user profile.

| Layer | Stored Data | TTL | Access Rule |
| --- | --- | --- | --- |
| Execution state | Current run's step record | Deleted on run end | Planner/validator read only |
| Session memory | Recent conversation/work summary | 1–7 days | Scoped to user |
| Long-term memory | Preferences, prohibitions | 30 days–permanent | Stored after explicit consent |

### Redis-based session memory example

```python
import json
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def save_session_memory(session_id: str, item: dict):
    key = f"agent:session:{session_id}"
    r.rpush(key, json.dumps(item, ensure_ascii=False))
    r.expire(key, 60 * 60 * 24 * 3)

def load_recent_memory(session_id: str, limit: int = 20) -> list[dict]:
    key = f"agent:session:{session_id}"
    rows = r.lrange(key, -limit, -1)
    return [json.loads(x) for x in rows]
```

Enforcing TTL in code moves the retention policy from documentation-dependent to execution-dependent. This distinction matters for privacy regulation compliance.

### Re-ranking before injecting retrieved memory

```python
def rerank(memories: list[dict], goal: str) -> list[dict]:
    # Simple example: score by overlap with goal tokens
    tokens = set(goal.lower().split())
    scored = []
    for m in memories:
        score = sum(1 for t in tokens if t in m.get("summary", "").lower())
        scored.append((score, m))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored[:8]]
```

Injecting all retrieved memories into the prompt increases cost and noise simultaneously. Searching then re-ranking to inject only a few items is more stable.

### State corruption detection rules

| Rule | Description |
| --- | --- |
| monotonic_step | Step number must not decrease |
| immutable_goal | Goal must not change mid-execution |
| checksum_match | Must chain to previous state hash |
| tool_result_schema | Tool results must satisfy schema |

State corruption is rare but extremely hard to reproduce when it occurs. Adding basic integrity checks per loop iteration makes a big difference in long-term operations.

## Operations Notes

### Failure classification template

In production you never close a failure with "the model got it wrong." Splitting failure axes like the template below makes improvement priorities clear.

| Axis | Question | Example |
| --- | --- | --- |
| Planning failure | Was the goal decomposed wrong? | Unnecessary step repeated 6 times |
| Execution failure | Did a tool call fail? | Timeout, 429, schema mismatch |
| Verification failure | Was result checking insufficient? | Wrong observation adopted |
| Policy failure | Was a safety boundary crossed? | Sensitive data sent externally |

Pinning this table to the runbook lets on-call engineers classify incidents with the same criteria.

### Prompt and tool version pinning

```json
{
  "run_id": "run_2026_05_21_001",
  "model": "gpt-4.1-mini",
  "prompt_version": "agent-101-en-v3",
  "tool_schema_version": "tools-v5",
  "policy_version": "policy-2026-05"
}
```

Version fields alone dramatically speed up regression analysis. You can immediately narrow whether a quality drop came from a model change, prompt change, or tool change.

### Observability event example

```python
import json
from datetime import datetime

def emit_event(event_type: str, payload: dict):
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "payload": payload,
    }
    print(json.dumps(record, ensure_ascii=False))

emit_event("agent.step", {"step": 2, "tool": "search_docs", "latency_ms": 412})
```

Introducing structured logs first lowers migration cost when later expanding to OpenTelemetry, ELK, or Grafana.

### Deployment checklist

- Confirm model API keys are separated into environment variables and Secret Manager.
- Verify `max_steps`, `timeout_ms`, `retry_budget` defaults fit the production profile.
- Check that fallback response wording does not give users overconfident assurances during outages.
- Keep alarm thresholds (`error_rate`, `p95_latency`, `policy_violation_rate`) identical in docs and code.

### Cost control points

| Item | Description | Recommended Default |
| --- | --- | --- |
| max_steps | Max loops per execution | 4–8 |
| max_tool_calls | Tool call ceiling | 3–6 |
| input_token_budget | Input token budget | Per-service policy |
| output_token_budget | Output token budget | Per-service policy |

Cost control is not an add-on after performance optimization. Fixing execution budgets from the start keeps the service stable during usage spikes.

### CI gate example for preventing quality regression

```bash
python3 scripts/eval_agent.py --dataset eval/agent_core_en.jsonl --min-success 0.82
python3 scripts/check_tool_schema.py --strict
python3 scripts/check_prompt_version.py --require-changelog
```

Automating minimum quality gates in the deployment pipeline reduces "accidentally good-looking builds" from reaching production.

## Common Misconceptions

- Keeping history long seems like it would make the agent smarter, but in practice it can increase cost and confusion together.
- Putting memory and state in the same dict feels convenient short-term but makes retry and recovery harder.
- It is tempting to solve long-term memory with a single vector DB, but many pieces of information fit a simple key-value store better.
- Storage alone is not enough — if retrieval precision is low, harmful context enters the prompt.
- Filling the context window to capacity feels like utilization, but reducing the working set is actually more stable.

## Operations Checklist

- [ ] Storage criteria for short-term and long-term memory are separated
- [ ] A dedicated state structure exists for the current workflow position
- [ ] A policy for summarizing or compressing old history is in place
- [ ] Long-term memory retrieval results are filtered before injection
- [ ] Memory usage, retrieval hits, and context length are measured

## Wrap-Up

Memory and state are the foundation that lets an agent survive over time. But without distinguishing them, cost quickly balloons, the current position gets lost, and retry and recovery become difficult. So the starting point of good design is not remembering more — it is classifying what kind of memory each piece is.

Short-term memory is the current session's working set, long-term memory is an asset to retrieve later, and state is control information about how far execution has progressed. When these three layers are separated, workflow, reliability, and evaluation all become more robust.

The next post examines multi-agent systems that build on this foundation. As the number of roles grows, who reads which state and who shares which memory must be designed even more explicitly.

## Answering the Opening Questions

- **What design problem appears when agent memory and state are treated as the same store?**
  - Mixing them tangles long-lived knowledge with the current execution position, making resume, summary, and deletion criteria all blurry.
- **When do short-term memory, long-term memory, and execution state each matter?**
  - Short-term memory holds the current conversation context, long-term memory stores knowledge worth retrieving across sessions, and execution state tracks workflow step and intermediate results.
- **When the context window is tight, what should be summarized and what must remain exact?**
  - Keep evidence and tool results exact when they are needed for reproducibility. Summarize repetitive conversation and old explanations to free context.

<!-- toc:begin -->
## In this series

- [AI Agent 101 (1/10): What Is an AI Agent?](./01-what-is-an-ai-agent.md)
- [AI Agent 101 (2/10): Context Engineering](./02-context-engineering.md)
- [AI Agent 101 (3/10): Tool Use Fundamentals](./03-tool-use-fundamentals.md)
- [AI Agent 101 (4/10): Agent Workflow Design](./04-agent-workflow-design.md)
- **AI Agent 101 (5/10): Memory and State (current)**
- AI Agent 101 (6/10): Multi-Agent Systems (upcoming)
- AI Agent 101 (7/10): Agent Evaluation (upcoming)
- AI Agent 101 (8/10): Error Handling and Reliability (upcoming)
- AI Agent 101 (9/10): Production Operations (upcoming)
- AI Agent 101 (10/10): Building Your First Agent (upcoming)

<!-- toc:end -->

## References

### Official Documentation

- [LangGraph - Persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [OpenAI Platform - Conversation state guide](https://platform.openai.com/docs/guides/conversation-state)
- [Anthropic - Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [LangChain - Memory overview](https://python.langchain.com/docs/concepts/chat_history/)

### Related Series

- [LangGraph 101 - Checkpoints and state management](../../langgraph-101/ko/02-state-and-checkpoints.md)
- [RAG 101 - Retrieval context composition](../../multimodal-ai-101/ko/05-multimodal-rag.md)

- [Example code for this post (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-agent-101/en/05-memory-and-state)

Tags: AI Agent, LLM, Tool Use, Python
