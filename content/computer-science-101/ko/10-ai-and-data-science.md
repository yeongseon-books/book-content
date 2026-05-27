---
series: computer-science-101
episode: 10
title: "Computer Science 101 (10/10): AI와 데이터사이언스까지의 연결"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - AI
  - 데이터사이언스
  - 머신러닝
  - 통계
  - 진로
seo_description: CS 기초가 AI와 데이터사이언스에 어떻게 이어지는지와 다음 학습 경로를 정리합니다.
last_reviewed: '2026-05-12'
---

# Computer Science 101 (10/10): AI와 데이터사이언스까지의 연결

AI와 데이터사이언스는 갑자기 하늘에서 떨어진 별도 분야가 아닙니다. 데이터 표현, 알고리즘 비용, 메모리 계층, 데이터베이스, 엔지니어링 습관 위에 통계와 도메인 지식을 더한 결과에 가깝습니다.

이 글은 Computer Science 101 시리즈의 마지막 글입니다.

여기서는 머신러닝의 기본 구조를 훑고, 앞선 아홉 편이 AI/DS 실무와 어떻게 이어지는지 연결한 뒤, 다음에 무엇을 공부하면 좋을지 로드맵을 정리하겠습니다.

![Computer Science 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/10/10-01-concept-at-a-glance.ko.png)
*Computer Science 101 10장 흐름 개요*

## 먼저 던지는 질문

- 지금까지 배운 CS 기초가 AI와 데이터사이언스에서 어디에 직접 쓰일까요?
- 규칙 기반 시스템과 머신러닝 시스템은 무엇이 본질적으로 다를까요?
- 학습, 추론, 데이터 품질 검증은 왜 결국 계산과 시스템 문제일까요?

## 이 글에서 배울 것

- 머신러닝의 기본 구성요소와 흐름
- 규칙 기반 시스템과 ML 기반 시스템의 차이
- 앞선 아홉 편이 AI/DS와 연결되는 방식
- 다음 학습 로드맵을 설계하는 기준

## 왜 중요한가

AI는 마법이 아닙니다. 모델은 데이터로 학습되고, 추론은 행렬 연산이며, 그 모든 것은 결국 CPU·메모리·디스크 위에서 돌아갑니다. CS 기초가 단단할수록 AI 코드를 디버깅하고, 비용을 추정하고, 문제를 정의하는 능력이 빠르게 성장합니다.

> AI/DS = CS + 통계 + 도메인

도구는 빨리 변해도 기초는 오래 유효합니다.

## 한눈에 보는 개념

> 규칙 기반은 사람이 규칙을 적고, 머신러닝은 데이터로부터 규칙을 추론합니다.

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Machine learning | 데이터에서 패턴을 학습해 새 입력의 출력을 예측하는 기법 |
| Training | 데이터로부터 모델 파라미터를 추정하는 과정 |
| Inference | 학습된 모델로 새 입력의 출력을 계산하는 과정 |
| Feature | 모델이 다룰 수 있도록 숫자로 표현한 입력 정보 |
| Model | 입력에서 출력을 계산하는 파라미터 묶음 |
| Dataset | 학습·검증·평가에 사용하는 입력과 라벨의 집합 |

## 적용 전후 비교
**Before — 규칙 기반 분류:**

```python
def classify_email(text: str) -> str:
    """A spam classifier with hand-written rules."""
    spam_words = {"free", "winner", "click now", "discount"}
    score = sum(word in text for word in spam_words)
    return "spam" if score >= 2 else "ham"

print(classify_email("free coupon, you are the winner"))   # spam
# 새 표현이 나올 때마다 사람이 규칙을 갱신해야 함
```

**After — 데이터로 학습한 분류:**

