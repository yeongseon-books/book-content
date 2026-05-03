---
title: 데이터 품질 필터링
series: ai-data-preparation-101
episode: 6
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Quality Filtering
- Heuristic Rules
- Classifier Filter
- perplexity
- KenLM
- fastText
last_reviewed: '2026-05-03'
---

# 데이터 품질 필터링 — Heuristic과 Classifier

> AI Data Preparation 101 시리즈 (6/10)

---
## "수집했다고 다 학습데이터인가요?"

원본 corpus는 거의 항상 절반 이상이 쓰레기입니다. 광고, 자동 생성 spam, 깨진 인코딩, 의미 없는 boilerplate가 섞여 있습니다. 이걸 그대로 학습시키면 model perplexity가 망가지고 hallucination 비율이 올라갑니다.

Quality filtering의 목표는 "이 sample이 학습에 도움이 되는가"를 판정하는 것입니다. 두 가지 접근이 있습니다.

1. **Heuristic filtering**: 빠른 rule 기반 (ratio, length, repetition)
2. **Model-based filtering**: classifier 또는 perplexity score

production은 둘 다 씁니다. heuristic으로 명백한 쓰레기를 떨어내고, classifier로 borderline을 거릅니다.

## Heuristic filter — 7가지 기본 rule

CCNet, RefinedWeb, C4 같은 대형 corpus가 쓰는 기본 rule들입니다.

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

각 threshold는 domain에 맞춰 조정합니다. 코드 corpus라면 symbol_ratio 한계를 0.5로 올리고, 한국어라면 avg_word_len 범위를 넓혀야 합니다.

## Language detection — domain 외 sample 제거

multilingual scrape에서 원하는 언어만 남길 때.

```python
# pip install fasttext-langdetect
from ftlangdetect import detect

def keep_languages(text: str, allowed: set[str], min_conf: float = 0.7) -> bool:
    sample = text[:1000]  # 앞부분만 봐도 충분
    result = detect(text=sample, low_memory=True)
    return result["lang"] in allowed and result["score"] >= min_conf

# 한국어와 영어만 남기기
ok = keep_languages(doc, allowed={"ko", "en"})
```

fasttext가 빠르고 정확합니다. langdetect 같은 순수 python 라이브러리는 짧은 문장에서 흔들립니다.

## Perplexity filter — KenLM 기반

자연스러운 문장은 좋은 LM에서 perplexity가 낮습니다. 비정상적으로 높은 sample은 깨진 텍스트일 가능성이 큽니다.

```python
# pip install kenlm
import kenlm
import math

class PerplexityFilter:
    def __init__(self, model_path: str, max_perplexity: float = 1000.0):
        self.model = kenlm.Model(model_path)
        self.max_perplexity = max_perplexity

    def score(self, text: str) -> float:
        # KenLM은 log10 확률을 반환
        log_prob = self.model.score(text, bos=True, eos=True)
        n_tokens = len(text.split()) + 1
        return 10 ** (-log_prob / n_tokens)

    def passes(self, text: str) -> bool:
        return self.score(text) <= self.max_perplexity

# Wikipedia로 학습한 KenLM model을 기준으로 사용
pf = PerplexityFilter("wiki-ko.binary", max_perplexity=500.0)
```

CCNet 논문이 사용한 방식입니다. Wikipedia를 reference로 잡으면 "위키처럼 자연스러운가"를 측정하는 셈입니다.

## Classifier filter — fastText로 quality score

GPT-3는 reddit upvote를 positive label로 써서 fastText classifier를 학습했습니다. 같은 패턴을 쉽게 재현할 수 있습니다.

```python
# pip install fasttext
import fasttext

# 1) 학습 데이터 준비: 위키/책은 positive, common-crawl 잡문은 negative
# format: __label__pos text...
# train.txt를 만들어둔 상태라고 가정
model = fasttext.train_supervised(
    input="train.txt",
    epoch=10,
    lr=0.5,
    wordNgrams=2,
    dim=100,
)
model.save_model("quality-clf.bin")

# 2) inference
clf = fasttext.load_model("quality-clf.bin")

def quality_score(text: str) -> float:
    labels, probs = clf.predict(text.replace("\n", " "), k=2)
    # __label__pos 의 확률
    return float(probs[labels.index("__label__pos")]) if "__label__pos" in labels else 0.0

threshold = 0.5
keep = quality_score(doc) >= threshold
```

fastText는 cpu에서도 초당 수만 sample을 처리합니다. 대형 corpus 필터링에 적합합니다.

## 통합 pipeline

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

순서가 중요합니다. heuristic은 가장 빠르므로 먼저 돌립니다. perplexity와 classifier는 모델을 호출하니 마지막입니다. 명백한 쓰레기를 일찍 떨어낼수록 cost가 줄어듭니다.

## 흔한 실수 5가지

1. **Threshold를 처음부터 hard-code**: 매 batch마다 분포가 달라집니다. histogram을 그려보고 percentile 기반으로 정합니다 (예: 하위 5% 제거).
2. **Heuristic만으로 충분하다고 가정**: spam, scraped boilerplate는 heuristic을 통과합니다. classifier가 필요합니다.
3. **Reference corpus가 작거나 편향됨**: KenLM을 1MB Wikipedia dump로 학습하면 perplexity가 의미 없는 숫자가 됩니다. 최소 수 GB 이상으로 학습합니다.
4. **language detection을 전체 텍스트에 실행**: 1000자 sampling이면 충분합니다. 전체 실행은 cost만 늘립니다.
5. **filtering 후 분포 변화를 측정 안 함**: filter가 한쪽 domain만 살려놓는 경우가 흔합니다. before/after distribution을 token count, language, source별로 비교합니다.

## 핵심 요약

- Quality filtering은 heuristic + model-based의 2단계 조합입니다.
- Heuristic은 length, symbol/digit/upper ratio, repetition을 빠르게 잘라냅니다.
- Language detection은 fasttext-langdetect로 1000자 sampling이면 충분합니다.
- Perplexity filter는 KenLM 같은 reference LM이 필요하며 깨진 텍스트 제거에 강합니다.
- fastText classifier는 cpu에서 초당 수만 건을 처리하며 GPT-3가 사용한 방식입니다.
- Pipeline 순서는 cheap -> expensive로 두어 cost를 최소화합니다.
- 다음 편(7편)은 synthetic data generation입니다.

---

<!-- toc:begin -->
## AI Data Preparation 101 시리즈

- [데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- [데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
- [학습 데이터 PII 탐지와 익명화](./04-pii-detection-anonymization.md)
- [Tokenization과 Chunking 전략](./05-tokenization-chunking.md)
- **데이터 품질 필터링 — Heuristic과 Classifier (현재 글)**
- 합성 데이터 생성 (예정)
- 데이터 증강 기법 (예정)
- 학습/평가/테스트 분할과 오염 통제 (예정)
- 프로덕션 데이터 파이프라인 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [CCNet: Extracting High Quality Monolingual Datasets from Web Crawl Data (Wenzek et al., 2020)](https://arxiv.org/abs/1911.00359)
- [The RefinedWeb Dataset for Falcon LLM (Penedo et al., 2023)](https://arxiv.org/abs/2306.01116)
- [KenLM Language Model Toolkit](https://kheafield.com/code/kenlm/)
- [fastText Quality Classifier (used in GPT-3)](https://fasttext.cc/docs/en/supervised-tutorial.html)

Tags: Quality Filtering, Heuristic Rules, Classifier Filter, perplexity, KenLM, fastText
