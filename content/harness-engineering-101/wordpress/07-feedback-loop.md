---
title: "바이브코딩을 위한 하네스 엔지니어링 (7/10): Feedback Loop — 실패를 고치게 만드는 반복 구조"
series: harness-engineering-101
episode: 7
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- AI Agent
- Harness
- Feedback
- Reflection
---

# 바이브코딩을 위한 하네스 엔지니어링 (7/10): Feedback Loop — 실패를 고치게 만드는 반복 구조

이 글은 **바이브코딩을 위한 하네스 엔지니어링** 시리즈의 일곱 번째 글입니다. 에이전트가 실패했을 때 단순히 멈추지 않고 이유를 분석해 재시도하는 Feedback Loop를 다룹니다.

---

에이전트가 테스트를 통과하지 못했습니다. 어떻게 하나요? "실패"를 반환하고 멈추면, 사람이 개입해서 다시 시작해야 합니다. 에이전트가 왜 실패했는지 파악하고 다음 시도에서 수정할 수 있다면, 더 많은 작업을 자동으로 처리할 수 있습니다.

Feedback Loop는 테스트 실패 결과를 에이전트에게 다시 전달해 원인을 파악하고 수정 후 재시도하는 반복 구조입니다. 단, 무한 반복은 위험하므로 최대 반복 횟수와 탈출 조건이 필요합니다.

> "에이전트가 실패를 보고 배울 수 있어야 자율적으로 작업합니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 에이전트 작업 실패 시 자동으로 재시도하는 구조가 있나요?
2. 재시도 횟수 제한이 있나요?
3. 각 실패 이유를 다음 시도에 어떻게 전달하나요?
4. 같은 실수를 반복하는 루프를 어떻게 감지하나요?
5. 재시도를 포기하고 사람에게 넘기는 시점이 정해져 있나요?

---

## FeedbackLoop 설계

```python
from dataclasses import dataclass, field

@dataclass
class LoopState:
    attempt: int = 0
    max_attempts: int = 3
    history: list[dict] = field(default_factory=list)
    last_error: str | None = None

    def can_retry(self) -> bool:
        return self.attempt < self.max_attempts

    def record_attempt(self, result: dict):
        self.history.append({
            "attempt": self.attempt,
            "result": result,
        })
        self.attempt += 1
        if not result.get("success"):
            self.last_error = result.get("error", "알 수 없는 오류")
```

## 피드백 생성

```python
def generate_feedback(test_results: dict, last_output: Any) -> str:
    failed_tests = [
        r for r in test_results.get("results", [])
        if not r.passed
    ]
    if not failed_tests:
        return "모든 테스트를 통과했습니다."

    feedback_parts = ["이전 시도에서 다음 조건을 충족하지 못했습니다:"]
    for test in failed_tests:
        feedback_parts.append(f"- {test.name}: {test.message}")
    feedback_parts.append("위 조건을 충족하도록 수정해서 다시 시도해주세요.")

    return "\n".join(feedback_parts)
```

## 피드백 루프 실행

```python
def run_with_feedback(
    agent,
    task: dict,
    test_runner,
    max_attempts: int = 3,
) -> dict:
    state = LoopState(max_attempts=max_attempts)
    feedback = None

    while state.can_retry():
        # 피드백을 포함한 컨텍스트로 에이전트 실행
        agent_input = {**task}
        if feedback:
            agent_input["feedback"] = feedback

        output = agent.run(agent_input)
        test_results = test_runner.run(output)

        state.record_attempt({"success": test_results["all_required_passed"]})

        if test_results["all_required_passed"]:
            return {"success": True, "output": output, "attempts": state.attempt}

        feedback = generate_feedback(test_results, output)

    return {
        "success": False,
        "error": f"{max_attempts}회 시도 후 실패",
        "last_error": state.last_error,
        "attempts": state.attempt,
    }
```

---

## Before / After

| 항목 | Before (실패 = 종료) | After (Feedback Loop) |
|------|--------------------|-----------------------|
| 테스트 실패 시 | 사람 개입 필요 | 자동 재시도 |
| 실패 이유 전달 | 없음 | feedback 메시지 |
| 무한 루프 | 가능 | max_attempts 제한 |
| 재시도 포기 | 수동 판단 | 한도 초과 시 에스컬레이션 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 재시도 횟수 제한 없음 | 무한 루프 | max_attempts 설정 |
| 피드백 없이 재시도 | 같은 실수 반복 | 실패 이유를 컨텍스트에 포함 |
| 모든 오류 재시도 | 수정 불가 오류도 반복 | 오류 유형별 재시도 결정 |
| 시도 기록 없음 | 반복 패턴 파악 불가 | LoopState에 history 기록 |

---

## AI 활용 팁

```
에이전트 작업 실패 시 피드백을 전달하고 재시도하는 Feedback Loop를 만들어줘.
LoopState는 시도 횟수, 최대 횟수, 히스토리를 추적해야 해.
generate_feedback는 실패한 테스트 케이스 목록을 에이전트에게 전달할 메시지로 변환해야 해.
최대 횟수 초과 시 에스컬레이션 신호를 반환해줘.
```

---

## 체크리스트

- [ ] LoopState(시도 횟수, 최대 횟수, 히스토리)
- [ ] generate_feedback(실패 테스트 → 메시지)
- [ ] run_with_feedback 루프 실행
- [ ] max_attempts 초과 시 에스컬레이션
- [ ] 오류 유형별 재시도 결정 로직
- [ ] 시도 기록 영속화

---

## 처음 질문으로 돌아가기

"에이전트가 실패하면 사람이 항상 개입해야 하나요?" — max_attempts와 feedback이 있으면 많은 실패를 자동으로 복구할 수 있습니다. 하지만 무한 재시도는 더 위험합니다. 최대 횟수를 설정하고, 초과 시 Approval Gate로 에스컬레이션하는 구조가 균형을 만듭니다.

---

## 정리

- Feedback Loop는 테스트 실패 이유를 에이전트에게 피드백으로 전달한다
- max_attempts로 무한 루프를 방지한다
- 각 시도의 결과를 LoopState에 기록해 패턴을 추적한다
- 한도 초과 시 에스컬레이션으로 사람 개입을 요청한다

---

## 참고 자료

- [LangGraph 반복 실행](https://langchain-ai.github.io/langgraph/concepts/low_level/#cycles)
- [Reflexion 논문](https://arxiv.org/abs/2303.11366)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- FeedbackLoop 설계
- 피드백 생성
- 피드백 루프 실행
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, AI Agent, Harness, Feedback, Reflection
