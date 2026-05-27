---
series: web-development-101
episode: 3
title: "Web Development 101 (3/10): 브라우저와 DOM"
status: publish-ready
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
  - Browser
  - DOM
  - JavaScript
  - Frontend
seo_description: 브라우저가 HTML을 파싱하여 DOM 트리를 형성하고 렌더링 파이프라인을 거쳐 화면을 그리는 과정과 이벤트 루프의 동작 원리를 알아봅니다.
last_reviewed: '2026-05-15'
---

# Web Development 101 (3/10): 브라우저와 DOM

브라우저는 HTML 파일을 그대로 화면에 붙이지 않습니다. 텍스트를 읽고 구조를 만들고, 스타일을 계산하고, 위치를 정하고, 픽셀을 그린 뒤에야 우리가 보는 페이지가 완성됩니다. 여기에 JavaScript의 이벤트 처리까지 얹히면 비로소 클릭 가능한 화면이 됩니다.

이 글은 Web Development 101 시리즈의 3번째 글입니다.

여기서는 브라우저가 HTML을 DOM으로 바꾸고, 렌더링 파이프라인과 이벤트 루프를 통해 살아 있는 화면을 만드는 과정을 정리하겠습니다.

![Web Development 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/03/03-01-concept-at-a-glance.ko.png)
*Web Development 101 3장 흐름 개요*

> 브라우저는 HTML 텍스트를 DOM 트리로 바꾼 뒤 스타일·레이아웃·페인트·이벤트 루프를 거쳐야 비로소 클릭 가능한 화면이 됩니다 — 이 파이프라인을 알면 JavaScript가 무엇을 읽고 무엇을 바꾸는지가 명확해집니다.

## 먼저 던지는 질문

- DOM은 정확히 무엇이며 어떻게 만들어질까요?
- 브라우저 렌더링 파이프라인은 어떤 단계로 이어질까요?
- JavaScript는 DOM을 어떻게 읽고 바꿀까요?

## 왜 이 모델이 중요한가

DOM에 대한 감각이 없으면 페이지가 왜 느린지 설명하기 어렵습니다. HTML, CSS, JavaScript가 모두 정상처럼 보여도 실제 병목은 layout이나 paint에서 생길 수 있기 때문입니다. 이 과정을 알지 못하면 React, Vue 같은 프레임워크도 그저 복잡한 마법처럼 보입니다.

반대로 브라우저가 무엇을 파싱하고, 언제 레이아웃을 다시 계산하고, 어떤 시점에 비동기 콜백을 실행하는지 알고 있으면 프레임워크의 동작도 훨씬 명확해집니다. 성능 문제를 볼 때도 추측 대신 구체적인 단계 이름으로 대화를 시작할 수 있습니다.

## 한눈에 보는 개념 지도

브라우저는 텍스트를 곧바로 픽셀로 그리지 않습니다. DOM과 스타일 계산, layout, paint가 순서대로 이어지고, 그 사이에 JavaScript가 DOM을 바꾸면 일부 단계가 다시 실행됩니다.

### 직접 검증해 볼 포인트

- DevTools Elements 탭에서 HTML이 DOM 트리로 보이는지 확인합니다.
- Performance 탭에서 버튼 클릭 뒤 layout과 paint 이벤트가 다시 생기는지 기록합니다.
- `setTimeout(..., 0)` 예제를 실행해 동기 코드와 비동기 콜백 순서를 비교합니다.

**기대 결과:** DOM 변경이 있으면 layout 또는 paint가 다시 나타나고, `setTimeout` 콜백은 동기 로그 뒤에 실행됩니다.

**실패 모드:** 반복문 안에서 DOM을 계속 바꾸면 layout 비용이 누적됩니다. 사용자 입력을 `innerHTML`에 직접 넣으면 성능보다 먼저 보안 문제가 생길 수 있습니다.

## 먼저 알아둘 용어

- **DOM (Document Object Model)**: HTML을 객체 트리로 표현한 구조입니다.
- **Render tree**: DOM과 계산된 스타일을 합친 렌더링용 트리입니다.
- **Layout**: 각 요소의 위치와 크기를 계산하는 단계입니다.
- **Paint**: 실제 픽셀을 그리는 단계입니다.
- **Event loop**: 비동기 작업과 콜백 실행 순서를 관리하는 큐 시스템입니다.

## 전후 비교로 보는 DOM 조작 방식

**Before (문자열 방식 HTML)**

```js
document.body.innerHTML += "<p>new item</p>";
```

**After (DOM API)**

```js
const p = document.createElement("p");
p.textContent = "new item";
document.body.appendChild(p);
```

