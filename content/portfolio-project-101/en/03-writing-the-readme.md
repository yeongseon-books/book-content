---
series: portfolio-project-101
episode: 3
title: "Portfolio Project 101 (3/10): Writing the README"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Portfolio
  - README
  - Documentation
  - Onboarding
  - Beginner
seo_description: How to write a README that helps a hiring reviewer understand your project quickly and decide what to inspect next.
last_reviewed: '2026-05-15'
---

# Portfolio Project 101 (3/10): Writing the README

A good project can still lose power at the entrance if the README is weak. Most visitors read the README before they read any code. In that short window, they need to understand what problem the project solves, whether there is a demo worth opening, and how they could run it themselves.

If those answers are buried or missing, the reviewer often leaves before your implementation quality gets a chance to matter.

This is the 3rd post in the Portfolio Project 101 series. Here we will treat the README as the project's first demo and look at how to arrange it so a reviewer can understand the value in about a minute.

---

> A strong README is not just a repository description. It is an entry document that helps a first-time visitor decide what to do next.


![portfolio project 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/portfolio-project-101/03/03-01-concept-at-a-glance.en.png)
*portfolio project 101 chapter 3 flow overview*
> A README is the face of a repository. If you can explain the problem and solution within a minute, the visitor gains momentum to read code.

## Questions to Keep in Mind

- What information should a portfolio README show first?
- Why does the order pitch → demo → stack → run → next feel easy to scan?
- Why can a README still feel weak even when it contains many screenshots?

## Why It Matters

A README shapes the first impression of the project. The exact same codebase can feel much stronger when the README is tight, structured, and honest about the current state. Reviewers often read communication quality, onboarding care, and scope discipline from the README itself.

In portfolio work, that matters a lot because the reviewer is not a teammate who already knows the context. The README has to do the work of orientation on its own.

## Mental Model

The simplest way to design a README is to follow the visitor’s question order.

Most first-time readers think in roughly this order: what is this, does it work, what is it built with, can I run it, and what is still left. A README works best when it follows that flow instead of following the author's implementation history.

## Key Terms

- **Pitch**: a one-line summary of the problem and project shape.
- **Demo**: a live link or screenshot that proves the product experience exists.
- **Stack**: the short list of technologies that matter for orientation.
- **Run path**: copy-paste steps for trying the project locally.
- **Next**: the unfinished work or improvement list that sets expectations honestly.

## Before and After

**Before**: the README shows a title and maybe an install command, but the actual value of the project is hard to infer.

**After**: a visitor can understand the project, open the demo, and decide whether to inspect the implementation in well under a minute.

The difference is not length. It is whether the document is written for a first-time reader.

## Step by Step

### Step 1 — Start with a one-line pitch

Lead with the problem the project solves, not the framework name.

```markdown
> A mini SaaS that fixes lost team schedules
```

A strong pitch does not repeat the title. It compresses the reason the project exists.

### Step 2 — Surface the demo early

A reviewer should not have to hunt for the proof.

```markdown
[Live Demo](https://demo.example.com)
```

A visible demo link creates trust faster than a long explanation paragraph.

### Step 3 — Keep the stack short

The stack section is for orientation, not for showing off every library.

```markdown
- FastAPI, PostgreSQL, Docker
```

The goal is to make the system shape legible. The reasoning behind those choices can live elsewhere.

### Step 4 — Make the run path copy-paste friendly

The first local run should feel simple.

```bash
docker compose up
```

The more setup assumptions you require, the weaker the README becomes as an onboarding path.

### Step 5 — Leave the next tasks visible

Unfinished work is easier to trust when it is named clearly.

```markdown
- [ ] add notifications
```

A next-tasks section is not a weakness. It shows scope control and gives the reviewer an honest sense of what is done versus what is still planned.

## What to Notice in the Code

- The pitch should describe the problem, not restate the title.
- The demo should arrive before deep detail.
- The run path should be short enough that a reviewer can try it without guesswork.

## Common Mistakes

1. Starting with a long preface that pushes the real value too far down.
2. Showing only screenshots without a live link or clear run path.
3. Making the setup instructions too complex for a quick first pass.
4. Naming the stack without explaining what the project is trying to do.
5. Hiding unfinished work so the current state becomes harder to judge.

