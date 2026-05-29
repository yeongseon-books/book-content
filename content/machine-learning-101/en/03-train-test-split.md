---
series: machine-learning-101
episode: 3
title: "Machine Learning 101 (3/10): Train/Test Split"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - MachineLearning
  - TrainTestSplit
  - Generalization
  - CrossValidation
  - scikit-learn
seo_description: Why train and test splits measure generalization, plus leakage, seeds, stratification, and K-fold cross-validation in scikit-learn
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (3/10): Train/Test Split

A model can brag about 99% training accuracy and still be useless the moment it sees live traffic. That gap is not a minor detail. It is the core reason ML teams separate fitting from evaluation and guard the test set so aggressively.

This is the 3rd post in the Machine Learning 101 series. Here we will use train/test splits, stratification, seeds, and cross-validation to turn "the model seems good" into an experiment that measures generalization.

![machine learning 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/03/03-01-concept-at-a-glance.en.png)
*machine learning 101 chapter 3 flow overview*
> A train/test split is the only honest way to estimate how a model will behave on data it has not seen — every shortcut here leaks future performance into the present.

## Questions to Keep in Mind

- What do the train, validation, and test sets each protect?
- Why should `random_state` be fixed even in small experiments?
- How does `stratify` help on imbalanced classes?

## Split Strategy Comparison

| Strategy | Advantage | Disadvantage | Best For |
|---|---|---|---|
| Hold-out | Fast | Depends on a single split | Large datasets |
| K-fold | Uses all data | Takes longer | Small sample sizes |
| Stratified | Preserves class ratio | One more parameter | Imbalanced data |
| Time-series split | Prevents temporal leakage | Reduces training data | Time-ordered problems |

The choice of split strategy depends on data characteristics and problem type. Random splitting is not always the right answer.

## Why It Matters

Without measuring generalization, you cannot select or compare models. Training scores look good but they are not numbers you can ship. Which split strategy you use ultimately determines how model selection and MLOps gating work.

## Key Terms

- **Train**: Data used for fitting the model.
- **Validation**: Data used for tuning hyperparameters.
- **Test**: Held out, looked at exactly once.
- **Stratify**: Keep class proportions constant across splits.
- **K-fold**: Split into K parts and rotate the test fold.

## Before/After

**Before**: Fit on all data, score on the same data. Performance is overestimated.

**After**: Fit on train, score on held-out test. The number reflects reality.

## Hands-on: 5 Steps to Split and Evaluate

### Step 1 — Data

```python
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)
```

### Step 2 — Split

```python
from sklearn.model_selection import train_test_split
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
```

### Step 3 — Model

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
```

### Step 4 — Evaluate

```python
print("train:", model.score(Xtr, ytr))
print("test :", model.score(Xte, yte))
```

### Step 5 — Cross-validate

```python
from sklearn.model_selection import cross_val_score
print(cross_val_score(model, X, y, cv=5).mean())
```

**Expected output:** The training score should come out a bit higher than the test score, and the cross-validation mean should land in the same neighborhood. If those numbers diverge sharply, your split strategy deserves suspicion before the model does.

## Data Leakage

Data leakage occurs when information from the test set bleeds into training — one of the most dangerous errors in ML.

### Common Leakage Sources

1. **Preprocessing leakage**: Fitting a scaler on the entire dataset before splitting.
2. **Target leakage**: Features contain target information directly.
3. **Temporal leakage**: Using future information to predict the past.
4. **Group leakage**: The same user or entity appears in both train and test.

### Prevention

- Perform the split **first**, before any preprocessing.
- Fit transformers on training data only (`.fit()`) and apply `.transform()` to test data.
- Remove columns that carry target information during feature selection.
- For time-series problems, enforce strict temporal ordering.

## Python Example: train_test_split + cross_val_score

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression

X, y = load_iris(return_X_y=True)

# Hold-out split
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
print("Train:", model.score(Xtr, ytr))
print("Test:", model.score(Xte, yte))

# Cross-validation
scores = cross_val_score(model, X, y, cv=5)
print("CV mean:", scores.mean(), "std:", scores.std())
```

