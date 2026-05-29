---
series: data-science-career-101
episode: 3
title: "Data Science Career 101 (3/10): Designing the Learning Path"
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
  - LearningPath
  - SQL
  - Python
  - Beginner
seo_description: A beginner-friendly tour of a 12-week learning roadmap for data roles.
last_reviewed: '2026-05-14'
---

# Data Science Career 101 (3/10): Designing the Learning Path

Many beginners do not fail because they study too little. They fail because they study in a way that never compounds. A course here, a notebook there, a few SQL exercises over the weekend—effort accumulates, but the path does not, so it becomes hard to tell what is foundational and what is optional.

In data work, sequence matters. If you jump into modeling before you are comfortable with SQL, data cleaning, and basic statistics, you end up building on a surface that cannot support the kinds of questions interviews and real projects actually ask.

This is the 3rd post in the Data Science Career 101 series.


![data science career 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-science-career-101/03/03-01-concept-at-a-glance.en.png)
*data science career 101 chapter 3 flow overview*
> In learning structure, what matters most is not knowing every tool or concept, but asking the right questions at each stage and knowing when you have a good answer.

## Questions to Keep in Mind

- What should a beginner learn first, and what can wait?
- Why is a 12-week roadmap a more useful frame than a loose reading list?
- What outcomes should each four-week phase produce?

## What You Will Learn

- A *12-week roadmap*
- *Fundamentals* (4 weeks)
- *Analytics* (4 weeks)
- *Modeling* (4 weeks)
- *Weekly review*

## Why It Matters

Random study usually produces random confidence. You touch many topics, but you cannot tell which ones you can actually use.

An ordered path gives you something more valuable than motivation: it gives you checkpoints. You know when to move from syntax to analysis, when to build a small project, and when to pause and correct the pace instead of just collecting more material.

The first 12 weeks matter more than the next 12 months. By pacing basics, analytics, and modeling in order—and leaving a small artifact each week—you build both skill and confidence.

Data roles require SQL, Python, statistics, visualization, experimentation, and modeling. That is a long list. Get the sequence wrong and the perceived difficulty spikes—not because the material is harder, but because you lack the prerequisite vocabulary to decode it. The principle is simple: "what order you build in" matters more than "how much you build."

## Key Terms

- **fundamentals**: Core building blocks—Python, SQL, descriptive statistics.
- **analytics**: Question-driven analysis—reading and interpreting data around a specific business question.
- **modeling**: Predictive modeling—regression, classification, and evaluation metrics.
- **product sense**: The ability to read how a result affects users and the product.
- **retro**: A periodic reflection exercise where you identify what worked, what did not, and what to change next.

## Before/After

**Before**: "I just buy books and stall. Three months in, I cannot tell what I actually know."

**After**: "A 12-week roadmap with weekly artifacts. Each week has a concrete output, so I know exactly where I am and what comes next."

## Hands-on: 12-Week Learning Path

Block out 12 weeks on a calendar. Each week has a specific output: a small script, a dashboard, a written analysis. The output is proof—not proof that you consumed content, but proof that you can produce something from it.

### Step 1 — Fundamentals (Weeks 1-4)

```text
- Python syntax, pandas
- SQL JOIN, GROUP BY
- Statistics basics (mean, variance, p-value)
- Visualization (matplotlib)
```

The first four weeks are not glamorous. That is fine. Skipping this phase is the single most expensive mistake beginners make. Every modeling concept you encounter later assumes you can write a query, manipulate a DataFrame, and reason about distributions. If you cannot, you spend modeling time re-learning basics under pressure.

### Step 2 — Analytics (Weeks 5-8)

```text
- Data cleaning
- A/B test design
- One dashboard
- One case study
```

In the analytics phase, the shift is from "running code" to "answering questions." You practice structuring a question, choosing the right metric, slicing by segment, and writing a one-paragraph interpretation. This is the phase where communication skill starts compounding alongside technical skill.

### Step 3 — Modeling (Weeks 9-12)

```text
- One regression, one classification
- scikit-learn pipeline
- Model evaluation metrics
- One mini project
```

Modeling builds on top of fundamentals and analytics. At this stage, the habit that matters most is not tuning hyperparameters—it is defining the problem clearly, choosing an appropriate baseline, and explaining why a given metric is the right one to optimize. Model scores without interpretation have no portfolio power.

### Step 4 — Weekly Artifact

```markdown
- README
- Data source
- Code
- Result
- Retro
```

A weekly artifact is not "I studied." It is "I produced." The difference matters because artifacts become portfolio material, and portfolio material is what hiring managers can actually evaluate. Each artifact should be self-contained: someone unfamiliar with your context should be able to read the README and understand what you did and why.