```python
# 개념만 예시(scikit-learn 미사용) — 실무에서는 sklearn, transformers 등 사용
def train_naive_bayes(samples: list[tuple[str, str]]) -> dict:
    """Naive count-based learner: tally words per class."""
    counts = {"spam": {}, "ham": {}}
    totals = {"spam": 0, "ham": 0}
    for text, label in samples:
        for word in text.split():
            counts[label][word] = counts[label].get(word, 0) + 1
            totals[label] += 1
    return {"counts": counts, "totals": totals}

def predict(model: dict, text: str) -> str:
    spam_score = sum(model["counts"]["spam"].get(w, 0) for w in text.split())
    ham_score  = sum(model["counts"]["ham"].get(w, 0)  for w in text.split())
    return "spam" if spam_score > ham_score else "ham"

model = train_naive_bayes([
    ("free coupon winner", "spam"),
    ("meeting notes attached", "ham"),
    ("click now discount", "spam"),
    ("lunch together?", "ham"),
])
print(predict(model, "free lunch coupon"))   # decided from data
```

## 단계별로 따라하기

### 1단계: 데이터로부터 직선 학습 (선형 회귀)

```python
# 데이터에서 y ≈ a*x + b의 a, b 추정 — 외부 라이브러리 없음
xs = [1, 2, 3, 4, 5]
ys = [2.1, 3.9, 6.1, 8.0, 10.2]   # roughly y = 2x

n = len(xs)
mean_x = sum(xs) / n
mean_y = sum(ys) / n
num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
den = sum((x - mean_x) ** 2 for x in xs)
a = num / den
b = mean_y - a * mean_x
print(f"y ≈ {a:.2f}x + {b:.2f}")    # y ≈ 2.03x + -0.05
```

### 2단계: 학습/검증/평가 분리

```python
import random

def train_test_split(data: list, ratio: float = 0.8) -> tuple[list, list]:
    """Split data into training and evaluation sets."""
    data = list(data)
    random.shuffle(data)
    cut = int(len(data) * ratio)
    return data[:cut], data[cut:]

train, test = train_test_split(list(zip(xs, ys)))
print("train:", train)
print("test :", test)
```

### 3단계: 추론 비용을 시간으로 측정

```python
import time

def predict_y(x: float, a: float, b: float) -> float:
    return a * x + b

start = time.perf_counter()
for x in range(1_000_000):
    predict_y(x, a, b)
print(f"1M inferences: {time.perf_counter() - start:.3f}s")
# 단순한 모델일수록 추론이 빠름 — 실시간 서비스의 핵심 지표
```

**Expected output:** 백만 번의 추론 시간이 숫자로 출력되고, 같은 정확도라면 더 단순한 모델이 운영 비용과 지연 시간에서 유리하다는 점을 확인할 수 있어야 합니다.

### 4단계: 데이터 품질 확인

```python
def basic_stats(values: list[float]) -> dict:
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    return {"n": n, "mean": mean, "std": var ** 0.5,
            "min": min(values), "max": max(values)}

print(basic_stats(ys))
# 학습 전 분포, 결측치, 이상치 확인이 ML 작업의 절반
```

### 5단계: ML 워크플로우 한 줄 요약

```python
# 1) 문제 정의 -> 2) 데이터 수집 -> 3) 전처리 -> 4) 모델 학습
# -> 5) 평가 -> 6) 배포 -> 7) 모니터링 -> 1)로 반복

steps = [
    "frame problem", "collect data", "preprocess", "train model",
    "evaluate", "deploy", "monitor",
]
for i, step in enumerate(steps, 1):
    print(f"{i}. {step}")
```

## 이 코드에서 먼저 봐야 할 점

