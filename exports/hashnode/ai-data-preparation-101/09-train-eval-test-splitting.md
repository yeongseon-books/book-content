
# Train/Eval/Test Splitting and Contamination Control

> AI Data Preparation 101 series (9/10)

---
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

## AI Data Preparation 101 series

- [Why Data Preparation Determines Model Quality](./01-why-data-preparation-matters.md)
- [Source Data Collection and Cataloging](./02-source-data-collection-cataloging.md)
- [Cleaning and Deduplication](./03-cleaning-deduplication.md)
- [PII Detection and Anonymization for Training Data](./04-pii-detection-anonymization.md)
- [Tokenization and Chunking Strategies](./05-tokenization-chunking.md)
- [Quality Filtering - Heuristics and Classifiers](./06-quality-filtering.md)
- [Synthetic Data Generation - From Self-Instruct to Distillation](./07-synthetic-data-generation.md)
- [Data Augmentation - From EDA to Back-Translation](./08-data-augmentation.md)
- **Train/Eval/Test Splitting and Contamination Control (current)**
- Building a Production Data Pipeline (upcoming)
## References

- [Language Models are Few-Shot Learners (GPT-3, Brown et al., 2020) - 13-gram contamination](https://arxiv.org/abs/2005.14165)
- [Investigating Data Contamination in Modern Benchmarks (Yang et al., 2024)](https://arxiv.org/abs/2311.09783)
- [scikit-learn Cross-validation Guide](https://scikit-learn.org/stable/modules/cross_validation.html)
- [Hidden Stratification and Spurious Correlations in ML (Oakden-Rayner et al., 2020)](https://arxiv.org/abs/1909.12475)

Tags: Train/Test Split, Contamination, Data Leakage, Stratification, Temporal Split, scikit-learn

---

© 2026 YeongseonBooks. All rights reserved.
