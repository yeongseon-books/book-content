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
last_reviewed: '2026-05-11'
seo_description: migration은 "가장 비가역적인 코드 변경"입니다. 일반 코드는 revert 한 번으로 되돌리지만, schema
  변경은 데이터를…
---

# Production과 team workflow: PR, CI, 모니터링, 그리고 incident response

## 핵심 질문

팀 단위로 Alembic을 운영할 때 PR 리뷰·릴리스·롤백을 어떻게 표준화해야 할까요?

이 글은 그 질문에 답하기 위해 운영과 팀 워크플로우의 핵심 결정과 실무 함정을 살펴봅니다.


## 이 글에서 다룰 문제

지금까지 9편에서 다룬 내용은 한 명이 자기 환경에서 실수 없이 적용하는 방법이었습니다. 팀이 동시에 schema를 바꾸기 시작하면 다른 차원의 문제가 생깁니다. 두 사람이 동시에 새 revision을 만들면 multi-head가 발생하고, 누군가가 downgrade를 테스트하지 않으면 rollback이 깨지고, 운영 중에 schema가 어긋나기 시작하면 어디부터 손대야 할지 모릅니다. 운영의 안정성은 코드 품질이 아니라 워크플로우 품질에서 옵니다.

## 멘탈 모델

> migration은 "가장 비가역적인 코드 변경"입니다. 일반 코드는 revert 한 번으로 되돌릴 수 있지만, schema 변경은 데이터를 동반하므로 되돌리기가 훨씬 어렵습니다. 그래서 PR 단계에서 일반 코드보다 더 엄격하게 다뤄야 합니다.

PR 한 건이 한 revision을 의미하고, 그 revision의 upgrade와 downgrade가 모두 검증되었음을 보장하는 것이 운영 워크플로우의 출발점입니다.

## 핵심 개념

### 한 PR에 한 revision 원칙

여러 schema 변경을 한 PR에 묶으면 두 가지 문제가 생깁니다.

- 리뷰어가 모든 변경을 동시에 이해해야 함 → 사고 확률 증가
- 일부만 문제가 있을 때 부분 revert가 불가 → 모든 변경을 함께 되돌려야 함

각 revision이 독립적으로 PR 단위가 되면 리뷰가 단순해지고 실패 시 영향 범위가 작습니다. expand-contract도 자연스럽게 단계별 PR로 분해됩니다.

### CI 체크 항목

```text
1. python3 -m pytest                                    # 단위 테스트
2. alembic check                                        # 모델과 스키마 차이 확인
3. alembic upgrade head && alembic downgrade -1         # 되돌리기 검증
4. alembic upgrade head --sql                           # SQL 미리보기 생성, PR 산출물로 첨부
5. python3 scripts/check_alembic_heads.py               # head가 1개인지 확인
6. python3 scripts/migrate_smoke_test.py                # 새 DB 기준 마이그레이션 적용
```

`alembic check`은 1.9 버전 이상에서 지원됩니다. model이 추가됐는데 revision이 빠졌다면 즉시 실패합니다.

### 다중 환경 전략

| 환경 | DB | 옵션 |
| --- | --- | --- |
| dev | SQLite | `render_as_batch=True` |
| staging | PostgreSQL | `compare_type=True`, `compare_server_default=True` |
| prod | PostgreSQL | deploy script가 `alembic upgrade` 호출 |

dev에서 SQLite를 쓰면 한 명이 빠르게 시작하고 빠르게 마이그레이션을 시뮬레이션할 수 있습니다. staging부터는 production과 같은 PostgreSQL을 써서 SQLite와 PostgreSQL의 차이로 인한 사고를 staging에서 잡습니다. autogenerate 검증도 staging에서 합니다.

### 팀 컨벤션

