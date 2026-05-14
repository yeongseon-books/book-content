# Quality Audit Rubric

This rubric is the single scoring yardstick for auditing a series against the benchmark set by `content/azure-app-service-101/`.

## Scoring unit and method

- **Score the entire series, not one article in isolation.** Review every canonical `ko/*.md` and `en/*.md` post in the series.
- **Use integer scores only** on each axis: 1, 2, 3, 4, 5.
- **Weighted total** = `sum(axis_score / 5 * axis_weight)`.
- **Both languages matter** for Axes 1, 2, 4, 5. **Axis 3 uses only `ko/*.md`.**
- **Mechanical first, then human confirmation.** Run grep/count checks, then read the flagged lines. Do not let a regex false positive or false negative decide the score by itself.
- If a bilingual series is missing one canonical language, **cap Axis 1 and Axis 5 at 1**.

## Axis weights

| Axis | Weight |
| --- | ---: |
| 1. Structural completeness | 25 |
| 2. Code & diagrams substance | 25 |
| 3. Korean naturalness | 20 |
| 4. Narrative flow & reader value | 20 |
| 5. References & metadata polish | 10 |
| **Total** | **100** |

---

## 1. Structural completeness (25)

### What to inspect

Every source post should follow the repository’s mandatory order: H1 → intro with series-position sentence → body → TOC block → references → visible `Tags:` last line. The structure checker also expects a questions block, a mental-model blockquote, code blocks when `code_required` is true, and a checklist.

### Mechanical signals

Use these signals per file:

- H1: `^# `
- Series intro anchor near top: ko `이 글은 ... 시리즈`, en `This is ... series`
- Questions block: ko `^##\s+.*(질문|답할 질문|다룰 질문|다룰 문제)` / en `^##\s+.*(Questions|answers|What you will learn)`
- Mental model blockquote: `^> `
- Code fences: lines starting with triple backticks (for example, ```python`, ```bash`)
- Checklist items: `^- \[[ x]\]`
- TOC block: `^<!-- toc:begin -->` and `^<!-- toc:end -->`
- References heading: `^## 참고 자료$` or `^## References$`
- Tags last line: `^Tags: ` on the final non-empty line
- A-grade bypass marker: `<!-- a-grade-intro:begin -->`

### Score definitions

| Score | Observable criteria |
| --- | --- |
| **5** | **95-100%** of article files contain the full structural spine: H1, real series-position intro near H1, questions block, at least one mental-model blockquote, code block when needed, checklist, TOC, references, and `Tags:` as the last line. Any omission is isolated and minor. A-grade marker is absent or clearly justified, never used as a shortcut. |
| **4** | **80-94%** of files contain the full spine. Missing pieces are limited to one or two recurring items such as weak checklist coverage or missing blockquotes. The article is still navigable without guesswork. |
| **3** | **60-79%** coverage. Several files have the basics (H1/refs/tags) but repeatedly miss advisory structure such as questions blocks, checklists, or mental-model blockquotes. |
| **2** | **30-59%** coverage. TOC/references/tags may exist, but multiple articles feel like loose notes: missing intro sentence, no checklist, no explicit question framing, or misplaced end matter. |
| **1** | **<30%** coverage or systematic breakage of mandatory order. Missing H1/TOC/references/last-line tags is common, or the series is missing a canonical language directory. |

### Worked example: 5 vs 2

**What a 5 looks like**

- `content/azure-app-service-101/ko/01-what-is-app-service.md:21-28` opens with H1, a reader hook, then a standalone series-position sentence.
- `content/azure-app-service-101/ko/01-what-is-app-service.md:31-38` adds a concrete “이 글에서 다룰 문제” block instead of jumping straight into definitions.
- `content/azure-app-service-101/ko/01-what-is-app-service.md:260-295` closes with checklist → TOC → references → visible tags in the correct order.
- `content/azure-app-service-101/en/02-request-lifecycle.md:372-407` shows the same closing discipline in English: checklist, TOC, references, tags.

**What a 2 looks like**

