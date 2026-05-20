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
seo_description: For agents to perform multi-step tasks, they must remember what they
  did in previous steps. This is memory.
---

# AI Agent 101 (5/10): Memory and State

For agents to perform multi-step tasks, they must remember what they did in previous steps. This is memory. Short-term memory persists during the current conversation session, while long-term memory persists beyond sessions.

However, model context windows are limited. You can't keep including all conversation history, so you must selectively maintain important information or leverage external storage (vector DB, general DB).

This is post 5 in the AI Agent 101 series. Here we cover the difference between short-term and long-term memory, conversation history management strategies, context window management methods, and external memory storage utilization patterns.

## Questions to Keep in Mind

- What design problem appears when agent memory and state are treated as the same store?
- When do short-term memory, long-term memory, and execution state each matter?
- When the context window is tight, what should be summarized and what must remain exact?

## Big Picture

![Memory and state split](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/05/05-01-memory-and-state-split.en.png)

*Memory and state split*

This picture separates the current-turn working set, execution state for workflow position, and long-term memory for later retrieval. Memory design is not storing more; it is placing the right information in the right layer for the next decision.

> Memory preserves useful past information; state tells the workflow where the current execution stands.

## Short-term Memory vs Long-term Memory

## Short-term Memory vs Long-term Memory

Agent memory is divided into short-term memory and long-term memory based on retention period and purpose.

![Short-term Memory vs Long-term Memory](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/05/05-01-short-term-memory-vs-long-term-memory.en.png)
*A practical memory design separates the working set for the current turn, the execution state for the current workflow position, and the long-term store for information worth retrieving later.*

### Short-term Memory

Short-term memory is information retained only within the current execution session. It holds the context from conversation start to end.

**Characteristics:**
- Disappears when the session ends.
- Contained within the model's context window.
- Includes system prompt, conversation history, and tool call results.

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
# Agent remembers previous conversation ("weather today") and understands "tomorrow" refers to weather

print(f"Message count: {len(memory.get_context())}")  # 4 (system + user + assistant + user)
```

**Pros:**
- Simple implementation (just append to message list).
- Can be passed directly to LLM API.

**Cons:**
- Continuously consumes context window.
- Token cost increases as session grows.
- Information disappears after session ends.

---

### Long-term Memory

Long-term memory is information persisted beyond session end. It stores user preferences, past conversation summaries, and accumulated knowledge.

**Characteristics:**
- Persists after session end.
- Stored in external storage (DB, files, vector DB).
- Retrieved and injected into context only when needed.

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
            # Return only memories matching the key
            return [m for m in memories if m["key"] == key]
        
        return memories

# Usage example
long_memory = LongTermMemory()

# Session 1: Save user preferences
long_memory.add_memory(
    user_id="user123",
    key="language_preference",
    value="Korean"
)
long_memory.add_memory(
    user_id="user123",
    key="topic_interest",
    value="AI Agent"
)

# Session 2 (later reconnection): Retrieve previous information
preferences = long_memory.retrieve_memory(user_id="user123")
print(f"User preferences: {preferences}")
# [{'key': 'language_preference', 'value': 'Korean', 'timestamp': '...'}, ...]

# Retrieve specific key only
lang_pref = long_memory.retrieve_memory(user_id="user123", key="language_preference")
if lang_pref:
    print(f"Preferred language: {lang_pref[0]['value']}")  # Korean
```

**Pros:**
- Information persists after session ends.
- Saves context window (load only when needed).
- Enables personalized user experience.

**Cons:**
- Requires external storage management.
- Adds search logic complexity.
- Search speed may slow with large information sets.

---

### Combining Short-term + Long-term Memory

Real agents use both together.

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
            # Add long-term memory content to system prompt
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

# Usage example
memory = HybridMemory(user_id="user123", system_prompt="You are a helpful assistant.")

# Start session: Load previous information from long-term memory
memory.start_session()

# Conversation
memory.add_user_message("Tell me about AI Agents")
memory.add_assistant_message("AI Agents are systems that autonomously perform tasks using LLMs.")

