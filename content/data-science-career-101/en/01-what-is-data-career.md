---
series: data-science-career-101
episode: 1
title: "Data Science Career 101 (1/10): What Is a Data Career"
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
  - Analyst
  - Scientist
  - Engineer
  - Beginner
seo_description: Identify core data roles including analyst, scientist, and engineer while exploring entry paths and essential skills for a data science career.
last_reviewed: '2026-05-14'
---

# Data Science Career 101 (1/10): What Is a Data Career

When people first look into data careers, the landscape often feels flatter than it really is. Job boards list analyst, scientist, engineer, analytics engineer, and ML engineer side by side, but they rarely explain which questions each role owns or what kind of evidence each role is expected to produce.

That ambiguity matters early. If you cannot tell whether a team mainly values business interpretation, experimentation, data modeling, or production pipelines, it becomes easy to study the wrong things, build the wrong portfolio, and apply for titles that sound right but do not match the work you actually want.

This is the first post in the Data Science Career 101 series.

What makes it worse is that even within the same company, data role definitions vary from team to team. Some teams have analysts running experiment design; others have engineers owning metric tables end to end. So the safest early heuristic is to read the landscape by question, deliverable, and collaborator — not by title.


![data science career 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-science-career-101/01/01-01-concept-at-a-glance.en.png)
*data science career 101 chapter 1 flow overview*
> In data career, what matters most is not knowing every tool or concept, but asking the right questions at each stage and knowing when you have a good answer.

## Questions to Keep in Mind

- What roles are usually grouped together when people say "data career"?
- Why is it safer to distinguish data jobs by responsibility and deliverable than by title alone?
- What do analyst, scientist, engineer, ML engineer, and analytics engineer each optimize for?

## What You Will Learn

- The data career landscape
- Five major roles
- Core skills that separate them
- Entry paths
- Common misconceptions

## Why It Matters

The same dataset leads to very different expectations depending on the role around it.

An analyst may be asked to define a metric and explain a drop in conversion. A scientist may need to frame that same change as a hypothesis and test it. An engineer may care more about whether the underlying event table is complete, trustworthy, and fresh enough to support either of those conversations. The earlier you see those differences, the easier it becomes to make deliberate learning trade-offs.

For example, whether you should go deeper on SQL, practice modeling first, or focus on dashboard and metric design all depends on the role you are aiming for. Establishing this criterion early saves study time and sharpens your portfolio direction.

## Key Terms

- **data analyst**: interprets data to help teams make faster, better decisions.
- **data scientist**: converts questions into hypotheses and validates them with experiments and models.
- **data engineer**: builds the pipelines and storage structures that keep data flowing reliably.
- **ML engineer**: trains, deploys, and monitors models as production systems.
- **analytics engineer**: creates reliable, reproducible analytics models between analysts and engineers.

## Before/After

**Before**: "I thought data work meant statistics only."

**After**: "I can distinguish five roles by their purpose and deliverables."

## Hands-on: One-Liner per Role

As a beginner, the simplest way to start thinking about roles is to ask: what problem does each role own?

### Step 1 — Analyst

```text
Drives decisions with SQL and dashboards.
```

An analyst interprets data to speed up the team's judgment. That is why SQL, metrics, and dashboards become the central tools.

### Step 2 — Scientist

```text
Tests hypotheses with experiments and models.
```

A scientist converts questions into hypotheses and validates them with experiments and models. Both explanatory power and verifiability are expected.

### Step 3 — Engineer

```text
Builds pipelines and storage as data infrastructure.
```

An engineer builds the foundation for data to flow reliably. When pipeline and schema quality breaks down, every other role shakes with it.

### Step 4 — ML Engineer

```text
Trains, deploys, and monitors models.
```

An ML engineer treats models not as research subjects but as operational systems. The ability to see training, deployment, and monitoring as one integrated system is key.

### Step 5 — Analytics Engineer

```text
Builds reliable analytics models with dbt and friends.
```

An analytics engineer sits between analysts and engineers, building reproducible and consistent analytical foundations. Think of it as the role that raises metric trust.

## What to Notice in This Code

- Look at responsibilities, not titles.
- Definitions vary by company — same title, different scope.
- Boundaries blur in practice.

The most common blind spot for beginners is confusing tools with purpose. Using SQL does not make everyone an analyst, and using Python does not make everyone a modeling-focused practitioner. Which questions you own and which results you leave behind is far more fundamental.

## Five Common Mistakes

1. **Judging by job title alone.**
2. **Learning every tool at once.**
3. **Memorizing tools without context.**
4. **Ignoring the business domain.**
5. **Skipping measurement and verification.**

## How This Shows Up in Production

