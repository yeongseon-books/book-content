---
title: "배포 순서와 blue/green: schema와 application code의 안전한 동기화"
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
last_reviewed: '2026-05-03'
---

# 배포 순서와 blue/green: schema와 application code의 안전한 동기화

## 이 글에서 배울 것

- migration-first와 code-first 배포 순서의 차이
- blue/green 배포에서 schema 변경이 동시에 두 버전과 호환되어야 하는 이유
- NOT NULL 강화를 두 단계로 나누는 expand-contract 적용
- 컬럼 rename을 4단계로 나누는 표준 흐름
- 다중 인스턴스 환경에서 마이그레이션을 한 번만 실행하는 기법

## 이 글에서 답할 질문

- migration-first 배포와 code-first 배포는 각각 어떤 위험을 키우거나 줄이는가?
- blue/green 배포에서 schema 변경은 왜 두 코드 버전과 동시에 호환되어야 하는가?
- NOT NULL 강화를 두 단계로 나누어 안전하게 적용하는 절차는 어떻게 되는가?
- 컬럼 rename을 4단계 expand-contract로 나누면 각 단계에서 무슨 일이 벌어지는가?
- 다중 인스턴스 환경에서 마이그레이션이 단 한 번만 실행되도록 보장하는 방법은 무엇인가?

## 왜 중요한가

production에서 가장 많은 schema 사고는 코드와 schema의 배포 순서가 어긋났을 때 발생합니다. 새 컬럼이 코드보다 먼저 만들어져 있으면 안전하지만, 코드가 새 컬럼을 먼저 사용하기 시작하는데 schema가 따라오지 않으면 즉시 500 에러입니다. blue/green 배포에서는 두 버전이 동시에 같은 schema에 접근하므로, schema는 항상 두 버전과 호환되어야 합니다.

## Mental Model

> migration은 항상 **"코드보다 먼저, 그리고 코드보다 호환성이 넓게"**입니다. 새 컬럼을 추가할 때는 컬럼이 먼저 존재하고, 컬럼을 제거할 때는 코드가 먼저 사용을 멈춥니다. 이 두 방향을 한 줄로 외우면 거의 모든 배포 사고가 사라집니다.

git에 비유하면 migration은 코드보다 빠른 PR이고, drop은 코드의 사용 중단 PR보다 늦은 PR입니다.

## 핵심 개념

### migration-first vs code-first

| 변경 종류 | 배포 순서 | 이유 |
| --- | --- | --- |
| **컬럼/테이블 추가** | migration → code | 코드가 새 컬럼을 사용할 때 이미 존재해야 함 |
| **컬럼/테이블 삭제** | code → migration | 코드가 사용을 멈춘 후에 안전하게 drop |
| **타입 확장** (`String(50)` → `String(100)`) | migration → code | 더 큰 데이터 저장 가능해야 코드가 사용 |
| **타입 축소** | code → migration | 코드가 작은 값만 쓰기 시작한 후 축소 |

핵심은 "이전 버전의 코드도 여전히 동작해야 한다"는 점입니다. 이것이 blue/green과 rolling deploy의 기본 가정입니다.

### blue/green 배포의 schema 호환성 요구

```text
시점 t0: blue(v1)만 동작, schema=S1
시점 t1: schema를 S2로 migrate (S1, S2 모두 v1 호환)
시점 t2: green(v2) 띄움, blue(v1) green(v2) 동시 동작 (둘 다 S2 동작)
시점 t3: blue 종료, green만 동작
시점 t4 (다음 배포): schema를 S3로 migrate (S2 호환 제거 가능)
```

t1 시점의 schema 변경은 v1과 v2 양쪽에 호환되어야 합니다. 이것이 expand-contract가 필수인 이유입니다.

### NOT NULL 강화의 두 단계 분리

`nullable=False`를 한 revision에 묶으면 blue/green 환경에서 즉시 사고입니다. 두 단계로 나눕니다.

```text
단계 1 (now):
  - DB: nullable=True로 컬럼 추가, default 설정
  - 코드: 새 컬럼에 항상 값을 채움
  - 배포: migration → code

(시간 경과, 모든 row에 값이 채워졌는지 확인)

단계 2 (next deploy):
  - DB: nullable=False로 강화
  - 코드: 변경 없음
  - 배포: migration만
```

단계 사이의 시간은 짧을 수도 길 수도 있지만, 적어도 데이터가 모두 채워졌다는 검증 후에 단계 2를 적용합니다.

### 컬럼 rename의 4단계

```text
단계 1: 새 컬럼 추가 (nullable=True), 코드는 이전 컬럼 사용
단계 2: 코드가 새 컬럼에 dual-write (이전, 새 모두에 쓰기)
단계 3: 데이터 backfill, 코드가 새 컬럼만 read+write
단계 4: 이전 컬럼 drop (코드는 이미 사용 안 함)
```

각 단계가 독립 PR이고, 각 단계 사이에 production이 안정되었음을 확인합니다. 시간이 걸리지만 가장 안전합니다.

### 다중 인스턴스에서 한 번만 실행

`alembic upgrade`를 모든 인스턴스가 실행하면 race condition이 발생합니다. alembic 자체가 `alembic_version` 테이블에 락을 걸지만, 더 안전한 방법은 다음 중 하나입니다.

