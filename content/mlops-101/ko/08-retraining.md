---
series: mlops-101
episode: 8
title: "MLOps 101 (8/10): 재학습"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - MLOps
  - Retraining
  - Automation
  - Pipeline
  - DataScience
seo_description: 명시적 트리거와 챔피언-챌린저 비교 정책을 바탕으로, 모델을 안전하게 재학습하고 프로덕션 환경에 승격시키는 운영 루프 구축 방법을 소개합니다.
last_reviewed: '2026-05-12'
---

# MLOps 101 (8/10): 재학습

모델은 한 번 배포했다고 끝나지 않습니다. 입력 분포가 바뀌고, 사용자 행동이 바뀌고, 성능 목표가 달라지면 언젠가는 다시 학습해야 합니다. 문제는 그 시점을 누가 어떤 기준으로 판단하느냐입니다.

재학습을 사람 감각에만 맡기면 느리고 일관성이 떨어집니다. 어떤 팀은 매달 돌리고, 어떤 팀은 사고가 난 뒤에야 돌리고, 어떤 팀은 새 모델이 좋아졌는지 검증도 없이 바로 교체합니다. 이러면 자동화가 아니라 더 빠른 혼란이 됩니다.

이 글은 MLOps 101 시리즈의 8번째 글입니다.

여기서는 재학습을 단순 재실행이 아니라, 명시적 트리거와 챔피언-챌린저 비교를 거쳐 승격 여부를 판단하는 운영 루프로 보겠습니다.


![MLOps 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/08/08-01-see-the-flow-first.ko.png)
*MLOps 101 8장 흐름 개요*
> 되돌림 발동은 늨른 정진로, 결부부 되돌림은 랜덴 노아웰단 모델 뽄석기단 다른 거라임을 브랈동기 를미긴 되어브단 람닝 둌삤낙 두른 를응다라는 시스템도 나냈음단 중실단반듰 개닱옉답니다.

## 먼저 던지는 질문

- 언제 재학습해야 하는지를 어떤 신호로 정할 수 있을까요?
- 일정 기반, 드리프트 기반, 성능 기반 트리거는 어떻게 다를까요?
- 챔피언과 챌린저를 비교할 때 왜 마진이 필요할까요?

## 왜 중요한가

재학습이 없으면 모델은 서서히 낡아 갑니다. 하지만 재학습이 자동이라고 해서 무조건 좋은 것도 아닙니다. 기준 없이 자주 재학습하면 작은 잡음에도 모델이 계속 바뀌고, 운영 안정성은 오히려 나빠질 수 있습니다.

그래서 중요한 것은 자동 실행 자체보다 정책입니다. 어떤 신호가 들어오면 학습을 다시 시작하고, 새 모델이 기존 챔피언보다 얼마나 좋아야 승격하는지, 실패하면 어떻게 되돌아갈지를 먼저 정해야 합니다.

---

## 전체 흐름을 먼저 보겠습니다

이 구조는 재학습을 잘 설명합니다. 어떤 트리거가 발생하면 챌린저 모델을 학습하고, 평가하고, 현재 챔피언과 비교하고, 마지막에 승격하거나 반려합니다. 즉, 재학습은 학습만이 아니라 비교와 승격 정책을 함께 포함한 루프입니다.

---

## 먼저 잡아야 할 핵심 개념

- 챔피언: 현재 프로덕션에 올라가 있는 모델입니다.
- 챌린저: 새로 학습된 후보 모델입니다.
- **섀도우 평가**: 실제 트래픽이나 운영 데이터로 병렬 평가만 하고 결과는 사용자에게 반영하지 않는 방식입니다.
- 승격: 챌린저를 새 챔피언으로 바꾸는 결정입니다.
- **히스테리시스**: 작은 우연한 차이로 모델이 자주 바뀌지 않도록 두는 완충 마진입니다.

재학습을 운영 가능한 체계로 만들려면 이 개념 다섯 개를 먼저 분리해서 봐야 합니다.

---

## 도입 전과 도입 후를 비교해 보겠습니다

**Before**: 분기마다 한 번씩 감으로 재학습하고 근거는 약합니다.

**After**: 드리프트 경고나 성능 저하가 감지되면 야간 재학습이 돌고, 챔피언과 비교한 뒤 승격 여부를 결정합니다.

