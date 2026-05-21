---
series: backend-development-101
episode: 6
title: "Backend Development 101 (6/10): 인증과 권한"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Backend
  - Auth
  - Security
  - JWT
  - Python
seo_description: 인증(AuthN)과 권한(AuthZ)의 차이를 이해하고 bcrypt와 JWT를 사용하여 안전한 백엔드 보안 시스템을 구축하는 기본기를 익힙니다.
last_reviewed: '2026-05-15'
---

# Backend Development 101 (6/10): 인증과 권한

이 글은 Backend Development 101 시리즈의 6번째 글입니다.

로그인 기능은 단순해 보여도 서버 관점에서는 두 가지 질문이 동시에 따라옵니다. 사용자가 누구인지 증명해야 하고, 이번 요청에서 무엇을 해도 되는지도 따로 판단해야 합니다.

이 글은 Backend Development 101 시리즈의 여섯 번째 글입니다. 여기서는 authentication과 authorization을 분리해서 이해하고, FastAPI에서 안전한 기본 흐름을 어떻게 잡는지 살펴보겠습니다.

![Backend Development 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/06/06-01-concept-at-a-glance.ko.png)
*Backend Development 101 6장 흐름 개요*

## 먼저 던지는 질문

- authentication과 authorization은 무엇이 다를까요?
- 비밀번호 저장에서 최소한으로 지켜야 할 안전 기준은 무엇일까요?
- session과 JWT는 각각 언제 더 자연스러울까요?

## 왜 중요한가

인증 코드는 단 한 줄의 실수로도 회사 전체를 위험하게 만들 수 있는 영역입니다. 비밀번호를 평문으로 저장했다거나, 토큰 검증을 빠뜨렸다거나, 만료 시간이 없는 토큰을 발급했다는 사실은 몇 년 뒤 보안 사고로 돌아오기 쉽습니다.

그래서 인증 코드는 화려할수록 좋은 것이 아니라, 작고 표준적일수록 좋습니다. 직접 발명한 보안 로직보다 검증된 라이브러리와 단순한 구조가 훨씬 안전합니다.

> authentication은 신원을 확인하고, authorization은 그 신원이 무엇을 할 수 있는지 판단합니다.

## 한눈에 보는 개념

authentication은 “누구인가”를 묻고, authorization은 “무엇을 할 수 있는가”를 묻습니다. 두 문제를 섞어 생각하면 인증 흐름이 점점 불명확해집니다.

## 핵심 용어

- **Authentication**: 사용자의 신원을 확인하는 과정입니다.
- **Authorization**: 특정 행동을 허용할지 판단하는 과정입니다.
- **Hash**: 비밀번호를 되돌릴 수 없도록 변환한 값입니다.
- **Session**: 사용자 상태를 서버 쪽에 저장하는 방식입니다.
- **JWT**: 서버 상태 없이도 검증할 수 있는 서명된 토큰입니다.

## 개선 전/개선 후

**Before (평문 비밀번호)**

```python
def register(name, password):
    db.execute("INSERT INTO users(name, pw) VALUES(?, ?)", (name, password))
```

**After (해시 후 검증)**

```python
from passlib.hash import bcrypt
def register(name, password):
    pw_hash = bcrypt.hash(password)
    db.execute("INSERT INTO users(name, pw_hash) VALUES(?, ?)", (name, pw_hash))

def verify(name, password):
    row = db.fetchone("SELECT pw_hash FROM users WHERE name=?", (name,))
    return row and bcrypt.verify(password, row["pw_hash"])
```

데이터베이스가 유출되더라도 평문 비밀번호가 바로 드러나지 않게 만드는 것이 핵심입니다. 인증에서 가장 먼저 지켜야 할 기본선이 바로 여기입니다.

## 실습: 다섯 단계로 보는 인증 흐름

### 단계 1 — 비밀번호 해시

```python
# 1_hash.py
from passlib.hash import bcrypt
hashed = bcrypt.hash("mySecret123")
print(bcrypt.verify("mySecret123", hashed))  # True
```

비밀번호는 저장이 아니라 해시가 되어야 합니다. 같은 문자열도 매번 다른 해시가 나올 수 있고, 검증은 비교 함수로 수행한다는 감각을 먼저 잡아야 합니다.

### 단계 2 — 토큰 발급

```python
# 2_jwt.py
import jwt, time
SECRET = "change-me"
token = jwt.encode({"sub": "alice", "exp": time.time() + 3600}, SECRET, algorithm="HS256")
print(token)
```

JWT는 사용자의 identity를 담은 서명된 토큰입니다. 중요한 점은 영원히 유효한 토큰을 만들지 않는 것입니다. 만료 시간이 반드시 들어가야 합니다.

### 단계 3 — 토큰 검증

```python
# 3_verify.py
import jwt
data = jwt.decode(token, SECRET, algorithms=["HS256"])
print(data["sub"])
```

서버는 매 요청마다 토큰을 검증하고, 그 안의 subject가 누구인지 확인합니다. 로그인은 한 번이지만 검증은 모든 보호된 요청마다 반복됩니다.

### 단계 4 — 엔드포인트 보호

```python
# 4_protected.py
from fastapi import FastAPI, Depends, HTTPException, Header

app = FastAPI()

def current_user(authorization: str = Header(...)):
    try:
        token = authorization.removeprefix("Bearer ")
        data = jwt.decode(token, SECRET, algorithms=["HS256"])
        return data["sub"]
    except Exception:
        raise HTTPException(401)

@app.get("/me")
def me(user: str = Depends(current_user)):
    return {"user": user}
```

