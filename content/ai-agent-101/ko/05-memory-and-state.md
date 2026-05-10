---
title: Memory와 State
series: ai-agent-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Memory
- State Management
- Context Window
last_reviewed: '2026-05-02'
seo_description: Agent가 여러 단계를 거쳐 작업을 수행하려면 이전 단계에서 무엇을 했는지 기억해야 합니다. 이것이 Memory입니다.
---

# Memory와 State

> AI Agent 101 시리즈 (5/10)

Agent가 여러 단계를 거쳐 작업을 수행하려면 이전 단계에서 무엇을 했는지 기억해야 합니다. 이것이 Memory입니다. 단기 메모리는 현재 대화 세션 동안 유지되고, 장기 메모리는 세션이 끝나도 유지됩니다.

하지만 모델의 컨텍스트 윈도우는 제한적입니다. 모든 대화 기록을 계속 포함할 수 없으므로, 중요한 정보만 선택해서 유지하거나, 외부 저장소(벡터 DB, 일반 DB)를 활용해야 합니다.

이번 글에서는 단기 메모리와 장기 메모리의 차이, 대화 기록 관리 전략, 컨텍스트 윈도우 관리 방법, 외부 메모리 저장소 활용 패턴을 다룹니다.

---

## 단기 메모리 vs 장기 메모리

## 단기 메모리 vs 장기 메모리

Agent의 Memory는 유지 기간과 용도에 따라 단기 메모리(Short-term Memory)와 장기 메모리(Long-term Memory)로 나뉩니다.

### 단기 메모리 (Short-term Memory)

단기 메모리는 현재 실행 중인 세션 내에서만 유지되는 정보입니다. 대화가 시작되고 끝날 때까지의 컨텍스트를 담습니다.

**특징:**
- 세션이 종료되면 사라집니다.
- 모델의 컨텍스트 윈도우 안에 포함됩니다.
- System prompt, 대화 기록, Tool 호출 결과가 여기 속합니다.

```python
from typing import List, Dict

class ShortTermMemory:
    """단기 메모리: 현재 세션 동안만 유지"""
    
    def __init__(self, system_prompt: str):
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]
    
    def add_user_message(self, content: str):
        """사용자 메시지 추가"""
        self.messages.append({"role": "user", "content": content})
    
    def add_assistant_message(self, content: str):
        """Agent 응답 추가"""
        self.messages.append({"role": "assistant", "content": content})
    
    def get_context(self) -> List[Dict[str, str]]:
        """현재 컨텍스트 반환"""
        return self.messages
    
    def clear(self):
        """세션 종료 시 메모리 초기화"""
        system_msg = self.messages[0]
        self.messages = [system_msg]

# 사용 예시
memory = ShortTermMemory(system_prompt="You are a helpful assistant.")

memory.add_user_message("오늘 날씨는?")
memory.add_assistant_message("오늘 서울 날씨는 맑습니다.")

memory.add_user_message("내일은?")
# Agent는 이전 대화("오늘 날씨")를 기억하고 "내일"이 날씨를 묻는다는 것을 이해합니다.

print(f"메시지 수: {len(memory.get_context())}")  # 4개 (system + user + assistant + user)
```

**장점:**
- 구현이 단순합니다 (메시지 리스트에 append).
- LLM API에 그대로 전달 가능합니다.

**단점:**
- 컨텍스트 윈도우를 계속 소비합니다.
- 세션이 길어지면 토큰 비용이 증가합니다.
- 세션 종료 후 정보가 사라집니다.

---

### 장기 메모리 (Long-term Memory)

장기 메모리는 세션이 끝나도 유지되는 정보입니다. 사용자 선호도, 과거 대화 요약, 누적된 지식 등을 저장합니다.

**특징:**
- 세션 종료 후에도 유지됩니다.
- 외부 저장소(DB, 파일, 벡터 DB)에 저장됩니다.
- 필요할 때만 검색해서 컨텍스트에 주입합니다.

```python
import json
from datetime import datetime
from typing import List, Dict, Optional

class LongTermMemory:
    """장기 메모리: 외부 저장소에 영구 보관"""
    
    def __init__(self, storage_path: str = "memory.json"):
        self.storage_path = storage_path
        self.memories: Dict[str, List[Dict]] = self._load()
    
    def _load(self) -> Dict[str, List[Dict]]:
        """저장소에서 메모리 로드"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save(self):
        """메모리를 저장소에 저장"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)
    
    def add_memory(self, user_id: str, key: str, value: str):
        """특정 사용자의 메모리에 정보 추가"""
        if user_id not in self.memories:
            self.memories[user_id] = []
        
        self.memories[user_id].append({
            "key": key,
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
        self._save()
    
    def retrieve_memory(self, user_id: str, key: Optional[str] = None) -> List[Dict]:
        """특정 사용자의 메모리 검색"""
        if user_id not in self.memories:
            return []
        
        memories = self.memories[user_id]
        
        if key:
            # 특정 키와 일치하는 메모리만 반환
            return [m for m in memories if m["key"] == key]
        
        return memories

# 사용 예시
long_memory = LongTermMemory()

# 세션 1: 사용자 선호도 저장
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

# 세션 2 (나중에 다시 접속): 이전 정보 검색
preferences = long_memory.retrieve_memory(user_id="user123")
print(f"사용자 선호도: {preferences}")
# [{'key': 'language_preference', 'value': 'Korean', 'timestamp': '...'}, ...]

# 특정 키만 검색
lang_pref = long_memory.retrieve_memory(user_id="user123", key="language_preference")
if lang_pref:
    print(f"선호 언어: {lang_pref[0]['value']}")  # Korean
```