A README does not win by saying everything. It wins by making the next step obvious.

## How This Reads in Practice

Well-maintained open source projects usually repeat the same pattern: short intro, quick start, visible example or demo, and a clear path to the deeper docs. They do that because first-time visitors always need roughly the same things.

Portfolio projects benefit from the same discipline. A small repository can feel polished when the entry path is easy to follow.

## Checklist

- [ ] The README opens with a problem-first pitch.
- [ ] The demo link or screenshot is visible immediately.
- [ ] The local run path is easy to copy and follow.
- [ ] The core stack is listed without unnecessary noise.
- [ ] The next tasks are written down honestly.

## Practice Problems

1. Rewrite your project pitch without using technology names.
2. List the three things a reviewer should learn within 30 seconds.
3. Find the least friendly part of your current run section and rewrite it.

## Wrap-up and Next Steps

A README is not just a summary page. It is the first user experience of the project. When it leads with the problem, proves the demo, makes the run path simple, and shows unfinished work honestly, even a small project becomes much easier to trust.

Next, we will move from the repository to the product surface itself and look at how to build a demo that reveals value quickly.

### README Structure Template (Copy-Paste Starter)

A README is the first screen where a visitor evaluates your project. Information placement matters more than document length. The template below contains the minimum structure a portfolio project needs and can be applied directly to any repository.

```markdown
# Project Name

One-line intro: explain what user problem this project solves in a single sentence.

## Demo
- Live: https://...
- Video: https://...
- Test Account: guest@example.com / demo1234

## Problem
- User situation
- Pain point with current approach
- Goal of this project

## Solution
- Three core features
- Brief rationale for tech choices

## Tech Stack
- Backend: FastAPI
- DB: PostgreSQL
- Infra: Docker, Render

## Run Locally
```bash
cp .env.example .env
docker compose up --build
```

## Test
```bash
pytest -q
```

## Roadmap
- [x] MVP
- [ ] Notification
- [ ] Audit log
```

The key point of this template is following the reader's question order. What is this, does it work, why is it needed, how do I run it, and how far along is it. Answering those in sequence makes the README much stronger.

### Good README vs Weak README Comparison

The comparison below shows how document structure changes perception of the same project.

| Aspect | Weak README | Good README |
| --- | --- | --- |
| Opening line | Technology-focused | Problem and user focused |
| Demo info | Missing or buried at bottom | Immediately visible at top |
| Run path | Missing or long paragraph | Copy-paste command block |
| Current state | Packaged to look complete | Done/not-done clearly separated |
| Verification | No test info | Test command and status included |

A good README does not need fancy prose. It needs to make "what should I do next" immediately clear to the visitor.

### README Quality Checkpoint

After writing your README, use these five items as a self-check:

1. Is the problem and demo link visible within 5 lines below the title?
2. Does local setup finish in 3 steps or fewer?
3. Does the environment variable description match `.env.example`?
4. Is there a link to verify test/deploy status?
5. Are TODOs managed in a realistic order?

When all five are met, the README becomes a reviewable project entrance rather than a simple notice. Polishing just the README before an interview often makes a surprisingly large difference in project impression.

### README Refactoring Procedure (1-Hour Version)

To quickly improve an existing README, follow this order:

1. Read only the top 20 lines and check if problem/demo/run path are visible.
2. If not, add a one-line problem definition and demo link below the title.
3. Convert run instructions from paragraphs to command blocks.
4. State current status with checkboxes.
5. Finally, verify all links and commands by actually running them.

| Check Item | Before | After |
| --- | --- | --- |
| First-visit readability | Low | High |
| Run reproducibility | Unclear | Clear |
| Project state transparency | Low | High |

This procedure is short but high-impact. Once the README is organized, code review entry rates go up and project trust improves together.

### README Template Variants by Project Type

Not every project fits the same README structure. The sections to emphasize differ by project type.

**API Server Project**