- **deploy script가 한 번만 호출**: 여러 인스턴스가 동작하기 전에 별도 단계로 마이그레이션 실행
- **kubernetes Job/initContainer**: 컨테이너 시작 전에 별도 Job으로 마이그레이션 실행
- **CI/CD 파이프라인 단계 분리**: `migrate` 단계를 `deploy` 단계 앞에 둠

application 시작 시 `alembic upgrade head`를 호출하는 패턴은 단일 인스턴스 dev에는 좋지만 production에서는 권장하지 않습니다.

## Before-After

```text
# Before: code-first 배포로 즉시 500 에러
1. v2 deploy (새 컬럼 사용 코드)
2. 모든 요청이 "no such column" 에러
3. 30분 후 schema migrate
```

```text
# After: migration-first 배포
1. schema migrate (새 컬럼 nullable=True 추가)
2. v1 인스턴스 정상 동작 (새 컬럼 무시)
3. v2 deploy (새 컬럼 사용)
4. blue/green 양쪽 정상 동작
```

After 패턴은 사고 윈도우가 0입니다. 모든 배포에서 이 순서를 강제하는 것이 운영의 기본입니다.

## 단계별 실습

### 1단계: schema add 단계

```python
# revision: add_users_phone
def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(20), nullable=True))

def downgrade() -> None:
    op.drop_column("users", "phone")
```

CI에서 먼저 적용. application 코드는 아직 phone을 사용하지 않습니다. v1과 v2 모두 정상 동작.

### 2단계: code deploy

application 코드가 phone에 값을 쓰기 시작합니다. blue/green 동시 동작 시점에서 v1은 phone을 무시하고 v2는 채웁니다. 둘 다 안전.

### 3단계: NOT NULL 강화

모든 row에 phone이 채워졌음을 확인합니다.

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

assertion으로 안전성을 확보합니다. 만약 NULL이 남아 있다면 마이그레이션이 실패하고 schema는 그대로 유지됩니다.

### 4단계: drop 단계

오래된 컬럼을 제거하려면 application이 더 이상 사용하지 않음을 확인한 후, 그 다음 배포 cycle에서 drop revision을 적용합니다.

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

`migrate`가 `deploy`보다 항상 먼저 실행되도록 강제.

## 자주 하는 실수

- **code-first 배포.** 코드가 먼저 새 schema를 가정하면 즉시 사고.
- **NOT NULL을 한 revision에 묶기.** blue/green에서 v1이 NULL을 쓰는 순간 fail.
- **drop을 즉시 실행.** 코드가 사용을 멈춘 직후 drop은 위험. 한 배포 cycle을 기다립니다.
- **application 시작 시 `alembic upgrade head` 호출.** 다중 인스턴스에서 race + 부분 적용 위험.
- **rename을 한 단계에.** drop+add로 풀려 데이터 손실. 4단계 dual-write 패턴 필수.

## 실무에서 쓰는 패턴

- **CI 단계 분리: `migrate`가 `deploy` 앞에.** 가장 단순하고 효과적.
- **NOT NULL 강화는 항상 두 단계.** 사이에 데이터 검증 마이그레이션.
- **drop은 한 배포 cycle 늦춘다.** 즉시 drop 금지.
- **kubernetes initContainer 패턴.** Job으로 한 번만 실행 보장.
- **deploy 전 `alembic check`**: model과 schema가 어긋났는지 자동 검출.
- **expand-contract를 PR description의 표준 항목으로.** "어떤 단계인가"를 명시.

## 체크리스트

- [ ] 모든 schema 추가는 code 배포보다 먼저 적용된다
- [ ] 모든 schema 삭제는 code가 사용을 멈춘 다음 배포 cycle에 적용된다
- [ ] NOT NULL 강화는 두 단계로 나뉘어 있다
- [ ] rename은 dual-write 4단계 패턴을 따른다
- [ ] application 시작 시 `alembic upgrade`를 호출하지 않는다
- [ ] CI/CD 파이프라인에서 migrate가 deploy 앞에 있다
- [ ] kubernetes 환경이면 initContainer 또는 Job으로 한 번만 실행

## 연습 문제

1. 새 컬럼 추가 → code deploy → NOT NULL 강화 흐름을 SQLite에서 직접 시뮬레이션하세요.
2. 컬럼 rename을 4단계 dual-write로 작성하고 단계별 PR을 그려 보세요.
3. CI/CD 파이프라인에 `migrate` 단계를 분리해 deploy와의 순서가 어긋나지 않도록 설정하세요.

## 정리, 다음 글

배포 순서는 alembic 자체가 아닌 운영 정책의 영역입니다. "schema는 코드보다 먼저, 호환성이 넓게"라는 한 줄을 머릿속에 두고 모든 변경을 그 기준으로 분해하세요. blue/green에서는 schema가 두 버전과 호환되어야 한다는 점이 핵심.

다음 글은 실제 팀에서 사용하는 PR/리뷰/CI 워크플로우와 운영 자동화 도구를 다룹니다.

## 참고 자료

- Alembic: Cookbook — https://alembic.sqlalchemy.org/en/latest/cookbook.html
- Martin Fowler: Blue Green Deployment — https://martinfowler.com/bliki/BlueGreenDeployment.html
- "Refactoring Databases" by Scott Ambler & Pramod Sadalage
- Kubernetes: Init Containers — https://kubernetes.io/docs/concepts/workloads/pods/init-containers/

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, Alembic, deploy, blue-green, ordering, SQLite
