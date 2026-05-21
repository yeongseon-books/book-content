---
series: secure-coding-101
episode: 7
title: "Secure Coding 101 (7/10): SQL Injection과 ORM 안전 사용"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - SQLInjection
  - ORM
  - Database
  - SecureCoding
  - OWASP
seo_description: Parameterized query, ORM 안전 사용, raw SQL 위험성 그리고 SQLi 방어 5단계
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (7/10): SQL Injection과 ORM 안전 사용

SQL injection은 오래된 취약점이지만 아직도 가장 비싼 사고를 만듭니다. 이유는 단순합니다. 한 번 뚫리면 개별 화면이 아니라 데이터베이스 전체가 보상으로 걸려 있기 때문입니다. 인증 우회, 데이터 유출, 데이터 조작이 한 줄의 문자열 연결에서 동시에 시작될 수 있습니다.

이 글은 Secure Coding 101 시리즈의 7번째 글입니다.

여기서는 SQL injection을 ORM을 쓰면 자동으로 사라지는 문제로 보지 않고, SQL과 데이터를 문법적으로 분리하지 않았을 때 생기는 구조적 문제로 정리하겠습니다. 이 관점을 잡아 두면 raw SQL, ORM, 정렬 컬럼, DB 계정 권한을 한 흐름에서 함께 볼 수 있습니다.


![Secure Coding 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/07/07-01-concept-at-a-glance.ko.png)
*Secure Coding 101 7장 흐름 개요*

## 먼저 던지는 질문

- SQL injection은 정확히 어떤 식으로 SQL 의미를 바꿀까요?
- parameterized query는 왜 가장 중요한 기본기일까요?
- ORM을 써도 SQL injection이 생기는 경우는 언제일까요?

## 왜 중요한가

SQL injection은 단일 필드 검증 실수가 데이터베이스 전체 사고로 번지는 전형적인 취약점입니다. 애플리케이션이 사용자 입력을 SQL 구문의 일부로 해석하는 순간, 공격자는 값을 넣는 것이 아니라 쿼리 구조 자체를 바꾸게 됩니다. 이 차이가 치명적입니다.

또한 많은 팀이 ORM을 사용하면서 안심하는데, 이 안심이 오히려 위험할 수 있습니다. ORM은 안전한 습관을 돕지만, raw SQL이나 `text()` 호출, 동적 컬럼 이름 처리, 문자열 합성을 잘못 쓰면 같은 취약점이 그대로 남습니다. 결국 핵심은 도구보다 데이터와 구문을 어떻게 분리했는가입니다.

## 한눈에 보는 구조

이 그림은 SQL injection의 본질을 단순하게 보여 줍니다. 문자열 연결은 입력값을 SQL 문법 안으로 섞어 넣고, prepared statement는 SQL과 값을 분리합니다. 이 한 차이가 공격 가능성과 안전성을 가릅니다.

## 핵심 용어

- **SQL injection**: 입력값이 SQL의 의미를 바꾸도록 만드는 취약점입니다.
- **파라미터 바인딩(parameterized query)**: SQL 구문과 데이터 값을 문법적으로 분리해 넘기는 방식입니다.
- **준비된 구문(prepared statement)**: 데이터베이스가 미리 해석해 두는 SQL 실행 단위입니다.
- **ORM**: 객체 모델을 바탕으로 SQL을 만들어 주는 라이브러리입니다.
- **저장 프로시저(stored procedure)**: 데이터베이스 내부에 저장된 함수 형태의 실행 단위입니다.

## 바꾸기 전과 후

**바꾸기 전**: `f"SELECT * FROM users WHERE name='{name}'"`처럼 문자열을 이어 붙여 쿼리를 만듭니다. 입력 하나가 그대로 SQL 구문 일부가 됩니다.

**바꾼 후**: `cursor.execute("SELECT * FROM users WHERE name=%s", (name,))`처럼 SQL과 값을 분리해 전달합니다. 데이터베이스는 값을 구문이 아니라 값으로만 해석합니다.

## 실습: SQL injection을 막는 5단계

### 1단계 — 모든 값을 파라미터로 넘깁니다

