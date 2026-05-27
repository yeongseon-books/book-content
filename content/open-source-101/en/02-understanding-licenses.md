---
series: open-source-101
episode: 2
title: "Open Source 101 (2/10): Understanding Licenses"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - OpenSource
  - License
  - MIT
  - GPL
  - Beginner
seo_description: Compare MIT, Apache 2.0, and GPL, and learn to read open source licenses as usage conditions rather than labels.
last_reviewed: '2026-05-15'
---

# Open Source 101 (2/10): Understanding Licenses

Beginners usually look at features first when they evaluate an open source project. They want to know whether it solves today's problem, whether installation is easy, and whether examples are good. In real production work, though, there is often one document you should read before all of that: the license. It defines what you may do, what notice you must keep, and how redistribution works.

This is the 2nd post in the Open Source 101 series.

Here, we will use MIT, Apache 2.0, and GPL as the main reference points and learn to read licenses as permission-and-obligation documents rather than brand names.


![open source 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/open-source-101/02/02-01-draw-the-license-map-first.en.png)
*open source 101 chapter 2 flow overview*
> A license is not just a legal document. It is a contract that lets people collaborate safely because everyone knows the boundaries.

## Questions to Keep in Mind

- What is the practical difference between *permissive* and *copyleft* licenses?
- How do MIT, Apache 2.0, and GPL v3 create different operational burdens?
- Why does an SPDX identifier matter for automation and compliance work?

## Why It Matters

Licenses shape a project's future, not just its current usability. A library may run perfectly today, but later questions such as commercial distribution, derivative work obligations, and patent risk all depend on the license text.

Open source choices are both technical choices and legal choices. A developer may think they selected a convenient library, but an organization also selected a redistribution burden and a compliance cost. That is why reading the license early is cheaper than discovering the constraints during release.

## Draw the License Map First

There is no reason to treat this split as a moral ranking. Permissive licenses make reuse easier. Copyleft licenses push sharing obligations harder. Neither side is universally better. The practical question is what kind of project behavior and distribution model you want to support.

When you read a license, the name matters less than the questions you ask. Can I modify this code? Can I redistribute it? Must I keep the copyright notice? Must I publish source for derivative work? Is there explicit patent language? If you can answer those questions, you already understand the important part.

## Five Concepts Worth Knowing

A *permissive* license broadly allows use, modification, distribution, and often commercial use. A *copyleft* license ties stronger sharing obligations to derivative work. *Public domain* aims to remove most copyright restriction, but legal treatment still differs across jurisdictions. A *dual license* offers the same software under two licensing models, often to balance open source distribution and commercial terms. *SPDX* is a short, standardized identifier that automated tools can read reliably.

The real goal is not memorizing license names. It is building the habit of seeing where rights and obligations diverge. Selling, redistributing, preserving notice, disclosing source, and handling patent terms do not all behave the same way.

## How Your Mental Model Should Change

At first, MIT and GPL can feel like two labels under the same broad category of open source. With one closer look, the difference becomes operationally large. The shared category is not enough to make an implementation decision.

Once you start reading licenses properly, your question changes from “Can I use this?” to “Under what conditions can I use this?” That shift is what matters in real projects.

## Hands-on: A License Comparison Procedure

### Step 1 — MIT essentials

MIT is one of the most common beginner-facing licenses. It is broad, simple, and frequently used by libraries and small tools.

```text
Allows: use, modify, distribute, sell
Requires: keep the copyright notice
```

### Step 2 — Apache 2.0 essentials

Apache 2.0 can look similar to MIT at a glance, but its explicit patent grant makes it a separate conversation in many organizations.

```text
Allows: same as MIT
Adds: explicit patent grant
```

### Step 3 — GPL v3 essentials

GPL protects sharing more aggressively. It is especially important to distinguish between internal use and distribution.

```text
Allows: use, modify, distribute
Requires: derivative works share their source
```

### Step 4 — SPDX identifier

Do not stop at dropping a `LICENSE` file into the repository. If your package metadata or release automation can expose a machine-readable identifier, that will help scanners and governance tools.

```yaml
license: MIT
```

### Step 5 — Bring in verified source text

Copy-paste from a random blog is not a great plan. Use a trusted source for the original license text.

```bash
curl -O https://choosealicense.com/licenses/mit/
```

## A Fast Decision Matrix

| Question | MIT | Apache 2.0 | GPL v3 |
| --- | --- | --- | --- |
| Commercial use | Easy | Easy | Possible, but obligations matter |
| Patent language | Minimal | Explicit grant | Present, but with stronger reciprocity context |
| Derivative source disclosure | No | No | Yes, when distributed |
| Beginner friction | Low | Low to medium | Medium to high |

## What to Notice in This Walkthrough

Permissive licenses optimize for low friction. Copyleft licenses optimize for stronger reciprocal sharing. SPDX looks small, but it is what keeps humans and automation aligned. Once you see that, license reading stops feeling like clerical work and starts feeling like architecture risk management.

## Five Common Mistakes

1. Copying the license text without understanding the obligations.
2. Removing copyright notices when redistributing code.
3. Pulling GPL code into a proprietary product without checking distribution consequences.
4. Reading only one side of a dual-license offer.
5. Skipping SPDX identifiers and breaking automated compliance chains.

## How This Shows Up in Production

Companies rarely leave license decisions to individual intuition alone. They use scanners such as FOSSA or Snyk to traverse dependency trees, compare them against allowlists or review lists, and surface risky combinations early. Once a release ships, license cleanup is much more expensive.

## How a Senior Engineer Thinks

- A license is a usage condition, not metadata fluff.
- MIT is low-friction reuse.
- Apache 2.0 matters when patent language matters.
- GPL changes the distribution conversation.
- Dual licensing is often a business strategy, not a legal oddity.

## Checklist

- [ ] I checked whether the repository has a `LICENSE` file.
- [ ] I know where to place or expose an SPDX identifier.
- [ ] I understand whether copyright notice must be preserved.
- [ ] I reviewed compatibility between the dependency license and my distribution model.

## Practice Problems

1. Summarize the difference between *permissive* and *copyleft* in one sentence.
2. Explain why SPDX matters in one sentence.
3. Explain why a dual license can also be a business strategy.

## Wrap-up and Next Steps

In this post, we treated licenses as the terms that define what you may do with open source code, not as a checkbox at the bottom of a repository. The important shift is that using open source means accepting its rules, not only its features.

Next, we will move into issues. To contribute well, you need to know not only which problem to pick, but also how to interpret the problem statement already on the table.

## Answering the Opening Questions

- **What is the practical difference between *permissive* and *copyleft* licenses?**
  - The article treats Understanding Licenses as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How do MIT, Apache 2.0, and GPL v3 create different operational burdens?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Why does an SPDX identifier matter for automation and compliance work?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Open Source 101 (1/10): What Is Open Source](./01-what-is-open-source.md)
- **Understanding Licenses (current)**
- Reading Issues (upcoming)
- Creating Pull Requests (upcoming)
- A Good README (upcoming)
- Release and Versioning (upcoming)
- Community Management (upcoming)
- The Maintainer Role (upcoming)
- An Open Source Portfolio (upcoming)
- My First Open Source Project (upcoming)

<!-- toc:end -->

## References

- [Choose a License](https://choosealicense.com/)
- [SPDX License List](https://spdx.org/licenses/)
- [Open Source Initiative Licenses](https://opensource.org/licenses)
- [choosealicense.com repository](https://github.com/github/choosealicense.com)
- [tl;dr Legal](https://www.tldrlegal.com/)

Tags: OpenSource, License, MIT, GPL, Beginner
