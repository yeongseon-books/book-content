---
series: web-development-101
episode: 6
title: "Web Development 101 (6/10): 인증과 세션"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/208"
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
  - Authentication
  - Sessions
  - Security
  - Backend
seo_description: 쿠키, 세션, JWT, OAuth로 사용자를 기억하는 방법을 설명합니다.
last_reviewed: '2026-05-15'
---

# Web Development 101 (6/10): 인증과 세션

거의 모든 앱에는 로그인 기능이 들어갑니다. 여기가 약하면 계정 탈취, 세션 하이재킹, 권한 우회가 한 번에 이어집니다. 인증은 부가 기능이 아니라 서비스 전체를 떠받치는 기반입니다.

이 글은 Web Development 101 시리즈의 여섯 번째 글입니다.

HTTP는 상태를 기억하지 않는 프로토콜입니다. 요청 하나가 끝나면 서버는 다음 요청이 같은 사용자인지 자동으로 알지 못합니다. 그런데 실제 서비스는 로그인 상태, 권한, 장바구니, 내 정보 같은 사용자 맥락을 계속 이어 가야 합니다. 이 간극을 메우는 도구가 인증과 세션입니다.

여기서는 인증과 인가의 차이, 쿠키와 세션의 동작 방식, JWT와 OAuth의 역할, 그리고 자주 놓치는 보안 기본기를 함께 정리하겠습니다.

![Web Development 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/06/06-01-concept-at-a-glance.ko.png)
*Web Development 101 6장 흐름 개요*

> HTTP는 상태를 기억하지 않으므로, 인증·세션은 매 요청에 같은 사용자임을 증명하는 토큰(쿠키/JWT)을 끼워 넣는 작업입니다 — 그래서 보안 사고는 거의 항상 이 토큰을 어디에 두고 어떻게 검증하느냐에서 발생합니다.

## 이 글에서 다룰 문제

- 인증과 인가는 무엇이 다를까요?
- 상태가 없는 HTTP 위에서 서버는 사용자를 어떻게 기억할까요?
- 쿠키와 세션은 어떤 식으로 맞물릴까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 주제가 중요한가

이 도구들의 이름과 역할을 분명히 알아 두면 많은 실수를 초기에 막을 수 있습니다. 비밀번호는 어디에 저장하면 안 되는지, JWT에 무엇을 넣으면 안 되는지, 쿠키 옵션을 왜 꼼꼼히 봐야 하는지 같은 판단이 전부 이 기반 위에서 나옵니다.

## 인증 vs 인가

```
인증 (Authentication): 당신이 누구인지 확인
  예) 아이디/비밀번호로 로그인 → "당신은 alice입니다"

인가 (Authorization): 당신이 무엇을 할 수 있는지 결정
  예) alice는 admin 역할 → "/admin 페이지 접근 허용"
       bob은 user 역할  → "/admin 페이지 접근 거부 (403)"
```

```python
# 401 Unauthorized: 로그인이 필요한 상태
# 403 Forbidden: 로그인은 됐지만 권한이 없는 상태

@app.get("/admin")
def admin_page():
    user = get_current_user()
    if not user:
        return jsonify(error={"code": "UNAUTHORIZED"}), 401   # 로그인 안 됨
    if user["role"] != "admin":
        return jsonify(error={"code": "FORBIDDEN"}), 403      # 권한 없음
    return jsonify(data="관리자 전용 데이터")
```

## 쿠키와 세션의 동작 방식

```
로그인 흐름:
  1. POST /login  (id, password 전송)
  2. 서버: 비밀번호 검증 → 세션 생성 → 세션 ID를 쿠키로 전송
     Set-Cookie: session_id=abc123; HttpOnly; Secure; SameSite=Lax
  3. 브라우저: 쿠키 저장

이후 요청마다:
  4. GET /me  (자동으로 쿠키 포함)
     Cookie: session_id=abc123
  5. 서버: 세션 ID로 사용자 조회 → 인증 성공

로그아웃:
  6. POST /logout
  7. 서버: 세션 삭제
  8. 이후 같은 세션 ID를 보내도 → 401 Unauthorized
```

## Flask 세션 구현

