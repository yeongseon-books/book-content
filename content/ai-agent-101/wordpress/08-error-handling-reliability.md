---
title: "바이브코딩을 위한 AI Agent 기초 (8/10): 오류 처리와 신뢰성"
series: ai-agent-101
episode: 8
language: ko
tags:
- Error Handling
- Reliability
- Circuit Breaker
- Retry
- 바이브코딩
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI Agent 기초 (8/10): 오류 처리와 신뢰성

이 글은 **바이브코딩을 위한 AI Agent 기초** 시리즈의 여덟 번째 글입니다.

---

바이브코딩으로 에이전트를 만들다 보면 "완성된 것 같은데 실제로 쓰면 자꾸 망가진다"는 경험을 하게 됩니다. LLM이 JSON 형식을 잘못 반환하고, API가 타임아웃되고, 도구가 예상치 못한 오류를 냅니다. 에이전트는 이런 불확실한 환경에서도 멈추지 않고 동작해야 합니다.

오류 처리는 "오류가 나면 try-except로 잡는다"보다 훨씬 정교해야 합니다. 어떤 오류는 재시도하면 해결되고, 어떤 오류는 다른 방법으로 우회해야 하고, 어떤 오류는 즉시 중단하고 사람에게 알려야 합니다. 이 판단 로직이 에이전트의 신뢰성을 결정합니다.

> "에이전트의 신뢰성은 '오류가 없는 것'이 아니라 '오류가 났을 때 어떻게 회복하는가'로 판단합니다."

## 이 글에서 다룰 질문

1. 에이전트에서 오류 유형을 어떻게 분류하나요?
2. 재시도 로직에서 지수 백오프가 중요한 이유는 무엇인가요?
3. 폴백 체인(Fallback Chain)은 어떻게 설계하나요?
4. 서킷 브레이커(Circuit Breaker)는 무엇이고 언제 필요한가요?
5. LLM이 잘못된 JSON을 반환할 때 어떻게 처리하나요?

---

## 오류 분류: 재시도 가능 vs 불가능

| 오류 유형 | 예시 | 처리 방법 |
|-----------|------|-----------|
| 일시적 오류 (재시도 가능) | 네트워크 타임아웃, API 속도 제한 | 지수 백오프 재시도 |
| 입력 오류 (수정 후 재시도) | 잘못된 파라미터, 형식 오류 | 오류 메시지 에이전트에 전달 |
| 영구적 오류 (즉시 중단) | 인증 실패, 존재하지 않는 리소스 | 사람에게 에스컬레이션 |
| 비즈니스 오류 (대안 경로) | 검색 결과 없음 | 폴백 도구 또는 방법으로 전환 |

## Before / After: 단순 예외 처리 vs 체계적 오류 처리

**Before (단순 try-except)**
```python
try:
    result = web_search("삼성전자 주가")
    return result
except Exception as e:
    return f"오류 발생: {e}"
# 문제: 재시도 없음, 대안 없음, 에이전트가 포기
```

**After (재시도 + 폴백 + 에이전트에 전달)**
```python
import time
from dataclasses import dataclass

@dataclass
class ToolError(Exception):
    message: str
    recoverable: bool  # 재시도 가능 여부
    tool_name: str

def retry_with_backoff(fn, max_retries: int = 3, base_delay: float = 1.0):
    """지수 백오프로 함수를 재시도합니다."""
    for attempt in range(max_retries):
        try:
            return fn()
        except ToolError as e:
            if not e.recoverable or attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
    raise ToolError("최대 재시도 초과", recoverable=False, tool_name="unknown")

class FallbackChain:
    """여러 도구를 순서대로 시도하는 폴백 체인."""
    def __init__(self, tools: list):
        self.tools = tools

    def execute(self, *args, **kwargs):
        for tool in self.tools:
            try:
                return tool(*args, **kwargs)
            except Exception as e:
                continue
        raise RuntimeError("모든 폴백 도구 실패")
```

## 서킷 브레이커: 반복 실패 차단

```python
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # 정상 동작
    OPEN = "open"          # 차단 (실패 임계값 초과)
    HALF_OPEN = "half_open"  # 복구 시도 중

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = CircuitState.CLOSED
        self.last_failure_time = None

    def call(self, fn, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise RuntimeError("서킷 오픈 — 도구 일시적 사용 불가")

        try:
            result = fn(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

## LLM JSON 파싱 오류 처리

```python
import json
import re

