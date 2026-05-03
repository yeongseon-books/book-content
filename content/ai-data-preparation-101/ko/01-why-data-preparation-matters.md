---
title: 데이터 준비가 모델 품질을 결정하는 이유
series: ai-data-preparation-101
episode: 1
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Data Preparation
- ML Foundations
- Data Quality
- Pipelines
last_reviewed: '2026-05-03'
---

# 데이터 준비가 모델 품질을 결정하는 이유

> AI Data Preparation 101 시리즈 (1/10)

---
## "데이터 좀 모아서 그냥 학습시키면 안 되나요?"

ML 입문자가 가장 많이 던지는 질문입니다. Kaggle에서 데이터셋을 받고, `pandas.read_csv()`로 읽고, 모델에 넣으면 끝나는 것처럼 보입니다. 그런데 실무에서 모델 품질 문제를 추적해 보면 70~80%가 데이터에서 출발합니다.

Andrew Ng가 2021년 "Data-centric AI" 캠페인에서 던진 메시지가 정확히 이 지점입니다. 같은 모델 아키텍처라도 데이터 품질이 1~2점 올라가면 정확도가 5~10% 뛰는 경우가 흔합니다. 반대로 모델을 아무리 튜닝해도 더러운 데이터로는 한계가 있습니다.

이 시리즈는 raw 데이터를 production 학습 셋으로 만드는 전 과정을 다룹니다. 1편에서는 왜 데이터 준비가 그렇게 중요한지, 그리고 흔히 놓치는 데이터 함정 다섯 가지를 살펴봅니다.

## Garbage In, Garbage Out — 그 이상의 의미

전통적인 GIGO는 "쓰레기 데이터를 넣으면 쓰레기가 나온다"입니다. 그런데 LLM과 추천 시스템 시대에는 더 무서운 변형이 있습니다.

- **Silent failure**: 모델이 그럴듯한 답을 내놓지만 사실은 학습 데이터의 편향된 패턴을 그대로 답습합니다. 메트릭은 좋아 보이지만 실제 사용자 경험은 무너집니다.
- **Test set leakage**: 학습 데이터가 평가 데이터와 겹치면 메트릭이 부풀려집니다. 배포 후에 성능이 절반으로 떨어지는 사고는 대부분 여기서 출발합니다.
- **Distribution shift**: 학습 시점에는 잘 동작했지만, 사용자 데이터가 시간이 지나면서 학습 분포에서 벗어나면서 정확도가 점점 떨어집니다.

다음 코드는 같은 모델로 두 가지 데이터셋을 학습한 결과를 비교합니다. 데이터만 바꿔도 차이가 명확합니다.

```python
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import re

categories = ["sci.space", "rec.autos"]
train = fetch_20newsgroups(subset="train", categories=categories)
test = fetch_20newsgroups(subset="test", categories=categories)

def clean(text: str) -> str:
    # 헤더, 인용, 이메일 제거
    text = re.sub(r"^(From|Subject|Lines|Organization):.*$", "", text, flags=re.M)
    text = re.sub(r"^>.*$", "", text, flags=re.M)
    text = re.sub(r"\S+@\S+", "", text)
    return text

def train_eval(train_texts, test_texts):
    vec = TfidfVectorizer(max_features=5000, stop_words="english")
    X_train = vec.fit_transform(train_texts)
    X_test = vec.transform(test_texts)
    clf = LogisticRegression(max_iter=1000).fit(X_train, train.target)
    pred = clf.predict(X_test)
    return accuracy_score(test.target, pred)

raw_acc = train_eval(train.data, test.data)
clean_acc = train_eval([clean(t) for t in train.data],
                        [clean(t) for t in test.data])
print(f"Raw:     {raw_acc:.4f}")
print(f"Cleaned: {clean_acc:.4f}")
```

실행해 보면 정제 전후로 정확도가 1~3%포인트씩 차이 납니다. 모델 코드는 한 줄도 바꾸지 않았습니다. 데이터만 정리했을 뿐입니다.

## 데이터 준비 파이프라인의 6단계

production에서 쓰는 데이터 준비 파이프라인은 보통 다음 6단계로 구성됩니다.

1. **Collection (수집)**: 원본 소스에서 데이터를 가져오고 출처를 기록합니다. 라이선스, 수집 시점, 버전이 핵심입니다.
2. **Cleaning (정제)**: 인코딩 오류, HTML 태그, 깨진 문자, 중복을 제거합니다.
3. **Privacy (개인정보 처리)**: 학습에 들어가면 안 되는 PII를 탐지하고 익명화합니다.
4. **Quality filtering (품질 필터링)**: heuristic 규칙과 분류기로 저품질 샘플을 걸러냅니다.
5. **Tokenization & chunking (토큰화·청킹)**: 모델 입력 형태로 변환합니다.
6. **Splitting (분할)**: train/eval/test로 나누되, contamination을 막는 검증을 거칩니다.

이 시리즈는 각 단계를 한 편씩 다룹니다. 6편 이후에는 합성 데이터 생성, 증강, 그리고 마지막에 모든 단계를 묶은 production 파이프라인까지 이어집니다.

## 흔히 놓치는 데이터 함정 다섯 가지

### 1. 중복 샘플이 평가 점수를 부풀림