# Save important information to long-term memory
memory.save_important_info("last_topic", "AI Agent")

# End session
memory.end_session()

# Next session will automatically load "last_topic: AI Agent"
```

**Core Principle:**
- Short-term memory: Maintains current conversation flow.
- Long-term memory: Stores important information beyond sessions.
- Agent searches long-term memory for relevant information on session start and injects it into short-term memory.

## Conversation History Management

As conversations grow longer, they exceed the context window. Since you can't keep all messages indefinitely, you must remove old messages or summarize them.

### Strategy 1: Sliding Window

Keep only the most recent N messages and remove older ones.

```python
from typing import List, Dict

class SlidingWindowMemory:
    """Sliding window: retain only recent N messages"""
    
    def __init__(self, system_prompt: str, max_messages: int = 10):
        self.system_prompt = system_prompt
        self.max_messages = max_messages  # excluding system prompt
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]
    
    def add_message(self, role: str, content: str):
        """Add message"""
        self.messages.append({"role": role, "content": content})
        
        # Keep only recent N messages (excluding system prompt)
        if len(self.messages) - 1 > self.max_messages:
            # Keep system prompt, remove oldest 2 messages (user + assistant pair)
            self.messages = [self.messages[0]] + self.messages[3:]
    
    def get_context(self) -> List[Dict[str, str]]:
        """Return current context"""
        return self.messages

# Usage example
memory = SlidingWindowMemory(system_prompt="You are a helpful assistant.", max_messages=4)

memory.add_message("user", "Question 1")
memory.add_message("assistant", "Answer 1")
memory.add_message("user", "Question 2")
memory.add_message("assistant", "Answer 2")
memory.add_message("user", "Question 3")  # Question 1, Answer 1 removed

print(f"Message count: {len(memory.get_context())}")  # 5 (system + recent 4)
```

**Pros:**
- Simple implementation.
- Constant context window usage.

**Cons:**
- Important early information may be lost.
- Conversation context may break.

---

### Strategy 2: Summarization-based Compression

Summarize old conversations with LLM and include the summary in context.

```python
from openai import OpenAI
from typing import List, Dict