**장점:**
- 세션이 끝나도 정보가 유지됩니다.
- 컨텍스트 윈도우를 절약합니다 (필요할 때만 로드).
- 사용자별 맞춤 경험을 제공할 수 있습니다.

**단점:**
- 외부 저장소 관리가 필요합니다.
- 검색 로직이 추가됩니다.
- 정보가 많아지면 검색 속도가 느려질 수 있습니다.

---

### 단기 + 장기 메모리 결합

실제 Agent는 두 가지를 함께 사용합니다.

```python
class HybridMemory:
    """단기 메모리 + 장기 메모리 결합"""
    
    def __init__(self, user_id: str, system_prompt: str):
        self.user_id = user_id
        self.short_term = ShortTermMemory(system_prompt)
        self.long_term = LongTermMemory()
    
    def start_session(self):
        """세션 시작 시 장기 메모리에서 관련 정보 로드"""
        memories = self.long_term.retrieve_memory(self.user_id)
        
        if memories:
            # 장기 메모리 내용을 system prompt에 추가
            context = "Previous user preferences:\n"
            for mem in memories:
                context += f"- {mem['key']}: {mem['value']}\n"
            
            self.short_term.messages[0]["content"] += f"\n\n{context}"
    
    def add_user_message(self, content: str):
        """사용자 메시지 추가"""
        self.short_term.add_user_message(content)
    
    def add_assistant_message(self, content: str):
        """Agent 응답 추가"""
        self.short_term.add_assistant_message(content)
    
    def save_important_info(self, key: str, value: str):
        """중요한 정보는 장기 메모리에 저장"""
        self.long_term.add_memory(self.user_id, key, value)
    
    def get_context(self) -> List[Dict[str, str]]:
        """현재 컨텍스트 반환"""
        return self.short_term.get_context()
    
    def end_session(self):
        """세션 종료: 단기 메모리 초기화"""
        self.short_term.clear()

# 사용 예시
memory = HybridMemory(user_id="user123", system_prompt="You are a helpful assistant.")

# 세션 시작: 장기 메모리에서 이전 정보 로드
memory.start_session()

# 대화
memory.add_user_message("AI Agent에 대해 알려줘")
memory.add_assistant_message("AI Agent는 LLM을 활용해 자율적으로 작업을 수행하는 시스템입니다.")

# 중요한 정보는 장기 메모리에 저장
memory.save_important_info("last_topic", "AI Agent")

# 세션 종료
memory.end_session()

# 다음 세션에서는 "last_topic: AI Agent"가 자동으로 로드됩니다.
```

**핵심 원리:**
- 단기 메모리: 현재 대화 흐름을 유지합니다.
- 장기 메모리: 세션을 넘어 중요한 정보를 보관합니다.
- Agent는 세션 시작 시 장기 메모리에서 관련 정보를 검색해 단기 메모리에 주입합니다.

## 대화 기록 관리
## 대화 기록 관리

대화가 길어지면 컨텍스트 윈도우를 초과하게 됩니다. 모든 대화를 계속 유지할 수 없으므로, 오래된 메시지를 제거하거나 요약해야 합니다.

### 전략 1: 슬라이딩 윈도우 (Sliding Window)

가장 최근 N개의 메시지만 유지하고, 오래된 메시지는 제거합니다.

```python
from typing import List, Dict

class SlidingWindowMemory:
    """슬라이딩 윈도우: 최근 N개 메시지만 유지"""
    
    def __init__(self, system_prompt: str, max_messages: int = 10):
        self.system_prompt = system_prompt
        self.max_messages = max_messages  # system prompt 제외
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]
    
    def add_message(self, role: str, content: str):
        """메시지 추가"""
        self.messages.append({"role": role, "content": content})
        
        # System prompt 제외하고 최근 N개만 유지
        if len(self.messages) - 1 > self.max_messages:
            # System prompt는 유지, 가장 오래된 메시지 2개 제거 (user + assistant 쌍)
            self.messages = [self.messages[0]] + self.messages[3:]
    
    def get_context(self) -> List[Dict[str, str]]:
        """현재 컨텍스트 반환"""
        return self.messages

# 사용 예시
memory = SlidingWindowMemory(system_prompt="You are a helpful assistant.", max_messages=4)

memory.add_message("user", "질문 1")
memory.add_message("assistant", "답변 1")
memory.add_message("user", "질문 2")
memory.add_message("assistant", "답변 2")
memory.add_message("user", "질문 3")  # 질문 1, 답변 1 제거됨

print(f"메시지 수: {len(memory.get_context())}")  # 5개 (system + 최근 4개)
```

**장점:**
- 구현이 단순합니다.
- 컨텍스트 윈도우 사용량이 일정합니다.

