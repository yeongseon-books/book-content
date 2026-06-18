---
title: "바이브코딩을 위한 MLOps 기초 (2/10): AI가 학습을 여러 번 돌렸는데 뭐가 제일 좋았는지 — 실험 관리"
series: mlops-101
episode: 2
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- MLOps
- 실험관리
- MLflow
- Reproducibility
seo_description: "바이브코딩으로 AI와 함께 모델을 여러 번 돌릴 때 실험을 추적하지 않으면 무슨 일이 생기는지, MLflow로 실험 관리를 시작하는 방법을 소개합니다."
---

# 바이브코딩을 위한 MLOps 기초 (2/10): AI가 학습을 여러 번 돌렸는데 뭐가 제일 좋았는지 — 실험 관리

이 글은 바이브코딩을 위한 MLOps 기초 시리즈의 2번째 글입니다.

AI에게 "정확도 더 높여줘"라고 했더니 파라미터를 바꿔가며 다섯 번을 돌렸습니다. 각 결과를 슬랙에 붙여 넣었고, 제일 좋은 게 뭔지 확인하려고 스크롤을 올리다 보니 어느 게 어느 파라미터였는지 이미 알 수 없었습니다. 결국 "아까 그것 중에 제일 좋은 걸 다시 돌려줘"라고 AI에게 부탁했는데, 같은 결과가 나오지 않았습니다.

바이브코딩 시대에 AI는 실험을 빠르게 많이 돌릴 수 있습니다. 그런데 그 실험들이 기록되지 않으면, 빠르게 많은 걸 잃어버리는 것이나 마찬가지입니다. 슬랙 메시지, 노트북 셀, 변수명에 날짜가 들어간 파일 이름. 이것들이 유일한 실험 기록이라면 AI와 협업하는 속도가 빨라질수록 기억의 혼란도 빨라집니다.

실험 관리는 "모든 run을 저장하자"가 아닙니다. 나중에 어떤 파라미터 조합으로 그 결과가 나왔는지, 어느 데이터 버전으로 돌린 건지 다시 찾을 수 있어야 AI와의 반복 실험이 실제 자산이 됩니다. MLflow 같은 도구 하나로 이 문제를 구조적으로 해결할 수 있습니다.

> AI가 실험을 빠르게 돌릴수록, 기록 없이는 그 결과들이 더 빠르게 사라집니다.

---

## 이 글에서 다룰 문제
- AI와 실험을 여러 번 돌릴 때 기록이 없으면 왜 같은 모델을 다시 만들기 어려울까요?
- 파라미터, 메트릭, 아티팩트 중 무엇을 반드시 남겨야 할까요?
- MLflow에서 experiment와 run은 어떤 관계로 이해하면 좋을까요?
- AI가 선택한 모델이 최선인지 어떻게 검증할 수 있을까요?
- 실험 관리를 잘못하면 어떤 문제가 반복될까요?

## 실험 추적 도구 비교

| 도구 | 무료 한도 | 특징 | 시작 난이도 |
|---|---|---|---|
| MLflow | 무제한 (셀프 호스팅) | 오픈소스, 로컬 바로 시작 가능 | 낮음 |
| W&B | 개인 프로젝트 무료 | UI 우수, 협업 기능 강력 | 낮음 |
| Neptune | 200시간 무료 | 모델 비교 UI 우수 | 보통 |

바이브코딩 시작 단계에서는 MLflow가 가장 빠르게 시작할 수 있습니다. `pip install mlflow` 한 줄로 로컬에서 바로 사용 가능합니다.

## AI와 MLOps 작업할 때 알아야 할 핵심 개념

- **Experiment**: 관련 run들을 모아 두는 논리적 상자입니다.
- **Run**: 학습 한 번의 실행 단위입니다.
- **Param**: 학습 전에 정해지는 입력 값입니다. (예: learning_rate, max_depth)
- **Metric**: 실행 뒤 측정된 결과 값입니다. (예: val_auc, val_f1)
- **Artifact**: 모델 파일, 그래프처럼 파일 형태로 남는 결과물입니다.

## Before / After

**Before**: `model_final_v2_really.pkl` 파일명이 사실상 유일한 실험 기록입니다. AI가 돌린 다섯 가지 조합 중 어느 게 이 파일인지 기억이 가물가물합니다.

**After**: MLflow run 목록이 남고, 파라미터와 메트릭을 나란히 비교할 수 있습니다. AI에게 "run a1b2에서 val_auc가 제일 높았던 조합으로 다시 학습시켜줘"라고 정확하게 요청할 수 있습니다.

## MLflow로 AI 실험 추적 시작하기

AI가 만든 학습 코드에 MLflow 추적을 붙이는 최소 예제입니다.

```python
import mlflow
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import hashlib, json

mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("vibe-coding-demo")

# 데이터 버전 계산
X, y = make_classification(n_samples=1000, random_state=42)
data_repr = json.dumps({"n": len(X), "seed": 42})
data_version = hashlib.sha1(data_repr.encode()).hexdigest()[:8]

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=0)

# AI가 제안한 파라미터 조합들을 run으로 기록합니다
for C in [0.1, 1.0, 10.0]:
    with mlflow.start_run():
        mlflow.log_param("C", C)
        mlflow.log_param("data_version", data_version)

        model = LogisticRegression(C=C, max_iter=1000).fit(X_train, y_train)

        mlflow.log_metric("val_acc", model.score(X_val, y_val))
        mlflow.log_metric("train_acc", model.score(X_train, y_train))

print("실험 기록 완료. mlflow ui 로 확인하세요.")
```