- 단순한 모델일수록 디버깅과 운영이 쉽습니다 — 항상 기준선(baseline)부터 시작합니다
- 데이터를 학습/검증/평가로 분리하지 않으면 성능을 과대 평가하게 됩니다
- 추론 시간은 사용자 경험과 인프라 비용을 동시에 좌우합니다
- 모델 코드보다 데이터 파이프라인이 훨씬 더 많은 시간을 차지합니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 모델부터 고민 | 데이터·문제 정의 부실 | 문제·데이터·기준선 → 그다음에 모델 |
| 학습/평가 데이터 누수 | 평가 점수 거짓으로 높음 | 시간·사용자 단위로 엄격히 분리 |
| 평균 정확도만 보고 판단 | 클래스 불균형 가려짐 | 정밀도·재현율·F1·혼동 행렬 |
| 배포 후 모니터링 부재 | 데이터 분포 변화로 성능 저하 | drift 모니터링, 재학습 주기 정의 |
| GPU·메모리 비용 무시 | 운영 비용이 비즈니스 가치 초과 | 모델 경량화, 배치 추론, 캐싱 |

## 실무에서는 이렇게 쓰입니다

- 추천·랭킹·검색에서 사용자 행동 로그를 학습 데이터로 활용
- LLM 기반 도구에서 프롬프트·검색·캐시를 결합한 RAG 파이프라인
- ML 모델을 마이크로서비스로 배포하고 A/B 테스트로 효과 측정
- MLOps — 데이터셋 버전 관리, 실험 추적, 자동 재학습
- AI 비용 관리 — 모델 크기·토큰·GPU 시간의 단가 추적

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 AI를 만능 해법이 아니라 하나의 도구로 다룹니다. 규칙으로 충분한 문제는 규칙으로 풀고, 데이터에서 패턴을 끌어내야 할 때만 ML을 씁니다. 그리고 ML 시스템도 결국 소프트웨어이므로 테스트, 모니터링, 롤백 계획이 필요하다는 점을 잊지 않습니다.

오히려 AI 시대일수록 기초가 더 중요합니다. 모델은 매년 바뀌지만 데이터 표현, 연산 비용, 시스템 설계 원리는 오래 남습니다. 그래서 CS 기초가 탄탄한 사람이 새로운 AI 도구도 가장 빨리 받아들입니다.

## 시리즈에서 배운 것이 어떻게 이어지는가

| 이 시리즈에서 | AI/DS에서 |
| --- | --- |
| 데이터 표현(EP3) | 텐서 dtype, 임베딩 벡터 |
| 알고리즘과 복잡도(EP4) | 학습·추론 비용, 인덱스 검색 |
| 컴퓨터 구조(EP5) | GPU 메모리·캐시, 배치 처리 |
| 운영체제(EP6) | 멀티프로세싱 학습, GPU 스케줄 |
| 네트워크(EP7) | 분산 학습, 모델 서빙 |
| 데이터베이스(EP8) | 특징 저장소(feature store), 벡터 DB |
| 소프트웨어 엔지니어링(EP9) | MLOps, 실험 재현성 |

### 혼동 행렬(Confusion Matrix)과 평가 지표

분류 모델의 성능을 단일 정확도(accuracy)로 판단하면 위험합니다. 클래스 불균형이 있을 때 혼동 행렬이 실체를 보여줍니다.

```text
                    예측
              Positive    Negative
실제 Positive │  TP (42)  │  FN (8)   │  → 재현율 = TP/(TP+FN) = 84%
실제 Negative │  FP (12)  │  TN (938) │
              └───────────┴───────────┘
                    ↓
              정밀도 = TP/(TP+FP) = 78%

정확도 = (TP+TN)/전체 = 980/1000 = 98%  ← 높아 보이지만...
```

스팸 필터 예시: 1000통 중 스팸이 50통뿐이면 "전부 정상"이라고 예측해도 정확도 95%입니다. 하지만 재현율은 0%이므로 쓸모없습니다.

```python
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np

# 실제값과 예측값
y_true = [1]*50 + [0]*950   # 스팸 50개, 정상 950개
y_pred = [1]*42 + [0]*8 + [1]*12 + [0]*938

cm = confusion_matrix(y_true, y_pred, labels=[1, 0])
print("혼동 행렬:")
print(f"  TP={cm[0,0]}  FN={cm[0,1]}")
print(f"  FP={cm[1,0]}  TN={cm[1,1]}")
print()
print(classification_report(y_true, y_pred, target_names=["스팸", "정상"]))
```

