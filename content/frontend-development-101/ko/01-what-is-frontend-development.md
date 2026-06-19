---
series: frontend-development-101
episode: 1
title: "Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/213"
    published_at: '2026-05-27'
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Frontend
  - Web
  - JavaScript
  - HTML
  - Beginner
seo_description: 프론트엔드 본질인 브라우저 환경을 이해하고 HTML, CSS, JS의 역할 분담과 DOM, SPA 같은 현대 웹의 핵심 개념을 익힙니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?

브라우저는 HTML, CSS, JavaScript 세 요소를 결합해 화면을 만듭니다. 프론트엔드를 이해한다는 것은 결국 이 세 가지가 언제, 어떻게 함께 동작하는지 이해하는 일입니다.

이 글은 Frontend Development 101 시리즈의 첫 번째 글입니다. 여기서는 프론트엔드를 단순한 UI 작업이 아니라 브라우저 안에서 실행되는 제품 계층으로 설명합니다. 핵심은 프론트엔드가 사용자가 보는 모든 것을 그리는 동시에, 사용자가 느끼는 성능과 신뢰를 직접 결정하는 실행 환경이라는 사실입니다.

프론트엔드를 처음 배우면 대개 화면을 예쁘게 만드는 일부터 떠올립니다. 물론 맞는 설명입니다. 하지만 실무에서 프론트엔드는 그보다 훨씬 넓습니다. 브라우저가 화면을 어떻게 그리는지, 사용자 입력을 어떤 흐름으로 처리하는지, 서버와 어떤 경계로 연결되는지까지 함께 이해해야 비로소 전체 그림이 잡힙니다.

![Frontend Development 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/01/01-01-diagram.ko.png)
*Frontend Development 101 1장 흐름 개요*

> 프론트엔드는 'HTML/CSS/JS를 잘 다루는 일'이기 전에 '브라우저라는 런타임 위에서 상태와 화면을 동기화하는 일'입니다 — 이 한 줄이 잡히면 jQuery·React·Vue·Svelte가 같은 문제를 다르게 푸는 답으로 보입니다.

## 이 글에서 다룰 문제

- 프론트엔드와 백엔드의 경계는 정확히 어디에서 나뉠까요?
- 브라우저는 HTML, CSS, JavaScript를 어떤 순서와 역할로 조합할까요?
- DOM, 렌더링, SPA 같은 단어는 왜 프론트엔드 입문에서 계속 등장할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

사용자가 느끼는 모든 것은 프론트엔드를 통과합니다. 백엔드가 아무리 안정적이어도 화면이 느리거나 어색하면 제품 전체가 느리다고 평가됩니다. 반대로 프론트엔드가 빠르고 자연스럽게 동작하면 사용자는 기술 구조를 의식하지 않고 제품 자체를 신뢰합니다.

그래서 프론트엔드는 제품의 첫인상과 마지막 인상을 동시에 담당합니다. 좋은 프론트엔드는 눈에 띄지 않습니다. 사용자가 "이 앱은 그냥 잘 된다"라고 느끼게 만들면 그 프론트엔드는 이미 역할을 잘 해낸 것입니다.

## 개념 한눈에 보기

브라우저는 HTML, CSS, JavaScript 세 요소를 결합해 화면을 만듭니다. 프론트엔드를 이해한다는 것은 결국 이 세 가지가 언제, 어떻게 함께 동작하는지 이해하는 일입니다.

| 용어 | 뜻 | 실무에서 왜 중요한가 |
|---|---|---|
| DOM | 브라우저가 HTML을 읽고 만든 트리 구조입니다. | 화면이 왜 그렇게 보이는지, 어떤 노드를 JavaScript가 바꾸는지 설명할 때 출발점이 됩니다. |
| 렌더링 | HTML과 CSS를 실제 픽셀로 바꿔 화면에 그리는 과정입니다. | 성능 문제를 볼 때 DOM 생성과 페인트를 구분해서 생각하게 해 줍니다. |
| 번들 | 여러 JavaScript 파일을 브라우저가 받기 쉬운 형태로 묶은 산출물입니다. | 초기 로딩 속도와 배포 결과물을 이해할 때 꼭 필요한 개념입니다. |
| SPA | 페이지 전체를 다시 로드하지 않고 JavaScript로 화면을 바꾸는 앱 구조입니다. | 라우팅, 상태 관리, 번들링 같은 뒤의 주제를 한 줄로 묶어 줍니다. |
| Hydration | 서버가 미리 그린 HTML에 JavaScript 동작을 다시 붙이는 과정입니다. | SSR 프레임워크가 왜 빠르게 보이면서도 상호작용을 유지하는지 설명해 줍니다. |