- H1 exists, but there is **no standalone series-position sentence near the top**, no questions block, and no checklist.
- TOC/references/tags are missing or out of order, so the file lacks the closing spine seen in `.../ko/01-what-is-app-service.md:260-295`.
- The A-grade marker is used to dodge missing sections rather than to justify a genuinely different article shape.

---

## 2. Code & diagrams substance (25)

### What to inspect

Audit whether examples are operationally useful, technically plausible, and matched to the article’s promise. Gold-level posts do not rely on screenshots or toy code when the reader expects deployment, configuration, logging, or scaling patterns.

### Mechanical signals

Use these signals across the series:

- Fenced blocks by language: `^```(python|bash|json|kql|text|gitignore)`
- Image count: `^!\[`
- Caption pattern: image line followed within 1-2 lines by italic caption `*...*`
- Expected-output markers: `^\*\*Expected output:` or `^\*\*Output:`
- Red-flag placeholders to review manually: `TODO|lorem|foobar|your-name|replace-me|pass|NotImplemented|coming soon`
- Operational commands: `az webapp`, `curl`, `gunicorn`, `nslookup`, `openssl`, `az monitor`

If a series contains Mermaid source, additionally audit label quoting against `AGENTS.md:106-110` and `STYLE_GUIDE.md:207-210`. The gold reference uses rendered PNG diagrams rather than inline Mermaid, so this must be checked on the target series itself.

### Score definitions

| Score | Observable criteria |
| --- | --- |
| **5** | Core tutorial posts contain **real runnable or directly usable snippets**. At least one end-to-end snippet exists where the article promises hands-on work; supporting fragments are scoped clearly and remain technically correct. Diagrams explain architecture, flow, or trade-offs; they are not decorative. Images are captioned. Placeholder-only code is absent. |
| **4** | Most articles contain useful commands/snippets, but some examples are abbreviated enough that readers must infer missing context. Diagrams still explain real concepts. Minor placeholder use or one weak example is acceptable. |
| **3** | Mixed quality. Some posts have strong code, others fall back to pseudo-code, shallow shell fragments, or screenshots without explanatory depth. Diagrams exist but are not consistently tied back to decisions. |
| **2** | Many examples are toy-level, non-runnable, or missing crucial setup/imports without warning. Diagrams are generic, unlabeled, or captionless. The series promises practical guidance but mostly provides surface syntax. |
| **1** | Code and diagrams are largely absent, placeholder-heavy, or technically misleading. The series cannot support real implementation or troubleshooting work. |

### Worked example: 5 vs 2

**What a 5 looks like**

- `content/azure-app-service-101/ko/04-first-deploy.md:67-102` provides a self-contained Flask app with imports, routes, and `PORT` binding.
- `content/azure-app-service-101/ko/04-first-deploy.md:153-176` checks production parity locally with Gunicorn instead of stopping at the Flask dev server.
- `content/azure-app-service-101/ko/06-logging-monitoring.md:150-245` shows structured JSON logging plus correlation ID middleware that is immediately usable in a Flask app.
- `content/azure-app-service-101/en/07-scaling-101.md:137-170` contrasts a scale-breaking in-memory session pattern with a Redis-backed alternative.
- `content/azure-app-service-101/ko/01-what-is-app-service.md:68-70` shows the diagram+caption pattern expected of explanatory images.

**What a 2 looks like**

- A deployment article gives only `az webapp create ...` with omitted critical flags, no verification step, and no expected output.
- A scaling article uses toy `print("hello")` code instead of state, connection, or autoscale patterns.
- Diagrams are screenshots or unlabeled images with no caption, unlike `.../ko/01-what-is-app-service.md:68-70`.

---

## 3. Korean naturalness (20)

### What to inspect

Judge only `ko/*.md`. The target is senior-engineer Korean in a consistent `~입니다` register, with low translation smell and readable paragraph rhythm.

### Mechanical signals

- Run: `bash .sisyphus/style/check-ko.sh content/<series>/ko`
- Review hits for S1/S2 patterns from `.sisyphus/skills/humanize-korean/quick-rules.md`, especially:
  - `~에 대해(서)`
  - `~에 있어서`
  - `가지고 있다`
  - `되어진다`
  - `요약하면|정리하면|결론적으로`
  - `나아가,|아울러,|게다가,|더욱이,`
  - hype words such as `획기적|압도적|혁신적`
  - `~한 것이다|~다는 뜻이다`
- Manual checks:
  - register drift away from `~입니다`
  - repeated paragraph shape (every sentence same length)
  - multiple 6+ sentence dense paragraphs in a row
  - obvious translation syntax from English

### Score definitions

| Score | Observable criteria |
| --- | --- |
| **5** | Korean reads as authored prose, not translation output. `~입니다` register is stable. Confirmed S1 issues are **rare (roughly ≤0.5/article on average)** and do not cluster across the series. Sentence length varies naturally; paragraphs stay readable. |
| **4** | Mostly natural, with occasional stiff or translated sentences. A few repeated smells appear, but they do not dominate the reading experience. Register is still mostly stable. |
| **3** | Noticeable translation smell in several posts. The series remains understandable, but repeated patterns (`~에 대해`, `~한 것이다`, formulaic conclusions, connector overuse) weaken trust and flow. |
| **2** | Translation smell is frequent and easy to spot in most posts. Register drifts, paragraphs become dense and monotonous, and many sentences sound machine-composed. |
| **1** | Korean is consistently unnatural, heavily translated, or mixed-register to the point that it damages comprehension and credibility. |

### Worked example: 5 vs 2

**What a 5 looks like**

- `content/azure-app-service-101/ko/01-what-is-app-service.md:23-27` opens with a concrete operator’s confusion, then narrows into an actionable thesis without hype or textbook stiffness.
- `content/azure-app-service-101/ko/06-logging-monitoring.md:23-27` turns reader pain into a clear operating goal in compact, natural prose.
- `content/azure-app-service-101/ko/07-scaling-101.md:23-32` mixes short and long sentences, keeps the `~입니다` register, and lands a concrete caution instead of an AI-style slogan.

**What a 2 looks like**

- Several posts repeat endings like `정리하면`, `~한 것이다`, `~해야 한다` or stack connector words such as `나아가, 아울러, 더욱이`.
- The prose reads like direct translation, with repeated `~에 대해`, `~에 있어서`, and abstract hype in place of operational explanation.

**Calibration note:** the gold series is not defined as “zero automated hits.” Running `check-ko.sh` on `content/azure-app-service-101/ko` returns **2 hits across 7 posts**, so treat isolated tool hits as review prompts, not automatic downgrades.

---

## 4. Narrative flow & reader value (20)

### What to inspect

Gold-level articles move from **reader pain → mental model → concrete mechanism → example/troubleshooting → operational checklist**. They do not restate obvious service descriptions when a sharper operating question is available.

### Mechanical signals

- Early problem framing within the first ~40 lines
- Early mental model / thesis signal: blockquote near top (`^> `) or explicit framing section
- Concrete sections such as `Step`, `Troubleshooting`, `Checklist`, `Health Check`, `KQL`, `Autoscale`, `Key Vault`
- Red flags to review manually:
  - repeated meta-intros (`This post will...`, `이 글에서는 ... 설명하겠습니다`) with little payoff
  - long abstract sections with no example, scenario, metric, or command
  - headings that duplicate each other without advancing the article

### Score definitions

| Score | Observable criteria |
| --- | --- |
| **5** | Nearly every article gives the reader a practical reason to care in the opening, introduces a mental model or decision frame early, and keeps moving toward concrete actions, commands, tables, or troubleshooting steps. Explanations answer “so what?” and “what do I do next?” instead of restating docs. |
| **4** | Most articles follow a strong why→what→how flow, but some sections drift into summary or option listing before returning to practical value. Reader payoff still arrives reliably. |
| **3** | The flow is uneven. Some chapters are helpful, others feel like catalogs of settings or definitions with limited prioritization or consequence. |
| **2** | The series often explains what a feature is without showing why it matters, when it breaks, or how to act on it. Progression is shallow or repetitive. |
| **1** | Little reader guidance. Articles are mostly disconnected notes, definitions, or vendor-doc paraphrases. |

### Worked example: 5 vs 2

**What a 5 looks like**

- `content/azure-app-service-101/ko/01-what-is-app-service.md:49-67` introduces the 3-plane mental model, then immediately ties it to real operator confusion and failure modes.
- `content/azure-app-service-101/ko/02-request-lifecycle.md:99-131` turns a `403/502/503` symptom into a first-check sequence rather than a vague explanation of routing.
- `content/azure-app-service-101/ko/07-scaling-101.md:293-325` pushes scaling advice into dependency math, connection pools, and real cost/risk trade-offs.
- `content/azure-app-service-101/en/06-logging-monitoring.md:236-244` turns “user reported an error” into a concrete log-query workflow via correlation IDs.

**What a 2 looks like**

- The article spends most of its length naming features or tiers but never gives a decision frame.
- Troubleshooting sections list symptoms without telling the reader what to check first, unlike `.../ko/02-request-lifecycle.md:360-365`.
- The ending simply restates the introduction instead of converting the chapter into an operational checklist or next action.

---

## 5. References & metadata polish (10)

### What to inspect

This axis covers front matter completeness, SEO usefulness, tag quality, and reference quality.

### Mechanical signals

Per file, confirm:

- Front matter fields: `title`, `series`, `episode`, `language`, `status`, `targets`, `tags`
- `last_reviewed` for `publish-ready` / `published`
- `seo_description` present and specific
- `Tags:` last line present and aligned with the series topic
- References section present and populated with named links
- Review link authority with grep such as `learn.microsoft.com|azure.microsoft.com|12factor.net|github.com/`
- Red flags: empty or generic SEO descriptions, generic tags, naked URLs, “see docs” bullets with no title, outdated `ready` status

### Score definitions

| Score | Observable criteria |
| --- | --- |
| **5** | **100%** of files have complete front matter for their status, useful `seo_description`, stable topic-relevant tags, and a real references section with authoritative named sources. The references help verification, not just formality. |
| **4** | Minor metadata gaps or weaker SEO copy in a few files, but references are still mostly authoritative and tags are sensible. |
| **3** | Several files have thin metadata, generic SEO descriptions, inconsistent tags, or shallow references. |
| **2** | Metadata is incomplete in many files, references are vague or low-authority, and tags/SEO fields look templated rather than article-specific. |
| **1** | Metadata is broadly missing or broken. References do not support verification, and tags/SEO fields are absent or misleading. |

### Worked example: 5 vs 2

**What a 5 looks like**

- `content/azure-app-service-101/ko/05-configuration.md:1-18` shows complete front matter, including `last_reviewed` and a specific `seo_description`.
- `content/azure-app-service-101/en/06-logging-monitoring.md:1-18` does the same in English.
- `content/azure-app-service-101/ko/05-configuration.md:441-446` cites Microsoft Learn plus Twelve-Factor App, which helps readers verify both product behavior and design principle.
- `content/azure-app-service-101/en/07-scaling-101.md:464-469` uses named, authoritative references instead of vague “read the docs” bullets.

**What a 2 looks like**

- Missing `last_reviewed` or `seo_description` in publish-ready articles.
- Reference section exists but contains only generic bullets such as “Azure docs” with no exact page.
- Tags are generic (`Cloud`, `Tech`) without series-specific precision, unlike the consistent gold-series ending lines such as `.../ko/01-what-is-app-service.md:295`.

---

## Recommended scoring workflow

1. Count structural and metadata coverage across all canonical files.
2. Run `check-ko.sh` on `ko/` and review every hit manually.
3. Sample at least **two strongest** and **two weakest** articles for code substance and narrative flow.
4. Score each axis independently; do not let a strong code axis hide weak Korean or metadata.
5. Write audit evidence with file-path and line-range citations.
