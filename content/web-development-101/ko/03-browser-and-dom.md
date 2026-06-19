---
series: web-development-101
episode: 3
title: "Web Development 101 (3/10): 브라우저와 DOM"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/205"
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

## 이 글에서 다룰 문제

- DOM은 정확히 무엇이며 어떻게 만들어질까요?
- 브라우저 렌더링 파이프라인은 어떤 단계로 이어질까요?
- JavaScript는 DOM을 어떻게 읽고 바꿀까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 모델이 중요한가

DOM에 대한 감각이 없으면 페이지가 왜 느린지 설명하기 어렵습니다. HTML, CSS, JavaScript가 모두 정상처럼 보여도 실제 병목은 layout이나 paint에서 생길 수 있기 때문입니다. 이 과정을 알지 못하면 React, Vue 같은 프레임워크도 그저 복잡한 마법처럼 보입니다.

반대로 브라우저가 무엇을 파싱하고, 언제 레이아웃을 다시 계산하고, 어떤 시점에 비동기 콜백을 실행하는지 알고 있으면 프레임워크의 동작도 훨씬 명확해집니다.

## 브라우저 렌더링 파이프라인

```
HTML 텍스트 수신
      |
      v  파싱 (Parse)
DOM 트리
      |           CSS 파싱
      |           CSSOM 트리
      |              |
      v  결합 (Attach)
Render Tree (화면에 그려질 노드만)
      |
      v  Layout (Reflow)
각 노드의 크기와 위치 계산
      |
      v  Paint (Rasterize)
픽셀 색칠
      |
      v  Composite
GPU 레이어 합성 → 최종 화면
```

JavaScript가 DOM을 바꾸면 이 파이프라인의 일부가 다시 실행됩니다. 어느 단계부터 다시 시작하느냐에 따라 성능 비용이 달라집니다.

```
DOM 변경 종류별 비용:
- transform/opacity 변경 → Composite만 (가장 싸다)
- background-color 변경 → Paint + Composite
- width/height 변경 → Layout + Paint + Composite (가장 비싸다)
```

## 먼저 알아둘 용어

- **DOM (Document Object Model)**: HTML을 객체 트리로 표현한 구조입니다.
- **CSSOM**: CSS 규칙을 객체 트리로 표현한 구조입니다.
- **Render tree**: DOM과 계산된 스타일을 합친 렌더링용 트리입니다.
- **Reflow (Layout)**: 각 요소의 위치와 크기를 계산하는 단계입니다.
- **Repaint (Paint)**: 실제 픽셀을 그리는 단계입니다.
- **Event loop**: 비동기 작업과 콜백 실행 순서를 관리하는 큐 시스템입니다.

## DOM 트리의 구조

```html
<!doctype html>
<html>
  <body>
    <ul id="list">
      <li class="item">apple</li>
      <li class="item">pear</li>
    </ul>
  </body>
</html>
```

브라우저는 위 HTML을 읽고 아래와 같은 트리를 만듭니다:

```
Document
  └─ html
       └─ body
            └─ ul#list
                 ├─ li.item  (textNode: "apple")
                 └─ li.item  (textNode: "pear")
```

JavaScript는 이 트리를 탐색하고 수정하는 API를 제공합니다.

## DOM API로 노드 다루기

### 요소 선택

```js
// ID로 선택 (하나)
const list = document.getElementById("list");

// CSS 선택자로 선택 (하나, 첫 번째)
const firstItem = document.querySelector(".item");

// CSS 선택자로 모두 선택
const allItems = document.querySelectorAll(".item");

// 부모-자식 관계
const parent = list.parentElement;    // body
const children = list.children;      // HTMLCollection of li elements
const firstChild = list.firstElementChild;
```

### 요소 생성과 추가

```js
// 문자열 방식 (XSS 위험, 성능 비용 큼)
list.innerHTML += "<li>grape</li>";  // 전체 재파싱 발생

// DOM API 방식 (안전, 효율적)
const li = document.createElement("li");
li.textContent = "grape";        // textContent: 텍스트만 (XSS 안전)
li.className = "item";
list.appendChild(li);

// DocumentFragment로 묶어서 한 번에 추가
const fragment = document.createDocumentFragment();
["mango", "banana", "kiwi"].forEach(fruit => {
  const li = document.createElement("li");
  li.textContent = fruit;
  fragment.appendChild(li);
});
list.appendChild(fragment);  // DOM 수정 1회
```

### 속성과 스타일 수정

```js
const btn = document.querySelector("#submit-btn");

// 속성
btn.setAttribute("disabled", "");
btn.removeAttribute("disabled");
btn.getAttribute("data-id");  // → "42"

// 클래스 (CSS와 연동)
btn.classList.add("loading");
btn.classList.remove("loading");
btn.classList.toggle("active");
btn.classList.contains("active");  // → true/false

// 인라인 스타일 (최후의 수단)
btn.style.display = "none";
btn.style.backgroundColor = "red";
```

## 이벤트 처리

### 이벤트 등록과 제거

```js
function handleClick(event) {
  console.log("클릭됨:", event.target.textContent);
  event.stopPropagation();  // 이벤트 버블링 중단
  event.preventDefault();   // 기본 동작 취소
}

const btn = document.querySelector("#btn");
btn.addEventListener("click", handleClick);
btn.removeEventListener("click", handleClick);  // 동일한 함수 참조 필요
```

### 이벤트 위임 (Event Delegation)

```js
// 나쁜 예: 리스너 100개
document.querySelectorAll("li").forEach(li => {
  li.addEventListener("click", handler);  // 100개 리스너
});

// 좋은 예: 부모에 리스너 1개
const list = document.getElementById("list");
list.addEventListener("click", (event) => {
  const li = event.target.closest("li");
  if (li) {
    console.log("클릭됨:", li.textContent);
    li.classList.toggle("done");
  }
});
```

