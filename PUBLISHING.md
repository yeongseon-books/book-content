# Publishing Guide

이 문서는 `content/` 아래의 원본 Markdown을 Tistory, Hashnode, Medium, MkDocs, eBook source로 변환하는 규칙을 정의한다.

## 출판 모델

본 저장소의 발행 모델은 **blog-first / book-later**이다.

1. 블로그 글을 먼저 쓴다 (Tistory, Hashnode, Medium).
2. 쌓인 시리즈를 eBook으로 묶는다.
3. 이미지는 private `book-content`에 원본을 두고, public `book-public-assets`를 거쳐 외부에 제공한다.

이미지 자산 정책의 상세 사항은 [`ASSET_POLICY.md`](./ASSET_POLICY.md)를 참조한다.

> **현재 상태**: 모든 시리즈가 `content/<series>/` 아래로 이동 완료되었다 (Phase 6 완료). 이행 전 경로(`<series>/{ko,en,medium}/`)는 더 이상 사용하지 않는다.

---

## Writing Rules vs Publishing Rules

이 문서는 원본 Markdown을 각 플랫폼 산출물로 변환하는 **기술적 규칙**을 다룬다.

원고를 어떻게 써야 하는가는 아래 문서를 따른다.

- [`BLOG_WRITING_GUIDE.md`](./BLOG_WRITING_GUIDE.md) — Tistory/Hashnode/Medium 블로그 글 작성 규칙 (SEO 제목, 글 구조, blog-only 블록, 발행 체크리스트)
- [`EBOOK_WRITING_GUIDE.md`](./EBOOK_WRITING_GUIDE.md) — 시리즈를 eBook으로 묶을 때의 원고 구성 규칙 (장 구조, ebook-only 블록, Part 구성, 반복 제거)
- [`STYLE_GUIDE.md`](./STYLE_GUIDE.md) — 문체, 이미지, 코드, 태그, 참고자료 공통 규칙

---

## Publication Pipelines

`book-content`는 하나의 canonical content base를 다섯 가지 발행 파이프라인으로 변환한다.

| Pipeline | Platform | Source | Output | Purpose |
| --- | --- | --- | --- | --- |
| Korean Blog | Tistory | `content/<series>/ko/*.md` | `exports/tistory/<series>/*.md` | 한국어 검색 유입용 블로그 |
| English Blog | Hashnode | `content/<series>/en/*.md` | (Hashnode에 직접 Markdown 붙여넣기) | 한국어 원문의 충실한 영어 대응본 |
| Medium | Medium | `content/<series>/en/*.md` + adaptation | `content/<series>/medium/*.html` | 영어권 독자용 발행 변형 |
| Web Book | MkDocs | `content/<series>/{ko,en}/*.md` | `docs/` | 웹북 형태의 학습 콘텐츠 |
| eBook | private `mkdocs-ebook` | `content/<series>/{ko,en}/*.md` + ebook-only blocks | `exports/ebook-source/<series>-<lang>/` | 책 단위 학습형 원고 |

`ko/`와 `en/`은 canonical source다. `medium/`은 `to-medium.py`가 생성하는 발행 변형 산출물이며 canonical source가 아니다.

> `content/<series>/medium/`은 generated Medium draft 디렉터리다.
> canonical source는 `ko/`와 `en/`이며, `medium/`은 발행 편의를 위한 변형 산출물이다.

---

## 1. Source Principle

모든 글은 `content/` 아래에서 작성한다.

```text
content/<series>/<language>/<NN>-<slug>.md

예:
content/azure-functions-101/ko/01-what-is-azure-functions.md
content/azure-functions-101/en/01-what-is-azure-functions.md
```

플랫폼별 최종 산출물은 `exports/` 아래에 생성한다.

```text
exports/tistory/<series>/<NN>-<slug>.md
exports/medium/<series>/<NN>.html
exports/ebook-source/<series>-<lang>/...
```

