---
title: "AI Data Preparation 101 (9/10): Train/Eval/Test Splitting and Contamination Control"
series: ai-data-preparation-101
episode: 9
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Train/Test Split
- Contamination
- Data Leakage
- Stratification
- Temporal Split
- scikit-learn
last_reviewed: '2026-05-14'
seo_description: 'The pattern of train_test_split(data, test_size=0.2) failing in
  production repeats every year. Two reasons:'
---

# AI Data Preparation 101 (9/10): Train/Eval/Test Splitting and Contamination Control

Many experiments look healthy right up until they meet production traffic because a simple random split hid the real failure mode. If your split ignores time, users, or benchmark contamination, validation scores can tell the wrong story.

This is the 9th post in the AI Data Preparation 101 series. Here we cover practical split strategies and the checks that keep contamination from invalidating evaluation.


![AI data preparation chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/09/09-01-big-picture.en.png)
*AI data preparation chapter 9 flow overview*

> Train/eval/test splitting is not a 70/20/10 ritual — it is the moment you decide what counts as 'unseen' for your model, and a leaky split here invalidates every metric you will ever compute downstream.

## Questions to Keep in Mind

- When does a random split stop representing the production problem you actually care about?
- How do stratified, group, and temporal splits protect against different leakage patterns?
- Why is contamination now a first-class evaluation problem for LLMs?

## "Doesn't random_split cover it?"

The pattern of `train_test_split(data, test_size=0.2)` failing in production repeats every year. Two reasons:

1. **Distribution mismatch**: random split ignores time order or user-level grouping. Validation scores diverge from production.
2. **Contamination**: when the pretraining corpus has already seen the evaluation benchmark, scores are inflated. This is the largest evaluation problem of the LLM era.

This episode covers 4 split strategies and contamination detection/defense.

## Split strategy 1 - Random split (baseline)

The simplest. Valid only when the iid assumption holds.

```python
from sklearn.model_selection import train_test_split

train, temp = train_test_split(data, test_size=0.3, random_state=42)
val, test = train_test_split(temp, test_size=0.5, random_state=42)
# Result: 70% train, 15% val, 15% test
```

**When NOT to use**:

- Time-dependent data (news, price prediction, churn)
- Multiple samples from the same user/session
- Severe class imbalance (use StratifiedShuffleSplit)

## Split strategy 2 - Stratified split (class imbalance)

Keeps label distribution identical across train/val/test.

```python
from sklearn.model_selection import StratifiedShuffleSplit

X, y = features, labels
sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_idx, test_idx in sss.split(X, y):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

# Verify
import numpy as np
print("train:", np.bincount(y_train) / len(y_train))
print("test :", np.bincount(y_test) / len(y_test))
```

If a minority class is below 5%, random split can put zero of them in the test set. Stratified prevents this.

## Split strategy 3 - Group split (prevent user/session leakage)

When samples from the same user appear in both train and test, the model leaks by exploiting user identity.

```python
from sklearn.model_selection import GroupShuffleSplit

groups = df["user_id"].values
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_idx, test_idx in gss.split(df, groups=groups):
    train_df = df.iloc[train_idx]
    test_df = df.iloc[test_idx]

# Verify: no shared user_id
assert set(train_df["user_id"]) & set(test_df["user_id"]) == set()
```

Mandatory for recommender systems, fraud detection, and patient-level medical evaluation.

## Split strategy 4 - Temporal split (prevent time leakage)

Prevents leaking the future into training. The closest to a real production deployment.

```python
import pandas as pd

df = df.sort_values("timestamp")
n = len(df)
train = df.iloc[: int(n * 0.7)]
val   = df.iloc[int(n * 0.7) : int(n * 0.85)]
test  = df.iloc[int(n * 0.85) :]

# Rolling-window backtest (optional)
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5, test_size=int(n * 0.1))
for fold, (tr, te) in enumerate(tscv.split(df)):
    print(f"fold {fold}: train={len(tr)}, test={len(te)}")
```

News classification, recommendations, demand forecasting, and churn models almost always require temporal split. Random split leaks future information into training.

## Contamination - the biggest trap in LLM evaluation

Models like GPT-4 have learned the entire web. Benchmark text from MMLU, HumanEval, and GSM8K is likely in the pretraining corpus. Scores look high but they are not generalization scores.

The simplest detection is substring overlap.

