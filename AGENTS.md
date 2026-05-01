# Repository Agent Rules

> Persistent conventions for any agent (human or AI) working in this repository.
> Apply these rules to every post, every commit, every script run.

> **Migration in progress**: this repo is moving from `tech-blog` to `tech-writing` (multi-channel publishing pipeline). See [`MIGRATION_PLAN.md`](./MIGRATION_PLAN.md) and [`ROADMAP.md`](./ROADMAP.md). All 10 series have been moved under `content/<series>/` (Phase 6 complete). Path examples below use `content/<series>/...` accordingly. Tooling (`finalize-posts.py`, `to-medium.py`, `finalize-ai-web-dev.py`) resolves series paths via `series.yaml`'s `path:` field; never hardcode `ROOT/<series-id>`.

## Series catalog

Eight Azure series (52 posts × 3 variants = 156 markdown files):

- `azure-app-service-101/`, `azure-app-service-deep-dive/`
- `azure-functions-101/`, `azure-functions-deep-dive/`
- `azure-aks-101/`, `azure-aks-deep-dive/`
- `azure-aca-101/`, `azure-aca-deep-dive/`

Each Azure series has three variants: `ko/`, `en/`, `medium/`.

- `ko/<NN>-<slug>.md` — Tistory original (Korean)
- `en/<NN>-<slug>.md` — Hashnode English Blog (한국어 원문의 충실한 영어 대응본). Published to `https://hashnode.com/@yeongseon`.
- `medium/<NN>.html` — Medium publication adaptation. Generated from `en/<NN>-<slug>.md` by `.sisyphus/medium/to-medium.py` (which delegates HTML rendering to `to-medium-html.py`). During markdown processing image refs are kept as relative local paths; during HTML rendering PNGs are inlined as base64 `data:` URIs. Open in Chrome, select-all, copy, paste into a fresh empty Medium draft; the first H1 maps to Medium's title slot, the trailing visible `Tags: ...` line is copied manually into Medium's tag input field.

Plus the single-variant Korean series:

- `ai-web-dev-101/` — 7 Korean-only posts published to Tistory. Flat layout, no `ko/`/`en/`/`medium/` subfolders. Same conventions apply (H1 → tag line at the bottom → series TOC above references), with TOC heading `## 시리즈 목차` and references heading `## 참고 자료`. Series tags: `AI, LLM, 웹 개발, Python, Tutorial` (defined in `.sisyphus/medium/finalize-ai-web-dev.py`).

And the LLM series (3-variant like Azure):

- `llm-from-scratch-101/` — 9-part series (`ko/`, `en/`, `medium/`). PyTorch 2.x, ~720 LOC tiny GPT, TinyShakespeare. Series tags: `LLM, PyTorch, Transformer, Tutorial`.

And the RAG series (3-variant like Azure):

- `rag-deep-dive/` — 6-part series (`ko/`, `en/`, `medium/`). LangChain, FAISS, RAGAS source-pinned. Series tags: `RAG, LangChain, Vector Search, LLM`.

And the new LLM/AI application 101 series (3-variant, sequential roadmap — write one at a time in order):

