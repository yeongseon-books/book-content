---
title: "바이브코딩을 위한 AI Agent 기초 (4/10): 에이전트 워크플로우 설계"
series: ai-agent-101
episode: 4
language: ko
tags:
- Workflow Design
- ReAct
- Plan-and-Execute
- Reflexion
- 바이브코딩
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI Agent 기초 (4/10): 에이전트 워크플로우 설계

이 글은 **바이브코딩을 위한 AI Agent 기초** 시리즈의 네 번째 글입니다.

---

바이브코딩으로 에이전트를 만들다 보면 "한 번에 모든 걸 처리하는 에이전트" vs "단계별로 나누는 에이전트" 중 어느 것이 나은지 고민하게 됩니다. 간단한 작업은 단일 루프로 충분하지만, 복잡한 작업은 미리 계획을 세우거나 자기 반성을 통해 개선하는 구조가 필요합니다.

에이전트 워크플로우 패턴은 세 가지로 정리됩니다. **ReAct**(즉흥 실행), **Plan-and-Execute**(계획 후 실행), **Reflexion**(반성을 통한 개선). 바이브코딩에서는 이 세 가지 패턴을 언제 어떻게 선택하느냐가 에이전트 품질을 결정합니다.

> "에이전트 워크플로우는 단순한 코드 구조가 아닙니다. '이 작업을 어떤 방식으로 생각하게 할 것인가'를 설계하는 일입니다."

## 이 글에서 다룰 질문

1. ReAct, Plan-and-Execute, Reflexion 패턴은 각각 어떤 상황에 적합한가요?
2. 복잡한 작업에서 계획 단계가 왜 필요한가요?
3. Reflexion 패턴은 어떻게 에이전트 품질을 높이나요?
4. 워크플로우 선택이 잘못되면 어떤 문제가 생기나요?
5. LangGraph 같은 워크플로우 프레임워크는 언제 사용하나요?

---

## 세 가지 워크플로우 패턴 비교

| 패턴 | 특징 | 적합한 상황 | 주의점 |
|------|------|------------|--------|
| ReAct | 즉흥적 추론+행동 루프 | 간단한 검색/조회 작업 | 복잡한 멀티스텝 작업에서 방향 잃음 |
| Plan-and-Execute | 미리 계획 수립 후 실행 | 여러 단계가 필요한 복잡한 작업 | 계획 수정이 어려울 수 있음 |
| Reflexion | 실행 후 자기 반성으로 개선 | 품질이 중요한 생성 작업 | 반성 루프가 많으면 비용 증가 |

## Before / After: 워크플로우 패턴 선택

**Before (ReAct를 모든 곳에 사용)**
```python
# 복잡한 리포트 작성에 단순 ReAct 적용
agent = ReactAgent(tools=[search, write])
result = agent.run("경쟁사 분석 리포트를 작성해줘")
# 문제: 방향 없이 임의로 검색하다 품질 낮은 리포트 생성
```

**After (Plan-and-Execute 적용)**
```python
class PlanAndExecuteAgent:
    def run(self, goal: str) -> str:
        # 1단계: 계획 수립
        plan = self.llm.chat(f"""
        목표: {goal}
        이 목표를 달성하기 위한 단계별 계획을 JSON으로 작성하세요.
        각 단계에 필요한 도구와 예상 결과를 포함하세요.
        """)

        # 2단계: 계획 실행
        results = []
        for step in plan["steps"]:
            result = self.execute_step(step)
            results.append(result)

        # 3단계: 결과 통합
        return self.synthesize(goal, results)
```

## Reflexion: 자기 반성으로 품질 향상

Reflexion 패턴은 에이전트가 결과를 생성한 뒤 스스로 비판하고 개선하는 루프를 추가합니다.

```python
class ReflexionAgent:
    def run(self, goal: str, max_iterations: int = 3) -> str:
        draft = self.initial_attempt(goal)

        for i in range(max_iterations):
            # 자기 반성
            critique = self.llm.chat(f"""
            목표: {goal}
            현재 답변: {draft}

            이 답변의 문제점을 구체적으로 지적하세요:
            1. 빠진 정보가 있는가?
            2. 부정확한 내용이 있는가?
            3. 더 좋은 표현이 가능한가?
            """)

            if "개선 불필요" in critique:
                break

            # 개선
            draft = self.improve(draft, critique)

        return draft
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 모든 작업에 ReAct 사용 | 복잡한 작업에서 품질 저하 | 작업 복잡도에 따라 패턴 선택 |
| Reflexion 루프 무제한 | 비용 폭발, 과개선 | max_iterations 설정 |
| 계획을 실행 중 수정 불가 | 예상치 못한 상황 대응 불가 | 실행 중 재계획 허용 설계 |
| StepResult 없이 진행 | 어느 단계가 실패했는지 모름 | 각 단계 결과를 명시적으로 기록 |

## AI 팁

각 워크플로우 단계의 결과를 `StepResult` 형태로 기록하면 나중에 어느 단계에서 문제가 생겼는지 디버깅하기 훨씬 쉬워집니다.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class StepResult:
    step_id: int
    description: str
    tool_used: str | None
    input_data: Any
    output_data: Any
    success: bool
    duration_ms: float
    error: str | None = None
```

