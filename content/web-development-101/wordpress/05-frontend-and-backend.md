---
series: web-development-101
episode: 5
title: "바이브코딩을 위한 웹 개발 기초 (5/10): Frontend와 Backend"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - 웹개발
  - 프론트엔드
  - 백엔드
  - 아키텍처
  - 풀스택
seo_description: 바이브코딩으로 웹앱을 만들 때 Frontend와 Backend의 책임 경계를 이해하는 방법을 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 웹 개발 기초 (5/10): Frontend와 Backend

이 글은 **바이브코딩을 위한 웹 개발 기초** 시리즈의 다섯 번째 글입니다. AI에게 웹앱을 만들어달라고 요청하기 전에, 웹이 실제로 어떻게 동작하는지 알아야 합니다.

---

AI에게 "로그인 기능 있는 웹앱 만들어줘"라고 하면 꽤 많은 코드가 나옵니다. 그런데 "비밀번호 확인 로직을 JavaScript에 넣었는지, 서버에 넣었는지"를 모르면 보안 구멍이 생깁니다. 브라우저 코드는 사용자가 열어볼 수 있습니다. 비밀번호 비교, 권한 검사, 민감한 데이터 처리는 반드시 서버에서 해야 합니다.

바이브코딩의 흔한 함정이 여기에 있습니다. AI는 요청대로 코드를 만들어 주지만, "이 코드가 브라우저에서 실행되는지 서버에서 실행되는지"를 구분하지 않으면 나중에 큰 문제가 됩니다. Frontend와 Backend의 책임 경계를 알면 AI에게 "이 부분은 서버에서 처리해줘", "이 부분은 프론트엔드에서만 써도 돼"라고 정확하게 요청할 수 있습니다.

이 글에서는 Frontend와 Backend의 역할 분리, SPA와 SSR의 차이, API 계약의 중요성을 정리합니다. 바이브코딩 중 이 경계를 모르면 생기는 문제와 올바른 질문 방법도 함께 다룹니다.

> Frontend와 Backend는 기술 묶음이 아니라 책임 경계입니다. 바이브코딩으로 만든 코드가 브라우저에서 실행되는지 서버에서 실행되는지 구분할 수 있어야, 보안 구멍 없는 앱을 만들 수 있습니다.

## 이 글에서 다룰 문제

- Frontend와 Backend의 일은 어디서 갈릴까요?
- 데이터의 진실은 어느 쪽이 가져야 할까요?
- SPA와 SSR은 무엇이 다를까요?
- 바이브코딩 중 권한 검사를 잘못 배치하면 어떤 문제가 생길까요?
- API 계약이란 무엇이고 왜 중요한가요?

## 바이브코딩 관점: 경계를 알아야 하는 이유

AI에게 "관리자만 볼 수 있는 페이지 만들어줘"라고 하면 두 가지 코드가 나올 수 있습니다. JavaScript로 "관리자 여부를 확인해서 페이지를 숨기는" 코드와, 서버에서 "관리자가 아니면 403을 돌려주는" 코드입니다. 전자는 개발자 도구에서 변수 하나 바꾸면 우회할 수 있습니다.

바이브코딩으로 빠르게 만든 앱에서 이 구분이 없으면, 나중에 "어, 일반 사용자가 관리자 데이터에 접근할 수 있었어요"라는 상황이 생깁니다. 이 글을 읽고 나면 AI에게 "권한 검사는 반드시 서버에서 처리해줘"라고 명시적으로 요청할 수 있게 됩니다.

## 먼저 알아둘 용어

- **Frontend**: 브라우저에서 실행되며 사용자에게 정보를 보여 주는 영역입니다.
- **Backend**: 서버에서 실행되며 데이터를 처리하고 저장하는 영역입니다.
- **SPA**: 첫 페이지를 한 번 로드한 뒤 JavaScript로 화면을 바꾸는 방식입니다.
- **SSR**: 요청마다 서버가 HTML을 만들어 돌려주는 방식입니다.
- **API 계약**: 두 영역이 합의한 요청과 응답의 형태입니다.

## Before / After: 권한 검사의 올바른 위치

**Before — Frontend에서만 검사 (위험)**

```js
// 브라우저 코드 — 누구나 열어볼 수 있음
if (user.role === "admin") {
    showAdminPanel();
}
```

**After — Backend에서도 반드시 검사**

```python
# 서버 코드 — 우회 불가
@app.get("/api/admin/users")
def admin_users():
    if not current_user.is_admin:
        return jsonify(error="forbidden"), 403
    return jsonify(db.get_all_users())
```

Frontend 검사는 UX를 위한 것이고, Backend 검사는 보안을 위한 것입니다. 둘 다 있어야 합니다.

## 두 세계를 다섯 단계로 연결해 보기

### 1단계 — 간단한 Backend 만들기

```python
from flask import Flask, jsonify
app = Flask(__name__)

@app.get("/api/items")
def items():
    return jsonify([{"id": 1, "name": "사과"}, {"id": 2, "name": "배"}])
```

### 2단계 — Frontend에서 호출하기