> **Hashnode**: `scripts/export_hashnode.py`로 `en/*.md`를 변환하여 `exports/hashnode/<series>/`에 생성한다. `make hashnode SERIES=<id>` 또는 `make hashnode-one SERIES=<id> EPISODE=<N>`으로 실행한다.

> **Medium**: `content/<series>/medium/<NN>.html`이 `exports/medium/`의 역할을 수행한다. `scripts/export_medium.py`는 이 .html 파일을 `exports/medium/`로 복사하는 thin wrapper다.

---

## 2. Tistory Publishing (Korean)

### 대상

```text
content/<series>/ko/*.md
```

### 변환 결과

```text
exports/tistory/<series>/<NN>-<slug>.md
```

### 규칙

- `ebook-only` 블록은 제거한다.
- `blog-only` 블록은 유지한다.
- Mermaid 다이어그램은 PNG로 export한다 (`.sisyphus/medium/mermaid-to-png.py`).
- 이미지 경로는 Tistory 업로드 방식에 맞게 정리한다.
- 하단 `Tags: A, B, C, D` visible 라인은 **그대로 유지한다**. Tistory 태그 칸에 그대로 복사한다.
- 시리즈 TOC `<!-- toc:begin --> ... <!-- toc:end -->` 블록은 그대로 유지한다.

### 명령 (예정)

```bash
python3 scripts/export_tistory.py azure-functions-101 --episode 1
```

---

## 3. Hashnode Publishing (English Blog)

> **현재 상태**: `export_hashnode.py`를 통해 `en/*.md`를 변환하여 `exports/hashnode/`에 생성한다.

### 대상

```text
content/<series>/en/*.md
```

### 변환 결과

```text
exports/hashnode/<series>/<NN>-<slug>.md
```

Hashnode는 Markdown 네이티브 에디터를 제공하므로 HTML 변환 없이 `.md`를 사용한다.

### 규칙

- 목적: `ko/` 원문의 충실한 영어 대응본. 개발자 브랜딩 및 eBook 유입 채널.
- 구조, 기술적 주장, 코드, 그림, 참고자료를 `ko/` 원문과 최대한 일치시킨다.
- Medium처럼 hook 중심으로 재작성하지 않는다.
- `ebook-only` 블록은 제거한다.
- `blog-only` 블록은 유지한다 (마커는 제거, 본문은 유지).
- 하단 `Tags:` 라인은 Hashnode tags에 활용한다.
- 이미지는 canonical source의 public GitHub Pages URL을 그대로 통과시킨다. `--local-assets`로 상대 경로로 강제 변환 가능.
- TOC `<!-- toc:* -->` 마커는 제거되고 TOC 본문은 유지된다.
- 저작권 표시가 글 하단에 visible로 자동 삽입된다 (`series.yaml` meta 기반).

### 명령

```bash
python3 scripts/export_hashnode.py azure-functions-101 --episode 1
python3 scripts/export_hashnode.py azure-functions-101 --all
```

---

## 4. Medium Publishing (English)

> Medium 산출물은 `en/`의 strict translation output이 아니다.
> `en/`의 기술적 내용, 코드, 그림, 참고자료를 유지하되, Medium 독자에게 맞게 제목, opening, transition, ending을 조정할 수 있는 publication adaptation이다.

### 대상

```text
content/<series>/en/*.md
```

### 산출물

```text
content/<series>/medium/<NN>.html   ← to-medium.py 가 생성
exports/medium/<series>/<NN>.html   ← export_medium.py 가 복사
```

### 산출물 형식

Medium 산출물은 **브라우저 붙여넣기용 .html** 파일이다.

- Chrome에서 열고 전체 선택(Ctrl+A) → 복사 → 빈 Medium 초안에 붙여넣기
- 첫 번째 `<h1>` 이 Medium의 제목 슬롯에 매핑된다
- 이미지는 기본적으로 canonical source의 public GitHub Pages URL을 그대로 통과시킨다(`--asset-mode public`). `--asset-mode inline`을 사용하면 base64 data URI로 내장할 수 있다. Medium 붙여넣기에서 이미지가 유지되지 않으면, 원본 경로를 참고해 PNG를 Medium UI에 수동 업로드한다.
- 하단 `Tags: A, B, C` visible 라인을 Medium의 태그 입력칸에 수동 복사

