---
series: mlops-101
episode: 7
title: "MLOps 101 (7/10): 데이터 드리프트와 모델 드리프트"
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
  - Drift
  - Monitoring
  - DataScience
  - Statistics
seo_description: 데이터 드리프트와 모델 드리프트를 구분하여 감지하고, PSI와 KS 검정을 활용해 재학습 시점을 결정하는 운영 체계를 소개합니다.
last_reviewed: '2026-05-12'
---

# MLOps 101 (7/10): 데이터 드리프트와 모델 드리프트

운영 중인 모델이 예전 같지 않다고 느껴질 때, 원인은 하나가 아닙니다. 입력 데이터 분포가 바뀌었을 수도 있고, 입력은 비슷한데 레이블과의 관계가 바뀌어 모델이 덜 맞기 시작했을 수도 있습니다. 둘을 구분하지 않으면 대응도 자꾸 헛짚게 됩니다.

많은 팀이 정확도 하락 하나만 보고 뒤늦게 문제를 인지합니다. 하지만 실제 현장에서는 입력 분포 변화가 먼저 나타나고, 그다음에야 비즈니스 손실이나 성능 저하가 보이는 경우가 많습니다.

여기서는 데이터 드리프트와 모델 드리프트를 분리해서 이해하고, PSI와 KS 같은 통계 도구를 어떻게 운영 경보로 연결할지 봅니다.

![MLOps 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/07/07-01-see-the-flow-first.ko.png)
*MLOps 101 7장 흐름 개요*
> 드리프트 감지의 핵심은 남는 메타데이터를 검증 가능한 운영 신호로 되돌릴 수 있다는 사실입니다. 예를 들면 예측 분포 이동, 스코어 변화, 입력 특성 변화가 모두 되돌림 신호로 나타날 수 있습니다.

## 먼저 던지는 질문

- 데이터 드리프트와 모델 드리프트는 무엇이 다를까요?
- 왜 기준 분포를 잘못 잡으면 드리프트가 안 보이게 될까요?
- PSI와 KS 검정은 어떤 상황에서 유용할까요?

## 왜 중요한가

세상은 멈추지 않습니다. 사용자 행동도, 계절성도, 정책도, 수집 방식도 계속 바뀝니다. 학습 시점에는 정상적이던 분포가 한 달 뒤에도 그대로 유지된다고 가정하는 순간 운영 모델은 서서히 낡기 시작합니다.

드리프트 감지가 없으면 손실은 조용히 쌓입니다. 그리고 나서야 정확도 하락이나 비즈니스 이상 신호가 눈에 들어옵니다. 조기 경보가 필요한 이유가 바로 여기에 있습니다.

---

## 전체 흐름을 먼저 보겠습니다

이 그림은 드리프트 감지의 핵심을 단순하게 보여 줍니다. 학습 시점 분포를 기준선으로 잡고, 운영 중에 들어오는 현재 분포와 통계적으로 비교한 뒤, 차이가 일정 수준을 넘으면 경고를 내보냅니다.

여기서 가장 중요한 선택은 기준선을 무엇으로 둘지입니다. 기준선이 흔들리면 드리프트 감지 자체가 흐려집니다.

---

## 먼저 잡아야 할 핵심 개념

- **데이터 드리프트**: 입력 X의 분포가 달라지는 현상입니다.
- **개념 드리프트**: X와 Y의 관계 자체가 달라지는 현상입니다.
- **PSI**: 분포 안정성을 보는 지표로, 보통 0.1 이하면 안정, 0.2 이상이면 주의 신호로 많이 봅니다.
- **KS 검정**: 두 연속 분포의 차이를 수치로 비교하는 방법입니다.
- 기준선: 대개 학습 데이터나 검증된 기준 기간의 분포입니다.

이 다섯 개를 분리해서 이해해야 경고가 떴을 때 무엇이 바뀐 것인지 더 빠르게 해석할 수 있습니다.

