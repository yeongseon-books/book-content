---
episode: 1
language: ko
last_reviewed: '2026-05-14'
seo_description: 모델 선택보다 데이터 준비 단계가 LLM 품질을 더 크게 좌우하는 이유와, 운영에서 반복되는 데이터 문제 패턴을 정리합니다.
series: ai-data-preparation-101
status: publish-ready
tags:
- Data Preparation
- ML Foundations
- Data Quality
- Pipelines
targets:
  ebook: true
  medium: false
  mkdocs: true
  tistory: true
title: "AI Data Preparation 101 (1/10): 데이터 준비가 모델 품질을 결정하는 이유"
---

# AI Data Preparation 101 (1/10): 데이터 준비가 모델 품질을 결정하는 이유

입문 단계에서는 모델 선택이 가장 큰 변수처럼 보입니다. 어떤 아키텍처를 쓰는지, 몇 epoch를 돌리는지, learning rate를 어떻게 잡는지가 결과를 좌우한다고 생각하기 쉽습니다. 그런데 운영에서 성능 문제를 되짚어 보면 모델보다 먼저 데이터 준비 단계가 드러나는 경우가 훨씬 많습니다.

같은 모델 코드라도 중복이 섞인 학습셋, 오염된 평가셋, 시점이 뒤섞인 분할을 쓰면 숫자는 좋아 보이지만 실제 배포 성능은 흔들립니다. 반대로 데이터 준비 기준을 한 번 세워 두면 모델을 바꾸지 않아도 품질과 재현성이 동시에 올라갑니다.

시니어 엔지니어 관점에서는 이 차이가 중요합니다. 모델 튜닝은 반복 비용이 크고, 잘못된 데이터 위에서 얻은 개선은 오래 가지 않기 때문입니다. 데이터 준비는 성능을 높이는 작업이기도 하지만, 나중에 원인 분석을 가능하게 만드는 운영 설계이기도 합니다.

처음부터 이 관점을 잡아 두면 이후 수집, 정제, PII 처리, 토큰화, 분할, 파이프라인 자동화를 각각 따로 배우더라도 하나의 시스템으로 연결해서 이해할 수 있습니다.

이 글은 AI Data Preparation 101 시리즈의 첫 번째 글입니다.

여기서는 왜 데이터 준비가 모델 품질을 사실상 결정하는지, 그리고 초기에 놓치면 뒤에서 크게 돌아오는 함정을 어떤 순서로 봐야 하는지 정리하겠습니다.

## 먼저 던지는 질문

- 모델 아키텍처보다 데이터 준비가 더 큰 차이를 만드는 순간은 언제일까요?
- 겉보기 정확도는 높은데 실제 사용자 경험이 나빠지는 대표적인 데이터 실패는 무엇일까요?
- 수집부터 분할까지의 데이터 준비 단계를 왜 하나의 파이프라인으로 봐야 할까요?

## 큰 그림

![AI 데이터 준비 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/01/01-01-big-picture.ko.png)

*AI 데이터 준비 1장 흐름 개요*

이 그림에서는 데이터 준비가 모델 품질을 결정하는 이유를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 데이터 준비가 모델 품질을 결정하는 이유의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

데이터 준비를 제대로 하면 같은 모델로도 더 높은 정확도, 더 낮은 재학습 비용, 더 안정적인 배포 성능을 얻을 수 있습니다. 특히 레이블링 비용이 비싼 팀일수록 한 번 모은 데이터를 얼마나 깨끗하게 다루는지가 ROI를 크게 바꿉니다.

반대로 데이터 준비를 생략하면 모델은 조용히 잘못 학습합니다. 중복 샘플은 평가 점수를 부풀리고, 시간 누수는 미래 정보를 학습으로 새게 만들고, PII는 규제와 보안 문제로 이어집니다. 이때 나오는 수치는 좋아 보여도 신뢰할 수 없습니다.

그래서 이 글은 단순한 입문 설명이 아니라 이후 아홉 편을 읽는 기준점을 세우는 글입니다. 데이터 준비를 모델 전처리가 아니라 품질·안전·재현성을 동시에 다루는 엔지니어링 문제로 보아야 시리즈 전체가 제대로 연결됩니다.

