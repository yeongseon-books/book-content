---
series: web-development-101
episode: 7
title: "Web Development 101 (7/10): 데이터베이스 연결"
status: publish-ready
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

## 먼저 던지는 질문

- 웹앱은 왜 파일이 아니라 데이터베이스를 쓸까요?
- SQL의 네 가지 기본 작업은 무엇일까요?
- ORM은 어디서 편하고 어디서 한계가 생길까요?

## 왜 이 주제가 중요한가

웹앱의 거의 모든 상태는 데이터베이스에 있습니다. 사용자 수가 조금만 늘어나도 연결을 잘못 다루는 서버는 금방 느려지거나 멈춥니다. 반대로 데이터 모델과 연결 관리 감각이 있으면 기능을 추가할 때 구조가 훨씬 안정적입니다.

이 지식은 오래 갑니다. Python에서 SQLite를 다루든, PostgreSQL과 SQLAlchemy를 쓰든, Java나 Go로 옮기든 기본 원리는 크게 달라지지 않습니다. SQL, 연결, 트랜잭션, 인덱스라는 바닥 구조는 계속 남습니다.

## 한눈에 보는 개념 지도

애플리케이션은 요청마다 데이터를 읽고 쓰지만 연결 자체는 비싼 자원입니다. 그래서 연결 풀을 두고, 여러 SQL 작업이 하나의 비즈니스 작업이면 트랜잭션으로 묶습니다.

### 직접 검증해 볼 포인트

- SQLite로 테이블을 만든 뒤 INSERT와 SELECT가 실제 파일에 영속적으로 남는지 확인합니다.
- 공격자 입력 문자열을 파라미터 바인딩으로 넘겨도 쿼리 구조가 깨지지 않는지 검증합니다.
- 트랜잭션 중간에 예외를 발생시켜 rollback 뒤 데이터가 이전 상태로 남는지 봅니다.

**기대 결과:** 바인딩을 쓰면 악성 문자열도 값으로만 처리되고, rollback 뒤에는 절반만 반영된 데이터가 남지 않습니다.

**실패 모드:** 문자열 연결로 SQL을 만들면 injection 위험이 생깁니다. 요청마다 연결을 새로 열면 트래픽이 늘 때 연결 비용이 먼저 병목이 됩니다.

## 먼저 알아둘 용어

- **SQL**: 관계형 데이터베이스와 대화하는 언어입니다.
- **Schema**: 테이블의 컬럼과 타입 같은 구조 정의입니다.
- **ORM**: SQL과 객체 세계를 이어 주는 도구입니다.
- **Connection**: 애플리케이션과 데이터베이스 사이의 통신 채널입니다.
- **Transaction**: 여러 쓰기 작업을 하나의 단위로 묶는 장치입니다.

## 전후 비교로 보는 저장 방식

**Before (파일에 기록)**

```python
open("users.txt", "a").write("alice\n")  # 동시 접근이 겹치면 깨집니다
```

**After (DB에 기록)**

```python
import sqlite3
con = sqlite3.connect("app.db")
con.execute("INSERT INTO users(name) VALUES (?)", ("alice",))
con.commit()
```

데이터베이스는 동시성, 제약 조건, 영속성을 함께 다룹니다. 파일에 문자열을 덧붙이는 방식보다 훨씬 안정적입니다.

## 작은 데이터베이스를 다섯 단계로 다뤄 보기

### 1단계 — 테이블 만들기

```python
# 1_init.py
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

테이블은 데이터 구조를 고정합니다. `name`은 비어 있으면 안 되고, `email`은 중복되면 안 된다는 제약도 함께 정의합니다.

### 2단계 — 넣고 읽기

```python
# 2_crud.py
import sqlite3
con = sqlite3.connect("app.db")
con.execute("INSERT INTO users(name, email) VALUES (?, ?)", ("alice", "a@x.com"))
con.commit()
for row in con.execute("SELECT id, name FROM users"):
    print(row)
```

여기서 `INSERT`와 `SELECT`가 가장 기본적인 쓰기와 읽기입니다. 이후 `UPDATE`, `DELETE`까지 합치면 흔히 CRUD라고 부르는 작업이 완성됩니다.

### 3단계 — 파라미터 바인딩으로 SQL injection 막기

```python
name = "alice'; DROP TABLE users; --"  # 공격자 입력
con.execute("SELECT * FROM users WHERE name = ?", (name,))  # 안전
```

입력값을 문자열로 이어 붙이지 않고 파라미터로 넘겨야 합니다. 이 한 가지 원칙만 지켜도 SQL injection 위험을 크게 줄일 수 있습니다.

### 4단계 — ORM 사용하기

```python
# 4_orm.py
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

ORM은 객체 중심 코드를 쓰게 도와주지만, 내부에서 어떤 SQL이 생성되는지는 계속 의식해야 합니다.

### 5단계 — 트랜잭션 묶기

