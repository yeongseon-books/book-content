---
title: "바이브코딩을 위한 하네스 엔지니어링 (5/10): Tool Harness — Agent가 사용할 도구를 안전하게 설계하기"
series: harness-engineering-101
episode: 5
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- AI Agent
- Harness
- Tool Design
---

# 바이브코딩을 위한 하네스 엔지니어링 (5/10): Tool Harness — Agent가 사용할 도구를 안전하게 설계하기

이 글은 **바이브코딩을 위한 하네스 엔지니어링** 시리즈의 다섯 번째 글입니다. 에이전트가 사용할 도구를 안전하고 예측 가능하게 설계하는 Tool Harness를 다룹니다.

---

에이전트에게 도구를 주면 강력해집니다. 파일을 읽고, API를 호출하고, 데이터베이스를 쿼리합니다. 그런데 도구가 안전하지 않으면, 에이전트의 능력이 곧 위험입니다. 같은 작업을 두 번 실행하면 두 번 과금되거나, 파일이 두 번 삭제됩니다.

바이브코딩으로 AI에게 "이 API를 도구로 만들어줘"라고 하면, 함수 하나를 만들어줍니다. 그 함수는 오류가 날 때 무슨 메시지를 돌려줘야 하는지, 같은 요청이 두 번 오면 어떻게 해야 하는지 모릅니다.

Tool Harness는 도구를 5가지 원칙(명확한 입출력, 오류 처리, 멱등성, 격리, 로그)으로 설계하는 구조입니다.

> "도구가 안전하지 않으면 에이전트의 능력이 위험이 됩니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 에이전트 도구에서 오류가 나면 에이전트에게 어떤 메시지를 돌려주나요?
2. 같은 도구 호출이 두 번 실행되면 어떻게 되나요?
3. 도구가 외부 시스템을 변경하는 경우 롤백 방법이 있나요?
4. 도구 실행 결과를 로그로 기록하나요?
5. 도구의 입출력 스키마가 문서화되어 있나요?

---

## 5가지 도구 설계 원칙

1. **명확한 입출력**: 입력 파라미터와 반환값 타입을 명시
2. **실행 가능한 오류 메시지**: 에이전트가 다음 행동을 결정할 수 있는 오류 설명
3. **멱등성**: 같은 입력으로 두 번 호출해도 동일한 결과
4. **격리**: 도구 실패가 에이전트 전체를 중단시키지 않음
5. **로그**: 모든 호출과 결과 기록

## 도구 기본 구조

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class ToolResult:
    success: bool
    data: Any = None
    error: str | None = None
    action_hint: str | None = None  # 에이전트가 다음에 할 행동 힌트

def safe_tool(func):
    """도구를 안전하게 감싸는 데코레이터"""
    def wrapper(*args, **kwargs) -> ToolResult:
        try:
            result = func(*args, **kwargs)
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                action_hint="오류를 확인하고 파라미터를 수정한 후 재시도하세요.",
            )
    return wrapper
```

## 실행 가능한 오류 메시지

```python
class ToolError:
    @staticmethod
    def not_found(resource: str) -> ToolResult:
        return ToolResult(
            success=False,
            error=f"'{resource}'를 찾을 수 없습니다.",
            action_hint=f"파일 경로나 ID를 확인하고 다시 시도하세요.",
        )

    @staticmethod
    def permission_denied(action: str) -> ToolResult:
        return ToolResult(
            success=False,
            error=f"'{action}' 작업이 허용되지 않습니다.",
            action_hint="이 작업은 승인이 필요합니다. 사용자에게 확인을 요청하세요.",
        )
```

## 멱등성 보장

```python
import hashlib
import json

class IdempotentTool:
    def __init__(self):
        self._executed: set[str] = set()

    def _request_key(self, func_name: str, kwargs: dict) -> str:
        payload = json.dumps({"fn": func_name, "args": kwargs}, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def execute(self, func_name: str, func, **kwargs) -> ToolResult:
        key = self._request_key(func_name, kwargs)
        if key in self._executed:
            return ToolResult(success=True, data=None, error="이미 실행된 요청입니다.")
        result = func(**kwargs)
        if result.success:
            self._executed.add(key)
        return result
```

---

## Before / After

| 항목 | Before (일반 함수) | After (Tool Harness) |
|------|-------------------|---------------------|
| 오류 메시지 | Python 예외 그대로 | action_hint 포함 |
| 중복 실행 | 두 번 실행됨 | 멱등성 보장 |
| 실패 시 | 에이전트 중단 | ToolResult로 계속 진행 |
| 로그 | 없음 | 모든 호출 기록 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 예외를 그대로 전달 | 에이전트가 오류 해석 불가 | ToolResult로 래핑 |
| 멱등성 없음 | 중복 실행 부작용 | 요청 해시 기반 중복 방지 |
| action_hint 없음 | 에이전트 루프 가능 | 다음 행동 힌트 포함 |
| 도구 로그 없음 | 실패 추적 불가 | 모든 호출 기록 |

---

## AI 활용 팁

```
에이전트 도구를 안전하게 설계해줘.
모든 도구는 ToolResult를 반환하고, 성공·실패 여부와 action_hint를 포함해야 해.
safe_tool 데코레이터로 예외를 ToolResult로 변환해줘.
같은 요청이 두 번 오면 중복 실행을 방지하는 멱등성 로직도 포함해줘.
```

---

## 체크리스트

- [ ] ToolResult dataclass 정의
- [ ] safe_tool 데코레이터 구현
- [ ] 실행 가능한 오류 메시지(action_hint) 포함
- [ ] 멱등성 보장(요청 해시 기반)
- [ ] 도구 호출 로그 기록
- [ ] 도구 입출력 타입 힌트 명시

---

## 처음 질문으로 돌아가기

"도구를 주면 에이전트가 알아서 잘 쓰지 않나요?" — 도구가 안전하게 설계되지 않으면 에이전트의 능력이 위험이 됩니다. ToolResult, action_hint, 멱등성이 갖춰져야 에이전트가 오류를 만났을 때 다음 행동을 결정할 수 있습니다.

---

## 정리

- 모든 도구는 ToolResult(success, data, error, action_hint)를 반환한다
- safe_tool 데코레이터로 예외를 에이전트가 처리 가능한 형태로 변환한다
- 멱등성 보장으로 중복 실행을 방지한다
- 모든 도구 호출과 결과를 로그로 기록한다

---

## 참고 자료

- [LangChain Tool 설계](https://python.langchain.com/docs/modules/agents/tools/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 5가지 도구 설계 원칙
- 도구 기본 구조
- 실행 가능한 오류 메시지
- 멱등성 보장
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, AI Agent, Harness, Tool Design
