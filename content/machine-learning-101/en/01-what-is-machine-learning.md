---
series: machine-learning-101
episode: 1
title: "Machine Learning 101 (1/10): What Is Machine Learning?"
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
  - AI
  - DataScience
  - Foundations
  - Beginner
seo_description: A clear intro to machine learning — what learning, generalization, and prediction mean and how ML differs from statistics and rule-based code
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (1/10): What Is Machine Learning?

Recommendation systems, fraud filters, and medical triage tools all get called "machine learning," but that label hides the real operating question. Are you writing smarter rules, doing statistics with a new library, or building a system that learns a reusable function from data? If that distinction stays fuzzy, every later discussion about models, metrics, and deployment turns into memorizing API names.

This is the first post in the Machine Learning 101 series. Here we will pin the topic down to one practical definition: machine learning means fitting a function from data, then trusting that function on inputs the model has never seen before.

![machine learning 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/01/01-01-concept-at-a-glance.en.png)
*machine learning 101 chapter 1 flow overview*
> Machine learning replaces hand-written rules with a function fit from data, then judges that function by how well it works on inputs it has never seen.

## Questions to Keep in Mind

- What exactly is the model learning when we say "machine learning"?
- Why is generalization different from scoring well on the training set?
- Where does machine learning diverge from statistics and rule-based code?

## ML Type Comparison

| Type | Input | Output | Typical Examples |
|---|---|---|---|
| Supervised | X, y (labeled) | Classification / regression prediction | Spam filter, price forecasting |
| Unsupervised | X (no labels) | Structure discovery | Customer segments, anomaly detection |
| Reinforcement | State, reward | Action policy | Game AI, robot control |

At the introductory level, the boundary between supervised and unsupervised learning is what you notice first. Reinforcement learning changes the problem drastically depending on how you design the reward signal, so we leave it for a later discussion.

## Why It Matters

Recommendation, medicine, finance, autonomous driving — nearly every industry is being reshaped by ML. But weak fundamentals make every downstream decision fragile. If you celebrate a good training score without checking generalization, or if you reach for algorithm names before nailing the problem definition, the project is already unstable.

## Key Terms

- **Learning**: Estimating a function from data.
- **Generalization**: Working well on data the model never saw during training.
- **Prediction**: Applying the learned function to new inputs.
- **Feature**: An input variable fed to the model.
- **Label**: The target value the model is trying to predict.

## Before/After

**Before**: "Code every rule with if-else" — every new pattern means more code to maintain.

**After**: "Give data, the model learns rules" — scale with data, not code.

## Hands-on: Your First ML in Five Steps

### Step 1 — Data

```python
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)
print(X.shape, y.shape)
```

