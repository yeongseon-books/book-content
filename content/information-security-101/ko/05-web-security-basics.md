---
title: "Information Security 101 (5/10): 웹 보안 기초"
series: information-security-101
episode: 5
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
  - WebSecurity
  - CORS
  - CSP
  - SameOrigin
last_reviewed: '2026-05-12'
seo_description: 동일 출처 정책, CORS, CSP, 쿠키 플래그를 웹 보안 관점에서 정리합니다.
---

# Information Security 101 (5/10): 웹 보안 기초

웹 보안을 처음 공부할 때는 CORS, CSP, 쿠키, CSRF, XSS가 서로 다른 주제처럼 보입니다. 하지만 브라우저 관점에서 보면 대부분은 같은 질문으로 모입니다. “이 요청과 이 스크립트는 어느 출처에서 왔는가?” 출처 개념이 머릿속에 잡히면 그 뒤의 규칙들이 한 줄로 이어집니다.

이 글은 Information Security 101 시리즈의 5번째 글입니다.


![Information Security 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/information-security-101/05/05-01-big-picture.ko.png)
*Information Security 101 5장 흐름 개요*
> 웹 보안의 기초는 HTTPS만으로는 부족합니다. 입력 검증, 세션 토큰, 쿠키 설정(HttpOnly/Secure/SameSite), 에러 메시지가 정보를 새지 않게 하는 것이 얼마나 일관되는지가 전부입니다.

## 먼저 던지는 질문

- 동일 출처 정책은 정확히 무엇을 뜻할까요?
- CORS는 무엇을 허용하고 무엇을 허용하지 않을까요?
- CSP는 왜 XSS 피해를 줄이는 데 중요할까요?

## 왜 중요한가

웹 보안의 큰 줄기는 몇 가지 개념이 반복되는 구조입니다. 출처와 쿠키를 이해하면 CSRF와 XSS 노출의 상당 부분을 줄일 수 있습니다. 반대로 CORS를 “보안 기능”으로 오해하거나, SameSite를 제대로 이해하지 못하거나, CSP를 형식적으로만 추가하면 브라우저가 주는 기본 보호를 오히려 약하게 만드는 일이 생깁니다.

브라우저 보안은 복잡한 마법이 아니라 기본 경계와 예외 규칙의 조합입니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    A["app.example.com"] -->|"Same-Origin OK"| A
    A -->|"Cross-Origin"| B["api.other.com"]
    B -->|"CORS header allows"| A
```

같은 출처 요청은 기본적으로 허용됩니다. 다른 출처 요청은 서버가 명시적으로 허용해야 합니다.

## 핵심 용어

- 출처: 스킴, 호스트, 포트의 조합입니다.
- **CORS**: 다른 출처 요청을 서버가 허용하는 방식입니다.
- **CSP**: 어떤 출처의 리소스를 불러올 수 있는지 제한하는 헤더입니다.
- **CSRF**: 로그인된 사용자의 세션을 악용해 위조 요청을 보내는 공격입니다.
- **SameSite 쿠키**: 교차 사이트 요청에 쿠키를 붙일지 제한하는 정책입니다.

## 전후 비교

### 이전 — 교차 사이트 요청에도 쿠키가 모두 전송

```text
Malicious site triggers a request with the victim's session cookie -> CSRF
```

### 이후 — SameSite=Lax 기본값 사용

```text
Cross-site POST omits the cookie -> CSRF blocked
```

브라우저 기본값이 강해졌다고 해도, 운영자가 정책을 정확히 이해하고 맞춰야 효과가 납니다.

## 단계별 실습

### 1단계 — Flask에서 CORS를 설정합니다

```python
# 1_cors.py
from flask import Flask, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://app.example.com"}})

@app.get("/api/me")
def me(): return jsonify(user="alice")
```

자격 증명이 포함되는 요청에 와일드카드 `*`를 쓰는 것은 허용되지 않습니다. 허용할 출처를 구체적으로 적어야 합니다.

### 2단계 — CSP 헤더를 추가합니다

```python
# 2_csp.py
@app.after_request
def csp(resp):
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; img-src 'self' data:"
    )
    return resp
