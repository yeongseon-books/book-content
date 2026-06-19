---
series: web-development-101
episode: 5
title: "Web Development 101 (5/10): Frontend와 Backend"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/207"
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
  - Frontend
  - Backend
  - Architecture
  - FullStack
seo_description: Frontend와 Backend의 책임, SPA와 SSR, API 계약의 의미를 설명합니다.
last_reviewed: '2026-05-15'
---

# Web Development 101 (5/10): Frontend와 Backend

웹 개발을 배우다 보면 Frontend와 Backend를 서로 다른 기술 묶음처럼만 보기 쉽습니다. 하지만 실무에서 더 중요한 것은 도구 이름이 아니라 책임 경계입니다. 누가 데이터를 보여 주고, 누가 저장하고, 누가 권한을 검증하는지 구분되지 않으면 작은 서비스도 금방 지저분해집니다.

이 글은 Web Development 101 시리즈의 5번째 글입니다.

여기서는 Frontend와 Backend의 역할을 나눠 보고, SPA와 SSR이 어떤 차이를 가지는지, 두 세계를 잇는 API 계약이 왜 중요한지 정리하겠습니다.

![Web Development 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/05/05-01-concept-at-a-glance.ko.png)
*Web Development 101 5장 흐름 개요*

> Frontend와 Backend는 기술 묶음이 아니라 책임 경계입니다 — 데이터의 진실은 백엔드, 표현과 즉각 반응은 프런트엔드가 가지고, 그 경계를 잇는 API 계약이 두 세계의 유일한 공식 통로입니다.

## 이 글에서 다룰 문제

- Frontend와 Backend의 일은 어디서 갈릴까요?
- 데이터의 진실은 어느 쪽이 가져야 할까요?
- SPA와 SSR은 무엇이 다를까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 경계가 중요한가

한 사람이 양쪽 코드를 모두 짜더라도 책임 경계가 흐려지면 코드가 빠르게 무너집니다. Frontend에서 권한 검사를 하고, Backend에서 화면용 문자열을 과하게 조립하고, API 형식이 문서 없이 바뀌기 시작하면 변경 영향 범위를 읽기 어려워집니다.

이 경계는 물리적인 선이 아니라 소유권에 대한 약속입니다. 무엇을 저장할지, 무엇을 노출할지, 어느 쪽이 최종 판단권을 가질지 먼저 정해야 시스템이 커져도 버틸 수 있습니다.

## 두 영역의 책임 분리

```
┌───────────────────────────────────────────────────────────────┐
│                        클라이언트 (Browser)                    │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                   FRONTEND                              │  │
│  │  - HTML/CSS/JS 렌더링                                   │  │
│  │  - 사용자 입력 처리 (폼, 클릭)                          │  │
│  │  - 즉각적인 UI 반응 (로딩 표시, 낙관적 업데이트)        │  │
│  │  - 클라이언트 사이드 유효성 검사 (UX를 위한 보조)       │  │
│  │  - 상태 관리 (장바구니 UI, 페이지 전환 애니메이션)      │  │
│  └─────────────────────┬───────────────────────────────────┘  │
└────────────────────────┼──────────────────────────────────────┘
                         │  HTTP API (JSON)
                         │  ↕ 유일한 공식 통로
┌────────────────────────┼──────────────────────────────────────┐
│   서버 (Server)        │                                       │
│  ┌─────────────────────▼───────────────────────────────────┐  │
│  │                   BACKEND                               │  │
│  │  - 비즈니스 로직 실행                                   │  │
│  │  - 권한 검증 (모든 API에서 서버 측 재확인)              │  │
│  │  - 데이터베이스 읽기/쓰기                               │  │
│  │  - 외부 서비스 호출 (이메일, 결제, 알림)               │  │
│  │  - 데이터의 진실 보관                                   │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

## 먼저 알아둘 용어

- **Frontend**: 브라우저에서 실행되며 사용자에게 정보를 보여 주는 영역입니다.
- **Backend**: 서버에서 실행되며 데이터를 처리하고 저장하는 영역입니다.
- **SPA (Single Page Application)**: 첫 페이지를 한 번 로드한 뒤 JavaScript로 화면을 바꾸는 방식입니다.
- **SSR (Server-Side Rendering)**: 요청마다 서버가 HTML을 만들어 돌려주는 방식입니다.
- **API Contract**: 두 영역이 합의한 요청과 응답의 형태입니다.
- **CORS**: 브라우저가 다른 origin에 대한 요청을 제한하는 정책입니다.

## 권한 검사: Frontend만으로는 안 된다

```js
// 나쁜 예: Frontend에서만 권한 검사
if (user.role === "admin") {
  showDeleteButton();    // 개발자 도구로 쉽게 우회 가능
}

function deleteUser(id) {
  fetch(`/api/users/${id}`, { method: "DELETE" });
  // Backend에서 권한을 다시 확인하지 않으면 누구나 삭제 가능
}
```

```python
# 올바른 예: Backend에서 권한 재확인
from flask import request, jsonify

