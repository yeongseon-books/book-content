---
series: developer-career-101
episode: 4
title: "Developer Career 101 (4/10): Resume and Portfolio"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
- Career
- Resume
- Portfolio
- Hiring
- Beginner
seo_description: A beginner-friendly tour of writing a resume and portfolio that recruiters
  grasp in thirty seconds.
last_reviewed: '2026-05-14'
---

# Developer Career 101 (4/10): Resume and Portfolio

Strong experience still gets ignored if it is hard to scan. Hiring teams usually decide within the first minute whether to keep reading, so the first job of a resume is not to tell your whole story. It is to make your role, your best evidence, and your likely interview topics obvious at a glance.

This is the 4th post in the Developer Career 101 series.


![developer career 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/developer-career-101/04/04-01-concept-at-a-glance.en.png)
*developer career 101 chapter 4 flow overview*
> A resume and portfolio speak not to your technology list, but to the size of problems you solved and what you learned in solving them.

## Questions to Keep in Mind

- What structure lets a recruiter understand you quickly without guessing?
- How do you rewrite responsibilities into outcome-oriented bullets with evidence?
- Why are numbers and a compact STAR structure such strong hiring signals?

## What You Will Learn

- *Resume* structure
- Writing *bullets*
- Linking to a *portfolio*
- Keywords and *ATS*
- The *application flow*

## Why It Matters

A resume is the ticket into the interview. Even when you have the experience, the way you present results and impact determines how quickly the reader trusts you and moves forward.

> A resume is not a long autobiography — it is a short ad that opens the door to an interview.

## Key Terms

- **summary**: A two-to-three-line elevator pitch combining role, tenure, and strongest number.
- **bullet**: A result sentence structured around what changed, not what you did.
- **STAR**: Situation, Task, Action, Result — a compact narrative frame.
- **ATS**: Applicant Tracking System — automated resume classifier used by most large companies.
- **portfolio**: A collection of evidence links — repos, demos, docs, talks — that back up resume claims.

## Before/After

**Before**: "I list my responsibilities."

**After**: "I write results and impact with numbers, and every claim links to verifiable evidence."

## Hands-on: Build the Resume

### Step 1 — Header

```text
Name | Email | GitHub | LinkedIn
```

Keep the header simple. Contact info and verifiable links only — no street address or photo.

### Step 2 — Summary

```text
Backend, 3 yrs. Cut payment p95 from 200ms to 80ms.
```

The summary is not a career introduction — it is a compressed highlight reel. Role, tenure, and one headline number give the reader instant context.

### Step 3 — Experience Bullets (STAR)

```markdown
- Cut p95 latency from 200ms to 80ms by introducing read replicas, serving 5M req/day.
```

A bullet should be a result sentence, not a job description. Show the situation, what you did, and how the metric changed — in one line.

### Step 4 — Projects

```markdown
- tinytool: 1.2k stars, used by 30 orgs
```

Projects are not hobby lists — they are evidence. Star count, user count, or a live deploy link make the claim verifiable.

### Step 5 — Skills

```text
Python, PostgreSQL, AWS, Kubernetes
```

A skills section is weakest when it floats disconnected from experience. List only technologies that actually appeared in your experience and project sections.

## What the Screening Flow Actually Looks For

| Stage | What the reviewer wants fast | Evidence you should provide |
| --- | --- | --- |
| 30-second scan | Role, level, strongest number | Three-line summary and one headline outcome |
| 3-minute read | Dense, credible result bullets | STAR-shaped bullets with quantified change |
| Portfolio check | Do the links support the claims? | README, demo, repo, slides, shipped artifact |
| Interview bridge | What should we ask next? | Incidents, performance wins, collaboration stories |

## Resume Section-by-Section DO/DON'T

| Section | DO | DON'T |
| --- | --- | --- |
| Summary | Role, tenure, strongest number | Abstract adjectives (passionate, creative) |
| Experience | STAR structure, numbers, outcomes | Responsibility lists (participated, collaborated) |
| Projects | Verifiable links, user count, stars | Technology lists with no context |
| Skills | Only tech that appeared in experience above | Listing unfamiliar technologies |

Limit the summary to three lines. Each experience bullet gets one result. Projects include a deployed link or repo URL. Skills are a distilled subset of what appeared above.

## Experience Bullet Before/After Examples

Experience bullets must convey what changed, not what you were assigned. Compare weak and strong versions side by side.

### Example 1: API Performance

**Bad:**