| 지표 | 공식 | 중요한 경우 |
|------|------|-------------|
| 정밀도(Precision) | TP / (TP + FP) | 오탐이 비싼 경우 (금융 사기) |
| 재현율(Recall) | TP / (TP + FN) | 놓침이 치명적인 경우 (암 진단) |
| F1 Score | 2 × P × R / (P + R) | 정밀도-재현율 균형 |
| AUC-ROC | 분류 임계값 전체에서의 면적 | 모델 전반적 판별력 |

### 경사 하강법(Gradient Descent) 직관

머신러닝의 학습은 손실 함수를 최소화하는 파라미터를 찾는 최적화 문제입니다.

```python
import numpy as np

def gradient_descent_demo():
    """1차원 경사 하강법으로 y = (x-3)^2 의 최솟값을 찾습니다."""
    # 손실 함수: f(x) = (x - 3)^2
    # 기울기:    f'(x) = 2(x - 3)

    x = 10.0              # 초기값 (임의)
    learning_rate = 0.1   # 학습률
    history = []

    for step in range(20):
        gradient = 2 * (x - 3)           # 기울기 계산
        x = x - learning_rate * gradient  # 파라미터 업데이트
        loss = (x - 3) ** 2              # 현재 손실
        history.append((step, x, loss))

    print(f"{'Step':>4} {'x':>8} {'Loss':>10}")
    print("-" * 24)
    for step, xi, loss in history[:10]:
        print(f"{step:>4} {xi:>8.4f} {loss:>10.6f}")
    print(f"최종: x = {x:.6f}, 최솟값 위치 = 3.0")

gradient_descent_demo()
```

학습률이 너무 크면 발산하고, 너무 작으면 수렴이 느립니다.

```text
학습률에 따른 수렴 양상:

Loss
 ↑
 │ ×            lr = 0.01 (느림)
 │  ×
 │   ×──×──×──×──×──×──  → 수렴하지만 느림
 │
 │ ×
 │  ×
 │   ×                    lr = 0.1 (적절)
 │    ×─×─→ 수렴
 │
 │ × × × × × × × ×       lr = 1.0 (발산)
 │× × × × × × × × ×     → 발산
 └──────────────────────→ Step
```

실전에서는 학습률 스케줄러(cosine annealing, warmup)를 사용해 초기에는 크게, 후반에는 작게 조정합니다.

### 데이터 파이프라인과 특징 엔지니어링

모델 성능의 80%는 데이터 품질과 특징 설계에서 결정됩니다.

```text
원시 데이터 → [수집] → [정제] → [특징 추출] → [학습] → [평가] → [배포]
                        │                                        │
                        └─── 피드백 루프 ──────────────────────────┘
```

```python
import pandas as pd
import numpy as np

def feature_engineering_example():
    """전자상거래 데이터에서 특징을 생성하는 예시입니다."""
    # 원시 주문 데이터
    orders = pd.DataFrame({
        "user_id": [1, 1, 1, 2, 2, 3],
        "amount": [15000, 32000, 8000, 120000, 45000, 5000],
        "created_at": pd.to_datetime([
            "2026-01-01", "2026-01-15", "2026-02-01",
            "2026-01-05", "2026-01-20", "2026-03-01",
        ]),
    })

    # 사용자별 집계 특징 생성
    features = orders.groupby("user_id").agg(
        order_count=("amount", "count"),
        total_spent=("amount", "sum"),
        avg_order_value=("amount", "mean"),
        max_order_value=("amount", "max"),
        days_since_first=("created_at", lambda x: (x.max() - x.min()).days),
    ).reset_index()

    # 파생 특징
    features["spending_velocity"] = (
        features["total_spent"] / (features["days_since_first"] + 1)
    )

    print(features.to_string(index=False))

feature_engineering_example()
```

특징 엔지니어링에서 흔한 실수:

| 실수 | 결과 | 해결 |
|------|------|------|
| 미래 정보 누출(data leakage) | 학습 정확도↑, 운영 성능↓ | 시간 기준 분할 엄수 |
| 결측값 무시 | NaN 전파로 모델 오류 | 명시적 대체 또는 제거 |
| 스케일 미조정 | 큰 값 특징이 지배 | StandardScaler, MinMaxScaler |
| 범주형 직접 입력 | 순서 관계 오해석 | One-hot encoding, Target encoding |
| 학습/평가 데이터 오염 | 과적합을 탐지 못함 | 별도 검증 세트 + 교차 검증 |

### MLOps: 모델을 운영 시스템으로 만드는 과정

노트북에서 잘 되는 모델을 운영 서비스로 만들려면 소프트웨어 엔지니어링의 모든 원칙이 필요합니다.

```text
실험 단계                    운영 단계
─────────────────────────────────────────────────
Jupyter 노트북          →   패키지화된 Python 모듈
로컬 CSV                →   데이터 파이프라인 (Airflow/Prefect)
수동 학습               →   자동 재학습 파이프라인
print() 디버깅          →   구조화된 로깅 + 모니터링
단일 모델 파일          →   모델 레지스트리 (MLflow)
수동 배포               →   CI/CD + 카나리 배포
결과 수동 확인          →   A/B 테스트 + 자동 롤백
```

| MLOps 구성 요소 | 도구 예시 | 역할 |
|-----------------|-----------|------|
| 실험 추적 | MLflow, W&B | 하이퍼파라미터, 메트릭, 아티팩트 기록 |
| 데이터 버전 관리 | DVC, lakeFS | 데이터셋 변경 이력 추적 |
| 모델 서빙 | TorchServe, Triton, FastAPI | 저지연 추론 API |
| 모니터링 | Evidently, Grafana | 데이터/모델 드리프트 감지 |
| 오케스트레이션 | Kubeflow, Airflow | 파이프라인 스케줄링 |

### 모델 드리프트와 재학습 전략

운영 중인 모델은 시간이 지나면 성능이 떨어집니다. 입력 데이터의 분포가 변하기 때문입니다.

| 드리프트 유형 | 원인 | 감지 방법 |
|---------------|------|----------|
| 데이터 드리프트 | 사용자 행동 변화, 계절성 | 입력 특징 분포 비교 (KS 검정, PSI) |
| 개념 드리프트 | 입력-출력 관계 자체가 변함 | 예측 정확도 모니터링 |
| 라벨 드리프트 | 라벨링 기준 변경 | 라벨 분포 추적 |

재학습 전략:

1. **정기 재학습**: 매주/매월 새 데이터로 재학습 (단순하지만 낭비 가능)
2. **트리거 기반 재학습**: 성능 지표가 임계값 이하로 떨어지면 자동 실행
3. **온라인 학습**: 새 데이터가 들어올 때마다 점진적 업데이트 (스트리밍)

```python
# 간단한 모델 드리프트 감지 예시
from scipy import stats
import numpy as np

def detect_drift(reference: np.ndarray, current: np.ndarray, threshold: float = 0.05) -> bool:
    """KS 검정으로 두 분포가 유의하게 다른지 판단합니다."""
    statistic, p_value = stats.ks_2samp(reference, current)
    drifted = p_value < threshold
    print(f"KS statistic: {statistic:.4f}, p-value: {p_value:.4f}, drift: {drifted}")
    return drifted

# 학습 시 데이터 분포 (기준)
train_distribution = np.random.normal(loc=50, scale=10, size=10000)

# 운영 중 수집된 데이터 (정상)
production_normal = np.random.normal(loc=50, scale=10, size=1000)
detect_drift(train_distribution, production_normal)  # drift: False

# 운영 중 수집된 데이터 (드리프트 발생)
production_drifted = np.random.normal(loc=60, scale=15, size=1000)
detect_drift(train_distribution, production_drifted)  # drift: True
```
## 체크리스트

