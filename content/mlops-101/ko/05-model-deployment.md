---
series: mlops-101
episode: 5
title: "MLOps 101 (5/10): 모델 배포"
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
  - Deployment
  - FastAPI
  - Docker
  - DataScience
seo_description: 학습한 모델을 FastAPI와 Docker로 감싸고, 버전 관리와 전환 정책을 통해 안전하고 재현 가능하게 배포하는 방법을 소개합니다.
last_reviewed: '2026-05-12'
---

# MLOps 101 (5/10): 모델 배포

모델 학습이 끝났다고 서비스가 생기는 것은 아닙니다. 학습된 파일을 어떤 프로세스가 읽고, 어떤 입력을 검증하고, 어떤 환경에서 실행할지 정해지지 않으면 좋은 모델도 운영에서는 금방 흔들립니다.

현업에서 배포가 어렵다고 할 때는 대개 모델 자체보다 환경 차이, 버전 추적 부재, 롤백 불가능 상태를 말합니다. 그래서 모델 배포의 핵심은 파일을 서버에 올리는 일이 아니라, 재현 가능한 실행 환경과 안전한 전환 절차를 만드는 데 있습니다.

이 글은 MLOps 101 시리즈의 5번째 글입니다.

여기서는 학습된 모델을 API와 컨테이너로 감싸는 기본 흐름을 보고, 왜 카나리나 롤백 같은 운영 절차가 함께 필요해지는지 정리하겠습니다.


![MLOps 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/05/05-01-see-the-flow-first.ko.png)
*MLOps 101 5장 흐름 개요*
> 배포의 핵심은 여러 버전을 한 시스템 안에서 안전하게 전환하고, 문제가 생기면 빠르게 되돌릴 수 있는 구조를 만드는 데 있습니다.

## 먼저 던지는 질문

- 학습된 모델 파일을 어떻게 사용자 요청에 연결할 수 있을까요?
- 온라인 추론, 배치 추론, 스트리밍 추론은 어떤 차이로 이해하면 좋을까요?
- FastAPI와 Docker는 모델 배포에서 어떤 역할을 할까요?

## 왜 중요한가

많은 팀이 배포를 어렵게 만드는 원인을 모델 복잡도에서 찾지만, 실제로는 환경 불일치와 무계획 롤백이 더 자주 문제를 만듭니다. 로컬에서는 잘 돌던 모델이 서버에서는 라이브러리 버전 차이로 깨지고, 새 버전이 이상해도 이전 버전으로 되돌리는 절차가 없으면 장애가 길어집니다.

그래서 배포는 학습의 마지막 단계가 아니라 운영의 첫 단계입니다. 어떤 버전이 살아 있는지, 어디까지 트래픽을 보낼지, 이상 징후가 보이면 어떻게 되돌릴지부터 함께 설계해야 합니다.

### 모델 서빙 패턴 비교

모델 배포를 설계할 때 가장 먼저 결정할 것은 서빙 패턴입니다. 응답 시간, 처리량, 비용이 모두 다르기 때문에 용도에 맞는 패턴을 골라야 합니다.

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

이 그림은 모델 배포를 파일 복사 작업이 아니라 전달 경로로 보게 해 줍니다. 모델 파일은 API 안으로 들어가고, API는 Docker 이미지로 묶이고, 이미지는 프로덕션에 배포된 뒤 점진적으로 트래픽을 받습니다.

즉, 모델 배포는 "모델 + 실행 코드 + 런타임 환경 + 전환 정책"의 묶음입니다.

---

## 먼저 잡아야 할 핵심 개념

- **온라인 추론**: 요청을 받으면 즉시 예측을 반환하는 방식입니다.
- **배치 추론**: 대량 데이터를 일정 주기로 처리하는 방식입니다.
- **Blue/Green**: 두 환경을 병렬로 두고 전환하는 배포 방식입니다.
- **Canary**: 소량 트래픽부터 새 버전에 보내는 방식입니다.
- 롤백: 문제가 생겼을 때 이전 버전으로 되돌리는 절차입니다.