같은 문서가 학습/평가 양쪽에 들어가면 모델은 외운 답을 그대로 뱉습니다. CC-Net, The Pile 등 대규모 코퍼스를 다뤄본 팀들은 모두 dedup 단계를 가장 먼저 수행합니다 (3편에서 MinHash로 다룹니다).

### 2. 클래스 불균형을 고려하지 않은 split

```python
from sklearn.model_selection import train_test_split
# 잘못된 방법: 단순 random split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 올바른 방법: stratify로 클래스 비율 유지
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
```

stratify를 빠뜨리면 minority class가 test set에 거의 없어서 metric이 의미를 잃습니다.

### 3. 시간 순서 무시

시계열 데이터를 random split하면 미래 정보가 학습에 새는 temporal leakage가 발생합니다. 항상 cutoff date 기준으로 분할해야 합니다 (9편에서 자세히).

### 4. PII가 학습 데이터에 그대로 들어감

이메일, 전화번호, 주민등록번호가 raw 텍스트에 섞여 있으면 모델이 이를 그대로 출력하는 사고가 납니다 (4편). LLM에서는 "membership inference attack"이라는 별도 공격 벡터까지 생깁니다.

### 5. 토큰화 단계에서 정보 손실

영문 BPE tokenizer를 한국어에 그대로 쓰면 한 글자가 3~4 토큰으로 쪼개집니다. context window를 비효율적으로 쓰고, 학습 신호가 흐려집니다 (5편).

## 데이터 품질을 측정하는 간단한 지표

production에 들어가기 전, 다음 5가지 지표를 매번 측정합니다.

```python
import pandas as pd
from collections import Counter

def quick_quality_report(df: pd.DataFrame, text_col: str) -> dict:
    texts = df[text_col].dropna().astype(str)
    lengths = texts.str.len()
    word_counts = texts.str.split().str.len()
    return {
        "total_rows": len(df),
        "null_ratio": df[text_col].isna().mean(),
        "duplicate_ratio": 1 - texts.nunique() / len(texts),
        "avg_length": float(lengths.mean()),
        "p99_length": float(lengths.quantile(0.99)),
        "avg_words": float(word_counts.mean()),
        "language_dist": Counter(
            "en" if t.isascii() else "non-en" for t in texts.head(1000)
        ),
    }

# 사용 예
df = pd.DataFrame({"text": ["hello", "hello", "안녕", None, "world"]})
print(quick_quality_report(df, "text"))
```

이 보고서를 매 데이터 버전마다 자동 생성해서, 이전 버전과 비교하면 데이터 품질 회귀를 빠르게 잡을 수 있습니다.

## 흔한 실수 5가지

1. **"일단 학습부터 돌려보자"**: 데이터 검증 없이 학습을 시작하면 며칠을 날릴 수 있습니다. 학습 전에 quality report부터 확인합니다.
2. **샘플 100개만 보고 결정**: head(100)으로는 long-tail 문제를 못 잡습니다. 무작위 샘플 1000개와 길이 percentile 99% 지점도 확인합니다.
3. **단일 메트릭 의존**: accuracy 하나만 보면 클래스 불균형이나 sub-group 성능 저하를 놓칩니다. per-class metric, per-segment metric을 같이 봅니다.
4. **데이터 출처 미기록**: 어디서 가져왔는지, 언제 가져왔는지 기록 안 하면 라이선스 문제와 reproducibility 문제가 동시에 터집니다 (2편 카탈로깅).
5. **"한 번 정제하면 끝"이라는 가정**: 데이터 분포는 시간에 따라 변합니다. 정제 파이프라인은 코드처럼 버전 관리하고 CI에 통합해야 합니다 (10편).

## 핵심 요약

- 모델 품질의 70~80%는 데이터에서 결정됩니다. 데이터-centric 접근이 모델-centric 튜닝보다 ROI가 큽니다.
- 데이터 준비는 6단계 파이프라인입니다: Collection → Cleaning → Privacy → Quality filtering → Tokenization → Splitting.
- Silent failure, test set leakage, distribution shift는 데이터 단계에서 막아야 하는 대표 위험입니다.
- 매 데이터 버전마다 quick quality report를 자동 생성하고, 이전 버전과 비교합니다.
- 다음 편부터 6단계를 하나씩 깊게 다룹니다. 2편은 데이터 수집과 카탈로깅입니다.

---

<!-- toc:begin -->
## AI Data Preparation 101 시리즈

- **데이터 준비가 모델 품질을 결정하는 이유 (현재 글)**
- 원본 데이터 수집과 카탈로깅 (예정)
- 데이터 정제와 중복 제거 (예정)
- 학습 데이터 PII 탐지와 익명화 (예정)
- 토큰화와 청킹 전략 (예정)
- 데이터 품질 필터링 (예정)
- 합성 데이터 생성 (예정)
- 데이터 증강 기법 (예정)
- 학습/평가/테스트 분할과 오염 통제 (예정)
- 프로덕션 데이터 파이프라인 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [Andrew Ng - Data-centric AI Resources](https://datacentricai.org/)
- [The Pile: An 800GB Dataset of Diverse Text](https://arxiv.org/abs/2101.00027)
- [scikit-learn: Cross-validation and stratified splits](https://scikit-learn.org/stable/modules/cross_validation.html)
- [Google: Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml)

Tags: Data Preparation, ML Foundations, Data Quality, Pipelines
