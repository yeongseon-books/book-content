---
series: mlops-101
episode: 4
title: "MLOps 101 (4/10): 모델 학습 파이프라인"
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
  - Pipeline
  - Airflow
  - DAG
  - DataScience
seo_description: 학습 과정을 단계로 분해하고 DAG로 연결하여, 모델 학습의 재현성과 운영 효율을 높이고 실패 복구 속도를 개선하는 파이프라인 설계법입니다.
last_reviewed: '2026-05-12'
---

# MLOps 101 (4/10): 모델 학습 파이프라인

`train.py` 하나를 정기 실행한다고 해서 곧바로 운영 가능한 학습 체계가 되지는 않습니다. 데이터 수집, 전처리, 학습, 평가, 등록이 한 파일 안에 뭉쳐 있으면 어디서 실패했는지 보기 어렵고, 일부만 다시 돌리는 것도 힘듭니다.

학습이 사람 손을 탈수록 재현성과 운영 속도는 함께 떨어집니다. 그래서 MLOps에서 파이프라인은 편의 기능이 아니라, 학습을 단계로 분해해 다시 실행 가능하게 만드는 기본 구조입니다.

이 글은 MLOps 101 시리즈의 4번째 글입니다.

여기서는 학습 파이프라인을 스크립트 자동화와 구분해서 보고, 왜 단계 분리와 DAG가 중요한지 작은 예제로 정리하겠습니다.

## 먼저 던지는 질문

- 학습 스크립트 하나를 여러 단계 파이프라인으로 나누는 이유는 무엇일까요?
- DAG는 단순 실행 순서와 어떻게 다를까요?
- Airflow, Prefect, Kubeflow 같은 오케스트레이터는 어디에 들어갈까요?

## 큰 그림

![MLOps 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/04/04-01-see-the-flow-first.ko.png)

*MLOps 101 4장 흐름 개요*

이 그림은 데이터 수집부터 모델 배포까지 각 단계가 명시적으로 정의되고 자동화되는 구조를 보여줍니다. 파이프라인이 있으면 실패 지점을 빨리 찾고 부분 재실행이 가능해집니다.

> 파이프라인의 핵심은 처음부터 끝까지 같은 구조로 모두 배울 수 있다는 데 있습니다. 한 단계 실패 시 거기서만 재시작할 수 있고, 각 단계의 입출력이 명확해 장애 원인도 빨리 찾힙니다.

## 왜 중요한가

수동 학습은 느리고, 재현이 어렵고, 장애 원인을 찾기 힘듭니다. 특히 야간 배치 학습이 실패했을 때 전체를 처음부터 다시 돌려야 한다면 운영 비용이 빠르게 커집니다.

반대로 단계를 잘게 나누면 문제가 난 지점을 바로 좁힐 수 있고, 바뀐 입력이 있는 구간만 다시 실행할 수 있습니다. 파이프라인은 곧 학습의 관측성과 복구성을 높이는 장치입니다.

### 모델 서빙 패턴

모델을 운영에 내보내는 방식은 크게 세 가지로 나뒩니다. 각 패턴은 응답 시간, 처리량, 인프라 복잡도에서 다른 트레이드오프를 가집니다.

| 패턴 | 지연시간 | 처리량 | 적합한 경우 |
|---|---|---|---|
| 배치 추론 | 분~시간 | 매우 높음 | 주간 리포트, 대량 예측 일괄 처리 |
| 실시간 추론 | ms~초 | 보통 | 사용자 요청에 즉시 응답, 추천, 검색 |
| 스트리밍 추론 | 초 이하 | 높음 | 실시간 사기 탐지, 이상 탐지, 로그 분석 |

#### 배치 추론

모든 입력을 모아 두고 정해진 시간에 한 번에 실행합니다. Airflow나 Cron으로 스케줄링하고, 결과는 DB나 파일로 저장합니다. 응답 속도보다 처리량이 중요한 경우에 적합합니다.

