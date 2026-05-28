---
series: machine-learning-101
episode: 6
title: "Machine Learning 101 (6/10): Decision Tree and Random Forest"
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
  - DecisionTree
  - RandomForest
  - Ensemble
  - scikit-learn
seo_description: How decision trees split the feature space, why a single tree overfits, and how random forests combine many trees into a strong tabular baseline
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (6/10): Decision Tree and Random Forest

On tabular data, a stack of well-chosen `if-else` rules often beats more fashionable models. That feels counterintuitive until you remember what trees do well: they capture nonlinear structure, handle mixed feature behavior naturally, and produce a baseline that is hard to embarrass.

This is the 6th post in the Machine Learning 101 series. Here we will look at what a single decision tree learns, why that tree overfits so easily, and how a random forest stabilizes the same idea by averaging many trees together.


![machine learning 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/06/06-01-concept-at-a-glance.en.png)
*machine learning 101 chapter 6 flow overview*
> A decision tree splits the feature space into rectangles; a random forest is many such trees voting together so no single tree's mistakes dominate.

## Questions to Keep in Mind

- How does a decision tree split the feature space?
- What do Gini and entropy actually measure?
- Why does a single deep tree overfit so quickly?

## Why It Matters

Random forests and gradient-boosted trees still dominate tabular data. They belong in every baseline before you reach for deep learning.

## Key Terms

- **Split**: separates data using a feature and threshold.
- **Gini and entropy**: impurity measures.
- **Pruning**: limit depth or leaf size.
- **Bagging**: bootstrap aggregation.
- **Feature importance**: contribution of each feature to splits.

## Before/After

**Before**: "Trees are interpretable, end of story" — single trees have huge variance.

**After**: Use a forest to reduce variance and explain it with SHAP.

## Hands-on: 5 Steps with Trees and Forests

### Step 1 — Data

```python
from sklearn.datasets import load_breast_cancer
X, y = load_breast_cancer(return_X_y=True)
```

### Step 2 — Split

```python
from sklearn.model_selection import train_test_split
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
```

### Step 3 — Single tree

```python
from sklearn.tree import DecisionTreeClassifier
tree = DecisionTreeClassifier(max_depth=4, random_state=0).fit(Xtr, ytr)
print("tree:", tree.score(Xte, yte))
```

### Step 4 — Random Forest

```python
from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(n_estimators=200, random_state=0).fit(Xtr, ytr)
print("rf  :", rf.score(Xte, yte))
```

### Step 5 — Feature importance

```python
import numpy as np
order = np.argsort(rf.feature_importances_)[::-1][:5]
print("top:", order)
```

**Expected output:** the single tree and the forest both print test accuracy, but the forest should usually be more stable. The feature-importance list is useful as a ranking hint, not as a proof of causality.

## What to Notice in This Code

- `max_depth` is the main lever against overfitting.
- More `n_estimators` is more stable, with diminishing returns.
- `feature_importances_` splits credit across correlated features.

## Read the first failure signal this way

- If the training score is perfect and the test score drops, cap tree depth before trying a more exotic model.
- If feature importance seems to contradict domain knowledge, check for correlated predictors and compare with permutation importance.
- If the forest wins only by a tiny margin, keep the simpler baseline in the conversation because interpretability may matter more than the last point of accuracy.

## Five Common Mistakes

1. Using a single deep tree without depth limits.
2. Reading feature importance as causal.
3. Standardizing features even though trees do not need it.
4. Trusting a 100% training accuracy.
5. Skipping a comparison with gradient-boosted trees.

## How This Shows Up in Production

Credit scoring, click prediction, and recommender features all run on tree ensembles. They remain the workhorse of tabular ML.

## How a Senior Engineer Thinks

- Random forest is baseline plus epsilon.
- Gradient boosting is usually stronger.
- Permutation importance is more trustworthy.
- Add SHAP for instance-level interpretation.
- Categorical features need model-specific handling.

## Checklist

- [ ] I set `max_depth` explicitly.
- [ ] I use enough trees in the forest.
- [ ] I know the limits of feature importance.
- [ ] I compare against a GBDT model.

## Practice Problems

1. Sweep `max_depth` from 1 to 20 and chart the test score.
2. Compare random forest with gradient boosting.
3. Compare default importance against permutation importance.

## Wrap-up and Next Steps

Trees and forests are the workhorse of tabular ML. Next we explore unsupervised learning through clustering.

## Answering the Opening Questions

- **By what criterion does a decision tree split the feature space?**
  - A decision tree repeatedly selects one feature and threshold to divide data in two, progressively partitioning the feature space. `DecisionTreeClassifier(max_depth=4)` stacks these splits within a limited depth to build prediction rules.
- **What do Gini and entropy measure?**
  - Gini and entropy measure how mixed the classes are within a node—impurity. The tree prefers splits that reduce this value most, so both metrics quantify "how much cleaner do labels become after one split."
- **Why does a single tree overfit so easily?**
  - Without depth limits, a single tree can create rules fine-grained enough to nearly memorize training data. That is why `max_depth` is emphasized as the most important knob, and `RandomForestClassifier(n_estimators=200)` averaging multiple trees typically produces more stable test scores.
<!-- toc:begin -->
## In this series

- [Machine Learning 101 (1/10): What Is Machine Learning?](./01-what-is-machine-learning.md)
- [Machine Learning 101 (2/10): Supervised and Unsupervised Learning](./02-supervised-and-unsupervised.md)
- [Machine Learning 101 (3/10): Train/Test Split](./03-train-test-split.md)
- [Machine Learning 101 (4/10): Linear Regression](./04-linear-regression.md)
- [Machine Learning 101 (5/10): Logistic Regression](./05-logistic-regression.md)
- **Decision Tree and Random Forest (current)**
- Clustering (upcoming)
- Overfitting and Regularization (upcoming)
- Model Evaluation (upcoming)
- The ML Project Workflow (upcoming)

<!-- toc:end -->

## References

- [scikit-learn — Decision Trees](https://scikit-learn.org/stable/modules/tree.html)
- [scikit-learn — Ensemble methods](https://scikit-learn.org/stable/modules/ensemble.html)
- [Random Forests — Breiman (2001)](https://link.springer.com/article/10.1023/A:1010933404324)
- [StatQuest — Random Forests](https://www.youtube.com/watch?v=J4Wdy0Wc_xQ)

Tags: MachineLearning, DecisionTree, RandomForest, Ensemble, scikit-learn