---

## 도입 전과 도입 후를 비교해 보겠습니다

**Before**: 비즈니스 손실이 실제로 발생한 뒤에야 정확도 하락을 알아챕니다.

**After**: PSI가 임계값을 넘는 순간 먼저 조사와 재학습 검토가 시작됩니다.

Before 상태에서는 문제 인지가 늦고 원인도 모호합니다. After 상태에서는 적어도 입력 분포 변화가 먼저 경고로 드러납니다.

---

## 모델 레지스트리 기능 비교

드리프트를 감지한 다음에는 재학습하고, 새 모델을 등록하고, 버전 간 비교가 필요합니다. 아래 표는 대표적인 모델 레지스트리 도구를 버전 관리, 스테이지 전환, 메타데이터, 접근 제어 기능으로 비교합니다.

| 기능 | MLflow | Vertex AI Model Registry | SageMaker Model Registry |
|---|---|---|---|
| 버전 관리 | 자동 버전 번호 | 수동 + 자동 | 자동 버전 번호 |
| 스테이지 전환 | Staging → Production | Undeployed → Deployed | Pending → Approved |
| 메타데이터 | 태그, 설명, 링크 | 라벨, 설명 | 메타데이터 key-value |
| 접근 제어 | 파일 기반 | IAM | IAM |

MLflow는 로컬 개발부터 클라우드까지 일관되게 쓸 수 있고, Vertex AI와 SageMaker는 각각 GCP, AWS 생태계와 깊게 통합됩니다. 선택 기준은 클라우드 벤더 종속성, 팀 규모, 거버넝스 요구사항입니다.

---

## MLflow로 모델 등록과 스테이지 전환 예시

드리프트가 감지된 후 새 모델을 학습하고 등록하면, 그 모델을 Staging으로 올리고 검증한 뒤 Production으로 승격시킬 수 있습니다.

```python
import mlflow
from mlflow.tracking import MlflowClient

# 1. 모델 등록
mlflow.set_tracking_uri("http://localhost:5000")
with mlflow.start_run():
    mlflow.log_param("alpha", 0.5)
    mlflow.log_metric("accuracy", 0.92)
    mlflow.sklearn.log_model(model, "model")

# 2. 레지스트리에 등록
client = MlflowClient()
model_uri = "runs:/<run_id>/model"
mv = mlflow.register_model(model_uri, "risk_model")

# 3. Staging으로 전환
client.transition_model_version_stage(
    name="risk_model",
    version=mv.version,
    stage="Staging",
)

# 4. 검증 후 Production으로 승격
client.transition_model_version_stage(
    name="risk_model",
    version=mv.version,
    stage="Production",
)
```

이 흐름에서 중요한 점은 Staging 단계를 건너뛰지 않는 것입니다. Production으로 바로 올리면 검증 없이 배포되어, 드리프트보다 더 큰 성능 저하가 생길 수 있습니다.

---

## 모델 거버넝스

드리프트 감지와 재학습이 자동화되면, 모델 버전이 빠르게 쌓입니다. 이때 거버넝스 체계가 없으면 어떤 모델이 언제 누구에 의해 승인되어 배포되었는지 추적하기 어려워집니다.

모델 거버넝스의 핵심 요소는 다음과 같습니다.

1. **승인 프로세스**: Production 승격에 리뷰어를 둡니다.
2. **감사 로그**: 누가 언제 모델을 승격했는지 기록합니다.
3. **링크**: 모델 버전과 학습 런, 데이터 버전을 연결합니다.
4. **보유 기간**: 오래된 모델 버전을 언제 삭제할지 정책을 둡니다.

거버넝스 없이 자동화만 하면, 모델 버전이 무늘려나고 문제가 생겨도 원인을 찾기 어렵습니다. 거버넝스는 자동화를 안전하게 만드는 제동 장치입니다.

---

