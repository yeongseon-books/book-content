---
title: 'env.py와 target_metadata: 모델과 마이그레이션 연결'
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

# env.py와 target_metadata: 모델과 마이그레이션 연결

이 글은 Alembic 101 시리즈의 두 번째 글입니다. 여기서는 `env.py`가 Alembic 실행 흐름에서 정확히 어떤 위치를 차지하는지, 그리고 `target_metadata`가 autogenerate의 근거로서 무엇을 제공해야 하는지 실무 관점에서 정리합니다.

1편에서 `alembic init`까지 마쳤더라도 그 상태의 Alembic은 여러분 모델을 모릅니다. 이 연결을 `env.py`에서 제대로 하지 못하면 `alembic revision --autogenerate`는 즉시 신뢰를 잃습니다.

## 이 글에서 다룰 문제

- `env.py`는 정확히 무엇이고 언제 실행될까요?
- 왜 `target_metadata`는 선택 사항이 아니라 필수일까요?
- DB URL을 환경 변수에서 안전하게 읽는 패턴은 어떻게 만들까요?
- online과 offline 모드는 무엇이 다르고 언제 중요할까요?
- SQLite와 Alembic을 함께 쓸 때 거의 항상 필요한 옵션은 무엇일까요?

## 왜 중요한가

1편의 scaffold 상태에서 Alembic은 아직 모델 metadata의 위치를 모릅니다. 그래서 `alembic revision --autogenerate`를 실행해도 빈 파일이 나옵니다. `env.py`에 모델 metadata를 알려 주는 한 줄이 없으면, Alembic은 live DB schema와 무엇을 비교해야 하는지조차 알 수 없습니다.

또 하나의 문제는 URL입니다. `alembic.ini`에 staging이나 production용 DB URL을 평문으로 두면 credential이 그대로 git에 남습니다. 이 글에서는 `env.py`를 열어 보고, metadata 연결과 URL 처리라는 두 문제를 함께 해결하겠습니다.

## 멘탈 모델

> `env.py`는 Alembic이 **모든 명령마다 실행하는 부트 스크립트**입니다. 각 실행(`upgrade`, `revision --autogenerate` 등)에서 Alembic은 (1) `alembic.ini`를 읽고, (2) `env.py`를 실행해 connection과 metadata를 얻고, (3) `versions/` 아래의 revision을 적용합니다.

여기서 가장 중요한 사실은 매번 실행된다는 점입니다. 환경 변수도 매번 다시 읽히고, 모델 import도 매번 일어납니다. 이 흐름을 받아들이면 `env.py`의 책임이 훨씬 또렷해집니다.

### 다이어그램: `env.py`가 metadata와 연결을 조립하는 위치

![env.py가 metadata와 연결을 조립하는 위치](https://yeongseon-books.github.io/book-public-assets/assets/alembic-101/02/02-01-diagram-where-env-py-assembles-metadata.ko.png)
*Alembic 실행마다 `env.py`가 URL, metadata, 실행 모드를 조립하는 순서*

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
# Before: scaffolded defaults (autogenerate produces empty files)
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
# After: model wired in, URL from environment
import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from app.models import Base   # ← import the model

config = context.config

# Override alembic.ini if DATABASE_URL is set in the environment
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

<!-- toc:begin -->
## 시리즈 목차

- [왜 Alembic인가, 그리고 init까지](./01-why-alembic-and-init.md)
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

Tags: Python, Alembic, SQLAlchemy, Migration
