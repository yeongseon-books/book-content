---
series: web-development-101
episode: 3
title: "바이브코딩을 위한 웹 개발 기초 (3/10): 브라우저와 DOM"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - 웹개발
  - 브라우저
  - DOM
  - JavaScript
  - 프론트엔드
seo_description: 브라우저가 HTML을 DOM으로 바꾸는 과정과 바이브코딩에서 DOM을 다루는 방법을 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 웹 개발 기초 (3/10): 브라우저와 DOM

이 글은 **바이브코딩을 위한 웹 개발 기초** 시리즈의 세 번째 글입니다. AI에게 웹앱을 만들어달라고 요청하기 전에, 웹이 실제로 어떻게 동작하는지 알아야 합니다.

---

AI에게 "목록에 항목을 동적으로 추가해줘"라고 하면 JavaScript 코드가 나옵니다. 그 코드가 실행되지 않을 때 왜 안 되는지 이해하려면, 브라우저가 HTML을 어떻게 다루는지 알아야 합니다. 브라우저는 HTML 파일을 그냥 화면에 붙이지 않습니다. 구조를 만들고, 스타일을 계산하고, 위치를 정하고, 픽셀을 그린 뒤에야 우리가 보는 페이지가 완성됩니다.

바이브코딩 중 "이 버튼이 클릭이 안 돼요", "동적으로 추가한 요소가 안 보여요"처럼 보이는 문제들이 있습니다. 이런 문제의 원인 대부분은 DOM과 이벤트 처리 타이밍에 있습니다. AI가 만들어준 JavaScript가 DOM이 완성되기 전에 실행되거나, 잘못된 방식으로 요소를 참조하는 경우입니다. 이 원리를 알면 AI에게 더 정확하게 문제를 설명할 수 있습니다.

이 글에서는 브라우저가 HTML을 DOM으로 바꾸는 과정, 렌더링 파이프라인, 이벤트 루프의 동작 원리를 정리합니다. 바이브코딩 관점에서 이 개념이 실제 문제 해결에 어떻게 연결되는지도 함께 봅니다.

> 브라우저는 HTML 텍스트를 DOM 트리로 바꾼 뒤 스타일·레이아웃·페인트·이벤트 루프를 거쳐야 클릭 가능한 화면이 됩니다. 바이브코딩 중 JavaScript가 "DOM을 찾지 못한다"는 오류는 대부분 이 순서를 모르는 데서 옵니다.

## 이 글에서 다룰 문제

- DOM은 정확히 무엇이며 어떻게 만들어질까요?
- 브라우저 렌더링 파이프라인은 어떤 단계로 이어질까요?
- JavaScript는 DOM을 어떻게 읽고 바꿀까요?
- 바이브코딩에서 DOM 관련 문제가 왜 자주 생길까요?
- 이벤트 위임이란 무엇이고 왜 중요한가요?

## 바이브코딩 관점: DOM을 알아야 하는 이유

AI가 JavaScript 코드를 생성할 때 가장 자주 쓰는 패턴이 DOM 조작입니다. `document.getElementById`, `querySelector`, `addEventListener` 같은 코드가 모두 DOM을 다루는 코드입니다. 이 코드가 왜 존재하는지, 언제 실행되는지 모르면 오류가 났을 때 대응할 수 없습니다.

특히 `<script>` 태그의 위치와 `defer` 키워드는 DOM이 완성되기 전에 JavaScript가 실행될지 여부를 결정합니다. AI가 생성한 코드에 `defer`가 없는데 `<head>` 안에 `<script>`가 있다면, DOM이 아직 만들어지기 전에 JavaScript가 실행되어 요소를 찾지 못합니다.

## 먼저 알아둘 용어

- **DOM (Document Object Model)**: HTML을 객체 트리로 표현한 구조입니다.
- **Render tree**: DOM과 계산된 스타일을 합친 렌더링용 트리입니다.
- **Layout**: 각 요소의 위치와 크기를 계산하는 단계입니다.
- **Paint**: 실제 픽셀을 그리는 단계입니다.
- **Event loop**: 비동기 작업과 콜백 실행 순서를 관리하는 큐 시스템입니다.

## Before / After: DOM 조작 방식

**Before — 문자열로 HTML 삽입**

```js
document.body.innerHTML += "<p>새 항목</p>";
// 기존 이벤트 리스너가 모두 사라지는 부작용
```

**After — DOM API 사용**

```js
const p = document.createElement("p");
p.textContent = "새 항목";
document.body.appendChild(p);
// 기존 요소에 영향 없음, XSS 위험도 낮음
```

바이브코딩으로 받은 코드에서 `innerHTML +=` 패턴이 보이면, AI에게 "DOM API를 사용해서 요소를 추가하는 방식으로 바꿔줘"라고 요청하는 편이 좋습니다.

## DOM을 다섯 단계로 다뤄 보기

### 1단계 — 트리 구조 확인

```html
<ul id="list">
  <li>사과</li>
  <li>배</li>
</ul>
<script src="app.js" defer></script>
```

`defer`를 추가해야 HTML 파싱이 끝난 뒤 JavaScript가 실행됩니다.