#### 실시간 추론

HTTP 요청을 받아 즉시 예측을 반환합니다. FastAPI, Flask, BentoML 같은 프레임워크가 쓰입니다. 응답 시간이 중요하고, 요청마다 결과가 달라야 하는 경우에 적합합니다.

#### 스트리밍 추론

Kafka, Kinesis 같은 메시지 큐에서 데이터를 받아 순차적으로 처리합니다. 이벤트가 계속 들어오고, 각 이벤트마다 즉시 판단이 필요한 경우에 적합합니다.

### FastAPI 모델 서빙 코드 예제

앞서 본 예제를 조금 더 확장해보겠습니다. 버전 정보, 입력 검증, 로깅, 메트릭 수집까지 포함한 예제입니다.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pickle
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Model API", version="1.0.0")

# 시작 시 모델 로드
MODEL_PATH = "model.pkl"
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    logger.info(f"Model loaded from {MODEL_PATH}")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = None

class PredictRequest(BaseModel):
    x: float = Field(..., ge=0, le=100, description="Input feature (0-100)")

class PredictResponse(BaseModel):
    prediction: int
    model_version: str
    latency_ms: float

@app.get("/healthz")
def health():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ok", "version": "1.0.0"}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    start = time.time()
    try:
        pred = int(model.predict([[req.x]])[0])
        latency = (time.time() - start) * 1000
        logger.info(f"Prediction: x={req.x}, pred={pred}, latency={latency:.2f}ms")
        return PredictResponse(
            prediction=pred,
            model_version="1.0.0",
            latency_ms=round(latency, 2),
        )
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Prediction error")
```

이 코드에서는 입력 범위 검증(`ge=0, le=100`), 모델 로드 실패 처리, 지연시간 측정, 로깅이 모두 들어가 있습니다. 운영에서는 이런 요소가 있어야 문제 상황을 빠르게 파악할 수 있습니다.

### 모델 패키징

모델을 배포하려면 코드, 모델 파일, 라이브러리, 환경 변수를 한 묶음으로 만들어야 합니다. 세 가지 패키징 방식을 소개합니다.

#### 1. Docker 이미지

가장 흐하게 쓰이는 방식입니다. 모델, 코드, 라이브러리, OS 환경을 통째로 묶습니다.

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY model.pkl .
COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

장점: 환경 일관성, Kubernetes 같은 오케스트레이터와 호환성 높음.

#### 2. ONNX 포맷

ONNX는 프레임워크 중립적인 모델 포맷입니다. PyTorch, TensorFlow, scikit-learn 모델을 ONNX로 변환하면 다른 언어나 환경에서도 쓸 수 있습니다.

```python
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

initial_type = [("float_input", FloatTensorType([None, 1]))]
onnx_model = convert_sklearn(model, initial_types=initial_type)