Large organizations usually separate Analyst, Scientist, ML Engineer, and Analytics Engineer much more clearly because the volume of data, the number of stakeholders, and the cost of ambiguity are all higher.

Smaller teams often combine two or three of these responsibilities into one role. Even then, the distinction still matters. The title might say "data scientist," but the day-to-day work may still lean toward analytics, experimentation, pipeline ownership, or model operations. That is why reading actual responsibilities is safer than reading titles at the entry stage.

## How a Senior Engineer Thinks

- Question first — data is the means, not the end.
- Measurable outcomes must exist for work to be complete.
- Domain understanding creates leverage on the same data.
- Connecting roles yields larger impact than optimizing one.
- Understanding problem structure is what sustains a long career.

## Checklist

- [ ] I can distinguish the five major roles.
- [ ] I picked one area that interests me most.
- [ ] I listed the basic tools for each role.
- [ ] I reserved one week of exploration time.

## Practice Problems

1. Define data analyst in one line.
2. Write one line describing what an analytics engineer does.
3. Summarize the difference between ML engineer and data scientist in one line.

## Wrap-up and Next Steps

The first useful mental shift is to stop treating "data" as a single job family with one skill checklist. Different roles use overlapping tools, but they create value in different ways, leave different deliverables behind, and are judged by different success metrics.

The next post compares analyst, scientist, and engineer directly so you can see those differences in a more concrete side-by-side format.

## Data Role Comparison Table: DA / DE / DS / MLE at a Glance

The most helpful learning at the entry stage is not memorizing more tools — it is comparing roles along the same axes. Even when everyone uses SQL, the questions differ. Even when everyone uses Python, the deliverables and validation criteria differ. The table below compares Data Analyst (DA), Data Engineer (DE), Data Scientist (DS), and ML Engineer (MLE) through one consistent frame so you can anchor your career decision.

| Dimension | DA (Data Analyst) | DE (Data Engineer) | DS (Data Scientist) | MLE (ML Engineer) |
| --- | --- | --- | --- | --- |
| Core question | What happened, and why? | Does data flow reliably? | Which hypothesis holds? What can we predict? | Does the model run stably in production? |
| Key deliverable | Dashboard, analysis report, KPI definition | Data pipeline, table schema, quality monitoring | Experiment results, model prototype, feature analysis | Inference API, deployment pipeline, monitoring dashboard |
| Primary collaborators | PM, marketing, business team | Backend, platform, analytics team | PM, research, analysts | Backend, platform, data scientists |
| Success metric | Decision adoption rate, analysis reuse rate | Pipeline stability, latency, data quality | Experiment reliability, model performance, insight adoption | Serving stability, latency, performance maintenance |
| Failure pattern | Ambiguous metric definition, missing interpretation | Poor schema management, insufficient automation | Overfitting, leakage, missing business context | Train-serve skew, no drift response |
| Early learning priority | SQL, metric design, storytelling | SQL, data modeling, orchestration | Statistics, experiment design, model evaluation | Serving architecture, deployment, monitoring |

The key point when reading this table is not "which role is senior to which" but "which problem do I want to keep solving?" If you are drawn to interpreting numbers and driving decision meetings, the DA axis fits. If you find yourself energized by making sure data flows without breaking, the DE axis is more natural. DS centers on hypothesis-driven thinking; MLE centers on managing models as production systems.

One frequently missed point: early in your career, roles tend to blur. In small organizations, a DA might handle experiment analysis, or a DS might own simple deployments. What matters then is tracking which axis your work is building competency in. Your title may be one thing, but actual effort might split DA 60 / DS 40. The blend itself is fine — the risk is when your long-term direction and the competency you are accumulating diverge.

Here is one actionable approach. First, list everything you did in the past four weeks and classify each item into the four role axes in the table above. Second, separate the axis where you spent the most time from the axis where you felt the most energy. Third, realign your next eight weeks of study toward the axis that gives you energy. For example, if you lean MLE, shifting from model experimentation toward serving-latency measurement and deployment automation practice is more effective.

Finally, this table is a powerful frame for interview preparation as well. "I can use SQL" is far less convincing than "from the DA perspective I focus on metric definition and interpretation; from the DE perspective I also verify data consistency." Speaking in role language — responsibilities instead of tools — raises persuasion dramatically. The first button of a data career is learning that responsibility language quickly.

## Execution Framework: Weekly Check Template

This section converts the concepts above into action. Many readers feel they understand while reading but stall at execution a week later because the "next action" was never pinned down in writing. The frame below connects learning, practice, and reflection as a minimum repeatable unit.

First, write this week's goal in one sentence. The goal should be problem-based, not tool-based. "Study SQL window functions" is weaker than "calculate cumulative payments per user to find churn signals." Problem-centered goals naturally extend into result interpretation even in the same time window.

