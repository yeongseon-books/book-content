---
episode: 6
language: ko
last_reviewed: '2026-05-12'
seo_description: 광고와 스팸이 섞인 corpus를 학습 가능한 상태로 만드는 heuristic 필터와 classifier 기반 필터를
  비교합니다.
series: ai-data-preparation-101
status: publish-ready
tags:
- Quality Filtering
- Heuristic Rules
- Classifier Filter
- perplexity
- KenLM
- fastText
targets:
  ebook: true
  medium: false
  mkdocs: true
  tistory: true
title: "AI Data Preparation 101 (6/10): 데이터 품질 필터링 — Heuristic과 Classifier"
---

# AI Data Preparation 101 (6/10): 데이터 품질 필터링 — Heuristic과 Classifier

수집과 정제를 거친 데이터라도 그대로 학습에 넣을 수 있는 경우는 드뭅니다. 광고 문구, 자동 생성 스팸, 깨진 인코딩, 의미 없는 boilerplate가 절반 이상 섞여 있는 코퍼스는 생각보다 흔합니다.

문제는 이런 샘플이 단지 지저분해 보이는 수준에서 끝나지 않는다는 점입니다. 저품질 샘플은 perplexity를 악화시키고, 환각 비율을 높이고, 특정 도메인 편향을 몰래 주입합니다. 그래서 품질 필터링은 나쁜 데이터를 제거하는 단계이자, 학습 가치가 있는 샘플을 남기는 분류 단계입니다.

운영에서는 heuristic rule과 모델 기반 필터를 따로 보지 않습니다. 값이 뻔한 garbage는 규칙으로 빨리 제거하고, 애매한 경계선 샘플은 classifier나 perplexity filter로 넘기는 식으로 비용을 나눕니다.

좋은 품질 필터는 완벽한 판정을 약속하지 않습니다. 대신 값싼 순서로 많은 샘플을 걸러내고, 어떤 규칙 때문에 빠졌는지 통계로 남겨 나중에 threshold를 조정할 수 있게 만듭니다.

이 글은 AI Data Preparation 101 시리즈의 6번째 글입니다.

여기서는 heuristic과 classifier를 조합해 품질 필터를 설계하는 방법과, 언어 감지·perplexity·quality score를 어떤 순서로 배치해야 효율적인지 설명하겠습니다.

## 먼저 던지는 질문

- 왜 수집된 데이터와 학습 가능한 데이터는 같은 집합이 아닐까요?
- 길이, symbol ratio, digit ratio, repetition 같은 heuristic signal은 무엇을 빠르게 잡아낼까요?
- 언어 감지와 perplexity filter는 각각 어떤 종류의 오염을 제거할까요?

## 큰 그림

![AI 데이터 준비 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/06/06-01-big-picture.ko.png)

*AI 데이터 준비 6장 흐름 개요*

이 그림에서는 데이터 품질 필터링 — Heuristic과 Classifier를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 데이터 품질 필터링 — Heuristic과 Classifier의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

품질 필터링을 잘하면 모델이 실제로 학습할 가치가 있는 샘플에 더 많은 예산을 쓰게 됩니다. 같은 양의 데이터라도 학습 곡선이 더 안정적이고, 분포 drift 감지도 더 빨라집니다.

반대로 저품질 샘플을 그대로 두면 데이터셋은 커 보이지만 밀도는 낮아집니다. 광고, 스팸, 언어 혼입, 깨진 텍스트가 그대로 남아 있으면 모델은 유용한 패턴보다 잡음을 더 많이 보게 됩니다.

이 글은 품질 필터를 “데이터를 많이 버리는 단계”가 아니라 “학습 가치와 운영 비용을 동시에 최적화하는 단계”로 이해하게 만드는 데 초점을 둡니다.

## 핵심 관점

품질 필터는 한 번의 점수로 좋은 문서와 나쁜 문서를 완전히 나누는 문제가 아닙니다. 길이, 기호 비율, 반복률처럼 거의 공짜인 signal이 있고, 언어 감지와 perplexity처럼 조금 더 비싼 signal이 있고, classifier처럼 학습된 판정기가 있습니다.

