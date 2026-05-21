---
series: mlops-101
episode: 6
title: "MLOps 101 (6/10): 모델 모니터링"
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
  - Monitoring
  - Prometheus
  - Observability
  - DataScience
seo_description: 운영 중인 모델의 지연 시간과 예측 분포를 시각화하고, 이상 징후 발생 시 즉각 대응할 수 있는 모니터링 체계 구축 방법을 소개합니다.
last_reviewed: '2026-05-12'
---

# MLOps 101 (6/10): 모델 모니터링

배포까지 끝낸 모델은 겉으로는 조용합니다. 요청도 받고 응답도 잘 주는 것처럼 보이는데, 실제로는 지연 시간이 조금씩 늘고 있거나 예측 분포가 한쪽으로 쏠리고 있을 수 있습니다. 이 단계의 문제는 대부분 사용자가 먼저 느끼기 전까지 잘 드러나지 않습니다.

그래서 모델 모니터링은 단순 운영 부가 기능이 아닙니다. 모델이 살아 있다는 사실만 확인하는 것이 아니라, 지금 이 모델이 정상적으로 예측하고 있는지, 곧 문제가 생길 조짐은 없는지를 계속 읽는 장치입니다.

이 글은 MLOps 101 시리즈의 6번째 글입니다.

여기서는 모델 모니터링을 시스템 메트릭, 모델 메트릭, 비즈니스 메트릭이 만나는 관측 계층으로 보고, Prometheus 중심의 최소 구성을 정리하겠습니다.

![MLOps 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/06/06-01-see-the-flow-first.ko.png)
*MLOps 101 6장 흐름 개요*
> 로그드 메트릭 링크가 배포 직후부터 끝답 초까지 리두머드 되기 때문에 단순한 로그 서칙 난제도 큰 문제가 된 수 있습니다.

## 먼저 던지는 질문

- 정확도만 봐서는 왜 운영 문제를 너무 늦게 알게 될까요?
- 메트릭, 로그, 트레이스는 무엇이 다를까요?
- Prometheus와 Grafana는 모델 운영에서 어떤 역할을 할까요?

## 왜 중요한가

정확도는 보통 늦게 옵니다. 라벨이 바로 생기지 않는 서비스라면 더 그렇습니다. 반면 지연 시간, 오류율, 입력 분포, 예측 클래스 분포 같은 신호는 훨씬 먼저 흔들립니다. 즉, 운영 중인 모델은 정확도 하나로만 볼 수 없습니다.

또한 모니터링이 없으면 배포는 사실상 눈 감고 운전하는 것과 비슷합니다. 문제가 생겨도 언제부터 이상했는지, 어느 버전에서 시작됐는지, 시스템 문제인지 모델 문제인지 나눌 근거가 부족해집니다.

---

## 전체 흐름을 먼저 보겠습니다

이 구성은 모델 모니터링의 가장 기본적인 형태입니다. 애플리케이션이 `/metrics` 엔드포인트로 시계열 메트릭을 노출하고, Prometheus가 주기적으로 긁어 오고, Grafana가 시각화하고, Alertmanager가 임계값을 넘는 상황을 사람에게 전달합니다.

여기서 중요한 것은 메트릭 수집이 자동이어야 한다는 점입니다. 사람 손으로 대시보드를 열어 확인하는 체계는 운영 체계가 아니라 점검 습관에 가깝습니다.

---

## 먼저 잡아야 할 핵심 개념

- 메트릭: 시간에 따라 쌓이는 숫자 시계열입니다.
- 로그: 개별 이벤트를 텍스트로 남긴 기록입니다.
- **트레이스**: 요청 하나가 여러 계층을 거치는 경로입니다.
- **SLO**: 예를 들어 99% 요청이 200ms 이내여야 한다는 목표입니다.
- 알림: 임계값을 넘었을 때 사람이나 자동화에 전달되는 신호입니다.

모니터링은 이 다섯 요소를 분리해서 이해할 때 훨씬 명확해집니다. 숫자를 계속 보는 것과, 사건을 자세히 복기하는 것은 같은 일이 아닙니다.

---

## 도입 전과 도입 후를 비교해 보겠습니다

