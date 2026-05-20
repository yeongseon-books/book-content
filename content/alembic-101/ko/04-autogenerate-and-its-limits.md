---
title: "Alembic 101 (4/10): autogenerate: 잡는 것과 못 잡는 것의 경계"
series: alembic-101
episode: 4
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
- autogenerate
- compare_type
- MetaData
- SQLite
last_reviewed: '2026-05-12'
seo_description: autogenerate는 현재 DB(ground truth)와 target_metadata(desired state)의
  diff를 만들어…
---

# Alembic 101 (4/10): autogenerate: 잡는 것과 못 잡는 것의 경계

이 글은 Alembic 101 시리즈의 네 번째 글입니다. 여기서는 `alembic revision --autogenerate`가 내부에서 무엇을 비교하는지, 그리고 어디까지는 자동화가 안전하고 어디부터는 사람이 직접 개입해야 하는지 구분합니다.

autogenerate는 매우 강력하지만, 의도까지 읽어 주는 도구는 아닙니다. 특히 rename처럼 의미를 해석해야 하는 변경은 사람이 마지막 책임을 져야 합니다.

## 먼저 던지는 질문

- `alembic revision --autogenerate`는 내부에서 무엇을 비교할까요?
- 어떤 변경은 잘 잡고, 어떤 변경은 놓치거나 옵션이 필요할까요?
- `compare_type`, `compare_server_default`, `include_object`, `include_name`은 언제 필요할까요?

## 큰 그림

![Alembic 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/alembic-101/04/04-01-diagram-the-autogenerate-diff-pipeline.ko.png)

*Alembic 101 4장 흐름 개요*

이 그림에서는 autogenerate: 잡는 것과 못 잡는 것의 경계를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> autogenerate: 잡는 것과 못 잡는 것의 경계의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

autogenerate는 Alembic에서 가장 생산성이 큰 기능이지만, “버튼 한 번 누르면 끝”이라고 믿는 순간 사고가 시작됩니다. generated file을 그대로 커밋했다가 column rename이 drop+create로 풀리고, 그 결과 데이터가 사라지는 일은 실제로 흔합니다.

이 글의 목표는 autogenerate를 과장되게 두려워하게 만드는 것이 아니라, 한계를 정확히 지도로 그려 주는 것입니다. 그래야 자동화가 잘하는 부분은 최대한 활용하고, 사람이 꼭 봐야 할 부분만 정확히 보강할 수 있습니다.

## 멘탈 모델

> Autogenerate는 **현재 DB(ground truth)와 `target_metadata`(desired state)의 diff를 만들고, 그 차이를 `op` 호출로 직렬화하는 도구**입니다. diff 알고리즘이 볼 수 없는 것, 즉 데이터 의미 수준의 의도, 식별자 rename, DB 전용 객체는 자동으로 감지할 수 없습니다.

git diff 비유가 잘 맞습니다. autogenerate는 line-level diff입니다. 의미상 같은 변경이라도 rename은 삭제와 추가로 보입니다.

### 다이어그램: autogenerate diff 파이프라인

## 핵심 개념

### 동작 원리

`alembic revision --autogenerate -m "..."`는 다음 순서로 동작합니다.

1. `env.py`가 DB에 연결합니다.
2. 현재 schema를 SQLAlchemy `Inspector`로 introspect해서 `MetaData`를 만듭니다.
3. 그것을 `target_metadata`(보통 `Base.metadata`)와 비교합니다.
4. 차이를 `MigrationOps` 트리로 변환합니다.
5. 결과를 `versions/<hash>_<msg>.py`에 `op` 호출로 렌더링합니다.

여기서 중요한 사실은 4단계까지가 모두 메모리 안에서 끝나는 비교라는 점입니다. 무엇이 잡히고 놓치는지는 이 비교 단계에서 이미 결정됩니다.

### autogenerate가 잘 잡는 것

| 변경 | 비고 |
| --- | --- |
| 새 테이블 추가/삭제 | 안정적 |
| 새 컬럼 추가/삭제 | 안정적 |
| 인덱스 추가/삭제 | `MetaData`에 정의된 경우 |
| 외래키 추가/삭제 | 기본 케이스 |
| `nullable` 변경 | 기본 활성화 |

### autogenerate가 놓치는 것 (또는 옵션이 필요한 것)

