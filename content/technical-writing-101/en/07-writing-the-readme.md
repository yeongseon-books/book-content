---
series: technical-writing-101
episode: 7
title: "Technical Writing 101 (7/10): Writing the README"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - TechnicalWriting
  - README
  - OpenSource
  - Documentation
  - Beginner
seo_description: Write a README that gives first-time visitors a five-minute path to install, run, and verify the project.
last_reviewed: '2026-05-15'
---

# Technical Writing 101 (7/10): Writing the README

Most readers decide whether to stay in a repository before they inspect a single source file. If the README hides the purpose, the install path, or the first success, the project already feels expensive to approach.

A strong README does not try to explain everything. It lowers entry friction. It tells the reader what this project is, why it exists, how to try it quickly, and what result should appear when the happy path works.

This is the 7th post in the Technical Writing 101 series. It focuses on designing that five-minute first-run experience.


![technical writing 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/07/07-01-concept-at-a-glance.en.png)
*technical writing 101 chapter 7 flow overview*
> A README succeeds when a first-time visitor reaches a visible success without leaving the screen.

## Questions to Keep in Mind

- What are the five essential sections every README needs, and why that order?
- How do you write a Quick Start that a stranger can follow in under five minutes?
- When should you add badges, a FAQ, or a Contributing guide—and when are they noise?

## Why It Matters

The README is the first impression of a project. GitHub renders it automatically, search engines index it, and package managers link to it. If a developer cannot figure out what the project does, how to install it, and how to verify it works within the first screen of scrolling, they will leave and find an alternative.

> Mental model: the README should get a first-time visitor to a visible success with minimal scrolling.

A strong README compresses the install, run, and verification steps into one screen so the reader gets a first success before reading the full backstory. That early win makes the rest of the README feel safer to trust.

## Key Terms

- **What**: A one-line description of what the project is.
- **Why**: The problem it solves or the motivation behind it.
- **How**: The install and run commands.
- **Demo**: Proof that it works—expected output or a screenshot.
- **License**: The legal terms under which the code can be used.

## Before/After

**Before**: "A Python package called Hello." — no install path, no output, no license.

**After**: A README with all five parts: What, Why, Quick Start, Demo output, and License.

## Treat the README like a five-minute contract

The core idea is that a stranger should be able to clone, install, run, and verify the project within five minutes using only the README. Everything above the fold should serve that contract.

### The five-section checklist

| Section | Purpose | Typical Length | Required |
| --- | --- | --- | --- |
| **What** | One sentence describing what it does | 1–2 lines | Yes |
| **Why** | The problem it solves | 2–4 lines | Yes |
| **Quick Start** | Install + run + verify in copy-paste commands | 5–10 lines | Yes |
| **Demo** | Expected output, screenshot, or GIF | 1–5 lines | Yes |
| **License** | Legal terms | 1 line | Yes |

Everything else—configuration, architecture, contributing guidelines—comes after these five. Readers who survive the Quick Start will look for deeper content. Readers who do not survive will not read anything else anyway.

### Quick Start pattern

You can compress the first-run path near the top of the README like this.

~~~markdown
## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```
~~~

**Expected output:**

```text
Uvicorn running on http://127.0.0.1:8000
```

This pattern works because install, run, and proof live in one screen. The reader does not need to absorb the whole backstory before seeing a first success. Once the project feels runnable, the rest of the README becomes easier to trust.

### Full README template for a Python project

Below is a realistic template showing how the five sections fit together in practice.

~~~markdown
# project-name

One sentence: what it does and for whom.

## Why

The problem this project solves. Two to four sentences maximum.

## Quick Start

```bash
git clone https://github.com/org/project-name.git
cd project-name
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest --tb=short
```

Expected output:

```text
====== 42 passed in 3.12s ======
```

## Usage

```python
from project_name import greet

print(greet("world"))
# Hello, world!
```

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `PORT` | `8000` | Server listen port |
| `LOG_LEVEL` | `info` | One of debug, info, warning, error |
| `DB_URL` | `sqlite:///app.db` | Database connection string |

## Development

```bash
pre-commit install
pytest --cov=project_name
```

## License

MIT
~~~

Notice that the template gets to a runnable command within 10 lines of the project description. Configuration and development details come later because they serve returning contributors, not first-time visitors.

## When to add badges

Badges (build status, coverage percentage, PyPI version) belong at the very top of the README—between the H1 and the description—only when they provide information the reader needs to decide whether to use the project.

| Badge | Add when | Skip when |
| --- | --- | --- |
| CI status | The project has public CI | No CI or always green |
| Coverage | Coverage is above 80% | Coverage is embarrassingly low |
| PyPI version | Published on PyPI | Internal-only project |
| License | Non-standard license | MIT (already expected) |

A row of six or more badges usually signals vanity rather than usefulness. Each badge should answer a question the reader actually has.

## FAQ and Troubleshooting sections

A FAQ earns its place once the same question appears three or more times in issues or support channels. Before that threshold, the section is speculative and may never be read.

**FAQ pattern:**

```markdown
## FAQ

### Why does `greet()` return bytes instead of str?

On Python 3.8, the default encoding differs. Upgrade to 3.11+
or pass `encoding="utf-8"` explicitly.
```

**Troubleshooting pattern:**