운영에서는 항상 값싼 단계부터 먼저 실행합니다. obvious garbage를 초반에 제거해야 이후 단계의 모델 호출 비용이 줄고, 어떤 이유로 얼마나 버렸는지도 해석하기 쉬워집니다.

또한 threshold는 정답이 아니라 운영 가설입니다. 배치별 분포가 바뀌므로 histogram과 percentile을 보면서 계속 조정할 수 있어야 합니다.

> 품질 필터링의 핵심은 완벽한 분류기가 아니라, 값싼 규칙으로 대부분을 정리하고 비싼 모델은 경계선 샘플에만 쓰도록 단계별 비용을 설계하는 것입니다.

## 핵심 개념

### Heuristic filter는 일곱 가지 기본 signal에서 시작합니다

대규모 웹 코퍼스에서 공통적으로 쓰는 기준은 길이, 평균 단어 길이, symbol ratio, digit ratio, 대문자 비율, 반복률 같은 수치입니다.

```python
import re
from dataclasses import dataclass

@dataclass
class QualitySignals:
    n_chars: int
    n_words: int
    avg_word_len: float
    symbol_ratio: float
    digit_ratio: float
    upper_ratio: float
    repetition_ratio: float

def compute_signals(text: str) -> QualitySignals:
    n_chars = len(text)
    words = text.split()
    n_words = len(words)
    if n_words == 0:
        return QualitySignals(n_chars, 0, 0, 1, 1, 1, 1)
    avg_word_len = sum(len(w) for w in words) / n_words
    symbol_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / max(n_chars, 1)
    digit_ratio = sum(1 for c in text if c.isdigit()) / max(n_chars, 1)
    upper_ratio = sum(1 for c in text if c.isupper()) / max(n_chars, 1)
    # 5-gram repetition
    grams = [" ".join(words[i:i+5]) for i in range(len(words)-4)]
    repetition_ratio = 1 - len(set(grams)) / max(len(grams), 1)
    return QualitySignals(n_chars, n_words, avg_word_len,
                          symbol_ratio, digit_ratio, upper_ratio, repetition_ratio)

def passes_heuristic(text: str) -> tuple[bool, str]:
    s = compute_signals(text)
    if s.n_words < 50:
        return False, "too_short"
    if s.n_words > 100_000:
        return False, "too_long"
    if s.avg_word_len < 2 or s.avg_word_len > 15:
        return False, "bad_avg_word_len"
    if s.symbol_ratio > 0.3:
        return False, "symbol_heavy"
    if s.digit_ratio > 0.5:
        return False, "digit_heavy"
    if s.upper_ratio > 0.4:
        return False, "shouting"
    if s.repetition_ratio > 0.3:
        return False, "repetitive"
    return True, "ok"
```

이 값들은 도메인별로 조정해야 합니다. 예를 들어 코드 코퍼스라면 symbol ratio 상한을 높여야 하고, 한국어 문서는 평균 단어 길이 기준을 영어와 다르게 잡아야 합니다.

### 언어 감지로 out-of-domain 샘플을 제거합니다

다국어 스크레이핑 데이터에서 언어 혼입은 매우 흔합니다. 모든 문서를 직접 눈으로 볼 수 없기 때문에 빠른 language filter가 필요합니다.

```python
# pip install fasttext-langdetect
from ftlangdetect import detect

def keep_languages(text: str, allowed: set[str], min_conf: float = 0.7) -> bool:
    sample = text[:1000]  # the head is enough
    result = detect(text=sample, low_memory=True)
    return result["lang"] in allowed and result["score"] >= min_conf

# Keep only Korean and English
ok = keep_languages(doc, allowed={"ko", "en"})
```

짧은 헤드 1,000자만으로도 충분한 경우가 많습니다. 전체 텍스트에 대해 언어 감지를 돌리는 것은 비용만 늘리고 실익은 크지 않습니다.

### Perplexity filter는 깨진 텍스트를 잘 걸러냅니다

정상적인 문장은 기준 언어모델 아래에서 비교적 낮은 perplexity를 가집니다. 반대로 깨진 인코딩이나 의미 없는 boilerplate는 비정상적으로 높게 나옵니다.

