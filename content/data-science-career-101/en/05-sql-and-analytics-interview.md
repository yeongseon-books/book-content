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

Many candidates prepare for SQL interviews as if they were grammar exams. They memorize JOIN types, aggregation syntax, and window functions, but they still struggle once the interviewer asks, "What exactly are you counting?" or "How would you explain this result to a product manager?"

That gap exists because SQL interviews are usually reasoning interviews in disguise. The query matters, but so do the assumptions behind it: the metric definition, the NULL behavior, the time boundary, and the interpretation that turns a result set into an insight.

This is the 5th post in the Data Science Career 101 series.


![data science career 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-science-career-101/05/05-01-concept-at-a-glance.en.png)
*data science career 101 chapter 5 flow overview*
> In SQL interviews, what matters most is not knowing every tool or concept, but asking the right questions at each stage and knowing when you have a good answer.

## Questions to Keep in Mind

- What do SQL and analytics interviews actually evaluate beyond syntax?
- How should you break a business question into query steps?
- What are the recurring patterns around JOINs, aggregation, windows, and funnels?

## What You Will Learn

- Core *SQL* patterns
- Question *decomposition*
- Metric *definition*
- Result *interpretation*
- Mock *practice*

## Why It Matters

SQL is the shared language across most data roles, which is why interviewers use it to observe more than database fluency. They are also watching how you define the metric, whether you surface assumptions, and whether you can tell the difference between "I got a number" and "I understand what this number means."

In practice, many interviews bundle SQL problems with product interpretation questions. The query itself is evaluated alongside what assumptions you stated, how you defined the calculation boundary, and what follow-up validation you proposed after seeing the result. SQL questions are less about syntax and more about question decomposition—a good SQL answer shows you break the problem into smaller steps and explain your reasoning at each stage.

## Key Terms

- **JOIN**: An operation that combines rows from multiple tables based on a matching condition.
- **GROUP BY**: A clause that partitions rows into groups for aggregation (COUNT, SUM, AVG).
- **window function**: A function that performs a calculation across a set of rows related to the current row without collapsing them—useful for running totals, ranks, and moving averages.
- **CTE**: Common Table Expression—a named temporary result set that makes complex queries readable by breaking them into logical steps.
- **funnel**: An analysis pattern that measures conversion rates between sequential steps (e.g., visit → signup → purchase).

## Before/After

**Before**: "When a problem appears, I start with SELECT * and figure it out as I go."

**After**: "I decompose the question into steps, define the metric explicitly, structure the query with CTEs, and close with a one-sentence interpretation."

## Hands-on: Five Question Patterns

Most SQL interview questions follow five recurring patterns. The faster you recognize the pattern, the faster you can plan your solution.

### Step 1 — Single-Table Aggregation

```sql
SELECT date, COUNT(*) AS dau
FROM events
WHERE event = 'login'
GROUP BY date
ORDER BY date;
```

The most basic pattern. You must be able to clearly articulate what you are counting and on what basis you are grouping. Interviewers often follow up with "what is your denominator?" and "how do you handle users who log in multiple times per day?"

### Step 2 — JOIN

```sql
SELECT u.country, COUNT(o.id) AS orders
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.country;
```

In JOIN problems, the join key and NULL handling are evaluated together. You should be able to explain why you chose LEFT JOIN over INNER JOIN—here it preserves countries with zero orders rather than silently dropping them.

### Step 3 — Window Function

```sql
SELECT user_id, amount,
       SUM(amount) OVER (PARTITION BY user_id ORDER BY ts) AS cum
FROM payments;
```

Window functions handle context-aware calculations: running totals, ranks, moving averages. In interviews, explaining the meaning of PARTITION BY and ORDER BY matters more than memorizing syntax. The frame clause (ROWS BETWEEN) is a common follow-up topic.

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