### Step 5 — Retro Template

```text
What went well / Improve / Next
```

A retro is not a motivational exercise. It is a direction-correction device. What went well tells you what to keep. What to improve tells you where the bottleneck is. Next tells you the single most important action for the coming week. Keep it short—three sentences is enough—but do it every week without exception.

## What to Notice in This Code

- Weekly artifacts are progress evidence.
- Fundamentals carry modeling—without them, modeling concepts do not stick.
- Retros close the loop and prevent the same mistake from repeating.

Beginners often start with models because they seem more impressive. But the place where people actually get stuck in practice is SQL, data cleaning, and basic statistics. Skipping fundamentals is slower, not faster.

## Portfolio Project Types and Selection Criteria

The hardest question during a learning path is "what should I build?" Many beginners pick high-difficulty projects, but evaluators look for completeness and clear problem definition before they look for complexity. The table below maps project types directly to target roles.

| Project Type | Target Role | Core Question | Recommended Output | Minimum Validation |
| --- | --- | --- | --- | --- |
| Funnel/cohort analysis | Analyst | Where does conversion drop? | SQL queries, dashboard, interpretation memo | Metric definitions and segment comparison included |
| A/B test analysis | Analyst/Scientist | Is the change statistically significant? | Experiment design doc, result interpretation | Assumptions/limitations/next actions stated |
| Demand forecasting model | Scientist | How well can we predict the next period? | Model code, feature explanation, error analysis | Improvement over baseline quantified |
| Churn prediction model | Scientist/MLE | Which users are at high churn risk? | Classification model, threshold strategy | Precision-recall tradeoff explained |
| ELT pipeline build | Engineer | Is ingestion and transformation stable? | DAG, data model doc, quality checks | Rerunnable with failure recovery documented |
| Recommendation serving PoC | MLE | Can we serve predictions as a service? | Inference API, monitoring metrics | Latency, error rate, deployment procedure |

A common mistake in project selection is choosing topics based on "tech trends." Trends are not irrelevant, but at the beginner level, data source reliability, reproducibility, and question specificity matter far more. A cohort analysis project built on public data can send a clearer hiring signal than a complex deep-learning project that cannot be reproduced.

When turning a project into portfolio-grade work, use this composition checklist:

| Item | Must Include | Common Omission |
| --- | --- | --- |
| Problem definition | Why this problem, whose decision it serves | Writing a tech intro instead of a problem statement |
| Data description | Source, time range, preprocessing criteria | No documentation of missing-value or outlier handling |
| Approach | Why this method was chosen | Single method with no alternative comparison |
| Result interpretation | What the numbers mean, business implication | Performance numbers with no interpretation |
| Reproduction | Run command, dependencies, folder structure | Repository that cannot actually be executed |

Project difficulty is best measured by "decision connectivity"—can you read the result and recommend a next action? If yes, it is a strong project regardless of model complexity. If the model score is high but you cannot say what should change, the portfolio signal is weak.

Connecting this to the 12-week roadmap: weeks 1-4 are ideal for SQL and data-cleaning projects, weeks 5-8 for experimentation or basic model projects, weeks 9-12 for reproducibility and documentation polish. Do not run three projects in parallel. Finish one end-to-end first. The experience of completion compounds into the quality of the next project.

## Five Common Mistakes

1. **Reading a book cover-to-cover before starting.** You learn by producing, not by consuming. Start building in week one.
2. **Starting from models.** Models without data intuition produce numbers you cannot interpret. The dependency chain exists for a reason.
3. **No artifacts.** If there is no output, there is no evidence. Growth without evidence is invisible to everyone, including yourself.
4. **Skipping retros.** Without retros, you repeat the same inefficiencies every week. Three sentences once a week prevents drift.
5. **Switching tools frequently.** Mastery requires depth in one stack before breadth across many. Pick Python + SQL and stay there for 12 weeks.

## How This Shows Up in Production

Most bootcamps and internal training programs follow some version of this progression because the dependency chain is hard to escape: fundamentals first, analysis second, modeling third, product judgment throughout.

The exact tools vary, but the structure holds because real work still depends on being able to query data, clean it, explain it, and only then decide whether a model is even the right move. Companies with mature data teams often onboard new hires with a 4-week ramp that mirrors the fundamentals phase—metric definitions, key dashboards, core queries—before assigning independent analysis work.

## Skill Assessment Matrix: Turning Self-Diagnosis into Numbers

After completing the 12-week roadmap, the next question is not "what should I study more?" but "which skills are still weak?" A self-assessment matrix makes the answer concrete.