Before 상태에서는 왜 교체했는지 설명이 어렵습니다. After 상태에서는 트리거와 비교 근거가 모두 남습니다.

---

## ML A/B 테스트 vs 전통적 A/B

재학습한 모델을 배포하기 전에 A/B 테스트로 성능을 검증할 수 있습니다. 하지만 ML A/B 테스트는 웹 UI A/B 테스트와 몇 가지 차이가 있습니다.

| 차원 | 웹 A/B 테스트 | ML A/B 테스트 |
|---|---|---|
| 메트릭 | 클릭률, 전환율 | 정확도, AUC, 지연 시간 |
| 관찰 기간 | 1-2주 | 2-4주 (라벨 지연) |
| 표본 크기 | 클릭 모수로 결정 | 모델 예측 모수 + 라벨 수집 지연 |
| 통계 검정 | Z-test, Chi-square | Paired t-test, Wilcoxon |

가장 큰 차이는 라벨 지연입니다. 웹 A/B는 클릭 여부가 즉시 관찰되지만, ML은 예측 후 며칠 또는 몇 주 후에야 정답이 확정되는 경우가 많습니다. 그래서 A/B 기간이 길어지고, 표본 크기 계산도 달라집니다.

---

## Python으로 A/B 결과 통계 분석

A/B 테스트 결과를 통계적으로 분석하려면 paired t-test나 Wilcoxon 검정을 쓸 수 있습니다. 아래 코드는 두 모델의 정확도를 비교하는 최소 예시입니다.

```python
import numpy as np
from scipy.stats import ttest_rel

# A: 챔피언, B: 챌린저
champion_acc = np.array([0.82, 0.83, 0.81, 0.84, 0.82])
challenger_acc = np.array([0.84, 0.85, 0.83, 0.86, 0.84])

stat, p = ttest_rel(champion_acc, challenger_acc)
print(f"t-statistic: {stat:.3f}, p-value: {p:.4f}")

if p < 0.05:
    print("Challenger is significantly better.")
else:
    print("No significant difference.")
```

이 코드는 paired t-test를 사용해 두 모델의 정확도 차이가 통계적으로 유의미한지 확인합니다. p-value가 0.05 미만이면 챌린저가 유의미하게 더 좋다고 판단합니다. 이 방법은 우연한 차이로 모델을 교체하는 실수를 줄여 줍니다.

---

## 카나리 배포로 모델 검증

새 모델을 전체 트래픽에 바로 적용하면 위험이 큽니다. 카나리 배포는 일부 트래픽(5-10%)에만 먼저 적용하고, 문제가 없으면 점진적으로 확대하는 방식입니다.

카나리 배포의 핵심 단계는 다음과 같습니다.

1. 새 모델을 5% 트래픽에만 적용합니다.
2. 1-2시간 동안 지연 시간, 오류율, 예측 분포를 모니터링합니다.
3. 문제가 없으면 20%, 50%, 100%로 확대합니다.
4. 이상 징후가 보이면 즉시 롤백합니다.

이 방식은 전체 사용자에게 영향을 주기 전에 실제 환경에서 모델을 검증하게 해 줍니다. 특히 지연 시간이나 오류율 같은 운영 메트릭은 오프라인 평가에서 보이지 않던 문제를 드러낼 수 있습니다.

---

## 밴딧 알고리즘 간단 소개

카나리와 A/B는 정적 비율 할당을 사용하지만, 밴딧 알고리즘은 성능을 관찰하면서 트래픽 비율을 동적으로 조정합니다. 성능이 좋은 모델에 더 많은 트래픽을 보내고, 나쁜 모델에는 적게 보냅니다.

대표적인 방법은 다음과 같습니다.

- **Epsilon-Greedy**: 확률 ε로 탐색, 1-ε로 최선 모델 선택
- **Thompson Sampling**: 베이지안 확률로 모델 선택
- **UCB (Upper Confidence Bound)**: 신뢰 구간 상한을 기준으로 선택

밴딧은 모델 성능이 불분명하거나, 사용자 그룹별로 성능이 다를 때 유용합니다. 하지만 라벨 지연이 큰 ML 시스템에서는 피드백이 느려 효과가 제한적일 수 있습니다. 따라서 재학습 초기에는 고정 비율 A/B나 카나리가 더 안전한 선택입니다.

---

## 아주 작은 재학습 루프를 만들어 보겠습니다

