---
title: "바이브코딩을 위한 MLOps 기초 (6/10): 배포한 모델이 지금 잘 동작하고 있는지 어떻게 알까 — 모델 모니터링"
series: mlops-101
episode: 6
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- MLOps
- 모델모니터링
- Prometheus
- Observability
seo_description: "바이브코딩으로 배포한 AI 모델이 지금도 잘 동작하고 있는지 확인하려면 모니터링이 필요합니다. Prometheus와 예측 로그로 시작하는 방법을 소개합니다."
---

# 바이브코딩을 위한 MLOps 기초 (6/10): 배포한 모델이 지금 잘 동작하고 있는지 어떻게 알까 — 모델 모니터링

이 글은 바이브코딩을 위한 MLOps 기초 시리즈의 6번째 글입니다.

AI가 만든 모델을 배포하고 일주일이 지났습니다. 서버는 살아 있었습니다. 요청도 처리되고 있었습니다. 그런데 팀장이 "요즘 추천이 이상한 것 같다"고 했습니다. 로그를 확인해보니 예측 결과가 일주일 전부터 한쪽으로 쏠리고 있었습니다. 언제부터인지, 왜인지, 어느 정도 심각한지 아무것도 몰랐습니다. 사용자가 먼저 느꼈습니다.

바이브코딩에서 AI는 모델을 만들고 배포하는 코드까지 도와줍니다. 그런데 그 다음이 없습니다. 배포 후에 모델이 잘 동작하고 있는지, 지연 시간이 이상하지 않은지, 예측 분포가 바뀌고 있는지 알려면 모니터링 코드가 따로 필요합니다.

모델 모니터링은 서버가 살아 있는지 확인하는 게 아닙니다. 지금 이 모델이 정상적인 예측을 하고 있는지, 시스템 메트릭, 모델 메트릭, 비즈니스 메트릭이 함께 정상 범위 안에 있는지를 자동으로 감시하는 일입니다. 사람이 대시보드를 열어 확인하는 것은 모니터링이 아니라 점검입니다.

> 모델이 서버에서 살아 있다는 것과, 올바른 예측을 하고 있다는 것은 다릅니다. 모니터링이 없으면 그 차이를 사용자가 먼저 알게 됩니다.

---

## 이 글에서 다룰 문제
- 정확도만 봐서는 왜 운영 문제를 너무 늦게 알게 될까요?
- 메트릭, 로그, 트레이스는 무엇이 다를까요?
- Prometheus와 Grafana는 모델 운영에서 어떤 역할을 할까요?
- 모니터링 없이 배포하면 어떤 상황이 반복될까요?
- 바이브코딩 프로젝트에서 모니터링을 최소한 어떻게 시작할까요?

## 모니터링 신호 비교

| 신호 유형 | 예시 | 왜 중요한가 |
|---|---|---|
| 시스템 메트릭 | 지연 시간, 오류율, 처리량 | 서버 이상을 가장 빨리 감지 |
| 모델 메트릭 | 예측 클래스 분포, 신뢰도 평균 | 모델 동작 이상 조기 탐지 |
| 비즈니스 메트릭 | 클릭률, 전환율, 이탈률 | 실제 비즈니스 영향 측정 |

바이브코딩 프로젝트에서는 시스템 메트릭과 예측 분포 모니터링부터 시작하는 것이 가장 현실적입니다.

## AI와 MLOps 작업할 때 알아야 할 핵심 개념

- **메트릭**: 시간에 따라 쌓이는 숫자 시계열입니다. (예: 초당 요청 수, p95 지연 시간)
- **로그**: 개별 이벤트를 텍스트로 남긴 기록입니다. (예: 예측 요청/응답 내용)
- **SLO**: "99% 요청이 200ms 이내여야 한다"처럼 측정 가능한 서비스 목표입니다.
- **알림**: 임계값을 넘었을 때 사람이나 자동화에 전달되는 신호입니다.
- **예측 드리프트**: 모델이 내는 예측값 분포가 시간에 따라 변하는 현상입니다.