### Step 2 — Pick a model

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(max_iter=1000)
```

### Step 3 — Fit

```python
model.fit(X, y)
```

### Step 4 — Predict

```python
print(model.predict(X[:5]))
```

### Step 5 — Score

```python
print("acc:", model.score(X, y))
```

**Expected output:** `X.shape` and `y.shape` report `(150, 4)` and `(150,)` — a small tabular dataset. `predict` returns class IDs. The accuracy will look high, but remember: this is *training accuracy*, not proof of generalization.

## When ML Fits vs When It Doesn't

**Good fit:**

- Rules are hard to write explicitly, but data is plentiful.
- Patterns are complex or constantly changing.
- Probabilistic predictions are useful.

**Bad fit:**

- Rules are clear and stable.
- Data is nearly nonexistent or labeling is prohibitively expensive.
- The decision process must be fully transparent.

Machine learning is not a universal tool. Problem definition comes first; algorithm selection comes after.

## Three-Line Classification

```python
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
X, y = load_iris(return_X_y=True)
model = LogisticRegression(max_iter=1000).fit(X, y)
print("Accuracy:", model.score(X, y))  # e.g. 0.97
```

Three lines, yet the full *learn → generalize → predict* pipeline is visible. The catch: the score above is training accuracy, likely over-optimistic.

## What to Notice in This Code

- `fit / predict / score` is the **scikit-learn standard interface**.
- `score` here is only **training accuracy** — not generalization.
- Model choice depends on **problem type**.

## Reading the First Failure Signals

- If training accuracy looks excellent but live data fails, suspect **input distribution shift** or **target definition ambiguity** before blaming the model.
- If the team cannot explain what `X` and `y` represent in one sentence, you are in a **problem definition** phase, not a model comparison phase.
- If a notebook demo only works on the same sample rows you keep reusing, suspect **leakage or memorization** before the algorithm.

## Five Common Mistakes

1. **Judging success on training data only.**
2. **Ignoring feature scaling.**
3. **Target leakage hidden in features.**
4. **No random seed — results are not reproducible.**
5. **Training without handling missing values or outliers.**

## How This Shows Up in Production

Recommendation, fraud detection, demand forecasting, image recognition, NLP chatbots — the *data → train → predict* pipeline is the backbone of every ML product.

## How a Senior Engineer Thinks

- **Problem definition** comes before **model selection**.
- **Data quality** matters more than **algorithm name** in most cases.
- Generalization is always confirmed on **separate data**.
- Build a **baseline model** first.
- Complexity is a **last resort**, not a starting point.

## Reading Classification Metrics Together

Accuracy alone creates illusions under class imbalance. For example, if only 5 % of samples are positive, predicting "negative" for everything still yields 95 % accuracy. That is why you need the metrics below alongside accuracy.

| Metric | Question It Answers | When It Matters Most |
|---|---|---|
| Precision | Of everything the model called positive, how many actually were? | When false-positive cost is high |
| Recall | Of all true positives, how many did the model catch? | When false-negative cost is high |
| F1-score | Harmonic mean of precision and recall — balance check | When one-sided high scores are suspicious |
| ROC-AUC | How well does the model separate positives from negatives across thresholds? | Model comparison before fixing a threshold |

In practice, teams rank metrics by domain cost. Fraud detection prioritizes recall; marketing lead scoring prioritizes precision. A "good model" is not the one with the absolute highest number — it is the one that minimizes business loss given the cost structure.

## Interpreting a Confusion Matrix Operationally

The confusion matrix is less about four raw numbers and more about which error type keeps repeating.

- True Positive: correctly detected positive.
- True Negative: correctly filtered negative.
- False Positive: incorrectly flagged as positive.
- False Negative: missed positive.

In medical screening, false negatives can be life-threatening, so you adjust the threshold toward higher recall. In auto-approval systems, false positives drive cost, so you lean toward precision. In model review meetings, sharing "most errors are FP" or "most errors are FN" produces better decisions than reporting a single accuracy number.

## Cross-Validation and Standardized Model Comparison

A single train/test split can mislead by luck. Use at least 5-fold cross-validation to see variance alongside mean performance.

```python
from sklearn.model_selection import cross_validate
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

candidates = {
    "logreg": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=2000))
    ]),
    "dt": DecisionTreeClassifier(max_depth=5, random_state=42),
    "rf": RandomForestClassifier(n_estimators=300, random_state=42)
}

for name, est in candidates.items():
    scores = cross_validate(
        est,
        X_train_full,
        y_train_full,
        cv=5,
        scoring={"acc": "accuracy", "f1": "f1", "auc": "roc_auc"},
        n_jobs=-1
    )
    print(name)
    print("acc:", scores["test_acc"].mean(), "+/-", scores["test_acc"].std())
    print("f1 :", scores["test_f1"].mean(), "+/-", scores["test_f1"].std())
    print("auc:", scores["test_auc"].mean(), "+/-", scores["test_auc"].std())
```

When mean scores are similar, the model with lower standard deviation is the safer production starting point. As traffic and data grow, you can migrate to a more complex model incrementally.

## Feature Engineering: First Things to Check

Feature engineering is about basic hygiene before fancy tricks.

1. Confirm that missing-value handling rules are identical at training and inference time.
2. Check categorical encoding (One-Hot, Target Encoding) for leakage potential.
3. Decompose date features into cyclical components (day-of-week, month, hour).
4. Verify whether log-scale transforms stabilize long-tail distributions.
5. Record whether validation metrics actually improve after adding derived features.

Combining a `ColumnTransformer` with a pipeline keeps preprocessing consistent:

```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder

num_cols = ["age", "income", "tenure_month"]
cat_cols = ["region", "device_type"]

preprocess = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]), num_cols),
    ("cat", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ]), cat_cols)
])
```

This structure ensures that training-time preprocessing rules are reproduced identically at inference time. Documentation becomes straightforward, and team handoff cost drops.

## Pre-Production Checklist

- Data-split parameters (`random_state`, `stratify`) are pinned in code.
- Evaluation metrics map to business cost structure.
- FP/FN response policy has been agreed upon based on the confusion matrix.
- Cross-validation reports mean *and* variance.
- Preprocessing and model live in a single pipeline object.

When these five criteria hold, you move past "the model runs" into "a reproducible and explainable learning system."

## Deep Dive: Loss Functions, Validation Curves, and Comparison Tables

This section brings together loss function shapes, confusion matrix reading, and hyperparameter curves into a single verification routine. The key idea: fix the validation loop, not the model.

### Loss Functions at a Glance

Classification and regression target different outputs, so their losses differ:

- Linear regression: MSE — penalizes large residuals quadratically.
- Logistic regression: binary cross-entropy — penalizes confident wrong predictions harshly.
- Tree-based classification: Gini or entropy reduction guides splits.

The critical takeaway is not the formula itself but this: a wrong loss function on the same data can select a completely different model.

### Scikit-learn Verification Template

```python
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(max_iter=3000))
])

