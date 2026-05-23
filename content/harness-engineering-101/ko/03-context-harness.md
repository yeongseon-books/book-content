---
title: "Harness Engineering 101 (3/10): Context Harness — Agent에게 줄 정보와 숨길 정보 설계하기"
series: harness-engineering-101
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Harness
- Context
- RAG
last_reviewed: '2026-05-14'
seo_description: Agent가 받는 컨텍스트는 결과를 결정합니다. 너무 적으면 추측하고, 너무 많으면 길을 잃습니다.
---

# Harness Engineering 101 (3/10): Context Harness — Agent에게 줄 정보와 숨길 정보 설계하기
에이전트 시스템에서 가장 자주 과소평가되는 자원은 모델이 아니라 컨텍스트입니다. 팀은 더 많은 문서, 더 긴 대화 이력, 더 많은 도구 스키마를 넣으면 품질이 좋아질 것이라고 기대합니다. 실제 운영에서는 반대가 더 자주 일어납니다.
정보가 많아질수록 모델은 느려지고 비싸지고, 관련 없는 텍스트에 흔들리며, 중간의 중요한 정보를 놓칩니다. 큰 컨텍스트 윈도우는 여유 공간이 아니라 여러 출처가 서로 밀어내는 경쟁 공간에 가깝습니다.
Context Harness는 이 경쟁을 설계하는 층입니다. 어떤 정보를 어느 시점에 보여줄지, 어떤 정보는 의도적으로 숨길지, 긴 이력과 RAG 문서를 어떻게 압축할지를 먼저 정해야 합니다.
결국 컨텍스트 품질은 길이보다 밀도로 결정됩니다.

![Context Harness - Agent에게 줄 정보와 숨길 정보 설계하기](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/03/03-01-context-harness-designing-what-the-agent.ko.png)
*Context Harness - Agent에게 줄 정보와 숨길 정보 설계하기*
> Context Harness의 목표는 더 많은 정보를 넣는 것이 아니라, agent가 지금 결정해야 할 정보만 보게 만드는 일입니다.

## 먼저 던지는 질문

- Context Harness는 왜 무한한 메모리가 아니라 제한된 예산 배분 문제일까요?
- agent에게 보여줄 정보와 숨길 정보는 어떤 기준으로 나눠야 할까요?
- retrieved context가 많아질수록 정밀도는 어떻게 지켜야 할까요?

## 왜 이 글이 중요한가
Context Harness가 중요한 첫 번째 이유는 비용입니다. 너무 많은 컨텍스트는 단순히 토큰만 더 쓰는 것이 아니라 추론 시간을 늘리고, 잡음을 키우고, 잘못된 결론으로 끌고 갑니다.
두 번째 이유는 재현성입니다. 운영에서 왜 이런 출력이 나왔는지 설명하려면 그 순간 모델이 실제로 무엇을 봤는지 알아야 합니다. 동적으로 조립되는 컨텍스트에서는 스냅샷이 없으면 재현이 거의 불가능합니다.
세 번째 이유는 보안입니다. 비밀 값과 PII가 컨텍스트에 들어간 순간 로그와 출력으로 새어 나갈 수 있습니다. 무엇을 보여줄지와 무엇을 숨길지를 동시에 설계해야 합니다.
## 핵심 관점
에이전트가 한 번의 추론에서 보는 컨텍스트는 하나의 긴 문자열이 아니라 여러 출처가 경쟁하는 예산입니다. 시스템 프롬프트, 태스크 명세, history, retrieval, 도구 스키마, 최근 도구 출력이 모두 같은 창 안에 들어가려 합니다.
실무에서는 history와 retrieval이 가장 위험합니다. history는 오래될수록 길어지고, retrieval은 recall을 높일수록 문서 수가 불어납니다. 그래서 Context Harness는 무엇을 넣을지보다 무엇을 언제 얼마나 줄일지에 더 가깝습니다.
좋은 Context Harness는 정보량보다 정보 밀도를 관리합니다. 모델이 봐야 할 내용을 무조건 많이 주는 대신, 판단에 필요한 내용을 가장 압축된 형태로 전달하는 설계입니다.
> 컨텍스트 품질은 길이보다 밀도로 결정됩니다. 필요한 정보를 정해진 슬롯 안에 정확히 배치하는 편이 훨씬 중요합니다.
## 핵심 개념
Agent가 받는 컨텍스트는 결과를 결정합니다. 너무 적으면 추측하고, 너무 많으면 길을 잃습니다. Context Harness는 Agent에게 줄 정보와 숨길 정보를 설계하는 일입니다.