```python
cursor.execute(
    "SELECT id FROM users WHERE name=%s AND status=%s",
    (name, "active"),
)
```

이 방식의 핵심은 단순 편의가 아니라 문법 분리입니다. 사용자 입력이 문자열 따옴표나 SQL 조각을 포함해도 데이터베이스는 이를 값으로만 취급합니다. SQLi 방어는 여기서 출발합니다.

### 2단계 — ORM을 올바른 방식으로 사용합니다

```python
from sqlalchemy import select
stmt = select(User).where(User.name == name)
result = session.scalars(stmt).all()
```

ORM은 안전한 패턴을 기본값으로 제공하지만, 어디까지나 기본값일 뿐입니다. ORM 쿼리 빌더를 그대로 사용하면 파라미터 분리가 자연스럽게 따라오지만, 문자열 조합으로 우회하면 같은 문제를 다시 끌어옵니다.

### 3단계 — 동적 컬럼은 허용 목록으로 제한합니다

```python
ALLOWED = {"name", "created_at", "id"}
def order_by(field):
    if field not in ALLOWED:
        raise ValueError("invalid order field")
    return field  # 안전하게 SQL에 끼워 넣을 수 있음
```

컬럼명이나 테이블명처럼 SQL 식별자는 일반 파라미터 바인딩으로 처리할 수 없습니다. 그래서 동적 식별자가 필요하다면 허용 목록이 유일한 안전한 선택입니다. 이 부분에서 자주 실수가 납니다.

### 4단계 — raw SQL도 예외 없이 파라미터를 씁니다

```python
session.execute(text("SELECT * FROM logs WHERE user_id=:uid"), {"uid": uid})
```

보고서 쿼리나 배치 작업처럼 raw SQL이 꼭 필요할 수는 있습니다. 그렇더라도 규칙은 바뀌지 않습니다. raw SQL은 예외 상황일 뿐이고, 예외일수록 더 엄격하게 파라미터 사용 여부를 확인해야 합니다.

### 5단계 — DB 계정 권한을 분리합니다

```sql
-- 애플리케이션 계정은 DML만 수행하고 DDL은 별도 계정이 맡습니다.
GRANT SELECT, INSERT, UPDATE ON db.* TO 'app'@'%';
```

## 배포 전에 꼭 해 볼 검증

SQL injection 방어는 “ORM을 쓰니까 괜찮다”로 끝내지 말고, 위험한 입력을 직접 넣어 보며 확인하는 편이 좋습니다.

```python
payload = "' OR 1=1 --"

# 안전한 경로: payload를 문자열 값으로만 취급
cursor.execute("SELECT id FROM users WHERE name=%s", (payload,))

# 위험한 경로: payload가 SQL 의미를 바꿔 버림
sql = f"SELECT id FROM users WHERE name='{payload}'"
```

**기대 결과:** 파라미터 바인딩 버전은 해당 문자열과 정확히 일치하는 값만 찾고, 문자열 결합 버전은 의도하지 않은 행을 돌려줄 수 있습니다. 이 차이를 팀 전체가 한 번 눈으로 확인하면 코드 리뷰 기준도 훨씬 단단해집니다.

SQL injection이 완전히 막히지 못하더라도 DB 계정 권한이 최소화돼 있으면 피해 범위를 줄일 수 있습니다. 애플리케이션 계정에 `DROP`이나 광범위한 관리자 권한이 있으면 취약점 하나가 곧 데이터 파괴로 이어집니다.

## 이 코드에서 먼저 볼 점

- SQL 문자열 연결은 항상 경고 신호입니다.
- ORM은 안전한 습관을 돕지만 마법 방패는 아닙니다.
- 동적 식별자는 허용 목록 없이는 안전하게 처리할 수 없습니다.
- DB 계정 권한도 최소 권한 원칙을 따라야 합니다.

## 실무에서 자주 헷갈리는 지점

1. **f-string으로 SQL을 만드는 경우**: 가장 흔한 SQL injection 패턴입니다.
2. **ORM 안에서도 문자열 합성을 하는 경우**: ORM을 써도 취약점은 그대로 생깁니다.
3. **정렬 컬럼을 입력값 그대로 받는 경우**: 동적 컬럼 기반 SQL injection이 됩니다.
4. **애플리케이션 계정에 과한 권한을 주는 경우**: 사고 반경이 불필요하게 커집니다.
5. **오류 메시지에 raw SQL을 노출하는 경우**: blind SQLi 실마리를 공격자에게 줍니다.