with open("model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())
```

장점: 추론 속도 최적화, 프레임워크 독립성.

#### 3. BentoML Bundle

BentoML은 모델과 API 코드를 함께 패키징하는 도구입니다.

```python
import bentoml
from sklearn.linear_model import LogisticRegression

# 모델 저장
model = LogisticRegression().fit([[0], [1]], [0, 1])
bentoml.sklearn.save_model("lr_model", model)

# 서빙 코드
# service.py
import bentoml
from bentoml.io import JSON

runner = bentoml.sklearn.get("lr_model:latest").to_runner()
svc = bentoml.Service("lr_service", runners=[runner])

@svc.api(input=JSON(), output=JSON())
def predict(input_data):
    result = runner.predict.run([input_data["x"]])
    return {"prediction": int(result[0])}
```

장점: 모델 저장, API 서빙, Docker 빌드를 한 곳에서 처리.
---

## 전체 흐름을 먼저 보겠습니다

이 그림에서 중요한 것은 각 단계 이름보다 경계입니다. 수집, 전처리, 학습, 평가, 등록이 분리되어 있어야 입력이 바뀐 단계만 다시 실행할 수 있고, 실패한 지점도 빠르게 확인할 수 있습니다.

즉, 파이프라인의 목적은 화려한 스케줄링이 아니라 단계 경계를 명확히 만드는 데 있습니다.

---

## 먼저 잡아야 할 핵심 개념

- **단계(stage)**: 입력, 명령, 출력이 분리된 실행 단위입니다.
- **DAG**: 단계 사이의 의존 관계를 표현하는 방향성 비순환 그래프입니다.
- 멱등성: 같은 입력이면 같은 출력을 다시 만드는 성질입니다.
- 캐싱: 바뀐 단계만 다시 실행하도록 결과를 재사용하는 방식입니다.
- 백필: 과거 날짜나 누락 구간을 다시 채워 실행하는 작업입니다.

이 개념을 먼저 잡아야 오케스트레이터를 도입해도 구조가 흔들리지 않습니다. 도구는 DAG를 실행해 주지만, 단계 경계를 대신 설계해 주지는 않기 때문입니다.

---

## 도입 전과 도입 후를 비교해 보겠습니다

**Before**: `train.py`를 cron으로 돌리고 무사히 끝나기를 바랍니다.

**After**: DAG가 단계를 나누고, 재시도와 알림과 캐싱이 함께 동작합니다.

Before 상태에서는 실패가 나도 어느 단계가 문제인지 바로 보이지 않습니다. After 상태에서는 실패 지점, 재실행 범위, 산출물 위치가 모두 더 분명해집니다.

---

## 아주 작은 파이프라인을 만들어 보겠습니다

### 1단계 — 수집 단계를 정의합니다

```python
import pandas as pd

def ingest():
    df = pd.DataFrame({"x": range(50), "y": [i % 2 for i in range(50)]})
    df.to_csv("/tmp/raw.csv", index=False)
    return "/tmp/raw.csv"
```

수집 단계는 raw 입력을 만들어 다음 단계에 넘깁니다. 중요한 것은 이 함수가 어떤 파일을 만들었는지 명확히 드러난다는 점입니다.

### 2단계 — 전처리 단계를 분리합니다

```python
def preprocess(path):
    df = pd.read_csv(path)
    df["x"] = (df["x"] - df["x"].mean()) / df["x"].std()
    out = "/tmp/clean.csv"
    df.to_csv(out, index=False)
    return out
```

전처리를 별도 단계로 빼면 입력 스케일 변경이나 정규화 로직 변경이 학습 단계와 분리됩니다. 이 구분이 있어야 전처리만 다시 돌려도 되는 상황을 만들 수 있습니다.

### 3단계 — 학습 단계를 분리합니다

```python
import pickle
from sklearn.linear_model import LogisticRegression

def train(path):
    df = pd.read_csv(path)
    m = LogisticRegression().fit(df[["x"]], df["y"])
    with open("/tmp/model.pkl", "wb") as f:
        pickle.dump(m, f)
    return "/tmp/model.pkl"
```

학습 단계는 전처리 결과를 받아 모델 파일을 만듭니다. 파이프라인 관점에서는 정확도보다도, 이 단계의 입력과 출력이 고정되어 있다는 점이 중요합니다.

### 4단계 — 평가를 따로 둡니다

```python
def evaluate(path, model_path):
    df = pd.read_csv(path)
    with open(model_path, "rb") as f:
        m = pickle.load(f)
    return float(m.score(df[["x"]], df["y"]))
```

평가를 학습과 분리해 두면 승격 기준을 더 명확히 운영할 수 있습니다. 학습이 끝났다고 바로 배포하지 않고, 평가 결과를 중간 경계로 둘 수 있기 때문입니다.

### 5단계 — 오케스트레이션으로 연결합니다

```python
def run():
    raw = ingest()
    clean = preprocess(raw)
    model = train(clean)
    metric = evaluate(clean, model)
    print({"metric": metric, "model": model})

run()
```

이 함수는 단계의 순서를 조합할 뿐입니다. 실제 오케스트레이터가 들어오면 Airflow의 Operator나 Prefect의 task 같은 형태로 감싸겠지만, 본질은 바뀌지 않습니다.

---

## 이 코드에서 먼저 봐야 할 점

- 각 단계는 함수와 파일 입출력으로 경계가 분명합니다.
- 오케스트레이터는 단계 순서를 강제하지만 단계 내부 의미까지 바꾸지는 않습니다.
- 단계가 작을수록 실패 원인 추적과 재실행이 쉬워집니다.
- 멱등성이 있어야 재시도와 캐싱이 안전하게 동작합니다.

파이프라인을 잘 설계한 팀은 코드보다 DAG 그림만 봐도 운영 흐름이 이해됩니다. 반대로 단계가 너무 크면 오케스트레이터를 붙여도 여전히 거대한 스크립트 한 덩어리로 남습니다.

---

## 자주 헷갈리는 지점

1. **단계를 너무 크게 잡습니다.**
   일부 실패에도 전체를 다시 실행하게 됩니다.
2. **랜덤 시드를 고정하지 않아 멱등성이 깨집니다.**
   같은 입력인데도 결과가 달라집니다.
3. **출력 경로를 고정해 병렬 실행이 충돌합니다.**
   날짜나 run ID가 빠지면 산출물이 덮어써집니다.
4. **재시도 정책이 없습니다.**
   일시적 오류도 전체 실패가 됩니다.
5. **알림이 없어 실패를 너무 늦게 압니다.**
   야간 배치에서는 특히 치명적입니다.

---

## 실무에서는 이렇게 봅니다

실제 운영에서는 매일 새벽 Airflow DAG가 데이터 준비, 학습, 평가, 등록을 순서대로 돌리고, 주간 리포트는 같은 DAG의 마지막 결과를 재사용하는 식으로 설계하는 경우가 많습니다. 중요한 것은 도구 이름보다 단계를 작게 나누고 입출력을 명확히 두는 습관입니다.

시니어 엔지니어는 파이프라인을 문서로도 봅니다. 단계 이름만 읽어도 팀원이 구조를 이해할 수 있는지, 재시도와 알림이 기본값인지, 캐싱과 백필을 어디까지 허용할지 먼저 점검합니다.

---

## 체크리스트

- [ ] 단계가 작고 역할이 분명하다.
- [ ] 각 단계의 입력과 출력이 명시되어 있다.
- [ ] 재시도와 알림이 설정되어 있다.
- [ ] DAG 구조를 설명할 수 있다.

## 연습 문제

1. 이 예제를 Airflow DAG 의사코드로 바꿔 보세요.
2. 전처리 단계만 캐싱하는 규칙을 설계해 보세요.
3. 실패 시 슬랙 알림이 가도록 의사코드를 적어 보세요.

## 정리

학습 파이프라인은 단순 자동 실행이 아니라, 학습 과정을 단계로 쪼개 재현과 복구를 쉽게 만드는 구조입니다. MLOps에서 DAG가 중요한 이유도 바로 여기에 있습니다.

이 글에서 기억할 핵심은 하나입니다. **좋은 파이프라인은 학습 속도보다 실패 복구 속도를 먼저 높입니다.** 다음 글에서는 이렇게 만들어진 모델을 안전하게 서비스로 내보내는 배포를 다루겠습니다.


## Airflow와 Prefect로 보는 파이프라인 설계 차이

오케스트레이터를 고를 때는 기능 목록보다 팀 운영 방식과 장애 대응 방식을 먼저 봐야 합니다.

| 항목 | Airflow | Prefect |
|---|---|---|
| DAG 표현 | 정적 DAG 정의 중심 | 동적 플로우 표현 유연 |
| 운영 경험 | 대규모 배치 운영 사례 풍부 | 초기 도입과 로컬 개발 편의 |
| UI 관측 | 태스크/스케줄 관측 강함 | 실행 상태/재시도 가시성 우수 |
| 적합 팀 | 데이터 플랫폼/배치 중심 | 제품 팀 주도 반복 실험 |

둘 중 무엇이 절대적으로 낫다기보다, 팀이 어떤 종류의 파이프라인을 얼마나 자주 바꾸는지가 선택 기준입니다.

## Airflow DAG 확장 예시

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime


def validate_schema():
    print("validate schema")


def train_model():
    print("train model")


def evaluate_model():
    print("evaluate model")


def register_model():
    print("register model")

with DAG(
    dag_id="ml_training_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * *",
    catchup=False,
    max_active_runs=1,
) as dag:
    start = EmptyOperator(task_id="start")
    schema = PythonOperator(task_id="validate_schema", python_callable=validate_schema)
    train = PythonOperator(task_id="train", python_callable=train_model)
    evaluate = PythonOperator(task_id="evaluate", python_callable=evaluate_model)
    register = PythonOperator(task_id="register", python_callable=register_model)
    end = EmptyOperator(task_id="end")

    start >> schema >> train >> evaluate >> register >> end
```

이 구조에서 핵심은 각 단계가 실패 원인을 분리할 수 있도록 역할이 분명하다는 점입니다.

## 파이프라인 설정 파일 예시

```yaml
pipeline:
  name: churn-train
  schedule: "0 2 * * *"
  retries: 2
  retry_delay_sec: 300

data:
  source: s3://ml-data/churn/raw/
  schema_path: schemas/churn_v3.json
  min_rows: 50000

training:
  algorithm: xgboost
  objective: binary:logistic
  max_depth: 6
  eta: 0.1
  n_estimators: 400

evaluation:
  min_auc: 0.84
  max_inference_latency_ms: 80

registry:
  model_name: churn-risk-model
  stage_on_success: Staging
```

파라미터를 코드에서 분리해 설정 파일로 두면, 운영 변경을 코드 수정 없이 관리할 수 있습니다.

## 파이프라인 품질 게이트

- 입력 스키마 검증 실패 시 학습 단계로 진행하지 않습니다.
- 평가 지표 기준 미달 시 레지스트리 등록을 차단합니다.
- 재시도 횟수 초과 시 알림과 런북 링크를 함께 보냅니다.
- 동일 입력 재실행 시 출력 일관성을 검증합니다.

이 게이트가 있어야 파이프라인 자동화가 단순 스케줄러를 넘어 품질 방어선 역할을 합니다.

## 처음 질문으로 돌아가기

- **학습 스크립트 하나를 여러 단계 파이프라인으로 나누는 이유는 무엇일까요?**
  - 본문의 기준은 모델 학습 파이프라인를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **DAG는 단순 실행 순서와 어떻게 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Airflow, Prefect, Kubeflow 같은 오케스트레이터는 어디에 들어갈까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [MLOps 101 (1/10): MLOps란 무엇인가?](./01-what-is-mlops.md)
- [MLOps 101 (2/10): 실험 관리](./02-experiment-tracking.md)
- [MLOps 101 (3/10): 데이터 버전 관리](./03-data-versioning.md)
- **모델 학습 파이프라인 (현재 글)**
- 모델 배포 (예정)
- 모델 모니터링 (예정)
- 데이터 드리프트와 모델 드리프트 (예정)
- 재학습 (예정)
- 피처 스토어 (예정)
- 운영 가능한 ML 시스템 (예정)

<!-- toc:end -->

## 참고 자료

- [Apache Airflow](https://airflow.apache.org/docs/)
- [Prefect](https://docs.prefect.io/)
- [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/)
- [Google — TFX](https://www.tensorflow.org/tfx)

Tags: MLOps, Pipeline, Airflow, DAG, DataScience