```markdown
- Participated in backend API development.
- Worked on DB query optimization.
```

**Good:**

```markdown
- Cut API p95 response time from 200ms to 80ms via read replicas and query tuning, handling 5M req/day.
```

### Example 2: Deployment Automation

**Bad:**

```markdown
- Built a CI/CD pipeline.
- Used GitHub Actions.
```

**Good:**

```markdown
- Built a GitHub Actions CI/CD pipeline that shortened the deploy cycle from 2 weeks to 3 days and reduced manual deploy errors by 90%.
```

### Example 3: Code Quality

**Bad:**

```markdown
- Conducted code reviews.
- Increased test coverage.
```

**Good:**

```markdown
- Introduced a review template and raised pytest coverage from 40% to 75%, cutting production bugs by 60%.
```

## ATS Strategy

ATS (Applicant Tracking System) auto-classifies resumes before a human ever reads them. Larger companies almost always use one.

### ATS-Friendly Format

1. **Text-based PDF** — image PDFs are unreadable by ATS parsers.
2. **Standard section names** — Experience, Education, Skills. Avoid creative headings.
3. **Mirror JD keywords** — use the exact phrasing from the job description.

```python
# ATS keyword matching example
job_description_keywords = ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"]

resume_skills = ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"]

matched = len(set(job_description_keywords) & set(resume_skills))
total = len(job_description_keywords)
match_rate = (matched / total) * 100

print(f"Keyword match rate: {match_rate}%")
# Output: Keyword match rate: 100.0%
```

### Formats to Avoid

- Two-column layouts (ATS confuses reading order)
- Important info in headers/footers (ATS skips them)
- Text rendered as images (OCR failure risk)

A resume must pass ATS first, then convince the human reviewer. Design for both audiences.

## Resume Structure Template: Pass the 30-Second Scan

Reviewers do not read resumes leisurely — they decide in 30 seconds whether to advance you. Information order accounts for half the persuasion.

| Section | Recommended length | Include | Avoid |
| --- | --- | --- | --- |
| Header | 1 line | Name, contact, GitHub/LinkedIn | Address, unnecessary personal info |
| Summary | 2–3 lines | Role, tenure, headline metric | Personality descriptions |
| Experience | 3–5 bullets per role | Problem, action, result, number | Responsibility lists |
| Projects | 2–4 entries | Link, contribution scope, metric | Non-functional demos |
| Skills | 1 block | Only tech used in sections above | Keyword flooding |

The summary matters most. "Backend 3 yrs, cut payment API p95 from 210ms to 95ms" lets the reader anchor immediately.

## STAR Bullet Comparison

Below are weak versus strong versions of the same experience.

| Weak sentence | Strong sentence |
| --- | --- |
| Worked on the payment API. | Redesigned the bottleneck query in the payment API, cutting p95 from 210ms to 95ms. |
| Handled incident response. | Reduced a twice-weekly batch failure to less than once per month via retry policies and alarm tuning. |
| Conducted code reviews. | Introduced a review template that lowered average PR re-request count from 3.1 to 1.7. |

The key shift is from "what I did" to "what changed because I did it."

## Portfolio Connection Structure

A portfolio is not a project list — it is a collection of evidence links. Structure each entry so the reviewer can verify claims quickly.

1. **Problem definition**: What user or business problem did this solve?
2. **Design choice**: Why this architecture over alternatives?
3. **Result metric**: What improved — latency, reliability, adoption?
4. **Reproduction link**: Repo, live demo, docs, or presentation slides.

This structure lets hiring managers cross-reference claim and proof in seconds.

## Job Posting → Resume Mapping Sheet

Instead of writing a generic resume first, deconstruct the job posting and map your evidence to each requirement.

| Posting requirement | My evidence | Resume sentence | Proof link |
| --- | --- | --- | --- |
| High-traffic API operation | Order API p95 420ms→260ms | "Reduced p95 by 38% via cache policy and index tuning" | Project README, dashboard screenshot |
| Test automation | Introduced pytest, reduced regressions | "Expanded test suite from 0 to 65 cases on core modules" | Test report |
| Collaboration / communication | Aligned release criteria with PM | "Standardized deploy checklist across 3 teams" | ADR document |

Building this table for each application dramatically cuts customization time. The critical insight: do not copy-paste the same bullets. Reorder them to match the posting's priority — screening often hinges on the top five bullets.

## Portfolio Quality Checklist

