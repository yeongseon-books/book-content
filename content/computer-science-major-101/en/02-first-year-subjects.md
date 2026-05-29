---
series: computer-science-major-101
episode: 2
title: "Computer Science Major 101 (2/10): Understanding First Year Subjects"
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
  - Freshman
  - Math
  - Programming
  - Beginner
seo_description: A beginner-friendly tour of first year CS subjects covering calculus, linear algebra, discrete math, and intro programming.
code_required: false
last_reviewed: '2026-05-14'
---

# Computer Science Major 101 (2/10): Understanding First Year Subjects

> Computer Science Major 101 series (2/10)

**Core question**: Why do first year CS subjects *focus* on *math* and *intro programming*?

> Because *foundation strength* must be built in *one year* before upper courses pile on top.

This is the 2nd post in the Computer Science Major 101 series.


![computer science major 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-major-101/02/02-01-first-year-foundation-map.en.png)
*computer science major 101 chapter 2 flow overview*
> First-year subjects are not obstacles to 'real' CS—they are the ground floor. Each hour spent on calculus, linear algebra, discrete math, and intro programming saves you days of rework in upper courses.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Understanding First Year Subjects?
- Which signal should the example or diagram make visible for Understanding First Year Subjects?
- What failure should be prevented first when Understanding First Year Subjects reaches a real system?

## What You Will Learn

- Meaning of *calculus*
- Role of *linear algebra*
- Use of *discrete math*
- *Intro programming*
- Building *study habits*

## Why It Matters

Year-one *foundations* underlie *algorithms*, *AI*, and *systems* — every later course.

## Concept at a Glance
First-year courses establish the *pace*, *language*, and *thinking habits* you will carry forward. They are not prerequisites—they are ground-builders.
## Key Terms

- **calculus**: math of *continuous* change.
- **linear algebra**: *vectors* and *matrices*.
- **discrete math**: *logic* and *sets*.
- **intro programming**: *language* basics.
- **lab**: *hands-on* time.

## Before/After

**Before**: First year subjects feel *far* from your career.

**After**: You see them as the *roots* of every upper course.

## Hands-on: First Year Course Matrix

### Step 1 — List courses

```python
courses = ["calculus", "linalg", "discrete", "intro_prog"]
```

### Step 2 — Map to upper courses

```python
maps = {"calculus": "ml", "linalg": "ml", "discrete": "algorithms", "intro_prog": "all"}
```

### Step 3 — Weekly study hours

```python
hours = {c: 6 for c in courses}
```

### Step 4 — Lab weight

```python
labs = {"intro_prog": 4, "discrete": 1}
```

### Step 5 — Mark weak spots

```python
weak = [c for c, h in hours.items() if h < 5]
```

## What to Notice in This Code

- Each subject *links* to upper courses.
- *Study hours* equal *foundation strength*.
- *Lab time* sits separately.

## Five Common Mistakes

1. **Just *attending* without *reviewing*.**
2. **Treating *math* as pure *memorization*.**
3. **Switching *languages* and delaying basics.**
4. **Starting *lab assignments* the night before.**
5. **Never *asking the professor* questions.**

## How This Shows Up in Production

If your *algebra* and *logic* shake during code review, *upper work* also collapses.

## How a Senior Engineer Thinks

- *Foundations* are wealth.
- *Math* takes time.
- *Code* is daily.
- *Mistakes* are notes.
- *Questions* are habit.

## Checklist

- [ ] Course *links* mapped.
- [ ] *Study hours* secured.
- [ ] *Lab* weight set.
- [ ] *Weak spots* reinforced.

## Practice Problems

1. Define *linear algebra* in one line.
2. Define *discrete math* in one line.
3. State the meaning of *intro programming* in one line.

## Wrap-up and Next Steps

Next post: *Data Structures and Algorithms*.

## A Strategic Frame for First-Year Subjects

First year is not when you learn the flashiest topics — it is when you build the capacity to handle flashy topics later. Course selection should prioritize cumulative efficiency over immediate interest. Calculus, linear algebra, discrete math, and intro programming look like separate subjects, but they form stages of a single problem-solving pipeline: calculus builds intuition for change and optimization, linear algebra provides grammar for multidimensional structures, discrete math fixes logic and proof habits, and intro programming converts all of it into executable procedures.

### First Language Comparison

