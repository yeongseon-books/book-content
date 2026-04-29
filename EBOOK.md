# eBook Publishing Guide

이 문서는 본 저장소(`tech-writing`)에서 eBook source bundle을 생성하고, private `mkdocs-ebook` 도구와 연동하는 방식을 정의한다.

---

## 1. 중요한 전제

`mkdocs-ebook` 은 private repository 이다.

```text
yeongseon/mkdocs-ebook  (private)
```

따라서:

- 본 저장소의 `requirements.txt` 에 `mkdocs-ebook` 을 **필수 의존성으로 넣지 않는다**.
- 본 저장소는 PDF/EPUB 를 직접 생성하지 않는다.
- 본 저장소는 private eBook compiler 가 사용할 source bundle 까지만 생성한다.
- private builder를 가진 환경에서만 `requirements-dev.txt` 를 통해 옵션 설치한다.

### 1.1 설치 방법 (둘 중 하나)

```bash
# A) SSH (권장 — 로컬 개발):
pip install git+ssh://git@github.com/yeongseon/mkdocs-ebook.git

# B) HTTPS + gh token (CI / SSH 키 미등록 환경):
pip install "git+https://x-access-token:$(gh auth token)@github.com/yeongseon/mkdocs-ebook.git"
```

`gh auth token` 은 `gh auth login` 으로 인증된 토큰을 반환한다 (`repo` scope 필요).
`mkdocs-ebook lint` 만 돌리는 데는 추가 시스템 의존성이 필요 없다. PDF/EPUB 빌드 시
pandoc, xelatex, Nanum 폰트, playwright, poppler-utils, epubcheck 가 추가로 필요하며
`mkdocs-ebook doctor` 로 확인할 수 있다.

---

## 2. 책임 분리

```text
tech-writing
  = canonical Markdown
  = blog export (Tistory/Medium)
  = MkDocs source
  = eBook source bundle export

mkdocs-ebook (private)
  = eBook compiler
  = PDF/EPUB generation
  = book-specific theming
```

본 저장소는 "책 한 권을 만드는 데 필요한 모든 입력"을 디렉토리로 묶어 내보내는 일까지만 책임진다.

---

## 3. eBook Workflow

```text
1. content/ 에 원본 글 작성 (한국어/영어)
2. <series>/series.yaml 로 챕터 순서 / 책 메타 관리
3. scripts/export_ebook_source.py 실행
4. exports/ebook-source/<series>-<lang>/ 디렉토리 생성
5. private mkdocs-ebook 에서 PDF/EPUB 빌드
```

---

## 4. 명령

```bash
python3 scripts/export_ebook_source.py <series-id> --lang <ko|en>
```

생성 결과 (`exports/ebook-source/<series-id>-<lang>/`):

```text
mkdocs.yml                                # site_name, theme=material, nav (Cover / Preface / 제 N 장)
docs/
├── index.md                              # 표지 다음 안내 페이지 (templates/ebook-index.md 렌더)
├── preface.md                            # 서문 (templates/ebook-preface.md 렌더)
├── 01-<slug>.md ... NN-<slug>.md         # 본문 챕터 (transform_for_ebook 적용)
└── assets/<series-id>/<NN>/...           # 본문이 참조하는 모든 이미지
```

`mkdocs build --strict` 가 번들 안에서 그대로 통과해야 한다. 19/19 시리즈가 현재 통과한다.

private builder 에서:

```bash
mkdocs-ebook build exports/ebook-source/<series-id>-<lang>
```

### 4.1 번들 contract

bundle 을 소비하는 빌더(예: private `mkdocs-ebook`) 가 의존하는 보증:

- `mkdocs.yml` 의 `docs_dir: docs`, `theme.name: material`, `theme.language: <lang>`.
- `docs/` 안의 모든 markdown 은 YAML front matter 가 제거된 순수 본문이다.
- `docs/index.md` 와 `docs/preface.md` 는 항상 존재하고 nav 에 등록되어 있다.
- 본문 챕터의 이미지 참조는 `assets/<series-id>/<NN>/...` (즉 `docs/assets/...` 기준) 로만 적힌다.
- 본문 안의 cross-series 링크는 `https://github.com/<owner>/<repo>/tree/<TAG>/content/<other-series>/<lang>/...` 형태의 절대 URL 로 재작성되어 번들 외부를 가리킨다 (책은 self-contained, 외부 참조는 자료 링크).
- preface 의 "원본 블로그 글" 링크 또한 절대 URL 이다.
- 시리즈 TOC, 하단 `Tags:` 라인, `blog-only` 블록은 모두 제거되어 있다. `ebook-only` 블록은 마커만 제거하고 본문은 유지한다.

