---
series: devops-101
episode: 1
title: "DevOps 101 (1/10): What Is DevOps?"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - DevOps
  - Culture
  - CI
  - CD
  - Engineering
seo_description: The definition, principles, and first practical steps for DevOps that bridges development and operations.
last_reviewed: '2026-05-15'
---

# DevOps 101 (1/10): What Is DevOps?

Most teams do not fail because they lack tools. They fail because code review, deployment, monitoring, and incident response all live in different conversations. One team says the feature is done. Another team says production is unstable. The handoff itself becomes the bottleneck.

DevOps is the attempt to remove that handoff cost. It gives one team a shared feedback loop for building, shipping, operating, and learning, so deployment speed and operational stability stop pulling in opposite directions.

This is the first post in the DevOps 101 series. In this chapter, we set the mental model for the rest of the series: DevOps is not a tool purchase but a way to shorten the path from change to feedback.


![devops 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/01/01-01-concept-at-a-glance.en.png)
*devops 101 chapter 1 flow overview*
> DevOps succeeds when you treat *deployment speed* and *operational stability* as *one goal*, not opposing forces.

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Is DevOps??
- Which signal should the example or diagram make visible for What Is DevOps??
- What failure should be prevented first when What Is DevOps? reaches a real system?

## Questions this article answers

- What is *DevOps*, and why did treating *development* and *operations* as separate worlds start to hit its limits?
- Why is *DevOps* described as a *culture* rather than just a collection of *tools*?
- What roles do terms like *CI*, *CD*, and *SRE* play inside the *DevOps* flow?
- If you want to start *DevOps* in practice, which kinds of *automation* should you usually add first?
- What are the most common traps that make teams think they are doing *DevOps* when they are not?

## Why It Matters

Software produces no value when *only built*. It must be *deployed* and *operated* to reach users. *DevOps* is the practice of keeping that flow *unbroken*.

> *Fast deploys* and *stable operations* are *not in conflict*. They go together.

DevOps is not a tool purchase or a team rename. It is a practice where development and operations share one feedback loop: write code → ship → run → learn → write code again.

## Key Terms

- **Dev**: *Development*.
- **Ops**: *Operations*.
- **CI**: *Auto-integrate and validate* every commit.
- **CD**: *Auto-deploy* validated code.
- **SRE**: *Site Reliability Engineering*. The role that treats operations *as code*.

## Before/After

**Before (separated organizations)**

```text
- Dev team: "It works on my laptop"
- Ops team: "You broke it again"
- Deploys *once a quarter*, every time a *weekend overtime*
```

**After (DevOps)**

```text
- Every PR is merged after *passing CI*
- Capable of *dozens of deploys per day*
- Incidents are handled *together*; postmortems are run *together*
```

## Hands-on: Five Steps to Start with DevOps

### Step 1 - Git-based collaboration

```bash
git checkout -b feat/login
# after changes
git commit -m "feat(auth): add login form"
git push origin feat/login
# open a PR
```

### Step 2 - Automate CI

```yaml
# .github/workflows/ci.yml
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest
```

### Step 3 - Add one auto-deploy line

```yaml
deploy:
  needs: test
  if: github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest
  steps:
    - run: ./deploy.sh
```

### Step 4 - Attach monitoring

```python
# a one-line health check
@app.get("/health")
def health(): return {"status": "ok"}
```

### Step 5 - Start incident postmortems

```text
- What happened
- Why was the discovery late
- How will we know faster next time
```

## What to Notice in This Code

- Start from *small automation*. It is not a grand transformation.
- *Dev and Ops* look at *the same repository*.
- Everything is expressed *as code*.

## Five Common Mistakes

1. **Making DevOps a *department name*.** It is *culture*, not an *org chart*.
2. **Adopting tools while *keeping the same process*.** Installing Jenkins is meaningless if you still ship quarterly.
3. **Pushing *all responsibility* onto ops.** *Own it together*.
4. **Over-investing in automation.** Do not build a *3-day automation* for a *one-shot task*.
5. **Blaming people after incidents.** Blame the *system*.

## How This Shows Up in Production

Successful teams start *small*. Auto tests on PRs -> auto deploy -> monitoring -> postmortem culture, settling in over *six months*.

## How a Senior Engineer Thinks

- *Every manual step* is an automation candidate.
- *Deploy frequency* is a *health indicator* of the organization.
- *Incidents are learning opportunities* for the system.
- *Dev and Ops* are *one team*.
- The *length of the feedback loop* decides everything.

## Checklist

- [ ] *Every PR* runs automated tests.
- [ ] A *main merge* triggers *automatic deployment*.
- [ ] Basic *monitoring* exists.
- [ ] *Postmortems* are held regularly.

## Practice Problems

1. List every *manual deploy step* in your project.
2. Mark *three of them* as automation candidates.
3. Summarize your *most recent incident* postmortem in *three sentences*.

## Wrap-up and Next Steps

DevOps is a *cultural shift*. In the next post we go deep on its first lever — the *CI pipeline*.

## Answering the Opening Questions

- **What is DevOps, and why did separating development and operations hit its limits?**
  - In this article, DevOps is a practical approach that ties build, deployment, and operational signals after code writing into a single loop. As the comparison table shows, when dev and ops are separated, deployment cycles grow large and feedback loops stretch to weeks—but frequent small deploys let you find problems faster and roll back smaller.
- **Why is DevOps called a culture rather than a tool?**
  - The article explains DevOps through CALMS: Culture, Automation, Lean, Measurement, Sharing. Only when teams share the same repository, the same postmortem, and the same metrics do tools like GitHub Actions and deployment scripts gain the power to actually change how the team operates.
- **What roles do terms like CI, CD, and SRE play within the DevOps flow?**
  - CI is the front gate that automatically validates changes—like the `lint -> test -> build` GitHub Actions example. CD is the delivery path that moves validated code to real environments—the `deploy` stage. SRE connects operational signals to code and procedures via `/health` checks, metrics, and postmortems, keeping the loop unbroken.
<!-- toc:begin -->
## In this series

- **What Is DevOps? (current)**
- CI Pipeline (upcoming)
- CD and Deployment Strategies (upcoming)
- Environments and Configuration (upcoming)
- Infrastructure as Code (upcoming)
- Containers and Build (upcoming)
- Monitoring and Alerting (upcoming)
- Logging and Analysis (upcoming)
- Incident Response and On-Call (upcoming)
- An Operable DevOps Flow (upcoming)

<!-- toc:end -->

## References

- [The Phoenix Project (Gene Kim)](https://itrevolution.com/product/the-phoenix-project/)
- [Google SRE Book](https://sre.google/books/)
- [Atlassian DevOps Guide](https://www.atlassian.com/devops)
- [DORA State of DevOps](https://dora.dev/)

Tags: DevOps, Culture, CI, CD, Engineering
