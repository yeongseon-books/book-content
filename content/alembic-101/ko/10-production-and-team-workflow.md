---
title: "Alembic 101 (10/10): Production과 team workflow: PR, CI, 모니터링, 그리고 incident response"
series: alembic-101
episode: 10
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- Python
- Alembic
- Production
- CI
- workflow
- SQLite
last_reviewed: '2026-05-12'
seo_description: migration은 "가장 비가역적인 코드 변경"입니다. 일반 코드는 revert 한 번으로 되돌리지만, schema
  변경은 데이터를…
---

# Alembic 101 (10/10): Production과 team workflow: PR, CI, 모니터링, 그리고 incident response

이 글은 Alembic 101 시리즈의 마지막 글입니다. 여기서는 앞선 아홉 편의 내용을 production 운영 모델로 묶어서, PR 규칙, CI 체크, 모니터링, incident response까지 하나의 workflow로 정리합니다.

production에서 migration은 일반 application code보다 훨씬 비가역적입니다. 그래서 Alembic 안전성은 개인 습관이 아니라 팀 workflow, PR 규칙, 검증 루틴 안에 들어가 있어야 합니다.

![Alembic 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/alembic-101/10/10-01-diagram-the-team-level-alembic-operating.ko.png)
*Alembic 101 10장 흐름 개요*

## 먼저 던지는 질문

- one-revision-per-PR 원칙은 왜 중요할까요?
- Alembic-aware PR template과 CI checks는 어떻게 구성할까요?
- dev=SQLite, staging+prod=PostgreSQL 같은 multi-environment 전략은 어떻게 가져갈까요?

## 왜 중요한가

앞선 아홉 편은 한 명의 엔지니어가 자신의 환경에서 migration을 안전하게 적용하는 방법을 설명했습니다. 하지만 팀이 동시에 schema를 바꾸기 시작하면 문제가 달라집니다. 두 사람이 동시에 revision을 만들면 multi-head가 생기고, downgrade 검증이 없으면 rollback이 깨지며, production schema가 drift하기 시작하면 어디부터 손대야 할지도 모르게 됩니다. 운영 안정성은 코드 품질이 아니라 workflow 품질에서 나옵니다.

## 멘탈 모델

> migration은 **“가장 비가역적인 코드 변경”**입니다. 일반 코드는 버튼 한 번으로 revert할 수 있어도, schema 변경은 데이터를 끌고 가기 때문에 훨씬 되돌리기 어렵습니다. 그래서 PR 단계에서부터 일반 코드보다 더 엄격하게 다뤄야 합니다.

운영 workflow의 출발점은 단순합니다. 하나의 PR은 하나의 revision을 담고, 그 revision의 `upgrade`와 `downgrade`는 둘 다 검증되어 있어야 합니다.

### 다이어그램: 팀 단위 Alembic 운영 루프

## 핵심 개념

### 한 PR에 한 revision

여러 schema 변경을 한 PR에 묶으면 두 가지 문제가 생깁니다.

- 리뷰어가 모든 변경을 한꺼번에 이해해야 하므로 사고 확률이 올라갑니다.
- 그중 하나만 잘못돼도 일부만 되돌릴 수 없어서 전체를 함께 처리해야 합니다.

revision마다 PR을 분리하면 리뷰가 짧아지고, 실패 시 blast radius가 작아집니다. expand-contract도 자연스럽게 phase별 PR로 나눌 수 있습니다.

### CI 체크 항목

| 체크 | 명령 | Pass 조건 | Fail이 뜻하는 것 |
| --- | --- | --- | --- |
| unit tests | `python3 -m pytest` | 애플리케이션/모델 테스트가 모두 통과 | migration이 기대한 런타임 동작과 코드가 이미 어긋남 |
| drift guard | `alembic check` | 모델 변경이 revision과 일치 | 모델은 바뀌었는데 revision이 누락됐거나 autogenerate 검토가 덜 끝남 |
| downgrade round-trip | `alembic upgrade head && alembic downgrade -1 && alembic upgrade head` | upgrade와 downgrade가 모두 성공 | 비가역 변경, broken downgrade, 또는 stateful data migration 가정이 숨어 있음 |
| single-head guard | `alembic heads` 결과를 세어 정확히 1개 | head count = 1 | 동시에 만들어진 revision이 merge되지 않았음 |
| SQL preview artifact | `alembic upgrade head --sql > migration_preview.sql` | preview 파일 생성 + 리뷰어가 SQL을 읽을 수 있음 | 위험한 DDL이 숨어 있거나 PR 리뷰에서 SQL을 확인할 근거가 없음 |
| fresh DB smoke | 임시 DB를 만들고 `alembic upgrade head` 후 최소 검증 쿼리 실행 | 빈 DB에서 head까지 한 번에 적용되고 핵심 테이블이 존재 | 신규 환경 부트스트랩이나 초기 revision chain이 깨져 있음 |

