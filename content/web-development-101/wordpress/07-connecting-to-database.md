---
series: web-development-101
episode: 7
title: "바이브코딩을 위한 웹 개발 기초 (7/10): 데이터베이스 연결"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - 웹개발
  - 데이터베이스
  - SQL
  - ORM
  - 백엔드
seo_description: 바이브코딩으로 만드는 웹앱에서 데이터베이스를 안전하게 연결하고 사용하는 방법을 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 웹 개발 기초 (7/10): 데이터베이스 연결

이 글은 **바이브코딩을 위한 웹 개발 기초** 시리즈의 일곱 번째 글입니다. AI에게 웹앱을 만들어달라고 요청하기 전에, 웹이 실제로 어떻게 동작하는지 알아야 합니다.

---

바이브코딩으로 데이터를 저장하는 기능을 만들 때 가장 많이 놓치는 것이 보안입니다. AI가 만들어준 데이터베이스 코드에 SQL 쿼리를 문자열로 이어 붙이는 방식이 있다면, 그것은 SQL injection 취약점입니다. 사용자가 입력한 값을 쿼리에 직접 넣으면 공격자가 데이터베이스 전체를 삭제할 수 있습니다.

웹앱은 화면만으로 끝나지 않습니다. 사용자 정보, 게시글, 주문 기록처럼 남아야 하는 데이터는 결국 데이터베이스에 들어갑니다. AI가 데이터베이스 코드를 만들어줘도, 그 코드가 안전한지, 효율적인지 판단하려면 기본 원리를 알아야 합니다. SQL의 기본 구조, 파라미터 바인딩, ORM의 역할, 트랜잭션이 무엇인지 이해하면 AI와의 협업이 훨씬 안전해집니다.

이 글에서는 SQL 기본 작업, SQL injection 방어, ORM의 편리함과 한계, 트랜잭션의 필요성을 바이브코딩 관점에서 정리합니다.

> 데이터베이스 연결은 웹앱의 거의 모든 요청이 통과하는 핵심 경로입니다. 바이브코딩으로 받은 코드에서 SQL 문자열 이어 붙이기가 보이면, 그것은 즉시 고쳐야 하는 보안 취약점입니다.

## 이 글에서 다룰 문제

- 웹앱은 왜 파일이 아니라 데이터베이스를 쓸까요?
- SQL injection이란 무엇이고 어떻게 막을까요?
- ORM은 어디서 편하고 어디서 한계가 생길까요?
- 트랜잭션은 언제 필요할까요?
- 바이브코딩 중 데이터베이스 관련 보안 실수를 어떻게 막을까요?

## 바이브코딩 관점: 데이터베이스를 알아야 하는 이유

AI에게 "사용자가 입력한 이름으로 검색하는 기능 만들어줘"라고 하면 이런 코드가 나올 수 있습니다.

```python
# 위험한 코드 — AI가 생성할 수 있는 패턴
name = request.args.get("name")
query = f"SELECT * FROM users WHERE name = '{name}'"
```

사용자가 `name`에 `' OR '1'='1`을 입력하면 모든 사용자 데이터가 노출됩니다. `'; DROP TABLE users; --`을 입력하면 테이블이 삭제됩니다. 이 위험을 알고 AI에게 "파라미터 바인딩을 사용해줘"라고 요청할 수 있어야 합니다.

## 먼저 알아둘 용어

- **SQL**: 관계형 데이터베이스와 대화하는 언어입니다.
- **Schema**: 테이블의 컬럼과 타입 같은 구조 정의입니다.
- **ORM**: SQL과 객체 세계를 이어 주는 도구입니다.
- **파라미터 바인딩**: 사용자 입력을 쿼리 구조와 분리해 안전하게 처리하는 방법입니다.
- **Transaction**: 여러 쓰기 작업을 하나의 단위로 묶는 장치입니다.

## Before / After: 안전한 저장 방식

**Before — 파일에 기록 (동시성 문제)**

```python
open("users.txt", "a").write("alice\n")
# 여러 요청이 동시에 쓰면 데이터가 꼬입니다
```

**After — DB에 파라미터 바인딩으로 기록**

```python
import sqlite3
con = sqlite3.connect("app.db")
con.execute("INSERT INTO users(name) VALUES (?)", ("alice",))
con.commit()
```

`?` 자리표시자를 쓰면 사용자 입력이 SQL 구조가 아닌 데이터로만 처리됩니다.

## 데이터베이스를 다섯 단계로 다뤄 보기

### 1단계 — 테이블 만들기

```python
import sqlite3
con = sqlite3.connect("app.db")
con.execute("""
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE
)
""")
con.commit()
```

### 2단계 — 넣고 읽기

```python
con.execute("INSERT INTO users(name, email) VALUES (?, ?)", ("alice", "a@x.com"))
con.commit()
for row in con.execute("SELECT id, name FROM users"):
    print(row)
```

### 3단계 — SQL injection 방어

```python
# 공격자 입력이 들어와도 안전
name = "alice'; DROP TABLE users; --"
rows = con.execute("SELECT * FROM users WHERE name = ?", (name,))
# 이 name은 데이터로만 처리됩니다
```

