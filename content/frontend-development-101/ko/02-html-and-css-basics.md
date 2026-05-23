---
series: frontend-development-101
episode: 2
title: "Frontend Development 101 (2/10): HTML과 CSS 기본"
status: publish-ready
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

이 글은 Frontend Development 101 시리즈의 두 번째 글입니다. 여기서는 HTML을 페이지의 뼈대로, CSS를 그 뼈대 위에 입히는 규칙으로 설명합니다. HTML은 의미를 담고 CSS는 모양을 담아야 나중의 레이아웃, 접근성, SEO가 함께 정리됩니다.

프론트엔드를 조금만 공부해도 금방 느끼는 사실이 하나 있습니다. 화면을 빨리 만드는 일과 오래 유지되는 화면을 만드는 일은 전혀 다르다는 점입니다. 전자는 아무 태그나 놓고 색을 입혀도 되지만, 후자는 구조와 의미를 분리해야 합니다.

![Frontend Development 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/02/02-01-diagram.ko.png)
*Frontend Development 101 2장 흐름 개요*

## 먼저 던지는 질문

- 시맨틱 HTML이 단순한 취향 문제가 아니라 기본 설계인 이유는 무엇일까요?
- 박스 모델은 CSS를 이해할 때 왜 가장 먼저 잡아야 할 개념일까요?
- Flexbox와 Grid는 각각 어떤 상황에서 더 적합할까요?

## 왜 중요한가

HTML과 CSS는 프론트엔드에서 가장 오래 살아남는 기술입니다. 프레임워크는 몇 년마다 바뀌지만, 시맨틱 태그와 박스 모델과 레이아웃 원리는 계속 남습니다. 그래서 이 구간에 들인 시간은 거의 항상 수익률이 높습니다.

특히 시맨틱 HTML은 검색 엔진과 스크린 리더가 같은 문서를 읽을 수 있게 만드는 가장 값싼 투자입니다. 화면을 비슷하게 그리는 것만으로는 부족하고, 그 구조가 무엇을 의미하는지도 코드 안에 남아 있어야 합니다.

## 개념 한눈에 보기

대부분의 프론트엔드 레이아웃 문제는 결국 이 흐름 안에 들어 있습니다. 구조를 잡고, 박스를 이해하고, 배치를 결정하고, 화면 크기에 맞춰 조정한 뒤, 접근성까지 확인하는 순서입니다.

## 핵심 용어

- **시맨틱 HTML**: `<header>`, `<nav>`, `<article>`처럼 의미를 가진 태그입니다.
- **박스 모델**: 모든 요소를 content, padding, border, margin의 조합으로 보는 방식입니다.
- **Flexbox**: 한 축 중심으로 배치하는 레이아웃 시스템입니다.
- **Grid**: 행과 열 두 축을 함께 다루는 레이아웃 시스템입니다.
- **미디어 쿼리**: 화면 크기나 환경에 따라 다른 스타일을 적용하는 문법입니다.

## 전통 방식과 현대 방식 비교

**Before (의미 없는 div 더미)**

```html
<div class="header">
  <div class="nav">...</div>
</div>
<div class="content">...</div>
```

**After (시맨틱 구조)**

```html
<header><nav>...</nav></header>
<main>...</main>
<footer>...</footer>
```

둘 다 화면은 비슷하게 만들 수 있습니다. 하지만 아래 예제처럼 시맨틱 태그를 쓰면 검색 엔진, 스크린 리더, 미래의 동료 개발자 모두가 구조를 더 쉽게 이해합니다.

## 실습: 카드 레이아웃을 5단계로 만들기

### 1단계 — Semantic structure

```html
<main>
  <article class="card">
    <h2>Title</h2>
    <p>Body</p>
  </article>
</main>
```

### 2단계 — Apply the box model

```css
.card {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 1rem;
}
```

### 3단계 — Flexbox row

```css
main {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
.card { flex: 1 1 250px; }
```

### 4단계 — Grid regions

```css
main {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}
```

### 5단계 — Media query

```css
@media (max-width: 600px) {
  main { grid-template-columns: 1fr; }
}
```

이 예제에서 중요한 것은 예쁜 카드가 아니라 레이아웃 사고방식입니다. 의미 있는 구조를 먼저 만들고, 박스 모델을 적용하고, Flexbox나 Grid로 배치하고, 마지막에 반응형 보정을 넣는 순서가 안정적입니다.

## 검증 포인트

- 브라우저 폭을 600px 아래로 줄였을 때 카드가 한 열로 접히는지 확인합니다.
- DevTools Elements 탭에서 `<main>`, `<article>` 같은 시맨틱 태그가 의도한 구조로 들어갔는지 확인합니다.

## 문제가 생기면 먼저 볼 것

- 레이아웃이 안 바뀌면 미디어 쿼리 조건과 선택자 이름이 실제 HTML과 일치하는지 확인합니다.
- 간격이 어색하면 `gap`, `padding`, `margin`이 어느 요소에 걸렸는지 박스 모델로 다시 봅니다.

## 이 코드에서 주목할 점