def require_admin(f):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        user = verify_token(token)
        if not user or user["role"] != "admin":
            return jsonify(error={"code": "FORBIDDEN"}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.delete("/api/users/<int:user_id>")
@require_admin
def delete_user(user_id):
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    return "", 204
```

프론트엔드의 권한 체크는 UX를 위한 것이고, 실제 보안은 반드시 백엔드에서 다시 검증해야 합니다.

## 작은 Backend API 만들기

```python
# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])  # 특정 origin만 허용

items = []

@app.get("/api/items")
def list_items():
    return jsonify(items)

@app.post("/api/items")
def create_item():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify(error={"code": "VALIDATION_ERROR", "message": "name 필드 필수"}), 400
    item = {"id": len(items) + 1, "name": data["name"]}
    items.append(item)
    return jsonify(item), 201

@app.delete("/api/items/<int:item_id>")
def delete_item(item_id):
    global items
    items = [i for i in items if i["id"] != item_id]
    return "", 204

if __name__ == "__main__":
    app.run(port=8000, debug=True)
```

## Frontend에서 API 호출

```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>아이템 목록</title>
  <style>
    body { font-family: system-ui; max-width: 600px; margin: 2rem auto; }
    .item { display: flex; justify-content: space-between; padding: 0.5rem; border-bottom: 1px solid #eee; }
    .btn-delete { background: #ef4444; color: white; border: none; padding: 4px 8px; cursor: pointer; border-radius: 4px; }
    .error { color: red; margin: 1rem 0; }
  </style>
</head>
<body>
  <h1>아이템 목록</h1>
  <form id="form">
    <input id="name" placeholder="이름 입력" required>
    <button type="submit">추가</button>
  </form>
  <div id="error" class="error" hidden></div>
  <div id="list"></div>

  <script>
    const API = "http://localhost:8000/api";

    async function apiCall(path, options = {}) {
      const r = await fetch(API + path, {
        headers: { "Content-Type": "application/json", ...options.headers },
        ...options,
      });
      if (!r.ok) {
        const err = await r.json().catch(() => ({}));
        throw new Error(err.error?.message || `HTTP ${r.status}`);
      }
      return r.status === 204 ? null : r.json();
    }

    function showError(msg) {
      const el = document.getElementById("error");
      el.textContent = msg;
      el.hidden = false;
      setTimeout(() => { el.hidden = true; }, 4000);
    }

    async function loadItems() {
      const items = await apiCall("/items");
      const listEl = document.getElementById("list");
      listEl.innerHTML = items.map(item => `
        <div class="item">
          <span>${item.name}</span>
          <button class="btn-delete" data-id="${item.id}">삭제</button>
        </div>
      `).join("");
    }

    document.getElementById("form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = document.getElementById("name").value.trim();
      try {
        await apiCall("/items", { method: "POST", body: JSON.stringify({ name }) });
        document.getElementById("name").value = "";
        await loadItems();
      } catch (err) {
        showError(err.message);
      }
    });

    document.getElementById("list").addEventListener("click", async (e) => {
      const btn = e.target.closest(".btn-delete");
      if (!btn) return;
      try {
        await apiCall(`/items/${btn.dataset.id}`, { method: "DELETE" });
        await loadItems();
      } catch (err) {
        showError(err.message);
      }
    });

    loadItems();
  </script>
</body>
</html>
```

## SPA vs SSR 비교

```
SPA (Single Page Application)
─────────────────────────────
브라우저에서 처음 받는 것:
  <!doctype html><html><body><div id="root"></div><script src="bundle.js"></script></body></html>

이후 흐름:
  1. bundle.js 다운로드 및 실행
  2. JavaScript가 fetch("/api/data")로 데이터 요청
  3. 응답 받아 DOM 생성 → 화면 표시

장점: 페이지 전환이 부드럽고 빠름, Backend와 명확한 분리
단점: 초기 로딩이 느림, SEO가 불리할 수 있음

SSR (Server-Side Rendering)
──────────────────────────
브라우저에서 처음 받는 것:
  <html><body><ul><li>apple</li><li>pear</li></ul></body></html>

이후 흐름:
  HTML이 이미 데이터를 포함 → 즉시 화면 표시

장점: 첫 화면이 빠름, SEO 유리
단점: 페이지 전환마다 서버 왕복
```

```python
# SSR 예시 (Flask Jinja2)
@app.get("/")
def home():
    items = db.execute("SELECT * FROM items ORDER BY id DESC").fetchall()
    return render_template("index.html", items=items)
```

```html
<!-- templates/index.html -->
<ul>
  {% for item in items %}
    <li>{{ item.name }}</li>
  {% endfor %}
</ul>
```

```js
// SPA 예시 (JavaScript fetch)
const items = await fetch("/api/items").then(r => r.json());
const ul = document.querySelector("ul");
items.forEach(item => {
  const li = document.createElement("li");
  li.textContent = item.name;
  ul.appendChild(li);
});
```

## CORS 이해하기

```
CORS (Cross-Origin Resource Sharing)

브라우저 기본 정책:
  http://frontend.com → http://api.example.com/data
  브라우저: "다른 origin이라서 요청 차단!"

해결: 서버가 허용 origin을 명시
```

```python
# Flask-CORS로 설정
from flask_cors import CORS

app = Flask(__name__)

# 개발: 모든 origin 허용 (운영에서는 절대 이렇게 하지 말 것)
# CORS(app)

# 운영: 특정 origin만 허용
CORS(app, origins=["https://myapp.com", "https://www.myapp.com"])

# 특정 엔드포인트에만
@app.get("/api/public")
@cross_origin(origins=["*"])
def public_endpoint():
    return jsonify(data="누구나 접근 가능")
```

```
CORS 요청 흐름 (간단 요청):
  1. 브라우저: GET /api/data 요청
  2. 서버: Access-Control-Allow-Origin: https://myapp.com 응답
  3. 브라우저: origin 확인 후 허용 or 차단

CORS 요청 흐름 (Preflight):
  1. 브라우저: OPTIONS /api/data 사전 요청
  2. 서버: 허용 메서드, 헤더, origin 응답
  3. 브라우저: 허용이면 실제 요청 전송
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|------|------|-------------|
| 권한 검사를 Frontend에서만 하기 | 개발자 도구로 쉽게 우회 | Backend API에서 반드시 재확인 |
| API 계약 없이 양쪽 동시 개발 | 필드 이름, 타입 불일치 | API 스펙 먼저 합의 후 병렬 개발 |
| CORS를 모든 origin에 열어 두기 | 불필요한 보안 구멍 | 특정 origin만 명시적으로 허용 |
| 비즈니스 로직 전부를 Frontend에 | 민감 정보와 검증 로직 노출 | 비즈니스 로직은 Backend에 |
| Backend가 화면용 HTML 문자열 반환 | Frontend가 재활용 불가 | Backend는 JSON, Frontend가 렌더링 |

## 운영에서는 이렇게 보입니다

스타트업은 SPA + REST API 조합으로 시작하는 경우가 많고, 콘텐츠 사이트는 SSR 계열 프레임워크를 선호하는 경우가 많습니다. 어떤 조합을 택하더라도 강한 팀은 API 계약을 먼저 그리고, 진실은 Backend에, 사용자 경험은 Frontend에 두려는 원칙을 유지합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 데이터의 진실은 Backend에 둡니다.
- 사용자 경험은 Frontend에서 세심하게 다룹니다.
- API 계약을 먼저 그려 두고 양쪽 구현을 시작합니다.
- 보안과 권한 검사는 반드시 Backend에서 다시 확인합니다.
- SPA와 SSR은 유행이 아니라 상황에 맞춰 선택합니다.

## 운영 체크리스트

- [ ] Frontend와 Backend의 책임을 각각 한 문장으로 설명할 수 있습니다.
- [ ] API 계약의 예를 간단히 그릴 수 있습니다.
- [ ] CORS 오류 메시지를 읽을 수 있습니다.
- [ ] SPA와 SSR의 장단점을 알고 있습니다.
- [ ] 권한 검사는 Backend가 맡는다는 점을 알고 있습니다.

## 연습 문제

1. 같은 화면을 SPA와 SSR 두 방식으로 각각 만들어 보고 첫 화면 속도를 비교해 보세요.
2. 일부러 CORS 오류를 만든 뒤 브라우저 콘솔 메시지를 읽어 보세요.
3. Frontend에서만 권한 체크하는 코드를 개발자 도구로 우회해 보세요.

## 정리와 다음 글

Frontend와 Backend의 경계는 기술 분류표가 아니라 책임 약속입니다. 이 약속이 선명해야 데이터, 보안, 사용자 경험이 제자리를 찾습니다. 다음 글에서는 이 경계 위에 로그인과 사용자 기억을 얹는 인증과 세션을 다루겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Web Development 101 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [Web Development 101 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [Web Development 101 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [Web Development 101 (4/10): HTTP와 API](./04-http-and-api.md)
- **Web Development 101 (5/10): Frontend와 Backend (현재 글)**
- [Web Development 101 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- [Web Development 101 (7/10): 데이터베이스 연결](./07-connecting-to-database.md)
- [Web Development 101 (8/10): 배포](./08-deployment.md)
- [Web Development 101 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- [작은 웹앱 만들기](./10-building-a-small-web-app.md)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Client-side and server-side website programming (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/First_steps/Client-Server_overview)
- [Single-page application (MDN)](https://developer.mozilla.org/en-US/docs/Glossary/SPA)
- [Server-side rendering (MDN)](https://developer.mozilla.org/en-US/docs/Glossary/SSR)

### 검증용 자료
- [CORS guide (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
- [Fetch API 사용법 (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)

- [web-development-101 예제 코드 저장소 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/web-development-101/ko)

Tags: Computer Science, WebDevelopment, Frontend, Backend, Architecture, FullStack