**단점:**
- 중요한 초기 정보가 사라질 수 있습니다.
- 대화 맥락이 끊길 수 있습니다.

---

### 전략 2: 요약 기반 압축 (Summarization)

오래된 대화를 LLM으로 요약하고, 요약본을 컨텍스트에 포함합니다.

```python
from openai import OpenAI
from typing import List, Dict

class SummarizationMemory:
    """요약 기반 메모리: 오래된 대화를 요약"""
    
    def __init__(self, system_prompt: str, api_key: str, max_messages: int = 10):
        self.system_prompt = system_prompt
        self.max_messages = max_messages
        self.client = OpenAI(api_key=api_key)
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]
        self.summary: str = ""
    
    def _summarize(self, messages: List[Dict[str, str]]) -> str:
        """대화 내용을 요약"""
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
        """메시지 추가"""
        self.messages.append({"role": role, "content": content})
        
        # 메시지가 많아지면 요약 수행
        if len(self.messages) - 1 > self.max_messages:
            # System prompt 제외하고 처음 절반 요약
            to_summarize = self.messages[1:self.max_messages//2 + 1]
            new_summary = self._summarize(to_summarize)
            
            # 기존 요약과 결합
            if self.summary:
                self.summary += f"\n\n{new_summary}"
            else:
                self.summary = new_summary
            
            # 요약된 부분 제거
            self.messages = [self.messages[0]] + self.messages[self.max_messages//2 + 1:]
    
    def get_context(self) -> List[Dict[str, str]]:
        """현재 컨텍스트 반환 (요약 포함)"""
        system_content = self.system_prompt
        
        if self.summary:
            system_content += f"\n\nPrevious conversation summary:\n{self.summary}"
        
        return [
            {"role": "system", "content": system_content}
        ] + self.messages[1:]

# 사용 예시
memory = SummarizationMemory(
    system_prompt="You are a helpful assistant.",
    api_key="your-api-key",
    max_messages=6
)

memory.add_message("user", "Python으로 웹 스크래핑하는 방법 알려줘")
memory.add_message("assistant", "requests와 BeautifulSoup 라이브러리를 사용하면 됩니다...")
memory.add_message("user", "예제 코드 보여줘")
memory.add_message("assistant", "다음은 예제입니다: import requests...")
memory.add_message("user", "에러 처리는 어떻게?")
memory.add_message("assistant", "try-except로 처리합니다...")
memory.add_message("user", "다른 질문: FastAPI 사용법은?")  
# 이 시점에서 웹 스크래핑 대화가 요약되고, 최근 대화만 유지됩니다.

context = memory.get_context()
print(f"요약: {memory.summary[:100]}...")  # "User asked about web scraping in Python..."
```

**장점:**
- 중요한 정보를 압축해서 유지합니다.
- 대화 맥락이 완전히 사라지지 않습니다.

**단점:**
- 요약 API 호출 비용이 발생합니다.
- 요약 과정에서 세부 정보가 손실될 수 있습니다.

---

### 전략 3: 중요도 기반 선택 (Importance-based Selection)

메시지마다 중요도 점수를 매기고, 중요한 메시지만 유지합니다.

```python
from typing import List, Dict, Tuple

class ImportanceBasedMemory:
    """중요도 기반 메모리: 중요한 메시지만 유지"""
    
    def __init__(self, system_prompt: str, max_messages: int = 10):
        self.system_prompt = system_prompt
        self.max_messages = max_messages
        self.messages: List[Tuple[Dict[str, str], float]] = []  # (message, importance_score)
    
    def _calculate_importance(self, content: str) -> float:
        """메시지 중요도 계산 (간단한 휴리스틱)"""
        importance = 0.5  # 기본 점수
        
        # Tool 호출 결과는 중요
        if "tool_calls" in content or "function_call" in content:
            importance += 0.3
        
        # 질문은 중요
        if "?" in content or "how" in content.lower() or "what" in content.lower():
            importance += 0.2
        
        # 짧은 메시지는 덜 중요
        if len(content) < 20:
            importance -= 0.1
        
        return min(1.0, max(0.0, importance))
    
    def add_message(self, role: str, content: str):
        """메시지 추가 (중요도 점수 계산)"""
        message = {"role": role, "content": content}
        importance = self._calculate_importance(content)
        
        self.messages.append((message, importance))
        
        # 메시지가 많아지면 중요도 낮은 것 제거
        if len(self.messages) > self.max_messages:
            # 중요도 순으로 정렬
            self.messages.sort(key=lambda x: x[1], reverse=True)
            # 상위 max_messages개만 유지
            self.messages = self.messages[:self.max_messages]
            # 시간 순으로 다시 정렬 (대화 흐름 유지)
            self.messages.sort(key=lambda x: self.messages.index(x))
    
    def get_context(self) -> List[Dict[str, str]]:
        """현재 컨텍스트 반환"""
        return [
            {"role": "system", "content": self.system_prompt}
        ] + [msg for msg, _ in self.messages]

# 사용 예시
memory = ImportanceBasedMemory(system_prompt="You are a helpful assistant.", max_messages=5)

memory.add_message("user", "안녕")  # 중요도 낮음 (짧음)
memory.add_message("assistant", "안녕하세요!")  # 중요도 낮음
memory.add_message("user", "Python으로 API 호출하는 방법은?")  # 중요도 높음 (질문)
memory.add_message("assistant", "requests 라이브러리를 사용합니다: import requests...")  # 중요도 중간
memory.add_message("user", "tool_calls: search_api")  # 중요도 높음 (Tool 호출)
memory.add_message("assistant", "검색 결과: ...")  # 중요도 중간
memory.add_message("user", "고마워")  # 중요도 낮음 (짧음) → 제거될 가능성

context = memory.get_context()
print(f"유지된 메시지 수: {len(context) - 1}")  # system 제외
```

