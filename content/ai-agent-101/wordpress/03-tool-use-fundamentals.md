---
title: "바이브코딩을 위한 AI Agent 기초 (3/10): 도구 사용 기초"
series: ai-agent-101
episode: 3
language: ko
tags:
- Tool Use
- Function Calling
- 바이브코딩
- Vibe Coding
- Agent Loop
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI Agent 기초 (3/10): 도구 사용 기초

이 글은 **바이브코딩을 위한 AI Agent 기초** 시리즈의 세 번째 글입니다.

---

바이브코딩으로 에이전트를 만들 때 가장 흥미로운 순간은 에이전트가 처음으로 도구를 호출하는 장면입니다. LLM이 "웹 검색을 해야겠다"고 판단하고, 실제로 검색 함수를 호출하고, 결과를 받아 다음 판단을 내리는 과정 — 이게 에이전트가 단순 챗봇과 달라지는 핵심입니다.

도구 사용(Function Calling)은 LLM이 텍스트 생성 외에 실제 세계와 상호작용하는 방법입니다. API를 호출하고, 데이터베이스를 조회하고, 계산을 수행합니다. 바이브코딩에서는 이 도구 호출 흐름을 이해하는 것이 에이전트 개발의 출발점입니다.

이 글에서는 Function Calling의 4단계 흐름, 좋은 스키마 설계 원칙, 병렬 도구 호출, 그리고 실패에 강한 도구 래퍼 패턴을 다룹니다.

> "도구는 에이전트의 손입니다. 좋은 도구 설명은 에이전트가 언제 무엇을 집어야 할지 명확히 알게 합니다."

## 이 글에서 다룰 질문

1. Function Calling의 4단계 흐름은 어떻게 되나요?
2. 도구 스키마를 잘 설계하는 기준은 무엇인가요?
3. 병렬 도구 호출은 언제 사용하나요?
4. 도구 실행 오류를 에이전트가 어떻게 처리해야 하나요?
5. 도구 호출 비용을 줄이는 방법은 무엇인가요?

---

## Function Calling 4단계 흐름

```
1. LLM 판단
   → "검색 도구를 써야 한다"
   → tool_name: "web_search", args: {"query": "삼성전자 주가"}

2. 애플리케이션 실행
   → call_tool("web_search", {"query": "삼성전자 주가"})
   → 실제 API 호출

3. 결과 반환
   → {"results": [{"title": "...", "url": "..."}]}

4. LLM에 결과 전달
   → 다음 판단 ("이 결과로 답변 가능한가?")
```

이 4단계가 에이전트 루프 한 번의 핵심입니다. 루프를 몇 번 돌릴지는 목표 달성 여부에 따라 결정됩니다.

## Before / After: 도구 스키마 설계

**Before (나쁜 스키마)**
```python
{
    "name": "search",
    "description": "검색합니다",
    "parameters": {
        "q": "검색어"
    }
}
```

이 스키마는 도구가 무엇을 검색하는지, 어떤 결과를 돌려주는지, 언제 써야 하는지 아무것도 알려주지 않습니다.

**After (좋은 스키마)**
```python
{
    "name": "web_search",
    "description": "인터넷에서 최신 정보를 검색합니다. 학습 데이터 이후의 최신 사실, 현재 가격/날씨/뉴스가 필요할 때 사용하세요.",
    "when_to_use": "LLM 학습 데이터 이후 정보나 실시간 데이터가 필요한 경우",
    "when_not_to_use": "일반 상식이나 개념 설명은 도구 없이 직접 답변 가능",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "검색할 질문 (자연어 또는 키워드)"
            },
            "max_results": {
                "type": "integer",
                "description": "반환할 결과 수 (기본값: 5, 최대: 20)",
                "default": 5
            }
        },
        "required": ["query"]
    }
}
```

## 실패에 강한 도구 래퍼

```python
import time
from typing import Any

def call_tool(name: str, args: dict, max_retries: int = 3) -> dict[str, Any]:
    """도구 호출을 실행하고 결과를 표준화된 형식으로 반환합니다."""
    for attempt in range(max_retries):
        try:
            result = TOOL_REGISTRY[name](**args)
            return {"success": True, "result": result, "tool": name}
        except KeyError:
            return {"success": False, "error": f"도구 '{name}'를 찾을 수 없습니다", "tool": name}
        except Exception as e:
            if attempt == max_retries - 1:
                return {"success": False, "error": str(e), "tool": name, "retries": attempt + 1}
            time.sleep(2 ** attempt)  # 지수 백오프

    return {"success": False, "error": "최대 재시도 횟수 초과", "tool": name}
```