Funnel problems appear frequently in product analytics roles. The conclusion changes significantly depending on how you define each step and how you handle users who appear in later steps without earlier ones.

### Step 5 — One-Sentence Interpretation

```text
"Conversion fell from X to Y, hypothesis Z."
```

The final sentence is what separates a query exercise from an analytics answer. You must state how the number changed and what hypothesis explains it. Without this, the answer is technically correct but professionally incomplete.

## What to Notice in This Code

- CTEs improve readability—they let the interviewer follow your reasoning step by step.
- Metric definition changes the conclusion—different denominators produce different stories.
- Interpretation is the finish line—a query without a concluding sentence is not a complete answer.

Interviewers watch your thinking process alongside your SQL. What assumptions you state, whether you consider time zones, how you handle NULLs—all of these surface during a live coding session.

## Core SQL Interview Problems and Commentary

To maximize preparation efficiency, learn the recurring thinking patterns before increasing problem count. The three problems below appear (in variations) in nearly every SQL interview.

| Problem Type | Example Question | Key Commentary |
| --- | --- | --- |
| Repeat purchase rate | "Calculate the 30-day repeat purchase rate" | Denominator definition, period boundary, duplicate user handling |
| Funnel conversion | "Calculate visit→signup→purchase conversion" | Step definitions, missing-step handling, aggregation unit consistency |
| Cumulative revenue trend | "Show daily cumulative revenue and 7-day moving average" | Window frame setting, missing-date imputation |

The answer structure is always the same: redefine the problem, state the aggregation unit, mention edge cases first, then close with a one-sentence business interpretation. Practicing this flow reduces interpretation errors—which are more costly than syntax mistakes.

## SQL Interview Q&A Samples: Interpreting Question Intent First

SQL interviews are not just about producing correct queries. You must demonstrate that you can identify the question's intent and the data's traps before writing code.

### Question 1

"Calculate the repeat purchase rate for the last 30 days."

- First clarify: definition of "repeat," denominator period, cancelled order handling
- Answer structure: Agree on definition → CTE for intermediate aggregation → Final ratio → Edge case explanation

### Question 2

"Find the top 3 products by revenue per country."

- Key point: Explain why you chose `ROW_NUMBER()` vs `DENSE_RANK()`
- Production considerations: Tie-breaking policy, refund handling, date filter range

This approach ensures that even if you make a minor syntax error, your problem-solving capability is clearly demonstrated.

## Analytics Interview Answer Script: 90-Second Structure

```text
1) Redefine the problem: Translate the request into metric language.
2) Plan approach: State the data needed and verification sequence.
3) Interpret result: Separate the number's meaning from its risks.
4) Propose action: Suggest the next experiment or improvement.
```

The strongest interview answers are not the fastest calculations—they are the ones where interpretation and action are clearly connected. Practicing the 90-second structure stabilizes your delivery under pressure.

## Growth Milestones: Junior to Senior

Preparing for SQL interviews is also a good time to check your long-term growth axis. If you optimize only for passing interviews, you risk short-term thinking. Setting milestones from junior to senior keeps your preparation aligned with career trajectory.

| Stage | Core Competency | Representative Behavior | Output Quality Standard | Signal for Next Stage |
| --- | --- | --- | --- | --- |
| Early Junior | Accurate execution | Follow requirements to analyze/implement | Reproducible results submitted | Error rate decreasing on repeated tasks |
| Mid Junior | Problem decomposition | Turn ambiguous requests into structured questions | Metric definitions and assumptions stated | Independently lead small tasks |
| Mid-Level | Priority judgment | Choose high-impact work from multiple requests | Interpretation and recommendation included | Own quarterly-scope projects |
| Early Senior | Systems thinking | Connect data-product-operations | Proposals include measurement plans | Lead cross-team initiatives |
| Senior+ | Organizational amplification | Drive colleague growth and standardization | Build reusable frameworks | Team-wide speed and quality improvement |

