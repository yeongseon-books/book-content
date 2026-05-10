---
title: 운영 가드레일 시스템 구축
series: ai-safety-guardrails-101
episode: 10
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Safety
- Guardrails
- Production
- Architecture
last_reviewed: '2026-05-03'
seo_description: 지금까지 Ep1~9에서 다룬 guardrail은 모두 독립된 부품입니다.
---

# 운영 가드레일 시스템 구축

> AI Safety & Guardrails 101 시리즈 (10/10)

---
<!-- a-grade-intro:begin -->
## 핵심 질문

운영 가드레일 시스템을 어떻게 통합해야 다층 방어가 일관되게 동작할까요?

이 글은 그 질문에 답하기 위해 운영 가드레일 시스템의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## Section 1

## 9개의 부품을 하나의 시스템으로

지금까지 Ep1~9에서 다룬 guardrail은 모두 독립된 부품입니다. 운영에서는 각 부품이 어느 위치에서, 어떤 순서로, 어떤 fallback으로 동작하는지 한 장의 아키텍처로 정리해야 합니다. 이 글은 capstone으로 그 아키텍처를 만듭니다.

목표:

- 입력 → 모델 → 도구 호출 → 출력의 각 경계마다 어떤 guardrail을 둘지 결정
- fail-open과 fail-closed 정책을 명확히
- 성능 예산 안에서 guardrail 비용을 통제
- 단일 observability 평면에서 모든 차단·통과 사건을 추적

## 4계층 아키텍처

LLM 시스템에서 guardrail이 자리 잡는 위치는 네 곳입니다.

| 계층 | 시점 | 담당 guardrail |
| --- | --- | --- |
| Pre-input | 사용자 요청 직후 | rate limit, jailbreak 탐지, prompt injection 정규화 |
| Pre-prompt | 모델 호출 직전 | PII 마스킹, 컨텍스트 sanitization, system prompt 검증 |
| Post-output | 모델 응답 직후 | 모더레이션, hallucination grounding, PII 재검사 |
| Audit | 모든 단계 | append-only log, decision rationale, cost 추적 |

각 계층은 독립적으로 fail해야 하며, 한 계층의 실패가 다른 계층 실행을 막아서는 안 됩니다.

## Pipeline 구현

위 4계층을 코드로 옮긴 단순화된 버전입니다. 실제 구현에서는 각 함수를 Ep1~9의 모듈로 교체합니다.

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class GuardrailResult:
    allowed: bool
    stage: str
    reason: str | None = None
    metadata: dict | None = None

class GuardrailPipeline:
    def __init__(self, audit_sink: Callable):
        self.audit = audit_sink

    def run(self, request: dict) -> dict:
        ctx = {"request_id": request["request_id"], "user_id": request["user_id"]}

        # Pre-input
        for check in [self.rate_limit, self.detect_jailbreak, self.sanitize_input]:
            res = check(request)
            self.audit({**ctx, "stage": res.stage, "allowed": res.allowed, "reason": res.reason})
            if not res.allowed:
                return self._block(res)

        # Pre-prompt
        masked_prompt, pii_meta = self.mask_pii(request["prompt"])
        retrieved = self.retrieve(masked_prompt)
        sanitized_chunks = self.sanitize_context(retrieved)

        # Model call
        response = self.call_model(masked_prompt, sanitized_chunks)

        # Post-output
        for check in [self.moderate_output, self.verify_grounding, self.recheck_pii]:
            res = check(response, sanitized_chunks)
            self.audit({**ctx, "stage": res.stage, "allowed": res.allowed, "reason": res.reason})
            if not res.allowed:
                return self._block(res)

        # Restore PII tokens for the original user
        final = self.unmask_pii(response, pii_meta)
        self.audit({**ctx, "stage": "delivered", "allowed": True})
        return {"answer": final}

    def _block(self, res: GuardrailResult) -> dict:
        return {"answer": "요청을 처리할 수 없습니다.", "blocked": True, "stage": res.stage}
```

핵심은 audit가 모든 단계의 결과를 기록한다는 점입니다. 차단되더라도 언제 어디서 왜 차단되었는지 사후 추적이 가능합니다.

## Fail-Open vs Fail-Closed

Guardrail이 자체 오류로 결과를 내지 못할 때 어떻게 할 것인가? 정책을 사전에 결정해야 합니다.

| 시나리오 | 권장 정책 | 이유 |
| --- | --- | --- |
| Rate limiter Redis down | fail-open + alert | 사용자 차단보다 알림이 우선, 짧은 시간이라면 비용 위험 < UX 위험 |
| Moderation API down | fail-closed | 유해 콘텐츠 통과 위험이 큼 |
| PII 마스킹 실패 | fail-closed | GDPR 위반 위험 |
| Grounding 검증 timeout | partial-deliver + 경고 | 검증 표시만 빼고 응답 |
| Audit log 실패 | fail-closed (production), fail-open (dev) | 감사 누락은 컴플라이언스 위반 |

각 가드레일에 명시적으로 `on_error` 정책을 표시합니다.

```python
def safe_call(check_fn, request, on_error="closed"):
    try:
        return check_fn(request)
    except Exception as e:
        log_guardrail_error(check_fn.__name__, e)
        if on_error == "open":
            return GuardrailResult(allowed=True, stage=check_fn.__name__, reason="degraded")
        return GuardrailResult(allowed=False, stage=check_fn.__name__, reason="error")
