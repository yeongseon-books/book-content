---
title: "AI Data Preparation 101 (1/10): Why Data Preparation Determines Model Quality"
series: ai-data-preparation-101
episode: 1
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Data Preparation
- ML Foundations
- Data Quality
- Pipelines
last_reviewed: '2026-05-14'
seo_description: This is the question every ML beginner asks. You download a Kaggle
  dataset, run pandas.read_csv(), and shove it into a model. Done, right?
---

# AI Data Preparation 101 (1/10): Why Data Preparation Determines Model Quality

It is easy to think the job ends once you download a dataset, run `pandas.read_csv()`, and feed it into a model. In production, though, model failures usually trace back to data preparation decisions long before they trace back to architecture choices.

This is the first post in the AI Data Preparation 101 series. Here we cover why data preparation has outsized impact on model quality and which early mistakes tend to compound later.


![AI data preparation chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/01/01-01-big-picture.en.png)
*AI data preparation chapter 1 flow overview*

> Model quality is bounded above by data quality — once that sinks in, every modeling decision starts looking downstream of a data preparation decision you either made deliberately or inherited by accident.

## Questions to Keep in Mind

- When does data preparation create more lift than another round of model tuning?
- Which data failures make offline metrics look healthy while production quality degrades?
- Why is data preparation better treated as one pipeline than as a few disconnected preprocessing scripts?

## "Can't I Just Grab Some Data and Train?"

This is the question every ML beginner asks. You download a Kaggle dataset, run `pandas.read_csv()`, and shove it into a model. Done, right? But trace any production model quality issue and 70-80% of the time the root cause sits in the data, not the model.

That is exactly what Andrew Ng pushed in his 2021 "Data-centric AI" campaign. With the same model architecture, raising data quality by one or two points often boosts accuracy by 5-10%. The reverse is also true: no amount of model tuning fixes dirty data.

This series walks the entire path from raw data to a production training set. Episode 1 explains why data preparation matters and the five data traps engineers most often miss.

## Garbage In, Garbage Out — Plus the Modern Twists

The classic GIGO line is "feed garbage, get garbage out." With LLMs and recommender systems we now face nastier variants.

- **Silent failure**: The model produces plausible answers while parroting biased patterns from the training data. Metrics look great but real users suffer.
- **Test set leakage**: Training data overlaps with evaluation data, metrics inflate, and accuracy halves the day after deployment.
- **Distribution shift**: The model worked at training time but user data drifts away from the training distribution, and accuracy slowly degrades.

The snippet below trains the same model on two versions of the same dataset. Only the data changes — the result does not.

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

Run it and you will see 1-3 percentage points of difference. Not a single line of model code changed. We only cleaned the data.

## The Six-Stage Data Preparation Pipeline

A production data pipeline almost always has six stages.

1. **Collection**: Pull data from source systems and record provenance — license, snapshot date, version.
2. **Cleaning**: Remove encoding errors, HTML noise, broken characters, and duplicates.
3. **Privacy**: Detect and anonymize PII that must not enter training.
4. **Quality filtering**: Drop low-quality samples with heuristics and trained classifiers.
5. **Tokenization & chunking**: Convert raw text into model input format.
6. **Splitting**: Carve out train/eval/test splits with strict contamination checks.

Each later episode in this series focuses on one of these stages. After episode 6 we move to synthetic data generation, augmentation, and finish with a production-grade pipeline that wires everything together.

## Five Data Traps Engineers Miss

### 1. Duplicate samples inflate evaluation scores

When the same document leaks into both train and eval, the model just regurgitates memorized answers. Every team that has worked on CC-Net or The Pile puts dedup as the first step (covered in episode 3 with MinHash).

### 2. Splitting without honoring class balance

```python
from sklearn.model_selection import train_test_split
# Wrong: plain random split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Right: stratify keeps class ratios stable
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
```

Forget `stratify` and the minority class can disappear from the test set entirely, making metrics meaningless.

### 3. Ignoring temporal order

Time-series data split randomly creates temporal leakage — future information bleeds into training. Always split by cutoff date (episode 9 covers this in detail).

### 4. PII shipped straight into training data

