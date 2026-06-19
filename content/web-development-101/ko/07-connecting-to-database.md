---
series: web-development-101
episode: 7
title: "Web Development 101 (7/10): 데이터베이스 연결"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/209"
    published_at: '2026-05-26'
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - WebDevelopment
  - Database
  - SQL
  - ORM
  - Backend
seo_description: SQL, ORM, 연결 풀, 트랜잭션으로 데이터베이스 연결을 설명합니다.
last_reviewed: '2026-05-15'
---

# Web Development 101 (7/10): 데이터베이스 연결

웹앱은 화면만으로 끝나지 않습니다. 사용자 정보, 게시글, 주문, 결제 기록처럼 남아야 하는 데이터는 결국 데이터베이스에 들어갑니다. 서버가 메모리만 믿고 있으면 프로세스가 재시작되는 순간 상태가 사라집니다. 그래서 웹앱에서 데이터베이스 연결은 거의 항상 핵심 경로입니다.

이 글은 Web Development 101 시리즈의 7번째 글입니다.

여기서는 SQL의 기본 작업, ORM의 역할, 연결과 연결 풀, 트랜잭션이 왜 필요한지 정리하면서 웹앱이 데이터를 오래 보관하는 방식을 봅니다.

![Web Development 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/07/07-01-concept-at-a-glance.ko.png)
*Web Development 101 7장 흐름 개요*

> 데이터베이스 연결은 웹앱의 거의 모든 요청이 통과하는 핵심 경로입니다 — SQL·ORM·연결 풀·트랜잭션은 각각 '무엇을 묻는가·어떻게 묻는가·연결을 어떻게 재사용하는가·실패 시 어디로 되돌리는가'라는 다른 문제를 답합니다.

## 이 글에서 다룰 문제

- 웹앱은 왜 파일이 아니라 데이터베이스를 쓸까요?
- SQL의 네 가지 기본 작업은 무엇일까요?
- ORM은 어디서 편하고 어디서 한계가 생길까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 주제가 중요한가

웹앱의 거의 모든 상태는 데이터베이스에 있습니다. 사용자 수가 조금만 늘어나도 연결을 잘못 다루는 서버는 금방 느려지거나 멈춥니다. 반대로 데이터 모델과 연결 관리 감각이 있으면 기능을 추가할 때 구조가 훨씬 안정적입니다.

## 웹앱과 데이터베이스의 관계

```
사용자 요청
    |
    v
웹 서버 (Flask/Django/Node.js)
    |
    v  Connection Pool에서 연결 하나 가져옴
데이터베이스 드라이버
    |  SQL 쿼리 전송
    v
데이터베이스 서버 (SQLite/PostgreSQL/MySQL)
    |
    v  결과 반환
웹 서버 → 응답 생성 → 사용자
    |
    v  연결을 Pool에 반납
Connection Pool (연결 재사용)
```

연결(Connection)을 여는 것은 비용이 큰 작업입니다. TCP 핸드쉐이크, 인증, 리소스 할당이 포함됩니다. 연결 풀은 미리 만든 연결을 재사용해 이 비용을 줄입니다.

## 먼저 알아둘 용어

- **SQL**: 관계형 데이터베이스와 대화하는 선언형 언어입니다.
- **Schema**: 테이블의 컬럼과 타입 같은 구조 정의입니다.
- **CRUD**: Create, Read, Update, Delete — 기본 데이터 작업 4가지입니다.
- **ORM**: SQL과 객체 세계를 이어 주는 도구입니다.
- **Connection Pool**: 미리 열어 둔 DB 연결의 재사용 집합입니다.
- **Transaction**: 여러 쓰기 작업을 하나의 원자 단위로 묶는 장치입니다.

## 스키마 설계와 테이블 생성

```sql
-- 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT    NOT NULL UNIQUE,
  email    TEXT    NOT NULL UNIQUE,
  password TEXT    NOT NULL,          -- bcrypt hash 저장
  role     TEXT    NOT NULL DEFAULT 'user',
  created_at TEXT  NOT NULL DEFAULT (datetime('now'))
);

-- 게시글 테이블 (users에 대한 외래 키)
CREATE TABLE IF NOT EXISTS posts (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title      TEXT    NOT NULL,
  body       TEXT    NOT NULL,
  created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- 조회 패턴에 맞는 인덱스
CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at DESC);
```

스키마를 먼저 그리면 이후 코드 구조도 따라옵니다. 컬럼 제약(`NOT NULL`, `UNIQUE`, `DEFAULT`)을 초기에 정의해 두면 애플리케이션 레이어의 검증 부담이 줄어듭니다.

## CRUD 기본 작업

