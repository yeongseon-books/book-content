---
series: computer-science-major-101
episode: 1
title: "Computer Science Major 101 (1/10): What Computer Science Majors Learn"
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
  - Major
  - Curriculum
  - Career
  - Beginner
seo_description: A beginner-friendly tour of the CS major map covering math, programming, systems, data, AI, and capstone projects.
code_required: false
last_reviewed: '2026-05-14'
---

# Computer Science Major 101 (1/10): What Computer Science Majors Learn

> Computer Science Major 101 series (1/10)

**Core question**: What will you *actually* learn across four years of a CS major?

> Five axes — *math*, *systems*, *data*, *AI*, *projects* — form the *big picture* of the major.

This is the first post in the Computer Science Major 101 series.


![computer science major 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-major-101/01/01-01-major-learning-map.en.png)
*computer science major 101 chapter 1 flow overview*
> The CS major is not a collection of topic names—it is a foundation of *math* and *programming*, layered with *systems*, *data*, *AI*, and *capstone projects*, where each layer depends on what came before.

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Computer Science Majors Learn?
- Which signal should the example or diagram make visible for What Computer Science Majors Learn?
- What failure should be prevented first when What Computer Science Majors Learn reaches a real system?

## What You Will Learn

- The *big picture* of the major
- Weight of *math* and *programming*
- Balance of *systems* and *theory*
- Role of *projects*
- Connection to *career*

## Why It Matters

A clear *map* keeps your *four years* from drifting.

## Concept at a Glance
The six axes—*math*, *programming*, *systems*, *data*, *AI*, and *projects*—build on each other. Each is foundational to the next.
## Key Terms

- **major**: your *primary* field.
- **core course**: *required* class.
- **elective**: *optional* class.
- **track**: *sub-specialty*.
- **capstone**: *graduation* project.

## Before/After

**Before**: You memorize course names.

**After**: You understand each course's *role* and *links*.

## Hands-on: Draw Your Major Map

### Step 1 — Define areas

```python
areas = ["math", "programming", "systems", "data", "ai", "project"]
```

### Step 2 — Place by year

```python
plan = {1: ["math", "programming"], 2: ["systems"], 3: ["data", "ai"], 4: ["project"]}
```

### Step 3 — Distribute credits

```python
credits = {a: 6 for a in areas}
```

### Step 4 — Check balance

```python
total = sum(credits.values())  # 36
```

### Step 5 — Find weak areas

```python
weak = [a for a, c in credits.items() if c < 6]
```

## What to Notice in This Code

- Courses cluster into *areas*.
- *Year order* matters.
- Credit *sums* reveal *balance*.

## Five Common Mistakes

1. **Pushing *required* courses to the *last semester*.**
2. **Picking *only theory or only practice*.**
3. **Underweighting *math* in early years.**
4. **Treating *projects* as just credits.**
5. **Not linking *courses* to a *career path*.**

## How This Shows Up in Production

Job listings are essentially a *combination* of *major courses*.

## How a Senior Engineer Thinks

- *Math* lasts longest.
- *Languages* change.
- *Systems* are foundation.
- *Data* is universal.
- *Projects* are evidence.

## Checklist

- [ ] List your *areas*.
- [ ] Place by *year*.
- [ ] Balance *credits*.
- [ ] Reinforce *weak* areas.

## Practice Problems

1. Define *required course* in one line.
2. Define *track* in one line.
3. State the meaning of a *capstone* in one line.


## How to Actually Read the Curriculum Map

Reading the curriculum properly means moving beyond memorizing course names. The first step is to regroup courses by problem type: math courses teach modeling languages, programming courses teach converting problems into procedures, systems courses teach constraints below the code, data courses teach state design and query cost, and AI courses teach assumptions and generalization.

| Category | Representative courses | Skill to build first | Directly feeds into |
| --- | --- | --- | --- |
| Math foundations | Calculus, Linear Algebra, Discrete Math, Probability | Interpret formulas and decompose assumptions | Algorithms, ML, Computer Graphics |
| Programming foundations | Intro to Programming, OOP, Data Structures lab | Decompose problems into functions and modules | Systems programming, backend projects |
| Systems core | Computer Architecture, OS, Compilers, Networking | Read execution paths and resource costs | Performance tuning, distributed systems |
| Data core | Databases, SQL, Data Modeling | Design storage structures and query patterns | Data engineering, analytics platforms |
| Intelligent applications | ML, Deep Learning, Data Mining | Define features, labels, and evaluation metrics | Recommendation, vision, NLP |
| Integrated practice | Software Engineering, Capstone, Team projects | Convert requirements into schedules and deliverables | Job portfolio, graduate research |

