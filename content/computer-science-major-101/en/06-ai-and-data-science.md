---
series: computer-science-major-101
episode: 6
title: "Computer Science Major 101 (6/10): AI and Data Science"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - CS
  - AI
  - DataScience
  - ML
  - Beginner
seo_description: A beginner-friendly tour of AI and data science covering statistics, ML, deep learning, and data analysis.
code_required: false
last_reviewed: '2026-05-14'
---

# Computer Science Major 101 (6/10): AI and Data Science

> Computer Science Major 101 series (6/10)

**Core question**: *How* do *AI* and *data science* *split* and *connect* inside the major?

> *Data* is the *common input*, *AI* is the *model*, *analysis* is the *interpretation*.

This is the 6th post in the Computer Science Major 101 series.


![computer science major 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-major-101/06/06-01-ai-learning-pipeline.en.png)
*computer science major 101 chapter 6 flow overview*
> AI and data science are not about algorithms—they are about matching the *right model* to the *right problem*, given the *right constraints*.

## Questions to Keep in Mind

- How do AI and data science divide and connect within the CS major?
- What flow connects statistics, machine learning, deep learning, and data analysis?
- Why does studying only models quickly hit a ceiling?

## What You Will Learn

- *Statistics* basics
- *Machine learning* intro
- *Deep learning* basics
- *Data analysis*
- The *division of labor* between the two

## Why It Matters

Data sense is not a specialized skill for one role — it is a baseline competency for nearly every modern engineer. Model performance only means something on top of data quality and evaluation design, so the ability to read underlying structure matters more than surface-level results.

## Concept at a Glance

> Data is the raw material, statistics is the language for reading it, and a model is the tool that computes patterns on top.

Data is the starting point, statistics is the language for reading that data. Machine learning and neural networks build predictive models on top, and analysis interprets results and connects them to real problems. The field names differ but the flow is continuous.

## Key Terms

- **feature**: *input* variable.
- **label**: *target* value.
- **training**: *learning* patterns from data.
- **inference**: *prediction* using a trained model.
- **dataset**: *collection* of data for analysis and learning.

## Before/After

**Before**: You only look at *models* and performance numbers.

**After**: You look at *data quality*, *distribution*, and *evaluation methodology* together.

## Hands-on: Mini ML Pipeline

### Step 1 — Data

```python
xs = [1, 2, 3, 4]
ys = [2, 4, 6, 8]
```

The smallest possible supervised learning example. Input-target pairs must exist for the subsequent steps to make sense.

### Step 2 — Mean

```python
avg = sum(ys) / len(ys)
```

Basic statistics like the mean are the starting point for reading data before a model. Picking models without knowing even the center of your data is a habit that does not last.

### Step 3 — Regression slope

```python
def slope(xs, ys):
    mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    den = sum((x-mx)**2 for x in xs)
    return num / den
```

The simplest regression example, but it illustrates that a model is ultimately a function that mathematically approximates relationships in data.

### Step 4 — Prediction

```python
m = slope(xs, ys)
pred = m * 5
```

After training, the model predicts values for new inputs. In production, this step connects to inference cost, response latency, and operational quality.

### Step 5 — Evaluation

```python
mae = sum(abs(m*x - y) for x, y in zip(xs, ys)) / len(xs)
```

A model producing output is not enough. You need a numeric measure of how wrong it is before comparison and improvement become possible.

## What to Notice in This Code

- *Statistics* underlies the *model*.
- *Prediction* is *function application*.
- *Evaluation* validates *learning*.

## Shifting from Model Names to Problem-Centered Thinking

The biggest trap when taking AI and data science courses is assuming that knowing many model names equals competence. Real competence is measured by whether you can coherently explain the entire pipeline: problem definition, data collection/cleaning, baseline setting, evaluation design, error analysis, and operational monitoring. A model is only one step in this pipeline.

The table below organizes common analysis tasks by approach:

| Problem Type | Input Data | First Baseline | Advanced Direction | Key Metric |
|---|---|---|---|---|
| Binary classification | Customer churn, spam detection | Logistic regression | Tree ensembles, neural nets | Precision/Recall/F1 |
| Regression | Demand forecasting, price prediction | Linear regression | GBM, time-series models | MAE/RMSE |
| Clustering | User segments | K-means | HDBSCAN, embedding-based | Silhouette score, interpretability |
| Recommendation | User-item logs | Popularity baseline | Collaborative filtering, deep learning | CTR, NDCG |

The point is not to recommend specific models but to build the habit of "always start with a baseline." Without a baseline, you cannot prove improvement.

## Where Statistics and ML Courses Connect

- The sample vs population concept is the starting point for explaining data bias.
- Understanding variance and covariance is necessary for feature scaling and correlation structure.
- Hypothesis testing tells you whether a performance difference is chance or meaningful.
- Overfitting/underfitting diagnosis is directly tied to bias-variance balance intuition.

