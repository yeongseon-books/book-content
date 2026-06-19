---
series: frontend-development-101
episode: 2
title: "Frontend Development 101 (2/10): HTML과 CSS 기본"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/214"
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
  - HTML
  - CSS
  - Web
  - Beginner
seo_description: 시맨틱 HTML 구조 설계와 CSS 박스 모델, Flexbox, Grid 레이아웃 시스템을 익히고 반응형 웹과 접근성 기초를 정리합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (2/10): HTML과 CSS 기본

대부분의 프론트엔드 레이아웃 문제는 결국 이 흐름 안에 들어 있습니다. 구조를 잡고, 박스를 이해하고, 배치를 결정하고, 화면 크기에 맞춰 조정한 뒤, 접근성까지 확인하는 순서입니다.

이 글은 Frontend Development 101 시리즈의 두 번째 글입니다. 여기서는 HTML을 페이지의 뼈대로, CSS를 그 뼈대 위에 입히는 규칙으로 설명합니다. HTML은 의미를 담고 CSS는 모양을 담아야 나중의 레이아웃, 접근성, SEO가 함께 정리됩니다.

![Frontend Development 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/02/02-01-diagram.ko.png)
*Frontend Development 101 2장 흐름 개요*

> HTML은 '문서 구조'이고 CSS는 '그 구조 위에 얹는 시각 규칙'입니다 — div를 남발하면 안 되는 이유와 시맨틱 태그가 접근성·SEO·유지보수를 동시에 결정하는 이유가 모두 이 분리에서 출발합니다.

## 이 글에서 다룰 문제

- 시맨틱 HTML이 단순한 취향 문제가 아니라 기본 설계인 이유는 무엇일까요?
- 박스 모델은 CSS를 이해할 때 왜 가장 먼저 잡아야 할 개념일까요?
- Flexbox와 Grid는 각각 어떤 상황에서 더 적합할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

HTML과 CSS는 프론트엔드에서 가장 오래 살아남는 기술입니다. 프레임워크는 몇 년마다 바뀌지만, 시맨틱 태그와 박스 모델과 레이아웃 원리는 계속 남습니다.

## 개념 한눈에 보기

| 용어 | 뜻 | 실무에서 왜 중요한가 |
|---|---|---|
| 시맨틱 HTML | `<header>`, `<nav>`, `<article>`처럼 의미를 가진 태그입니다. | 검색 엔진, 스크린 리더, 동료 개발자가 문서 구조를 같은 방식으로 읽게 만듭니다. |
| 박스 모델 | 모든 요소를 content, padding, border, margin의 조합으로 보는 방식입니다. | 간격과 경계가 왜 어긋나는지 추측하지 않고 설명할 수 있게 해 줍니다. |
| Flexbox | 한 축 중심으로 배치하는 레이아웃 시스템입니다. | 메뉴, 카드 행, 정렬 같은 문제를 빠르게 풀 수 있습니다. |
| Grid | 행과 열 두 축을 함께 다루는 레이아웃 시스템입니다. | 대시보드나 카드 매트릭스처럼 구조가 뚜렷한 화면에 잘 맞습니다. |
| 미디어 쿼리 | 화면 크기나 환경에 따라 다른 스타일을 적용하는 문법입니다. | 모바일과 데스크톱을 같은 코드베이스로 자연스럽게 연결할 수 있습니다. |

## 시맨틱 HTML: 의미 있는 구조 만들기

같은 화면처럼 보여도 마크업에 의미가 있느냐 없느냐에 따라 유지보수, 접근성, SEO의 품질이 크게 갈립니다.

| 방식 | 코드 특징 | 실무 영향 |
|---|---|---|
| 의미 없는 `div` 중심 구조 | 화면 모양은 만들 수 있지만 문서 역할이 코드에 드러나지 않습니다. | 검색 엔진과 보조 기술이 구조를 추론해야 해서 품질이 흔들립니다. |
| 시맨틱 태그 중심 구조 | 구조와 역할이 태그 이름에 직접 드러납니다. | 레이아웃 변경, 접근성 보강, SEO 개선을 함께 가져가기 쉽습니다. |

**Before (의미 없는 div 더미)**

```html
<div class="header">
  <div class="nav">
    <div class="nav-item"><a href="/">홈</a></div>
    <div class="nav-item"><a href="/about">소개</a></div>
  </div>
</div>
<div class="content">
  <div class="article">
    <div class="article-title">제목</div>
    <div class="article-body">본문...</div>
  </div>
</div>
<div class="footer">푸터</div>
```

