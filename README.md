# Book Content

블로그 글을 먼저 쓰고, 쌓인 시리즈를 eBook으로 묶는 blog-first / book-later 저장소입니다. 하나의 원본 콘텐츠를 여러 발행 채널로 변환합니다.

> 모든 시리즈가 `content/<series>/` 아래로 이동 완료되었습니다 (Phase 6 완료).

## Publication Pipelines

| Pipeline | Platform | URL | Source | Output | Purpose |
| --- | --- | --- | --- | --- | --- |
| Korean Blog | Tistory | `https://yeongseonchoe.tistory.com/` | `content/<series>/ko/*.md` | `exports/tistory/<series>/*.md` | 한국어 검색 유입용 블로그 |
| English Blog | Hashnode | `https://hashnode.com/@yeongseon` | `content/<series>/en/*.md` | (Hashnode 직접 Markdown 발행) | 한국어 원문의 충실한 영어 대응본 |
| Medium | Medium | `https://medium.com/@yeongseonchoe` | `content/<series>/en/*.md` (adaptation) | `content/<series>/medium/*.html` → `exports/medium/<series>/*.html` | 영어권 독자용 발행 변형 |
| Web Book | MkDocs | GitHub Pages 또는 내부 preview | `content/<series>/{ko,en}/*.md` | `docs/` | 웹북 형태의 학습 콘텐츠 |
| eBook | private `mkdocs-ebook` | — | `content/<series>/{ko,en}/*.md` | `exports/ebook-source/<series>-<lang>/` | 시리즈를 책처럼 묶은 학습형 원고 |

`ko/`와 `en/`이 canonical source다. `medium/`은 `to-medium.py`가 생성하는 발행 변형 산출물이며 canonical source가 아니다.

> eBook PDF/EPUB 생성은 항상 최신 private `mkdocs-ebook` builder 기준으로 수행한다. `book-content`는 source bundle까지만 생성하며, 실제 빌드 환경에서 `mkdocs-ebook`을 최신으로 설치/갱신(`--upgrade --force-reinstall`)한 뒤 `mkdocs-ebook build`를 실행한다. 자세한 정책은 `EBOOK.md §1.3` 참조.

## Key Documents

- [`SERIES.md`](./SERIES.md) — 전체 시리즈 카탈로그와 상태
- [`BLOG_WRITING_GUIDE.md`](./BLOG_WRITING_GUIDE.md) — Tistory/Hashnode/Medium 블로그 글 작성 규칙 (SEO 제목, 글 구조, 발행 체크리스트)
- [`EBOOK_WRITING_GUIDE.md`](./EBOOK_WRITING_GUIDE.md) — 시리즈를 eBook으로 묶을 때의 원고 구성 규칙 (장 구조, Part 구성)
- [`STYLE_GUIDE.md`](./STYLE_GUIDE.md) — 문체, 구조, 이미지, 태그, 참고자료 공통 규칙
- [`PUBLISHING.md`](./PUBLISHING.md) — 원본 Markdown → 각 파이프라인 산출물 변환 기술 규칙
- [`EBOOK.md`](./EBOOK.md) — eBook export·build 정책 및 private builder 연동
- [`ARCHITECTURE.md`](./ARCHITECTURE.md) — 저장소 구조와 빌드 흐름
- [`ROADMAP.md`](./ROADMAP.md) — 개편 로드맵과 진행 상황
- [`CONTENT_MODEL.md`](./CONTENT_MODEL.md) — 시리즈 카탈로그, front matter, status 체계
- [`AGENTS.md`](./AGENTS.md) — 에이전트(인간/AI) 운영 규칙
- [`ASSET_POLICY.md`](./ASSET_POLICY.md) — 공개 이미지 자산 정책 및 dual-repo 구조

## Quality Gates

```bash
# 전체 파이프라인 한 번에
make check

# 개별 실행
python3 .sisyphus/medium/finalize-posts.py    # idempotent: tags + TOC + ko refs
.sisyphus/style/check-ko.sh                   # ko translation-smell + im-not-ai S1 check
python3 scripts/check_frontmatter.py
python3 scripts/check_links.py
python3 scripts/lint_captions.py
python3 scripts/check_article_structure.py     # article structure (A-grade) check
```

medium 변형 재생성 시:

```bash
python3 .sisyphus/medium/to-medium.py content/<series>/en   # → medium/<NN>.html
python3 .sisyphus/medium/finalize-posts.py
```

## 폴더 구조

```text
book-content/                               # private — canonical source
├── README.md
├── SERIES.md, PUBLISHING.md, STYLE_GUIDE.md, EBOOK.md, ROADMAP.md, AGENTS.md, ARCHITECTURE.md, CONTENT_MODEL.md
├── ASSET_POLICY.md                         # 공개 이미지 자산 정책
├── mkdocs.yml, requirements.txt, requirements-dev.txt
├── series.yaml                             # 시리즈 카탈로그 단일 출처 (path: 필드로 위치 해석)
├── content/
│   └── <series>/
│       ├── ko/                             # 한국어 원본
│       ├── en/                             # 영어 번역
│       └── medium/                         # Medium 브라우저 붙여넣기용 .html (to-medium.py 생성)
├── docs/                                   # MkDocs 웹북 산출물
├── exports/
│   ├── tistory/                            # Tistory 붙여넣기용 Markdown
│   ├── medium/                             # Medium 발행용 HTML 사본
│   └── ebook-source/                       # private mkdocs-ebook 입력용 source bundle
├── templates/, scripts/
├── assets/<series>/<NN>/...                # 이미지 (본문에서 ../../../assets/ 로 참조)
└── .sisyphus/medium/                       # finalize-posts.py / to-medium.py / _catalog.py

book-public-assets/                         # public — GitHub Pages 호스팅
├── assets/<series>/<NN>/...                # book-content/assets/ 의 미러
└── index.html                              # GitHub Pages placeholder

자세한 변환 규칙은 [`PUBLISHING.md`](./PUBLISHING.md)를 참조하세요.
