---
title: "Information Security 101 (6/10): SQL 인젝션과 XSS"
series: information-security-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
  - Computer Science
  - Security
  - SQLInjection
  - XSS
  - InputValidation
  - OutputEncoding
last_reviewed: '2026-05-12'
seo_description: SQL 인젝션과 XSS의 원인, 방어 원칙, 실전 코드를 짧게 정리합니다.
---

# Information Security 101 (6/10): SQL 인젝션과 XSS

보안 입문자가 가장 먼저 듣는 취약점 이름 두 개를 고르라면 아마 SQL 인젝션과 XSS일 것입니다. 오래된 취약점인데도 계속 반복되는 이유는 단순합니다. 새 프레임워크가 나와도 뿌리는 거의 같기 때문입니다. 입력값이 데이터로 남아야 할 자리에 코드처럼 해석되는 순간 문제가 시작됩니다.

이 글은 Information Security 101 시리즈의 6번째 글입니다.


![Information Security 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/information-security-101/06/06-01-big-picture.ko.png)
*Information Security 101 6장 흐름 개요*
> SQL 인젝션과 XSS 모두 신뢰할 수 없는 입력을 그 컨텍스트의 명령어로 해석하게 만드는 공격입니다. 방어는 입력 필터가 아니라 준비된 문과 컨텍스트 기반 이스케이핑입니다.

## 먼저 던지는 질문

- SQL 인젝션은 정확히 어떤 메커니즘으로 발생할까요?
- ORM을 쓰면 정말 안전해질까요?
- Reflected, Stored, DOM 기반 XSS는 어디서 갈릴까요?

## 왜 중요한가

이 두 취약점은 여러 해 동안 OWASP Top 10에 반복해서 등장했습니다. 한 번 원리를 이해하면 언어와 프레임워크가 바뀌어도 같은 방식으로 방어할 수 있습니다. 반대로 특정 라이브러리나 특정 프레임워크의 “자동 보호”만 믿으면 예외 경로에서 그대로 무너집니다.

결국 중요한 것은 입력이 코드가 되지 않게 막는 일과, 출력이 해석되는 문맥을 분명히 구분하는 일입니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    U["User input"] -->|"String concat"| Q["SQL/HTML"]
    Q -->|"interpreted as code"| X["Vulnerable"]
    U -->|"parameter binding / escape"| S["treated as data"]
    S --> O["Safe"]
```

같은 입력도 다루는 방식에 따라 결과가 완전히 달라집니다. 문자열 결합은 취약점으로 이어지고, 바인딩과 인코딩은 데이터를 데이터로 남깁니다.

## 핵심 용어

- **SQL 인젝션**: 입력이 SQL 문법 일부로 해석되는 취약점입니다.
- **매개변수 바인딩**: 입력을 SQL과 분리해 데이터로 전달하는 방식입니다.
- **반사형 XSS**: 입력이 응답에 바로 반영되는 형태입니다.
- **저장형 XSS**: 입력이 저장된 뒤 다른 사용자에게 다시 제공되는 형태입니다.
- **출력 인코딩**: HTML, 자바스크립트, URL처럼 출력 문맥에 맞게 이스케이프하는 방식입니다.

## 전후 비교

### 이전 — 문자열 결합으로 쿼리 작성

```python
cur.execute(f"SELECT * FROM users WHERE name='{name}'")
# name = "' OR 1=1 --"  -> returns every row
```

### 이후 — 매개변수 바인딩 사용

```python
cur.execute("SELECT * FROM users WHERE name=%s", (name,))
```

## 주입 공격 유형 비교

| 공격 유형 | 동작 원리 | 예시 | 주요 방어 방법 |
|---|---|---|---|
| **SQL Injection** | 입력이 SQL 구문의 일부로 해석됨 | `' OR 1=1 --` | 매개변수 바인딩, ORM, Prepared Statement |
| **XSS** | 입력이 HTML/JS로 실행됨 | `<script>alert(1)</script>` | 출력 인코딩, CSP, 프레임워크 기본 이스케이핑 |
| **CSRF** | 사용자 브라우저가 위조 요청을 보냄 | 이미지 태그로 POST 트리거 | CSRF 토큰, SameSite 쿠키, Referer 검증 |
| **Command Injection** | 입력이 셸 명령어로 해석됨 | `; rm -rf /` | 인수 배열 전달, 셸 호출 금지, 샌드박싱 |

