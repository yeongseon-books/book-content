---
title: "바이브코딩을 위한 머신러닝 기초 (10/10): AI와 함께 ML 프로젝트 처음부터 끝까지"
series: machine-learning-101
episode: 10
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- MachineLearning
- AI코딩
- ML프로젝트
- Pipeline
seo_description: "바이브코딩 시대, AI와 함께 ML 프로젝트를 문제 정의부터 배포, 모니터링까지 처음부터 끝까지 완성하는 방법을 정리합니다"
---

# 바이브코딩을 위한 머신러닝 기초 (10/10): AI와 함께 ML 프로젝트 처음부터 끝까지

이 글은 바이브코딩을 위한 머신러닝 기초 시리즈의 10번째 글입니다.

노트북에서 정확도 93%가 나왔습니다. 흥분해서 팀에 공유했더니 "이거 실제로 쓸 수 있어요?"라는 질문이 돌아왔습니다. 당황했습니다. 모델 파일을 어떻게 저장하는지, 새 데이터가 들어오면 어떻게 예측하는지, 나중에 모델 성능이 떨어지면 어떻게 알 수 있는지 전혀 생각해 보지 않았던 것입니다.

바이브코딩에서 AI는 코드를 빠르게 만들어 주지만, 프로젝트의 완성은 모델 정확도가 아니라 전체 루프입니다. 문제 정의부터 시작해서 데이터 준비, 모델 학습, 평가, 저장, 배포, 모니터링까지 이어지는 흐름을 AI와 함께 처음부터 끝까지 만드는 방법을 이 글에서 정리합니다.

이 시리즈 전체에서 배운 개념들, train/test split, 올바른 지표 선택, 과적합 진단, Pipeline 구성이 모두 이 마지막 글에서 하나의 프로젝트로 합쳐집니다. 노트북에서 좋은 점수를 얻는 것과 실제로 동작하는 ML 시스템을 만드는 것은 다른 일입니다.

> ML 프로젝트는 직선이 아닌 루프입니다. 좋은 점수를 얻는 것이 끝이 아니라, 그 모델이 실제 환경에서 계속 잘 동작하는지 지켜보는 것까지가 프로젝트입니다.

---

## 이 글에서 다룰 문제
- 노트북의 ML 코드를 실제 사용 가능한 형태로 만들려면 무엇이 필요한가요?
- Pipeline을 쓰면 왜 전처리 누수를 원천 차단할 수 있나요?
- 모델 파일을 저장하고 다시 불러올 때 주의할 점은 무엇인가요?
- 배포 후 모델 성능이 떨어지는 걸 어떻게 감지하나요?
- AI와 함께 ML 프로젝트 전체를 만드는 단계별 요청 방법은?

## ML 프로젝트 7단계

| 단계 | 내용 | AI 요청 핵심 |
|---|---|---|
| 1. 문제 정의 | X와 y 결정, 성공 기준 설정 | "이 문제의 ML 유형과 지표 제안해줘" |
| 2. 데이터 준비 | 분할, 전처리, 누수 점검 | "train/test split + 전처리 Pipeline 만들어줘" |
| 3. 베이스라인 | 간단한 모델로 기준점 설정 | "로지스틱 회귀로 베이스라인 잡아줘" |
| 4. 모델 개선 | 다른 모델 시도, 튜닝 | "랜덤 포레스트로 교체해서 비교해줘" |
| 5. 평가 | 올바른 지표로 검증 | "classification_report + ROC-AUC 출력해줘" |
| 6. 저장 | Pipeline으로 저장 | "joblib으로 Pipeline 저장하는 코드 만들어줘" |
| 7. 모니터링 | 배포 후 성능 추적 | "입력 분포 변화 감지 코드 만들어줘" |

## Pipeline: 바이브코딩 ML의 핵심 도구

Pipeline이 없으면 전처리와 모델이 따로 놀아서 배포 후 문제가 생깁니다. Pipeline으로 묶으면 저장, 로드, 예측이 모두 일관되게 동작합니다.

```python
# AI에게 요청: "전처리와 모델을 Pipeline으로 묶어줘"
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_breast_cancer

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(max_iter=2000))
])

pipe.fit(Xtr, ytr)
print("Test score:", pipe.score(Xte, yte))
```

Pipeline의 장점: 새 데이터가 들어오면 `pipe.predict(new_data)` 한 줄로 전처리와 예측이 동시에 일어납니다. 스케일러를 따로 적용할 필요가 없습니다.

## Before / After

