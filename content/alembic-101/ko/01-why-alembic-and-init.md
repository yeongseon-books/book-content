---
title: 왜 Alembic인가, 그리고 init까지
series: alembic-101
episode: 1
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
- SQLAlchemy
- Migration
- SQLite
last_reviewed: '2026-05-03'
seo_description: Alembic은 DB 스키마를 위한 git입니다. 각 마이그레이션 파일은 commit이고, alembic_version
  테이블은 현재…
---

# 왜 Alembic인가, 그리고 init까지

## 이 글에서 배울 것

- "마이그레이션 도구"가 정확히 어떤 문제를 해결하는지
- `Base.metadata.create_all` 만으로는 production이 안 되는 이유
- Alembic의 핵심 개념: revision, head, version table
- `alembic init`로 프로젝트 구조를 만드는 방법
- SQLite 기준 alembic 환경에서 처음 마주치는 함정 두세 가지

## 이 글에서 답할 질문

- 왜 `Base.metadata.create_all`만으로는 production 스키마 운영이 안 되는가?
- Alembic의 revision, head, version table은 각각 어떤 역할을 하는가?
- `alembic init` 직후 만들어지는 디렉터리 구조에서 무엇을 먼저 손봐야 하는가?
- SQLite 환경에서 alembic을 처음 돌릴 때 자주 마주치는 함정은 무엇인가?
- 팀이 도구 없이 손으로 SQL을 돌릴 때 잃게 되는 것은 정확히 무엇인가?

## 왜 중요한가

스키마 변경은 모든 production 사고의 단골 원인입니다. 코드는 git으로, 인프라는 Terraform으로 관리하면서, "DB 스키마는 누가 어떤 SQL을 언제 돌렸는가"를 손으로 관리하는 팀이 의외로 많습니다. 그 결과 staging은 프로덕션과 미묘하게 달라지고, 롤백할 때는 누구도 자신 있게 "스키마를 어디까지 되돌려야 하는지" 답하지 못합니다.

Alembic은 SQLAlchemy 저자가 만든 마이그레이션 도구로, 이 문제를 git처럼 다룹니다. 각 변경은 revision이고, head는 최신 상태이며, 모든 환경은 같은 history를 따라 올라가거나 내려옵니다. 이 글은 그 첫 단추인 "왜 필요한가"와 "어떻게 시작하는가"를 정리합니다.

## Mental Model

> Alembic은 **DB 스키마를 위한 git**입니다. 각 마이그레이션 파일은 commit이고, `alembic_version` 테이블은 현재 HEAD를 가리키며, `upgrade head`는 fast-forward이고, `downgrade -1`은 reset 한 칸입니다.

이 비유가 한 번 자리잡으면 거의 모든 명령이 자연스러워집니다. `revision`은 새 commit을 만드는 것이고, `merge`는 두 head를 합치는 것이며, `stamp`는 working tree는 그대로 두고 HEAD만 바꾸는 `git reset` 같은 동작입니다.

## 핵심 개념

### Revision과 Head

각 마이그레이션 파일은 `revision`이라는 고유 ID와 `down_revision`이라는 부모 ID를 가집니다. revision들은 단방향 그래프를 이루고, 그래프의 마지막 노드(자식 없는 노드)가 `head`입니다. 일반적으로 head는 하나지만, branch가 생기면 둘 이상이 될 수 있습니다.

### `alembic_version` 테이블

DB에는 `alembic_version`이라는 한 줄짜리 메타 테이블이 생깁니다. 이 테이블의 값은 "이 DB가 현재 어느 revision까지 적용됐는가"입니다. Alembic의 모든 명령은 이 값을 읽고 그래프와 비교해 결정합니다.

### `create_all`과의 차이

| 항목 | `Base.metadata.create_all` | Alembic |
| --- | --- | --- |
| 용도 | 테스트, 초기 prototyping | production 운영 |
| 변경 추적 | 없음 | revision 그래프 |
| 컬럼 변경/삭제 | 못 함 | 자유롭게 |
| 환경 간 동기화 | 안 됨 | 동일 history |
| 롤백 | 없음 | downgrade 명령 |

`create_all`은 "테이블이 없으면 만든다"가 전부입니다. 컬럼 하나 추가하면 `create_all`로는 절대 production에 반영이 안 됩니다.

### `alembic init`이 만드는 것

```text
project/
├── alembic.ini           # 전역 설정 (DB URL, 로깅, 파일명 템플릿)
└── alembic/
    ├── env.py            # 마이그레이션 실행 컨텍스트
    ├── script.py.mako    # revision 파일 템플릿
    └── versions/         # 실제 마이그레이션 파일들
```

가장 자주 만지는 파일은 `env.py`(다음 글)와 `versions/*.py`(매 변경마다)입니다.

## Before-After

```bash
# Before: 프로덕션 DB에 손으로 SQL을 돌림
psql -h prod -U app -d main -c "ALTER TABLE users ADD COLUMN tier VARCHAR(16) NOT NULL DEFAULT 'free';"
# 누가, 언제, 어떤 환경에 돌렸는지 사후 추적 불가
```

```bash
# After: revision 파일이 변경 기록 그 자체
alembic revision -m "add users.tier"
# alembic/versions/3f9c..._add_users_tier.py 자동 생성
# 코드 리뷰, 환경 간 동기화, 롤백이 모두 가능
alembic upgrade head
```

