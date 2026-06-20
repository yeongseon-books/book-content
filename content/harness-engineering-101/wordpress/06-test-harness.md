---
title: "바이브코딩을 위한 하네스 엔지니어링 (6/10): Test Harness — 완료 조건을 테스트로 고정하기"
series: harness-engineering-101
episode: 6
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- AI Agent
- Harness
- Testing
- Eval
---

# 바이브코딩을 위한 하네스 엔지니어링 (6/10): Test Harness — 완료 조건을 테스트로 고정하기

이 글은 **바이브코딩을 위한 하네스 엔지니어링** 시리즈의 여섯 번째 글입니다. 에이전트 작업의 완료 조건을 테스트로 고정하고 자동 검증하는 Test Harness를 다룹니다.

---

에이전트가 작업을 마쳤다고 합니다. 정말 끝난 걸까요? "보고서를 작성했습니다"라는 에이전트의 말을 믿어야 할까요? 파일이 생성되었는지, 내용이 요구사항을 충족하는지, 형식이 맞는지 — 에이전트의 자기 평가는 신뢰하기 어렵습니다.

Test Harness는 완료 조건을 에이전트의 판단에 맡기지 않고, 코드로 자동 검증하는 구조입니다. 에이전트가 "완료"라고 말하더라도, 테스트를 통과해야 진짜 완료입니다.

> "에이전트의 '완료'와 테스트의 '통과'는 다릅니다. 테스트가 기준입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 에이전트 작업 완료를 어떻게 검증하나요?
2. 완료 조건을 코드로 표현할 수 있나요?
3. 에이전트 출력의 품질을 자동으로 측정하나요?
4. 테스트 실패 시 에이전트가 재시도할 수 있나요?
5. 완료 조건 중 일부만 통과하면 어떻게 처리하나요?

---

## TestCase 설계

```python
from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class TestCase:
    name: str
    check: Callable[[Any], bool]
    description: str
    required: bool = True  # False면 경고만

@dataclass
class TestResult:
    name: str
    passed: bool
    required: bool
    message: str = ""
```

## Test Runner

```python
class AgentTestRunner:
    def __init__(self, test_cases: list[TestCase]):
        self.test_cases = test_cases

    def run(self, agent_output: Any) -> dict:
        results = []
        for tc in self.test_cases:
            try:
                passed = tc.check(agent_output)
                results.append(TestResult(
                    name=tc.name,
                    passed=passed,
                    required=tc.required,
                    message="통과" if passed else f"실패: {tc.description}",
                ))
            except Exception as e:
                results.append(TestResult(
                    name=tc.name,
                    passed=False,
                    required=tc.required,
                    message=f"오류: {str(e)}",
                ))

        required_passed = all(r.passed for r in results if r.required)
        return {
            "all_required_passed": required_passed,
            "results": results,
            "passed_count": sum(1 for r in results if r.passed),
            "total_count": len(results),
        }
```

## 실용 테스트 케이스

```python
def file_exists_test(path: str) -> TestCase:
    from pathlib import Path
    return TestCase(
        name="파일 존재",
        check=lambda output: Path(output.get("file_path", "")).exists(),
        description="출력 파일이 생성되어야 합니다.",
    )

def min_length_test(min_chars: int) -> TestCase:
    return TestCase(
        name=f"최소 길이 {min_chars}자",
        check=lambda output: len(output.get("content", "")) >= min_chars,
        description=f"내용이 {min_chars}자 이상이어야 합니다.",
    )

def format_contains_test(pattern: str) -> TestCase:
    import re
    return TestCase(
        name=f"형식 포함: {pattern}",
        check=lambda output: bool(re.search(pattern, output.get("content", ""))),
        description=f"'{pattern}' 패턴이 포함되어야 합니다.",
    )
```

---

## Before / After

| 항목 | Before (에이전트 자기 평가) | After (Test Harness) |
|------|--------------------------|---------------------|
| 완료 판단 | "완료했습니다" 메시지 | 테스트 통과 여부 |
| 형식 검증 | 사람이 확인 | 자동 패턴 검증 |
| 재시도 | 수동 | 테스트 실패 시 자동 |
| 완료 기준 | 암묵적 | TestCase로 명시적 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 테스트 없이 에이전트 신뢰 | 잘못된 결과 통과 | AgentTestRunner 필수 |
| 필수/선택 테스트 미구분 | 경미한 실패로 전체 중단 | required 필드 분리 |
| 테스트 예외 미처리 | 테스트 자체 실패 | try-except 감싸기 |
| 재시도 로직 없음 | 실패 후 멈춤 | 실패 시 재시도 트리거 |

---

## AI 활용 팁

```
에이전트 출력을 자동으로 검증하는 Test Harness를 만들어줘.
TestCase는 name, check 함수, description, required 필드를 가져야 해.
AgentTestRunner는 모든 테스트를 실행하고 필수/선택 구분해서 결과를 반환해야 해.
파일 존재, 최소 길이, 형식 패턴 같은 재사용 가능한 테스트 케이스 팩토리 함수도 만들어줘.
```

---

## 체크리스트

- [ ] TestCase dataclass 정의
- [ ] AgentTestRunner 구현
- [ ] 재사용 테스트 케이스 팩토리(파일 존재, 길이, 패턴)
- [ ] required/optional 테스트 구분
- [ ] 테스트 실패 시 재시도 트리거
- [ ] 테스트 결과 로깅

---

## 처음 질문으로 돌아가기

"에이전트가 완료했다고 하는데 믿어도 되나요?" — 에이전트의 완료 선언은 참고 사항입니다. TestCase와 AgentTestRunner로 코드가 검증해야 진짜 완료입니다. 필수 테스트를 모두 통과해야 다음 단계로 넘어갑니다.

---

## 정리

- 완료 조건을 TestCase로 명시하고 코드로 자동 검증한다
- required/optional을 구분해서 필수 테스트 실패 시에만 차단한다
- AgentTestRunner는 예외를 처리하고 결과를 구조화된 형태로 반환한다
- 테스트 실패 시 에이전트가 재시도할 수 있는 피드백을 제공한다

---

## 참고 자료

- [pytest 공식 문서](https://docs.pytest.org/)
- [LangSmith Evaluation](https://docs.smith.langchain.com/evaluation)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- TestCase 설계
- Test Runner
- 실용 테스트 케이스
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, AI Agent, Harness, Testing, Eval
