---
series: machine-learning-101
episode: 4
title: "Machine Learning 101 (4/10): Linear Regression"
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
  - LinearRegression
  - Regression
  - scikit-learn
  - Beginner
seo_description: Linear regression intuition, MSE, R-squared, residual interpretation, and why this model is still the first baseline to try
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (4/10): Linear Regression

A scatter plot that "looks like a line" is not an explanation. If one line can account for the bulk of variation in your data, that alone makes a powerful model — but you also need to see what it *cannot* explain. Linear regression is simple, which makes it fast, and that simplicity makes it an exceptional baseline.

This is the 4th post in the Machine Learning 101 series. Here we cover the linear regression equation and intuition, mean squared error, R-squared, and residual interpretation — together explaining why this model should still be the first thing you run.

![machine learning 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/04/04-01-concept-at-a-glance.en.png)
*machine learning 101 chapter 4 flow overview*
> Linear regression draws the single line whose total squared distance to all data points is smallest. Coefficients, R², and residuals are just different lenses on that same line.

## Questions to Keep in Mind

- How does the linear regression equation produce a prediction?
- What do MSE and the least-squares solution minimize?
- What exactly does R-squared explain?

## Cost Function and Gradient Descent

Linear regression predicts `y_hat = Xw + b`, but how does it find `w` and `b`? By minimizing a **cost function**.

### Mean Squared Error (MSE)

$$
\text{MSE} = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2
$$

Squaring errors penalizes large mistakes heavily, making the model sensitive to outliers.

### Gradient Descent

Gradient descent moves parameters in the direction opposite to the cost function's gradient, step by step:

1. Initialize weights randomly.
2. Compute the gradient of the cost at the current position.
3. Move weights a small step opposite to the gradient.
4. Repeat until convergence.

Linear regression can also be solved in closed form (normal equation), but understanding gradient descent here pays off when you encounter models without closed-form solutions.

## Python Example: Implementing with NumPy

```python
import numpy as np

# Simple data
X = np.array([[1], [2], [3], [4]])
y = np.array([2, 4, 6, 8])

# Add bias column (bias trick)
X_b = np.c_[np.ones((X.shape[0], 1)), X]

# Closed-form least-squares solution
theta = np.linalg.inv(X_b.T @ X_b) @ X_b.T @ y
print("w, b:", theta)
```

Under 10 lines showing the core of linear regression. Scikit-learn optimizes this and adds many options, but the math is the same.

## Linear Regression Assumptions

| Assumption | Meaning | How to Check |
|---|---|---|
| Linearity | X and y have a linear relationship | Residual vs. predicted plot |
| Independence | No multicollinearity among features | VIF (Variance Inflation Factor) |
| Homoscedasticity | Residual variance is constant | Absolute residual plot |
| Normality | Residuals are normally distributed | Q-Q plot |

Linear regression works best when these assumptions hold. Violated assumptions weaken coefficient interpretation and prediction quality.

## Why It Matters

Linear regression is interpretable, fast, and surprisingly powerful. It should be the first model you try. Without a baseline, there is no justification for more complex models.

## Key Terms

- **Weight `w`**: How much each feature contributes to the prediction.
- **Intercept `b`**: The baseline prediction when all features are zero.
- **MSE**: Mean squared error.
- **R-squared**: Proportion of variance explained by the model.
- **Residual**: `y - y_hat`.

## Before/After

**Before**: "It looks linear on the chart" — an impression without numeric verification.

**After**: Model, metrics, and residuals examined together in three verification steps.

## Hands-on: 5-Step Regression

### Step 1 — Data

```python
from sklearn.datasets import fetch_california_housing
X, y = fetch_california_housing(return_X_y=True)
```

### Step 2 — Split

```python
from sklearn.model_selection import train_test_split
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
```

### Step 3 — Fit

```python
from sklearn.linear_model import LinearRegression
model = LinearRegression().fit(Xtr, ytr)
```

### Step 4 — Evaluate

```python
from sklearn.metrics import mean_squared_error, r2_score
pred = model.predict(Xte)
print("MSE:", mean_squared_error(yte, pred))
print("R^2:", r2_score(yte, pred))
```