1. `llm-app-foundations-101/` — 6-part. LLM API basics, tokens, prompt engineering. Tags: `LLM, OpenAI, Prompt Engineering, Python`.
2. `llm-api-production-101/` — 6-part. Structured Output, Tool Calling, Streaming, Caching, Retry, Rate Limit. Tags: `LLM, OpenAI, Streaming, Python`.
3. `vector-search-101/` — 6-part. Embeddings, FAISS, similarity, chunking. Tags: `Vector Search, FAISS, Embeddings, Python`.
4. `langchain-101/` — 6-part. LCEL, Runnable, Retriever, Tool Calling basics, Streaming. Positioning: LangChain API usage only (not app design patterns). Tags: `LangChain, LCEL, Python, LLM`.
5. `ai-app-patterns-101/` — 6-part. Chatbot, RAG Q&A, Document Assistant, Agent+Tool, Workflow Automation, Human-in-the-loop design patterns. Positioning: product/service patterns using LangChain components (not API syntax). Tags: `LLM, RAG, Agent, Python`.
6. `korean-ai-stack-101/` — 6-part. Korean embeddings (KoSimCSE, bge-m3, Solar), OCR (CLOVA), domestic LLM APIs (HyperCLOVA X, Upstage Solar, Kakao KoGPT). Tags: `Korean NLP, LLM, Embeddings, OCR`.
7. `document-ingestion-101/` — 6-part. PDF parsing, metadata, incremental indexing. Tags: `RAG, Document Processing, LangChain, Python`.
8. `llm-apps-ops-101/` — 6-part. Observability, evaluation, cost, security, deployment. Tags: `LLMOps, Observability, Python, LLM`.
9. `rag-benchmark-101/` — 6-part. VectorDB, embedding model, retriever, RAG pipeline evaluation. Tags: `RAG, VectorDB, Benchmarking, LLM`.
10. `langgraph-101/` — 6-part. Graph agents, checkpoints, multi-agent. Tags: `LangGraph, Agent, Python, LLM`.
11. `llm-finetuning-101/` — 6-part (optional). LoRA, datasets, serving. Tags: `Fine-tuning, LoRA, LLM, Python`.

All new series: `ko/`, `en/`, `medium/` three-variant layout. Code samples use Groq (free tier) + HuggingFaceEmbeddings (`sentence-transformers/all-MiniLM-L6-v2`) unless the topic specifically requires a different model. No OpenAI API key required for readers.

The single source of truth for the catalog is now [`series.yaml`](./series.yaml); [`SERIES.md`](./SERIES.md) is the human-readable summary.

## Post structure (mandatory order)

This block describes the canonical **source** posts (`ko/<NN>-<slug>.md` and `en/<NN>-<slug>.md`). Derived **medium artifacts** (`medium/<NN>.html`) follow a different shape — they are produced by `.sisyphus/medium/to-medium.py` and live outside the source-post structure. See "Medium artifact rules" below.

Every source post (ko + en) MUST have, top to bottom:

1. **H1 title** (`# Title`) as the first content line
2. **Body** (sections, code, images, etc.)
3. **Series TOC block** wrapped in `<!-- toc:begin -->` / `<!-- toc:end -->`
4. **References section** (`## 참고 자료` for ko, `## References` for en)
5. **Tag line** as the very last line: `Tags: A, B, C, D` (visible plain text, per-series set, see `.sisyphus/medium/finalize-posts.py`)

The TOC block sits immediately above the references section, separated by a single `---` divider. The tag line sits at the very bottom of the file (after the references section), separated by one blank line. Legacy `<!-- tags: ... -->` HTML comments on line 1 are removed automatically by `finalize-posts.py`.

## Medium artifact rules

`medium/<NN>.html` is a derived artifact, not a source post. It is regenerated end-to-end by `.sisyphus/medium/to-medium.py` from `en/<NN>-<slug>.md` (the script applies Medium-specific markdown transforms in memory, then delegates rendering to `to-medium-html.py`). No intermediate `medium/<NN>.md` file is written. `finalize-posts.py` does not touch the `medium/` directory; do not hand-edit medium files.

- Tag surface: visible `Tags: A, B, C, D` plain-text line as the very last line (matches ko/en source convention; no leading HTML comment). On publish, copy the comma list manually into Medium's separate tag input field; the visible line then gets removed in Medium UI or simply ignored — Tistory readers tolerate it, Medium readers see the body end at References.
- First line: H1 (`# Title`). Medium's web editor maps the first H1 in a fresh empty draft to the title slot, so the artifact MUST start with H1 — no preface comments, no front matter, no kicker line.
- TOC: the `<!-- toc:begin -->` / `<!-- toc:end -->` markers are stripped, but the TOC body lines are kept (Medium has no native series nav).
- Image refs: during markdown processing, image refs are kept as relative local paths (`../../../assets/...`). During HTML rendering (`to-medium-html.py`), PNGs are inlined as base64 `data:` URIs so the `.html` artifact is self-contained for browser-paste publishing. The publishing repo is private, so `raw.githubusercontent.com` URLs are not used.
- Headings: H3+ are demoted (Medium import compatibility).
- Tables: 2-col → `- **key**: value` bullets; 3-col → `**label**` header + nested `- key: value` bullets; 4+ col → kept as raw GFM table with `<!-- TODO: render this table as PNG -->` marker (Medium has no native table renderer; wide tables need manual PNG conversion on publish).