In other words, statistics is not an elective for ML — it is a safety mechanism. Without it, you easily over-trust performance numbers and misinterpret production performance drops.

## Practical Learning Loop

1. Rewrite the problem as a business sentence
2. Lock the label definition and evaluation metric first
3. Build a baseline model, then analyze error cases
4. Check data quality before introducing advanced models
5. Record results in a reproducible notebook/report

Running through this loop even once makes it clear that AI courses are judgment courses, not tool-usage courses.

## Why Evaluation Design Comes Before Model Performance

The same accuracy number means different things depending on data distribution and error costs. In medical or security contexts where false-negative cost is high, recall may matter more than accuracy. In recommendation systems, ranking metrics are closer to perceived quality. Therefore metric selection is not a technical choice — it is part of problem definition.

At the undergraduate level, repeating "small reproducible experiments" is ideal. Change only the feature preprocessing on the same data and record the result difference, or tabulate improvement over the baseline. This habit lets you judge new models without hype.

## Paper Reading Guide and Experiment Record Template

In AI courses, the ability to read papers and convert them into implementation hypotheses is important. Reading in this order lets you interpret even cutting-edge model papers without exaggeration:

1. Check the problem definition and evaluation metric first
2. Check dataset composition and preprocessing conditions
3. Check improvement over baseline and statistical significance
4. Record failure cases and limitations first
5. Reduce to the smallest reproducible experiment for your own project

Recommended experiment record template has six columns: `hypothesis`, `data`, `model`, `metric`, `result`, `next experiment`. Maintaining this structure keeps quality consistent across lab projects, capstones, and job portfolios.

## Five Common Mistakes

1. **Creating *data leakage*.**
2. **Mixing *train and test* sets.**
3. **Comparing *without scaling*.**
4. **Reaching for *complex models* first.**
5. **Leaving *metrics* vague.**

## How This Shows Up in Production

One of the most important production skills is detecting *distribution shift*. When training data and production data diverge, performance degrades quickly. Strong teams inspect data flow and evaluation systems more often than the model itself.

## How a Senior Engineer Thinks

- *Data* matters more than the *model*.
- *Baseline* first.
- *Evaluation* is *evidence*.
- Think about *interpretability*.
- Secure *reproducibility*.

## Checklist

- [ ] *Train/test* split.
- [ ] *Baseline* model.
- [ ] *Metric* stated.
- [ ] *Seed* fixed.

## Practice Problems

1. Define *feature* in one line.
2. Define *label* in one line.
3. State the meaning of *model* in one line.

## Wrap-up and Next Steps

AI and data science carry different names but within the major they sit on a single flow of data understanding and modeling. Statistics and data analysis form the foundation; machine learning and deep learning build on top. Next post: *Project Subjects*.

## Answering the Opening Questions

- **How do AI and data science divide and connect within the CS major?**
  - AI models are built on data and statistics plus optimization theory, while data science covers the entire cycle from problem definition to result interpretation — not just models. The two overlap in some areas and diverge in others.
- **What flow connects statistics, machine learning, deep learning, and data analysis?**
  - As model layers increase from linear regression to neural networks, complexity grows — but so does interpretive difficulty. The ability to distinguish between a simple model and a complex model appropriate for the problem is what matters.
- **Why does studying only models quickly hit a ceiling?**
  - Real data differs from textbook-clean data. Handling missing values, outliers, and class imbalance — and verifying whether model performance is luck or meaningful improvement — is the practical competency that matters.
<!-- toc:begin -->
## In this series

- [Computer Science Major 101 (1/10): What Computer Science Majors Learn](./01-what-cs-majors-learn.md)
- [Computer Science Major 101 (2/10): Understanding First Year Subjects](./02-first-year-subjects.md)
- [Computer Science Major 101 (3/10): Data Structures and Algorithms](./03-data-structures-and-algorithms.md)
- [Computer Science Major 101 (4/10): Understanding Systems Subjects](./04-systems-subjects.md)
- [Computer Science Major 101 (5/10): Database and Network](./05-database-and-network.md)
- **AI and Data Science (current)**
- Project Subjects (upcoming)
- How to Study Computer Science (upcoming)
- Build Your Portfolio (upcoming)
- Skills to Have Before Graduation (upcoming)

<!-- toc:end -->

## References

- [An Introduction to Statistical Learning](https://www.statlearning.com/)
- [Deep Learning Book - Goodfellow](https://www.deeplearningbook.org/)
- [Pattern Recognition and Machine Learning](https://www.microsoft.com/en-us/research/uploads/prod/2006/01/Bishop-Pattern-Recognition-and-Machine-Learning-2006.pdf)
- [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)

Tags: CS, AI, DataScience, ML, Beginner
