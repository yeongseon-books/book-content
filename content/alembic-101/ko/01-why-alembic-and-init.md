---
title: "Alembic 101 (1/10): 왜 Alembic인가, 그리고 init까지"
series: alembic-101
episode: 1
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
- SQLAlchemy
- Migration
- SQLite
last_reviewed: '2026-05-12'
seo_description: Alembic은 DB 스키마를 위한 git입니다. 각 마이그레이션 파일은 commit이고, alembic_version
  테이블은 현재…
---

# Alembic 101 (1/10): 왜 Alembic인가, 그리고 init까지

이 글은 Alembic 101 시리즈의 첫 번째 글입니다. 여기서는 raw SQL 파일만으로는 왜 스키마 변경 이력이 금방 통제 불가능해지는지, 그리고 `alembic init`이 실제로 무엇을 준비하는지 정리합니다.

Alembic을 처음 접하면 명령어보다 먼저 이런 의문이 생깁니다. “SQL 파일 몇 개 잘 관리하면 되지 않을까?” 문제는 스키마 변경 이력이 revision history가 아니라 사람 기억에 기대는 순간 시작됩니다. 그때부터 배포와 롤백은 재현 가능한 절차가 아니라 추측이 됩니다.

## 먼저 던지는 질문

- 마이그레이션 도구가 실제로 해결하는 문제는 무엇일까요?
- 왜 `Base.metadata.create_all`만으로는 운영 환경을 버틸 수 없을까요?
- revision, head, `alembic_version` 테이블은 각각 어떤 역할을 할까요?

## 큰 그림

![Alembic 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/alembic-101/01/01-01-diagram-how-revision-history-reaches-the.ko.png)

*Alembic 101 1장 흐름 개요*

## 왜 중요한가

스키마 변경은 production 사고의 단골 원인입니다. 코드는 git으로, 인프라는 Terraform으로 관리하면서도 “누가 어떤 SQL을 어느 환경에 실행했는가”만 수작업으로 남기는 팀이 의외로 많습니다. 그러면 staging은 조용히 production과 어긋나고, 문제가 생겼을 때도 스키마를 어디까지 되돌려야 하는지 누구도 자신 있게 말하지 못합니다.

Alembic은 SQLAlchemy 작성자가 만든 마이그레이션 도구이고, 이 문제를 git이 코드 변경을 다루는 방식으로 풀어냅니다. 각 변경은 revision이고, head는 최신 상태이며, 모든 환경은 같은 이력을 따라 올라가거나 내려옵니다. 이 글에서는 그 출발점인 “왜 필요한가”와 “어떻게 시작하는가”를 잡겠습니다.

## 멘탈 모델

> Alembic은 **DB 스키마를 위한 git**입니다. 각 마이그레이션 파일은 commit이고, `alembic_version` 테이블은 현재 HEAD 포인터이며, `upgrade head`는 fast-forward이고, `downgrade -1`은 한 단계 reset에 가깝습니다.

이 비유를 받아들이면 거의 모든 명령이 자연스럽게 읽힙니다. `revision`은 새 commit을 만드는 일이고, `merge`는 두 head를 화해시키는 일이며, `stamp`는 working tree를 건드리지 않고 HEAD만 옮기는 `git reset`과 비슷합니다.

### 다이어그램: revision 이력이 DB에 적용되는 흐름

## 핵심 개념

### Revision과 head

각 마이그레이션 파일은 고유한 `revision` ID와 부모를 가리키는 `down_revision`을 가집니다. revision들은 방향성이 있는 그래프를 이루고, 자식이 없는 leaf node가 `head`입니다. 보통은 head가 하나지만, branch가 생기면 둘 이상이 될 수 있습니다.

### `alembic_version` 테이블

Alembic은 DB 안에 `alembic_version`이라는 한 줄짜리 메타 테이블을 만듭니다. 이 값은 “이 데이터베이스가 현재 어느 revision 위에 있는가”를 뜻합니다. Alembic의 모든 명령은 이 값을 읽고 revision graph와 비교해 다음 행동을 결정합니다.

### `create_all`과의 차이