## 브라우저 렌더링 파이프라인

브라우저가 `index.html`을 받은 뒤 화면을 그리기까지의 단계를 이해하면, 성능 문제가 어느 단계에서 생기는지 설명할 수 있습니다.

```
URL 입력
  → DNS 조회 + TCP 연결
  → HTTP 요청 → HTML 수신
  → HTML 파싱 → DOM 트리 생성
  → CSS 파싱 → CSSOM 트리 생성
  → DOM + CSSOM 합성 → Render Tree
  → 레이아웃(Reflow) → 각 요소 위치·크기 계산
  → 페인트(Paint) → 픽셀로 그리기
  → 컴포지팅(Compositing) → 레이어 합성 → 화면 표시
  → JavaScript 파싱·실행 → DOM 변경 → 재렌더링
```

JavaScript가 DOM을 바꾸면 Reflow와 Repaint가 다시 일어납니다. 루프 안에서 DOM을 반복 조작하면 성능이 급격히 나빠지는 이유가 바로 이 파이프라인에 있습니다.

## 문서형 웹에서 앱형 프론트엔드로 이동한 이유

프론트엔드는 예전의 정적인 문서 페이지를 넘어, 브라우저 안에서 상태와 화면을 계속 동기화하는 실행 환경으로 확장됐습니다.

| 방식 | 화면 전환 방식 | 실무 영향 |
|---|---|---|
| 정적 문서 중심 웹 | 링크를 누를 때마다 새 HTML 문서를 다시 내려받습니다. | 구조는 단순하지만, 상호작용이 많아질수록 화면 전환 비용이 커집니다. |
| 앱형 프론트엔드 | 브라우저 안에서 상태를 바꾸며 필요한 화면 조각만 교체합니다. | 라우팅, 상태, 번들 관리가 중요해지지만 사용자 경험은 훨씬 자연스러워집니다. |

**Before (정적 웹사이트, 1995)**

```html
<!-- 각 페이지는 독립된 .html 파일 -->
<a href="/about.html">About</a>
```

**After (모던 SPA, 2025)**

```jsx
// 라우터는 한 페이지 내에서 화면을 전환합니다.
<Link to="/about">About</Link>
```

## 실습: 첫 페이지를 5단계로 만들기

### 1단계 — index.html

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>첫 프론트엔드 페이지</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <h1 id="greeting">안녕하세요</h1>
  </header>
  <main>
    <button id="change-btn" type="button">텍스트 바꾸기</button>
    <p id="counter">클릭 횟수: 0</p>
  </main>
  <script src="app.js"></script>
</body>
</html>
```

### 2단계 — style.css

```css
/* 시스템 폰트 스택으로 OS 기본 폰트 사용 */
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem 1rem;
  background: #f8fafc;
  color: #1e293b;
}

header {
  border-bottom: 2px solid #e2e8f0;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
}

button {
  padding: 0.5rem 1.25rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}

button:hover {
  background: #2563eb;
}

button:focus-visible {
  outline: 3px solid #93c5fd;
  outline-offset: 2px;
}
```

### 3단계 — app.js

```javascript
// 상태를 변수로 분리합니다.
let clickCount = 0;
const messages = ["안녕하세요", "Hello!", "안녕!", "Bonjour!"];
let messageIndex = 0;

// DOM 요소를 한 번만 가져옵니다.
const greetingEl = document.getElementById("greeting");
const counterEl  = document.getElementById("counter");
const buttonEl   = document.getElementById("change-btn");

// 상태를 화면에 반영하는 함수입니다.
function render() {
  greetingEl.textContent = messages[messageIndex];
  counterEl.textContent  = `클릭 횟수: ${clickCount}`;
}

// 이벤트가 상태를 바꾸고, render()가 화면을 갱신합니다.
buttonEl.addEventListener("click", () => {
  clickCount += 1;
  messageIndex = (messageIndex + 1) % messages.length;
  render();
});

// 초기 렌더링
render();
```

### 4단계 — 로컬 서버 실행

```bash
# Python 3 내장 서버 (설치 불필요)
python3 -m http.server 8000

# Node.js 환경이라면
npx serve .

# 브라우저에서 http://localhost:8000 접속
```

### 5단계 — DevTools로 내부 확인

`F12` → Elements 탭에서 버튼 클릭 시 `<h1>` 텍스트 노드가 바뀌는 것을 실시간으로 확인합니다.

```javascript
// Console 탭에서 직접 실행해 보세요.
console.log("DOM 상태:", document.readyState);
console.log("버튼 요소:", document.getElementById("change-btn"));
console.log("제목 텍스트:", document.getElementById("greeting").textContent);