**Before**: 사용자가 느리다고 말해야 문제를 알게 됩니다.

**After**: 지연 시간과 오류율 알림이 자동으로 팀 채널에 들어옵니다.

Before 상태에서는 장애 인지 시점이 늦고 맥락도 부족합니다. After 상태에서는 사람이 받는 첫 신호부터 어느 지표가 깨졌는지 드러납니다.

---

## 파이프라인 오케스트레이터 비교

모니터링 외에도, 실험 관리부터 배포까지 전체 흐름을 자동화하려면 오케스트레이터가 필요합니다. 아래 표는 대표적인 네 가지 도구를 학습 곡선, 확장 규모, ML 특화 정도로 비교합니다.

| 도구 | 학습 곡선 | 확장 규모 | ML 특화 | 주요 특징 |
|---|---|---|---|---|
| **Airflow** | 중간 | 대규모 | 범용 | Python DAG, 넓은 커뮤니티, 스케줄링 |
| **Prefect** | 낮음 | 중간 | 범용 | 동적 DAG, 로컬 실행 쉬움 |
| **Kubeflow** | 높음 | 대규모 | ML 특화 | Kubernetes 기반, TFX 통합 |
| **Dagster** | 중간 | 중간 | 범용 | 데이터 자산 중심, Type-safe |

선택 기준은 팀 규모, 인프라, ML 파이프라인 복잡도입니다. Airflow는 범용성이 높고 커뮤니티가 넓어 초기 도입이 안정적입니다. Kubeflow는 Kubernetes 환경에서 ML 전용 컴포넌트를 제공하지만, 초기 설정 비용이 큽니다.

---

## Airflow DAG로 모니터링 + 파이프라인 연결 예시

Airflow는 단순 스케줄링뿐 아니라, 모델 학습 → 평가 → 배포까지 순서를 보장하는 DAG를 정의할 수 있습니다. 아래 예시는 학습, 평가, 배포 단계를 연결하는 최소 파이프라인입니다.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def train():
    print("Training model...")
    # 실제 학습 로직

def evaluate():
    print("Evaluating model...")
    # 평가 로직
    return 0.92  # accuracy

def deploy():
    print("Deploying model...")
    # 배포 로직