```python
# 5_tx.py
import sqlite3
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

여러 변경이 함께 성공해야 할 때 트랜잭션이 필요합니다. 중간에 하나라도 실패하면 전체를 되돌려야 데이터가 어중간하게 남지 않습니다.

## 이 코드에서 먼저 봐야 할 점

- 파라미터 바인딩 없는 SQL은 언젠가 반드시 사고를 부릅니다.
- ORM은 편리하지만 생성된 SQL을 읽을 줄 알아야 합니다.
- 트랜잭션은 단일 문장이 아니라 비즈니스 단위를 감싸는 경우가 많습니다.

## 여기서 자주 헷갈립니다

1. **문자열을 이어 붙여 SQL을 만드는 경우**: SQL injection 위험이 생깁니다.
2. **요청마다 새 연결을 마구 여는 경우**: 연결 풀이 없으면 부하에 약해집니다.
3. **인덱스 없이 큰 조회를 반복하는 경우**: 읽기 성능이 급격히 떨어집니다.
4. **트랜잭션 없이 여러 쓰기를 이어 붙이는 경우**: 절반만 반영된 상태가 남을 수 있습니다.
5. **오류를 삼키는 경우**: 데이터 무결성 문제를 놓치기 쉽습니다.

## 운영에서는 이렇게 보입니다

많은 웹 백엔드는 PostgreSQL이나 MySQL과 ORM을 함께 씁니다. 트래픽이 늘면 읽기 복제본, Redis 캐시, 마이그레이션 도구가 등장하지만, 그 위에서도 연결 풀과 트랜잭션은 그대로 중요합니다. 결국 모든 확장은 이 기본기를 더 큰 규모에서 반복하는 일에 가깝습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 스키마를 먼저 그립니다.
- 인덱스는 조회 패턴을 보고 추가합니다.
- 트랜잭션 경계를 명시적으로 둡니다.
- N+1 query 가능성을 늘 의심합니다.
- 스키마 변경은 migration tool로 추적합니다.

## 체크리스트

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

## HTTP-인증-배포를 함께 검증하는 점검 루틴

웹 서비스는 단일 기능이 아니라 경로 전체의 안정성으로 평가됩니다. 따라서 API 스펙, 인증 예외, 배포 헬스체크를 같은 릴리스 체크리스트로 묶는 편이 안전합니다.

```text
배포 전 점검
1) 핵심 API 3개에 대해 상태 코드/응답 스키마 계약 테스트 실행
2) access 만료, refresh 만료, revoke 토큰 시나리오 재현
3) /health, /ready 엔드포인트를 배포 환경에서 실제 호출
4) CDN/브라우저 캐시 무효화 정책 확인
```

### 장애 예방을 위한 최소 헤더 정책

```http
Cache-Control: no-store
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
```

헤더 정책은 프론트엔드 코드 변경 없이도 보안/캐시 동작을 크게 바꿉니다. 기능 개발과 별개로 표준 헤더를 고정해 두면 릴리스 변동성이 줄어듭니다.

### 배포 후 15분 관찰 항목

- 5xx 비율과 p95 지연 시간의 급격한 상승 여부
- 로그인 성공률, 토큰 재발급 성공률
- 정적 자산 404 발생률

이 루틴을 반복하면 "배포는 되었지만 정상 운영은 아닌" 상태를 초기에 감지할 수 있습니다.

## 실전 앵커 모음: 데이터 무결성을 운영 문서로 바꾸기

작은 기능이라도 운영 단계까지 생각하면 문서화 기준이 달라집니다. 아래 예시는 팀이 기능 구현과 동시에 남겨 두면 바로 도움이 되는 최소 산출물입니다. 특히 요청/응답 계약, 세션/쿠키 정책, SQL 기준 쿼리, 배포 설정, 캐시 규칙을 함께 기록하면 변경 시점의 실패 반경을 크게 줄일 수 있습니다.

### HTTP 요청/응답 계약 예시

```http
GET /api/v1/todos?limit=20&cursor=todo_120 HTTP/1.1
Host: api.example.com
Accept: application/json
Authorization: Bearer <access_token>
X-Request-Id: req-2026-05-21-0001
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: private, max-age=30
ETag: "todo-list-v42"

{
  "items": [
    {"id": "todo_121", "text": "문서 작성", "done": false},
    {"id": "todo_122", "text": "테스트 실행", "done": true}
  ],
  "next_cursor": "todo_122"
}
```

응답 예시는 상태 코드만 맞추는 수준에서 끝내지 말고, 캐시 정책과 추적 ID를 함께 포함하는 편이 좋습니다. 특히 `X-Request-Id`를 표준화하면 장애 시점에 브라우저 로그와 서버 로그를 빠르게 결합할 수 있습니다.

### REST API 설계 스케치

```text
GET    /api/v1/todos            목록 조회
POST   /api/v1/todos            항목 생성
PATCH  /api/v1/todos/{id}       항목 일부 수정(done 토글 등)
DELETE /api/v1/todos/{id}       항목 삭제
```

리소스 이름은 복수형으로 고정하고, 동작은 method로 분리하는 편이 유지보수에 유리합니다. 예를 들어 `/toggleTodo`처럼 동사형 엔드포인트를 늘리기 시작하면 권한 정책과 감사 로그 규칙이 빠르게 파편화됩니다.

### 세션/쿠키 정책 코드 예시

```python
from flask import Flask, session, jsonify