// DOM을 직접 바꿔 봅니다.
document.getElementById("greeting").style.color = "red";
```

작은 예제지만 프론트엔드의 핵심 역할이 모두 들어 있습니다. HTML이 구조를 만들고, CSS가 모양을 입히고, JavaScript가 클릭이라는 사용자 행동에 반응합니다. 입문 단계에서 가장 중요한 습관은 결과만 보지 말고 DevTools로 브라우저 내부를 함께 보는 것입니다.

## 디버깅 시나리오: 버튼이 동작하지 않을 때

### 시나리오 1: `null` 오류가 콘솔에 찍힐 때

```javascript
// 오류 메시지 예시
// TypeError: Cannot read properties of null (reading 'addEventListener')

// 원인: script 태그가 body 닫기 전에 없거나 id가 틀렸을 때
// 확인 방법
console.log(document.getElementById("change-btn")); // null이면 문제

// 수정: HTML의 id 값과 JavaScript 선택자가 완전히 일치하는지 확인
```

### 시나리오 2: 클릭해도 화면이 안 바뀔 때

```javascript
// 디버깅 단계
buttonEl.addEventListener("click", () => {
  console.log("1. 이벤트 발생 확인");
  clickCount += 1;
  messageIndex = (messageIndex + 1) % messages.length;
  console.log("2. 상태 변경 확인:", { clickCount, messageIndex });
  render();
  console.log("3. render() 호출 완료");
});
```

### 시나리오 3: CSS가 적용되지 않을 때

```
DevTools → Network 탭 → style.css 클릭
→ Status: 200 이면 파일 로딩은 성공
→ 404 이면 파일 경로 문제 (index.html 기준 상대 경로 확인)
```

## 실무 점검 루프

아주 작은 프론트엔드 페이지도 브라우저 파이프라인 순서대로 보면 훨씬 빨리 원인을 좁힐 수 있습니다.

1. **네트워크부터 확인합니다.** DevTools Network 탭에서 `index.html`, `app.js`, CSS 파일이 모두 `200`으로 내려오는지 봅니다.
2. **DOM을 확인합니다.** Elements 패널에서 기대한 `id`가 실제로 렌더링된 노드에 붙어 있는지 확인합니다.
3. **동작을 확인합니다.** Console에서 선택자가 `null`이 아닌지 직접 확인합니다.

```javascript
// Console에서 직접 실행
console.log(document.readyState);              // "complete" 이어야 합니다
console.log(document.getElementById("change-btn")); // null이면 id 오타
console.log(document.getElementById("greeting")?.textContent); // 현재 텍스트
```

기대 결과는 단순합니다. 버튼 요소가 존재하고, 제목 텍스트를 읽을 수 있으며, 클릭 시 전체 새로고침 없이 DOM 텍스트만 바뀌어야 합니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|---|---|---|
| HTML 안에 `style=""` 직접 작성 | 유지보수 시 모든 태그를 열어야 함 | 별도 CSS 파일로 분리합니다 |
| 비즈니스 로직과 DOM 조작을 한 함수에 섞음 | 테스트와 변경 모두 어렵 | 상태 변경과 render()를 분리합니다 |
| DevTools를 거의 열지 않음 | 디버깅이 감에 의존 | Network, Elements, Console 탭을 습관적으로 확인합니다 |
| 모든 문제에 프레임워크부터 도입 | 단순한 페이지도 복잡해짐 | 순수 HTML/CSS/JS로 먼저 시도합니다 |
| 모바일을 나중 문제로 미룸 | 실제 사용자가 모바일에서 깨진 화면을 봄 | `viewport` 메타 태그와 반응형을 처음부터 적용합니다 |
| `<script>`를 `<head>` 안에 배치 | DOM이 준비되기 전에 JS 실행되어 `null` 오류 | `</body>` 직전에 배치하거나 `defer` 속성을 사용합니다 |

## 실무에서는 이렇게 보입니다

실무 팀은 대개 React, Vue, Svelte 같은 프레임워크에 TypeScript와 Vite 또는 Next.js를 조합해 사용합니다. 하지만 그 도구들 위에 놓인 기반은 여전히 HTML, CSS, JavaScript입니다. 기초를 건너뛰면 도구 이름은 외워도 문제를 설명하지 못하게 됩니다.

```
실무 팀의 일반적인 스택
├── 프레임워크: React / Vue / Svelte
├── 언어: TypeScript
├── 빌드 도구: Vite / Next.js / Nuxt
├── 스타일: Tailwind CSS / CSS Modules
├── 상태 관리: Zustand / Pinia / Redux Toolkit
└── API 통신: TanStack Query / SWR