param_grid = {
    "model__C": [0.01, 0.1, 1.0, 10.0, 30.0],
    "model__class_weight": [None, "balanced"],
    "model__solver": ["lbfgs"]
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
search = GridSearchCV(
    pipe,
    param_grid=param_grid,
    scoring="f1",
    cv=cv,
    n_jobs=-1,
    return_train_score=True
)
search.fit(X_train, y_train)

print("best:", search.best_params_)
print("best_f1:", search.best_score_)
```

Keep this structure unchanged across experiments; swapping models becomes trivial and team reviews stay aligned.

### Reading a Confusion Matrix as an Operational Signal

Suppose you get this confusion matrix:

| Actual \ Predicted | Negative | Positive |
|---|---:|---:|
| Negative | 880 | 70 |
| Positive | 35 | 215 |

Precision and recall both look decent. But if the cost structure says "missing a positive is catastrophic," the 35 FN cells demand threshold lowering. Conversely, if alert fatigue is the cost driver, the 70 FP cells need shrinking. Model scores do not replace decisions — they inform them.

### Reading Hyperparameter Curves

Plotting train/validation scores together exposes overfitting and underfitting quickly.

```python
import numpy as np
from sklearn.model_selection import validation_curve

param_range = np.logspace(-3, 2, 8)
train_scores, val_scores = validation_curve(
    LogisticRegression(max_iter=3000),
    X_train_scaled,
    y_train,
    param_name="C",
    param_range=param_range,
    scoring="f1",
    cv=5
)

print("C values:", param_range)
print("train mean:", train_scores.mean(axis=1))
print("valid mean:", val_scores.mean(axis=1))
```

- Left region: both train and valid are low → underfitting signal.
- Right region: train is high but valid drops → overfitting signal.
- Sweet spot: small gap between curves and valid is high → safe starting point for production.

### Model Comparison Table Example

Record mean *and* standard deviation from the same split to keep comparisons fair:

| Model | CV F1 Mean | CV F1 Std | Relative Training Time | Interpretability |
|---|---:|---:|---:|---|
| Logistic Regression | 0.911 | 0.012 | 1x | High |
| Decision Tree | 0.887 | 0.031 | 1x | Medium |
| Random Forest | 0.924 | 0.015 | 4x | Medium |

Do not pick the highest score automatically. Factor in variance and operational cost; post-deploy stability matters as much as pre-deploy accuracy.

### Hyperparameter Curve Interpretation Table

| Region | Train Score | Validation Score | Interpretation |
|---|---:|---:|---|
| Regularization too strong | Low | Low | Likely underfitting |
| Appropriate regularization | High | High | Priority candidate for generalization |
| Regularization too weak | Very high | Drops | Likely overfitting |

In production, choosing the region where the curve is *stable* beats chasing the single highest point, because retraining cycles will shift exact peaks.

### Threshold Adjustment Loop

```python
from sklearn.metrics import precision_score, recall_score, f1_score

thresholds = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
for t in thresholds:
    pred_t = (y_prob >= t).astype(int)
    p = precision_score(y_valid, pred_t)
    r = recall_score(y_valid, pred_t)
    f = f1_score(y_valid, pred_t)
    print(f"t={t:.1f}  precision={p:.3f}  recall={r:.3f}  f1={f:.3f}")
```

This loop can shift perceived performance dramatically without changing the model at all. It is especially powerful in alerting systems where FP/FN costs are asymmetric.

### Model Comparison Decision Rules

- If mean score difference is tiny, prefer the model with lower standard deviation.
- If the accuracy gain is under 1 %, factor in inference cost and operational complexity.
- In domains requiring explanations, default to interpretable models.
- If data is expected to grow significantly, prioritize retraining pipeline simplicity.
- Always record the selection rationale in a table and log so the next experiment has a clear baseline.

## Checklist

- [ ] I can explain what `X` and `y` represent.
- [ ] I can call `fit / predict / score`.
- [ ] I understand that training accuracy ≠ generalization.
- [ ] I understand the value of baseline models.

## Practice Problems

1. Run `fit / predict` on your own dataset (not iris).
2. Explain why `score` can be over-optimistic.
3. Show an example where feature scaling changes the result.

## Summary

Machine learning is **fitting a function from data and applying it to new inputs**. Anchoring that single sentence means you will not lose your way when classification, regression, clustering, and evaluation metrics arrive later.

Four takeaways from this post. First, learning is estimating a function, not memorizing data. Second, generalization must be measured separately from training score. Third, `fit / predict / score` is scikit-learn's universal language. Fourth, a good start is not a complex model — it is a clear problem definition and a baseline.

Next post: we compare supervised and unsupervised learning, and examine how the presence or absence of labels reshapes how you frame a problem.

## Answering the Opening Questions

- **What exactly does machine learning "learn"?**
  - ML estimates a function from data to produce predictions on new inputs. The `load_iris` → `LogisticRegression` → `fit` → `predict` example shows the model learning a decision boundary from `X` and `y` instead of relying on hand-written rules.
- **Why is generalization a different concept from training performance?**
  - `model.score(X, y)` reports training-data accuracy — how well the model fits samples it already saw. Generalization asks whether that performance holds on unseen data, which is why holdout sets and cross-validation must be used together.
- **Where do statistics, rule-based code, and machine learning diverge?**
  - Rule-based code means humans write `if-else` directly; ML fills the same role with a data-learned function. Statistics excels at explaining distributions and relationships; ML connects that knowledge into a prediction pipeline that answers new inputs for recommendation, fraud detection, and demand forecasting.

<!-- toc:begin -->
## In this series

- **What Is Machine Learning? (current)**
- Supervised and Unsupervised Learning (upcoming)
- Train/Test Split (upcoming)
- Linear Regression (upcoming)
- Logistic Regression (upcoming)
- Decision Tree and Random Forest (upcoming)
- Clustering (upcoming)
- Overfitting and Regularization (upcoming)
- Model Evaluation (upcoming)
- The ML Project Workflow (upcoming)

<!-- toc:end -->

## References

- [scikit-learn — Getting Started](https://scikit-learn.org/stable/getting_started.html)
- [Andrew Ng — Machine Learning Specialization](https://www.coursera.org/specializations/machine-learning-introduction)
- [Hands-On Machine Learning — Aurélien Géron](https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/)
- [Google — Machine Learning Crash Course](https://developers.google.com/machine-learning/crash-course)

Tags: MachineLearning, AI, DataScience, Foundations, Beginner
