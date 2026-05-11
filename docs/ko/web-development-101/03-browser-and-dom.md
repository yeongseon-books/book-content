---
series: web-development-101
episode: 3
title: 브라우저와 DOM
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
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
seo_description: 브라우저는 HTML을 어떻게 트리로 만드는가 — DOM/렌더링/이벤트 루프 입문.
last_reviewed: '2026-05-04'
---

# 브라우저와 DOM

> Web Development 101 시리즈 (3/10)


## 이 글에서 다룰 문제

DOM을 이해하지 못한 채 JS를 쓰면 *왜 화면이 느린지* 영원히 모릅니다. 브라우저의 렌더링 파이프라인을 한 번만 그려두면 React/Vue 같은 도구도 *왜* 그렇게 만들어졌는지 자명해집니다.

> 브라우저는 *DOM을 그리는 기계* 입니다.

## 전체 흐름
```mermaid
flowchart LR
    HTML["HTML"] --> Parse["Parse"]
    Parse --> DOM["DOM tree"]
    CSS["CSS"] --> Style["Style calc"]
    DOM --> Layout["Layout"]
    Style --> Layout
    Layout --> Paint["Paint"]
    Paint --> Pixels["Pixels"]
```

다섯 단계 — Parse → Style → Layout → Paint → Composite.

## Before/After

**Before (문자열로 HTML 조작)**

```js
document.body.innerHTML += "<p>새 항목</p>";
```

**After (DOM API로 조작)**

```js
const p = document.createElement("p");
p.textContent = "새 항목";
document.body.appendChild(p);
```

DOM API는 *안전하고 빠릅니다* — XSS도 막아줍니다.

## DOM 다루기 5단계

### 1단계 — DOM 트리 보기

```html
<!-- index.html -->
<ul id="list">
  <li>사과</li>
  <li>배</li>
</ul>
<script src="app.js"></script>
```

### 2단계 — 요소 선택

```js
// app.js
const list = document.getElementById("list");
const items = list.querySelectorAll("li");
console.log(items.length);  // 2
```

### 3단계 — 새 요소 추가

```js
const li = document.createElement("li");
li.textContent = "포도";
list.appendChild(li);
```

### 4단계 — 이벤트 등록

```js
list.addEventListener("click", (e) => {
  if (e.target.tagName === "LI") {
    console.log("클릭:", e.target.textContent);
  }
});
```

이벤트 *위임* — 부모 하나에만 등록합니다.

### 5단계 — 비동기로 비교

```js
console.log("1");
setTimeout(() => console.log("2"), 0);
console.log("3");
// 출력: 1, 3, 2 — 이벤트 루프가 콜백을 *나중* 에 실행합니다.
```

## 이 코드에서 주목할 점

- DOM 조작은 *비싼* 연산입니다 (layout/paint 트리거).
- 이벤트 위임은 메모리와 성능을 동시에 아낍니다.
- `setTimeout(fn, 0)` 도 *즉시* 실행되지 않습니다.

## 자주 하는 실수 5가지

1. **`innerHTML` 으로 사용자 입력을 넣는다.** XSS 위험.
2. **반복 안에서 DOM에 하나씩 추가한다.** 매번 layout 발생.
3. **모든 `<li>` 에 listener를 단다.** 이벤트 위임을 모른다.
4. **JS가 *언제* 실행되는지 모른다.** `defer`/`async`/inline의 차이.
5. **DOM이 *동기* 라고 가정한다.** 비동기 콜백 순서를 헷갈린다.

## 실무에서는 이렇게 쓰입니다

React/Vue는 *Virtual DOM* 으로 실제 DOM 호출을 묶어 한 번에 처리합니다. 무한 스크롤, 채팅, 게임 — 모두 DOM과 이벤트 루프 위에서 굴러갑니다. 성능 문제가 생기면 Chrome DevTools의 *Performance* 탭으로 layout/paint를 시각화합니다.

## 체크리스트

- [ ] 렌더링 파이프라인 5단계를 말할 수 있다.
- [ ] DOM API로 요소를 만들고 추가할 수 있다.
- [ ] 이벤트 위임을 사용한다.
- [ ] 동기 vs 비동기 실행 순서를 안다.
- [ ] `innerHTML` 의 위험을 안다.

## 정리 및 다음 단계

브라우저는 *DOM을 그리는 기계* 입니다. 다음 글에서는 클라이언트와 서버를 잇는 *HTTP와 API* 를 봅니다.

<!-- toc:begin -->
- [웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [HTML, CSS, JavaScript](./02-html-css-javascript.md)
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

- [DOM (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model)
- [Critical rendering path (MDN)](https://developer.mozilla.org/en-US/docs/Web/Performance/Critical_rendering_path)
- [Event delegation (MDN)](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Building_blocks/Events#event_delegation)
- [Event loop (MDN)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Event_loop)
