---
series: information-security-101
episode: 5
title: "바이브코딩을 위한 정보 보안 기초 (5/10): 웹 보안 기초"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 정보보안
  - CORS
  - CSP
  - CSRF
  - AI보안
language: ko
---

# 바이브코딩을 위한 정보 보안 기초 (5/10): 웹 보안 기초

이 글은 **바이브코딩을 위한 정보 보안 기초** 시리즈의 5편입니다. AI가 만들어주는 코드에는 보안 취약점이 숨어 있을 수 있습니다. 이번에는 AI가 웹 보안 설정에서 자주 만드는 구멍을 다룹니다.

---

AI에게 "CORS 설정해줘"라고 하면 `Access-Control-Allow-Origin: *`을 추가하는 코드가 나옵니다. 빠르게 작동하게 만드는 방법이긴 합니다. 그런데 이 한 줄이 어떤 사이트에서도 API를 호출할 수 있게 열어버립니다. AI는 동작시키는 것을 목표로 하지, 보안 경계를 그리는 것을 목표로 하지 않습니다.

> "CORS는 보안 기능이 아니라 브라우저가 적용하는 정책입니다. `Access-Control-Allow-Origin: *`은 CORS를 '해결'하는 것이 아니라 CORS가 제공하는 보호를 제거하는 것입니다. AI가 만들어준 CORS 설정에 별표(`*`)가 있다면, 경계가 없는 API를 만든 것과 같습니다."

## 이 글에서 다룰 질문들

- CORS는 왜 있고, `*` 설정이 왜 위험할까요?
- 동일 출처 정책은 어떤 공격을 막아줄까요?
- CSP는 XSS 피해를 어떻게 줄여줄까요?
- 쿠키의 HttpOnly, Secure, SameSite 플래그는 무엇을 보호할까요?
- AI가 웹 보안 헤더에서 자주 빠뜨리는 것은 무엇일까요?

---

## 바이브코딩 관점: AI가 웹 보안에서 자주 만드는 취약한 패턴

### Before: AI가 생성하는 전형적인 취약한 웹 설정

```python
# Flask 예시 — AI가 자주 생성하는 취약한 패턴들
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

# 문제 1: 모든 출처 허용 — CSRF 방어 무력화
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response

# 문제 2: 보안 헤더 없음
@app.route("/api/user")
def get_user():
    # Content-Security-Policy 없음 → XSS 스크립트 실행 가능
    # X-Content-Type-Options 없음 → MIME 스니핑 허용
    return jsonify({"user": "admin", "secret": "token123"})

# 문제 3: 쿠키에 보안 플래그 없음
@app.route("/login", methods=["POST"])
def login():
    response = make_response(jsonify({"status": "ok"}))
    response.set_cookie("session", "abc123")  # HttpOnly, Secure, SameSite 없음
    return response
```

### After: 올바른 웹 보안 설정

```python
from flask import Flask, request, jsonify, make_response
import os

app = Flask(__name__)
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "https://app.example.com").split(",")

@app.after_request
def add_security_headers(response):
    origin = request.headers.get("Origin")
    # 허용된 출처만 명시적으로 허용
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"

    # 보안 헤더 추가
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

@app.route("/login", methods=["POST"])
def login():
    response = make_response(jsonify({"status": "ok"}))
    response.set_cookie(
        "session", "abc123",
        httponly=True,    # JavaScript에서 접근 불가 — XSS로 탈취 방지
        secure=True,      # HTTPS에서만 전송
        samesite="Strict" # 크로스사이트 요청에서 전송 안 됨 — CSRF 방지
    )
    return response
```

---

## 웹 보안 헤더 필수 목록

AI가 생성한 웹 서버 코드에 아래 헤더들이 없으면 추가 요청을 해야 합니다.

| 헤더 | 목적 | AI 생성 코드에서 자주 놓치는 이유 |
| --- | --- | --- |
| `Content-Security-Policy` | XSS 스크립트 실행 차단 | 설정이 복잡해서 생략 |
| `Strict-Transport-Security` | HTTPS 강제 | AI가 HTTP 허용 코드를 그대로 생성 |
| `X-Content-Type-Options: nosniff` | MIME 스니핑 방지 | 잘 알려지지 않은 헤더 |
| `X-Frame-Options: DENY` | 클릭재킹 방지 | 자주 빠짐 |
| `Access-Control-Allow-Origin` | CORS 출처 제한 | `*`로 설정되어 오히려 위험 |

---

## 쿠키 플래그: 세 개 모두 필요합니다

```python
# 각 플래그가 무엇을 막는지
response.set_cookie(
    "session_id", session_token,

    # HttpOnly: JavaScript에서 document.cookie로 읽기 불가
    # → XSS 공격으로 쿠키를 탈취하는 것을 막는다
    httponly=True,

    # Secure: HTTPS 연결에서만 쿠키 전송
    # → HTTP로 폼 요청 시 쿠키가 평문으로 전송되는 것을 막는다
    secure=True,

    # SameSite=Strict: 다른 사이트에서 시작된 요청에 쿠키 미포함
    # → CSRF 공격 방어: 악성 사이트가 사용자의 쿠키로 API 호출 불가
    samesite="Strict",
)
```

---

## CSP: XSS 피해를 줄이는 마지막 방어선

