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

프론트엔드를 조금만 공부해도 금방 느끼는 사실이 하나 있습니다. 화면을 빨리 만드는 일과 오래 유지되는 화면을 만드는 일은 전혀 다르다는 점입니다. 전자는 아무 태그나 놓고 색을 입혀도 되지만, 후자는 구조와 의미를 분리해야 합니다.

이 글은 Frontend Development 101 시리즈의 두 번째 글입니다. 여기서는 HTML을 페이지의 뼈대로, CSS를 그 뼈대 위에 입히는 규칙으로 설명합니다. HTML은 의미를 담고 CSS는 모양을 담아야 나중의 레이아웃, 접근성, SEO가 함께 정리됩니다.

## 먼저 던지는 질문

- 시맨틱 HTML이 단순한 취향 문제가 아니라 기본 설계인 이유는 무엇일까요?
- 박스 모델은 CSS를 이해할 때 왜 가장 먼저 잡아야 할 개념일까요?
- Flexbox와 Grid는 각각 어떤 상황에서 더 적합할까요?

## 큰 그림

![Frontend Development 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/02/02-01-diagram.ko.png)

*Frontend Development 101 2장 흐름 개요*

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

## Before/After

**Before (의미 없는 div 더미)**

```html
<div class="header">
  <div class="nav">...</div>
</div>
<div class="content">...</div>
```

**After (semantic structure)**

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

다음 글에서는 이 구조 위에 동작을 붙이는 JavaScript 기본기를 살펴보겠습니다.


## 실전 구현 확장: HTML/CSS/JS, 컴포넌트, 빌드 설정

프론트엔드 글을 읽고 바로 실무에 연결하려면 이론 설명 뒤에 실행 가능한 구조를 붙여 보는 연습이 필요합니다. 핵심은 화면을 "보이는 결과"로만 다루지 않고, HTML 구조, CSS 토큰, JavaScript 상태, 컴포넌트 경계, 빌드 산출물까지 한 흐름으로 연결하는 것입니다. 이 흐름이 잡히면 기능 추가와 디버깅이 훨씬 예측 가능해집니다.

### HTML 구조를 의미 단위로 나누기

처음부터 시맨틱 태그를 사용하면 접근성과 유지보수 비용이 함께 좋아집니다.

```html
<main class="layout">
  <header class="hero">
    <h1>주문 대시보드</h1>
    <p>오늘 처리 상태를 빠르게 확인합니다.</p>
  </header>

  <section aria-labelledby="summary-title" class="card">
    <h2 id="summary-title">요약</h2>
    <ul id="summary-list"></ul>
  </section>

  <section aria-labelledby="queue-title" class="card">
    <h2 id="queue-title">대기 주문</h2>
    <div id="queue-root"></div>
  </section>
</main>
```

`div`만으로도 화면은 만들 수 있지만, `header`, `section`, `h1~h2` 계층을 쓰면 스크린 리더 탐색과 테스트 선택자가 안정됩니다. 구조가 명확하면 팀 내 협업에서도 컴포넌트 경계가 자연스럽게 정리됩니다.

### CSS를 토큰 중심으로 설계하기

디자인 시스템이 작더라도 색상, 간격, 타이포그래피 토큰을 먼저 선언하면 변경 비용을 크게 줄일 수 있습니다.

```css
:root {
  --bg: #f7f8fa;
  --surface: #ffffff;
  --text: #1f2937;
  --muted: #6b7280;
  --accent: #0f766e;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --radius-md: 12px;
}

body {
  margin: 0;
  background: linear-gradient(180deg, #eef4ff 0%, var(--bg) 35%);
  color: var(--text);
  font-family: "Noto Sans KR", sans-serif;
}

.card {
  background: var(--surface);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}
```

토큰 방식의 장점은 테마 변경, 브랜드 컬러 교체, 다크 테마 실험 시 영향 범위를 빠르게 파악할 수 있다는 점입니다. 임의 값 하드코딩이 늘어나면 작은 수정도 전체 회귀 테스트가 필요해집니다.

### JavaScript 상태 흐름을 단방향으로 유지하기

