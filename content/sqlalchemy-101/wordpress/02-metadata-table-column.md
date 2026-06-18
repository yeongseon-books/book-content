---
series: sqlalchemy-101
episode: 2
title: "바이브코딩을 위한 SQLAlchemy (2/10): MetaData, Table, Column으로 schema를 Python 객체로 만들기"
status: publish-ready
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - SQLAlchemy
  - Python
  - Database
  - Schema
---

# 바이브코딩을 위한 SQLAlchemy (2/10): MetaData, Table, Column으로 schema를 Python 객체로 만들기

이 글은 "바이브코딩을 위한 SQLAlchemy" 시리즈의 두 번째 글입니다. AI가 생성한 SQLAlchemy 코드를 검토하다 보면 스키마 정의 방식이 일관되지 않은 경우를 자주 봅니다. MetaData가 무엇이고 Table이 왜 필요한지 이해하면, 생성된 코드의 구조적 문제를 바로 파악할 수 있습니다.

---

## 바이브코딩 현장에서 이 문제가 왜 생기는가

"SQLAlchemy로 users 테이블 만드는 코드 작성해 줘"라고 하면 AI는 대개 두 가지 방식 중 하나를 씁니다. Core 방식(MetaData + Table)이거나 ORM 방식(DeclarativeBase)입니다. 이 둘이 섞인 코드가 나오기도 합니다.

문제는 두 방식이 동시에 쓰일 때입니다. `MetaData.create_all()`을 호출하면 어떤 테이블이 생성되는지, `Table` 객체와 ORM 모델이 같은 메타데이터를 공유하는지 여부가 불분명해집니다. 이를 이해하지 못하면 테이블이 이미 존재하는데 다시 생성하거나, 마이그레이션이 일부만 적용되는 문제가 생깁니다.

MetaData는 테이블 정의의 레지스트리입니다. Table 객체를 담아 두었다가 `create_all()`이나 `drop_all()`을 일괄적으로 실행할 수 있게 해 줍니다. Table은 실제 데이터베이스 테이블을 Python 객체로 표현합니다. Column은 각 열의 이름과 타입을 정의합니다.

`create_all()`은 이미 존재하는 테이블을 건드리지 않습니다. `checkfirst=True`가 기본값이므로 안전하게 반복 호출할 수 있습니다.

> "MetaData는 도시 계획 지도입니다. Table은 지도 위에 표시된 건물이고, Column은 건물의 방입니다."

---

## 이 글에서 답할 질문 5가지

1. `MetaData()`는 왜 필요하고 어디서 한 번만 만들어야 할까요?
2. `Table` 객체와 ORM 모델의 관계는 무엇인가요?
3. `create_all()`은 기존 테이블을 덮어쓰나요?
4. SQLAlchemy의 기본 타입과 DB별 타입은 어떻게 다른가요?
5. 기존 데이터베이스에서 스키마를 읽어오는 reflection은 어떻게 쓰나요?

---

## MetaData와 Table 핵심 개념

### MetaData: 테이블 레지스트리

```python
from sqlalchemy import MetaData

metadata = MetaData()
```

MetaData는 애플리케이션당 하나를 원칙으로 합니다. 모든 Table 정의가 이 객체에 등록되므로, 분산된 경우 `create_all()`이 일부 테이블만 생성할 수 있습니다.

### Table과 Column 정의

```python
from sqlalchemy import Column, Integer, String, Table, MetaData

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False),
    Column("email", String(200), unique=True),
)
```

### create_all로 테이블 생성

```python
metadata.create_all(engine)  # 없는 테이블만 생성
metadata.drop_all(engine)    # 모든 테이블 삭제
```

### reflection: 기존 DB에서 스키마 읽기

```python
existing_table = Table("users", metadata, autoload_with=engine)
```

`autoload_with`를 사용하면 데이터베이스에서 컬럼 정보를 자동으로 읽어옵니다. 기존 데이터베이스와 통합할 때 유용합니다.

---

## Before / After 비교

| 항목 | Before (문제 있는 패턴) | After (올바른 패턴) |
| --- | --- | --- |
| MetaData 위치 | 함수 안에서 매번 생성 | 모듈 레벨에서 한 번만 생성 |
| 테이블 생성 | 매 요청마다 `create_all()` | 앱 시작 시 한 번만 실행 |
| 타입 선택 | DB 전용 타입 남용 | SQLAlchemy 추상 타입 우선 |
| 스키마 확인 | 테이블 존재 여부 수동 확인 | `checkfirst=True` (기본값) 활용 |