After 버전은 git diff에 잡히고, PR 리뷰 대상이 되며, staging과 production이 같은 명령으로 같은 상태가 됩니다.

## 단계별 실습

### 1단계: 환경 준비

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

다음 구조가 생성됩니다.

```text
alembic-demo/
├── alembic.ini
└── alembic/
    ├── env.py
    ├── script.py.mako
    └── versions/
```

### 4단계: SQLite URL 설정

`alembic.ini`에서 다음 줄을 찾아 SQLite 경로로 바꿉니다.

```ini
sqlalchemy.url = sqlite:///./app.db
```

다음 글에서 다루지만 미리 환경 변수로 받아 쓰는 형태가 더 안전합니다(`os.environ["DATABASE_URL"]`).

### 5단계: 첫 빈 revision

```bash
alembic revision -m "init"
```

`alembic/versions/<hash>_init.py`가 생성되고, 안에는 `upgrade()`와 `downgrade()` 두 함수가 비어 있습니다. 이 파일이 첫 commit입니다.

### 6단계: upgrade와 version 테이블 확인

```bash
alembic upgrade head
sqlite3 app.db "SELECT * FROM alembic_version;"
# 결과: <hash>
```

`alembic_version`에 한 줄이 생긴 것을 보면 모든 게 명확해집니다. 이 테이블이 모든 마이그레이션 명령의 기준점입니다.

## 자주 하는 실수

- **`create_all`로 production을 시작하기.** 한 번 시작하면 alembic을 도입할 때 "현재 스키마를 첫 revision으로 stamping"하는 추가 단계가 필요합니다. 가능하면 처음부터 alembic만 씁니다.
- **`alembic.ini`에 production credential을 그대로 넣기.** 환경 변수로 받아 쓰도록 `env.py`에서 override합니다(다음 글).
- **`alembic_version`을 손으로 수정.** 가능은 하지만 거의 항상 사고로 이어집니다. `alembic stamp` 명령을 통해서만 바꿉니다.
- **revision 파일을 push 후에 수정.** revision ID는 history의 일부입니다. 이미 다른 환경에 적용됐다면 새 revision으로 고치는 게 안전합니다.
- **여러 사람이 동시에 `revision -m`.** branch가 생깁니다. 5편에서 다루는 `merge` 명령으로 합칠 수 있지만, 가능하면 PR 머지 직전에 rebase 비슷한 정리를 합니다.

## 실무에서 쓰는 패턴

- **revision 파일은 코드와 같은 PR.** "기능 코드 + 마이그레이션 + 테스트"가 한 PR에 모입니다.
- **CI에서 `alembic upgrade head --sql`로 DDL을 출력해 리뷰.** 자동 생성된 SQL을 사람 눈으로 한 번 보면 의외로 많은 사고를 막습니다.
- **`alembic.ini`의 파일명 템플릿을 의미 있게.** 기본은 hash만 들어가지만, `file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(slug)s`처럼 바꾸면 정렬이 시간순이 됩니다.
- **branch는 가능한 한 만들지 말기.** 큰 팀이 아니면 head 하나로 충분합니다.
- **첫 revision은 "현재 상태 baseline"으로.** 기존 DB에 도입할 때는 `alembic revision --autogenerate -m "baseline"` 후 `alembic stamp head`로 바로 HEAD에 표시합니다.

## 체크리스트

- [ ] `alembic init` 후 `alembic.ini` / `env.py` / `versions/` 구조를 확인했다
- [ ] `sqlalchemy.url`이 적절한 DB(여기서는 SQLite) URL로 설정돼 있다
- [ ] 첫 빈 revision을 만들고 `upgrade head`로 `alembic_version` 테이블 생성을 확인했다
- [ ] `create_all`은 테스트에서만 사용하고 production에는 쓰지 않는다는 결정이 명확하다
- [ ] revision 파일이 git에 포함되고 PR 리뷰 대상이 된다
- [ ] credential은 `alembic.ini` 평문이 아니라 환경 변수로 받는다(다음 글에서 구현)

## 연습 문제

1. 위 단계대로 SQLite + `alembic init`을 직접 실행하고 `alembic_version` 테이블이 생긴 것을 확인하세요.
2. `alembic history`와 `alembic current` 명령을 실행해 출력 차이를 비교하세요.
3. `alembic downgrade base`로 모든 revision을 되돌린 뒤 `alembic_version` 테이블이 어떻게 되는지 확인하세요.

## 정리, 다음 글

Alembic은 "DB 스키마를 위한 git"이라는 비유 한 줄로 거의 다 설명됩니다. revision, head, version 테이블 셋만 잡으면 나머지는 명령어 외우기에 가깝습니다.

다음 글에서는 `env.py`를 직접 들여다봅니다. 어떻게 모델 metadata와 연결하는지, 환경 변수로 DB URL을 어떻게 안전하게 받는지, online/offline 모드는 무엇인지 정리합니다.

## 참고 자료

- Alembic: Tutorial — https://alembic.sqlalchemy.org/en/latest/tutorial.html
- Alembic: Configuration — https://alembic.sqlalchemy.org/en/latest/config.html
- SQLAlchemy: MetaData — https://docs.sqlalchemy.org/en/20/core/metadata.html
- SQLite Documentation — https://www.sqlite.org/docs.html

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, Alembic, SQLAlchemy, Migration, init, SQLite