```python
# pip install kenlm
import kenlm
import math

class PerplexityFilter:
    def __init__(self, model_path: str, max_perplexity: float = 1000.0):
        self.model = kenlm.Model(model_path)
        self.max_perplexity = max_perplexity

    def score(self, text: str) -> float:
        # KenLM returns log10 probability
        log_prob = self.model.score(text, bos=True, eos=True)
        n_tokens = len(text.split()) + 1
        return 10 ** (-log_prob / n_tokens)

    def passes(self, text: str) -> bool:
        return self.score(text) <= self.max_perplexity

# Use a KenLM model trained on Wikipedia as the reference
pf = PerplexityFilter("wiki-en.binary", max_perplexity=500.0)
```

CCNet이 Wikipedia 기반 KenLM을 reference로 쓴 것도 같은 이유입니다. 결국 이 문서가 “정상적인 텍스트처럼 보이는가”를 값으로 재는 것입니다.

### Classifier filter는 애매한 경계 샘플을 처리합니다

heuristic은 obvious junk에 강하지만, 보기에는 문장처럼 생긴 저품질 페이지를 잘 못 잡습니다. 이 구간을 quality classifier가 메웁니다.

```python
# pip install fasttext
import fasttext

# 1) Prepare training data: wiki/books as positive, common-crawl junk as negative
# format: __label__pos text...
# Assume train.txt is prepared
model = fasttext.train_supervised(
    input="train.txt",
    epoch=10,
    lr=0.5,
    wordNgrams=2,
    dim=100,
)
model.save_model("quality-clf.bin")

# 2) Inference
clf = fasttext.load_model("quality-clf.bin")

def quality_score(text: str) -> float:
    labels, probs = clf.predict(text.replace("\n", " "), k=2)
    # Probability of __label__pos
    return float(probs[labels.index("__label__pos")]) if "__label__pos" in labels else 0.0

threshold = 0.5
keep = quality_score(doc) >= threshold
```

CPU에서 빠르게 돌아가는 fastText는 대규모 코퍼스 필터링에 잘 맞습니다. Wikipedia·books를 positive, low-quality crawl을 negative로 두는 식의 weak supervision도 실전에서 자주 씁니다.

### 통합 파이프라인은 cheap → expensive 순서로 둡니다

```python
def quality_filter_pipeline(docs: list[str], pf: PerplexityFilter, clf) -> list[str]:
    survivors = []
    stats = {"heuristic": 0, "lang": 0, "perplexity": 0, "classifier": 0, "kept": 0}
    for d in docs:
        ok, reason = passes_heuristic(d)
        if not ok:
            stats["heuristic"] += 1
            continue
        if not keep_languages(d, allowed={"ko", "en"}):
            stats["lang"] += 1
            continue
        if not pf.passes(d):
            stats["perplexity"] += 1
            continue
        if quality_score(d) < 0.5:
            stats["classifier"] += 1
            continue
        survivors.append(d)
        stats["kept"] += 1
    return survivors, stats
```

이 순서가 중요한 이유는 두 가지입니다. 첫째, 명백한 garbage를 앞단에서 제거해야 비용이 줄어듭니다. 둘째, stage별 drop count를 남겨야 어떤 기준이 지나치게 공격적인지 분석할 수 있습니다.

### threshold는 하드코딩보다 분포 기반 조정이 낫습니다

처음부터 `symbol_ratio > 0.3` 같은 값을 영원한 기준처럼 박아 두면 배치 분포가 바뀔 때 대응하기 어렵습니다. 운영에서는 다음을 같이 봐야 합니다.

- 필터 전후의 언어 분포 변화
- 길이 분포와 token count 분포 변화
- source별 drop rate 차이
- 특정 도메인 문서만 과하게 남거나 사라지지 않는지

좋은 품질 필터는 버리는 양이 아니라 **어떤 이유로 버렸는지 설명 가능한 통계**를 남깁니다.

## 품질 필터 결과를 대시보드 지표로 고정하기

필터링 파이프라인의 성공 기준은 “많이 걸렀다”가 아니라 “왜 걸렀는지 설명 가능하다”입니다. 그래서 stage별 drop 통계를 배치 리포트로 남겨야 threshold 회귀를 추적할 수 있습니다.