- [ ] 머신러닝과 규칙 기반의 차이를 한 문장으로 설명할 수 있는가
- [ ] 학습/검증/평가 데이터 분리가 왜 필요한지 아는가
- [ ] 모델 추론도 결국 CPU/메모리 위의 연산임을 의식하는가
- [ ] AI 시스템에 테스트와 모니터링이 똑같이 필요함을 이해했는가
- [ ] 다음에 무엇을 공부할지 자기 학습 경로를 그려 봤는가

## 연습 문제

1. 작은 데이터셋을 직접 만들어 선형 회귀 코드로 직선을 학습시키고 새 입력의 출력을 예측해 보세요.
2. 같은 데이터셋을 학습용과 평가용으로 나눈 뒤 MAE 같은 간단한 지표를 계산해 보세요.
3. 이 시리즈에서 가장 약하다고 느낀 주제 하나를 골라, 그 주제만 100줄 분량으로 다시 설명하는 학습 글을 써 보세요.

## 정리 및 다음 단계

이 시리즈에서 우리는 컴퓨터 과학의 큰 지도를 그렸습니다. 데이터가 어떻게 표현되고, 알고리즘이 어떻게 측정되며, 하드웨어와 운영체제가 어떻게 협력하고, 네트워크와 데이터베이스가 어떻게 시스템을 받치고, 엔지니어링이 어떻게 그 모두를 시간에 견디게 만드는지 살펴봤습니다. AI/DS는 그 위에 통계와 도메인을 더한 한 분야일 뿐입니다.

다음 학습 경로 제안:

- **언어 깊이**: Python 101 → Python Advanced (자료구조·동시성·메타프로그래밍)
- **시스템 깊이**: Operating Systems: Three Easy Pieces, Designing Data-Intensive Applications
- **AI/DS**: 통계 기초 → 머신러닝(scikit-learn) → 딥러닝(PyTorch) → LLM과 RAG
- **엔지니어링**: 테스트 자동화, CI/CD, 클라우드(AWS/GCP), 관측성

도구는 변하지만 기초는 남습니다. 시리즈를 읽어 주셔서 감사합니다.

## 학습 설계 지도: 이 글을 커리큘럼에 연결하기

컴퓨터 과학 입문을 빠르게 끝내는 접근보다, 서로 연결된 개념을 축적하는 접근이 이후 학습 효율을 높입니다. 이 글의 핵심 개념은 단독 지식이 아니라 운영체제, 네트워크, 데이터베이스, 소프트웨어 공학으로 이어지는 선행 지식입니다. 따라서 한 주 단위 학습에서 이 글을 기준점으로 삼고, 다음과 같은 연결 훈련을 함께 수행하는 것이 좋습니다.

| 학습 축 | 이 글에서 확인할 포인트 | 다음 과목 연결 |
| --- | --- | --- |
| 계산 모델 | 입력, 상태, 출력의 관계를 명확히 정의 | 알고리즘 설계, 분산 시스템 모델링 |
| 추상화 | 세부 구현을 숨기고 인터페이스를 구분 | API 설계, 모듈 경계 설계 |
| 자원 제약 | 시간·메모리·I/O 비용을 동시에 고려 | 성능 튜닝, 인프라 비용 최적화 |
| 검증 가능성 | 주장 대신 측정과 반례로 판단 | 테스트 전략, 실험 설계 |

연결 학습을 할 때는 "개념 정의 1회 + 사례 적용 2회 + 반례 점검 1회" 구조를 반복합니다. 예를 들어 시간 복잡도를 배웠다면, 단순히 O 표기법을 외우지 않고 입력 크기 변화에 따른 실행 시간 그래프를 직접 기록합니다. 그래프가 기대와 다를 때 원인을 추정하고, 캐시 지역성이나 상수항의 영향을 설명해 보는 과정이 필요합니다. 이 연습이 쌓이면 글에서 다룬 개념이 시험 대비 지식이 아니라 실무 의사결정 기준으로 바뀝니다.