**장점:**
- 중요한 정보를 우선적으로 유지합니다.
- Tool 호출 기록 등 핵심 정보가 보존됩니다.

**단점:**
- 중요도 계산 로직이 복잡할 수 있습니다.
- 시간 순서가 섞이면 대화 흐름이 어색해질 수 있습니다.

---

### 전략 비교

| 전략 | 구현 난이도 | 비용 | 정보 보존 | 적합한 상황 |
|------|------------|------|----------|------------|
| 슬라이딩 윈도우 | 낮음 | 없음 | 낮음 (최근 정보만) | 짧은 대화, 단순 Agent |
| 요약 기반 | 중간 | 높음 (요약 API) | 중간 (압축 손실) | 긴 대화, 맥락 유지 필요 |
| 중요도 기반 | 높음 | 없음 | 높음 (선택적 보존) | Tool 사용 Agent, 복잡한 작업 |

실제로는 이 전략들을 조합해서 사용합니다:
- 최근 N개는 그대로 유지 (슬라이딩 윈도우).
- N개를 넘으면 중요도 낮은 메시지 제거 (중요도 기반).
- 주기적으로 오래된 메시지 요약 (요약 기반).

## 컨텍스트 윈도우 관리
## 컨텍스트 윈도우 관리

컨텍스트 윈도우는 모델이 한 번에 처리할 수 있는 토큰 수의 제한입니다. GPT-4의 경우 8K, 32K, 128K 등 모델에 따라 다릅니다.

Agent가 긴 대화나 많은 Tool 호출을 수행하면 컨텍스트 윈도우를 초과할 수 있습니다. 이를 관리하는 전략을 살펴봅니다.

### 토큰 카운팅

API 호출 전에 현재 컨텍스트의 토큰 수를 계산합니다.

```python
import tiktoken
from typing import List, Dict

class TokenAwareMemory:
    """토큰 수를 추적하는 메모리"""
    
    def __init__(self, system_prompt: str, model: str = "gpt-4", max_tokens: int = 8000):
        self.model = model
        self.max_tokens = max_tokens
        self.encoding = tiktoken.encoding_for_model(model)
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]
    
    def count_tokens(self, text: str) -> int:
        """텍스트의 토큰 수 계산"""
        return len(self.encoding.encode(text))
    
    def get_total_tokens(self) -> int:
        """현재 컨텍스트의 총 토큰 수"""
        total = 0
        for msg in self.messages:
            total += self.count_tokens(msg["content"])
            total += 4  # 메시지 구조 오버헤드 (role, content 구분자 등)
        return total
    
    def can_add_message(self, content: str) -> bool:
        """메시지를 추가할 수 있는지 확인"""
        new_tokens = self.count_tokens(content) + 4
        return self.get_total_tokens() + new_tokens <= self.max_tokens
    
    def add_message(self, role: str, content: str):
        """메시지 추가 (토큰 제한 확인)"""
        if not self.can_add_message(content):
            # 토큰 초과 시 오래된 메시지 제거
            self._trim_messages()
        
        self.messages.append({"role": role, "content": content})
    
    def _trim_messages(self):
        """오래된 메시지 제거 (system prompt는 유지)"""
        if len(self.messages) > 1:
            # 가장 오래된 user-assistant 쌍 제거
            self.messages = [self.messages[0]] + self.messages[3:]
    
    def get_context(self) -> List[Dict[str, str]]:
        """현재 컨텍스트 반환"""
        return self.messages

# 사용 예시
memory = TokenAwareMemory(
    system_prompt="You are a helpful assistant.",
    model="gpt-4",
    max_tokens=8000
)

memory.add_message("user", "긴 질문" * 1000)  # 매우 긴 메시지
print(f"총 토큰 수: {memory.get_total_tokens()}")

# 토큰 제한 체크
if memory.can_add_message("다음 질문"):
    memory.add_message("user", "다음 질문")
else:
    print("토큰 제한 초과, 오래된 메시지가 제거됩니다.")
```

**핵심:**
- `tiktoken` 라이브러리로 정확한 토큰 수를 계산합니다.
- 메시지 추가 전에 토큰 제한을 확인합니다.
- 초과 시 오래된 메시지를 제거합니다.

---

### 응답 길이 제한

모델의 응답도 컨텍스트 윈도우를 소비합니다. 응답 길이를 제한해 공간을 확보합니다.