```python
import pandas as pd

def build_drop_report(rows: list[dict]) -> pd.DataFrame:
    # rows: {doc_id, stage, decision, reason}
    df = pd.DataFrame(rows)
    report = (
        df.groupby(["stage", "reason", "decision"], dropna=False)
          .size()
          .reset_index(name="count")
          .sort_values(["stage", "count"], ascending=[True, False])
    )
    return report

def acceptance_by_source(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    agg = df.groupby(["source", "decision"]).size().unstack(fill_value=0)
    agg["accept_ratio"] = agg.get("keep", 0) / agg.sum(axis=1)
    return agg.reset_index()
```

## 품질 점수 모델 검증(간이)

classifier를 붙였다면 최소한 calibration을 확인해야 합니다. 스코어 0.9가 실제로도 고품질 비율 90% 근처인지 확인하지 않으면 threshold를 안정적으로 운영할 수 없습니다.

```python
from sklearn.calibration import calibration_curve

# y_true: 1=good, 0=bad
# y_prob: classifier probability for good
def calibration_summary(y_true, y_prob):
    frac_pos, mean_pred = calibration_curve(y_true, y_prob, n_bins=10)
    return [{"bin_pred": float(p), "bin_true": float(t)} for p, t in zip(mean_pred, frac_pos)]
```

## Label Studio로 경계 샘플 재라벨링

`0.45~0.55` 구간 샘플은 모델이 가장 헷갈리는 데이터입니다. 이 구간만 사람에게 다시 라벨링받으면 다음 버전 정확도가 크게 오르는 경우가 많습니다.

```xml
<View>
  <Text name="doc" value="$text"/>
  <Choices name="quality" toName="doc" choice="single">
    <Choice value="good"/>
    <Choice value="bad"/>
    <Choice value="borderline"/>
  </Choices>
  <TextArea name="reason" toName="doc" placeholder="판단 이유"/>
</View>
```

## before/after 샘플

```text
[drop: repetitive]
지금 클릭 지금 클릭 지금 클릭 지금 클릭 ...

[keep]
환불 지연 문의의 평균 처리 시간은 24시간이며, 주말에는 48시간까지 늘어날 수 있습니다.
```

이런 샘플과 통계를 같이 남기면 “필터가 과하게 공격적이다” 같은 논의를 데이터로 빠르게 정리할 수 있습니다.

## DVC 파이프라인 단계

```yaml
stages:
  quality_filter:
    cmd: python pipelines/quality_filter.py --input data/clean/train.parquet --output data/quality/train_filtered.parquet
    deps:
      - pipelines/quality_filter.py
      - data/clean/train.parquet
    outs:
      - data/quality/train_filtered.parquet
    metrics:
      - reports/quality_filter_metrics.json
      - reports/quality_filter_drop_report.csv
```

품질 필터는 한 번 맞추고 끝나는 규칙이 아닙니다. 배치마다 분포가 바뀌므로 리포트 기반 재조정이 기본 운영 루프가 되어야 합니다.

## quality score drift 감지

품질 분류기를 운영하면 스코어 분포 자체가 변하는 시점이 옵니다. 모델이 망가진 것이 아니라 입력 분포가 바뀐 경우가 많습니다.

```python
import numpy as np

def psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    eps = 1e-6
    cuts = np.quantile(expected, np.linspace(0, 1, bins + 1))
    e_hist, _ = np.histogram(expected, bins=cuts)
    a_hist, _ = np.histogram(actual, bins=cuts)
    e = e_hist / max(e_hist.sum(), 1) + eps
    a = a_hist / max(a_hist.sum(), 1) + eps
    return float(np.sum((a - e) * np.log(a / e)))
```

PSI가 임계값을 넘으면 threshold를 재튜닝하거나, 소스별 필터를 분리해야 합니다. 이 과정을 자동화하지 않으면 필터 성능은 시간이 갈수록 조용히 악화됩니다.

## 소스별 정책 분리