- revision 메시지는 명령형 한 줄로 씁니다: "add users phone column" (not "added", not "users phone added")
- PR 제목에 expand-contract 단계 태그를 붙입니다: `[expand]`, `[migrate]`, `[contract]`
- revision 단위로 PR을 분리합니다: 한 PR에 한 revision
- down_revision 충돌은 즉시 merge해 multi-head 상태가 24시간 이상 유지되지 않게 합니다

### 운영 모니터링

`/health` endpoint가 현재 alembic_version을 반환하도록 합니다.

```python
@app.get("/health")
def health():
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    return {"status": "ok", "alembic_version": version, "expected": EXPECTED_VERSION}
```

배포 시 EXPECTED_VERSION을 환경변수로 주입하고, 모든 인스턴스의 `/health`가 같은 버전을 보고하지 않으면 alarm을 발생시킵니다. multi-instance 환경에서 부분적으로만 마이그레이션이 적용되었거나 일부 인스턴스가 outdated 코드를 돌리고 있는 상황을 즉시 감지할 수 있습니다.

### 사고 대응

migration 사고가 나면 첫 번째 본능은 downgrade이지만, 8편에서 본 것처럼 downgrade가 가능한 경우는 제한적입니다. 실무에서 가장 자주 쓰는 절차는 다음입니다.

```text
1. 사고 인지 (alarm, error rate, /health version mismatch)
2. 원인 분류:
   - 코드 문제 → code rollback (schema는 그대로 둠, expand 단계라면 안전)
   - schema 문제 → forward-fix revision 작성
3. forward-fix revision: "fix <broken_revision_id>: <issue>"
4. 정상 회복 후, 사후 분석에서 broken_revision의 검증 단계가 왜 빠졌는지 회고
```

forward-fix는 새 revision을 추가하여 잘못된 상태를 정상 상태로 되돌리는 방식입니다. downgrade와 달리 alembic_version 그래프가 forward 방향으로 유지되어 추적성이 좋고, blue/green과도 호환됩니다.

## 변경 전후

```text
# 변경 전: 한 PR에 6개 revision, downgrade 미검증
- 리뷰어가 30분 동안 모든 revision을 추적
- 한 revision의 downgrade가 깨져 있는 것을 prod에서 발견
- rollback 불가, 30분 다운타임
```

```text
# 변경 후: 한 PR = 한 revision, CI에서 downgrade 검증 자동화
- 리뷰어는 한 revision만 봄, 5분 안에 머지
- CI가 upgrade head + downgrade -1 + upgrade head를 자동 실행
- 깨진 downgrade는 PR에서 차단
```

PR 사이즈를 작게 유지하고 CI에서 downgrade를 강제 검증하는 것만으로 사고의 절반이 사라집니다.

## 단계별 실습

### 1단계: PR 템플릿 작성

```markdown
## Migration PR 체크리스트

- [ ] 한 PR에 한 revision
- [ ] expand-contract 단계: [ ] expand / [ ] migrate / [ ] contract
- [ ] alembic check 통과
- [ ] downgrade 검증 (CI 자동)
- [ ] alembic upgrade head --sql 결과 첨부
- [ ] data migration이면 멱등성 확인 (WHERE 절)
- [ ] 영향받는 테이블의 row 수
```

이 템플릿을 GitHub의 `.github/pull_request_template.md`로 두면 모든 schema PR이 이 형식을 따르게 됩니다.

### 2단계: CI에 downgrade 검증 추가

```yaml
# 워크플로 파일 예시
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
    [ "$HEADS" = "1" ] || (echo "multi-head 감지"; exit 1)
- name: SQL preview
  run: alembic upgrade head --sql > migration_preview.sql
- uses: actions/upload-artifact@v4
  with:
    name: migration-preview
    path: migration_preview.sql
```

이 한 작업만으로 multi-head, 깨진 downgrade, 누락된 revision이 모두 차단됩니다.

### 3단계: 환경별 설정 분리