```python
from openai import OpenAI

class LengthControlledAgent:
    """응답 길이를 제어하는 Agent"""
    
    def __init__(self, api_key: str, max_context_tokens: int = 6000, max_response_tokens: int = 1000):
        self.client = OpenAI(api_key=api_key)
        self.max_context_tokens = max_context_tokens
        self.max_response_tokens = max_response_tokens
        self.memory = TokenAwareMemory(
            system_prompt="You are a helpful assistant. Keep responses concise.",
            model="gpt-4",
            max_tokens=max_context_tokens
        )
    
    def run(self, user_message: str) -> str:
        """Agent 실행 (응답 길이 제한)"""
        self.memory.add_message("user", user_message)
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=self.memory.get_context(),
            max_tokens=self.max_response_tokens,  # 응답 길이 제한
            temperature=0.7
        )
        
        assistant_message = response.choices[0].message.content
        self.memory.add_message("assistant", assistant_message)
        
        return assistant_message

# 사용 예시
agent = LengthControlledAgent(
    api_key="your-api-key",
    max_context_tokens=6000,  # 컨텍스트용 6000 토큰
    max_response_tokens=1000  # 응답용 1000 토큰
)

response = agent.run("Python의 장점을 자세히 설명해줘")
# 응답이 1000 토큰을 넘지 않습니다.
```

**전략:**
- `max_tokens` 파라미터로 응답 길이를 제한합니다.
- 컨텍스트 + 응답 = 모델의 윈도우 크기를 넘지 않도록 조정합니다.
- System prompt에 "Keep responses concise" 같은 지시를 추가합니다.

---

### 청크 단위 처리

입력이 너무 크면 여러 청크로 나누어 처리합니다.

```python
from typing import List

class ChunkedProcessor:
    """긴 입력을 청크로 나누어 처리"""
    
    def __init__(self, api_key: str, chunk_size: int = 3000):
        self.client = OpenAI(api_key=api_key)
        self.chunk_size = chunk_size
        self.encoding = tiktoken.encoding_for_model("gpt-4")
    
    def split_into_chunks(self, text: str) -> List[str]:
        """텍스트를 토큰 기준으로 청크 분할"""
        tokens = self.encoding.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), self.chunk_size):
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks
    
    def process_long_document(self, document: str, query: str) -> str:
        """긴 문서를 청크별로 처리하고 결과 결합"""
        chunks = self.split_into_chunks(document)
        results = []
        
        for i, chunk in enumerate(chunks):
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Answer the query based on the given text chunk."},
                    {"role": "user", "content": f"Query: {query}\n\nChunk {i+1}/{len(chunks)}:\n{chunk}"}
                ],
                temperature=0
            )
            
            results.append(response.choices[0].message.content)
        
        # 최종 결과 결합
        final_response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Combine the following answers into a coherent response."},
                {"role": "user", "content": "\n\n".join(results)}
            ],
            temperature=0
        )
        
        return final_response.choices[0].message.content

# 사용 예시
processor = ChunkedProcessor(api_key="your-api-key", chunk_size=3000)

long_document = "매우 긴 문서 내용..." * 5000  # 10만 토큰 이상
query = "이 문서의 핵심 요약은?"

answer = processor.process_long_document(long_document, query)
print(answer)
```

**원리:**
1. 긴 문서를 토큰 기준으로 청크로 분할합니다.
2. 각 청크에 대해 개별적으로 LLM을 호출합니다.
3. 청크별 결과를 결합해 최종 답변을 생성합니다.

**적용 사례:**
- 긴 PDF 문서 분석
- 대량의 로그 파일 요약
- 여러 웹페이지 내용 종합

---

### 컨텍스트 윈도우 관리 체크리스트

**실행 전:**
- [ ] 현재 컨텍스트 토큰 수를 확인합니다.
- [ ] 새로운 메시지 추가 시 토큰 제한을 체크합니다.
- [ ] 응답 길이 제한(`max_tokens`)을 설정합니다.

**실행 중:**
- [ ] 토큰 초과 시 오래된 메시지를 제거하거나 요약합니다.
- [ ] 중요한 정보(system prompt, Tool schema)는 항상 유지합니다.

**실행 후:**
- [ ] 실제 사용된 토큰 수를 로깅합니다 (`usage.total_tokens`).
- [ ] 비용 추적을 위해 토큰 사용량을 모니터링합니다.

```python
# 토큰 사용량 로깅 예시
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages
)

usage = response.usage
print(f"프롬프트 토큰: {usage.prompt_tokens}")
print(f"완성 토큰: {usage.completion_tokens}")
print(f"Total tokens: {usage.total_tokens}")

# 비용 계산 (GPT-4 기준: $0.03/1K prompt tokens, $0.06/1K completion tokens)
cost = (usage.prompt_tokens / 1000 * 0.03) + (usage.completion_tokens / 1000 * 0.06)
print(f"Cost: ${cost:.4f}")
```

**핵심:**
- 컨텍스트 윈도우는 유한한 자원입니다.
- 토큰 수를 추적하고 제한을 사전에 체크합니다.
- 긴 입력은 청크로 나누어 처리합니다.

## 외부 메모리 저장소
## 외부 메모리 저장소