Many people equate "senior" with "knows hard techniques," but actual evaluation splits on responsibility scope and influence style. A junior's strength is accurate execution; a senior's value lies in problem selection and organizational scaling. Even during interview prep, ask yourself: "Which stage's behavior am I demonstrating right now?"

| Monthly Check Item | Verification Question |
| --- | --- |
| Execution quality | Am I reducing the same mistakes? |
| Problem definition | Did I clarify assumptions after receiving a request? |
| Impact measurement | Can I explain results in numbers? |
| Collaboration | Did I align stakeholder expectations proactively? |
| Knowledge sharing | Did I document learnings in a session or doc? |

At each stage, identify one habit to drop. Juniors should drop perfectionism that delays starts. Mid-levels should drop the habit of executing requests as-is without questioning priority. Seniors should drop the instinct to solve everything alone. Growth is not only about adding new skills—it is equally about reducing behaviors that no longer fit your current stage.

## Five Common Mistakes

1. **Overusing SELECT *.** It hides your intent and makes it impossible for the interviewer to see what you actually need.
2. **Ignoring NULL handling.** NULLs propagate silently through aggregations. State your NULL assumption explicitly.
3. **Ignoring time zones.** UTC vs local time changes counts, especially around midnight boundaries.
4. **Vague metric definitions.** "Active users" means nothing without specifying the action, the window, and the deduplication rule.
5. **No interpretation.** A result without a concluding sentence and a proposed next step is an incomplete answer.

## How This Shows Up in Production

Analytics interviews commonly pair one SQL problem with one interpretation or case-style follow-up because real work almost never stops at query execution. In production, the important part is often the sentence after the query: what changed, whether the result is trustworthy, and what should be checked next.

The interview mirrors this reality. Companies want to see that you can move from "here is a number" to "here is what we should do about it" without prompting.

## How a Senior Engineer Thinks

- Define the metric first—before writing any SQL, state what you are measuring and why.
- CTEs are colleague-friendly—readable queries get reviewed faster and break less often.
- Interpretation is the value—the query is infrastructure; the insight is the deliverable.
- Remember NULL—assume it exists until proven otherwise.
- State the time zone—ambiguity here invalidates everything downstream.

## Checklist

- [ ] Can explain the difference between four JOIN types with examples.
- [ ] Solved at least three window function patterns (running total, rank, moving average).
- [ ] Completed one funnel analysis problem end-to-end.
- [ ] Practiced one-sentence interpretation for every query result.
- [ ] Practiced the 90-second answer structure at least three times.

## Practice Problems

1. Define CTE in one sentence, including when you would use one vs. a subquery.
2. Give one example of a funnel analysis and state what the conversion drop tells you.
3. State one criterion for a well-defined metric (hint: think about the denominator).

## Wrap-up and Next Steps

The strongest answers in SQL interviews feel structured before they feel clever. They define the metric, make the query readable, call out the edge cases, and close with a compact interpretation that points to the next useful question. Interview preparation and long-term career growth are not separate activities—the way you solve today's analysis problem is already shaping your senior-level behavior tomorrow.

The next post applies the same problem-first thinking to machine learning interviews.

## Answering the Opening Questions

- **What do SQL and analytics interviews actually evaluate beyond syntax?**
  - They evaluate question decomposition, assumption clarity, metric definition precision, NULL/timezone awareness, and the ability to interpret results as business recommendations—not just query correctness.
- **How should you break a business question into query steps?**
  - Redefine the question in metric language, identify the aggregation unit and denominator, plan CTEs for each logical step, handle edge cases explicitly, then close with interpretation.
- **What are the recurring patterns around JOINs, aggregation, windows, and funnels?**
  - Single-table aggregation (what/how to count), JOINs (key selection + NULL behavior), window functions (context-preserving calculations), and funnels (step definition + conversion measurement). Each pattern has a standard answer structure: define → query → validate → interpret.
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
