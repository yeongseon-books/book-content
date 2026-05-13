---
title: 'Production과 team workflow: PR, CI, 모니터링, 그리고 incident response'
series: alembic-101
episode: 10
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
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

# Production과 team workflow: PR, CI, 모니터링, 그리고 incident response

이 글은 Alembic 101 시리즈의 마지막 글입니다. 여기서는 앞선 아홉 편의 내용을 production 운영 모델로 묶어서, PR 규칙, CI 체크, 모니터링, incident response까지 하나의 workflow로 정리합니다.

production에서 migration은 일반 application code보다 훨씬 비가역적입니다. 그래서 Alembic 안전성은 개인 습관이 아니라 팀 workflow, PR 규칙, 검증 루틴 안에 들어가 있어야 합니다.

## 이 글에서 다룰 문제

- one-revision-per-PR 원칙은 왜 중요할까요?
- Alembic-aware PR template과 CI checks는 어떻게 구성할까요?
- dev=SQLite, staging+prod=PostgreSQL 같은 multi-environment 전략은 어떻게 가져갈까요?
- production에서 schema drift를 감지하는 monitoring 패턴은 무엇일까요?
- migration incident가 났을 때 forward-fix 절차는 어떻게 운영할까요?

## 왜 중요한가

앞선 아홉 편은 한 명의 엔지니어가 자신의 환경에서 migration을 안전하게 적용하는 방법을 설명했습니다. 하지만 팀이 동시에 schema를 바꾸기 시작하면 문제가 달라집니다. 두 사람이 동시에 revision을 만들면 multi-head가 생기고, downgrade 검증이 없으면 rollback이 깨지며, production schema가 drift하기 시작하면 어디부터 손대야 할지도 모르게 됩니다. 운영 안정성은 코드 품질이 아니라 workflow 품질에서 나옵니다.

## 멘탈 모델

> migration은 **“가장 비가역적인 코드 변경”**입니다. 일반 코드는 버튼 한 번으로 revert할 수 있어도, schema 변경은 데이터를 끌고 가기 때문에 훨씬 되돌리기 어렵습니다. 그래서 PR 단계에서부터 일반 코드보다 더 엄격하게 다뤄야 합니다.

운영 workflow의 출발점은 단순합니다. 하나의 PR은 하나의 revision을 담고, 그 revision의 `upgrade`와 `downgrade`는 둘 다 검증되어 있어야 합니다.

## 핵심 개념

### 한 PR에 한 revision

여러 schema 변경을 한 PR에 묶으면 두 가지 문제가 생깁니다.

- 리뷰어가 모든 변경을 한꺼번에 이해해야 하므로 사고 확률이 올라갑니다.
- 그중 하나만 잘못돼도 일부만 되돌릴 수 없어서 전체를 함께 처리해야 합니다.

revision마다 PR을 분리하면 리뷰가 짧아지고, 실패 시 blast radius가 작아집니다. expand-contract도 자연스럽게 phase별 PR로 나눌 수 있습니다.

### CI 체크 항목

```text
1. python3 -m pytest                                    # unit tests
2. alembic check                                        # model vs schema drift
3. alembic upgrade head && alembic downgrade -1         # downgrade verification
4. alembic upgrade head --sql                           # SQL preview, attached as PR artifact
5. python3 scripts/check_alembic_heads.py               # confirm head count = 1
6. python3 scripts/migrate_smoke_test.py                # apply migrations to a fresh DB
```

`alembic check`는 1.9 이상에서 지원됩니다. 모델은 바뀌었는데 revision이 없다면 즉시 실패시킬 수 있습니다.

### multi-environment 전략

| 환경 | DB | 옵션 |
| --- | --- | --- |
| dev | SQLite | `render_as_batch=True` |
| staging | PostgreSQL | `compare_type=True`, `compare_server_default=True` |
| prod | PostgreSQL | deploy script invokes `alembic upgrade` |

