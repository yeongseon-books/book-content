# Publishing Guide

이 문서는 `content/` 아래의 원본 Markdown을 Tistory, Medium, MkDocs, eBook source로 변환하는 규칙을 정의한다.

> **현재 상태**: 모든 시리즈가 `content/<series>/` 아래로 이동 완료되었다 (Phase 6 완료). 이행 전 경로(`<series>/{ko,en,medium}/`)는 더 이상 사용하지 않는다.

---

## Writing Rules vs Publishing Rules

이 문서는 원본 Markdown을 각 플랫폼 산출물로 변환하는 **기술적 규칙**을 다룬다.

원고를 어떻게 써야 하는가는 아래 문서를 따른다.

- [`BLOG_WRITING_GUIDE.md`](./BLOG_WRITING_GUIDE.md) — Tistory/Medium 블로그 글 작성 규칙 (SEO 제목, 글 구조, blog-only 블록, 발행 체크리스트)
- [`EBOOK_WRITING_GUIDE.md`](./EBOOK_WRITING_GUIDE.md) — 시리즈를 eBook으로 묶을 때의 원고 구성 규칙 (장 구조, ebook-only 블록, Part 구성, 반복 제거)
- [`STYLE_GUIDE.md`](./STYLE_GUIDE.md) — 문체, 이미지, 코드, 태그, 참고자료 공통 규칙

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

> **현행 워크플로우**: `content/<series>/medium/<NN>.html` 이 `exports/medium/` 의 역할을 수행한다. `scripts/export_medium.py` 는 이 .html 파일을 `exports/medium/` 로 복사하는 thin wrapper다.

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

## 3. Medium Publishing (English)

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
- 이미지는 base64 data URI로 인라인 처리되어 외부 URL 없이 자급자족
- 하단 `Tags: A, B, C` visible 라인을 Medium의 태그 입력칸에 수동 복사

### 변환 규칙

- `ebook-only` 블록은 제거한다.
- `blog-only` 블록은 유지한다.
- H3+ 헤딩은 demote한다 (Medium 호환성).
- 이미지는 base64 data URI로 인라인 처리한다 (저장소가 private이므로 raw URL 불가).
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

---

## 4. MkDocs Publishing

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

### 명령 (예정)

```bash
python3 scripts/build_docs.py
mkdocs serve
```

---

## 5. eBook Source Export

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

## 6. 변형(variant)별 비교

| 항목 | Tistory (ko) | Medium (en) | MkDocs (ko/en) | eBook source |
| --- | --- | --- | --- | --- |
| 산출물 형식 | .md | **.html** | .md | .md |
| `blog-only` 블록 | 유지 | 유지 | 제거 | 제거 |
| `ebook-only` 블록 | 제거 | 제거 | 옵션 | 유지 |
| Visible 하단 `Tags:` 라인 | 유지 | **유지** (Medium 태그칸에 수동 복사) | 제거 | 제거 |
| TOC `<!-- toc:* -->` 마커 | 유지 | 제거 (마커만; TOC 본문은 유지) | 제거 (전체) | 제거 (전체) |
| 이미지 경로 | 상대 / 호스팅 | **base64 data URI (인라인)** | 상대 (`docs/` 기준) | 번들 내부 상대 |
| Mermaid | PNG | PNG | mermaid 또는 PNG | PNG |
| H3+ demote | 그대로 | demote | 그대로 | 그대로 |
| `finalize-posts.py` 적용 | 적용 | **스킵** (`to-medium.py` 단독 책임) | N/A | N/A |

---

## 7. Quality Gates

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
