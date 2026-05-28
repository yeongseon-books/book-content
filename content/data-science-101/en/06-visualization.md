---
series: data-science-101
episode: 6
title: "Data Science 101 (6/10): Visualization"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - DataScience
  - Visualization
  - Matplotlib
  - Seaborn
  - Beginner
seo_description: A practical map from message to chart — distributions, comparisons, trends, relations, and parts of a whole, with rules that keep them honest
last_reviewed: '2026-05-15'
---

# Data Science 101 (6/10): Visualization

Charts are not the decorative end of analysis. They are the moment when your conclusions become fast enough for other people to consume. A good chart compresses a page of explanation into one glance. A bad chart makes a bad decision look reasonable.

That is why visualization is really about judgment, not software. The core skill is picking a visual form that matches the message, then removing the distortions that exaggerate or hide what the data is actually saying.

This is the 6th post in the Data Science 101 series. In this chapter, we connect common analytical messages to chart choices, and we treat axes, color, labels, and annotations as decision-support tools rather than styling details.


![data science 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/06/06-01-concept-at-a-glance.en.png)
*data science 101 chapter 6 flow overview*
> At its core, Visualization is about deciding what enters a system, where validation happens, and which signals stay for the next cycle—not about feature names.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Visualization?
- Which signal should the example or diagram make visible for Visualization?
- What failure should be prevented first when Visualization reaches a real system?

## Questions This Post Answers

- How do you choose a chart from the message instead of from habit?
- Which chart choices most often create misleading comparisons or trends?
- Why do axis scale, labels, and annotations change the decision a chart supports?
- How can one chart remain readable and honest for more than one audience?

> The right chart is the one that makes the intended decision easier without exaggerating the pattern.

## What You Will Learn

- A mapping from *5 messages* to *5 charts*
- Basic rules for *axis, color, labels*
- Patterns that *mislead* the reader
- A 5-step visualization exercise
- Five common pitfalls

## Why It Matters

Data is fastest to read as a *picture*. The wrong chart leads to the *wrong decision*. A clear *message-to-chart* mapping eliminates *half* of the misreadings.

> *Visualization is the *last line* of an analysis.*

The key boundary in this episode is between the concept itself and how it operates in a real system. You need to know where the data comes in, where the decision happens, and what signal must be recorded.

## Key Terms

- **Encoding**: mapping data to *position, length, color*.
- **Scale**: *linear, log* — the axis transform.
- **Faceting**: *small multiples* for comparison.
- **Annotation**: *notes and highlights* on the chart.
- **Colorblind-safe**: a palette that works for color-vision deficiencies.

## Before / After

**Before**: a *3D pie chart* makes proportions *impossible to compare*.

**After**: a *horizontal bar chart* makes them *exactly comparable*.

## Hands-on: 5-step Visualization

### Step 1 — Distribution (histogram)

```python
import matplotlib.pyplot as plt
df["amount"].plot.hist(bins=30, title="amount distribution")
plt.show()
```

### Step 2 — Comparison (bar)

```python
(
    df.groupby("country")["amount"]
      .sum()
      .sort_values()
      .plot.barh(title="revenue by country")
)
plt.show()
```

### Step 3 — Trend (line)

```python
df.groupby("order_date")["amount"].sum().plot(title="daily revenue")
plt.show()
```

### Step 4 — Relation (scatter + facet)

```python
import seaborn as sns
sns.relplot(
    data=df.sample(2000),
    x="quantity",
    y="amount",
    col="country",
    col_wrap=3,
)
```

### Step 5 — Annotation and color

```python
ax = df.groupby("order_date")["amount"].sum().plot()
ax.axvline(pd.Timestamp("2026-04-01"), color="red", linestyle="--", label="campaign")
ax.legend()
```

**Expected output:** a first-pass chart choice tied to the message, plus the annotation points needed to keep the chart honest.

## What to Notice in This Code

- The *message-to-chart* mapping comes *first*.
- The *axis scale* changes the *reading*.
- *Annotations* save the reader from a paragraph of explanation.

## Five Common Mistakes

1. **Using *3D charts*.** Comparisons become *hard*.
2. **Overusing *dual axes*.** A common source of *misreading*.
3. **Encoding categories *only by color*.** Unfriendly to *colorblind* users.
4. **Bar charts that don't start at *zero*.** They *exaggerate* differences.
5. **Charts without *labels*.** Not reusable next week.

## How This Shows Up in Production

Analysts mix *Tableau / Looker* dashboards with *Python* charts. A *dashboard* is the standard *unit of a weekly report*.

## How a Senior Engineer Thinks

- Write the *message first*, then pick the *chart*.
- Always fill in *axis and labels*.
- Default to a *colorblind-safe palette*.
- Use *annotations* to provide *context*.
- A dashboard should reach a *decision* within *3 screens*.

## Checklist

- [ ] I know the *5 message-to-chart* pairings.
- [ ] I value *axis and labels*.
- [ ] I know *colorblind-safe* palettes.
- [ ] I add *annotations* to aid interpretation.

## Practice Problems

1. Plot the *same data* with *3 different charts* and pick the clearest.
2. Take a *misleading* chart and *fix* it.
3. Sketch a *one-page dashboard* using *3 charts*.

## Wrap-up and Next Steps

Visualization is the *bridge from analysis to decision*. Next we move into *modeling* — using data to *predict*.

## Answering the Opening Questions

- **Which chart should you use for which message?**
  - If the message is about distribution, use histograms; comparisons, `plot.barh`; trends, line charts; relationships, `sns.relplot` or scatter plots. This article was structured to build the habit of choosing charts by the question you want to answer, not the data type.
- **Why do some graphs aid understanding while others create misunderstanding with the same data?**
  - Even the same proportion data becomes hard to compare in a 3D pie chart due to area and perspective distortion, while switching to a horizontal bar chart makes length differences immediately readable. Charts themselves change data interpretation rules, so incorrect encoding creates misunderstanding even without hiding facts.
- **Why are axes, colors, and labels core design elements rather than minor decoration?**
  - Context annotations like `ax.axvline(pd.Timestamp("2026-04-01"), ...)` are needed to read pre/post campaign context, and colorblind-safe palettes with labels are needed to reliably distinguish categories. A chart's message is completed not by data points alone but by axis scale, legend, and text annotations combined.
<!-- toc:begin -->
## In this series

- [Data Science 101 (1/10): What Is Data Science?](./01-what-is-data-science.md)
- [Data Science 101 (2/10): Turning a Problem into a Data Problem](./02-problem-to-data-problem.md)
- [Data Science 101 (3/10): Data Collection](./03-data-collection.md)
- [Data Science 101 (4/10): Data Cleaning](./04-data-cleaning.md)
- [Data Science 101 (5/10): Exploratory Data Analysis](./05-exploratory-data-analysis.md)
- **Visualization (current)**
- Modeling (upcoming)
- Evaluation (upcoming)
- Result Interpretation (upcoming)
- End-to-End Data Project Flow (upcoming)

<!-- toc:end -->

## References

- [matplotlib — Tutorials](https://matplotlib.org/stable/tutorials/index.html)
- [seaborn — Tutorial](https://seaborn.pydata.org/tutorial.html)
- [Cole Knaflic — Storytelling with Data](https://www.storytellingwithdata.com/)
- [Tableau — Visual Best Practices](https://www.tableau.com/learn/articles/data-visualization-tips)

Tags: DataScience, Visualization, Matplotlib, Seaborn, Beginner