## Series TOC rules (apply to every post, no exceptions)

The TOC reflects each post's position in the series. Three states:

- **Past posts (idx < current)**: `- [Title](./NN-slug.md)` — linked, plain
- **Current post (idx == current)**: `- **Title (현재 글)**` (ko) or `- **Title (current)**` (en/medium) — bold, no link
- **Future posts (idx > current)**: `- Title (예정)` (ko) or `- Title (upcoming)` (en/medium) — no link, no bold

This rule holds even when all posts are already written. The TOC describes the reader's journey, not publication state.

### Variant-specific labels

- **ko**: heading `## 시리즈 목차`, current marker `(현재 글)`, future marker `(예정)`
- **en**: heading `## In this series`, current marker `(current)`, future marker `(upcoming)`
- **medium**: same as en, but links use `./NN.md` form (filename = numeric prefix only)

### Title source

TOC entry titles are pulled from each post's H1 (single source of truth). Never duplicate title strings into README or scripts.

## Reference section heading

- **ko**: `## 참고 자료` (never `## References`, `## 참고문헌`, `## 참고`)
- **en/medium**: `## References`

## Tag line (source posts only — ko/en)

- Format: `Tags: A, B, C, D` (visible plain text, NOT an HTML comment)
- Position: very last line of every **source** post (after the references section, separated by one blank line)
- Source of truth: `SERIES_TAGS` in `.sisyphus/medium/finalize-posts.py`
- Same set is used for ko and en source posts; medium artifacts surface the same tags as a leading `<!-- tags: ... -->` HTML comment instead (see "Medium artifact rules")
- The tag line is visible to readers (Tistory); it doubles as a copy-paste source when publishing to Tistory and Medium

## Image conventions

- Path pattern: `assets/<series>/<NN>/<NN>-<idx>-<slug>.{ko|en}.png`
- ko slug = en counterpart heading slug (preserves ko/en file-name symmetry)
- All diagrams source: Mermaid → PNG via `.sisyphus/medium/mermaid-to-png.py`
- ko/en/medium bodies all reference local relative paths (`../../../assets/...`); during HTML rendering PNGs are inlined as base64 `data:` URIs in the `.html` artifact

## Image caption (alt text) policy

Image alt text in `![alt](src)` is **double duty**: it renders as a visible caption on Medium / in ebooks AND it is read aloud by screen readers. Treat captions as short descriptive fragments that name what the diagram is showing — not headlines, not body sentences, not questions.

### Korean (ko)

- 형태: **서술형 명사구** (subject + relationship/flow/comparison)
- 길이: **4–12어절**, 한 줄 안에서 끝낼 것
- 끝맺음: `흐름`, `구조`, `경로`, `관계`, `차이`, `비교`, `경계`, `단계`, `조건`, `반응` 같은 명사로 마무리
- **금지**: `~입니다` / `~습니다` 종결어미, 의문형 (`~할까`, `~인가`), 마침표/물음표/느낌표
- 좋음: `트리거가 함수를 깨우는 흐름`, `트래픽 급증 시 플랜별 확장 반응`, `Revision weight와 scale의 관계`
- 나쁨: `트리거는 함수를 깨우는 원인입니다`, `트래픽이 늘면 어떻게 반응할까`

### English (en)

- 형태: **sentence-case descriptive fragment** (subject + relationship/flow/comparison)
- 길이: **4–10 words**
- 케이싱: **sentence case only** (no Title Case)
- **금지**: 의문형, full sentences, trailing punctuation, Title Case
- 좋음: `Request flow with ARR Affinity enabled`, `Pre-norm and post-norm LayerNorm placement`
- 나쁨: `How Is This Different From a Traditional Web App?`, `What ZipDeploy actually means`

### Universal rules