### Context는 자원입니다

Agent의 context window는 무한하지 않습니다. GPT-4o는 128k tokens, Claude Sonnet 4는 200k tokens, Gemini 2.5 Pro는 1M tokens. 숫자가 커 보이지만 실제로는 항상 부족합니다. 시스템 프롬프트, 대화 이력, 검색된 문서, 도구 스키마, 직전 도구 출력이 모두 같은 공간을 두고 경쟁합니다.

게다가 context가 클수록 모델은 느려지고 비싸지고 정확도가 떨어집니다. "lost in the middle" 현상으로 중간에 있는 정보는 무시되기 쉽고, 관련 없는 정보는 추론을 흔듭니다. context는 자원입니다. 무한정 부어 넣는 것이 아니라 설계해야 하는 자원입니다.

Context Harness는 Agent가 어떤 정보를 어느 시점에 받고, 어떤 정보를 받지 않는지를 명시적으로 설계합니다. 이번 글에서는 context의 구성 요소, 선택 전략, 그리고 의도적으로 숨겨야 할 정보를 다룹니다.

### Context의 5가지 구성 요소

![Context의 5가지 구성 요소](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/03/03-02-the-five-components-of-context.ko.png)

*Context의 5가지 구성 요소*

Agent가 한 번의 추론에서 보는 context는 다섯 가지로 나뉩니다.

1. **System prompt**: Agent의 역할, 규칙, 목표. 거의 변하지 않습니다.
2. **Task spec**: 이번 task의 Goal, Inputs, Completion criteria. Task마다 바뀝니다.
3. **Conversation history**: 이전 turn의 메시지. 시간이 지날수록 길어집니다.
4. **Retrieved context**: RAG, 메모리, 외부 데이터 소스에서 가져온 정보. Task와 관련된 것만 가져와야 합니다.
5. **Tool schemas and outputs**: 사용 가능한 도구의 명세와 직전 호출 결과.

각 요소는 토큰 예산을 가집니다. 200k window라면 system prompt 2k, task spec 1k, history 5k, retrieved 10k, tool schemas 3k 같은 식으로 미리 분배합니다. 분배하지 않으면 history나 retrieved가 무한정 자라서 다른 요소를 잠식합니다.

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

예산이 정해지면 각 요소를 그 안으로 압축하는 것이 Context Harness의 역할입니다.

### Conversation History 관리 전략

대화 이력은 가장 빨리 자라는 요소입니다. 세 가지 전략을 조합합니다.

**1. Sliding window**: 최근 N개의 turn만 유지합니다. 가장 단순합니다. 오래된 정보는 사라집니다.

**2. Summarization**: 오래된 turn을 요약본으로 대체합니다. 정보는 유지되지만 디테일은 사라집니다.

**3. Selective recall**: 필요할 때만 과거 turn을 재검색해서 가져옵니다. RAG와 결합합니다.

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
        # 실무에서는 LLM으로 요약합니다
        return f"[Summary: {len(messages)} turns]"

    def to_context(self) -> list[dict]:
        result = []
        if self.summary:
            result.append({"role": "system", "content": self.summary})
        result.extend({"role": m.role, "content": m.content} for m in self.messages)
        return result