### 변환 규칙

- `ebook-only` 블록은 제거한다.
- `blog-only` 블록은 유지한다.
- H3+ 헤딩은 demote한다 (Medium 호환성).
- 이미지는 기본적으로 canonical source의 public GitHub Pages URL을 그대로 통과시킨다(`--asset-mode public`). `--asset-mode inline`(base64) 또는 `--asset-mode local`(상대 경로로 강제 변환)도 선택 가능하다. Medium 붙여넣기에서 이미지가 유지되지 않으면 PNG를 수동 업로드한다. private repository의 `raw.githubusercontent.com` URL은 사용하지 않는다.
- TOC 처리: `<!-- toc:begin --> ... <!-- toc:end -->` 마커는 제거되지만 TOC 본문 라인은 유지된다.
- 태그 처리: 하단 visible `Tags:` 라인은 **그대로 유지**한다. Medium 발행 시 태그칸에 수동 복사한다.
- `finalize-posts.py` 는 `medium/` 디렉토리를 스킵한다. medium 변형의 태그·TOC 는 `to-medium.py` 단독 책임이다.

### 명령

```bash
# medium/ 디렉토리 재생성
python3 .sisyphus/medium/to-medium.py content/<series>/en

# exports/medium/<series>/ 로 복사
python3 scripts/export_medium.py <series-id> --episode N
python3 scripts/export_medium.py <series-id> --all
```

### Medium 발행 체크리스트

- [ ] `python3 .sisyphus/medium/to-medium.py content/<series>/en`을 실행했다.
- [ ] 생성된 `content/<series>/medium/<NN>.html`을 Chrome에서 열었다.
- [ ] 전체 선택 후 Medium 빈 초안에 붙여넣었다.
- [ ] 첫 번째 H1이 Medium 제목 슬롯에 들어갔는지 확인했다.
- [ ] 이미지가 정상 표시되는지 확인했다.
- [ ] 깨진 이미지는 원본 상대 경로를 참고해 Medium UI에 수동 업로드했다.
- [ ] 마지막 `Tags:` 라인을 Medium tag input에 복사했다.
- [ ] 본문에 남은 `Tags:` 라인은 삭제했다.
- [ ] wide table 또는 TODO table marker가 남아 있지 않은지 확인했다.

---

## 5. MkDocs Publishing

### 대상

한국어/영어 모두 MkDocs 웹북으로 제공할 수 있다.

```text
docs/ko/<series>/...
docs/en/<series>/...
```

### 규칙

- `content/` 에서 `docs/` 로 복사 또는 변환한다 (`scripts/build_docs.py` 가 파일을 materialize).
- 하단 visible `Tags:` 라인과 `<!-- toc:begin -->...<!-- toc:end -->` 블록은 MkDocs 빌드 시 제거한다.
- `blog-only` 블록은 기본적으로 제거한다.
- `ebook-only` 블록은 MkDocs 웹북에서는 선택적으로 포함한다 (옵션 플래그).
- nav 메타데이터는 `scripts/build_series_index.py` 가 `series.yaml` 에서 생성하여 `mkdocs.yml` 에 inject 한다.

### 명령

```bash
# 검증용 build (strict mode)
make docs-build

# 로컬 preview
make docs-serve
```

---

## 6. eBook Source Export

`mkdocs-ebook`은 private repository이므로 본 저장소에서는 eBook PDF/EPUB를 직접 만들지 않는다. 대신 private builder가 입력으로 사용할 수 있는 source bundle만 생성한다.

### 변환 결과

```text
exports/ebook-source/<series>-<lang>/
├── mkdocs.yml
├── docs/
│   ├── index.md
│   ├── 01-*.md
│   └── ...
└── assets/
```

### 규칙