## 핵심 관점

데이터 준비를 잘 이해하려면 “학습 전에 한 번 손보는 전처리”라는 표현부터 버리는 편이 좋습니다. 실제로는 모델이 볼 수 있는 세계를 미리 규정하는 계약에 가깝습니다. 어떤 샘플을 남기고 어떤 샘플을 버릴지, 무엇을 민감정보로 간주할지, 어떤 기준으로 평가셋을 떼어낼지가 여기서 결정됩니다.

이 계약이 명확하면 나중에 모델 성능이 흔들려도 어디를 조사해야 할지 감이 생깁니다. 반대로 계약이 없으면 모든 실험이 우연처럼 보입니다. 같은 모델인데 왜 이번 배치는 잘 되고 저번 배치는 망가졌는지 설명할 수 없게 됩니다.

현업에서는 모델보다 데이터 파이프라인이 더 오래 남습니다. 팀이 바뀌고 모델이 바뀌어도, 데이터 품질 기준과 버전 기록이 남아 있어야 운영이 이어집니다.

> 데이터 준비는 모델을 위한 부속 작업이 아닙니다. 어떤 데이터를 학습·평가에 넣을 수 있는지 미리 정의하는 품질 계약이며, 이 계약이 흔들리면 이후의 모든 성능 숫자도 흔들립니다.

## 핵심 개념

### 같은 모델이라도 데이터가 바뀌면 결과가 바뀝니다

운영 현장에서 가장 자주 보는 착각은 모델 코드를 바꾸지 않았으니 품질도 비슷할 것이라는 기대입니다. 하지만 원문 정제 정도만 달라도 분류 정확도는 바로 달라집니다. 아래 예제는 같은 20 Newsgroups 데이터셋에 대해 정제 전후를 비교합니다.

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
    # Strip headers, quotes, emails
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

이 예제의 포인트는 알고리즘이 아니라 비교 방법입니다. 모델, 벡터라이저, 하이퍼파라미터를 모두 고정하고 데이터만 바꿨는데도 차이가 납니다. 이게 바로 데이터 중심 접근이 높은 레버리지를 가지는 이유입니다.

### 데이터 준비는 여섯 단계로 이어집니다

한 번의 전처리 스크립트로 끝나는 문제가 아니라, 다음 여섯 단계가 연결된 파이프라인으로 보는 편이 실용적입니다.

1. 수집: 데이터를 어디서 가져왔는지, 어떤 권한으로 가져왔는지 기록합니다.

2. 정제: HTML, 깨진 인코딩, 제어 문자, 중복을 제거합니다.

3. **개인정보 처리**: 학습에 들어가면 안 되는 식별자를 찾아 익명화합니다.

4. **품질 필터링**: 광고, 스팸, 보일러플레이트, 저품질 샘플을 제거합니다.

5. **토큰화와 청킹**: 모델이 실제로 소비할 단위로 바꿉니다.

6. 분할: train/eval/test를 떼어내고 누수 여부를 검사합니다.

이 단계들은 독립적이지 않습니다. 예를 들어 중복 제거를 빼먹으면 분할 단계의 평가 신뢰도가 무너지고, PII를 늦게 처리하면 이후 캐시와 아티팩트 전체가 규제 대상이 됩니다.

### 초기에 자주 놓치는 다섯 가지 함정

#### 1. 중복 샘플이 평가 점수를 올려 줍니다

같은 문서가 학습과 평가 양쪽에 있으면 모델은 일반화한 것이 아니라 외운 것입니다. 대규모 코퍼스를 다루는 팀들이 중복 제거를 가장 먼저 넣는 이유가 여기에 있습니다.

#### 2. 클래스 비율을 무시한 분할은 테스트셋을 망가뜨립니다

```python
from sklearn.model_selection import train_test_split
# Wrong: plain random split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Right: stratify keeps class ratios stable
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
```

`stratify`를 빠뜨리면 소수 클래스가 테스트셋에서 거의 사라질 수 있습니다. 이 경우 accuracy는 좋아 보여도 실제 현업 분포를 전혀 반영하지 못합니다.

#### 3. 시간 순서를 무시하면 미래 정보가 새어 들어갑니다