with DAG(
    dag_id="model_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:
    t1 = PythonOperator(task_id="train", python_callable=train)
    t2 = PythonOperator(task_id="evaluate", python_callable=evaluate)
    t3 = PythonOperator(task_id="deploy", python_callable=deploy)
    t1 >> t2 >> t3
```

이 DAG는 `train` → `evaluate` → `deploy` 순서를 강제합니다. 평가 단계에서 기준을 통과하지 못하면 배포를 건너뛰도록 `BranchPythonOperator`를 쓸 수 있습니다. 또한 매일 새벽 자동 실행되므로, 재학습 루프와 결합하면 드리프트 감지 후 자동 재학습까지 연결할 수 있습니다.

---

## 파이프라인 테스트

운영 파이프라인도 테스트가 필요합니다. DAG 문법 오류, 의존성 누락, 타임아웃 설정 실수는 배포 후 첫 실행에서만 발견되기 쉽습니다. 아래는 Airflow DAG를 로컬에서 검증하는 최소 테스트 코드입니다.

```python
import pytest
from airflow.models import DagBag

def test_dag_loads():
    dagbag = DagBag(dag_folder="dags/", include_examples=False)
    assert len(dagbag.import_errors) == 0, f"DAG import errors: {dagbag.import_errors}"

def test_task_count():
    dagbag = DagBag(dag_folder="dags/", include_examples=False)
    dag = dagbag.get_dag(dag_id="model_pipeline")
    assert len(dag.tasks) == 3

def test_task_dependencies():
    dagbag = DagBag(dag_folder="dags/", include_examples=False)
    dag = dagbag.get_dag(dag_id="model_pipeline")
    train = dag.get_task("train")
    evaluate = dag.get_task("evaluate")
    assert evaluate in train.downstream_list
```

이 테스트는 DAG 파일이 문법적으로 올바른지, 예상한 개수의 태스크가 있는지, 의존 관계가 올바른지 확인합니다. CI에서 이 테스트를 돌리면 배포 전에 파이프라인 구조 오류를 잡을 수 있습니다.

---
## FastAPI 모델에 메트릭을 붙여 보겠습니다

### 1단계 — 의존성을 설치합니다

```bash
pip install prometheus-client
```

모니터링은 별도 시스템처럼 보이지만, 출발점은 애플리케이션 안에서 어떤 숫자를 밖으로 내보낼지 정하는 일입니다.

### 2단계 — 카운터와 히스토그램을 정의합니다

```python
from prometheus_client import Counter, Histogram

REQS = Counter("predict_requests_total", "total predict requests")
LAT = Histogram("predict_latency_seconds", "predict latency")
```

요청 수와 지연 시간은 가장 기본적인 운영 지표입니다. 특히 히스토그램은 평균값 하나보다 더 실전적입니다. 나중에 p95, p99 같은 분위수를 계산할 수 있기 때문입니다.

### 3단계 — FastAPI와 연결합니다

```python
import time
from fastapi import FastAPI
from prometheus_client import make_asgi_app

app = FastAPI()
app.mount("/metrics", make_asgi_app())

@app.post("/predict")
def predict(x: float):
    start = time.time()
    REQS.inc()
    result = {"prediction": int(x > 0.5)}
    LAT.observe(time.time() - start)
    return result
```

이 코드는 메트릭 수집이 요청 처리 경로 안에서 자연스럽게 이뤄지게 만듭니다. 운영 관점에서 중요한 점은 추론 코드를 따로 복잡하게 바꾸지 않아도, 관측용 신호를 함께 남길 수 있다는 것입니다.

### 4단계 — 예측 분포를 기록합니다

```python
PRED = Counter("predict_class_total", "predicted class", ["cls"])

def record(p: int):
    PRED.labels(cls=str(p)).inc()
```

시스템 메트릭만 보면 서버는 멀쩡한데 모델이 이상해지는 상황을 놓치기 쉽습니다. 예측 클래스 분포 같은 모델 고유 지표를 같이 남겨야 드리프트의 전조를 볼 수 있습니다.

### 5단계 — 알림 규칙을 둡니다

```yaml
groups:
  - name: model
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.99, rate(predict_latency_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
```

**Expected effect:** p99 지연 시간이 5분 동안 기준을 넘을 때만 경고가 올라와, 일시적인 스파이크와 실제 이상 상황을 구분할 수 있어야 합니다.

알림 규칙의 핵심은 숫자를 많이 만드는 데 있지 않습니다. 사람이 실제로 대응할 수 있는 신호만 골라 보내야 합니다. 그렇지 않으면 알람 피로가 오고, 중요한 경고도 무뎌집니다.

---

## 경고가 울리면 가장 먼저 볼 것

모니터링에서 중요한 것은 지표 수집 자체보다, 경고를 받았을 때 첫 5분 안에 무엇을 볼지 정해 두는 일입니다.

### 1단계 — 런타임 문제인지 모델 문제인지 먼저 가릅니다

```text
p95/p99 latency, error rate, request volume을 함께 봅니다.
```

지연 시간과 오류율이 같이 튀면 먼저 런타임 경로를 봐야 하고, 지연 시간은 안정적인데 예측 분포만 바뀌면 데이터/모델 쪽부터 보는 편이 맞습니다.

### 2단계 — 예측 분포가 비즈니스 지표보다 먼저 흔들렸는지 봅니다

```text
최근 클래스 분포를 직전 정상 구간과 비교합니다.
```

예측 분포가 먼저 흔들렸다면, 서빙 인프라보다 입력 분포 변화나 드리프트 가능성을 먼저 점검해야 합니다.

### 3단계 — 알림에 다음 행동 문서가 연결되어 있는지 확인합니다

```yaml
annotations:
  runbook: https://internal.example/runbooks/model-latency
```

런북 링크가 없는 알림은 상태 표시등에 가깝고, 실제 대응 도구로는 약합니다.

---

## 이 코드에서 먼저 봐야 할 점

- `/metrics` 엔드포인트를 Prometheus가 주기적으로 수집합니다.
- 히스토그램은 나중에 분위수 계산으로 이어집니다.
- 레이블을 쓰면 하나의 카운터로 여러 분포를 추적할 수 있습니다.
- 모델 메트릭이 있어야 드리프트 감지가 가능합니다.

결국 좋은 모니터링은 많이 남기는 것이 아니라, 운영 판단에 필요한 숫자를 정확한 위치에 남기는 일입니다.

---

## 자주 헷갈리는 지점

1. **CPU와 메모리만 봅니다.**
   서버는 정상인데 모델이 이상한 상황을 놓칩니다.
2. **예측 분포를 기록하지 않습니다.**
   드리프트가 조용히 지나갑니다.
3. **알림을 너무 많이 만듭니다.**
   사람이 어느 순간부터 아무 경고도 믿지 않게 됩니다.
4. **SLO 없이 임계값을 정합니다.**
   왜 그 숫자가 중요한지 팀 합의가 없습니다.
5. **대시보드나 런북이 없습니다.**
   경고를 받아도 바로 다음 행동으로 이어지지 않습니다.

---

## 실무에서는 이렇게 봅니다

결제 사기 탐지 모델처럼 지연 시간과 오탐 비용이 모두 민감한 서비스에서는 시스템 메트릭, 모델 출력 분포, 비즈니스 KPI를 함께 봅니다. 어떤 경고는 대시보드로만 보내고, 어떤 경고는 온콜을 깨울지 구분하는 것도 중요합니다.

시니어 엔지니어는 모니터링을 관찰이 아니라 대응 체계로 봅니다. 모든 알림에는 대응 문서가 붙어야 하고, 대시보드는 5초 안에 읽혀야 하며, 사람을 깨우는 경고는 반드시 행동으로 이어져야 한다고 봅니다.

---

## 체크리스트

- [ ] `/metrics` 엔드포인트가 있다.
- [ ] 지연 시간과 오류율 알림이 설정되어 있다.
- [ ] 예측 분포를 추적한다.
- [ ] 각 알림에 대응 문서가 연결되어 있다.

## 연습 문제

1. 오류율이 1%를 넘으면 울리는 알림 규칙을 적어 보세요.
2. 분당 평균 입력값을 기록하는 메트릭을 설계해 보세요.
3. 첫 Grafana 화면에 어떤 위젯 네 개를 둘지 골라 보세요.

## 예측 드리프트 감지 코드 추가

시스템 메트릭만으로는 모델 품질 이상을 놓칠 수 있으므로, 예측 분포 변화를 함께 계산하는 것이 좋습니다.

```python
import numpy as np

def prediction_drift_score(ref_preds: np.ndarray, cur_preds: np.ndarray, bins: int = 20) -> float:
    edges = np.linspace(0.0, 1.0, bins + 1)
    r_hist, _ = np.histogram(ref_preds, bins=edges)
    c_hist, _ = np.histogram(cur_preds, bins=edges)

    r = r_hist / max(r_hist.sum(), 1)
    c = c_hist / max(c_hist.sum(), 1)

    eps = 1e-6
    r = r + eps
    c = c + eps

    return float(np.sum((c - r) * np.log(c / r)))

ref = np.random.beta(2, 5, size=5000)
cur = np.random.beta(3, 4, size=5000)
print(round(prediction_drift_score(ref, cur), 4))
```

이 값은 단독 판단 기준이 아니라 경보 신호로 쓰는 편이 안전합니다. 보통 임계값을 넘으면 대시보드 점검과 샘플 검토를 먼저 수행합니다.

## 모니터링 대시보드 핵심 패널

| 패널 | 목적 | 권장 시각화 |
|---|---|---|
| 요청량/성공률 | 트래픽과 실패 징후 파악 | 시계열 라인 |
| p50/p95/p99 지연시간 | 성능 저하 조기 감지 | 히스토그램 + 라인 |
| 예측 클래스 분포 | 모델 출력 이상 감지 | 스택 바/비율 라인 |
| 입력 피처 결측률 | 데이터 품질 감지 | 피처별 히트맵 |
| 배포 버전별 오류율 | 특정 버전 리스크 확인 | 버전 라벨 라인 |

패널이 많아질수록 좋은 것이 아니라, 온콜이 1분 안에 상황을 파악할 수 있느냐가 더 중요합니다.

## Prometheus 알림 룰 예시

```yaml
groups:
  - name: model-serving
    rules:
      - alert: ModelErrorRateHigh
        expr: rate(http_requests_total{path="/predict",status=~"5.."}[5m])
          /
          rate(http_requests_total{path="/predict"}[5m]) > 0.01
        for: 10m
        labels:
          severity: page
        annotations:
          summary: "모델 API 5xx 비율이 1%를 초과했습니다"
          runbook: "https://internal.example/runbooks/model-error"

      - alert: PredictionDriftSuspected
        expr: avg_over_time(prediction_drift_score[30m]) > 0.15
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "예측 분포 변화가 커졌습니다"
```

## 알림 피로를 줄이는 운영 원칙

- 같은 원인에서 반복되는 경고는 그룹화합니다.
- 일시 스파이크를 막기 위해 `for` 기간을 둡니다.
- 페이지 수준 경고는 즉시 행동이 가능한 것만 남깁니다.
- 모든 경고에는 런북 링크를 포함합니다.

모니터링은 수집보다 대응 설계가 더 중요합니다. 경고가 행동으로 이어지지 않으면 시스템 신뢰는 빠르게 떨어집니다.

## Grafana 대시보드 JSON 예시

Prometheus 메트릭을 Grafana로 시각화할 때, 모델 모니터링용 대시보드의 핵심 패널 구성을 JSON으로 보겠습니다.

```json
{
  "dashboard": {
    "title": "ML Model Monitoring",
    "panels": [
      {
        "title": "추론 요청 수 (분당)",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(prediction_requests_total[5m])",
            "legendFormat": "{{model_name}}"
          }
        ]
      },
      {
        "title": "추론 지연 시간 (p95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(prediction_latency_seconds_bucket[5m]))",
            "legendFormat": "p95"
          }
        ]
      },
      {
        "title": "예측값 분포",
        "type": "heatmap",
        "targets": [
          {
            "expr": "rate(prediction_value_bucket[10m])",
            "legendFormat": "{{le}}"
          }
        ]
      },
      {
        "title": "에러율",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(prediction_errors_total[5m]) / rate(prediction_requests_total[5m])",
            "legendFormat": "error_rate"
          }
        ]
      }
    ]
  }
}
```

이 대시보드에서 가장 먼저 봐야 할 패널은 "예측값 분포"입니다. 에러율이나 지연 시간은 인프라 문제로도 변할 수 있지만, 예측값 분포가 바뀌는 것은 모델 입력 데이터가 변했다는 뜻이기 때문입니다.

## 로그 기반 모니터링 보완

메트릭만으로 원인을 특정하기 어려울 때는 구조화된 로그가 필요합니다. 추론 요청마다 입력 특성 요약과 예측값을 로그로 남기면, 드리프트가 감지됐을 때 어떤 입력이 분포를 밀었는지 역추적할 수 있습니다.

```python
import structlog
import numpy as np