```python
import hashlib

def make_ngrams(text: str, n: int = 13) -> set[str]:
    tokens = text.split()
    if len(tokens) < n:
        return set()
    return {" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)}

def contamination_overlap(eval_doc: str, pretrain_chunks: list[str], n: int = 13) -> float:
    eval_grams = make_ngrams(eval_doc, n)
    if not eval_grams:
        return 0.0
    matched = 0
    for chunk in pretrain_chunks:
        chunk_grams = make_ngrams(chunk, n)
        matched += len(eval_grams & chunk_grams)
        if matched >= len(eval_grams):
            break
    return matched / len(eval_grams)

# 13-gram match >= 80% suggests contamination
```

The GPT-3 and PaLM papers both use a 13-gram criterion. Larger n misses paraphrased contamination; smaller n explodes false positives.

At production scale, accelerate with MinHash + LSH (see Episode 3).

## Contamination defenses - 4 strategies

1. **Held-out only benchmarks**: trust only eval sets first released after model training.
2. **Decontamination**: remove pretraining documents that match eval n-grams.
3. **Canary strings**: embed unique strings in eval sets and detect whether the model has memorized them.
4. **Date-cutoff**: evaluate only on data created after the model's training cutoff.

```python
# Canary detection (simple)
def canary_check(model_call, canary: str = "Th3_C@nary_X9z!") -> bool:
    rsp = model_call(f"Complete the string: {canary[:5]}")
    return canary in rsp  # True means suspected contamination
```

## Practical split workflow

```python
def production_split(df: pd.DataFrame, time_col: str, group_col: str | None = None,
                     stratify_col: str | None = None) -> dict:
    # 1) Time-based train/test split (mirrors production)
    df = df.sort_values(time_col)
    cutoff = df[time_col].quantile(0.85)
    pre, post = df[df[time_col] < cutoff], df[df[time_col] >= cutoff]
    # 2) Within train, separate val by group/stratify
    if group_col:
        from sklearn.model_selection import GroupShuffleSplit
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.15, random_state=42)
        idx_tr, idx_val = next(splitter.split(pre, groups=pre[group_col]))
    elif stratify_col:
        from sklearn.model_selection import StratifiedShuffleSplit
        splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.15, random_state=42)
        idx_tr, idx_val = next(splitter.split(pre, pre[stratify_col]))
    else:
        cut2 = pre[time_col].quantile(0.82)
        idx_tr = pre[time_col] < cut2
        idx_val = ~idx_tr
        return {"train": pre[idx_tr], "val": pre[idx_val], "test": post}
    return {"train": pre.iloc[idx_tr], "val": pre.iloc[idx_val], "test": post}
```

This function covers nearly all production cases.

## Embedding contamination checks into the batch pipeline

No matter how good the split strategy is, if contamination checks run manually they will be skipped in production. It is safer to force a decontamination stage right after the split as part of the DAG.

```python
SPLIT_DAG = {
    "build_raw_snapshot": [],
    "split_temporal_group": ["build_raw_snapshot"],
    "cross_dedup_train_eval": ["split_temporal_group"],
    "ngram_contamination_scan": ["cross_dedup_train_eval"],
    "publish_split_manifest": ["ngram_contamination_scan"],
}
```

## Split result manifest

```python
from dataclasses import dataclass

@dataclass
class SplitManifest:
    dataset_version: str
    split_strategy: str
    train_rows: int
    val_rows: int
    test_rows: int
    time_cutoff: str
    group_column: str | None
    contamination_ratio_test: float
    overlap_removed_train_rows: int

manifest = SplitManifest(
    dataset_version="v2.3.0",
    split_strategy="temporal+group",
    train_rows=420_000,
    val_rows=72_000,
    test_rows=88_000,
    time_cutoff="2026-03-01",
    group_column="user_id",
    contamination_ratio_test=0.006,
    overlap_removed_train_rows=5142,
)
```

This manifest is essential for separating "model difference" from "evaluation condition difference" when comparing experiment results.

## Contamination sample report

```python
def collect_contamination_examples(eval_docs, pretrain_docs, overlap_fn, top_k=20):
    rows = []
    for e in eval_docs:
        score, matched = overlap_fn(e, pretrain_docs)
        if score > 0.5:
            rows.append({"eval": e[:160], "score": score, "matched": matched[:160]})
    rows.sort(key=lambda x: x["score"], reverse=True)
    return rows[:top_k]
```