A portfolio should show "what problem I validated" more than "what I built." Use this checklist before submission.

| Item | Pass criteria | Fail signal |
| --- | --- | --- |
| Problem definition | User/business problem stated in one sentence | Only feature descriptions |
| Technology choice rationale | At least one alternative compared | "Used because I know it" |
| Operational perspective | Logging, error handling, deploy strategy included | Local-run instructions only |
| Result metric | Speed, error rate, or completion rate with numbers | Abstract "improved" claims |
| Reproducibility | Runnable from README alone | Missing environment setup |

Review against this checklist at least twice before submission. The result metric row is easiest to neglect — design measurement into the project from the start, not as an afterthought.

## How Interviewers Read a Portfolio

Interviewers typically scan a portfolio in under five minutes. They follow a predictable order — design your layout to match it.

1. Is the problem definition clear?
2. Is there a rationale for the technology choice?
3. Are results proven with numbers?
4. Are failures and corrections documented?

Arrange your documentation to answer these four questions in sequence, and perceived credibility rises significantly.

## What to Notice in This Code

- Bullets are result sentences, not activity logs.
- Numbers are evidence — they let the reader calibrate scope instantly.
- STAR provides a short narrative arc that holds attention.

## Five Common Mistakes

1. **Listing only responsibilities** — "participated" and "collaborated" convey no outcome.
2. **No numbers** — claims without metrics are unverifiable.
3. **Portfolio-resume mismatch** — links that contradict or fail to support bullets erode trust.
4. **ATS-hostile formats** — two-column PDFs or image-based text get silently filtered out.
5. **Resume longer than two pages** — dense evidence beats exhaustive history.

## How This Shows Up in Production

Big companies require a short internal resume even for internal transfers. The skill of writing outcome-oriented bullets applies to promotion packets, peer feedback, and performance reviews — not just external job applications.

## How a Senior Engineer Thinks

- The resume is an ad, not a memoir.
- Numbers are king — they compress trust into one glance.
- STAR is the frame that turns experience into a story.
- ATS is reality — design for the machine first, then the human.
- Portfolio is evidence — every claim must link to proof.

## Checklist

- [ ] Three-line summary with role, tenure, and one headline number.
- [ ] Five experience bullets with quantified outcomes.
- [ ] Portfolio link with verifiable demos or repos.
- [ ] PDF and plain-text-friendly format (no two-column, no image text).

## Practice Problems

1. Define STAR in one sentence.
2. Define ATS in one sentence.
3. Write one example of a numeric experience bullet.

## Wrap-up and Next Steps

A strong resume and portfolio are not about packaging experience attractively — they are about transmitting results and evidence fast. When role, numbers, outcomes, and links are clearly visible, the reader naturally formulates the next question to ask you in an interview. The next post covers how to prepare for coding interviews.

## Answering the Opening Questions

- **What structure lets a recruiter understand you quickly without guessing?**
  - A resume should record not past companies and tech stacks, but the size of problems you handled and what you learned solving them — compressed into a three-line summary and STAR bullets.
- **How do you rewrite responsibilities into outcome-oriented bullets?**
  - Replace "participated in X" with "changed Y metric from A to B by doing Z" — the STAR structure forces you to name the delta.
- **Why are numbers and STAR such strong hiring signals?**
  - Evaluators scan in 3-5 minutes. Numbers compress scope and credibility into a single glance; STAR gives a narrative arc that is easy to verify in an interview.
<!-- toc:begin -->
## In this series

- [Developer Career 101 (1/10): What Is a Developer Career](./01-what-is-developer-career.md)
- [Developer Career 101 (2/10): Understanding Roles](./02-understanding-roles.md)
- [Developer Career 101 (3/10): Building a Learning Plan](./03-learning-plan.md)
- **Resume and Portfolio (current)**
- Preparing for Coding Interviews (upcoming)
- System Design Interviews (upcoming)
- Settling into the First Job (upcoming)
- Side Projects and Learning (upcoming)
- Mentoring and Networking (upcoming)
- The Path to Senior (upcoming)

<!-- toc:end -->

## References

- [Google Careers — Resume tips](https://careers.google.com/how-we-hire/)
- [LinkedIn Talent Blog](https://business.linkedin.com/talent-solutions/blog)
- [The Muse — STAR method overview](https://www.themuse.com/advice/star-interview-method)
- [GitHub Docs — Profile README basics](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/about-your-profile)

Tags: Career, Resume, Portfolio, Hiring, Beginner
