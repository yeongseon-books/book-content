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
- `<!-- toc:begin --> ... <!-- toc:end -->` 시리즈 TOC 블록 (책 자체 TOC가 대체)
- 블로그용 문장 ("다음 글에서는...", "이번 글에서는...", "Tistory/Medium에 발행한 ...")
- 너무 강한 SEO형 제목 → 책 챕터 제목으로 정규화 (`series.yaml` `episodes[].title.ebook` 사용 가능)

### 유지 대상

- `<!-- ebook-only:start --> ... <!-- ebook-only:end -->` 블록 (마커는 제거하고 내용은 유지)
- Source Version / Call Path Summary 섹션 (Deep Dive)
- 코드 블록, 이미지, 표, 각주

### 추가 대상

- **Preface** (`templates/ebook-preface.md` 기반): 이 책을 읽는 방법, 시리즈 전체 구조, 챕터 간 연결.
- **Index page** (`templates/ebook-index.md`): 책 표지 다음의 안내 페이지.
- (선택) **Appendix / Glossary**.

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

## 8. Front matter 필드 (eBook 관련)

front matter 도입(Phase 7) 후 다음 필드가 eBook 빌드에 사용된다.

```yaml
targets:
  ebook: true
ebook:
  chapter_title: "Azure Functions란?"   # 책 본문에서 사용할 짧은 제목 (선택)
  include_in_toc: true
  preface_only: false                   # true면 본문에 포함하지 않고 preface 자료로만 사용
```

`series.yaml` 측:

```yaml
ebook:
  title:
    ko: "Azure Functions 101 — 입문에서 운영까지"
    en: "Azure Functions 101 — From First Deploy to Production"
  subtitle:
    ko: "이벤트 기반 실행 모델을 손에 익히는 7단계"
  cover_image: assets/azure-functions-101/cover.png
  preface: templates/ebook-preface.md
```

---

## 9. 이행 단계

eBook 파이프라인은 다음 순서로 활성화된다.

| Step | 상태 | 비고 |
| --- | --- | --- |
| `EBOOK.md` 정책 문서 | 완료 | 본 문서 |
| `templates/ebook-preface.md`, `ebook-index.md` skeleton | 완료 | 비어 있는 템플릿 |
| `scripts/export_ebook_source.py` skeleton | 완료 | 동작은 TODO |
| 실제 변환 로직 구현 | 보류 | front matter 도입 후 |
| Azure Functions 101 첫 빌드 | 보류 | 콘텐츠 이행 후 |
| private mkdocs-ebook 통합 테스트 | 보류 | private repo 접근 환경에서 |