모든 주입 공격의 뿌리는 같습니다. 신뢰할 수 없는 데이터가 코드로 해석될 수 있는 경계를 넘는 순간 발생합니다. 방어의 핵심은 데이터를 데이터로만 다루는 API를 사용하는 것입니다.
한 줄 차이지만 사고와 안전을 가르는 차이입니다.

## 단계별 실습

### 1단계 — 안전한 SQL을 작성합니다

```python
# 1_sql_safe.py
import sqlite3
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE u (id int, name text)")
con.execute("INSERT INTO u VALUES (?, ?)", (1, "alice"))
print(con.execute("SELECT * FROM u WHERE name=?", ("alice",)).fetchall())
```

`?`나 `%s` 자리에 입력값을 직접 끼워 넣으면 안 됩니다. 그 자리는 언제나 바인딩용 자리로 남겨 두어야 합니다.

### 2단계 — ORM도 예외 통로가 있다는 점을 봅니다

```python
# 2_orm_dynamic.py
# SQLAlchemy raw escape hatches stay risky
# session.execute(text(f"SELECT * FROM u WHERE name='{name}'"))  # do not do this
```

ORM은 많은 위험을 줄여 주지만, 원시 SQL이나 `text` 같은 탈출구를 쓰는 순간 같은 문제가 다시 들어옵니다.

### 3단계 — 반사형 XSS를 막습니다

```python
# 3_xss_reflect.py
from markupsafe import escape
def search(q):
    return f"<p>Query: {escape(q)}</p>"
```

서버에서 렌더링하기 전에 반드시 이스케이프해야 합니다. 사용자 입력을 그대로 HTML에 넣으면 바로 실행 표면이 됩니다.

### 4단계 — 저장형 XSS를 막습니다

```python
# 4_xss_stored.py
def render_comment(html):
    # store the original; encode at output time
    return f"<div>{escape(html)}</div>"
```

원문을 저장하고 출력 시점에 인코딩하는 규칙을 일관되게 지키는 것이 중요합니다.

### 5단계 — DOM 기반 XSS를 피합니다

```javascript
// 5_dom_xss.js
// document.body.innerHTML = location.hash;   // dangerous
const text = decodeURIComponent(location.hash.slice(1));
const node = document.createTextNode(text);   // safe
document.body.appendChild(node);
```

브라우저에서 DOM을 직접 다룰 때는 `innerHTML`보다 텍스트 노드 API를 먼저 떠올리는 편이 안전합니다.

### 6단계 — 안전한 쿼리와 취약한 쿼리를 비교합니다

```python
# 6_safe_vs_unsafe.py
import sqlite3

# 취약한 방식 — 절대 사용하지 마세요
def unsafe_query(name):
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE users (id int, name text)")
    con.execute("INSERT INTO users VALUES (1, 'alice')")
    # 공격: name = "' OR '1'='1"
    cursor = con.execute(f"SELECT * FROM users WHERE name='{name}'")
    return cursor.fetchall()

# 안전한 방식 — 항상 이렇게 작성하세요
def safe_query(name):
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE users (id int, name text)")
    con.execute("INSERT INTO users VALUES (1, 'alice')")
    cursor = con.execute("SELECT * FROM users WHERE name=?",(name,))
    return cursor.fetchall()

# 테스트
attack_payload = "' OR '1'='1"
print("Unsafe:", unsafe_query(attack_payload))  # 모든 행 반환
print("Safe:", safe_query(attack_payload))      # 빈 결과
```

취약한 쿼리는 공격 페이로드를 SQL 구문으로 해석합니다. 안전한 쿼리는 같은 값을 단순 문자열 데이터로 취급합니다. 이 한 줄 차이가 전체 데이터베이스 유출과 안전한 운영을 가릅니다.

## 이 코드와 예제에서 먼저 볼 점

- 모든 SQL은 매개변수 바인딩을 거쳐야 합니다.
- 출력 인코딩은 HTML 본문, 속성, URL, 자바스크립트처럼 문맥별로 달라집니다.
- DOM 조작에서는 `innerHTML`를 피하는 편이 안전합니다.
- 입력 검증은 보조 방어일 뿐, 주 방어는 아닙니다.

## 입력 검증 전략

입력 검증은 보조 방어층입니다. 주 방어는 매개변수 바인딩과 출력 인코딩입니다. 그럼에도 입력 검증은 공격 표면을 줄이는 데 도움이 됩니다.