**After (시맨틱 구조)**

```html
<header>
  <nav aria-label="주요 내비게이션">
    <ul>
      <li><a href="/">홈</a></li>
      <li><a href="/about">소개</a></li>
    </ul>
  </nav>
</header>
<main>
  <article>
    <h1>제목</h1>
    <p>본문...</p>
  </article>
</main>
<footer>
  <p>© 2026 My Site</p>
</footer>
```

## 박스 모델 완전 이해

CSS에서 모든 요소는 박스입니다. 박스는 안쪽부터 content → padding → border → margin 순서로 쌓입니다.

```
┌─────────────────────────────────┐
│           margin                │
│  ┌───────────────────────────┐  │
│  │         border            │  │
│  │  ┌─────────────────────┐  │  │
│  │  │       padding       │  │  │
│  │  │  ┌───────────────┐  │  │  │
│  │  │  │    content    │  │  │  │
│  │  │  │  width×height │  │  │  │
│  │  │  └───────────────┘  │  │  │
│  │  └─────────────────────┘  │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

```css
/* 기본값: box-sizing: content-box */
/* width = content 영역만 (padding, border 별도) */
.box-default {
  width: 200px;
  padding: 20px;
  border: 2px solid black;
  /* 실제 렌더링 너비: 200 + 40 + 4 = 244px */
}

/* 권장: box-sizing: border-box */
/* width = content + padding + border 포함 */
.box-border {
  box-sizing: border-box;
  width: 200px;
  padding: 20px;
  border: 2px solid black;
  /* 실제 렌더링 너비: 200px (예측 가능) */
}

/* 모든 요소에 border-box 적용하는 실무 패턴 */
*, *::before, *::after {
  box-sizing: border-box;
}
```

## 실습: 카드 레이아웃을 5단계로 만들기

### 1단계 — Semantic structure

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>카드 레이아웃</title>
  <link rel="stylesheet" href="cards.css">
</head>
<body>
  <main>
    <article class="card">
      <img src="https://picsum.photos/300/200?1" alt="카드 이미지 1">
      <div class="card__body">
        <h2 class="card__title">첫 번째 카드</h2>
        <p class="card__text">카드 설명 텍스트가 들어갑니다.</p>
        <a href="#" class="card__link">더 보기</a>
      </div>
    </article>
    <article class="card">
      <img src="https://picsum.photos/300/200?2" alt="카드 이미지 2">
      <div class="card__body">
        <h2 class="card__title">두 번째 카드</h2>
        <p class="card__text">두 번째 카드 설명입니다.</p>
        <a href="#" class="card__link">더 보기</a>
      </div>
    </article>
    <article class="card">
      <img src="https://picsum.photos/300/200?3" alt="카드 이미지 3">
      <div class="card__body">
        <h2 class="card__title">세 번째 카드</h2>
        <p class="card__text">세 번째 카드 설명입니다.</p>
        <a href="#" class="card__link">더 보기</a>
      </div>
    </article>
  </main>
</body>
</html>
```

### 2단계 — Apply the box model

```css
/* cards.css */
*, *::before, *::after { box-sizing: border-box; }

body {
  font-family: system-ui, sans-serif;
  margin: 0;
  padding: 1rem;
  background: #f1f5f9;
}

.card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  /* 박스 모델: border-box이므로 width에 border 포함 */
}

.card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
}

.card__body {
  padding: 1.25rem;    /* 내부 여백 */
}

.card__title {
  margin: 0 0 0.5rem;  /* 아래 여백만 */
  font-size: 1.125rem;
  color: #1e293b;
}

.card__text {
  margin: 0 0 1rem;
  color: #64748b;
  line-height: 1.6;
}

.card__link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

.card__link:hover {
  text-decoration: underline;
}
```

### 3단계 — Flexbox row

```css
/* Flexbox로 카드를 한 행에 배치 */
main {
  display: flex;
  flex-wrap: wrap;  /* 넘치면 줄바꿈 */
  gap: 1.5rem;      /* 카드 사이 간격 (margin 충돌 없음) */
}

/* 각 카드가 최소 280px이지만 남은 공간 균등 분배 */
.card {
  flex: 1 1 280px;  /* grow shrink basis */
}
```

### 4단계 — Grid regions

