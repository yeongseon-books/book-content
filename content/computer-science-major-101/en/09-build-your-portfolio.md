---
series: computer-science-major-101
episode: 9
title: "Computer Science Major 101 (9/10): Build Your Portfolio"
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
  - Portfolio
  - GitHub
  - Career
  - Beginner
seo_description: A beginner-friendly tour of turning major coursework into a GitHub portfolio with strong READMEs and clear documentation.
code_required: false
last_reviewed: '2026-05-14'
---

# Computer Science Major 101 (9/10): Build Your Portfolio

Assignments and projects disappear faster than most students expect if they are left inside local folders with no explanation. A year later, even the person who built them may struggle to remember what they did and why it mattered.

This is post 9 in the Computer Science Major 101 series.


![computer science major 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-major-101/09/09-01-portfolio-publishing-flow.en.png)
*computer science major 101 chapter 9 flow overview*
> A strong portfolio is not a collection of projects—it is a set of *decisions* made visible. Each project should show *why* you chose what you chose.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Build Your Portfolio?
- Which signal should the example or diagram make visible for Build Your Portfolio?
- What failure should be prevented first when Build Your Portfolio reaches a real system?

## Questions This Post Answers

- How can assignments and major projects become portfolio pieces?
- Why do a GitHub repository, README, run instructions, and demo link all matter?
- What is the difference between dumping code online and publishing a result that another person can actually read?
- Why does a portfolio often become the thing that starts the conversation during applications?

## What You Will Learn

- What a portfolio really is
- How to use GitHub well
- How to write a README
- Useful documentation patterns
- Why publishing your work matters

## Why It Matters

Applications need visible evidence to start a real conversation. A repository, README, and demo link say far more than a single line on a resume because they reveal not only what you built, but how you explain and present your work.

## Concept at a Glance
Show *reasoning*, not just code. Each project is a chance to document the boundaries, trade-offs, and lessons you learned.
> An assignment ends at submission, but a portfolio starts only when the work is organized into a repository and explained through documentation.

An assignment does not automatically become a portfolio piece. You need to organize it into a repository, add context through a README, and attach a demo when possible. That is when the work becomes readable to someone other than you.

## Key Terms

- **repository**: a place that holds code and supporting documents together.
- **README**: the first document most people read when they open a repository.
- **license**: a document that defines usage rights.
- **commit**: the basic unit of change history.
- **release**: a packaged version you can point to and share.

## Before/After

**Before**: Your assignment folders live only on your local machine.

**After**: You leave behind a public repository, README, and demo that other people can verify.

## Hands-on: A README Starter Generator

Weak portfolios usually do not fail because the code is missing. They fail because the reader cannot tell what to verify, how to run the project, or what counts as real evidence. The example below turns project metadata into a README draft that is ready to publish.

```python
from textwrap import dedent

project = {
    "name": "schedule-checker",
    "summary": "A Flask web tool that finds conflicts in a student's class schedule.",
    "demo_evidence": [
        "Demo video (recorded walkthrough): docs/demo-walkthrough.mp4",
        "Local demo GIF: docs/demo.gif",
    ],
    "run_steps": [
        "python -m venv .venv",
        "source .venv/bin/activate",
        "pip install -r requirements.txt",
        "flask --app app run",
    ],
    "tech_stack": ["Python", "Flask", "SQLite", "Bootstrap"],
    "license_note": "MIT License",
    "learned": [
        "Input validation had to become stable before UI polish mattered.",
        "Conflict-detection rules became easier to debug once they were written as tests first.",
    ],
}

def build_readme(project):
    demo_lines = "\n".join(f"- {item}" for item in project["demo_evidence"])
    run_lines = "\n".join(f"1. {step}" for step in project["run_steps"])
    stack = ", ".join(project["tech_stack"])
    learned_lines = "\n".join(f"- {item}" for item in project["learned"])

    return dedent(
        f"""
        # {project['name']}

        ## Project Summary
        {project['summary']}

        ## Demo Evidence
        {demo_lines}

        ## Setup and Run
        {run_lines}

        ## Tech Stack
        {stack}

        ## License
        {project['license_note']}

        ## What I Learned
        {learned_lines}
        """
    ).strip()

print(build_readme(project))
```

With the sample input, you should get output like this.