`alembic check`는 1.9 이상에서 지원됩니다. 모델은 바뀌었는데 revision이 없다면 즉시 실패시킬 수 있습니다.

### multi-environment 전략

| 환경 | DB | 옵션 |
| --- | --- | --- |
| dev | SQLite | `render_as_batch=True` |
| staging | PostgreSQL | `compare_type=True`, `compare_server_default=True` |
| prod | PostgreSQL | deploy script invokes `alembic upgrade` |

dev에서는 SQLite로 빠르게 실험하고, staging부터는 production과 같은 PostgreSQL로 검증합니다. 이렇게 해야 두 엔진 차이에서 생기는 사고를 staging에서 먼저 잡을 수 있습니다. autogenerate 검증도 staging에서 끝내야 안전합니다.

### 팀 컨벤션

- **Revision message는 명령형 한 줄**로 씁니다: `add users phone column`
- **PR 제목에는 expand-contract phase tag를 붙입니다**: `[expand]`, `[migrate]`, `[contract]`
- **One revision per PR**
- **`down_revision` 충돌은 즉시 해결합니다**: multi-head 상태를 24시간 이상 방치하지 않습니다

### 운영 모니터링

`/health` endpoint가 현재 `alembic_version`을 반환하게 합니다.

```python
@app.get("/health")
def health():
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    return {"status": "ok", "alembic_version": version, "expected": EXPECTED_VERSION}
```

deploy 시점에 `EXPECTED_VERSION`을 env var로 주입하고, 어떤 인스턴스라도 다른 version을 보고하면 alarm을 올립니다. multi-instance 환경에서 partially-applied migration이나 outdated code를 즉시 감지할 수 있습니다.

### 인시던트 대응

migration 사고가 나면 instinct는 downgrade일 수 있지만, 8편에서 봤듯 실제 production에서는 제한적으로만 가능합니다. 실무에서 더 자주 쓰는 절차는 다음입니다.

```text
1. `/health`가 보고한 version과 이번 release의 기대 version을 비교합니다
2. `alembic heads`와 현재 `alembic_version`을 확인합니다
3. 장애가 code-only인지, schema-only인지, mixed code/schema인지 분류합니다
4. schema가 아직 backward-compatible할 때만 code rollback을 검토하고, 아니면 forward-fix를 작성합니다
5. `fix <broken_revision_id>: <issue>`를 쓰기 전에 깨진 revision ID를 정확히 고정합니다
```

forward-fix는 새 revision을 추가해 잘못된 상태를 정상 상태로 이동시키는 방식입니다. downgrade와 달리 `alembic_version` graph가 앞으로만 진행되므로 추적성이 좋고 blue/green에도 잘 맞습니다.

### drift triage 표

incident 초반에는 긴 회의보다 `증상 → 첫 명령 → 다음 액션` 표가 더 유용합니다.

| 증상 | 가능한 원인 | 첫 명령 | 다음 액션 |
| --- | --- | --- | --- |
| `/health`의 `expected`와 `alembic_version`이 다름 | 일부 인스턴스만 새 코드 또는 새 schema를 봄 | `curl -fsS https://api.example.com/health` | 인스턴스별 응답을 비교해 code rollout 문제인지 schema drift인지 분리 |
| `alembic heads`가 2개 이상 | merge revision 누락 | `alembic heads` | deploy 중단, merge revision PR부터 생성 |
| 오류는 새 버전에서만 발생 | 코드가 새 schema를 잘못 가정 | `/health` 버전 비교 + 최근 deploy 확인 | expand phase면 코드 rollback 우선 |
| old+new 버전 모두 실패 | schema revision 자체가 잘못됨 | `SELECT version_num FROM alembic_version` | broken revision ID를 고정한 뒤 forward-fix 작성 |

## 변경 전후

```text
# Before: 6 revisions per PR, downgrade not verified
- reviewer spends 30 minutes tracing all revisions
- one broken downgrade is discovered in prod
- rollback impossible, 30-minute downtime
```

