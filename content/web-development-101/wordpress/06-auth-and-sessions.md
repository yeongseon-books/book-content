---
series: web-development-101
episode: 6
title: "바이브코딩을 위한 웹 개발 기초 (6/10): 인증과 세션"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - 웹개발
  - 인증
  - 세션
  - 보안
  - 백엔드
seo_description: 바이브코딩으로 로그인 기능을 만들 때 꼭 알아야 할 인증과 세션의 원리를 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 웹 개발 기초 (6/10): 인증과 세션

이 글은 **바이브코딩을 위한 웹 개발 기초** 시리즈의 여섯 번째 글입니다. AI에게 웹앱을 만들어달라고 요청하기 전에, 웹이 실제로 어떻게 동작하는지 알아야 합니다.

---

AI에게 "로그인 기능 만들어줘"라고 하면 코드가 나옵니다. 그 코드가 얼마나 안전한지 판단하려면 인증의 기본 원리를 알아야 합니다. "비밀번호를 어디에 저장하는지", "쿠키에 어떤 옵션이 필요한지", "JWT를 어디에 두는지" 같은 판단은 바이브코딩에서 가장 보안 사고가 많이 나는 영역입니다.

HTTP는 상태를 기억하지 않는 프로토콜입니다. 로그인 후 다음 요청을 보낼 때, 서버는 이전 요청과 같은 사용자라는 것을 자동으로 알지 못합니다. 이 간극을 쿠키, 세션, JWT로 채웁니다. 이 도구들이 어떻게 동작하는지 모르면, AI가 만들어준 코드의 보안 수준을 평가할 수 없습니다.

이 글에서는 인증과 인가의 차이, 세션 쿠키의 동작 방식, JWT의 역할, 그리고 바이브코딩 중 자주 나오는 인증 관련 실수를 정리합니다.

> HTTP는 상태를 기억하지 않습니다. 바이브코딩으로 만든 로그인 기능이 매 요청마다 "이 사람이 누구인지"를 제대로 확인하는지, 토큰이 안전하게 저장되는지 판단할 수 있어야 합니다.

## 이 글에서 다룰 문제

- 인증과 인가는 무엇이 다를까요?
- 상태가 없는 HTTP 위에서 서버는 사용자를 어떻게 기억할까요?
- 쿠키와 세션은 어떤 식으로 맞물릴까요?
- JWT는 무엇이고 어디에 써야 할까요?
- 바이브코딩 중 인증 관련 보안 실수를 어떻게 막을까요?

## 바이브코딩 관점: 인증을 알아야 하는 이유

AI가 만들어준 로그인 코드에 비밀번호가 평문으로 데이터베이스에 저장되거나, 쿠키에 `HttpOnly` 옵션이 없거나, JWT가 localStorage에 저장되는 경우가 있습니다. 이 각각이 왜 문제인지 모르면, "AI가 만들어준 코드니까 괜찮겠지"라고 생각하고 그냥 배포하게 됩니다.

인증의 기본 원리를 알면 AI에게 "비밀번호는 bcrypt로 해시해서 저장해줘", "쿠키에 HttpOnly, Secure, SameSite 옵션 추가해줘"처럼 구체적인 보안 요구사항을 요청할 수 있습니다.

## 먼저 알아둘 용어

- **Authentication (인증)**: 내가 누구인지 확인하는 과정입니다.
- **Authorization (인가)**: 내가 무엇을 할 수 있는지 결정하는 과정입니다.
- **Session**: 서버가 보관하는 사용자 상태입니다.
- **Cookie**: 브라우저가 도메인 단위로 저장하는 key/value 데이터입니다.
- **JWT**: 서버가 서명한 자기 설명 토큰입니다.

## Before / After: 인증 흐름의 개선

**Before — 매 요청마다 비밀번호 전송 (위험)**

```python
requests.get("/api/me", auth=("alice", "secret"))
# 비밀번호가 반복해서 네트워크를 흐릅니다
```

**After — 세션 쿠키로 한 번만 인증**

```python
s = requests.Session()
s.post("/login", json={"id": "alice", "pw": "secret"})
s.get("/api/me")  # 쿠키가 자동으로 함께 전송됩니다
```

로그인 시점에만 비밀번호를 확인하고, 이후에는 세션 식별자로 사용자를 이어 가는 편이 안전합니다.

## 로그인 흐름을 다섯 단계로 만들어 보기

### 1단계 — Flask 세션 로그인 구현

```python
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
    if not user:
        return jsonify(error="unauth"), 401
    return jsonify(user=user)
```

### 2단계 — 쿠키 생성 확인

```bash
curl -c c.txt -X POST -H "Content-Type: application/json" \
  -d '{"id":"alice","pw":"secret"}' http://localhost:5000/login
curl -b c.txt http://localhost:5000/me
# 출력: {"user":"alice"}
```

### 3단계 — 로그아웃 구현