| 변경 | 기본 동작 | 필요한 설정 |
| --- | --- | --- |
| 컬럼 type 변경 (예: `String(50)` → `String(100)`) | 무시 | `compare_type=True` |
| `server_default` 변경 | 무시 | `compare_server_default=True` |
| `CHECK` constraint | 거의 무시 | DB에 따라 다름 |
| **table rename** | drop + create로 인식 | 손으로 `op.rename_table` |
| **column rename** | drop + add로 인식 | 손으로 `op.alter_column(... new_column_name=...)` |
| trigger / function / sequence (PostgreSQL) | 무시 | 직접 작성 |
| 데이터 변경 | 항상 무시 | `op.execute` 또는 별도 data migration |

특히 **rename은 자동 감지가 불가능합니다.** 이 점이 데이터 손실 사고의 가장 흔한 출발점입니다.

### `compare_type`과 `compare_server_default`

타입과 default 변경을 감지하려면 `env.py`의 `context.configure(...)`에 두 옵션을 넣어야 합니다.

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    render_as_batch=connection.dialect.name == "sqlite",
    compare_type=True,
    compare_server_default=True,
)
```

기본값이 `False`인 이유는 false positive가 있기 때문입니다. `String(50)`과 `VARCHAR(50)`처럼 의미는 같지만 표현이 다른 경우가 diff로 잡힐 수 있습니다. 그래도 장기적으로는 켜 두는 편이 더 안전합니다.

### `include_object`와 `include_name`

특정 테이블이나 스키마를 diff에서 제외하고 싶을 때 사용합니다.

```python
def include_object(object, name, type_, reflected, compare_to):
    # Skip audit tables managed by an external system
    if type_ == "table" and name.startswith("legacy_"):
        return False
    return True

context.configure(
    connection=connection,
    target_metadata=target_metadata,
    include_object=include_object,
)
```

다른 팀이 소유한 테이블, 라이브러리가 만든 테이블, 임시 테이블을 diff에서 격리할 때 유용합니다.

## 변경 전후

```python
# Before: column rename misread as drop + add
def upgrade() -> None:
    op.add_column("users", sa.Column("display_name", sa.String(100)))
    op.drop_column("users", "name")  # ← data loss!

def downgrade() -> None:
    op.add_column("users", sa.Column("name", sa.String(100)))
    op.drop_column("users", "display_name")
```

```python
# After: hand-edited to a real rename
def upgrade() -> None:
    op.alter_column("users", "name", new_column_name="display_name")

def downgrade() -> None:
    op.alter_column("users", "display_name", new_column_name="name")
```

After 쪽은 데이터를 보존합니다. generated result를 매번 사람이 읽어야 하는 가장 큰 이유가 바로 이것입니다.

## 단계별 실습

### 1단계: 모델 변경

```python
# models.py
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    tier: Mapped[str] = mapped_column(String(16), server_default="free")  # ← new
```

### 2단계: autogenerate 실행

```bash
alembic revision --autogenerate -m "add users.tier"
```

### 3단계: 생성 파일 검토

```python
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(length=16), server_default="free", nullable=False))

def downgrade() -> None:
    op.drop_column("users", "tier")
```

이 정도 단순한 변경은 그대로 커밋해도 안전합니다. 하지만 rename이나 타입 변경이 섞이는 순간 반드시 손으로 다듬어야 합니다.

### 4단계: rename이 필요한 변경 고치기

모델의 `name` 컬럼을 `display_name`으로 바꾸고 autogenerate를 돌리면 위 Before처럼 drop+add가 나옵니다. 손으로 다음처럼 고쳐야 합니다.

```python
def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("name", new_column_name="display_name")

