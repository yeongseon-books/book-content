# Roadmap

본 저장소(`tech-blog` → `tech-writing`)의 개편 진행 상황을 추적한다. 자세한 배경은 [`MIGRATION_PLAN.md`](./MIGRATION_PLAN.md) 참조.

체크박스 의미: `[x]` 완료, `[ ]` 미완료, `[~]` 진행 중, `[!]` 차단됨.

---

## Phase 1 — Repository Identity

- [x] `MIGRATION_PLAN.md` 추가
- [x] `SERIES.md` 추가
- [x] `PUBLISHING.md` 추가
- [x] `STYLE_GUIDE.md` 추가
- [x] `EBOOK.md` 추가
- [x] `ROADMAP.md` 추가
- [x] `README.md` 재작성 (publishing-targets 프레임 + 기존 시리즈 표 유지)

리포지토리 rename 은 Phase 9 에서 진행한다.

## Phase 2 — Directory Restructure (scaffolding)

- [x] `content/` 생성 (`.gitkeep` 만)
- [x] `docs/` 생성 (`.gitkeep` 만)
- [x] `exports/{tistory,medium,ebook-source}/` 생성
- [x] `templates/` 생성 + 빈 템플릿 5개
- [x] `scripts/` 생성 + skeleton 스크립트
- [x] 기존 시리즈 폴더를 `content/` 로 실제 이동 (Phase 6에서 시리즈별)

## Phase 3 — Metadata

- [x] 루트 `series.yaml` 추가 (시리즈 카탈로그 단일 출처)
- [x] 시리즈별 `series.yaml` 추가 — Phase 6 시리즈 이동 커밋 안에서 동시 추가 (이동과 메타가 같은 원자 커밋이어야 경로 정합성 유지)
- [x] 모든 글에 YAML front matter 추가 (Phase 7b: 129/129)
- [ ] `finalize-posts.py` 의 `SERIES_TAGS` 와 `series.yaml` 동기화 검증 추가

## Phase 4 — MkDocs

- [x] `mkdocs.yml` 추가 (현재는 placeholder nav — Phase 6 전까지 빌드되지 않음)
- [x] `requirements.txt` 추가 (mkdocs + material + pymdown + pyyaml + frontmatter)
- [x] `requirements-dev.txt` 추가 (mkdocs-ebook 옵션 설치 주석)
- [x] `scripts/build_docs.py` (content -> docs materialization)
- [x] `docs/` 자동 생성 동작 (Phase 7d: 129 파일)
- [x] `mkdocs build --strict` ko/en 정상 빌드 (Phase 7d)

## Phase 5 — Exporters

- [x] `scripts/export_tistory.py` (Phase 7g)
- [x] `scripts/export_medium.py` (Phase 7g)
- [x] `scripts/export_ebook_source.py` (Phase 7g + 8: 19/19 strict-pass)
- [x] `scripts/check_links.py` (Phase 7e: 0 failures)
- [x] `scripts/check_frontmatter.py` (Phase 7a: H1==title 검증 포함)
- [x] `scripts/build_series_index.py` (Phase 7c: mkdocs.yml `nav` 단일 소유자)
- [x] `scripts/_transform.py` 공유 변환 매트릭스 (Phase 7h)
- [ ] `.sisyphus/medium/{to-medium.py, finalize-posts.py, mermaid-to-png.py}` 와 통합/병행 정책 결정 (현 상태: 병행)

## Phase 6 — Series file moves (시리즈별, 원자 커밋)

각 시리즈를 `<series>/` → `content/<series>/` 로 이동하고, **같은 커밋에서** (1) 모든 상대 경로(이미지, TOC 링크, references) 갱신 (2) `content/<series>/series.yaml` 추가를 함께 수행한다.

**Scope rule (catalog whitelist):** 이동 대상은 `series.yaml` 에 등재된 `path:` 값만이다. 루트의 다른 디렉토리는 절대 건드리지 않는다. 특히 다음을 명시적으로 제외한다.