이제 `mlflow ui`를 실행하면 세 가지 조합을 나란히 비교할 수 있습니다. AI에게 "이 중에 val_acc가 가장 높은 조합으로 재학습해줘"라고 말할 때 근거가 생깁니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| 성공한 run만 기록 | 실패 실험이 빠지면 탐색 과정 소실 | 실패 run도 삭제하지 않습니다 |
| 데이터 버전 미기록 | 메트릭이 높아진 이유를 설명 못 함 | data_version을 param으로 남깁니다 |
| 팀원마다 다른 키 이름 | 비교 화면이 쓸모없어짐 | 팀 공통 키 이름을 먼저 정합니다 |
| AI에게 베스트 run을 기억에 의존 | 재현 불가 | run ID를 레지스트리에 연결합니다 |

## AI에게 실험 관리 요청하는 팁

실험 추적이 포함된 코드를 AI에게 요청할 때 이 정보를 함께 주면 좋습니다.

1. **추적 도구 명시**: "MLflow를 사용합니다. 로컬 파일 기반으로 설정해주세요"
2. **기록할 항목 지정**: "파라미터, val_auc, 모델 파일을 함께 기록해주세요"
3. **비교 기준 전달**: "val_auc 기준으로 상위 3개 run을 찾는 코드도 추가해주세요"
4. **데이터 버전 포함**: "데이터 해시를 param으로 남겨주세요"

## 운영 체크리스트
- [ ] 모든 학습 실행이 run으로 기록됩니다
- [ ] 데이터 버전이 param으로 함께 남습니다
- [ ] 실패한 run도 삭제하지 않습니다
- [ ] 팀 공통 메트릭 키 이름 규약이 있습니다
- [ ] 베스트 모델 선택이 run 비교를 기반으로 이루어집니다

## 처음 질문으로 돌아가기

- **AI와 실험을 여러 번 돌릴 때 기록이 없으면 왜 같은 모델을 다시 만들기 어려울까요?**
  - 파라미터, 데이터 버전, 환경이 모두 달라질 수 있기 때문입니다. 기록이 없으면 재현 대신 추측에 의존하게 됩니다.
- **파라미터, 메트릭, 아티팩트 중 무엇을 반드시 남겨야 할까요?**
  - 세 가지 모두 필요하지만 우선순위가 있다면 파라미터와 데이터 버전이 먼저입니다. 이 두 가지가 없으면 재현이 불가능합니다.
- **MLflow에서 experiment와 run은 어떤 관계로 이해하면 좋을까요?**
  - experiment는 "이탈 예측 프로젝트"처럼 큰 주제, run은 그 안에서 파라미터 한 조합을 돌린 한 번의 실행입니다.
- **AI가 선택한 모델이 최선인지 어떻게 검증할 수 있을까요?**
  - run 비교 화면에서 val_auc, val_f1, 학습 시간을 나란히 놓고 성능과 비용을 함께 판단해야 합니다. 숫자 하나만 보면 안 됩니다.
- **실험 관리를 잘못하면 어떤 문제가 반복될까요?**
  - 같은 실수를 반복하고, 왜 이 모델을 선택했는지 설명할 수 없고, 더 좋은 모델을 다시 재현할 수 없는 상황이 반복됩니다.

## 정리

바이브코딩에서 AI는 실험을 빠르게 많이 돌려줍니다. 그 속도를 진짜 이점으로 만들려면, 기록이 없으면 빠른 실험이 빠른 망각이 됩니다. MLflow run 하나가 파라미터, 메트릭, 데이터 버전을 묶어주면, AI와의 반복 실험이 팀의 운영 자산이 됩니다. 다음 글에서는 그 기록을 더 오래 보존하는 데이터 버전 관리를 다룹니다.

## 참고 자료
### 공식 문서
- [MLflow — Tracking](https://mlflow.org/docs/latest/tracking.html)
- [Weights & Biases](https://docs.wandb.ai/)
### 관련 시리즈
- [Machine Learning 101](../../machine-learning-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 MLOps 기초 (1/10): AI 모델을 서비스로 올리려면 MLOps가 왜 필요한가](./01-what-is-mlops.md)
- **바이브코딩을 위한 MLOps 기초 (2/10): AI가 학습을 여러 번 돌렸는데 뭐가 제일 좋았는지 — 실험 관리 (현재 글)**
- [바이브코딩을 위한 MLOps 기초 (3/10): 어제 데이터랑 오늘 데이터가 달라졌다 — 데이터 버전 관리](./03-data-versioning.md)
- [바이브코딩을 위한 MLOps 기초 (4/10): AI가 만든 학습 코드를 자동으로 돌리려면 — 학습 파이프라인](./04-training-pipeline.md)
- [바이브코딩을 위한 MLOps 기초 (5/10): AI 모델을 API로 배포하는 가장 빠른 방법 — 모델 배포](./05-model-deployment.md)
- [바이브코딩을 위한 MLOps 기초 (6/10): 배포한 모델이 지금 잘 동작하고 있는지 어떻게 알까 — 모델 모니터링](./06-model-monitoring.md)
- [바이브코딩을 위한 MLOps 기초 (7/10): 모델이 갑자기 이상해진 이유 — 데이터 드리프트와 모델 드리프트](./07-data-and-model-drift.md)
- [바이브코딩을 위한 MLOps 기초 (8/10): 언제 모델을 다시 학습시켜야 할까 — 재학습](./08-retraining.md)
- [바이브코딩을 위한 MLOps 기초 (9/10): 학습과 서빙에서 피처가 달라지면 — 피처 스토어](./09-feature-store.md)
- [바이브코딩을 위한 MLOps 기초 (10/10): 조각들을 하나의 운영 루프로 — 운영 가능한 ML 시스템](./10-production-ml-system.md)

<!-- toc:end -->
Tags: 바이브코딩, MLOps, 실험관리, MLflow, Reproducibility