def parse_llm_json(response: str) -> dict:
    """LLM이 반환한 텍스트에서 JSON을 추출합니다."""
    # 1. 직접 파싱 시도
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # 2. 마크다운 코드 블록에서 추출
    match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. 중괄호로 시작하는 부분 추출
    match = re.search(r'\{[\s\S]*\}', response)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"JSON 파싱 실패: {response[:200]}")
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 모든 오류를 동일하게 처리 | 재시도 불가 오류도 무한 재시도 | 오류 유형 분류 (recoverable 플래그) |
| 재시도 간 딜레이 없음 | API 속도 제한 악화 | 지수 백오프 적용 |
| 폴백 없이 단일 도구 의존 | 도구 실패 시 전체 중단 | FallbackChain으로 대안 경로 |
| 오류를 에이전트에게 숨김 | 에이전트가 실패 상황 모름 | 오류 정보를 관찰값으로 전달 |

## AI 팁

오류를 에이전트에게 숨기지 마세요. 도구가 실패했을 때 에이전트에게 오류 메시지를 전달하면 에이전트가 "검색이 실패했으니 다른 방법을 써야겠다"고 판단할 수 있습니다. 오류를 숨기면 에이전트는 성공한 줄 알고 잘못된 방향으로 계속 진행합니다.

```python
# 오류를 관찰값으로 에이전트에게 전달
observation = {
    "success": False,
    "error": "검색 API 타임아웃 (30초)",
    "suggestion": "다른 검색 도구를 시도하거나 요청을 단순화하세요"
}
```

## 체크리스트

- [ ] 오류를 재시도 가능/불가능으로 분류했다
- [ ] 재시도 로직에 지수 백오프를 적용했다
- [ ] 중요한 도구에 폴백 체인을 구현했다
- [ ] 반복 실패하는 도구에 서킷 브레이커를 적용했다
- [ ] 오류 정보를 에이전트에게 관찰값으로 전달한다

## 처음 질문으로 돌아가기

**오류 유형을 어떻게 분류하나요?** 재시도 가능(일시적), 수정 후 재시도(입력 오류), 즉시 중단(영구적), 대안 경로(비즈니스 오류) 네 가지로 분류하면 각 상황에 맞는 처리가 가능합니다.

**지수 백오프가 중요한 이유는?** API 속도 제한에 걸렸을 때 즉시 재시도하면 더 많은 요청이 실패합니다. 간격을 늘려가며 재시도하면 API가 회복할 시간을 줍니다.

**폴백 체인 설계는?** 기본 도구가 실패하면 대안 도구를 순서대로 시도하는 체인입니다. 예: 공식 API → 스크래핑 → 캐시된 데이터.

**서킷 브레이커는 언제?** 외부 API가 불안정해서 연속 실패가 자주 발생하는 경우, 임계값 초과 시 일정 시간 동안 호출을 차단해 시스템을 보호합니다.

**LLM이 잘못된 JSON을 반환할 때?** 직접 파싱 → 마크다운 블록 추출 → 정규식으로 JSON 부분 추출 순서로 시도합니다.

## 정리

에이전트의 신뢰성은 오류를 없애는 것이 아니라 오류에서 회복하는 능력입니다. 오류 분류, 지수 백오프 재시도, 폴백 체인, 서킷 브레이커, LLM 출력 파싱 — 이 다섯 가지 패턴을 갖추면 실제 운영에서 훨씬 안정적인 에이전트를 만들 수 있습니다.

다음 글에서는 에이전트를 실제 운영 환경에 배포하는 **프로덕션 운영**을 다룹니다.

## 참고 자료

- [AI Agent 기초 원문: 오류 처리와 신뢰성](../ko/08-error-handling-reliability.md)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI Agent 기초 (1/10): AI 에이전트란 무엇인가](./01-what-is-an-ai-agent.md)
2. [바이브코딩을 위한 AI Agent 기초 (2/10): 컨텍스트 엔지니어링](./02-context-engineering.md)
3. [바이브코딩을 위한 AI Agent 기초 (3/10): 도구 사용 기초](./03-tool-use-fundamentals.md)
4. [바이브코딩을 위한 AI Agent 기초 (4/10): 에이전트 워크플로우 설계](./04-agent-workflow-design.md)
5. [바이브코딩을 위한 AI Agent 기초 (5/10): 메모리와 상태 관리](./05-memory-and-state.md)
6. [바이브코딩을 위한 AI Agent 기초 (6/10): 멀티 에이전트 시스템](./06-multi-agent-systems.md)
7. [바이브코딩을 위한 AI Agent 기초 (7/10): 에이전트 평가](./07-agent-evaluation.md)
8. **바이브코딩을 위한 AI Agent 기초 (8/10): 오류 처리와 신뢰성 (현재 글)**
9. [바이브코딩을 위한 AI Agent 기초 (9/10): 프로덕션 운영](./09-production-operations.md)
10. [바이브코딩을 위한 AI Agent 기초 (10/10): 첫 번째 에이전트 만들기](./10-building-first-agent.md)
<!-- toc:end -->

Tags: Error Handling, Reliability, Circuit Breaker, Retry, 바이브코딩