class SummarizationMemory:
    """Summarization-based memory: summarize old conversations"""
    
    def __init__(self, system_prompt: str, api_key: str, max_messages: int = 10):
        self.system_prompt = system_prompt
        self.max_messages = max_messages
        self.client = OpenAI(api_key=api_key)
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]
        self.summary: str = ""
    
    def _summarize(self, messages: List[Dict[str, str]]) -> str:
        """Summarize conversation content"""
        conversation = "\n".join([
            f"{msg['role']}: {msg['content']}" for msg in messages if msg['role'] != 'system'
        ])
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Summarize the following conversation in 2-3 sentences."},
                {"role": "user", "content": conversation}
            ],
            temperature=0
        )
        
        return response.choices[0].message.content
    
    def add_message(self, role: str, content: str):
        """Add message"""
        self.messages.append({"role": role, "content": content})
        
        # Summarize when messages grow too large
        if len(self.messages) - 1 > self.max_messages:
            # Summarize first half (excluding system prompt)
            to_summarize = self.messages[1:self.max_messages//2 + 1]
            new_summary = self._summarize(to_summarize)
            
            # Combine with existing summary
            if self.summary:
                self.summary += f"\n\n{new_summary}"
            else:
                self.summary = new_summary
            
            # Remove summarized portion
            self.messages = [self.messages[0]] + self.messages[self.max_messages//2 + 1:]
    
    def get_context(self) -> List[Dict[str, str]]:
        """Return current context (including summary)"""
        system_content = self.system_prompt
        
        if self.summary:
            system_content += f"\n\nPrevious conversation summary:\n{self.summary}"
        
        return [
            {"role": "system", "content": system_content}
        ] + self.messages[1:]

# Usage example
memory = SummarizationMemory(
    system_prompt="You are a helpful assistant.",
    api_key="your-api-key",
    max_messages=6
)

memory.add_message("user", "How to do web scraping in Python?")
memory.add_message("assistant", "Use requests and BeautifulSoup libraries...")
memory.add_message("user", "Show me example code")
memory.add_message("assistant", "Here's an example: import requests...")
memory.add_message("user", "How about error handling?")
memory.add_message("assistant", "Handle with try-except...")
memory.add_message("user", "Different question: How to use FastAPI?")  
# At this point, web scraping conversation gets summarized, only recent conversation retained

context = memory.get_context()
print(f"Summary: {memory.summary[:100]}...")  # "User asked about web scraping in Python..."
```

**Pros:**
- Important information is compressed and retained.
- Conversation context doesn't completely disappear.

**Cons:**
- Summary API call costs.
- Detail loss during summarization.

---

### Strategy 3: Importance-based Selection

Score each message by importance and keep only important messages.

```python
from typing import List, Dict, Tuple

class ImportanceBasedMemory:
    """Importance-based memory: retain only important messages"""
    
    def __init__(self, system_prompt: str, max_messages: int = 10):
        self.system_prompt = system_prompt
        self.max_messages = max_messages
        self.messages: List[Tuple[Dict[str, str], float]] = []  # (message, importance_score)
    
    def _calculate_importance(self, content: str) -> float:
        """Calculate message importance (simple heuristic)"""
        importance = 0.5  # base score
        
        # Tool call results are important
        if "tool_calls" in content or "function_call" in content:
            importance += 0.3
        
        # Questions are important
        if "?" in content or "how" in content.lower() or "what" in content.lower():
            importance += 0.2
        
        # Short messages are less important
        if len(content) < 20:
            importance -= 0.1
        
        return min(1.0, max(0.0, importance))
    
    def add_message(self, role: str, content: str):
        """Add message (calculate importance score)"""
        message = {"role": role, "content": content}
        importance = self._calculate_importance(content)
        
        self.messages.append((message, importance))
        
        # Remove low-importance messages when too many
        if len(self.messages) > self.max_messages:
            # Sort by importance
            self.messages.sort(key=lambda x: x[1], reverse=True)
            # Keep top max_messages only
            self.messages = self.messages[:self.max_messages]
            # Re-sort by time (maintain conversation flow)
            self.messages.sort(key=lambda x: self.messages.index(x))
    
    def get_context(self) -> List[Dict[str, str]]:
        """Return current context"""
        return [
            {"role": "system", "content": self.system_prompt}
        ] + [msg for msg, _ in self.messages]

# Usage example
memory = ImportanceBasedMemory(system_prompt="You are a helpful assistant.", max_messages=5)

memory.add_message("user", "Hi")  # Low importance (short)
memory.add_message("assistant", "Hello!")  # Low importance
memory.add_message("user", "How to call APIs in Python?")  # High importance (question)
memory.add_message("assistant", "Use requests library: import requests...")  # Medium importance
memory.add_message("user", "tool_calls: search_api")  # High importance (tool call)
memory.add_message("assistant", "Search results: ...")  # Medium importance
memory.add_message("user", "Thanks")  # Low importance (short) → likely to be removed

context = memory.get_context()
print(f"Retained messages: {len(context) - 1}")  # excluding system
```

**Pros:**
- Important information is prioritized.
- Tool call history and key information preserved.

**Cons:**
- Importance calculation logic can be complex.
- Time order mixing can make conversation flow awkward.

---

### Strategy Comparison

| Strategy | Implementation Complexity | Cost | Information Retention | Suitable For |
|----------|--------------------------|------|----------------------|--------------|
| Sliding Window | Low | None | Low (recent only) | Short conversations, simple agents |
| Summarization | Medium | High (summary API) | Medium (compression loss) | Long conversations, context needed |
| Importance-based | High | None | High (selective retention) | Tool-using agents, complex tasks |

In practice, these strategies are combined:
- Keep recent N messages as-is (sliding window).
- Remove low-importance messages when exceeding N (importance-based).
- Periodically summarize old messages (summarization).

## Context Window Management

The context window is the limit on the number of tokens a model can process at once. For GPT-4, this varies by model: 8K, 32K, 128K, etc.

Agents performing long conversations or many tool calls can exceed the context window. Let's examine strategies to manage this.

### Token Counting

Calculate the current context's token count before API calls.

```python
import tiktoken
from typing import List, Dict

class TokenAwareMemory:
    """Token-tracking memory"""
    
    def __init__(self, system_prompt: str, model: str = "gpt-4o", max_tokens: int = 8000):
        self.model = model
        self.max_tokens = max_tokens
        self.encoding = tiktoken.encoding_for_model(model)
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]
    
    def count_tokens(self, text: str) -> int:
        """Calculate text token count"""
        return len(self.encoding.encode(text))
    
    def get_total_tokens(self) -> int:
        """Get total token count of current context"""
        total = 0
        for msg in self.messages:
            total += self.count_tokens(msg["content"])
            total += 4  # message structure overhead (role, content separators, etc.)
        return total
    
    def can_add_message(self, content: str) -> bool:
        """Check if message can be added"""
        new_tokens = self.count_tokens(content) + 4
        return self.get_total_tokens() + new_tokens <= self.max_tokens
    
    def add_message(self, role: str, content: str):
        """Add message (check token limit)"""
        if not self.can_add_message(content):
            # Remove old messages when exceeding token limit
            self._trim_messages()
        
        self.messages.append({"role": role, "content": content})
    
    def _trim_messages(self):
        """Remove old messages (keep system prompt)"""
        if len(self.messages) > 1:
            # Remove oldest user-assistant pair
            self.messages = [self.messages[0]] + self.messages[3:]
    
    def get_context(self) -> List[Dict[str, str]]:
        """Return current context"""
        return self.messages

# Usage example
memory = TokenAwareMemory(
    system_prompt="You are a helpful assistant.",
    model="gpt-4o",
    max_tokens=8000
)

memory.add_message("user", "long question" * 1000)  # very long message
print(f"Total tokens: {memory.get_total_tokens()}")

# Check token limit
if memory.can_add_message("next question"):
    memory.add_message("user", "next question")
else:
    print("Token limit exceeded, old messages will be removed.")
```

**Core:**
- Use `tiktoken` library for accurate token counting.
- Check token limit before adding messages.
- Remove old messages when exceeding limit.

---

### Response Length Limiting

Model responses also consume the context window. Limit response length to preserve space.

```python
from openai import OpenAI

class LengthControlledAgent:
    """Agent with response length control"""
    
    def __init__(self, api_key: str, max_context_tokens: int = 6000, max_response_tokens: int = 1000):
        self.client = OpenAI(api_key=api_key)
        self.max_context_tokens = max_context_tokens
        self.max_response_tokens = max_response_tokens
        self.memory = TokenAwareMemory(
            system_prompt="You are a helpful assistant. Keep responses concise.",
            model="gpt-4o",
            max_tokens=max_context_tokens
        )
    
    def run(self, user_message: str) -> str:
        """Run agent (with response length limit)"""
        self.memory.add_message("user", user_message)
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.memory.get_context(),
            max_tokens=self.max_response_tokens,  # Response length limit
            temperature=0.7
        )
        
        assistant_message = response.choices[0].message.content
        self.memory.add_message("assistant", assistant_message)
        
        return assistant_message