```css
/* Grid로 더 정확한 열 제어 */
main {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

/* auto-fill: 가능한 한 많은 열 생성
   minmax(280px, 1fr): 최소 280px, 최대 남은 공간 균등 */
```

### 5단계 — Media query (모바일 우선)

```css
/* 모바일 기본: 1열 */
main {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

/* 태블릿: 2열 */
@media (min-width: 600px) {
  main {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
}

/* 데스크톱: 3열 */
@media (min-width: 900px) {
  main {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

## Flexbox vs Grid 선택 기준

두 시스템을 함께 이해하면 언제 어느 것을 써야 할지 감이 빨리 잡힙니다.

```css
/* Flexbox: 한 방향(행 또는 열) 배치가 필요할 때 */
.nav {
  display: flex;
  align-items: center;   /* 수직 중앙 정렬 */
  gap: 1rem;
  justify-content: space-between;
}

/* Grid: 행과 열 두 방향을 동시에 제어할 때 */
.dashboard {
  display: grid;
  grid-template-areas:
    "sidebar header"
    "sidebar main"
    "sidebar footer";
  grid-template-columns: 240px 1fr;
  grid-template-rows: 60px 1fr 60px;
  min-height: 100vh;
}

.header  { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main    { grid-area: main; }
.footer  { grid-area: footer; }
```

## 디버깅 시나리오: 레이아웃이 예상과 다를 때

### 시나리오 1: 카드가 한 줄에 안 들어올 때

```css
/* 원인 1: flex-wrap이 빠진 경우 */
.container {
  display: flex;
  /* flex-wrap: wrap; 빠짐 → 카드가 넘침 */
}

/* 수정 */
.container {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
```

### 시나리오 2: 간격이 두 배로 보일 때

```css
/* 원인: margin + gap이 중복 적용 */
.card {
  margin: 1rem;  /* 제거 */
}

.container {
  gap: 1rem;     /* gap만 사용 */
}
```

### 시나리오 3: 미디어 쿼리가 적용되지 않을 때

```html
<!-- viewport 메타 태그가 빠진 경우 -->
<!-- 아래 줄 없으면 모바일에서 미디어 쿼리가 제대로 동작하지 않음 -->
<meta name="viewport" content="width=device-width, initial-scale=1">
```

```css
/* 디버깅용: 모든 요소 테두리 표시 */
* { outline: 1px solid rgba(255, 0, 0, 0.3); }
```

## 실무 점검 루프

HTML/CSS 문제는 화면을 한 장의 그림처럼 볼 때보다 구조, 박스 모델, 레이아웃 규칙으로 나눠 볼 때 훨씬 빨리 풀립니다.

1. **구조를 봅니다.** Elements 패널에서 시맨틱 태그가 정말 그 콘텐츠를 감싸는지 확인합니다.
2. **간격을 봅니다.** Box Model에서 어긋난 간격이 `margin`인지 `padding`인지 구분합니다.
3. **레이아웃 모드를 봅니다.** 자식 요소를 고치기 전에 부모가 정말 `display: flex`인지 `display: grid`인지 먼저 확인합니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|---|---|---|
| 모든 것을 `<div>`로만 작성 | 검색 엔진과 스크린 리더가 구조를 모름 | 역할에 맞는 시맨틱 태그 사용 |
| `!important` 남발 | CSS 우선순위가 무너져 디버깅 불가 | 선택자 특이성을 올바르게 관리합니다 |
| 고정 `px`만 사용 | 폰트 크기 변경 시 레이아웃 깨짐 | `rem`, `%`, `fr`을 적절히 섞습니다 |
| 색만으로 정보 전달 | 색각 이상 사용자에게 정보 손실 | 아이콘, 텍스트, 패턴을 함께 사용합니다 |
| `alt` 비워두기 | 스크린 리더가 이미지 내용을 설명 못 함 | 이미지 목적을 담은 구체적인 `alt` 작성 |
| `box-sizing` 미지정 | 패딩 추가 시 레이아웃이 어긋남 | `*, *::before, *::after { box-sizing: border-box; }` 항상 추가 |

## 실무에서는 이렇게 보입니다

대부분의 팀은 Tailwind, Material UI, 자체 토큰 시스템 같은 디자인 시스템을 도입합니다. 하지만 그 시스템도 내부적으로는 시맨틱 HTML과 Flexbox/Grid 위에 서 있습니다. 기초가 약하면 디자인 시스템을 써도 디버깅이 어려워집니다.

```html
<!-- Tailwind를 써도 시맨틱 구조는 동일하게 중요합니다 -->
<header class="flex items-center justify-between px-6 py-4 bg-white shadow">
  <nav class="flex gap-4" aria-label="주요 내비게이션">
    <a href="/" class="text-blue-600 hover:text-blue-800">홈</a>
    <a href="/about" class="text-blue-600 hover:text-blue-800">소개</a>
  </nav>
</header>
<main class="max-w-6xl mx-auto px-6 py-8">
  <article class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
    <!-- 카드 컴포넌트들 -->
  </article>
</main>
```

## 시니어 엔지니어는 이렇게 생각합니다

- 시맨틱 태그는 가장 저렴한 SEO·접근성 투자입니다.
- 많은 레이아웃 문제는 Flexbox와 Grid 중 무엇을 고를지로 정리됩니다.
- 모바일 우선으로 설계하고 큰 화면으로 확장합니다.
- 색은 유일한 신호가 되면 안 됩니다.
- 습관적으로 "왜 이 요소가 div인가"를 다시 묻습니다.

## 운영 체크리스트

- [ ] `<header>`, `<main>`, `<footer>`를 적절히 사용할 수 있습니다.
- [ ] 박스 모델을 직접 그릴 수 있습니다.
- [ ] Flexbox와 Grid의 차이를 한 문장으로 설명할 수 있습니다.
- [ ] 미디어 쿼리로 반응형 레이아웃을 만들 수 있습니다.
- [ ] 모든 의미 있는 이미지에 적절한 `alt`를 작성할 수 있습니다.
- [ ] `box-sizing: border-box`를 모든 프로젝트에 기본으로 적용합니다.

## 연습 문제

1. 시맨틱 HTML과 CSS로 명함 형태의 작은 페이지를 만들어 보세요.
2. 카드 세 개를 Flexbox와 Grid로 각각 한 번씩 배치하고 차이를 정리해 보세요.
3. 600px 이하에서 한 열로 접히는 미디어 쿼리를 직접 추가해 보세요.
4. DevTools로 박스 모델 패널을 열고 padding, border, margin 값을 직접 확인해 보세요.

## 정리 및 다음 단계

HTML은 뼈대이고 CSS는 그 위에 입는 옷입니다. 두 역할이 분리되어 있어야 이후에 JavaScript가 자연스럽게 끼어들 수 있습니다.

다음 글에서는 이 구조 위에 동작을 붙이는 JavaScript 기본기를 봅니다.

## 처음 질문으로 돌아가기

- **시맨틱 HTML이 단순한 취향 문제가 아니라 기본 설계인 이유는 무엇일까요?**
  - 검색 엔진, 스크린 리더, 동료 개발자가 같은 코드로 문서 구조를 읽어야 하기 때문입니다. `<div>`만 있으면 이 세 주체 모두 구조를 직접 추론해야 합니다.
- **박스 모델은 CSS를 이해할 때 왜 가장 먼저 잡아야 할 개념일까요?**
  - 모든 CSS 레이아웃은 박스가 어떻게 공간을 차지하는지의 문제이기 때문입니다. 박스 모델이 없으면 간격 문제의 원인을 설명할 수 없습니다.
- **Flexbox와 Grid는 각각 어떤 상황에서 더 적합할까요?**
  - 내비게이션 바처럼 한 방향 배치는 Flexbox, 대시보드처럼 행열 두 방향이 동시에 필요하면 Grid가 더 자연스럽습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- **Frontend Development 101 (2/10): HTML과 CSS 기본 (현재 글)**
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
- [MDN: HTML elements reference](https://developer.mozilla.org/en-US/docs/Web/HTML/Element)
- [MDN: CSS box model](https://developer.mozilla.org/en-US/docs/Learn/CSS/Building_blocks/The_box_model)
- [MDN: Basic concepts of flexbox](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_flexible_box_layout/Basic_concepts_of_flexbox)
- [MDN: CSS grid layout](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout)

### 확인용 자료
- [web.dev: Responsive web design basics](https://web.dev/articles/responsive-web-design-basics)
- [WAI: Images and alt decisions](https://www.w3.org/WAI/tutorials/images/)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/frontend-development-101/ko)

Tags: Frontend, HTML, CSS, Web, Beginner