Second, distinguish input from output clearly. Input is the material you use — data, logs, documents, interview notes. Output is what someone else can review — queries, analysis notes, comparison tables, decision documents. Gathering input is not the same as producing output, and growth speed correlates more strongly with output frequency.

Third, write judgment criteria in advance. Many tasks wobble at the end because success criteria were never agreed upfront. Replace "is it accurate?" with checkable questions: "is the denominator definition clear?", "are any segments missing?", "is there a follow-up action?" Quality stabilizes when you think in checklist form.

Fourth, share work in small increments. The habit of showing only finished work delays feedback. Sharing mid-stage results as a one-page summary, with assumptions and risks exposed first, drastically cuts downstream rework. Data roles are stronger long-term when you align quickly on assumptions rather than building alone until perfection.

Fifth, make retrospectives decision records, not feelings journals. Don't end with "it was hard." Write what the bottleneck was, what sequence you would try next time, which metric to add. When you encounter the same problem type again, past records become instant templates, and growth accelerates.

The table below is a minimum operational template you can repeat weekly.

| Item | Guiding Question | Example Output |
| --- | --- | --- |
| Goal | What problem am I solving this week? | 3-line problem definition |
| Input | What data/materials will I use? | Source list |
| Method | What sequence will I follow? | Step checklist |
| Validation | What counts as success? | Quality checklist |
| Result | What changed? | One-sentence recommendation |
| Retro | What will I change next week? | 3 improvement actions |

The point of this template is not perfection but repeatability. You do not need to produce a massive document each time. What matters is leaving the same structure every week so you can compare. Once comparison is possible, growth becomes measurable, and measurable growth raises the quality of career decisions.

## Monthly Review Questions

Below are five questions you can use verbatim in an end-of-month retrospective. First: "What problem did I solve this month, and whose decision did it influence?" Second: "Can a colleague verify the reproducibility of my deliverable?" Third: "Did I summarize the result as a one-sentence recommendation?" Fourth: "Did I propose an alternative path in case my assumptions were wrong?" Fifth: "What will I not do next month?"

Repeating these five questions monthly keeps learning and execution from splitting apart. The last question is especially effective at reducing overload. Career growth does not come only from doing more. It accelerates when you clarify priorities and intentionally drop less important work.

| Question | Pass Criterion |
| --- | --- |
| Is the problem definition clear? | Stakeholders can explain it in the same sentence |
| Is the result reproducible? | Execution commands and data criteria are documented |
| Does interpretation connect to action? | At least one follow-up action stated |
| Were risks addressed proactively? | Assumptions and limitations documented together |
| Is next month's priority visible? | To-do / not-to-do lists separated |

## Job Posting Reading Practice: Decomposing Role Signals

At the entry stage, reading many job postings without knowing which signals matter means the effort never connects to a learning plan. So when reading postings, extracting problem type, deliverable, collaborator, and success metric — rather than counting technology keywords — is more effective. Translating posting sentences into role language (as in the table below) makes it easy to compare actual responsibilities even when titles differ.

| Posting Sentence | Hidden Role Signal | Preparation Action |
| --- | --- | --- |
| "Design business metrics and operate dashboards" | Analyst-focused | Write 1 metric definition doc + dashboard interpretation note |
| "Stabilize data pipelines and quality monitoring" | Engineer-focused | Document 5 data quality check rules |
| "Experiment design and model performance improvement" | Scientist or MLE-focused | Practice mock answers using hypothesis-metric-validation template |

Execution tip: this week, pick 5 postings, fill the table, and for each one write one line of "evidence I can show immediately." For an Analyst posting, that might be a cohort analysis link; for an Engineer posting, a pipeline re-run procedure document. Repeating this exercise shifts you quickly from tool-list self-introductions to responsibility-centered self-introductions.

## Career Map: Anchoring Your Starting Point with a Role-Capability Matrix

Starting to study based on job names alone makes it easy to lose direction within a month. That is why anchoring your starting point in sentences matters in this first article. The matrix below is a tool for quickly checking role fit based on "what problems do I want to solve?"

| Problem Interest | Best Starting Role | Early Evidence Deliverable | 8-Week Study Priority |
| --- | --- | --- | --- |
| Metric interpretation and decision support | Data Analyst | KPI definition doc, cohort analysis note | SQL, metric design, storytelling |
| Data flow stabilization | Data Engineer | Pipeline re-run procedure doc | Data modeling, quality rules |
| Hypothesis validation and prediction | Data Scientist | Experiment report, model comparison table | Statistics, experiment design, evaluation |
| Model operations and deployment | ML Engineer | Inference API demo, monitoring table | Serving, deployment, observability |