Cross-validation reduces the randomness of a single split. It is especially valuable when sample sizes are small.

## What to Notice in This Code

- `stratify=y` preserves class ratios in both splits.
- A fixed `random_state` makes results reproducible.
- `cross_val_score` repeats train and evaluate K times.

## Reading the First Failure Signals

- If the test score jumps around every run, check whether the sample is too small or the seed was left floating.
- If train and test both look suspiciously perfect, inspect **preprocessing leakage** before celebrating.
- If the problem is time-series or user-grouped data, random splitting is often the bug, not the metric.

## Five Common Mistakes

1. **Tuning on the test set, which leaks performance.**
2. **Fitting a scaler on the entire dataset before splitting.**
3. **Forgetting to set the random seed and chasing noise.**
4. **Ignoring `stratify` on imbalanced data.**
5. **Splitting time-series data randomly instead of by time.**

## How This Shows Up in Production

A/B experiments, model comparison, and MLOps gating all hinge on a sound split strategy. The split governs the decision, not just the metric.

## How a Senior Engineer Thinks

- Touch the test set **exactly once**.
- Keep validation and test separate.
- Split time-series chronologically.
- Always suspect group leakage.
- Preprocess **after** splitting, not before.

## Checklist

- [ ] I know the role of train, valid, and test.
- [ ] I understand what `stratify` does.
- [ ] I always fix `random_state`.
- [ ] I can run `cross_val_score`.

## Practice Problems

1. Vary `test_size` between 0.1 and 0.3 and observe the test score.
2. Compare class ratios in train and test with `stratify=None`.
3. Compare the variance of 5-fold and 10-fold scores.

## Summary

A correct split is the prerequisite for every measurement that follows. Without it, training scores create illusions, leakage goes undetected, and model comparisons become meaningless.

Three takeaways: First, split before preprocessing — never the other way around. Second, `stratify` and `random_state` are not optional luxuries; they are basic hygiene. Third, cross-validation smooths single-split variance so that decisions rest on stable numbers.

Next post: we cover linear regression as the foundation of supervised learning.

## Answering the Opening Questions

- **What role does each of training set, validation set, and test set play?**
  - The training set learns model parameters via `fit(Xtr, ytr)`. The validation set tunes hyperparameters and thresholds as an intermediate checkpoint. The test set opens only once at the end to confirm generalization — the final holdout.
- **Why should `random_state` always be fixed?**
  - Fixing `train_test_split(..., random_state=42)` ensures the same data split is reproducible. Without it, train/test composition changes each run, making it impossible to distinguish model improvement from accidental split variation.
- **How does `stratify` help with class imbalance?**
  - `stratify=y` maintains the original class ratios in both train and test splits. For problems with rare positives, it prevents splits where positives nearly vanish from one side — making test scores better reflect actual operational distributions.

<!-- toc:begin -->
## In this series

- [Machine Learning 101 (1/10): What Is Machine Learning?](./01-what-is-machine-learning.md)
- [Machine Learning 101 (2/10): Supervised and Unsupervised Learning](./02-supervised-and-unsupervised.md)
- **Train/Test Split (current)**
- Linear Regression (upcoming)
- Logistic Regression (upcoming)
- Decision Tree and Random Forest (upcoming)
- Clustering (upcoming)
- Overfitting and Regularization (upcoming)
- Model Evaluation (upcoming)
- The ML Project Workflow (upcoming)

<!-- toc:end -->

## References

- [scikit-learn — train_test_split](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)
- [scikit-learn — Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
- [Forecasting: Principles and Practice — Hyndman](https://otexts.com/fpp3/)
- [Google — Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)

Tags: MachineLearning, TrainTestSplit, Generalization, CrossValidation, scikit-learn
