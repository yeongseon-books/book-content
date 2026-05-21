---
series: frontend-development-101
episode: 4
title: "Frontend Development 101 (4/10): 컴포넌트와 상태"
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
  - React
  - Components
  - State
  - JavaScript
seo_description: 컴포넌트, props, state로 현대 프론트엔드의 핵심 구조를 설명합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (4/10): 컴포넌트와 상태

화면이 작을 때는 JavaScript 몇 줄과 DOM 조작만으로도 충분합니다. 하지만 화면이 커지고 기능이 늘어나면 금방 한 파일에 모든 로직이 몰립니다. 그 순간부터는 코드를 실행하는 것보다 읽는 일이 더 힘들어집니다.

이 글은 Frontend Development 101 시리즈의 네 번째 글입니다. 여기서는 이 복잡도를 줄이는 가장 기본적인 모델인 컴포넌트와 상태를 설명합니다. 화면은 작은 함수 단위로 나누고, 각 함수는 자신에게 들어오는 값과 자신이 들고 있는 상태만 책임져야 구조가 오래 버팁니다.

## 먼저 던지는 질문

- 컴포넌트 사고방식은 단순히 React 문법을 넘어서 무엇을 바꿔 줄까요?
- props와 state는 어떤 기준으로 구분해야 할까요?
- 단방향 데이터 흐름은 왜 대부분의 현대 프론트엔드 프레임워크의 기본 전제일까요?

## 큰 그림

![Frontend Development 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/04/04-01-diagram.ko.png)

*Frontend Development 101 4장 흐름 개요*

## 왜 중요한가

컴포넌트 사고방식은 React에만 한정되지 않습니다. Vue, Svelte, Angular는 물론이고 순수 JavaScript로도 같은 패턴을 적용할 수 있습니다. 한 번 이 감각을 익히면 프레임워크가 달라져도 코드가 훨씬 빠르게 읽힙니다.

또 중요한 점은 컴포넌트 분리가 재사용성만을 위한 작업이 아니라는 사실입니다. 잘 쪼개진 컴포넌트는 무엇보다도 읽기 쉽습니다. 시니어 엔지니어는 “나중에 어디서 재사용할 수 있을까”보다 “지금 이 화면이 읽히는가”를 먼저 봅니다.

## 개념 한눈에 보기

상태는 위에서 아래로 흐르고, 이벤트는 아래에서 위로 올라옵니다. 이 단순한 규칙 하나만 제대로 잡아도 복잡한 화면의 절반은 정리됩니다.

## 핵심 용어

- **컴포넌트**: 화면의 한 조각을 그리는 함수입니다.
- **Props**: 부모가 자식에게 내려주는 읽기 전용 값입니다.
- **State**: 컴포넌트가 내부에 유지하는 변경 가능한 값입니다.
- **단방향 데이터 흐름**: 데이터가 위에서 아래로만 흐르는 구조입니다.
- **상태 끌어올리기(lifting state up)**: 여러 자식이 공유해야 할 상태를 부모로 옮기는 방식입니다.

## Before/After

**Before (everything in one file)**

```html
<script>
  // 1000 lines of DOM manipulation
</script>
```

**After (split into components)**

```jsx
function App()    { ... }
function Header() { ... }
function List()   { ... }
function Item()   { ... }
```

예전 방식이 화면을 못 만드는 것은 아닙니다. 문제는 성장입니다. 코드가 길어질수록 역할 경계가 흐려지고, 수정이 무서워지며, 한 줄 바꾸는 일도 전체 파일을 다시 읽어야 합니다.

## 실습: React 카운터를 5단계로 만들기

### 1단계 — Project

```bash
npm create vite@latest counter -- --template react
cd counter && npm install && npm run dev
```

### 2단계 — Define a component

```jsx
function Counter({ initial = 0 }) {
  return <button>{initial}</button>;
}
```

### 3단계 — Add state