```

`unsafe-inline`를 피하는 것만으로도 XSS 피해 범위를 크게 줄일 수 있습니다.

### 3단계 — 안전한 쿠키를 설정합니다

```python
# 3_cookie.py
@app.get("/login")
def login():
    resp = app.make_response("ok")
    resp.set_cookie("sid", "xyz", secure=True, httponly=True, samesite="Lax")
    return resp
```

Secure, HttpOnly, SameSite는 따로 놀지 않습니다. 세 플래그를 한 세트로 보는 습관이 중요합니다.

### 4단계 — CSRF 토큰을 검사합니다

```python
# 4_csrf.py
def verify_csrf(req):
    if req.method in ("POST", "PUT", "DELETE"):
        if req.headers.get("X-CSRF") != session["csrf"]:
            raise PermissionError
```

double-submit 패턴이든 synchronizer 패턴이든 하나를 분명히 골라 끝까지 일관되게 적용해야 합니다.

### 5단계 — 자동 이스케이프로 XSS를 막습니다

```python
# 5_xss.py
from markupsafe import escape
def render(name):
    return f"<h1>Hello {escape(name)}</h1>"
```

템플릿 엔진의 자동 이스케이프를 신뢰하되, HTML, 자바스크립트, URL처럼 출력 문맥이 다르면 그 문맥에 맞게 인코딩해야 합니다.

## 이 코드와 예제에서 먼저 볼 점

- CORS는 보호 장치가 아니라 허용 목록입니다. 인증과 함께 가야 합니다.
- CSP는 Report-Only에서 시작해 Enforce로 옮기는 점진적 적용이 좋습니다.
- 쿠키 플래그는 세트로 관리해야 합니다.
- CSRF 방어는 토큰이든 SameSite든 반쯤이 아니라 끝까지 일관돼야 합니다.

## 자주 하는 실수 다섯 가지

1. **자격 증명이 있는 요청에 CORS `*`를 쓰는 실수**: 명세상 허용되지 않습니다.
2. **CSP에 `unsafe-inline`를 남겨 두는 실수**: 보호 효과가 크게 떨어집니다.
3. **쿠키에 Secure나 HttpOnly가 없는 실수**: XSS가 세션 탈취로 이어지기 쉽습니다.
4. **상태 변경을 GET으로 처리하는 실수**: 캐시, 링크, CSRF에 취약해집니다.
5. **출처 헤더 없이 리퍼러만 믿는 실수**: 환경에 따라 쉽게 흔들릴 수 있습니다.

## 실무에서는 이렇게 나타납니다

CSP는 nonce나 hash 기반으로 점진적으로 도입합니다. 인증된 API는 CORS 허용 목록, SameSite=Strict 또는 Lax 쿠키, CSRF 토큰을 함께 씁니다. CloudFront Functions 같은 에지 계층에서 보안 헤더를 중앙 관리하는 패턴도 흔합니다. 핵심은 정책을 서비스마다 따로 만들지 않고 한곳에서 일관되게 유지하는 데 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 보안 헤더는 미들웨어나 에지 계층 한곳에서 관리합니다.
- CSP는 Report-Only로 데이터를 모은 뒤 Enforce로 전환합니다.
- 쿠키 정책 변경에는 배포 계획과 모니터링이 함께 따라갑니다.
- CSRF와 XSS 방어는 하나의 기준 문서로 묶어 둡니다.
- 출처 정책은 변경 이력까지 문서화합니다.

## 체크리스트

- [ ] 동일 출처의 정의를 정확히 말할 수 있습니까?
- [ ] CORS 허용 목록의 소유자가 분명합니까?
- [ ] CSP가 실제로 적용되고 있습니까?
- [ ] 세션 쿠키에 세 가지 플래그가 모두 붙어 있습니까?
- [ ] CSRF 방어 방식이 문서화되어 있습니까?

## 연습 문제

1. `https://app.example.com`과 `https://app.example.com:8443`은 같은 출처인지 설명해 보세요.
2. `default-src 'self'`만으로 막지 못하는 공격 하나를 적어 보세요.
3. SameSite=Strict를 사용할 때 생길 수 있는 사용자 경험 영향 두 가지를 적어 보세요.

