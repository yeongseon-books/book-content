---
series: statistics-101
episode: 8
title: "Statistics 101 (8/10): Correlation and Regression"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Statistics
  - Correlation
  - Regression
  - Modeling
  - Beginner
seo_description: A side-by-side look at correlation coefficients and simple linear regression, with the limits of each and a clear note on causation
last_reviewed: '2026-05-04'
---

# Statistics 101 (8/10): Correlation and Regression

When two variables move together, people immediately want an explanation. Does more ad spend increase revenue? Does more study time improve the score? Does a lower price increase demand? Those are natural questions, but the first pattern you see is not automatically a proof of causation.

Correlation describes direction and strength. Regression writes the relationship as an equation you can inspect and use for prediction. They are closely related, but they do not answer the same question.

This is the 8th post in the Statistics 101 series. Here we will compare correlation coefficients with simple linear regression, explain why R² and residuals matter, and draw a clear boundary between relationship and causation.


![statistics 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/08/08-01-concept-at-a-glance.en.png)
*statistics 101 chapter 8 flow overview*
> Correlation shows *co-movement*; regression shows *prediction*. *Neither* proves *causation*.

## Questions to Keep in Mind

- What does a correlation coefficient tell us, and what does it not tell us?
- What extra information does a regression equation provide?
- How should we interpret R²?

## Why It Matters

*Revenue ~ ad spend*, *study time ~ score* — *relationships* are the *start of all analysis*. Correlation and regression are the tools that *put a relationship into numbers*.

> *Correlation is not causation.*

## Concept at a Glance
Correlation measures how tightly two variables move together. Regression builds a *line* (or *model*) to predict one variable from another. Both are powerful—and both are easily misused.
## Key Terms

- **Pearson r**: strength of *linear correlation* (-1 to +1).
- **Spearman ρ**: *rank-based* correlation — robust to non-linearity.
- **Simple Linear Regression**: y = β0 + β1·x + ε.
- **R²**: the *fraction of variance* the model *explains*.
- **Residual**: actual − predicted. *Residuals* are central to *model diagnostics*.

## Before / After

**Before**: *“Ad spend and revenue have correlation 0.6.”* — Type of relationship is *unknown*.

**After**: *“sales = 1,200 + 4.2·ads (R²=0.36) — every $10K of spend predicts +$4.2K of revenue.”*

## Hands-on: 5-step Regression

### Step 1 — Data

```python
import numpy as np, pandas as pd
ads = np.array([10, 20, 30, 40, 50, 60])
sales = np.array([1300, 1280, 1320, 1360, 1410, 1450])
```

### Step 2 — Correlation

```python
print("r:", np.corrcoef(ads, sales)[0, 1])
```

**Expected output:** something close to `r: 0.9...`, indicating a strong positive linear relationship in this toy dataset.

### Step 3 — Fit a regression

```python
from sklearn.linear_model import LinearRegression
X = ads.reshape(-1, 1)
model = LinearRegression().fit(X, sales)
print("β1:", model.coef_[0], "β0:", model.intercept_)
```

**Expected output:** `β1` tells you how much sales move per one-unit increase in ad spend, while `β0` gives the fitted intercept.

### Step 4 — R²

```python
print("R^2:", model.score(X, sales))
```

**Expected output:** often something like `R^2: 0.8...` on this simple example. That is high explanatory power, but it is still not a substitute for residual checks.

### Step 5 — Residuals

```python
import matplotlib.pyplot as plt
resid = sales - model.predict(X)
plt.scatter(model.predict(X), resid); plt.axhline(0); plt.show()
```

## What to Notice in This Code

- Correlation gives *direction and strength*; regression gives a *predictable equation*.
- *R²* lives in *0 to 1*; closer to 1 means *higher explanatory power*.
- *Patterns in residuals* point to *non-linearity*.

## Five Common Mistakes

1. **Confusing *correlation* with *causation*.**
2. **Letting *outliers* inflate the *correlation*.**
3. **Using *Pearson* on a *non-linear* relationship.**
4. **Calling a model good from *R² alone*.**
5. **Skipping *residual diagnostics*.**

## How This Shows Up in Production

Revenue forecasting, price ~ demand, ads ~ conversion, usage ~ churn — used everywhere in *business decisions*. It scales into *multivariate*, *logistic*, and *time-series* regression.

## How a Senior Engineer Thinks

- Knows the *correlation → causation* trap.
- *Always* visualizes.
- *Diagnoses residuals*.
- Reads *R²* alongside *effect size*.
- Separates *prediction* from *interpretation*.

## Checklist

- [ ] I know *correlation ≠ causation*.
- [ ] I know the difference between *Pearson and Spearman*.
- [ ] I understand *R²*.
- [ ] I check *residuals*.

## Practice Problems

1. Build *study time ~ score* data and compare *r* with *R²*.
2. Cite a *spurious correlation* mistakenly read as causation.
3. Explain why *Pearson* is *weak* on non-linear relationships.

## Wrap-up and Next Steps

Correlation and regression are the most basic tools for *expressing relationships as numbers*. The next episode goes deep into the *true meaning of the p-value*.

## Answering the Opening Questions

- **What does a correlation coefficient tell you, and what can't it tell?**
  Correlation measures how strongly two variables move together (direction and strength). It cannot establish causation—two variables may correlate because of a shared hidden cause.
- **What information does a regression equation provide beyond correlation?**
  Regression gives a predictive formula: for each unit change in X, Y changes by the slope amount. But past patterns don't guarantee future outcomes, and extrapolation beyond observed data is risky.
- **How should you read R² and within what range?**
  R² (0 to 1) indicates the fraction of Y's variance explained by X. In operations, correlation and regression results should be periodically re-validated and models updated as new patterns emerge.

<!-- toc:begin -->
## In this series

- [Statistics 101 (1/10): What Is Statistics?](./01-what-is-statistics.md)
- [Statistics 101 (2/10): Mean, Median, and Variance](./02-mean-median-variance.md)
- [Statistics 101 (3/10): Distributions](./03-distributions.md)
- [Statistics 101 (4/10): Sample and Population](./04-sample-and-population.md)
- [Statistics 101 (5/10): Estimation](./05-estimation.md)
- [Statistics 101 (6/10): Confidence Interval](./06-confidence-interval.md)
- [Statistics 101 (7/10): Hypothesis Testing](./07-hypothesis-testing.md)
- **Correlation and Regression (current)**
- Understanding p-value (upcoming)
- Statistical Thinking (upcoming)

<!-- toc:end -->

## References

- [scikit-learn — Linear Regression](https://scikit-learn.org/stable/modules/linear_model.html)
- [Khan Academy — Correlation](https://www.khanacademy.org/math/statistics-probability/describing-relationships-quantitative-data)
- [Spurious Correlations (Vigen)](https://www.tylervigen.com/spurious-correlations)
- [Wikipedia — Anscombe's Quartet](https://en.wikipedia.org/wiki/Anscombe%27s_quartet)

Tags: Statistics, Correlation, Regression, Modeling, Beginner