- **절 번호 prefix 항상 제거** (`4.`, `5.`, `1)`)
- **나란한 H2/H3 그대로 복붙 금지** — 캡션은 그림이 보여주는 관점을 더한다
- **백틱 금지** in alt text — 식별자는 평문으로 (`host.json`, `FUNCTIONS_WORKER_PROCESS_COUNT`)
- **Em dash 기본 회피** — 필요하면 `:` 한 번만
- **scare quotes 금지** — 강조용 따옴표 쓰지 않음
- **위치 어휘 금지** (`left side`, `blue box`, `top arrow`) unless position itself is the point
- **Vague 라벨 금지**: `Big picture`, `한 화면으로`, `Decision tree`, `One diagram first`
- ko/en counterpart 이미지는 **같은 의미 기반 paired rewrite**, 독립적 스타일 선택 아님

### Anti-patterns (lint blocks these)

- Heading clones: `배포`, `Big picture`
- Question captions: `기존 웹 앱과 뭐가 다른가`, `Why only some users fail sometimes`
- Body sentences: `Worker는 ... 실체입니다`
- Section/list prefixes: `4.`, `5.`, `1)`
- Formatting noise: backticks, scare quotes, multiple separators, emoji
- Editorial slogans: `No Peeking at the Future`, `3am`

### Verification

```bash
python3 scripts/lint_captions.py    # exits 1 on banned patterns
```

## Pinned tag

External and intra-repo URLs in `medium/` files MUST pin to a commit/tag, never `master`/`HEAD`/`main`.
Current pin: `f24a126` (defined in `.sisyphus/medium/to-medium.py` as `TAG`).
When regenerating medium variants, update `TAG` first, regenerate, then commit.

## Mermaid conventions

- `flowchart LR` for architecture diagrams (event source on the left)
- Node/edge labels containing `()`, `/`, `;`, or `(.NET)` MUST be wrapped in quotes: `["Label (with parens)"]`
- Minimize crossing arrows; reorder subgraphs before adding more edges
- en diagrams: English labels only; ko diagrams: Korean labels

## Tone & style

- ko: natural `~입니다` register, senior-engineer voice, no translation smells
- en: senior-engineer Medium voice, no AI slop
- No emoji (use text `Pass`/`Fail` instead of `✅`/`❌`)
- All user-facing code is Python (FastAPI / Flask)

## Quality gates before commit

Run from repo root:

```bash
python3 .sisyphus/medium/finalize-posts.py    # idempotent: tags + TOC + ko refs
.sisyphus/style/check-ko.sh                   # ko translation-smell + im-not-ai S1 check (must exit 0)
```

Korean writing additionally follows the **humanize-korean** ruleset mirrored at `.sisyphus/skills/humanize-korean/` (source: [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai), MIT). Before drafting any `ko/*.md`, scan `.sisyphus/skills/humanize-korean/quick-rules.md` S1 patterns and avoid them from the first line. `check-ko.sh` enforces grep-detectable S1 patterns automatically.

After regenerating medium variants:

```bash
python3 .sisyphus/medium/to-medium.py         # regenerate medium/ from en/
python3 .sisyphus/medium/finalize-posts.py    # re-apply tags+TOC to new medium/ files
```

## Operational scripts (in `.sisyphus/medium/`)

- `mermaid-to-png.py` — convert mermaid blocks in ko/en bodies to PNG references
- `to-medium.py` — convert `en/*.md` to `medium/<NN>.html` (browser-paste-ready: H1-first, base64-inline PNGs, native HTML headings/lists/tables/code, trailing visible Tags line)
- `to-medium-html.py` — helper module imported by `to-medium.py`; renders Medium-flavored markdown text to a self-contained HTML document
- `finalize-posts.py` — idempotent: tag line, ko refs heading, series TOC (Azure series, ko/en/medium variants)
- `finalize-ai-web-dev.py` — idempotent: same operations adapted for the single-variant `ai-web-dev-101/` series
- `add-tags.py` — superseded by `finalize-posts.py`; kept for reference

All finalizers are idempotent. Re-run any time the series catalog changes.

## Korean naturalization agent rule

