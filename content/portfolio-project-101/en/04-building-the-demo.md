---
series: portfolio-project-101
episode: 4
title: "Portfolio Project 101 (4/10): Building the Demo"
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
  - Demo
  - UX
  - Showcase
  - Beginner
seo_description: How to design a portfolio demo so a first-time visitor can understand the value quickly instead of getting stuck early.
last_reviewed: '2026-05-15'
---

# Portfolio Project 101 (4/10): Building the Demo

A README alone is not enough. A portfolio project becomes much more convincing when another person can click around and feel the value directly. If there is no demo, or if the first screen is empty, or if the login step blocks everything, the reviewer often leaves before the project has a chance to explain itself.

This is the 4th post in the Portfolio Project 101 series. Here we will treat the demo not as a feature showroom, but as a short experience that lets a first-time visitor understand the core value within the first few clicks.

---

> A good demo does not need to show everything. It needs to make the core value obvious quickly.


![portfolio project 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/portfolio-project-101/04/04-01-concept-at-a-glance.en.png)
*portfolio project 101 chapter 4 flow overview*
> Code without demonstration doesn't convince anyone. A live proof that the project actually runs, and can be inspected by any visitor, creates trust.

## Questions to Keep in Mind

- Why is the first screen the most important part of a portfolio demo?
- What do seed data and a shared demo account solve?
- What role does a backup video play when the live demo is not enough?

## Why It Matters

A live demo makes the project feel alive. Without it, the reviewer is still depending on your description. With it, they can verify the project on their own terms.

That does not mean you need to expose every feature. Portfolio demos are usually stronger when they focus on one sharp path and remove friction from the first experience.

## Mental Model

A useful demo often follows a short path: landing screen, sample context, one action, visible result, then a next step.

This flow helps you decide what to remove. Most visitors do not want a full feature tour. They want to know what the product does, why it matters, and whether it really works.

## Key Terms

- **First screen**: the first surface the visitor sees after opening the demo.
- **Seed data**: sample data that prevents the product from looking empty.
- **Shared account**: a low-friction way to let people try the system.
- **Backup video**: a short fallback proof when the live demo has trouble.
- **Failure path**: the route you use to understand what broke when the demo misbehaves.

## Before and After

**Before**: the visitor logs in and lands on a blank or confusing screen.

**After**: the first screen already contains enough context to explain the core workflow, and one short action produces a visible result.

The goal is not completeness. It is immediate legibility.

## Step by Step

### Step 1 — Define the demo scenario

Start by compressing the core journey into a few steps.

The demo flow is usually clear enough when you reduce it to these four stages:

- `land`
- `sample`
- `action`
- `result`

This protects the demo from turning into a feature maze.

### Step 2 — Prepare seed data

Blank states are often terrible portfolio experiences.

Even seed data as small as `5 users` and `12 tasks` can make the first screen feel much more real.

The seed gives the visitor context immediately. A scheduling app should show schedules. An analytics app should show a realistic example result.

### Step 3 — Offer a shared path

The project is much easier to inspect when the reviewer can try it without setup friction.

For example, you can offer a shared demo account such as `guest@demo / demo1234`.

A shared account or another guided access path keeps the reviewer from burning time before they reach the actual value.

### Step 4 — Keep a backup video

Live demos are powerful, but they are not always reliable.

Keep a backup video link ready, such as `https://youtu.be/example`.

A short backup video prevents one hosting hiccup from turning into a total explanation failure.

### Step 5 — Expose a health check

You need a quick way to separate “the link is broken” from “the app is down.”

A small route like `/healthz` is often enough for that first check.

Health checks are not just for infrastructure. They help you keep the demo trustworthy over time.

## What to Notice in the Code

- The first screen should prove value, not just show navigation.
- Seed data and shared access reduce the friction that makes many demos feel empty.
- Backup proof and health checks make the demo feel maintained, not accidental.

## Common Mistakes

