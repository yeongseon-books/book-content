---
series: portfolio-project-101
episode: 9
title: "Portfolio Project 101 (9/10): Explaining in Interviews"
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
  - Interview
  - STAR
  - Communication
  - Beginner
seo_description: How to explain a portfolio project in interviews using a short STAR-shaped answer with numbers, trade-offs, and lessons.
last_reviewed: '2026-05-15'
---

# Portfolio Project 101 (9/10): Explaining in Interviews

Interview answers do not get stronger just because they get longer. In most cases, a tighter explanation of the problem, the decision, and the result is much more persuasive than a broad tour of every library in the stack. Interviewers usually want to hear judgment, not a dependency list.

This is the 9th post in the Portfolio Project 101 series. Here we will shape a portfolio project into a short interview answer that makes the problem, the action, and the result easy to follow under time pressure.

---

> A strong interview answer is not a product pitch. It is a compressed record of problem, task, action, result, and learning.


![portfolio project 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/portfolio-project-101/09/09-01-concept-at-a-glance.en.png)
*portfolio project 101 chapter 9 flow overview*
> The same project can emphasize architecture decisions in a technical interview and problem-solving process in a behavioral interview. Matching your explanation to the audience builds trust.

## Questions to Keep in Mind

- What do interviewers usually want to hear before they care about implementation detail?
- Why is the STAR structure especially useful for short project answers?
- How do numbers and trade-offs change the credibility of the answer?

## Why It Matters

Interviews are short, and people remember stories more than stacks. Many candidates have touched similar tools. Fewer can explain a project as a chain of problem, decision, and result.

The first minute or two matters a lot because it shapes the quality of the follow-up questions. If the initial answer is vague, the rest of the conversation tends to stay vague too.

## Mental Model

A project answer becomes much easier to control when it follows situation, task, action, and result.

This structure prevents a common failure mode: jumping straight into implementation without first explaining why the project existed or what success looked like.

## Key Terms

- **Answer structure**: the order that keeps the explanation easy to follow.
- **Short summary answer**: a project explanation that fits into about two minutes.
- **Trade-off**: what you gained and what you knowingly accepted as a cost.
- **Metric**: a number that supports the result.
- **Follow-up question**: the deeper question that comes after your first explanation lands.

## Before and After

**Before**: “I built an API with Flask.”

**After**: “I built a scheduling tool to unify scattered team schedules, used Flask plus PostgreSQL to keep the first version simple, and kept average response time around 120 ms for a 30-user pilot.”

Both may be true, but the second answer gives the interviewer a problem, a design choice, and a result in a single pass.

## Step by Step

### Step 1 — Situation

Open with the real context that made the project worth building.

For example, you might open with the real pain point: the team schedule kept getting lost across tools.

The situation should be concrete enough that the interviewer can picture the pain quickly.

### Step 2 — Task

State what the project needed to accomplish.

Then name the task clearly: show every schedule on a single screen.

That line clarifies scope and makes later trade-offs easier to explain.

### Step 3 — Action

Describe what you actually did and why that path made sense.

In the action step, it is usually enough to name the key choices:

- `Flask API`
- `PostgreSQL`
- `Deploy to Render`

The tools matter less than the reason they were chosen. One sentence about why you picked the path often does more work than three sentences of implementation detail.

### Step 4 — Result

Give the interviewer at least one number.

For example, attach numbers such as `30 users` and `120ms average latency`.

Metrics create evidence. They do not need to be huge. They need to be real.

### Step 5 — Lesson

Close with what the project taught you.

Close with the lesson you would reuse: small MVPs survive.

That line is often what turns a build log into an engineering answer.

## What to Notice in the Code

- STAR is not a memorization trick. It is a way to stabilize the explanation order.
- Metrics do the work of proof.
- The lesson gives the answer a strong closing line and a natural bridge to follow-up discussion.

## Common Mistakes