### Step 5 — Inspect Coefficients

```python
for name, coef in zip(range(Xtr.shape[1]), model.coef_):
    print(f"x{name}: {coef:.3f}")
```

**Expected output:** MSE, R², and signed coefficients. The first thing to check is not absolute score but whether **coefficient directions make intuitive sense** and whether residuals show patterns the linear model cannot capture.

## What to Notice in This Code

- The sign and magnitude of `coef_` are the center of interpretation.
- Low R-squared may signal hidden nonlinearity.
- MSE squares errors, so outliers dominate.

## Reading the First Failure Signals

- If R² is low and residuals show a curve, check whether **nonlinear features** are missing before discarding the linear model.
- If coefficients swing wildly between runs, investigate **multicollinearity** and **scale differences** first.
- If a few samples dominate the error, deciding whether to keep or remove those outliers is itself a modeling decision that should be explicit.

## Five Common Mistakes

1. **Comparing coefficients across different scales without standardizing.**
2. **Missing multicollinearity that makes coefficients unstable.**
3. **Skipping the residual plot.**
4. **Letting outliers drag the line unchecked.**
5. **Extrapolating far beyond the training range.**

## How This Shows Up in Production

Pricing, demand modeling, A/B effect estimation — wherever stakeholders want an **interpretable lever** rather than a black box, linear regression remains central.

## How a Senior Engineer Thinks

- Always start with a **baseline**.
- Interpretability is a **business tool**, not just a technical option.
- Residuals are the model's diary.
- Standardize before comparing coefficients.
- When regularization is needed, add Ridge or Lasso.

## Checklist

- [ ] I report MSE and R-squared together.
- [ ] I visualize residuals.
- [ ] I scale features before reading coefficients.
- [ ] I explicitly flag extrapolation risk.

## Practice Problems

1. Add `PolynomialFeatures(degree=2)` and observe how R-squared changes.
2. Plot residuals vs. predicted values and describe any patterns.
3. Compare coefficient magnitudes between `Ridge(alpha=1.0)` and plain `LinearRegression`.

## Summary

Linear regression fits a single line that minimizes total squared error. Its simplicity is its strength: fast, interpretable, and a mandatory first baseline. R² tells you how much variance is explained; residuals tell you what the model is missing.

Next post: we move from continuous values to binary classification with logistic regression.

## Answering the Opening Questions

- **How does the linear regression equation produce a prediction?**
  - It computes `y_hat = Xw + b` — a weighted sum of features plus an intercept. Each coefficient tells you how much the predicted value changes per unit increase in that feature, holding others constant.
- **What do MSE and the least-squares solution minimize?**
  - Both minimize the average of squared differences between actual and predicted values. Squaring penalizes large errors more, which is why outliers have outsized influence on the fitted line.
- **What exactly does R-squared explain?**
  - R² measures the fraction of total variance in y that the model accounts for. An R² of 0.6 means the model explains 60% of variance; the remaining 40% lives in the residuals, pointing to patterns the model cannot capture.

<!-- toc:begin -->
## In this series

- [Machine Learning 101 (1/10): What Is Machine Learning?](./01-what-is-machine-learning.md)
- [Machine Learning 101 (2/10): Supervised and Unsupervised Learning](./02-supervised-and-unsupervised.md)
- [Machine Learning 101 (3/10): Train/Test Split](./03-train-test-split.md)
- **Linear Regression (current)**
- Logistic Regression (upcoming)
- Decision Tree and Random Forest (upcoming)
- Clustering (upcoming)
- Overfitting and Regularization (upcoming)
- Model Evaluation (upcoming)
- The ML Project Workflow (upcoming)

<!-- toc:end -->

## References

- [scikit-learn — LinearRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)
- [An Introduction to Statistical Learning — James et al.](https://www.statlearning.com/)
- [Hands-On Machine Learning — Aurélien Géron, Ch. 4](https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/)
- [Google — ML Crash Course: Linear Regression](https://developers.google.com/machine-learning/crash-course/descending-into-ml)

Tags: MachineLearning, LinearRegression, Regression, scikit-learn, Beginner