## 정리와 다음 글

웹 보안의 큰 축은 출처와 쿠키입니다. 브라우저가 어디를 경계로 삼는지 이해하면 CORS, CSP, CSRF 방어가 한 흐름으로 정리됩니다. 다음 글에서는 코드 수준에서 가장 유명한 두 취약점인 SQL 인젝션과 XSS를 다룹니다.


## 브라우저 경계에서 TLS와 세션을 함께 보기

웹 보안은 CORS/CSP 같은 브라우저 정책과 TLS 같은 전송 계층 보안이 함께 작동할 때 완성됩니다. HTTPS가 없으면 쿠키 `Secure` 플래그도 의미가 사라지고, HSTS도 적용할 수 없습니다. 즉, 웹 보안의 출발선은 "모든 트래픽 TLS"입니다.

| 계층 | 핵심 통제 | 대표 실패 | 즉시 점검 |
| --- | --- | --- | --- |
| 전송 계층 | TLS 1.2+ / HSTS | 중간자 공격, 쿠키 노출 | 리다이렉트/헤더 확인 |
| 브라우저 정책 | SOP/CORS/CSP | 교차 출처 오남용, XSS 확장 | 허용 목록 최소화 |
| 세션 계층 | HttpOnly/Secure/SameSite | CSRF/세션 탈취 | 쿠키 플래그 점검 |

## 보안 헤더 기준선

실무에서 빠르게 효과를 내는 방법은 보안 헤더 기준선을 공통 미들웨어로 강제하는 것입니다.

```python
# security_headers.py
from flask import Flask

app = Flask(__name__)

@app.after_request
def add_security_headers(resp):
    resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    resp.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none'"
    return resp
```

헤더를 기능별 코드에 흩뿌리면 누락이 생깁니다. 공통 계층에서 중앙 관리하고, 회귀 테스트로 누락을 탐지해야 합니다.

## CORS 정책 설계 원칙

| 질문 | 잘못된 접근 | 권장 접근 |
| --- | --- | --- |
| 어떤 출처를 허용할 것인가 | `*` 허용 | 명시적 허용 목록 |
| 자격 증명 쿠키를 보낼 것인가 | 무조건 허용 | 필요한 API만 제한 허용 |
| preflight 실패 대응 | 임시 우회 | 원인별 정책 정리 |
| 운영/스테이징 분리 | 동일 정책 사용 | 환경별 출처 분리 |

CORS는 공격을 막는 도구가 아니라 브라우저가 요청을 허용할지 결정하는 계약입니다. 따라서 서버 인가 검사를 대체하지 못합니다.

## 인증서 체인 문제와 웹 장애의 연결

웹 팀에서 자주 놓치는 포인트는 인증서 장애가 곧 애플리케이션 장애로 보인다는 사실입니다.

- 인증서 만료: 사용자 입장에서는 "사이트가 갑자기 안 열린다"로 보입니다.
- 중간 인증서 누락: 특정 브라우저/OS 조합에서만 실패해 원인 파악이 늦어집니다.
- 도메인/SAN 불일치: 신규 서브도메인 배포 때 자주 발생합니다.

따라서 웹 보안 체크리스트에는 CORS/CSP뿐 아니라 인증서 만료 모니터링, 자동 갱신 검증, 체인 점검이 반드시 함께 있어야 합니다.


## 운영 점검 루프와 문서화 기준

보안 글에서 가장 자주 빠지는 부분은 "그래서 운영에서는 무엇을 주기적으로 확인할 것인가"입니다. 아래 루프를 기준으로 문서화하면 개념이 실무로 연결됩니다.

| 주기 | 점검 항목 | 산출물 |
| --- | --- | --- |
| 매일 | 고위험 경보, 인증 실패 급증, 권한 거부 급증 | 일일 보안 브리핑 |
| 매주 | 신규 배포 변경점의 보안 영향 | 변경 검토 노트 |
| 매월 | 키/토큰/인증서 만료 예정, 미사용 권한, 미사용 시크릿 | 월간 정리 리포트 |
| 분기 | 위협 모델 재평가, 런북 훈련, 통제 효과 검토 | 분기 보안 회고 |