```python
from flask import Flask, session, request, jsonify
import hashlib, os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,    # JavaScript에서 접근 불가 (XSS 방어)
    SESSION_COOKIE_SECURE=True,      # HTTPS에서만 전송
    SESSION_COOKIE_SAMESITE="Lax",  # CSRF 부분 방어
    PERMANENT_SESSION_LIFETIME=3600, # 1시간 후 만료
)

# 실제 서비스에서는 bcrypt/argon2 같은 단방향 해시 사용
def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

USERS = {
    "alice": hash_password("secret123")
}

@app.post("/login")
def login():
    data = request.get_json()
    user_id = data.get("id")
    password = data.get("pw")

    stored_hash = USERS.get(user_id)
    if not stored_hash or stored_hash != hash_password(password):
        return jsonify(error={"code": "INVALID_CREDENTIALS"}), 401

    session["user_id"] = user_id
    session.permanent = True
    return jsonify(ok=True, user_id=user_id)

@app.get("/me")
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(error={"code": "UNAUTHORIZED"}), 401
    return jsonify(user_id=user_id)

@app.post("/logout")
def logout():
    session.clear()
    return jsonify(ok=True)
```

## curl로 쿠키 흐름 확인

```bash
# 1. 로그인 (쿠키를 파일에 저장)
curl -c cookies.txt -X POST \
  -H "Content-Type: application/json" \
  -d '{"id":"alice","pw":"secret123"}' \
  http://localhost:5000/login

# 2. 쿠키 파일 내용 확인
cat cookies.txt

# 3. 인증된 요청 (저장된 쿠키 사용)
curl -b cookies.txt http://localhost:5000/me
# → {"user_id": "alice"}

# 4. 로그아웃
curl -b cookies.txt -c cookies.txt -X POST http://localhost:5000/logout

# 5. 로그아웃 후 같은 쿠키로 요청
curl -b cookies.txt http://localhost:5000/me
# → 401 Unauthorized
```

## JWT (JSON Web Token)

세션은 서버가 상태를 저장합니다. JWT는 서버 저장 없이 토큰 자체에 정보를 담고 서명으로 위조를 방지합니다.

```
JWT 구조:
  eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhbGljZSIsImV4cCI6MTczMjI4ODAwMH0.abc123
  │                    │                                              │
  Header (알고리즘)     Payload (사용자 정보, 만료시간)               Signature

Header: {"alg": "HS256", "typ": "JWT"}
Payload: {"sub": "alice", "role": "user", "exp": 1732288000}
Signature: HMAC-SHA256(header + "." + payload, secret_key)
```

```python
import jwt
import time
import os

SECRET = os.environ.get("JWT_SECRET", "dev-only")

def create_token(user_id: str, role: str = "user") -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "iat": int(time.time()),          # 발급 시각
        "exp": int(time.time()) + 3600,   # 만료: 1시간 후
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ValueError("토큰 만료")
    except jwt.InvalidTokenError:
        raise ValueError("유효하지 않은 토큰")

# 발급
token = create_token("alice", role="admin")
print(token)

# 검증
payload = verify_token(token)
print(payload["sub"])   # "alice"
print(payload["role"])  # "admin"
```

```python
# JWT를 Authorization 헤더로 전송하는 API
@app.get("/api/profile")
def profile():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify(error={"code": "UNAUTHORIZED"}), 401
    try:
        payload = verify_token(auth[7:])
    except ValueError as e:
        return jsonify(error={"code": "INVALID_TOKEN", "message": str(e)}), 401
    return jsonify(user_id=payload["sub"], role=payload["role"])
```

```bash
# JWT로 API 호출
TOKEN=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"id":"alice","pw":"secret"}' http://localhost:5000/login | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/profile
```

## 세션 vs JWT 선택 기준

```
세션 (서버 저장)             JWT (Stateless)
───────────────────────────────────────────────────
서버가 세션 저장소 관리     서버에 상태 저장 불필요
즉각 폐기 가능              만료 전까지 폐기 어려움
단일 서버에 적합            분산 환경, 마이크로서비스에 적합
CSRF 방어 필요              Authorization 헤더 사용 시 CSRF 없음
쿠키로 자동 전송            클라이언트가 직접 헤더에 추가
```