- `blog-only` 블록은 제거한다.
- `ebook-only` 블록은 포함한다.
- 챕터 순서는 시리즈의 `series.yaml` `episodes:` 배열을 따른다.
- 이미지 경로를 bundle 내부 기준으로 정리한다 (`assets/` 를 bundle 안으로 복사).
- 하단 visible `Tags:` 라인은 제거한다.
- 시리즈 TOC 블록은 제거한다.

### 명령 (예정)

```bash
python3 scripts/export_ebook_source.py azure-functions-101 --lang ko
```

---

## 7. 변형(variant)별 비교

| 항목 | Tistory (ko) | Hashnode (en) | Medium (en adapted) | MkDocs (ko/en) | eBook source |
| --- | --- | --- | --- | --- | --- |
| 산출물 형식 | .md | .md | **.html** | .md | .md |
| `blog-only` 블록 | 유지 | 유지 | 유지 | 제거 | 제거 |
| `ebook-only` 블록 | 제거 | 제거 | 제거 | 옵션 | 유지 |
| Visible 하단 `Tags:` 라인 | 유지 | 유지 | **유지** (Medium 태그칸에 수동 복사) | 제거 | 제거 |
| TOC `<!-- toc:* -->` 마커 | 제거 (마커만; TOC 본문은 유지) | 제거 (마커만; TOC 본문은 유지) | 제거 (마커만; TOC 본문은 유지) | 제거 (전체) | 제거 (전체) |
| 이미지 경로 | **public URL (기본)** / local | **public URL (기본)** / local | **public URL (기본)** / inline / local | 상대 (`docs/` 기준) | 번들 내부 상대 |
| Mermaid | PNG | PNG | PNG | mermaid 또는 PNG | PNG |
| H3+ demote | 그대로 | 그대로 | demote | 그대로 | 그대로 |
| `finalize-posts.py` 적용 | 적용 | 적용 | **스킵** (`to-medium.py` 단독 책임) | N/A | N/A |
| 저작권 표시 | visible (한국어) | visible (영어) | 미삽입 (Medium 자체 약관) | N/A | `mkdocs-ebook` builder |

---

## 9. External Asset URL Policy

외부 발행(Medium, Tistory, Hashnode)에서 이미지를 참조할 때의 규칙이다.

- Canonical source(`ko/*.md`, `en/*.md`)는 `book-public-assets`의 public URL을 직접 참조한다. Tistory/Hashnode/Medium/MkDocs는 동일한 URL을 그대로 통과시키므로 발행 시점의 경로 재작성이 필요 없다.
- `series.yaml`의 `meta.asset_base_url`은 정책 참조용 단일 출처(`https://yeongseon-books.github.io/book-public-assets`)이며 trailing slash를 넣지 않는다.
- 최종 이미지 URL 예시: `{asset_base_url}/assets/{series}/{NN}/{file}.png`
- Medium은 `--asset-mode` 플래그로 `public` (기본: 그대로 통과) / `inline` (base64) / `local` (상대 경로)을 선택한다.
- Tistory는 `--local-assets` 플래그로 상대 경로로 강제 변환할 수 있다. 기본은 public URL 통과.
- eBook exporter는 자동으로 public URL을 로컬 `assets/...` 경로로 역재작성한다 (bundle self-contained, ASSET_POLICY.md §eBook 예외).
- `check_links.py`는 외부 public asset URL을 검증하지 않는다 (로컬 파일 존재 여부만 확인).

---

## 8. Quality Gates

```bash
# 1. visible Tags + TOC + ko refs heading 정합성 (idempotent)
python3 .sisyphus/medium/finalize-posts.py

# 2. ko 문체 검증 (translation smells + im-not-ai S1)
.sisyphus/style/check-ko.sh
```

medium 변형 재생성 시:

```bash
# 3. medium/ 디렉토리 재생성 (.html 산출)
python3 .sisyphus/medium/to-medium.py content/<series>/en

# 4. tags + TOC 재적용 (medium/ 스킵됨, ko/en 에만 적용)
python3 .sisyphus/medium/finalize-posts.py
```
