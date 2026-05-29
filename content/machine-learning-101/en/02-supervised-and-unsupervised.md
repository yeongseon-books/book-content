---
series: machine-learning-101
episode: 2
title: "Machine Learning 101 (2/10): Supervised and Unsupervised Learning"
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
  - SupervisedLearning
  - UnsupervisedLearning
  - Classification
  - Clustering
seo_description: When to use supervised vs unsupervised learning, the difference between classification, regression, clustering, with runnable code
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (2/10): Supervised and Unsupervised Learning

Most beginner ML mistakes are not model mistakes. They are framing mistakes. Teams jump into logistic regression or KMeans before agreeing on the more important question: do we have labels, do we need a numeric prediction, or are we only trying to surface structure in the data?

This is the 2nd post in the Machine Learning 101 series. Here we will separate supervised learning from unsupervised learning and use that split to clarify where classification, regression, and clustering actually belong.

![machine learning 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/02/02-01-concept-at-a-glance.en.png)
*machine learning 101 chapter 2 flow overview*
> The line between supervised and unsupervised learning is whether the data carries labels; classification, regression, and clustering all follow from that one fact.

## Questions to Keep in Mind

- When labels are present versus absent, do we reach for the same algorithms?
- How do classification and regression differ if both are supervised learning?
- Why is clustering not just "classification without labels"?

## ML Paradigm Comparison

| Type | Goal | Output | Representative Algorithms |
|---|---|---|---|
| Classification | Predict discrete labels | 0, 1, 2, etc. | Logistic Regression, Decision Tree |
| Regression | Predict continuous values | 123.4, -0.89, etc. | Linear Regression, SVR |
| Clustering | Group similar points | Cluster ID | KMeans, DBSCAN |
| Dimensionality Reduction | Compress features | Lower-dimensional X | PCA, t-SNE |

Classification and regression are both supervised but target different output types. Clustering and dimensionality reduction are unsupervised — they find structure without labels.

## Why It Matters

Picking the wrong paradigm makes any subsequent model improvement meaningless. Problem framing is the first lever. If you approach a continuous-value prediction as classification, or expect supervised-style accuracy when there are no labels, the problem definition — not the model — is what broke first.

## Key Terms

- **Supervised learning**: Learn a function from `(X, y)` pairs.
- **Unsupervised learning**: Discover structure from `X` alone.
- **Classification**: Predict discrete labels.
- **Regression**: Predict continuous values.
- **Clustering**: Group similar points by distance or density.

## Before/After

**Before**: "ML is one line of regression" — paradigm distinction is skipped entirely.

**After**: First check whether **labels exist**, then decide **classification or regression**, then pick the algorithm.

## Hands-on: 5 Steps Comparing Paradigms

### Step 1 — Load data

```python
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)
```

### Step 2 — Supervised classification

```python
from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(max_iter=1000).fit(X, y)
print("clf acc:", clf.score(X, y))
```

### Step 3 — Regression dataset

```python
from sklearn.datasets import fetch_california_housing
Xr, yr = fetch_california_housing(return_X_y=True)
```

### Step 4 — Regression model

```python
from sklearn.linear_model import LinearRegression
reg = LinearRegression().fit(Xr, yr)
print("R^2:", reg.score(Xr, yr))
```

### Step 5 — Unsupervised clustering

```python
from sklearn.cluster import KMeans
km = KMeans(n_clusters=3, n_init=10).fit(X)
print("inertia:", km.inertia_)
```

**Expected output:** The classifier prints training accuracy, the regression model prints R², and KMeans returns inertia. These numbers are **not comparable** — changing the paradigm changes the success criterion.

## Semi-supervised and Self-supervised Learning

In practice, the space between supervised and unsupervised is where most real projects live.

### Semi-supervised learning

- Used when labeled data is scarce but unlabeled data is abundant.
- Example: 100 images are human-labeled, 10,000 are not. Semi-supervised techniques reduce labeling cost dramatically.

### Self-supervised learning

- Labels are automatically derived from the data itself.
- Example: mask a word in a sentence and train the model to predict it — this is how modern language models learn.
- Widely adopted in NLP and computer vision.

At the introductory level, getting the supervised/unsupervised boundary right is sufficient. In production, considering these intermediate techniques often leads to more cost-effective solutions.

## Python Example: KMeans vs LogisticRegression