시계열, 뉴스, 추천 시스템에서는 무작위 분할이 오히려 가장 위험합니다. 오늘의 데이터를 학습에 넣고 어제의 데이터를 평가하면, 실제 배포보다 쉬운 문제를 풀게 됩니다.

#### 4. PII를 그대로 넣으면 학습 단계에서 이미 사고가 시작됩니다

이메일 주소나 전화번호는 한번 학습 코퍼스에 들어가면 모델 출력으로 재노출될 수 있습니다. 개인정보 처리는 수집 직후 단계에 들어가야 하지, 마지막 배포 직전에 붙이는 후처리가 아닙니다.

#### 5. 토크나이저가 정보 밀도를 바꿉니다

같은 길이의 한국어·영어·코드가 항상 같은 토큰 수를 갖는 것은 아닙니다. 도메인과 언어에 맞지 않는 토크나이저를 쓰면 context window를 낭비하고, 이후 chunk 설계도 연쇄적으로 왜곡됩니다.

### 최소한의 데이터 품질 보고서는 자동으로 남겨야 합니다

운영에서는 “문제가 생기면 봐야지”가 통하지 않습니다. 데이터셋 버전이 생길 때마다 기본 통계를 남겨야 합니다.

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

# Example
df = pd.DataFrame({"text": ["hello", "hello", "안녕", None, "world"]})
print(quick_quality_report(df, "text"))
```

**Expected output:**

```text
Raw:     0.93xx
Cleaned: 0.94xx
{'total_rows': 5, 'null_ratio': 0.2, 'duplicate_ratio': 0.25, ...}
```

숫자는 데이터셋과 시드에 따라 달라지지만, 패턴은 달라지지 않습니다. 정제만 바꿔도 지표가 움직여야 하고, 품질 리포트는 학습 전에 중복률·결측치·길이 이상치를 먼저 드러내야 합니다.

## 모델을 의심하기 전에 먼저 볼 실패 신호

실험이 잘못됐을 때 항상 모델부터 의심하면 원인 분석이 늦어집니다. 아래 세 가지는 데이터 단계에서 바로 볼 수 있는 경고 신호입니다.

1. **중복률 급증**: 데이터셋 버전이 바뀌었는데 duplicate ratio가 뛰면 평가 점수 부풀림 가능성을 먼저 봐야 합니다.
2. **길이 분포 붕괴**: `p99_length`가 갑자기 커지거나 줄면 tokenizer와 chunk 설정 비용이 함께 흔들립니다.
3. **언어·소스 비중 쏠림**: 특정 소스가 급증하면 한 세그먼트에서만 좋아 보이는 착시가 자주 생깁니다.

```python
def compare_reports(prev: dict, curr: dict) -> dict[str, float]:
    return {
        "duplicate_ratio_delta": curr["duplicate_ratio"] - prev["duplicate_ratio"],
        "p99_length_delta": curr["p99_length"] - prev["p99_length"],
        "null_ratio_delta": curr["null_ratio"] - prev["null_ratio"],
    }