When drafting or editing any `ko/*.md` post, run all Korean text through a naturalization pass before committing. The goal is to strip AI-generated phrasing and restore a natural senior-engineer voice.

Prompt to apply (ChatGPT Project / Claude Project / Gemini Gem — set this as the system instruction):

```
아래 글을 자연스러운 한국어로 다듬어줘.

조건:
- AI가 쓴 것 같은 표현을 줄일 것
- 번역투를 제거할 것
- 문장은 너무 딱딱하지 않게 할 것
- 의미는 바꾸지 말 것
- 기술 용어는 유지할 것
- 과장된 표현은 줄일 것
- 블로그 독자가 읽기 쉽게 바꿀 것
```

Recommended setup: create a dedicated "한국어 글 자연화" agent in your preferred LLM platform (ChatGPT Project, Claude Project, or Gemini Gem) with the prompt above pinned as the system instruction. Paste draft sections in, copy the output back.

This pass is in addition to the existing `check-ko.sh` gate (which catches grep-detectable S1 patterns automatically). The naturalization agent handles subtler stylistic issues that static checks cannot flag.

## When adding a new post

1. Write `ko/<NN>-<slug>.md` and `en/<NN>-<slug>.md` (full body, references included)
2. Insert mermaid diagrams as `flowchart LR` blocks
3. Run `python3 .sisyphus/medium/mermaid-to-png.py <ko-file> <en-file>`
4. Run `python3 .sisyphus/medium/to-medium.py <series>/en` to generate `medium/<NN>.html`
5. Run `python3 .sisyphus/medium/finalize-posts.py` to insert tags + TOC + normalize refs
6. Update `README.md` series table
7. Verify: no `## References` in ko, all 3 variants have tag + TOC, mermaid count = 0

## Post status lifecycle

Article-level status values (set in front matter `status:` field):

| Status | Meaning |
| --- | --- |
| `draft` | Skeleton or placeholder — not ready for any review |
| `content-ready` | Body complete, references in, no code yet checked |
| `code-checked` | All code blocks verified to run on stated versions |
| `publish-ready` | Final polish done, channel-specific titles set |
| `ready` | Legacy alias for `publish-ready`; prefer `publish-ready` in new posts |
| `published` | Live on at least one channel; `published:` URLs present |
| `needs-update` | Content is stale (API changes, deprecated features) |

Series-level `status:` in series.yaml uses: `planned`, `draft`, `active`, `complete`.

When bumping an article from `content-ready` → `code-checked`, add or confirm `last_reviewed: YYYY-MM-DD`.

## A-grade post structure

Every post targeting `publish-ready` or higher MUST include, in order:

1. H1 title (matches `title:` in front matter)
2. "이 글에서 답할 질문" block (ko) / "Questions this post answers" (en) — 3–5 bullet questions
3. One-sentence mental model (quoted block `> ...`)
4. Key diagram (Mermaid → PNG)
5. Minimal runnable example
6. Code walkthrough ("이 코드에서 봐야 할 것" / "What to notice in this code")
7. Common confusion points ("실무에서 헷갈리는 지점" / "Where engineers get confused")
8. Checklist
9. Summary / next post link (`blog-only` block)
10. Series TOC
11. References
12. Tags line

Items 2, 6, 7 are the most commonly missing. Check these before marking `publish-ready`.

## Channel-specific title fields (optional, recommended for publish-ready)

When a post is close to publication, add channel-specific titles to front matter:

```yaml
title: Azure Functions란? — 이벤트가 함수를 호출하는 세상    # canonical (H1 must match)
seo_title: Azure Functions란? Trigger, Binding, Host 구조 한 번에 이해하기
hashnode_title: What Is Azure Functions? — A World Where Events Call Your Code
medium_title: Azure Functions Is Not Just "Serverless"
ebook_title: The Azure Functions Mental Model
```

`title` is required and must match H1. Others are optional. `check_frontmatter.py` accepts all five.

## Syncing per-article metadata

After adding, renaming, or bulk-updating article status:

```bash
python3 scripts/sync_series_per.py
```

This reads front matter from disk and writes the `per.{ko,en}.articles` block in `series.yaml`. Run before `make ebook` or any eBook export.