## PSI로 드리프트를 감지해 보겠습니다

### 1단계 — 기준 데이터와 현재 데이터를 준비합니다

```python
import numpy as np

base = np.random.normal(0, 1, 1000)
live = np.random.normal(0.5, 1, 1000)
```

이 예제는 기준 분포와 현재 분포가 살짝 어긋난 상황을 가정합니다. 실제 서비스에서는 학습 데이터와 최근 운영 입력이 이 역할을 합니다.

### 2단계 — 구간 경계를 만듭니다

```python
def bin_edges(x, n=10):
    return np.quantile(x, np.linspace(0, 1, n + 1))
```

PSI는 분포를 구간으로 나누어 비교하기 때문에 경계 선택이 중요합니다. 기준선 쪽 분위수를 사용하면 현재 분포와 비교할 기준 프레임을 고정할 수 있습니다.

### 3단계 — PSI를 계산합니다

```python
def psi(base, live, n=10):
    edges = bin_edges(base, n)
    edges[0], edges[-1] = -np.inf, np.inf
    b, _ = np.histogram(base, edges)
    l, _ = np.histogram(live, edges)
    bp = b / b.sum() + 1e-6
    lp = l / l.sum() + 1e-6
    return float(np.sum((lp - bp) * np.log(lp / bp)))

print(round(psi(base, live), 3))
```

`+ 1e-6` 같은 작은 보정이 왜 들어가는지 꼭 봐야 합니다. 실제 운영 데이터에서는 특정 구간 빈도가 0이 될 수 있고, 그때 0 나눗셈이 생기면 계산 자체가 깨집니다.

### 4단계 — KS 검정도 함께 봅니다

```python
from scipy.stats import ks_2samp
stat, p = ks_2samp(base, live)
print(round(stat, 3), round(p, 4))
```

KS 검정은 두 분포 차이를 하나의 통계량으로 줄여 줍니다. PSI와 KS를 같이 보면 구간 기반 변화와 전체 분포 차이를 함께 읽을 수 있습니다.

### 5단계 — 운영용 정책으로 바꿉니다

```python
def status(p_value, psi_value):
    if psi_value > 0.2 or p_value < 0.01:
        return "drift"
    if psi_value > 0.1:
        return "watch"
    return "ok"
```

통계량이 나왔다고 바로 운영 판단이 끝나지는 않습니다. 결국 팀은 어떤 수준에서 조사하고, 어떤 수준에서 재학습 큐에 넣을지 규칙으로 정해야 합니다.

---

## 이 코드에서 먼저 봐야 할 점

- 작은 보정값은 수치 안정성을 지켜 줍니다.
- KS는 분포 차이를 한 숫자로 요약합니다.
- PSI와 KS는 신호일 뿐이고, 최종 판단은 정책이 결정합니다.
- 기준선과 임계값은 팀의 운영 계약입니다.

좋은 드리프트 감지는 통계 기법보다 운영 연결이 더 중요합니다. 경고가 떠도 다음 행동이 정해져 있지 않으면 숫자만 늘어날 뿐입니다.

---

## 자주 헷갈리는 지점

1. **기준선을 최근 며칠 데이터로 둡니다.**
   분포가 함께 움직여 드리프트가 잘 안 보입니다.
2. **라벨 없이 개념 드리프트를 단정합니다.**
   입력 변화와 성능 저하를 섞어 보게 됩니다.
3. **개별 피처만 보고 다변량 변화를 놓칩니다.**
   실제 문제는 피처 조합에서 생길 수 있습니다.
4. **범주형이나 경계형 피처에 KS를 그대로 씁니다.**
   특성에 맞는 지표 선택이 필요합니다.
5. **알림만 만들고 재학습 흐름과 연결하지 않습니다.**
   경고가 있어도 운영 루프가 닫히지 않습니다.

## 대규모 데이터에서 드리프트 감지 최적화