같은 threshold를 모든 소스에 강제하면 특정 도메인이 과도하게 삭제될 수 있습니다. 뉴스, 포럼, 제품 문서는 본질적으로 길이·기호 분포가 다르기 때문입니다.

```python
SOURCE_THRESHOLDS = {
    "news": {"max_symbol_ratio": 0.22, "max_perplexity": 420},
    "forum": {"max_symbol_ratio": 0.28, "max_perplexity": 520},
    "docs": {"max_symbol_ratio": 0.18, "max_perplexity": 380},
}
```

이처럼 소스별 기준을 분리하면 불필요한 데이터 손실을 줄이면서도 전체 품질을 일정하게 유지할 수 있습니다.

## 운영에서 바로 쓰는 점검 질문

아래 질문은 배포 직전 리뷰에서 실제로 자주 쓰는 체크 항목입니다. 단순 문서 확인이 아니라, 각 질문에 대해 파일 경로나 지표 값으로 즉시 답할 수 있어야 합니다.

1. 이번 데이터셋은 어떤 버전에서 왔고, sha256은 무엇인가요?
2. 지난 배치 대비 duplicate/null/length 분포가 얼마나 변했나요?
3. 제거된 샘플은 어떤 규칙 때문에 빠졌고, 상위 제거 사유는 무엇인가요?
4. train/eval/test 경계에서 누수 가능성은 수치로 얼마나 남아 있나요?
5. 이번 배치에서 사람이 검토한 샘플과 발견된 오류 유형은 무엇인가요?

```python
def release_readiness(summary: dict) -> tuple[bool, list[str]]:
    issues = []
    if not summary.get("dataset_sha256"):
        issues.append("missing_dataset_sha256")
    if summary.get("duplicate_ratio", 1.0) > 0.10:
        issues.append("duplicate_ratio_too_high")
    if summary.get("null_ratio", 1.0) > 0.02:
        issues.append("null_ratio_too_high")
    if summary.get("contamination_ratio", 1.0) > 0.01:
        issues.append("contamination_ratio_too_high")
    if summary.get("human_reviewed_rows", 0) < 100:
        issues.append("insufficient_human_review")
    return len(issues) == 0, issues
```

운영 팀은 이 함수를 그대로 쓰지 않더라도 같은 개념을 파이프라인 게이트로 구현해야 합니다. 핵심은 “준비가 되었는지 느낌으로 판단하지 않는다”는 점입니다.

## 실무 로그 예시

```text
[release-check] dataset=v2.4.1 sha=4fb1...
[release-check] duplicate_ratio=0.061 null_ratio=0.008
[release-check] contamination_ratio=0.004 human_reviewed_rows=240
[release-check] status=PASS
```

이 로그 한 묶음이 있으면 모델 성능이 흔들릴 때도 데이터 준비 단계를 빠르게 제외하거나 집중 점검할 수 있습니다. 데이터 준비의 품질은 글 한 편의 설명보다, 이런 반복 가능한 검증 로그에서 드러납니다.

### 품질 필터 재학습 주기

classifier 기반 필터는 분기마다 최소 한 번 재학습 후보를 검토하는 것이 안전합니다. 소스 도메인이 바뀌면 기존 negative 샘플이 낡아 경계 판단이 빠르게 흔들리기 때문입니다.

### 릴리스 노트에 남겨야 할 최소 항목

해당 단계의 변경은 릴리스 노트에도 남겨야 합니다. 최소한 `변경 규칙`, `영향받은 행 수`, `핵심 지표 변화`, `롤백 경로` 네 항목이 있어야 다음 배치에서 같은 판단을 반복할 수 있습니다.

필터는 정확도 지표뿐 아니라 제거 사유 분포의 안정성까지 함께 모니터링해야 합니다.

소스 유입이 바뀐 주에는 threshold 재점검을 기본 운영 절차로 두는 편이 좋습니다.

필터 규칙 변경 시에는 최소 하루치 배치를 shadow run으로 먼저 돌린 뒤 본 반영하는 절차를 권장합니다.

## 흔히 헷갈리는 지점