```

## 성능 예산

모든 guardrail을 직렬 실행하면 사용자가 체감하는 지연이 커집니다. 다음 패턴으로 비용을 통제합니다.

1. **병렬화 가능한 체크는 동시 실행**: PII 마스킹과 jailbreak 탐지처럼 서로 의존이 없는 체크는 `asyncio.gather`로 묶습니다.
2. **빠른 체크부터 직렬 실행**: regex(<1ms) → 임베딩(<50ms) → LLM judge(<800ms) 순서로 두어 차단되면 비싼 단계를 건너뜁니다.
3. **캐싱**: 같은 입력은 hash 키로 결과를 캐시. PII 마스킹·grounding 결과는 5분 TTL이 일반적입니다.
4. **샘플링**: 비용이 큰 체크(예: full grounding)를 모든 요청에 돌리지 않고 일부 트래픽에만 적용해 회귀 신호로 사용.

목표 예시: P95 guardrail overhead < 300ms (모델 호출 시간 제외).

## Observability

대시보드에 항상 표시할 핵심 지표:

| 그룹 | 지표 |
| --- | --- |
| 트래픽 | RPS, input/output tokens/min, $/min |
| 차단 | 카테고리별 차단율, false positive rate |
| 지연 | 단계별 P50/P95 latency |
| 신뢰 | hallucination flag rate, grounding fail rate |
| 비용 | 모델별, 사용자별 누적 $ |
| 보안 | jailbreak 탐지 rate, PII 발견 rate |

Slack 알림은 두 가지로 분리:

- **Page**: SLO 위반(P95 > 500ms 5분 이상, 차단율 급증, audit log 실패)
- **Daily digest**: false positive 의심 사례, 새로운 jailbreak 패턴, drift 신호

## 회귀 셋과 CI 통합

Guardrail 변경은 100% 코드 리뷰만으로 안전을 보장할 수 없습니다. PR 단위 회귀 셋이 필요합니다.

```python
def run_regression():
    suites = {
        "jailbreak_attacks": load_jailbreak_set(),
        "benign_prompts": load_benign_set(),
        "pii_examples": load_pii_set(),
        "moderation_cases": load_moderation_set(),
        "rag_grounding": load_rag_set(),
    }
    results = {}
    for name, cases in suites.items():
        results[name] = evaluate_pipeline(pipeline, cases)
    return results
```

GitHub Actions에서 PR마다 실행하고, 다음 항목 중 하나라도 회귀하면 merge를 막습니다.

- Jailbreak recall < 0.95
- Benign false positive > 1%
- PII recall < 0.98
- Grounding precision < 0.85

## 점진적 rollout

Guardrail 변경을 production에 한 번에 켜지 않습니다.

1. **Shadow mode (1주)**: 결과를 audit에만 기록, 실제 차단은 안 함. metric 확인.
2. **5% canary (3일)**: 5% 트래픽에 활성화. 단계별 차단율, 사용자 항의 모니터링.
3. **50% rollout (3일)**: 절반 트래픽으로 확대. SLO 위반 없으면 진행.
4. **100% rollout**: 전체 적용. 1주간 dashboard 집중 모니터링.

문제가 보이면 feature flag로 즉시 5%, 0%로 되돌립니다.

## 인적 절차

기술적 guardrail이 100% 막을 수 없는 영역은 사람의 개입으로 보완합니다.

- **On-call**: guardrail 알림 24/7 대응 인원
- **Red team review**: 분기마다 jailbreak 시도 팀이 새 패턴 시뮬레이션
- **Compliance review**: 분기마다 audit log 샘플링 검토
- **사용자 항의 처리**: false positive 보고 24시간 내 1차 응답

## Common Mistakes

1. **모든 guardrail을 직렬로 실행**: 사용자 체감 지연이 폭증합니다. 병렬화와 비용 순 정렬을 적용합니다.
2. **fail 정책을 명시하지 않음**: 장애 발생 시 매번 다르게 동작해 사고가 확대됩니다. 각 체크에 `on_error` 정책을 박아둡니다.
3. **Audit를 옵션으로 취급**: 차단·통과 결정의 근거가 없으면 컴플라이언스 대응이 불가능합니다. audit는 다른 모든 체크와 동등한 1급 기능입니다.
4. **회귀 셋 없이 배포**: 임계치 한 줄 바꿔도 false positive가 폭증합니다. PR마다 회귀 셋을 통과해야 merge합니다.
5. **한 번에 100% 켜기**: shadow → canary → rollout 단계를 건너뛰면 사고 발생 시 영향이 전체 사용자에 미칩니다.

## 핵심 요약

- Guardrail은 pre-input, pre-prompt, post-output, audit 4계층으로 분리해 각 위치별 책임을 명확히 합니다.
- fail-open/fail-closed 정책을 체크별로 사전 정의해 장애 시 일관된 동작을 보장합니다.
- 병렬화, 비용 순 직렬화, 캐싱, 샘플링으로 P95 guardrail overhead를 300ms 이하로 유지합니다.
- 회귀 셋을 CI에 통합하고 jailbreak recall, PII recall, grounding precision 등 정량 SLO로 merge gate를 둡니다.
- shadow → canary → rollout 단계와 on-call·red team·compliance review로 기술과 인적 절차를 함께 운영합니다.
## 참고 자료

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Google - Responsible AI practices](https://ai.google/responsibility/responsible-ai-practices/)
- [Anthropic - Responsible Scaling Policy](https://www.anthropic.com/news/anthropics-responsible-scaling-policy)