| 항목 | `Base.metadata.create_all` | Alembic |
| --- | --- | --- |
| 용도 | 테스트, 초기 프로토타입 | 운영 환경 관리 |
| 변경 추적 | 없음 | revision graph |
| 컬럼 변경/삭제 | 불가 | 가능 |
| 환경 간 동기화 | 없음 | 같은 history |
| 롤백 | 없음 | `downgrade` 명령 |

`create_all`은 “없는 테이블을 만든다”가 전부입니다. 컬럼 하나가 추가돼도 production에 그 변경을 전달해 주지 않습니다.

### `alembic init`이 만드는 것

```text
project/
├── alembic.ini           # global config (DB URL, logging, file template)
└── alembic/
    ├── env.py            # migration runtime context
    ├── script.py.mako    # revision file template
    └── versions/         # the actual migration files
```

실제로 자주 만지는 파일은 `env.py`(다음 글)와 `versions/` 아래의 revision 파일들입니다.

## 변경 전후

```bash
# Before: hand-running SQL on production
psql -h prod -U app -d main -c "ALTER TABLE users ADD COLUMN tier VARCHAR(16) NOT NULL DEFAULT 'free';"
# Nobody can reconstruct who, when, on which environment, after the fact
```

```bash
# After: the revision file IS the change log
alembic revision -m "add users.tier"
# alembic/versions/3f9c..._add_users_tier.py is created
# Code review, environment sync, rollback all become possible
alembic upgrade head
```

After 쪽은 `git diff`에 잡히고, PR 리뷰 대상이 되며, staging과 production이 같은 명령으로 같은 상태에 도달하게 만듭니다.

## 단계별 실습

### 1단계: 설치

```bash
mkdir alembic-demo && cd alembic-demo
python3 -m venv .venv && source .venv/bin/activate
pip install "sqlalchemy>=2.0" "alembic>=1.13"
```

### 2단계: 모델 정의

```python
# app/models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    name: Mapped[str]
```

### 3단계: `alembic init`

```bash
alembic init alembic
```

그러면 다음 구조가 생깁니다.

```text
alembic-demo/
├── alembic.ini
└── alembic/
    ├── env.py
    ├── script.py.mako
    └── versions/
```

### 4단계: SQLite URL 연결

`alembic.ini`에서 다음 줄을 찾습니다.

```ini
sqlalchemy.url = sqlite:///./app.db
```

다음 글에서는 `os.environ["DATABASE_URL"]`로 읽는 더 안전한 패턴을 다루지만, 여기서는 이 정도 설정으로 충분합니다.

### 5단계: 첫 빈 revision 생성

```bash
alembic revision -m "init"
```

그러면 `alembic/versions/<hash>_init.py`가 생성되고, 안에는 비어 있는 `upgrade()`와 `downgrade()`가 들어 있습니다. 이것이 첫 commit입니다.

### 6단계: upgrade 후 version 테이블 확인

```bash
alembic upgrade head
sqlite3 app.db "SELECT * FROM alembic_version;"
# result: <hash>
```

`alembic_version`에 한 줄이 보이는 순간 모델이 한 번에 잡힙니다. 이 테이블이 모든 마이그레이션 명령의 기준점입니다.

## 검증 루틴

```bash
alembic history
alembic current
sqlite3 app.db "SELECT version_num FROM alembic_version;"
```

**확인할 점:** `alembic history`에는 방금 만든 revision이 보이고, `alembic current`와 `alembic_version` 조회 결과는 같은 hash를 가리켜야 합니다.

## 자주 하는 실수

- **`create_all`로 production을 시작하기.** 나중에 Alembic을 도입하려면 현재 스키마를 baseline revision으로 찍어 두는 stamping 단계가 추가됩니다. 가능하면 첫날부터 Alembic을 씁니다.
- **`alembic.ini`에 production credential을 하드코딩하기.** 다음 글의 환경 변수 override 패턴을 표준처럼 생각하는 편이 안전합니다.
- **`alembic_version`을 손으로 수정하기.** 가능은 하지만 거의 항상 사고로 이어집니다. `alembic stamp`를 사용하세요.
- **push한 revision 파일을 다시 수정하기.** revision ID는 이력의 일부입니다. 이미 다른 환경에 적용됐다면 기존 파일을 바꾸지 말고 새 revision으로 고칩니다.
- **여러 사람이 동시에 `revision -m`을 실행하기.** branch가 생깁니다. 5편에서 `merge`로 정리하지만, 가장 좋은 방법은 PR 머지 직전에 정리하는 것입니다.