- **heuristic만 잘 짜면 classifier는 필요 없습니다**: 스팸과 보일러플레이트 중에는 규칙을 통과하는 샘플이 많아 classifier가 필요합니다.
- **threshold는 한 번 정하면 계속 쓸 수 있습니다**: 데이터 소스와 시기가 바뀌면 분포가 변하므로 histogram과 percentile 기준으로 주기적으로 조정해야 합니다.
- **언어 감지는 전체 문서에 돌려야 정확합니다**: 대부분 1,000자 샘플로 충분하며 전체 실행은 비용 대비 효용이 낮습니다.
- **perplexity가 높으면 무조건 나쁜 데이터입니다**: 도메인 특화 문서나 코드처럼 reference LM과 다른 분포는 예외가 있어 domain-aware 해석이 필요합니다.

## 운영 체크리스트

- [ ] heuristic signal별 분포와 threshold 근거를 배치 통계로 기록했다
- [ ] 언어 감지, perplexity, classifier를 cheap → expensive 순서로 실행한다
- [ ] quality filter 전후의 언어·길이·source 분포를 비교한다
- [ ] fastText 또는 동급 classifier의 positive/negative 학습 데이터를 문서화했다
- [ ] stage별 drop reason 통계를 남겨 threshold 회귀를 추적한다

## 정리

품질 필터링은 데이터셋을 작게 만드는 단계가 아니라 학습 가치가 높은 샘플을 남기는 단계입니다. heuristic과 classifier를 함께 써야 속도와 품질을 모두 잡을 수 있습니다.

길이, 기호 비율, 반복률 같은 기본 규칙은 빠르고 해석 가능하며, 언어 감지·perplexity·classifier는 그 위에서 더 미묘한 저품질 샘플을 정리합니다. 중요한 것은 순서와 통계입니다.

다음 글에서는 사람이 직접 레이블링하기 어려울 때 감독 신호를 확장하는 합성 데이터 생성 기법을 다룹니다. 품질 필터를 통과한 코퍼스 위에서 synthetic generation이 어떻게 붙는지 자연스럽게 이어집니다.

## 처음 질문으로 돌아가기

- **왜 수집된 데이터와 학습 가능한 데이터는 같은 집합이 아닐까요?**
  - 본문의 기준은 데이터 품질 필터링 — Heuristic과 Classifier를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **길이, symbol ratio, digit ratio, repetition 같은 heuristic signal은 무엇을 빠르게 잡아낼까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **언어 감지와 perplexity filter는 각각 어떤 종류의 오염을 제거할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Data Preparation 101 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [AI Data Preparation 101 (2/10): 원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- [AI Data Preparation 101 (3/10): 데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
- [AI Data Preparation 101 (4/10): 학습 데이터 PII 탐지와 익명화](./04-pii-detection-anonymization.md)
- [AI Data Preparation 101 (5/10): Tokenization과 Chunking 전략](./05-tokenization-chunking.md)
- **데이터 품질 필터링 — Heuristic과 Classifier (현재 글)**
- 합성 데이터 생성 — Self-Instruct부터 Distillation까지 (예정)
- 데이터 증강 기법 — EDA부터 Back-Translation까지 (예정)
- 학습/평가/테스트 분할과 Contamination 통제 (예정)
- 프로덕션 데이터 파이프라인 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [CCNet: Extracting High Quality Monolingual Datasets from Web Crawl Data (Wenzek et al., 2020)](https://arxiv.org/abs/1911.00359)
- [The RefinedWeb Dataset for Falcon LLM (Penedo et al., 2023)](https://arxiv.org/abs/2306.01116)
- [KenLM Language Model Toolkit](https://kheafield.com/code/kenlm/)
- [fastText Quality Classifier (used in GPT-3)](https://fasttext.cc/docs/en/supervised-tutorial.html)

### 관련 시리즈
- [LLM 파인튜닝 101 — 데이터셋 준비와 전처리](../../llm-finetuning-101/ko/02-dataset.md)
- [AI Evaluation 101 — LLM-as-Judge — 모델로 모델을 평가하기](../../ai-evaluation-101/ko/04-llm-as-judge.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-data-preparation-101/ko/06-quality-filtering)

Tags: Quality Filtering, Heuristic Rules, Classifier Filter, perplexity, KenLM, fastText