```python
@app.post("/logout")
def logout():
    session.clear()
    return jsonify(ok=True)
```

### 4단계 — JWT 발급

```python
import jwt, time
SECRET = "dev"
token = jwt.encode(
    {"sub": "alice", "exp": time.time() + 3600},
    SECRET,
    algorithm="HS256"
)
print(jwt.decode(token, SECRET, algorithms=["HS256"]))
```

### 5단계 — Authorization 헤더로 요청

```python
import requests
requests.get("/api/me", headers={"Authorization": f"Bearer {token}"})
```

## 바이브코딩에서 자주 나오는 실수

| 실수 | 원인 | 올바른 이해 |
|------|------|-------------|
| 비밀번호를 평문으로 DB 저장 | 해시 개념 부재 | bcrypt 같은 해시 함수로 저장 필수 |
| JWT를 localStorage에 저장 | 보안 무지 | XSS에 취약. HttpOnly 쿠키가 더 안전 |
| 쿠키에 HttpOnly 없음 | 옵션 모름 | JavaScript로 쿠키 탈취 가능해짐 |
| 만료 없는 JWT 발급 | 토큰 수명 개념 부재 | 짧은 만료 시간(1시간 이하) 설정 필수 |
| 로그인만 하고 로그아웃 구현 안 함 | 미완성 인증 | 세션 무효화 로직 필수 |

## AI 팁: 안전한 인증 요청 방법

```
"로그인 기능을 만들어줘. 다음 보안 요구사항을 반드시 포함해줘:
1. 비밀번호는 bcrypt로 해시해서 저장
2. 세션 쿠키에 HttpOnly=True, Secure=True, SameSite='Lax' 설정
3. 로그아웃 시 서버에서 세션 완전 삭제
4. JWT 사용 시 만료 시간 1시간으로 설정"
```

보안 요구사항을 구체적으로 명시하면 AI가 안전한 코드를 생성합니다.

## 체크리스트

- [ ] 인증과 인가의 차이를 설명할 수 있습니다.
- [ ] 세션과 JWT의 장단점을 알고 있습니다.
- [ ] 비밀번호를 저장할 때 해시 함수를 써야 함을 알고 있습니다.
- [ ] 쿠키 보안 플래그 세 가지(HttpOnly, Secure, SameSite)를 말할 수 있습니다.
- [ ] JWT에 민감한 정보를 넣으면 안 되는 이유를 알고 있습니다.

## 처음 질문으로 돌아가기

- **인증과 인가는 무엇이 다를까요?**
  인증은 "당신이 누구인지"(로그인), 인가는 "당신이 무엇을 할 수 있는지"(권한)를 확인하는 과정입니다.

- **상태가 없는 HTTP 위에서 서버는 사용자를 어떻게 기억할까요?**
  로그인 후 서버가 세션 ID를 만들어 쿠키로 보내고, 브라우저가 이후 요청마다 자동으로 쿠키를 함께 전송합니다.

- **JWT는 무엇이고 어디에 써야 할까요?**
  서버가 서명한 토큰으로, 서버가 상태를 저장하지 않아도 사용자를 확인할 수 있습니다. 하지만 내용이 노출될 수 있으므로 민감한 정보는 넣으면 안 됩니다.

## 정리

인증은 바이브코딩에서 보안 사고가 가장 많이 나는 영역입니다. AI가 만들어준 인증 코드에 비밀번호 해시, 쿠키 보안 옵션, 만료 시간이 제대로 설정되어 있는지 확인하는 습관이 중요합니다. 다음 글에서는 이렇게 확인한 사용자 데이터를 영구 저장하는 데이터베이스 연결을 다룹니다.

## 참고 자료

- [Using HTTP cookies (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)
- [Flask sessions](https://flask.palletsprojects.com/en/stable/quickstart/#sessions)
- [JWT introduction](https://jwt.io/introduction)
- [Session Management Cheat Sheet (OWASP)](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 웹 개발 기초 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [바이브코딩을 위한 웹 개발 기초 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [바이브코딩을 위한 웹 개발 기초 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [바이브코딩을 위한 웹 개발 기초 (4/10): HTTP와 API](./04-http-and-api.md)
- [바이브코딩을 위한 웹 개발 기초 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- **바이브코딩을 위한 웹 개발 기초 (6/10): 인증과 세션 (현재 글)**
- [바이브코딩을 위한 웹 개발 기초 (7/10): 데이터베이스 연결](./07-connecting-to-database.md)
- [바이브코딩을 위한 웹 개발 기초 (8/10): 배포](./08-deployment.md)
- [바이브코딩을 위한 웹 개발 기초 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- [바이브코딩을 위한 웹 개발 기초 (10/10): 작은 웹앱 만들기](./10-building-a-small-web-app.md)

<!-- toc:end -->

Tags: 바이브코딩, 웹개발, 인증, 세션, 보안, 백엔드
