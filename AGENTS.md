# Repository Agent Rules

> Persistent conventions for any agent (human or AI) working in this repository.

## Prime Directive — Quality Over Speed

이 저장소에서 일하는 모든 에이전트(인간/AI)는 다음을 절대 원칙으로 한다.

1. **시간이 오래 걸리는 것은 문제가 아니다. 제대로 하지 않는 것이 문제다.**
2. 분량/시리즈 수가 많다는 이유로 작업을 축소하거나, 병합하거나, 자동화 단순화로 품질을 희생하지 않는다.
3. "시간이 오래 걸립니다" 같은 경고로 사용자의 결정을 흔들지 않는다. 사용자가 시간 제약을 직접 명시하지 않는 한, 에이전트는 시간 비용을 이유로 더 빠르지만 더 나쁜 옵션을 권하지 않는다.
4. 의심스러우면 더 작은 단위로 쪼개고, 검증을 더 추가하고, 사용자 결정을 받는다. "한 번에 다 처리"는 default가 아니다.
5. 모든 변경은 검증 가능해야 한다. 검증 스크립트가 없다면 변경 전에 추가한다.
6. 골든 레퍼런스(`content/azure-app-service-101/ko/01-what-is-app-service.md` 등)는 절대 수정하지 않는다. 다른 글의 품질을 그 수준으로 올리는 것이 목표다.

위 원칙은 다른 모든 규칙보다 우선한다. 다른 규칙과 충돌하면 이 원칙이 이긴다.

## Repository Name

- **현재**: `yeongseon-books/book-content`
- **이전**: `yeongseon-books/technical-content` (Phase 9 2차 rename)
- **이전**: `yeongseon-books/tech-writing` (Phase 9 1차 rename)
- **최초**: `yeongseon-books/tech-blog`

## Canonical Source

1. Canonical source는 항상 `content/<series>/{ko,en}/`이다.
2. `content/<series>/medium/`은 `.sisyphus/medium/to-medium.py`가 생성하는 산출물이므로 직접 수정하지 않는다.
3. 경로는 hardcode하지 말고 `series.yaml`의 `path:` 필드를 기준으로 해석한다.
4. 시리즈 카탈로그의 단일 출처는 [`series.yaml`](./series.yaml)이다. 인간이 읽는 요약은 [`SERIES.md`](./SERIES.md).
5. 시리즈 순서는 카테고리별 학습 커리큘럼 순서를 따른다. 순서를 변경할 때는 `series.yaml`과 프로필 README(`yeongseon-books/.github/profile/README.md`) 두 곳을 반드시 함께 맞춘다. `SERIES.md`는 `scripts/build_series_index.py`가 `series.yaml` 순서대로 자동 생성한다.

## Before Editing Content

1. `series.yaml`과 해당 시리즈의 `content/<series>/series.yaml`을 확인한다.
2. 글의 front matter를 읽고 `status`, `targets`, `tags`를 파악한다.
3. Front matter 규격은 [`CONTENT_MODEL.md`](./CONTENT_MODEL.md) 참조.

## Post Structure (mandatory order)

Every source post (`ko/*.md`, `en/*.md`) MUST have, top to bottom:

1. **H1 title** (`# Title`) — front matter `title`과 일치
2. **Series intro line** — H1 직후 도입 단락 안에 한 문장 (`이 글은 {시리즈 표시명} 시리즈의 {첫 번째 / N번째 / 마지막} 글입니다.`)
3. **Body** (sections, code, images)
4. **Series TOC block** (`<!-- toc:begin -->` / `<!-- toc:end -->`)
5. **References section** (`## 참고 자료` for ko, `## References` for en)
6. **Tag line** as the very last line: `Tags: A, B, C, D`

상세 TOC rules, medium artifact rules, A-grade post structure, series intro 표준 템플릿은 [`STYLE_GUIDE.md`](./STYLE_GUIDE.md) §1 / §1.1 참조.

## Series TOC Rules

TOC는 글의 위치에 따라 세 가지 상태를 반영한다:

- Past posts (idx < current): `- [Title](./NN-slug.md)` — linked
- Current post (idx == current): `- **Title (현재 글)**` (ko) / `- **Title (current)**` (en) — bold, no link
- Future posts (idx > current): `- Title (예정)` (ko) / `- Title (upcoming)` (en) — no link

## Medium Artifact Rules

`medium/*.html`은 `en/*.md`에서 생성되는 파생물이다. 직접 수정 금지.

생성: `.sisyphus/medium/to-medium.py`
특징: H1-first, Markdown 변환 단계에서 local image path 유지, HTML 렌더링 단계에서 public GitHub Pages URL로 재작성(기본) 또는 base64-inline, trailing visible Tags line.

## Quality Gates

커밋 전에 반드시 실행:

```bash
make check
```

개별 실행:

```bash
python3 .sisyphus/medium/finalize-posts.py    # idempotent: tags + TOC + ko refs
.sisyphus/style/check-ko.sh                   # ko translation-smell + S1 check
python3 scripts/check_frontmatter.py           # front matter validation
python3 scripts/check_links.py                 # internal link check
python3 scripts/lint_captions.py               # image caption lint
python3 scripts/check_article_structure.py     # article structure (A-grade) check
```

## Status Rules

- 신규 글은 `ready`를 사용하지 않고 `publish-ready`를 사용한다.
- Status lifecycle: [`CONTENT_MODEL.md`](./CONTENT_MODEL.md) 참조.
- Historical repository names (`tech-blog`, `tech-writing`, `technical-content`)는 새 산출물, canonical 링크, 발행 URL에 사용하지 않는다. 역사적 기록은 `MIGRATION_PLAN.md`와 `ROADMAP.md`에만 남긴다.

## Writing Style

- 한국어 글은 [`STYLE_GUIDE.md`](./STYLE_GUIDE.md) + `.sisyphus/skills/humanize-korean/quick-rules.md` S1 규칙을 따른다.
- 영어 글은 senior-engineer Medium voice, no AI slop.
- Tone: ko는 `~입니다` register, en은 professional blog tone.
- No emoji (use text `Pass`/`Fail`).
- All user-facing code is Python (FastAPI / Flask).

## Image Conventions

- Path: `assets/<series>/<NN>/<NN>-<idx>-<slug>.{ko|en}.png`
- Diagrams: Mermaid → PNG via `.sisyphus/medium/mermaid-to-png.py`
- Caption policy: [`STYLE_GUIDE.md`](./STYLE_GUIDE.md) 참조.

## Mermaid Conventions

- `flowchart LR` for architecture diagrams
- Labels with `()`, `/`, `;` must be quoted: `["Label (with parens)"]`
- en diagrams: English labels; ko diagrams: Korean labels

## Public Asset Rules

- 이미지 원본은 `assets/<series>/<NN>/`에 저장한다 (private `book-content`).
- 외부 발행용 이미지는 `book-public-assets` 저장소(public)를 경유한다.
- Canonical source(`ko/*.md`, `en/*.md`)에 public asset URL을 hardcode하지 않는다.
- Exporter가 `series.yaml`의 `meta.asset_base_url`를 읽어 경로를 재작성한다.
- 동기화: `scripts/sync_assets.py`로 `book-content/assets/` → `book-public-assets/assets/`를 미러링한다.
- 상세 정책은 [`ASSET_POLICY.md`](./ASSET_POLICY.md) 참조.
## When Adding a New Post

1. `ko/<NN>-<slug>.md` + `en/<NN>-<slug>.md` 작성 (front matter 포함)
2. Mermaid → PNG: `python3 .sisyphus/medium/mermaid-to-png.py <ko-file> <en-file>`
3. Medium HTML: `python3 .sisyphus/medium/to-medium.py content/<series>/en`
4. Finalize: `python3 .sisyphus/medium/finalize-posts.py`
5. Verify: `make check`
6. Tistory export: `make tistory SERIES=<series-id>` or `make tistory-one SERIES=<series-id> EPISODE=<N>`
7. Hashnode export: `make hashnode SERIES=<series-id>` or `make hashnode-one SERIES=<series-id> EPISODE=<N>`

## Public Asset Validation

발행 전 public asset 검증:

```bash
make assets-sync-dry
make assets-sync
make assets-check
```

## Detailed References

| Topic | Document |
| --- | --- |
| 저장소 구조, 빌드 흐름 | [`ARCHITECTURE.md`](./ARCHITECTURE.md) |
| Front matter, status, series.yaml | [`CONTENT_MODEL.md`](./CONTENT_MODEL.md) |
| 블로그 글 작성 규칙 | [`BLOG_WRITING_GUIDE.md`](./BLOG_WRITING_GUIDE.md) |
| eBook 원고 규칙 | [`EBOOK_WRITING_GUIDE.md`](./EBOOK_WRITING_GUIDE.md) |
| 문체, 캡션, 태그 공통 규칙 | [`STYLE_GUIDE.md`](./STYLE_GUIDE.md) |
| 파이프라인 변환 기술 규칙 | [`PUBLISHING.md`](./PUBLISHING.md) |
| eBook export/build 정책 | [`EBOOK.md`](./EBOOK.md) |
| 시리즈 카탈로그 | [`SERIES.md`](./SERIES.md) |
| 개편 로드맵 | [`ROADMAP.md`](./ROADMAP.md) |
| Migration archive | [`MIGRATION_PLAN.md`](./MIGRATION_PLAN.md) |
| 공개 이미지 자산 정책 | [`ASSET_POLICY.md`](./ASSET_POLICY.md) |
