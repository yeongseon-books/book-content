---
title: '배포 순서와 blue/green: schema와 application code의 안전한 동기화'
series: alembic-101
episode: 9
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
- deploy
- blue-green
- ordering
- SQLite
last_reviewed: '2026-05-12'
seo_description: migration은 항상 "코드보다 먼저, 그리고 코드보다 호환성이 넓게"입니다.
---

# 배포 순서와 blue/green: schema와 application code의 안전한 동기화

이 글은 Alembic 101 시리즈의 아홉 번째 글입니다. 여기서는 migration과 application code를 어떤 순서로 배포해야 안전한지, 그리고 blue/green 환경에서 schema 호환성을 어떻게 설계해야 하는지 정리합니다.

많은 schema 사고는 migration 코드 자체보다 deploy ordering에서 시작됩니다. 특히 blue/green이나 rolling 환경에서는 두 버전의 앱이 같은 DB를 동시에 사용하므로, schema는 항상 그 두 버전 모두와 호환되어야 합니다.

## 이 글에서 다룰 문제

- migration-first와 code-first deploy ordering은 어떻게 다를까요?
- 왜 blue/green deploy는 두 앱 버전과 동시에 호환되는 schema를 요구할까요?
- NOT NULL 강화는 왜 두 단계로 나눠야 할까요?
- column rename은 왜 4단계 패턴으로 접근해야 할까요?
- 여러 인스턴스 환경에서 migration을 정확히 한 번만 실행하려면 어떻게 할까요?

## 왜 중요한가

production schema 사고의 상당수는 코드와 schema가 잘못된 순서로 배포될 때 발생합니다. 새 컬럼이 코드보다 먼저 존재하면 안전하지만, 코드가 새 컬럼을 먼저 가정하고 schema가 뒤따라오면 즉시 500 에러가 납니다. blue/green에서는 v1과 v2가 동시에 같은 schema를 읽고 쓰므로, schema는 전환 구간 내내 양쪽을 모두 수용해야 합니다.

## 멘탈 모델

> migration은 항상 **“코드보다 먼저, 그리고 코드보다 더 넓은 호환성으로”** 배포됩니다. 컬럼을 추가할 때는 컬럼이 먼저 존재해야 하고, 컬럼을 제거할 때는 코드가 먼저 사용을 멈춰야 합니다. 이 두 방향만 기억해도 deploy 사고 대부분을 피할 수 있습니다.

git 비유로 보면 migration은 코드 PR보다 먼저 들어가는 PR이고, drop은 “이 컬럼 사용을 중단한다”는 코드 PR보다 나중에 들어가는 PR입니다.

## 핵심 개념

### migration-first vs code-first

| 변경 종류 | 배포 순서 | 이유 |
| --- | --- | --- |
| **Add column / table** | migration → code | 코드는 새 컬럼이 이미 존재해야 쓸 수 있다 |
| **Drop column / table** | code → migration | 코드가 사용을 멈춘 뒤에 drop해야 안전하다 |
| **Type widen** (`String(50)` → `String(100)`) | migration → code | 더 큰 값을 저장할 수 있어야 코드가 쓸 수 있다 |
| **Type narrow** | code → migration | 코드가 작은 값만 쓰기 시작한 뒤에 줄여야 한다 |

핵심은 전환 중에도 이전 버전 코드가 계속 살아 있어야 한다는 점입니다. 이것이 blue/green과 rolling deploy의 기본 가정입니다.

### blue/green에서의 schema 호환성

```text
t0: only blue (v1) running, schema=S1
t1: migrate schema to S2 (S1, S2 both compatible with v1)
t2: bring up green (v2); blue (v1) and green (v2) run concurrently (both work with S2)
t3: shut down blue, only green runs
t4 (next deploy): migrate schema to S3 (now safe to drop S2 compatibility)
```

t1에서 적용하는 schema는 반드시 v1과 v2 모두를 받아야 합니다. 그래서 expand-contract가 사실상 필수입니다.

