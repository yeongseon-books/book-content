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

이 글은 Web Development 101 시리즈의 세 번째 글입니다. 여기서는 브라우저가 HTML을 DOM으로 바꾸고, 렌더링 파이프라인과 이벤트 루프를 통해 살아 있는 화면을 만드는 과정을 정리하겠습니다.

## 먼저 던지는 질문

- DOM은 정확히 무엇이며 어떻게 만들어질까요?
- 브라우저 렌더링 파이프라인은 어떤 단계로 이어질까요?
- JavaScript는 DOM을 어떻게 읽고 바꿀까요?

## 큰 그림

![Web Development 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/03/03-01-concept-at-a-glance.ko.png)

*Web Development 101 3장 흐름 개요*

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

## Before / After로 보는 DOM 조작 방식

**Before (string-style HTML)**

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

브라우저는 DOM을 만들고, 스타일을 계산하고, 배치를 정하고, 픽셀을 그리는 기계입니다. 이 파이프라인을 이해하면 화면 성능과 프레임워크 동작이 모두 더 또렷해집니다. 다음 글에서는 클라이언트와 서버가 실제로 무엇을 주고받는지 HTTP와 API를 살펴보겠습니다.

## 웹 서비스 품질을 높이는 추가 실전 예시

웹 개발에서는 기능 구현 속도만큼 프로토콜 이해와 운영 경계 관리가 중요합니다. 특히 HTTP 메시지 설계, 인증 흐름, 배포 구성은 기능이 늘어날수록 장애 확률과 직접 연결됩니다. 아래 예시는 실제 프로젝트에서 반복해서 쓰이는 기본 패턴입니다.

### HTTP 요청/응답 설계 예시

```http
POST /api/v1/orders HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer <access_token>
Idempotency-Key: 9a7d2f4a-31a2-4b11-9cd8-3e2f4dcf1b20

{
  "items": [{"sku": "A-100", "qty": 2}],
  "payment_method": "card"
}
```

```http
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/v1/orders/ord_1024

{
  "order_id": "ord_1024",
  "status": "created"
}
```

여기서 `Idempotency-Key`는 네트워크 재시도로 인한 중복 결제를 막는 핵심 장치입니다. 웹 API는 "한 번 보냈다"가 아니라 "여러 번 도착할 수 있다"를 기본 가정으로 설계해야 합니다.

### 인증 흐름: Access + Refresh 토큰 분리

```text
1) 사용자가 로그인하면 서버가 access(짧은 수명) + refresh(긴 수명)를 발급
2) 클라이언트는 access로 API 호출
3) access 만료 시 refresh로 재발급 요청
4) refresh 탈취 위험을 줄이기 위해 회전(rotation)과 폐기(revoke) 정책 적용
```

```python
# pseudo-auth-service.py
from datetime import timedelta

def issue_tokens(user_id: str) -> dict:
    return {
        "access_expires": timedelta(minutes=15),
        "refresh_expires": timedelta(days=14),
        "token_type": "Bearer",
    }
```

브라우저 환경에서는 refresh 토큰을 `HttpOnly`, `Secure`, `SameSite` 정책이 적용된 쿠키로 다루는 방식이 일반적입니다. 인증 실패 응답은 `401`과 명확한 오류 코드를 함께 제공해야 클라이언트 재시도 전략을 안정적으로 구성할 수 있습니다.

### 배포 구성: 앱/프록시/헬스체크 분리

```yaml
# docker-compose.prod.yml
services:
  web:
    image: ghcr.io/example/web:1.4.0
    env_file: .env
    ports: ["8000"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
  nginx:
    image: nginx:1.27
    ports: ["80:80", "443:443"]
    depends_on: [web]
```

헬스체크를 배포 단위에 포함하면 롤링 업데이트 중 비정상 인스턴스를 조기에 제외할 수 있습니다. 프록시 계층에서 TLS 종료와 정적 파일 캐싱을 처리하면 애플리케이션 서버는 비즈니스 로직에 더 집중할 수 있습니다.

### 운영 체크 포인트

- API마다 타임아웃, 재시도, 멱등 처리 기준을 문서화합니다.
- 인증 토큰 만료/재발급 실패 비율을 대시보드로 모니터링합니다.
- 배포 후 15분 동안 5xx 비율, p95, 로그인 성공률을 집중 관찰합니다.
- CORS 정책을 `*`로 열어두지 않고 허용 출처를 명시합니다.

웹 개발의 난이도는 화면 구현보다 경계 관리에서 더 크게 올라갑니다. HTTP 계약, 인증 수명주기, 배포 안전장치를 초기에 고정해 두면 기능 확장 시에도 장애 반경을 작게 유지할 수 있고, 팀 전체의 디버깅 속도도 안정적으로 유지됩니다.

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

## 처음 질문으로 돌아가기

- **DOM은 정확히 무엇이며 어떻게 만들어질까요?**
  - 본문의 기준은 브라우저와 DOM를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **브라우저 렌더링 파이프라인은 어떤 단계로 이어질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **JavaScript는 DOM을 어떻게 읽고 바꿀까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Computer Science, WebDevelopment, Browser, DOM, JavaScript, Frontend