## 실무에서는 이렇게 봅니다

대부분의 팀은 ORM을 기본 경로로 두고, raw SQL은 예외 상황으로 취급합니다. raw SQL이 등장하면 코드 리뷰에서 가장 먼저 파라미터 사용 여부를 확인합니다. 이 규칙만 잘 지켜도 많은 사고를 미리 막을 수 있습니다.

또한 데이터베이스 계정도 애플리케이션 일부라는 관점이 중요합니다. 읽기 전용 계정, 쓰기 계정, 마이그레이션 계정을 분리하면 쿼리 취약점이 생겨도 영향 범위를 줄일 수 있습니다. SQLi 대응은 애플리케이션 코드와 DB 운영 정책이 함께 맞물려야 완성됩니다.

## 선임 엔지니어는 이렇게 생각합니다

- 문자열로 만든 SQL은 금지된 패턴으로 봅니다.
- 동적 식별자는 허용 목록을 통과한 경우에만 사용합니다.
- DB 계정도 최소 권한 원칙을 따라야 합니다.
- SQL이 오류 메시지로 새지 않게 합니다.
- ORM은 안전한 기본 습관이지 자동 보호막이 아닙니다.

## 체크리스트

- [ ] 모든 SQL이 파라미터 바인딩을 사용합니다.
- [ ] 동적 컬럼과 테이블 이름이 허용 목록을 거칩니다.
- [ ] DB 계정이 역할별로 분리돼 있습니다.
- [ ] 오류 메시지가 SQL 내부 구조를 노출하지 않습니다.

## 연습 문제

1. blind SQL injection이 무엇인지 한 문단으로 설명해 보세요.
2. ORM에서 raw text를 안전하게 쓰는 패턴 두 가지를 적어 보세요.
3. 정렬용 허용 목록 헬퍼 함수를 직접 작성해 보세요.

## 정리와 다음 글

SQL injection은 새로운 종류의 공격이라기보다, SQL과 데이터를 분리하지 않았을 때 반복해서 생기는 오래된 구조적 문제입니다. 이 글에서는 파라미터 바인딩, ORM 기본 사용, 동적 식별자 허용 목록, 최소 권한 DB 계정이 왜 함께 가야 하는지 정리했습니다.

다음 글에서는 브라우저가 공격자의 실행 환경으로 바뀌는 두 가지 대표 시나리오, XSS와 CSRF를 다룹니다.

## 심화 실전 노트: Blind SQLi, 2차 인젝션, NoSQL 인젝션, 저장 프로시저 안전 사용

### Blind SQL Injection 이해와 탐지

Blind SQLi는 쿼리 결과가 화면에 직접 노출되지 않아도 성공할 수 있는 공격입니다. 공격자는 조건의 참/거짓에 따른 응답 차이(Boolean-based)나 응답 시간 차이(Time-based)로 데이터를 한 글자씩 추출합니다.

```python
# Boolean-based blind SQLi 시연
# 공격자가 보내는 입력 (name 파라미터)
payload_true  = "admin' AND SUBSTRING(password,1,1)='a' --"
payload_false = "admin' AND SUBSTRING(password,1,1)='z' --"

# 취약한 코드 — 문자열 연결
query = f"SELECT * FROM users WHERE name='{name}'"
# payload_true → 사용자 정보 반환 (200 OK, 데이터 있음)
# payload_false → 빈 결과 (200 OK, 데이터 없음)
# 응답 차이로 비밀번호를 한 글자씩 추출 가능
```

```python
# Time-based blind SQLi
payload = "admin'; SELECT CASE WHEN (SUBSTRING(password,1,1)='a') THEN pg_sleep(3) ELSE pg_sleep(0) END --"
# 응답이 3초 걸리면 첫 글자가 'a'
```