```text
# After: one PR = one revision, downgrade verified in CI
- reviewer sees one revision, merges in five minutes
- CI auto-runs upgrade head + downgrade -1 + upgrade head
- broken downgrade is blocked at the PR
```

PR을 작게 유지하고 CI에서 downgrade, single-head, fresh-DB smoke를 같이 검증하면 어떤 종류의 migration 결함을 PR 단계에서 걸러내는지 훨씬 명확해집니다.

## 단계별 실습

### 1단계: PR template 작성

```markdown
## Migration PR Checklist

- [ ] One revision per PR
- [ ] expand-contract phase: [ ] expand / [ ] migrate / [ ] contract
- [ ] alembic check passes
- [ ] downgrade verified (CI auto)
- [ ] alembic upgrade head --sql output attached
- [ ] data migration is idempotent (WHERE clause)
- [ ] row counts of affected tables
```

이 템플릿을 `.github/pull_request_template.md`에 두면 모든 schema PR이 같은 형식을 따르게 됩니다.

### 2단계: CI에 downgrade verification 추가

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
    set -euo pipefail
    HEADS=$(alembic heads | python3 -c "import sys; print(sum(1 for line in sys.stdin if line.strip()))")
    [ "$HEADS" = "1" ] || { echo "Fail: multi-head detected ($HEADS)"; exit 1; }
- name: SQL preview
  run: alembic upgrade head --sql > migration_preview.sql
- name: fresh DB smoke
  run: |
    set -euo pipefail
    DB_FILE=$(mktemp /tmp/alembic-smoke-XXXX.db)
    trap 'rm -f "$DB_FILE"' EXIT
    export DATABASE_URL="sqlite:///$DB_FILE"
    alembic upgrade head
    python3 - <<'PY'
    import os
    import sqlite3

    db_path = os.environ["DATABASE_URL"].removeprefix("sqlite:///")
    conn = sqlite3.connect(db_path)
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='alembic_version'"
        ).fetchone()[0]
        assert count == 1, f"alembic_version missing in {db_path}"
        print(f"Pass: fresh DB reached head at {db_path}")
    finally:
        conn.close()
PY
- uses: actions/upload-artifact@v4
  with:
    name: migration-preview
    path: migration_preview.sql
```

위 예시는 `scripts/check_alembic_heads.py`나 `scripts/migrate_smoke_test.py` 같은 저장소 바깥 helper에 기대지 않습니다. 문서에 적힌 명령만으로도 head guard, downgrade round-trip, fresh DB 부팅 검증을 재사용할 수 있어야 합니다.

### 3단계: 환경별 설정 분리

```python
# env.py의 일부
def get_url():
    env = os.environ.get("APP_ENV", "dev")
    return {
        "dev": "sqlite:///./dev.db",
        "staging": "postgresql://staging-host/app",
        "prod": "postgresql://prod-host/app",
    }[env]

def run_migrations_online() -> None:
    connectable = create_engine(get_url())
    is_sqlite = connectable.url.get_backend_name() == "sqlite"
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=is_sqlite,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()
```

dev에서는 SQLite와 batch mode가 자동 적용되고, staging과 prod에서는 PostgreSQL과 strict comparison이 켜집니다.

### 4단계: monitoring 연결

```python
# health.py
EXPECTED_VERSION = os.environ["EXPECTED_ALEMBIC_VERSION"]

@app.get("/health")
def health():
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    ok = version == EXPECTED_VERSION
    return {"status": "ok" if ok else "drift", "alembic_version": version, "expected": EXPECTED_VERSION}
```

deploy pipeline에서 `EXPECTED_ALEMBIC_VERSION`을 주입하고, per-instance 응답을 대시보드에 비교해 drift가 나면 알람을 올립니다.

## 검증 루틴

```bash
set -euo pipefail

alembic check
alembic upgrade head
alembic downgrade -1
alembic upgrade head
HEADS=$(alembic heads | python3 -c "import sys; print(sum(1 for line in sys.stdin if line.strip()))")
[ "$HEADS" = "1" ] || { echo "Fail: multi-head detected ($HEADS)"; exit 1; }