| Factor | Python-first | C-first | Java-first |
| --- | --- | --- | --- |
| Entry barrier | Low | Medium–High | Medium |
| Concept learning speed (vs syntax overhead) | Fast | Medium | Medium |
| Memory / low-level intuition | Relatively weak | Strong | Medium |
| Data structures course connection | Good | Very good | Good |
| Web / data lab connection | Very good | Average | Good |
| Beginner frustration risk | Low | High | Medium |

The conclusion is not that one language is universally superior. What matters is clarifying the purpose of your first language. In year one, you need to lock in function decomposition, condition design, exception handling, and testing habits in *one* language — not accumulate syntax across many.

## Connecting Math and Coding — Not Separate Tracks

Many students treat math as exam material and coding as project material. But real academic performance is decided at the intersection. Discrete-math propositional logic sharpens your ability to handle edge cases in conditionals. Linear algebra's vector intuition connects directly to recommendation scores and embedding similarity beyond ML. Calculus's rate-of-change concept is the basic intuition for reading learning rates and loss curves during optimization.

A minimal weekly loop you can apply immediately:

- Within 24 hours of a lecture: write a 3-line summary of the core concept.
- Within 48 hours: solve 3 related problems yourself.
- Within one week: classify errors into concept / calculation / interpretation / attention.
- Before next week: reinforce exactly one weak point.

This loop raises retention more than it raises study time. The performance gap in second year is often explained by routine stability in first year, not by talent.

## Year-End Self-Check

At the end of the year, review these items to significantly reduce the difficulty of subsequent courses:

- Can you explain the difference between functions, loops, types, and exception handling in your own words?
- Can you apply basic time-complexity concepts when solving problems?
- Can you explain matrix multiplication from a structural perspective, not just as a calculation procedure?
- Can you connect logical expression truth values to code branches?
- Have you recorded the difference between problems solved alone versus in collaboration?

If all five are satisfied, the entry cost to second-year courses drops significantly.

## First-Year Study Plan Template

Structure matters more than speed in year one. Placing course goals and verification methods in the same table prevents routine collapse after midterms.

| Subject | Weekly Goal | Verification Method | Reinforcement Trigger |
| --- | --- | --- | --- |
| Calculus | 2 core theorems + 10 problems | Classify errors into 3 types | Weekend 90-min session if error rate > 30% |
| Linear Algebra | Vector/matrix concept summary | 5 hand-calculations + 1 code exercise | Rewrite notes if concept explanation fails |
| Discrete Math | Proposition/set/proof training | Explain 3 proof problems orally | Register study-group question if logic gap found |
| Programming | Function/loop/exception practice | Pass tests + 1 code review | Reduce scope if tests fail 2+ times |

Some departments use relative grading. Understanding GPA calculation rules early helps identify at-risk courses:

```text
Example GPA = (A0 3cr×4.0 + B+ 3cr×3.5 + A+ 3cr×4.5 + B0 3cr×3.0) / 12
            = 45.0 / 12 = 3.75
```

The purpose of tracking GPA is not score obsession — it is early detection of courses that need intervention.

## Answering the Opening Questions

- **Why do first-year courses emphasize math and programming so heavily?**
  - First-year courses lock in mathematical thinking and implementation habits simultaneously. Building a solid foundation early dramatically improves comprehension speed and stability in second-year courses and beyond.
- **What roles do calculus, linear algebra, discrete math, and intro programming each play?**
  - Calculus handles rates of change, linear algebra covers vector and matrix structures, discrete math provides logic and proofs, and intro programming teaches implementation fundamentals. The four courses serve different roles but connect to form the foundation for everything that follows.
- **Why does a course that seems unrelated to your career now determine outcomes from second year onward?**
  - Courses from second year onward are designed assuming first-year concepts. Weak fundamentals mean you spend time re-learning the same material repeatedly, and project implementation quality suffers as a result.
<!-- toc:begin -->
## In this series

- [Computer Science Major 101 (1/10): What Computer Science Majors Learn](./01-what-cs-majors-learn.md)
- **Understanding First Year Subjects (current)**
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

- [MIT 6.0001 Introduction to Computer Science](https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/)
- [3Blue1Brown - Essence of Linear Algebra](https://www.3blue1brown.com/topics/linear-algebra)
- [Discrete Math - CMU](https://www.cs.cmu.edu/~rwh/discrete-math/)
- [Khan Academy Calculus](https://www.khanacademy.org/math/calculus-1)

Tags: CS, Freshman, Math, Programming, Beginner