```markdown
## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ModuleNotFoundError: project_name` | Virtual env not activated | `source .venv/bin/activate` |
| `Connection refused on :8000` | Port already in use | `lsof -i :8000` then kill the process |
| Slow startup (>10s) | Large DB migration pending | `alembic upgrade head` |
```

The table format works because readers arrive at Troubleshooting already frustrated. They need to scan, match their symptom, and leave with a fix—fast.

## Contributing guidelines

A CONTRIBUTING.md (or a Contributing section in the README) matters when external contributors are welcome. The minimum viable version answers three questions:

1. **How to set up the dev environment** — clone, install, run tests.
2. **What the PR process looks like** — branch naming, commit message style, review expectations.
3. **What is out of scope** — so contributors do not waste time on rejected directions.

```markdown
## Contributing

1. Fork and clone the repo.
2. Create a feature branch: `git checkout -b feat/short-description`
3. Install dev dependencies: `pip install -e ".[dev]"`
4. Run tests before pushing: `pytest --tb=short`
5. Open a PR against `main`. One reviewer approval required.

We do not accept PRs that add runtime dependencies without prior discussion in an issue.
```

## Five common README mistakes and their fixes

| Mistake | Why it hurts | Fix |
| --- | --- | --- |
| Missing **Why** | Reader cannot judge relevance | Add a 2-sentence problem statement |
| Quick Start longer than 10 lines | Reader abandons before success | Trim to clone + install + run + verify |
| No expected output | Reader cannot tell if it worked | Add a `text` code block with the output |
| No license | Legal ambiguity blocks adoption | Add an SPDX identifier or LICENSE file |
| Screenshots without context | Reader does not know what they show | Add a one-line caption above each image |

## Hands-on: Five README Parts

### Step 1 — What

```markdown
# greeter
A small greeting library.
```

### Step 2 — Why

```markdown
## Why
I wanted multilingual greetings in a single line.
```

### Step 3 — How

```bash
pip install greeter
python3 -c "from greeter import hello; print(hello('en'))"
```

### Step 4 — Demo

```text
Hello!
```

### Step 5 — License

```markdown
## License
MIT
```

## What to Notice in This Code

- All five parts are present.
- The commands are copy-paste safe—no placeholder brackets the reader must replace.
- The result is visible. The reader can compare their terminal output against the expected output.

## Five Common Mistakes

1. **Missing Why.** The project description says what it is but not why anyone should care.
2. **A long Quick Start.** More than ten lines means the reader has to understand too much before succeeding.
3. **No demo result.** Without expected output, the reader cannot confirm whether it worked.
4. **No license.** Without a license, the code is legally unusable by others.
5. **No screenshots.** For CLI tools or UI projects, a visual proof is more convincing than text.

## How This Shows Up in Production

Most trending GitHub projects follow nearly the same five-part pattern. FastAPI, Pydantic, and HTTPie all open with a one-liner, show a Quick Start, and include expected output. The pattern is popular because it works—not because it is fashionable.

## How a Senior Engineer Thinks

- Runnable in five minutes or it is not a good README.
- Why in one line—if you cannot explain the motivation concisely, the project scope is unclear.
- Commands run as written—no `<replace-this>` placeholders without explanation.
- License is stated—missing license is a legal landmine for any company.
- At least one screenshot or terminal output—proof of life.

## Checklist

- [ ] All five parts (What, Why, How, Demo, License) present.
- [ ] Quick Start is five to ten lines or fewer.
- [ ] Demo result shown as a code block or screenshot.
- [ ] License stated explicitly.
- [ ] Badges add information, not decoration.

## Practice Problems

1. Write the definition of *What* in one line.
2. Write the meaning of *Demo* in one line.
3. Write an example of a *License* in one line.

## Answering the Opening Questions

- **What are the five essential sections every README needs, and why that order?**
  What, Why, Quick Start, Demo, and License—in that order because the reader first decides relevance (What/Why), then tries it (Quick Start/Demo), then checks legal terms (License). Reversing this order forces readers to wade through legalese before knowing whether the project is even relevant.
- **How do you write a Quick Start that a stranger can follow in under five minutes?**
  Keep it to clone, install, run, verify—four commands maximum. Show the exact expected output so the reader can compare. Avoid environment-specific assumptions (no `brew install` without noting it is macOS-only). Test the commands in a fresh environment before publishing.
- **When should you add badges, a FAQ, or a Contributing guide—and when are they noise?**
  Badges belong when they answer a question the reader actually has (Is CI passing? What version is on PyPI?). FAQ earns its place after the same question appears three times. Contributing matters when external PRs are welcome. Before those thresholds, these sections are speculative padding.

<!-- toc:begin -->
## In this series

- [Technical Writing 101 (1/10): What Is Technical Writing](./01-what-is-technical-writing.md)
- [Technical Writing 101 (2/10): Defining the Reader](./02-defining-the-reader.md)
- [Technical Writing 101 (3/10): Title and Structure](./03-title-and-structure.md)
- [Technical Writing 101 (4/10): Explaining Concepts](./04-explaining-concepts.md)
- [Technical Writing 101 (5/10): Explaining Example Code](./05-explaining-example-code.md)
- [Technical Writing 101 (6/10): Using Figures and Tables](./06-using-figures-and-tables.md)
- **Writing the README (current)**
- Writing Tutorials (upcoming)
- Blog vs Documentation (upcoming)
- Pre-publish Checklist (upcoming)

<!-- toc:end -->

## References

- [Make a README - GitHub](https://www.makeareadme.com/)
- [Standard README - RichardLitt](https://github.com/RichardLitt/standard-readme)
- [Awesome README - matiassingers](https://github.com/matiassingers/awesome-readme)
- [Choose a License](https://choosealicense.com/)

Tags: TechnicalWriting, README, OpenSource, Documentation, Beginner