1. Listing technologies without explaining the problem or result.
2. Giving no numbers, so the scale and impact stay abstract.
3. Avoiding trade-offs, which makes the answer sound shallow.
4. Blurring personal contribution in a group project.
5. Ending without a lesson or reflection.

Those mistakes often leave the interviewer wondering whether the candidate really understood the project end to end.

## How This Reads in Practice

Teams use the same basic structure when they write retrospectives or summarize incidents: what happened, what needed to be done, what action was taken, and what happened next. Interview answers work well for the same reason.

The goal is not to sound rehearsed. The goal is to sound clear.

## Checklist

- [ ] I can finish the answer in about two minutes.
- [ ] The answer includes at least one metric.
- [ ] I can name at least one trade-off.
- [ ] I can end with one lesson I would reuse.

## Practice Problems

1. Rewrite your project in four sentences using STAR.
2. Choose one number that should appear in the result.
3. Name one technical choice and explain why an alternative was rejected.

## Wrap-up and Next Steps

Explaining a portfolio project well is about structure, not volume. When situation, task, action, result, and lesson appear in a clean order, the answer becomes easier to follow and much easier to trust. Add one real metric and one real trade-off, and the same project suddenly sounds far more mature.

Next, we will close the series with a final checklist you can use before sharing a portfolio project publicly.

### Postmortem Structure Comparison

Teams use nearly identical structures when writing postmortems and retrospectives: situation, task, action, result, and lesson learned. Interview answers work well for the same reason.

| Aspect | Postmortem | Interview Answer |
| --- | --- | --- |
| Situation | When incident occurred and scope of impact | Project context and problem |
| Task | Recovery goal (MTTR, minimize impact) | Problem to solve |
| Action | Timeline of steps taken | Technical choices and implementation |
| Result | Time to recovery, affected users | Metrics, user response, deployment result |
| Lesson | Actions to prevent recurrence | Learning from the project |

```text
Postmortem example (summary):
- Situation: 2024-03-15 14:00 UTC, payment API timeout spike
- Task: Restore 99.9% success rate within 30 minutes
- Action: Identified DB connection pool exhaustion → increased pool size 20→50 → added slow query index
- Result: Recovered at 14:22, ~1,200 affected users, zero revenue loss (retries succeeded)
- Lesson: Add connection pool monitoring alerts, establish weekly slow query review
```

Apply that same structure to an interview answer:

```text
Interview answer conversion:
"I experienced a payment API timeout spike. (Situation)
We needed to restore normal response rates within 30 minutes. (Task)
I identified connection pool exhaustion and expanded the pool size, then added an index on slow queries. (Action)
We recovered in 22 minutes, and I added connection pool monitoring afterward. (Result)
The lesson was that resources without monitoring can fail at any time."
```

If you have production experience, converting postmortems to STAR format is the most effective interview prep. For portfolio projects, you can reframe development challenges (bugs, architecture decisions, scope trade-offs) using the same structure.

### Explaining Contribution in a Group Project

The most common mistake when explaining a team project is starting with "we built...". Interviewers care far more about your personal contribution and decisions than about the team's aggregate output.

**Three principles for making contribution clear:**

1. **State role boundaries first**: "In a 4-person team, I owned the backend API and CI/CD pipeline."
2. **Identify decision ownership**: "The choice I proposed and we adopted was..."
3. **Quantify contribution**: "I made 87 of 250 commits (35%), built 8 of 12 API endpoints."

```python
# Team contribution template
contribution = {
    "team_size": 4,
    "my_role": "Backend API + CI/CD pipeline",
    "key_decisions": [
        "DB choice: SQLite to PostgreSQL migration proposal",
        "Test strategy: pytest + GitHub Actions CI adoption",
    ],
    "quantified": {
        "commits": "87 / 250 (35%)",
        "endpoints_built": "8 / 12",
        "test_coverage_contribution": "45 unit tests written",
    },
}
```

**Phrases to avoid and alternatives:**

| Avoid | Use Instead |
| --- | --- |
| "We built it together" | "The part I owned was..." |
| "We all did everything" | "I proposed and implemented..." |
| "Great teamwork" | "When opinions clashed, I bridged by..." |
| "Good collaboration" | "I wrote the API spec so frontend could develop in parallel" |