이 개념을 먼저 분리해 두면, 왜 어떤 모델은 API로 가고 어떤 모델은 배치 작업으로 가는지 자연스럽게 이해됩니다.

---

## 도입 전과 도입 후를 비교해 보겠습니다

**Before**: 노트북에서 `predict`를 직접 호출해 결과를 확인합니다.

**After**: 컨테이너가 HTTP 엔드포인트를 노출하고, 버전 태그와 헬스 체크를 함께 운영합니다.

Before 상태에서는 사람이 모델을 대신 호출합니다. After 상태에서는 서비스가 모델을 대신 호출하고, 운영 시스템이 그 상태를 감시합니다.

---

## FastAPI와 Docker로 작은 서빙 경로를 만들어 보겠습니다

### 1단계 — 모델 파일을 준비합니다

```python
import pickle
from sklearn.linear_model import LogisticRegression

m = LogisticRegression().fit([[0], [1], [2], [3]], [0, 0, 1, 1])
with open("model.pkl", "wb") as f:
    pickle.dump(m, f)
```

배포의 출발점은 학습 코드가 아니라 아티팩트입니다. 운영 환경에서는 모델이 코드 안에 숨어 있는 값이 아니라, 외부에서 로드되는 파일이어야 교체와 롤백이 쉬워집니다.

### 2단계 — FastAPI 앱으로 감쌉니다

```python
from fastapi import FastAPI
from pydantic import BaseModel
import pickle

app = FastAPI()
model = pickle.load(open("model.pkl", "rb"))

class Req(BaseModel):
    x: float

@app.post("/predict")
def predict(r: Req):
    p = model.predict([[r.x]])[0]
    return {"prediction": int(p)}
```

이 코드는 모델을 요청-응답 인터페이스로 바꾸는 최소 형태입니다. 입력 스키마를 분리하는 이유는 운영에서 잘못된 요청이 서버 전체를 흔드는 일을 막기 위해서입니다.

### 3단계 — 헬스 체크를 둡니다

```python
@app.get("/healthz")
def health():
    return {"ok": True, "version": "1.0.0"}
```

헬스 체크는 단순 편의 기능이 아닙니다. 오케스트레이터나 로드 밸런서가 어떤 인스턴스에 트래픽을 보내도 되는지 판단하는 기준이 됩니다.

### 4단계 — Docker 이미지로 고정합니다

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

컨테이너는 모델 서빙 환경을 재현 가능한 아티팩트로 묶어 줍니다. 같은 이미지 태그면 같은 실행 환경이라는 합의를 만들 수 있기 때문에 배포와 롤백이 훨씬 단순해집니다.

### 5단계 — 빌드하고 실행합니다

```bash
docker build -t model-api:1.0.0 .
docker run -p 8000:8000 model-api:1.0.0
curl -X POST localhost:8000/predict -H "Content-Type: application/json" -d '{"x": 2.5}'
```

**Expected output:** `{"prediction": 1}` 같은 JSON 응답이 돌아오고, `/healthz`가 계속 정상 상태를 반환해야 합니다.

여기서 `model-api:1.0.0` 같은 태그가 왜 중요한지 봐야 합니다. 운영 중인 모델이 무엇인지, 문제 발생 시 무엇으로 되돌릴지, 카나리 대상이 어느 버전인지 모두 이 태그 체계에 달려 있습니다.

---

## 배포가 이상할 때 가장 먼저 볼 것

새 모델을 올린 직후 요청이 실패하거나 응답이 이상하면, 바로 모델 품질부터 의심하기보다 어느 계약이 먼저 깨졌는지 좁혀 가는 편이 빠릅니다.

### 1단계 — 헬스 체크가 정상인지 확인합니다

```bash
curl -s http://localhost:8000/healthz
```

**Expected output:** `{"ok": true, "version": "1.0.0"}` 같은 응답입니다.