데이터가 커지면 모든 피처에 대해 PSI를 계산하는 비용이 커집니다. 이 경우 우선순위를 정해야 합니다.

1. **핵심 피처**: 모델 성능에 가장 큰 영향을 주는 5-10개 피처를 먼저 감시합니다.
2. **샘플링**: 전체 데이터가 아니라 대표 샘플로 PSI를 계산합니다.
3. **주기 조정**: 매시간 대신 매일 또는 매주 검사합니다.
4. **증분 계산**: 전체 데이터를 다시 읽지 않고, 새 데이터에 대해서만 PSI를 계산하고 이전 결과와 합칩니다.

크기가 커지면 효율이 중요해집니다. 하지만 효율보다 민감도가 더 중요한 피처는 샘플링하지 말고 전체를 다 검사해야 합니다.

---

## 드리프트 감지 후 재학습 트리거

드리프트를 감지했다고 무조건 재학습하는 것은 아닙니다. 드리프트가 실제 성능 저하로 이어지는지 확인해야 합니다.

```python
def should_retrain(psi: float, recent_accuracy: float, baseline_accuracy: float):
    if psi > 0.2 and recent_accuracy < baseline_accuracy - 0.05:
        return True
    if psi > 0.3:
        return True
    return False
```

이 함수는 두 가지 조건을 봅니다. 첨째, PSI가 0.2를 넘고 정확도가 5%p 이상 떨어졌으면 재학습합니다. 둘째, PSI가 0.3을 넘으면 정확도와 무관하게 재학습합니다. 이 규칙은 팀에 맞게 조정해야 하지만, 중요한 것은 드리프트와 성능을 함께 보는 것입니다.

---

## 드리프트 감지 테스트

드리프트 감지 코드도 테스트가 필요합니다. PSI 계산식이 올바른지, 임계값이 잘 작동하는지 확인해야 합니다.

```python
import pytest
import numpy as np

def test_psi_same_distribution():
    base = np.random.normal(0, 1, 1000)
    live = np.random.normal(0, 1, 1000)
    assert psi(base, live) < 0.1

def test_psi_shifted_distribution():
    base = np.random.normal(0, 1, 1000)
    live = np.random.normal(1, 1, 1000)
    assert psi(base, live) > 0.2

def test_status_logic():
    assert status(0.001, 0.05) == "ok"
    assert status(0.001, 0.15) == "watch"
    assert status(0.001, 0.25) == "drift"
```

이 테스트는 PSI 계산이 같은 분포에서는 낮게, 다른 분포에서는 높게 나오는지 확인합니다. 또한 상태 판단 로직이 임계값을 올바르게 판단하는지 검증합니다. 드리프트 감지는 운영 코드이므로 테스트 커버리지가 중요합니다.

---
---

## 실무에서는 이렇게 봅니다

리스크 점수 모델처럼 입력 분포 변화가 바로 손실로 이어질 수 있는 분야에서는 PSI를 매일 계산하고, 일정 임계값을 넘으면 자동으로 티켓을 만들거나 재학습 후보 큐에 넣는 식의 운영이 흔합니다. 중요한 것은 드리프트 감지를 사람 눈에만 맡기지 않는 것입니다.

시니어 엔지니어는 데이터 드리프트를 조기 경보로, 모델 드리프트를 영향 확인 지표로 봅니다. 기준선은 쉽게 바꾸지 않고, 임계값은 문서화하며, 경고는 재학습 워크플로와 연결합니다.

---

## 체크리스트

- [ ] 기준 분포가 정의되어 있다.
- [ ] PSI나 KS를 주기적으로 계산한다.
- [ ] 임계값과 대응 규칙이 문서화되어 있다.
- [ ] 재학습 트리거가 경고와 연결되어 있다.

## 연습 문제