**Before**: 노트북에서 스케일러 따로, 모델 따로, 정확도 93%. 모델만 저장했다가 나중에 불러왔을 때 스케일러를 잊어서 완전히 다른 결과가 나왔습니다.

**After**: "전처리와 모델을 Pipeline으로 묶고, joblib으로 저장하는 전체 코드 만들어줘"라고 요청해서 파이프라인 하나만 저장/로드하면 되는 구조를 만들었습니다.

## 모델 저장과 재현성

```python
# AI에게 요청: "모델 저장과 로드 코드 만들어줘"
import joblib

# 저장
joblib.dump(pipe, "model.joblib")
print("모델 저장 완료")

# 로드
loaded_pipe = joblib.load("model.joblib")
print("로드 후 점수:", loaded_pipe.score(Xte, yte))

# 동일해야 함
assert pipe.score(Xte, yte) == loaded_pipe.score(Xte, yte)
```

**재현성을 위해 함께 기록해야 하는 것들:**
- `random_state=42` (분할과 모델 모두)
- Python 버전: `python --version`
- scikit-learn 버전: `sklearn.__version__`
- 데이터 날짜/버전

## Drift 모니터링: 배포 후 성능 감지

```python
# AI에게 요청: "입력 데이터 분포 변화 감지 코드 만들어줘"
import numpy as np

# 기준: 훈련 데이터의 통계
train_mean = Xtr.mean(axis=0)
train_std = Xtr.std(axis=0)

def check_drift(new_data, threshold=2.0):
    """새 데이터가 훈련 분포에서 얼마나 벗어났는지 확인"""
    z_scores = np.abs((new_data.mean(axis=0) - train_mean) / train_std)
    drifted_features = np.where(z_scores > threshold)[0]
    if len(drifted_features) > 0:
        print(f"Drift 감지! 피처 인덱스: {drifted_features}")
        print(f"Z-scores: {z_scores[drifted_features]}")
    else:
        print("분포 변화 없음")

# 새 데이터 확인
check_drift(Xte)
```

AI에게 "정기적으로 모델 성능을 체크하는 코드도 만들어줘"라고 추가 요청하면 배포 후 모니터링 시스템을 완성할 수 있습니다.

## AI와 ML 프로젝트 전체 만들기: 단계별 요청

**1단계 - 문제 정의 요청:**
"이탈 고객 예측 프로젝트입니다. ML 유형을 결정해주고, 성공 지표로 뭘 써야 할지 제안해줘."

**2단계 - 데이터 준비 요청:**
"train/test split(20%, stratify, seed=42)과 StandardScaler를 Pipeline으로 묶는 코드 만들어줘. 데이터 누수 가능성도 확인해줘."

**3단계 - 베이스라인 요청:**
"로지스틱 회귀로 베이스라인 잡아줘. classification_report와 혼동 행렬 출력 포함."

**4단계 - 개선 요청:**
"랜덤 포레스트, 그래디언트 부스팅과 로지스틱 회귀를 5-fold 교차검증으로 비교해줘."

**5단계 - 최종 평가 요청:**
"최종 선택 모델로 테스트 세트 평가. ROC-AUC, PR-AUC, F1 모두 출력."

**6단계 - 저장 요청:**
"최종 Pipeline을 joblib으로 저장하고, 새 데이터로 예측하는 예시 코드 포함."

**7단계 - 모니터링 요청:**
"입력 데이터 분포 변화를 감지하는 간단한 drift 체크 함수 만들어줘."

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| Pipeline 없이 스케일러 따로 저장 | 배포 후 전처리 불일치 | 전처리 + 모델 Pipeline으로 묶기 |
| 노트북 점수만 확인 후 "완료" | 재현성, 배포, 모니터링 미완 | 7단계 워크플로 체크리스트 확인 |
| 버전 기록 없이 모델 공유 | 나중에 재현 불가 | python, sklearn 버전 함께 기록 |
| 배포 후 모니터링 없음 | drift 발생 시 모름 | 최소한 입력 분포 변화 체크 |

## AI에게 ML 관련 질문하는 팁

**프로젝트 검토 요청:**
- "이 코드에서 실제 배포 시 문제가 생길 수 있는 부분 찾아줘"
- "전처리 누수 가능성이 있는지 확인해줘"
- "이 프로젝트를 팀원이 재현할 수 있도록 필요한 정보 목록 만들어줘"

**다음 단계 제안 요청:**
- "현재 모델의 성능을 더 높이려면 어떤 순서로 시도해야 할까요?"
- "이 모델을 실제 서비스에 올리려면 추가로 뭐가 필요할까요?"

