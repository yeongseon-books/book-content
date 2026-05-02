> **Archive** — 이 문서는 과거 `tech-blog → tech-writing → technical-content → book-content` 개편 과정을 기록한 migration archive입니다.
> 현재 저장소 구조와 운영 규칙은 [`README.md`](./README.md), [`ARCHITECTURE.md`](./ARCHITECTURE.md), [`PUBLISHING.md`](./PUBLISHING.md), [`EBOOK.md`](./EBOOK.md), [`AGENTS.md`](./AGENTS.md)를 기준으로 합니다.

# tech-blog → tech-writing → book-content 개편 계획

> 이 문서는 본 저장소(`yeongseon-books/book-content`, 구 `yeongseon-books/tech-blog`)를 다채널 기술 콘텐츠 파이프라인 저장소로 단계적으로 개편하기 위한 마스터 플랜이다.
> 실제 진행 상황은 [`ROADMAP.md`](./ROADMAP.md)에서 추적한다. **Phase 9 리포지토리 rename 은 세 차례 완료되었다 (`tech-blog → tech-writing`: `cb179c5`, `tech-writing → technical-content`, `technical-content → book-content`).**

## 1. 개편 목적

`yeongseon-books/book-content`(구 `yeongseon-books/tech-blog`)은 기술 블로그 원고를 저장하는 저장소로 시작했지만, 단순 블로그 저장소를 넘어 다음 목적을 모두 지원한다.

- Tistory 한국어 글 발행
- Medium 영어 글 발행
- MkDocs 기반 웹북 제공
- private `mkdocs-ebook` 도구를 통한 eBook 생성
- Azure, AI, AX, 개발 생산성, 오픈소스, 기술 글쓰기 등 다양한 기술 주제 관리
- 시리즈형 콘텐츠를 장기적으로 재사용 가능한 지식 자산으로 관리

따라서 이 저장소는 앞으로 다음 역할을 가진다.

```text
기존:
tech-blog = 블로그 원고 저장소

변경:
book-content = 기술 콘텐츠 원본 저장소 + 멀티채널 퍼블리싱 파이프라인
```

## 2. 리포지토리 이름 변경

| 시점 | 이전 이름 | 새 이름 | 커밋 |
| --- | --- | --- | --- |
| Phase 9 (1차) | `yeongseon-books/tech-blog` | `yeongseon-books/tech-writing` | `cb179c5` |
| Phase 9 (2차) | `yeongseon-books/tech-writing` | `yeongseon-books/technical-content` | 별도 커밋 |
| Phase 9 (3차) | `yeongseon-books/technical-content` | `yeongseon-books/book-content` | 별도 커밋 |

`tech-blog`는 블로그 전용 저장소처럼 보인다. `tech-writing`은 글쓰기 행위에, `technical-content`는 기술 콘텐츠에 초점이 맞춰져 있다. 이 저장소는 기술서, 웹북, 블로그 시리즈 원고를 관리하는 영선북스의 콘텐츠 자산 저장소이므로 `book-content`로 최종 rename하였다.

## 3. 저장소 정체성

### README 한 줄 요약

> 영선북스의 기술서, 웹북, 블로그 시리즈 원고를 관리하는 canonical content repository.

### English description

> Canonical content repository for tech books, web books, and blog series by Yeongseon Books.

## 4. 핵심 설계 원칙 (목표 상태 — Phase 6 이후)

> 본 절은 Phase 6 시리즈 이동이 끝난 뒤의 목표 상태를 기술한다. Phase 6 이전에는 시리즈가 여전히 루트(`<series>/`)에 있고, [`AGENTS.md`](./AGENTS.md) 의 기존 규칙이 그대로 적용된다.

### 4.1 원본은 하나여야 한다

각 플랫폼별로 글을 따로 작성하지 않는다.

```text
Canonical Markdown
        ↓
 ┌──────────────┬──────────────┬───────────────┬─────────────────┐
 │ Tistory      │ Medium       │ MkDocs Site   │ eBook Source    │
 │ Korean Blog  │ English Blog │ Web Book      │ PDF/EPUB Input  │
 └──────────────┴──────────────┴───────────────┴─────────────────┘
```

