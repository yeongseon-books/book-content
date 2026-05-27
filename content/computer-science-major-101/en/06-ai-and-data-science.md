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

- What boundary should you inspect first when applying AI and Data Science?
- Which signal should the example or diagram make visible for AI and Data Science?
- What failure should be prevented first when AI and Data Science reaches a real system?

## What You Will Learn

- *Statistics* basics
- *Machine learning* intro
- *Deep learning* basics
- *Data analysis*
- The *division of labor* between the two

## Why It Matters

*Data sense* is the *core skill* of every *modern engineer*.

## Concept at a Glance
Classification, regression, clustering, and neural networks are not black boxes—they are *assumptions about data* made visible through math.
## Key Terms

- **feature**: *input* variable.
- **label**: *target* value.
- **training**: *learning*.
- **inference**: *prediction*.
- **dataset**: *collection* of data.

## Before/After

**Before**: You only look at *models*.

**After**: You look at *data quality* and *distribution*.

## Hands-on: Mini ML Pipeline

### Step 1 — Data

```python
xs = [1, 2, 3, 4]
ys = [2, 4, 6, 8]
```

### Step 2 — Mean

```python
avg = sum(ys) / len(ys)
```

### Step 3 — Regression slope

```python
def slope(xs, ys):
    mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    den = sum((x-mx)**2 for x in xs)
    return num / den
```

### Step 4 — Prediction

```python
m = slope(xs, ys)
pred = m * 5
```

### Step 5 — Evaluation

```python
mae = sum(abs(m*x - y) for x, y in zip(xs, ys)) / len(xs)
```

## What to Notice in This Code

- *Statistics* underlies the *model*.
- *Prediction* is *function application*.
- *Evaluation* validates *learning*.

## Five Common Mistakes

1. **Creating *data leakage*.**
2. **Mixing *train and test* sets.**
3. **Comparing *without scaling*.**
4. **Reaching for *complex models* first.**
5. **Leaving *metrics* vague.**

## How This Shows Up in Production

Detecting *distribution shift* is the *core* skill of *model operations*.

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

Next post: *Project Subjects*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying AI and Data Science?**
  - The article treats AI and Data Science as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for AI and Data Science?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when AI and Data Science reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
