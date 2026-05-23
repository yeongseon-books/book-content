---
series: web-development-101
episode: 6
title: "Web Development 101 (6/10): 인증과 세션"
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
  - Authentication
  - Sessions
  - Security
  - Backend
seo_description: 쿠키, 세션, JWT, OAuth로 사용자를 기억하는 방법을 설명합니다.
last_reviewed: '2026-05-15'
---

# Web Development 101 (6/10): 인증과 세션

이 글은 Web Development 101 시리즈의 여섯 번째 글입니다.

HTTP는 상태를 기억하지 않는 프로토콜입니다. 요청 하나가 끝나면 서버는 다음 요청이 같은 사용자인지 자동으로 알지 못합니다. 그런데 실제 서비스는 로그인 상태, 권한, 장바구니, 내 정보 같은 사용자 맥락을 계속 이어 가야 합니다. 이 간극을 메우는 도구가 인증과 세션입니다.

여기서는 인증과 인가의 차이, 쿠키와 세션의 동작 방식, JWT와 OAuth의 역할, 그리고 자주 놓치는 보안 기본기를 함께 정리하겠습니다.

![Web Development 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/06/06-01-concept-at-a-glance.ko.png)
*Web Development 101 6장 흐름 개요*

## 먼저 던지는 질문

- 인증과 인가는 무엇이 다를까요?
- 상태가 없는 HTTP 위에서 서버는 사용자를 어떻게 기억할까요?
- 쿠키와 세션은 어떤 식으로 맞물릴까요?

## 왜 이 주제가 중요한가

거의 모든 앱에는 로그인 기능이 들어갑니다. 여기가 약하면 계정 탈취, 세션 하이재킹, 권한 우회가 한 번에 이어집니다. 인증은 부가 기능이 아니라 서비스 전체를 떠받치는 기반입니다.

이 도구들의 이름과 역할을 분명히 알아 두면 많은 실수를 초기에 막을 수 있습니다. 비밀번호는 어디에 저장하면 안 되는지, JWT에 무엇을 넣으면 안 되는지, 쿠키 옵션을 왜 꼼꼼히 봐야 하는지 같은 판단이 전부 이 기반 위에서 나옵니다.

## 한눈에 보는 개념 지도

이 그림의 핵심은 서버가 비밀번호를 매번 다시 받지 않아도 된다는 점입니다. 로그인 한 번으로 세션 식별자를 만들고, 브라우저는 이후 요청마다 그 식별자를 쿠키로 자동 전송합니다.

### 직접 검증해 볼 포인트

- 로그인 요청 뒤 DevTools Application 탭에서 세션 쿠키가 실제로 저장되는지 확인합니다.
- `curl -c`와 `curl -b`로 쿠키 저장과 재사용이 분리되는지 검증합니다.
- 로그아웃 요청 뒤 같은 쿠키로 `/me`를 호출했을 때 401이 나는지 확인합니다.

**기대 결과:** 로그인 직후에는 세션 쿠키가 생기고, 로그아웃 뒤에는 같은 쿠키를 보내도 보호된 엔드포인트가 더는 사용자를 인정하지 않습니다.

**실패 모드:** 쿠키에 `HttpOnly`, `Secure`, `SameSite`를 두지 않으면 탈취와 재사용 위험이 커집니다. JWT에 민감 정보를 넣으면 서명만으로는 내용을 숨길 수 없습니다.

## 먼저 알아둘 용어

- **Authentication**: 내가 누구인지 확인하는 과정입니다.
- **Authorization**: 내가 무엇을 할 수 있는지 결정하는 과정입니다.
- **Session**: 서버가 보관하는 사용자 상태입니다.
- **Cookie**: 브라우저가 도메인 단위로 저장하는 key/value 데이터입니다.
- **JWT**: 서버가 서명한 self-describing token입니다.

## 전후 비교로 보는 인증 흐름

**Before (매 요청마다 비밀번호)**

```python
requests.get("/api/me", auth=("alice", "secret"))  # 비밀번호가 반복해서 흐릅니다
```

**After (세션 쿠키)**

```python
s = requests.Session()
s.post("/login", json={"id": "alice", "pw": "secret"})
s.get("/api/me")  # 쿠키가 자동으로 함께 전송됩니다
```

