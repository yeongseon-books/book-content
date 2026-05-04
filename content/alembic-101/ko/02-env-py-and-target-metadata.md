---
title: 'env.py와 target_metadata: 모델과 마이그레이션 연결'
series: alembic-101
episode: 2
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
- env.py
- target_metadata
- Configuration
- SQLite
last_reviewed: '2026-05-03'
seo_description: env.py는 alembic이 명령마다 실행하는 부트 스크립트입니다.
---

# env.py와 target_metadata: 모델과 마이그레이션 연결

## 이 글에서 배울 것

- `env.py`가 정확히 무엇이고 언제 실행되는지
- `target_metadata`가 왜 필수인지 (autogenerate의 근거)
- DB URL을 환경 변수에서 안전하게 읽는 패턴
- online 모드와 offline 모드의 차이와 각각의 쓰임
- SQLite + alembic 조합에서 거의 항상 필요한 두세 가지 옵션

## 이 글에서 답할 질문

- `env.py`는 alembic 명령 흐름의 어느 시점에 어떤 컨텍스트로 실행되는가?
- `target_metadata`를 비워 두면 autogenerate가 왜 의미를 잃는가?
- DB URL을 코드에 박지 않고 환경 변수에서 안전하게 읽으려면 어떻게 구성하는가?
- online 모드와 offline 모드는 각각 언제 쓰는 것이 맞는가?
- SQLite + alembic 조합에서 거의 항상 켜 두어야 하는 옵션은 무엇이며 왜 그런가?

## 왜 중요한가

1편의 `alembic init`은 모든 파일을 만들어 줬지만, 그 상태로는 모델을 모릅니다. `alembic revision --autogenerate`를 돌려도 빈 파일만 나옵니다. `env.py`에서 모델 metadata를 알려 주는 한 줄을 빠뜨리면 alembic은 "DB와 모델 차이"를 계산할 근거 자체가 없기 때문입니다.

또한 `alembic.ini`에 DB URL을 평문으로 두면 staging/production credential이 git에 들어갑니다. 이 글은 `env.py`를 직접 들여다보면서 그 두 가지 — metadata 연결과 URL 처리 — 를 정리합니다.

## Mental Model

> `env.py`는 alembic이 명령마다 실행하는 **부트 스크립트**입니다. 매 명령(`upgrade`, `revision --autogenerate` 등)에서 alembic은 (1) `alembic.ini`를 읽고 → (2) `env.py`를 실행해 connection과 metadata를 얻은 뒤 → (3) versions 디렉터리의 revision을 적용합니다.

핵심은 "매번 실행된다"입니다. 그래서 환경 변수도 매 실행 시점에 새로 읽히고, 모델 import도 매번 다시 됩니다. 이 흐름을 잡으면 `env.py`에서 무엇을 해야 하는지 명확해집니다.

## 핵심 개념

### `env.py`의 두 함수

기본 `env.py`는 두 함수를 정의합니다.

- `run_migrations_online()`: 실제 DB connection을 열고 마이그레이션을 실행
- `run_migrations_offline()`: connection 없이 SQL 스크립트만 출력

마지막에 `if context.is_offline_mode(): run_migrations_offline() else: run_migrations_online()` 분기로 둘 중 하나가 호출됩니다.

### `target_metadata`

```python
from app.models import Base
target_metadata = Base.metadata
```

이 한 줄이 autogenerate의 근거입니다. alembic은 connection 너머의 실제 DB 스키마를 introspection으로 읽고, `target_metadata`와 비교해 차이를 revision 파일로 출력합니다. `target_metadata = None`이면 autogenerate는 빈 파일만 만듭니다.

### Online vs Offline

| 모드 | 명령 | 쓰임 |
| --- | --- | --- |
| Online | `alembic upgrade head` | 실제 DB에 직접 적용 |
| Offline | `alembic upgrade head --sql > out.sql` | SQL만 출력해 DBA가 수동 적용 |

Offline 모드는 production DB 접근이 제한된 환경(별도 변경관리 프로세스, 망 분리 등)에서 자주 씁니다.

### URL 우선순위

alembic은 일반적으로 `alembic.ini`의 `sqlalchemy.url`을 읽지만, `env.py`에서 `config.set_main_option("sqlalchemy.url", ...)`로 override할 수 있습니다. 환경 변수 패턴은 이 override를 활용합니다.

## Before-After

```python
# Before: 기본 생성 그대로 (autogenerate가 빈 파일만 생성)
from alembic import context
config = context.config
target_metadata = None  # ← 빈 채로 두면 autogenerate가 무력화

def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section), ...)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

```python
# After: 모델 연결 + 환경 변수 URL
import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from app.models import Base   # ← 모델 import

config = context.config