Being specific about your contribution in a group project does not diminish teammates. It helps the interviewer understand what kind of role you play in a team.

### Creating Metrics When Numbers Are Scarce

Portfolio projects may have few or no real users. You can still create numbers.

**Types of measurable metrics:**

| Category | Example Metrics | How to Measure |
| --- | --- | --- |
| Performance | Response time, throughput | k6, locust, time command |
| Quality | Test coverage, lint pass rate | pytest --cov, ruff |
| Scale | Lines of code, number of endpoints | cloc, manual count |
| Efficiency | Dev time, commit count, PR count | git log --oneline \| wc -l |
| Automation | CI build time, deployment frequency | GitHub Actions logs |

```bash
# Example: collect project metrics
echo "=== Project Scale ==="
cloc src/ --quiet
echo ""
echo "=== Test Coverage ==="
pytest --cov=src --cov-report=term-missing --quiet 2>/dev/null | tail -3
echo ""
echo "=== Development Timeline ==="
git log --format='%ai' | tail -1  # first commit
git log --format='%ai' | head -1  # last commit
echo ""
echo "=== Commit Count ==="
git log --oneline | wc -l
```

In an interview, you might say:

- "I completed the MVP in two weeks with 87 commits."
- "I maintained 82% test coverage across 12 API endpoints."
- "I load-tested with k6 and confirmed the system handles 50 concurrent users with response times under 200ms."

The size of the number matters less than the fact that you measured. "Performance is good" is a subjective claim, but "120ms average response time" is evidence. That shift changes how the interviewer hears your answer.

As a bonus, if you forget the exact number on interview day, storing metrics in your README or ADRs reduces prep time significantly. And if you include measurement scripts in your CI, the numbers update on every deploy—no need to measure again the day before the interview.

Interviews are ultimately a trust game. Numbers are the fastest tool to build it.

### Demo Video Script Structure (for Interview Submission)

More and more interviews now ask for a 2–3 minute demo video alongside your portfolio link. The video should show problem-solving narrative rather than feature listing.

| Segment | Time | Core Message |
| --- | --- | --- |
| Opening | 20s | What problem does the project solve |
| Core demo | 90s | The actual change the user sees |
| Technical choice | 40s | Why you chose this architecture |
| Results and learning | 30s | Metrics and next improvement ideas |

```markdown
Opening example:
"I built this project to solve the problem of team schedules scattered across tools, which was eating up prep time for planning meetings."
```

This script is STAR-compatible. The structure you demonstrate in the video can be reused directly in the interview, reducing prep overhead.

### Presentation Slide Structure (5-slide template)

When an interview includes a presentation, slide density matters more than slide count. The 5-slide structure below is recommended:

1. Problem definition: user, situation, inconvenience
2. Solution approach: scope and architecture choices
3. Core demo: the most critical user flow
4. Results metrics: performance or usability improvement
5. Retrospective: trade-offs and next steps

| Slide | Include | Avoid |
| --- | --- | --- |
| Problem | Real user quote | List of tech stack |
| Approach | Three decision criteria | Too many code screenshots |
| Results | Before/after metrics | Vague "improved" language |

Slides exist to invite good questions, not to hide depth. When you show core decisions upfront, follow-up questions tend to be more meaningful.

### Expected Follow-up Questions Reference Table

Interview prep is more effective with question taxonomy than memorization. Prepare basic answer axes by question type, and you can maintain structure even under pressure.

| Question Type | Example | Answer Axis |
| --- | --- | --- |
| Problem definition | Why did you pick this problem? | User pain + scope impact |
| Tech choice | Why FastAPI? | Constraints + alternative comparison |
| Quality | How did you structure tests? | Unit / integration / CI flow |
| Operations | What if deployment fails? | Runbook + rollback procedure |
| Growth | What is next? | Priority + risk |