### 4단계 — ORM 사용하기

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

engine = create_engine("sqlite:///app.db")
Base.metadata.create_all(engine)
S = sessionmaker(bind=engine)
s = S()
s.add(User(name="bob"))
s.commit()
```

### 5단계 — 트랜잭션으로 묶기

```python
con = sqlite3.connect("app.db")
try:
    con.execute("BEGIN")
    con.execute("UPDATE users SET name='ALICE' WHERE id=1")
    con.execute("INSERT INTO users(name) VALUES ('charlie')")
    con.commit()
except Exception:
    con.rollback()
    raise
```

두 작업이 모두 성공해야 하거나, 하나라도 실패하면 둘 다 취소해야 할 때 트랜잭션을 씁니다.

## 바이브코딩에서 자주 나오는 실수

| 실수 | 원인 | 올바른 이해 |
|------|------|-------------|
| f-string으로 SQL 쿼리 조합 | SQL injection 모름 | `?` 파라미터 바인딩 필수 |
| 요청마다 새 DB 연결 생성 | 연결 비용 무지 | 연결 풀 또는 앱 레벨 연결 재사용 |
| 인덱스 없이 큰 테이블 조회 | 성능 무지 | 자주 조회하는 컬럼에 인덱스 추가 |
| 트랜잭션 없이 여러 쓰기 연속 | 무결성 개념 부재 | 관련된 쓰기는 하나의 트랜잭션으로 |
| ORM이 생성하는 SQL 무시 | ORM 맹신 | 로그로 생성 SQL 확인 습관 필요 |

## AI 팁: 안전한 데이터베이스 코드 요청 방법

```
"사용자 검색 기능을 만들어줘. 다음 사항을 반드시 지켜줘:
1. SQL 쿼리에 사용자 입력을 직접 넣지 말고 파라미터 바인딩 사용
2. ORM을 쓴다면 raw SQL을 쓸 때도 바인딩 유지
3. 데이터베이스 연결은 앱 시작 시 한 번만 열거나 연결 풀 사용
4. 여러 쓰기 작업이 있으면 트랜잭션으로 묶기"
```

## 체크리스트

- [ ] SQL injection이 무엇인지 설명할 수 있습니다.
- [ ] 파라미터 바인딩을 항상 사용해야 함을 알고 있습니다.
- [ ] 연결 풀이 무엇인지 설명할 수 있습니다.
- [ ] 트랜잭션을 사용하는 코드를 읽을 수 있습니다.
- [ ] ORM이 만든 SQL을 로그로 확인할 수 있습니다.

## 처음 질문으로 돌아가기

- **웹앱은 왜 파일이 아니라 데이터베이스를 쓸까요?**
  데이터베이스는 동시 접근, 제약 조건, 트랜잭션을 함께 다룹니다. 파일에 문자열을 추가하는 방식은 여러 요청이 동시에 올 때 데이터가 꼬입니다.

- **SQL injection이란 무엇이고 어떻게 막을까요?**
  사용자 입력이 SQL 쿼리의 일부로 실행되는 공격입니다. 파라미터 바인딩(`?` 자리표시자)을 사용하면 입력값이 데이터로만 처리됩니다.

- **트랜잭션은 언제 필요할까요?**
  여러 쓰기 작업이 모두 성공해야 의미 있는 경우입니다. 예를 들어 주문 생성과 재고 감소가 동시에 되어야 할 때, 하나가 실패하면 둘 다 취소해야 합니다.

## 정리

데이터베이스 연결은 바이브코딩에서 SQL injection과 성능 문제가 가장 많이 나오는 영역입니다. AI가 만들어준 코드에서 f-string으로 SQL을 조합하는 패턴이 보이면 즉시 파라미터 바인딩으로 교체를 요청해야 합니다. 다음 글에서는 이렇게 만든 앱을 실제 환경에 올리는 배포를 다룹니다.

## 참고 자료

- [sqlite3 — DB-API 2.0 interface for SQLite databases](https://docs.python.org/3/library/sqlite3.html)
- [SQLAlchemy ORM Quick Start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [SQL injection (OWASP)](https://owasp.org/www-community/attacks/SQL_Injection)
- [EXPLAIN QUERY PLAN (SQLite)](https://www.sqlite.org/eqp.html)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 웹 개발 기초 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [바이브코딩을 위한 웹 개발 기초 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [바이브코딩을 위한 웹 개발 기초 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [바이브코딩을 위한 웹 개발 기초 (4/10): HTTP와 API](./04-http-and-api.md)
- [바이브코딩을 위한 웹 개발 기초 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- [바이브코딩을 위한 웹 개발 기초 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- **바이브코딩을 위한 웹 개발 기초 (7/10): 데이터베이스 연결 (현재 글)**
- [바이브코딩을 위한 웹 개발 기초 (8/10): 배포](./08-deployment.md)
- [바이브코딩을 위한 웹 개발 기초 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- [바이브코딩을 위한 웹 개발 기초 (10/10): 작은 웹앱 만들기](./10-building-a-small-web-app.md)

<!-- toc:end -->

Tags: 바이브코딩, 웹개발, 데이터베이스, SQL, ORM, 백엔드