### 4.2 `content/` 가 원본이다

```text
content/  = canonical source = 사람이 직접 작성하는 원본
```

### 4.3 `docs/` 는 MkDocs 산출물이다

```text
docs/     = MkDocs site source = content/에서 생성/복사된 결과
```

### 4.4 `exports/` 는 외부 발행용 산출물이다

```text
exports/tistory/      = Tistory 붙여넣기 한국어 글
exports/medium/       = Medium 붙여넣기 영어 글
exports/ebook-source/ = private mkdocs-ebook 입력용 eBook source bundle
```

### 4.5 `mkdocs-ebook` 은 직접 의존하지 않는다

`mkdocs-ebook`은 private repository이므로 `requirements.txt`에 필수 의존성으로 넣지 않는다. 본 저장소는 eBook 빌드 자체를 수행하지 않고, eBook 빌드에 필요한 source bundle까지만 생성한다.

```text
book-content  = 콘텐츠 원본 + eBook source export
mkdocs-ebook  = private eBook compiler (PDF/EPUB)
```

## 5. 최종 디렉토리 구조 (목표 상태)

```text
book-content/
├── README.md
├── SERIES.md
├── PUBLISHING.md
├── STYLE_GUIDE.md
├── EBOOK.md
├── ROADMAP.md
├── MIGRATION_PLAN.md
├── mkdocs.yml
├── requirements.txt
├── requirements-dev.txt
├── series.yaml
│
├── content/
│   ├── azure-app-service-101/{series.yaml, ko/, en/}
│   ├── azure-app-service-deep-dive/{series.yaml, ko/, en/}
│   ├── azure-functions-101/{series.yaml, ko/, en/}
│   ├── azure-functions-deep-dive/{series.yaml, ko/, en/}
│   ├── azure-aca-101/{series.yaml, ko/, en/}
│   ├── azure-aca-deep-dive/{series.yaml, ko/, en/}
│   ├── azure-aks-101/{series.yaml, ko/, en/}
│   ├── azure-aks-deep-dive/{series.yaml, ko/, en/}
│   ├── ai-web-dev-101/{series.yaml, ko/, en/}
│   ├── llm-from-scratch-101/{series.yaml, ko/, en/}
│   ├── ax/{series.yaml, ko/, en/}
│   └── technical-writing/{series.yaml, ko/, en/}
│
├── docs/
│   ├── index.md
│   ├── ko/{index.md, <series>/...}
│   └── en/{index.md, <series>/...}
│
├── assets/
│   ├── <series>/...
│   └── shared/
│
├── exports/
│   ├── tistory/
│   ├── medium/
│   └── ebook-source/
│
├── templates/
│   ├── article.ko.md
│   ├── article.en.md
│   ├── series-index.md
│   ├── ebook-preface.md
│   └── ebook-index.md
│
└── scripts/
    ├── build_docs.py
    ├── export_tistory.py
    ├── export_medium.py
    ├── export_ebook_source.py
    ├── check_links.py
    ├── check_frontmatter.py
    └── build_series_index.py
```

## 6. 현재 저장소와의 차이 (Δ)

| 항목 | 현재 | 목표 |
| --- | --- | --- |
| 시리즈 위치 | 루트 직속 (`azure-functions-101/`) | `content/<series>/` |
| 단일 언어 시리즈 | `ai-web-dev-101/*.md` (flat) | `content/ai-web-dev-101/{ko,en}/*.md` |
| 시리즈 메타데이터 | 없음 (`finalize-posts.py` 코드 내 매핑) | `content/<series>/series.yaml` |
| Front matter | 없음 (visible Tags line만 사용) | YAML front matter + 하단 Tags 병행 (호환 유지) |
| MkDocs | 없음 | `mkdocs.yml` + `docs/` |
| eBook | 없음 | `exports/ebook-source/` (private builder 입력) |
| Tistory/Medium export | `medium/` 디렉토리만 (수동 복사) | `exports/{tistory,medium}/` (스크립트 자동화) |

## 7. 호환성 정책 (중요)

### 7.1 하단 `Tags:` 라인은 유지한다