## Before / After

**Before**: 사용자가 "추천이 이상해요"라고 말해야 문제를 알게 됩니다. 언제부터인지, 어느 정도인지, 왜인지 모릅니다.

**After**: 예측 클래스 분포가 이상하게 쏠리기 시작하면 알림이 슬랙에 들어옵니다. 언제부터 시작됐는지 그래프로 확인할 수 있습니다.

## FastAPI 모델에 모니터링 붙이기

AI가 만든 FastAPI 서버에 모니터링을 추가하는 최소 예제입니다.

```python
from fastapi import FastAPI
from pydantic import BaseModel
import pickle, time, logging
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# 간단한 인메모리 메트릭 수집 (실운영에서는 Prometheus 사용)
prediction_counts = Counter()
latency_history = []

class PredictRequest(BaseModel):
    x: float

@app.post("/predict")
def predict(req: PredictRequest):
    start = time.time()
    pred = int(model.predict([[req.x]])[0])
    latency_ms = (time.time() - start) * 1000

    # 예측 분포와 지연 시간을 기록합니다
    prediction_counts[pred] += 1
    latency_history.append(latency_ms)

    logger.info({
        "x": req.x,
        "prediction": pred,
        "latency_ms": round(latency_ms, 2)
    })
    return {"prediction": pred}

@app.get("/metrics/summary")
def metrics_summary():
    total = sum(prediction_counts.values())
    avg_latency = sum(latency_history) / len(latency_history) if latency_history else 0
    return {
        "total_predictions": total,
        "prediction_distribution": dict(prediction_counts),
        "avg_latency_ms": round(avg_latency, 2),
        "p95_latency_ms": sorted(latency_history)[int(len(latency_history) * 0.95)] if latency_history else 0
    }
```

`/metrics/summary`에서 예측 분포와 지연 시간을 확인할 수 있습니다. 예측 분포가 한쪽으로 너무 쏠리면 모델 이상 신호입니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| 서버 생존 확인만 모니터링 | 모델 이상은 서버가 살아있어도 발생 | 예측 분포와 지연 시간도 추적 |
| 정확도 하락만 기다림 | 라벨이 늦게 생기면 모니터링 의미 없음 | 입력 분포 변화를 먼저 감지 |
| 로그는 있지만 알림이 없음 | 사람이 직접 확인하는 건 모니터링 아님 | 임계값 초과 시 자동 알림 설정 |
| 비즈니스 메트릭 연결 안 함 | 모델 지표가 좋아도 비즈니스 효과 모름 | 클릭률, 전환율 등과 함께 추적 |

## AI에게 모니터링 요청하는 팁

모니터링 코드를 AI에게 요청할 때 이 정보를 함께 주면 좋습니다.

1. **모니터링 도구 명시**: "Prometheus 메트릭 엔드포인트를 FastAPI에 추가해주세요"
2. **감시할 지표 지정**: "예측 클래스별 분포와 p95 지연 시간을 추적해주세요"
3. **알림 조건 전달**: "지연 시간이 500ms를 초과하면 로그에 경고를 남겨주세요"
4. **예측 로그 형식**: "각 요청의 입력, 출력, 타임스탬프를 JSON으로 기록해주세요"

## 운영 체크리스트
- [ ] 예측 결과가 로그에 남습니다
- [ ] 지연 시간을 측정하고 있습니다
- [ ] 예측 분포를 추적하고 있습니다
- [ ] 임계값 초과 시 알림이 갑니다
- [ ] 모니터링 대시보드나 요약 엔드포인트가 있습니다

## 처음 질문으로 돌아가기

- **정확도만 봐서는 왜 운영 문제를 너무 늦게 알게 될까요?**
  - 정확도를 측정하려면 정답 라벨이 필요한데, 그 라벨이 만들어지는 데 시간이 걸립니다. 반면 입력 분포 변화와 지연 시간은 즉시 감지 가능합니다.