- `azure-functions-host/` — Azure/azure-functions-host 의 vendored upstream source (Deep Dive 시리즈 인용용). 시리즈 아님.
- `assets/` — 위치 보존 (모든 ko/en/medium 파일 경로 동시 갱신 위험 회피)
- `.sisyphus/`, `docs/`, `exports/`, `templates/`, `scripts/`, `content/` — 인프라 디렉토리
- 루트 문서 (`README.md`, `MIGRATION_PLAN.md`, `ROADMAP.md`, `SERIES.md`, `PUBLISHING.md`, `STYLE_GUIDE.md`, `EBOOK.md`, `AGENTS.md`)
- 설정 (`mkdocs.yml`, `series.yaml`, `requirements*.txt`)

이동 대상 (catalog 등재):

- [x] `azure-app-service-101`
- [x] `azure-app-service-deep-dive`
- [x] `azure-functions-101`
- [x] `azure-functions-deep-dive`
- [x] `azure-aks-101`
- [x] `azure-aks-deep-dive`
- [x] `azure-aca-101`
- [x] `azure-aca-deep-dive`
- [x] `ai-web-dev-101` (현재 flat → `content/ai-web-dev-101/{ko,en}/` 로 정규화)
- [x] `llm-from-scratch-101`

이동 후 시리즈별 검증:

```bash
python3 .sisyphus/medium/finalize-posts.py
.sisyphus/style/check-ko.sh
```

## Phase 7 — Content Quality

- [x] Oracle content review Waves 1-6 완료 (활성 9개 시리즈 전체)
- [x] P0 이슈 해결 완료 (`fix(...): P0 ...`, `fix(...): ebook prep ...`, Wave 1-4 반영)
- [x] P1 이슈 해결 완료 (Wave 5 + Wave 6 커밋 반영)
- [x] P2 후속 정리는 대부분 Wave 6 에서 반영 완료
- [x] 모든 글에 `last_reviewed` 갱신 (Phase 7b: 2026-04-29)
- [x] 리뷰 증적은 로컬 `.sisyphus/reviews/` 에 보존 (의도적으로 untracked, 비커밋)

시리즈별 완료 현황:

- [x] `azure-app-service-101`
- [x] `azure-app-service-deep-dive`
- [x] `azure-functions-101`
- [x] `azure-functions-deep-dive`
- [x] `azure-aks-101`
- [x] `azure-aks-deep-dive`
- [x] `azure-aca-101`
- [x] `azure-aca-deep-dive`
- [x] `ai-web-dev-101`
- [x] `llm-from-scratch-101`

## Phase 8 — eBook integration

- [x] `templates/ebook-preface.md`, `ebook-index.md` 채우기 (Phase 8: 렌더 시 `# Template:` 헤더 자동 제거)
- [x] `export_ebook_source.py` 실 동작 구현 (Phase 7g + 8: catalog validator + rmtree guard + cross-series rewrite)
- [x] Azure Functions 101 ko/en eBook source bundle 첫 빌드 (Phase 8: strict-pass)
- [x] 19/19 ebook-target 시리즈 번들 strict-pass (Phase 8)
- [x] private `mkdocs-ebook` 통합 테스트 — `pip install "git+https://x-access-token:$(gh auth token)@github.com/yeongseon/mkdocs-ebook.git"` 로 설치 후 19/19 번들 `mkdocs-ebook lint` 통과 (0 error / 0 warning each)
- [x] 첫 PDF 산출물 — 시스템 toolchain (pandoc + texlive-xetex + texlive-lang-korean + Nanum + NotoEmoji 등) 설치 후 5개 시리즈 cross-section 빌드 성공: `azure-functions-101` (en+ko PDF + en EPUB, 126/124 pages), `azure-app-service-101-ko` (1.9MB), `azure-aks-101-ko` (0.78MB), `azure-aca-101-ko` (0.44MB), `llm-from-scratch-101-ko` (PDF + EPUB). 시스템 의존성 설치 절차는 EBOOK.md §1.2; 전체 19개 빌드는 `scripts/build_ebook_artifacts.py` 로 일괄 가능.

## Phase 9 — Repository rename & cutover

