# Repository Agent Rules

> Persistent conventions for any agent (human or AI) working in this repository.
> Apply these rules to every post, every commit, every script run.

## Series catalog

Eight Azure series (52 posts × 3 variants = 156 markdown files):

- `azure-app-service-101/`, `azure-app-service-deep-dive/`
- `azure-functions-101/`, `azure-functions-deep-dive/`
- `azure-aks-101/`, `azure-aks-deep-dive/`
- `azure-aca-101/`, `azure-aca-deep-dive/`

Each Azure series has three variants: `ko/`, `en/`, `medium/`.

- `ko/<NN>-<slug>.md` — Tistory original (Korean)
- `en/<NN>-<slug>.md` — Medium-bound English translation
- `medium/<NN>.md` — Medium import-ready conversion of `en/` (raw URLs, bullet tables, demoted H3+, no toc markers, tags surfaced as leading HTML comment)

Plus one single-variant Korean series:

- `ai-web-dev-101/` — 7 Korean-only posts published to Tistory. Flat layout, no `ko/`/`en/`/`medium/` subfolders. Same conventions apply (H1 → tag line at the bottom → series TOC above references), with TOC heading `## 시리즈 목차` and references heading `## 참고 자료`. Series tags: `AI, LLM, 웹 개발, Python, Tutorial` (defined in `.sisyphus/medium/finalize-ai-web-dev.py`).

## Post structure (mandatory order)

Every post MUST have, top to bottom:

1. **H1 title** (`# Title`) as the first content line
2. **Body** (sections, code, images, etc.)
3. **Series TOC block** wrapped in `<!-- toc:begin -->` / `<!-- toc:end -->`
4. **References section** (`## 참고 자료` for ko, `## References` for en/medium)
5. **Tag line** as the very last line: `Tags: A, B, C, D` (visible plain text, per-series set, see `.sisyphus/medium/finalize-posts.py`)

The TOC block sits immediately above the references section, separated by a single `---` divider. The tag line sits at the very bottom of the file (after the references section), separated by one blank line. Legacy `<!-- tags: ... -->` HTML comments on line 1 are removed automatically by `finalize-posts.py`.

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

## Tag line

- Format: `Tags: A, B, C, D` (visible plain text, NOT an HTML comment)
- Position: very last line of every post (after the references section, separated by one blank line)
- Source of truth: `SERIES_TAGS` in `.sisyphus/medium/finalize-posts.py`
- Same set is used for ko, en, and medium variants
- The tag line is visible to readers (Tistory/Medium); it doubles as a copy-paste source when publishing

## Image conventions

- Path pattern: `assets/<series>/<NN>/<NN>-<idx>-<slug>.{ko|en}.png`
- ko slug = en counterpart heading slug (preserves ko/en file-name symmetry)
- All diagrams source: Mermaid → PNG via `.sisyphus/medium/mermaid-to-png.py`
- ko/en bodies reference local relative path; medium bodies reference `raw.githubusercontent.com/<owner>/<repo>/<TAG>/...`

## Pinned tag

External and intra-repo URLs in `medium/` files MUST pin to a commit/tag, never `master`/`HEAD`/`main`.
Current pin: `e8dca42` (defined in `.sisyphus/medium/to-medium.py` as `TAG`).
When regenerating medium variants, update `TAG` first, regenerate, then commit.
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
- `to-medium.py` — convert `en/*.md` to `medium/<NN>.md` (raw URLs, bullet tables, demoted headings)
- `finalize-posts.py` — idempotent: tag line, ko refs heading, series TOC (Azure series, ko/en/medium variants)
- `finalize-ai-web-dev.py` — idempotent: same operations adapted for the single-variant `ai-web-dev-101/` series
- `add-tags.py` — superseded by `finalize-posts.py`; kept for reference

All finalizers are idempotent. Re-run any time the series catalog changes.

## When adding a new post

1. Write `ko/<NN>-<slug>.md` and `en/<NN>-<slug>.md` (full body, references included)
2. Insert mermaid diagrams as `flowchart LR` blocks
3. Run `python3 .sisyphus/medium/mermaid-to-png.py <ko-file> <en-file>`
4. Run `python3 .sisyphus/medium/to-medium.py <series>/en` to generate `medium/<NN>.md`
5. Run `python3 .sisyphus/medium/finalize-posts.py` to insert tags + TOC + normalize refs
6. Update `README.md` series table
7. Verify: no `## References` in ko, all 3 variants have tag + TOC, mermaid count = 0
