---
series: data-science-career-101
episode: 5
title: "Data Science Career 101 (5/10): SQL and Analytics Interviews"
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
  - SQL
  - Analytics
  - Interview
  - Beginner
seo_description: A beginner-friendly tour of patterns for SQL and analytics interviews.
last_reviewed: '2026-05-14'
---

# Data Science Career 101 (5/10): SQL and Analytics Interviews

Many candidates prepare for SQL interviews as if they were grammar exams. They memorize JOIN types, aggregation syntax, and window functions, but they still struggle once the interviewer asks, “What exactly are you counting?” or “How would you explain this result to a product manager?”

That gap exists because SQL interviews are usually reasoning interviews in disguise. The query matters, but so do the assumptions behind it: the metric definition, the NULL behavior, the time boundary, and the interpretation that turns a result set into an insight.

This is post 5 in the Data Science Career 101 series.

## Questions to Keep in Mind

- What do SQL and analytics interviews actually evaluate beyond syntax?
- How should you break a business question into query steps?
- What are the recurring patterns around JOINs, aggregation, windows, and funnels?

## Big Picture

![data science career 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-science-career-101/05/05-01-concept-at-a-glance.en.png)

*data science career 101 chapter 5 flow overview*

This picture places SQL and Analytics Interviews inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of SQL and Analytics Interviews is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What You Will Learn

- Core *SQL* patterns
- Question *decomposition*
- Metric *definition*
- Result *interpretation*
- Mock *practice*

## Why It Matters

SQL is the shared language across most data roles, which is why interviewers use it to observe more than database fluency.

They are also watching how you define the metric, whether you surface assumptions, and whether you can tell the difference between “I got a number” and “I understand what this number means.”

## Concept at a Glance

## Key Terms

- **JOIN**: Combining tables.
- **GROUP BY**: Aggregation.
- **window function**: Row-wise aggregation over a frame.
- **CTE**: Common table expression.
- **funnel**: Funnel analysis.

## Before/After

**Before**: "I just write SELECT *."

**After**: "I decompose the question and use CTEs for readability."

## Hands-on: Five Question Patterns

### Step 1 — Single-Table Aggregation

```sql
SELECT date, COUNT(*) AS dau
FROM events
WHERE event = 'login'
GROUP BY date
ORDER BY date;
```

### Step 2 — JOIN

```sql
SELECT u.country, COUNT(o.id) AS orders
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.country;
```

### Step 3 — Window Function

```sql
SELECT user_id, amount,
       SUM(amount) OVER (PARTITION BY user_id ORDER BY ts) AS cum
FROM payments;
```

### Step 4 — Funnel

```sql
WITH steps AS (
  SELECT user_id,
         MAX(CASE WHEN step='visit' THEN 1 ELSE 0 END) AS s1,
         MAX(CASE WHEN step='signup' THEN 1 ELSE 0 END) AS s2,
         MAX(CASE WHEN step='purchase' THEN 1 ELSE 0 END) AS s3
  FROM funnel GROUP BY user_id
)
SELECT SUM(s1), SUM(s2), SUM(s3) FROM steps;
```

### Step 5 — One-Sentence Interpretation

```text
"Conversion fell from X to Y, hypothesis Z."
```

## What to Notice in This Code

- CTEs improve readability.
- Metric definition changes the conclusion.
- Interpretation is the finish line.

## Five Common Mistakes

1. **Overusing SELECT *.**
2. **Ignoring NULL handling.**
3. **Ignoring time zones.**
4. **Vague metric definitions.**
5. **No interpretation.**

## How This Shows Up in Production

Analytics interviews commonly pair one SQL problem with one interpretation or case-style follow-up because real work almost never stops at query execution.

In production, the important part is often the sentence after the query: what changed, whether the result is trustworthy, and what should be checked next.

## How a Senior Engineer Thinks

- Define the metric first.
- CTEs are colleague-friendly.
- Interpretation is the value.
- Remember NULL.
- State the time zone.

## Checklist

- [ ] Four kinds of JOIN.
- [ ] Three windows.
- [ ] One funnel.
- [ ] One-sentence interpretation.

## Practice Problems

1. One line: define CTE.
2. One line: example of a funnel.
3. One line: criterion for a metric definition.

## Wrap-up and Next Steps

The strongest answers in SQL interviews feel structured before they feel clever. They define the metric, make the query readable, call out the edge cases, and close with a compact interpretation that points to the next useful question.

The next post applies the same problem-first thinking to machine learning interviews.

## Answering the Opening Questions

- **What do SQL and analytics interviews actually evaluate beyond syntax?**
  - The article treats SQL and Analytics Interviews as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How should you break a business question into query steps?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What are the recurring patterns around JOINs, aggregation, windows, and funnels?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Data Science Career 101 (1/10): What Is a Data Career](./01-what-is-data-career.md)
- [Data Science Career 101 (2/10): Analyst vs Scientist vs Engineer](./02-analyst-scientist-engineer.md)
- [Data Science Career 101 (3/10): Designing the Learning Path](./03-learning-path.md)
- [Data Science Career 101 (4/10): The Data Portfolio](./04-data-portfolio.md)
- **SQL and Analytics Interviews (current)**
- The ML Interview (upcoming)
- The Case Interview (upcoming)
- Settling into the First Data Job (upcoming)
- Building Domain Expertise (upcoming)
- The Path to Senior in Data (upcoming)

<!-- toc:end -->

## References

- [Mode - SQL Tutorial](https://mode.com/sql-tutorial/)
- [LeetCode - Top SQL 50](https://leetcode.com/studyplan/top-sql-50/)
- [PostgreSQL Documentation - Window Functions Tutorial](https://www.postgresql.org/docs/current/tutorial-window.html)
- [Ron Kohavi et al. - Trustworthy Online Controlled Experiments](https://experimentguide.com/)

Tags: DataCareer, SQL, Analytics, Interview, Beginner
