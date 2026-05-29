---
series: capstone-project-101
episode: 9
title: "Capstone Project 101 (9/10): Building Presentation Materials"
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

# Capstone Project 101 (9/10): Building Presentation Materials

Presentation decks usually become bloated because teams try to show every feature they built. Audiences, however, care much more about why the project mattered and what changed as a result.

A strong deck is not a catalog of screens. It is a concise story about the problem, the chosen solution, the demonstrated result, and the next insight the team gained.

This is the 9th post in the Capstone Project 101 series. It uses a problem-solution-result arc for the deck and folds in demo fallback planning plus Q&A preparation.


![capstone project 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/capstone-project-101/09/09-01-the-flow-at-a-glance.en.png)
*capstone project 101 chapter 9 flow overview*
> A strong presentation does not show all features. It shows the problem, the path taken, and the learning captured.

## Questions to Keep in Mind

- Why do feature-list presentations lose attention quickly?
- What should survive on each slide?
- Why does the demo need a written script?

## What You Will Learn

- A *narrative* structure
- *Slide* composition
- A *demo script*
- *Q&A* preparation
- *Time* allocation

## Why It Matters

A problem-solution-result arc gives the audience context immediately, which means feature details can appear only where they support the story.

Separating demo planning and Q&A planning also makes the talk more resilient. Presentation-week failures are often caused less by missing features than by broken flow, time overruns, or unprepared questions.

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

Fix the presentation narrative in five steps first: `problem`, `solution`, `demo`, `result`, and `next`.

### Step 2 — Slide counts

Allocate slide counts by section in advance, for example `problem=2`, `solution=3`, `demo=1`, `result=2`, and `next=1`.

### Step 3 — Demo script

Keep the demo scenes to three steps or fewer, such as `login`, `core_action`, and `result_view`.

### Step 4 — Q&A prep

List likely questions in advance, such as `why_this_stack`, `how_we_tested`, and `what_we_cut`, and prepare the evidence for each answer.

### Step 5 — Time allocation

Write time allocation in numbers, for example `talk=8`, `demo=5`, and `qna=7`, so the ending does not get rushed.

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

## Practical Extension: Slide Composition Table and Demo Script Example

Presentation quality is determined more by message structure than slide design. In a capstone with limited time, you must show the problem, the choices made, and the results—so preparing a per-slide purpose table and a separate demo script is essential.

### Slide Composition Table

| Slide # | Title | Core Message | Visual Aid | Speaking Time |
| --- | --- | --- | --- | --- |
| 1 | Problem Background | Why this problem causes real inconvenience | User-situation image | 1 min |
| 2 | Problem Definition | Whose specific pain are we solving | Problem-statement box | 1 min |
| 3 | Solution Approach | Why this flow was chosen | System flow diagram | 1 min |
| 4 | MVP Scope | What was included and excluded | Scope table | 1 min |
| 5 | Demo | Does the core flow actually work | Live demonstration | 3 min |
| 6 | Result Metrics | What was validated | Metrics table/graph | 1 min |
| 7 | Limitations & Improvements | What remains and how to extend | Roadmap | 1 min |
| 8 | Conclusion | What learning this project left behind | 3 summary sentences | 1 min |

### Demo Script Example

```text
0:00-0:20  Introduce demo goal
"I'll now demonstrate the timetable conflict checker's core flow in 60 seconds."

0:20-0:50  Input stage
"Paste a sample timetable and press the check button."

0:50-1:20  Computation/result stage
"Conflicting courses and time slots are displayed immediately."

1:20-1:40  Value confirmation
"Manual checking time is significantly reduced compared to before."

1:40-2:00  Backup transition notice
"If a network issue occurs, I'll continue with the same flow using a recorded video."
```

Preparing the script sentence-by-sentence reduces explanation gaps caused by stage nerves. Fixing the opening and closing sentences of the demo in particular stabilizes delivery.

### Expected Q&A Preparation Table