```html
<ul id="list"></ul>
<script>
fetch("/api/items")
  .then(r => r.json())
  .then(items => {
    const ul = document.getElementById("list");
    items.forEach(it => {
      const li = document.createElement("li");
      li.textContent = it.name;
      ul.appendChild(li);
    });
  });
</script>
```

### 3단계 — CORS 설정하기

```python
from flask_cors import CORS
CORS(app)  # 다른 origin에서도 호출 가능하게
```

### 4단계 — SSR 방식과 비교하기

```python
from flask import render_template_string
@app.get("/")
def home():
    items = [{"name": "사과"}, {"name": "배"}]
    return render_template_string(
        "<ul>{% for i in items %}<li>{{ i.name }}</li>{% endfor %}</ul>",
        items=items
    )
```

### 5단계 — 책임 배치 확인하기

```text
Frontend (브라우저):  UI 표시, 사용자 입력 수집, API 호출
Backend (서버):       데이터 검증, 권한 검사, 저장, 비즈니스 로직
```

## 바이브코딩에서 자주 나오는 실수

| 실수 | 원인 | 올바른 이해 |
|------|------|-------------|
| 권한 검사를 Frontend에만 배치 | 경계 개념 부재 | Backend에서 반드시 재검사 필요 |
| API 계약 없이 양쪽 동시 개발 | 소통 부재 | 필드 이름, 타입, 구조를 먼저 합의 |
| 비밀번호를 JavaScript에서 비교 | 보안 무지 | 비교는 반드시 서버에서 |
| CORS를 모든 origin에 무조건 열기 | 빠른 해결 위주 | 필요한 origin만 허용 |
| SPA/SSR 선택 없이 섞어 씀 | 방식 미결정 | 초기에 렌더링 방식 결정 후 일관성 유지 |

## AI 팁: 경계를 명확히 한 요청 방법

```
"사용자 목록 페이지를 만들어줘.
- 관리자만 접근 가능하게 해줘 (서버에서 권한 검사)
- Frontend는 데이터를 가져와서 표시만 하게 해줘
- 비밀번호나 권한 로직은 JavaScript에 넣지 말고 서버에만 넣어줘"
```

책임 경계를 명시하면 AI가 보안상 올바른 구조로 코드를 생성합니다.

## 체크리스트

- [ ] Frontend와 Backend의 책임을 각각 한 문장으로 설명할 수 있습니다.
- [ ] 권한 검사는 Backend에서 해야 함을 알고 있습니다.
- [ ] API 계약의 예를 간단히 그릴 수 있습니다.
- [ ] CORS 오류 메시지를 읽을 수 있습니다.
- [ ] SPA와 SSR의 장단점을 알고 있습니다.

## 처음 질문으로 돌아가기

- **Frontend와 Backend의 일은 어디서 갈릴까요?**
  브라우저에서 실행되는 코드가 Frontend, 서버에서 실행되는 코드가 Backend입니다. 사용자가 볼 수 있는 코드(Frontend)에는 민감한 로직을 넣으면 안 됩니다.

- **데이터의 진실은 어느 쪽이 가져야 할까요?**
  데이터베이스와 연결된 Backend입니다. Frontend가 보여주는 값은 Backend가 제공한 데이터를 표현하는 것입니다.

- **SPA와 SSR은 무엇이 다를까요?**
  SPA는 첫 로드 후 JavaScript로 화면을 바꾸고, SSR은 매 요청마다 서버가 완성된 HTML을 만들어 줍니다. 초기 로딩 속도와 SEO 요구사항에 따라 선택합니다.

## 정리

Frontend와 Backend의 경계는 기술 분류가 아니라 보안과 책임의 문제입니다. 바이브코딩으로 앱을 만들 때 AI에게 "이 로직은 서버에서", "이 부분은 브라우저에서"라고 명확하게 요청하면, 나중에 보안 문제가 생기는 것을 미리 막을 수 있습니다. 다음 글에서는 로그인과 세션을 만드는 인증 방식을 정리합니다.

## 참고 자료

- [Client-side and server-side website programming (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/First_steps/Client-Server_overview)
- [Single-page application (MDN)](https://developer.mozilla.org/en-US/docs/Glossary/SPA)
- [CORS guide (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
- [Fetch API 사용법 (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 웹 개발 기초 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [바이브코딩을 위한 웹 개발 기초 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [바이브코딩을 위한 웹 개발 기초 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [바이브코딩을 위한 웹 개발 기초 (4/10): HTTP와 API](./04-http-and-api.md)
- **바이브코딩을 위한 웹 개발 기초 (5/10): Frontend와 Backend (현재 글)**
- [바이브코딩을 위한 웹 개발 기초 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- [바이브코딩을 위한 웹 개발 기초 (7/10): 데이터베이스 연결](./07-connecting-to-database.md)
- [바이브코딩을 위한 웹 개발 기초 (8/10): 배포](./08-deployment.md)
- [바이브코딩을 위한 웹 개발 기초 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- [바이브코딩을 위한 웹 개발 기초 (10/10): 작은 웹앱 만들기](./10-building-a-small-web-app.md)

<!-- toc:end -->

Tags: 바이브코딩, 웹개발, 프론트엔드, 백엔드, 아키텍처, 풀스택