## 비밀번호 안전 저장

```python
# 절대 안 되는 것
import hashlib
password_stored = hashlib.md5(password.encode()).hexdigest()  # MD5: 무지개 테이블 공격 취약
password_stored = password  # 평문 저장

# 올바른 방법: bcrypt
import bcrypt

# 저장 시
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))

# 검증 시
bcrypt.checkpw(password.encode(), hashed)  # True/False
```

bcrypt의 `rounds` 파라미터가 높을수록 해시 계산이 느려져 brute force 공격에 강해집니다. 하드웨어 성능에 맞춰 로그인 응답이 약 100-300ms 걸리도록 조정하는 것이 일반적입니다.

## 쿠키 보안 옵션

```http
Set-Cookie: session_id=abc123; HttpOnly; Secure; SameSite=Lax; Max-Age=3600; Path=/
```

```
옵션         의미                              없으면?
─────────────────────────────────────────────────────────
HttpOnly    JavaScript에서 쿠키 접근 불가    XSS로 쿠키 탈취 가능
Secure      HTTPS에서만 쿠키 전송            HTTP로 쿠키가 평문 전송됨
SameSite    다른 사이트에서 쿠키 전송 제한   CSRF 공격 취약
Max-Age     만료 시간                         세션 쿠키 (브라우저 종료 시 삭제)
Path        쿠키가 전송될 경로               /: 모든 경로, /api: API만
```

## OAuth 2.0: 소셜 로그인 흐름

직접 비밀번호를 관리하지 않고 Google, GitHub 같은 외부 서비스에 인증을 위임하는 표준입니다.

```
사용자          앱 서버            Google
  │               │                  │
  │ "Google 로그인" 클릭              │
  │──────────────►│                  │
  │               │ redirect to Google OAuth URL
  │◄──────────────│                  │
  │     구글 로그인 페이지로 이동     │
  │──────────────────────────────────►│
  │               │    로그인 + 앱 권한 승인
  │◄──────────────────────────────────│
  │  callback URL?code=AUTH_CODE      │
  │──────────────►│                  │
  │               │ POST /token {code}│
  │               │──────────────────►│
  │               │◄──────────────────│
  │               │   access_token   │
  │               │ GET /userinfo     │
  │               │──────────────────►│
  │               │◄──────────────────│
  │               │  {email, name}   │
  │   로그인 완료 │                  │
  │◄──────────────│                  │
```

Flask에서 Google OAuth를 구현하는 최소 예제입니다.

```python
import os
import requests
from flask import Flask, redirect, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = "https://example.com/auth/callback"

@app.route("/auth/google")
def google_login():
    """사용자를 Google 로그인 페이지로 리다이렉트"""
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?{query}")

@app.route("/auth/callback")
def google_callback():
    """Google이 code를 들고 여기로 돌아옴"""
    code = request.args.get("code")
    if not code:
        return "인증 실패", 400

    # code → access_token 교환
    token_res = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    })
    access_token = token_res.json()["access_token"]

    # access_token으로 사용자 정보 조회
    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    # 세션에 사용자 저장 (또는 DB에서 user_id 찾기)
    session["user_email"] = user_info["email"]
    session["user_name"] = user_info["name"]
    return redirect("/dashboard")
```

핵심은 앱 서버가 **비밀번호를 절대 받지 않는다**는 점입니다. 앱은 오직 사용자가 Google 계정을 소유하고 있음을 확인하는 증명서(code → token)만 주고받습니다.

## 토큰 갱신: Refresh Token 패턴

JWT access_token은 짧게(15분~1시간), refresh_token은 길게(30일) 발급합니다.