비밀번호는 로그인 시점에만 확인하고, 이후에는 세션 식별자로 사용자를 이어 가는 편이 안전합니다.

## 로그인 흐름을 다섯 단계로 만들어 보기

### 1단계 — Flask 세션 로그인 만들기

```python
# app.py
from flask import Flask, session, request, jsonify
app = Flask(__name__)
app.secret_key = "dev-only-change-me"

USERS = {"alice": "secret"}

@app.post("/login")
def login():
    data = request.get_json()
    if USERS.get(data["id"]) == data["pw"]:
        session["user"] = data["id"]
        return jsonify(ok=True)
    return jsonify(ok=False), 401

@app.get("/me")
def me():
    user = session.get("user")
    if not user: return jsonify(error="unauth"), 401
    return jsonify(user=user)
```

이 예제에서 서버는 로그인 성공 시 `session["user"]`에 사용자 ID를 저장합니다. 이후 `/me` 요청은 세션에 값이 있는지 보고 로그인 여부를 판단합니다.

### 2단계 — 쿠키가 실제로 생기는지 확인하기

```bash
curl -c c.txt -X POST -H "Content-Type: application/json" -d '{"id":"alice","pw":"secret"}' http://localhost:5000/login
curl -b c.txt http://localhost:5000/me  # → {"user":"alice"}
```

첫 번째 명령은 서버가 내려준 쿠키를 파일에 저장하고, 두 번째 명령은 그 쿠키를 다시 보내서 로그인 상태를 재사용합니다.

### 3단계 — 로그아웃 추가하기

```python
@app.post("/logout")
def logout():
    session.clear()
    return jsonify(ok=True)
```

로그아웃은 세션 정보를 지우는 작업입니다. 서버 기준 기억을 지우면 브라우저가 같은 세션 ID를 보내도 더는 유효하지 않습니다.

### 4단계 — JWT 발급하기

```python
# jwt_demo.py
import jwt, time
SECRET = "dev"
token = jwt.encode({"sub": "alice", "exp": time.time() + 3600}, SECRET, algorithm="HS256")
print(jwt.decode(token, SECRET, algorithms=["HS256"]))
```

JWT는 서버가 상태를 직접 저장하지 않고도 사용자를 식별하게 도와줍니다. 대신 서명 검증과 만료 시간 관리가 중요합니다.

### 5단계 — Authorization 헤더로 호출하기

```python
import requests
requests.get("/api/me", headers={"Authorization": f"Bearer {token}"})
```

세션 쿠키 대신 `Authorization` 헤더에 토큰을 넣어 요청하는 방식입니다. 모바일 앱과 분산 시스템에서 자주 보게 됩니다.

## 이 코드에서 먼저 봐야 할 점

- 세션은 서버 메모리나 데이터베이스 같은 저장소를 필요로 합니다.
- JWT는 서버가 매 요청마다 서명만 검증해도 되므로 분산 환경에 잘 맞습니다.
- 쿠키에는 `HttpOnly`, `Secure`, `SameSite` 같은 보안 옵션이 꼭 필요합니다.

## 여기서 자주 헷갈립니다

1. **비밀번호를 평문으로 저장하는 경우**: 반드시 hash 함수로 저장해야 합니다.
2. **JWT 안에 민감한 비밀을 넣는 경우**: JWT는 서명되었을 뿐 암호화된 것이 아닙니다.
3. **쿠키 보안 옵션을 비워 두는 경우**: XSS와 CSRF 위험이 커집니다.
4. **만료 시간이 없는 토큰을 쓰는 경우**: 한 번 유출되면 오래 남습니다.
5. **권한 검사를 로그인 한 번으로 끝내는 경우**: 보호된 모든 엔드포인트에서 다시 확인해야 합니다.

## 운영에서는 이렇게 보입니다