logger = structlog.get_logger()

def log_prediction(request_id: str, features: list, prediction: float):
    """추론 결과를 구조화된 로그로 남깁니다."""
    feature_array = np.array(features)
    logger.info(
        "prediction_logged",
        request_id=request_id,
        feature_mean=float(feature_array.mean()),
        feature_std=float(feature_array.std()),
        feature_min=float(feature_array.min()),
        feature_max=float(feature_array.max()),
        prediction=prediction,
        num_features=len(features),
    )
```

이 로그를 Elasticsearch나 Loki에 저장하면, Grafana에서 메트릭 이상 시점의 로그를 바로 조회할 수 있습니다. 핵심은 `feature_mean`과 `feature_std`를 함께 남기는 것입니다. 이 값의 추이가 학습 데이터 통계와 벌어지면 데이터 드리프트를 의심할 수 있습니다.

## SLO 기반 모니터링 설계

모니터링 지표가 많아지면 "어떤 알림이 진짜 중요한지" 판단이 어려워집니다. SLO(Service Level Objective)를 먼저 정의하고, 그 SLO를 위협하는 지표만 알림으로 연결하는 방식이 효과적입니다.

| SLO | 지표 | 임계치 | 알림 채널 |
| --- | --- | --- | --- |
| 추론 가용성 99.9% | 5xx 비율 | > 0.1% (5분) | PagerDuty |
| p95 지연 < 100ms | 지연 히스토그램 | > 100ms (5분) | Slack |
| 예측 정확도 > 85% | 일일 정확도 | < 85% (일간) | 이메일 |
| 드리프트 미감지 | PSI / KS 통계량 | PSI > 0.2 | Slack |

이렇게 SLO 계층을 나누면, 가용성 SLO 위반은 즉시 대응하고, 정확도 SLO 위반은 다음 영업일에 분석하는 식으로 대응 우선순위를 체계화할 수 있습니다.

## 인시던트 대응 런북

알림이 울렸을 때 담당자가 따라야 할 최소 절차를 문서화하면 평균 복구 시간(MTTR)을 줄일 수 있습니다.

```text
[모델 드리프트 알림 대응]

