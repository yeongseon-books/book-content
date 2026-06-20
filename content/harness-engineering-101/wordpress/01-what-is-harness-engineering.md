---
title: "바이브코딩을 위한 하네스 엔지니어링 (1/10): Harness Engineering이란 무엇인가?"
series: harness-engineering-101
episode: 1
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- AI Agent
- Harness
- Reliability
- Production
---

# 바이브코딩을 위한 하네스 엔지니어링 (1/10): Harness Engineering이란 무엇인가?

이 글은 **바이브코딩을 위한 하네스 엔지니어링** 시리즈의 첫 번째 글입니다. AI 에이전트가 신뢰할 수 있게 작동하도록 환경을 설계하는 Harness Engineering의 개념과 8가지 하네스 구조를 소개합니다.

---

AI 에이전트를 만들었습니다. 테스트에서는 잘 작동합니다. 프로덕션에 올렸더니 예상하지 못한 일을 합니다. 잘못된 파일을 삭제하거나, 승인 없이 이메일을 보내거나, 루프에 빠져 같은 작업을 반복합니다. 에이전트 자체가 문제일까요?

대부분은 에이전트가 아니라 에이전트를 둘러싼 환경이 문제입니다. 어떤 작업을 해야 하는지 명확하지 않고, 어떤 정보를 써야 하는지 정의되지 않았고, 어디까지 해도 되는지 경계가 없습니다. 그 환경을 설계하는 것이 Harness Engineering입니다.

바이브코딩으로 AI에게 "에이전트 만들어줘"라고 하면 에이전트 코드는 나옵니다. 하지만 그 에이전트가 잘못된 방향으로 달릴 때 멈출 구조는 나오지 않습니다. 하네스가 없는 에이전트는 빠른 차에 브레이크가 없는 것과 같습니다.

이 글에서는 Harness Engineering의 8가지 구성 요소를 개관하고 각 하네스가 어떤 문제를 해결하는지 설명합니다.

> "에이전트의 신뢰성은 에이전트의 능력이 아니라 에이전트를 둘러싼 하네스에서 나옵니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 에이전트가 프로덕션에서 예상치 못한 행동을 보일 때 어디를 먼저 확인하나요?
2. 에이전트에게 줄 컨텍스트의 양을 어떻게 결정하나요?
3. 에이전트가 사용하면 안 되는 도구를 어떻게 막나요?
4. 에이전트 작업이 완료되었는지 어떻게 판단하나요?
5. 에이전트 실패를 사람이 개입하기 전에 감지할 수 있나요?

---

## 8가지 하네스 구조

| 하네스 | 역할 | 없을 때 |
|--------|------|---------|
| Task Harness | 모호한 요청을 실행 가능한 작업으로 변환 | 에이전트가 잘못된 일을 함 |
| Context Harness | 필요한 정보만 에이전트에 전달 | 컨텍스트 창 낭비 또는 정보 부족 |
| Constraint Harness | 허용 범위와 금지 행동 정의 | 예상치 못한 부작용 발생 |
| Tool Harness | 도구를 안전하게 설계 | 위험한 작업이 실행됨 |
| Test Harness | 완료 조건을 테스트로 고정 | 작업 완료 여부 판단 불가 |
| Feedback Loop | 실패를 감지하고 수정 | 에이전트가 루프에 빠짐 |
| Approval Gate | 사람 승인이 필요한 지점 설계 | 중요 결정이 자동으로 실행됨 |
| Observability | 에이전트 작업 추적·재현 | 장애 원인 파악 불가 |

## 하네스 설계 원칙

```python
@dataclass
class HarnessConfig:
    task_spec: dict          # 작업 명세
    context_budget: int      # 컨텍스트 토큰 예산
    constraints: list[str]   # 금지 행동 목록
    allowed_tools: list[str] # 허용 도구 목록
    completion_tests: list   # 완료 조건 테스트
    approval_required: bool  # 승인 필요 여부
    log_level: str           # 로깅 수준
```

하네스는 에이전트 외부에서 정의합니다. 에이전트 코드를 수정하지 않고 하네스 설정만 바꿔서 동작을 제어할 수 있어야 합니다.

---

## Before / After

| 항목 | Before (하네스 없음) | After (하네스 적용) |
|------|--------------------|--------------------|
| 에이전트 행동 | 예측 불가 | 설정된 경계 내 동작 |
| 실패 감지 | 결과 확인 후 | 테스트로 즉시 감지 |
| 중요 결정 | 자동 실행 | 승인 게이트 통과 후 실행 |
| 장애 분석 | "뭔가 잘못됐다" | 단계별 추적 가능 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 하네스를 에이전트 내부에 구현 | 재사용 불가 | 외부 설정으로 분리 |
| 모든 도구를 허용 | 위험한 작업 실행 | 화이트리스트 도구 목록 |
| 완료 기준 미정의 | 루프 또는 조기 종료 | 테스트로 완료 조건 고정 |
| 승인 없는 자동화 | 돌이킬 수 없는 실수 | Approval Gate 설계 |

---

## AI 활용 팁

```
AI 에이전트를 설계할 때 에이전트 코드와 별도로 HarnessConfig를 먼저 정의해줘.
HarnessConfig는 task_spec, context_budget, constraints, allowed_tools, completion_tests, approval_required를 포함해야 해.
에이전트는 이 설정을 읽어서 동작하고, 설정 변경으로 행동을 제어할 수 있어야 해.
```

---

## 체크리스트

- [ ] 에이전트 작업 명세(task_spec) 문서화
- [ ] 컨텍스트 예산(context_budget) 설정
- [ ] 금지 행동 목록(constraints) 정의
- [ ] 허용 도구 화이트리스트 작성
- [ ] 완료 조건 테스트 정의
- [ ] Approval Gate 필요 지점 식별

---

## 처음 질문으로 돌아가기

"에이전트가 프로덕션에서 왜 이상하게 동작하나요?" — 에이전트 코드의 문제일 수도 있지만, 대부분은 하네스가 없는 문제입니다. Task, Context, Constraint, Tool, Test, Feedback, Approval, Observability — 8가지 하네스가 에이전트의 신뢰성을 만듭니다.

---

## 정리

- Harness Engineering은 에이전트를 둘러싼 환경을 설계하는 것이다
- 8가지 하네스(Task/Context/Constraint/Tool/Test/Feedback/Approval/Observability)가 에이전트의 신뢰성을 만든다
- 하네스는 에이전트 외부에서 설정으로 정의한다
- 이후 글에서 각 하네스를 코드와 함께 상세히 다룬다

---

## 참고 자료

- [LangGraph 에이전트 설계](https://langchain-ai.github.io/langgraph/)
- [Anthropic 에이전트 신뢰성 가이드](https://docs.anthropic.com/en/docs/build-with-claude/agentic-and-tool-use)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 8가지 하네스 구조
- 하네스 설계 원칙
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, AI Agent, Harness, Reliability, Production