### 1단계 — 트리거 정책을 정의합니다

```python
def should_retrain(psi: float, accuracy: float, days_since: int):
    if psi > 0.2:
        return "drift"
    if accuracy < 0.7:
        return "performance"
    if days_since >= 30:
        return "schedule"
    return None
```

이 함수는 재학습의 출발점을 명시적으로 보여 줍니다. 트리거가 코드로 드러나면 팀이 같은 기준으로 움직일 수 있고, 나중에 기준을 조정하기도 쉬워집니다.

### 2단계 — 챌린저를 학습합니다

```python
from sklearn.linear_model import LogisticRegression

def train_challenger(X, y):
    return LogisticRegression().fit(X, y)
```

재학습의 목적은 새 후보를 만드는 것입니다. 이 단계는 단순해 보여도, 운영적으로는 기존 챔피언과 분리된 새 아티팩트를 생성한다는 의미가 있습니다.

### 3단계 — 평가하고 비교합니다

```python
def evaluate(model, X, y):
    return float(model.score(X, y))

def compare(challenger_acc, champion_acc, margin=0.01):
    return challenger_acc >= champion_acc + margin
```

여기서 `margin`이 중요합니다. 0.001 차이처럼 우연에 가까운 개선으로 모델을 계속 바꾸면 운영이 불안정해집니다. 재학습에서는 승부보다 안정성이 더 중요할 때가 많습니다.

### 4단계 — 섀도우 평가를 합니다

```python
def shadow(challenger, X_live, y_live):
    return evaluate(challenger, X_live, y_live)
```

섀도우 평가는 사용자에게 영향을 주지 않고 새 모델을 검증하게 해 줍니다. 운영 데이터로 비교하되 실제 응답에는 반영하지 않으므로 위험이 작습니다.

### 5단계 — 승격 여부를 결정합니다

```python
def promote_decision(reason, challenger_acc, champion_acc):
    if reason is None:
        return "skip"
    if compare(challenger_acc, champion_acc):
        return "promote"
    return "reject"

print(promote_decision("drift", 0.82, 0.80))
```

이 단계가 재학습을 운영 체계로 만듭니다. 트리거가 생겼다고 무조건 승격하는 것이 아니라, 비교 규칙을 통과했을 때만 다음 단계로 넘어갑니다.

---

## 이 코드에서 먼저 봐야 할 점

- 트리거는 사람 감각이 아니라 명시적 규칙으로 두어야 합니다.
- 비교 마진이 있어야 모델 교체가 너무 잦아지지 않습니다.
- 섀도우 평가는 낮은 위험으로 검증 범위를 넓혀 줍니다.
- 재학습과 승격은 분리된 결정입니다.

좋은 재학습 체계는 자주 돌리는 체계가 아니라, 어떤 조건에서 무엇을 비교하고 왜 교체했는지 설명할 수 있는 체계입니다.

---

## 자주 헷갈리는 지점

1. **챔피언 모델을 보존하지 않습니다.**
   롤백이 불가능해집니다.
2. **섀도우 단계 없이 바로 프로덕션으로 올립니다.**
   새 모델의 운영 리스크를 너무 빨리 떠안게 됩니다.
3. **마진을 0으로 둡니다.**
   미세한 차이로 계속 교체되는 현상이 생깁니다.
4. **재학습 중에 새 피처까지 같이 넣습니다.**
   성능 변화 원인을 분리하기 어려워집니다.
5. **성공한 재학습만 기록하고 실패는 묻어 둡니다.**
   학습 루프에서 중요한 교훈이 사라집니다.

## 재학습 비용 추정

재학습은 공짜가 아닙니다. 학습 시간, 컴퓨팅 비용, 데이터 로드 비용이 모두 생깁니다. 특히 대규모 모델을 매일 재학습하면 비용이 빠르게 커집니다.

비용 추정 예시:

- 학습 1회: GPU 4시간 = $8 (AWS p3.2xlarge 기준)
- 매일 재학습: $8 × 30일 = $240/월
- 매주 재학습: $8 × 4회 = $32/월
- 드리프트 트리거: 불규칙, 월 1-3회 예상 = $8-24/월

그래서 재학습 빈도는 비용과 모델 성능 개선 사이의 균형입니다. 모델이 빠르게 낙하는 분야는 자주 돌려야 하고, 안정적인 분야는 드리프트 트리거로 충분합니다.