1. The visitor gets stuck at login before seeing any meaningful value.
2. The product opens in an empty state with no context.
3. The only usable account is private.
4. The live demo fails and there is no backup evidence.
5. There is no quick path to confirm whether the service itself is healthy.

For portfolio demos, the number of friction points usually matters more than the number of features.

## How This Reads in Practice

Real SaaS teams spend a lot of time on guest mode, sample data, and the first-time user path for exactly this reason: people want to feel value quickly. Portfolio projects benefit from the same thinking.

If you make one convincing path obvious, the whole project feels stronger.

## Checklist

- [ ] The demo scenario fits into a few steps.
- [ ] The first screen includes sample data or a visible result.
- [ ] There is a shared account or another low-friction access path.
- [ ] A backup video exists in case the live demo is unavailable.

## Practice Problems

1. Rewrite your demo as a four-step scenario.
2. Choose one sample data point that should be visible immediately.
3. Decide what proof you would show if the live demo went down.

## Wrap-up and Next Steps

A strong demo does not have to show every feature. It should show context on the first screen, let the reviewer take one meaningful action, and produce a clear result. When you add a shared path, a backup video, and a health check, even a small project starts to feel much more real.

Next, we will look at deployment and at what makes a portfolio project verifiable from a public URL instead of only from your machine.

## Appendix: User Story and Acceptance Criteria Example

Start with a clear user story that drives the demo design.

```markdown
- As a team lead,
  I want to see all team schedules in one calendar,
  so that I can finalize weekly planning in 10 minutes.

Acceptance Criteria:
1. After login, the weekly view loads immediately.
2. When I select a team member filter, schedules update within 1 second.
3. After generating a share link, the same view opens in another browser.
```

A story-driven design connects demo prep to test cases. It also makes it easy to explain later why you showed this flow.

## Appendix: Demo Script by Duration

In real demos, time is always scarce. Prepare two scripts: one for 30 seconds, one for 90 seconds.

| Section | 30s Script | 90s Script |
| --- | --- | --- |
| Setup | Problem (1 sentence) | Problem + existing workaround |
| Showcase | One core action | Two actions + one edge case |
| Outcome | Result screen | Result + metrics + architecture |

**30-second script:**

```markdown
1. "Team schedules are scattered across three tools, making weekly planning take 40+ minutes."
2. "Here when I select the team, the weekly view filters instantly."
3. "Planning time dropped from 40 to 18 minutes."
```

Pre-written scripts prevent nervous stumbles. They also keep the focus on value, not feature count.

## Appendix: Pre-Demo Failure Checklist

Most demo failures are preventable. This checklist catches the common ones.

| Failure Point | Root Cause | Prevention |
| --- | --- | --- |
| Blank landing | No seed data | Auto-load sample data |
| Login block | No shared account | Document guest credentials |
| Slow response | Overloaded init | Add cache layer / loading message |
| Demo crashes | Deployment instability | Keep backup video + health check |

Demos are closer to UX design than engineering showcase. Focus on whether a visitor can feel the value within 30 seconds.

## Appendix: Demo Video Scripting by Duration

When the live demo is risky, a short backup video is essential. Make it a 30-second or 90-second proof of value, not a full feature tour.

**30-second video template**

```text
[0:00-0:05] Problem statement (caption or voiceover)
  'Team schedules spread across Notion, Google Calendar, and Jira took 40+ minutes to consolidate.'

[0:05-0:20] One core action
  - Open browser -> select team -> filter schedules
  - Move cursor slowly so viewers can follow

[0:20-0:30] Result + CTA
  'Planning time reduced from 40 to 18 minutes. Check the README to run locally.'
  - Show GitHub repo URL on screen
```

**90-second video template**

