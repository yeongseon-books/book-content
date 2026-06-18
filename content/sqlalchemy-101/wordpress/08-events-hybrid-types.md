---
title: "바이브코딩을 위한 SQLAlchemy 기초 (8/10): 이벤트와 확장점"
series: sqlalchemy-101
episode: 8
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - SQLAlchemy
  - Python
  - ORM
  - HybridProperty
---

# 바이브코딩을 위한 SQLAlchemy 기초 (8/10): 이벤트와 확장점

이 글은 "바이브코딩을 위한 SQLAlchemy 기초" 시리즈의 여덟 번째 글입니다.

---

바이브코딩에서 AI는 SQLAlchemy 모델 코드를 빠르게 만들어 줍니다. 그런데 도메인 규칙이 커지면 같은 질문이 반복됩니다. 이메일 정규화는 어디에 둬야 할까요? 핸들러에 두면 같은 코드가 여러 곳에 흩어집니다. 비밀번호 해싱은 모델 저장 시 자동으로 적용되어야 합니다. 파생 속성(예: 전체 이름 = 성 + 이름)을 Python 속성과 SQL 표현으로 동시에 쓰고 싶습니다.

AI가 만든 ORM 코드에서 이 규칙들은 대부분 핸들러나 서비스 함수에 흩어져 있습니다. 모델을 직접 저장해도 정규화가 적용되지 않고, `WHERE users.full_name = ?`처럼 파생 속성을 SQL WHERE 절에 쓸 수 없습니다.

SQLAlchemy의 event 시스템, `@validates`, `hybrid_property`, `TypeDecorator`는 도메인 규칙을 모델 가까이 두기 위한 공식 확장점입니다. 타입 층, 속성 층, 이벤트 층 중 어디에 규칙을 두느냐에 따라 적용 범위와 디버깅 방식이 달라집니다.

> **핵심 인사이트:** 도메인 규칙의 위치는 세 층으로 구분됩니다. 타입 층(`TypeDecorator`)은 컬럼 값이 DB로 들고 날 때, 속성 층(`@validates`, `hybrid_property`)은 Python 객체 레벨에서, 이벤트 층(mapper 이벤트)은 세션/엔진 라이프사이클 시점에 규칙을 적용합니다.

## 이 글에서 다룰 문제

- 이벤트, 속성, 타입 확장점은 각각 어떤 책임을 맡아야 할까요?
- `@validates`와 mapper 이벤트는 언제 선택이 갈릴까요?
- `hybrid_property`는 왜 Python 속성과 SQL 표현을 함께 제공할까요?
- `TypeDecorator`로 어떤 타입 변환을 구현할 수 있나요?
- AI가 만든 ORM 코드에서 확장점 관련으로 확인할 것은 무엇인가요?

## 이벤트와 확장점 핵심 패턴

```python
from sqlalchemy.orm import validates, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import String, Integer, select
import re

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _email: Mapped[str] = mapped_column("email", String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)

    # @validates: 속성 설정 시 검증/변환 (Python 레벨)
    @validates("_email")
    def validate_email(self, key, value):
        value = value.strip().lower()       # 정규화
        if "@" not in value:
            raise ValueError(f"Invalid email: {value}")
        return value

    # hybrid_property: Python 속성 + SQL 표현 동시 제공
    @hybrid_property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @full_name.expression
    def full_name(cls):
        # SQL 표현: WHERE full_name = ? 사용 가능
        return cls.first_name + " " + cls.last_name
```

```python
from sqlalchemy import TypeDecorator, String
import json

# TypeDecorator: 컬럼 값 저장/로딩 시 자동 변환
class JSONType(TypeDecorator):
    """Python dict/list를 JSON 문자열로 저장"""
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Python → DB: dict를 JSON 문자열로"""
        if value is not None:
            return json.dumps(value, ensure_ascii=False)
        return value

    def process_result_value(self, value, dialect):
        """DB → Python: JSON 문자열을 dict로"""
        if value is not None:
            return json.loads(value)
        return value

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    settings: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
```

```python
from sqlalchemy import event
from sqlalchemy.orm import Session

# mapper 이벤트: Session 레벨 audit log
@event.listens_for(Session, "before_flush")
def _audit_changes(session, flush_context, instances):
    for obj in session.new:
        if hasattr(obj, "__tablename__"):
            print(f"INSERT: {obj.__tablename__}")
    for obj in session.dirty:
        if hasattr(obj, "__tablename__"):
            print(f"UPDATE: {obj.__tablename__}")

# hybrid_property를 SQL WHERE에서 사용
with Session(engine) as session:
    users = session.execute(
        select(User).where(User.full_name == "Alice Kim")
    ).scalars().all()
    # full_name.expression이 SQL 표현을 생성
```

## 변경 전후 비교

**Before: 규칙이 핸들러에 흩어진 패턴**
```text
- 이메일 정규화: 핸들러마다 email.strip().lower() 반복
- 파생 속성: 매번 f"{user.first_name} {user.last_name}" 계산
- TypeDecorator 없이 핸들러에서 json.dumps/loads 반복
- 검증 누락 시 DB에 잘못된 데이터 저장
- SQL WHERE에서 파생 속성 사용 불가
```