---

## 자주 하는 실수

| 실수 | 원인 | 해결 |
| --- | --- | --- |
| 여러 MetaData 사용 | 모듈별 분리 | 중앙 집중식 MetaData 인스턴스 |
| 테이블 누락 | MetaData가 일부만 포함 | 모든 Table이 같은 MetaData 사용 확인 |
| 타입 불일치 | DB별 타입 직접 사용 | SQLAlchemy 추상 타입 사용 |
| reflection 혼용 | 정의와 reflection 혼재 | 한 가지 방식으로 통일 |

---

## AI 활용 팁

> "SQLAlchemy 2.x Core 방식으로, 모듈 레벨 MetaData를 사용하는 users와 posts 테이블 정의를 작성해 줘. 추상 타입(Integer, String, DateTime)을 사용하고, 외래 키 관계도 포함해 줘."

생성된 코드에서 확인할 것:
- 모든 Table이 동일한 MetaData 객체를 참조하는지
- DB 전용 타입 대신 SQLAlchemy 추상 타입 사용 여부
- `nullable`, `unique`, `index` 옵션이 의도에 맞게 설정되었는지

---

## 체크리스트

- [ ] MetaData를 모듈 레벨에서 한 번만 생성하는가
- [ ] 모든 Table이 같은 MetaData를 참조하는가
- [ ] `create_all()`을 앱 시작 시 한 번만 호출하는가
- [ ] SQLAlchemy 추상 타입(Integer, String, DateTime)을 우선 사용하는가
- [ ] 기존 DB 통합 시 reflection(`autoload_with`)을 고려했는가

---

## 처음 질문으로 돌아가기

**`MetaData()`는 왜 하나만 만들어야 하나요?**
모든 Table이 같은 MetaData에 등록되어야 `create_all()`이 전체 스키마를 한 번에 처리할 수 있습니다. 분산된 MetaData는 부분적인 생성/삭제로 이어집니다.

**`create_all()`은 기존 테이블을 덮어쓰나요?**
아닙니다. 기본적으로 이미 존재하는 테이블은 건드리지 않습니다(`checkfirst=True`).

---

## 정리

MetaData는 스키마의 중앙 레지스트리입니다. Table과 Column으로 Python 객체로 스키마를 표현하면, `create_all()`이 전체를 일관되게 관리합니다. 다음 글에서는 이 테이블을 대상으로 select, insert, update, delete를 2.x 스타일로 다루는 방법을 살펴봅니다.

---

## 참고 자료

- [SQLAlchemy MetaData Documentation](https://docs.sqlalchemy.org/en/20/core/metadata.html)
- [SQLAlchemy Column and Data Types](https://docs.sqlalchemy.org/en/20/core/types.html)

---

<!-- toc:begin -->
## 시리즈 목차

1. 바이브코딩을 위한 SQLAlchemy (1/10): Engine과 Connection의 본질
2. **바이브코딩을 위한 SQLAlchemy (2/10): MetaData, Table, Column으로 schema를 Python 객체로 만들기 (현재 글)**
3. 바이브코딩을 위한 SQLAlchemy (3/10): select·insert·update·delete를 2.x style로 다루기
4. 바이브코딩을 위한 SQLAlchemy (4/10): DeclarativeBase와 mapped_column으로 모델 정의하기
5. 바이브코딩을 위한 SQLAlchemy (5/10): Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리
6. 바이브코딩을 위한 SQLAlchemy (6/10): relationship과 back_populates로 양방향 탐색 안전하게 잇기
7. 바이브코딩을 위한 SQLAlchemy (7/10): 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가
8. 바이브코딩을 위한 SQLAlchemy (8/10): 이벤트, hybrid_property, 그리고 커스텀 타입
9. 바이브코딩을 위한 SQLAlchemy (9/10): 비동기 SQLAlchemy: aiosqlite와 AsyncSession
10. 바이브코딩을 위한 SQLAlchemy (10/10): 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포
<!-- toc:end -->

Tags: 바이브코딩, SQLAlchemy, Python, Database, Schema