Blind SQLi는 일반 SQLi보다 탐지가 어렵습니다. WAF는 `SLEEP`, `BENCHMARK`, `pg_sleep` 같은 시간 함수를 차단할 수 있지만, Boolean-based는 정상 쿼리와 구문이 비슷해서 놓치기 쉽습니다. 근본 대응은 동일합니다 — 파라미터 바인딩으로 구조적으로 차단합니다.

```python
# 방어: 파라미터 바인딩이면 blind SQLi도 불가능
cursor.execute("SELECT * FROM users WHERE name=%s", (name,))
# payload가 그대로 문자열 값으로 취급됨 → 조건 조작 불가
```

### 2차 인젝션(Second-Order Injection)

2차 인젝션은 입력 시점에는 무해하지만, 저장된 뒤 다른 쿼리에서 사용될 때 SQL 의미를 바꾸는 패턴입니다. 입력 검증과 출력 사용을 별도로 봐야 하는 이유가 여기에 있습니다.

```python
# 1단계: 사용자 등록 — 입력은 파라미터로 안전하게 저장
username = "admin'--"
cursor.execute("INSERT INTO users (name) VALUES (%s)", (username,))
# DB에 "admin'--" 문자열이 그대로 저장됨 (여기까진 안전)

# 2단계: 다른 기능에서 저장된 값을 꺼내 쓸 때
row = cursor.fetchone()  # row[0] = "admin'--"
# 취약한 코드 — 저장된 값을 신뢰하고 문자열 연결
query = f"SELECT * FROM orders WHERE user_name='{row[0]}'"
# → SELECT * FROM orders WHERE user_name='admin'--'
# → 조건 무효화, 모든 주문 조회 가능
```

**교훈**: 데이터베이스에서 꺼낸 값도 외부 입력과 동일하게 취급해야 합니다. "이미 검증돼서 안전하다"는 가정이 2차 인젝션의 원인입니다.

```python
# 수정: 저장된 값을 사용할 때도 파라미터 바인딩
cursor.execute("SELECT * FROM orders WHERE user_name=%s", (row[0],))
```

### NoSQL Injection

MongoDB 같은 문서 데이터베이스도 인젝션에 취약합니다. SQL 문법은 아니지만, 쿼리 연산자를 입력으로 주입할 수 있습니다.

```python
from flask import request
from pymongo import MongoClient

db = MongoClient().mydb

# 취약한 코드 — request.json을 그대로 쿼리에 전달
@app.post("/login")
def login():
    body = request.json
    # body = {"username": "admin", "password": {"$ne": ""}}
    user = db.users.find_one({
        "username": body["username"],
        "password": body["password"]  # {"$ne": ""} → 비밀번호가 빈 문자열이 아닌 모든 문서 매칭
    })
    if user:
        return {"status": "logged in"}  # 인증 우회 성공
```

```python
# 수정 패턴 1: 타입 강제
@app.post("/login")
def login():
    body = request.json
    username = str(body.get("username", ""))
    password = str(body.get("password", ""))  # 반드시 문자열로 변환
    user = db.users.find_one({"username": username, "password": password})

# 수정 패턴 2: Pydantic으로 스키마 강제
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str  # 연산자 객체는 검증 실패

@app.post("/login")
def login(req: LoginRequest):
    user = db.users.find_one({"username": req.username, "password": req.password})
```

NoSQL 인젝션의 핵심은 쿼리 연산자(`$ne`, `$gt`, `$regex` 등)가 입력으로 들어오는 것을 차단하는 것입니다. 타입을 강제하거나, 입력 객체에서 `$` 접두사 키를 거부하는 방법이 있습니다.

### 저장 프로시저의 안전한 사용

저장 프로시저가 SQL injection을 자동으로 막아준다는 오해가 있습니다. 프로시저 내부에서 동적 SQL을 사용하면 동일한 취약점이 발생합니다.

```sql
-- 취약한 저장 프로시저 (MySQL)
CREATE PROCEDURE search_users(IN search_term VARCHAR(255))
BEGIN
    SET @query = CONCAT('SELECT * FROM users WHERE name LIKE ''%', search_term, '%''');
    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END;

-- 수정: 파라미터 바인딩 사용
CREATE PROCEDURE search_users_safe(IN search_term VARCHAR(255))
BEGIN
    SET @search = CONCAT('%', search_term, '%');
    PREPARE stmt FROM 'SELECT * FROM users WHERE name LIKE ?';
    EXECUTE stmt USING @search;
    DEALLOCATE PREPARE stmt;
END;
```