**After: 확장점에 규칙을 모은 패턴**
```text
- @validates로 이메일 정규화를 모델에 위임
- hybrid_property로 full_name을 Python과 SQL 양쪽에서 사용
- TypeDecorator로 JSON 변환 자동화
- 어디서 저장해도 @validates 규칙이 적용됨
- WHERE User.full_name == "..." SQL 표현 사용 가능
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 검증 로직을 핸들러에만 둠 | 다른 경로로 저장 시 검증 누락 | `@validates`로 모델에 위임 |
| `hybrid_property` `expression` 누락 | SQL WHERE에서 파생 속성 사용 불가 | `@full_name.expression` 추가 |
| TypeDecorator 없이 핸들러에서 json.dumps | 변환 로직 여러 곳에 중복 | `TypeDecorator`로 자동화 |
| mapper 이벤트 남용 | 추적 어려운 부작용 | 로깅/audit은 이벤트, 검증은 @validates |
| `cache_ok = True` 누락 | TypeDecorator 성능 경고 | `TypeDecorator`에 `cache_ok = True` 설정 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"SQLAlchemy ORM 모델에 이메일 정규화와 full_name 파생 속성을 추가해줘.
@validates로 이메일 소문자 변환 + 형식 검증,
hybrid_property로 first_name + last_name을 Python과 SQL WHERE 양쪽에서 사용,
dict를 JSON으로 저장하는 TypeDecorator 포함"

# AI 결과물 검증 체크포인트:
# - @validates가 핸들러가 아닌 모델에 정의되어 있는가?
# - hybrid_property에 .expression이 정의되어 있는가?
# - TypeDecorator에 cache_ok = True가 설정되어 있는가?
# - 이벤트 리스너가 부작용을 만들지 않는가?
# - 검증/변환 로직이 여러 곳에 중복되어 있는가?
```

## 운영 체크리스트

- [ ] 이메일 정규화, 값 검증 등을 `@validates`로 모델에 위임한다
- [ ] 파생 속성에 `hybrid_property`와 `.expression`을 함께 정의한다
- [ ] 반복되는 타입 변환은 `TypeDecorator`로 자동화한다
- [ ] `TypeDecorator`에 `cache_ok = True`를 설정한다
- [ ] 이벤트 리스너의 부작용을 제한하고 로깅/audit 용도로만 사용한다

## 처음 질문으로 돌아가기

- **`@validates`와 mapper 이벤트의 선택 기준은?** `@validates`는 특정 모델 속성이 설정되는 시점에 검증/변환하는 Python 레벨 훅입니다. mapper 이벤트(`before_insert`, `before_update`)는 Session이 flush하는 시점에 적용됩니다. 특정 속성 검증은 `@validates`, 전체 객체 변화 감지는 mapper 이벤트가 적합합니다.
- **`hybrid_property`가 왜 두 가지를 제공하는가?** Python 코드에서 `user.full_name`처럼 사용할 때는 `@hybrid_property`가 Python 문자열을 반환합니다. `select(User).where(User.full_name == "...")`처럼 SQL WHERE 절에서 사용할 때는 `.expression`이 SQL 표현으로 전환됩니다.
- **확장점의 세 층은 어떻게 선택하는가?** 컬럼 값의 DB 변환은 `TypeDecorator`(타입 층), 속성 검증/파생 계산은 `@validates`/`hybrid_property`(속성 층), 세션/엔진 라이프사이클 훅은 `@event.listens_for`(이벤트 층)에 두세요.

## 정리

바이브코딩에서 AI가 만든 ORM 코드에서 검증 로직이 핸들러에만 있거나, 파생 속성을 SQL에서 사용하지 못하거나, 타입 변환이 여러 곳에 중복되어 있으면 확장점을 활용하세요. 도메인 규칙을 모델 가까이 두면 어느 경로로 저장해도 일관되게 적용됩니다. 다음 글에서는 비동기 SQLAlchemy와 `AsyncSession`을 다룹니다.

## 참고 자료

- [SQLAlchemy 2.x - ORM Events](https://docs.sqlalchemy.org/en/20/orm/events.html)
- [SQLAlchemy 2.x - Hybrid Attributes](https://docs.sqlalchemy.org/en/20/orm/extensions/hybrid.html)
- [SQLAlchemy 2.x - Custom Types](https://docs.sqlalchemy.org/en/20/core/custom_types.html)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/sqlalchemy-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 SQLAlchemy 기초 (1/10): Engine과 Connection
- 바이브코딩을 위한 SQLAlchemy 기초 (2/10): MetaData와 Schema
- 바이브코딩을 위한 SQLAlchemy 기초 (3/10): Core CRUD
- 바이브코딩을 위한 SQLAlchemy 기초 (4/10): ORM 모델 정의
- 바이브코딩을 위한 SQLAlchemy 기초 (5/10): Session과 Unit of Work
- 바이브코딩을 위한 SQLAlchemy 기초 (6/10): 관계 매핑
- 바이브코딩을 위한 SQLAlchemy 기초 (7/10): 로딩 전략과 N+1
- **바이브코딩을 위한 SQLAlchemy 기초 (8/10): 이벤트와 확장점 (현재 글)**
- 바이브코딩을 위한 SQLAlchemy 기초 (9/10): 비동기 SQLAlchemy
- 바이브코딩을 위한 SQLAlchemy 기초 (10/10): 프로덕션 패턴
<!-- toc:end -->

Tags: 바이브코딩, SQLAlchemy, Python, ORM, HybridProperty
