---
series: capstone-project-101
episode: 9
title: Building Presentation Materials
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Capstone
  - Presentation
  - Demo
  - Storytelling
  - Beginner
seo_description: A beginner-friendly tour of capstone presentation materials with a problem solution result narrative and demo script.
last_reviewed: '2026-05-14'
---

# Building Presentation Materials

Presentation decks usually become bloated because teams try to show every feature they built. Audiences, however, care much more about why the project mattered and what changed as a result.

A strong deck is not a catalog of screens. It is a concise story about the problem, the chosen solution, the demonstrated result, and the next insight the team gained.

This is post 9 in the Capstone Project 101 series. It uses a problem-solution-result arc for the deck and folds in demo fallback planning plus Q&A preparation.

## Questions this chapter answers

- Why do feature-list presentations lose attention quickly?
- What should survive on each slide?
- Why does the demo need a written script?
- How should demo fallback material be prepared?
- How does Q&A preparation raise the quality of the talk?

> A good presentation is not the place to show everything. It is the place to compress problem, choice, and result into a story the audience can grasp immediately.


## What You Will Learn

- A *narrative* structure
- *Slide* composition
- A *demo script*
- *Q&A* preparation
- *Time* allocation

## Why It Matters

A problem-solution-result arc gives the audience context immediately, which means feature details can appear only where they support the story.

Separating demo planning and Q&A planning also makes the talk more resilient. Presentation-week failures are often caused less by missing features than by broken flow, time overruns, or unprepared questions.

## The flow at a glance

![The flow at a glance](https://yeongseon-books.github.io/book-public-assets/assets/capstone-project-101/09/09-01-the-flow-at-a-glance.en.png)
*A presentation narrative from problem to next step*

## Practical artifact: a presentation run sheet

Creating a run sheet like this before polishing slides often improves the talk more than visual tweaks do.

```text
Segment | Time | Key message | Backup material
Problem framing | 2 min | why the pain matters | one user-interview slide
Solution choice | 3 min | why this flow was selected | one requirements table
Demo | 4 min | 60-second core-flow walkthrough | three screenshots, recorded clip
Results and learning | 2 min | what was validated and what remains | feedback summary table
Q&A | 4 min | explain stack, testing, and scope cuts | ADR and retrospective notes
```

## What to validate first

- Keep one message per slide.
- Prepare backup material that can replace a failed live demo immediately.
- Rehearse against the real time limit.
- Attach evidence documents to likely Q&A topics.

## Key Terms

- **narrative**: a *story arc*.
- **slide**: *one* slide, *one* message.
- **demo**: a *scripted* walkthrough.
- **QnA**: *expected* questions.
- **timing**: *time allocation*.

## Before/After

**Before**: A *feature list* slide deck.

**After**: A *problem solution result* deck.

## Hands-on: Slide Table

### Step 1 — Build the narrative

```python
story = ["problem", "solution", "demo", "result", "next"]
```

### Step 2 — Slide counts

```python
slides = {"problem": 2, "solution": 3, "demo": 1, "result": 2, "next": 1}
```

### Step 3 — Demo script

```python
demo_steps = ["login", "core_action", "result_view"]
```

### Step 4 — Q&A prep

```python
qna = ["why_this_stack", "how_we_tested", "what_we_cut"]
```

### Step 5 — Time allocation

```python
minutes = {"talk": 8, "demo": 5, "qna": 7}
```

## What to Notice in This Code

- *One slide* equals *one message*.
- The *demo* is *three steps* or fewer.
- *Q&A* answers are *prepared*.

## Five Common Mistakes

1. **Too much *text*.**
2. **A *feature list*.**
3. **No *demo failure* fallback.**
4. **No *Q&A* preparation.**
5. **Going *over time*.**

## How This Shows Up in Production

Investor pitches also use the *problem solution result* arc.

## How a Senior Engineer Thinks

- *Narrative* outranks *features*.
- *Slides* are *visual*.
- *Demos* are *rehearsed*.
- *Q&A* is *scripted*.
- *Time* is *kept*.

## Checklist

- [ ] *Narrative* in five steps.
- [ ] *Demo* script.
- [ ] *Q&A* answers.
- [ ] *Time* allocation table.

## Practice Problems

1. State the *narrative* structure in one line.
2. State *demo failure* fallback in one line.
3. State a *Q&A* prep method in one line.

## Wrap-up and Next Steps

The job of presentation materials is not to show everything but to create understanding quickly. When the story arc, demo script, fallback assets, and Q&A evidence are prepared together, the talk becomes far more resilient. The next post closes the project with a retrospective.

<!-- toc:begin -->
- [What is a Capstone Project](./01-what-is-capstone.md)
- [Choosing a Topic](./02-choosing-a-topic.md)
- [Defining the Problem](./03-defining-the-problem.md)
- [Organizing Requirements](./04-organizing-requirements.md)
- [Splitting Team Roles](./05-splitting-team-roles.md)
- [Designing the MVP](./06-designing-the-mvp.md)
- [Choosing the Tech Stack](./07-choosing-the-tech-stack.md)
- [Schedule Management](./08-schedule-management.md)
- **Building Presentation Materials (current)**
- Project Retrospective (upcoming)
<!-- toc:end -->

## References

### Official docs and practical guides

- [Presentation Zen](https://www.presentationzen.com/)
- [The Cognitive Style of PowerPoint](https://www.edwardtufte.com/tufte/powerpoint)
- [TED guide to public speaking](https://www.ted.com/playlists/574/how_to_make_a_great_presentation)
- [Pyramid Principle](https://en.wikipedia.org/wiki/Pyramid_principle)

Tags: Capstone, Presentation, Demo, Storytelling, Beginner
