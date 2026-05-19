---
series: computer-science-major-101
episode: 8
title: How to Study Computer Science
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
  - Study
  - Habit
  - Learning
  - Beginner
seo_description: A beginner-friendly tour of CS study habits covering routine, note taking, review cycles, drills, and questions.
code_required: false
last_reviewed: '2026-05-14'
---

# How to Study Computer Science

Some students remember concepts weeks later, while others lose them almost as soon as the lecture ends. The gap is often less about talent than about whether their study method has a repeatable structure.

This is post 8 in the Computer Science Major 101 series.

## Questions This Post Answers

- Why does the same amount of study time produce very different results depending on the method?
- How should lectures, notes, review, and coding practice fit together?
- Why does cramming fail especially badly in computer science courses?
- Why do questions and written records create such a large long-term advantage?

## What You Will Learn

- A weekly routine
- How to structure lecture notes
- How to build a review cycle
- How to use coding drills
- Why asking questions matters

## Why It Matters

Study efficiency creates a large share of the gap between students in a CS major. Two students can attend the same lecture, but review spacing, practice frequency, and question habits create very different levels of understanding and retention.

## Concept at a Glance

![Study loop for CS majors](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-major-101/08/08-01-study-loop.en.png)

*The study loop from lecture to questions and practice*

> Studying computer science does not end when the lecture ends. It becomes real only when you revisit the idea, test it with your hands, and use questions to clear what still feels vague.

Listening to a lecture is only the beginning. You need to compress the idea into notes, reopen it during review, test it through practice, and resolve weak spots through questions. When that loop keeps running, knowledge starts to stick instead of fading after the exam.

## Key Terms

- **routine**: a repeatable study schedule.
- **note**: a short record of core ideas.
- **review**: the act of revisiting something you already studied.
- **drill**: repeated hands-on practice.
- **office hour**: time when you can ask a professor or TA questions.

## Before/After

**Before**: You study only right before exams.

**After**: You spread lectures, review, and practice across a weekly routine.

## Hands-on: A Weekly Review Loop Tracker

Counting hours is not enough for CS study. You also need to know when you heard the concept, when you plan to revisit it, whether the review actually happened, and where your open questions still live. The script below creates a small weekly report around that loop.

```python
from collections import defaultdict
from datetime import date, timedelta

sessions = [
    {
        "course": "algorithms",
        "lecture_date": date(2026, 5, 4),
        "study_minutes": 100,
        "review_completed": True,
        "questions": ["Why does merge sort stay O(n log n)?"],
    },
    {
        "course": "operating-systems",
        "lecture_date": date(2026, 5, 5),
        "study_minutes": 60,
        "review_completed": False,
        "questions": ["What exactly causes context-switch overhead?"],
    },
    {
        "course": "databases",
        "lecture_date": date(2026, 5, 6),
        "study_minutes": 45,
        "review_completed": False,
        "questions": [],
    },
]


def build_weekly_report(entries):
    totals = defaultdict(int)
    weak_areas = []
    lines = []

    for entry in entries:
        next_review = entry["lecture_date"] + timedelta(days=2)
        totals[entry["course"]] += entry["study_minutes"]
        status = "done" if entry["review_completed"] else "pending"
        lines.append(
            f"{entry['course']}: lecture={entry['lecture_date']}, "
            f"next_review={next_review}, review={status}, "
            f"questions={len(entry['questions'])}"
        )

    for course, minutes in totals.items():
        if minutes < 90 or any(
            e["course"] == course and not e["review_completed"] for e in entries
        ):
            weak_areas.append(course)

    summary = ", ".join(f"{course}={minutes}m" for course, minutes in totals.items())
    weak_summary = ", ".join(weak_areas) if weak_areas else "none"
    return "\n".join(lines + [f"weekly_totals: {summary}", f"weak_areas: {weak_summary}"])


print(build_weekly_report(sessions))
```

With the sample input, you should see output like this.

```text
algorithms: lecture=2026-05-04, next_review=2026-05-06, review=done, questions=1
operating-systems: lecture=2026-05-05, next_review=2026-05-07, review=pending, questions=1
databases: lecture=2026-05-06, next_review=2026-05-08, review=pending, questions=0
weekly_totals: algorithms=100m, operating-systems=60m, databases=45m
weak_areas: operating-systems, databases
```