### 허용 목록 방식

```python
# allow_list.py
ALLOWED_SORT_COLUMNS = {"name", "created_at", "id"}

def get_users(sort_by: str):
    if sort_by not in ALLOWED_SORT_COLUMNS:
        raise ValueError(f"Invalid sort column: {sort_by}")
    # 여기서는 직접 삽입 가능 (허용 목록 검증 완료)
    return f"SELECT * FROM users ORDER BY {sort_by}"
```

허용 목록은 예측 가능한 값의 집합이 작을 때 가장 안전합니다. 컬럼 이름, 정렬 방향, 테이블 이름처럼 미리 정의된 값에 적합합니다.

### 거부 목록의 한계

```python
# deny_list.py — 권장하지 않음
FORBIDDEN_PATTERNS = ["--", ";", "'", '"', "OR", "DROP"]

def unsafe_filter(user_input: str):
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.lower() in user_input.lower():
            raise ValueError("Forbidden pattern detected")
    return user_input

# 우회 가능:
# 1. 대소문자: oR, Or
# 2. 인코딩: %4F%52 (OR의 URL 인코딩)
# 3. 주석: /**/ 사이에 공백 삽입
# 4. Unicode: fullwidth 문자 사용
```

거부 목록은 우회 방법이 무한합니다. 가능하면 허용 목록과 매개변수 바인딩을 함께 사용하는 것이 훨씬 안전합니다.

### 타입 기반 검증

```python
# type_validation.py
from pydantic import BaseModel, validator

class UserQuery(BaseModel):
    user_id: int
    sort: str

    @validator("sort")
    def validate_sort(cls, v):
        allowed = {"name", "created_at"}
        if v not in allowed:
            raise ValueError(f"Sort must be one of {allowed}")
        return v

# FastAPI 엔드포인트
# @app.get("/users")
# def list_users(q: UserQuery):
#     return db.execute(
#         f"SELECT * FROM users WHERE id > ? ORDER BY {q.sort}",
#         (q.user_id,)
#     )
```

프레임워크 수준에서 타입과 값을 먼저 검증하면 잘못된 입력이 핸들러까지 도달하지 못합니다. 이 방식은 API 계약 검증과 보안 검증을 하나로 통합합니다.

## 자주 하는 실수 다섯 가지

1. **f-string으로 SQL을 만드는 실수**: 가장 흔한 인젝션 경로입니다.
2. **HTML 입력을 저장한 뒤 정제 없이 다시 렌더링하는 실수**: 저장형 XSS로 이어집니다.
3. **자바스크립트 문맥에 HTML 이스케이프만 적용하는 실수**: 잘못된 인코더입니다.
4. **사용자 입력을 `innerHTML`에 넣는 실수**: DOM 기반 XSS가 생깁니다.
5. **블랙리스트 필터만 믿는 실수**: 우회가 쉽습니다. 허용 목록이 더 안전합니다.

## 실무에서는 이렇게 나타납니다

큰 시스템은 ORM으로만 타입이 정해진 쿼리를 허용하고, 원시 SQL은 코드 리뷰를 강제합니다. 프런트엔드는 프레임워크의 기본 텍스트 보간을 신뢰하되 `dangerouslySetInnerHTML` 같은 직접 HTML 주입 경로는 승인 절차를 따로 둡니다. 웹 방화벽은 보조층일 뿐, 주 방어가 아닙니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 입력은 데이터로, 출력은 문맥에 맞게 인코딩한다는 두 줄 규칙을 팀 표준으로 둡니다.
- 정적 분석과 린트로 원시 SQL을 막습니다.
- HTML 정제기는 하나를 정해 전역에서 같이 씁니다.
- DOM 기반 XSS는 코드 리뷰와 정적 분석으로 잡습니다.
- 새 입력 경로가 생기면 위협 모델을 갱신합니다.

## 체크리스트

- [ ] 모든 SQL이 매개변수 바인딩을 사용합니까?
- [ ] 출력 인코딩이 문맥별로 적용되고 있습니까?
- [ ] `innerHTML` 사용 지점을 점검했습니까?
- [ ] HTML 정제기가 표준화되어 있습니까?
- [ ] 웹 방화벽 외에도 코드 수준 방어가 있습니까?

## 연습 문제

1. `name=' OR '1'='1`을 막는 한 줄 수정 코드를 적어 보세요.
2. 반사형 XSS와 저장형 XSS의 운영 차이 두 가지를 적어 보세요.
3. DOM 기반 XSS를 막는 React 패턴 하나를 설명해 보세요.