prev = {"duplicate_ratio": 0.04, "p99_length": 820, "null_ratio": 0.01}
curr = {"duplicate_ratio": 0.13, "p99_length": 1410, "null_ratio": 0.03}
print(compare_reports(prev, curr))
```

**Expected output:**

```text
{'duplicate_ratio_delta': 0.09, 'p99_length_delta': 590, 'null_ratio_delta': 0.02}
```

수치가 이렇게 뛰면 먼저 데이터 버전 차이부터 확인해야 합니다. GPU 시간을 더 쓰기 전에 입력 데이터가 어디서 달라졌는지부터 좁혀 보는 편이 안전합니다.

이 보고서는 단순해 보여도 강력합니다. null 비율, 중복 비율, 길이 분포, 언어 분포를 이전 버전과 비교하면 학습을 시작하기 전에 이상 징후를 잡을 수 있습니다. 좋은 팀일수록 GPU를 켜기 전에 데이터 리포트를 먼저 봅니다.

## 흔히 헷갈리는 지점

- **모델만 강하면 데이터 문제를 덮을 수 있습니다**: 더 큰 모델은 더러운 데이터에서도 그럴듯한 출력을 낼 수 있지만, 평가 누수와 편향까지 해결하지는 못합니다.
- **데이터 준비는 초기에 한 번만 하면 됩니다**: 분포는 계속 변하므로 정제·필터링·분할 규칙도 코드처럼 버전 관리하고 반복 실행해야 합니다.
- **샘플 몇 줄만 훑어보면 데이터 상태를 알 수 있습니다**: long-tail 문제는 `head()`에서 거의 보이지 않습니다. 통계와 무작위 샘플을 함께 봐야 합니다.
- **정확도 하나만 보면 충분합니다**: 데이터 문제는 세그먼트별 성능, 누수, 중복, 언어 혼합 같은 형태로 나타나므로 단일 지표로는 숨겨집니다.

## 운영 체크리스트

- [ ] 데이터셋 버전마다 null 비율, 중복 비율, 길이 분포, 언어 분포 리포트를 자동 생성했다
- [ ] 학습 전에 평가셋 누수 가능성을 중복 검사 항목으로 넣었다
- [ ] 시계열·사용자 단위·클래스 불균형 여부에 따라 split 전략을 명시했다
- [ ] PII 처리와 토크나이저 선택을 데이터 준비 초기 설계에 포함했다
- [ ] 모델 실험 로그와 데이터 버전을 1:1로 추적할 수 있게 만들었다

## 정리

데이터 준비는 모델 학습 전에 잠깐 거치는 관문이 아닙니다. 어떤 정보를 모델이 보게 할지, 무엇을 평가 기준으로 삼을지, 어떤 위험을 사전에 차단할지를 결정하는 첫 번째 엔지니어링 단계입니다.

이 글에서 본 예제처럼 모델 코드를 바꾸지 않아도 데이터 정제만으로 성능 차이가 납니다. 그만큼 데이터 품질, 중복, 누수, 개인정보, 토큰 효율은 이후 단계 전체에 연쇄적으로 영향을 줍니다.

이 시리즈는 이제 수집과 카탈로깅부터 시작해 각 단계를 하나씩 구체화합니다. 다음 글에서는 데이터를 가져오는 순간부터 출처와 라이선스를 어떻게 함께 기록해야 재현성과 운영 안정성을 지킬 수 있는지 다룹니다.

## 처음 질문으로 돌아가기

- **모델 아키텍처보다 데이터 준비가 더 큰 차이를 만드는 순간은 언제일까요?**
  - 본문의 기준은 데이터 준비가 모델 품질을 결정하는 이유를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **겉보기 정확도는 높은데 실제 사용자 경험이 나빠지는 대표적인 데이터 실패는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **수집부터 분할까지의 데이터 준비 단계를 왜 하나의 파이프라인으로 봐야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **데이터 준비가 모델 품질을 결정하는 이유 (현재 글)**
- 원본 데이터 수집과 카탈로깅 (예정)
- 데이터 정제와 중복 제거 (예정)
- 학습 데이터 PII 탐지와 익명화 (예정)
- Tokenization과 Chunking 전략 (예정)
- 데이터 품질 필터링 — Heuristic과 Classifier (예정)
- 합성 데이터 생성 — Self-Instruct부터 Distillation까지 (예정)
- 데이터 증강 기법 — EDA부터 Back-Translation까지 (예정)
- 학습/평가/테스트 분할과 Contamination 통제 (예정)
- 프로덕션 데이터 파이프라인 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Andrew Ng - Data-centric AI Resources](https://datacentricai.org/)
- [The Pile: An 800GB Dataset of Diverse Text](https://arxiv.org/abs/2101.00027)
- [scikit-learn: Cross-validation and stratified splits](https://scikit-learn.org/stable/modules/cross_validation.html)
- [Google: Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml)

### 관련 시리즈
- [LLM 파인튜닝 101 — 데이터셋 준비와 전처리](../../llm-finetuning-101/ko/02-dataset.md)
- [AI Evaluation 101 — 평가 데이터셋 설계하기](../../ai-evaluation-101/ko/02-evaluation-dataset-design.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-data-preparation-101/ko/01-why-data-preparation-matters)

Tags: Data Preparation, ML Foundations, Data Quality, Pipelines