This report makes three claims visible at once: when the next review should happen, where unanswered questions are accumulating, and which courses are receiving too little practice. That is the practical link between spaced review, question habits, and weekly planning.

## What to Notice in This Code

- Lecture date and next review date turn spaced learning into a concrete schedule.
- Review status and question count reveal where understanding is still weak.
- Weekly totals only become useful when you read them together with unfinished reviews.

## Five Common Mistakes

1. **Only transcribing notes and never reopening them.**
2. **Following the schedule without building any review loop.**
3. **Pushing coding drills into exam week.**
4. **Feeling embarrassed about asking questions and dragging confusion for too long.**
5. **Trying to buy more study time by cutting sleep.**

## How This Shows Up in Production

The growth speed of a new engineer often shows up first in question frequency and note-taking habits. People who surface blockers quickly, record how they solved them, and reduce repeated mistakes usually adapt much faster.

## A Sample Weekly Routine

The table below is not a perfect routine. It is a practical example of the minimum rhythm needed when you are taking several CS courses at once. The goal is to build a weekly loop you can sustain.

| Day | What to do | Why it matters |
| --- | --- | --- |
| Monday | Summarize the lecture in three lines right after class | Compression works best while the memory is still fresh. |
| Tuesday | Spend one hour on algorithms or programming drills | Ideas do not become execution skill until your hands move. |
| Wednesday | Review concept-heavy courses such as OS or databases | Theory sticks better when you revisit it after a short gap. |
| Thursday | Gather question lists and ask a professor, TA, or peer | It is important to clear blockers within the same week. |
| Friday | Check study hours and identify weak subjects | Numbers make subject imbalance immediately visible. |
| Weekend | Preview next week for 30 minutes and finish leftover assignments | Weekends work better for consolidation than for impulsive new learning. |

You do not need to copy this table exactly. The important part is that lecture, review, practice, questions, and reflection all happen at least once inside the same week.

## How a Senior Engineer Thinks

- Routine lasts longer than talent.
- Written records compound over time.
- Questions are not weakness. They are learning tools.
- Sleep is part of productivity.
- Review is what turns exposure into real learning.

## Checklist

- [ ] I wrote down a weekly routine.
- [ ] I chose one note format.
- [ ] I defined a review cycle.
- [ ] I started keeping a separate question list.

## Practice Problems

1. Define a routine in one line.
2. State the meaning of review in one line.
3. Explain how you would use office hours in one line.

## Wrap-up and Next Steps

You cannot sustain CS study for long on motivation alone. Lectures, notes, review, practice, and questions need to form one loop before learning starts to accumulate. The same amount of time can produce very different results depending on the method. In the next post, we will look at how to turn coursework and projects into a portfolio that other people can read.

<!-- toc:begin -->
- [What Computer Science Majors Learn](./01-what-cs-majors-learn.md)
- [Understanding First Year Subjects](./02-first-year-subjects.md)
- [Data Structures and Algorithms](./03-data-structures-and-algorithms.md)
- [Understanding Systems Subjects](./04-systems-subjects.md)
- [Database and Network](./05-database-and-network.md)
- [AI and Data Science](./06-ai-and-data-science.md)
- [Project Subjects](./07-project-subjects.md)
- **How to Study Computer Science (current)**
- Build Your Portfolio (upcoming)
- Skills to Have Before Graduation (upcoming)
<!-- toc:end -->

## References

- [Make It Stick](https://www.hup.harvard.edu/books/9780674729018)
- [Improving Students' Learning With Effective Learning Techniques](https://journals.sagepub.com/doi/10.1177/1529100612453266)
- [How Learning Works](https://www.wiley.com/en-us/How+Learning+Works%3A+Eight+Research-Based+Principles+for+Smart+Teaching-p-9780470484104)
- [ACM/IEEE-CS/AAAI Computer Science Curricula 2023](https://csed.acm.org/cs2023/)

Tags: CS, Study, Habit, Learning, Beginner