def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("display_name", new_column_name="name")
```

SQLite에서는 batch mode가 필요합니다.

### 5단계: 잡히지 말아야 할 것 제외

테스트 환경에 사람이 직접 만든 임시 테이블이 있다면 `include_object`로 제외해서 diff가 계속 오염되지 않게 해야 합니다.

## 검증 루틴

```bash
alembic revision --autogenerate -m "rename probe"
python3 - <<'PY'
from pathlib import Path
latest = sorted(Path("alembic/versions").glob("*_rename_probe.py"))[-1]
print(latest.read_text())
PY
```

**확인할 점:** rename처럼 의미 해석이 필요한 변경은 대개 `drop_column` + `add_column`으로 출력됩니다. 그 순간이 손수 수정해야 한다는 신호입니다.

## 자주 하는 실수

- **autogenerate 결과를 그대로 커밋하기.** 가장 흔한 사고 원인입니다. git diff 읽듯이 한 줄씩 검토하세요.
- **모델 이름만 바꾸고 rename을 자동에 맡기기.** 결과는 drop+add이고 데이터는 사라집니다.
- **`compare_type` 없이 타입 변경하기.** revision은 비어 있는데 schema는 실제로 drift한 상태가 됩니다.
- **`server_default` 변경을 놓치기.** `compare_server_default=True`가 필요합니다.
- **다른 팀 소유 테이블까지 함께 잡기.** `include_object`로 경계를 만드세요.

## 실무 패턴

- **PR diff 리뷰 체크리스트를 만듭니다.** “rename이 drop+add로 풀렸는가?”, “타입 변경이 누락됐는가?”는 필수 항목입니다.
- **`compare_type`과 `compare_server_default`를 켜고 운영합니다.** 초반 false positive 몇 개보다 장기 안전이 더 중요합니다.
- **큰 변경은 autogenerate를 초안으로만 씁니다.** 결과를 참고하되 최종 revision은 손으로 정리합니다.
- **라이브러리 소유 테이블을 격리합니다.** Celery, APScheduler 같은 third-party 테이블은 exclusion으로 빼는 편이 좋습니다.
- **CI에서 `alembic check`를 돌립니다.** model과 migration drift를 자동으로 감지합니다.

## 체크리스트

- [ ] 생성된 파일을 한 줄씩 읽고 의심스러운 부분을 손으로 고쳤다
- [ ] rename이 drop + add로 풀린 부분이 없다
- [ ] `compare_type=True`와 `compare_server_default=True`가 켜져 있다
- [ ] 외부 팀/라이브러리 테이블은 `include_object`로 제외된다
- [ ] 큰 변경은 “빈 revision 후 수동 작성” 정책을 따른다
- [ ] CI에서 `alembic check`를 실행한다

## 연습 문제

1. `User` 모델에 `bio` 컬럼을 추가하고 autogenerate를 돌린 뒤, 그대로 커밋해도 안전한지 판단해 보세요.
2. `name` 컬럼을 `display_name`으로 rename한 뒤, 깨진 autogenerate 결과를 손으로 수정해 보세요.
3. `users.tier`의 default를 `"free"`에서 `"basic"`으로 바꾼 뒤 `compare_server_default`를 끈 경우와 켠 경우의 결과를 비교해 보세요.

## 정리, 다음 글

autogenerate는 제대로 쓰면 매우 효율적이지만, 한계를 무시하면 데이터 손실로 곧장 이어집니다. “이 도구는 diff를 만든다”라는 멘탈 모델을 유지하고, generated result를 항상 사람 눈으로 검토하는 습관을 가져가야 합니다.

다음 글에서는 여러 사람이 동시에 revision을 만들 때 생기는 branch와, 그것을 `alembic merge`로 어떻게 하나의 head로 다시 묶는지 다룹니다.

## 처음 질문으로 돌아가기

- **`alembic revision --autogenerate`는 내부에서 무엇을 비교할까요?**
  - 본문의 기준은 autogenerate: 잡는 것과 못 잡는 것의 경계를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **어떤 변경은 잘 잡고, 어떤 변경은 놓치거나 옵션이 필요할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`compare_type`, `compare_server_default`, `include_object`, `include_name`은 언제 필요할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Alembic 101 (1/10): 왜 Alembic인가, 그리고 init까지](./01-why-alembic-and-init.md)
- [Alembic 101 (2/10): env.py와 target_metadata: 모델과 마이그레이션 연결](./02-env-py-and-target-metadata.md)
- [Alembic 101 (3/10): 첫 revision: upgrade와 downgrade를 손으로 작성](./03-first-revision-upgrade-downgrade.md)
- **autogenerate: 잡는 것과 못 잡는 것의 경계 (현재 글)**
- branch와 merge: 동시에 만든 revision을 합치는 법 (예정)
- 데이터 마이그레이션: schema 변경과 데이터 변경을 분리하기 (예정)
- online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기 (예정)
- downgrade 전략: 언제 진심으로 작성하고 언제 막을 것인가 (예정)
- 배포 순서와 blue/green: schema와 application code의 안전한 동기화 (예정)
- Production과 team workflow: PR, CI, 모니터링, 그리고 incident response (예정)

<!-- toc:end -->

## 참고 자료

- [sqlalchemy/alembic GitHub 저장소](https://github.com/sqlalchemy/alembic)
- [Alembic: Auto Generating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- [Alembic: Comparing Types](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#comparing-types)
- [Alembic: Comparing Server Defaults](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#comparing-server-defaults)
- [Alembic: Limitations of Autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect)

Tags: Python, Alembic, SQLAlchemy, Migration