실행 가능한 문서의 조건도 분명해야 합니다.

- 담당자(owner)와 대체 담당자가 명시되어야 합니다.
- 실패 조건과 에스컬레이션 기준이 수치로 정의되어야 합니다.
- 점검 결과가 티켓이나 액션 아이템으로 추적되어야 합니다.
- 예외 승인에는 만료일이 반드시 있어야 합니다.

보안은 단발성 프로젝트가 아니라 운영 루프입니다. 같은 점검을 반복해도 기준이 유지될 때 품질이 올라갑니다.


## 서브리소스 무결성 검증(SRI)


외부 CDN에서 스크립트나 스타일시트를 불러올 때, CDN이 침해되면 악성 코드가 삽입될 수 있습니다. SRI는 브라우저가 다운로드된 리소스의 해시를 검증해 변조된 파일을 차단합니다.


```html

<!-- SRI 적용 예시 -->

<script src="https://cdn.example.com/lib.js"

  integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxAh...="

  crossorigin="anonymous"></script>

```


SRI를 적용하면 CDN 공급망 공격으로부터 클라이언트를 보호할 수 있습니다. 다만 리소스 업데이트 시 해시값도 함께 갱신해야 하므로 배포 파이프라인에 포함시키는 것이 좋습니다.


## CSP 위반 리포팅 설정


CSP를 처음 도입할 때는 Enforce 대신 Report-Only로 시작해야 서비스 장애를 피할 수 있습니다. 리포팅 엔드포인트를 마련하고 수집된 위반 데이터를 분석한 뒤 정책을 좀혀 나갑니다.


```python

# csp_report_endpoint.py

from flask import Flask, request, jsonify

import json


app = Flask(__name__)


@app.post("/csp-report")

def csp_report():

    report = request.get_json(force=True)

    # 위반 내역을 구조화된 로그로 저장

    print(json.dumps(report, indent=2))

    return jsonify(status="received"), 204

```


수집된 리포트에서 빈도가 높은 위반을 정리한 뒤, 허용 목록을 조정하거나 정말로 차단해야 하는 스크립트를 확인할 수 있습니다. 이 반복 루프가 CSP 도입의 핵심입니다.


## OWASP Top 10 관점에서 보는 웹 기본 통제

웹 보안 기본 항목을 OWASP Top 10에 매핑하면 우선순위를 설명하기 쉬워집니다.

| 통제 | 대응하는 OWASP 위험 | 구현 포인트 |
| --- | --- | --- |
| 입력 검증 + 출력 인코딩 | A03 Injection | 서버 측 검증, 문맥별 인코딩 |
| CSP | A03 Injection(XSS) | `script-src` 최소화, nonce 전략 |
| SameSite/HttpOnly/Secure 쿠키 | A07 Identification and Authentication Failures | 세션 탈취 표면 축소 |
| 보안 헤더 세트(HSTS 등) | A05 Security Misconfiguration | 공통 미들웨어 강제 |

프레임워크 기본값이 있다고 해도 팀 표준이 없으면 예외 코드에서 빈틈이 생깁니다. 따라서 "기본 미들웨어 + 회귀 테스트" 조합이 필수입니다.

## 프런트엔드 렌더링 안전 규칙

- 사용자 입력을 HTML로 직접 주입하지 않습니다.
- 허용 목록 기반 마크업 정제가 필요한 경우 전용 라이브러리를 단일 경로로 사용합니다.
- 링크 렌더링 시 `javascript:` 스킴을 차단합니다.
- 보안 헤더 누락을 CI에서 실패로 처리합니다.


## 프런트엔드 보안 코드 리뷰 체크포인트

웹 보안 이슈는 백엔드보다 프런트엔드 변경에서 조용히 유입되는 경우가 많습니다. 리뷰 체크포인트를 고정하면 누락을 줄일 수 있습니다.