### NOT NULL 강화는 2단계로

`nullable=False`를 한 revision에 몰아넣으면 blue/green 전환 중 즉시 사고가 날 수 있습니다. 두 단계로 분리해야 합니다.

```text
phase 1 (now):
  - DB: add column as nullable=True with a default
  - code: always writes a value into the new column
  - deploy: migration → code

(time passes; verify every row has a value)

phase 2 (next deploy):
  - DB: tighten column to nullable=False
  - code: unchanged
  - deploy: migration only
```

phase 2는 모든 row가 채워졌다는 검증이 끝난 뒤에만 적용해야 합니다.

### column rename의 4단계

```text
phase 1: add new column (nullable=True); code keeps using the old column
phase 2: code dual-writes (writes both old and new)
phase 3: backfill data; code reads and writes only the new column
phase 4: drop the old column (code already stopped using it)
```

각 phase는 독립 PR로 가져가고, phase 사이마다 production 안정성을 확인해야 합니다. 느리지만 가장 안전한 패턴입니다.

### 여러 인스턴스에서 정확히 한 번 실행하기

모든 application instance가 `alembic upgrade`를 실행하면 race condition이 생깁니다. Alembic이 `alembic_version`에 lock을 걸긴 하지만, 더 안전한 방법은 다음 중 하나입니다.

- **deploy script가 한 번만 호출**: 앱 인스턴스가 뜨기 전에 별도 stage에서 migration 실행
- **Kubernetes Job / initContainer**: 전용 Job으로 앱 컨테이너보다 먼저 migration 수행
- **CI/CD pipeline 분리**: `deploy` 앞에 `migrate` stage 배치

application startup에서 `alembic upgrade head`를 호출하는 패턴은 단일 인스턴스 개발 환경에서는 괜찮지만 production에는 권장되지 않습니다.

## 변경 전후

```text
# Before: code-first deploy, immediate 500 errors
1. deploy v2 (code that uses the new column)
2. every request fails with "no such column"
3. 30 minutes later, schema migrate
```

```text
# After: migration-first deploy
1. schema migrate (add new column as nullable=True)
2. v1 instances keep running normally (they ignore the new column)
3. deploy v2 (code that uses the new column)
4. blue/green both work correctly
```

After 패턴은 전환 구간의 사고 창을 거의 없애 줍니다. 이 순서를 매 deploy에서 지키는 것이 운영 기본값입니다.

## 단계별 실습

### 1단계: schema add

```python
# revision: add_users_phone
def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(20), nullable=True))

def downgrade() -> None:
    op.drop_column("users", "phone")
```

먼저 CI/CD에서 이 migration을 적용합니다. 아직 application code는 `phone`을 건드리지 않습니다. v1과 v2 모두 안전합니다.

### 2단계: code deploy

이제 application code가 `phone`에 값을 쓰기 시작합니다. blue/green 전환 구간에서 v1은 이 컬럼을 무시하고, v2는 채우기만 하므로 두 버전 모두 안전합니다.

### 3단계: NOT NULL 강화

모든 row에 `phone`이 채워졌는지 확인한 뒤 schema를 조입니다.

```python
# revision: tighten_users_phone_not_null
def upgrade() -> None:
    bind = op.get_bind()
    null_count = bind.execute(text("SELECT COUNT(*) FROM users WHERE phone IS NULL")).scalar()
    assert null_count == 0, f"{null_count} rows still NULL"
    with op.batch_alter_table("users") as batch:
        batch.alter_column("phone", existing_type=sa.String(20), nullable=False)

def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("phone", existing_type=sa.String(20), nullable=True)
```

assertion이 마지막 안전망입니다. NULL이 남아 있으면 migration은 실패하고 schema는 바뀌지 않습니다.

### 4단계: old column drop

이전 컬럼을 제거할 때는 application code가 더 이상 쓰지 않는다는 사실을 확인하고, 다음 deploy cycle에서 내립니다.

