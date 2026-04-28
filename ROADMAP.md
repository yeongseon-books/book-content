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
- [ ] 기존 시리즈 폴더를 `content/` 로 실제 이동 (Phase 6에서 시리즈별)

## Phase 3 — Metadata

- [x] 루트 `series.yaml` 추가 (시리즈 카탈로그 단일 출처)
- [ ] 시리즈별 `series.yaml` 추가 — Phase 6 시리즈 이동 커밋 안에서 동시 추가 (이동과 메타가 같은 원자 커밋이어야 경로 정합성 유지)
- [ ] 모든 글에 YAML front matter 추가 (Phase 7)
- [ ] `finalize-posts.py` 의 `SERIES_TAGS` 와 `series.yaml` 동기화 검증 추가

## Phase 4 — MkDocs

- [x] `mkdocs.yml` 추가 (현재는 placeholder nav — Phase 6 전까지 빌드되지 않음)
- [x] `requirements.txt` 추가 (mkdocs + material + pymdown + pyyaml + frontmatter)
- [x] `requirements-dev.txt` 추가 (mkdocs-ebook 옵션 설치 주석)
- [x] `scripts/build_docs.py` skeleton (content -> docs materialization 만 담당)
- [ ] `docs/` 자동 생성 로직 구현 (Phase 6 이후)
- [ ] `mkdocs serve` 로 ko/en 사이트 정상 빌드 확인 (Phase 6 이후)

## Phase 5 — Exporters (skeleton)

- [x] `scripts/export_tistory.py` skeleton
- [x] `scripts/export_medium.py` skeleton
- [x] `scripts/export_ebook_source.py` skeleton
- [x] `scripts/check_links.py` skeleton
- [x] `scripts/check_frontmatter.py` skeleton
- [x] `scripts/build_series_index.py` skeleton (mkdocs.yml `nav` 단일 소유자)
- [ ] 각 스크립트 실제 변환 로직 구현
- [ ] 기존 `.sisyphus/medium/{to-medium.py, finalize-posts.py, mermaid-to-png.py}` 와 통합/병행 정책 결정

## Phase 6 — Series file moves (시리즈별, 원자 커밋)

각 시리즈를 `<series>/` → `content/<series>/` 로 이동하고, **같은 커밋에서** (1) 모든 상대 경로(이미지, TOC 링크, references) 갱신 (2) `content/<series>/series.yaml` 추가를 함께 수행한다.

**Scope rule (catalog whitelist):** 이동 대상은 `series.yaml` 에 등재된 `path:` 값만이다. 루트의 다른 디렉토리는 절대 건드리지 않는다. 특히 다음을 명시적으로 제외한다.

- `azure-functions-host/` — Azure/azure-functions-host 의 vendored upstream source (Deep Dive 시리즈 인용용). 시리즈 아님.
- `assets/` — 위치 보존 (모든 ko/en/medium 파일 경로 동시 갱신 위험 회피)
- `.sisyphus/`, `docs/`, `exports/`, `templates/`, `scripts/`, `content/` — 인프라 디렉토리
- 루트 문서 (`README.md`, `MIGRATION_PLAN.md`, `ROADMAP.md`, `SERIES.md`, `PUBLISHING.md`, `STYLE_GUIDE.md`, `EBOOK.md`, `AGENTS.md`)
- 설정 (`mkdocs.yml`, `series.yaml`, `requirements*.txt`)

이동 대상 (catalog 등재):

- [ ] `azure-app-service-101`
- [ ] `azure-app-service-deep-dive`
- [ ] `azure-functions-101`
- [ ] `azure-functions-deep-dive`
- [ ] `azure-aks-101`
- [ ] `azure-aks-deep-dive`
- [ ] `azure-aca-101`
- [ ] `azure-aca-deep-dive`
- [ ] `ai-web-dev-101` (현재 flat → `content/ai-web-dev-101/{ko,en}/` 로 정규화)
- [ ] `llm-from-scratch-101`

이동 후 시리즈별 검증:

```bash
python3 .sisyphus/medium/finalize-posts.py
.sisyphus/style/check-ko.sh
```

## Phase 7 — Content Quality

- [ ] AI Web Dev 101 OpenAI API 예제 갱신 (모델/SDK/가격 stale 제거)
- [ ] AI Web Dev 101 영어 변형 작성
- [ ] Deep Dive 글에 `Source Version` 섹션 추가
- [ ] Deep Dive 글에 `Call Path Summary` 섹션 추가
- [ ] 101 글에 `Common Mistakes` 또는 `Checklist` 섹션 추가
- [ ] 모든 글에 `seo_title` front matter 필드 추가
- [ ] 모든 글에 `last_reviewed` 갱신
- [ ] `blog-only` / `ebook-only` 블록 도입 (필요한 글에 한해)

## Phase 8 — eBook integration

- [ ] `templates/ebook-preface.md`, `ebook-index.md` 채우기
- [ ] `export_ebook_source.py` 실 동작 구현
- [ ] Azure Functions 101 ko/en eBook source bundle 첫 빌드
- [ ] private `mkdocs-ebook` 와 통합 테스트
- [ ] 첫 PDF 산출물 확인

## Phase 9 — Repository rename & cutover

- [ ] **수동**: `gh repo rename tech-writing` (또는 GitHub UI Settings → Rename)
- [ ] `.sisyphus/medium/to-medium.py` 의 `OWNER/REPO` 상수 업데이트
- [ ] medium 변형 `OWNER/REPO` URL 일괄 재생성 (`to-medium.py` 의 `TAG` 도 함께 갱신)
- [ ] 이미 발행된 Medium 글의 raw URL 은 GitHub redirect 에 의존 — 장기 신뢰 보증 아님, 가능하면 재발행
- [ ] README badge / 외부 링크 업데이트
- [ ] 새 이름으로 첫 announcement post (선택)

---

## 차단 / 위험 (Risks)

- **R1**: 시리즈 이동 시 medium 변형의 commit-pinned URL 이 일시적으로 깨질 수 있음 → 이동 커밋 직후 `to-medium.py TAG` 를 새 commit으로 갱신하고 medium 재생성 동일 커밋에 포함.
- **R2**: front matter 도입 시 `finalize-posts.py` 의 visible Tags 라인 처리 로직과 충돌 가능 → finalizer 가 front matter `tags:` 를 우선 읽고 visible 라인을 동기화하도록 확장 필요 (Phase 3 후속 작업).
- **R3**: `mkdocs-ebook` 이 private 이라 CI 에서 eBook 빌드 검증 불가 → 본 저장소는 source bundle 검증(`python3 -c "import yaml; yaml.safe_load(open('.../mkdocs.yml'))"`)까지만 수행.
- **R4**: 한 번에 156+ 파일 이동 시 충돌/리뷰 부담 → 시리즈별 원자 커밋 강제 (Phase 6).