1. 범주형 피처용 PSI 함수를 직접 설계해 보세요.
2. 라벨이 늦게 들어오는 서비스에서 개념 드리프트를 어떻게 볼지 적어 보세요.
3. PSI가 0.18일 때 경고를 보낼지 감시만 할지 기준을 정해 보세요.

## 드리프트 유형 비교와 대응 우선순위

드리프트는 하나의 현상처럼 보이지만, 실제 대응은 유형마다 다릅니다.

| 유형 | 무엇이 변했는가 | 빠른 감지 지표 | 우선 대응 |
|---|---|---|---|
| 데이터 드리프트 | 입력 분포 X | PSI, KS, 결측률 | 수집/전처리 경로 점검 |
| 개념 드리프트 | X와 Y 관계 | 지연 라벨 기반 성능 하락 | 재학습 후보 생성 |
| 예측 드리프트 | 출력 분포 P(y^) | 클래스 비율 변화, 점수 분포 | 서빙 버전/입력 분포 동시 점검 |

운영에서는 데이터 드리프트를 조기 경보로, 개념 드리프트를 영향 확인 신호로 함께 보는 편이 효과적입니다.

## KS 검정 실전 코드

```python
import numpy as np
from scipy.stats import ks_2samp

def ks_drift(reference: np.ndarray, current: np.ndarray, alpha: float = 0.01) -> dict:
    stat, p = ks_2samp(reference, current)
    return {
        "ks_stat": float(stat),
        "p_value": float(p),
        "drift": bool(p < alpha),
    }

ref = np.random.normal(loc=0.0, scale=1.0, size=3000)
cur = np.random.normal(loc=0.25, scale=1.0, size=3000)
print(ks_drift(ref, cur))
```

KS는 연속형 피처에서 유용하지만, 범주형 피처에는 카이제곱 검정이나 Jensen-Shannon divergence 같은 대안을 검토해야 합니다.

## 피처별 드리프트 집계 예시

```python
import pandas as pd

def drift_report(df_ref: pd.DataFrame, df_cur: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for c in cols:
        out = ks_drift(df_ref[c].to_numpy(), df_cur[c].to_numpy())
        rows.append({"feature": c, **out})
    return pd.DataFrame(rows).sort_values("p_value")
```

피처 단위 보고서가 있으면 어떤 입력 경로가 먼저 흔들렸는지 빠르게 좁힐 수 있습니다.

## 드리프트 대응 런북 초안

1. 드리프트 경고 발생 시 기준선과 현재 구간을 먼저 확인합니다.
2. 수집 누락, 스키마 변경, 결측 증가 같은 데이터 경로 이상을 점검합니다.
3. 모델 예측 분포와 비즈니스 지표를 함께 확인합니다.
4. 영향이 크면 챌린저 재학습 파이프라인을 실행합니다.
5. 승격 전까지는 챔피언 모델과 비교 결과를 문서화합니다.

드리프트 감지는 통계 계산 자체보다 운영 흐름과 연결될 때 가치가 생깁니다.

## KS 검정 배치 잡 예시

운영에서는 단일 함수보다 배치 잡 형태가 더 유용합니다. 아래 예시는 기준 구간과 현재 구간을 읽어 KS 결과와 판정을 한 번에 남기는 형태입니다.

```python
from __future__ import annotations

import json
import numpy as np
from scipy.stats import ks_2samp

def evaluate_ks(reference: np.ndarray, current: np.ndarray, alpha: float = 0.01) -> dict:
    stat, p_value = ks_2samp(reference, current)
    return {
        "ks_stat": float(stat),
        "p_value": float(p_value),
        "alpha": alpha,
        "drift": bool(p_value < alpha),
    }

def run_batch(reference: np.ndarray, current: np.ndarray, feature_name: str) -> None:
    result = evaluate_ks(reference, current)
    payload = {
        "feature": feature_name,
        "sample_ref": int(reference.size),
        "sample_cur": int(current.size),
        **result,
    }
    print(json.dumps(payload, ensure_ascii=False))

if __name__ == "__main__":
    ref = np.random.normal(0.0, 1.0, 5000)
    cur = np.random.normal(0.35, 1.0, 5000)
    run_batch(ref, cur, "risk_score")
```