- [x] `gh repo rename tech-writing` (`cb179c5`)
- [x] `series.yaml` `meta.repo` 를 `yeongseon-books/tech-writing` 으로 갱신; `meta.published_ref` 를 `cb179c5` 로 bump
- [x] `python3 .sisyphus/medium/to-medium.py` — medium 변형 raw URL 일괄 재생성 (61 파일, `tech-writing/cb179c5` 핀)
- [x] `python3 scripts/export_ebook_source.py <series> --lang <lang>` — 19개 ebook 번들 재생성 + mkdocs strict 통과
- [x] MIGRATION_PLAN 업데이트 (rename 완료 표기)
- [ ] 이미 발행된 Medium 글의 raw URL 은 GitHub redirect 에 의존 — 장기 신뢰 보증 아님, 가능하면 본문 다시 import (사용자 작업)
- [ ] `python3 scripts/export_medium.py <series> --all` — `exports/medium/` 발행 사본 재생성 (선택; disposable)
- [ ] 새 이름으로 첫 announcement post (선택)

---

## 차단 / 위험 (Risks)

- **R1**: 시리즈 이동 시 medium 변형의 commit-pinned URL 이 일시적으로 깨질 수 있음 → 이동 커밋 직후 `to-medium.py TAG` 를 새 commit으로 갱신하고 medium 재생성 동일 커밋에 포함.
- **R2**: front matter 도입 시 `finalize-posts.py` 의 visible Tags 라인 처리 로직과 충돌 가능 → finalizer 가 front matter `tags:` 를 우선 읽고 visible 라인을 동기화하도록 확장 필요 (Phase 3 후속 작업).
- **R3**: `mkdocs-ebook` 이 private 이라 CI 에서 eBook 빌드 검증 불가 → 본 저장소는 source bundle 검증(`python3 -c "import yaml; yaml.safe_load(open('.../mkdocs.yml'))"`)까지만 수행.
- **R4**: 한 번에 156+ 파일 이동 시 충돌/리뷰 부담 → 시리즈별 원자 커밋 강제 (Phase 6).

## Phase 10 — AI/LLM Content Strategy

리뷰 기반 AI/LLM 시리즈 출판 전략.

### 시리즈 트랙 분류

**Track A — Traffic / Search** (검색 유입 우선)
1. `llm-app-foundations-101` — AI/LLM 입구 시리즈
2. `llm-api-production-101` — Structured Output / Tool Calling / Streaming
3. `vector-search-101` — Embedding / FAISS / Chunking
4. `rag-benchmark-101` — RAGAS / Evaluation
5. `korean-ai-stack-101` — 한국어 특화

**Track B — eBook / Learning Path** (책으로 묶기 좋은 학습 경로)
1. `llm-app-foundations-101`
2. `llm-api-production-101`
3. `vector-search-101`
4. `document-ingestion-101`
5. `ai-app-patterns-101`

**Track C — Authority / Deep Tech** (전문성/브랜딩)
1. `rag-deep-dive` (301)
2. `langchain-101`
3. `langgraph-101`
4. `llm-from-scratch-101`
5. `llm-finetuning-101`

### ai-web-dev-101 처리

- [ ] `status: needs-update` 유지 — 신규 글 추가 금지
- [ ] 기존 7편 내용을 새 시리즈로 흡수:
  - 1~2화 → `llm-app-foundations-101`
  - 3화(챗봇) → `ai-app-patterns-101`
  - 4화(RAG) → `vector-search-101` / `document-ingestion-101` 이후 시리즈 연계
  - 5화(Agent) → `ai-app-patterns-101` / `langgraph-101`
  - 6화(배포) → `llm-apps-ops-101`
  - 7화(평가) → `rag-benchmark-101` / `llm-apps-ops-101`

### 출판 우선순위 (추천 순서)

1. `llm-app-foundations-101` — AI/LLM 전체 입구
2. `llm-api-production-101` — 트래픽 + 전문성 모두 잡음
3. `vector-search-101` — RAG 기반 기초
4. `document-ingestion-101` — RAG 기반 기초 (연계)
5. `rag-benchmark-101` — 차별화 높음
6. `ai-app-patterns-101` — eBook/브랜딩용
7. `rag-deep-dive` — Draft 유지, version-pinned deep dive
8. `langchain-101` — version-pinned, LCEL/Runnable 중심
9. `langgraph-101` — 브랜딩
10. `korean-ai-stack-101` — 한국어 트래픽 특화
11. `llm-finetuning-101`
12. `llm-from-scratch-101` polish/eBook화

### 진행 상황

- [ ] `llm-app-foundations-101` 목차 확정 및 1화 집필
- [ ] `llm-api-production-101` 목차 확정 및 1화 집필
- [ ] `ai-web-dev-101` → 흡수 계획 문서화