DOM API는 문자열을 이어 붙이는 방식보다 안전하고 예측 가능하며, 기본적으로 XSS 위험도 줄여 줍니다.

## DOM을 다섯 단계로 다뤄 보기

### 1단계 — 트리 보기

```html
<!-- index.html -->
<ul id="list">
  <li>apple</li>
  <li>pear</li>
</ul>
<script src="app.js"></script>
```

브라우저는 이 HTML을 읽고 `ul` 아래에 두 개의 `li`가 있는 트리를 만듭니다.

### 2단계 — 요소 선택하기

```js
// app.js
const list = document.getElementById("list");
const items = list.querySelectorAll("li");
console.log(items.length);  // 2
```

JavaScript는 DOM API를 통해 트리 안의 특정 노드를 선택합니다. 이 단계가 있어야 읽기와 수정이 시작됩니다.

### 3단계 — 새 요소 추가하기

```js
const li = document.createElement("li");
li.textContent = "grape";
list.appendChild(li);
```

새 노드를 만들고 부모 노드에 붙이면 DOM이 바뀝니다. 이런 변화는 이후 layout과 paint를 다시 일으킬 수 있습니다.

### 4단계 — 이벤트 등록하기

```js
list.addEventListener("click", (e) => {
  if (e.target.tagName === "LI") {
    console.log("clicked:", e.target.textContent);
  }
});
```

부모 요소 하나에 리스너를 달고 자식 클릭을 처리하는 방식이 이벤트 위임입니다. 요소가 많아질수록 이 방식이 더 효율적입니다.

### 5단계 — 비동기 순서 비교하기

```js
console.log("1");
setTimeout(() => console.log("2"), 0);
console.log("3");
// 출력: 1, 3, 2 — 이벤트 루프가 콜백을 나중에 실행합니다.
```

`setTimeout(fn, 0)`이라고 해도 콜백이 즉시 실행되지는 않습니다. 현재 실행 중인 동기 코드가 끝난 뒤 이벤트 루프가 큐에서 콜백을 꺼냅니다.

## 이 코드에서 먼저 봐야 할 점

- DOM 변경은 비용이 큰 연산입니다. layout과 paint를 다시 유발할 수 있습니다.
- 이벤트 위임은 메모리와 시간 비용을 함께 줄여 줍니다.
- `setTimeout(fn, 0)`은 지금 즉시가 아니라 나중 실행입니다.

## 여기서 자주 헷갈립니다

1. **사용자 입력을 `innerHTML`에 넣는 경우**: XSS 위험이 커집니다.
2. **반복문 안에서 DOM 노드를 하나씩 붙이는 경우**: layout이 반복해서 일어날 수 있습니다.
3. **모든 `<li>`에 리스너를 따로 붙이는 경우**: 이벤트 위임의 장점을 놓칩니다.
4. **JavaScript 실행 시점을 모르는 경우**: `defer`, `async`, inline script의 차이를 모르면 순서 버그가 생깁니다.
5. **DOM이 항상 동기적으로 보인다고 가정하는 경우**: 비동기 콜백 순서가 예상과 다르게 느껴질 수 있습니다.

## 운영에서는 이렇게 보입니다

React와 Vue는 Virtual DOM이나 반응형 시스템을 이용해 실제 DOM 호출을 묶어서 처리합니다. 긴 리스트, 채팅 화면, 무한 스크롤처럼 화면 갱신이 많은 앱은 모두 DOM과 이벤트 루프 위에서 돌아갑니다. 페이지가 느리면 Chrome DevTools의 Performance 탭에서 layout과 paint를 flame chart로 확인하는 습관이 필요합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- DOM 변경은 가능한 한 묶어서 처리합니다.
- 이벤트는 부모에 위임해 리스너 수를 줄입니다.
- 최적화 전에 먼저 측정합니다.
- 긴 리스트에는 virtualization을 검토합니다.
- repaint와 reflow를 많이 일으키는 코드를 먼저 찾습니다.

## 체크리스트

- [ ] 렌더링 다섯 단계를 말할 수 있습니다.
- [ ] DOM API로 요소를 만들고 붙일 수 있습니다.
- [ ] 이벤트 위임을 사용할 수 있습니다.
- [ ] 동기 코드와 비동기 콜백의 순서를 예상할 수 있습니다.
- [ ] `innerHTML`의 위험을 알고 있습니다.

## 연습 문제