```markdown
# task-tracker-api

> Solves the problem of team schedules scattered across tools, increasing lookup cost.

## Demo
- Live: https://demo.example.com
- API Docs: https://demo.example.com/docs (Swagger UI)

## Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /schedules | Fetch weekly schedule |
| POST | /schedules | Create schedule |
| GET | /schedules/shared/{token} | Shared link lookup |

## Run
```bash
cp .env.example .env
docker compose up -d
open http://localhost:8000/docs
```

## Test
```bash
pytest --cov=src tests/
```

## Tech Choice Rationale
- FastAPI: auto OpenAPI docs, async support
- PostgreSQL: complex query performance, JSON field support

## Next Steps
- [ ] Calendar sync (Google Calendar API)
- [ ] Email notifications
```

**Data Analysis Project**

```markdown
# sales-funnel-analysis

> Identifies conversion drop-off stages in a B2B SaaS funnel to guide marketing budget allocation.

## Results Summary
- Funnel stage 3 conversion: 12% → 18% (after improvement)
- Budget reallocation reduced CAC by 23%

## Data
- Sample data: `data/sample_funnel.csv` (10,000 rows, anonymized)
- Original: private (NDA)

## Run
```bash
pip install -r requirements.txt
jupyter notebook notebooks/01-eda.ipynb
```

## Analysis Flow
1. EDA → 2. Per-stage conversion calculation → 3. Bottleneck identification → 4. Improvement proposal → 5. A/B test design
```

The difference between these two templates shows that API projects emphasize endpoints and run commands, while data analysis projects emphasize results and analysis flow. Highlighting the right sections for your project type helps visitors find key information quickly.

### Portfolio Website Structure

A portfolio website is a top-level document that shows multiple projects from a single entrance. Separate from a GitHub profile README, building it as a static site lets you connect context across projects.

```text
portfolio-site/
├── index.html              # visitor entry: intro + project list
├── projects/
│   ├── task-tracker.html   # project detail: problem, demo, stack, result
│   └── sales-analysis.html
├── blog/                   # tech post links (can link to external blog)
├── about.html              # self-intro, career, interests
└── assets/
    ├── screenshots/        # project screenshots
    └── resume.pdf          # PDF resume download
```

The most important page is `index.html`. It should show a one-line intro, 2-3 featured project cards, and contact info all at once. Project detail pages are essentially web versions of the README. They follow the same problem/demo/stack/result structure but allow freer placement of screenshots and GIFs.

A common mistake when building a portfolio site is spending too much time on design. The purpose is not proving design ability but improving project accessibility. A minimal site deployable on GitHub Pages or Vercel in 30 minutes is enough.

### README Self-Review Checklist

After writing a README, always run a self-review. Following this checklist in order catches items that are easy to miss.

```text
[Self-Review Checklist]

Phase 1: First Impression (5-second test)
  □ Can someone guess what this project does from just the name?
  □ Does the one-line description talk about the problem/value, not technology?
  □ Is a demo GIF or live URL visible without scrolling?

Phase 2: Runnability (3-minute test)
  □ Can someone run the project from a fresh terminal using only README commands?
  □ Are environment variable or API key setup instructions specified?
  □ Are Python/Node version requirements stated?
  □ Is docker-compose up or equivalent one-command execution possible?

Phase 3: Context Delivery
  □ Is there a one-paragraph explanation of why this project was built?
  □ Is there at least one line on why the tech stack was chosen?
  □ Is the current state (complete/in-progress/experimental) stated?

Phase 4: Structural Quality
  □ Is there a table of contents with clickable section links?
  □ Do code blocks have language tags?
  □ Do images have meaningful alt text?
  □ Are all links valid? (no 404s)
```

Adding this checklist to your PR template reduces the need for reviewers to flag README quality separately. The "5-second test" in particular simulates a hiring manager's first glance, so showing your README to a colleague for 5 seconds and asking "what does this project do?" is the most effective validation.

### README Version Management

A README must evolve with the code. If code is updated but the README still describes a past version, it causes confusion. Here are practical ways to keep them in sync.

**Method 1: Add README item to PR checklist**

```markdown
<!-- .github/pull_request_template.md -->
## PR Checklist
- [ ] Updated README if code changes affect it
- [ ] Added new environment variables to README if applicable
- [ ] Updated README examples if API endpoints changed
```

**Method 2: Validate README in CI**

```yaml
# .github/workflows/readme-check.yml
name: README Validation
on: [pull_request]
jobs:
  check-readme:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check README links
        run: |
          pip install linkchecker
          linkchecker README.md --check-extern
      - name: Verify install commands work
        run: |
          # Extract and execute install command blocks from README
          grep -A 3 '```bash' README.md | grep -v '```' | bash
```

