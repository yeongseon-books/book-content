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

이 글은 Web Development 101 시리즈의 일곱 번째 글입니다. 여기서는 SQL의 기본 작업, ORM의 역할, 연결과 연결 풀, 트랜잭션이 왜 필요한지 정리하면서 웹앱이 데이터를 오래 보관하는 방식을 살펴보겠습니다.

## 먼저 던지는 질문

- 웹앱은 왜 파일이 아니라 데이터베이스를 쓸까요?
- SQL의 네 가지 기본 작업은 무엇일까요?
- ORM은 어디서 편하고 어디서 한계가 생길까요?

## 큰 그림

![Web Development 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/07/07-01-concept-at-a-glance.ko.png)

*Web Development 101 7장 흐름 개요*

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

## Before / After로 보는 저장 방식

**Before (write to a file)**

```python
open("users.txt", "a").write("alice\n")  # 동시 접근이 겹치면 깨집니다
```

**After (write to a DB)**

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

데이터베이스는 웹앱의 진실을 오래 보관하는 저장소입니다. SQL, 연결, 연결 풀, 트랜잭션 감각이 있어야 기능이 늘어나도 데이터가 버텨 줍니다. 다음 글에서는 이렇게 만든 앱을 실제 환경에 올리는 배포를 살펴보겠습니다.

## 웹 서비스 품질을 높이는 추가 실전 예시

웹 개발에서는 기능 구현 속도만큼 프로토콜 이해와 운영 경계 관리가 중요합니다. 특히 HTTP 메시지 설계, 인증 흐름, 배포 구성은 기능이 늘어날수록 장애 확률과 직접 연결됩니다. 아래 예시는 실제 프로젝트에서 반복해서 쓰이는 기본 패턴입니다.

### HTTP 요청/응답 설계 예시

```http
POST /api/v1/orders HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer <access_token>
Idempotency-Key: 9a7d2f4a-31a2-4b11-9cd8-3e2f4dcf1b20

{
  "items": [{"sku": "A-100", "qty": 2}],
  "payment_method": "card"
}
```

```http
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/v1/orders/ord_1024

{
  "order_id": "ord_1024",
  "status": "created"
}
```

여기서 `Idempotency-Key`는 네트워크 재시도로 인한 중복 결제를 막는 핵심 장치입니다. 웹 API는 "한 번 보냈다"가 아니라 "여러 번 도착할 수 있다"를 기본 가정으로 설계해야 합니다.

### 인증 흐름: Access + Refresh 토큰 분리

```text
1) 사용자가 로그인하면 서버가 access(짧은 수명) + refresh(긴 수명)를 발급
2) 클라이언트는 access로 API 호출
3) access 만료 시 refresh로 재발급 요청
4) refresh 탈취 위험을 줄이기 위해 회전(rotation)과 폐기(revoke) 정책 적용
```

```python
# pseudo-auth-service.py
from datetime import timedelta

def issue_tokens(user_id: str) -> dict:
    return {
        "access_expires": timedelta(minutes=15),
        "refresh_expires": timedelta(days=14),
        "token_type": "Bearer",
    }
```

브라우저 환경에서는 refresh 토큰을 `HttpOnly`, `Secure`, `SameSite` 정책이 적용된 쿠키로 다루는 방식이 일반적입니다. 인증 실패 응답은 `401`과 명확한 오류 코드를 함께 제공해야 클라이언트 재시도 전략을 안정적으로 구성할 수 있습니다.

### 배포 구성: 앱/프록시/헬스체크 분리

```yaml
# docker-compose.prod.yml
services:
  web:
    image: ghcr.io/example/web:1.4.0
    env_file: .env
    ports: ["8000"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
  nginx:
    image: nginx:1.27
    ports: ["80:80", "443:443"]
    depends_on: [web]
```

헬스체크를 배포 단위에 포함하면 롤링 업데이트 중 비정상 인스턴스를 조기에 제외할 수 있습니다. 프록시 계층에서 TLS 종료와 정적 파일 캐싱을 처리하면 애플리케이션 서버는 비즈니스 로직에 더 집중할 수 있습니다.

### 운영 체크 포인트

- API마다 타임아웃, 재시도, 멱등 처리 기준을 문서화합니다.
- 인증 토큰 만료/재발급 실패 비율을 대시보드로 모니터링합니다.
- 배포 후 15분 동안 5xx 비율, p95, 로그인 성공률을 집중 관찰합니다.
- CORS 정책을 `*`로 열어두지 않고 허용 출처를 명시합니다.

웹 개발의 난이도는 화면 구현보다 경계 관리에서 더 크게 올라갑니다. HTTP 계약, 인증 수명주기, 배포 안전장치를 초기에 고정해 두면 기능 확장 시에도 장애 반경을 작게 유지할 수 있고, 팀 전체의 디버깅 속도도 안정적으로 유지됩니다.

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

## 처음 질문으로 돌아가기

- **웹앱은 왜 파일이 아니라 데이터베이스를 쓸까요?**
  - 본문의 기준은 데이터베이스 연결를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **SQL의 네 가지 기본 작업은 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **ORM은 어디서 편하고 어디서 한계가 생길까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Computer Science, WebDevelopment, Database, SQL, ORM, Backend