원안에서는 "front matter만 사용하고 visible Tags line은 제거"였다. 그러나 다음 이유로 본 저장소에서는 **둘 다 유지**한다.

- 현행 `AGENTS.md`가 visible Tags line을 강제한다
- `.sisyphus/medium/finalize-posts.py`가 visible Tags line을 자동 삽입/검증한다
- visible Tags line은 Tistory/Medium 발행 시 **태그 입력 칸에 그대로 복사하기 위한 단일 출처**다
- 제거 시 현재 발행 워크플로우 전체가 깨진다

따라서 정책은 다음과 같다.

- visible 하단 `Tags: A, B, C, D` 라인 → **유지** (단일 출처는 `finalize-posts.py`의 `SERIES_TAGS`)
- YAML front matter `tags:` 필드 → 신규 도입(자동 생성, visible 라인과 동기화)
- 충돌 시 우선순위: `finalize-posts.py` `SERIES_TAGS` > front matter > visible 라인

### 7.2 파일 이동은 시리즈 단위 원자적 커밋

`<series>/` → `content/<series>/` 이동 시:

- 한 시리즈를 한 커밋으로 이동
- 같은 커밋 내에서 모든 상대 경로(이미지, 시리즈 TOC, references) 갱신
- 이동 후 즉시 `python3 .sisyphus/medium/finalize-posts.py` 재실행하여 idempotency 확인
- 이동 후 즉시 `.sisyphus/style/check-ko.sh` 실행하여 ko 품질 회귀 없음 확인

### 7.3 `assets/` 위치는 보존

이미지는 현재 위치(`assets/<series>/<NN>/...`)를 그대로 유지한다. 이동하면 ko/en/medium 모든 파일의 이미지 경로를 동시에 갱신해야 하므로 위험이 크다.

상대 경로는 `<series>/ko/01.md` → `content/<series>/ko/01.md`로 옮길 때 `./assets/...` → `../../../assets/...` 로 변경된다. 이 변환은 시리즈 이동 스크립트가 수행한다.

### 7.4 medium URL pin 정책 유지

`.sisyphus/medium/to-medium.py`의 `TAG`는 계속 commit hash로 pin한다. 시리즈 이동 후 medium 재생성 시 `TAG`를 먼저 갱신하고 재빌드한 뒤 커밋한다.

## 8. 단계별 실행 순서

자세한 체크리스트는 [`ROADMAP.md`](./ROADMAP.md)를 참조.

| Phase | 내용 | 위험도 | 자동화 가능 |
| --- | --- | --- | --- |
| 1 | 문서 분리 (SERIES/PUBLISHING/STYLE_GUIDE/EBOOK/ROADMAP) + README 재작성 | 낮음 | 완료 |
| 2 | 디렉토리 스캐폴딩 (content/ docs/ exports/ templates/ scripts/) | 낮음 | 완료 |
| 3 | 메타데이터 (root `series.yaml`) | 낮음 | 완료 (per-series `series.yaml` 는 Phase 6 에서 시리즈별로 함께 추가됨) |
| 4 | MkDocs 셋업 (mkdocs.yml + requirements.txt + build_docs.py) | 낮음 | 완료 (Phase 7d: mkdocs build --strict 통과, 129 파일) |
| 5 | 스크립트 실 동작 (export_tistory/medium/ebook_source, check_*, build_series_index, _transform) | 중간 | 완료 (Phase 7c-h: 7개 스크립트 + 공유 transform 모듈) |
| 6 | 시리즈 파일 이동 (`<series>/` → `content/<series>/`) + per-series `series.yaml` 동시 추가 | **높음** | 완료 (10/10 시리즈, 시리즈별 원자 커밋) |
| 7 | 콘텐츠 품질 (front matter 도입, 스크립트 실 동작, mkdocs build 검증) | 중간 | 완료 (129/129 front matter, 7개 스크립트 실 동작, mkdocs build --strict 통과) |
| 8 | eBook source bundle 통합 (`export_ebook_source.py` 실 동작 + private `mkdocs-ebook` 빌드) | 중간 | 완료 (19/19 번들 strict-pass; 빌더 contract 는 EBOOK.md §4.1) |
| 9 | 리포지토리 rename (`tech-blog` → `tech-writing` → `technical-content` → `book-content`) + medium URL 일괄 재생성 | 낮음 | 수동 (아래 9.1) |

