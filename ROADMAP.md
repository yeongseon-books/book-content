# Roadmap

## Current Focus

1. `llm-app-foundations-101` 1차 집필
2. `llm-api-production-101` 목차 확정
3. `ready` status 제거 및 `publish-ready`로 통일
4. ~~`ARCHITECTURE.md` 추가~~ (완료)
5. ~~`.sisyphus/medium`과 `scripts/`의 책임 경계 정리~~ (현재 구조 유지 결정, ARCHITECTURE.md 문서화 완료)
6. ~~Public asset pipeline hardening~~ (완료: validation, dual-repo, documentation, smoke test)
7. `assets/` Git LFS 또는 외부 CDN 이전 검토 (29 MB / 1,396 PNG)
8. GitHub Actions CI 고도화 (캐싱, 병렬 job 분리)
9. ~~Repository rename (`tech-writing` → `technical-content` → `book-content`)~~ (완료)
## Next Content Priorities

| Priority | Series | Track | Notes |
| --- | --- | --- | --- |
| 1 | `llm-app-foundations-101` | Traffic + eBook | AI/LLM 전체 입구 |
| 2 | `llm-api-production-101` | Traffic + eBook | Structured Output / Tool Calling / Streaming |
| 3 | `vector-search-101` | Traffic + eBook | Embedding / FAISS / Chunking |
| 4 | `document-ingestion-101` | eBook | RAG 기반 연계 |
| 5 | `rag-benchmark-101` | Traffic | RAGAS / Evaluation, 차별화 높음 |
| 6 | `ai-app-patterns-101` | eBook | Chatbot, RAG, Agent 패턴 |
| 7 | `rag-deep-dive` | Authority | version-pinned deep dive |
| 8 | `langchain-101` | Authority | LCEL/Runnable 중심 |
| 9 | `langgraph-101` | Authority | Graph agents |
| 10 | `korean-ai-stack-101` | Traffic | 한국어 특화 |
| 11 | `llm-finetuning-101` | Authority | LoRA, optional |
| 12 | `llm-from-scratch-101` | Authority | polish/eBook화 |

## ai-web-dev-101 처리

- `status: needs-update` 유지 — 신규 글 추가 금지
- 기존 7편 내용을 새 시리즈로 흡수:
  - 1~2화 → `llm-app-foundations-101`
  - 3화(챗봇) → `ai-app-patterns-101`
  - 4화(RAG) → `vector-search-101` / `document-ingestion-101`
  - 5화(Agent) → `ai-app-patterns-101` / `langgraph-101`
  - 6화(배포) → `llm-apps-ops-101`
  - 7화(평가) → `rag-benchmark-101` / `llm-apps-ops-101`

## Completed Migration Summary

Repository rename (`tech-blog` → `tech-writing` → `technical-content` → `book-content`)과 멀티채널 파이프라인 구축이 완료되었다.

- Phase 1: 문서 분리 (SERIES, PUBLISHING, STYLE_GUIDE, EBOOK, ROADMAP)
- Phase 2: 디렉토리 스캐폴딩 (`content/`, `docs/`, `exports/`, `templates/`, `scripts/`)
- Phase 3: 메타데이터 (`series.yaml`, per-series `series.yaml`, front matter 129/129)
- Phase 4: MkDocs 셋업 (`mkdocs build --strict` 통과, 129 파일)
- Phase 5: 스크립트 실 동작 (7개 스크립트 + `_transform.py`)
- Phase 6: 시리즈 파일 이동 (10/10 시리즈, 원자 커밋)
- Phase 7: 콘텐츠 품질 (Oracle review Waves 1-6, P0/P1/P2 이슈 해결)
- Phase 8: eBook integration (19/19 번들 strict-pass, 첫 PDF 산출물)
- Phase 9: Repository rename (`tech-blog` → `tech-writing` → `technical-content` → `book-content`) + medium URL 재생성

자세한 migration 기록은 [`MIGRATION_PLAN.md`](./MIGRATION_PLAN.md) 참조.

## Risks

- `finalize-posts.py`의 `SERIES_TAGS`와 `series.yaml` 동기화 검증 미구현
- `assets/` 바이너리(29 MB)가 Git history에 누적 — LFS 또는 외부 호스팅 필요
- 발행된 Medium 글의 raw URL이 GitHub redirect에 의존 (장기 신뢰 보증 아님)
- `book-content` rename 후 발행된 Medium 글의 old raw URL이 GitHub redirect에 의존 (장기 신뢰 보증 아님)