```

전략 선택 기준은 task의 성격입니다. 짧은 대화는 sliding이면 충분합니다. 긴 협업 task는 summarization이 필요합니다. 과거 결정을 정확히 참조해야 하는 task는 selective recall을 씁니다.

### Retrieved Context의 정밀도

![Retrieved Context의 정밀도](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/03/03-03-precision-in-retrieved-context.ko.png)

*Retrieved Context의 정밀도*

RAG로 가져온 문서는 context의 큰 부분을 차지합니다. 가져오는 양보다 가져오는 정밀도가 중요합니다.

문서 10개를 통째로 넣으면 90%는 task와 무관합니다. 무관한 정보는 단순한 낭비가 아니라 추론을 방해합니다. 모델은 모든 입력을 "관련 있다"고 가정하고 추론하기 때문에, 관련 없는 텍스트가 잘못된 결론으로 끌고 갑니다.

세 단계로 정밀도를 높입니다.

**1. Retrieval**: 후보 20~50개를 가져옵니다. recall 우선.
**2. Reranking**: cross-encoder로 task와의 관련도를 다시 점수화해서 상위 5~10개만 남깁니다. precision 우선.
**3. Compression**: 각 문서에서 task와 관련된 문장만 추출합니다. LLM 또는 extractive summarizer로.

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

Retrieval만으로 끝내는 시스템은 context를 낭비합니다. Reranking과 Compression이 Context Harness의 핵심입니다.

### 의도적으로 숨겨야 할 정보

context에 넣으면 안 되는 정보가 있습니다. Context Harness는 무엇을 보여줄지 못지않게 무엇을 숨길지를 설계합니다.

**1. 비밀 정보**: API 키, 사용자 비밀번호, PII (개인 식별 정보), 의료 기록. Agent의 출력이나 로그로 새어 나갈 수 있습니다. context에 들어가지 않게 마스킹하거나 토큰화합니다.

**2. 무관한 도구 스키마**: 이번 task에 필요 없는 도구의 schema는 빼야 합니다. 도구가 많으면 모델은 "다 써야 한다"고 추측합니다.

**3. 모순되는 지시**: 시스템 프롬프트와 사용자 메시지가 모순되면 모델은 어느 쪽을 따를지 결정하지 못합니다. 명확한 우선순위를 정하거나 모순을 제거합니다.

**4. 오래된 도구 출력**: 5번 전 도구 호출의 결과는 보통 현재 task와 무관합니다. 가장 최근 N개의 도구 출력만 유지합니다.

**5. 실패한 시도의 상세**: Agent가 한 번 실패한 접근을 다시 시도하지 않게 "이 방법은 실패했음"이라는 사실만 남기고 디테일은 압축합니다.

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

숨기는 설계는 보여주는 설계만큼 중요합니다.

### Context Snapshot으로 재현성 확보

![Context Snapshot으로 재현성 확보](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/03/03-04-context-snapshots-for-reproducibility.ko.png)

*Context Snapshot으로 재현성 확보*

Production agent는 같은 입력에 같은 출력을 내야 합니다. 그런데 context는 여러 단계를 거쳐 조립되기 때문에 재현이 어렵습니다. Context Snapshot으로 해결합니다.

각 추론 직전의 최종 context를 그대로 저장합니다. 나중에 같은 context를 모델에 주면 (temperature 0이라면) 같은 출력이 나옵니다. 디버깅과 재현 테스트의 기반입니다.

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

Snapshot이 있으면 "왜 이런 출력이 나왔는가?"를 사후에 분석할 수 있습니다. 없으면 "그때는 그랬다"로 끝납니다.

### Context 조립 YAML과 슬롯 검증

Context Harness를 운영 환경으로 옮기면 가장 먼저 필요한 것은 조립 규칙의 외부화입니다. 코드 안에서 하드코딩된 순서로 메시지를 붙이면 릴리스마다 diff를 추적하기 어렵습니다. 슬롯 기반 YAML을 두고, 각 슬롯의 최대 토큰과 우선순위를 검증하는 방식이 유지보수에 유리합니다.

```yaml
# context_assembly.yaml
context_policy:
  version: 1
  slots:
    - name: system_prompt
      max_tokens: 2000
      required: true
    - name: task_spec
      max_tokens: 1200
      required: true
    - name: conversation_summary
      max_tokens: 1800
      required: false
    - name: retrieved_context
      max_tokens: 7000
      required: true
      rerank_top_k: 8
      compression: extractive
    - name: tool_schemas
      max_tokens: 3000
      required: true
    - name: guardrail_notes
      max_tokens: 800
      required: false
  response_buffer_tokens: 4000
  hard_window_tokens: 32000