DB_FILE=$(mktemp /tmp/alembic-smoke-XXXX.db)
trap 'rm -f "$DB_FILE"' EXIT
export DATABASE_URL="sqlite:///$DB_FILE"
alembic upgrade head
```

**확인할 점:** 위 블록은 문서 앞부분에서 소개한 것과 같은 게이트를 그대로 다시 실행합니다. `alembic check`는 drift를, round-trip은 downgrade를, head count는 branch hygiene를, fresh DB smoke는 신규 환경 부팅을 검증합니다.

### incident 첫 10분 진단 순서

```text
1. /health의 expected vs alembic_version을 비교한다.
2. `alembic heads`와 `SELECT version_num FROM alembic_version`으로 graph 상태를 확인한다.
3. 장애가 code-only인지 schema-only인지 mixed인지 분류한다.
4. backward-compatible expand phase면 code rollback을 검토하고, 아니면 forward-fix로 전환한다.
5. 깨진 revision ID를 고정한 뒤 `fix <broken_revision_id>: <issue>` 초안을 만든다.
6. 복구 후에는 어떤 CI gate가 빠졌는지 post-mortem에 남긴다.
```

이 순서는 green 체크리스트가 아니라 분기형 진단 절차입니다. 2단계에서 multi-head가 나오면 deploy를 멈추고 merge revision으로 돌아가야 하고, 3단계에서 mixed failure면 code rollback만으로 끝내지 말고 schema 호환성까지 같이 확인해야 합니다.

## 자주 하는 실수

- **한 PR에 여러 revision을 넣기.** 리뷰가 무거워지고 부분 revert가 불가능합니다.
- **CI에서 downgrade를 검증하지 않기.** 실제 사고가 난 뒤에야 broken downgrade를 발견하게 됩니다.
- **dev에서도 PostgreSQL만 강제하기.** 설정 비용이 커져 빠른 실험이 어려워집니다.
- **SQLite dev만 보고 바로 prod로 가기.** SQLite/PostgreSQL 차이로 인한 사고를 staging에서 못 잡습니다.
- **모니터링에 `alembic_version`을 넣지 않기.** partial application 상태를 감지할 방법이 없습니다.

## 실무 패턴

- **PR template과 CI enforcement를 함께 둡니다.** 사람이 놓쳐도 시스템이 막아 줍니다.
- **dev=SQLite, staging+prod=PostgreSQL** 전략으로 속도와 정확성을 함께 잡습니다.
- **incident response의 기본값은 forward-fix입니다.** downgrade는 정말 필요할 때만 씁니다.
- **revision message에 GitHub issue 번호를 포함합니다.** 예: `add users phone column (#1234)`.
- **schema 변경은 업무 시간대에 배포합니다.** 사고가 났을 때 대응 인력이 바로 있어야 합니다.
- **post-mortem에 schema-change verification 흐름을 반드시 포함합니다.** 무엇이 빠졌는지 되짚어야 같은 사고를 막을 수 있습니다.

## 체크리스트

- [ ] PR template이 one PR = one revision 원칙을 강제한다
- [ ] CI가 alembic check, upgrade+downgrade, head-count guard, SQL preview, fresh DB smoke를 자동 실행한다
- [ ] 환경 전략이 dev=SQLite, staging+prod=PostgreSQL로 분리돼 있다
- [ ] `/health` 응답에 `alembic_version`이 포함된다
- [ ] forward-fix 절차와 템플릿이 문서화돼 있다
- [ ] revision message가 명령형 한 줄이며 issue 번호를 포함한다

## 연습 문제

1. 위 PR template과 CI workflow를 프로젝트에 추가하고, 의도적으로 broken downgrade를 넣어 CI가 막는지 확인해 보세요.
2. `/health`에 `alembic_version`을 추가하고 drift가 나면 알람을 올리는 간단한 모니터링 스크립트를 작성해 보세요.
3. 가상의 incident 시나리오 하나를 정하고, 그 상황을 해결하는 forward-fix revision을 설계해 보세요.

## 팀 런북 템플릿: migration release day

문서가 길어질수록 현장 대응 속도는 떨어집니다. 운영일에는 아래처럼 짧은 런북 템플릿이 더 효과적입니다.

```text
[Release Day Runbook]
1. 대상 revision: <revision_id>
2. 변경 유형: expand / migrate / contract
3. 사전 게이트
   - alembic check: Pass
   - heads==1: Pass
   - fresh DB smoke: Pass
4. 실행 순서
   - migrate stage
   - deploy stage
   - smoke test
5. 실패 시 기본 대응
   - backward-compatible: code rollback 우선
   - non-compatible: forward-fix revision 작성
6. 기록
   - 실제 실행 시간
   - 관측된 alembic_version
   - 이상 징후
```

템플릿의 목적은 완벽한 문서화가 아니라, 장애 순간에 의사결정 순서를 강제하는 것입니다.

## CI 로그에서 보는 조기 경고 신호

아래 로그는 merge 전에 바로 잡아야 하는 대표 신호입니다.

```text
Fail: multi-head detected (2)
```

merge revision 누락입니다. 기능 코드 검토를 멈추고 그래프 정리부터 해야 합니다.

```text
FAILED: Can't proceed with --autogenerate option; ... does not provide a MetaData object
```

`env.py` wiring 결함입니다. migration 내용보다 설정부터 수정해야 합니다.

```text
AssertionError: backfill incomplete: 73 rows remain
```

데이터 단계 검증이 의도대로 동작한 상태입니다. 실패를 억지로 통과시키지 말고 backfill 기준을 다시 맞춰야 합니다.

## 프로덕션 모니터링 지표 최소 세트

Alembic 관점에서 최소 지표는 세 가지입니다.

1. 인스턴스별 `alembic_version` 분포
2. 배포 직후 5xx/latency 변화
3. 변경 대상 테이블의 NULL/불일치 카운트

```sql
SELECT version_num FROM alembic_version;
SELECT COUNT(*) FROM users WHERE phone IS NULL;
```

이 두 쿼리만 정기적으로 수집해도 schema drift와 tighten 타이밍 오류를 빠르게 감지할 수 있습니다.

## 정리

열 편에 걸쳐 Alembic의 init부터 production workflow까지 이어 봤습니다. 핵심을 한 문장으로 요약하면 이렇습니다.

> “Schema changes ship before code, with broader compatibility, one PR per revision, downgrade verified in CI, monitoring detects drift, incidents respond with forward-fix.”

시리즈는 여기서 끝나지만, 실제 운영에서는 위 원칙을 사람 기억이 아니라 PR template, CI enforcement, deploy pipeline, monitoring으로 자동화해야 합니다. 그다음 학습 단계는 SQLAlchemy ORM의 더 깊은 주제들입니다.

## 처음 질문으로 돌아가기

- **one-revision-per-PR 원칙은 왜 중요할까요?**
  - 본문의 기준은 Production과 team workflow: PR, CI, 모니터링, 그리고 incident response를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Alembic-aware PR template과 CI checks는 어떻게 구성할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **dev=SQLite, staging+prod=PostgreSQL 같은 multi-environment 전략은 어떻게 가져갈까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Alembic 101 (1/10): 왜 Alembic인가, 그리고 init까지](./01-why-alembic-and-init.md)