여기서 실패하면 모델 성능보다 먼저 컨테이너 기동 로그, import 오류, 포트 바인딩 상태를 확인해야 합니다.

### 2단계 — 실제로 어떤 이미지 태그가 떠 있는지 확인합니다

```bash
docker ps --format "table {{.Image}}\t{{.Status}}\t{{.Names}}"
```

**Expected output:** 의도한 태그(`model-api:1.0.0`)가 실행 중으로 보여야 합니다.

태그가 다르면 모델 문제라기보다 배포 절차 문제입니다.

### 3단계 — 잘못된 입력을 안전하게 막는지 봅니다

```bash
curl -s -X POST localhost:8000/predict -H "Content-Type: application/json" -d '{"x":"bad"}'
```

**Expected output:** 서버 크래시가 아니라 입력 검증 오류가 반환되어야 합니다.

이 확인은 잘못된 요청이 서비스 전체 장애로 번지지 않도록 막고 있는지 보여 줍니다.

---

## 이 코드에서 먼저 봐야 할 점

- 모델은 요청마다 로드하지 않고 시작 시 한 번만 읽습니다.
- 입력 검증이 있어야 잘못된 페이로드가 장애로 번지지 않습니다.
- 헬스 체크는 트래픽 제어와 배포 자동화의 기준입니다.
- 이미지 태그가 곧 배포 단위 버전이 됩니다.

배포를 안정적으로 만드는 요소는 화려한 플랫폼보다 이런 기본 계약에 더 가깝습니다. 입력, 버전, 상태 확인, 롤백 경로가 분명해야 운영이 쉬워집니다.

---

## 자주 헷갈리는 지점

1. **버전 태그 없이 배포합니다.**
   어떤 모델이 살아 있는지 알 수 없습니다.
2. **`requirements.txt`를 고정하지 않습니다.**
   같은 코드인데 다른 환경이 됩니다.
3. **롤백 절차를 문서화하지 않습니다.**
   사고가 나면 되돌리는 시간부터 길어집니다.
4. **모델과 코드를 너무 강하게 묶습니다.**
   모델 교체가 배포 전체 변경으로 번집니다.
5. **입력 검증을 생략합니다.**
   잘못된 요청이 서버 안정성을 무너뜨립니다.

---

## 실무에서는 이렇게 봅니다

추천 모델은 FastAPI와 Docker를 묶어 Kubernetes 위에서 온라인 추론으로 돌리고, 주간 리포트는 배치 작업으로 따로 돌리는 식의 분리가 흔합니다. 같은 모델이라도 응답 시간 요구와 호출 패턴이 다르면 배포 형태도 달라집니다.

시니어 엔지니어는 배포를 모델 교체 문제가 아니라 폭발 반경 관리 문제로 봅니다. 그래서 카나리, 헬스 체크, 이미지 태그, 환경 변수 주입, 롤백 절차를 처음부터 함께 봅니다.

---

## 체크리스트

- [ ] `Dockerfile`이 있다.
- [ ] 헬스 체크 엔드포인트가 있다.
- [ ] 입력 스키마를 검증한다.
- [ ] 롤백 계획이 문서화되어 있다.

## 연습 문제

1. 모델 SHA를 반환하는 `/version` 엔드포인트를 설계해 보세요.
2. Nginx 가중치 기반 카나리 전환 흐름을 그림으로 적어 보세요.
3. 이 모델을 배치 추론 작업으로 바꾸면 무엇이 달라질지 정리해 보세요.

## 정리

모델 배포는 학습 결과를 서비스 인터페이스와 실행 환경 안으로 옮기는 일입니다. 여기서 중요한 것은 단순 배포 성공이 아니라, 같은 환경을 다시 만들 수 있고 문제 시 되돌릴 수 있는가입니다.

