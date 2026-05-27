---
series: open-source-101
episode: 5
title: "Open Source 101 (5/10): A Good README"
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
  - README
  - Documentation
  - GitHub
  - Beginner
seo_description: Learn how to write a README that helps a first-time visitor understand, install, and run your project within minutes.
last_reviewed: '2026-05-15'
---

# Open Source 101 (5/10): A Good README

Even a strong project makes a weak first impression if the README is confusing. In open source, the README is the product page, installation guide, and often the first indicator of a maintainer's care. Most visitors read it before they read the code.

This is the 5th post in the Open Source 101 series.

Here, we will define a good README as the document that helps a first-time visitor understand and run the project within the first five minutes.


![open source 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/open-source-101/05/05-01-follow-the-reader-s-order.en.png)
*open source 101 chapter 5 flow overview*
> A good README is not a technical manual. It is a 5-minute message that answers: What does this do? When would I use it? How do I start?

## Questions to Keep in Mind

- What information does a first-time visitor look for first?
- Why are the title, one-line summary, installation, usage example, and license the core sections?
- When do badges and screenshots help, and when do they get in the way?

## Why It Matters

People often say the README is the face of the project. In practice it is even more operational than that. A weak README makes users drop off before installation, contributors miss the rules, and maintainers answer the same questions repeatedly.

Good README quality lowers support cost and builds trust. Small projects especially get judged through their documentation maturity. Great code is still easy to abandon if the starting path is invisible.

## Follow the Reader's Order

That flow matters because the reader's attention usually moves in that order. First they want to know what the project is. Then whether it is installable. Then how to use it. License and contribution details come after that.

Long READMEs are not automatically bad. The key is whether the first five minutes of necessary information live near the top. If you front-load architecture detail and internal design before the user can even run the tool, the README becomes a barrier instead of an entrance.

## Five Concepts Worth Knowing

The *README* is the entry document, not the entire design archive. A *badge* is a quick status indicator, but too many badges turn into noise. A *TOC* lowers navigation cost when the document grows. A *quickstart* is the shortest successful path. `CONTRIBUTING.md` is where you place contribution rules that do not belong in the main onboarding path.

The README should get people started. Deeper details can live behind links.

## How Your Mental Model Should Change

Many people treat the README as decoration they will write later. In reality it is often the first interface users have with the project.

A strong README does not exist to make the repository look impressive. It exists to help someone install, run, and understand the tool quickly. Once you adopt that view, section priority changes immediately.

## Hands-on: Build the Basic README Skeleton

### Step 1 — Title and One-Line Summary

The title states identity. The one-line summary states user value. Aim for clarity about who it is for and what it does.

```markdown
# my-project

> A tiny tool that does X in one command.
```

### Step 2 — Badges

Badges can summarize useful status, but decoration that no one reads only adds noise.

```markdown
![CI](https://github.com/user/repo/actions/workflows/ci.yml/badge.svg)
```

### Step 3 — Install

If the install command is missing, the document is asking the user to guess.

```markdown
## Install

\`\`\`bash
pip install my-project
\`\`\`
```

### Step 4 — Usage Example

Examples are usually stronger than explanations. One command that actually runs is often more valuable than a long paragraph.

```markdown
## Usage

\`\`\`bash
my-project --help
\`\`\`
```

### Step 5 — License

Even if the rest of the README is strong, missing license information can stop adoption and reuse immediately.

```markdown
## License

MIT © 2026 Author Name
```

## What to Notice in This Walkthrough

The title should be unambiguous. The example should actually run. Install and usage should be separated so the reader can scan faster. License information can sit near the bottom, but it cannot be omitted.

The best README experience is not verbal elegance. It is a fast first success. If the user can install and run the project within minutes, the document already did half of its job.

## Five Common Mistakes

1. Forgetting the install command.
2. Leaving examples that no longer run.
3. Using screenshots without explanation.
4. Skipping the license section.
5. Trying to place every design detail in the README.

## How This Shows Up in Production

The same pattern shows up in internal tooling. When a new teammate can boot a library or service from the README alone, support cost drops. When they cannot, chat messages become an expensive replacement for documentation.

## How a Senior Engineer Thinks

- A README is an onboarding interface.
- Five minutes is a useful target.
- Runnable examples beat decorative prose.
- Short sentences reduce friction.
- Separate links give depth without blocking entry.

## Checklist

- [ ] I have a title and one-line summary.
- [ ] The install command is immediately visible.
- [ ] There is a runnable usage example.
- [ ] The license section is present.

## Practice Problems

1. Explain the target time of a quickstart in one sentence.
2. Explain the purpose of a badge in one sentence.
3. Explain why `CONTRIBUTING.md` should often be separate from the README.

## Wrap-up and Next Steps

In this post, we reframed the README as a first-five-minutes onboarding document rather than a repository description. The practical goal is to help a reader move, not just understand.

Next, we will look at release and versioning. Once people can start using your project, they also need a reliable way to understand updates.

## Answering the Opening Questions

- **What information does a first-time visitor look for first?**
  - The article treats A Good README as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why are the title, one-line summary, installation, usage example, and license the core sections?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **When do badges and screenshots help, and when do they get in the way?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Open Source 101 (1/10): What Is Open Source](./01-what-is-open-source.md)
- [Open Source 101 (2/10): Understanding Licenses](./02-understanding-licenses.md)
- [Open Source 101 (3/10): Reading Issues](./03-reading-issues.md)
- [Open Source 101 (4/10): Creating Pull Requests](./04-creating-pull-requests.md)
- **A Good README (current)**
- Release and Versioning (upcoming)
- Community Management (upcoming)
- The Maintainer Role (upcoming)
- An Open Source Portfolio (upcoming)
- My First Open Source Project (upcoming)

<!-- toc:end -->

## References

- [Make a README](https://www.makeareadme.com/)
- [GitHub README guide](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [Awesome README](https://github.com/matiassingers/awesome-readme)
- [Shields.io](https://shields.io/)
- [GitHub Docs repository README style examples](https://github.com/github/docs)

Tags: OpenSource, README, Documentation, GitHub, Beginner