입문 단계부터 상태 갱신 규칙을 일정하게 가져가면 복잡한 프레임워크로 넘어가도 사고 비용이 낮습니다.

```javascript
const state = {
  orders: [],
  loading: false,
  error: null,
};

async function loadOrders() {
  setState({ loading: true, error: null });
  try {
    const res = await fetch("/api/orders?status=pending");
    const data = await res.json();
    setState({ orders: data.items, loading: false });
  } catch (err) {
    setState({ error: "주문 목록을 불러오지 못했습니다.", loading: false });
  }
}

function setState(patch) {
  Object.assign(state, patch);
  render();
}
```

`setState -> render` 규칙을 명시하면 상태 변경 지점을 추적하기 쉬워지고, 비동기 오류 처리도 일관되게 유지됩니다.

### 컴포넌트 패턴: Presentational vs Container

작은 프로젝트에서도 데이터 책임과 표현 책임을 분리해 두면 재사용성이 올라갑니다.

```javascript
function OrderList({ items }) {
  return `
    <ul>
      ${items.map((o) => `<li>${o.id} - ${o.customer}</li>`).join("")}
    </ul>
  `;
}

async function OrderListContainer(root) {
  root.innerHTML = "<p>불러오는 중...</p>";
  const res = await fetch("/api/orders");
  const data = await res.json();
  root.innerHTML = OrderList({ items: data.items });
}
```

- Presentational 컴포넌트는 입력 props를 받아 화면만 렌더링합니다.
- Container 컴포넌트는 데이터 조회, 예외 처리, 로딩 상태를 담당합니다.

이 분리는 테스트 단위를 명확히 만들어 줍니다. 화면 렌더링 테스트와 API 실패 테스트를 별도로 설계할 수 있기 때문입니다.

### 빌드 설정 예시: Vite 기반 최소 구성

빌드 도구는 복잡해 보이지만 기본 설정은 단순합니다. 중요한 것은 개발 서버와 운영 번들의 차이를 이해하는 것입니다.

```ts
// vite.config.ts
import { defineConfig } from "vite";

export default defineConfig({
  server: {
    port: 5173,
  },
  build: {
    sourcemap: true,
    target: "es2020",
    outDir: "dist",
  },
});
```

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "check": "npm run build && npm run test"
  }
}
```

운영 이슈를 빠르게 추적하려면 `sourcemap` 유지 전략, 캐시 무효화 파일명(hash), 환경변수 주입 규칙(`import.meta.env`)을 함께 문서화해야 합니다.

### 프런트엔드 품질을 좌우하는 검증 항목

- 접근성: 버튼/입력 요소의 label과 키보드 포커스 경로 확인
- 성능: 첫 렌더링 크기, 이미지 최적화, 코드 스플리팅 여부 확인
- 안정성: 네트워크 실패 시 로딩/오류/재시도 UI 동작 확인
- 유지보수: 컴포넌트 props 계약과 상태 변경 규칙 일관성 확인

이 항목을 PR 체크리스트로 고정하면 "기능은 동작하지만 운영 품질이 낮은 화면"을 사전에 걸러낼 수 있습니다.

### 실무 연결 포인트

프론트엔드는 더 이상 단순 화면 기술이 아닙니다. API 계약, 번들 최적화, 브라우저 성능, 접근성, 운영 관측이 모두 만나는 실행 계층입니다. 따라서 작은 예제라도 HTML/CSS/JS 코드, 컴포넌트 패턴, 빌드 설정을 한 번에 다뤄 보는 연습이 필요합니다. 이 연습을 반복하면 도구가 바뀌어도 구조를 잃지 않고, 신규 기능을 추가할 때도 안정적으로 확장할 수 있습니다.


## 처음 질문으로 돌아가기

- **시맨틱 HTML이 단순한 취향 문제가 아니라 기본 설계인 이유는 무엇일까요?**
  - 본문의 기준은 HTML과 CSS 기본를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **박스 모델은 CSS를 이해할 때 왜 가장 먼저 잡아야 할 개념일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Flexbox와 Grid는 각각 어떤 상황에서 더 적합할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Frontend, HTML, CSS, Web, Beginner