이 코드는 결과를 JSON 한 줄로 출력하므로, 로그 수집기나 경고 시스템과 연결하기 쉽습니다. 특히 `sample_ref`, `sample_cur`를 함께 남기면 샘플 수 부족으로 인한 오탐지를 빠르게 구분할 수 있습니다.

## 드리프트 유형별 대응 전략

| 드리프트 신호 | 1차 점검 | 2차 조치 | 재학습 여부 |
|---|---|---|---|
| PSI 급등, KS 유의 | 수집 경로/스키마 변경 확인 | 전처리 롤백 또는 결측 보정 | 조건부 |
| 예측 점수 분포 이동 | 입력 분포와 서빙 버전 동시 점검 | 서빙 설정/피처 적재 지연 복구 | 조건부 |
| 지연 라벨 성능 하락 | 라벨 품질/지연 시간 확인 | 챌린저 학습 및 오프라인 재평가 | 높음 |
| 특정 세그먼트만 악화 | 세그먼트별 샘플 수 점검 | 세그먼트 전용 임계값 재설계 | 선택적 |

운영팀은 통계량 자체보다 "경고 이후 무엇을 먼저 할지"를 표준화해야 합니다. 위 표처럼 1차 점검과 2차 조치를 분리하면, 같은 경고가 반복될 때 대응 속도와 일관성이 크게 좋아집니다.

## 다변량 드리프트 감지

단변량 검정(KS, PSI)은 특성 하나씩 비교하므로, 특성 간 상관관계가 바뀌는 경우를 놓칠 수 있습니다. 다변량 드리프트 감지는 특성 공간 전체의 분포 변화를 잡아냅니다.

```python
from alibi_detect.cd import MMDDrift
import numpy as np

# 레퍼런스 데이터: 학습 시점의 특성 분포
reference_data = np.load("reference_features.npy")  # shape: (N, D)

# MMD 기반 드리프트 감지기 초기화
drift_detector = MMDDrift(
    reference_data,
    backend="pytorch",
    p_val=0.05,
    n_permutations=100,
)

def check_multivariate_drift(new_batch: np.ndarray) -> dict:
    """새 배치 데이터에 대해 다변량 드리프트를 검정합니다."""
    result = drift_detector.predict(new_batch)
    return {
        "is_drift": bool(result["data"]["is_drift"]),
        "p_value": float(result["data"]["p_val"]),
        "threshold": 0.05,
        "distance": float(result["data"]["distance"]),
    }
```

MMD(Maximum Mean Discrepancy)는 두 분포를 커널 공간에서 비교합니다. 단변량 검정과 달리 특성 간 상호작용 변화도 감지하므로, 개별 특성은 안정적인데 조합이 바뀐 경우(예: 나이-소득 상관관계 변화)를 잡아낼 수 있습니다.

## 드리프트 감지 자동화 파이프라인

드리프트 감지를 수동으로 실행하면 놓치기 쉽습니다. 정기적으로 실행되는 파이프라인에 통합하는 것이 좋습니다.

```python
from datetime import datetime, timedelta
import json

def daily_drift_report(
    reference_path: str,
    today_data_path: str,
    output_path: str,
):
    """일일 드리프트 리포트를 생성합니다."""
    reference = np.load(reference_path)
    today = np.load(today_data_path)

    # 다변량 검정
    multi_result = check_multivariate_drift(today)

    # 단변량 검정 (각 특성별)
    from scipy.stats import ks_2samp

    univariate_results = []
    for col_idx in range(reference.shape[1]):
        stat, p_val = ks_2samp(reference[:, col_idx], today[:, col_idx])
        univariate_results.append({
            "feature_index": col_idx,
            "ks_statistic": float(stat),
            "p_value": float(p_val),
            "is_drift": p_val < 0.05,
        })

    report = {
        "date": datetime.now().isoformat(),
        "multivariate": multi_result,
        "univariate": univariate_results,
        "drifted_features": [
            r["feature_index"]
            for r in univariate_results
            if r["is_drift"]
        ],
        "recommendation": (
            "retrain" if multi_result["is_drift"] else "monitor"
        ),
    }

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    return report
```