오류를 단순히 예외로 던지지 않고 에이전트가 관찰할 수 있는 딕셔너리로 반환하는 것이 핵심입니다. 에이전트는 오류도 관찰값으로 받아 다음 행동을 결정할 수 있어야 합니다.

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 도구 설명이 너무 짧음 | LLM이 언제 쓸지 모름 | when_to_use 명시, 예시 추가 |
| 오류를 에이전트에게 숨김 | 에이전트가 실패를 모르고 계속 진행 | 오류를 관찰값으로 전달 |
| 모든 파라미터를 required로 | 불필요한 오류 발생 | 선택적 파라미터는 default 값 설정 |
| 직렬 호출로 병렬 가능한 도구 처리 | 불필요한 지연 | 독립적 도구는 동시 호출 |

## AI 팁

독립적인 여러 도구를 동시에 호출해 시간을 절약할 수 있습니다. 예를 들어 "날씨와 주가를 동시에 조회"하는 경우, 두 도구를 순차가 아닌 병렬로 실행하면 응답 시간이 절반으로 줄어듭니다.

```python
import asyncio

async def parallel_tool_calls(tool_calls: list[dict]) -> list[dict]:
    """여러 도구를 병렬로 실행합니다."""
    tasks = [
        call_tool_async(tc["name"], tc["args"])
        for tc in tool_calls
    ]
    return await asyncio.gather(*tasks)
```

LLM이 JSON 배열로 여러 도구를 한 번에 요청하면 이를 병렬로 실행한 뒤 결과를 모두 전달합니다.

## 체크리스트

- [ ] 각 도구 스키마에 when_to_use와 when_not_to_use를 포함했다
- [ ] 도구 오류를 예외가 아닌 관찰값으로 에이전트에게 전달한다
- [ ] 재시도 로직에 지수 백오프를 적용했다
- [ ] 독립적인 도구 호출은 병렬로 실행한다
- [ ] 도구 호출 횟수와 소요 시간을 로깅한다

## 처음 질문으로 돌아가기

**Function Calling의 4단계 흐름은?** LLM 판단 → 애플리케이션 실행 → 결과 반환 → LLM에 결과 전달. 이 루프가 목표 달성까지 반복됩니다.

**도구 스키마를 잘 설계하는 기준은?** 이름과 설명만으로는 부족합니다. when_to_use, when_not_to_use, 파라미터 타입과 예시, required/optional 구분이 필요합니다.

**병렬 도구 호출은 언제?** 두 도구의 결과가 서로 독립적일 때 (A의 결과가 B 호출에 필요 없을 때) 병렬로 실행합니다.

**도구 실행 오류 처리는?** 오류를 예외로 던지지 말고, `{"success": false, "error": "..."}` 형태로 에이전트에게 전달하면 에이전트가 오류에서 학습하고 대안을 시도할 수 있습니다.

**도구 호출 비용을 줄이는 방법은?** when_not_to_use 명시로 불필요한 호출 줄이기, 결과 캐싱, 병렬 호출로 지연 시간 단축.

## 정리

도구 사용은 에이전트가 실제 세계와 상호작용하는 방법입니다. 좋은 스키마 설계와 실패에 강한 래퍼, 그리고 오류를 관찰값으로 처리하는 패턴이 핵심입니다. 바이브코딩에서 도구를 추가할 때마다 "LLM이 이 도구를 언제 써야 할지 이해할 수 있는가?"를 확인하는 습관을 갖는 것이 중요합니다.

다음 글에서는 여러 도구를 조합해 복잡한 작업을 처리하는 **에이전트 워크플로우 설계**를 다룹니다.

## 참고 자료

- [AI Agent 기초 원문: 도구 사용 기초](../ko/03-tool-use-fundamentals.md)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI Agent 기초 (1/10): AI 에이전트란 무엇인가](./01-what-is-an-ai-agent.md)
2. [바이브코딩을 위한 AI Agent 기초 (2/10): 컨텍스트 엔지니어링](./02-context-engineering.md)
3. **바이브코딩을 위한 AI Agent 기초 (3/10): 도구 사용 기초 (현재 글)**
4. [바이브코딩을 위한 AI Agent 기초 (4/10): 에이전트 워크플로우 설계](./04-agent-workflow-design.md)
5. [바이브코딩을 위한 AI Agent 기초 (5/10): 메모리와 상태 관리](./05-memory-and-state.md)
6. [바이브코딩을 위한 AI Agent 기초 (6/10): 멀티 에이전트 시스템](./06-multi-agent-systems.md)
7. [바이브코딩을 위한 AI Agent 기초 (7/10): 에이전트 평가](./07-agent-evaluation.md)
8. [바이브코딩을 위한 AI Agent 기초 (8/10): 오류 처리와 신뢰성](./08-error-handling-reliability.md)
9. [바이브코딩을 위한 AI Agent 기초 (9/10): 프로덕션 운영](./09-production-operations.md)
10. [바이브코딩을 위한 AI Agent 기초 (10/10): 첫 번째 에이전트 만들기](./10-building-first-agent.md)
<!-- toc:end -->

Tags: Tool Use, Function Calling, 바이브코딩, Vibe Coding, Agent Loop