---

## 5. eBook 변환 시 적용되는 변형 규칙

`exports/ebook-source/` 로 내보낼 때 다음을 적용한다.

### 제거 대상

- `<!-- blog-only:start --> ... <!-- blog-only:end -->` 블록
- 하단 `Tags: A, B, C, D` visible 라인
- `<!-- toc:begin --> ... <!-- toc:end -->` 시리즈 TOC 블록 전체 (책 자체 TOC가 대체)
- YAML front matter 블록 전체 (책에서는 본문만 필요; 메타는 빌더가 별도 관리)

### 유지 대상

- `<!-- ebook-only:start --> ... <!-- ebook-only:end -->` 블록 (마커는 제거하고 내용은 유지)
- Source Version / Call Path Summary 섹션 (Deep Dive)
- 코드 블록, 이미지, 표, 각주, H1 챕터 제목, 본문 모든 prose

### 재작성 대상

- 본문 내 cross-series 링크 (`../../<other-series>/<lang>/...`) 는
  `https://github.com/<repo>/tree/<TAG>/content/<other-series>/<lang>/...`
  절대 GitHub URL 로 재작성된다 (책은 self-contained, 외부 참조는 commit-pinned).
- 본문 내 이미지 참조 (`../../../assets/...`) 는 `assets/<series>/<NN>/...` 로 재작성되어
  `docs/assets/...` 에 복사된 사본을 가리킨다.

### 추가 대상

- **Preface** (`templates/ebook-preface.md` 기반): 이 책을 읽는 방법, 시리즈 전체 구조, 책 자체 목차, 원본 블로그 글 canonical URL 목록.
- **Index page** (`templates/ebook-index.md`): 책 표지 다음의 안내 페이지 (제목, 부제, 저자, 한눈에 보는 목차).

---

## 6. eBook 후보 우선순위

첫 eBook은 다음 순서로 진행한다.

1. Azure Functions 101
2. Azure App Service 101
3. AI Web Dev 101 (en 번역 완료 후)
4. LLM from Scratch 101
5. Azure Functions Deep Dive
6. Azure App Service Deep Dive
7. Azure PaaS Troubleshooting Handbook (cross-series compilation)

---

## 7. eBook 구조 권장

각 eBook 권장 구조:

```text
Cover (private builder가 처리)
Preface
Table of Contents (자동)
Chapter 1
Chapter 2
...
Appendix (선택)
References
```

---

## 8. Front matter / 카탈로그 필드 (eBook 빌드가 실제로 읽는 것)

**현재 ebook 빌드가 실제로 사용하는 필드만 명시한다.** 미래에 추가될 ebook-specific 메타필드는 본 절에 추가될 때 비로소 contract 의 일부가 된다.

### 시리즈 (`series.yaml` 루트)

```yaml
meta:
  repo: <owner>/<repo>      # 절대 URL 빌드용
  tag: <commit-sha>         # commit-pinned 절대 URL 빌드용

series:
  - id: <series-id>
    title:
      ko: ...               # ebook 표지 제목 (lang 별)
      en: ...
    description:
      ko: ...               # ebook 부제
      en: ...
    languages: [ko, en]     # ebook 빌드 가능한 언어 집합
    targets:
      ebook: true           # false 면 export_ebook_source.py 가 거부
    path: content/<series>/ # canonical URL 빌드용
```

### 시리즈 (`content/<series>/series.yaml` 카탈로그)

```yaml
articles:
  - idx: 1
    slug: 01-what-is-azure-functions   # docs/<NN>-<slug-tail>.md 생성에 사용
```

### Article front matter

```yaml
title: ...                  # H1 과 동일해야 한다 (build_series_index 가 이 필드를 읽음)
```

article 의 front matter 블록 자체는 ebook 본문에서 제거된다.

---

## 9. 이행 단계

eBook 파이프라인은 다음 순서로 활성화된다.

| Step | 상태 | 비고 |
| --- | --- | --- |
| `EBOOK.md` 정책 문서 | 완료 | 본 문서 |
| `templates/ebook-preface.md`, `ebook-index.md` | 완료 | 렌더 시점에 `# Template:` 헤더 자동 제거 |
| `scripts/export_ebook_source.py` 실 동작 | 완료 (Phase 7g + 8) | 19/19 시리즈 번들이 `mkdocs build --strict` 통과 |
| 모든 ebook-target 시리즈에 front matter 도입 | 완료 (Phase 7b) | 129/129 article |
| Azure Functions 101 첫 빌드 | 완료 | `exports/ebook-source/azure-functions-101-{ko,en}/` |
| private mkdocs-ebook 통합 테스트 | 보류 | private repo 접근 환경에서 |