이 글에서 기억할 핵심은 하나입니다. **배포는 모델을 노출하는 단계가 아니라, 운영 위험을 제어하는 단계입니다.** 다음 글에서는 배포된 모델을 어떻게 관찰할지, 즉 모델 모니터링을 다루겠습니다.


## FastAPI 서빙을 운영형으로 확장하기

기본 예제에서 한 단계 더 나가려면 요청 식별자, 예측 로그, 모델 버전 라우팅을 함께 고려해야 합니다.

```python
from fastapi import FastAPI, Header
from pydantic import BaseModel
import time

app = FastAPI()

class Req(BaseModel):
    x: float

MODEL_VERSION = "2026.05.12"

@app.post("/predict")
def predict(req: Req, x_request_id: str | None = Header(default=None)):
    start = time.time()
    pred = int(req.x > 0.5)
    latency_ms = (time.time() - start) * 1000
    log = {
        "request_id": x_request_id,
        "model_version": MODEL_VERSION,
        "x": req.x,
        "pred": pred,
        "latency_ms": round(latency_ms, 2),
    }
    print(log)
    return {"prediction": pred, "model_version": MODEL_VERSION}
```

운영에서 가장 중요한 것은 결과 숫자뿐 아니라 "어떤 버전이 어떤 요청을 처리했는가"를 남기는 일입니다.

## Docker 배포 구성 예시

```yaml
version: "3.9"
services:
  model-api:
    build: .
    image: model-api:2026.05.12
    ports:
      - "8000:8000"
    environment:
      - MODEL_VERSION=2026.05.12
      - LOG_LEVEL=info
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 30s
      timeout: 5s
      retries: 3
```

이 구성은 단일 호스트에서도 버전 태그와 헬스 체크 기반 운영을 가능하게 해 줍니다.

## A/B 또는 카나리 전환 규칙

| 단계 | 트래픽 비율 | 관찰 지표 | 진행 조건 |
|---|---:|---|---|
| Stage 1 | 5% | 오류율, p95 지연시간 | 기존 대비 악화 없음 |
| Stage 2 | 20% | 예측 분포, 비즈니스 KPI | 2시간 이상 안정 |
| Stage 3 | 50% | KPI, 비용, 재시도율 | 온콜 승인 |
| Stage 4 | 100% | 전체 SLO | 24시간 이상 안정 |

이런 전환표가 있어야 "언제 확대하고 언제 중단할지"를 팀이 같은 기준으로 판단할 수 있습니다.

## 롤백 런북 최소 템플릿

1. 현재 서비스 이미지 태그와 배포 시각 확인
2. 직전 안정 버전 태그 선택
3. 트래픽을 직전 버전으로 전환
4. 전환 후 10분간 오류율/지연시간 모니터링
5. 사고 타임라인과 원인 후보 기록

모델 배포에서 사고는 피하기보다 빠르게 복구하는 설계가 더 현실적입니다. 따라서 배포 설계의 핵심은 성공 경로뿐 아니라 실패 경로를 명시하는 데 있습니다.


## 모델 레지스트리 연동

운영 환경에서는 모델 파일을 직접 복사하지 않고, 모델 레지스트리에서 버전을 지정해 가져옵니다. MLflow Model Registry를 기준으로 배포 시점에 모델을 로드하는 패턴을 보겠습니다.

```python
import mlflow
from mlflow.tracking import MlflowClient

MLFLOW_TRACKING_URI = "http://mlflow.internal:5000"
MODEL_NAME = "fraud-detector"
MODEL_STAGE = "Production"

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
client = MlflowClient()


def load_production_model():
    """레지스트리에서 Production 스테이지 모델을 로드합니다."""
    model_uri = f"models:/{MODEL_NAME}/{MODEL_STAGE}"
    model = mlflow.pyfunc.load_model(model_uri)
    version_info = client.get_latest_versions(MODEL_NAME, stages=[MODEL_STAGE])
    current_version = version_info[0].version if version_info else "unknown"
    return model, current_version


model, model_version = load_production_model()
```

