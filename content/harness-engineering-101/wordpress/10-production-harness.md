---
title: "바이브코딩을 위한 하네스 엔지니어링 (10/10): Production Harness — 운영 가능한 Agent 작업 환경 만들기"
series: harness-engineering-101
episode: 10
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- AI Agent
- Harness
- Production
- Deployment
---

# 바이브코딩을 위한 하네스 엔지니어링 (10/10): Production Harness — 운영 가능한 Agent 작업 환경 만들기

이 글은 **바이브코딩을 위한 하네스 엔지니어링** 시리즈의 마지막 글입니다. Task부터 Observability까지 9개 하네스를 통합해 프로덕션에서 운영 가능한 에이전트 작업 환경을 완성합니다.

---

Task, Context, Constraint, Tool, Test, Feedback, Approval, Observability — 8개 하네스를 각각 만들었습니다. 이제 연결해야 합니다. "그냥 순서대로 실행하면 되지 않나요?"라고 생각하면, 하네스들이 서로 상태를 공유하는 방법, 실패가 전파되는 방식, 운영 환경에서 설정을 바꾸는 방법을 고민하지 않은 것입니다.

Production Harness는 모든 하네스를 단일 에이전트 런타임으로 통합하고, 운영 관점에서 모니터링·재시작·설정 변경을 가능하게 하는 구조입니다.

> "운영 가능한 에이전트는 하네스가 통합된 에이전트입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 8개 하네스를 어떻게 하나의 런타임으로 통합하나요?
2. 에이전트 재시작 시 어떤 상태가 유지되어야 하나요?
3. 프로덕션에서 하네스 설정을 코드 변경 없이 바꿀 수 있나요?
4. 에이전트 여러 인스턴스가 동시에 실행될 때 상태 충돌을 어떻게 방지하나요?
5. 에이전트 헬스체크를 어떻게 구현하나요?

---

## AgentRuntime 통합

```python
from dataclasses import dataclass

@dataclass
class AgentRuntime:
    task_harness: TaskHarness
    context_harness: ContextHarness
    constraint_harness: ConstraintHarness
    tool_harness: ToolHarness
    test_harness: TestHarness
    feedback_loop: FeedbackLoop
    approval_gate: ApprovalGate
    tracer: AgentTracer

    def run(self, raw_request: str) -> dict:
        trace_id = self.tracer.start_trace(raw_request)

        # 1. Task 명세 생성
        task = self.task_harness.parse(raw_request)

        # 2. 제약 확인
        self.constraint_harness.validate_task(task)

        # 3. 컨텍스트 구성
        context = self.context_harness.build(task)

        # 4. Approval Gate
        if self.approval_gate.requires_approval(task):
            approval = self.approval_gate.request(task)
            if not approval.approved:
                return {"success": False, "reason": "승인 거부"}

        # 5. 피드백 루프 실행
        result = self.feedback_loop.run(task, context, self.tool_harness)

        # 6. 테스트 검증
        test_result = self.test_harness.run(result)

        return {
            "success": test_result["all_required_passed"],
            "result": result,
            "trace_id": trace_id,
        }
```

## 운영 설정 외부화

```python
import yaml
from pathlib import Path

def load_harness_config(config_path: str) -> dict:
    return yaml.safe_load(Path(config_path).read_text())

# harness_config.yaml 예시
# constraint:
#   allowed_tools: [search, file_read, api_call]
#   max_cost_usd: 2.0
# context:
#   total_tokens: 8000
# feedback:
#   max_attempts: 3
# approval:
#   high_risk_actions: [data_modify, email_send]
```

## 헬스체크

```python
def agent_health_check(runtime: AgentRuntime) -> dict:
    checks = {
        "tool_registry": len(runtime.tool_harness.registry) > 0,
        "constraint_active": runtime.constraint_harness.is_active(),
        "tracer_running": runtime.tracer is not None,
    }
    return {
        "healthy": all(checks.values()),
        "checks": checks,
    }
```

---

## Before / After

| 항목 | Before (하네스 분산) | After (Production Harness) |
|------|--------------------|-----------------------------|
| 설정 변경 | 코드 수정 후 배포 | YAML 파일 변경 |
| 상태 관리 | 각 하네스 독립 | AgentRuntime으로 통합 |
| 헬스체크 | 없음 | 자동 상태 확인 |
| 운영 가시성 | 산발적 로그 | 통합 트레이스 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 설정 코드 내 하드코딩 | 배포 없이 변경 불가 | YAML/환경변수 외부화 |
| 헬스체크 없음 | 장애 늦게 발견 | /health 엔드포인트 |
| 하네스 순서 미정의 | 상태 불일치 | AgentRuntime에서 순서 고정 |
| 인스턴스 간 상태 공유 | 충돌 | 인스턴스별 독립 상태 |

---

## AI 활용 팁

```
8개 하네스(Task/Context/Constraint/Tool/Test/Feedback/Approval/Observability)를 AgentRuntime으로 통합해줘.
설정은 YAML 파일로 외부화하고, 코드 변경 없이 파라미터를 바꿀 수 있어야 해.
agent_health_check 함수로 런타임 상태를 확인할 수 있게 해줘.
```

---

## 체크리스트

- [ ] AgentRuntime dataclass로 모든 하네스 통합
- [ ] 하네스 실행 순서 정의
- [ ] YAML 설정 파일 외부화
- [ ] 헬스체크 엔드포인트
- [ ] 통합 트레이스(trace_id가 전체 실행에 걸쳐 유지)
- [ ] 재시작 후 상태 복구 로직

---

## 처음 질문으로 돌아가기

"하네스를 각각 만들었는데 어떻게 연결하나요?" — AgentRuntime이 모든 하네스를 순서대로 실행하고 상태를 공유합니다. 설정을 YAML로 외부화하면 코드 변경 없이 운영 중에 파라미터를 조정할 수 있습니다. 헬스체크가 있으면 문제를 서비스 전에 감지합니다.

---

## 정리

- AgentRuntime이 8개 하네스를 통합하고 실행 순서를 정의한다
- 하네스 설정을 YAML로 외부화해서 코드 변경 없이 조정한다
- 헬스체크로 런타임 상태를 지속적으로 모니터링한다
- trace_id가 전체 실행에 걸쳐 유지되어 통합 추적이 가능하다

---

## 참고 자료

- [LangGraph 프로덕션 배포](https://langchain-ai.github.io/langgraph/cloud/)
- [Python yaml 라이브러리](https://pyyaml.org/wiki/PyYAMLDocumentation)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- AgentRuntime 통합
- 운영 설정 외부화
- 헬스체크
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, AI Agent, Harness, Production, Deployment