복잡한 멀티스텝 워크플로우에서는 LangGraph 같은 프레임워크를 사용하면 단계 간 의존성과 조건 분기를 그래프로 명시할 수 있어 관리가 쉬워집니다.

## 체크리스트

- [ ] 작업의 복잡도에 따라 ReAct/Plan-and-Execute/Reflexion 중 선택했다
- [ ] 각 실행 단계를 StepResult로 기록한다
- [ ] Reflexion 루프에 max_iterations를 설정했다
- [ ] 실행 중 계획 재수립이 필요한 상황을 처리한다
- [ ] 워크플로우 실행 시간과 비용을 모니터링한다

## 처음 질문으로 돌아가기

**ReAct vs Plan-and-Execute vs Reflexion 언제 쓰나요?** ReAct는 단순한 조회 작업, Plan-and-Execute는 여러 단계가 필요한 복잡한 작업, Reflexion은 품질이 특히 중요한 생성 작업에 적합합니다.

**복잡한 작업에서 계획 단계가 왜 필요한가요?** 미리 계획을 세우면 필요한 도구와 단계를 파악하고 순서를 최적화할 수 있습니다. 즉흥적으로 진행하면 중요한 단계를 빠뜨리거나 불필요한 작업을 반복합니다.

**Reflexion 패턴은 어떻게 품질을 높이나요?** 초안을 생성한 뒤 스스로 비판적으로 검토하고 개선하는 루프를 통해 점진적으로 품질을 높입니다. 사람이 초안을 다듬는 과정과 유사합니다.

**워크플로우 선택이 잘못되면?** 복잡한 작업에 ReAct를 쓰면 방향 없이 헤매다 낮은 품질의 결과를 냅니다. Reflexion을 간단한 작업에 쓰면 불필요한 비용이 발생합니다.

**LangGraph는 언제?** 조건 분기, 병렬 실행, 루프가 복잡하게 얽힌 워크플로우에서 LangGraph 같은 그래프 기반 프레임워크가 코드를 관리하기 훨씬 쉽게 만들어 줍니다.

## 정리

에이전트 워크플로우는 "어떻게 생각하게 할 것인가"를 설계하는 작업입니다. 단순한 작업에는 ReAct로 충분하지만, 복잡한 멀티스텝 작업에는 계획 수립, 자기 반성 같은 추가 구조가 필요합니다. 바이브코딩에서 에이전트 품질이 낮다면 워크플로우 패턴을 먼저 점검해보세요.

다음 글에서는 에이전트가 정보를 기억하고 상태를 유지하는 **메모리와 상태 관리**를 다룹니다.

## 참고 자료

- [AI Agent 기초 원문: 에이전트 워크플로우 설계](../ko/04-agent-workflow-design.md)
- [Reflexion: Language Agents with Verbal Reinforcement Learning (Shinn et al., 2023)](https://arxiv.org/abs/2303.11366)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI Agent 기초 (1/10): AI 에이전트란 무엇인가](./01-what-is-an-ai-agent.md)
2. [바이브코딩을 위한 AI Agent 기초 (2/10): 컨텍스트 엔지니어링](./02-context-engineering.md)
3. [바이브코딩을 위한 AI Agent 기초 (3/10): 도구 사용 기초](./03-tool-use-fundamentals.md)
4. **바이브코딩을 위한 AI Agent 기초 (4/10): 에이전트 워크플로우 설계 (현재 글)**
5. [바이브코딩을 위한 AI Agent 기초 (5/10): 메모리와 상태 관리](./05-memory-and-state.md)
6. [바이브코딩을 위한 AI Agent 기초 (6/10): 멀티 에이전트 시스템](./06-multi-agent-systems.md)
7. [바이브코딩을 위한 AI Agent 기초 (7/10): 에이전트 평가](./07-agent-evaluation.md)
8. [바이브코딩을 위한 AI Agent 기초 (8/10): 오류 처리와 신뢰성](./08-error-handling-reliability.md)
9. [바이브코딩을 위한 AI Agent 기초 (9/10): 프로덕션 운영](./09-production-operations.md)
10. [바이브코딩을 위한 AI Agent 기초 (10/10): 첫 번째 에이전트 만들기](./10-building-first-agent.md)
<!-- toc:end -->

Tags: Workflow Design, ReAct, Plan-and-Execute, Reflexion, 바이브코딩