Numbers alone can mislead. Having a human review the top contaminated samples makes threshold tuning far more accurate.

## Before/after split samples

```text
[Bad split]
train: includes 2026-04 data
test : includes 2026-03 data

[Improved split]
train: <= 2026-02
val  : partial 2026-02
test : >= 2026-03
```

Aligning the time axis honestly may lower offline scores, but it reduces the gap between offline and post-deployment performance.

## DVC stage for split reproducibility

```yaml
stages:
  split_dataset:
    cmd: python pipelines/split_dataset.py --strategy temporal_group --time-col timestamp --group-col user_id
    deps:
      - pipelines/split_dataset.py
      - data/quality/train_filtered.parquet
    outs:
      - data/splits/train.parquet
      - data/splits/val.parquet
      - data/splits/test.parquet
    metrics:
      - reports/split_manifest.json
      - reports/contamination_report.json
```

Splitting is not experiment preprocessing—it is an evaluation contract. Unless the contract is preserved in code and version control, subsequent model improvements cannot be trusted.

## Split validation automation

Even a good strategy falls apart without automated verification. Right after generating splits, all the following checks must pass before proceeding to the next stage.

```python
def validate_split(train_df, val_df, test_df, group_col=None):
    checks = {}
    checks["non_empty"] = len(train_df) > 0 and len(val_df) > 0 and len(test_df) > 0
    checks["disjoint_index"] = (
        set(train_df.index).isdisjoint(val_df.index) and
        set(train_df.index).isdisjoint(test_df.index) and
        set(val_df.index).isdisjoint(test_df.index)
    )
    if group_col:
        checks["group_disjoint"] = (
            set(train_df[group_col]).isdisjoint(val_df[group_col]) and
            set(train_df[group_col]).isdisjoint(test_df[group_col]) and
            set(val_df[group_col]).isdisjoint(test_df[group_col])
        )
    return checks
```

## Class distribution stability check

```python
def class_ratio(df, label_col):
    vc = df[label_col].value_counts(normalize=True)
    return {k: float(v) for k, v in vc.items()}

def max_ratio_delta(a: dict, b: dict) -> float:
    keys = set(a) | set(b)
    return max(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys)
```

If the maximum distribution gap across train/val/test is excessive, revisit the split criteria. For minority classes, even a 1-2% difference can significantly affect production metrics.

## Contamination response steps

1. Extract samples where `ngram overlap > threshold`.
2. Have humans review the top samples to remove false positives.
3. Remove confirmed contaminated samples from train and record in the report.
4. Compare performance before/after removal to confirm evaluation reliability change.

Automating this loop dramatically reduces the state of "high scores that cannot be trusted."

## Inspection questions for immediate ops use

The questions below are actual check items used in pre-deployment reviews. Each question must be answerable with a file path or metric value, not just a document reference.

1. Which dataset version is this batch from, and what is the sha256?
2. How much has the duplicate/null/length distribution changed compared to the previous batch?
3. Which rules caused sample removal, and what are the top rejection reasons?
4. How much contamination risk remains at the train/eval/test boundary, in numeric terms?
5. Which samples were human-reviewed in this batch, and what error types were found?

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

Operations teams may not use this function verbatim, but the same concepts must be implemented as pipeline gates. The key principle is: never judge readiness by feel.

## Production log example

```text
[release-check] dataset=v2.4.1 sha=4fb1...
[release-check] duplicate_ratio=0.061 null_ratio=0.008
[release-check] contamination_ratio=0.004 human_reviewed_rows=240
[release-check] status=PASS
```

With this single log block, even when model performance wavers, you can quickly exclude or deep-dive the data preparation stage.

### Test set access control

The test set should be used only for final pre-deployment verification. Restrict access during iterative experimentation. Defining access paths via repository permissions and CI job separation significantly reduces unconscious test overfitting.

### Minimum items for release notes

Changes at this stage must also appear in release notes. At minimum, include `changed rule`, `affected row count`, `key metric delta`, and `rollback path` so the same decision can be replicated in the next batch.

Split rule changes should always be recorded as independent experiments to separate their effect from model changes.

For temporal splits, inspecting periods around service events (promotions, outage notices) as separate slices increases evaluation reliability.

Keep split manifests alongside experiment logs so that score changes can be clearly attributed to either data boundary changes or model improvements. Without this, performance interpretation within teams frequently conflicts.

