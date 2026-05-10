---
series: secure-coding-101
episode: 8
title: XSS와 CSRF 방어
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - XSS
  - CSRF
  - CSP
  - SecureCoding
  - WebSecurity
seo_description: Output escaping, CSP, SameSite cookie, CSRF token 그리고 브라우저 공격 방어 5단계
last_reviewed: '2026-05-04'
---

# XSS와 CSRF 방어

> Secure Coding 101 시리즈 (8/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 같은 사용자의 *브라우저* 가 *우리 편* 인지 *공격자의 무기* 인지를 어떻게 구분할까요?

> *XSS 는 *우리 페이지에서 공격자 코드 실행*. CSRF 는 *사용자 권한으로 의도치 않은 요청*.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *XSS* 의 세 가지 유형
- *Output escaping* 과 *CSP* 의 역할
- *CSRF* 의 원리
- *SameSite cookie* 와 *CSRF token*
- 방어 5단계와 흔한 함정 5가지

## 왜 중요한가

*XSS* 한 번이면 세션이 *탈취* 됩니다. *CSRF* 는 *사용자가 모르게* 송금/삭제를 일으킵니다.

> *기본 원칙은 *출력은 escape, 요청은 origin 확인*.*

## 개념 한눈에 보기

```mermaid
flowchart LR
    Input["사용자 입력"] --> Store["저장"]
    Store --> Render["출력 (escape!)"]
    Form["다른 사이트 폼"] -->|쿠키 자동전송| API["우리 API"]
    API --> Csrf["CSRF token / SameSite 검사"]
```

## 핵심 용어 정리

- **Reflected XSS**: URL 의 입력이 *그대로 출력*.
- **Stored XSS**: DB 에 *저장된 입력* 이 출력.
- **DOM XSS**: 클라이언트 JS 가 *innerHTML* 등으로 삽입.
- **CSP**: 브라우저가 *허용된 출처의 코드만* 실행.
- **CSRF token**: 요청에 *예측 불가 토큰* 을 묶는다.

## Before/After

**Before**: `<div>{{ comment }}</div>` 그대로 출력. `<script>` 가 *그대로 실행*.

**After**: 출력 escape, *CSP* 적용, 쿠키 *SameSite=Lax*, 변경 요청에 *CSRF token*.

## 실습: 방어 5단계

### 1단계 — Output escape

```python
import html
def render_comment(text):
    return f"<div>{html.escape(text)}</div>"
```

### 2단계 — Content Security Policy

```python
response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'"
```

### 3단계 — SameSite 쿠키

```python
response.set_cookie(
    "session", sid,
    httponly=True, secure=True, samesite="Lax",
)
```

### 4단계 — CSRF token

```python
import secrets
def issue_csrf():
    return secrets.token_urlsafe(32)

def verify_csrf(form_token, session_token):
    return secrets.compare_digest(form_token, session_token)
```

### 5단계 — 위험한 sink 금지

```javascript
// element.innerHTML = userInput;  // 금지
element.textContent = userInput;    // 안전
```

## 이 코드에서 주목할 점

- 출력 escape 는 *컨텍스트 별* 로 (HTML, JS, attribute, URL).
- CSP 는 *심층 방어* — escape 가 새도 *마지막 방어선*.
- *SameSite* 와 *CSRF token* 은 *함께* 쓴다.

## 자주 하는 실수 5가지

1. **Markdown 을 *그대로 HTML* 로 출력.** *script* 가 들어간다.
2. **`innerHTML` 으로 *사용자 입력* 삽입.** 전형적 *DOM XSS*.
3. **CSP 를 `unsafe-inline` 으로 둔다.** 의미가 *없다*.
4. **CSRF token 을 *GET* 에 의존.** 캐시에 *남는다*.
5. **API 가 *Origin/Referer* 를 안 본다.** CSRF 가 *통과*.

## 실무에서는 이렇게 쓰입니다

대부분의 팀은 템플릿 엔진의 *기본 escape* 를 켭니다. *CSP* 를 *report-only* 로 시작해 점진적으로 강화. 모든 변경 API 는 *CSRF token* 또는 *Origin* 검증.

## 시니어 엔지니어는 이렇게 생각합니다

- *기본은 *escape*, raw 는 *예외* 처리.*
- *CSP 는 *시간 들여 강화*.*
- *SameSite + CSRF token* 은 *둘 다*.*
- *DOM 에 *입력을 넣지 않는다*, textContent 만.*
- *입력 sanitization 보다 *출력 escape* 가 안전.*

## 체크리스트

- [ ] 템플릿 *기본 escape* 가 켜져 있다.
- [ ] *CSP* 가 적용.
- [ ] 쿠키가 *SameSite*.
- [ ] 변경 요청에 *CSRF 검증*.

## 연습 문제

1. *Reflected* 와 *Stored* XSS 의 코드 예시를 각각 한 줄.
2. *CSP nonce* 의 동작.
3. *SameSite=Strict* 가 깰 수 있는 흐름.

## 정리 및 다음 단계

브라우저 측 공격은 *기본기* 로 막습니다. 다음은 *우리가 안 짠 코드* — *dependency 취약점* 입니다.

<!-- toc:begin -->
- [Secure Coding이란 무엇인가?](./01-what-is-secure-coding.md)
- [입력값 검증](./02-input-validation.md)
- [인증과 세션](./03-authentication-and-session.md)
- [인가와 권한](./04-authorization-and-permissions.md)
- [안전한 데이터 저장](./05-safe-data-storage.md)
- [Secret과 키 관리](./06-secret-and-key-management.md)
- [SQL Injection과 ORM 안전 사용](./07-sql-injection-and-orm.md)
- **XSS와 CSRF 방어 (현재 글)**
- Dependency 취약점 관리 (예정)
- 안전한 로깅과 감사 (예정)
<!-- toc:end -->

## 참고 자료

- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [MDN — Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [MDN — SameSite cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