### 9.1 Phase 9 수동 절차 (rename 후 실행)

1. `gh repo rename tech-writing` (또는 GitHub UI).
2. 로컬: `git remote set-url origin git@github.com:yeongseon-books/tech-writing.git`.
3. `series.yaml` `meta.repo` 를 `yeongseon-books/tech-writing` 으로 변경하고 (선택) `meta.tag` 도 새 commit SHA 로 갱신.
4. Medium 변형 재생성 (URL 이 변경되므로 두 단계 모두 필요):
   - `python3 .sisyphus/medium/to-medium.py` — `content/<series>/medium/*.md` 의 raw 이미지 URL 갱신
   - `python3 scripts/export_medium.py <series> --all` — 발행용 사본 (`exports/medium/`) 갱신; 발행 직전이라면 이 단계 생략 가능 (`exports/` 는 disposable)
5. ebook 번들 재생성: `python3 scripts/export_ebook_source.py <each ebook series> --lang <ko|en>` — 새 URL 로 ebook 번들을 다시 만들고 `mkdocs build --strict` 로 모두 통과 확인.
6. 이미 발행된 Tistory/Medium 게시물은 본문 URL 이 자동 변경되지 않으므로 (Medium 은 raw URL 이 본문에 박힘) 새 URL 로 본문 갱신이 필요한 글만 수동으로 다시 import 한다.

## 9. 산출물 목록

이 마이그레이션 1차 사이클이 끝났을 때 추가되는 파일:

- `MIGRATION_PLAN.md` (본 문서)
- `SERIES.md`, `PUBLISHING.md`, `STYLE_GUIDE.md`, `EBOOK.md`, `ROADMAP.md`
- `mkdocs.yml`, `requirements.txt`, `requirements-dev.txt`, `series.yaml` (루트 카탈로그)
- `content/`, `docs/`, `exports/`, `templates/`, `scripts/` 디렉토리 스캐폴딩
- `scripts/{build_docs,export_tistory,export_medium,export_ebook_source,check_links,check_frontmatter,build_series_index}.py` + `_transform.py` (실 동작)

각 시리즈별 `series.yaml` 은 본 사이클이 아닌 Phase 6 시리즈 이동 커밋 안에서 함께 추가된다 (이동과 메타가 같은 원자 커밋이어야 경로 정합성이 유지됨).

## 10. 명시적으로 보류되는 작업

다음은 **이번 사이클에서 수행하지 않는다**. 후속 세션에서 시리즈 단위로 진행한다.

- ~~156+ Markdown 파일을 `content/`로 실제 이동~~ (완료)
- ~~모든 파일에 YAML front matter 삽입~~ (완료)
- ~~이미지 경로 일괄 재작성~~ (완료)
- AI Web Dev 101 OpenAI API 예제 갱신
- Deep Dive 글에 Source Version / Call Path Summary 추가
- ~~GitHub repository rename~~ (완료)
- ~~private `mkdocs-ebook` 통합 테스트~~ (완료)
각 항목은 [`ROADMAP.md`](./ROADMAP.md)의 Phase 6/7/8에 추적된다.

## 11. 검증 기준

이 사이클의 성공 기준:

- [ ] 새 문서 6개(MIGRATION/SERIES/PUBLISHING/STYLE_GUIDE/EBOOK/ROADMAP) 생성
- [ ] README가 새 정체성을 반영
- [ ] `mkdocs.yml`, `requirements.txt`, `series.yaml` 생성 (실제 content 이동 없이도 자체 정합성)
- [ ] `python3 .sisyphus/medium/finalize-posts.py` 여전히 통과 (idempotent)
- [ ] `.sisyphus/style/check-ko.sh` 여전히 통과
- [ ] 기존 시리즈(`azure-*`, `ai-web-dev-101`, `llm-from-scratch-101`) 발행 워크플로우 무영향
