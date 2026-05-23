---
title: "Alembic 101 (2/10): env.py와 target_metadata: 모델과 마이그레이션 연결"
series: alembic-101
episode: 2
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
- env.py
- target_metadata
- Configuration
- SQLite
last_reviewed: '2026-05-12'
seo_description: Alembic의 부트 스크립트인 env.py 설정법과 target_metadata를 통한 모델 연결, 환경 변수 활용 패턴을 정리합니다.
---

# Alembic 101 (2/10): env.py와 target_metadata: 모델과 마이그레이션 연결

이 글은 Alembic 101 시리즈의 두 번째 글입니다. 여기서는 `env.py`가 Alembic 실행 흐름에서 정확히 어떤 위치를 차지하는지, 그리고 `target_metadata`가 autogenerate의 근거로서 무엇을 제공해야 하는지 실무 관점에서 정리합니다.

1편에서 `alembic init`까지 마쳤더라도 그 상태의 Alembic은 여러분 모델을 모릅니다. 이 연결을 `env.py`에서 제대로 하지 못하면 `alembic revision --autogenerate`는 즉시 신뢰를 잃습니다.

![Alembic 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/alembic-101/02/02-01-diagram-where-env-py-assembles-metadata.ko.png)
*Alembic 101 2장 흐름 개요*

## 먼저 던지는 질문

- `env.py`는 정확히 무엇이고 언제 실행될까요?
- 왜 `target_metadata`는 선택 사항이 아니라 필수일까요?
- DB URL을 환경 변수에서 안전하게 읽는 패턴은 어떻게 만들까요?

## 왜 중요한가

1편의 scaffold 상태에서 Alembic은 아직 모델 metadata의 위치를 모릅니다. 그래서 `alembic revision --autogenerate`를 실행해도 빈 파일이 나옵니다. `env.py`에 모델 metadata를 알려 주는 한 줄이 없으면, Alembic은 live DB schema와 무엇을 비교해야 하는지조차 알 수 없습니다.

또 하나의 문제는 URL입니다. `alembic.ini`에 staging이나 production용 DB URL을 평문으로 두면 credential이 그대로 git에 남습니다. 이 글에서는 `env.py`를 열어 보고, metadata 연결과 URL 처리라는 두 문제를 함께 해결하겠습니다.

## 멘탈 모델

> `env.py`는 Alembic이 **모든 명령마다 실행하는 부트 스크립트**입니다. 각 실행(`upgrade`, `revision --autogenerate` 등)에서 Alembic은 (1) `alembic.ini`를 읽고, (2) `env.py`를 실행해 connection과 metadata를 얻고, (3) `versions/` 아래의 revision을 적용합니다.

여기서 가장 중요한 사실은 매번 실행된다는 점입니다. 환경 변수도 매번 다시 읽히고, 모델 import도 매번 일어납니다. 이 흐름을 받아들이면 `env.py`의 책임이 훨씬 또렷해집니다.

### 다이어그램: `env.py`가 metadata와 연결을 조립하는 위치

## 핵심 개념

### `env.py` 안의 두 함수

기본 `env.py`는 보통 두 함수를 정의합니다.

- `run_migrations_online()` — 실제 DB 연결을 열고 마이그레이션을 적용합니다
- `run_migrations_offline()` — 연결 없이 SQL만 출력합니다

파일 맨 아래에서는 `if context.is_offline_mode(): ... else: ...` 분기로 둘 중 하나를 호출합니다.

### `target_metadata`

```python
from app.models import Base
target_metadata = Base.metadata
```

이 한 줄이 autogenerate의 근거입니다. Alembic은 connection을 통해 live DB를 introspect하고, 그 결과를 `target_metadata`와 비교해 diff를 revision 파일에 씁니다. `target_metadata = None`이면 autogenerate는 조용히 아무 일도 하지 않습니다.

### online과 offline

| 모드 | 명령 | 쓰임 |
| --- | --- | --- |
| Online | `alembic upgrade head` | DB에 직접 적용 |
| Offline | `alembic upgrade head --sql > out.sql` | SQL만 출력하고 DBA가 수동 적용 |

offline 모드는 production DB 직접 접근이 제한된 환경에서 자주 씁니다.

### URL 우선순위