## 운영 체크리스트
- [ ] 문제 정의: X, y, 성공 지표가 명확합니다
- [ ] 데이터: train/test split + stratify + random_state 설정됨
- [ ] 전처리: Pipeline으로 묶여서 누수 없음
- [ ] 평가: 비즈니스 맥락에 맞는 지표 사용
- [ ] 저장: joblib으로 Pipeline 저장, 버전 기록
- [ ] 모니터링: 입력 분포 변화 감지 방법 마련

## 처음 질문으로 돌아가기

- **노트북 ML 코드를 실제 사용 가능한 형태로 만들려면?**
  - 전처리와 모델을 Pipeline으로 묶고, joblib으로 저장하고, 버전을 기록하는 것이 최소 조건입니다.
- **Pipeline을 쓰면 왜 전처리 누수를 막을 수 있나요?**
  - Pipeline은 fit할 때 훈련 데이터로만 스케일러를 학습하고, predict할 때 새 데이터를 자동으로 변환합니다. 따로 관리하면 실수할 수 있지만 Pipeline은 구조적으로 막아 줍니다.
- **모델 저장/로드 시 주의할 점은?**
  - 스케일러 따로, 모델 따로 저장하지 말고 Pipeline을 통째로 저장합니다. Python과 scikit-learn 버전이 달라지면 로드가 안 될 수 있으므로 버전을 함께 기록합니다.
- **배포 후 성능 저하를 어떻게 감지하나요?**
  - 입력 데이터의 평균과 표준편차를 훈련 데이터와 비교해서 분포가 크게 달라지면 경고를 내는 drift 체크를 구현합니다.
- **AI와 ML 프로젝트를 처음부터 끝까지 만들 때 가장 중요한 것은?**
  - 각 단계를 하나씩 명확하게 요청하는 것입니다. "ML 프로젝트 만들어줘" 한 번보다 7단계를 순서대로 요청하면 훨씬 완성도 높은 결과가 나옵니다.

## 정리

바이브코딩을 위한 머신러닝 기초 시리즈를 마칩니다. AI와 ML 작업을 할 때 핵심은 각 단계를 이해하고 명확하게 요청하는 것입니다. 문제 정의부터 Pipeline 구성, 올바른 지표 선택, 과적합 진단, 모델 저장, 모니터링까지 7단계 체크리스트를 갖추면 AI가 만드는 ML 코드를 신뢰하고 활용할 수 있는 수준이 됩니다. 노트북에서 좋은 점수를 얻는 것과 실제로 동작하는 ML 시스템은 다르다는 것, 그 차이를 아는 것이 바이브코딩 시대의 ML 역량입니다.

## 참고 자료
### 공식 문서
- [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
- [Google ML Crash Course](https://developers.google.com/machine-learning/crash-course)
### 관련 시리즈
- [Data Science 101](../../data-science-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 머신러닝 기초 (1/10): ML이 뭔지 알아야 AI에게 제대로 시킬 수 있다](./01-what-is-machine-learning.md)
- [바이브코딩을 위한 머신러닝 기초 (2/10): 지도학습 vs 비지도학습 — AI에게 어떤 유형인지 말해줘야](./02-supervised-unsupervised.md)
- [바이브코딩을 위한 머신러닝 기초 (3/10): AI가 전체 데이터로 학습시켰다 — train/test split이 왜 필요한지](./03-training-test-split.md)
- [바이브코딩을 위한 머신러닝 기초 (4/10): AI가 선형 회귀를 썼는데 맞는 선택인지 판단하려면](./04-linear-regression.md)
- [바이브코딩을 위한 머신러닝 기초 (5/10): AI가 로지스틱 회귀를 쓴 이유를 이해하려면](./05-logistic-regression.md)
- [바이브코딩을 위한 머신러닝 기초 (6/10): AI가 랜덤 포레스트를 추천했다 — 트리 모델 이해하기](./06-tree-models.md)
- [바이브코딩을 위한 머신러닝 기초 (7/10): AI가 KMeans를 썼는데 K를 어떻게 정할지](./07-clustering.md)
- [바이브코딩을 위한 머신러닝 기초 (8/10): AI 모델이 훈련에서만 잘 된다 — 과적합 이해하기](./08-overfitting.md)
- [바이브코딩을 위한 머신러닝 기초 (9/10): AI가 "정확도 95%"라고 했는데 진짜 좋은 건지 — 평가 지표](./09-evaluation-metrics.md)
- **AI와 함께 ML 프로젝트 처음부터 끝까지 (현재 글)**

<!-- toc:end -->
Tags: 바이브코딩, MachineLearning, AI코딩, ML프로젝트, Pipeline
