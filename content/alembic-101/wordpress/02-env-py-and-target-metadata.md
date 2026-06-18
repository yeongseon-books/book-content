---
title: "바이브코딩을 위한 Alembic 기초 (2/10): env.py와 target_metadata"
series: alembic-101
episode: 2
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Python
  - Alembic
  - SQLAlchemy
  - Migration
  - DB마이그레이션
---

# 바이브코딩을 위한 Alembic 기초 (2/10): env.py와 target_metadata

이 글은 "바이브코딩을 위한 Alembic 기초" 시리즈의 두 번째 글입니다.

---

AI가 새 모델 파일을 뚝딱 만들어 줬습니다. `User`, `Post`, `Comment` 클래스가 깔끔하게 정의됐고, 여러분은 기쁘게 `alembic revision --autogenerate`를 실행합니다. 그런데 생성된 파일을 열면 `upgrade()`가 텅 비어 있습니다. "AI가 만든 모델인데 왜 Alembic이 변경을 못 잡지?" 이 문제의 원인은 거의 항상 `env.py`의 `target_metadata` 설정이 빠져 있기 때문입니다.

바이브코딩에서 AI는 모델 코드를 잘 만들지만, `env.py`에 그 모델의 `Base.metadata`를 연결하는 설정은 종종 빠뜨립니다. `env.py`는 Alembic의 런타임 컨텍스트입니다. 여기서 어떤 모델의 metadata를 바라볼지, DB URL을 어디서 읽을지가 결정됩니다.

이 두 가지를 올바르게 설정하면 AI가 모델을 바꿀 때마다 autogenerate가 정확하게 변경을 감지합니다. 반대로 이 설정이 없으면 revision 파일은 항상 비어 있거나, 엉뚱한 DB에 적용됩니다.

> **핵심 인사이트:** `env.py`의 `target_metadata`는 Alembic이 "무엇이 바뀌었는지" 알아내는 기준점입니다. AI가 모델을 추가할 때마다 이 연결이 올바른지 확인하는 것이 바이브코딩의 핵심 습관입니다.

## 이 글에서 다룰 문제

- `target_metadata`가 없으면 autogenerate는 왜 빈 revision을 만들까요?
- `env.py`에서 DB URL을 환경 변수로 읽는 안전한 패턴은 무엇인가요?
- online 모드와 offline 모드는 실제로 어떤 차이가 있을까요?
- AI가 새 모델을 추가할 때 `env.py`에서 확인해야 할 것은 무엇인가요?
- multi-schema 프로젝트에서 `env.py`를 어떻게 구성해야 할까요?

## target_metadata 연결

```python
# env.py - 핵심 설정
from app.models import Base  # AI가 만든 모델의 Base import

target_metadata = Base.metadata  # 이 한 줄이 autogenerate의 기준
```

AI가 새 모델 파일을 만들면 반드시 `Base`를 같은 `DeclarativeBase`에서 상속받는지 확인하세요.

## 변경 전후 비교

**Before: target_metadata 없음**
```python
target_metadata = None  # autogenerate가 아무것도 감지 못함
```

**After: 올바른 연결**
```python
from app.models import Base
target_metadata = Base.metadata  # 모든 테이블 변경이 감지됨
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| `target_metadata = None` 유지 | autogenerate가 항상 빈 파일 생성 | `Base.metadata` 연결 |
| DB URL 하드코딩 | 보안, 환경별 분리 불가 | `os.environ["DATABASE_URL"]` 사용 |
| 모델 import 누락 | 새 테이블이 감지 안 됨 | 모든 모델 파일 import 확인 |
| online/offline 혼용 | 환경에 따라 다른 동작 | CI는 offline, 배포는 online |
| 여러 Base 사용 | 일부 테이블 누락 | 단일 Base로 통일 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"새 Comment 모델을 추가하고, env.py의 target_metadata에 포함되도록 해줘"

# AI가 확인할 사항:
# 1. Comment가 같은 Base를 상속받는지
# 2. env.py에서 Comment 모델 파일이 import되는지
# 3. DATABASE_URL이 환경 변수에서 읽히는지
```

## 운영 체크리스트

- [ ] `env.py`에서 `target_metadata = Base.metadata`가 설정되어 있다
- [ ] DB URL이 환경 변수에서 읽힌다 (`os.environ["DATABASE_URL"]`)
- [ ] 모든 모델이 같은 `Base`를 상속받는다
- [ ] `alembic revision --autogenerate`가 변경을 올바르게 감지한다
- [ ] online/offline 모드 중 어느 것을 사용할지 팀 규칙이 있다

## 처음 질문으로 돌아가기

- **`target_metadata`가 없으면 autogenerate가 왜 빈 revision을 만들까요?** Alembic이 현재 모델 상태를 모르기 때문에 "변경 없음"으로 판단합니다.
- **DB URL을 환경 변수로 읽는 이유는?** 환경별(dev/staging/prod) 다른 DB를 사용할 수 있고, credential이 코드에 노출되지 않습니다.
- **AI가 새 모델을 추가할 때 확인할 것은?** 같은 Base 상속 여부, env.py import 여부, target_metadata 포함 여부입니다.

## 정리

`env.py`는 Alembic의 브레인입니다. AI가 아무리 좋은 모델을 만들어도 `target_metadata`가 연결되지 않으면 autogenerate는 작동하지 않습니다. 다음 글에서는 첫 revision을 손으로 작성하며 `upgrade()`와 `downgrade()`의 구조를 이해합니다.

## 참고 자료

- [Alembic 환경 설정](https://alembic.sqlalchemy.org/en/latest/ops.html)
- [SQLAlchemy DeclarativeBase](https://docs.sqlalchemy.org/en/20/orm/declarative_bases.html)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Alembic 기초 (1/10): 왜 Alembic인가, 그리고 init까지
- **바이브코딩을 위한 Alembic 기초 (2/10): env.py와 target_metadata (현재 글)**
- 바이브코딩을 위한 Alembic 기초 (3/10): 첫 revision: upgrade와 downgrade
- 바이브코딩을 위한 Alembic 기초 (4/10): autogenerate와 그 한계
- 바이브코딩을 위한 Alembic 기초 (5/10): branch와 merge
- 바이브코딩을 위한 Alembic 기초 (6/10): 데이터 마이그레이션
- 바이브코딩을 위한 Alembic 기초 (7/10): online과 offline 모드
- 바이브코딩을 위한 Alembic 기초 (8/10): downgrade 전략
- 바이브코딩을 위한 Alembic 기초 (9/10): 배포 순서와 blue/green
- 바이브코딩을 위한 Alembic 기초 (10/10): production과 팀 workflow
<!-- toc:end -->

Tags: 바이브코딩, Python, Alembic, SQLAlchemy, Migration, DB마이그레이션
