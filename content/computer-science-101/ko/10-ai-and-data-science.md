---
series: computer-science-101
episode: 10
title: AI와 데이터사이언스까지의 연결
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
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
seo_description: CS 기초가 AI·데이터사이언스로 어떻게 이어지는지, 다음 학습 경로를 정리하는 CS 입문 시리즈 마지막 글입니다.
last_reviewed: '2026-05-04'
---

# AI와 데이터사이언스까지의 연결

> Computer Science 101 시리즈 (10/10)


## 이 글에서 다룰 문제

AI는 마법이 아닙니다. 모델은 데이터로 학습되고, 추론은 행렬 연산이며, 그 모든 것은 결국 CPU·메모리·디스크 위에서 돌아갑니다. CS 기초가 단단할수록 AI 코드를 디버깅하고, 비용을 추정하고, 문제를 정의하는 능력이 빠르게 성장합니다.

> AI/DS = CS + 통계 + 도메인

도구는 빨리 변해도 기초는 오래 유효합니다.

## 전체 흐름
> 규칙 기반은 사람이 규칙을 적고, 머신러닝은 데이터로부터 규칙을 추론합니다.

```text
규칙 기반                              머신러닝
입력 ──┐                              입력 ──┐
       ├─ 사람이 만든 규칙 ─→ 출력          ├─ 학습된 모델 ─→ 출력
규칙 ──┘                              모델 ←── 학습 데이터로 추정
```

## Before / After

**Before — 규칙 기반 분류:**

```python
def classify_email(text: str) -> str:
    """사람이 직접 규칙을 만든 스팸 분류기."""
    spam_words = {"무료", "당첨", "지금 클릭", "할인"}
    score = sum(word in text for word in spam_words)
    return "spam" if score >= 2 else "ham"


print(classify_email("무료 쿠폰 당첨"))   # spam
# 새 표현이 나올 때마다 사람이 규칙을 갱신해야 합니다
```

**After — 데이터로 학습한 분류:**

```python
# scikit-learn 없이 개념만 — 실제로는 sklearn, transformers 등을 사용합니다
def train_naive_bayes(samples: list[tuple[str, str]]) -> dict:
    """단어별로 spam/ham 빈도를 세는 단순 학습."""
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
    ("무료 쿠폰 당첨", "spam"),
    ("회의 자료 첨부", "ham"),
    ("지금 클릭 할인", "spam"),
    ("점심 같이 드실래요", "ham"),
])
print(predict(model, "무료 점심 쿠폰"))   # 데이터 기반으로 결정
```

## 단계별로 따라하기

### 1단계: 데이터로부터 직선 학습 (선형 회귀)

```python
# y ≈ a*x + b 의 a, b를 데이터로부터 추정합니다 — 외부 라이브러리 없이
xs = [1, 2, 3, 4, 5]
ys = [2.1, 3.9, 6.1, 8.0, 10.2]   # 대략 y = 2x

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
    """데이터를 학습용과 평가용으로 나눕니다."""
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
print(f"100만 추론: {time.perf_counter() - start:.3f}s")
# 모델이 단순할수록 추론이 빠릅니다 — 실시간 서비스에서 중요한 지표
```

### 4단계: 데이터 품질 확인

```python
def basic_stats(values: list[float]) -> dict:
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    return {"n": n, "mean": mean, "std": var ** 0.5,
            "min": min(values), "max": max(values)}


print(basic_stats(ys))
# 학습 전 데이터의 분포·결측·이상치를 보는 습관이 ML의 절반입니다
```

### 5단계: ML 워크플로우 한 줄 요약

```python
# ① 문제 정의 → ② 데이터 수집 → ③ 전처리 → ④ 모델 학습
# → ⑤ 평가 → ⑥ 배포 → ⑦ 모니터링 → ① 로 돌아가기

steps = [
    "문제 정의", "데이터 수집", "전처리", "모델 학습",
    "평가", "배포", "모니터링",
]
for i, step in enumerate(steps, 1):
    print(f"{i}. {step}")
```

## 이 코드에서 주목할 점

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

## 체크리스트

- [ ] 머신러닝과 규칙 기반의 차이를 한 문장으로 설명할 수 있는가
- [ ] 학습/검증/평가 데이터 분리가 왜 필요한지 아는가
- [ ] 모델 추론도 결국 CPU/메모리 위의 연산임을 의식하는가
- [ ] AI 시스템에 테스트와 모니터링이 똑같이 필요함을 이해했는가
- [ ] 다음에 무엇을 공부할지 자기 학습 경로를 그려 봤는가

## 정리 및 다음 단계

이 시리즈에서 우리는 컴퓨터 과학의 큰 지도를 그렸습니다. 데이터가 어떻게 표현되고, 알고리즘이 어떻게 측정되며, 하드웨어와 운영체제가 어떻게 협력하고, 네트워크와 데이터베이스가 어떻게 시스템을 받치고, 엔지니어링이 어떻게 그 모두를 시간에 견디게 만드는지 살펴봤습니다. AI/DS는 그 위에 통계와 도메인을 더한 한 분야일 뿐입니다.

다음 학습 경로 제안:

- **언어 깊이**: Python 101 → Python Advanced (자료구조·동시성·메타프로그래밍)
- **시스템 깊이**: Operating Systems: Three Easy Pieces, Designing Data-Intensive Applications
- **AI/DS**: 통계 기초 → 머신러닝(scikit-learn) → 딥러닝(PyTorch) → LLM과 RAG
- **엔지니어링**: 테스트 자동화, CI/CD, 클라우드(AWS/GCP), 관측성

도구는 변하지만 기초는 남습니다. 시리즈를 읽어 주셔서 감사합니다.

<!-- toc:begin -->
- [Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- [계산과 프로그램](./02-computation-and-programs.md)
- [데이터 표현](./03-data-representation.md)
- [알고리즘과 복잡도](./04-algorithms-and-complexity.md)
- [컴퓨터 구조](./05-computer-architecture.md)
- [운영체제](./06-operating-systems.md)
- [네트워크](./07-networks.md)
- [데이터베이스](./08-databases.md)
- [소프트웨어 엔지니어링](./09-software-engineering.md)
- **AI와 데이터사이언스까지의 연결 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Hands-On Machine Learning — Aurélien Géron](https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/)
- [scikit-learn — User Guide](https://scikit-learn.org/stable/user_guide.html)
- [Designing Machine Learning Systems — Chip Huyen](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/)
- [The Bitter Lesson — Rich Sutton](http://www.incompleteideas.net/IncIdeas/BitterLesson.html)

Tags: Computer Science, AI, 데이터사이언스, 머신러닝, 통계, 진로
