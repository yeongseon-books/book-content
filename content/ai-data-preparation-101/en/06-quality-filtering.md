---
episode: 6
language: en
last_reviewed: '2026-05-14'
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
  tistory: false
title: "AI Data Preparation 101 (6/10): Quality Filtering - Heuristics and Classifiers"
seo_description: A raw corpus is almost always more than half garbage. Ads, auto-generated
  spam, broken encodings, and meaningless boilerplate are mixed in.
---

# AI Data Preparation 101 (6/10): Quality Filtering - Heuristics and Classifiers

Collected data is rarely clean enough to become training data as-is. The real question is how quickly you can separate usable samples from ads, spam, encoding breakage, and boilerplate before they distort learning.

This is post 6 in the AI Data Preparation 101 series. Here we cover how heuristic rules and classifier-based filters work together to keep low-value samples out of the corpus.

## Questions to Keep in Mind

- Which low-cost heuristics catch obvious junk before you spend model calls on it?
- What does language detection remove that simple length or symbol checks cannot?
- How should perplexity and classifier scores sit behind the heuristic layer?

## Big Picture

![AI data preparation chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/06/06-01-big-picture.en.png)

*AI data preparation chapter 6 flow overview*

This picture places Quality Filtering - Heuristics and Classifiers inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## "Collected does not mean trainable."

A raw corpus is almost always more than half garbage. Ads, auto-generated spam, broken encodings, and meaningless boilerplate are mixed in. Training on it directly wrecks model perplexity and inflates hallucination rates.

The goal of quality filtering is to decide whether a sample helps training. Two approaches:

1. **Heuristic filtering**: fast rule-based (ratios, length, repetition)
2. **Model-based filtering**: classifiers or perplexity scores

Production uses both. Heuristics drop the obvious garbage; classifiers handle the borderline cases.

## Heuristic filter - 7 baseline rules

These are the basic rules used by large corpora like CCNet, RefinedWeb, and C4.

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

Tune each threshold to your domain. For a code corpus, raise the symbol_ratio limit to 0.5; for Korean text, widen the avg_word_len range.

## Language detection - drop out-of-domain samples

When you want to keep only specific languages from a multilingual scrape.

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

fastText is fast and accurate. Pure-Python libraries like langdetect are unreliable on short text.

## Perplexity filter - KenLM-based

Natural sentences score low perplexity under a good LM. Abnormally high samples are likely broken text.

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

This is the approach in the CCNet paper. Using Wikipedia as reference means you measure "how Wikipedia-like is this".

## Classifier filter - fastText quality score

GPT-3 trained a fastText classifier with reddit upvotes as the positive label. The pattern is easy to reproduce.

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

fastText handles tens of thousands of samples per second on CPU. It is well suited to large-corpus filtering.

## Integrated pipeline

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

Ordering matters. Heuristics run first because they are fastest. Perplexity and classifiers call models, so they run last. Dropping obvious garbage early reduces cost.

## 5 common mistakes

1. **Hard-coding thresholds upfront**: distributions shift batch by batch. Plot histograms and use percentile-based cutoffs (e.g., drop the bottom 5%).
2. **Assuming heuristics alone are enough**: spam and scraped boilerplate pass heuristics. A classifier is required.
3. **Reference corpus too small or biased**: training KenLM on a 1MB Wikipedia dump produces meaningless perplexity numbers. Use at least several GB.
4. **Running language detection on full text**: a 1000-character sample is enough. Full runs only burn cost.
5. **Not measuring distribution shift after filtering**: filters often preserve only one domain. Compare before/after distributions by token count, language, and source.

## Key Takeaways

- Quality filtering combines heuristic and model-based stages.
- Heuristics quickly cut on length, symbol/digit/upper ratios, and repetition.
- Language detection works fine with fasttext-langdetect on a 1000-character sample.
- Perplexity filtering needs a reference LM like KenLM and is strong at removing broken text.
- A fastText classifier handles tens of thousands of samples per second on CPU - the GPT-3 approach.
- Order the pipeline cheap -> expensive to minimize cost.
- Episode 7 covers synthetic data generation.

---

## Operational checklist

- [ ] Keep heuristic thresholds tied to observed distributions rather than frozen constants
- [ ] Run language detection, perplexity, and classifiers in cheap-to-expensive order
- [ ] Compare source, language, and token-length distributions before and after filtering
- [ ] Document the positive and negative corpora used to train the quality classifier
- [ ] Track drop reasons by stage so threshold changes stay explainable

## Answering the Opening Questions

- **Which low-cost heuristics catch obvious junk before you spend model calls on it?**
  - The article treats Quality Filtering - Heuristics and Classifiers as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **What does language detection remove that simple length or symbol checks cannot?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How should perplexity and classifier scores sit behind the heuristic layer?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [AI Data Preparation 101 (1/10): Why Data Preparation Determines Model Quality](./01-why-data-preparation-matters.md)
- [AI Data Preparation 101 (2/10): Source Data Collection and Cataloging](./02-source-data-collection-cataloging.md)
- [AI Data Preparation 101 (3/10): Cleaning and Deduplication](./03-cleaning-deduplication.md)
- [AI Data Preparation 101 (4/10): PII Detection and Anonymization for Training Data](./04-pii-detection-anonymization.md)
- [AI Data Preparation 101 (5/10): Tokenization and Chunking Strategies](./05-tokenization-chunking.md)
- **Quality Filtering - Heuristics and Classifiers (current)**
- Synthetic Data Generation - From Self-Instruct to Distillation (upcoming)
- Data Augmentation - From EDA to Back-Translation (upcoming)
- Train/Eval/Test Splitting and Contamination Control (upcoming)
- Building a Production Data Pipeline (upcoming)

<!-- toc:end -->

## References

- [CCNet: Extracting High Quality Monolingual Datasets from Web Crawl Data (Wenzek et al., 2020)](https://arxiv.org/abs/1911.00359)
- [The RefinedWeb Dataset for Falcon LLM (Penedo et al., 2023)](https://arxiv.org/abs/2306.01116)
- [KenLM Language Model Toolkit](https://kheafield.com/code/kenlm/)
- [fastText Quality Classifier (used in GPT-3)](https://fasttext.cc/docs/en/supervised-tutorial.html)

Tags: Quality Filtering, Heuristic Rules, Classifier Filter, perplexity, KenLM, fastText