```python
import jwt, datetime, secrets

SECRET = os.environ["JWT_SECRET"]

def create_tokens(user_id: int) -> dict:
    """access + refresh 토큰 쌍 발급"""
    now = datetime.datetime.utcnow()
    access_payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=15),  # 15분
        "type": "access",
    }
    refresh_payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + datetime.timedelta(days=30),     # 30일
        "type": "refresh",
        "jti": secrets.token_hex(16),  # JWT ID — 폐기 리스트에 활용
    }
    return {
        "access_token": jwt.encode(access_payload, SECRET, algorithm="HS256"),
        "refresh_token": jwt.encode(refresh_payload, SECRET, algorithm="HS256"),
    }

@app.route("/auth/refresh", methods=["POST"])
def refresh():
    """refresh_token으로 새 access_token 발급"""
    refresh_token = request.json.get("refresh_token")
    try:
        payload = jwt.decode(refresh_token, SECRET, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            return {"error": "invalid token type"}, 401
        # DB에서 jti가 폐기 목록에 있는지 확인 (선택)
        tokens = create_tokens(payload["sub"])
        return tokens
    except jwt.ExpiredSignatureError:
        return {"error": "refresh token expired, login again"}, 401
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|------|------|-------------|
| 비밀번호를 평문 또는 MD5로 저장 | DB 유출 시 즉시 노출 | bcrypt, argon2id 사용 |
| JWT에 비밀번호나 민감 정보 저장 | Base64 디코딩으로 내용 노출 | JWT는 서명만, 암호화 아님 |
| 쿠키에 HttpOnly 없음 | XSS로 세션 쿠키 탈취 | 항상 HttpOnly 설정 |
| 만료 시간 없는 JWT | 유출 시 영구 사용 가능 | access token 15분, refresh 1주 |
| 권한 검사를 로그인 한 번으로 끝내기 | 모든 API에서 권한 재확인 | 미들웨어로 매 요청 검증 |
| secret_key를 코드에 하드코딩 | 저장소 노출 시 모든 토큰 위조 가능 | 환경 변수로 관리 |

## 운영에서는 이렇게 보입니다

전통적인 웹앱은 세션 쿠키와 CSRF 토큰 조합을 많이 씁니다. SPA, 모바일 앱, 마이크로서비스 환경은 JWT를 더 자주 선택합니다. Google, GitHub 로그인은 OAuth 2.0 흐름 위에서 돌아가며, 서비스는 사용자 비밀번호 대신 외부 제공자의 인증 결과를 받습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 비밀번호는 hash로 저장하고 토큰 수명은 짧게 둡니다.
- 쿠키 기본값은 `HttpOnly + Secure + SameSite=Lax` 쪽으로 생각합니다.
- 권한 검사는 middleware처럼 공통 경로에 둡니다.
- refresh token으로 수명을 분리합니다.
- 유출을 전제로 설계하고, 모든 credential이 폐기 가능해야 한다고 봅니다.

## 운영 체크리스트

- [ ] 인증과 인가의 차이를 설명할 수 있습니다.
- [ ] 세션과 JWT의 장단점을 알고 있습니다.
- [ ] 비밀번호를 저장할 때 bcrypt를 써야 함을 알고 있습니다.
- [ ] 쿠키 보안 플래그 세 가지를 말할 수 있습니다.
- [ ] 401과 403의 차이를 설명할 수 있습니다.

## 연습 문제

1. Flask 세션으로 login/logout을 만들고 DevTools에서 쿠키를 직접 확인해 보세요.
2. JWT를 발급한 뒤 만료 시간이 지나면 거부되는지 확인해 보세요.
3. 엔드포인트 하나에 인증 middleware를 적용하고 비로그인 요청이 401을 받는지 검증해 보세요.

## 정리와 다음 글

HTTP는 상태를 기억하지 않지만, 웹앱은 쿠키, 세션, 토큰, OAuth를 이용해 사용자 맥락을 이어 갑니다. 인증 구조를 제대로 잡아야 나머지 기능도 안전하게 쌓을 수 있습니다. 다음 글에서는 이렇게 확인한 사용자 데이터를 영속적으로 저장하는 데이터베이스 연결을 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Web Development 101 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [Web Development 101 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [Web Development 101 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [Web Development 101 (4/10): HTTP와 API](./04-http-and-api.md)
- [Web Development 101 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- **Web Development 101 (6/10): 인증과 세션 (현재 글)**
- [Web Development 101 (7/10): 데이터베이스 연결](./07-connecting-to-database.md)
- [Web Development 101 (8/10): 배포](./08-deployment.md)
- [Web Development 101 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- [작은 웹앱 만들기](./10-building-a-small-web-app.md)

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
