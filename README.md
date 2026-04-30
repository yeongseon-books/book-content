# Tech Writing

Tistory, Medium, MkDocs, eBook 발행을 위한 기술 콘텐츠 원본 저장소. 한 번 작성한 글을 여러 채널로 변환하기 위한 멀티채널 퍼블리싱 파이프라인입니다.

> 모든 시리즈가 `content/<series>/` 아래로 이동 완료되었습니다 (Phase 6 완료).

## Publishing Targets

| Target | 용도 | 언어 |
| --- | --- | --- |
| Tistory | 한국어 블로그 | ko |
| Medium | 영어 블로그 | en |
| MkDocs | 웹북 / 문서 사이트 | ko + en |
| eBook source | private `mkdocs-ebook` 입력 번들 | ko + en |

## Key Documents

- [`SERIES.md`](./SERIES.md) — 전체 시리즈 카탈로그와 상태
- [`PUBLISHING.md`](./PUBLISHING.md) — Tistory/Medium/MkDocs/eBook 변환 규칙 및 산출물 형식
- [`STYLE_GUIDE.md`](./STYLE_GUIDE.md) — 문체, 구조, 이미지, 태그, 참고자료 규칙
- [`EBOOK.md`](./EBOOK.md) — eBook source bundle 정책 (private builder 연동)
- [`ROADMAP.md`](./ROADMAP.md) — 개편 로드맵과 진행 상황
- [`AGENTS.md`](./AGENTS.md) — 에이전트(인간/AI) 운영 규칙

## Quality Gates

```bash
python3 .sisyphus/medium/finalize-posts.py    # idempotent: tags + TOC + ko refs
.sisyphus/style/check-ko.sh                   # ko translation-smell + im-not-ai S1 check
```

medium 변형 재생성 시:

```bash
python3 .sisyphus/medium/to-medium.py content/<series>/en   # → medium/<NN>.html
python3 .sisyphus/medium/finalize-posts.py
```

## 폴더 구조

```text
tech-writing/
├── README.md
├── SERIES.md, PUBLISHING.md, STYLE_GUIDE.md, EBOOK.md, ROADMAP.md, AGENTS.md
├── mkdocs.yml, requirements.txt, requirements-dev.txt
├── series.yaml                          # 시리즈 카탈로그 단일 출처 (path: 필드로 위치 해석)
├── content/
│   └── <series>/
│       ├── ko/                          # 한국어 원본
│       ├── en/                          # 영어 번역
│       └── medium/                      # Medium 브라우저 붙여넣기용 .html (to-medium.py 생성)
├── docs/, exports/, templates/, scripts/
├── assets/<series>/<NN>/...             # 이미지 (본문에서 ../../../assets/ 로 참조)
└── .sisyphus/medium/                    # finalize-posts.py / to-medium.py / _catalog.py
```

## 발행처 매핑

| 언어 | 플랫폼 | 산출물 | 비고 |
|---|---|---|---|
| 한국어 | Tistory | .md | Mermaid는 PNG로 export |
| 영어 | Medium | **.html** | Chrome 붙여넣기; 이미지 base64 인라인 |
| ko + en | MkDocs | .md | `scripts/build_docs.py` 로 materialize |
| ko + en | eBook | 번들 | `scripts/export_ebook_source.py` 예정 |

자세한 변환 규칙은 [`PUBLISHING.md`](./PUBLISHING.md)를 참조하세요.