1. `DocumentFragment` 없이 100개의 `<li>`를 추가하는 경우와 사용하는 경우를 비교해 보세요.
2. 부모 `<ul>` 하나에 클릭 리스너를 달고 클릭된 `<li>`의 텍스트를 출력해 보세요.
3. `console.log("a"); Promise.resolve().then(() => console.log("b")); console.log("c");`의 출력 순서를 예상해 보세요.

## 정리와 다음 글

브라우저는 DOM을 만들고, 스타일을 계산하고, 배치를 정하고, 픽셀을 그리는 기계입니다. 이 파이프라인을 이해하면 화면 성능과 프레임워크 동작이 모두 더 또렷해집니다. 다음 글에서는 클라이언트와 서버가 실제로 무엇을 주고받는지 HTTP와 API를 봅니다.

## HTTP-인증-배포를 함께 검증하는 점검 루틴

웹 서비스는 단일 기능이 아니라 경로 전체의 안정성으로 평가됩니다. 따라서 API 스펙, 인증 예외, 배포 헬스체크를 같은 릴리스 체크리스트로 묶는 편이 안전합니다.

```text
배포 전 점검
1) 핵심 API 3개에 대해 상태 코드/응답 스키마 계약 테스트 실행
2) access 만료, refresh 만료, revoke 토큰 시나리오 재현
3) /health, /ready 엔드포인트를 배포 환경에서 실제 호출
4) CDN/브라우저 캐시 무효화 정책 확인
```

### 장애 예방을 위한 최소 헤더 정책

```http
Cache-Control: no-store
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
```

헤더 정책은 프론트엔드 코드 변경 없이도 보안/캐시 동작을 크게 바꿉니다. 기능 개발과 별개로 표준 헤더를 고정해 두면 릴리스 변동성이 줄어듭니다.

### 배포 후 15분 관찰 항목

- 5xx 비율과 p95 지연 시간의 급격한 상승 여부
- 로그인 성공률, 토큰 재발급 성공률
- 정적 자산 404 발생률

이 루틴을 반복하면 "배포는 되었지만 정상 운영은 아닌" 상태를 초기에 감지할 수 있습니다.

## 실전 앵커 모음: 렌더링을 운영 문서로 바꾸기

작은 기능이라도 운영 단계까지 생각하면 문서화 기준이 달라집니다. 아래 예시는 팀이 기능 구현과 동시에 남겨 두면 바로 도움이 되는 최소 산출물입니다. 특히 요청/응답 계약, 세션/쿠키 정책, SQL 기준 쿼리, 배포 설정, 캐시 규칙을 함께 기록하면 변경 시점의 실패 반경을 크게 줄일 수 있습니다.

### HTTP 요청/응답 계약 예시

```http
GET /api/v1/todos?limit=20&cursor=todo_120 HTTP/1.1
Host: api.example.com
Accept: application/json
Authorization: Bearer <access_token>
X-Request-Id: req-2026-05-21-0001
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: private, max-age=30
ETag: "todo-list-v42"

{
  "items": [
    {"id": "todo_121", "text": "문서 작성", "done": false},
    {"id": "todo_122", "text": "테스트 실행", "done": true}
  ],
  "next_cursor": "todo_122"
}
```

응답 예시는 상태 코드만 맞추는 수준에서 끝내지 말고, 캐시 정책과 추적 ID를 함께 포함하는 편이 좋습니다. 특히 `X-Request-Id`를 표준화하면 장애 시점에 브라우저 로그와 서버 로그를 빠르게 결합할 수 있습니다.

### REST API 설계 스케치

```text
GET    /api/v1/todos            목록 조회
POST   /api/v1/todos            항목 생성
PATCH  /api/v1/todos/{id}       항목 일부 수정(done 토글 등)
DELETE /api/v1/todos/{id}       항목 삭제
```

리소스 이름은 복수형으로 고정하고, 동작은 method로 분리하는 편이 유지보수에 유리합니다. 예를 들어 `/toggleTodo`처럼 동사형 엔드포인트를 늘리기 시작하면 권한 정책과 감사 로그 규칙이 빠르게 파편화됩니다.

### 세션/쿠키 정책 코드 예시

```python
from flask import Flask, session, jsonify

app = Flask(__name__)
app.secret_key = "change-me"
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

@app.get("/api/v1/me")
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(error={"code": "UNAUTHORIZED"}), 401
    return jsonify(user_id=user_id)
```

인증은 로그인 성공 시점보다 실패 시점 설계가 더 중요합니다. 어떤 경우에 401을 돌리고, 어떤 경우에 403을 돌릴지 미리 고정해 두어야 프론트엔드 재시도 정책과 알림 문구가 안정됩니다.

### SQL 기준 쿼리와 인덱스 예시

