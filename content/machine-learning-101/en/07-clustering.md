---
series: machine-learning-101
episode: 7
title: Clustering
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
  - Clustering
  - KMeans
  - DBSCAN
  - UnsupervisedLearning
seo_description: When to use KMeans versus DBSCAN, how to pick K with the elbow and silhouette methods, and why standardization changes everything in clustering
last_reviewed: '2026-05-15'
---

# Clustering

Clustering feels less certain than classification because there is no answer sheet waiting in the test set. That uncertainty is exactly why teams misuse it. A clean-looking cluster plot can tempt you into believing you discovered truth when you may only have discovered the geometry created by scaling choices.

This is post 7 in the Machine Learning 101 series. Here we will compare KMeans and DBSCAN, use elbow and silhouette scores as guide rails, and keep the main discipline in view: clusters are hypotheses that still need interpretation.

## Questions this post answers

- Without labels, how do you judge whether the clusters are any good?
- When should you prefer KMeans over DBSCAN?
- How do you choose `K` without pretending the metric picks it for you?
- Why does standardization change the result so dramatically?
- Why should cluster labels be treated as hypotheses rather than truth?

> Clustering exposes the latent structure in data through similarity. But validation does not end with a metric; the result only becomes meaningful when the numbers and the interpretation agree.

## Why It Matters

Clustering is the backbone of segmentation, anomaly detection, and exploratory data analysis. It often runs before any supervised model.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/07/07-01-concept-at-a-glance.en.png)

*Once the inputs are standardized, KMeans and DBSCAN expose different kinds of structure: centroid-based groups versus density-based regions.*

## Key Terms

- **KMeans**: K centroids minimizing within-cluster distance.
- **DBSCAN**: density-based clustering with noise.
- **Inertia**: sum of squared distances to centroids.
- **Silhouette**: cohesion versus separation.
- **Elbow**: the point where additional K stops helping much.

## Before/After

**Before**: "K = 3, done." — without justification.

**After**: Combine elbow, silhouette, and domain knowledge to choose K.

## Hands-on: 5 Steps of Clustering

### Step 1 — Data

```python
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
X = StandardScaler().fit_transform(load_iris().data)
```

### Step 2 — KMeans

```python
from sklearn.cluster import KMeans
km = KMeans(n_clusters=3, n_init=10, random_state=0).fit(X)
print("inertia:", km.inertia_)
```

### Step 3 — Silhouette

```python
from sklearn.metrics import silhouette_score
print("sil:", silhouette_score(X, km.labels_))
```

### Step 4 — Elbow

```python
ks = list(range(2, 8))
scores = [KMeans(n_clusters=k, n_init=10, random_state=0).fit(X).inertia_ for k in ks]
print(list(zip(ks, scores)))
```

### Step 5 — DBSCAN

```python
from sklearn.cluster import DBSCAN
db = DBSCAN(eps=0.5, min_samples=5).fit(X)
print("labels:", set(db.labels_))
```

**Expected output:** KMeans produces inertia and silhouette values, while DBSCAN returns a set of labels that may include `-1` for noise. If that label appears, the algorithm is telling you some points do not belong cleanly to any dense region.

## What to Notice in This Code

- KMeans needs `K`; DBSCAN needs `eps`.
- Standardization changes the entire result.
- A label of `-1` from DBSCAN means noise.

## Read the first failure signal this way

- If the cluster assignment changes wildly after scaling, the distance geometry was doing more work than your intuition.
- If elbow and silhouette disagree, plot the clusters and ask which decision would survive contact with the business context.
- If DBSCAN labels almost everything as noise, revisit `eps`, `min_samples`, and feature scale before concluding the data has no structure.

## Five Common Mistakes

1. Using distance-based methods without standardizing first.
2. Choosing K without visual confirmation.
3. Forgetting that KMeans only fits convex clusters well.
4. Treating cluster labels as ground truth.
5. Fixing DBSCAN's `eps` without considering data scale.

## How This Shows Up in Production

Customer segmentation, color quantization, and anomaly detection all rely on clustering as the standard tool of unsupervised exploration.

## How a Senior Engineer Thinks

- Clusters are hypotheses, not answers.
- Validate downstream with measurable outcomes.
- Visualization carries the decision.
- Density methods handle outliers gracefully.
- Business meaning ultimately picks K.

## Checklist

- [ ] I always standardize before distance-based methods.
- [ ] I look at elbow and silhouette together.
- [ ] I know the meaning of DBSCAN noise labels.
- [ ] I treat cluster output as a hypothesis.

## Practice Problems

1. Sweep K from 2 to 7 and compare silhouette scores.
2. Compare KMeans with and without standardization.
3. Try DBSCAN with `eps` values 0.3, 0.5, and 1.0 and count clusters.

## Wrap-up and Next Steps

Clustering exposes hidden structure. Next, we examine overfitting and regularization, the limits of model fitting.

<!-- toc:begin -->
- [What Is Machine Learning?](./01-what-is-machine-learning.md)
- [Supervised and Unsupervised Learning](./02-supervised-and-unsupervised.md)
- [Train/Test Split](./03-train-test-split.md)
- [Linear Regression](./04-linear-regression.md)
- [Logistic Regression](./05-logistic-regression.md)
- [Decision Tree and Random Forest](./06-decision-tree-and-random-forest.md)
- **Clustering (current)**
- Overfitting and Regularization (upcoming)
- Model Evaluation (upcoming)
- The ML Project Workflow (upcoming)
<!-- toc:end -->

## References

- [scikit-learn — Clustering](https://scikit-learn.org/stable/modules/clustering.html)
- [scikit-learn — Silhouette analysis](https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html)
- [DBSCAN — Ester et al. (1996)](https://www.aaai.org/Papers/KDD/1996/KDD96-037.pdf)
- [StatQuest — KMeans](https://www.youtube.com/watch?v=4b5d3muPQmA)

Tags: MachineLearning, Clustering, KMeans, DBSCAN, UnsupervisedLearning