저장 프로시저의 보안 이점은 인젝션 방지가 아니라 권한 분리입니다. 애플리케이션 계정에 테이블 직접 접근 권한 대신 프로시저 실행 권한만 부여하면, 인젝션이 성공해도 실행 가능한 SQL이 제한됩니다.

### SQLAlchemy에서 흔히 실수하는 패턴

ORM을 잘 쓰면 안전하지만, 다음 패턴들은 ORM 사용 중에도 SQLi를 만듭니다.

```python
from sqlalchemy import text, column, desc
from sqlalchemy.orm import Session

# ❌ 실수 1: text() 안에 문자열 포매팅
def search_users(session: Session, keyword: str):
    # 취약
    return session.execute(text(f"SELECT * FROM users WHERE name LIKE '%{keyword}%'"))

# ✅ 수정: text()에도 바인드 파라미터
def search_users_safe(session: Session, keyword: str):
    return session.execute(
        text("SELECT * FROM users WHERE name LIKE :kw"),
        {"kw": f"%{keyword}%"}
    )

# ❌ 실수 2: order_by에 입력값 직접 전달
def get_sorted(session: Session, sort_field: str):
    # 취약 — sort_field가 "name; DROP TABLE users--"이면?
    return session.execute(text(f"SELECT * FROM users ORDER BY {sort_field}"))

# ✅ 수정: 허용 목록 + getattr
SORT_COLUMNS = {"name": User.name, "created_at": User.created_at, "id": User.id}

def get_sorted_safe(session: Session, sort_field: str):
    col = SORT_COLUMNS.get(sort_field)
    if col is None:
        raise ValueError(f"Invalid sort field: {sort_field}")
    return session.query(User).order_by(col).all()

# ❌ 실수 3: filter에 문자열 조건
def find_active(session: Session, status: str):
    # 취약
    return session.query(User).filter(text(f"status = '{status}'"))

# ✅ 수정: ORM 비교 연산자 사용
def find_active_safe(session: Session, status: str):
    return session.query(User).filter(User.status == status).all()
```

### 정적 분석으로 SQL injection 사전 탐지

코드 리뷰만으로 모든 SQL 문자열 결합을 잡기 어렵습니다. 정적 분석 도구를 CI에 붙이면 자동으로 탐지할 수 있습니다.

```bash
# Bandit — Python 보안 정적 분석
pip install bandit
bandit -r src/ -t B608  # B608: SQL injection 탐지 규칙

# 출력 예시:
# >> Issue: [B608:hardcoded_sql_expressions]
#    Severity: Medium   Confidence: Low
#    Location: src/users/repository.py:45
#    More Info: https://bandit.readthedocs.io/...
#    45  query = f"SELECT * FROM users WHERE id = {user_id}"
```

```yaml
# CI 파이프라인에 통합
- name: SQL injection scan
  run: |
    pip install bandit
    bandit -r src/ -t B608 -f json -o bandit-report.json
    if [ $? -ne 0 ]; then
      echo "SQL injection 위험 코드 발견"
      exit 1
    fi
```

Semgrep도 커스텀 규칙으로 프로젝트 특화 패턴을 탐지할 수 있습니다:

```yaml
# .semgrep/sql-injection.yaml
rules:
  - id: raw-sql-format-string
    patterns:
      - pattern: |
          $QUERY = f"...{$VAR}..."
      - metavariable-regex:
          metavariable: $QUERY
          regex: ".*(SELECT|INSERT|UPDATE|DELETE).*"
    message: "SQL 쿼리에 f-string 사용 금지. 파라미터 바인딩을 사용하세요."
    severity: ERROR
    languages: [python]
```

### SQL injection 사고 후 운영 대응

방어를 뚫렸을 때를 대비한 탐지와 대응도 필요합니다.