- [Alembic 101 (2/10): env.py와 target_metadata: 모델과 마이그레이션 연결](./02-env-py-and-target-metadata.md)
- [Alembic 101 (3/10): 첫 revision: upgrade와 downgrade를 손으로 작성](./03-first-revision-upgrade-downgrade.md)
- [Alembic 101 (4/10): autogenerate: 잡는 것과 못 잡는 것의 경계](./04-autogenerate-and-its-limits.md)
- [Alembic 101 (5/10): branch와 merge: 동시에 만든 revision을 합치는 법](./05-branches-and-merges.md)
- [Alembic 101 (6/10): 데이터 마이그레이션: schema 변경과 데이터 변경을 분리하기](./06-data-migrations.md)
- [Alembic 101 (7/10): online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기](./07-online-vs-offline-and-batch.md)
- [Alembic 101 (8/10): downgrade 전략: 언제 진심으로 작성하고 언제 막을 것인가](./08-downgrade-strategy.md)
- [Alembic 101 (9/10): 배포 순서와 blue/green: schema와 application code의 안전한 동기화](./09-deploy-ordering-and-blue-green.md)
- **Production과 team workflow: PR, CI, 모니터링, 그리고 incident response (현재 글)**

<!-- toc:end -->

## 참고 자료

- [sqlalchemy/alembic GitHub 저장소](https://github.com/sqlalchemy/alembic)
- [Alembic: Cookbook](https://alembic.sqlalchemy.org/en/latest/cookbook.html)
- [Alembic: `alembic check`](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#detecting-changes-in-models)
- [GitHub: PR templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)
- "Database Reliability Engineering" by Laine Campbell & Charity Majors

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/alembic-101/ko/10-production-and-team-workflow)

Tags: Python, Alembic, SQLAlchemy, Migration
