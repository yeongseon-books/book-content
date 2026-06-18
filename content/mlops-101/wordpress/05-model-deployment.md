---
title: "바이브코딩을 위한 MLOps 기초 (5/10): AI 모델을 API로 배포하는 가장 빠른 방법 — 모델 배포"
series: mlops-101
episode: 5
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- MLOps
- 모델배포
- FastAPI
- Docker
seo_description: "바이브코딩으로 AI가 만든 모델을 FastAPI와 Docker로 감싸고, 버전 관리와 롤백 계획까지 갖춘 배포를 하는 방법을 소개합니다."
---

# 바이브코딩을 위한 MLOps 기초 (5/10): AI 모델을 API로 배포하는 가장 빠른 방법 — 모델 배포

이 글은 바이브코딩을 위한 MLOps 기초 시리즈의 5번째 글입니다.

AI에게 "이 모델을 API로 배포해줘"라고 했더니 FastAPI 코드가 나왔습니다. 로컬에서 잘 돌았습니다. 서버에 올렸더니 깨졌습니다. 로컬에는 Python 3.11이 설치되어 있었고 서버에는 3.9가 있었습니다. 라이브러리 버전도 달랐습니다. 패닉 상태에서 서버 환경을 맞추느라 한 시간이 걸렸습니다. 겨우 올렸더니 이번에는 "새 버전으로 교체해줘"라는 요청이 들어왔습니다. 교체하고 나서 뭔가 이상했는데, 직전 버전으로 돌아가는 방법을 몰랐습니다.

바이브코딩에서 AI는 멋진 FastAPI 서버 코드를 금방 만들어 줍니다. 그런데 그 코드를 어떤 환경에서 실행할지, 어떤 버전이 지금 서비스 중인지, 이상할 때 어떻게 돌아갈지가 없으면 배포는 매번 도박이 됩니다.

모델 배포의 핵심은 파일을 서버에 올리는 일이 아닙니다. 재현 가능한 실행 환경을 만들고, 버전을 태그로 관리하고, 안전하게 전환하며, 이상 시 롤백할 수 있는 구조를 만드는 것입니다. Docker 이미지가 이 문제를 해결합니다.

> AI가 만든 FastAPI 코드는 로컬에서 돌아갑니다. 그것이 프로덕션에서도 동일하게 돌아가게 만드는 건 Docker와 버전 관리가 합니다.

---

## 이 글에서 다룰 문제
- AI가 만든 모델 파일을 어떻게 사용자 요청에 연결할 수 있을까요?
- 온라인 추론과 배치 추론은 어떤 차이로 이해하면 좋을까요?
- FastAPI와 Docker는 모델 배포에서 각각 어떤 역할을 할까요?
- 버전 태그 없이 배포하면 왜 위험할까요?
- 배포 후 이상이 생겼을 때 어떻게 빠르게 롤백할 수 있을까요?

## 모델 서빙 패턴 비교

| 패턴 | 응답 시간 | 처리량 | AI 프로젝트에서 언제 쓰나 |
|---|---|---|---|
| 실시간 추론 | ms~초 | 보통 | "사용자가 버튼 누르면 즉시 예측" |
| 배치 추론 | 분~시간 | 매우 높음 | "매일 밤 전체 고객 이탈 점수 계산" |
| 스트리밍 추론 | 초 이하 | 높음 | "로그가 들어올 때마다 이상 탐지" |

바이브코딩으로 만든 모델을 처음 배포한다면 대부분 실시간 추론(FastAPI)이나 배치 추론(스크립트 + cron)으로 시작합니다.

## AI와 MLOps 작업할 때 알아야 할 핵심 개념

- **온라인 추론**: 요청을 받으면 즉시 예측을 반환하는 방식입니다.
- **배치 추론**: 대량 데이터를 일정 주기로 처리하는 방식입니다.
- **Blue/Green**: 두 환경을 병렬로 두고 전환하는 배포 방식입니다.
- **Canary**: 소량 트래픽부터 새 버전에 보내는 방식입니다.
- **롤백**: 문제가 생겼을 때 이전 버전으로 되돌리는 절차입니다.

## Before / After

**Before**: 노트북에서 `predict()`를 직접 호출해서 결과를 확인합니다. 서버에 올리면 환경 차이로 깨지고, 새 버전을 올리면 이전 버전으로 돌아가는 방법이 없습니다.

**After**: Docker 이미지가 모델 + 코드 + 라이브러리 + 환경을 하나로 묶어줍니다. `model-api:1.0.0` 태그가 곧 버전 기록이 되고, 문제 시 `model-api:0.9.0`으로 즉시 롤백할 수 있습니다.

## FastAPI + Docker로 모델 배포하기

AI가 만들어 준 코드에 배포에 필요한 요소들을 추가하는 예제입니다.

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle, time, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Model API", version="1.0.0")

# 시작 시 한 번만 모델을 로드합니다
try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = None

class PredictRequest(BaseModel):
    x: float

@app.get("/healthz")
def health():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ok", "version": "1.0.0"}