## 실무 패턴

- **revision 파일은 코드와 같은 PR에 넣습니다.** 기능 코드, 마이그레이션, 테스트가 함께 움직여야 합니다.
- **CI에서 `alembic upgrade head --sql`을 출력합니다.** 사람이 DDL을 한 번만 읽어도 의외로 많은 사고를 막습니다.
- **파일명 템플릿을 의미 있게 바꿉니다.** `file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(slug)s`처럼 두면 파일이 시간순으로 정렬됩니다.
- **가능하면 single head를 유지합니다.** 대부분 팀에는 branch보다 head 하나가 더 단순합니다.
- **첫 revision은 baseline입니다.** 기존 DB에 Alembic을 도입한다면 `alembic revision --autogenerate -m "baseline"` 후 `alembic stamp head`로 현재 상태를 맞춥니다.

## 체크리스트

- [ ] `alembic init` 뒤에 `alembic.ini`, `env.py`, `versions/`를 구분할 수 있다
- [ ] `sqlalchemy.url`이 올바른 데이터베이스를 가리킨다 (이 시리즈에서는 SQLite)
- [ ] 첫 빈 revision을 만들고 `upgrade head` 후 `alembic_version`이 생기는 것을 확인했다
- [ ] `create_all`은 테스트용이고, 운영 환경은 Alembic으로만 관리한다는 원칙이 분명하다
- [ ] revision 파일을 git에 커밋하고 PR에서 리뷰한다
- [ ] credential은 `alembic.ini` 평문이 아니라 환경 변수에서 읽는다 (다음 글에서 구현)

## 연습 문제

1. 위 단계를 SQLite와 `alembic init`으로 그대로 따라 하고, `alembic_version` 테이블이 생기는지 확인해 보세요.
2. `alembic history`와 `alembic current`를 실행해 출력 차이를 비교해 보세요.
3. `alembic downgrade base`를 실행한 뒤 `alembic_version` 테이블이 어떻게 바뀌는지 확인해 보세요.

## 정리, 다음 글

Alembic은 결국 “DB 스키마를 위한 git”이라는 한 줄로 요약됩니다. revision, head, version table만 머릿속에 자리 잡으면 나머지는 명령을 익히는 문제에 가깝습니다.

다음 글에서는 `env.py`를 열어 봅니다. 모델 metadata를 어떻게 연결하는지, DB URL을 환경 변수에서 어떻게 안전하게 읽는지, online과 offline 모드는 실제로 무엇을 뜻하는지 정리합니다.

## 팀 합류 시점에 바로 쓰는 점검 질문

Alembic을 이미 쓰는 프로젝트에 합류했을 때는 명령어를 외우기 전에 "이 팀이 어떤 원칙으로 이력을 관리하는지"부터 확인하는 편이 좋습니다. 아래 질문은 온보딩 초기에 바로 써먹을 수 있는 최소 점검 목록입니다.

1. **revision 생성 시점이 언제인지** 확인합니다. 기능 개발 중간인지, PR 머지 직전인지에 따라 충돌 빈도가 크게 달라집니다.
2. **downgrade 정책이 있는지** 확인합니다. 모든 revision에 downgrade를 요구하는지, 특정 환경에서는 차단하는지 명시가 필요합니다.
3. **배포 파이프라인에서 migration 실행 주체가 누구인지** 확인합니다. 앱 시작 시 자동 실행인지, 별도 release job인지에 따라 롤백 전략이 달라집니다.
4. **장애 시 복구 절차 문서가 있는지** 확인합니다. `alembic current`, `history`, DB 백업 시점 확인 같은 기본 절차가 문서화돼 있어야 합니다.

이 질문이 중요한 이유는, Alembic 자체보다 운영 방식이 사고를 더 많이 좌우하기 때문입니다. 같은 도구를 써도 팀 규칙이 모호하면 head 충돌, 누락 배포, 복구 지연이 반복됩니다. 반대로 원칙이 분명하면 revision 파일은 자연스럽게 코드 리뷰 대상이 되고, 데이터베이스 변경도 애플리케이션 코드와 같은 품질 기준으로 관리할 수 있습니다.

