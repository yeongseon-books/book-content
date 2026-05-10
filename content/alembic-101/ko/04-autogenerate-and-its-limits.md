---
title: 'autogenerate: 잡는 것과 못 잡는 것의 경계'
series: alembic-101
episode: 4
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
- autogenerate
- compare_type
- MetaData
- SQLite
last_reviewed: '2026-05-03'
seo_description: autogenerate는 현재 DB(ground truth)와 target_metadata(desired state)의
  diff를 만들어…
---

# autogenerate: 잡는 것과 못 잡는 것의 경계

## 이 글에서 답할 질문

- `alembic revision --autogenerate`는 내부적으로 무엇과 무엇을 비교하여 diff를 만드는가?
- autogenerate가 잘 잡지 못하는 변경에는 어떤 것들이 있는가?
- `compare_type`, `compare_server_default`, `include_object`, `include_name`은 각각 무엇을 제어하는가?
- table 또는 column rename을 autogenerate에 맡기면 위험한 이유는 무엇인가?
- 자동 생성된 revision을 사람이 다시 손볼 때 어떤 항목을 가장 먼저 검토해야 하는가?

## 이 글에서 다룰 문제

autogenerate는 alembic의 가장 강력한 기능이지만, "버튼 한 번 누르면 끝나는" 도구로 다루는 순간 production 사고가 납니다. 자동 생성된 파일을 그대로 commit하다가 column rename이 drop+create로 풀려 데이터가 사라지는 사례는 실제로 자주 발생합니다.

이 글의 목표는 autogenerate를 무서워하지 말고 정확히 그 한계를 이해해 "필요한 부분만 손으로 보강"할 수 있게 만드는 것입니다.

## Mental Model

> autogenerate는 **현재 DB(ground truth)와 `target_metadata`(desired state)의 diff**를 만들어 op 호출로 직렬화하는 도구입니다. diff 알고리즘이 보지 못하는 영역(데이터 수준의 의도, 식별자 변경, DB 종속 객체)은 자동으로 잡을 수 없습니다.

git diff에 비유하면 autogenerate는 라인 diff입니다. 의미적으로 같은 변경(rename)을 두 줄 삭제 + 두 줄 추가로 보는 것과 같은 한계가 있습니다.

## 핵심 개념

### 동작 원리

`alembic revision --autogenerate -m "..."`를 실행하면 다음 순서로 동작합니다.

1. `env.py`가 DB에 연결한다.
2. 현재 DB의 schema를 `MetaData`로 introspect한다 (Inspector 사용).
3. `target_metadata`(보통 `Base.metadata`)와 비교한다.
4. 차이를 `MigrationOps` 트리로 만든다.
5. `versions/<hash>_<msg>.py`에 op 호출로 렌더링한다.

핵심은 4번까지가 전부 in-memory diff라는 점입니다. 어떤 변경이 잡히고 잡히지 않는지는 모두 이 diff 단계에서 결정됩니다.

### autogenerate가 잘 잡는 것

| 변경 | 비고 |
| --- | --- |
| 새 테이블 추가/삭제 | 안정적 |
| 새 컬럼 추가/삭제 | 안정적 |
| 인덱스 추가/삭제 | `MetaData`에 정의된 경우 |
| 외래키 추가/삭제 | 기본 케이스 |
| `nullable` 변경 | 기본 켜짐 |

### autogenerate가 못 잡는 것 (또는 옵션 필요)

| 변경 | 기본 동작 | 필요한 설정 |
| --- | --- | --- |
| 컬럼 type 변경 (예: `String(50)` → `String(100)`) | 무시 | `compare_type=True` |
| `server_default` 변경 | 무시 | `compare_server_default=True` |
| `CHECK` constraint | 거의 무시 | DB에 따라 다름 |
| **table rename** | drop + create로 보임 | 손으로 `op.rename_table` |
| **column rename** | drop + add로 보임 | 손으로 `op.alter_column(... new_column_name=...)` |
| trigger/function/sequence(PostgreSQL) | 무시 | 직접 작성 |
| 데이터 변경 | 무시(영원히) | `op.execute` 또는 데이터 마이그레이션 |

특히 **rename**은 autogenerate가 절대 자동으로 잡을 수 없습니다. 이것이 데이터 손실 사고의 가장 흔한 원인입니다.

### `compare_type`과 `compare_server_default`

`env.py`의 `context.configure(...)`에 두 옵션을 넣어야 type/default 변경을 감지합니다.

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    render_as_batch=connection.dialect.name == "sqlite",
    compare_type=True,
    compare_server_default=True,
)
```

기본값이 `False`인 이유는 false positive가 적지 않기 때문입니다. `String(50)` ↔ `VARCHAR(50)`처럼 의미는 같은데 표현이 달라 diff가 잡히는 경우가 있습니다. 켜는 쪽이 일반적으로 안전하지만, 처음 켜면 한 번 정도는 "왜 잡히지?" 싶은 revision이 나올 수 있다는 점을 알아 두세요.

### `include_object`와 `include_name`

특정 테이블/스키마를 diff에서 제외하고 싶을 때 사용합니다.

```python
def include_object(object, name, type_, reflected, compare_to):
    # 외부 시스템이 관리하는 audit 테이블은 제외
    if type_ == "table" and name.startswith("legacy_"):
        return False
    return True