app = Flask(__name__)
app.secret_key = "change-me"
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

@app.get("/api/v1/me")
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(error={"code": "UNAUTHORIZED"}), 401
    return jsonify(user_id=user_id)
```

인증은 로그인 성공 시점보다 실패 시점 설계가 더 중요합니다. 어떤 경우에 401을 돌리고, 어떤 경우에 403을 돌릴지 미리 고정해 두어야 프론트엔드 재시도 정책과 알림 문구가 안정됩니다.

### SQL 기준 쿼리와 인덱스 예시

```sql
CREATE TABLE IF NOT EXISTS todo_items (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  text TEXT NOT NULL,
  done INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_todo_user_created
ON todo_items(user_id, created_at DESC);

SELECT id, text, done, created_at
FROM todo_items
WHERE user_id = ?
ORDER BY created_at DESC
LIMIT 20;
```

조회 패턴을 먼저 적고 그다음 인덱스를 정의하면 불필요한 인덱스 폭증을 피할 수 있습니다. 특히 쓰기 비중이 높은 서비스에서는 인덱스를 한 개 추가할 때마다 INSERT 비용이 늘어난다는 점을 함께 기록해야 합니다.

### 배포 설정과 헬스 체크 예시

```yaml
services:
  api:
    image: ghcr.io/example/todo-api:1.0.0
    environment:
      - APP_ENV=production
      - DATABASE_URL=postgresql://app:***@db:5432/todo
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

배포 문서에는 반드시 "성공 기준"을 남겨야 합니다. 예를 들어 `/health`가 200을 반환하고, 배포 후 15분 동안 5xx 비율이 1% 미만이며, 로그인 성공률이 평시 대비 하락하지 않는지를 체크리스트로 고정하면 릴리스 판단이 사람마다 달라지지 않습니다.

### 캐시 전략 표준 예시

```http
Cache-Control: public, max-age=31536000, immutable
```

정적 자산은 파일명에 해시를 넣고 장기 캐시를 적용하는 편이 안전합니다. 반대로 사용자별 데이터는 `private` 또는 `no-store` 정책을 명시해 캐시 오염을 방지해야 합니다. 이 구분을 코드 리뷰 항목으로 올려 두면 보안 이슈와 성능 이슈를 동시에 예방할 수 있습니다.

### 운영 체크리스트

- 요청/응답 샘플에 상태 코드, 헤더, 오류 본문 형식을 모두 기록합니다.
- 인증 실패(401), 권한 실패(403), 입력 오류(400) 경계를 API 문서에 고정합니다.
- 핵심 SQL 쿼리 3개를 선정해 `EXPLAIN` 결과를 릴리스마다 비교합니다.
- 배포 후 15분 관측 지표(5xx, p95, 로그인 성공률)를 팀 표준으로 유지합니다.
- 캐시 정책 변경 시 무효화 전략과 롤백 절차를 같은 PR에 포함합니다.

## 처음 질문으로 돌아가기

- **웹앱은 왜 파일이 아니라 데이터베이스를 쓸까요?**
  - `open("users.txt", "a")`처럼 파일에 문자열을 덧붙이는 방식은 동시 접근과 제약 조건, 영속성 관리에 취약합니다. 반면 SQLite 예제처럼 테이블과 `NOT NULL`, `UNIQUE` 제약, `commit()`을 함께 쓰면 프로세스가 다시 떠도 데이터와 규칙이 안정적으로 남습니다.
- **SQL의 네 가지 기본 작업은 무엇일까요?**
  - 글에서 보여 준 `INSERT`와 `SELECT`에 더해 `UPDATE`, `DELETE`를 합치면 CRUD 네 가지 기본 작업이 됩니다. 특히 `VALUES (?, ?)`처럼 파라미터 바인딩을 써야 입력값이 값으로만 처리되고 쿼리 구조가 깨지지 않습니다.
- **ORM은 어디서 편하고 어디서 한계가 생길까요?**
  - SQLAlchemy의 `User` 모델과 `sessionmaker` 예제처럼 ORM은 객체 중심으로 코드를 쓰게 해 주어 생산성이 좋습니다. 하지만 내부에서 어떤 SQL이 생성되는지 모르면 N+1 query나 비효율적인 조회를 놓치기 쉬워서, 결국 생성된 SQL과 트랜잭션 경계를 읽을 줄 알아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Web Development 101 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [Web Development 101 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [Web Development 101 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [Web Development 101 (4/10): HTTP와 API](./04-http-and-api.md)
- [Web Development 101 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- [Web Development 101 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- **데이터베이스 연결 (현재 글)**
- 배포 (예정)
- 성능과 캐싱 (예정)
- 작은 웹앱 만들기 (예정)

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