추가로, 첫 주에는 의도적으로 작은 스키마 변경 하나를 만들어 `revision -> upgrade -> 확인 -> downgrade`까지 한 번 왕복해 보는 것이 좋습니다. 문서로 이해한 흐름과 실제 팀 파이프라인이 일치하는지 확인할 수 있고, 비상시에 어떤 명령을 어디서 실행해야 하는지도 몸에 익힐 수 있습니다.

## 현장에서 바로 쓰는 baseline 도입 시나리오

기존 서비스에 Alembic을 나중에 도입할 때는 `init` 자체보다 baseline 전략이 더 중요합니다. 이미 운영 중인 스키마가 있는데도 무심코 `upgrade head`를 실행하면, Alembic은 "아무것도 적용되지 않은 DB"로 판단하고 처음 revision부터 모두 실행하려고 시도합니다. 이때 가장 흔한 실패가 "이미 존재하는 테이블 생성" 오류입니다.

아래 순서가 실무에서 안전합니다.

```bash
# 1) 운영 DB를 직접 건드리지 않고 스냅샷으로 검증
pg_dump -s "$DATABASE_URL" > schema-before-alembic.sql

# 2) 현재 모델 기준 baseline revision 생성
alembic revision --autogenerate -m "baseline current production schema"

# 3) 생성 파일 검토: 절대 DROP/ALTER이 섞이면 안 됨
git diff -- alembic/versions

# 4) 운영 DB에는 DDL 실행 대신 stamp만 수행
alembic stamp head

# 5) 버전 포인터 확인
alembic current
```

핵심은 4단계입니다. baseline 단계에서 필요한 것은 스키마 변경이 아니라 "이 DB는 이미 이 revision 상태다"라는 선언입니다. 그래서 `upgrade`가 아니라 `stamp`를 씁니다. 이 원칙이 없으면 도입 첫날부터 운영 DB를 불필요하게 흔들게 됩니다.

## revision 파일 품질을 올리는 최소 리뷰 기준

`alembic revision -m "..."`으로 파일이 생성되면 아래 다섯 항목만은 반드시 확인하는 편이 좋습니다.

1. `revision`, `down_revision`이 의도한 그래프를 만드는가
2. `upgrade`에서 생성한 객체를 `downgrade`에서 정확히 역순으로 제거하는가
3. `server_default`와 ORM `default`를 혼동하지 않았는가
4. SQLite라면 `batch_alter_table`이 필요한 연산인지 확인했는가
5. data migration이 섞였다면 idempotent `WHERE` 조건이 있는가

아래처럼 아주 작은 템플릿을 팀 위키에 두면 리뷰 밀도가 올라갑니다.

```text
[Migration Review]
- graph: single head / intended branch
- DDL safety: no accidental drop
- downgrade: exact inverse or explicit irreversible
- data step: idempotent + bounded batch
- deploy note: expand / migrate / contract phase
```

이 체크리스트는 복잡한 규칙이 아니라 "사고가 자주 나는 지점"만 모아 둔 것입니다. 특히 `down_revision` 오타와 `downgrade` 누락은 작은 실수처럼 보여도 배포 파이프라인 전체를 멈추게 만듭니다.

## 오류 시그널과 즉시 대응

초기 도입 단계에서 자주 만나는 에러는 대체로 몇 가지로 수렴합니다.

```text
sqlalchemy.exc.OperationalError: table users already exists
-> baseline이 필요한 DB에 upgrade를 실행했을 가능성

FAILED: Can't locate revision identified by 'abc123...'
-> 누락된 revision 파일 또는 잘못된 down_revision 체인

FAILED: Multiple head revisions are present
-> 병렬 revision이 merge 없이 main에 합쳐진 상태
```

첫 번째 에러는 `stamp`로 경로를 되돌리는 문제이고, 두 번째는 revision 파일 자체가 손실되었는지부터 확인해야 합니다. 세 번째는 기능 결함이 아니라 그래프 정리 문제이므로 `alembic merge`로 해결합니다. 에러를 유형별로 분리해서 대응하면 복구 시간이 크게 줄어듭니다.

## schema 전후 비교 예시

Alembic 도입 전후로 팀이 얻는 것은 "DDL 실행 기능"보다 "재현 가능한 이력"입니다. 아래 예시는 같은 변경을 두 방식으로 처리했을 때의 차이를 보여 줍니다.