```python
# 쿼리 이상 탐지 — 느린 쿼리/비정상 패턴 모니터링
import logging
import time

logger = logging.getLogger("sql.audit")

class QueryAuditor:
    SUSPICIOUS_PATTERNS = [
        "UNION SELECT", "OR 1=1", "SLEEP(", "BENCHMARK(",
        "pg_sleep", "WAITFOR DELAY", "INTO OUTFILE",
    ]

    def audit_query(self, query: str, params: tuple, duration_ms: float):
        # 1. 느린 쿼리 탐지 (time-based blind SQLi 징후)
        if duration_ms > 3000:
            logger.warning("slow_query", extra={
                "query_hash": hash(query),
                "duration_ms": duration_ms,
                "alert": "possible_time_based_sqli"
            })

        # 2. 의심 패턴 탐지 (파라미터가 아닌 곳에 나타나면 경고)
        query_upper = query.upper()
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern in query_upper:
                logger.error("suspicious_query_pattern", extra={
                    "pattern": pattern,
                    "query_hash": hash(query),
                    "alert": "possible_sqli_attempt"
                })
```

```text
운영 대응 체크리스트:
1. DB 감사 로그에서 비정상 쿼리 패턴 확인
2. 영향받은 테이블의 데이터 무결성 검증
3. 유출 가능 데이터 범위 확인 (SELECT 권한 기준)
4. 데이터 변조 여부 확인 (UPDATE/DELETE 로그)
5. 취약 지점 패치 후 동일 입력 차단 확인
6. 관련 사용자에게 비밀번호 재설정 요청 (데이터 유출 시)
```

### LIKE 절과 와일드카드 인젝션

파라미터 바인딩을 사용해도 LIKE 절에서는 와일드카드 문자(`%`, `_`)를 통한 의도치 않은 패턴 매칭이 가능합니다. 이것은 SQL injection은 아니지만, 데이터 유출로 이어질 수 있는 논리적 취약점입니다.

```python
# 문제: 사용자가 '%'를 입력하면 모든 행이 매칭됨
keyword = request.args.get("q")  # 사용자가 "%" 입력
cursor.execute("SELECT * FROM products WHERE name LIKE %s", (f"%{keyword}%",))
# → SELECT * FROM products WHERE name LIKE '%%%'  → 모든 행 반환

# 수정: 와일드카드 이스케이프
def escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

safe_keyword = escape_like(keyword)
cursor.execute(
    "SELECT * FROM products WHERE name LIKE %s ESCAPE '\\'",
    (f"%{safe_keyword}%",)
)
```

### 다중 데이터베이스 환경에서의 SQLi 고려 사항

마이크로서비스 환경에서는 서비스마다 다른 DB를 쓰는 경우가 많습니다. PostgreSQL, MySQL, SQLite, Oracle은 각각 SQL 방언이 다르고, 인젝션 페이로드도 다릅니다.

```text
DB별 시간 지연 함수 (time-based blind SQLi에 사용됨):
- PostgreSQL: pg_sleep(5)
- MySQL: SLEEP(5), BENCHMARK(10000000, SHA1('test'))
- SQLite: 시간 함수 없음 → heavy query로 대체
- MSSQL: WAITFOR DELAY '0:0:5'
- Oracle: DBMS_PIPE.RECEIVE_MESSAGE('x', 5)

DB별 주석 문법:
- MySQL/PostgreSQL/SQLite: -- (공백 필요), /* */
- MySQL 전용: #
- Oracle: -- (공백 필요)
```

이 차이가 의미하는 것은, WAF 규칙이나 입력 필터링에만 의존하면 DB 종류에 따라 우회 가능하다는 점입니다. 파라미터 바인딩은 DB 종류에 무관하게 동작하므로, 방어의 기본은 항상 파라미터 바인딩이어야 합니다.

### 대량 쿼리와 배치 처리에서의 안전 패턴

보고서 생성이나 데이터 마이그레이션 같은 배치 작업에서는 동적 조건이 많아 raw SQL 유혹이 커집니다. 이런 상황에서도 안전한 패턴이 있습니다.