컨텍스트 윈도우를 넘어서는 정보는 외부 저장소에 보관하고, 필요할 때 검색해서 사용합니다.

### 벡터 DB를 활용한 시맨틱 검색

대화 기록이나 지식을 벡터로 변환해 저장하고, 유사도 검색으로 관련 정보를 가져옵니다.

```python
from openai import OpenAI
from typing import List, Dict
import numpy as np
from datetime import datetime

class VectorMemoryStore:
    """벡터 DB 기반 장기 메모리"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.memories: List[Dict] = []  # 실제로는 Pinecone, Weaviate 등 사용
    
    def _get_embedding(self, text: str) -> List[float]:
        """텍스트를 임베딩 벡터로 변환"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def add_memory(self, user_id: str, content: str, metadata: Dict = None):
        """메모리 추가 (벡터로 변환하여 저장)"""
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
        """유사도 기반 메모리 검색"""
        query_embedding = self._get_embedding(query)
        
        # 해당 사용자의 메모리만 필터링
        user_memories = [m for m in self.memories if m["user_id"] == user_id]
        
        if not user_memories:
            return []
        
        # 코사인 유사도 계산
        similarities = []
        for memory in user_memories:
            similarity = self._cosine_similarity(query_embedding, memory["embedding"])
            similarities.append((memory, similarity))
        
        # 유사도 높은 순으로 정렬
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 상위 k개 반환
        return [{"content": m["content"], "similarity": sim} for m, sim in similarities[:top_k]]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """코사인 유사도 계산"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# 사용 예시
memory_store = VectorMemoryStore(api_key="your-api-key")

# 과거 대화 저장
memory_store.add_memory(
    user_id="user123",
    content="사용자가 Python으로 웹 스크래핑 방법을 질문했고, BeautifulSoup 사용을 추천했습니다.",
    metadata={"topic": "web_scraping"}
)
memory_store.add_memory(
    user_id="user123",
    content="사용자가 FastAPI로 REST API 구축 방법을 질문했습니다.",
    metadata={"topic": "fastapi"}
)

# 현재 질문과 관련된 과거 정보 검색
query = "Python 웹 크롤링에 대해 알려줘"
relevant_memories = memory_store.search_memory(user_id="user123", query=query, top_k=2)

print("관련 과거 대화:")
for mem in relevant_memories:
    print(f"- {mem['content']} (유사도: {mem['similarity']:.2f})")

# "웹 스크래핑" 대화가 높은 유사도로 검색됩니다.
```

**장점:**
- 의미적으로 관련된 정보를 찾을 수 있습니다.
- 키워드가 정확히 일치하지 않아도 검색됩니다.

**단점:**
- 임베딩 생성 비용이 발생합니다.
- 벡터 DB 인프라가 필요합니다.

---

### 일반 DB를 활용한 구조화된 저장

구조화된 정보(사용자 프로필, 설정 등)는 일반 DB에 저장합니다.

```python
import sqlite3
from typing import Optional, List, Dict
from datetime import datetime

class StructuredMemoryStore:
    """일반 DB 기반 구조화된 메모리"""
    
    def __init__(self, db_path: str = "memory.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()
    
    def _init_db(self):
        """테이블 생성"""
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
        """사용자 선호도 저장"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_preferences (user_id, key, value, updated_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, key, value, datetime.now().isoformat()))
        self.conn.commit()
    
    def get_preference(self, user_id: str, key: str) -> Optional[str]:
        """사용자 선호도 조회"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT value FROM user_preferences
            WHERE user_id = ? AND key = ?
        """, (user_id, key))
        
        result = cursor.fetchone()
        return result[0] if result else None
    
    def get_all_preferences(self, user_id: str) -> Dict[str, str]:
        """사용자의 모든 선호도 조회"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT key, value FROM user_preferences
            WHERE user_id = ?
        """, (user_id,))
        
        return {row[0]: row[1] for row in cursor.fetchall()}
    
    def save_session_summary(self, user_id: str, session_id: str, summary: str):
        """세션 요약 저장"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO conversation_summary (user_id, session_id, summary, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, session_id, summary, datetime.now().isoformat()))
        self.conn.commit()
    
    def get_recent_summaries(self, user_id: str, limit: int = 5) -> List[Dict]:
        """최근 세션 요약 조회"""
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

# 사용 예시
db_store = StructuredMemoryStore()

# 사용자 선호도 저장
db_store.set_preference("user123", "language", "Korean")
db_store.set_preference("user123", "notification", "enabled")

# 조회
lang = db_store.get_preference("user123", "language")
print(f"선호 언어: {lang}")  # Korean

all_prefs = db_store.get_all_preferences("user123")
print(f"모든 설정: {all_prefs}")

# 세션 요약 저장
db_store.save_session_summary(
    user_id="user123",
    session_id="sess_001",
    summary="사용자가 Python 웹 스크래핑에 대해 질문했고, BeautifulSoup 사용법을 안내받았습니다."
)

# 최근 대화 요약 조회
recent = db_store.get_recent_summaries("user123", limit=3)
print(f"최근 대화: {recent}")
```

**장점:**
- 구조화된 쿼리가 가능합니다 (WHERE, ORDER BY, JOIN 등).
- 트랜잭션 지원으로 데이터 일관성을 보장합니다.
- 인덱스를 활용해 빠른 검색이 가능합니다.

