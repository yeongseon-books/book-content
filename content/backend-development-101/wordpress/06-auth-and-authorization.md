---
series: backend-development-101
episode: 6
title: "바이브코딩을 위한 백엔드 개발 기초 (6/10): 인증과 권한"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - Backend
  - Auth
  - Security
  - JWT
  - Python
seo_description: AI가 만든 인증 코드에서 놓치기 쉬운 보안 문제를 짚고, authentication과 authorization을 올바르게 분리하는 방법을 바이브코딩 관점에서 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 백엔드 개발 기초 (6/10): 인증과 권한

이 글은 **바이브코딩을 위한 백엔드 개발 기초** 시리즈의 6번째 글입니다. AI에게 코드를 맡기기 전에 백엔드가 어떻게 동작하는지 이해해야 원하는 결과를 얻을 수 있습니다.

---

AI에게 "로그인 기능 만들어줘"라고 하면 코드가 나옵니다. 하지만 보안 사고 보고서를 읽어 보면 치명적인 문제 상당수가 대단한 암호학 실패가 아니라 경계 혼동에서 시작됩니다. 인증은 통과했는데 권한 검사를 잊은 엔드포인트가 열려 있었거나, 토큰 검증은 했는데 만료 검증이 빠졌거나. AI가 만든 인증 코드를 검토할 때 이 경계를 아는 것이 중요합니다.

> 인증은 "신원 확인 경계", 권한은 "행동 허용 경계"입니다. 두 경계가 코드에서 분리되어 있지 않으면 보안 사고는 기능 버그 형태로 숨어 들어옵니다.

## 이 글에서 다룰 문제

- authentication과 authorization은 무엇이 다를까요?
- 비밀번호 저장에서 최소한으로 지켜야 할 안전 기준은 무엇일까요?
- session과 JWT는 각각 언제 더 자연스러울까요?
- AI가 만든 인증 코드에서 어떤 취약점을 먼저 확인해야 할까요?
- 바이브코딩에서 보안을 AI에게 맡길 때 주의할 점은 무엇일까요?

## 바이브코딩과 보안: AI가 자주 놓치는 것

AI는 동작하는 인증 코드를 빠르게 만들지만, 보안 세부사항을 놓치는 경우가 있습니다. 가장 흔한 문제:

- 비밀번호를 SHA-256으로 해시 (bcrypt가 아닌 빠른 해시 사용)
- JWT 알고리즘 검증 없이 토큰 파싱
- 인증(401)과 권한(403)을 구분하지 않고 모두 401로 반환
- 새 엔드포인트 추가 시 권한 검사 누락
- 로그인 시도 횟수 제한 없음

## 인증과 권한을 분리해야 하는 이유

| 구분 | 질문 | 실패 시 응답 | 주 책임 컴포넌트 |
| --- | --- | --- | --- |
| Authentication (AuthN) | "당신은 누구입니까?" | `401 Unauthorized` | 로그인, 토큰 검증, 세션 확인 |
| Authorization (AuthZ) | "그 행동을 할 수 있습니까?" | `403 Forbidden` | 역할/권한 매핑, 정책 엔진, 리소스 소유권 검사 |

AuthN이 실패하면 사용자 식별 자체가 안 된 상태이고, AuthZ가 실패하면 식별은 되었지만 행동이 거부된 상태입니다. 이 차이를 API 설계와 로그에 명확히 반영해야 합니다.

## 비밀번호 저장: bcrypt를 사용해야 하는 이유

AI가 SHA-256으로 비밀번호를 해시하는 코드를 만들면 수정이 필요합니다. MD5, SHA-1, SHA-256은 너무 빠릅니다. 공격자가 GPU로 초당 수십억 번 해시를 시도할 수 있습니다.

비밀번호 저장에는 bcrypt 또는 argon2id를 사용해야 합니다:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

로그인 엔드포인트에서 100~300ms 지연은 느린 것이 아닙니다. 의도된 방어막입니다.

## JWT: 필수 검증 항목

AI가 만든 JWT 코드에서 확인해야 할 필수 항목:

```python
from datetime import UTC, datetime, timedelta
import jwt

SECRET_KEY = "replace-with-env-secret"
ALGORITHM = "HS256"

def create_access_token(subject: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "iss": "my-app",
        "aud": "my-api",
        "iat": now,
        "exp": now + timedelta(minutes=15),  # 짧은 만료 시간
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],      # 허용 알고리즘 명시 (alg:none 공격 차단)
        issuer="my-app",             # issuer 검증
        audience="my-api",           # audience 검증
    )
```

| 검증 항목 | 이유 |
| --- | --- |
| 서명 알고리즘 고정(`alg` allowlist) | `alg:none` 혼동 공격 차단 |
| `exp` 검증 | 만료 토큰 차단 |
| `iss`/`aud` 검증 | 다른 시스템 토큰 오용 차단 |

## FastAPI에서 AuthN/AuthZ 경계 코드로 고정하기

```python
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  # 인증 실패: 401
            detail="유효하지 않은 인증 토큰입니다.",
        )
    user = fake_get_user_from_db(payload.get("sub"))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user

def require_permission(permission: str):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if permission not in set(user.get("permissions", [])):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,  # 권한 부족: 403
                detail="요청한 작업 권한이 없습니다.",
            )
        return user
    return checker

@app.get("/profile")
def profile(user: dict = Depends(get_current_user)):
    return {"id": user["id"], "email": user["email"]}

@app.delete("/admin/users/{user_id}")
def delete_user(user_id: int, _: dict = Depends(require_permission("users:delete"))):
    return {"deleted_user_id": user_id}
```

인증 실패는 항상 401, 권한 실패는 항상 403입니다.