@app.post("/predict")
def predict(req: PredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    start = time.time()
    pred = int(model.predict([[req.x]])[0])
    latency_ms = (time.time() - start) * 1000
    logger.info(f"pred={pred}, latency={latency_ms:.2f}ms")
    return {"prediction": pred, "latency_ms": round(latency_ms, 2)}
```

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY model.pkl .
COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# 버전 태그를 붙여서 빌드합니다
docker build -t model-api:1.0.0 .
docker run -p 8000:8000 model-api:1.0.0
curl -X POST localhost:8000/predict -H "Content-Type: application/json" -d '{"x": 2.5}'
```

`model-api:1.0.0`처럼 명확한 태그를 붙이면 "지금 어떤 버전이 살아 있는지", "문제 시 어떤 버전으로 롤백할지"가 명확해집니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| 버전 태그 없이 `latest`로 배포 | 어느 버전이 서비스 중인지 알 수 없음 | 날짜나 버전 번호로 태그 부여 |
| `requirements.txt` 버전 미고정 | 같은 코드인데 다른 환경이 만들어짐 | `pip freeze > requirements.txt` |
| 롤백 절차 미문서화 | 사고 시 되돌리는 시간만 길어짐 | 이전 버전 태그로 재배포 절차 작성 |
| 헬스 체크 없음 | 이상한 서버에 트래픽이 계속 들어옴 | `/healthz` 엔드포인트 필수 |
| 모델과 코드를 너무 강하게 결합 | 모델 교체가 전체 재배포로 번짐 | 모델 파일을 외부에서 로드하는 구조 |

## AI에게 배포 관련 요청하는 팁

모델 배포 코드를 AI에게 요청할 때 이 정보를 함께 주면 좋습니다.

1. **배포 방식 명시**: "FastAPI + Docker로 실시간 추론 API를 만들어주세요"
2. **헬스 체크 요구**: "/healthz 엔드포인트를 추가해주세요"
3. **로깅 요구**: "각 요청의 입력값, 예측 결과, 지연 시간을 로그로 남겨주세요"
4. **버전 관리 의도**: "모델 버전을 응답에 포함시켜주세요"

## 운영 체크리스트
- [ ] Dockerfile이 있습니다
- [ ] Docker 이미지에 버전 태그가 있습니다
- [ ] `/healthz` 헬스 체크 엔드포인트가 있습니다
- [ ] 입력 스키마 검증이 있습니다
- [ ] 롤백 절차가 문서화되어 있습니다

## 처음 질문으로 돌아가기

- **AI가 만든 모델 파일을 어떻게 사용자 요청에 연결할 수 있을까요?**
  - FastAPI로 HTTP 엔드포인트를 만들고, 모델 파일을 시작 시 로드해두면 요청마다 로딩 없이 빠르게 예측할 수 있습니다.
- **온라인 추론과 배치 추론은 어떤 차이로 이해하면 좋을까요?**
  - 온라인 추론은 "사용자가 요청하면 즉시 답하는 것", 배치 추론은 "모아서 한 번에 처리하는 것"입니다.
- **FastAPI와 Docker는 모델 배포에서 각각 어떤 역할을 할까요?**
  - FastAPI는 모델을 HTTP 인터페이스로 감싸고, Docker는 그 코드와 환경 전체를 재현 가능한 이미지로 묶습니다.
- **버전 태그 없이 배포하면 왜 위험할까요?**
  - 어떤 버전이 실행 중인지, 롤백할 때 어느 버전으로 가야 하는지 알 수 없습니다.
- **배포 후 이상이 생겼을 때 어떻게 빠르게 롤백할 수 있을까요?**
  - 이전 버전 이미지 태그로 재배포하는 것이 가장 빠릅니다. 그래서 직전 안정 버전 태그를 항상 알고 있어야 합니다.

## 정리

바이브코딩에서 AI가 만들어 준 FastAPI 코드는 좋은 출발점입니다. 거기에 Docker 이미지, 버전 태그, 헬스 체크, 롤백 계획을 더하면 그게 진짜 배포입니다. 배포는 모델을 노출하는 단계가 아니라 운영 위험을 제어하는 단계입니다. 다음 글에서는 배포된 모델이 지금 잘 동작하고 있는지 확인하는 모델 모니터링을 다룹니다.

## 참고 자료
### 공식 문서
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Docker — Dockerfile best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
### 관련 시리즈
- [Docker 101](../../docker-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 MLOps 기초 (1/10): AI 모델을 서비스로 올리려면 MLOps가 왜 필요한가](./01-what-is-mlops.md)
- [바이브코딩을 위한 MLOps 기초 (2/10): AI가 학습을 여러 번 돌렸는데 뭐가 제일 좋았는지 — 실험 관리](./02-experiment-tracking.md)
- [바이브코딩을 위한 MLOps 기초 (3/10): 어제 데이터랑 오늘 데이터가 달라졌다 — 데이터 버전 관리](./03-data-versioning.md)
- [바이브코딩을 위한 MLOps 기초 (4/10): AI가 만든 학습 코드를 자동으로 돌리려면 — 학습 파이프라인](./04-training-pipeline.md)
- **바이브코딩을 위한 MLOps 기초 (5/10): AI 모델을 API로 배포하는 가장 빠른 방법 — 모델 배포 (현재 글)**
- [바이브코딩을 위한 MLOps 기초 (6/10): 배포한 모델이 지금 잘 동작하고 있는지 어떻게 알까 — 모델 모니터링](./06-model-monitoring.md)
- [바이브코딩을 위한 MLOps 기초 (7/10): 모델이 갑자기 이상해진 이유 — 데이터 드리프트와 모델 드리프트](./07-data-and-model-drift.md)
- [바이브코딩을 위한 MLOps 기초 (8/10): 언제 모델을 다시 학습시켜야 할까 — 재학습](./08-retraining.md)
- [바이브코딩을 위한 MLOps 기초 (9/10): 학습과 서빙에서 피처가 달라지면 — 피처 스토어](./09-feature-store.md)
- [바이브코딩을 위한 MLOps 기초 (10/10): 조각들을 하나의 운영 루프로 — 운영 가능한 ML 시스템](./10-production-ml-system.md)

<!-- toc:end -->
Tags: 바이브코딩, MLOps, 모델배포, FastAPI, Docker