The key insight is not difficulty comparison but dependency understanding. For example, without programming fundamentals and data-structure intuition before OS, scheduling and memory management concepts cannot connect to code.

## Course Dependency Graph in Prose

When first building a curriculum map, writing dependencies as sentences is more effective than drawing diagrams.

- Math foundations are shared prerequisites for algorithm correctness proofs and ML loss optimization.
- Programming foundations are the shared execution platform for systems, data, and AI coursework.
- The systems core provides debugging literacy: reproducing performance issues and narrowing causes.
- The data core is the central axis for reliably storing service state and reducing query latency.
- Intelligent applications reach reproducible quality only when earlier axes are stable.
- Integrated practice is the final stage that verifies balance across all five axes.

Applying this structure to semester planning clarifies elective priorities. The universally valid principle regardless of career target: "fix fundamentals first, extend applications later."

## Registration Strategy Checkpoints

Before each semester, writing answers to these four questions raises plan quality fast.

1. Which of this semester's courses is a prerequisite for other courses?
2. Which course feeds directly into a project, and does it need prerequisite reinforcement?
3. Which axis can I own in a team assignment?
4. What gap must I fill now for next semester's target course?

When these have answers, a simple timetable becomes a curriculum-map-based study plan.

## Reverse-Tracking Careers Through Course Combinations

To use the curriculum map for real decisions, trace course combinations backward from your target career. A backend engineer needs data structures, OS, networking, databases, and software engineering as the baseline. A data role needs linear algebra, probability, databases, ML, and experiment design. A security role needs OS, networking, cryptography, systems programming, and log analysis. Career targets differ in emphasis but cannot skip foundational axes.

A recommended semester ratio is "2 foundations + 1 application + 1 integration." Two foundation courses maintain the floor, one application course provides motivation, one integration course produces a deliverable.

## Curriculum Dependency Table

| Subject area | Prerequisite | Feeds directly into | Signal when missed |
| --- | --- | --- | --- |
| Discrete Math | Basic math | Data Structures, Algorithms | Frequent logic jumps in proof problems |
| Programming fundamentals | None | Data Structures, Systems Programming | Fast implementation but high error rate |
| Computer Architecture | Basic programming | Operating Systems | Explaining performance bottlenecks only by guessing |
| Databases | Programming fundamentals | Backend projects | Can write SQL but cannot justify schema decisions |
| Probability and Statistics | Calculus, Linear Algebra | Machine Learning | Repeated overconfidence or underestimation in metric interpretation |

Course dependencies are more directly useful for setting study order than credit tables. Customizing this table to your situation before registration aligns course selection and weekly study plans in the same direction.
## Wrap-up and Next Steps

Next post: *Understanding First Year Subjects*.

## Answering the Opening Questions

- **How can you understand the four-year CS curriculum as a big picture?**
  - The major is built on six pillars (math, programming, systems, data, AI, projects), each supporting the next. Once you grasp this flow, individual courses make sense as connected steps rather than isolated subjects.
- **Why are math, programming, systems, data, AI, and projects a continuous flow rather than separate courses?**
  - Each pillar serves as the foundation for the next. Understanding this progression lets you see the meaning behind each course at a glance.
- **What is the difference between memorizing course names and understanding the curriculum map?**
  - You need to understand what problem each course solves and how it connects to the next. Then every new course becomes a piece fitting into the big picture, not just another assignment to complete.
<!-- toc:begin -->
## In this series

- **What Computer Science Majors Learn (current)**
- Understanding First Year Subjects (upcoming)
- Data Structures and Algorithms (upcoming)
- Understanding Systems Subjects (upcoming)
- Database and Network (upcoming)
- AI and Data Science (upcoming)
- Project Subjects (upcoming)
- How to Study Computer Science (upcoming)
- Build Your Portfolio (upcoming)
- Skills to Have Before Graduation (upcoming)

<!-- toc:end -->

## References

- [ACM Computing Curricula 2020](https://www.acm.org/binaries/content/assets/education/curricula-recommendations/cc2020.pdf)
- [MIT EECS Undergraduate Curriculum](https://www.eecs.mit.edu/academics/undergraduate-programs/)
- [Stanford CS Major Requirements](https://cs.stanford.edu/degrees/undergrad/)
- [Open Source Society University](https://github.com/ossu/computer-science)

Tags: CS, Major, Curriculum, Career, Beginner
