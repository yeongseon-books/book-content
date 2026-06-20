---
title: "바이브코딩을 위한 AI Agent 기초 (7/10): 에이전트 평가"
series: ai-agent-101
episode: 7
language: ko
tags:
- Agent Evaluation
- Trajectory
- Cost Tracking
- 바이브코딩
- Vibe Coding
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI Agent 기초 (7/10): 에이전트 평가

이 글은 **바이브코딩을 위한 AI Agent 기초** 시리즈의 일곱 번째 글입니다.

---

바이브코딩으로 에이전트를 만들고 나면 "이 에이전트가 잘 동작하고 있는 걸까?"라는 의문이 생깁니다. 에이전트 평가는 챗봇 평가보다 훨씬 복잡합니다. 단순히 최종 답변이 맞는지만 보는 것이 아니라, **어떤 경로로 그 답변에 도달했는지**, **얼마나 효율적으로 도구를 사용했는지**, **비용은 얼마였는지**까지 측정해야 합니다.

에이전트가 우연히 맞는 답을 내더라도 불필요한 도구를 10번 호출했다면 그건 좋은 에이전트가 아닙니다. 반대로 효율적이지만 가끔 틀리는 에이전트도 개선이 필요합니다. 평가 기준을 세우지 않으면 에이전트를 개선하는 방향을 잡을 수 없습니다.

> "에이전트를 평가한다는 것은 '결과가 맞는가?'뿐만 아니라 '올바른 방식으로 도달했는가?'를 묻는 것입니다."

## 이 글에서 다룰 질문

1. 에이전트 평가에서 최종 성공률 외에 어떤 지표가 필요한가요?
2. Trajectory 평가는 무엇이고 왜 중요한가요?
3. 비용과 품질 사이의 트레이드오프를 어떻게 관리하나요?
4. 자동화된 평가 파이프라인을 어떻게 구축하나요?
5. 에이전트 평가 결과로 어떻게 개선 방향을 잡나요?

---

## 에이전트 평가 4가지 축

| 평가 축 | 측정 항목 | 왜 중요한가 |
|---------|----------|------------|
| 종단 성공률 | 목표 달성 여부 | 기본적인 품질 지표 |
| 궤적(Trajectory) | 도구 사용 순서와 효율성 | 최적 경로로 도달했는지 |
| 비용 | 토큰 사용량, API 호출 수 | 운영 비용 예측과 관리 |
| 도구 정확도 | 올바른 도구를 올바른 시점에 사용 | 에이전트의 판단 능력 |

## Before / After: 평가 없는 vs 체계적 평가

**Before (결과만 확인)**
```python
result = agent.run("삼성전자 주가를 찾아줘")
print("성공" if "원" in result else "실패")
# 문제: 어떻게 도달했는지, 비용은 얼마인지 모름
```

**After (체계적 평가)**
```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class EvaluationResult:
    test_case_id: str
    goal: str
    success: bool
    trajectory: list[dict]  # 실행 단계별 기록
    total_tokens: int
    total_cost: float
    tool_calls: int
    duration_seconds: float
    final_answer: str

def evaluate_agent(agent, test_cases: list[dict]) -> list[EvaluationResult]:
    results = []
    for tc in test_cases:
        start_time = time.time()
        tracker = CostTracker()

        with tracker:
            answer = agent.run(tc["goal"])

        result = EvaluationResult(
            test_case_id=tc["id"],
            goal=tc["goal"],
            success=tc["evaluator"](answer),
            trajectory=agent.get_trajectory(),
            total_tokens=tracker.total_tokens,
            total_cost=tracker.total_cost,
            tool_calls=tracker.tool_call_count,
            duration_seconds=time.time() - start_time,
            final_answer=answer
        )
        results.append(result)
    return results
```

## Trajectory 평가: 경로가 중요한 이유

같은 답변이라도 좋은 경로와 나쁜 경로가 있습니다.

```python
# 나쁜 Trajectory (비효율적)
trajectory_bad = [
    {"step": 1, "action": "web_search", "query": "삼성전자"},
    {"step": 2, "action": "web_search", "query": "삼성전자 주가"},  # 중복
    {"step": 3, "action": "web_search", "query": "삼성전자 주가 오늘"},  # 또 중복
    {"step": 4, "action": "final_answer", "content": "82,000원"}
]

# 좋은 Trajectory (효율적)
trajectory_good = [
    {"step": 1, "action": "web_search", "query": "삼성전자 주가 오늘"},
    {"step": 2, "action": "final_answer", "content": "82,000원"}
]
```

비용 추적기(CostTracker)로 각 실행의 총 비용을 기록하면 에이전트 개선이 비용을 줄이는 방향으로 가고 있는지 확인할 수 있습니다.

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 최종 성공률만 측정 | 비효율적 경로를 놓침 | Trajectory 평가 추가 |
| 수동으로만 평가 | 확장 불가, 일관성 없음 | 자동화 평가 파이프라인 구축 |
| 테스트 케이스가 너무 적음 | 오버피팅된 에이전트를 만들 수 있음 | 다양한 케이스 커버 |
| 비용 추적 없음 | 운영 비용 예측 불가 | API 호출마다 토큰 사용량 기록 |