| Competency Area | 1-Point Baseline | 3-Point Baseline | 5-Point Baseline |
| --- | --- | --- | --- |
| SQL | Basic SELECT queries | Window functions and CTEs for problem-solving | Performance and data integrity explanation |
| Statistics | Terminology understood | Experiment design possible | Interpretation risk controlled |
| Python | Notebook-level analysis | Functions and modules | Reproducible pipeline |
| Communication | Results shared | Decision sentence provided | Stakeholder alignment driven |

Score yourself monthly and focus on the two lowest areas only. Trying to raise all areas simultaneously is a strategy that does not sustain. Evidence-based scoring—using actual artifacts rather than gut feeling—makes the matrix useful for interview prep and performance reviews alike.

| Competency Area | Current Level (1-5) | Evidence Artifact | Next 4-Week Action |
| --- | --- | --- | --- |
| SQL problem decomposition | | Query review notes | 2 problems/week + error pattern log |
| Interpretation/storytelling | | One-page analysis memo | Practice summarizing results as recommendation sentences |
| Model evaluation | | Model comparison table | Write improvement rationale vs. baseline |
| Reproducibility/documentation | | README and run scripts | Document failure cases, not just happy path |

The key is evidence-based assessment. "I think I am good at X" is not a plan. "Here is the artifact that proves level 3" is. Updating the same table quarterly gives you a clear growth trajectory you can present in interviews and performance reviews.

## How a Senior Engineer Thinks

- Fundamentals compound over time like interest—early investment pays disproportionately.
- Weekly evidence wins over monthly marathons because consistency beats intensity.
- Retros direct the next week—without them, you optimize by accident.
- Projects integrate isolated skills into a coherent story.
- Sustainment is strategy—the path you can maintain for 12 weeks beats the plan you abandon in 3.

## Checklist

- [ ] 12-week calendar created with specific weekly outputs.
- [ ] Weekly artifact template set up (README, data source, code, result, retro).
- [ ] One end-to-end project selected and scoped.
- [ ] At least four retro checkpoints scheduled.
- [ ] Self-assessment matrix filled for baseline measurement.

## Practice Problems

1. Define "fundamentals" in one sentence, including why the order matters.
2. Give one example of a useful retro insight and the action it would trigger.
3. State one criterion that separates a strong weekly artifact from a weak one.

## Wrap-up and Next Steps

The goal is not to consume the maximum number of resources in 12 weeks. It is to finish the period with a stronger base, a set of reusable artifacts, and at least one small body of work that proves you can turn study into output. The weekly retro is the mechanism that keeps the path self-correcting rather than blindly forward.

The next post shows how those artifacts become a portfolio instead of a pile of disconnected exercises.

## Answering the Opening Questions

- **What should data career beginners learn and in what order?**
  - The core structure is: 4-week foundation (Python, SQL, statistics), 4-week analysis (EDA, dashboards, A/B tests), 4-week modeling (simple models, evaluation), plus weekly retrospectives to close the loop.
- **Why split the 12-week roadmap into foundation, analysis, and modeling phases?**
  - Skipping the foundation phase causes problems later — when you skip stages, problems become harder to analyze and results harder to interpret. The dependency is real: analytics requires fluent data access, and modeling requires analytical judgment.
- **Why are weekly deliverables important?**
  - Tracking visible progress and building habits at each stage makes it easier to move from one phase to the next. Artifacts also serve as portfolio material and provide concrete evidence during interviews.
<!-- toc:begin -->
## In this series

- [Data Science Career 101 (1/10): What Is a Data Career](./01-what-is-data-career.md)
- [Data Science Career 101 (2/10): Analyst vs Scientist vs Engineer](./02-analyst-scientist-engineer.md)
- **Designing the Learning Path (current)**
- The Data Portfolio (upcoming)
- SQL and Analytics Interviews (upcoming)
- The ML Interview (upcoming)
- The Case Interview (upcoming)
- Settling into the First Data Job (upcoming)
- Building Domain Expertise (upcoming)
- The Path to Senior in Data (upcoming)

<!-- toc:end -->

## References

- [Mode - SQL Tutorial](https://mode.com/sql-tutorial/)
- [pandas documentation - User Guide](https://pandas.pydata.org/docs/user_guide/index.html)
- [scikit-learn - User Guide](https://scikit-learn.org/stable/user_guide.html)
- [Ron Kohavi et al. - Trustworthy Online Controlled Experiments](https://experimentguide.com/)

Tags: DataCareer, LearningPath, SQL, Python, Beginner