### 2단계 — 요소 선택

```js
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

### 4단계 — 이벤트 위임

```js
list.addEventListener("click", (e) => {
  if (e.target.tagName === "LI") {
    console.log("클릭:", e.target.textContent);
  }
});
```

부모 요소 하나에 리스너를 달고 자식 클릭을 처리하는 방식입니다. 동적으로 추가된 요소에도 작동합니다.

### 5단계 — 비동기 순서 이해

```js
console.log("1");
setTimeout(() => console.log("2"), 0);
console.log("3");
// 출력: 1, 3, 2
```

`setTimeout(fn, 0)`이라도 즉시 실행되지 않습니다. 동기 코드가 끝난 뒤 이벤트 루프가 큐에서 꺼냅니다.

## 바이브코딩에서 자주 나오는 실수

| 실수 | 원인 | 올바른 이해 |
|------|------|-------------|
| `<head>`에 `defer` 없이 `<script>` | 실행 순서 모름 | `defer` 추가 또는 `<body>` 끝으로 이동 |
| `innerHTML`에 사용자 입력 직접 삽입 | XSS 위험 | `textContent` 사용 또는 DOM API로 요소 생성 |
| 동적 추가 요소에 리스너 없음 | 이벤트 위임 모름 | 부모 요소에 이벤트 위임으로 처리 |
| `innerHTML +=` 반복 사용 | 성능 무지 | 기존 리스너 소멸, `appendChild` 사용 필요 |
| 비동기 콜백 순서 예상 실패 | 이벤트 루프 모름 | 동기 코드 먼저, 비동기는 큐에서 대기 |

## AI 팁: DOM 관련 문제 설명 방법

DOM 관련 문제가 생겼을 때 AI에게 이렇게 설명하면 더 정확한 답을 받을 수 있습니다.

```
"JavaScript에서 document.getElementById('list')가 null을 반환합니다.
<script> 태그는 <head> 안에 있고 defer가 없습니다.
DOM이 준비되기 전에 실행되는 문제인지 확인해주세요."
```

에러 메시지와 함께 스크립트 위치와 `defer` 여부를 포함하면 AI가 정확하게 진단합니다.

## 체크리스트

- [ ] DOM이 HTML에서 어떻게 만들어지는지 설명할 수 있습니다.
- [ ] `defer`가 왜 필요한지 알고 있습니다.
- [ ] DOM API로 요소를 만들고 붙일 수 있습니다.
- [ ] 이벤트 위임을 사용할 수 있습니다.
- [ ] 동기 코드와 비동기 콜백의 순서를 예상할 수 있습니다.

## 처음 질문으로 돌아가기

- **DOM은 정확히 무엇이며 어떻게 만들어질까요?**
  브라우저가 HTML 텍스트를 파싱해 만든 객체 트리입니다. JavaScript는 이 트리를 통해 페이지를 읽고 바꿉니다.

- **브라우저 렌더링 파이프라인은 어떤 단계로 이어질까요?**
  DOM 생성 → 스타일 계산 → 레이아웃 → 페인트 → 합성 순서로 이어지며, JavaScript가 DOM을 바꾸면 일부 단계가 다시 실행됩니다.

- **JavaScript는 DOM을 어떻게 읽고 바꿀까요?**
  `document.getElementById`, `querySelector` 등으로 요소를 선택하고, `createElement`, `appendChild` 등으로 구조를 바꿉니다.

## 정리

브라우저가 DOM을 만들고 화면을 그리는 과정을 이해하면, AI가 만들어준 JavaScript 코드가 "왜 이 시점에 실행되는지"가 보입니다. 특히 `defer`, 이벤트 위임, `innerHTML` 대신 DOM API 사용은 바이브코딩 중 자주 등장하는 패턴입니다. 다음 글에서는 클라이언트와 서버가 주고받는 HTTP와 API를 봅니다.

## 참고 자료

- [Introduction to the DOM (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction)
- [Critical rendering path (MDN)](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Critical_rendering_path)
- [Event loop (MDN)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Event_loop)
- [Event delegation (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 웹 개발 기초 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [바이브코딩을 위한 웹 개발 기초 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- **바이브코딩을 위한 웹 개발 기초 (3/10): 브라우저와 DOM (현재 글)**
- [바이브코딩을 위한 웹 개발 기초 (4/10): HTTP와 API](./04-http-and-api.md)
- [바이브코딩을 위한 웹 개발 기초 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- [바이브코딩을 위한 웹 개발 기초 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- [바이브코딩을 위한 웹 개발 기초 (7/10): 데이터베이스 연결](./07-connecting-to-database.md)
- [바이브코딩을 위한 웹 개발 기초 (8/10): 배포](./08-deployment.md)
- [바이브코딩을 위한 웹 개발 기초 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- [바이브코딩을 위한 웹 개발 기초 (10/10): 작은 웹앱 만들기](./10-building-a-small-web-app.md)

<!-- toc:end -->

Tags: 바이브코딩, 웹개발, 브라우저, DOM, JavaScript, 프론트엔드
