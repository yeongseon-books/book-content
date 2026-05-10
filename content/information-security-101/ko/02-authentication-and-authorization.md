---
series: information-security-101
episode: 2
title: 인증과 인가
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - Security
  - Authentication
  - Authorization
  - OAuth
  - RBAC
seo_description: 인증과 인가의 차이, password와 MFA, 세션과 토큰, OAuth와 RBAC까지 한 화면에 정리합니다.
last_reviewed: '2026-05-04'
---

# 인증과 인가

> Information Security 101 시리즈 (2/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: "당신이 누구인가"와 "당신이 무엇을 해도 되는가"는 같은 질문일까요?

> 인증(authentication)은 신원의 문제, 인가(authorization)는 권한의 문제입니다. 둘을 섞으면 보안의 절반이 무너집니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 인증과 인가의 정의와 차이
- password, MFA, 생체 인증의 보안 모델
- 세션 vs 토큰 (JWT 포함)
- OAuth 2.0 / OIDC 흐름의 골격
- RBAC, ABAC의 비교와 선택 기준

## 왜 중요한가

대부분의 침해 사고는 자격 증명 탈취 또는 권한 오용에서 시작합니다. 인증과 인가의 분리, 그리고 각각의 적절한 패턴을 이해하면 사고의 큰 문 두 개를 닫을 수 있습니다.

> "누구"를 확인하는 것과 "무엇을"을 결정하는 것은 다른 책임입니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    U["user"] -->|credential| AuthN["authentication"]
    AuthN -->|identity| AuthZ["authorization"]
    AuthZ -->|allow/deny| R["resource"]
```

먼저 신원을 확인하고, 그 신원에 대해 권한을 확인합니다. 두 단계는 시간적으로도 코드적으로도 분리됩니다.

## 핵심 용어 정리

- **Authentication**: 사용자가 주장하는 신원이 맞는지 확인.
- **Authorization**: 그 신원이 자원에 접근할 권한이 있는지 결정.
- **MFA**: knowledge / possession / inherence 중 둘 이상.
- **Session vs Token**: 서버가 상태를 가지냐, 토큰 자체가 자기-증명이냐.
- **RBAC / ABAC**: 역할 기반 / 속성 기반 인가 모델.

## Before/After

**Before — password만으로 끝**

```text
한 번 유출되면 영구 침투
```

**After — password + MFA + 토큰 만료 + RBAC**

```text
다단계, 시간 제한, 권한 분리 -> 한 약점이 전체를 깨지 않음
```

방어는 한 겹이 아니라 여러 겹입니다.

## 실습: 인증과 인가 짧은 코드

### 1단계 — 안전한 password 저장

```python
# 1_password.py
import bcrypt
def hash_pw(pw): return bcrypt.hashpw(pw.encode(), bcrypt.gensalt(12))
def check_pw(pw, h): return bcrypt.checkpw(pw.encode(), h)
```

bcrypt/argon2/scrypt — 의도적으로 느린 해시. SHA-256은 password용이 아닙니다.

### 2단계 — TOTP MFA

```python
# 2_totp.py
import pyotp
totp = pyotp.TOTP("JBSWY3DPEHPK3PXP")
print(totp.now())                   # 6자리 숫자
print(totp.verify("123456"))        # bool
```

possession 요소(휴대폰의 시드)를 추가해 한 단계가 깨져도 안전합니다.

### 3단계 — 세션 vs JWT

```python
# 3_session_vs_jwt.py
# session: 서버가 sid -> user를 저장 (revoke 쉬움, 상태 필요)
# jwt:    토큰에 user/exp/sig (revoke 어려움, 상태 없음)
import jwt
t = jwt.encode({"sub": "u1", "exp": 9999999999}, "secret", algorithm="HS256")
print(jwt.decode(t, "secret", algorithms=["HS256"]))
```

revoke가 자주 필요하면 세션, 마이크로서비스 간 stateless 호출이면 JWT.

### 4단계 — OAuth 2.0 authorization code (의사코드)

```text
4_oauth.txt
client -> auth server: GET /authorize?response_type=code
user logs in & consents
auth server -> client: redirect with ?code=...
client -> auth server: POST /token (code + secret) -> access_token
client -> resource server: GET /api with Bearer access_token
```

password를 third-party에 절대 주지 않는 것이 OAuth의 본질입니다.

### 5단계 — RBAC 결정

```python
# 5_rbac.py
ROLE_PERMS = {"admin": {"read","write","delete"}, "user": {"read"}}
def can(role, action): return action in ROLE_PERMS.get(role, set())
print(can("user", "delete"))   # False
```

역할에 권한 집합을 묶는 가장 단순한 인가. 작은 시스템엔 이걸로 충분합니다.

## 이 코드에서 주목할 점

- password는 빠른 해시로 저장하지 않습니다 — 의도적으로 느리게.
- MFA는 "한 요소가 깨져도"의 약속입니다.
- JWT는 sign 키 관리가 본질, secret 노출은 모든 토큰을 위조 가능하게 만듭니다.
- OAuth의 access_token은 짧게, refresh_token은 안전한 곳에.

## 자주 하는 실수 5가지

1. **MD5/SHA로 password를 해시.** GPU로 분당 수십억 회 시도 가능.
2. **JWT를 long-lived로 사용.** revoke 불가, 탈취 시 대응 불가.
3. **인가 검사를 클라이언트에 둔다.** 서버 검사 없으면 결국 무방비.
4. **role 하나에 모든 권한 묶기.** 권한 최소화 원칙 위반.
5. **로그인 실패에 자세한 메시지.** 사용자 enumeration 가능.

## 실무에서는 이렇게 쓰입니다

웹/모바일 앱 거의 모두가 OIDC(OAuth 위의 ID 표준)와 SSO를 사용합니다. 클라우드는 IAM이 RBAC + ABAC 혼합. 큰 조직은 SSO + MFA + 짧은 토큰 + 감사 로그를 표준 조합으로 둡니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 인증 라이브러리를 직접 만들지 않습니다 (auth0, Keycloak, Cognito 등).
- 인가 로직은 정책 엔진(OPA 등)으로 코드와 분리합니다.
- MFA를 기본값으로 둡니다.
- 토큰 만료 시간을 짧게 두고 refresh로 회복합니다.
- 권한 변경은 audit 로그에 반드시 남깁니다.

## 체크리스트

- [ ] 인증과 인가의 차이를 한 줄로 말할 수 있는가?
- [ ] password 해시 함수의 조건을 답할 수 있는가?
- [ ] 세션과 JWT의 트레이드오프를 설명할 수 있는가?
- [ ] OAuth authorization code 흐름을 그릴 수 있는가?
- [ ] RBAC와 ABAC를 언제 쓸지 판단할 수 있는가?

## 연습 문제

1. 본인 서비스의 인증 흐름을 세션/토큰 관점에서 그려 보세요.
2. password 정책(길이, 복잡도, lockout)을 한 페이지로 적어 보세요.
3. 가장 위험한 권한 한 가지를 골라 RBAC 매트릭스를 만들어 보세요.

## 정리 및 다음 단계

인증과 인가는 보안의 가장 큰 문 두 개입니다. 다음 글에서는 데이터 보호의 기본기 — 암호화와 해시 — 를 다룹니다.

<!-- toc:begin -->
- [정보보안이란 무엇인가?](./01-what-is-information-security.md)
- **인증과 인가 (현재 글)**
- 암호화와 해시 (예정)
- TLS와 인증서 (예정)
- Web 보안 기초 (예정)
- SQL Injection과 XSS (예정)
- secret 관리 (예정)
- 권한 최소화 (예정)
- 로그와 감사 (예정)
- 보안 사고 대응 (예정)
<!-- toc:end -->

## 참고 자료

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OAuth 2.0 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)
- [NIST SP 800-63B Digital Identity](https://pages.nist.gov/800-63-3/sp800-63b.html)

Tags: Computer Science, Security, Authentication, Authorization, OAuth, RBAC