## 정리와 다음 글

SQL 인젝션과 XSS는 모두 입력 처리 일관성이 무너질 때 생깁니다. 입력을 코드로 해석시키지 않는 원칙만 분명해도 새로운 프레임워크에서도 같은 방식으로 방어할 수 있습니다. 다음 글에서는 코드 밖의 설정 영역으로 넘어가 비밀 정보 관리를 다룹니다.


## OWASP Top 10과 SQLi/XSS의 위치

SQL 인젝션과 XSS는 이름은 오래됐지만, OWASP Top 10 관점에서는 여전히 중심 축입니다. 특히 다음 항목과 강하게 연결됩니다.

| OWASP Top 10 항목 | SQLi/XSS와의 연결 | 예방 핵심 |
| --- | --- | --- |
| A03 Injection | SQL/NoSQL/OS 명령 주입 | 매개변수화, 입력 경계 검증 |
| A03 Injection (XSS 포함) | 브라우저에서 스크립트 실행 | 컨텍스트 인코딩, CSP |
| A01 Broken Access Control | 주입 이후 권한 우회 확장 | 서버 인가 재검증 |
| A09 Security Logging and Monitoring Failures | 탐지 지연 | 공격 시그널 로깅/경보 |

입력 취약점은 단독 이슈가 아니라 권한, 로깅, 배포 파이프라인과 함께 증폭됩니다.

## 취약점별 방어 코드 패턴

```python
# vuln_defense_patterns.py
import sqlite3
from markupsafe import escape

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE users (id INTEGER, name TEXT)")


def safe_lookup(name: str):
    # SQL 인젝션 방어: 바인딩 사용
    return con.execute("SELECT id, name FROM users WHERE name = ?", (name,)).fetchall()


def safe_html(name: str) -> str:
    # XSS 방어: 출력 시점 이스케이프
    return f"<p>{escape(name)}</p>"


def validate_limit(limit: int) -> int:
    # 입력 검증: 허용 범위 강제
    if not 1 <= limit <= 100:
        raise ValueError("limit out of range")
    return limit
```

이 코드에서 중요한 점은 방어 레이어가 다르다는 것입니다.

- SQL 방어: 쿼리 작성 단계
- XSS 방어: 렌더링 단계
- 입력 검증: 비즈니스 규칙 단계

한 레이어만으로 전체를 해결할 수 없습니다.

## 테스트 케이스를 먼저 고정하기

보안 회귀를 줄이려면 취약점 재현 문자열을 테스트 자산으로 유지해야 합니다.

| 테스트 대상 | 악성 입력 예시 | 기대 결과 |
| --- | --- | --- |
| 사용자 조회 API | `' OR 1=1 --` | 400 또는 빈 결과 |
| 댓글 렌더링 | `<script>alert(1)</script>` | 스크립트 미실행, 이스케이프 출력 |
| 검색 정렬 파라미터 | `name; DROP TABLE users` | 허용 목록 외 값 거부 |

정적 분석(SAST)과 동적 테스트(DAST)를 결합하면 코드와 런타임 양쪽에서 누수를 줄일 수 있습니다.

## 운영에서 반드시 남길 탐지 신호

- 짧은 시간 내 반복되는 SQL 문법 오류
- 특정 사용자/아이피의 비정상적으로 긴 쿼리 파라미터
- HTML/JS 특수 문자 포함 입력 급증
- WAF 차단 이벤트와 애플리케이션 오류 로그 상관관계

탐지 신호가 없으면 "막았는지"를 알 수 없습니다. 방어와 탐지는 같이 설계해야 합니다.

## 공격 재현과 방어 검증 시나리오

취약점 방어는 "코드가 안전해 보인다"가 아니라 재현 테스트 통과로 확인해야 합니다.

| 시나리오 | 입력 값 | 기대 결과 |
| --- | --- | --- |
| SQL 인젝션 우회 시도 | `' OR 1=1 --` | 400 또는 빈 결과 |
| 저장형 XSS 시도 | `<script>alert(1)</script>` | 스크립트 미실행, 이스케이프 출력 |
| DOM 기반 XSS 시도 | `#<img src=x onerror=alert(1)>` | 텍스트로 출력, 이벤트 미실행 |

## WAF와 애플리케이션 방어의 역할 분리