```text
[0:00-0:10] Problem + existing workaround
  'Consolidating schedules from three tools into a weekly plan.'

[0:10-0:40] Two core actions
  Action 1: select team -> auto-filter (weekly view)
  Action 2: detect conflict -> auto-create alert

[0:40-0:55] Edge case handling
  - Network offline -> local cache works
  - New team member with no data -> handled gracefully

[0:55-1:10] Results + architecture
  'FastAPI + React + PostgreSQL. Planning time down 55%. After adding conflict alerts, meeting cancellations dropped 70%.'

[1:10-1:30] Next steps + CTA
  'OAuth and Slack alerts coming next. See README for how to run locally.'
```

The difference is clear: 30s shows problem-action-result once. 90s adds edge cases and depth. In interviews, start with 30s and ask 'Want to see more?'

## Appendix: Recording Environment Setup

Video quality matters. Use this config to keep quality high with free tools.

```yaml
# demo-recording-config.yml
recording:
  tool: OBS Studio (free) or macOS QuickTime
  resolution: 1920x1080
  fps: 30
  format: MP4 (H.264)
  max_file_size: 50MB  # GitHub README embedding limit

browser:
  zoom: 110%  # improve text readability
  bookmarks_bar: hidden
  extensions: disabled  # remove icon clutter
  tab_count: 1  # only demo tab open

terminal:
  font_size: 16pt
  theme: dark (high contrast)
  prompt: $ only (no path noise)
  history: clear  # hide previous commands

post_processing:
  tool: FFmpeg (free)
  trim_silence: true
  speed_up_typing: 1.5x  # cut typing wait time
  add_subtitles: true  # support muted environments
```

**Pre-recording checklist:**

```text
[ ] Disable all notifications (Slack, mail, OS)
[ ] Clean desktop (hide personal files)
[ ] Use incognito browser or fresh profile
[ ] Confirm resolution at 1920x1080
[ ] Test microphone (if narrating)
[ ] Verify seed data loads
[ ] Set recording area (full screen or app window)
```

After recording, always play it back muted. If the flow is clear without sound, it will work in an office or on mobile.

## Appendix: GIF vs Video — When to Use Each

README demos can use GIF or video link. Choose based on context.

| Criteria | GIF | Video (YouTube/Loom) |
| --- | --- | --- |
| Auto-play | Auto in GitHub | Click required |
| File size | 5-15MB (10s) | Unlimited |
| Length | 10s max recommended | Unlimited |
| Narration | No | Yes |
| Edit flexibility | Re-record | Trim clips |
| Best use | Single action | Full workflow |

The most effective strategy: GIF at the top (5-10s, one core action) + 'Full video' link below. GIF catches attention, video provides depth.

**GIF creation from video:**

```bash
# FFmpeg: MP4 -> GIF (10 sec, 800px width)
ffmpeg -i demo.mp4 -t 10 -vf "fps=15,scale=800:-1:flags=lanczos" \
  -gifflags +transdiff demo.gif

# If file size exceeds 10MB, reduce frame rate
ffmpeg -i demo.mp4 -t 8 -vf "fps=10,scale=640:-1:flags=lanczos" \
  -gifflags +transdiff demo-small.gif
```

## Appendix: Seed Data Design

Empty screens are a demo killer. Good seed data makes the first view meaningful.

```python
# scripts/seed_demo_data.py
"""Generate demo seed data.

Run: python scripts/seed_demo_data.py
Goal: first-time visitors see meaningful data, not blank screens
"""
import json
from pathlib import Path

SEED_DATA = {
    "teams": [
        {"name": "Backend", "members": ["Alice", "Bob", "Charlie"]},
        {"name": "Frontend", "members": ["Diana", "Eve"]},
    ],
    "tasks": [
        {
            "title": "Implement API response caching",
            "assignee": "Alice",
            "status": "in_progress",
            "due": "2024-03-20",
        },
        {
            "title": "Redesign login page",
            "assignee": "Diana",
            "status": "done",
            "due": "2024-03-15",
        },
        {
            "title": "Add E2E tests",
            "assignee": "Bob",
            "status": "todo",
            "due": "2024-03-25",
        },
    ],
}


def seed(output_path: Path = Path("data/seed.json")) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(SEED_DATA, ensure_ascii=False, indent=2))
    print(f"Seed data written to {output_path}")


if __name__ == "__main__":
    seed()
```