이 패턴의 핵심은 배포 코드가 모델 파일 경로를 직접 알 필요가 없다는 것입니다. 레지스트리가 "Production 스테이지에 해당하는 최신 버전"을 관리하므로, 배포 코드는 스테이지 이름만 참조합니다.

## 헬스 체크와 준비 상태 프로브

Kubernetes나 로드 밸런서가 컨테이너의 상태를 판단하려면 두 가지 엔드포인트가 필요합니다.

```python
from fastapi import FastAPI, Response, status

app = FastAPI()
model_loaded = False


@app.on_event("startup")
async def startup_load_model():
    global model_loaded
    load_production_model()
    model_loaded = True


@app.get("/healthz")
async def liveness():
    return {"status": "alive"}


@app.get("/readyz")
async def readiness(response: Response):
    if not model_loaded:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready", "reason": "model loading"}
    return {"status": "ready"}
```

Kubernetes 매니페스트에서는 다음처럼 설정합니다.

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /readyz
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 3
```

`readinessProbe`의 `initialDelaySeconds`를 모델 로드 시간보다 크게 잡아야 합니다. 대형 모델은 로드에 30초 이상 걸릴 수 있으므로, 이 값을 너무 작게 설정하면 컨테이너가 준비되지 않은 상태에서 트래픽이 유입됩니다.

## 배포 검증 스크립트

배포 직후에는 자동화된 스모크 테스트로 기본 동작을 확인합니다.

```python
import httpx
import sys

BASE_URL = "http://localhost:8000"
TIMEOUT = 10.0


def smoke_test():
    """배포 직후 실행하는 최소 검증입니다."""
    # 1. 헬스 체크
    resp = httpx.get(f"{BASE_URL}/healthz", timeout=TIMEOUT)
    assert resp.status_code == 200, f"healthz failed: {resp.status_code}"

    # 2. 준비 상태
    resp = httpx.get(f"{BASE_URL}/readyz", timeout=TIMEOUT)
    assert resp.status_code == 200, f"readyz failed: {resp.status_code}"

    # 3. 추론 요청
    payload = {"features": [0.1, 0.2, 0.3, 0.4]}
    resp = httpx.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
    assert resp.status_code == 200, f"predict failed: {resp.status_code}"
    result = resp.json()
    assert "prediction" in result, "response missing prediction field"

    print("PASS: all smoke tests passed")


if __name__ == "__main__":
    try:
        smoke_test()
    except AssertionError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
```

이 스크립트를 CI/CD 파이프라인의 배포 후 단계에 넣으면, 실패 시 자동으로 롤백을 트리거할 수 있습니다.

## 처음 질문으로 돌아가기

- **학습된 모델 파일을 어떻게 사용자 요청에 연결할 수 있을까요?**
  - 본문의 기준은 모델 배포를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **온라인 추론, 배치 추론, 스트리밍 추론은 어떤 차이로 이해하면 좋을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **FastAPI와 Docker는 모델 배포에서 어떤 역할을 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [MLOps 101 (1/10): MLOps란 무엇인가?](./01-what-is-mlops.md)
- [MLOps 101 (2/10): 실험 관리](./02-experiment-tracking.md)
- [MLOps 101 (3/10): 데이터 버전 관리](./03-data-versioning.md)
- [MLOps 101 (4/10): 모델 학습 파이프라인](./04-training-pipeline.md)
- **모델 배포 (현재 글)**
- 모델 모니터링 (예정)
- 데이터 드리프트와 모델 드리프트 (예정)
- 재학습 (예정)
- 피처 스토어 (예정)
- 운영 가능한 ML 시스템 (예정)

<!-- toc:end -->

## 참고 자료

- [예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/mlops-101/ko)

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Docker — Dockerfile best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [BentoML](https://docs.bentoml.com/)
- [Seldon Core](https://docs.seldon.io/projects/seldon-core/en/latest/)

Tags: MLOps, Deployment, FastAPI, Docker, DataScience