# Usage example
agent = LengthControlledAgent(
    api_key="your-api-key",
    max_context_tokens=6000,  # 6000 tokens for context
    max_response_tokens=1000  # 1000 tokens for response
)

response = agent.run("Explain Python's advantages in detail")
# Response won't exceed 1000 tokens
```

**Strategy:**
- Use `max_tokens` parameter to limit response length.
- Adjust so context + response doesn't exceed model's window size.
- Add instructions like "Keep responses concise" to system prompt.

---

### Chunk-based Processing

When input is too large, split into chunks for processing.

```python
from typing import List

class ChunkedProcessor:
    """Process long input by splitting into chunks"""
    
    def __init__(self, api_key: str, chunk_size: int = 3000):
        self.client = OpenAI(api_key=api_key)
        self.chunk_size = chunk_size
        self.encoding = tiktoken.encoding_for_model("gpt-4o")
    
    def split_into_chunks(self, text: str) -> List[str]:
        """Split text into chunks by token count"""
        tokens = self.encoding.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), self.chunk_size):
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks
    
    def process_long_document(self, document: str, query: str) -> str:
        """Process long document chunk-by-chunk and combine results"""
        chunks = self.split_into_chunks(document)
        results = []
        
        for i, chunk in enumerate(chunks):
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Answer the query based on the given text chunk."},
                    {"role": "user", "content": f"Query: {query}\n\nChunk {i+1}/{len(chunks)}:\n{chunk}"}
                ],
                temperature=0
            )
            
            results.append(response.choices[0].message.content)
        
        # Combine final results
        final_response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Combine the following answers into a coherent response."},
                {"role": "user", "content": "\n\n".join(results)}
            ],
            temperature=0
        )
        
        return final_response.choices[0].message.content