이 리포트에서 `recommendation` 필드가 `"retrain"`이면 재학습 파이프라인을 자동으로 트리거하는 구조를 만들 수 있습니다. 다음 장(재학습)에서 이 연결 고리를 구체적으로 다루겠습니다.

## 정리

드리프트 감지는 모델이 조용히 낡아 가는 과정을 조기에 드러내는 장치입니다. 입력 분포 변화와 실제 성능 저하를 구분해서 봐야 대응도 더 정확해집니다.

이 글에서 기억할 핵심은 하나입니다. **데이터 드리프트는 먼저 오는 신호이고, 모델 드리프트는 그 신호가 만든 결과입니다.** 다음 글에서는 이 신호를 받아 실제로 모델을 다시 학습시키는 재학습 자동화를 다루겠습니다.

## 처음 질문으로 돌아가기

- **데이터 드리프트와 모델 드리프트는 무엇이 다를까요?**
  - 데이터 드리프트는 `base`와 `live`처럼 입력 X의 분포가 바뀌는 현상이고, 모델 드리프트는 그 변화나 관계 변화 때문에 실제 성능과 예측 분포가 악화된 결과입니다. 그래서 본문은 데이터 드리프트를 조기 경보로, 모델 드리프트를 영향 확인 신호로 따로 다뤘습니다.
- **왜 기준 분포를 잘못 잡으면 드리프트가 안 보이게 될까요?**
  - PSI와 KS는 결국 현재 분포를 무엇과 비교하느냐에 달려 있으므로, 기준선을 최근 며칠 데이터처럼 함께 흔들리는 값으로 두면 변화가 상쇄됩니다. 본문이 학습 시점 분포나 검증된 기준 기간을 고정선으로 두라고 한 이유가 바로 여기에 있습니다.
- **PSI와 KS 검정은 어떤 상황에서 유용할까요?**
  - PSI는 구간별 비율 변화가 얼마나 커졌는지 볼 때 유용하고, KS 검정은 연속형 피처 두 분포 차이를 `stat`과 `p_value`로 요약할 때 강합니다. 본문 예시처럼 둘을 함께 쓰면 `status()`나 재학습 조건에 연결하기 쉬워져, 단순 통계량을 실제 운영 경고로 바꿀 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [MLOps 101 (1/10): MLOps란 무엇인가?](./01-what-is-mlops.md)
- [MLOps 101 (2/10): 실험 관리](./02-experiment-tracking.md)
- [MLOps 101 (3/10): 데이터 버전 관리](./03-data-versioning.md)
- [MLOps 101 (4/10): 모델 학습 파이프라인](./04-training-pipeline.md)
- [MLOps 101 (5/10): 모델 배포](./05-model-deployment.md)
- [MLOps 101 (6/10): 모델 모니터링](./06-model-monitoring.md)
- **데이터 드리프트와 모델 드리프트 (현재 글)**
- 재학습 (예정)
- 피처 스토어 (예정)
- 운영 가능한 ML 시스템 (예정)

<!-- toc:end -->

## 참고 자료

- [예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/mlops-101/ko)

- [Evidently AI — drift detection](https://docs.evidentlyai.com/)
- [SciPy — `ks_2samp`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html)
- [Population Stability Index explained](https://www.listendata.com/2015/05/population-stability-index.html)
- [Google — Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)

Tags: MLOps, Drift, Monitoring, DataScience, Statistics
