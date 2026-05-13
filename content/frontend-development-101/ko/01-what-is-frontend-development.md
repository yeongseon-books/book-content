---
series: frontend-development-101
episode: 1
title: 프론트엔드 개발이란 무엇인가?
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Frontend
  - Web
  - JavaScript
  - HTML
  - Beginner
seo_description: 브라우저, 렌더링, 자바스크립트로 프론트엔드의 전체 그림을 잡습니다.
last_reviewed: '2026-05-12'
---

# 프론트엔드 개발이란 무엇인가?

이 글은 Frontend Development 101 시리즈의 첫 번째 글입니다.

프론트엔드를 처음 배우면 대개 화면을 예쁘게 만드는 일부터 떠올립니다. 물론 맞는 설명입니다. 하지만 실무에서 프론트엔드는 그보다 훨씬 넓습니다. 브라우저가 화면을 어떻게 그리는지, 사용자 입력을 어떤 흐름으로 처리하는지, 서버와 어떤 경계로 연결되는지까지 함께 이해해야 비로소 전체 그림이 잡힙니다.

이 글에서는 프론트엔드를 단순한 UI 작업이 아니라 브라우저 안에서 실행되는 제품 계층으로 설명하겠습니다. 한 가지 관점이 중요합니다. 프론트엔드는 사용자가 보는 모든 것을 그리는 동시에, 사용자가 느끼는 성능과 신뢰를 직접 결정하는 실행 환경이라는 점입니다.

## 이 글에서 다룰 문제

- 프론트엔드와 백엔드의 경계는 정확히 어디에서 나뉠까요?
- 브라우저는 HTML, CSS, JavaScript를 어떤 순서와 역할로 조합할까요?
- DOM, 렌더링, SPA 같은 단어는 왜 프론트엔드 입문에서 계속 등장할까요?
- 현대 프론트엔드 도구 체계는 어떤 문제를 해결하려고 생겼을까요?
- 처음 배우는 사람이 어떤 순서로 학습하면 가장 빠르게 감을 잡을 수 있을까요?

> 프론트엔드는 브라우저 안에서 돌아가는 작은 운영체제로 이해하면 편합니다. HTML은 구조를 정의하고, CSS는 모양을 결정하고, JavaScript는 동작을 붙입니다.

## 왜 중요한가

사용자가 느끼는 모든 것은 프론트엔드를 통과합니다. 백엔드가 아무리 안정적이어도 화면이 느리거나 어색하면 제품 전체가 느리다고 평가됩니다. 반대로 프론트엔드가 빠르고 자연스럽게 동작하면 사용자는 기술 구조를 의식하지 않고 제품 자체를 신뢰합니다.

그래서 프론트엔드는 제품의 첫인상과 마지막 인상을 동시에 담당합니다. 좋은 프론트엔드는 눈에 띄지 않습니다. 사용자가 “이 앱은 그냥 잘 된다”라고 느끼게 만들면 그 프론트엔드는 이미 역할을 잘 해낸 것입니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    User["User"] --> Browser["Browser"]
    Browser --> HTML["HTML (structure)"]
    Browser --> CSS["CSS (style)"]
    Browser --> JS["JavaScript (behavior)"]
    JS --> API["Backend API"]
```

브라우저는 HTML, CSS, JavaScript 세 요소를 결합해 화면을 만듭니다. 프론트엔드를 이해한다는 것은 결국 이 세 가지가 언제, 어떻게 함께 동작하는지 이해하는 일입니다.

## 핵심 용어

- **DOM**: 브라우저가 HTML을 읽고 만든 트리 구조입니다.
- 렌더링: HTML과 CSS를 실제 픽셀로 바꾸어 화면에 그리는 과정입니다.
- 번들: 여러 JavaScript 파일을 브라우저가 받기 쉬운 형태로 묶은 산출물입니다.
- **SPA(Single Page Application)**: 페이지를 통째로 다시 로드하지 않고 JavaScript로 화면을 바꾸는 앱 구조입니다.
- **Hydration**: 서버가 미리 그려 둔 HTML에 JavaScript 동작을 다시 붙이는 과정입니다.

## Before/After

**Before (정적 웹사이트, 1995)**

```html
<!-- Each page is its own .html file -->
<a href="/about.html">About</a>
```

**After (modern SPA, 2025)**

```javascript
// A router swaps the screen inside one page
<Link to="/about">About</Link>
```

예전 웹은 페이지 하나가 곧 문서 하나였습니다. 지금은 하나의 애플리케이션 안에서 URL과 상태에 따라 화면 조각이 바뀌는 방식이 훨씬 흔합니다. 이 차이를 이해하면 뒤에서 나올 라우팅, 상태 관리, 빌드 도구 이야기가 한 줄로 이어집니다.

## 실습: 첫 페이지를 5단계로 만들기

### 1단계 — index.html

```html
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Hi</title></head>
<body>
  <h1 id="t">Hello</h1>
  <button id="b">Click me</button>
  <script src="app.js"></script>
