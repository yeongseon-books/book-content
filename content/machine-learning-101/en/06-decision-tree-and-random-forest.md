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
seo_description: How decision trees split feature space, why single trees overfit, and how random forests reduce variance through bagging
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (6/10): Decision Tree and Random Forest

A giant `if-else` rule set sometimes outperforms neural networks on tabular data. That sounds surprising, but on customer records, transaction logs, and click data — anything organized into rows and columns — tree-based methods remain extremely strong baselines. The reason is straightforward: they capture nonlinear relationships naturally and require comparatively little preprocessing.

This is the 6th post in the Machine Learning 101 series. Here we cover how decision trees split feature space, why a single tree overfits easily, and how random forests combine many trees into a more stable ensemble.

![machine learning 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/06/06-01-concept-at-a-glance.en.png)
*machine learning 101 chapter 6 flow overview*
> A decision tree carves feature space into rectangles; a random forest takes a majority vote across many such trees to cover any single tree's mistakes.

## Questions to Keep in Mind

- On what basis does a decision tree split feature space?
- What do Gini and entropy measure?
- Why does a single tree overfit so easily?

## Why It Matters

Random forests and gradient-boosted trees remain the default strong choices for tabular data today. Before jumping to deep learning, they are the baselines you must beat.

## Key Terms

- **Split**: Dividing data using one feature and one threshold.
- **Gini / Entropy**: Metrics that measure impurity.
- **Pruning**: Limiting depth or leaf size.
- **Bagging**: Averaging over bootstrap samples.
- **Feature importance**: How much each feature contributed to splits.

## Before/After

**Before**: "Trees are interpretable" — and the explanation stops there. A single tree has very high variance.

**After**: Use forests to reduce variance, and extend explanation with tools like SHAP.

## Hands-on: 5-Step Trees and Forest

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

**Expected output:** Test accuracy for both models, with the forest generally more stable. The importance ranking is a **priority hint** for where to look next — not proof of causation.

## How Splits Work: Gini vs Entropy

At each node, the tree tries every feature and every possible threshold, choosing the split that reduces impurity the most.

- **Gini impurity**: `1 - Σ(p_i²)` — probability of misclassifying a randomly chosen sample.
- **Entropy**: `-Σ(p_i * log₂(p_i))` — information needed to describe the distribution.

In practice, Gini and entropy produce very similar trees. Gini is slightly faster to compute.

## Why Single Trees Overfit

An unrestricted tree will keep splitting until every leaf is pure — effectively memorizing the training data. That is why `max_depth`, `min_samples_split`, and `min_samples_leaf` exist: they trade a small amount of training accuracy for much better generalization.

## How Random Forest Reduces Variance

1. **Bootstrap sampling**: Each tree sees a different random subset of rows.
2. **Feature randomization**: At each split, only a random subset of features is considered.
3. **Averaging**: Final prediction is a majority vote (classification) or mean (regression).

This decorrelates individual trees so their errors cancel out rather than compound.

## What to Notice in This Code

- `max_depth` is the most important overfitting control.
- More `n_estimators` → more stable, but diminishing returns beyond ~200–500.
- Feature importance gives ranking, not causal explanation.

## Reading the First Failure Signals

- If training accuracy is 100% but test drops significantly, the tree is too deep — prune first.
- If a few features dominate importance, check whether they are leaking target information.
- If the forest barely beats the single tree, your data may simply not have much exploitable nonlinearity.

## Five Common Mistakes

1. **Letting a tree grow without depth limits.**
2. **Using feature importance as proof of causation.**
3. **Ignoring class imbalance (use `class_weight="balanced"`).**
4. **Forgetting that trees are unstable — small data changes create entirely different splits.**
5. **Not comparing to a simple logistic regression baseline.**

## How This Shows Up in Production

Credit scoring, ad click prediction, insurance risk, medical triage — anywhere tabular features are well-defined and interpretability is valued, tree ensembles dominate Kaggle leaderboards and production systems alike.

## How a Senior Engineer Thinks

- Start with a shallow tree to understand the data, then scale to a forest.
- Feature importance is a starting signal, not the final answer — follow up with SHAP.
- Gradient boosting (XGBoost, LightGBM) is the next step when forests plateau.
- For real-time serving, tree count and depth directly affect latency.
- Always compare to a linear baseline to quantify the nonlinearity benefit.

## Checklist

- [ ] I set `max_depth` or `min_samples_leaf` to prevent overfitting.
- [ ] I compare single tree vs. forest performance.
- [ ] I inspect top-5 feature importances.
- [ ] I know that importance ≠ causation.

## Practice Problems

1. Train trees at `max_depth` = 2, 5, 10, None and plot train vs. test accuracy.
2. Compare `RandomForestClassifier` with `GradientBoostingClassifier` on the same split.
3. Use `sklearn.tree.export_text` to print the first 3 levels of your tree and interpret the splits.

## Summary

Decision trees partition feature space with recursive splits. A single tree memorizes; a random forest diversifies and averages. The ensemble trades individual tree interpretability for much better generalization, and feature importance serves as a guide — not a conclusion.

Next post: we move to clustering, where there are no labels at all.

## Answering the Opening Questions

- **On what basis does a decision tree split feature space?**
  - At each node it evaluates every feature and threshold, picking the split that maximizes impurity reduction (Gini or entropy). The result is a set of axis-aligned rectangles in feature space.
- **What do Gini and entropy measure?**
  - Both measure how mixed the classes are at a node. Pure nodes (all one class) score 0. The tree picks splits that create the purest child nodes, minimizing remaining impurity.
- **Why does a single tree overfit so easily?**
  - Without depth constraints, it keeps splitting until every leaf is pure — essentially memorizing training data. Depth limits, minimum leaf sizes, and pruning are required to trade training perfection for generalization.

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
- [scikit-learn — Random Forests](https://scikit-learn.org/stable/modules/ensemble.html#forests-of-randomized-trees)
- [An Introduction to Statistical Learning — James et al., Ch. 8](https://www.statlearning.com/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)

Tags: MachineLearning, DecisionTree, RandomForest, Ensemble, scikit-learn
