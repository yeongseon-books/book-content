---
series: secure-coding-101
episode: 1
title: Secure Coding이란 무엇인가?
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - SecureCoding
  - Security
  - OWASP
  - DevSecOps
  - AppSec
seo_description: Secure Coding의 정의, 위협 모델, OWASP Top 10, 그리고 안전한 개발 습관의 출발점
last_reviewed: '2026-05-04'
---

# Secure Coding이란 무엇인가?

> Secure Coding 101 시리즈 (1/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 코드는 *기능이 끝났을 때 완성* 되는 것이 아니라, *공격받아도 무너지지 않을 때* 완성됩니다. 우리는 그 차이를 어떻게 만들까요?

> *Secure coding 은 *기능을 멈추게 하지 않으면서* *공격면을 줄이는* 일상의 코딩 습관입니다.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *Secure coding* 의 정의와 *왜* 필요한가
- *위협 모델* 의 개념과 첫 적용
- *OWASP Top 10* 이 다루는 영역
- 안전한 개발 흐름 5단계
- 흔한 함정 5가지

## 왜 중요한가

대부분의 보안 사고는 *알려진 패턴* 의 반복입니다. *입력 검증을 잊는다*, *secret 을 코드에 박는다*, *권한을 안 본다*. Secure coding 은 *대단한 암호학* 이 아니라 *일상의 작은 규칙* 입니다.

> *보안은 *기능 위에 얹는 코팅* 이 아니라, *처음부터 짜는 구조* 다.*

## 개념 한눈에 보기

```mermaid
flowchart LR
    User["사용자 입력"] --> Validate["검증"]
    Validate --> Logic["애플리케이션 로직"]
    Logic --> Storage["저장 (암호화)"]
    Logic --> Logs["안전한 로그"]
    Auth["인증 / 인가"] --> Logic
```

## 핵심 용어 정리

- **Threat model**: 누가, 어디서, 무엇을 노리는지에 대한 *지도*.
- **Attack surface**: 공격자가 만질 수 있는 *입력 지점들*.
- **Trust boundary**: *신뢰하는 영역* 과 *신뢰하지 않는 영역* 의 경계.
- **Defense in depth**: 여러 *얇은 방어선* 을 겹친다.
- **Least privilege**: 권한은 *필요한 만큼만*.

## Before/After

**Before**: 기능을 먼저 만들고 보안은 *나중에* 본다. 사고가 나면 *전체를 다시 짠다*.

**After**: 입력, 인증, 저장, 로그를 *처음부터 함께* 설계한다. 사고가 나도 *영향 범위가 좁다*.

## 실습: 안전한 흐름 5단계

### 1단계 — 입력의 경계를 표시한다

```python
def parse_age(raw: str) -> int:
    if not raw.isdigit():
        raise ValueError("age must be digits")
    age = int(raw)
    if not (0 < age < 150):
        raise ValueError("age out of range")
    return age
```

### 2단계 — secret 을 분리한다

```python
import os
DB_PASSWORD = os.environ["DB_PASSWORD"]  # 코드에 박지 않는다
```

### 3단계 — 권한을 함수 안에서 확인한다

```python
def delete_post(user, post):
    if post.author_id != user.id:
        raise PermissionError("not your post")
    post.delete()
```

### 4단계 — 출력에서 escape 한다

```python
import html
def render(name: str) -> str:
    return f"<p>Hello, {html.escape(name)}</p>"
```

### 5단계 — 로그에 비밀을 남기지 않는다

```python
def log_login(user):
    print({"event": "login", "user_id": user.id})  # password 금지
```

## 이 코드에서 주목할 점

- 검증은 *경계에서 한 번* 이 아니라 *경계마다* 한다.
- *Secret* 은 *환경 변수* 또는 *비밀 저장소* 에서 읽는다.
- 권한은 *route 에서 한 번, 함수에서 다시*.

## 자주 하는 실수 5가지

1. **검증을 *클라이언트만* 에서 한다.** 서버는 *항상 다시* 검증한다.
2. **Secret 을 *git 에 commit* 한다.** 한 번 새면 *영원히 샌다*.
3. **Error 메시지에 *내부 구조* 를 노출.** 공격자에게 *지도* 를 준다.
4. **권한을 *UI* 만 숨긴다.** API 는 *그대로 호출* 가능.
5. **Dependency 를 *영원히 안 올린다*.** *알려진 취약점* 이 쌓인다.

## 실무에서는 이렇게 쓰입니다

대부분의 팀은 *threat model 워크숍* 으로 시작합니다. *데이터 흐름도* 를 그리고, *trust boundary* 마다 *위협* 을 적습니다. CI 에서 *secret scan*, *dependency scan*, *SAST* 를 *기본* 으로 돌립니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *입력은 *기본적으로 적대적*.*
- *Secret 은 *코드와 분리되어야* 한다.*
- *권한은 *서버에서 결정*, UI 는 *힌트*.*
- *로그는 *증거이자 위험*.*
- *완벽한 보안은 없다, *시간을 버는* 보안만 있다.*

## 체크리스트

- [ ] *Threat model* 을 한 문단으로 쓸 수 있다.
- [ ] *Attack surface* 를 나열할 수 있다.
- [ ] *Secret* 이 *코드에 없다*.
- [ ] *서버 검증* 이 모든 입력에 있다.

## 연습 문제

1. 만들고 있는 서비스의 *trust boundary* 를 그려 보세요.
2. 가장 자주 받는 *입력 3가지* 의 *검증 규칙* 을 적어 보세요.
3. 코드베이스에서 *secret 으로 의심되는 문자열* 을 *grep* 으로 찾아 보세요.

## 정리 및 다음 단계

Secure coding 은 *습관* 입니다. 다음 글에서는 가장 많이 새는 곳, *입력값 검증* 을 깊이 봅니다.

<!-- toc:begin -->
- **Secure Coding이란 무엇인가? (현재 글)**
- 입력값 검증 (예정)
- 인증과 세션 (예정)
- 인가와 권한 (예정)
- 안전한 데이터 저장 (예정)
- Secret과 키 관리 (예정)
- SQL Injection과 ORM 안전 사용 (예정)
- XSS와 CSRF 방어 (예정)
- Dependency 취약점 관리 (예정)
- 안전한 로깅과 감사 (예정)
<!-- toc:end -->

## 참고 자료

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Secure Coding Practices Quick Reference](https://owasp.org/www-pdf-archive/OWASP_SCP_Quick_Reference_Guide_v2.pdf)
- [Microsoft Threat Modeling](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool)
- [Google — Secure by Design](https://security.googleblog.com/2024/01/secure-by-design.html)

Tags: SecureCoding, Security, OWASP, DevSecOps, AppSec