</body>
</html>
```

### 2단계 — style.css

```css
body { font-family: system-ui; padding: 2rem; }
button { padding: .5rem 1rem; cursor: pointer; }
```

### 3단계 — app.js

```javascript
document.getElementById("b").addEventListener("click", () => {
  document.getElementById("t").textContent = "Hello, frontend!";
});
```

### 4단계 — Local server

```bash
python3 -m http.server 8000
# Visit http://localhost:8000 in the browser
```

### 5단계 — Open DevTools

`F12`를 눌러 Elements, Console, Network 탭을 열고 브라우저가 실제로 무엇을 받았는지 확인합니다.

작은 예제지만 프론트엔드의 핵심 역할이 모두 들어 있습니다. HTML이 구조를 만들고, CSS가 모양을 입히고, JavaScript가 클릭이라는 사용자 행동에 반응합니다. 입문 단계에서 가장 중요한 습관은 결과만 보지 말고 DevTools로 브라우저 내부를 함께 보는 것입니다.

## 이 코드에서 주목할 점

- HTML은 구조, CSS는 모양, JavaScript는 동작을 담당합니다.
- 세 층이 분리되어 있어 각각 독립적으로 바꾸고 디버깅할 수 있습니다.
- DevTools는 프론트엔드에서 가장 강력한 관찰 도구입니다.

## 자주 하는 실수 5가지

1. **HTML 안에 스타일을 직접 넣습니다.** 처음엔 빨라 보여도 유지보수 난도가 급격히 올라갑니다.
2. **비즈니스 로직과 DOM 조작을 한 함수에 섞습니다.** 테스트와 변경이 모두 어려워집니다.
3. **DevTools를 거의 열지 않습니다.** 브라우저가 실제로 받은 것을 확인하지 않으면 디버깅이 반쯤 감에 의존하게 됩니다.
4. **모든 문제에 프레임워크부터 가져옵니다.** 단순한 페이지에는 순수 HTML/CSS/JS가 더 좋은 선택일 수 있습니다.
5. **모바일을 나중 문제로 미룹니다.** 실제 사용자는 이미 모바일에서 제품을 먼저 만나는 경우가 많습니다.

## 실무에서는 이렇게 보입니다

실무 팀은 대개 React, Vue, Svelte 같은 프레임워크에 TypeScript와 Vite 또는 Next.js를 조합해 사용합니다. 하지만 그 도구들 위에 놓인 기반은 여전히 HTML, CSS, JavaScript입니다. 기초를 건너뛰면 도구 이름은 외워도 문제를 설명하지 못하게 됩니다.

처음부터 모든 도구를 한 번에 배우려 하기보다, 먼저 순수 HTML/CSS/JS로 작은 페이지를 만들어 보는 편이 훨씬 빠릅니다. 이 경험이 있어야 나중에 프레임워크가 해결하는 문제도 정확히 보입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 기초 개념은 프레임워크보다 훨씬 오래 살아남습니다.
- 사용자 경험은 결국 밀리초 단위로 평가됩니다.
- HTML과 CSS만으로 풀 수 있는 문제에 JavaScript를 먼저 들이대지 않습니다.
- 접근성은 처음부터 설계에 넣는 편이 가장 저렴합니다.
- 프론트엔드의 답은 대개 DevTools 안에 있습니다.

## 체크리스트

- [ ] HTML, CSS, JavaScript의 역할을 구분할 수 있습니다.
- [ ] 로컬에서 정적 페이지를 띄울 수 있습니다.
- [ ] DevTools의 Elements, Console, Network 탭을 열어볼 수 있습니다.
- [ ] DOM이 무엇인지 설명할 수 있습니다.
- [ ] SPA를 한 문장으로 설명할 수 있습니다.

## 연습 문제

1. JavaScript 없이 HTML과 CSS만으로 자기소개 페이지를 만들어 보세요.
2. 버튼을 눌렀을 때 텍스트가 바뀌도록 기능을 추가해 보세요.
3. DevTools Network 탭에서 페이지를 한 번 열 때 몇 개의 파일이 내려오는지 세어 보세요.

## 정리 및 다음 단계

프론트엔드는 브라우저 안에서 제품이 사용자와 만나는 계층입니다. 여기서 중요한 것은 단순히 화면을 그리는 법이 아니라, 구조와 스타일과 동작이 어떻게 함께 제품 경험을 만드는지 이해하는 일입니다.

다음 글에서는 이 계층의 가장 오래가는 기초인 HTML과 CSS를 본격적으로 살펴보겠습니다.

<!-- toc:begin -->
- **프론트엔드 개발이란 무엇인가? (현재 글)**
- HTML과 CSS 기본 (예정)
- JavaScript 기본 (예정)
- 컴포넌트와 상태 (예정)
- 라우팅과 페이지 (예정)
- API 호출과 비동기 (예정)
- 폼과 유효성 검사 (예정)
- 스타일링과 디자인 시스템 (예정)
- 빌드 도구와 번들링 (예정)
- 작은 프론트엔드 앱 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [MDN Web Docs](https://developer.mozilla.org/)
- [web.dev](https://web.dev/)
- [Frontend Roadmap](https://roadmap.sh/frontend)
- [HTML Living Standard](https://html.spec.whatwg.org/)

Tags: Frontend, Web, JavaScript, HTML, Beginner
