---
series: web-development-101
episode: 3
title: 브라우저와 DOM
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

# 브라우저와 DOM

브라우저는 HTML 파일을 그대로 화면에 붙이지 않습니다. 텍스트를 읽고 구조를 만들고, 스타일을 계산하고, 위치를 정하고, 픽셀을 그린 뒤에야 우리가 보는 페이지가 완성됩니다. 여기에 JavaScript의 이벤트 처리까지 얹히면 비로소 클릭 가능한 화면이 됩니다.

이 글은 Web Development 101 시리즈의 세 번째 글입니다. 여기서는 브라우저가 HTML을 DOM으로 바꾸고, 렌더링 파이프라인과 이벤트 루프를 통해 살아 있는 화면을 만드는 과정을 정리하겠습니다.

---

## 이 글에서 다룰 문제

- DOM은 정확히 무엇이며 어떻게 만들어질까요?
- 브라우저 렌더링 파이프라인은 어떤 단계로 이어질까요?
- JavaScript는 DOM을 어떻게 읽고 바꿀까요?
- 이벤트와 이벤트 루프는 화면 동작에 어떤 영향을 줄까요?
- DOM 조작이 성능 문제로 이어지는 지점은 어디일까요?

> 브라우저는 DOM 트리를 만들고 그 트리를 화면으로 그리는 기계입니다.

## 왜 이 모델이 중요한가

DOM에 대한 감각이 없으면 페이지가 왜 느린지 설명하기 어렵습니다. HTML, CSS, JavaScript가 모두 정상처럼 보여도 실제 병목은 layout이나 paint에서 생길 수 있기 때문입니다. 이 과정을 알지 못하면 React, Vue 같은 프레임워크도 그저 복잡한 마법처럼 보입니다.

반대로 브라우저가 무엇을 파싱하고, 언제 레이아웃을 다시 계산하고, 어떤 시점에 비동기 콜백을 실행하는지 알고 있으면 프레임워크의 동작도 훨씬 명확해집니다. 성능 문제를 볼 때도 추측 대신 구체적인 단계 이름으로 대화를 시작할 수 있습니다.

## 한눈에 보는 개념 지도

![한눈에 보는 개념 지도](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/03/03-01-concept-at-a-glance.ko.png)

*HTML 파싱부터 layout과 paint까지 이어지는 브라우저 렌더링 파이프라인 요약입니다.*

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

### 공식 문서
- [Introduction to the DOM (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction)
- [Critical rendering path (MDN)](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Critical_rendering_path)
- [Event loop (MDN)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Event_loop)

### 실습 도구
- [Event delegation (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling)
- [Performance panel overview (Chrome DevTools)](https://developer.chrome.com/docs/devtools/performance)

Tags: Computer Science, WebDevelopment, Browser, DOM, JavaScript, Frontend