| 점검 항목 | 위험 신호 | 권장 수정 |
| --- | --- | --- |
| `innerHTML` 사용 | 사용자 입력 직접 삽입 | 텍스트 노드/안전 렌더링 사용 |
| 외부 스크립트 로드 | 출처 검증 없음 | CSP 허용 목록 + SRI 적용 |
| 쿠키 설정 | `Secure`/`HttpOnly` 누락 | 세 플래그 기본값 강제 |
| CORS 설정 | `*`와 자격증명 동시 허용 시도 | 명시적 출처 제한 |

## OWASP 시나리오 기반 테스트 예시

1. 댓글 입력에 스크립트 삽입 시도 후 실행 여부 확인.
2. 로그인 상태에서 외부 사이트 POST 요청으로 CSRF 방어 확인.
3. 개발 도구로 헤더를 점검해 CSP/HSTS 적용 여부 확인.
4. SameSite 정책 변경 시 결제/리다이렉트 흐름 회귀 테스트.

보안 테스트는 별도 팀 전용 작업이 아니라 프런트엔드 QA 시나리오에 포함되어야 지속됩니다.


## 브라우저 정책 회귀 테스트 설계

| 테스트 | 목적 | 실패 시 의미 |
| --- | --- | --- |
| CSP 위반 리포트 검사 | 예상 외 스크립트 실행 차단 검증 | 신규 스크립트 경로 누락 |
| CORS preflight 검사 | 교차 출처 허용 범위 검증 | 과도한 허용 또는 기능 장애 |
| SameSite 쿠키 시나리오 | CSRF 방어와 사용자 흐름 균형 확인 | 결제/로그인 흐름 중단 가능 |
| 보안 헤더 스냅샷 | 배포 중 헤더 누락 탐지 | 미들웨어 회귀 가능성 |

테스트는 정적 점검만으로 부족합니다. 실제 브라우저 동작을 재현하는 E2E 시나리오를 함께 두어야 정책 변경의 영향이 보입니다.

## CSRF 방어 전략 비교

| 전략 | 장점 | 단점 | 권장 조건 |
| --- | --- | --- | --- |
| Synchronizer Token | 서버 검증 강력 | 서버 상태 관리 필요 | 세션 기반 서비스 |
| Double Submit Cookie | 구현 단순 | 쿠키 설정 의존성 높음 | SPA + API 조합 |
| SameSite 중심 | 설정 용이 | 일부 흐름 예외 필요 | 저위험 트랜잭션 |

한 전략만 맹신하기보다, 서비스 특성에 맞춰 두 가지 이상을 결합하는 편이 안정적입니다.


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


## 부록: 브라우저 보안 회귀 방지 규칙

1. 보안 헤더 변경은 기능 배포와 분리해 단계적으로 적용합니다.
2. CSP 정책 변경 시 Report-Only 데이터를 최소 1주 수집한 뒤 강제 모드로 전환합니다.
3. CORS 허용 목록 변경은 API 오너와 보안 리뷰를 동시에 통과해야 합니다.
4. 쿠키 정책(`SameSite`, `Secure`, `HttpOnly`) 변경은 로그인/결제 E2E 테스트를 필수로 수행합니다.
5. XSS 관련 코드 경로(`innerHTML`, 사용자 HTML 렌더링)는 전용 코드리뷰 라벨을 사용합니다.

이 규칙을 팀 규약으로 두면 프론트엔드 변경 속도를 유지하면서도 보안 회귀를 줄일 수 있습니다.


### 프론트엔드 보안 자동 점검 파이프라인

CI/CD에서 프론트엔드 보안을 자동으로 점검하는 구성 예시입니다.

```yaml
# .github/workflows/frontend-security.yml
name: Frontend Security Check
on:
  pull_request:
    paths:
      - 'src/**/*.{js,ts,tsx}'

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Dependency audit
        run: npm audit --audit-level=moderate

      - name: Static analysis for XSS patterns
        run: |
          # innerHTML, dangerouslySetInnerHTML, eval 사용 탐지
          grep -rn 'innerHTML\|dangerouslySetInnerHTML\|eval(' src/ \
            && echo 'WARN: potential XSS sink found' \
            || echo 'PASS: no obvious XSS sink'

      - name: CSP header validation
        run: |
          curl -sI https://staging.example.com \
            | grep -i content-security-policy \
            || (echo 'FAIL: CSP header missing'; exit 1)

      - name: HTTPS redirect check
        run: |
          STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://staging.example.com)
          [ "$STATUS" = "301" ] || (echo "FAIL: HTTP not redirecting"; exit 1)
```