```python
from sklearn.datasets import load_iris
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression

X, y = load_iris(return_X_y=True)

# Unsupervised: clustering
km = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X)
print("Inertia:", km.inertia_)  # cohesion (lower is tighter)

# Supervised: classification
clf = LogisticRegression(max_iter=1000).fit(X, y)
print("Accuracy:", clf.score(X, y))  # training accuracy
```

Inertia and accuracy cannot be compared. Unsupervised learning has no ground truth, which makes interpretation inherently harder.

## What to Notice in This Code

- `clf.score` returns accuracy, `reg.score` returns R-squared, `km.inertia_` measures cluster cohesion. **Different metrics mean different things.**
- `KMeans(n_init=...)` directly affects reproducibility and stability.
- Unsupervised results are harder to interpret because there is no ground truth.

## Reading the First Failure Signals

- If the team cannot say what the label is, ask what **downstream action** the prediction should trigger before touching any algorithm.
- If clustering output gets treated like a true class label, stop and define the **validation method** first.
- If metric discussions keep going in circles, check whether people are comparing a supervised score to an unsupervised cohesion number in the same table.

## Five Common Mistakes

1. **Solving a regression problem as classification (or the reverse).**
2. **Discarding partially labeled data instead of exploring semi-supervised methods.**
3. **Treating cluster assignments as ground truth.**
4. **Fixing `K` for clustering without ever visualizing.**
5. **Skipping standardization before distance-based algorithms.**

## How This Shows Up in Production

Spam and fraud detection rely on classification. Pricing and demand forecasting rely on regression. Customer segmentation relies on clustering. Real systems combine all three to produce ranking and recommendation.

## How a Senior Engineer Thinks

- Order matters: **problem → metric → paradigm**.
- Unsupervised methods are extremely valuable early on for exploration.
- Semi-supervised setups are actually the more common case in industry.
- Reinforcement learning is the last card to play.
- A **labeling strategy** often makes a bigger difference than algorithm choice.

## Checklist

- [ ] I can give an example of classification, regression, and clustering.
- [ ] I know the meaning behind each `.score()` value.
- [ ] I know `K` in KMeans is a hyperparameter.
- [ ] I know which algorithms require standardized inputs.

## Practice Problems

1. Cluster `iris` with KMeans and produce a cross-tab against the true `y`.
2. List three problems best framed as regression and three as classification.
3. Describe one situation where semi-supervised learning is the right answer.

## Summary

Paradigm selection sets the ceiling on model performance. Getting the supervised/unsupervised distinction right means all downstream steps — data preparation, evaluation, interpretation — align in the same direction.

Three takeaways: First, classification and regression are both supervised but target different output types. Second, clustering is a structure-discovery problem without ground truth. Third, a wrong problem framing makes model improvement pointless.

Next post: we measure generalization with train/test splits.

## Answering the Opening Questions

- **Can you use the same algorithm with and without labels?**
  - With labels, `LogisticRegression` or `LinearRegression` computes accuracy or R² from `(X, y)`. Without labels, you need structure-finding algorithms like `KMeans`, where `inertia_` has a different meaning from accuracy and cannot be compared on the same scale.
- **Classification and regression are both supervised—what differs?**
  - Classification predicts discrete class labels (0, 1, 2) like the iris example; regression predicts continuous values like the California housing example. Same supervised framework, but loss functions, metrics, and interpretation all differ.
- **Why is clustering treated as an entirely different problem from classification?**
  - Clustering groups similar samples without ground-truth labels — the article evaluated KMeans results through cohesion and interpretation, not accuracy. Cluster IDs should not be used as class labels directly; visualization and downstream validation must confirm whether groupings match actual business distinctions.

<!-- toc:begin -->
## In this series

- [Machine Learning 101 (1/10): What Is Machine Learning?](./01-what-is-machine-learning.md)
- **Supervised and Unsupervised Learning (current)**
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

- [scikit-learn — Supervised learning](https://scikit-learn.org/stable/supervised_learning.html)
- [scikit-learn — Unsupervised learning](https://scikit-learn.org/stable/unsupervised_learning.html)
- [Pattern Recognition and Machine Learning — Bishop](https://www.microsoft.com/en-us/research/people/cmbishop/prml-book/)
- [Google — ML Problem Framing](https://developers.google.com/machine-learning/problem-framing)

Tags: MachineLearning, SupervisedLearning, UnsupervisedLearning, Classification, Clustering