Alembic은 기본적으로 `alembic.ini`의 `sqlalchemy.url`을 읽지만, `env.py`에서 `config.set_main_option("sqlalchemy.url", ...)`로 덮어쓸 수 있습니다. 환경 변수 패턴은 바로 이 override를 이용합니다.

## 변경 전후

```python
# 이전: 스캐폴드 기본값(자동 생성으로 빈 파일 생성)
from alembic import context
config = context.config
target_metadata = None  # ← leaving this empty disables autogenerate

def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section), ...)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

```python
# 이후: 모델 연결, 환경의 URL
import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from app.models import Base   # ← import the model

config = context.config

# DATABASE_URL이 환경에 맞는 경우 alembic.ini를 재정의합니다.
db_url = os.environ.get("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata   # ← basis for autogenerate

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=url.startswith("sqlite"),  # SQLite-only batch mode
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

After 버전은 (1) 모델을 알기 때문에 autogenerate가 동작하고, (2) production credential을 환경 변수에서 읽어 git을 안전하게 유지하며, (3) SQLite의 ALTER 제약을 우회하기 위해 batch mode를 자동으로 켭니다.

## 단계별 실습

### 1단계: 모델 import가 실제로 되는지 확인

`env.py`는 보통 project root에서 `alembic` 명령을 실행할 때 import됩니다. 따라서 `from app.models import Base`가 바로 동작하도록 패키지 구조를 잡거나, 필요하면 project root를 `sys.path`에 직접 넣습니다.

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from app.models import Base
```

### 2단계: `target_metadata` 설정

```python
target_metadata = Base.metadata
```

`Base`가 여러 개라면 각 `MetaData`를 합쳐야 합니다.

```python
from sqlalchemy import MetaData
combined = MetaData()
for m in [Base.metadata, OtherBase.metadata]:
    for t in m.tables.values():
        t.tometadata(combined)
target_metadata = combined
```

### 3단계: 환경 변수로 URL override

```python
import os
db_url = os.environ.get("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)
```

`alembic.ini`에는 local SQLite 같은 안전한 기본값만 두고, staging과 production은 환경 변수로 주입하는 편이 좋습니다.

### 4단계: SQLite용 `render_as_batch`

SQLite는 컬럼 삭제, 타입 변경, nullable 변경 같은 `ALTER TABLE` 지원이 매우 약합니다. Alembic의 batch mode는 임시 테이블을 만들고, 데이터를 복사하고, 원본을 바꾸는 방식으로 이를 우회합니다. SQLite를 쓴다면 거의 항상 켜 두는 편이 맞습니다.

### 5단계: autogenerate 검증

```bash
# Add a column to the model
# class User(Base):
#     ...
#     tier: Mapped[str] = mapped_column(default="free")

alembic revision --autogenerate -m "add users.tier"
```

`versions/<hash>_add_users_tier.py` 안에 `op.add_column(...)`이 생성됐다면 metadata 연결이 제대로 된 것입니다.

### 6단계: offline SQL 미리 보기

```bash
alembic upgrade head --sql
```

이 명령은 connection 없이 DDL을 출력합니다. 많은 팀이 이 출력을 CI 산출물로 남기고 PR 본문에 붙입니다. SQL을 사람 눈으로 읽는 과정 자체가 꽤 강한 안전 장치입니다.

## 검증 루틴

```bash
alembic revision --autogenerate -m "probe metadata wiring"
python3 - <<'PY'
from pathlib import Path
latest = sorted(Path("alembic/versions").glob("*_probe_metadata_wiring.py"))[-1]
print(latest.read_text())
PY
```

**확인할 점:** 생성된 revision 안에 `op.add_column(...)` 같은 실제 diff가 들어 있어야 합니다. 파일이 비어 있으면 `target_metadata` 연결부터 다시 봐야 합니다.

## 자주 하는 실수

- **`target_metadata = None`을 그대로 두기.** autogenerate가 빈 파일만 만듭니다. 가장 먼저 확인해야 할 지점입니다.
- **모델 import는 했는데 결과가 비어 있기.** 모델 모듈이 실제로 로드되지 않으면 `Base.metadata`는 비어 있습니다. `__init__.py`에서 모든 모델을 명시적으로 import하거나 `env.py`에서 직접 import하세요.
- **SQLite에서 `render_as_batch` 없이 컬럼 drop을 시도하기.** 지원되지 않는 ALTER 에러를 만나게 됩니다.
- **`alembic.ini`에 production URL을 그대로 커밋하기.** 환경 변수 override 패턴을 사실상 표준으로 보세요.
- **기본 pool 설정을 그대로 두기.** Alembic 명령은 보통 one-shot이므로 `poolclass=pool.NullPool`이 더 적절합니다.

## 실무 패턴

- **`env.py`는 한 번 제대로 만들면 오래 갑니다.** 보통 필요한 것은 모델 import, env-var URL, batch mode 정도입니다.
- **모든 환경에서 같은 `env.py`를 씁니다.** 차이는 코드가 아니라 환경 변수에서 흡수하는 편이 단순합니다.
- **`compare_type=True`, `compare_server_default=True`를 켭니다.** 다음 글의 autogenerate에서 타입과 default 변경까지 잡기 위해서입니다.
- **`include_object` hook으로 특정 테이블을 제외합니다.** 외부 시스템이 관리하는 테이블이 있을 때 유용합니다.
- **async 앱이어도 Alembic은 sync engine으로 돌리는 경우가 많습니다.** 정말 async가 필요할 때만 `connectable.run_sync(...)` 패턴을 검토하세요.

## 체크리스트

- [ ] `from app.models import Base` 또는 동등한 import가 `env.py` 상단에서 실제로 동작한다
- [ ] `target_metadata = Base.metadata`가 명시돼 있다
- [ ] `DATABASE_URL` 환경 변수로 URL을 override할 수 있다
- [ ] SQLite를 쓴다면 `render_as_batch=True`가 `context.configure(...)`에 들어 있다
- [ ] `alembic.ini`에는 안전한 기본값(local SQLite)만 있다
- [ ] `alembic revision --autogenerate`가 빈 파일이 아니라 실제 diff를 만든다
- [ ] `alembic upgrade head --sql`로 offline DDL을 출력할 수 있다

## 연습 문제

1. `target_metadata = None`으로 둔 채 `alembic revision --autogenerate`를 실행해 보고, 결과 파일이 비는지 확인해 보세요.
2. `DATABASE_URL`을 두 개의 서로 다른 SQLite 파일로 번갈아 지정해 같은 migration을 둘 다에 적용해 보세요.
3. `render_as_batch`를 끈 상태에서 SQLite 컬럼 삭제 migration을 시도해 오류를 재현해 보세요.

## 정리, 다음 글

`env.py`는 Alembic의 부트 스크립트이고, 실제로 핵심은 두 가지입니다. `target_metadata`를 올바르게 연결하는 일과 URL을 환경 변수에서 안전하게 읽는 일입니다. SQLite를 쓴다면 여기에 `render_as_batch`까지 더하면 됩니다.

다음 글에서는 첫 의미 있는 revision을 손으로 작성해 봅니다. `op.create_table`, `op.add_column`, `op.execute`를 중심으로 수동 작성과 autogenerate 결과를 비교하고, `upgrade`와 `downgrade`를 대칭으로 유지하는 법을 다룹니다.

## env.py 실전 구성 패턴

`env.py`는 한 번만 잘 만들어 두면 이후 모든 revision 품질을 끌어올립니다. 팀에서 많이 쓰는 패턴은 "환경 분기 최소화 + 비교 옵션 명시 + 로깅 보강"입니다.

```python
from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
import os

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

db_url = os.environ.get("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

from app.models import Base
target_metadata = Base.metadata

def include_object(obj, name, type_, reflected, compare_to):
    if type_ == "table" and name.startswith("legacy_"):
        return False
    return True
```

`include_object` 같은 hook을 초기에 넣어 두면 외부 시스템 테이블이 autogenerate diff를 오염시키는 문제를 줄일 수 있습니다. 특히 모놀리식 DB에서 여러 서비스가 테이블을 공유하는 환경이라면 거의 필수에 가깝습니다.

## target_metadata 누락을 빠르게 찾는 진단 루틴

`autogenerate` 결과가 비어 있을 때는 감으로 고치지 말고 순서대로 좁혀 가는 편이 좋습니다.

```bash
# 1) env.py import 자체가 성공하는지
python3 - <<'PY'
from alembic.config import Config
from alembic import command
cfg = Config("alembic.ini")
print("Pass: config loaded")
PY

# 2) metadata에 실제 테이블이 올라왔는지
python3 - <<'PY'
from app.models import Base
print(sorted(Base.metadata.tables.keys()))
PY

# 3) autogenerate probe
alembic revision --autogenerate -m "probe metadata"
```

2단계 출력이 빈 배열이면 Alembic 문제가 아니라 모델 import 경로 문제입니다. 이때는 `env.py` 수정보다 애플리케이션 패키지 구조를 먼저 점검해야 합니다.

## offline/online에서 같은 정책을 유지하는 방법

운영에서 흔한 실수는 online 설정과 offline 설정이 조금씩 달라지는 것입니다. 예를 들어 online에는 `compare_type=True`를 켜 두고 offline에는 빼 두면 PR 리뷰 SQL과 실제 적용 SQL의 의미가 어긋납니다. 아래처럼 `configure` 인자를 함수로 묶어 두면 일관성이 좋아집니다.

```python
def common_config_kwargs(url_or_conn):
    return {
        "target_metadata": target_metadata,
        "compare_type": True,
        "compare_server_default": True,
        "include_object": include_object,
        "render_as_batch": True if isinstance(url_or_conn, str) and url_or_conn.startswith("sqlite") else False,
    }
```

핵심은 "모드가 달라도 비교 기준은 같다"입니다. 모드 차이는 연결 유무여야지, diff 정책 차이가 되어서는 안 됩니다.

## 에러 시나리오: env.py 설정 불일치

실무에서 자주 보는 로그는 다음과 같습니다.

```text
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
FAILED: Can't proceed with --autogenerate option; environment script ... does not provide a MetaData object
```

이 메시지는 거의 항상 `target_metadata` 누락입니다. 반면 아래 로그는 URL 오버라이드 문제 신호입니다.

```text
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file
```

이 경우 `DATABASE_URL` 값이 잘못됐거나 상대 경로 기준 디렉터리가 예상과 다를 가능성이 큽니다. Alembic은 실행 위치의 영향을 받으므로 CI에서는 항상 저장소 루트에서 실행하는 규칙을 두는 편이 안전합니다.

## env.py 변경 후 검증 체크

```bash
alembic current
alembic revision --autogenerate -m "env wiring check"
alembic upgrade head --sql > /tmp/alembic-preview.sql
alembic downgrade -1 || true
```

여기서 중요한 건 마지막 줄이 아니라 첫 세 줄입니다. `current`가 읽히고, `autogenerate`가 실제 diff를 만들고, `--sql`이 정상 출력되면 env.py 책임 범위는 대체로 통과입니다.

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

- **`env.py`는 정확히 무엇이고 언제 실행될까요?**
  - `env.py`는 Alembic이 `upgrade`, `revision --autogenerate`, `--sql` 같은 모든 명령마다 실행하는 부트 스크립트입니다. 여기서 `run_migrations_online()`과 `run_migrations_offline()`이 갈리고, 실제 connection과 설정이 이 파일에서 조립됩니다.
- **왜 `target_metadata`는 선택 사항이 아니라 필수일까요?**
  - `target_metadata = Base.metadata`가 있어야 Alembic이 live DB와 모델 정의를 비교해 `op.add_column(...)` 같은 diff를 만들 수 있습니다. 본문이 강조했듯 `target_metadata = None`이면 autogenerate는 조용히 빈 파일만 냅니다.
- **DB URL을 환경 변수에서 안전하게 읽는 패턴은 어떻게 만들까요?**
  - `db_url = os.environ.get("DATABASE_URL")`로 읽고 `config.set_main_option("sqlalchemy.url", db_url)`로 `alembic.ini`를 덮어쓰는 패턴이 이 글의 답입니다. 이렇게 해야 local 기본값은 남기면서 staging·production credential은 git 밖에 둘 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Alembic 101 (1/10): 왜 Alembic인가, 그리고 init까지](./01-why-alembic-and-init.md)
- **env.py와 target_metadata: 모델과 마이그레이션 연결 (현재 글)**
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
- [Alembic: env.py](https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file)
- [Alembic: target_metadata](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- [Alembic: Batch Mode](https://alembic.sqlalchemy.org/en/latest/batch.html)
- [Alembic: Offline Mode](https://alembic.sqlalchemy.org/en/latest/offline.html)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/alembic-101/ko/02-env-py-and-target-metadata)

Tags: Python, Alembic, SQLAlchemy, Migration