↑ 이 모두가 HTML + CSS + JavaScript 위에 있습니다
```

처음부터 모든 도구를 한 번에 배우려 하기보다, 먼저 순수 HTML/CSS/JS로 작은 페이지를 만들어 보는 편이 훨씬 빠릅니다. 이 경험이 있어야 나중에 프레임워크가 해결하는 문제도 정확히 보입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 기초 개념은 프레임워크보다 훨씬 오래 살아남습니다.
- 사용자 경험은 결국 밀리초 단위로 평가됩니다.
- HTML과 CSS만으로 풀 수 있는 문제에 JavaScript를 먼저 들이대지 않습니다.
- 접근성은 처음부터 설계에 넣는 편이 가장 저렴합니다.
- 프론트엔드의 답은 대개 DevTools 안에 있습니다.

## 운영 체크리스트

- [ ] HTML, CSS, JavaScript의 역할을 구분할 수 있습니다.
- [ ] 로컬에서 정적 페이지를 띄울 수 있습니다.
- [ ] DevTools의 Elements, Console, Network 탭을 열어볼 수 있습니다.
- [ ] DOM이 무엇인지 설명할 수 있습니다.
- [ ] SPA를 한 문장으로 설명할 수 있습니다.
- [ ] 브라우저 렌더링 파이프라인의 주요 단계를 순서대로 말할 수 있습니다.

## 연습 문제

1. JavaScript 없이 HTML과 CSS만으로 자기소개 페이지를 만들어 보세요.
2. 버튼을 눌렀을 때 텍스트가 바뀌도록 기능을 추가해 보세요.
3. DevTools Network 탭에서 페이지를 한 번 열 때 몇 개의 파일이 내려오는지 세어 보세요.
4. Console에서 `document.querySelector("button").click()`을 실행해 이벤트를 강제로 발생시켜 보세요.

## 정리 및 다음 단계

프론트엔드는 브라우저 안에서 제품이 사용자와 만나는 계층입니다. 여기서 중요한 것은 단순히 화면을 그리는 법이 아니라, 구조와 스타일과 동작이 어떻게 함께 제품 경험을 만드는지 이해하는 일입니다.

다음 글에서는 이 계층의 가장 오래가는 기초인 HTML과 CSS를 본격적으로 봅니다.

## 처음 질문으로 돌아가기

- **프론트엔드와 백엔드의 경계는 정확히 어디에서 나뉠까요?**
  - 브라우저에서 실행되는 코드가 프론트엔드입니다. 서버에서 실행되는 코드가 백엔드입니다. HTTP 요청이 이 두 세계를 연결하는 경계선입니다.
- **브라우저는 HTML, CSS, JavaScript를 어떤 순서와 역할로 조합할까요?**
  - HTML 파싱 → DOM 생성 → CSS 적용 → 레이아웃 → 페인트 순서로 처리하고, JavaScript는 이 파이프라인 중간에 DOM을 수정할 수 있습니다.
- **DOM, 렌더링, SPA 같은 단어는 왜 프론트엔드 입문에서 계속 등장할까요?**
  - 프론트엔드가 브라우저 안에서 상태와 화면을 동기화하는 일이기 때문입니다. DOM은 그 중간 표현이고, 렌더링은 DOM을 픽셀로 바꾸는 과정이며, SPA는 이 동기화를 서버 개입 없이 하는 구조입니다.

<!-- toc:begin -->
## 시리즈 목차

- **Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가? (현재 글)**
- [Frontend Development 101 (2/10): HTML과 CSS 기본](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript 기본](./03-javascript-basics.md)
- [Frontend Development 101 (4/10): 컴포넌트와 상태](./04-components-and-state.md)
- [Frontend Development 101 (5/10): 라우팅과 페이지](./05-routing-and-pages.md)
- [Frontend Development 101 (6/10): API 호출과 비동기](./06-api-calls-and-async.md)
- [Frontend Development 101 (7/10): 폼과 유효성 검사](./07-forms-and-validation.md)
- [Frontend Development 101 (8/10): 스타일링과 디자인 시스템](./08-styling-and-design-system.md)
- [Frontend Development 101 (9/10): 빌드 도구와 번들링](./09-build-tools-and-bundling.md)
- [작은 프론트엔드 앱 만들기](./10-building-a-small-frontend-app.md)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [MDN: How browsers work](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Performance/How_browsers_work)
- [MDN: Client-side web APIs](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Client-side_web_APIs/Introduction)
- [web.dev: Learn HTML](https://web.dev/learn/html/)

### 확인용 자료
- [Chrome DevTools documentation](https://developer.chrome.com/docs/devtools/)
- [Frontend Developer Roadmap](https://roadmap.sh/frontend)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/frontend-development-101/ko)

Tags: Frontend, Web, JavaScript, HTML, Beginner
