---
title: "바이브코딩을 위한 하네스 엔지니어링 (4/10): Constraint Harness — 규칙, 경계, 금지 행동 정의하기"
series: harness-engineering-101
episode: 4
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- AI Agent
- Harness
- Safety
---

# 바이브코딩을 위한 하네스 엔지니어링 (4/10): Constraint Harness — 규칙, 경계, 금지 행동 정의하기

이 글은 **바이브코딩을 위한 하네스 엔지니어링** 시리즈의 네 번째 글입니다. 에이전트가 해서는 안 되는 행동을 명시적으로 정의하고 강제하는 Constraint Harness를 다룹니다.

---

에이전트가 파일을 삭제했습니다. 요청하지 않은 이메일을 보냈습니다. 데이터베이스를 직접 수정했습니다. 이런 일이 발생했을 때 "에이전트에게 하지 말라고 했는데"라고 말하지만, 시스템 프롬프트에 "하지 마세요"라고 쓴 것은 제약이 아닙니다. 에이전트가 읽고 따를 수도 있지만, 강제하지 않습니다.

Constraint Harness는 허용되지 않은 행동을 시스템 레벨에서 차단하는 구조입니다. LLM의 판단에 의존하지 않고, 코드로 강제합니다.

> "제약은 프롬프트에 쓰는 것이 아니라 코드로 강제하는 것입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 에이전트가 사용하면 안 되는 도구가 있나요? 어떻게 막고 있나요?
2. 에이전트의 리소스 사용량(API 호출 수, 비용)에 한도가 있나요?
3. 에이전트 출력이 특정 형식을 벗어나면 어떻게 처리하나요?
4. 제약을 프롬프트로 주는 것과 코드로 강제하는 차이를 알고 있나요?
5. 제약 위반이 발생했을 때 로그를 남기나요?

---

## 4가지 제약 유형

```python
from enum import Enum

class ConstraintType(Enum):
    TOOL = "tool"          # 도구 사용 제한
    RESOURCE = "resource"  # 리소스 사용 제한
    OUTPUT = "output"      # 출력 형식 제한
    BEHAVIOR = "behavior"  # 행동 패턴 제한
```

## ToolRegistry 화이트리스트

```python
class ToolRegistry:
    def __init__(self, allowed_tools: list[str]):
        self._allowed = set(allowed_tools)

    def is_allowed(self, tool_name: str) -> bool:
        return tool_name in self._allowed

    def check(self, tool_name: str) -> None:
        if not self.is_allowed(tool_name):
            raise ConstraintViolation(
                f"도구 '{tool_name}'은 허용 목록에 없습니다."
            )

class ConstraintViolation(Exception):
    pass
```

## ResourceMeter

```python
class ResourceMeter:
    def __init__(self, max_api_calls: int = 50, max_cost_usd: float = 1.0):
        self.max_api_calls = max_api_calls
        self.max_cost_usd = max_cost_usd
        self._api_calls = 0
        self._cost_usd = 0.0

    def record_call(self, cost_usd: float = 0.0):
        self._api_calls += 1
        self._cost_usd += cost_usd
        if self._api_calls > self.max_api_calls:
            raise ConstraintViolation(f"API 호출 한도({self.max_api_calls}) 초과")
        if self._cost_usd > self.max_cost_usd:
            raise ConstraintViolation(f"비용 한도(${self.max_cost_usd}) 초과")
```

## 출력 정책 검증

```python
import re

class OutputPolicy:
    def __init__(self, forbidden_patterns: list[str], required_format: str | None = None):
        self.forbidden = [re.compile(p) for p in forbidden_patterns]
        self.required_format = required_format

    def validate(self, output: str) -> None:
        for pattern in self.forbidden:
            if pattern.search(output):
                raise ConstraintViolation(f"금지 패턴 발견: {pattern.pattern}")
        if self.required_format and self.required_format not in output:
            raise ConstraintViolation(f"필수 형식 '{self.required_format}' 누락")
```

---

## Before / After

| 항목 | Before (프롬프트 제약) | After (Constraint Harness) |
|------|----------------------|--------------------------|
| 도구 제한 | "이 도구는 쓰지 마세요" | ToolRegistry 화이트리스트 |
| 비용 제한 | 없음 | ResourceMeter 실시간 체크 |
| 출력 형식 | "이 형식으로 출력하세요" | OutputPolicy 검증 |
| 위반 감지 | 사람이 검토 후 | 즉시 ConstraintViolation |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 제약을 프롬프트에만 명시 | 에이전트가 무시할 수 있음 | 코드 레벨 강제 |
| 블랙리스트 방식 | 새 도구가 추가되면 누락 | 화이트리스트 방식 |
| 리소스 한도 없음 | 비용 폭발 가능 | ResourceMeter 필수 |
| 위반 로그 없음 | 어디서 막혔는지 불명 | 위반 시 로그 기록 |

---

## AI 활용 팁

```
에이전트 제약을 코드로 강제하는 Constraint Harness를 만들어줘.
ToolRegistry는 화이트리스트 기반으로 허용되지 않은 도구 호출 시 예외를 발생시켜야 해.
ResourceMeter는 API 호출 수와 비용 합계를 추적하고 한도 초과 시 중단해야 해.
모든 위반은 ConstraintViolation 예외로 처리하고 로그를 남겨줘.
```

---

## 체크리스트

- [ ] ToolRegistry 화이트리스트 구현
- [ ] ResourceMeter(API 호출 수, 비용 한도)
- [ ] OutputPolicy(금지 패턴, 필수 형식)
- [ ] ConstraintViolation 예외 클래스
- [ ] 위반 로그 기록
- [ ] 제약 설정을 외부 파일(YAML/JSON)로 분리

---

## 처음 질문으로 돌아가기

"프롬프트에 '하지 마세요'라고 써도 에이전트가 왜 하나요?" — 프롬프트는 요청이고, 코드 제약은 강제입니다. 허용 도구 화이트리스트, 비용 한도, 출력 정책을 코드로 구현해야 에이전트가 경계를 넘을 수 없습니다.

---

## 정리

- 제약은 프롬프트가 아니라 코드로 강제해야 한다
- ToolRegistry 화이트리스트로 허용 도구만 사용 가능하게 한다
- ResourceMeter로 API 호출 수와 비용을 실시간 추적한다
- 모든 제약 위반은 즉시 예외로 처리하고 로그를 남긴다

---

## 참고 자료

- [Python dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [LangGraph 에이전트 제약 설계](https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 4가지 제약 유형
- ToolRegistry 화이트리스트
- ResourceMeter
- 출력 정책 검증
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, AI Agent, Harness, Safety