**단점:**
- 의미적 검색이 불가능합니다 (키워드 기반).
- 스키마 설계가 필요합니다.

---

### 하이브리드 저장소 패턴

벡터 DB와 일반 DB를 조합해 사용합니다.

```python
class HybridMemorySystem:
    """벡터 DB + 일반 DB 결합"""
    
    def __init__(self, api_key: str, db_path: str = "memory.db"):
        self.vector_store = VectorMemoryStore(api_key=api_key)
        self.structured_store = StructuredMemoryStore(db_path=db_path)
    
    def initialize_user_context(self, user_id: str, query: str) -> str:
        """사용자 컨텍스트 초기화 (장기 메모리 로드)"""
        context_parts = []
        
        # 1. 구조화된 선호도 로드
        preferences = self.structured_store.get_all_preferences(user_id)
        if preferences:
            context_parts.append("User Preferences:")
            for key, value in preferences.items():
                context_parts.append(f"- {key}: {value}")
        
        # 2. 최근 세션 요약 로드
        recent_summaries = self.structured_store.get_recent_summaries(user_id, limit=3)
        if recent_summaries:
            context_parts.append("\nRecent Conversations:")
            for summary in recent_summaries:
                context_parts.append(f"- {summary['summary']}")
        
        # 3. 현재 질문과 관련된 과거 대화 검색
        relevant_memories = self.vector_store.search_memory(user_id, query, top_k=2)
        if relevant_memories:
            context_parts.append("\nRelevant Past Discussions:")
            for mem in relevant_memories:
                context_parts.append(f"- {mem['content']}")
        
        return "\n".join(context_parts)
    
    def save_conversation(self, user_id: str, session_id: str, messages: List[Dict]):
        """대화 종료 시 저장"""
        # 1. 대화 요약 생성 (실제로는 LLM 호출)
        summary = f"Discussed {len(messages)} topics"
        self.structured_store.save_session_summary(user_id, session_id, summary)
        
        # 2. 중요한 대화는 벡터 DB에 저장
        for msg in messages:
            if msg["role"] == "user" and len(msg["content"]) > 50:
                self.vector_store.add_memory(
                    user_id=user_id,
                    content=msg["content"],
                    metadata={"session_id": session_id}
                )

# 사용 예시
hybrid_system = HybridMemorySystem(api_key="your-api-key")

# 세션 시작: 장기 메모리 로드
user_context = hybrid_system.initialize_user_context(
    user_id="user123",
    query="Python 데이터 분석 방법 알려줘"
)

print("User Context:")
print(user_context)
# 출력:
# User Preferences:
# - language: Korean
# Recent Conversations:
# - 사용자가 Python 웹 스크래핑에 대해 질문...
# Relevant Past Discussions:
# - Python pandas를 사용한 데이터 분석...

# 이 컨텍스트를 system prompt에 추가해 Agent에 전달합니다.
```

**핵심 원리:**
- **구조화된 정보** (선호도, 설정) → 일반 DB
- **시맨틱 검색이 필요한 정보** (대화 기록, 지식) → 벡터 DB
- Agent는 세션 시작 시 두 저장소에서 관련 정보를 검색해 컨텍스트에 주입합니다.

---

### 외부 메모리 활용 시 고려사항

**검색 타이밍:**
- 세션 시작 시: 사용자 프로필, 최근 대화 요약 로드
- 질문마다: 현재 질문과 관련된 과거 정보 검색
- Tool 실행 전: Tool 사용 이력 검색

**검색 범위 제한:**
```python
# 너무 많은 정보를 가져오면 컨텍스트 윈도우 초과
relevant_memories = vector_store.search_memory(
    user_id="user123",
    query=query,
    top_k=3  # 상위 3개만
)

# 시간 범위 제한
recent_summaries = structured_store.get_recent_summaries(
    user_id="user123",
    limit=5  # 최근 5개 세션만
)
```

**비용 관리:**
- 임베딩 생성은 비용이 발생하므로, 중요한 메시지만 벡터화합니다.
- 캐싱을 활용해 동일한 쿼리의 반복 검색을 피합니다.

**개인정보 보호:**
- 사용자 동의 없이 대화 내용을 장기 저장하지 않습니다.
- 민감한 정보(비밀번호, 카드번호)는 저장하지 않습니다.
- 데이터 삭제 요청 시 완전히 제거합니다.

---

## 흔한 실수 5가지

### 실수 1: 컨텍스트 윈도우 초과를 사전에 체크하지 않음

**나쁜 예:**
```python
# 토큰 수를 체크하지 않고 계속 메시지 추가
messages.append({"role": "user", "content": user_input})
response = client.chat.completions.create(model="gpt-4", messages=messages)
# 컨텍스트 윈도우 초과 시 에러 발생
```

**좋은 예:**
```python
import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4")

def count_tokens(messages):
    total = sum(len(encoding.encode(msg["content"])) for msg in messages)
    return total

# 메시지 추가 전 토큰 수 체크
if count_tokens(messages) + len(encoding.encode(user_input)) < 7000:
    messages.append({"role": "user", "content": user_input})
else:
    # 오래된 메시지 제거
    messages = [messages[0]] + messages[-5:]
    messages.append({"role": "user", "content": user_input})
```

