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
  medium: true
  mkdocs: true
  tistory: true
title: 데이터 품질 필터링 — Heuristic과 Classifier
---

# 데이터 품질 필터링 — Heuristic과 Classifier

수집과 정제를 거친 데이터라도 그대로 학습에 넣을 수 있는 경우는 드뭅니다. 광고 문구, 자동 생성 스팸, 깨진 인코딩, 의미 없는 boilerplate가 절반 이상 섞여 있는 코퍼스는 생각보다 흔합니다.

문제는 이런 샘플이 단지 지저분해 보이는 수준에서 끝나지 않는다는 점입니다. 저품질 샘플은 perplexity를 악화시키고, 환각 비율을 높이고, 특정 도메인 편향을 몰래 주입합니다. 그래서 품질 필터링은 나쁜 데이터를 제거하는 단계이자, 학습 가치가 있는 샘플을 남기는 분류 단계입니다.

운영에서는 heuristic rule과 모델 기반 필터를 따로 보지 않습니다. 값이 뻔한 garbage는 규칙으로 빨리 제거하고, 애매한 경계선 샘플은 classifier나 perplexity filter로 넘기는 식으로 비용을 나눕니다.

좋은 품질 필터는 완벽한 판정을 약속하지 않습니다. 대신 값싼 순서로 많은 샘플을 걸러내고, 어떤 규칙 때문에 빠졌는지 통계로 남겨 나중에 threshold를 조정할 수 있게 만듭니다.

이 글은 AI Data Preparation 101 시리즈의 6번째 글입니다.

여기서는 heuristic과 classifier를 조합해 품질 필터를 설계하는 방법과, 언어 감지·perplexity·quality score를 어떤 순서로 배치해야 효율적인지 설명하겠습니다.

## 이 글에서 다룰 문제

- 왜 수집된 데이터와 학습 가능한 데이터는 같은 집합이 아닐까요?
- 길이, symbol ratio, digit ratio, repetition 같은 heuristic signal은 무엇을 빠르게 잡아낼까요?
- 언어 감지와 perplexity filter는 각각 어떤 종류의 오염을 제거할까요?
- fastText 기반 quality classifier는 heuristic만으로 못 잡는 어떤 경계 샘플을 걸러낼까요?
- 품질 필터의 threshold를 코드에 고정해 두면 왜 시간이 갈수록 위험해질까요?

## 왜 이 글이 중요한가

품질 필터링을 잘하면 모델이 실제로 학습할 가치가 있는 샘플에 더 많은 예산을 쓰게 됩니다. 같은 양의 데이터라도 학습 곡선이 더 안정적이고, 분포 drift 감지도 더 빨라집니다.

반대로 저품질 샘플을 그대로 두면 데이터셋은 커 보이지만 밀도는 낮아집니다. 광고, 스팸, 언어 혼입, 깨진 텍스트가 그대로 남아 있으면 모델은 유용한 패턴보다 잡음을 더 많이 보게 됩니다.

이 글은 품질 필터를 “데이터를 많이 버리는 단계”가 아니라 “학습 가치와 운영 비용을 동시에 최적화하는 단계”로 이해하게 만드는 데 초점을 둡니다.

## 품질 필터링을 이해하는 가장 좋은 방법: 싼 규칙부터 비싼 모델까지 계층적으로 배치하는 것입니다

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

<!-- toc:begin -->
## 시리즈 목차

- [데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- [데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
- [학습 데이터 PII 탐지와 익명화](./04-pii-detection-anonymization.md)
- [Tokenization과 Chunking 전략](./05-tokenization-chunking.md)
- **데이터 품질 필터링 — Heuristic과 Classifier (현재 글)**
- [합성 데이터 생성 — Self-Instruct부터 Distillation까지](./07-synthetic-data-generation.md)
- [데이터 증강 기법 — EDA부터 Back-Translation까지](./08-data-augmentation.md)
- [학습/평가/테스트 분할과 Contamination 통제](./09-train-eval-test-splitting.md)
- [프로덕션 데이터 파이프라인 구축](./10-production-data-pipeline.md)
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

Tags: Quality Filtering, Heuristic Rules, Classifier Filter, perplexity, KenLM, fastText