**Method 3: Keep a recent-changes section**

Maintaining the latest 3 changes at the bottom of the README lets visitors immediately judge whether the project is active.

```markdown
## Recent Changes
- 2024-03-15: Added OAuth2 auth, 2 new env variables
- 2024-03-01: Python 3.12 support, minimum version raised to 3.10
- 2024-02-20: Docker Compose config added, one-command run supported
```

The core principle of README version management is "never let the README lie." Outdated install commands, deleted endpoints, or changed environment variables left in the README erode trust.

### Section Priority by Project Type

Applying the same README structure to every project can bury key information. Section placement priority differs by project type.

| Section | Web App | CLI Tool | Library | Data Analysis | Infra/DevOps |
| --- | --- | --- | --- | --- | --- |
| Demo/Screenshots | 1st | 3rd | 4th | 2nd | 5th |
| Install/Run | 2nd | 1st | 1st | 3rd | 2nd |
| API/Usage Examples | 3rd | 2nd | 2nd | 5th | 4th |
| Results/Metrics | 4th | 5th | 5th | 1st | 3rd |
| Architecture Diagram | 5th | 4th | 3rd | 4th | 1st |

The key insight is placing "what a visitor most wants to check for this project type" at the top. For a web app they want to see a working screen, for a CLI tool they want to install and try it, for data analysis they want to see results first.

In practice, check your project type column in the table above and place the 1st-priority section immediately below H1, the 2nd next, and so on. Sections ranked 4th-5th can move to the bottom of the README or to separate docs (e.g., `docs/architecture.md`).

### Connecting GitHub Profile README to Project READMEs

A GitHub profile README (`username/username` repo) is the entry point of your portfolio. You need to design the path from there to your featured project READMEs.

```markdown
<!-- GitHub Profile README example -->
## Featured Projects

| Project | Description | Stack | Status |
|---------|-------------|-------|--------|
| [task-tracker](link) | Real-time team task progress dashboard | FastAPI, React, PostgreSQL | Production |
| [sales-funnel](link) | B2B SaaS funnel conversion analysis | Python, Pandas, Plotly | Complete |
| [deploy-bot](link) | Slack chatbot for deploy automation | Python, GitHub Actions | In Progress |
```

To reduce cognitive load when visitors move from the profile README to a project README, the one-line description in the profile and the one-line description in the project README should use the same sentence. Different wording makes visitors wonder "is this the same project?"

Also, keep the project count in your profile README to 3 or fewer. Listing 5+ means none stands out as a signature work. Pin your 2-3 most complete projects and align them with the profile README table for a consistent impression.

## Answering the Opening Questions

- **What information should a portfolio README show first?**
  - A one-sentence problem definition. When "what does this solve" is clear, a visitor can judge whether the repository matches their interest.
- **Why does the order pitch → demo → stack → run → next feel easy to scan?**
  - It follows the visitor's natural question sequence: what is this, does it work, what is it made of, can I try it, and what is left. Each answer builds on the previous one.
- **Why can a README still feel weak even when it contains many screenshots?**
  - Screenshots without a live link or run path are one-directional proof. The visitor cannot verify, reproduce, or explore further. A README is strong when it enables action, not just observation.
<!-- toc:begin -->
## In this series

- [Portfolio Project 101 (1/10): What is a Portfolio Project](./01-what-is-a-portfolio-project.md)
- [Portfolio Project 101 (2/10): Traits of a Good Project](./02-traits-of-a-good-project.md)
- **Writing the README (current)**
- Building the Demo (upcoming)
- Deploying the Project (upcoming)
- Tests and Documentation (upcoming)
- Recording Tech Decisions (upcoming)
- Summarizing as Blog Posts (upcoming)
- Explaining in Interviews (upcoming)
- Portfolio Improvement Checklist (upcoming)

<!-- toc:end -->

## References

- [About READMEs (GitHub Docs)](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [Make a README](https://www.makeareadme.com/)
- [Standard Readme](https://github.com/RichardLitt/standard-readme)
- [Awesome README](https://github.com/matiassingers/awesome-readme)

Tags: Portfolio, README, Documentation, Onboarding, Beginner
