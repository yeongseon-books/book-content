---
series: data-science-career-101
episode: 6
title: "Data Science Career 101 (6/10): The ML Interview"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - DataCareer
  - ML
  - Interview
  - Modeling
  - Beginner
seo_description: Prepare for machine learning interviews by mastering core modeling concepts, evaluation metrics, and practical strategies for solving problems.
last_reviewed: '2026-05-14'
---

# Data Science Career 101 (6/10): The ML Interview

Many candidates prepare for ML interviews by collecting model names and metric definitions. That is necessary, but it is not what makes an answer convincing. The hard part starts when the interviewer asks why a metric fits the business cost structure, what kind of leakage might exist, or how the model would be monitored after deployment.

That is why strong ML interview answers sound less like a glossary and more like a decision process. They begin with the problem, move through model choice and evaluation, and then widen into failure modes, retraining, and system behavior over time.

This is the 6th post in the Data Science Career 101 series.


![data science career 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-science-career-101/06/06-01-concept-at-a-glance.en.png)
*data science career 101 chapter 6 flow overview*
> In ML interviews, what matters most is not knowing every tool or concept, but asking the right questions at each stage and knowing when you have a good answer.

## Questions to Keep in Mind

- What topics do ML interviews usually cover besides algorithm basics?
- How should you explain model choice in a way that reflects real trade-offs?
- Why can metric selection not be separated from the problem definition?

## Why It Matters

Memorizing models without a decision frame usually produces shallow answers.

Interviewers want to hear how you reason under constraints: data size, interpretability, latency, class imbalance, labeling quality, and post-deployment drift. The model matters, but the reasoning matters more.

ML interview questions rarely have one right answer. Instead, they test whether you ask good clarifying questions, think about trade-offs, and know when to keep it simple.

## Key Terms

- **bias-variance**: The balance between underfit and overfit.
- **overfitting**: Memorizing training data.
- **AUC**: Area under the ROC curve.
- **precision/recall**: Trade-off between false positives and negatives.
- **drift**: Change in data distribution over time.

## Before/After

**Before**: "Random Forest is always good."

**After**: "I pick the model from problem and metric."

## Hands-on: Five Answer Patterns

Practice building five core answers: classification problem, regression problem, unbalanced data, feature selection, and model evaluation. These five cover 70% of real interviews.

### Step 1 — Fundamentals

```text
Explain bias-variance in one line.
```

Good fundamentals answers are concise but show the trade-off structure. For bias-variance: "high bias misses the signal; high variance captures noise as if it were signal."

### Step 2 — Model Choice

```text
- assumptions: linear vs tree vs neural
- data size, interpretability
```

When explaining model choice, never start with the model name. Start with the problem constraint. "We have 5K labeled rows, the stakeholder needs to audit individual predictions, and latency must stay under 50ms" immediately narrows the field without sounding like a memorized list.

### Step 3 — Evaluation

```python
from sklearn.metrics import precision_score, recall_score, roc_auc_score
```

Metric selection is inseparable from problem definition. If the cost of a false negative is 100x the cost of a false positive (fraud detection, cancer screening), optimizing accuracy is misleading. Always connect the metric back to the business cost structure.

### Step 4 — Production Traps

```text
- data leakage
- class imbalance
- time leakage
```

Interviewers often probe production traps because they separate textbook knowledge from deployment experience. Below is a table of the three most common traps and how to address them in an interview answer:

| Trap | What Goes Wrong | Interview Answer Pattern |
| --- | --- | --- |
| Data leakage | Future information bleeds into training features | "I check whether any feature uses data unavailable at prediction time. Common sources: aggregating over future rows, joining on post-event labels." |
| Class imbalance | Model predicts majority class and still scores high on accuracy | "I report precision-recall and calibration, not accuracy. I consider stratified splits, SMOTE only if justified, and threshold tuning." |
| Post-deploy degradation | Distribution shifts after launch | "I define monitoring metrics (PSI for features, performance on recent labeled slice) and set an automated retraining trigger." |

### Step 5 — System Design

```text
- data -> train -> serve -> monitor
- retraining cadence
- drift detection
```

A complete ML system answer covers five stages: data ingestion, feature engineering, training, serving, and monitoring. When the interviewer asks about retraining, they want to hear a decision rule ("retrain when weekly AUC drops below 0.72 for two consecutive weeks") rather than a vague "we retrain periodically."

## Domain-Specific ML Interviews

ML interviews differ significantly by industry because the success metric, risk profile, and data characteristics change. The table below summarizes what interviewers prioritize in three common domains:

| Domain | Representative Problems | Priority Metrics | Key Risks | Modeling Perspective |
| --- | --- | --- | --- | --- |
| Finance | Fraud detection, credit scoring, churn prediction | Precision at low FPR, expected loss | Regulatory audit, explainability requirements | Interpretable models preferred; ensemble only with SHAP |
| Healthcare | Diagnosis support, readmission prediction | Sensitivity (recall), calibration | Patient safety, FDA/IRB compliance | Threshold conservatism; false negatives carry highest cost |
| E-commerce | Recommendation, demand forecasting, dynamic pricing | Revenue lift, NDCG, MAPE | Cold-start users, seasonality, price elasticity | Real-time serving latency critical; A/B test everything |

When preparing for a domain-specific interview, build one end-to-end example per domain: state the problem, choose the metric with a business justification, name one likely failure mode, and describe how you would monitor after launch.

## Model Operations Checklist for Interview Answers

Interviewers at companies with production ML systems often ask how you would operate a model after deployment. This checklist structures a strong answer:

```text
1. Monitoring: feature drift (PSI), prediction drift, latency p99
2. Alerting: threshold breach → on-call notification → runbook
3. Retraining trigger: scheduled (weekly) + conditional (metric drop)
4. Rollback plan: shadow scoring against previous version
5. Documentation: model card with training data, performance bounds, known limitations
```

Mentioning even three of these five items signals operational maturity and separates you from candidates who treat modeling as a notebook exercise.

## What to Notice in This Code

- The metric decides the answer.
- Mentioning traps signals seniority.
- Think in systems.

## Five Common Mistakes

1. **Random Forest as the answer to everything.**
2. **Watching AUC only.**
3. **Not knowing leakage.**
4. **No retraining plan.**
5. **Ignoring interpretability.**

## How This Shows Up in Production

Many ML interviews spend more time on operations than candidates expect because production systems fail in more ways than a notebook suggests.

Accuracy is only one part of the story. A model can score well offline and still fail if the data pipeline changes, the monitoring is weak, or the retraining loop is undefined.

## How a Senior Engineer Thinks

- Start from problem definition.
- Metric chooses the model.
- Mention traps first.
- Think system-level.
- Plan for drift.

## Checklist

- [ ] Five metrics.
- [ ] Compare three models.
- [ ] Memorize three traps.
- [ ] One system diagram.

## Practice Problems

1. One line: define overfitting.
2. One line: example of drift.
3. One line: AUC vs recall.

## Wrap-up and Next Steps

The most useful preparation move is to build a repeatable answer structure: define the problem, choose a model class, justify the metric, name the traps, and describe the deployment and monitoring loop.

The next post shifts from model judgment to product and business judgment through the case interview format.

## Answering the Opening Questions

- **What areas do ML interviews actually test?**
  - Beyond algorithm basics, interviews test metric justification tied to business costs, production trap awareness (leakage, drift, imbalance), and system design from training through monitoring.
- **What should you say first when explaining model selection?**
  - Start with the problem constraints—data size, interpretability needs, latency budget—then show how those constraints narrow the model class before naming specific algorithms.
- **Why must evaluation metrics be viewed alongside problem definition?**
  - Because the same model can look excellent or terrible depending on which metric you report; metric choice encodes the business cost structure, so choosing the wrong metric means optimizing for the wrong outcome.
<!-- toc:begin -->
## In this series

- [Data Science Career 101 (1/10): What Is a Data Career](./01-what-is-data-career.md)
- [Data Science Career 101 (2/10): Analyst vs Scientist vs Engineer](./02-analyst-scientist-engineer.md)
- [Data Science Career 101 (3/10): Designing the Learning Path](./03-learning-path.md)
- [Data Science Career 101 (4/10): The Data Portfolio](./04-data-portfolio.md)
- [Data Science Career 101 (5/10): SQL and Analytics Interviews](./05-sql-and-analytics-interview.md)
- **The ML Interview (current)**
- The Case Interview (upcoming)
- Settling into the First Data Job (upcoming)
- Building Domain Expertise (upcoming)
- The Path to Senior in Data (upcoming)

<!-- toc:end -->

## References

- [Chip Huyen - Designing Machine Learning Systems](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/)
- [scikit-learn - Model Evaluation: Quantifying the Quality of Predictions](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [Chip Huyen - Machine Learning Interviews Book](https://huyenchip.com/ml-interviews-book/)
- [Google Developers - Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)

Tags: DataCareer, ML, Interview, Modeling, Beginner