context.configure(
    connection=connection,
    target_metadata=target_metadata,
    include_object=include_object,
)
```

multi-tenant 환경, 다른 팀이 관리하는 테이블, 임시 테이블 등을 격리할 때 유용합니다.

## Before-After

```python
# Before: column rename이 drop + add로 잘못 잡힘
def upgrade() -> None:
    op.add_column("users", sa.Column("display_name", sa.String(100)))
    op.drop_column("users", "name")  # ← 데이터 손실!

def downgrade() -> None:
    op.add_column("users", sa.Column("name", sa.String(100)))
    op.drop_column("users", "display_name")
```

```python
# After: 손으로 rename으로 교체
def upgrade() -> None:
    op.alter_column("users", "name", new_column_name="display_name")

def downgrade() -> None:
    op.alter_column("users", "display_name", new_column_name="name")
```

After 버전은 데이터를 보존합니다. autogenerate가 만든 결과를 commit 전에 한 번 읽어야 하는 가장 큰 이유가 이것입니다.

## 단계별 실습

### 1단계: model 변경

```python
# models.py
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    tier: Mapped[str] = mapped_column(String(16), server_default="free")  # ← 추가
```

### 2단계: autogenerate 실행

```bash
alembic revision --autogenerate -m "add users.tier"
```

### 3단계: 생성된 파일 검토

```python
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(length=16), server_default="free", nullable=False))

def downgrade() -> None:
    op.drop_column("users", "tier")
```

이 정도는 그대로 commit해도 안전합니다. 하지만 type 변경이나 rename이 섞여 있다면 항상 손으로 교정해야 합니다.

### 4단계: rename이 필요한 변경

`name` → `display_name` rename을 하려고 model을 바꾸고 autogenerate를 돌리면 위 Before처럼 drop + add가 나옵니다. 이것을 다음과 같이 손으로 교정합니다.

```python
def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("name", new_column_name="display_name")

def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("display_name", new_column_name="name")
```

SQLite에서는 batch 모드가 필요합니다(3편 참고).

### 5단계: 잡히지 말아야 할 것 제외

테스트 환경에 사람이 직접 만든 임시 테이블이 있다면 `include_object`로 걸러서 매번 diff에 끼지 않게 합니다.

## 자주 하는 실수

- **autogenerate 결과를 그대로 commit.** 가장 흔한 사고 원인. 항상 git diff처럼 한 번 읽고 의심스러운 부분은 손으로 교정합니다.
- **rename을 model만 바꾸고 자동에 맡기기.** drop + add로 풀려 데이터가 사라집니다.
- **`compare_type`을 켜지 않고 type 변경.** revision은 비어 있는데 실제 schema는 다른 상태가 됩니다.
- **`server_default` 변경을 잡지 못함.** `compare_server_default=True`가 필요합니다.
- **다른 팀의 테이블을 함께 잡기.** `include_object`로 격리합니다.

## 실무에서 쓰는 패턴

- **PR diff 리뷰 체크리스트.** "rename이 drop+add로 풀린 곳 없는가?", "type 변경이 누락되지 않았는가?" 두 항목은 필수.
- **`compare_type`/`compare_server_default`는 켜고 운영.** 첫 한두 revision의 false positive는 감수하고, 그 후의 안전을 얻습니다.
- **migration이 큰 변경일 때는 autogenerate 결과를 일단 빈 revision으로 받고 손으로 다시 작성.** 자동 결과는 참고용으로 옆에 둡니다.
- **schema-only 라이브러리 테이블 격리.** Celery, APScheduler 등 third-party 테이블은 `include_object`로 제외하거나 별도 metadata로 분리합니다.
- **CI에서 `alembic check` 활용.** model과 migration이 어긋났는지 자동으로 검출합니다(alembic 1.9+).

## 체크리스트

- [ ] 자동 생성된 파일을 한 줄씩 읽고 의심스러운 부분을 손으로 교정했다
- [ ] rename이 drop + add로 풀린 부분이 없다
- [ ] `compare_type=True`, `compare_server_default=True`가 켜져 있다
- [ ] 외부 팀/라이브러리의 테이블은 `include_object`로 격리되어 있다
- [ ] 큰 변경은 빈 revision으로 받고 손으로 작성하는 정책을 따랐다
- [ ] CI에 `alembic check`이 들어 있다 (1.9+)

## 정리, 다음 글

autogenerate는 잘 쓰면 굉장히 효율적이지만 한계를 모르면 데이터 손실로 직결됩니다. "diff를 만들어 주는 도구"라는 모델을 머릿속에 두고, 자동 결과를 항상 사람 눈으로 한 번 더 검토하는 습관을 들이세요.

다음 글은 여러 사람이 동시에 revision을 만들 때 생기는 branch와 그것을 합치는 `alembic merge`를 다룹니다.

## 참고 자료

- Alembic: Auto Generating Migrations — https://alembic.sqlalchemy.org/en/latest/autogenerate.html
- Alembic: Comparing Types — https://alembic.sqlalchemy.org/en/latest/autogenerate.html#comparing-types
- Alembic: Comparing Server Defaults — https://alembic.sqlalchemy.org/en/latest/autogenerate.html#comparing-server-defaults
- Alembic: Limitations of Autogenerate — https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, Alembic, autogenerate, compare_type, MetaData, SQLite