```jsx
import { useState } from "react";

function Counter({ initial = 0 }) {
  const [count, setCount] = useState(initial);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

### 4단계 — Use it from the parent

```jsx
function App() {
  return (
    <>
      <Counter initial={0} />
      <Counter initial={10} />
    </>
  );
}
```

### 5단계 — Lift state up

```jsx
function App() {
  const [total, setTotal] = useState(0);
  return (
    <>
      <p>Total: {total}</p>
      <button onClick={() => setTotal(total + 1)}>+1</button>
    </>
  );
}
```

이 예제는 작지만 중요한 차이를 보여 줍니다. `props`는 외부에서 들어오고, `state`는 내부에서 바뀌며, 같은 컴포넌트도 여러 인스턴스로 독립 동작합니다. 그리고 여러 조각이 같은 상태를 봐야 할 때는 상태를 공통 부모로 끌어올립니다.

## 검증 포인트

- 카운터 두 개를 렌더링했을 때 각 버튼이 서로 독립적으로 증가하는지 확인합니다.
- 상태 끌어올리기 버전에서는 공통 부모가 가진 값이 화면 여러 곳에서 동시에 갱신되는지 확인합니다.

## 문제가 생기면 먼저 볼 것

- 상태가 안 바뀌면 `useState` import와 `setCount` 호출 위치를 먼저 확인합니다.
- 부모-자식 동기화가 꼬이면 상태를 어디에 두었는지, props 이름이 일치하는지 다시 봅니다.

## 이 코드에서 주목할 점

- `props`는 입력이고 `state`는 내부 기억입니다.
- 자식이 부모 상태를 바꾸려면 함수를 props로 전달받는 구조를 사용합니다.
- 같은 컴포넌트가 여러 인스턴스로 독립 동작할 수 있습니다.

## 자주 하는 실수 5가지

1. **컴포넌트 안에서 props를 직접 바꿉니다.** props는 읽기 전용이어야 합니다.
2. **모든 상태를 최상단에 몰아둡니다.** 불필요한 전역화는 성능과 가독성을 함께 해칩니다.
3. **컴포넌트가 1000줄 가까이 커지는데도 쪼개지 않습니다.** 보통 200줄 전후부터는 분리 신호를 의심해 볼 만합니다.
4. **매 렌더마다 이벤트 콜백을 무분별하게 새로 만듭니다.** 자식 리렌더링이 불필요하게 늘어날 수 있습니다.
5. **원본 상태와 파생 값을 함께 저장합니다.** 진실의 출처가 둘이 되어 버그가 생깁니다.

## 실무에서는 이렇게 보입니다

대부분의 회사는 디자인 시스템을 컴포넌트 라이브러리 형태로 운영합니다. 새로운 화면은 Button, Input, Card 같은 기본 컴포넌트를 조합해 만들어집니다. 그래서 실무에서 중요한 역량은 무엇을 만들 것인가 못지않게 무엇을 새로 만들지 않을 것인가를 판단하는 일입니다.

결국 좋은 컴포넌트 구조는 재사용보다 읽기와 변경 비용을 먼저 줄입니다. 화면이 커질수록 이 차이는 더 크게 드러납니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 컴포넌트는 작아야 하지만, 의미 있는 단위일 때만 쪼갭니다.
- 상태는 가장 가까운 공통 부모에 둡니다.
- 겉모습이 비슷하다고 바로 합치지 않습니다.
- 순환하는 데이터 흐름은 설계가 잘못됐다는 신호로 봅니다.
- 재사용성보다 가독성을 먼저 지킵니다.

## 체크리스트

- [ ] 컴포넌트를 함수로 정의할 수 있습니다.
- [ ] props와 state를 구분할 수 있습니다.
- [ ] 자식에서 부모로 이벤트를 올릴 수 있습니다.
- [ ] 상태를 적절한 위치에 둘 수 있습니다.
- [ ] 단방향 데이터 흐름을 그림으로 설명할 수 있습니다.

## 연습 문제

1. `<TodoItem>`, `<TodoList>`, `<App>`으로 나눈 todo 앱을 만들어 보세요.
2. 두 카운터가 같은 총합을 공유하도록 상태 끌어올리기를 적용해 보세요.
3. props만 받는 순수 프레젠테이션 컴포넌트를 만들고 단위 테스트를 작성해 보세요.

## 정리 및 다음 단계

컴포넌트와 상태는 화면을 조합 가능한 구조로 바꿔 줍니다. 이 관점이 잡히면 여러 화면을 연결하는 문제도 훨씬 자연스럽게 이해됩니다.

다음 글에서는 URL과 라우터를 사용해 여러 페이지를 연결하는 방법을 살펴보겠습니다.


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

- **컴포넌트 사고방식은 단순히 React 문법을 넘어서 무엇을 바꿔 줄까요?**
  - 본문의 기준은 컴포넌트와 상태를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **props와 state는 어떤 기준으로 구분해야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **단방향 데이터 흐름은 왜 대부분의 현대 프론트엔드 프레임워크의 기본 전제일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML과 CSS 기본](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript 기본](./03-javascript-basics.md)
- **컴포넌트와 상태 (현재 글)**
- 라우팅과 페이지 (예정)
- API 호출과 비동기 (예정)
- 폼과 유효성 검사 (예정)
- 스타일링과 디자인 시스템 (예정)
- 빌드 도구와 번들링 (예정)
- 작은 프론트엔드 앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [React: Thinking in React](https://react.dev/learn/thinking-in-react)
- [React: Sharing state between components](https://react.dev/learn/sharing-state-between-components)
- [Vue: Component basics](https://vuejs.org/guide/essentials/component-basics.html)

### 확인용 자료
- [Svelte tutorial](https://svelte.dev/tutorial)
- [React: State as a snapshot](https://react.dev/learn/state-as-a-snapshot)

Tags: Frontend, React, Components, State, JavaScript