```sql
CREATE TABLE IF NOT EXISTS todo_items (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  text TEXT NOT NULL,
  done INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_todo_user_created
ON todo_items(user_id, created_at DESC);

SELECT id, text, done, created_at
FROM todo_items
WHERE user_id = ?
ORDER BY created_at DESC
LIMIT 20;
```

조회 패턴을 먼저 적고 그다음 인덱스를 정의하면 불필요한 인덱스 폭증을 피할 수 있습니다. 특히 쓰기 비중이 높은 서비스에서는 인덱스를 한 개 추가할 때마다 INSERT 비용이 늘어난다는 점을 함께 기록해야 합니다.

### 배포 설정과 헬스 체크 예시

```yaml
services:
  api:
    image: ghcr.io/example/todo-api:1.0.0
    environment:
      - APP_ENV=production
      - DATABASE_URL=postgresql://app:***@db:5432/todo
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

배포 문서에는 반드시 "성공 기준"을 남겨야 합니다. 예를 들어 `/health`가 200을 반환하고, 배포 후 15분 동안 5xx 비율이 1% 미만이며, 로그인 성공률이 평시 대비 하락하지 않는지를 체크리스트로 고정하면 릴리스 판단이 사람마다 달라지지 않습니다.

### 캐시 전략 표준 예시

```http
Cache-Control: public, max-age=31536000, immutable
```

정적 자산은 파일명에 해시를 넣고 장기 캐시를 적용하는 편이 안전합니다. 반대로 사용자별 데이터는 `private` 또는 `no-store` 정책을 명시해 캐시 오염을 방지해야 합니다. 이 구분을 코드 리뷰 항목으로 올려 두면 보안 이슈와 성능 이슈를 동시에 예방할 수 있습니다.

### 운영 체크리스트

- 요청/응답 샘플에 상태 코드, 헤더, 오류 본문 형식을 모두 기록합니다.
- 인증 실패(401), 권한 실패(403), 입력 오류(400) 경계를 API 문서에 고정합니다.
- 핵심 SQL 쿼리 3개를 선정해 `EXPLAIN` 결과를 릴리스마다 비교합니다.
- 배포 후 15분 관측 지표(5xx, p95, 로그인 성공률)를 팀 표준으로 유지합니다.
- 캐시 정책 변경 시 무효화 전략과 롤백 절차를 같은 PR에 포함합니다.

## 처음 질문으로 돌아가기

- **DOM은 정확히 무엇이며 어떻게 만들어질까요?**
  - DOM은 HTML을 브라우저가 객체 트리로 바꿔 놓은 결과물이며, 글의 예시에서는 `ul#list` 아래에 두 개의 `li`가 달린 구조로 만들어집니다. 그래서 JavaScript가 `getElementById("list")`나 `querySelectorAll("li")`로 노드를 읽고 조작할 수 있습니다.
- **브라우저 렌더링 파이프라인은 어떤 단계로 이어질까요?**
  - 브라우저는 DOM을 만든 뒤 계산된 스타일을 합쳐 render tree를 만들고, 이어서 layout으로 위치와 크기를 계산한 뒤 paint로 픽셀을 그립니다. `appendChild`처럼 DOM을 바꾸면 일부 layout과 paint가 다시 일어나므로 Performance 탭에서 재렌더링 비용을 확인할 수 있습니다.
- **JavaScript는 DOM을 어떻게 읽고 바꿀까요?**
  - JavaScript는 `createElement`, `textContent`, `appendChild` 같은 DOM API로 새 노드를 만들고 붙이며, `addEventListener`로 이벤트 위임도 처리합니다. `console.log("1")`, `setTimeout(..., 0)`, `console.log("3")` 예시처럼 비동기 콜백은 이벤트 루프를 거쳐 나중에 실행되므로 DOM 변경 시점도 그 순서 안에서 읽어야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Web Development 101 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [Web Development 101 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- **브라우저와 DOM (현재 글)**
- HTTP와 API (예정)
- Frontend와 Backend (예정)
- 인증과 세션 (예정)
- 데이터베이스 연결 (예정)
- 배포 (예정)
- 성능과 캐싱 (예정)
- 작은 웹앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Introduction to the DOM (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction)
- [Critical rendering path (MDN)](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Critical_rendering_path)
- [Event loop (MDN)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Event_loop)

### 실습 도구
- [Event delegation (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling)
- [Performance panel overview (Chrome DevTools)](https://developer.chrome.com/docs/devtools/performance)

- [web-development-101 예제 코드 저장소 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/web-development-101/ko)

Tags: Computer Science, WebDevelopment, Browser, DOM, JavaScript, Frontend
