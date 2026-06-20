---
title: "바이브코딩을 위한 하네스 엔지니어링 (2/10): Task Harness — 모호한 일을 실행 가능한 작업으로 바꾸기"
series: harness-engineering-101
episode: 2
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- AI Agent
- Harness
- Task Design
---

# 바이브코딩을 위한 하네스 엔지니어링 (2/10): Task Harness — 모호한 일을 실행 가능한 작업으로 바꾸기

이 글은 **바이브코딩을 위한 하네스 엔지니어링** 시리즈의 두 번째 글입니다. 모호한 요청을 에이전트가 실행할 수 있는 명확한 작업 명세로 변환하는 Task Harness를 다룹니다.

---

"보고서 작성해줘" — 이 요청을 에이전트에게 넘기면 어떻게 될까요? 어떤 보고서인지, 얼마나 긴지, 어떤 형식인지, 언제까지인지 아무것도 없습니다. 에이전트는 뭔가를 만들겠지만, 원하는 것과 다를 가능성이 높습니다.

사람도 모호한 요청을 받으면 "어떤 보고서인가요?"라고 되묻습니다. 에이전트는 되묻지 않고 추측합니다. 그 추측이 맞으면 운이 좋은 것이고, 틀리면 다시 시작해야 합니다.

Task Harness는 모호한 요청을 에이전트에게 넘기기 전에 명확한 작업 명세(TaskSpec)로 변환하는 구조입니다.

> "에이전트에게 모호한 요청을 주면 모호한 결과를 받습니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 에이전트에게 전달하는 작업 명세가 얼마나 구체적인가요?
2. 작업 완료 기준을 코드로 검증할 수 있나요?
3. 입력이 불완전할 때 에이전트가 어떻게 처리하나요?
4. 작업 명세에 실패 조건도 포함되어 있나요?
5. 동일한 작업을 반복 실행해도 같은 결과를 기대할 수 있나요?

---

## TaskSpec 설계

```python
from dataclasses import dataclass, field

@dataclass
class TaskSpec:
    task_id: str
    description: str
    inputs: dict                    # 필수 입력값
    expected_outputs: list[str]     # 기대 출력 목록
    completion_criteria: list[str]  # 완료 판단 기준
    failure_conditions: list[str]   # 실패 조건
    max_steps: int = 10
    timeout_seconds: int = 300
```

## 모호한 요청을 TaskSpec으로 변환

```python
def parse_task_request(raw_request: str) -> TaskSpec:
    # 실제 구현에서는 LLM으로 파싱하거나 템플릿 매칭 사용
    if "보고서" in raw_request:
        return TaskSpec(
            task_id="report_001",
            description="월간 판매 보고서 작성",
            inputs={"period": "2024-01", "format": "markdown"},
            expected_outputs=["report.md"],
            completion_criteria=[
                "파일이 생성되었다",
                "파일 크기가 100바이트 이상이다",
                "# 제목 헤더가 포함되어 있다",
            ],
            failure_conditions=["빈 파일", "형식 오류"],
        )
    raise ValueError(f"인식할 수 없는 요청: {raw_request}")
```

## 완료 기준 검증

```python
def verify_completion(task: TaskSpec, outputs: dict) -> dict:
    results = {}
    for criterion in task.completion_criteria:
        # 간단한 예시: 실제는 더 복잡한 검증 로직 필요
        passed = _check_criterion(criterion, outputs)
        results[criterion] = passed
    return {
        "all_passed": all(results.values()),
        "details": results,
    }
```

## JSON Schema로 입력 검증

```python
import jsonschema

TASK_SCHEMA = {
    "type": "object",
    "required": ["task_id", "description", "inputs"],
    "properties": {
        "task_id": {"type": "string"},
        "description": {"type": "string"},
        "inputs": {"type": "object"},
    }
}

def validate_task_spec(spec: dict) -> bool:
    try:
        jsonschema.validate(spec, TASK_SCHEMA)
        return True
    except jsonschema.ValidationError:
        return False
```

---

## Before / After

| 항목 | Before (모호한 요청) | After (TaskSpec) |
|------|--------------------|--------------------|
| 작업 명확성 | "보고서 작성해줘" | 형식·기간·출력 파일 명시 |
| 완료 판단 | 에이전트 추측 | criteria 리스트 검증 |
| 실패 감지 | 결과물 검토 후 | failure_conditions 자동 체크 |
| 재현성 | 매번 다른 결과 | 동일 TaskSpec = 일관된 결과 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 완료 기준 없음 | 에이전트가 임의로 종료 | completion_criteria 필수화 |
| 입력 검증 없음 | 잘못된 입력으로 실행 | jsonschema 검증 |
| 실패 조건 미정의 | 실패를 성공으로 판단 | failure_conditions 목록 |
| timeout 없음 | 무한 루프 가능 | max_steps + timeout_seconds |

---

## AI 활용 팁

```
사용자의 자연어 요청을 TaskSpec으로 변환하는 함수를 만들어줘.
TaskSpec은 task_id, description, inputs, expected_outputs, completion_criteria, failure_conditions를 포함해야 해.
completion_criteria는 코드로 검증 가능한 조건으로 작성해줘(파일 존재, 크기, 형식 등).
```

---

## 체크리스트

- [ ] TaskSpec dataclass 정의
- [ ] 자연어 요청 → TaskSpec 변환 함수
- [ ] JSON Schema로 입력 검증
- [ ] completion_criteria 자동 검증 함수
- [ ] failure_conditions 체크 로직
- [ ] max_steps + timeout 설정

---

## 처음 질문으로 돌아가기

"에이전트에게 요청하면 왜 원하는 결과가 안 나오나요?" — 요청이 모호하면 에이전트도 모호하게 실행합니다. TaskSpec으로 작업을 명확하게 정의하고 완료 기준을 코드로 검증할 수 있어야 에이전트가 신뢰할 수 있는 결과를 냅니다.

---

## 정리

- TaskSpec으로 작업의 입력·출력·완료 기준·실패 조건을 명시한다
- 모호한 자연어 요청은 TaskSpec으로 변환한 후 에이전트에 전달한다
- completion_criteria는 코드로 검증 가능한 조건으로 작성한다
- max_steps와 timeout으로 무한 실행을 방지한다

---

## 참고 자료

- [jsonschema Python 라이브러리](https://python-jsonschema.readthedocs.io/)
- [LangGraph Task 설계 가이드](https://langchain-ai.github.io/langgraph/concepts/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- TaskSpec 설계
- 모호한 요청을 TaskSpec으로 변환
- 완료 기준 검증
- JSON Schema로 입력 검증
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, AI Agent, Harness, Task Design