- **메트릭, 로그, 트레이스는 무엇이 다를까요?**
  - 메트릭은 숫자 시계열, 로그는 이벤트 텍스트, 트레이스는 요청이 여러 서비스를 거치는 경로입니다. 모두 다른 문제를 진단합니다.
- **Prometheus와 Grafana는 모델 운영에서 어떤 역할을 할까요?**
  - Prometheus는 메트릭을 수집하고, Grafana는 그 메트릭을 시각화합니다. FastAPI에서 `/metrics` 엔드포인트로 메트릭을 노출하면 Prometheus가 주기적으로 수집합니다.
- **모니터링 없이 배포하면 어떤 상황이 반복될까요?**
  - 문제를 사용자가 먼저 발견하고, 언제부터 이상했는지 알 수 없고, 원인을 좁히는 데 오래 걸립니다.
- **바이브코딩 프로젝트에서 모니터링을 최소한 어떻게 시작할까요?**
  - 예측 결과를 JSON 로그로 남기는 것부터 시작하세요. 그것만으로도 이상 징후를 추적할 수 있습니다.

## 정리

바이브코딩에서 AI가 배포까지 도와줬다고 끝이 아닙니다. 배포 후 모델이 잘 동작하고 있는지 자동으로 감시하는 체계가 없으면, 문제를 항상 사용자가 먼저 발견합니다. 예측 분포와 지연 시간을 로그와 메트릭으로 남기고, 임계값 초과 시 알림을 받는 것이 최소한의 시작입니다. 다음 글에서는 모델이 갑자기 이상해지는 더 깊은 이유, 데이터 드리프트와 모델 드리프트를 다룹니다.

## 참고 자료
### 공식 문서
- [Prometheus](https://prometheus.io/docs/introduction/overview/)
- [Grafana](https://grafana.com/docs/)
### 관련 시리즈
- [DevOps 101](../../devops-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 MLOps 기초 (1/10): AI 모델을 서비스로 올리려면 MLOps가 왜 필요한가](./01-what-is-mlops.md)
- [바이브코딩을 위한 MLOps 기초 (2/10): AI가 학습을 여러 번 돌렸는데 뭐가 제일 좋았는지 — 실험 관리](./02-experiment-tracking.md)
- [바이브코딩을 위한 MLOps 기초 (3/10): 어제 데이터랑 오늘 데이터가 달라졌다 — 데이터 버전 관리](./03-data-versioning.md)
- [바이브코딩을 위한 MLOps 기초 (4/10): AI가 만든 학습 코드를 자동으로 돌리려면 — 학습 파이프라인](./04-training-pipeline.md)
- [바이브코딩을 위한 MLOps 기초 (5/10): AI 모델을 API로 배포하는 가장 빠른 방법 — 모델 배포](./05-model-deployment.md)
- **바이브코딩을 위한 MLOps 기초 (6/10): 배포한 모델이 지금 잘 동작하고 있는지 어떻게 알까 — 모델 모니터링 (현재 글)**
- [바이브코딩을 위한 MLOps 기초 (7/10): 모델이 갑자기 이상해진 이유 — 데이터 드리프트와 모델 드리프트](./07-data-and-model-drift.md)
- [바이브코딩을 위한 MLOps 기초 (8/10): 언제 모델을 다시 학습시켜야 할까 — 재학습](./08-retraining.md)
- [바이브코딩을 위한 MLOps 기초 (9/10): 학습과 서빙에서 피처가 달라지면 — 피처 스토어](./09-feature-store.md)
- [바이브코딩을 위한 MLOps 기초 (10/10): 조각들을 하나의 운영 루프로 — 운영 가능한 ML 시스템](./10-production-ml-system.md)

<!-- toc:end -->
Tags: 바이브코딩, MLOps, 모델모니터링, Prometheus, Observability