```python
# env.py 일부
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

dev에서는 SQLite + batch 모드가 자동 적용되고 staging/prod에서는 PostgreSQL과 strict comparison이 활성화됩니다.

### 4단계: 모니터링 연동

```python
# 파일: health.py
EXPECTED_VERSION = os.environ["EXPECTED_ALEMBIC_VERSION"]

@app.get("/health")
def health():
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    ok = version == EXPECTED_VERSION
    return {"status": "ok" if ok else "drift", "alembic_version": version, "expected": EXPECTED_VERSION}
```

배포 파이프라인에서 EXPECTED_ALEMBIC_VERSION을 주입하고 운영 dashboard에서 인스턴스별 응답을 비교합니다. drift가 감지되면 alarm.

## 자주 하는 실수

- 한 PR에 여러 revision을 넣기. 리뷰가 어렵고 부분 revert가 불가능합니다.
- downgrade를 CI에서 검증하지 않기. prod에서 사고가 난 뒤에야 깨진 것을 알게 됩니다.
- dev에서 PostgreSQL을 강제하기. 환경 구축 비용이 올라가고 한 명이 빠르게 실험하기 어려워집니다.
- dev SQLite로만 검증한 뒤 바로 prod로 가기. SQLite와 PostgreSQL의 차이 때문에 staging에서 사고가 납니다.
- monitoring에 alembic_version을 넣지 않기. 부분 적용 상태를 감지할 방법이 없습니다.

## 실무에서 쓰는 패턴

- PR template과 CI 강제를 함께 둡니다. 사람이 잊어도 시스템이 막아 줍니다.
- dev=SQLite, staging+prod=PostgreSQL 구성을 유지합니다. 빠른 실험과 정확성을 함께 가져갈 수 있습니다.
- forward-fix를 기본 사고 대응으로 삼습니다. downgrade는 정말 필요한 경우에만 씁니다.
- revision 메시지에 GitHub issue 번호를 포함합니다. 예: "add users phone column (#1234)".
- schema 변경은 영업시간에 수행합니다. 새벽 배포는 사고가 나면 대응 인력이 부족해질 수 있습니다.
- 사후 분석에는 schema 변경 검증 흐름을 항상 포함합니다. 무엇이 빠졌는지 회고해야 다음 사고를 줄일 수 있습니다.

## 체크리스트

- [ ] PR 템플릿이 한 PR = 한 revision을 강제한다
- [ ] CI가 alembic check, upgrade+downgrade, head-count guard, SQL preview를 자동 실행한다
- [ ] 환경별로 dev=SQLite, staging+prod=PostgreSQL이 구분되어 있다
- [ ] `/health` 응답이 alembic_version을 포함한다
- [ ] forward-fix template과 절차가 문서화되어 있다
- [ ] revision 메시지는 명령형 한 줄에 issue 번호 포함

## 정리, 다음 글

10편을 통해 alembic의 init부터 production workflow까지를 끝까지 다뤘습니다. 핵심을 한 문장으로 줄이면 다음과 같습니다.

> "schema 변경은 코드보다 먼저, 호환성이 넓게, 한 PR에 한 revision, downgrade는 CI에서 검증, monitoring으로 drift 감지, 사고는 forward-fix로 대응."

이 시리즈는 여기서 끝이지만, 실제 운영에서는 이 모든 항목이 자동화되고 PR 템플릿과 CI 강제로 정착되어야 합니다. 다음 학습은 SQLAlchemy의 ORM 깊이 (relationship, query optimization, async)로 이어집니다.

<!-- toc:begin -->
<!-- toc:end -->

## 참고 자료

- Alembic: Cookbook — https://alembic.sqlalchemy.org/en/latest/cookbook.html
- Alembic: `alembic check` — https://alembic.sqlalchemy.org/en/latest/autogenerate.html#detecting-changes-in-models
- GitHub: PR templates — https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests
- "Database Reliability Engineering" by Laine Campbell & Charity Majors

Tags: Python, Alembic, Production, CI, workflow, SQLite
