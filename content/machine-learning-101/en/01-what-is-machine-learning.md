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

Recommendation systems, fraud filters, and medical triage tools all get called “machine learning,” but that label hides the real operating question. Are you writing smarter rules, doing statistics with a new library, or building a system that learns a reusable function from data? If that distinction stays fuzzy, every later discussion about models, metrics, and deployment turns into memorizing API names.

This is the first post in the Machine Learning 101 series. Here we will pin the topic down to one practical definition: machine learning means fitting a function from data, then trusting that function on inputs the model has never seen before.

## Questions to Keep in Mind

- What exactly is the model learning when we say “machine learning”?
- Why is generalization different from scoring well on the training set?
- Where does machine learning diverge from statistics and rule-based code?

## Big Picture

![machine learning 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/01/01-01-concept-at-a-glance.en.png)

*machine learning 101 chapter 1 flow overview*

This picture places What Is Machine Learning? inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of What Is Machine Learning? is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Why It Matters

Recommendation, medicine, finance, autonomous driving — *every industry* is being *reshaped* by ML. Weak fundamentals make *every model collapse* later.

## Concept at a Glance

## Key Terms

- **Learning**: *estimating a function* from data.
- **Generalization**: *working well* on *unseen data*.
- **Prediction**: applying the learned *function* to *new inputs*.
- **Feature**: *input variable*.
- **Label**: *target to predict*.

## Before/After

**Before**: *"Code every rule with if-else"* — every new pattern adds code.

**After**: *"Give data, the model learns rules"* — scale with *data, not code*.

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

**Expected output:** `X.shape` and `y.shape` should report a small tabular dataset such as `(150, 4)` and `(150,)`, `model.predict(X[:5])` should print class IDs, and the training accuracy will usually look very high. That last number is a teaching device, not proof that the model generalizes.

## What to Notice in This Code

- *fit / predict / score* is the *scikit-learn standard interface*.
- *score* here is only *training accuracy* — not generalization.
- *Model choice* depends on *problem type*.

## Read the first failure signal this way

- If training accuracy looks excellent but live data fails, check whether the input distribution changed or whether the target was defined too loosely.
- If the team cannot explain what `X` and `y` represent in one sentence, the project is not ready for model comparison yet.
- If a notebook demo works only on the sample rows you kept reusing, suspect leakage or accidental memorization before you blame the algorithm.

## Five Common Mistakes

1. **Judging *success* on *training data only*.**
2. **Ignoring *feature scaling*.**
3. ***Target leakage* in features.**
4. **No *random seed* — not reproducible.**
5. **Training without handling *missing values or outliers*.**

## How This Shows Up in Production

Recommendation, fraud detection, demand forecasting, image recognition, NLP chatbots — the *data → train → predict* pipeline is the *backbone of every ML product*.

## How a Senior Engineer Thinks

- *Problem definition* matters more than *model selection*.
- *Data quality* matters more than *algorithm*.
- Always measure *generalization* on *separate data*.
- Build a *baseline model* first.
- Save *complex models* for *last*.

## Checklist

- [ ] I know what *X, y* mean.
- [ ] I call *fit/predict/score*.
- [ ] I know *training accuracy ≠ generalization*.
- [ ] I value *baselines*.

## Practice Problems

1. Run *fit/predict* on *your own dataset* (not iris).
2. Explain when *score* would be *over-optimistic*.
3. Show an example where *feature scaling* changes the result.

## Wrap-up and Next Steps

ML is *a function learned from data*. Next we cover *supervised vs unsupervised learning*.

## Answering the Opening Questions

- **What exactly is the model learning when we say “machine learning”?**
  - The article treats What Is Machine Learning? as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why is generalization different from scoring well on the training set?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Where does machine learning diverge from statistics and rule-based code?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
