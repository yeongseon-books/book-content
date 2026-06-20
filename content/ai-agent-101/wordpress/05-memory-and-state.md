---
title: "바이브코딩을 위한 AI Agent 기초 (5/10): 메모리와 상태 관리"
series: ai-agent-101
episode: 5
language: ko
tags:
- Memory
- State Management
- 바이브코딩
- Vibe Coding
- Redis
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI Agent 기초 (5/10): 메모리와 상태 관리

이 글은 **바이브코딩을 위한 AI Agent 기초** 시리즈의 다섯 번째 글입니다.

---

바이브코딩으로 에이전트를 만들다 보면 "에이전트가 이전에 했던 것을 기억하게 하려면 어떻게 하나요?"라는 질문이 자주 나옵니다. LLM 자체는 상태를 갖지 않습니다. 대화가 끝나면 모든 걸 잊습니다. 에이전트가 장기적으로 작동하려면 메모리와 상태 관리를 직접 설계해야 합니다.

메모리는 세 가지로 나뉩니다. **단기 메모리**(현재 대화 컨텍스트), **장기 메모리**(사용자 정보, 과거 결과), **실행 상태**(현재 작업의 진행 단계). 이 세 가지를 어디에 저장하고 어떻게 불러올지가 에이전트의 "기억력"을 결정합니다.

> "에이전트의 메모리는 사람의 메모리와 다릅니다. 설계하지 않으면 없는 것이고, 설계하면 얼마든지 정교하게 만들 수 있습니다."

## 이 글에서 다룰 질문

1. 단기 메모리, 장기 메모리, 실행 상태는 어떻게 다른가요?
2. 컨텍스트 윈도우가 꽉 찰 때 단기 메모리를 어떻게 관리하나요?
3. 장기 메모리는 어떤 저장소에 두는 게 좋은가요?
4. 에이전트 실행 중단 후 재개는 어떻게 구현하나요?
5. 메모리 검색 품질을 높이는 방법은 무엇인가요?

---

## 메모리 타입 비교

| 타입 | 저장 위치 | 지속성 | 예시 |
|------|----------|--------|------|
| 단기 메모리 | 컨텍스트 윈도우 | 대화 종료 시 소멸 | 현재 대화 히스토리 |
| 장기 메모리 | 벡터 DB, SQL | 영구 | 사용자 선호도, 과거 결과 |
| 실행 상태 | 파일, Redis | 작업 완료 시까지 | 현재 단계, 수집된 데이터 |

## Before / After: 메모리 관리

**Before (메모리 없음)**
```python
# 모든 대화를 그냥 누적
messages = []
for user_input in conversation:
    messages.append({"role": "user", "content": user_input})
    response = llm.chat(messages)
    messages.append({"role": "assistant", "content": response})
# 문제: 대화가 길어질수록 컨텍스트 윈도우 초과
```

**After (슬라이딩 윈도우 단기 메모리)**
```python
class ShortTermMemory:
    def __init__(self, max_tokens: int = 4000):
        self.messages = []
        self.max_tokens = max_tokens

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self._trim_if_needed()

    def _trim_if_needed(self):
        while self.estimate_tokens() > self.max_tokens:
            # 시스템 메시지는 보존, 가장 오래된 대화 제거
            for i, msg in enumerate(self.messages):
                if msg["role"] != "system":
                    self.messages.pop(i)
                    break

    def get_context(self) -> list[dict]:
        return self.messages
```

## 장기 메모리: 벡터 검색으로 관련 정보 조회

```python
class LongTermMemory:
    def __init__(self, vector_db, embedder):
        self.db = vector_db
        self.embedder = embedder

    def store(self, key: str, content: str, metadata: dict = None):
        embedding = self.embedder.encode(content)
        self.db.upsert(key, embedding, {"content": content, **(metadata or {})})

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        query_embedding = self.embedder.encode(query)
        results = self.db.search(query_embedding, top_k=top_k)
        return [{"content": r["content"], "score": r["score"]} for r in results]
```

## 실행 상태: 중단 후 재개 가능한 에이전트

```python
import json
from pathlib import Path

class AgentState:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.current_step = 0
        self.collected_data = {}
        self.is_complete = False

    def save(self, path: str = "agent_state.json"):
        Path(path).write_text(json.dumps({
            "task_id": self.task_id,
            "current_step": self.current_step,
            "collected_data": self.collected_data,
            "is_complete": self.is_complete
        }))

    @classmethod
    def load(cls, path: str = "agent_state.json") -> "AgentState":
        data = json.loads(Path(path).read_text())
        state = cls(data["task_id"])
        state.current_step = data["current_step"]
        state.collected_data = data["collected_data"]
        state.is_complete = data["is_complete"]
        return state
```