dev에서 SQLite를 쓰면 한 명의 엔지니어가 빠르게 시작하고 migration을 손쉽게 실험할 수 있습니다. staging부터는 production과 같은 PostgreSQL을 써야 SQLite/PostgreSQL 차이로 인한 사고를 미리 잡을 수 있습니다. autogenerate 검증도 staging에서 하는 편이 맞습니다.

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

### incident response

migration 사고가 나면 instinct는 downgrade일 수 있지만, 8편에서 봤듯 실제 production에서는 제한적으로만 가능합니다. 실무에서 더 자주 쓰는 절차는 다음입니다.

```text
1. Detect the incident (alarm, error rate, /health version mismatch)
2. Classify the cause:
   - code issue → code rollback (leave schema as is; safe if you are in expand phase)
   - schema issue → write a forward-fix revision
3. forward-fix revision: "fix <broken_revision_id>: <issue>"
4. After recovery, post-mortem investigates which verification step was missing for the broken revision
```

forward-fix는 새 revision을 추가해 잘못된 상태를 정상 상태로 이동시키는 방식입니다. downgrade와 달리 `alembic_version` graph가 앞으로만 진행되므로 추적성이 좋고 blue/green에도 잘 맞습니다.

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

PR을 작게 유지하고 CI에서 downgrade를 강제 검증하면 실제 사고의 상당 부분을 줄일 수 있습니다.

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
    alembic upgrade head
    alembic downgrade -1
    alembic upgrade head
- name: head count guard
  run: |
    HEADS=$(alembic heads | wc -l)
    [ "$HEADS" = "1" ] || (echo "multi-head detected"; exit 1)
- name: SQL preview
  run: alembic upgrade head --sql > migration_preview.sql
- uses: actions/upload-artifact@v4
  with:
    name: migration-preview
    path: migration_preview.sql
```

이 한 job만으로 multi-head, broken downgrade, missing revision을 대부분 차단할 수 있습니다.

### 3단계: 환경별 설정 분리

```python
# part of env.py
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
- [ ] CI가 alembic check, upgrade+downgrade, head-count guard, SQL preview를 자동 실행한다
- [ ] 환경 전략이 dev=SQLite, staging+prod=PostgreSQL로 분리돼 있다
- [ ] `/health` 응답에 `alembic_version`이 포함된다
- [ ] forward-fix 절차와 템플릿이 문서화돼 있다
- [ ] revision message가 명령형 한 줄이며 issue 번호를 포함한다

## 연습 문제

1. 위 PR template과 CI workflow를 프로젝트에 추가하고, 의도적으로 broken downgrade를 넣어 CI가 막는지 확인해 보세요.
2. `/health`에 `alembic_version`을 추가하고 drift가 나면 알람을 올리는 간단한 모니터링 스크립트를 작성해 보세요.
3. 가상의 incident 시나리오 하나를 정하고, 그 상황을 해결하는 forward-fix revision을 설계해 보세요.

## 정리

열 편에 걸쳐 Alembic의 init부터 production workflow까지 이어 봤습니다. 핵심을 한 문장으로 요약하면 이렇습니다.

> “Schema changes ship before code, with broader compatibility, one PR per revision, downgrade verified in CI, monitoring detects drift, incidents respond with forward-fix.”

시리즈는 여기서 끝나지만, 실제 운영에서는 위 원칙을 사람 기억이 아니라 PR template, CI enforcement, deploy pipeline, monitoring으로 자동화해야 합니다. 그다음 학습 단계는 SQLAlchemy ORM의 더 깊은 주제들입니다.

<!-- toc:begin -->
<!-- toc:end -->

## 참고 자료

- Alembic: Cookbook — https://alembic.sqlalchemy.org/en/latest/cookbook.html
- Alembic: `alembic check` — https://alembic.sqlalchemy.org/en/latest/autogenerate.html#detecting-changes-in-models
- GitHub: PR templates — https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests
- "Database Reliability Engineering" by Laine Campbell & Charity Majors

Tags: Python, Alembic, Production, CI, workflow, SQLite