**교훈**: 토큰 제한을 사전에 체크해 에러를 방지합니다.

---

### 실수 2: 모든 대화 기록을 무조건 유지

**나쁜 예:**
```python
# 대화가 길어져도 계속 누적
class MemoryNoLimit:
    def __init__(self):
        self.messages = []
    
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        # 수십 번의 대화 후 토큰 초과 또는 비용 폭증
```

**좋은 예:**
```python
class MemoryWithLimit:
    def __init__(self, max_messages=10):
        self.messages = []
        self.max_messages = max_messages
    
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        
        # 제한 초과 시 슬라이딩 윈도우 적용
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
```

**교훈**: 대화 기록에 명확한 제한을 설정합니다.

---

### 실수 3: System Prompt를 메모리 관리 대상에 포함

**나쁜 예:**
```python
# System prompt도 함께 제거
def trim_messages(messages):
    return messages[-5:]  # System prompt가 사라질 수 있음
```

**좋은 예:**
```python
def trim_messages(messages):
    # System prompt는 항상 유지
    system_msg = messages[0]
    recent_msgs = messages[-5:]
    
    if system_msg not in recent_msgs:
        return [system_msg] + recent_msgs
    return recent_msgs
```

**교훈**: System prompt는 Agent의 역할과 지시사항을 담고 있으므로 항상 유지합니다.

---

### 실수 4: 장기 메모리를 세션마다 다시 검색

**나쁜 예:**
```python
# 매 메시지마다 장기 메모리 검색
def run_agent(user_message):
    preferences = long_term_memory.retrieve(user_id)  # 반복적인 DB 조회
    context = build_context(preferences, user_message)
    response = llm.generate(context)
    return response
```

**좋은 예:**
```python
class Agent:
    def __init__(self, user_id):
        self.user_id = user_id
        # 세션 시작 시 한 번만 로드
        self.preferences = long_term_memory.retrieve(user_id)
    
    def run(self, user_message):
        # 이미 로드된 선호도 사용
        context = build_context(self.preferences, user_message)
        response = llm.generate(context)
        return response
```

**교훈**: 장기 메모리는 세션 시작 시 한 번만 로드하고 캐시합니다.

---

### 실수 5: 중요한 정보와 불필요한 정보를 구분하지 않음

**나쁜 예:**
```python
# 모든 대화를 장기 메모리에 저장
def save_conversation(user_id, messages):
    for msg in messages:
        long_term_memory.add(user_id, msg["content"])
# "안녕", "고마워" 같은 인사도 모두 저장됨
```

**좋은 예:**
```python
def save_conversation(user_id, messages):
    for msg in messages:
        # 중요한 정보만 저장 (길이, 키워드 기준)
        if len(msg["content"]) > 50 and msg["role"] == "user":
            # 질문이나 요청만 저장
            if any(keyword in msg["content"] for keyword in ["?", "how", "what", "알려줘", "방법"]):
                long_term_memory.add(user_id, msg["content"])
```

**교훈**: 중요한 정보만 선별해서 장기 메모리에 저장합니다.

## 핵심 요약

- Agent는 Memory를 통해 이전 행동과 결과를 기억하고 다음 행동을 결정합니다.
- 컨텍스트 윈도우 제한 때문에 중요한 정보만 선택해서 유지해야 합니다.
- 장기 메모리가 필요한 경우 외부 저장소(벡터 DB, 일반 DB)를 활용합니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Agent란 무엇인가?](./01-what-is-an-ai-agent.md)
- [컨텍스트 엔지니어링](./02-context-engineering.md)
- [Tool Use 기초](./03-tool-use-fundamentals.md)
- [Agent Workflow 설계](./04-agent-workflow-design.md)
- **Memory와 State (현재 글)**
- Multi-Agent 시스템 (예정)
- Agent 평가 (예정)
- 에러 처리와 안정성 (예정)
- 운영 (예정)
- 첫 Agent 만들기 (예정)

<!-- toc:end -->

---

## 참고 자료

1. **LangChain Memory Documentation** - https://python.langchain.com/docs/modules/memory/  
   LangChain의 다양한 메모리 패턴 구현. 슬라이딩 윈도우, 요약 기반, 벡터 저장소 활용 방법을 다룹니다.

2. **OpenAI Embeddings API** - https://platform.openai.com/docs/guides/embeddings  
   텍스트를 벡터로 변환하는 임베딩 API 문서. 시맨틱 검색 기반 메모리 구현에 필요합니다.

3. **tiktoken** - https://github.com/openai/tiktoken  
   OpenAI의 공식 토큰 카운팅 라이브러리. 컨텍스트 윈도우 관리에 필수적입니다.

4. **Building LLM Applications: Memory Systems** - https://www.pinecone.io/learn/series/langchain/langchain-conversational-memory/  
   Pinecone의 대화형 Agent 메모리 시스템 가이드. 벡터 DB 활용 패턴을 설명합니다.

Tags: AI Agent, LLM, Tool Use, Python