이 패턴으로 에이전트가 중간에 실패하더라도 저장된 상태에서 재개할 수 있습니다.

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 모든 대화 히스토리 누적 | 토큰 초과, 비용 폭발 | 슬라이딩 윈도우나 요약 적용 |
| 실행 상태를 메모리에만 저장 | 에이전트 재시작 시 모든 것 소멸 | 파일/Redis에 주기적으로 저장 |
| 장기 메모리 검색 없이 전부 로드 | 컨텍스트 오염, 느린 응답 | 관련성 기반 검색(rerank)으로 선택 |
| 메모리 오염 방지 없음 | 잘못된 정보가 누적되어 지속 | 명시적 수정/삭제 API 구현 |

## AI 팁

장기 메모리에서 검색한 결과가 많을 때는 **rerank**를 적용해 가장 관련성 높은 항목만 컨텍스트에 포함하세요. 단순 벡터 유사도가 아닌 교차 인코더(cross-encoder)로 재정렬하면 정밀도가 높아집니다.

Redis 같은 외부 저장소를 쓰면 여러 에이전트 인스턴스가 동일한 상태를 공유하거나, 사용자 세션을 서버 재시작 후에도 유지할 수 있습니다.

## 체크리스트

- [ ] 단기 메모리에 최대 토큰 제한을 설정했다
- [ ] 장기 메모리를 영구 저장소(DB, 파일)에 저장한다
- [ ] 실행 상태를 주기적으로 저장해 재개 가능하게 했다
- [ ] 장기 메모리 검색 시 관련성 기반 필터링을 적용한다
- [ ] 잘못된 메모리를 수정/삭제하는 방법을 구현했다

## 처음 질문으로 돌아가기

**단기/장기 메모리/실행 상태의 차이는?** 단기 메모리는 현재 대화, 장기 메모리는 영구 보존 정보, 실행 상태는 현재 작업의 진행 단계입니다.

**컨텍스트 윈도우가 꽉 찰 때?** 슬라이딩 윈도우(오래된 메시지 제거) 또는 요약 압축(오래된 대화를 LLM으로 요약)을 씁니다.

**장기 메모리 저장소는?** 벡터 검색이 필요하면 벡터 DB(Pinecone, ChromaDB), 구조화된 정보는 SQL, 세션 데이터는 Redis가 적합합니다.

**에이전트 실행 중단 후 재개는?** 실행 상태를 파일이나 DB에 주기적으로 저장하고, 재시작 시 마지막 저장 지점부터 재개합니다.

**메모리 검색 품질을 높이는 방법은?** 벡터 유사도 검색 후 cross-encoder로 재정렬(rerank)하면 정밀도가 높아집니다.

## 정리

에이전트의 메모리는 설계하지 않으면 없는 것입니다. 단기 메모리는 슬라이딩 윈도우나 요약으로 관리하고, 장기 메모리는 영구 저장소에 두고 관련성 기반으로 검색하며, 실행 상태는 중단/재개를 지원하도록 직렬화해야 합니다. 바이브코딩에서 에이전트가 "기억을 못 한다"고 느껴진다면 이 세 가지 레이어 중 무엇이 빠져 있는지 확인하세요.

다음 글에서는 여러 에이전트가 협력하는 **멀티 에이전트 시스템**을 다룹니다.

## 참고 자료

- [AI Agent 기초 원문: 메모리와 상태 관리](../ko/05-memory-and-state.md)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI Agent 기초 (1/10): AI 에이전트란 무엇인가](./01-what-is-an-ai-agent.md)
2. [바이브코딩을 위한 AI Agent 기초 (2/10): 컨텍스트 엔지니어링](./02-context-engineering.md)
3. [바이브코딩을 위한 AI Agent 기초 (3/10): 도구 사용 기초](./03-tool-use-fundamentals.md)
4. [바이브코딩을 위한 AI Agent 기초 (4/10): 에이전트 워크플로우 설계](./04-agent-workflow-design.md)
5. **바이브코딩을 위한 AI Agent 기초 (5/10): 메모리와 상태 관리 (현재 글)**
6. [바이브코딩을 위한 AI Agent 기초 (6/10): 멀티 에이전트 시스템](./06-multi-agent-systems.md)
7. [바이브코딩을 위한 AI Agent 기초 (7/10): 에이전트 평가](./07-agent-evaluation.md)
8. [바이브코딩을 위한 AI Agent 기초 (8/10): 오류 처리와 신뢰성](./08-error-handling-reliability.md)
9. [바이브코딩을 위한 AI Agent 기초 (9/10): 프로덕션 운영](./09-production-operations.md)
10. [바이브코딩을 위한 AI Agent 기초 (10/10): 첫 번째 에이전트 만들기](./10-building-first-agent.md)
<!-- toc:end -->

Tags: Memory, State Management, 바이브코딩, Vibe Coding, Redis
