---
series: web-development-101
episode: 2
title: "바이브코딩을 위한 웹 개발 기초 (2/10): HTML, CSS, JavaScript"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - 웹개발
  - HTML
  - CSS
  - JavaScript
  - 프론트엔드
seo_description: AI가 생성한 HTML, CSS, JavaScript 코드를 읽고 수정하는 데 필요한 기초를 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 웹 개발 기초 (2/10): HTML, CSS, JavaScript

이 글은 **바이브코딩을 위한 웹 개발 기초** 시리즈의 두 번째 글입니다. AI에게 웹앱을 만들어달라고 요청하기 전에, 웹이 실제로 어떻게 동작하는지 알아야 합니다.

---

AI에게 "버튼 클릭 시 색상이 바뀌는 페이지 만들어줘"라고 하면 HTML, CSS, JavaScript가 섞인 코드가 나옵니다. 이것이 어떻게 구성되어 있는지 모르면, 한 가지를 고치려다 세 가지를 망가뜨리는 일이 생깁니다. 바이브코딩의 함정이 여기에 있습니다. AI는 코드를 만들어 주지만, 그 구조를 이해하지 못하면 유지보수는 사람이 할 수 없습니다.

웹 페이지를 만드는 세 언어는 각자 담당하는 역할이 다릅니다. HTML은 "이 페이지에 무엇이 있는가"를 정하고, CSS는 "어떻게 보이는가"를 정하고, JavaScript는 "어떻게 반응하는가"를 정합니다. 이 세 가지가 같은 파일에 뒤섞이면, 나중에 색상 하나 바꾸려고 JavaScript 코드를 뒤져야 하는 상황이 생깁니다.

이 글에서는 세 언어가 각각 무엇을 맡고, 왜 분리하는 것이 중요한지, 그리고 바이브코딩 중 AI가 생성한 코드에서 이 구분이 어떻게 보이는지 정리합니다.

> HTML·CSS·JavaScript는 구조·표현·동작이라는 서로 다른 책임을 가진 세 층입니다. 바이브코딩으로 코드를 받았을 때 이 구분이 보이지 않으면, 작은 수정도 예상치 못한 곳을 건드리게 됩니다.

## 이 글에서 다룰 문제

- 웹 페이지는 왜 세 가지 언어로 나뉠까요?
- HTML, CSS, JavaScript는 각각 무엇을 책임질까요?
- 세 언어가 함께 동작할 때 어떤 연결 지점이 생길까요?
- 바이브코딩 중에 이 구분을 모르면 어떤 문제가 생길까요?
- AI가 생성한 코드에서 이 구조를 어떻게 읽을까요?

## 바이브코딩 관점: 세 언어를 구분해야 하는 이유

AI에게 "빨간 버튼에 클릭 기능 추가해줘"라고 할 때, AI는 세 파일 중 어딘가에 코드를 추가합니다. 어디에 추가했는지 이해하지 못하면 다음 요청이 어긋납니다. "파란 버튼으로 바꿔줘"라고 했을 때 JavaScript를 바꾸는 대신 CSS를 바꿔야 하는데, 이 구분이 없으면 대화가 꼬입니다.

또한 AI가 생성한 코드에 `style="color:red"`처럼 HTML 안에 CSS가 섞여 있으면, 나중에 디자인을 전체적으로 바꿀 때 HTML 파일을 전부 뒤져야 합니다. 분리된 구조를 요청하는 방법을 알면, AI가 더 유지보수하기 좋은 코드를 만들어 줍니다.

## 먼저 알아둘 용어

- **HTML**: 제목, 문단, 링크, 폼 같은 구조를 표현합니다.
- **CSS**: 색상, 폰트, 레이아웃처럼 보이는 스타일을 정의합니다.
- **JavaScript**: 클릭, 입력, 비동기 호출 같은 동작을 추가합니다.
- **Selector**: CSS가 어느 요소에 적용될지 고르는 규칙입니다.
- **Event**: 사용자 입력이나 브라우저 상태 변화를 JavaScript가 받을 수 있게 하는 신호입니다.

## Before / After: 역할 분리의 가치

**Before — 모든 것이 한 줄에**

```html
<h1 style="color:red" onclick="alert('hi')">Title</h1>
```

**After — 역할 분리**

```html
<h1 class="title">Title</h1>
```

```css
.title { color: red; }
```

```js
document.querySelector(".title").addEventListener("click", () => alert("hi"));
```

결과는 같지만 유지보수 방법이 완전히 다릅니다. 색상을 바꿀 때 HTML을 건드리지 않아도 되고, 클릭 동작을 제거할 때 CSS를 건드릴 이유가 없습니다. AI에게 "스타일만 바꿔줘"라고 할 때도 어느 파일을 봐야 하는지 명확해집니다.

## 분리된 페이지를 다섯 단계로 만들기

### 1단계 — HTML 기본 구조

```html
<!-- index.html -->
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <title>안녕</title>
    <link rel="stylesheet" href="style.css">
  </head>
  <body>
    <h1 class="title">안녕하세요</h1>
    <button id="say">인사하기</button>
    <script src="app.js" defer></script>
  </body>
</html>
```

HTML은 이 페이지에 어떤 요소가 있는지 선언합니다.

### 2단계 — CSS로 스타일 추가