보호된 endpoint는 요청 헤더에서 토큰을 꺼내고, 검증에 성공했을 때만 다음 로직으로 넘어가게 만듭니다. 인증 실패를 명시적으로 막는 경계가 바로 여기입니다.

### 단계 5 — 역할 기반 권한

```python
# 5_role.py
def require_role(role: str):
    def _dep(user: dict = Depends(current_user_with_role)):
        if user["role"] != role:
            raise HTTPException(403)
        return user
    return _dep

@app.delete("/admin/users/{uid}")
def delete_user(uid: int, _: dict = Depends(require_role("admin"))):
    return {"deleted": uid}
```

인증이 “누구인가”를 확인했다면, 권한은 “이 역할이 이 작업을 해도 되는가”를 확인합니다. 두 단계가 분리되어 있어야 정책을 읽고 바꾸기 쉽습니다.

## 검증 포인트

**Expected output:** 올바른 비밀번호는 토큰을 발급받고, 잘못된 비밀번호는 `401`, 권한 없는 `admin` 경로 접근은 `403`으로 끝나야 합니다.

### 먼저 확인할 실패 지점

- 비밀번호 검증이 계속 실패하면 해시 저장과 verify 경로가 같은 알고리즘을 쓰는지 봅니다.
- JWT가 만료 뒤에도 통과하면 `exp` 검증이 실제로 실행되는지 확인합니다.
- 권한 검사가 프론트엔드에만 있으면 서버에서 같은 경로를 반드시 다시 막아야 합니다.

## 이 코드에서 먼저 볼 점

- 비밀번호는 절대 평문으로 저장하지 않습니다.
- JWT secret은 코드에 하드코딩하지 않고 환경 변수나 secret manager에 둡니다.
- 401과 403은 서로 다른 의미를 가집니다.

401은 인증되지 않았다는 뜻이고, 403은 인증은 되었지만 권한이 없다는 뜻입니다. 이 차이를 분명히 지켜야 클라이언트와 운영자가 상황을 정확히 해석할 수 있습니다.

## 자주 하는 실수 5가지

1. **MD5나 SHA-1로 비밀번호를 해싱하는 실수**입니다. bcrypt나 argon2 같은 전용 알고리즘을 써야 합니다.
2. **JWT에 `exp`를 넣지 않는 실수**입니다. 토큰이 사실상 영구 유효해집니다.
3. **JWT를 localStorage에만 저장하는 실수**입니다. XSS에 노출될 수 있어 httpOnly cookie 같은 대안도 검토해야 합니다.
4. **권한 검사를 프론트엔드에서만 하는 실수**입니다. 서버가 항상 다시 검사해야 합니다.
5. **모든 endpoint를 무조건 인증 뒤에 숨기는 실수**입니다. `/healthz`, `/login`처럼 공개되어야 할 경로는 명시적으로 분리해야 합니다.

## 운영에서는 이렇게 드러납니다

대부분의 SaaS 제품은 bcrypt + JWT + role 기반 권한 모델에서 출발합니다. 규모가 커지면 OAuth2, MFA, 세분화된 policy가 추가되지만, 핵심은 여전히 인증과 권한을 분리해 두는 것입니다.

운영에서 중요한 것은 “로그인 기능이 있다”가 아니라 “인증 실패와 권한 거부를 추적하고 설명할 수 있다”입니다. 구조가 단순할수록 그 설명이 쉬워집니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 인증 코드는 작고 표준 라이브러리 중심이어야 합니다.
- secret은 환경 변수와 secret manager에만 둡니다.
- access token은 짧게, refresh token은 별도 전략으로 다룹니다.
- permission은 role이나 policy로 명시적으로 모델링합니다.
- 인증 실패 로그는 brute force 징후일 수 있으므로 반드시 관찰합니다.

## 체크리스트

- [ ] bcrypt로 해시와 검증을 할 수 있습니다.
- [ ] 만료 시간이 있는 JWT를 발급할 수 있습니다.
- [ ] FastAPI endpoint를 보호할 수 있습니다.
- [ ] 401과 403의 차이를 설명할 수 있습니다.
- [ ] role 기반 권한 검사를 작성할 수 있습니다.

## 연습 문제

1. `/register`, `/login`, `/me` endpoint를 가진 서비스를 만들어 보세요.
2. JWT 만료 시간을 1분으로 줄이고 만료 후 `401`이 나는지 확인해 보세요.
3. `admin` role만 접근 가능한 `/admin` 경로를 추가해 보세요.

## 정리와 다음 글

authentication은 identity이고 authorization은 permission입니다. 다음 글에서는 운영자가 시스템을 보는 눈인 Logging과 Error Handling을 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **authentication과 authorization은 무엇이 다를까요?**
  - 본문의 기준은 인증과 권한를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **비밀번호 저장에서 최소한으로 지켜야 할 안전 기준은 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **session과 JWT는 각각 언제 더 자연스러울까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Backend Development 101 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [Backend Development 101 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- [Backend Development 101 (3/10): Routing과 Controller](./03-routing-and-controllers.md)
- [Backend Development 101 (4/10): Service Layer](./04-service-layer.md)
- [Backend Development 101 (5/10): Database Layer](./05-database-layer.md)
- **인증과 권한 (현재 글)**
- Logging과 Error Handling (예정)
- 백엔드 테스트 (예정)
- 백엔드 배포 (예정)
- 운영 가능한 백엔드 구조 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Passlib bcrypt docs](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)

- [JWT Introduction](https://jwt.io/introduction)

Tags: Backend, Auth, Security, JWT, Python