# Usage example
processor = ChunkedProcessor(api_key="your-api-key", chunk_size=3000)

long_document = "very long document content..." * 5000  # 100K+ tokens
query = "What's the key summary of this document?"

answer = processor.process_long_document(long_document, query)
print(answer)
```

**Principle:**
1. Split long document into chunks by token count.
2. Call LLM individually for each chunk.
3. Combine chunk results to generate final answer.

**Use Cases:**
- Long PDF document analysis
- Large log file summarization
- Multiple webpage content synthesis

---

### Context Window Management Checklist

**Before Execution:**
- [ ] Check current context token count.
- [ ] Check token limit when adding new messages.
- [ ] Set response length limit (`max_tokens`).

**During Execution:**
- [ ] Remove or summarize old messages when exceeding tokens.
- [ ] Always maintain important information (system prompt, tool schema).

**After Execution:**
- [ ] Log actual token usage (`usage.total_tokens`).
- [ ] Monitor token usage for cost tracking.

```python
# Token usage logging example
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)

usage = response.usage
print(f"Prompt tokens: {usage.prompt_tokens}")
print(f"Completion tokens: {usage.completion_tokens}")
print(f"Total tokens: {usage.total_tokens}")

# Cost calculation (GPT-4: $0.03/1K prompt tokens, $0.06/1K completion tokens)
cost = (usage.prompt_tokens / 1000 * 0.03) + (usage.completion_tokens / 1000 * 0.06)
print(f"Cost: ${cost:.4f}")
```

**Core:**
- Context window is a finite resource.
- Track token count and check limits proactively.
- Split long inputs into chunks for processing.

---

## External Memory Storage

Information exceeding the context window is stored in external storage and retrieved when needed.

### Vector DB for Semantic Search

Convert conversation history or knowledge to vectors, store them, and retrieve related information via similarity search.

```python
from openai import OpenAI
from typing import List, Dict
import numpy as np
from datetime import datetime