# DATABASE_URL 환경 변수가 있으면 alembic.ini를 override
db_url = os.environ.get("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata   # ← autogenerate 근거

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=url.startswith("sqlite"),  # SQLite 전용 batch 모드
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

After 버전은 (1) 모델을 안다 → autogenerate가 동작, (2) production credential은 환경 변수로만 받는다 → git 안전, (3) SQLite에서는 batch 모드를 자동으로 켠다 → ALTER 제약을 우회.

## 단계별 실습

### 1단계: 모델 import 경로 확보

`env.py`는 alembic 명령어 실행 위치에서 import됩니다. 보통 프로젝트 루트에서 `alembic` 명령을 실행하므로, `from app.models import Base`가 바로 import되도록 패키지 구조를 잡거나 `sys.path`에 명시적으로 루트를 추가합니다.

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from app.models import Base
```

### 2단계: `target_metadata` 설정

```python
target_metadata = Base.metadata
```

여러 `Base`가 있다면 `MetaData`를 합쳐 전달합니다.

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

`alembic.ini`의 평문 URL은 로컬 SQLite 같은 안전한 기본값만 두고, staging/production은 환경 변수로 주입합니다.

### 4단계: SQLite를 위한 `render_as_batch`

SQLite는 `ALTER TABLE`로 컬럼 drop, type change 등을 거의 지원하지 않습니다. alembic의 batch 모드는 (1) 임시 테이블 생성 → (2) 데이터 복사 → (3) 원본 drop → (4) 임시 테이블 rename으로 우회합니다. SQLite를 쓴다면 거의 항상 켭니다.

### 5단계: autogenerate 동작 확인

```bash
# 모델에 컬럼 하나 추가
# class User(Base):
#     ...
#     tier: Mapped[str] = mapped_column(default="free")

alembic revision --autogenerate -m "add users.tier"
```

`versions/<hash>_add_users_tier.py`가 생성되고 `upgrade()`에 `op.add_column(...)`이 들어 있으면 metadata 연결이 성공한 것입니다.

### 6단계: offline 모드로 SQL 미리 보기

```bash
alembic upgrade head --sql
```

connection 없이 DDL을 출력합니다. CI에 이 명령을 넣고 PR 본문에 출력 결과를 붙이는 팀이 많습니다. 사람 눈으로 SQL을 보는 습관 자체가 큰 안전 장치입니다.

## 자주 하는 실수

- **`target_metadata = None`을 그대로 두기.** autogenerate가 빈 파일만 만듭니다. 첫 디버깅 포인트.
- **모델을 import 했는데 빈 결과.** 모델 모듈이 로딩되지 않으면 `Base.metadata`가 비어 있습니다. `__init__.py`에서 모든 모델을 명시적으로 import하거나 `env.py`에서 직접 import합니다.
- **SQLite에서 `render_as_batch`를 빼고 컬럼 drop 시도.** "ALTER TABLE drop column not supported" 에러가 납니다.
- **`alembic.ini`에 production URL을 그대로 commit.** 환경 변수 override 패턴이 사실상 표준입니다.
- **pool을 기본으로 두기.** alembic은 보통 단발성 명령이므로 `poolclass=pool.NullPool`이 더 적절합니다.

## 실무에서 쓰는 패턴

- **`env.py`는 한 번 잘 짜면 거의 건드리지 않음.** 모델 import + 환경 변수 URL + batch 모드(SQLite/MySQL) 세 가지가 끝.
- **여러 environment(local/staging/prod)에서 같은 `env.py`.** 차이는 환경 변수만으로 흡수.
- **`compare_type=True`, `compare_server_default=True`.** autogenerate가 컬럼 타입 변경과 default 변경까지 잡도록 켭니다(다음 글에서 자세히).
- **`include_object` hook으로 특정 테이블 제외.** 외부 시스템이 관리하는 테이블이 있을 때 유용합니다.
- **sync vs async.** async SQLAlchemy를 쓰더라도 alembic은 `env.py`에서 sync engine으로 동작하는 게 일반적입니다. async가 필요하면 `connectable.run_sync(...)` 패턴을 씁니다.

## 체크리스트

- [ ] `from app.models import Base` 같은 import가 `env.py` 상단에 있고 실제로 동작한다
- [ ] `target_metadata = Base.metadata`가 명시돼 있다
- [ ] `DATABASE_URL` 환경 변수로 URL을 override할 수 있다
- [ ] SQLite를 쓴다면 `render_as_batch=True`가 `context.configure(...)`에 들어 있다
- [ ] `alembic.ini`에는 안전한 기본값(local SQLite)만 들어 있다
- [ ] `alembic revision --autogenerate`가 빈 파일이 아니라 실제 차이를 출력한다
- [ ] `alembic upgrade head --sql`로 offline DDL 출력이 가능하다

## 연습 문제

1. `env.py`에서 `target_metadata = None`인 채로 `alembic revision --autogenerate`를 돌려 빈 파일이 생성되는 걸 직접 확인하세요.
2. `DATABASE_URL`을 두 개의 다른 SQLite 파일로 바꿔 가며 같은 마이그레이션을 적용해 보세요.
3. `render_as_batch`를 끄고 SQLite에서 컬럼 drop 마이그레이션을 시도해 어떤 에러가 나는지 재현하세요.

## 정리, 다음 글

`env.py`는 alembic의 부트 스크립트이고, 그 안에서 단 두 가지 — `target_metadata` 연결과 환경 변수 URL — 만 잡으면 나머지는 거의 손댈 일이 없습니다. SQLite를 쓴다면 `render_as_batch`를 추가합니다.

다음 글에서는 첫 의미 있는 revision을 직접 작성합니다. `op.create_table`, `op.add_column`, `op.execute`의 세 도구로 손으로 작성하는 마이그레이션과 자동 생성된 마이그레이션을 비교하고, `upgrade`/`downgrade`가 대칭이 되도록 짜는 법을 정리합니다.

## 참고 자료

- Alembic: env.py — https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file
- Alembic: target_metadata — https://alembic.sqlalchemy.org/en/latest/autogenerate.html
- Alembic: Batch Mode — https://alembic.sqlalchemy.org/en/latest/batch.html
- Alembic: Offline Mode — https://alembic.sqlalchemy.org/en/latest/offline.html

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, Alembic, env.py, target_metadata, Configuration, SQLite