```python
from sqlalchemy import text, bindparam
from sqlalchemy.orm import Session

# 동적 IN 절 — 안전한 처리
def get_users_by_ids(session: Session, user_ids: list[int]):
    if not user_ids:
        return []
    # SQLAlchemy의 expanding bind parameter
    stmt = text("SELECT * FROM users WHERE id IN :ids")
    stmt = stmt.bindparams(bindparam("ids", expanding=True))
    return session.execute(stmt, {"ids": user_ids}).fetchall()

# 동적 WHERE 조건 조합 — ORM 빌더 활용
from sqlalchemy import and_, or_

def search_users(session: Session, filters: dict):
    query = session.query(User)
    conditions = []

    if "name" in filters:
        conditions.append(User.name.ilike(f"%{escape_like(filters['name'])}%"))
    if "status" in filters:
        if filters["status"] not in ("active", "inactive", "suspended"):
            raise ValueError("invalid status")
        conditions.append(User.status == filters["status"])
    if "min_age" in filters:
        conditions.append(User.age >= int(filters["min_age"]))

    if conditions:
        query = query.filter(and_(*conditions))
    return query.all()
```

핵심 원칙: 동적 쿼리가 필요하더라도, 동적인 부분은 "어떤 조건을 포함할지"이지 "SQL 문자열을 어떻게 조합할지"가 아닙니다. ORM의 쿼리 빌더는 이 구분을 자연스럽게 강제합니다.

## 처음 질문으로 돌아가기

- **SQL injection은 정확히 어떤 식으로 SQL 의미를 바꿀까요?**
  - 문자열 연결로 만든 SQL에 사용자 입력이 들어가면, 따옴표를 닫거나 주석(`--`)을 넣어 원래 쿼리의 조건을 무효화하거나 새 SQL 구문을 추가할 수 있습니다. Blind SQLi 절에서 본 것처럼, 화면에 결과가 보이지 않아도 응답 시간이나 조건 참/거짓 차이만으로 데이터를 추출할 수 있습니다.
- **parameterized query는 왜 가장 중요한 기본기일까요?**
  - 파라미터 바인딩은 SQL 구문과 값을 문법 레벨에서 분리합니다. 데이터베이스가 쿼리를 먼저 해석하고 값을 나중에 채우므로, 입력이 아무리 악의적이어도 SQL 의미를 바꿀 수 없습니다. 이 한 가지 원칙이 일반 SQLi, Blind SQLi, 2차 인젝션을 모두 구조적으로 차단합니다.
- **ORM을 써도 SQL injection이 생기는 경우는 언제일까요?**
  - SQLAlchemy 실수 패턴 절에서 본 것처럼, `text()` 안에 f-string을 쓰거나, `filter`에 문자열 조건을 넣거나, 정렬 컬럼을 입력값으로 직접 받으면 ORM을 쓰고 있어도 인젝션이 그대로 발생합니다. ORM의 쿼리 빌더를 사용하되, raw SQL이 필요한 지점에서는 반드시 바인드 파라미터를 확인해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Secure Coding 101 (1/10): Secure Coding이란 무엇인가?](./01-what-is-secure-coding.md)
- [Secure Coding 101 (2/10): 입력값 검증](./02-input-validation.md)
- [Secure Coding 101 (3/10): 인증과 세션](./03-authentication-and-session.md)
- [Secure Coding 101 (4/10): 인가와 권한](./04-authorization-and-permissions.md)
- [Secure Coding 101 (5/10): 안전한 데이터 저장](./05-safe-data-storage.md)
- [Secure Coding 101 (6/10): Secret과 키 관리](./06-secret-and-key-management.md)
- **SQL Injection과 ORM 안전 사용 (현재 글)**
- XSS와 CSRF 방어 (예정)
- Dependency 취약점 관리 (예정)
- 안전한 로깅과 감사 (예정)

<!-- toc:end -->

## 참고 자료

- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [PortSwigger — SQL injection](https://portswigger.net/web-security/sql-injection)
- [SQLAlchemy security](https://docs.sqlalchemy.org/)
- [psycopg parameter binding](https://www.psycopg.org/psycopg3/docs/basic/params.html)
- [SQLAlchemy — Working with DBAPI transactions and statements](https://docs.sqlalchemy.org/en/20/tutorial/dbapi_transactions.html)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/secure-coding-101/ko)

Tags: SQLInjection, ORM, Database, SecureCoding, OWASP
