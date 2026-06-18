---
title: "바이브코딩을 위한 Alembic 기초 (10/10): production과 팀 workflow"
series: alembic-101
episode: 10
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Python
  - Alembic
  - SQLAlchemy
  - Migration
  - DB마이그레이션
---

# 바이브코딩을 위한 Alembic 기초 (10/10): production과 팀 workflow

이 글은 "바이브코딩을 위한 Alembic 기초" 시리즈의 마지막 글입니다.

---

migration은 "가장 비가역적인 코드 변경"입니다. 바이브코딩에서 AI는 PR과 CI 설정을 간단하게 제안하지만, schema 변경은 일반 코드보다 훨씬 엄격하게 관리해야 합니다. 한 PR에 여러 revision이 섞이거나, downgrade 검증이 빠지거나, production schema가 drift하기 시작하면 어디서부터 손대야 할지 모르게 됩니다.

여기서는 앞선 아홉 편의 내용을 production 운영 모델로 묶어서, PR 규칙, CI 체크, 모니터링, incident response까지 하나의 workflow로 정리합니다. 운영 안정성은 코드 품질이 아니라 workflow 품질에서 나옵니다.

> **핵심 인사이트:** one-revision-per-PR, CI에서 downgrade 검증, `/health`에 `alembic_version` 포함, incident 대응은 forward-fix 우선. 이 네 가지가 팀 수준 Alembic 운영의 핵심입니다.

## 이 글에서 다룰 문제

- one-revision-per-PR 원칙은 왜 중요할까요?
- Alembic-aware PR template과 CI checks는 어떻게 구성할까요?
- dev=SQLite, staging+prod=PostgreSQL 같은 multi-environment 전략은 어떻게 가져갈까요?
- production에서 incident가 나면 어떤 순서로 대응해야 할까요?
- AI가 단순하게 안내할 때 팀 workflow에서 어떻게 보완할까요?

## PR template과 CI 체크

**한 PR에 한 revision**을 강제하고, CI에서 다음을 자동 검증합니다.

```yaml
# .github/workflows/migrate.yml
- name: alembic check
  run: alembic check
- name: upgrade then downgrade
  run: |
    set -euo pipefail
    alembic upgrade head
    alembic downgrade -1
    alembic upgrade head
- name: head count guard
  run: |
    HEADS=$(alembic heads | python3 -c "import sys; print(sum(1 for line in sys.stdin if line.strip()))")
    [ "$HEADS" = "1" ] || { echo "Fail: multi-head detected ($HEADS)"; exit 1; }
- name: SQL preview
  run: alembic upgrade head --sql > migration_preview.sql
```

## 변경 전후 비교

**Before: 여러 revision을 한 PR에**
```text
- 리뷰어가 30분 동안 모든 revision을 추적
- broken downgrade가 production에서 발견됨
- rollback 불가, 30분 다운타임
```

**After: one PR = one revision, CI에서 downgrade 검증**
```text
- 리뷰어는 revision 하나만 보고 5분 안에 merge
- CI가 upgrade head → downgrade -1 → upgrade head 자동 실행
- broken downgrade가 PR 단계에서 차단됨
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 한 PR에 여러 revision | 리뷰가 무겁고 부분 revert 불가 | one PR = one revision 원칙 |
| CI에서 downgrade 미검증 | production에서야 broken downgrade 발견 | CI에 round-trip 자동화 |
| dev에서 PostgreSQL 강제 | 설정 비용으로 빠른 실험 어려움 | dev=SQLite, staging+prod=PostgreSQL |
| `/health`에 alembic_version 미포함 | partial application 감지 불가 | health endpoint에 version 포함 |
| forward-fix 대신 무조건 downgrade | production에서 downgrade는 제한적 | forward-fix를 기본 대응으로 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"Alembic CI workflow를 만들어줘.
alembic check, upgrade+downgrade round-trip,
single-head guard, SQL preview를 모두 포함해야 해"

# /health endpoint에 alembic_version 추가:
@app.get("/health")
def health():
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    return {"status": "ok", "alembic_version": version, "expected": EXPECTED_VERSION}
```

## 운영 체크리스트

- [ ] PR template이 one PR = one revision 원칙을 강제한다
- [ ] CI가 alembic check, upgrade+downgrade, head-count guard, SQL preview를 자동 실행한다
- [ ] 환경 전략이 dev=SQLite, staging+prod=PostgreSQL로 분리돼 있다
- [ ] `/health` 응답에 `alembic_version`이 포함된다
- [ ] forward-fix 절차와 템플릿이 문서화돼 있다
- [ ] revision message가 명령형 한 줄이며 issue 번호를 포함한다

## 처음 질문으로 돌아가기

- **one-revision-per-PR 원칙은 왜 중요할까요?** migration은 가장 비가역적인 코드 변경이라 PR을 작게 유지해야 리뷰 품질과 rollback 가능성이 모두 올라갑니다.
- **CI checks는 어떻게 구성할까요?** alembic check, upgrade+downgrade round-trip, single-head guard, SQL preview, fresh DB smoke를 자동화합니다.
- **incident 대응은?** forward-fix를 기본값으로 두고, backward-compatible한 경우에만 code rollback을 검토합니다.

## 정리

열 편에 걸쳐 Alembic의 init부터 production workflow까지 이어 봤습니다. 핵심을 한 문장으로 요약하면: schema changes ship before code, with broader compatibility, one PR per revision, downgrade verified in CI, monitoring detects drift, incidents respond with forward-fix. 바이브코딩에서 AI의 단순한 안내를 넘어 팀 workflow로 안전성을 자동화하는 것이 Alembic 운영의 완성입니다.

## 참고 자료

- [Alembic: Cookbook](https://alembic.sqlalchemy.org/en/latest/cookbook.html)
- [Alembic: `alembic check`](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#detecting-changes-in-models)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/alembic-101/ko/10-production-and-team-workflow)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Alembic 기초 (1/10): 왜 Alembic인가, 그리고 init까지
- 바이브코딩을 위한 Alembic 기초 (2/10): env.py와 target_metadata
- 바이브코딩을 위한 Alembic 기초 (3/10): 첫 revision: upgrade와 downgrade
- 바이브코딩을 위한 Alembic 기초 (4/10): autogenerate와 그 한계
- 바이브코딩을 위한 Alembic 기초 (5/10): branch와 merge
- 바이브코딩을 위한 Alembic 기초 (6/10): 데이터 마이그레이션
- 바이브코딩을 위한 Alembic 기초 (7/10): online과 offline 모드
- 바이브코딩을 위한 Alembic 기초 (8/10): downgrade 전략
- 바이브코딩을 위한 Alembic 기초 (9/10): 배포 순서와 blue/green
- **바이브코딩을 위한 Alembic 기초 (10/10): production과 팀 workflow (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, Python, Alembic, SQLAlchemy, Migration, DB마이그레이션