With this table as a foundation, prepare two versions of each answer—a 1-minute version and a 3-minute version—and you can handle most interview formats. The interviewer's follow-ups will often fall into these buckets, so your prep translates directly.

### 2-Minute Answer Template (structure, not memorization)

In interviews, remember structure, not words. Fill in the template below with your project, and you can answer most opening questions:

```markdown
[Situation] One sentence about what user or team pain existed.
[Task] One sentence about the goal.
[Action] Two core choices + one reason.
[Result] One or two metrics.
[Lesson] One sentence about what you'd carry forward.
```

### Interview Type Strategy: Technical vs. Behavioral

The same project emphasizes different things depending on interview type.

| Aspect | Technical | Behavioral |
| --- | --- | --- |
| Core message | Architecture decisions and technical depth | Collaboration, overcoming challenges, growth |
| Code mention | Handling logic, design choices | Minimal (context only) |
| Metrics focus | Performance, reliability, scalability | User impact, team contribution |
| Trade-offs | Technical alternatives | Priority decisions |
| Expected follow-up | "How would you scale?" "How would you handle failure?" | "Any conflicts?" "What if you failed?" |

To handle both, prepare two versions of your answer: the technical version emphasizes "why this architecture", the behavioral version emphasizes "what challenges did I overcome and what did I learn".

### The Structure for "I Don't Know"

When an unexpected question comes up in an interview, ending with "I don't know" closes the conversation. This structure keeps it open:

```text
1. Admit honestly: "I haven't had experience with that yet."
2. Connect a similar experience: "But I have worked with..."
3. Show learning intent: "Next, I'd explore..."
```

Example:
- "I haven't handled large-scale traffic. However, I kept response time at 120ms for 30 concurrent users, and if scaling were needed, I'd start by adding a cache layer."

This reframes "I don't know" as "I haven't had that experience, but I know how to learn."


## Answering the Opening Questions

- **What do interviewers want to hear more than code volume?**
  - Interviewers want to hear what problem you understood and what criteria drove your decisions, not how much code you wrote. Answers where the judgment process is audible are strongest.
- **Why is the STAR structure particularly powerful in short answers?**
  - STAR arranges Situation-Task-Action-Result in order matching the interviewer's comprehension flow. Even finishing in two minutes, structure makes value transmit.
- **How do numbers and tradeoffs change an answer's persuasiveness?**
  - "Performance improved" is subjective, but "280ms down to 120ms" is evidence. Stating tradeoffs alongside signals "I truly understood and chose."
<!-- toc:begin -->
## In this series

- [Portfolio Project 101 (1/10): What is a Portfolio Project](./01-what-is-a-portfolio-project.md)
- [Portfolio Project 101 (2/10): Traits of a Good Project](./02-traits-of-a-good-project.md)
- [Portfolio Project 101 (3/10): Writing the README](./03-writing-the-readme.md)
- [Portfolio Project 101 (4/10): Building the Demo](./04-building-the-demo.md)
- [Portfolio Project 101 (5/10): Deploying the Project](./05-deploying-the-project.md)
- [Portfolio Project 101 (6/10): Tests and Documentation](./06-tests-and-documentation.md)
- [Portfolio Project 101 (7/10): Recording Tech Decisions](./07-recording-tech-decisions.md)
- [Portfolio Project 101 (8/10): Summarizing as Blog Posts](./08-summarizing-as-blog-posts.md)
- **Explaining in Interviews (current)**
- Portfolio Improvement Checklist (upcoming)

<!-- toc:end -->

## References

- [How to use the STAR interview response technique](https://www.indeed.com/career-advice/interviewing/how-to-use-the-star-interview-response-technique)
- [Google re:Work — Structured interviewing](https://rework.withgoogle.com/guides/hiring-use-structured-interviewing/steps/introduction/)
- [The Tech Resume Inside Out](https://thetechresume.com/)
- [The Manager's Path](https://www.oreilly.com/library/view/the-managers-path/9781491973882/)

Tags: Portfolio, Interview, STAR, Communication, Beginner