WAF는 공격 노이즈를 줄이는 보조선입니다. 근본 방어는 애플리케이션 코드에서 수행해야 합니다.

```text
요청 -> WAF 1차 필터 -> 앱 입력 검증 -> 바인딩 쿼리 -> 출력 인코딩 -> 응답
```

코드 수준 방어가 없는 상태에서 WAF만 의존하면 정상 요청 오탐과 우회 공격이 반복됩니다. 따라서 방어 책임을 계층별로 분리해 문서화해야 합니다.


## 데이터베이스 계정 분리 전략

SQL 인젝션 방어는 쿼리 작성법뿐 아니라 DB 권한 모델과 함께 봐야 합니다. 앱 계정이 과권한이면 우회 성공 시 피해가 커집니다.

| 계정 | 허용 권한 | 금지 권한 |
| --- | --- | --- |
| 읽기 전용 API 계정 | SELECT | INSERT/UPDATE/DELETE/DDL |
| 일반 쓰기 API 계정 | SELECT/INSERT/UPDATE | DROP/ALTER/GRANT |
| 마이그레이션 계정 | DDL(제한 시간) | 상시 사용 금지 |

## XSS 사고 대응 최소 절차

- 취약 경로를 일시 차단하고 캐시된 악성 콘텐츠를 삭제합니다.
- 세션 쿠키 회전과 강제 로그아웃 여부를 판단합니다.
- CSP 위반 리포트를 수집해 재발 경로를 분석합니다.
- 유입 경로(입력 폼, 관리자 화면, 외부 동기화)를 분류합니다.

주입 취약점은 단일 패치로 끝나지 않습니다. 입력, 저장, 렌더링, 권한의 네 경계를 함께 보완해야 재발률이 내려갑니다.


## 보안 테스트 자동화 예시

```python
# test_injection_regression.py
import requests

BASE = "https://staging.example.com"

def test_sql_injection_payload_rejected():
    payload = "' OR 1=1 --"
    r = requests.get(f"{BASE}/api/users", params={"name": payload}, timeout=5)
    assert r.status_code in (200, 400)
    assert "alice" not in r.text

def test_xss_payload_escaped():
    payload = "<script>alert(1)</script>"
    r = requests.post(f"{BASE}/comments", json={"body": payload}, timeout=5)
    assert r.status_code == 201
    page = requests.get(f"{BASE}/comments/latest", timeout=5)
    assert "<script>" not in page.text
```

보안 테스트를 CI에 넣으면 취약점이 회귀로 재유입되는 것을 줄일 수 있습니다. 한 번 고친 취약점은 테스트로 잠가야 합니다.

## OWASP 예시 시나리오

- A03 Injection: 검색 필터 파라미터를 SQL 구문으로 해석.
- A03 Injection(XSS): 댓글 렌더링 시 HTML 이스케이프 누락.
- A05 Security Misconfiguration: 디버그 템플릿에서 `innerHTML` 사용.

시나리오를 OWASP 항목에 매핑해두면 경영진/제품팀과 우선순위 대화를 할 때 공통 언어를 만들 수 있습니다.


## 부록: 팀 보안 리뷰 워크시트

다음 워크시트는 기능 배포 전 보안 리뷰에서 반복적으로 확인하는 항목을 표준화한 것입니다.

### 1) 자산과 경계 정의

| 항목 | 기록 예시 |
| --- | --- |
| 보호 대상 데이터 | 사용자 이메일, 결제 토큰, 내부 리포트 |
| 진입 경로 | 웹 폼, 모바일 API, 관리자 콘솔 |
| 신뢰 경계 | 인터넷-엣지, 엣지-앱, 앱-DB |
| 외부 의존성 | 결제 API, 메시지 큐, 파일 저장소 |

### 2) 통제 매핑

| 위협 | 예방 통제 | 탐지 통제 | 대응 통제 |
| --- | --- | --- | --- |
| 계정 탈취 | MFA, 비밀번호 정책 | 로그인 이상 징후 경보 | 세션 강제 종료, 자격 재설정 |
| 데이터 변조 | 입력 검증, 무결성 서명 | 감사 로그 무결성 검증 | 롤백, 포렌식 조사 |
| 서비스 과부하 | 레이트 리밋, WAF | 오류율/지연 경보 | 트래픽 차단, 임시 확장 |

### 3) 운영 점검 질문