```python
import sqlite3

def get_db():
    con = sqlite3.connect("app.db")
    con.row_factory = sqlite3.Row  # 컬럼 이름으로 접근 가능
    return con

# CREATE
def create_post(user_id: int, title: str, body: str) -> int:
    with get_db() as con:
        cur = con.execute(
            "INSERT INTO posts(user_id, title, body) VALUES (?, ?, ?)",
            (user_id, title, body)
        )
        return cur.lastrowid

# READ (단건)
def get_post(post_id: int) -> dict | None:
    con = get_db()
    row = con.execute(
        "SELECT p.*, u.username FROM posts p JOIN users u ON u.id = p.user_id WHERE p.id = ?",
        (post_id,)
    ).fetchone()
    return dict(row) if row else None

# READ (목록, 페이지네이션)
def list_posts(limit: int = 20, offset: int = 0) -> list:
    con = get_db()
    rows = con.execute(
        "SELECT id, title, created_at FROM posts ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset)
    ).fetchall()
    return [dict(r) for r in rows]

# UPDATE
def update_post(post_id: int, title: str, body: str) -> bool:
    with get_db() as con:
        cur = con.execute(
            "UPDATE posts SET title = ?, body = ? WHERE id = ?",
            (title, body, post_id)
        )
        return cur.rowcount > 0

# DELETE
def delete_post(post_id: int) -> bool:
    with get_db() as con:
        cur = con.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        return cur.rowcount > 0
```

## SQL Injection 방어

```python
# 위험: 문자열 연결로 SQL 생성
name = "alice'; DROP TABLE users; --"
sql = f"SELECT * FROM users WHERE name = '{name}'"
# 실행되는 SQL: SELECT * FROM users WHERE name = 'alice'; DROP TABLE users; --

# 안전: 파라미터 바인딩
con.execute("SELECT * FROM users WHERE name = ?", (name,))
# DB 드라이버가 name을 값으로만 처리, SQL 구조 변경 불가
```

파라미터 바인딩은 웹 개발에서 가장 기본적인 보안 원칙 중 하나입니다. ORM을 쓰면 기본적으로 바인딩을 사용하지만, raw SQL을 쓸 때는 반드시 `?` 또는 `%s` 플레이스홀더를 사용해야 합니다.

## ORM 사용하기

```python
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(200), nullable=False, unique=True)
    posts = relationship("Post", back_populates="author", cascade="all, delete")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    author = relationship("User", back_populates="posts")

engine = create_engine("sqlite:///app.db", echo=True)  # echo=True: SQL 로그 출력
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# 사용
with Session() as session:
    user = User(username="alice", email="alice@example.com", password="hashed")
    session.add(user)
    session.commit()

    # 조회
    posts = session.query(Post).filter(Post.user_id == user.id).all()

    # N+1 문제 방지: eager loading
    from sqlalchemy.orm import joinedload
    posts_with_author = (
        session.query(Post)
        .options(joinedload(Post.author))
        .order_by(Post.created_at.desc())
        .limit(20)
        .all()
    )
    # 위: JOIN으로 한 번에 조회 (N+1 방지)
```

## 트랜잭션

```python
# 예시: 계좌 이체 (원자적으로 처리해야 함)
def transfer_balance(from_user_id: int, to_user_id: int, amount: int) -> bool:
    with get_db() as con:
        try:
            con.execute("BEGIN")

            # 잔액 확인
            from_bal = con.execute(
                "SELECT balance FROM accounts WHERE user_id = ?", (from_user_id,)
            ).fetchone()["balance"]

            if from_bal < amount:
                con.rollback()
                return False

            # 차감
            con.execute(
                "UPDATE accounts SET balance = balance - ? WHERE user_id = ?",
                (amount, from_user_id)
            )
            # 증가
            con.execute(
                "UPDATE accounts SET balance = balance + ? WHERE user_id = ?",
                (amount, to_user_id)
            )

            con.commit()
            return True

        except Exception:
            con.rollback()
            raise
```

트랜잭션 없이 두 UPDATE 사이에 서버가 죽으면 차감만 되고 증가가 안 된 상태가 영구히 남습니다. 트랜잭션은 "전부 성공하거나 전부 실패"를 보장합니다.

## N+1 쿼리 문제

```python
# N+1 문제 (나쁜 예)
posts = db.execute("SELECT * FROM posts LIMIT 20").fetchall()
for post in posts:
    # 포스트마다 별도 쿼리 → 20개 포스트면 1 + 20 = 21번 쿼리
    author = db.execute(
        "SELECT username FROM users WHERE id = ?", (post["user_id"],)
    ).fetchone()
    print(post["title"], "by", author["username"])

# 해결: JOIN으로 한 번에
posts_with_authors = db.execute("""
    SELECT p.id, p.title, u.username as author_name
    FROM posts p
    JOIN users u ON u.id = p.user_id
    ORDER BY p.created_at DESC
    LIMIT 20
""").fetchall()
```