```sql
-- Before (수동 SQL)
ALTER TABLE users ADD COLUMN tier VARCHAR(16) NOT NULL DEFAULT 'free';
CREATE INDEX ix_users_tier ON users(tier);
```

```python
# After (revision 파일)
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(16), nullable=False, server_default="free"))
    op.create_index("ix_users_tier", "users", ["tier"])

def downgrade() -> None:
    op.drop_index("ix_users_tier", table_name="users")
    op.drop_column("users", "tier")
```

수동 SQL은 실행 당시에는 빠르지만 시간이 지나면 "누가, 왜, 어떤 순서로"를 잃습니다. revision 파일은 변경의 의도와 복구 경로를 코드로 남깁니다. Alembic을 도입하는 이유를 한 줄로 줄이면 결국 이 차이입니다.


## 실전 부록: 운영 앵커 모음

아래 블록은 migration 리뷰와 배포 검증에서 반복해서 쓰는 공통 앵커입니다.

### 1) DDL 미리 보기

```bash
alembic upgrade <from>:<to> --sql > migration-preview.sql
```

리뷰 시점에서 실제 SQL을 확인하면 `DROP`, `ALTER`, 인덱스 재생성 비용을 사전에 파악할 수 있습니다.

### 2) revision 그래프 확인

```bash
alembic history --verbose
alembic heads
alembic current
```

`heads`가 2개 이상이면 기능 결함이 아니라 그래프 정리 이슈입니다. merge revision으로 정리한 뒤 배포해야 안전합니다.

### 3) schema 전후 비교

```bash
sqlite3 app.db ".schema" > before.sql
alembic upgrade head
sqlite3 app.db ".schema" > after.sql
```

변경 의도와 실제 결과를 텍스트로 남기면 코드 리뷰 품질이 올라갑니다.

### 4) data migration 검증 쿼리

```sql
SELECT COUNT(*) FROM users WHERE tier IS NULL;
SELECT tier, COUNT(*) FROM users GROUP BY tier ORDER BY tier;
```

`NULL` 잔여 수와 분포를 함께 보면 backfill 완료 여부를 빠르게 판단할 수 있습니다.

### 5) env.py 핵심 설정

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    compare_type=True,
    compare_server_default=True,
    render_as_batch=connection.dialect.name == "sqlite",
)
```

type/default 비교 옵션과 SQLite batch 옵션은 drift 탐지와 호환성 유지에 직접적인 영향을 줍니다.

### 6) blue/green 배포 게이트

```text
Gate A: expand 적용 후 v1 정상
Gate B: v2 배포 후 overlap 정상
Gate C: NULL row 0 확인 후 tighten
Gate D: 구 컬럼 사용 중단 확인 후 contract
```

게이트를 코드화하면 배포 순서 실수를 줄일 수 있습니다.

### 7) 비가역 변경 정책

```python
def downgrade() -> None:
    raise NotImplementedError("irreversible revision by policy")
```

비가역 변경에서 침묵하는 `pass`보다 명시적 예외가 훨씬 안전합니다.

### 8) CI 최소 게이트

```bash
alembic check
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

drift, downgrade 결함, 체인 무결성을 PR 단계에서 차단할 수 있습니다.

### 9) 에러 시그널 해석

```text
Multiple head revisions are present -> merge 필요
Can't locate revision identified by ... -> revision chain 점검 필요
table already exists -> baseline/stamp 전략 점검 필요
```

에러 유형별 대응 경로를 정해 두면 incident 대응 시간이 짧아집니다.

### 10) 팀 운영 원칙

```text
- one PR = one revision
- migration-first deploy
- expand-contract 기본 적용
- production 사고는 forward-fix 우선
```

원칙을 문서가 아니라 PR 템플릿과 CI로 강제하는 것이 핵심입니다.



## 확장 부록: 배포/복구 실습 시나리오

### 시나리오 A: add column + backfill + tighten

```bash
alembic revision -m "add users.phone nullable"
alembic revision -m "backfill users.phone"
alembic revision -m "tighten users.phone not null"
alembic upgrade head
```

```sql
SELECT COUNT(*) FROM users WHERE phone IS NULL;
```