---

## 재학습 실패 처리

재학습이 항상 성공하는 것은 아닙니다. 데이터 파일 손상, 메모리 부족, 타임아웃 등으로 실패할 수 있습니다. 실패했을 때 처리 정책을 미리 정해야 합니다.

```python
def handle_failure(reason: str):
    if reason == "data_missing":
        return "skip_and_alert"
    if reason == "oom":
        return "retry_with_smaller_batch"
    if reason == "timeout":
        return "retry_once"
    return "alert_and_stop"
```

이 함수는 실패 종류에 따라 다른 대응을 합니다. 데이터 누락은 건너뛰고 경고를 보내고, OOM은 배치 크기를 줄여 재시도하고, 타임아웃은 한 번 더 시도합니다. 중요한 것은 실패를 조용히 묻지 않는 것입니다.

---
---

## 실무에서는 이렇게 봅니다

추천 모델은 야간 재학습으로 새 챌린저를 만들고, AUC나 CTR을 챔피언과 비교한 뒤, 기준을 넘기면 카나리로 일부 트래픽에만 먼저 적용하는 식의 운영이 흔합니다. 재학습 성공이 곧바로 전체 배포 성공을 뜻하지는 않습니다.

시니어 엔지니어는 재학습을 배포 자동화의 하위 기능으로 보지 않습니다. 비교 기준을 먼저 합의하고, 챔피언을 항상 남겨 두고, 변경은 한 번에 하나씩만 넣는 방식으로 운영 안정성을 우선합니다.

---

## 체크리스트

- [ ] 트리거 정책이 문서화되어 있다.
- [ ] 챌린저 평가가 자동으로 실행된다.
- [ ] 승격 마진이 정의되어 있다.
- [ ] 롤백 절차가 있다.

## 연습 문제

1. 모델 교체가 너무 잦지 않도록 최소 안정 기간 규칙을 설계해 보세요.
2. 섀도우 결과가 나쁘게 나왔을 때 어떤 데이터부터 점검할지 적어 보세요.
3. 두 모델이 비슷하게 나오면 왜 챔피언 유지가 기본값이어야 하는지 설명해 보세요.

## 정리

재학습은 모델을 자동으로 다시 돌리는 기능이 아니라, 명시적 신호를 받아 새 후보를 만들고 챔피언과 비교해 승격 여부를 판단하는 운영 루프입니다.

이 글에서 기억할 핵심은 하나입니다. **재학습이 자동이어도 승격은 항상 근거 기반이어야 합니다.** 다음 글에서는 학습과 서빙에서 같은 피처를 쓰기 위한 피처 스토어를 다루겠습니다.


## 재학습 트리거 정책을 코드로 고정하기

재학습 자동화는 트리거 규칙이 명시적일 때만 안전합니다. 아래는 다중 신호를 결합하는 예시입니다.

```python
from dataclasses import dataclass


@dataclass
class RetrainSignals:
    psi: float
    val_auc: float
    days_since_train: int
    new_rows: int


def retrain_reason(s: RetrainSignals) -> str | None:
    if s.psi >= 0.2:
        return "drift"
    if s.val_auc <= 0.80:
        return "performance"
    if s.days_since_train >= 30:
        return "time"
    if s.new_rows >= 200000:
        return "data_volume"
    return None
```

신호 우선순위를 코드로 정해 두면, 같은 상황에서 팀이 서로 다른 판단을 내리는 문제를 줄일 수 있습니다.

## 스케줄러 설정 예시

```yaml
retraining_job:
  schedule: "0 3 * * *"
  timezone: "Asia/Seoul"
  max_active_runs: 1
  retries: 1

quality_gate:
  min_auc: 0.82
  min_pr_auc: 0.35
  max_p99_latency_ms: 120

promotion:
  stage_from: Staging
  stage_to: Production
  margin_auc: 0.01
  require_shadow_pass: true
```

## 모델 레지스트리 워크플로

| 단계 | 수행 작업 | 산출물 |
|---|---|---|
| Train | 챌린저 학습 | 모델 아티팩트 |
| Evaluate | 챔피언 대비 성능 비교 | 비교 리포트 |
| Shadow | 실제 트래픽 병렬 평가 | 운영 메트릭 리포트 |
| Approve | 리뷰어 승인 | 승격 기록 |
| Promote | Production 전환 | 새 챔피언 버전 |