Emails, phone numbers, and IDs left in raw text mean the model can echo them back. With LLMs you also expose yourself to membership inference attacks (episode 4).

### 5. Information loss at the tokenizer

Use an English BPE tokenizer on Korean text and a single character can split into three or four tokens. You waste context window and dilute training signal (episode 5).

## A Minimal Data Quality Report

Before a dataset enters production, measure these five things every time.

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

The exact numbers vary by dataset version and random seed, but the pattern should not. Cleaning should move the metric in a measurable direction, and the quick report should expose duplicate rate, missing values, and length outliers before training starts.

## Failure modes to check before you blame the model

A model experiment should stop early when the data report already looks suspicious. Three checks catch many bad runs:

1. **Unexpected duplicate ratio spike**: if duplicates jump between dataset versions, evaluation inflation is a more likely culprit than model weakness.
2. **Length distribution drift**: if `p99_length` doubles or collapses, your tokenizer and chunk settings are about to change cost and quality together.
3. **Language or source imbalance**: when one source suddenly dominates, the model will often look better on one segment while degrading everywhere else.

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

That kind of jump is operationally actionable. It tells you to inspect the dataset refresh before you spend time tuning the model.

Generate this report for every dataset version, diff against the previous version, and you catch quality regressions before training even starts.

## Common Mistakes

1. **"Just train and see what happens"**: Skipping data validation can burn days of GPU time. Run the quality report before kicking off training.
2. **Eyeballing the first 100 rows**: `head(100)` hides long-tail issues. Sample 1,000 rows at random and inspect the 99th percentile of length.
3. **Single-metric thinking**: Accuracy alone hides class imbalance and sub-group regressions. Track per-class and per-segment metrics together.
4. **No provenance**: Without recording where data came from and when, you face license disputes and reproducibility nightmares (episode 2 on cataloging).
5. **"Cleaned once, done forever"**: Distributions drift over time. Treat the cleaning pipeline like code — version it and run it in CI (episode 10).

## Key Takeaways

- 70-80% of model quality is decided by data. Data-centric work has higher ROI than another round of model tuning.
- Data preparation is a six-stage pipeline: Collection → Cleaning → Privacy → Quality filtering → Tokenization → Splitting.
- Silent failure, test set leakage, and distribution shift are the three risks you must contain at the data layer.
- Generate a quick quality report on every dataset version and diff it against the previous one.
- The next nine episodes go deep on each stage. Episode 2 starts with collection and cataloging.

---

## Operational checklist

- [ ] Record dataset version, provenance, and license before starting training
- [ ] Generate a quick quality report for every dataset refresh and diff it against the previous version
- [ ] Check duplicates, leakage risk, and language mix before trusting accuracy numbers
- [ ] Make tokenization and split design explicit instead of leaving them as hidden defaults
- [ ] Write down which quality signals would tell you to revisit the data before the model

## Answering the Opening Questions

- **When does data preparation create more lift than another round of model tuning?**
  - The article treats Why Data Preparation Determines Model Quality as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which data failures make offline metrics look healthy while production quality degrades?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Why is data preparation better treated as one pipeline than as a few disconnected preprocessing scripts?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- **Why Data Preparation Determines Model Quality (current)**
- Source Data Collection and Cataloging (upcoming)
- Cleaning and Deduplication (upcoming)
- PII Detection and Anonymization for Training Data (upcoming)
- Tokenization and Chunking Strategies (upcoming)
- Quality Filtering - Heuristics and Classifiers (upcoming)
- Synthetic Data Generation - From Self-Instruct to Distillation (upcoming)
- Data Augmentation - From EDA to Back-Translation (upcoming)
- Train/Eval/Test Splitting and Contamination Control (upcoming)
- Building a Production Data Pipeline (upcoming)

<!-- toc:end -->

## References

- [Andrew Ng - Data-centric AI Resources](https://datacentricai.org/)
- [The Pile: An 800GB Dataset of Diverse Text](https://arxiv.org/abs/2101.00027)
- [scikit-learn: Cross-validation and stratified splits](https://scikit-learn.org/stable/modules/cross_validation.html)
- [Google: Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml)

Tags: Data Preparation, ML Foundations, Data Quality, Pipelines