1. 알림 확인
   - 어떤 모델, 어떤 메트릭이 임계치를 넘었는지 확인
   - 알림 발생 시각과 지속 시간 기록

2. 영향 범위 파악
   - 해당 모델을 사용하는 서비스 목록 확인
   - 실제 비즈니스 지표(전환율, 클릭률 등)에 영향이 있는지 확인

3. 긴급 조치 판단
   - 비즈니스 영향 O → 이전 모델 버전으로 즉시 롤백
   - 비즈니스 영향 X → 원인 분석 후 다음 배포 사이클에 반영

4. 원인 분석
   - 입력 데이터 분포 변화 확인 (feature_mean, feature_std 추이)
   - 최근 업스트림 데이터 파이프라인 변경 이력 확인
   - 계절성, 이벤트성 변화인지 판단

5. 후속 조치
   - 재학습 필요 여부 결정
   - 알림 임계치 조정 필요 여부 검토
   - 사후 분석(postmortem) 문서 작성
```

이 런북의 핵심은 2번 "영향 범위 파악"입니다. 드리프트가 감지됐더라도 비즈니스 지표에 영향이 없으면 즉시 대응할 필요가 없습니다. 반대로 비즈니스 지표가 떨어지고 있다면 원인 분석보다 롤백이 먼저입니다.

## 정리

모니터링은 배포 뒤에 붙는 옵션이 아니라, 모델을 운영 자산으로 다루기 위한 기본 관측 장치입니다. 정확도만 기다리면 너무 늦고, 운영 신호를 먼저 봐야 문제를 조기에 잡을 수 있습니다.

이 글에서 기억할 핵심은 하나입니다. **모델이 살아 있는지보다, 지금 어떤 상태로 살아 있는지를 알아야 운영이 됩니다.** 다음 글에서는 그 신호를 바탕으로 데이터 드리프트와 모델 드리프트를 어떻게 구분할지 다루겠습니다.

## 처음 질문으로 돌아가기

- **정확도만 봐서는 왜 운영 문제를 너무 늦게 알게 될까요?**
  - 본문의 기준은 모델 모니터링를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **메트릭, 로그, 트레이스는 무엇이 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Prometheus와 Grafana는 모델 운영에서 어떤 역할을 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [MLOps 101 (1/10): MLOps란 무엇인가?](./01-what-is-mlops.md)
- [MLOps 101 (2/10): 실험 관리](./02-experiment-tracking.md)
- [MLOps 101 (3/10): 데이터 버전 관리](./03-data-versioning.md)
- [MLOps 101 (4/10): 모델 학습 파이프라인](./04-training-pipeline.md)
- [MLOps 101 (5/10): 모델 배포](./05-model-deployment.md)
- **모델 모니터링 (현재 글)**
- 데이터 드리프트와 모델 드리프트 (예정)
- 재학습 (예정)
- 피처 스토어 (예정)
- 운영 가능한 ML 시스템 (예정)

<!-- toc:end -->

## 참고 자료

- [예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/mlops-101/ko)

- [Prometheus documentation](https://prometheus.io/docs/)
- [prometheus-client (Python)](https://github.com/prometheus/client_python)
- [Grafana documentation](https://grafana.com/docs/)
- [Google SRE workbook — SLOs](https://sre.google/workbook/implementing-slos/)

Tags: MLOps, Monitoring, Prometheus, Observability, DataScience
