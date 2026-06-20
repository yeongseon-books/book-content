---
title: "바이브코딩을 위한 LLM 앱 운영 (6/6): LLM 앱 운영 완성"
series: llm-apps-ops-101
episode: 6
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LLMOps
- Production
- Python
- LLM
---

# 바이브코딩을 위한 LLM 앱 운영 (6/6): LLM 앱 운영 완성

이 글은 **바이브코딩을 위한 LLM 앱 운영** 시리즈의 마지막 글입니다. 모니터링·비용·평가·보안·배포 레이어를 한 요청 경로 위에 통합해 운영 파이프라인을 완성합니다.

---

금요일 오후, 대시보드에 비용 알람이 울립니다. 30분 전부터 토큰 소비가 평소의 3배입니다. 비용 담당자는 "어떤 요청이 문제인지 모르겠다"고 말하고, 보안 담당자는 "내 로그에는 차단된 게 없다"고 합니다. 평가 담당자는 "품질 점수는 정상"이라고 합니다. 세 사람 모두 맞는 말을 하고 있지만, 한 시간이 지나도 원인은 좁혀지지 않습니다.

이것이 레이어가 분산되어 있을 때 생기는 문제입니다. 모든 레이어가 같은 call_id 위에서 연결되어야 "비용 급증 → 보안 이벤트 없음 → 품질 정상 → 요청 패턴 분석"으로 빠르게 좁혀집니다.

> "운영 파이프라인은 모든 레이어가 call_id 하나로 연결될 때 완성됩니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 5개 레이어(로깅·비용·평가·보안·배포)를 어떻게 단일 파이프라인으로 연결하나요?
2. call_id가 모든 레이어를 연결하는 방법이 무엇인가요?
3. 운영 대시보드에서 어떤 지표를 우선으로 봐야 하나요?
4. 장애 발생 시 어떤 순서로 레이어를 확인하나요?
5. 팀원이 각 레이어의 로그를 쉽게 조회할 수 있나요?

---

## 통합 운영 파이프라인

```python
from dataclasses import dataclass
import uuid
import time

@dataclass
class OpsContext:
    call_id: str
    session_id: str
    endpoint: str
    user_id: str

def ops_pipeline(user_input: str, ctx: OpsContext, version_set, llm_call_fn) -> dict:
    result = {
        "call_id": ctx.call_id,
        "success": False,
        "response": None,
        "layers": {},
    }

    # 1. 보안 검증
    from .security import check_input, filter_output
    input_check = check_input(user_input)
    result["layers"]["security_input"] = {"safe": input_check.safe}
    if not input_check.safe:
        result["layers"]["security_input"]["threat"] = input_check.threat_type
        return result

    # 2. LLM 호출 (로깅 포함)
    start = time.time()
    try:
        response = llm_call_fn(user_input, version_set)
        latency_ms = (time.time() - start) * 1000
        result["layers"]["llm_call"] = {"latency_ms": latency_ms}
    except Exception as e:
        result["layers"]["llm_call"] = {"error": str(e)}
        return result

    # 3. 출력 보안 필터
    output_check = filter_output(response)
    result["layers"]["security_output"] = {"safe": output_check["safe"]}
    if not output_check["safe"]:
        response = output_check["filtered_response"]

    # 4. 품질 평가
    from .evaluation import RuleEvaluator
    eval_result = RuleEvaluator(version_set.eval_rules).evaluate(response)
    result["layers"]["evaluation"] = {"passed": eval_result.passed, "score": eval_result.score}

    # 5. 비용 기록
    result["layers"]["cost"] = {"endpoint": ctx.endpoint}

    result["success"] = True
    result["response"] = response
    return result
```

## 운영 대시보드 지표

```python
def get_dashboard_metrics(log_store, cost_tracker, quality_tracker, last_hours: int = 24) -> dict:
    return {
        "total_calls": log_store.count_recent(hours=last_hours),
        "error_rate": log_store.error_rate(hours=last_hours),
        "avg_latency_ms": log_store.avg_latency(hours=last_hours),
        "total_cost_usd": cost_tracker.recent_total(hours=last_hours),
        "quality_failure_rate": quality_tracker.failure_rate("all"),
        "security_blocks": log_store.security_block_count(hours=last_hours),
    }
```

## 장애 분석 조회

```python
def investigate_call(call_id: str, stores: dict) -> dict:
    """call_id로 모든 레이어의 정보를 한 번에 조회"""
    return {
        "llm_log": stores["log"].get_by_id(call_id),
        "cost": stores["cost"].get_by_call_id(call_id),
        "quality": stores["quality"].get_by_call_id(call_id),
        "security": stores["security"].get_by_call_id(call_id),
    }
```

---

## Before / After

| 항목 | Before (레이어 분산) | After (통합 파이프라인) |
|------|--------------------|-----------------------|
| 장애 원인 파악 | 레이어별 개별 조회 | call_id 하나로 통합 조회 |
| 비용-품질 연결 | 별도 분석 | 같은 레코드에서 확인 |
| 운영 가시성 | 팀별 분산 | 단일 대시보드 |
| 장애 대응 시간 | 1시간+ | 분 단위 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| call_id 미공유 | 레이어 간 연결 불가 | OpsContext에 call_id 필수 |
| 레이어 순서 오류 | 보안 검증 누락 | 보안 → LLM → 출력 보안 순서 |
| 장애 조회 수동 | 대응 지연 | investigate_call 통합 조회 |
| 대시보드 지표 없음 | 운영 상태 불명 | get_dashboard_metrics |

---

## AI 활용 팁

```
모니터링·비용·평가·보안 레이어를 ops_pipeline 함수로 통합해줘.
모든 레이어는 call_id를 공유하고, layers 딕셔너리에 각 레이어 결과를 기록해줘.
call_id 하나로 모든 레이어의 정보를 조회하는 investigate_call 함수도 만들어줘.
운영 대시보드에 필요한 지표(오류율, 지연시간, 비용, 품질 실패율)를 get_dashboard_metrics로 집계해줘.
```

---

## 체크리스트

- [ ] OpsContext(call_id, session_id, endpoint, user_id)
- [ ] ops_pipeline에 5개 레이어 통합
- [ ] 레이어 실행 순서 고정(보안→LLM→보안→평가→비용)
- [ ] investigate_call 통합 조회
- [ ] get_dashboard_metrics 집계
- [ ] 대시보드 알람 임계값 설정

---

## 처음 질문으로 돌아가기

"레이어가 5개인데 어떻게 하나로 연결하나요?" — call_id가 열쇠입니다. 모든 레이어가 같은 call_id를 기록하면, 장애 발생 시 call_id 하나로 로그·비용·품질·보안 정보를 한 번에 조회할 수 있습니다. ops_pipeline이 그 연결 통로입니다.

---

## 정리

- OpsContext의 call_id가 모든 레이어를 연결하는 키다
- ops_pipeline이 보안→LLM→출력 보안→평가→비용 순서로 레이어를 실행한다
- investigate_call로 call_id 하나에서 모든 레이어 정보를 조회한다
- get_dashboard_metrics로 실시간 운영 상태를 집계한다

---

## 참고 자료

- [LangSmith 프로덕션 모니터링](https://docs.smith.langchain.com/)
- [LLMOps 가이드](https://www.databricks.com/blog/llmops)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 통합 운영 파이프라인
- 운영 대시보드 지표
- 장애 분석 조회
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LLMOps, Production, Python, LLM