```

```python
from dataclasses import dataclass

@dataclass
class Slot:
    name: str
    max_tokens: int
    required: bool

def validate_slots(slots: list[Slot], response_buffer: int, hard_window: int) -> None:
    total = sum(s.max_tokens for s in slots) + response_buffer
    if total > hard_window:
        raise ValueError(f"context budget overflow: {total} > {hard_window}")

    names = [s.name for s in slots]
    if len(names) != len(set(names)):
        raise ValueError("duplicate slot name detected")

    required_missing = [s.name for s in slots if s.required and s.max_tokens <= 0]
    if required_missing:
        raise ValueError(f"required slots misconfigured: {required_missing}")
```

이 검증을 부팅 단계에서 강제하면 retrieved_context를 과도하게 키워 응답 버퍼가 사라지는 사고를 사전에 막을 수 있습니다.

또 하나의 실전 팁은 슬롯별 품질 메트릭을 따로 남기는 것입니다. retrieved_context 슬롯에는 hit-rate와 overlap-rate, history 슬롯에는 summary compression ratio를 기록하면 "어느 슬롯이 품질을 깎는지"를 수치로 볼 수 있습니다. Context Harness는 조립 규칙을 만드는 단계에서 끝나지 않고, 슬롯별 성능을 지속적으로 관찰해야 안정화됩니다.

예를 들어 hit-rate는 높지만 overlap-rate가 같이 높다면 문서를 많이 가져오는 대신 중복 문서만 쌓고 있을 가능성이 큽니다. 이 경우 retrieval top_k를 늘리는 대신 reranker 임계값과 chunk granularity를 먼저 조정하는 편이 정확도와 비용 모두에 유리합니다.

### 흔한 실수

"window가 200k니까 다 넣자"는 잘못된 직관입니다. 모델은 모든 입력을 동등하게 처리하지 않습니다. 토큰 예산을 정하고 그 안에서 압축합니다.

sliding window나 summarization 없이 모든 메시지를 보관하면 100 turn 후 context는 무너집니다. history 관리 전략을 처음부터 정합니다.

top-20 문서를 가공 없이 context에 붙이면 90%가 노이즈입니다. Reranking과 Compression을 거칩니다.

도구가 30개인데 매번 다 보여주면 모델은 잘못된 도구를 선택할 확률이 높아집니다. task별로 필터링합니다.

API 키, PII, 의료 정보가 context에 그대로 들어가면 로그와 출력으로 새어 나갑니다. 입력 단계에서 마스킹합니다.
## 흔히 헷갈리는 지점
- 윈도우가 크면 가능한 한 꽉 채우는 것이 좋다고 생각하기 쉽지만, 모델은 모든 입력을 동일한 품질로 처리하지 않습니다.
- history를 오래 보존할수록 똑똑해진다고 생각하기 쉽지만, 요약이나 잘라내기가 없으면 현재 태스크가 흐려집니다.
- retrieval만 잘하면 RAG가 끝났다고 보기 쉽지만, reranking과 compression이 빠지면 잡음이 너무 큽니다.
- 모든 도구 스키마를 늘 노출해도 상관없다고 생각하기 쉽지만, 도구가 많을수록 잘못 고를 확률도 올라갑니다.
- 비밀 값과 PII는 출력 단계에서만 막으면 된다고 생각하기 쉽지만, 컨텍스트와 로그 단계에서 이미 새어 나갈 수 있습니다.
## 운영 체크리스트
- [ ] 시스템 프롬프트, 태스크 명세, history, retrieval, tool schema에 토큰 예산을 따로 둡니다.
- [ ] 긴 대화에는 sliding window, summarization, selective recall 중 하나를 명시적으로 선택합니다.
- [ ] retrieval 이후 reranking과 compression 단계를 넣습니다.
- [ ] 비밀 값, PII, 불필요한 도구 스키마, 오래된 도구 출력을 컨텍스트에서 제거합니다.
- [ ] inference 직전 최종 컨텍스트 스냅샷을 저장해 재현 가능성을 확보합니다.
## 정리
Context Harness는 정보를 많이 넣는 기술이 아니라 정보를 적절히 줄이는 기술입니다. 에이전트는 아무리 큰 윈도우를 가져도 불필요한 문맥 속에서는 쉽게 길을 잃습니다.
또한 컨텍스트는 품질 문제이면서 보안 문제입니다. 무엇을 보여줄지와 무엇을 숨길지를 동시에 설계해야 추론 품질과 정보 보호를 함께 얻을 수 있습니다.
다음 글에서는 Constraint Harness를 다룹니다. 태스크와 컨텍스트가 정해졌다면, 이제 에이전트가 무엇을 해도 되고 무엇을 하면 안 되는지 코드 수준에서 고정해야 합니다.

## 처음 질문으로 돌아가기

- **Context Harness는 왜 무한한 메모리가 아니라 제한된 예산 배분 문제일까요?**
  - context window, 토큰 비용, attention, 보안 범위가 모두 제한되어 있기 때문입니다. 필요한 정보와 불필요한 정보를 같은 공간에 넣으면 판단 품질이 떨어집니다.
- **agent에게 보여줄 정보와 숨길 정보는 어떤 기준으로 나눠야 할까요?**
  - 현재 task 수행에 필요한 근거, 규칙, state는 보여주고 민감 정보, 오래된 noise, 결정에 무관한 문서는 숨겨야 합니다.
- **retrieved context가 많아질수록 정밀도는 어떻게 지켜야 할까요?**
  - 검색 결과 수를 늘리기보다 출처, 최신성, task 관련성, 중복 제거 기준을 두고 context snapshot을 남겨 재현 가능하게 만듭니다.

<!-- toc:begin -->
## 시리즈 목차

- [Harness Engineering 101 (1/10): Harness Engineering이란 무엇인가?](./01-what-is-harness-engineering.md)
- [Harness Engineering 101 (2/10): Task Harness — 모호한 일을 실행 가능한 작업으로 바꾸기](./02-task-harness.md)
- **Harness Engineering 101 (3/10): Context Harness — Agent에게 줄 정보와 숨길 정보 설계하기 (현재 글)**
- Harness Engineering 101 (4/10): Constraint Harness — 규칙, 경계, 금지 행동 정의하기 (예정)
- Harness Engineering 101 (5/10): Tool Harness — Agent가 사용할 도구를 안전하게 설계하기 (예정)
- Harness Engineering 101 (6/10): Test Harness — 완료 조건을 테스트로 고정하기 (예정)
- Harness Engineering 101 (7/10): Feedback Loop — 실패를 고치게 만드는 반복 구조 (예정)
- Harness Engineering 101 (8/10): Approval Gate — 사람 승인이 필요한 지점 설계하기 (예정)
- Harness Engineering 101 (9/10): Observability — Agent 작업을 추적하고 재현하기 (예정)
- Harness Engineering 101 (10/10): Production Harness — 운영 가능한 Agent 작업 환경 만들기 (예정)

<!-- toc:end -->

## 참고 자료
### 공식 문서

- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [Liu et al. — Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)
- [LangChain — Contextual Compression Retriever](https://python.langchain.com/docs/how_to/contextual_compression/)
- [OpenAI — Retrieval-Augmented Generation Best Practices](https://cookbook.openai.com/examples/question_answering_using_embeddings)
### 관련 시리즈

- [LangGraph 101 — 멀티 에이전트 시스템](../../langgraph-101/ko/05-multi-agent.md)
- [AI Safety & Guardrails 101 — 운영 가드레일 시스템 구축](../../ai-safety-guardrails-101/ko/10-production-guardrail-system.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/harness-engineering-101/ko/03-context-harness)

Tags: AI Agent, Harness, Production, Reliability