After filling this table, separate "what I am good at" from "what I want to keep doing." Being good at something generates short-term results; wanting to keep doing something determines long-term career direction. Acknowledging early that these two axes may differ drastically cuts the cost of direction changes later.

## Resume Template: One Page in Responsibility Language

A data role resume should lead with responsibility sentences, not tool lists. The template below is a one-page structure beginners and juniors can use immediately.

```text
[Summary]
- I structure business questions as data problems and connect them to reproducible analysis results.

[Core Capabilities]
- SQL: aggregation, window functions, metric validation
- Python: data cleaning, EDA, visualization
- Communication: translating analysis results into decision sentences

[Key Project]
- Problem: identify cause of payment conversion decline
- Approach: funnel decomposition + segment comparison + anomaly validation
- Result: pinpointed churn segment, proposed 2 experiments, reflected in weekly metrics

[Collaboration Style]
- Align with PM/marketing/engineering on hypothesis-metric-experiment criteria
```

The core principle: leave behind not "what I learned" but "what problem I solved, how, and what decision it enabled." Rewriting sentences through this template makes even the same experience communicate far more clearly.

## Practical Appendix: Preparing Application Docs and Interview Answers as One Set

To turn reading comprehension into actual career action, your resume sentences, portfolio evidence, and interview answers must all point at the same problem. The structure below is the preparation method that produces the fastest results for entry-level and junior data practitioners.

### Resume Bullet Template

```text
- [Problem] What business or operational problem did you own?
- [Action] What data approach (metric/experiment/pipeline/model) did you apply?
- [Result] What improved, by how much?
- [Impact] How did that result influence team decisions?
```

Example sentence: "Decomposed payment funnel churn by cohort, identified the primary bottleneck, reprioritized onboarding experiments, and improved conversion within 4 weeks." The key: leave responsibility and result in sentences, not technology names.

### Portfolio Project Selection Check

| Check Item | Pass Criterion |
| --- | --- |
| Problem clarity | Can explain problem and impact scope in one sentence |
| Data realism | Even with public data, missing values/bias/limits documented |
| Reproducibility | Execution steps and validation criteria stated in README |
| Decision connection | Result leads to a next action |

Using this table to select projects reduces "show-off analysis" and leaves "real-world problem solving" instead.

### Interview Q&A 3-Sentence Frame

1. State how you defined the problem.
2. Explain what approach you chose and why.
3. Describe the result and its limitations, then propose a next action.

Answering in these three sentences quickly surfaces the judgment process interviewers care most about. Stating limitations proactively raises trust.

### Capability Check Matrix

| Area | Current Level (1–5) | Target Level (1–5) | Next 2-Week Action |
| --- | --- | --- | --- |
| Problem definition |  |  |  |
| Data processing |  |  |  |
| Validation design |  |  |  |
| Communication |  |  |  |
| Collaboration ops |  |  |  |

Filling this table once a month turns growth perception from feeling into record. The quality of career decisions ultimately rises from the quality of records.

## Answering the Opening Questions

- **What roles actually fall under "data jobs"?**
  - The article distinguished five roles — analyst, scientist, engineer, ML engineer, and analytics engineer — and clarified what questions each answers and what deliverables each produces.
- **Why should you distinguish roles by responsibilities and deliverables rather than job titles?**
  - Job titles alone don't reveal the role. Even within the same company, definitions differ, so you must look at responsibilities and deliverables.
- **What are the five core roles a beginner should distinguish first?**
  - Mapping the five roles introduced in this article to their core tools helps beginners set a learning direction.
<!-- toc:begin -->
## In this series

- **What Is a Data Career (current)**
- Analyst vs Scientist vs Engineer (upcoming)
- Designing the Learning Path (upcoming)
- The Data Portfolio (upcoming)
- SQL and Analytics Interviews (upcoming)
- The ML Interview (upcoming)
- The Case Interview (upcoming)
- Settling into the First Data Job (upcoming)
- Building Domain Expertise (upcoming)
- The Path to Senior in Data (upcoming)

<!-- toc:end -->

## References

- [Google Career Certificates - Google Data Analytics Professional Certificate](https://grow.google/certificates/data-analytics/)
- [dbt Labs - What Is Analytics Engineering?](https://www.getdbt.com/blog/what-is-analytics-engineering)
- [IBM - What Is a Data Engineer?](https://www.ibm.com/think/topics/data-engineer)
- [Harvard Business Review - Data Scientist: The Sexiest Job of the 21st Century](https://hbr.org/2012/10/data-scientist-the-sexiest-job-of-the-21st-century)

Tags: DataCareer, Analyst, Scientist, Engineer, Beginner