- `card`처럼 역할 기반 이름을 쓰고 `red`처럼 표현 중심 이름은 피하는 편이 좋습니다.
- `gap`은 margin 충돌을 줄여 레이아웃을 더 단순하게 만듭니다.
- `minmax(250px, 1fr)`는 반응형 Grid에서 매우 자주 쓰이는 기본 패턴입니다.

## 자주 하는 실수 5가지

1. **모든 것을 `<div>`로만 작성합니다.** 구조의 의미가 사라져 검색 엔진과 스크린 리더 모두 불리해집니다.
2. **`!important`를 남발합니다.** 우선순위 체계가 무너져 CSS가 금방 혼란스러워집니다.
3. **고정 `px`만 사용합니다.** `rem`, `%`, `fr`을 섞어야 반응형 흐름이 살아납니다.
4. **색만으로 정보를 전달합니다.** 색각 이상 사용자에게는 중요한 신호가 사라질 수 있습니다.
5. **이미지 alt를 비워 둡니다.** 의미 있는 이미지는 반드시 대체 텍스트가 필요합니다.

## 실무에서는 이렇게 보입니다

대부분의 팀은 Tailwind, Material UI, 자체 토큰 시스템 같은 디자인 시스템을 도입합니다. 하지만 그 시스템도 내부적으로는 시맨틱 HTML과 Flexbox/Grid 위에 서 있습니다. 기초가 약하면 디자인 시스템을 써도 디버깅이 어려워집니다.

결국 실무에서도 질문은 같습니다. 이 레이아웃이 어떤 의미 구조를 갖는가, 이 문제는 Flexbox로 풀 문제인가 Grid로 풀 문제인가, 이 화면이 모바일에서 자연스럽게 줄어드는가를 계속 묻게 됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 시맨틱 태그는 가장 저렴한 SEO·접근성 투자입니다.
- 많은 레이아웃 문제는 Flexbox와 Grid 중 무엇을 고를지로 정리됩니다.
- 모바일 우선으로 설계하고 큰 화면으로 확장합니다.
- 색은 유일한 신호가 되면 안 됩니다.
- 습관적으로 “왜 이 요소가 div인가”를 다시 묻습니다.

## 체크리스트

- [ ] `<header>`, `<main>`, `<footer>`를 적절히 사용할 수 있습니다.
- [ ] 박스 모델을 직접 그릴 수 있습니다.
- [ ] Flexbox와 Grid의 차이를 한 문장으로 설명할 수 있습니다.
- [ ] 미디어 쿼리로 반응형 레이아웃을 만들 수 있습니다.
- [ ] 모든 의미 있는 이미지에 적절한 `alt`를 작성할 수 있습니다.

## 연습 문제

1. 시맨틱 HTML과 CSS로 명함 형태의 작은 페이지를 만들어 보세요.
2. 카드 세 개를 Flexbox와 Grid로 각각 한 번씩 배치하고 차이를 정리해 보세요.
3. 600px 이하에서 한 열로 접히는 미디어 쿼리를 직접 추가해 보세요.

## 정리 및 다음 단계

HTML은 뼈대이고 CSS는 그 위에 입는 옷입니다. 두 역할이 분리되어 있어야 이후에 JavaScript가 자연스럽게 끼어들 수 있습니다.

다음 글에서는 이 구조 위에 동작을 붙이는 JavaScript 기본기를 봅니다.

## 처음 질문으로 돌아가기

- **시맨틱 HTML이 단순한 취향 문제가 아니라 기본 설계인 이유는 무엇일까요?**
  - `<header>`, `<main>`, `<article>`처럼 의미를 가진 태그를 쓰면 화면 모양뿐 아니라 문서 구조까지 코드에 남길 수 있습니다. 그래서 검색 엔진, 스크린 리더, 미래의 동료가 같은 페이지를 더 정확히 읽을 수 있고, 단순한 `<div>` 더미보다 유지보수 기준이 훨씬 선명해집니다.
- **박스 모델은 CSS를 이해할 때 왜 가장 먼저 잡아야 할 개념일까요?**
  - 카드 예제에서 `padding`, `border`, `margin`이 각각 어디에 적용되는지 이해해야 간격과 경계가 왜 그렇게 보이는지 설명할 수 있습니다. 레이아웃이 어색할 때도 먼저 박스 모델로 되돌아가면 `gap` 문제인지, 내부 여백 문제인지, 바깥 간격 문제인지 빠르게 분리할 수 있습니다.
- **Flexbox와 Grid는 각각 어떤 상황에서 더 적합할까요?**
  - 본문처럼 카드들을 한 축 기준으로 유연하게 흐르게 둘 때는 `display: flex`와 `flex-wrap`이 잘 맞습니다. 반대로 `repeat(auto-fill, minmax(250px, 1fr))`처럼 행과 열을 함께 통제해야 하는 화면에서는 Grid가 더 직접적이며, 미디어 쿼리와 결합했을 때 반응형 구조도 명확해집니다.

<!-- toc:begin -->
## 시리즈 목차

- [Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- **HTML과 CSS 기본 (현재 글)**
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
