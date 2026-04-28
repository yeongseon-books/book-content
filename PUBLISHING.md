# Publishing Guide

이 문서는 `content/` 아래의 원본 Markdown을 Tistory, Medium, MkDocs, eBook source로 변환하는 규칙을 정의한다.

> 현재 단계: 본 저장소는 아직 시리즈를 `content/` 로 이동하지 않았다. 본 문서는 **목표 상태(target state)** 를 기준으로 작성되었으며, 실제 동작하는 워크플로우는 [`AGENTS.md`](./AGENTS.md) 의 "Quality gates before commit" 섹션을 함께 참조한다.

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
exports/medium/<series>/<NN>.md
exports/ebook-source/<series>-<lang>/...
```

> **이행 기간**: 시리즈가 `content/`로 이동되기 전까지는 기존 위치(`<series>/{ko,en,medium}/`)를 source로 간주한다. `medium/` 변형이 `exports/medium/` 역할을 임시로 수행한다.

---

## 2. Tistory Publishing (Korean)

### 대상

```text
content/<series>/ko/*.md   (이행 후)
<series>/ko/*.md           (이행 전)
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
- SEO 제목은 front matter `seo_title` 을 우선 사용한다 (front matter 도입 후).
- 시리즈 TOC `<!-- toc:begin --> ... <!-- toc:end -->` 블록은 그대로 유지한다.

### 명령 (예정)

```bash
python3 scripts/export_tistory.py azure-functions-101 --episode 1
```

---

## 3. Medium Publishing (English)

### 대상

```text
content/<series>/en/*.md   (이행 후)
<series>/en/*.md           (이행 전)
```

### 변환 결과

```text
exports/medium/<series>/<NN>.md
```

> 현재는 `<series>/medium/<NN>.md` 가 동일한 역할을 한다. 이행 전까지는 `.sisyphus/medium/to-medium.py` 가 단일 출처이다.

### 규칙

- `ebook-only` 블록은 제거한다.
- `blog-only` 블록은 유지한다.
- 이미지 URL은 `raw.githubusercontent.com/<owner>/<repo>/<TAG>/...` 형태로 commit-pinned 절대 경로를 사용한다 (`TAG` 는 `.sisyphus/medium/to-medium.py` 상단에서 관리).
- 표는 Medium에서 깨지므로 bullet table 형태로 demote한다 (이미 `to-medium.py` 가 처리).
- H3 이상의 헤딩은 demote한다 (Medium 호환).
- 내부 상대 링크는 GitHub 절대 URL로 변환한다.
- Medium 제목은 front matter `medium_title` → `seo_title` → `title` 순으로 fallback (front matter 도입 후).
- 태그 처리(현행 `to-medium.py` 기준):
  - 하단 visible `Tags:` 라인은 **제거**한다 (Medium UI 가 자체 태그 입력칸을 갖기 때문).
  - 파일 첫 줄에 `<!-- tags: A, B, C, D -->` HTML comment 한 줄로 surface 한다 (Medium 발행 시 태그칸에 그대로 복사할 수 있도록).
  - `finalize-posts.py` 는 `medium/` 디렉토리를 스킵하므로, medium 변형의 태그/TOC 는 `to-medium.py` 단독 책임이다.
- TOC 처리: `<!-- toc:begin --> ... <!-- toc:end -->` 마커는 제거되지만 TOC 본문 라인은 유지된다 (Medium 에는 자체 nav 가 없으므로 시리즈 인덱스 역할).

### 명령 (예정)

```bash
python3 scripts/export_medium.py azure-functions-101 --episode 1
```

### 이행 전 현행 명령

```bash
python3 .sisyphus/medium/to-medium.py <series>/en
python3 .sisyphus/medium/finalize-posts.py
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
- 하단 visible `Tags:` 라인과 `<!-- toc:begin -->...<!-- toc:end -->` 블록은 MkDocs 빌드 시 제거한다 (사이트 nav가 같은 역할 수행).
- `blog-only` 블록은 기본적으로 제거한다.
- `ebook-only` 블록은 MkDocs 웹북에서는 선택적으로 포함한다 (옵션 플래그).
- nav 메타데이터는 `scripts/build_series_index.py` 가 `series.yaml` 에서 생성하여 `mkdocs.yml` 에 inject 한다 (단일 소유자). `build_docs.py` 는 nav 를 만지지 않는다.

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
- eBook 전용 Preface/Index 페이지를 추가한다 (`templates/ebook-preface.md`, `templates/ebook-index.md`).
- 이미지 경로를 bundle 내부 기준으로 정리한다 (`assets/` 를 bundle 안으로 복사).
- 하단 visible `Tags:` 라인은 제거한다 (book에는 노출 불필요).
- 시리즈 TOC 블록은 제거한다 (book에는 자체 TOC가 있음).

### 명령 (예정)

```bash
python3 scripts/export_ebook_source.py azure-functions-101 --lang ko
```

이후 private `mkdocs-ebook` 에서:

```bash
mkdocs-ebook build exports/ebook-source/azure-functions-101-ko
```

---

## 6. 변형(variant)별 비교

| 항목 | Tistory (ko) | Medium (en) | MkDocs (ko/en) | eBook source |
| --- | --- | --- | --- | --- |
| `blog-only` 블록 | 유지 | 유지 | 제거 | 제거 |
| `ebook-only` 블록 | 제거 | 제거 | 옵션 | 유지 |
| Visible 하단 `Tags:` 라인 | 유지 | **제거** (leading HTML comment 로 대체) | 제거 | 제거 |
| Leading `<!-- tags: ... -->` 라인 | 없음 | **있음** (`to-medium.py` 가 첫 줄에 삽입) | 없음 | 없음 |
| TOC `<!-- toc:* -->` 마커 | 유지 | 제거 (마커만; TOC 본문은 유지) | 제거 (전체) | 제거 (전체) |
| 이미지 경로 | 상대 / 호스팅 | commit-pinned 절대 URL | 상대 (`docs/` 기준) | 번들 내부 상대 |
| Mermaid | PNG | PNG | mermaid 또는 PNG | PNG |
| H3+ demote | 그대로 | demote | 그대로 | 그대로 |
| `finalize-posts.py` 적용 | 적용 | **스킵** (`to-medium.py` 단독 책임) | N/A | N/A |

---

## 7. Quality Gates (현재 단계, AGENTS.md와 동일)

```bash
# 1. visible Tags + TOC + ko refs heading 정합성 (idempotent)
python3 .sisyphus/medium/finalize-posts.py

# 2. ko 문체 검증 (translation smells + im-not-ai S1)
.sisyphus/style/check-ko.sh
```

medium 변형 재생성 시:

```bash
# 3. medium 디렉토리 재생성
python3 .sisyphus/medium/to-medium.py <series>/en

# 4. tags + TOC 재적용
python3 .sisyphus/medium/finalize-posts.py
```