- 이번 변경으로 새로 열리는 네트워크 포트가 있는가
- 권한 범위가 기존보다 넓어지는가
- 로그 스키마 변경이 탐지 규칙에 영향을 주는가
- 비밀 정보 또는 토큰 수명 정책이 달라지는가
- 장애 시 롤백 절차가 검증되어 있는가

### 4) 배포 전 검증 항목

| 항목 | 통과 기준 |
| --- | --- |
| 보안 테스트 | 고위험 실패 없음 |
| 설정 검증 | 디버그/임시 설정 제거 |
| 감사 로그 | 주요 이벤트 필드 누락 없음 |
| 문서 최신화 | 런북과 운영 가이드 업데이트 완료 |

워크시트의 목적은 문서를 늘리는 것이 아니라 의사결정 속도를 높이는 것입니다. 보안 검토가 반복될수록 질문과 답변이 짧아지고, 같은 사고가 재발할 가능성이 줄어듭니다.


## 부록: 주입 취약점 대응 우선순위

| 우선순위 | 작업 | 완료 기준 |
| --- | --- | --- |
| 1 | 취약 경로 임시 차단 | 재현 페이로드 차단 확인 |
| 2 | 코드 수정(바인딩/인코딩) | 보안 테스트 통과 |
| 3 | 로그 기반 영향 분석 | 영향 사용자/데이터 범위 확정 |
| 4 | 재발 방지 룰 추가 | 정적 분석/테스트 게이트 추가 |

우선순위를 명시하면 사고 중 논쟁 시간을 줄이고 복구 속도를 올릴 수 있습니다.


## OWASP Top 10에서 인젝션 취약점의 위치


OWASP Top 10 2021 기준으로 A03(Injection)은 SQL 인젝션과 XSS를 모두 포함합니다. 이 카테고리가 여전히 상위에 있는 이유는 단순합니다. 새 프레임워크가 나와도 입력값을 데이터로 취급하지 않는 코드는 계속 생기기 때문입니다.


| OWASP A03 세부 | 대응 원칙 | 검증 수단 |

| --- | --- | --- |

| SQL 인젝션 | 파라미터화 쿼리, ORM | SAST + 동적 테스트 |

| XSS(Reflected/Stored) | 출력 인코딩, CSP | CSP report-uri 모니터링 |

| Command Injection | 시스템 호출 회피, 허용 목록 | 코드 리뷰 체크리스트 |


프레임워크의 기본 보호를 신뢰하되, 예외 경로에서 보호가 없는 코드가 생기지 않는지 CI에서 정적 분석을 돌려야 합니다.


## 처음 질문으로 돌아가기

- **SQL 인젝션은 정확히 어떤 메커니즘으로 발생할까요?**
  - SELECT * FROM users WHERE id = ? 쿼리의 준비된 문 구성 방식과 HTML 템플릿의 자동 이스케이핑 메커니즘을 구분하면 구현이 명확해집니다.
- **ORM을 쓰면 정말 안전해질까요?**
  - 페이로드가 어떻게 파싱되고, 어느 단계에서 기각되거나 실행되는지를 단계별로 따라가면 대응 기준이 명확해집니다.
- **Reflected, Stored, DOM 기반 XSS는 어디서 갈릴까요?**
  - 쿼리 로그에서 의심스러운 문법 검사, XSS 시뮬레이션 테스트, 외부 라이브러리 업데이트 시 이스케이핑 규칙 변경 모니터링을 정의합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Information Security 101 (1/10): 정보보안이란 무엇인가?](./01-what-is-information-security.md)
- [Information Security 101 (2/10): 인증과 인가](./02-authentication-and-authorization.md)
- [Information Security 101 (3/10): 암호화와 해시](./03-cryptography-and-hash.md)
- [Information Security 101 (4/10): TLS와 인증서](./04-tls-and-certificates.md)
- [Information Security 101 (5/10): 웹 보안 기초](./05-web-security-basics.md)
- **SQL 인젝션과 XSS (현재 글)**
- 비밀 정보 관리 (예정)
- 권한 최소화 (예정)
- 로그와 감사 (예정)
- 보안 사고 대응 (예정)

<!-- toc:end -->

## 참고 자료

- [OWASP — SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [OWASP — XSS](https://owasp.org/www-community/attacks/xss/)
- [OWASP Cheat Sheet — XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/information-security-101/ko)

Tags: Computer Science, Security, SQLInjection, XSS, InputValidation, OutputEncoding