```markdown
# schedule-checker

## Project Summary
A Flask web tool that finds conflicts in a student's class schedule.

## Demo Evidence
- Demo video (recorded walkthrough): docs/demo-walkthrough.mp4
- Local demo GIF: docs/demo.gif

## Setup and Run
1. python -m venv .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt
4. flask --app app run

## Tech Stack
Python, Flask, SQLite, Bootstrap

## License
MIT License

## What I Learned
- Input validation had to become stable before UI polish mattered.
- Conflict-detection rules became easier to debug once they were written as tests first.
```

The important part is that there is no fake-looking `https://example.com/demo` link anywhere. If you do not have a live deployment, name the evidence honestly: a recorded walkthrough, a local GIF, a screenshot folder, or a release artifact. Clear evidence is more credible than a placeholder URL.

## What to Notice in This Code

- A README is both an introduction document and a reproducibility document.
- Demo sections work only when the evidence type is explicit.
- A short reflection section turns a repository from a dump of files into a record of engineering judgment.

## Five Common Mistakes

1. **Leaving the README empty.**
2. **Using vague commit messages such as `update` everywhere.**
3. **Forgetting to add a license.**
4. **Leaving only explanation with no screenshots or demo.**
5. **Writing run instructions so vaguely that the project is hard to reproduce.**

## How This Shows Up in Production

Interviewers and reviewers often read the README before they open the code. How you introduce the project, explain run steps, and care for documentation tells them a great deal about your collaboration habits.

## README Draft Example

Many students try to write an overly long README and end up burying the essentials. In the beginning, it is usually better to publish a short but complete draft that shows evidence and reproducibility clearly.

```markdown
# Schedule Checker

A web tool that finds conflicts in a student's class schedule.

## Demo Evidence
- Demo video (recorded walkthrough): docs/demo-walkthrough.mp4
- Local demo GIF: docs/demo.gif

## Run
1. pip install -r requirements.txt
2. flask --app app run

## What I Learned
- I stabilized the conflict rules by writing tests before polishing the UI.
```

Even this small draft already answers four questions for the reader: what the project is, what kind of evidence exists, how to run it locally, and what the builder learned. The first gate of a portfolio is not flashiness. It is reproducibility.

## How a Senior Engineer Thinks

- Publishing your work is part of learning.
- Documentation matters as much as code.
- Small improvement records can still be strong evidence.
- A license is a basic expectation.
- A demo link is one of the strongest persuasive signals.

## Checklist

- [ ] I added the five core README sections.
- [ ] I included a license.
- [ ] I prepared a screenshot or demo.
- [ ] I wrote run commands where they are easy to find.

## Practice Problems

1. Define a README in one line.
2. State the meaning of a license in one line.
3. Explain why a demo is strong evidence in one line.

## Wrap-up and Next Steps

A portfolio is not a decorative extra for exceptional students. It is the work of turning assignments and projects you already built into a form that another person can read. Once repository name, README, run steps, demo, and documentation are in place, even a small class project can become credible evidence. In the next post, we will close the series by looking at the skills worth checking before graduation.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Build Your Portfolio?**
  - The article treats Build Your Portfolio as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Build Your Portfolio?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Build Your Portfolio reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Computer Science Major 101 (1/10): What Computer Science Majors Learn](./01-what-cs-majors-learn.md)
- [Computer Science Major 101 (2/10): Understanding First Year Subjects](./02-first-year-subjects.md)
- [Computer Science Major 101 (3/10): Data Structures and Algorithms](./03-data-structures-and-algorithms.md)
- [Computer Science Major 101 (4/10): Understanding Systems Subjects](./04-systems-subjects.md)
- [Computer Science Major 101 (5/10): Database and Network](./05-database-and-network.md)
- [Computer Science Major 101 (6/10): AI and Data Science](./06-ai-and-data-science.md)
- [Computer Science Major 101 (7/10): Project Subjects](./07-project-subjects.md)
- [Computer Science Major 101 (8/10): How to Study Computer Science](./08-how-to-study-cs.md)
- **Build Your Portfolio (current)**
- Skills to Have Before Graduation (upcoming)

<!-- toc:end -->

## References

- [GitHub Docs - About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [Open Source Guides - Starting an Open Source Project](https://opensource.guide/starting-a-project/)
- [The Turing Way](https://book.the-turing-way.org/)
- [Good Enough Practices in Scientific Computing](https://doi.org/10.1371/journal.pcbi.1005510)

Tags: CS, Portfolio, GitHub, Career, Beginner