이 워크플로는 네 가지를 점검합니다. 첫째, 의존성 취약점이 moderate 이상인지 확인합니다. 둘째, XSS 싱크로 자주 사용되는 패턴을 정적 탐색합니다. 셋째, 스테이징 환경에 CSP 헤더가 존재하는지 검증합니다. 넷째, HTTP → HTTPS 리다이렉트가 올바르게 설정되었는지 확인합니다.

### 쿠키 속성 점검표

웹 보안에서 쿠키 설정은 세션 탈취 방어의 기초입니다. 다음 표는 주요 쿠키 속성과 권장 설정을 정리한 것입니다.

| 속성 | 권장 값 | 효과 | 미설정 시 위험 |
| --- | --- | --- | --- |
| `Secure` | 항상 설정 | HTTPS에서만 전송 | 평문 네트워크에서 쿠키 노출 |
| `HttpOnly` | 인증 쿠키 필수 | JavaScript 접근 차단 | XSS로 세션 토큰 탈취 |
| `SameSite` | `Lax` 또는 `Strict` | 교차 사이트 요청 시 쿠키 제외 | CSRF 공격 가능 |
| `Path` | 최소 경로 지정 | 해당 경로에서만 전송 | 불필요한 경로에 쿠키 노출 |
| `Max-Age` | 세션 쿠키는 생략, 영속 쿠키는 최소 | 만료 시간 제한 | 장기 세션 유지로 탈취 창 확대 |

Python Flask에서 이를 적용하는 예시입니다.

```python
from flask import Flask, make_response

app = Flask(__name__)

# 앱 전역 쿠키 보안 설정
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)


@app.after_request
def set_security_headers(response):
    # CSP 헤더
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "frame-ancestors 'none'"
    )
    # 추가 보안 헤더
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```

이 설정은 세 가지 방어층을 동시에 구현합니다. 쿠키 속성으로 세션 보호, CSP 헤더로 스크립트 실행 범위 제한, 추가 헤더로 MIME 스니핑과 클릭재킹을 방지합니다.

## 처음 질문으로 돌아가기

- **동일 출처 정책은 정확히 무엇을 뜻할까요?**
  - 폼 제출 → 경로 라우팅 → 쿼리 구성 → 응답 생성 → 쿠키 설정의 각 단계에서 어디서 검증이 일어나고 어디서 로그가 남는지 명확히 합니다.
- **CORS는 무엇을 허용하고 무엇을 허용하지 않을까요?**
  - GET vs POST 쿠키 전송, CORS preflight 요청의 필요성, CSP 헤더의 XSS 방어 원리를 이해하면 배포 후 혼란이 줄어듭니다.
- **CSP는 왜 XSS 피해를 줄이는 데 중요할까요?**
  - 보안 헤더(HSTS/X-Frame-Options/X-Content-Type-Options) 설정, 쿠키 속성 감사, 입력 검증 규칙 변경 시 회귀 테스트를 정의합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Information Security 101 (1/10): 정보보안이란 무엇인가?](./01-what-is-information-security.md)
- [Information Security 101 (2/10): 인증과 인가](./02-authentication-and-authorization.md)
- [Information Security 101 (3/10): 암호화와 해시](./03-cryptography-and-hash.md)
- [Information Security 101 (4/10): TLS와 인증서](./04-tls-and-certificates.md)
- **웹 보안 기초 (현재 글)**
- SQL 인젝션과 XSS (예정)
- 비밀 정보 관리 (예정)
- 권한 최소화 (예정)
- 로그와 감사 (예정)
- 보안 사고 대응 (예정)

<!-- toc:end -->

## 참고 자료

- [OWASP — Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [MDN — Same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy)
- [MDN — Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [web.dev — SameSite cookies explained](https://web.dev/articles/samesite-cookies-explained)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/information-security-101/ko)

Tags: Computer Science, Security, WebSecurity, CORS, CSP, SameOrigin