## AI 팁

테스트 케이스를 만들 때 "정상 케이스"만이 아니라 **엣지 케이스**(모호한 요청, 도구 실패 상황, 매우 복잡한 목표)도 포함하세요. 에이전트가 정상 케이스만 잘 처리한다면 실제 운영에서 자주 실패합니다.

```python
test_cases = [
    # 정상 케이스
    {"id": "tc-001", "goal": "삼성전자 현재 주가", "evaluator": lambda r: "원" in r},
    # 엣지 케이스
    {"id": "tc-002", "goal": "삼성전자 내일 주가", "evaluator": lambda r: "예측" in r or "알 수 없" in r},
    # 도구 실패 케이스
    {"id": "tc-003", "goal": "존재하지 않는 회사 주가", "evaluator": lambda r: "찾을 수 없" in r}
]
```

## 체크리스트

- [ ] 종단 성공률, Trajectory 효율성, 비용 세 가지를 모두 측정한다
- [ ] 자동화된 평가 파이프라인을 구축했다
- [ ] 정상 케이스와 엣지 케이스를 모두 포함한 테스트 셋이 있다
- [ ] 에이전트 변경 시 평가를 자동으로 실행한다
- [ ] 비용 예산 초과 시 알림을 설정했다

## 처음 질문으로 돌아가기

**성공률 외 필요한 지표는?** Trajectory 효율성(몇 단계로 도달했는지), 비용(토큰과 API 호출 수), 도구 정확도(올바른 도구를 올바른 시점에 사용했는지).

**Trajectory 평가가 중요한 이유는?** 답이 맞더라도 10번의 중복 검색을 했다면 운영 비용이 과도합니다. 최적 경로를 찾아야 효율적인 에이전트가 됩니다.

**비용과 품질 트레이드오프는?** 더 많은 도구 호출은 품질을 높일 수 있지만 비용도 증가합니다. 목표에 맞는 최소 도구 호출로 최고 품질을 내는 경로를 찾는 것이 핵심입니다.

**자동화 평가 파이프라인은?** 에이전트를 실행하고, 결과를 미리 정의한 평가 함수로 채점하고, 비용과 Trajectory를 기록하는 파이프라인을 CI/CD에 통합합니다.

**평가 결과로 개선 방향은?** 성공률이 낮으면 프롬프트 개선, 비용이 높으면 불필요한 도구 호출 제거, Trajectory가 비효율적이면 도구 선택 로직 개선.

## 정리

에이전트 평가는 "결과가 맞는가?"만이 아닙니다. 어떤 경로로 도달했는지, 얼마나 효율적이었는지, 비용은 얼마인지까지 측정해야 합니다. 자동화된 평가 파이프라인 없이는 에이전트를 체계적으로 개선할 수 없습니다. 바이브코딩에서 에이전트를 운영에 올리기 전에 평가 파이프라인을 먼저 구축하세요.

다음 글에서는 에이전트가 실패해도 복구하는 **오류 처리와 신뢰성**을 다룹니다.

## 참고 자료

- [AI Agent 기초 원문: 에이전트 평가](../ko/07-agent-evaluation.md)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI Agent 기초 (1/10): AI 에이전트란 무엇인가](./01-what-is-an-ai-agent.md)
2. [바이브코딩을 위한 AI Agent 기초 (2/10): 컨텍스트 엔지니어링](./02-context-engineering.md)
3. [바이브코딩을 위한 AI Agent 기초 (3/10): 도구 사용 기초](./03-tool-use-fundamentals.md)
4. [바이브코딩을 위한 AI Agent 기초 (4/10): 에이전트 워크플로우 설계](./04-agent-workflow-design.md)
5. [바이브코딩을 위한 AI Agent 기초 (5/10): 메모리와 상태 관리](./05-memory-and-state.md)
6. [바이브코딩을 위한 AI Agent 기초 (6/10): 멀티 에이전트 시스템](./06-multi-agent-systems.md)
7. **바이브코딩을 위한 AI Agent 기초 (7/10): 에이전트 평가 (현재 글)**
8. [바이브코딩을 위한 AI Agent 기초 (8/10): 오류 처리와 신뢰성](./08-error-handling-reliability.md)
9. [바이브코딩을 위한 AI Agent 기초 (9/10): 프로덕션 운영](./09-production-operations.md)
10. [바이브코딩을 위한 AI Agent 기초 (10/10): 첫 번째 에이전트 만들기](./10-building-first-agent.md)
<!-- toc:end -->

Tags: Agent Evaluation, Trajectory, Cost Tracking, 바이브코딩, Vibe Coding