전통적인 웹앱은 세션 쿠키와 CSRF 토큰 조합을 많이 씁니다. SPA, 모바일 앱, 마이크로서비스 환경은 JWT를 더 자주 선택합니다. Google, GitHub 로그인은 OAuth 2.0 흐름 위에서 돌아가며, 서비스는 사용자 비밀번호 대신 외부 제공자의 인증 결과를 받습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 비밀번호는 hash로 저장하고 토큰 수명은 짧게 둡니다.
- 쿠키 기본값은 `HttpOnly + Secure + SameSite=Lax` 쪽으로 생각합니다.
- 권한 검사는 middleware처럼 공통 경로에 둡니다.
- refresh token으로 수명을 분리합니다.
- 유출을 전제로 설계하고, 모든 credential이 폐기 가능해야 한다고 봅니다.

## 체크리스트

- [ ] 인증과 인가의 차이를 설명할 수 있습니다.
- [ ] 세션과 JWT의 장단점을 알고 있습니다.
- [ ] 비밀번호를 저장할 때 hash 함수를 써야 함을 알고 있습니다.
- [ ] 쿠키 보안 플래그 세 가지를 말할 수 있습니다.
- [ ] OAuth 흐름을 한 줄로 설명할 수 있습니다.

## 연습 문제

1. Flask 세션으로 login/logout을 만들고 DevTools에서 쿠키를 직접 확인해 보세요.
2. JWT를 발급한 뒤 만료 시간이 지나면 거부되는지 확인해 보세요.
3. 엔드포인트 하나에 인증 middleware를 적용하고 비로그인 요청이 401을 받는지 검증해 보세요.

## 정리와 다음 글

HTTP는 상태를 기억하지 않지만, 웹앱은 쿠키, 세션, 토큰, OAuth를 이용해 사용자 맥락을 이어 갑니다. 인증 구조를 제대로 잡아야 나머지 기능도 안전하게 쌓을 수 있습니다. 다음 글에서는 이렇게 확인한 사용자 데이터를 영속적으로 저장하는 데이터베이스 연결을 보겠습니다.

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

## 실전 앵커 모음: 인증 경계을 운영 문서로 바꾸기

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

- **인증과 인가는 무엇이 다를까요?**
  - 인증은 `/login`에서 `id`와 `pw`를 확인해 사용자가 누구인지 밝히는 단계이고, 인가는 로그인된 뒤 그 사용자가 특정 API를 호출할 권한이 있는지 판단하는 단계입니다. 글에서도 `/me` 같은 보호된 엔드포인트는 로그인 여부와 별개로 매번 다시 확인해야 한다고 설명했습니다.
- **상태가 없는 HTTP 위에서 서버는 사용자를 어떻게 기억할까요?**
  - 서버는 로그인 성공 뒤 `session["user"] = data["id"]`처럼 사용자 상태를 저장하고, 브라우저는 세션 쿠키를 다음 요청마다 자동으로 보냅니다. 또는 JWT를 발급해 `Authorization: Bearer ...` 헤더로 보내는 방식처럼, 상태 없는 HTTP 위에 식별자를 얹어 사용자를 이어 갑니다.
- **쿠키와 세션은 어떤 식으로 맞물릴까요?**
  - 세션의 실제 데이터는 서버 쪽 저장소에 있고, 쿠키는 그 세션을 다시 찾게 해 주는 식별자 전달 수단입니다. `curl -c c.txt`로 쿠키를 저장하고 `curl -b c.txt`로 재사용하는 예시, 그리고 `session.clear()`로 로그아웃하는 예시가 이 연결을 그대로 보여 줍니다.

<!-- toc:begin -->
## 시리즈 목차

- [Web Development 101 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [Web Development 101 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [Web Development 101 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [Web Development 101 (4/10): HTTP와 API](./04-http-and-api.md)
- [Web Development 101 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- **인증과 세션 (현재 글)**
- 데이터베이스 연결 (예정)
- 배포 (예정)
- 성능과 캐싱 (예정)
- 작은 웹앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Using HTTP cookies (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)
- [Flask sessions](https://flask.palletsprojects.com/en/stable/quickstart/#sessions)
- [OAuth 2.0 Authorization Framework (RFC 6749)](https://www.rfc-editor.org/rfc/rfc6749)

### 보안 가이드
- [JWT introduction](https://jwt.io/introduction)
- [Session Management Cheat Sheet (OWASP)](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

- [web-development-101 예제 코드 저장소 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/web-development-101/ko)

Tags: Computer Science, WebDevelopment, Authentication, Sessions, Security, Backend