**Seed data principles:**

1. **Real-looking names and values**: use actual domain words, not 'test1' or 'foo'.
2. **Variety of states**: mix todo, in_progress, done so the screen looks rich.
3. **Right quantity**: not too sparse, not too crowded. 5-15 items usually works.
4. **Reproducible**: script it so you can reset to clean slate anytime.

## Appendix: Demo Health Check Automation

A dead live link is worse than no link. Keep a simple health check running.

```yaml
# .github/workflows/demo-health.yml
name: Demo Health Check
on:
  schedule:
    - cron: '0 9 * * 1'  # every Monday at 9am
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Check demo is alive
        run: |
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://my-demo.vercel.app)
          if [ "$STATUS" != "200" ]; then
            echo "Demo is down! Status: $STATUS"
            exit 1
          fi
          echo "Demo is healthy (HTTP $STATUS)"

      - name: Notify on failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {"text": "Portfolio demo is down! Check https://my-demo.vercel.app"}
```

A weekly check prevents 'it died last month and I didn't notice.' Reviewers need to find it alive the moment they click.

## Appendix: Demo Context Template

Never share a demo link alone. Always provide context.

**Email/chat template:**

```text
Hi,

I built a team schedule unification tool.
- Live demo: https://task-tracker-demo.vercel.app
- Guest account: guest@demo.com / demo1234
- 30-second video: https://youtube.com/watch?v=xxx

The core feature is selecting a team, then seeing the filtered weekly schedule.
Happy to answer questions.
```

**README demo section:**

```markdown
## Demo

| Format | Link | Note |
|--------|------|------|
| Live | [task-tracker.vercel.app](url) | Guest: guest@demo.com / demo1234 |
| Video | [30-second demo](youtube-url) | Captions included, muted-friendly |
| GIF | See below | One core action |

![Core feature](./assets/demo.gif)
```

The goal is simple: whether the reviewer clicks live, watches video, or opens GIF, they see value in 30 seconds. Demo is about speed of understanding, not feature count.

## Answering the Opening Questions

- **Why is the demo's first screen the most important evaluation point?**
  - Visitors judge the project's value on the first screen. If the first screen is empty or behind a login wall, they leave without checking even brilliant internal logic. Seed data and guest accounts must make the core feature immediately experienceable.
- **What problems do seed data and shared accounts solve?**
  - Seed data solves the empty-screen problem, and shared accounts remove the login barrier. Both are tools for creating a state where visitors can see core functionality without any preparation.
- **What is the role difference between a live demo and a backup video?**
  - A live demo proves real-time interaction but carries outage risk. A backup video is stable but non-interactive. Using both ensures the demo is delivered regardless of circumstances.
<!-- toc:begin -->
## In this series

- [Portfolio Project 101 (1/10): What is a Portfolio Project](./01-what-is-a-portfolio-project.md)
- [Portfolio Project 101 (2/10): Traits of a Good Project](./02-traits-of-a-good-project.md)
- [Portfolio Project 101 (3/10): Writing the README](./03-writing-the-readme.md)
- **Building the Demo (current)**
- Deploying the Project (upcoming)
- Tests and Documentation (upcoming)
- Recording Tech Decisions (upcoming)
- Summarizing as Blog Posts (upcoming)
- Explaining in Interviews (upcoming)
- Portfolio Improvement Checklist (upcoming)

<!-- toc:end -->

## References

- [Great Demo!](https://greatdemo.com/)
- [The Mom Test](https://momtestbook.com/)
- [Open Source Guides — Building welcoming communities](https://opensource.guide/building-community/)
- [About issue and project templates (GitHub Docs)](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)

Tags: Portfolio, Demo, UX, Showcase, Beginner
