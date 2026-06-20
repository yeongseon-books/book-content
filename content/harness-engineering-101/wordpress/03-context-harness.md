---
title: "바이브코딩을 위한 하네스 엔지니어링 (3/10): Context Harness — Agent에게 줄 정보와 숨길 정보 설계하기"
series: harness-engineering-101
episode: 3
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- AI Agent
- Harness
- Context Management
---

# 바이브코딩을 위한 하네스 엔지니어링 (3/10): Context Harness — Agent에게 줄 정보와 숨길 정보 설계하기

이 글은 **바이브코딩을 위한 하네스 엔지니어링** 시리즈의 세 번째 글입니다. 에이전트에게 어떤 정보를 주고 어떤 정보를 숨길지 설계하는 Context Harness를 다룹니다.

---

에이전트에게 정보를 많이 줄수록 좋을까요? 아닙니다. 컨텍스트 창에 모든 것을 넣으면 에이전트는 오히려 핵심을 찾지 못합니다. 관련 없는 이전 대화, 전체 문서, 모든 로그를 다 넣으면 비용은 높아지고 정확도는 낮아집니다.

바이브코딩으로 AI에게 "에이전트에게 필요한 정보 넘겨줘"라고 하면, 모든 것을 컨텍스트에 넣는 코드가 나옵니다. 처음엔 작동합니다. 대화가 길어지면 토큰 한도에 걸리거나 응답 품질이 떨어집니다.

Context Harness는 에이전트가 지금 작업에 필요한 정보만 선택해서 전달하는 구조입니다.

> "에이전트에게 모든 정보를 주는 것이 아니라, 필요한 정보만 주는 것이 Context Harness입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 에이전트의 컨텍스트 창 토큰 예산을 설정한 적 있나요?
2. 이전 대화에서 어떤 부분을 버리고 어떤 부분을 유지할지 기준이 있나요?
3. 검색으로 가져온 문서를 컨텍스트에 추가할 때 크기를 제한하나요?
4. 민감한 정보를 컨텍스트에서 제외하는 방법이 있나요?
5. 컨텍스트 크기가 응답 품질에 미치는 영향을 측정한 적 있나요?

---

## ContextBudget 설계

```python
from dataclasses import dataclass

@dataclass
class ContextBudget:
    total_tokens: int = 8000
    system_tokens: int = 1000
    history_tokens: int = 3000
    retrieval_tokens: int = 2000
    task_tokens: int = 1000
    response_reserve: int = 1000

    def available_for_history(self) -> int:
        return self.history_tokens

    def available_for_retrieval(self) -> int:
        return self.retrieval_tokens
```

## HistoryManager

대화 기록에서 필요한 부분만 선택합니다.

```python
class HistoryManager:
    def __init__(self, budget: ContextBudget, tokenizer):
        self.budget = budget
        self.tokenizer = tokenizer

    def select_history(self, messages: list[dict]) -> list[dict]:
        selected = []
        token_count = 0
        # 최신 메시지부터 역순으로 선택
        for msg in reversed(messages):
            tokens = len(self.tokenizer.encode(msg["content"]))
            if token_count + tokens > self.budget.history_tokens:
                break
            selected.insert(0, msg)
            token_count += tokens
        return selected
```

## 검색 컨텍스트 주입

```python
def inject_retrieval_context(
    query: str,
    retriever,
    budget: ContextBudget,
    tokenizer,
) -> str:
    docs = retriever.get_relevant_documents(query)
    context_parts = []
    token_count = 0

    for doc in docs:
        text = doc.page_content
        tokens = len(tokenizer.encode(text))
        if token_count + tokens > budget.retrieval_tokens:
            break
        context_parts.append(text)
        token_count += tokens

    return "\n\n---\n\n".join(context_parts)
```

## 컨텍스트 스냅샷

```python
def build_context_snapshot(
    system_prompt: str,
    task: dict,
    history: list[dict],
    retrieved_docs: str,
    budget: ContextBudget,
) -> dict:
    return {
        "system": system_prompt[:budget.system_tokens * 4],  # 대략적 문자 수
        "task": task,
        "history": history,
        "retrieved": retrieved_docs,
        "budget_used": {
            "history": len(history),
            "retrieved_chars": len(retrieved_docs),
        },
    }
```

---

## Before / After

| 항목 | Before (모든 것을 컨텍스트에) | After (Context Harness) |
|------|------------------------------|------------------------|
| 토큰 사용 | 한도 초과 가능 | 예산 내 보장 |
| 이전 대화 | 전체 포함 | 최신·관련 메시지만 |
| 검색 결과 | 무제한 추가 | retrieval_tokens 제한 |
| 민감 정보 | 포함될 수 있음 | 명시적 제외 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 대화 전체 포함 | 토큰 한도 초과 | HistoryManager로 선택 |
| 검색 결과 무제한 | 핵심 희석 | retrieval_tokens 예산 설정 |
| 토큰 측정 없음 | 예산 초과 발견 못함 | tokenizer로 사전 측정 |
| 시스템 프롬프트 미분리 | 재사용 불가 | 별도 예산으로 관리 |

---

## AI 활용 팁

```
에이전트 컨텍스트를 system/history/retrieval/task 4개 영역으로 나누고 각 영역에 토큰 예산을 설정해줘.
HistoryManager는 최신 메시지부터 역순으로 예산 내에서 선택해야 해.
inject_retrieval_context는 검색 결과를 retrieval 예산 내에서만 포함해야 해.
```

---

## 체크리스트

- [ ] ContextBudget 영역별 토큰 예산 설정
- [ ] HistoryManager(역순 선택, 예산 내 제한)
- [ ] 검색 컨텍스트 주입(retrieval_tokens 제한)
- [ ] 컨텍스트 스냅샷 생성 함수
- [ ] 민감 정보 제외 로직
- [ ] 토큰 사용량 로깅

---

## 처음 질문으로 돌아가기

"에이전트에게 정보를 많이 줄수록 좋지 않나요?" — 컨텍스트 창에는 한계가 있습니다. 핵심 정보가 관련 없는 내용에 묻히면 에이전트는 정확도가 떨어집니다. 예산을 정하고 필요한 정보만 선택해서 전달하는 Context Harness가 응답 품질을 높입니다.

---

## 정리

- ContextBudget으로 system/history/retrieval/task 영역별 토큰 예산을 설정한다
- HistoryManager는 최신 메시지부터 역순으로 예산 내에서 선택한다
- 검색 결과는 retrieval_tokens 예산 내에서만 포함한다
- 컨텍스트 스냅샷으로 각 호출에서 실제 사용된 컨텍스트를 추적한다

---

## 참고 자료

- [tiktoken Python 라이브러리](https://github.com/openai/tiktoken)
- [Anthropic 컨텍스트 창 관리](https://docs.anthropic.com/en/docs/build-with-claude/context-windows)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- ContextBudget 설계
- HistoryManager
- 검색 컨텍스트 주입
- 컨텍스트 스냅샷
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, AI Agent, Harness, Context Management