class VectorMemoryStore:
    """Vector DB-based long-term memory"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.memories: List[Dict] = []  # Use Pinecone, Weaviate, etc. in practice
    
    def _get_embedding(self, text: str) -> List[float]:
        """Convert text to embedding vector"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def add_memory(self, user_id: str, content: str, metadata: Dict = None):
        """Add memory (convert to vector and store)"""
        embedding = self._get_embedding(content)
        
        memory = {
            "user_id": user_id,
            "content": content,
            "embedding": embedding,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.memories.append(memory)
    
    def search_memory(self, user_id: str, query: str, top_k: int = 3) -> List[Dict]:
        """Similarity-based memory search"""
        query_embedding = self._get_embedding(query)
        
        # Filter to user's memories only
        user_memories = [m for m in self.memories if m["user_id"] == user_id]
        
        if not user_memories:
            return []
        
        # Calculate cosine similarity
        similarities = []
        for memory in user_memories:
            similarity = self._cosine_similarity(query_embedding, memory["embedding"])
            similarities.append((memory, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k
        return [{"content": m["content"], "similarity": sim} for m, sim in similarities[:top_k]]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# Usage example
memory_store = VectorMemoryStore(api_key="your-api-key")

# Store past conversations
memory_store.add_memory(
    user_id="user123",
    content="User asked about web scraping in Python, recommended BeautifulSoup.",
    metadata={"topic": "web_scraping"}
)
memory_store.add_memory(
    user_id="user123",
    content="User asked about building REST API with FastAPI.",
    metadata={"topic": "fastapi"}
)

# Search for past information related to current question
query = "Tell me about Python web crawling"
relevant_memories = memory_store.search_memory(user_id="user123", query=query, top_k=2)

print("Related past conversations:")
for mem in relevant_memories:
    print(f"- {mem['content']} (similarity: {mem['similarity']:.2f})")

# "web scraping" conversation retrieved with high similarity
```

**Pros:**
- Can find semantically related information.
- Works even when keywords don't match exactly.

**Cons:**
- Embedding generation costs.
- Requires vector DB infrastructure.

---

### General DB for Structured Storage

Store structured information (user profiles, settings, etc.) in general DB.

```python
import sqlite3
from typing import Optional, List, Dict
from datetime import datetime

class StructuredMemoryStore:
    """General DB-based structured memory"""
    
    def __init__(self, db_path: str = "memory.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()
    
    def _init_db(self):
        """Create tables"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT,
                key TEXT,
                value TEXT,
                updated_at TEXT,
                PRIMARY KEY (user_id, key)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                session_id TEXT,
                summary TEXT,
                created_at TEXT
            )
        """)
        self.conn.commit()
    
    def set_preference(self, user_id: str, key: str, value: str):
        """Save user preference"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_preferences (user_id, key, value, updated_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, key, value, datetime.now().isoformat()))
        self.conn.commit()
    
    def get_preference(self, user_id: str, key: str) -> Optional[str]:
        """Retrieve user preference"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT value FROM user_preferences
            WHERE user_id = ? AND key = ?
        """, (user_id, key))
        
        result = cursor.fetchone()
        return result[0] if result else None
    
    def get_all_preferences(self, user_id: str) -> Dict[str, str]:
        """Retrieve all user preferences"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT key, value FROM user_preferences
            WHERE user_id = ?
        """, (user_id,))
        
        return {row[0]: row[1] for row in cursor.fetchall()}
    
    def save_session_summary(self, user_id: str, session_id: str, summary: str):
        """Save session summary"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO conversation_summary (user_id, session_id, summary, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, session_id, summary, datetime.now().isoformat()))
        self.conn.commit()
    
    def get_recent_summaries(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Retrieve recent session summaries"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT session_id, summary, created_at
            FROM conversation_summary
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit))
        
        return [
            {"session_id": row[0], "summary": row[1], "created_at": row[2]}
            for row in cursor.fetchall()
        ]

# Usage example
db_store = StructuredMemoryStore()

# Save user preferences
db_store.set_preference("user123", "language", "Korean")
db_store.set_preference("user123", "notification", "enabled")

# Retrieve
lang = db_store.get_preference("user123", "language")
print(f"Preferred language: {lang}")  # Korean

all_prefs = db_store.get_all_preferences("user123")
print(f"All settings: {all_prefs}")

# Save session summary
db_store.save_session_summary(
    user_id="user123",
    session_id="sess_001",
    summary="User asked about Python web scraping and was guided on BeautifulSoup usage."
)

# Retrieve recent conversation summaries
recent = db_store.get_recent_summaries("user123", limit=3)
print(f"Recent conversations: {recent}")
```

**Pros:**
- Structured queries possible (WHERE, ORDER BY, JOIN, etc.).
- Transaction support ensures data consistency.
- Fast search using indexes.

**Cons:**
- Semantic search impossible (keyword-based).
- Schema design required.

---

### Hybrid Storage Pattern

Combine vector DB and general DB.

```python
class HybridMemorySystem:
    """Vector DB + general DB combined"""
    
    def __init__(self, api_key: str, db_path: str = "memory.db"):
        self.vector_store = VectorMemoryStore(api_key=api_key)
        self.structured_store = StructuredMemoryStore(db_path=db_path)
    
    def initialize_user_context(self, user_id: str, query: str) -> str:
        """Initialize user context (load long-term memory)"""
        context_parts = []
        
        # 1. Load structured preferences
        preferences = self.structured_store.get_all_preferences(user_id)
        if preferences:
            context_parts.append("User Preferences:")
            for key, value in preferences.items():
                context_parts.append(f"- {key}: {value}")
        
        # 2. Load recent session summaries
        recent_summaries = self.structured_store.get_recent_summaries(user_id, limit=3)
        if recent_summaries:
            context_parts.append("\nRecent Conversations:")
            for summary in recent_summaries:
                context_parts.append(f"- {summary['summary']}")
        
        # 3. Search past conversations related to current question
        relevant_memories = self.vector_store.search_memory(user_id, query, top_k=2)
        if relevant_memories:
            context_parts.append("\nRelevant Past Discussions:")
            for mem in relevant_memories:
                context_parts.append(f"- {mem['content']}")
        
        return "\n".join(context_parts)
    
    def save_conversation(self, user_id: str, session_id: str, messages: List[Dict]):
        """Save on conversation end"""
        # 1. Generate conversation summary (use LLM in practice)
        summary = f"Discussed {len(messages)} topics"
        self.structured_store.save_session_summary(user_id, session_id, summary)
        
        # 2. Save important conversations to vector DB
        for msg in messages:
            if msg["role"] == "user" and len(msg["content"]) > 50:
                self.vector_store.add_memory(
                    user_id=user_id,
                    content=msg["content"],
                    metadata={"session_id": session_id}
                )

# Usage example
hybrid_system = HybridMemorySystem(api_key="your-api-key")

# Session start: Load long-term memory
user_context = hybrid_system.initialize_user_context(
    user_id="user123",
    query="Tell me about Python data analysis"
)

print("User Context:")
print(user_context)
# Output:
# User Preferences:
# - language: Korean
# Recent Conversations:
# - User asked about Python web scraping...
# Relevant Past Discussions:
# - Data analysis using Python pandas...

# Add this context to system prompt and pass to agent
```

**Core Principle:**
- **Structured information** (preferences, settings) → general DB
- **Information needing semantic search** (conversation history, knowledge) → vector DB
- Agent searches both stores for relevant information on session start and injects into context.

---

### External Memory Considerations

**Search Timing:**
- Session start: Load user profile, recent conversation summary
- Per question: Search past information related to current question
- Before tool execution: Search tool usage history

**Search Scope Limits:**
```python
# Fetching too much information exceeds context window
relevant_memories = vector_store.search_memory(
    user_id="user123",
    query=query,
    top_k=3  # Top 3 only
)

# Time range limit
recent_summaries = structured_store.get_recent_summaries(
    user_id="user123",
    limit=5  # Recent 5 sessions only
)
```

**Cost Management:**
- Embedding generation costs, so vectorize only important messages.
- Use caching to avoid repeated searches for identical queries.

**Privacy Protection:**
- Don't store conversation content long-term without user consent.
- Don't store sensitive information (passwords, card numbers).
- Completely remove data when deletion requested.

---

## Common Mistakes

### Mistake 1: Not Pre-checking Context Window Limits

**Bad:**
```python
# Add messages without checking token count
messages.append({"role": "user", "content": user_input})
response = client.chat.completions.create(model="gpt-4o", messages=messages)
# Error when context window exceeded
```

**Good:**
```python
import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4o")

def count_tokens(messages):
    total = sum(len(encoding.encode(msg["content"])) for msg in messages)
    return total

# Check token count before adding message
if count_tokens(messages) + len(encoding.encode(user_input)) < 7000:
    messages.append({"role": "user", "content": user_input})
else:
    # Remove old messages
    messages = [messages[0]] + messages[-5:]
    messages.append({"role": "user", "content": user_input})
```

**Lesson**: Pre-check token limits to prevent errors.

---

### Mistake 2: Unconditionally Keeping All Conversation History

**Bad:**
```python
# Continuously accumulate even as conversation grows
class MemoryNoLimit:
    def __init__(self):
        self.messages = []
    
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        # Token overflow or cost explosion after dozens of exchanges
```

**Good:**
```python
class MemoryWithLimit:
    def __init__(self, max_messages=10):
        self.messages = []
        self.max_messages = max_messages
    
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        
        # Apply sliding window when exceeding limit
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
```

**Lesson**: Set clear limits on conversation history.

---

### Mistake 3: Including System Prompt in Memory Management

**Bad:**
```python
# Remove system prompt along with others
def trim_messages(messages):
    return messages[-5:]  # System prompt may disappear
```

**Good:**
```python
def trim_messages(messages):
    # Always keep system prompt
    system_msg = messages[0]
    recent_msgs = messages[-5:]
    
    if system_msg not in recent_msgs:
        return [system_msg] + recent_msgs
    return recent_msgs
```

**Lesson**: Always maintain system prompt as it contains agent role and instructions.

---

### Mistake 4: Re-searching Long-term Memory Every Session

**Bad:**
```python
# Search long-term memory every message
def run_agent(user_message):
    preferences = long_term_memory.retrieve(user_id)  # Repeated DB queries
    context = build_context(preferences, user_message)
    response = llm.generate(context)
    return response
```

**Good:**
```python
class Agent:
    def __init__(self, user_id):
        self.user_id = user_id
        # Load once on session start
        self.preferences = long_term_memory.retrieve(user_id)
    
    def run(self, user_message):
        # Use already-loaded preferences
        context = build_context(self.preferences, user_message)
        response = llm.generate(context)
        return response
```

**Lesson**: Load long-term memory once on session start and cache.

---

### Mistake 5: Not Distinguishing Important from Unnecessary Information

**Bad:**
```python
# Save all conversations to long-term memory
def save_conversation(user_id, messages):
    for msg in messages:
        long_term_memory.add(user_id, msg["content"])
# Greetings like "Hi", "Thanks" all saved
```

**Good:**
```python
def save_conversation(user_id, messages):
    for msg in messages:
        # Save only important information (by length, keywords)
        if len(msg["content"]) > 50 and msg["role"] == "user":
            # Save only questions or requests
            if any(keyword in msg["content"] for keyword in ["?", "how", "what", "tell me", "method"]):
                long_term_memory.add(user_id, msg["content"])
```

**Lesson**: Selectively save only important information to long-term memory.

---

## Key Takeaways

- Agents use memory to remember previous actions and results and decide next actions.
- Context window limitations require selectively maintaining only important information.
- When long-term memory is needed, leverage external storage (vector DB, general DB).

<!-- a-grade-example:begin -->

## Checklist

- [ ] Can explain short vs long memory in one sentence.
- [ ] Compared sliding-window vs summarization truncation.
- [ ] Wrote code that auto-summarizes near the token limit.
- [ ] Built a one-table guide on when to pick Vector vs KV.

<!-- a-grade-example:end -->

## Answering the Opening Questions

- **What design problem appears when agent memory and state are treated as the same store?**
  - Mixing them blurs what should be retained, summarized, deleted, or used to resume execution. Long-lived knowledge and current workflow position need different rules.
- **When do short-term memory, long-term memory, and execution state each matter?**
  - Short-term memory holds the current conversation, long-term memory stores information worth retrieving across sessions, and execution state tracks workflow position and intermediate results.
- **When the context window is tight, what should be summarized and what must remain exact?**
  - Keep evidence and tool results exactly when they are needed for reproducibility. Summarize repetitive conversation or old explanation to save context.

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

---

## References

- [OpenAI conversation state guide](https://platform.openai.com/docs/guides/conversation-state)
- [OpenAI embeddings guide](https://platform.openai.com/docs/guides/embeddings)
- [LangGraph persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [tiktoken](https://github.com/openai/tiktoken)

Tags: AI Agent, LLM, Tool Use, Python