이 단계가 분리되어 있어야 재학습 성공과 운영 승격을 구분할 수 있습니다.

## 승격 결정 코드 예시

```python
def should_promote(champion_auc: float, challenger_auc: float, margin: float = 0.01) -> bool:
    return challenger_auc >= champion_auc + margin


def final_decision(reason: str | None, shadow_ok: bool, champion_auc: float, challenger_auc: float) -> str:
    if reason is None:
        return "skip"
    if not shadow_ok:
        return "reject"
    if should_promote(champion_auc, challenger_auc):
        return "promote"
    return "reject"
```

## 운영 체크포인트

- 트리거 발생 사유를 로그와 티켓에 남깁니다.
- 재학습 실패도 성공과 동일하게 기록합니다.
- 승격 기준은 숫자와 기간을 함께 정의합니다.
- 최소 안정 기간을 두어 잦은 교체를 방지합니다.

재학습 자동화의 목적은 빠른 교체가 아니라 일관된 품질 유지입니다.

## 재학습 트리거 오케스트레이션 예시

운영에서는 트리거 판단, 잡 생성, 평가 리포트 저장을 분리하는 편이 안정적입니다. 아래 코드는 트리거 판단과 실행 요청 페이로드 생성을 분리한 예시입니다.

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class MetricsSnapshot:
    psi: float
    auc: float
    baseline_auc: float
    days_since_train: int


def decide_trigger(m: MetricsSnapshot) -> str | None:
    if m.psi >= 0.25:
        return "drift"
    if m.auc <= m.baseline_auc - 0.03:
        return "performance"
    if m.days_since_train >= 30:
        return "schedule"
    return None


def build_retrain_request(model_name: str, trigger: str, data_version: str) -> dict:
    return {
        "model": model_name,
        "trigger": trigger,
        "data_version": data_version,
        "requested_at": datetime.utcnow().isoformat() + "Z",
        "require_shadow": True,
    }
```

핵심은 `decide_trigger`와 `build_retrain_request`를 분리해 재학습 근거와 실행 파라미터를 감사 가능하게 남기는 것입니다.

## 스케줄러 실행 정책 YAML

```yaml
workflow:
  name: retraining-nightly
  cron: "0 2 * * *"
  timezone: "Asia/Seoul"

policy:
  trigger_priority:
    - drift
    - performance
    - schedule
  min_days_between_promotions: 7
  max_parallel_retrains: 1

quality_gate:
  min_auc_gain: 0.01
  max_p95_latency_ms: 100
  require_shadow_pass: true

notifications:
  on_success: "#mlops-release"
  on_failure: "#mlops-oncall"
```

스케줄러 설정은 단순 실행 시간이 아니라, 승격 간 최소 간격과 품질 게이트까지 함께 정의해야 운영 안정성을 유지할 수 있습니다.


## A/B 테스트로 재학습 모델 검증하기

재학습한 모델이 기존 모델보다 정말 나은지 확인하려면 A/B 테스트가 필요합니다. 오프라인 메트릭(AUC, RMSE)이 좋아도 온라인 비즈니스 지표(전환율, 매출)가 나빠질 수 있기 때문입니다.

```python
import hashlib
from dataclasses import dataclass


@dataclass
class ABConfig:
    experiment_name: str
    control_model: str      # 기존 모델 버전
    treatment_model: str    # 재학습 모델 버전
    traffic_split: float    # treatment 비율 (0.0 ~ 1.0)


def assign_variant(user_id: str, config: ABConfig) -> str:
    """사용자를 deterministic하게 control/treatment에 배정합니다."""
    hash_input = f"{config.experiment_name}:{user_id}"
    hash_value = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)
    bucket = (hash_value % 1000) / 1000.0
    return "treatment" if bucket < config.traffic_split else "control"


def route_prediction(user_id: str, features: dict, config: ABConfig):
    """배정된 variant에 따라 해당 모델로 추론을 라우팅합니다."""
    variant = assign_variant(user_id, config)
    if variant == "treatment":
        prediction = predict_with_model(config.treatment_model, features)
    else:
        prediction = predict_with_model(config.control_model, features)
    log_ab_event(user_id, variant, prediction, config.experiment_name)
    return prediction