```python
# AI가 생성한 코드에 XSS 취약점이 있더라도
# CSP가 스크립트 실행을 차단해 피해를 줄일 수 있다

# 가장 기본적인 CSP
csp_basic = "default-src 'self'"
# → 같은 출처의 리소스만 허용, 인라인 스크립트 차단

# 실용적인 CSP (nonce 기반)
import secrets
nonce = secrets.token_urlsafe(16)
csp_with_nonce = f"script-src 'self' 'nonce-{nonce}'"
# → nonce가 있는 스크립트 태그만 실행 허용
# <script nonce="{nonce}">...합법적인 스크립트...</script>
# 공격자가 주입한 스크립트는 nonce가 없어서 실행 안 됨

# 주의: 'unsafe-inline'은 CSP를 사실상 무력화
csp_wrong = "script-src 'self' 'unsafe-inline'"  # AI가 자주 생성하는 잘못된 패턴
```

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
| --- | --- | --- |
| CORS에 `*` 설정 | 모든 출처에서 API 호출 가능 | 허용할 출처 목록을 명시적으로 설정 |
| 쿠키에 보안 플래그 없음 | XSS로 세션 탈취, CSRF 공격 가능 | HttpOnly + Secure + SameSite 세 개 모두 설정 |
| CSP에 `unsafe-inline` | 인라인 스크립트 실행 허용 → XSS 방어 무력화 | nonce 기반 CSP 사용 |
| 보안 헤더 미설정 | 클릭재킹, MIME 스니핑 등 브라우저 공격 가능 | 배포 시 보안 헤더 체크리스트 적용 |

---

## AI 팁: AI에게 웹 보안 설정을 올바르게 요청하는 법

1. **CORS 출처 확인**: "CORS 설정에서 `*` 대신 허용할 출처를 명시적으로 설정해주세요"
2. **보안 헤더 요청**: "응답에 CSP, HSTS, X-Frame-Options, X-Content-Type-Options 헤더를 추가해주세요"
3. **쿠키 플래그 확인**: "세션 쿠키에 HttpOnly, Secure, SameSite=Strict 플래그가 설정되어 있나요?"
4. **unsafe-inline 탐지**: "CSP 설정에 unsafe-inline이 포함되어 있나요? 있다면 nonce 방식으로 바꿔주세요"

---

## 실전 체크리스트

- [ ] CORS 설정에 `*` 대신 허용 출처 목록이 명시되어 있다
- [ ] 세션 쿠키에 HttpOnly, Secure, SameSite가 모두 설정되어 있다
- [ ] Content-Security-Policy 헤더가 설정되어 있다
- [ ] Strict-Transport-Security 헤더가 설정되어 있다
- [ ] X-Frame-Options: DENY가 설정되어 있다
- [ ] CSP에 `unsafe-inline`이 없다 (또는 nonce를 사용한다)

---

## 처음 질문으로 돌아가기

- **CORS는 왜 있고, `*` 설정이 왜 위험할까요?**
  CORS는 브라우저가 기본적으로 막는 크로스 출처 요청을 선택적으로 허용하는 메커니즘입니다. `*`는 모든 출처를 허용해서 이 보호를 완전히 제거합니다. 악성 사이트에서 사용자의 쿠키로 API를 호출하는 CSRF 공격이 가능해집니다.

- **CSP는 XSS 피해를 어떻게 줄여줄까요?**
  CSP는 실행 가능한 스크립트의 출처를 제한합니다. AI 코드에 XSS 취약점이 있더라도 공격자가 주입한 스크립트가 실행되지 않도록 막습니다. 완벽한 방어는 아니지만 피해 범위를 크게 줄입니다.

- **쿠키의 HttpOnly, Secure, SameSite 플래그는 무엇을 보호할까요?**
  HttpOnly는 JavaScript에서 쿠키 접근을 막아 XSS로 탈취를 방지합니다. Secure는 HTTPS에서만 전송되도록 합니다. SameSite=Strict는 다른 사이트에서 시작된 요청에 쿠키를 포함하지 않아 CSRF를 방어합니다.

---

## 정리

웹 보안은 헤더 몇 줄과 쿠키 플래그 세 개로 상당 부분 강화됩니다. AI가 만들어준 웹 서버 코드에서 CORS `*` 설정, 쿠키 보안 플래그 없음, CSP 미설정을 확인하세요. 이 세 가지만 고쳐도 흔히 발생하는 웹 보안 사고의 상당 부분을 막을 수 있습니다. 다음 글에서는 SQL 인젝션과 XSS를 바이브코딩 관점에서 다룹니다.

---

## 참고 자료

- [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [MDN CORS 가이드](https://developer.mozilla.org/ko/docs/Web/HTTP/CORS)
- [Content Security Policy 레퍼런스](https://content-security-policy.com/)
- [OWASP CSRF 방어 가이드](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 정보 보안 기초 (1/10): 정보보안이란 무엇인가?](./01-what-is-information-security.md)
- [바이브코딩을 위한 정보 보안 기초 (2/10): 인증과 인가](./02-authentication-and-authorization.md)
- [바이브코딩을 위한 정보 보안 기초 (3/10): 암호화와 해시](./03-cryptography-and-hash.md)
- [바이브코딩을 위한 정보 보안 기초 (4/10): TLS와 인증서](./04-tls-and-certificates.md)
- **바이브코딩을 위한 정보 보안 기초 (5/10): 웹 보안 기초 (현재 글)**
- 바이브코딩을 위한 정보 보안 기초 (6/10): SQL 인젝션과 XSS
- 바이브코딩을 위한 정보 보안 기초 (7/10): 비밀 정보 관리
- 바이브코딩을 위한 정보 보안 기초 (8/10): 권한 최소화
- 바이브코딩을 위한 정보 보안 기초 (9/10): 로그와 감사
- 바이브코딩을 위한 정보 보안 기초 (10/10): 보안 사고 대응
<!-- toc:end -->

Tags: 바이브코딩, 정보보안, CORS, CSP, CSRF, AI보안