이벤트는 자식에서 부모로 bubble up합니다. 부모 하나에 리스너를 달고 `event.target`으로 실제 클릭된 요소를 읽으면 메모리와 등록 비용을 모두 줄일 수 있습니다.

## 이벤트 루프와 비동기 실행

브라우저의 이벤트 루프는 Call Stack, Web API, Callback Queue, Microtask Queue로 구성됩니다.

```js
console.log("1");                              // 동기: 즉시 실행

setTimeout(() => console.log("2"), 0);        // Macro task: 나중에 실행

Promise.resolve().then(() => console.log("3")); // Micro task: setTimeout보다 먼저

console.log("4");                              // 동기: 즉시 실행

// 출력 순서: 1 → 4 → 3 → 2
```

```
실행 순서 규칙:
1. 동기 코드 (Call Stack) 전부 실행
2. Microtask Queue 전부 비움 (Promise, queueMicrotask)
3. Macro task Queue에서 하나 꺼내 실행
4. 다시 2번으로
```

```js
// 실제 예: fetch 이후 DOM 업데이트
async function loadData() {
  console.log("로딩 시작");              // 동기

  const data = await fetch("/api/items")  // 비동기 대기
    .then(r => r.json());

  // await 이후는 microtask로 실행됨
  document.getElementById("list").textContent = JSON.stringify(data);
  console.log("화면 업데이트 완료");
}

loadData();
console.log("loadData 호출 직후");  // loadData 내부 await 전에 실행됨
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|------|------|-------------|
| 사용자 입력을 `innerHTML`에 직접 넣기 | XSS 공격 취약점 | `textContent` 사용 또는 DOMPurify로 정화 |
| 반복문 안에서 DOM 노드 하나씩 추가 | Reflow 반복 발생, 성능 저하 | `DocumentFragment`로 묶어서 한 번에 추가 |
| 모든 `<li>`에 리스너 따로 등록 | 메모리 낭비, 동적 요소 처리 불가 | 이벤트 위임으로 부모 하나에 등록 |
| `<head>` 안에 `<script>` 넣기 | DOM 준비 전 실행으로 `null` 오류 | `defer` 사용 |
| setTimeout(fn, 0)이 즉시 실행된다 생각 | 실행 순서 버그 | 이벤트 루프 이해 후 Promise 사용 |
| `offsetWidth` 읽기 후 스타일 변경 반복 | Layout Thrashing | 읽기 묶고 쓰기 묶어 순서 분리 |

## DevTools로 렌더링 분석

```
F12 → Performance 탭
1. 녹화 시작
2. 버튼 클릭 등 인터랙션 실행
3. 녹화 중지
4. Flame Chart에서 확인:
   - Parse HTML
   - Recalculate Style
   - Layout
   - Paint
   - Composite Layers
```

Layout이 반복해서 나타나면 Reflow가 많다는 신호입니다. `transform`과 `opacity`를 써서 Composite 단계만 유발하도록 바꾸면 성능이 크게 개선됩니다.

## 운영에서는 이렇게 보입니다

React와 Vue는 Virtual DOM이나 반응형 시스템을 이용해 실제 DOM 호출을 묶어서 처리합니다. 긴 리스트, 채팅 화면, 무한 스크롤처럼 화면 갱신이 많은 앱은 모두 DOM과 이벤트 루프 위에서 돌아갑니다.

## 시니어 엔지니어는 이렇게 생각합니다

- DOM 변경은 가능한 한 묶어서 처리합니다.
- 이벤트는 부모에 위임해 리스너 수를 줄입니다.
- 최적화 전에 먼저 Performance 탭으로 측정합니다.
- 긴 리스트에는 virtualization을 검토합니다.
- `transform`/`opacity`로 Layout을 건드리지 않는 애니메이션을 선호합니다.

## 운영 체크리스트

- [ ] 렌더링 파이프라인 다섯 단계를 말할 수 있습니다.
- [ ] DOM API로 요소를 만들고 붙일 수 있습니다.
- [ ] 이벤트 위임을 사용할 수 있습니다.
- [ ] 동기 코드와 비동기 콜백의 순서를 예상할 수 있습니다.
- [ ] `innerHTML`의 XSS 위험을 알고 있습니다.

## 연습 문제

1. `DocumentFragment` 없이 100개의 `<li>`를 추가하는 경우와 사용하는 경우를 비교해 보세요.
2. 부모 `<ul>` 하나에 클릭 리스너를 달고 클릭된 `<li>`의 텍스트를 출력해 보세요.
3. `console.log("a"); Promise.resolve().then(() => console.log("b")); console.log("c");`의 출력 순서를 예상해 보세요.

## 정리와 다음 글

브라우저는 DOM을 만들고, 스타일을 계산하고, 배치를 정하고, 픽셀을 그리는 기계입니다. 이 파이프라인을 이해하면 화면 성능과 프레임워크 동작이 모두 더 또렷해집니다. 다음 글에서는 클라이언트와 서버가 실제로 무엇을 주고받는지 HTTP와 API를 봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Web Development 101 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [Web Development 101 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- **Web Development 101 (3/10): 브라우저와 DOM (현재 글)**
- [Web Development 101 (4/10): HTTP와 API](./04-http-and-api.md)
- [Web Development 101 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- [Web Development 101 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- [Web Development 101 (7/10): 데이터베이스 연결](./07-connecting-to-database.md)
- [Web Development 101 (8/10): 배포](./08-deployment.md)
- [Web Development 101 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- [작은 웹앱 만들기](./10-building-a-small-web-app.md)

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