| Question Type | Expected Question | Answer Core | Evidence Document |
| --- | --- | --- | --- |
| Tech choice | Why did you pick this stack? | Low learning cost and ops burden | ADR document |
| Scope adjustment | Why was a feature excluded? | High difficulty relative to demo impact | MVP scope table |
| Testing | How did you verify reliability? | Integration test scenarios passed | Test report |
| Extension plan | What is the next step? | Recommendations feature / mobile | Roadmap slide |

### Rehearsal Operation Checklist

- Mark speaker-switch points down to the second.
- Practice the backup-transition sentence for demo failure.
- Fix a "one-line conclusion" for each slide.
- Pull 10 random questions and rehearse answers.
- Pre-designate which slides to cut if time overruns.

### Reducing Presentation Wobble

Presentations require clear priority delivery over perfect information delivery. "Show less, repeat the key point" is more effective than "show everything." Operating the slide composition table and demo script together ensures the entire team delivers the same message, and evaluators can quickly understand the project's decision quality.

## Practical Anchor: Slide Structure and Demo Script Template

Presentation materials need structure before design. Even with many slides, if the message order is unclear, delivery power drops sharply. For capstone presentations, fixing a problem-solution-validation-retrospective sequence is the most stable approach.

### 10-Slide Standard Structure

| Slide # | Title | Core Message |
| --- | --- | --- |
| 1 | Problem Background | Why this problem matters |
| 2 | User Definition | Who benefits from the solution |
| 3 | Existing Approach Limits | Evidence of current inconvenience |
| 4 | Proposed Solution | The core idea |
| 5 | System Flow | Summary of how it works |
| 6 | MVP Scope | What was built this semester |
| 7 | Validation Results | Metrics and test outcomes |
| 8 | Demo Scene | Actual usage flow |
| 9 | Limitations & Risks | Remaining challenges |
| 10 | Retrospective & Next Steps | Learning and extension plan |

### Demo Script Template

```text
Opening (20s): Explain the user problem in one sentence
Scene 1 (40s): Input and initial state
Scene 2 (60s): Core processing
Scene 3 (40s): Result and metrics confirmation
Closing (20s): Limitations and next experiment
```

The script should be managed as a team document, not a personal presenter's note. That way, even if the presenter changes, the message order stays intact, and Q&A responses remain grounded in the same evidence.

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

## Answering the Opening Questions

- **Why do feature-list-centric presentations become boring?**
  - This article unpacks creating presentation materials not as a simple definition but through concrete situations and decision processes encountered in practice. Follow the examples and checklists in each section to apply them to your own situation.
- **Why does the problem-solution-result structure have high communication power?**
  - Referring to the example code and matrices presented in this article, you can concretely feel what good judgment criteria look like. Understanding "in what situation do you set such criteria" matters more than the numbers themselves.
- **How should slides be structured so each one has a clear message?**
  - The core message of this article is that regardless of what evaluation criteria you use, it never ends with a single judgment. Recording criteria in documents early on, so the same mistakes aren't repeated when looking back later—that process itself leads a project to success.
<!-- toc:begin -->
## In this series

- [Capstone Project 101 (1/10): What is a Capstone Project](./01-what-is-capstone.md)
- [Capstone Project 101 (2/10): Choosing a Topic](./02-choosing-a-topic.md)
- [Capstone Project 101 (3/10): Defining the Problem](./03-defining-the-problem.md)
- [Capstone Project 101 (4/10): Organizing Requirements](./04-organizing-requirements.md)
- [Capstone Project 101 (5/10): Splitting Team Roles](./05-splitting-team-roles.md)
- [Capstone Project 101 (6/10): Designing the MVP](./06-designing-the-mvp.md)
- [Capstone Project 101 (7/10): Choosing the Tech Stack](./07-choosing-the-tech-stack.md)
- [Capstone Project 101 (8/10): Schedule Management](./08-schedule-management.md)
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