```python
def upgrade() -> None:
    op.drop_column("users", "old_phone")

def downgrade() -> None:
    raise NotImplementedError("drop is irreversible")
```

### 5단계: deploy pipeline 정렬

```yaml
# CI/CD
stages:
  - test
  - migrate     # alembic upgrade head
  - deploy      # rolling update
  - smoke-test
```

`migrate`가 항상 `deploy`보다 먼저 오도록 강제해야 합니다.

## 자주 하는 실수

- **code-first deploy.** 코드가 새 schema를 먼저 가정하면 즉시 실패합니다.
- **NOT NULL을 한 revision에 묶기.** blue/green에서 이전 버전이 NULL을 쓰는 순간 사고가 납니다.
- **컬럼을 즉시 drop하기.** 코드가 사용을 멈췄더라도 최소 한 deploy cycle은 기다리는 편이 안전합니다.
- **application startup에서 `alembic upgrade head`를 호출하기.** multi-instance 환경에서는 race와 partial application 리스크가 큽니다.
- **rename을 한 번에 처리하기.** 실제로는 drop+add와 다르지 않아서 데이터 손실 위험이 큽니다.

## 실무 패턴

- **CI/CD stage를 `migrate` → `deploy`로 고정합니다.** 가장 단순하고 효과적인 규칙입니다.
- **NOT NULL 강화는 항상 두 단계로 나눕니다.** 중간에 data verification을 넣습니다.
- **drop은 한 deploy cycle 늦춥니다.** 즉시 제거는 피합니다.
- **Kubernetes에서는 Job이나 initContainer로 exactly-once execution을 보장합니다.**
- **deploy 전 `alembic check`를 실행합니다.** model/schema drift를 자동 탐지합니다.
- **PR 템플릿에 expand-contract phase를 적게 합니다.** 지금 이 변경이 어느 단계인지 항상 드러나게 만듭니다.

## 체크리스트

- [ ] schema add는 항상 code deploy보다 먼저 나간다
- [ ] schema drop은 코드가 사용을 멈춘 다음 deploy cycle에 나간다
- [ ] NOT NULL 강화는 두 단계로 분리했다
- [ ] rename은 dual-write 4단계를 따른다
- [ ] application startup에서 `alembic upgrade`를 호출하지 않는다
- [ ] CI/CD는 `migrate` 후 `deploy` 순서를 강제한다
- [ ] Kubernetes 환경에서는 Job 또는 initContainer로 exactly-once execution을 보장한다

## 연습 문제

1. add-column → code-deploy → NOT NULL tighten 흐름을 SQLite에서 끝까지 시뮬레이션해 보세요.
2. column rename을 4단계 dual-write 패턴으로 설계하고 phase별 PR 순서를 그려 보세요.
3. CI/CD pipeline을 `migrate` stage가 항상 `deploy`보다 먼저 오도록 바꿔 보세요.

## 정리, 다음 글

deploy ordering은 Alembic 기능이 아니라 운영 정책입니다. “schema first, broader compatibility”라는 한 문장을 머릿속에 두고, 모든 변경을 그 기준으로 분해해야 합니다. blue/green에서 가장 중요한 점은 전환 구간 내내 schema가 두 버전과 동시에 호환되어야 한다는 사실입니다.

다음 글에서는 팀 단위의 실제 workflow, 즉 PR 규칙, CI 체크, 모니터링, incident response를 다룹니다.

<!-- toc:begin -->
<!-- toc:end -->

## 참고 자료

- Alembic: Cookbook — https://alembic.sqlalchemy.org/en/latest/cookbook.html
- Martin Fowler: Blue Green Deployment — https://martinfowler.com/bliki/BlueGreenDeployment.html
- "Refactoring Databases" by Scott Ambler & Pramod Sadalage
- Kubernetes: Init Containers — https://kubernetes.io/docs/concepts/workloads/pods/init-containers/

Tags: Python, Alembic, deploy, blue-green, ordering, SQLite