```

핵심은 `assign_variant`가 deterministic이라는 점입니다. 같은 사용자는 실험 기간 동안 항상 같은 그룹에 속하므로, 결과가 일관됩니다.

## 통계적 유의성 판단

A/B 테스트 결과를 판단할 때는 충분한 샘플이 모여야 합니다. 너무 일찍 판단하면 잘못된 결론을 내립니다.

```python
from scipy import stats
import numpy as np


def evaluate_ab_test(
    control_conversions: int,
    control_total: int,
    treatment_conversions: int,
    treatment_total: int,
    significance_level: float = 0.05,
) -> dict:
    """두 그룹의 전환율 차이를 검정합니다."""
    control_rate = control_conversions / control_total
    treatment_rate = treatment_conversions / treatment_total

    # 이항 비율의 z-검정
    pooled_rate = (control_conversions + treatment_conversions) / (
        control_total + treatment_total
    )
    se = np.sqrt(
        pooled_rate * (1 - pooled_rate) * (1 / control_total + 1 / treatment_total)
    )
    z_stat = (treatment_rate - control_rate) / se if se > 0 else 0.0
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

    return {
        "control_rate": control_rate,
        "treatment_rate": treatment_rate,
        "lift": (treatment_rate - control_rate) / control_rate if control_rate > 0 else 0,
        "z_statistic": z_stat,
        "p_value": p_value,
        "is_significant": p_value < significance_level,
        "recommendation": (
            "deploy_treatment" if p_value < significance_level and treatment_rate > control_rate
            else "keep_control"
        ),
    }
```

`recommendation`이 `"deploy_treatment"`이면 재학습 모델을 Production 스테이지로 승격합니다. 그렇지 않으면 기존 모델을 유지하고, 왜 재학습이 효과가 없었는지 원인을 분석합니다. 흔한 원인은 학습 데이터와 서빙 데이터의 분포 차이, 레이블 노이즈, 특성 엔지니어링 오류입니다.

## 재학습 주기 결정 기준

재학습 주기를 어떻게 잡을지는 도메인과 데이터 변화 속도에 따라 다릅니다.

| 도메인 | 데이터 변화 속도 | 권장 주기 | 트리거 |
| --- | --- | --- | --- |
| 사기 탐지 | 빠름 (일 단위) | 매일~매주 | 드리프트 감지 |
| 추천 시스템 | 중간 (주 단위) | 매주 | 정기 스케줄 |
| 수요 예측 | 계절성 | 월간~분기 | 성능 하락 |
| 의료 영상 | 느림 | 분기~연간 | 새 데이터셋 확보 시 |

정기 스케줄과 이벤트 트리거를 함께 사용하는 것이 가장 안정적입니다. 정기 재학습으로 점진적 변화를 따라가고, 드리프트 알림으로 급격한 변화에 대응합니다.

## 처음 질문으로 돌아가기

- **언제 재학습해야 하는지를 어떤 신호로 정할 수 있을까요?**
  - 본문의 기준은 재학습를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **일정 기반, 드리프트 기반, 성능 기반 트리거는 어떻게 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **챔피언과 챌린저를 비교할 때 왜 마진이 필요할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [MLOps 101 (1/10): MLOps란 무엇인가?](./01-what-is-mlops.md)
- [MLOps 101 (2/10): 실험 관리](./02-experiment-tracking.md)
- [MLOps 101 (3/10): 데이터 버전 관리](./03-data-versioning.md)
- [MLOps 101 (4/10): 모델 학습 파이프라인](./04-training-pipeline.md)
- [MLOps 101 (5/10): 모델 배포](./05-model-deployment.md)
- [MLOps 101 (6/10): 모델 모니터링](./06-model-monitoring.md)
- [MLOps 101 (7/10): 데이터 드리프트와 모델 드리프트](./07-data-and-model-drift.md)
- **재학습 (현재 글)**
- 피처 스토어 (예정)
- 운영 가능한 ML 시스템 (예정)

<!-- toc:end -->

## 참고 자료

- [예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/mlops-101/ko)

- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)
- [Google — continuous training](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
- [Uber — Michelangelo](https://www.uber.com/blog/michelangelo-machine-learning-platform/)
- [Netflix Tech Blog](https://netflixtechblog.com/)

Tags: MLOps, Retraining, Automation, Pipeline, DataScience