또한 과목 간 언어를 통일해 두는 것이 중요합니다. 같은 현상을 운영체제에서는 스케줄링, 네트워크에서는 큐잉, 데이터베이스에서는 트랜잭션 대기라고 부를 수 있습니다. 이름은 달라도 "경합 상태에서 자원을 배분한다"는 본질은 동일합니다. 학습 노트에 용어 사전을 만들어 개념 동치 관계를 표시해 두면, 새로운 분야를 배울 때 기존 이해를 재사용하기 쉬워집니다.

마지막으로 주간 복습은 요약보다 질문 중심으로 구성합니다. "왜 이 추상화가 필요한가", "어떤 조건에서 깨지는가", "대안의 비용은 무엇인가"를 각각 한 문장으로 답하면 학습 깊이가 빠르게 올라갑니다. 이렇게 축적한 질문-답변 세트는 면접, 설계 리뷰, 코드 리뷰에서 그대로 활용 가능한 사고 프레임이 됩니다.

AI·데이터 과학 단원에서는 모델 성능 수치뿐 아니라 데이터 품질, 피처 생성 비용, 배포 이후 드리프트 감시를 포함한 전체 수명주기를 기준으로 평가합니다.

## 처음 질문으로 돌아가기

- **지금까지 배운 CS 기초가 AI와 데이터사이언스에서 어디에 직접 쓰일까요?**
  - 알고리즘 복잡도는 학습 시간 예측에, 컴퓨터 구조는 GPU 병렬화 이해에, OS는 분산 학습 오케스트레이션에, 네트워크는 모델 서빙 지연 분석에, DB는 특징 저장소 설계에 직접 대응됩니다.
- **규칙 기반 시스템과 머신러닝 시스템은 무엇이 본질적으로 다를까요?**
  - 규칙 기반은 사람이 입력→출력 매핑을 명시적으로 코딩합니다. 머신러닝은 데이터에서 그 매핑을 자동으로 학습합니다. 규칙은 해석 가능하지만 복잡한 패턴에 한계가 있고, ML은 패턴 발견에 강하지만 블랙박스와 데이터 품질 의존이라는 대가를 치릅니다.
- **학습, 추론, 데이터 품질 검증은 왜 결국 계산과 시스템 문제일까요?**
  - 학습은 경사 하강법이라는 반복 최적화(행렬 연산 수십억 회)이고, 추론은 지연 시간 내에 결과를 반환하는 시스템 문제이며, 데이터 품질 검증은 파이프라인의 각 단계에서 분포 변화를 감시하는 모니터링 문제입니다.
<!-- toc:begin -->
## 시리즈 목차

- [Computer Science 101 (1/10): Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- [Computer Science 101 (2/10): 계산과 프로그램](./02-computation-and-programs.md)
- [Computer Science 101 (3/10): 데이터 표현](./03-data-representation.md)
- [Computer Science 101 (4/10): 알고리즘과 복잡도](./04-algorithms-and-complexity.md)
- [Computer Science 101 (5/10): 컴퓨터 구조](./05-computer-architecture.md)
- [Computer Science 101 (6/10): 운영체제](./06-operating-systems.md)
- [Computer Science 101 (7/10): 네트워크](./07-networks.md)
- [Computer Science 101 (8/10): 데이터베이스](./08-databases.md)
- [Computer Science 101 (9/10): 소프트웨어 엔지니어링](./09-software-engineering.md)
- **AI와 데이터사이언스까지의 연결 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Hands-On Machine Learning — Aurélien Géron](https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/)
- [scikit-learn — User Guide](https://scikit-learn.org/stable/user_guide.html)
- [Designing Machine Learning Systems — Chip Huyen](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/)
- [The Bitter Lesson — Rich Sutton](http://www.incompleteideas.net/IncIdeas/BitterLesson.html)

- [이 시리즈의 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-science-101/ko)
Tags: Computer Science, AI, 데이터사이언스, 머신러닝, 통계, 진로