`COUNT(*) = 0`이 아니라면 tighten 단계는 멈춰야 합니다.

### 시나리오 B: 동시에 생성된 head 정리

```bash
alembic heads
alembic merge -m "merge concurrent heads" <head1> <head2>
alembic heads
```

merge 후 head가 하나여야 합니다.

### 시나리오 C: offline SQL 승인 흐름

```bash
alembic upgrade <prev>:head --sql > review.sql
```

검토 포인트는 `DROP`, `ALTER`, 인덱스 재생성, `alembic_version` 갱신 SQL 포함 여부입니다.

### 시나리오 D: incident first checks

```bash
alembic current
alembic heads
```

```sql
SELECT version_num FROM alembic_version;
```

애플리케이션 `/health`의 기대 버전과 DB 버전이 다르면 drift 가능성을 먼저 의심합니다.

### 운영 스크립트 예시

```bash
set -euo pipefail
alembic check
alembic upgrade head
alembic upgrade head --sql > /tmp/migration-preview.sql
```

### 품질 게이트 정리

```text
- autogenerate 결과 수동 검토
- downgrade 정책 명시
- data migration idempotency 확보
- migration-first 배포
- post-deploy smoke test
```

이 게이트들은 Alembic 자체 기능이라기보다 팀 운영 안전장치입니다.



## 보강 메모: 검증 중심 운영 노트

Alembic 운영에서 가장 큰 차이는 "명령 실행"이 아니라 "검증 기록"입니다. 같은 `upgrade head`를 실행해도 검증 쿼리, SQL preview, head 개수 확인을 함께 남기면 문제 재현성이 크게 높아집니다.

```bash
alembic heads
alembic current
alembic upgrade head --sql > /tmp/ddl.sql
```

```sql
SELECT version_num FROM alembic_version;
```

또한 data migration이 포함된 경우에는 진행률을 관찰 가능한 숫자로 남겨야 합니다.

```sql
SELECT COUNT(*) FROM users WHERE tier IS NULL;
```

운영자는 이 숫자를 기준으로 tighten 단계 진행 여부를 결정해야 합니다. 값이 0이 아니면 단계 진행을 멈추고 backfill을 계속해야 합니다.

배포 실패 대응의 기본 원칙은 다음과 같습니다.

```text
1) 현재 revision 위치를 먼저 확정한다.
2) graph 상태(single head인지)를 확인한다.
3) backward-compatible 여부를 판단한다.
4) 가능하면 forward-fix revision으로 복구한다.
```

이 네 단계는 엔진(SQLite/PostgreSQL)과 무관하게 공통으로 적용됩니다.


## 처음 질문으로 돌아가기

- **마이그레이션 도구가 실제로 해결하는 문제는 무엇일까요?**
  - 본문의 기준은 왜 Alembic인가, 그리고 init까지를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **왜 `Base.metadata.create_all`만으로는 운영 환경을 버틸 수 없을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **revision, head, `alembic_version` 테이블은 각각 어떤 역할을 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **왜 Alembic인가, 그리고 init까지 (현재 글)**
- env.py와 target_metadata: 모델과 마이그레이션 연결 (예정)
- 첫 revision: upgrade와 downgrade를 손으로 작성 (예정)
- autogenerate: 잡는 것과 못 잡는 것의 경계 (예정)
- branch와 merge: 동시에 만든 revision을 합치는 법 (예정)
- 데이터 마이그레이션: schema 변경과 데이터 변경을 분리하기 (예정)
- online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기 (예정)
- downgrade 전략: 언제 진심으로 작성하고 언제 막을 것인가 (예정)
- 배포 순서와 blue/green: schema와 application code의 안전한 동기화 (예정)
- Production과 team workflow: PR, CI, 모니터링, 그리고 incident response (예정)

<!-- toc:end -->

## 참고 자료

- [sqlalchemy/alembic GitHub 저장소](https://github.com/sqlalchemy/alembic)
- [Alembic: Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Alembic: Configuration](https://alembic.sqlalchemy.org/en/latest/config.html)
- [SQLAlchemy: MetaData](https://docs.sqlalchemy.org/en/20/core/metadata.html)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/alembic-101/ko/01-why-alembic-and-init)

Tags: Python, Alembic, SQLAlchemy, Migration