## EXPLAIN으로 쿼리 성능 분석

```sql
-- SQLite
EXPLAIN QUERY PLAN
SELECT * FROM posts WHERE user_id = 1 ORDER BY created_at DESC;

-- 인덱스 없을 때: SCAN TABLE posts (전체 스캔)
-- 인덱스 있을 때: SEARCH TABLE posts USING INDEX idx_posts_user_id

-- PostgreSQL
EXPLAIN ANALYZE
SELECT * FROM posts WHERE user_id = 1 ORDER BY created_at DESC;
```

인덱스는 조회 패턴을 먼저 파악하고 추가해야 합니다. 아무 컬럼에나 인덱스를 달면 INSERT/UPDATE 비용이 증가합니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|------|------|-------------|
| 문자열 연결로 SQL 생성 | SQL injection 취약점 | 파라미터 바인딩 (`?` 플레이스홀더) |
| 요청마다 새 DB 연결 열기 | 연결 비용 누적, 연결 수 초과 | Connection Pool 사용 |
| 인덱스 없이 대용량 조회 | 전체 테이블 스캔으로 느림 | EXPLAIN으로 확인 후 인덱스 추가 |
| 트랜잭션 없이 여러 쓰기 | 절반만 반영된 데이터 남음 | 관련 쓰기를 하나의 트랜잭션으로 |
| N+1 쿼리 방치 | 트래픽 증가 시 DB 과부하 | JOIN 또는 IN 쿼리로 묶기 |
| ORM이 만든 SQL을 확인 안 함 | 예상치 못한 쿼리 패턴 발생 | `echo=True` 또는 DB 로그로 확인 |

## 운영에서는 이렇게 보입니다

많은 웹 백엔드는 PostgreSQL이나 MySQL과 ORM을 함께 씁니다. 트래픽이 늘면 읽기 복제본, Redis 캐시, 마이그레이션 도구가 등장하지만, 그 위에서도 연결 풀과 트랜잭션은 그대로 중요합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 스키마를 먼저 그립니다.
- 인덱스는 조회 패턴을 보고 추가합니다.
- 트랜잭션 경계를 명시적으로 둡니다.
- N+1 query 가능성을 늘 의심합니다.
- 스키마 변경은 migration tool로 추적합니다.

## 운영 체크리스트

- [ ] SQL의 네 가지 기본 작업을 알고 있습니다.
- [ ] 항상 파라미터 바인딩을 사용해야 함을 알고 있습니다.
- [ ] 연결 풀이 무엇인지 설명할 수 있습니다.
- [ ] 트랜잭션을 사용하는 코드를 읽을 수 있습니다.
- [ ] ORM이 만든 SQL을 로그로 확인할 수 있습니다.

## 연습 문제

1. SQLite로 `posts` 테이블을 만들고 CRUD를 모두 구현해 보세요.
2. 같은 작업을 ORM으로 다시 작성하고 실제 생성되는 SQL을 로그로 확인해 보세요.
3. 트랜잭션 안에서 예외를 일부러 발생시켜 rollback이 되는지 검증해 보세요.

## 정리와 다음 글

데이터베이스는 웹앱의 진실을 오래 보관하는 저장소입니다. SQL, 연결, 연결 풀, 트랜잭션 감각이 있어야 기능이 늘어나도 데이터가 버텨 줍니다. 다음 글에서는 이렇게 만든 앱을 실제 환경에 올리는 배포를 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Web Development 101 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [Web Development 101 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [Web Development 101 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [Web Development 101 (4/10): HTTP와 API](./04-http-and-api.md)
- [Web Development 101 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- [Web Development 101 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- **Web Development 101 (7/10): 데이터베이스 연결 (현재 글)**
- [Web Development 101 (8/10): 배포](./08-deployment.md)
- [Web Development 101 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- [작은 웹앱 만들기](./10-building-a-small-web-app.md)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [sqlite3 — DB-API 2.0 interface for SQLite databases](https://docs.python.org/3/library/sqlite3.html)
- [SQLAlchemy ORM Quick Start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [Transaction (Wikipedia)](https://en.wikipedia.org/wiki/Database_transaction)

### 검증용 자료
- [SQL injection (OWASP)](https://owasp.org/www-community/attacks/SQL_Injection)
- [EXPLAIN QUERY PLAN (SQLite)](https://www.sqlite.org/eqp.html)

- [web-development-101 예제 코드 저장소 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/web-development-101/ko)

Tags: Computer Science, WebDevelopment, Database, SQL, ORM, Backend