Logging access to the evaluation set allows tracking unconscious leakage after the fact.

Split results should be frozen after review approval.

## 5 common mistakes

1. **Random split on time-series data**: leaks the future into training and inflates validation.
2. **Ignoring user leakage**: when the same user appears in both train and test, the model cheats by recognizing user identity.
3. **Skipping contamination checks**: without 13-gram overlap measurement, LLM evaluation scores are not trustworthy.
4. **Using the test set for hyperparameter tuning**: test must be touched only once. Tune on validation.
5. **Naive stratify on multi-label data**: use `iterstrat.MultilabelStratifiedShuffleSplit` for multi-label.

## Key Takeaways

- Pick split strategy by data characteristics: random / stratified / group / temporal.
- Time-dependent data almost always needs temporal split.
- Apply group split so the same user does not appear in both train and test.
- LLM evaluation requires 13-gram contamination overlap measurement.
- Defense strategies: held-out, decontamination, canary, date-cutoff.
- The test set is a single-use final measurement.
- Episode 10 covers production data pipeline construction.

---

## Operational checklist

- [ ] Document why the current problem needs random, stratified, group, temporal, or hybrid splitting
- [ ] Verify that no user, session, or patient identifiers cross the train/test boundary
- [ ] Run contamination overlap checks on LLM evaluation sets before publishing scores
- [ ] Keep the test set out of hyperparameter tuning and define who may access it
- [ ] Record the time cutoff and backtest strategy whenever temporal split is in use

## Answering the Opening Questions

- **What is a representative case where a simple `train_test_split` misses real operating conditions?**
  - The default `train_test_split(data, test_size=0.3)` assumes i.i.d., so it misses time ordering, user repetition, and minority-class issues. That is why the article separately introduced temporal split, `GroupShuffleSplit`, and `StratifiedShuffleSplit`.
- **Why do class imbalance, user leakage, and time-series data each require a different split strategy?**
  - If label ratios are the problem, use `stratify=y`; if the same `user_id` leaks, use group split; if future information bleeds in, split by `timestamp`. The three situations break for different reasons and cannot be solved simultaneously by a single split.
- **How does LLM benchmark contamination differ from traditional data leakage, and why is it more dangerous?**
  - Traditional leakage is direct overlap between train and eval, whereas contamination asks whether benchmark sentences already appeared in the pretraining corpus. The article therefore separately computed 13-gram overlap with `make_ngrams()` and `contamination_overlap()`, and enforced a decontamination step in the DAG after splitting.
<!-- toc:begin -->
## In this series

- [AI Data Preparation 101 (1/10): Why Data Preparation Determines Model Quality](./01-why-data-preparation-matters.md)
- [AI Data Preparation 101 (2/10): Source Data Collection and Cataloging](./02-source-data-collection-cataloging.md)
- [AI Data Preparation 101 (3/10): Cleaning and Deduplication](./03-cleaning-deduplication.md)
- [AI Data Preparation 101 (4/10): PII Detection and Anonymization for Training Data](./04-pii-detection-anonymization.md)
- [AI Data Preparation 101 (5/10): Tokenization and Chunking Strategies](./05-tokenization-chunking.md)
- [AI Data Preparation 101 (6/10): Quality Filtering - Heuristics and Classifiers](./06-quality-filtering.md)
- [AI Data Preparation 101 (7/10): Synthetic Data Generation - From Self-Instruct to Distillation](./07-synthetic-data-generation.md)
- [AI Data Preparation 101 (8/10): Data Augmentation - From EDA to Back-Translation](./08-data-augmentation.md)
- **Train/Eval/Test Splitting and Contamination Control (current)**
- Building a Production Data Pipeline (upcoming)

<!-- toc:end -->

## References

- [Language Models are Few-Shot Learners (GPT-3, Brown et al., 2020) - 13-gram contamination](https://arxiv.org/abs/2005.14165)
- [Investigating Data Contamination in Modern Benchmarks (Yang et al., 2024)](https://arxiv.org/abs/2311.09783)
- [scikit-learn Cross-validation Guide](https://scikit-learn.org/stable/modules/cross_validation.html)
- [Hidden Stratification and Spurious Correlations in ML (Oakden-Rayner et al., 2020)](https://arxiv.org/abs/1909.12475)

Tags: Train/Test Split, Contamination, Data Leakage, Stratification, Temporal Split, scikit-learn