## Before/After: 보안 문제 수정

### Before: AI가 자주 만드는 취약한 패턴

```python
import hashlib

def hash_password(password: str) -> str:
    # SHA-256은 비밀번호 해시에 부적합
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/login")
def login(email: str, password: str):
    user = get_user(email)
    if user.password_hash == hash_password(password):  # 문자열 비교 취약
        token = jwt.encode({"sub": email}, "hardcoded-secret")  # 하드코딩된 시크릿
        return {"token": token}
    return {"error": "wrong password"}  # 인증 실패인데 200 응답
```

### After: 올바른 보안 패턴

```python
@app.post("/login")
def login(credentials: LoginRequest):
    user = get_user(credentials.email)
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )
    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}
```

## AI가 만든 인증 코드에서 자주 하는 실수

| 실수 | 왜 위험한가 | AI에게 수정 요청 방법 |
| --- | --- | --- |
| MD5/SHA-256으로 비밀번호 해시 | 공격자 비용이 낮음 | "비밀번호는 bcrypt 또는 argon2id로 해시해줘" |
| JWT `alg` 검증 없음 | alg:none 공격에 취약 | "JWT 디코딩 시 허용 알고리즘을 명시해줘" |
| 인증 실패를 200으로 반환 | 모니터링에서 감지 불가 | "인증 실패는 401, 권한 부족은 403을 사용해줘" |
| 권한 검사 누락 | 새 API가 열린 채로 배포 | "모든 민감 엔드포인트에 require_permission을 추가해줘" |
| 시크릿 키 하드코딩 | 코드 저장소에서 유출 | "JWT 시크릿은 환경 변수에서 읽도록 수정해줘" |

## AI 팁: 인증/권한을 AI에게 요청하는 방법

**보안 기본 설정**: "비밀번호는 bcrypt로 해시하고, JWT는 HS256으로 서명하며 만료 시간은 15분으로 설정해줘."

**경계 분리**: "인증(토큰 검증)과 권한(권한 확인)을 별도 Depends 함수로 분리해줘."

**환경 변수**: "JWT 시크릿 키와 알고리즘은 환경 변수에서 읽도록 pydantic-settings를 사용해줘."

**레이트리밋**: "로그인 엔드포인트에 IP 기준 레이트리밋을 추가해줘."

## 체크리스트

- [ ] authentication과 authorization의 차이를 설명할 수 있습니다.
- [ ] 비밀번호 해시에 bcrypt를 사용해야 하는 이유를 말할 수 있습니다.
- [ ] JWT 검증 시 필수 항목(alg, exp, iss, aud)을 확인할 수 있습니다.
- [ ] AI가 만든 인증 코드에서 SHA-256 해시와 하드코딩된 시크릿을 발견할 수 있습니다.
- [ ] 인증 실패(401)와 권한 부족(403)을 구분할 수 있습니다.

## 처음 질문으로 돌아가기

- **authentication과 authorization은 무엇이 다를까요?**
  - authentication은 "당신이 누구인가"를 확인(401), authorization은 "그 행동을 할 수 있는가"를 확인(403)합니다. 코드에서 분리되지 않으면 보안 사고가 기능 버그처럼 나타납니다.
- **비밀번호 저장에서 최소한으로 지켜야 할 안전 기준은 무엇일까요?**
  - bcrypt 또는 argon2id를 사용해야 합니다. SHA-256은 너무 빨라서 공격자가 대입 공격을 저렴하게 할 수 있습니다. 로그인 응답 100~300ms는 의도된 방어막입니다.
- **session과 JWT는 각각 언제 더 자연스러울까요?**
  - 전통적 웹앱에서는 httpOnly 쿠키 세션이 단순하고 강력합니다. 다중 서비스 API + 모바일 조합에서는 짧은 만료 JWT + 회전형 리프레시 전략이 운영적으로 유리합니다.

## 정리

보안은 AI에게 완전히 맡기기 가장 어려운 영역입니다. 동작하는 코드와 안전한 코드는 다릅니다. AI에게 인증 기능을 요청할 때 "bcrypt 사용", "JWT alg 검증", "401/403 구분", "시크릿 환경 변수"를 명시하면 훨씬 안전한 코드를 얻을 수 있습니다. 생성된 코드는 반드시 보안 항목을 직접 검토하는 습관이 필요합니다.

## 참고 자료

### 공식 문서

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Passlib bcrypt docs](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)
- [JWT Introduction](https://jwt.io/introduction)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 백엔드 개발 기초 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [바이브코딩을 위한 백엔드 개발 기초 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- [바이브코딩을 위한 백엔드 개발 기초 (3/10): Routing과 Controller](./03-routing-and-controllers.md)
- [바이브코딩을 위한 백엔드 개발 기초 (4/10): Service Layer](./04-service-layer.md)
- [바이브코딩을 위한 백엔드 개발 기초 (5/10): Database Layer](./05-database-layer.md)
- **바이브코딩을 위한 백엔드 개발 기초 (6/10): 인증과 권한 (현재 글)**
- [바이브코딩을 위한 백엔드 개발 기초 (7/10): Logging과 Error Handling](./07-logging-and-error-handling.md)
- [바이브코딩을 위한 백엔드 개발 기초 (8/10): 백엔드 테스트](./08-testing-the-backend.md)
- [바이브코딩을 위한 백엔드 개발 기초 (9/10): 백엔드 배포](./09-deploying-the-backend.md)
- [바이브코딩을 위한 백엔드 개발 기초 (10/10): 운영 가능한 백엔드 구조](./10-production-ready-backend.md)

<!-- toc:end -->

Tags: 바이브코딩, Backend, Auth, Security, JWT, Python