```css
/* style.css */
body { font-family: system-ui; }
.title { color: steelblue; }
button { padding: 8px 16px; }
```

CSS는 구조를 바꾸지 않고 모양만 조절합니다.

### 3단계 — JavaScript로 동작 추가

```js
// app.js
document.getElementById("say").addEventListener("click", () => {
  alert("만나서 반갑습니다");
});
```

JavaScript는 사용자 입력에 반응합니다. `id`와 `class`는 HTML이 JavaScript와 CSS에 제공하는 연결 고리입니다.

### 4단계 — 브라우저에서 열기

```bash
python3 -m http.server 8000
# http://localhost:8000 열기
```

### 5단계 — DevTools에서 확인

```text
F12 → Elements 탭 → DOM 트리와 적용된 스타일 확인
```

## 바이브코딩에서 자주 나오는 실수

| 실수 | 원인 | 올바른 이해 |
|------|------|-------------|
| `style="..."` 남발 | 분리 개념 부재 | CSS 파일로 분리하면 전체 디자인 변경이 쉬워짐 |
| `<script>` 블록을 HTML에 넣음 | 편의 위주 | 별도 JS 파일로 분리해야 캐시 효율 좋음 |
| 같은 `id`를 여러 요소에 쓰음 | id 규칙 모름 | id는 문서 안에서 유일해야 함 |
| 모든 스타일 변경을 JS로 처리 | CSS 활용 부족 | CSS 클래스 토글이 더 단순하고 빠름 |
| AI 생성 코드 구조를 파악 못 함 | 개념 부재 | 세 파일이 어떻게 연결되는지 확인 필수 |

## AI 팁: 역할 분리를 요청하는 방법

AI에게 처음부터 분리된 구조를 요청하면 나중에 수정하기 훨씬 좋습니다.

```
"HTML, CSS, JavaScript를 각각 별도 파일로 분리해서 만들어줘.
HTML에는 인라인 스타일(style=...)이나 인라인 이벤트(onclick=...)를 쓰지 말고,
CSS 파일에 스타일을, JS 파일에 이벤트 처리를 넣어줘."
```

이렇게 요청하면 AI가 유지보수하기 좋은 분리된 코드를 생성합니다.

## 체크리스트

- [ ] 세 언어의 책임을 각각 한 문장으로 설명할 수 있습니다.
- [ ] inline CSS와 external CSS의 차이를 알고 있습니다.
- [ ] DevTools에서 DOM 트리와 CSS 규칙을 읽을 수 있습니다.
- [ ] `defer`와 `async`의 차이를 알고 있습니다.
- [ ] AI가 생성한 코드에서 HTML/CSS/JS의 경계를 구분할 수 있습니다.

## 처음 질문으로 돌아가기

- **웹 페이지는 왜 세 가지 언어로 나뉠까요?**
  구조, 스타일, 동작은 서로 다른 변경 이유를 가지기 때문입니다. 분리해야 한 가지를 고칠 때 다른 두 가지를 건드리지 않아도 됩니다.

- **HTML, CSS, JavaScript는 각각 무엇을 책임질까요?**
  HTML은 "무엇이 있는가", CSS는 "어떻게 보이는가", JavaScript는 "어떻게 반응하는가"를 담당합니다.

- **세 언어가 함께 동작할 때 어떤 연결 지점이 생길까요?**
  HTML의 `class`와 `id`가 CSS 셀렉터와 JavaScript의 `querySelector` 모두와 연결되는 공통 고리입니다.

## 정리

HTML, CSS, JavaScript의 역할 분리는 바이브코딩에서도 중요한 원칙입니다. AI가 만들어준 코드가 이 세 가지를 어떻게 나눴는지 파악할 수 있어야, 나중에 수정을 요청할 때도 정확하게 "CSS 파일에서 색상만 바꿔줘"처럼 말할 수 있습니다. 다음 글에서는 브라우저가 HTML을 DOM 트리로 바꾸는 과정을 봅니다.

## 참고 자료

- [HTML basics (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Your_first_website/Creating_the_content)
- [CSS basics (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Your_first_website/Styling_the_content)
- [JavaScript basics (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Your_first_website/Adding_interactivity)
- [Semantic HTML (MDN)](https://developer.mozilla.org/en-US/docs/Glossary/Semantics)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 웹 개발 기초 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- **바이브코딩을 위한 웹 개발 기초 (2/10): HTML, CSS, JavaScript (현재 글)**
- [바이브코딩을 위한 웹 개발 기초 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [바이브코딩을 위한 웹 개발 기초 (4/10): HTTP와 API](./04-http-and-api.md)
- [바이브코딩을 위한 웹 개발 기초 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- [바이브코딩을 위한 웹 개발 기초 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- [바이브코딩을 위한 웹 개발 기초 (7/10): 데이터베이스 연결](./07-connecting-to-database.md)
- [바이브코딩을 위한 웹 개발 기초 (8/10): 배포](./08-deployment.md)
- [바이브코딩을 위한 웹 개발 기초 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- [바이브코딩을 위한 웹 개발 기초 (10/10): 작은 웹앱 만들기](./10-building-a-small-web-app.md)

<!-- toc:end -->

Tags: 바이브코딩, 웹개발, HTML, CSS, JavaScript, 프론트엔드
