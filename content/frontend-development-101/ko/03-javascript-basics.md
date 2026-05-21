---
series: frontend-development-101
episode: 3
title: "Frontend Development 101 (3/10): JavaScript 기본"
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
  - JavaScript
  - DOM
  - Web
  - Beginner
seo_description: 변수, 함수, DOM, 이벤트 중심으로 JavaScript 핵심을 정리합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (3/10): JavaScript 기본

JavaScript를 처음 배우면 문법이 끝없이 많아 보입니다. 배열 메서드도 많고 함수 표현식도 여러 가지이며 DOM API도 낯섭니다. 그래서 많은 입문자가 모든 기능을 순서대로 외우려다 오히려 속도를 잃습니다.

이 글은 Frontend Development 101 시리즈의 세 번째 글입니다. 여기서는 JavaScript를 완전한 언어 사전처럼 다루지 않고, 프론트엔드에서 가장 자주 쓰는 변수, 함수, 컬렉션 처리, DOM, 이벤트 다섯 축으로 정리합니다.

## 먼저 던지는 질문

- `let`과 `const`를 어떻게 구분해 쓰는 편이 좋을까요?
- 함수와 화살표 함수는 어떤 기준으로 읽고 작성하면 될까요?
- `map`, `filter`, `reduce`는 왜 for문보다 자주 권장될까요?

## 큰 그림

![Frontend Development 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/03/03-01-diagram.ko.png)

*Frontend Development 101 3장 흐름 개요*

## 왜 중요한가

JavaScript는 프레임워크를 바꿔도 그대로 따라옵니다. React 컴포넌트 안에서도 JavaScript를 쓰고, Vue 안에서도 JavaScript를 쓰고, Node.js에서도 같은 문법을 씁니다. 결국 이 언어에 투자한 시간은 특정 도구가 아니라 전체 생태계로 회수됩니다.

좋은 JavaScript는 거대한 함수 하나에서 나오지 않습니다. 작고 분리된 함수가 상태와 화면 변경을 예측 가능하게 연결할 때 비로소 읽기 쉬운 코드가 됩니다.

## 개념 한눈에 보기

프론트엔드의 JavaScript는 대개 이 흐름으로 전개됩니다. 값을 만들고, 함수를 정의하고, 컬렉션을 변환하고, DOM에 반영하고, 이벤트로 다시 상태를 바꿉니다.

## 핵심 용어

- **`const`**: 재할당할 수 없는 변수입니다. 기본 선택으로 두는 편이 좋습니다.
- **화살표 함수**: `() => {}` 형태의 간결한 함수 문법입니다.
- 클로저: 함수가 자신이 만들어질 당시의 환경을 기억하는 성질입니다.
- **`map/filter/reduce`**: 반복문 대신 컬렉션을 변환할 때 쓰는 표준 도구입니다.
- **이벤트 위임(event delegation)**: 자식마다 리스너를 붙이지 않고 부모에 한 번만 리스너를 두는 방식입니다.

## Before/After

**Before (var and for)**

```javascript
var arr = [1,2,3];
var doubled = [];
for (var i = 0; i < arr.length; i++) doubled.push(arr[i] * 2);
```

**After (modern JS)**

```javascript
const arr = [1, 2, 3];
const doubled = arr.map(n => n * 2);
```

현대 JavaScript는 반복과 상태 변경을 더 짧고 명확하게 표현하는 방향으로 이동했습니다. 특히 배열 메서드를 익히면 코드 길이보다 의도가 훨씬 빠르게 읽힙니다.

## 실습: 할 일 목록을 5단계로 만들기

### 1단계 — HTML skeleton

```html
<input id="todo">
<button id="add">Add</button>
<ul id="list"></ul>
```

### 2단계 — State variable

```javascript
const todos = [];
```

### 3단계 — A render function

```javascript
function render() {
  const list = document.getElementById("list");
  list.innerHTML = todos.map(t => `<li>${t}</li>`).join("");
}
```

### 4단계 — Events

```javascript
document.getElementById("add").addEventListener("click", () => {
  const input = document.getElementById("todo");
  if (!input.value) return;
  todos.push(input.value);
  input.value = "";
  render();
});
```

### 5단계 — Delete via event delegation

```javascript
document.getElementById("list").addEventListener("click", (e) => {
  if (e.target.tagName === "LI") {
    const idx = [...e.target.parentNode.children].indexOf(e.target);
    todos.splice(idx, 1);
    render();
  }
});
```

이 예제는 프레임워크 없이도 중요한 프론트엔드 사고방식을 보여 줍니다. 상태인 `todos`가 있고, 상태를 화면으로 바꾸는 `render()`가 있고, 이벤트가 상태를 바꾸면 다시 렌더링합니다. 나중에 React를 배우면 이 흐름이 왜 익숙하게 느껴지는지 바로 이해하게 됩니다.

## 검증 포인트

- Add 버튼을 눌렀을 때 목록이 새로고침 없이 늘어나고, 항목을 클릭하면 삭제되는지 확인합니다.
- DevTools Console에서 `todos` 배열이 렌더링 결과와 같은 순서로 유지되는지 확인합니다.

## 문제가 생기면 먼저 볼 것

- 버튼이 동작하지 않으면 `render()` 호출이 빠지지 않았는지, `getElementById`가 `null`을 반환하지 않는지 봅니다.
- 삭제가 꼬이면 event delegation 대상이 `LI`인지, 인덱스 계산이 현재 DOM 구조와 맞는지 확인합니다.

## 이 코드에서 주목할 점

- 상태(`todos`)와 렌더링(`render`)이 분리되어 있습니다.
- 모든 변경이 상태에서 시작해 렌더링으로 흘러갑니다.
- 자식마다 리스너를 붙이기보다 부모에 하나 두는 방식이 더 효율적일 때가 많습니다.

## 자주 하는 실수 5가지

1. **`var`를 계속 사용합니다.** 함수 스코프 특성 때문에 버그를 만들기 쉽습니다.
2. **`==`를 사용합니다.** 느슨한 형변환이 예상하지 못한 결과를 만들 수 있으니 `===`를 기본값으로 두는 편이 안전합니다.
3. **상태와 DOM을 동시에 이곳저곳에서 수정합니다.** 진실의 출처가 사라져 디버깅이 어려워집니다.
4. **모든 요소에 리스너를 개별로 붙입니다.** 메모리와 CPU를 불필요하게 더 쓰게 됩니다.
5. **`async` 내부 에러를 처리하지 않습니다.** 실패가 조용히 묻히는 버그가 생깁니다.

## 실무에서는 이렇게 보입니다

대부분의 팀은 TypeScript, ESLint, Prettier를 함께 사용합니다. JavaScript의 자유로움이 팀 단위에서는 오히려 위험이 되기 때문에 타입과 규칙으로 경계를 세웁니다. 하지만 그 모든 도구도 결국 순수 JavaScript 위에서 동작합니다.

그래서 실무에서는 화려한 문법보다 읽기 쉬운 함수 분리, 상태와 UI 책임 분리, 일관된 배열 메서드 사용이 더 중요하게 평가됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 함수는 한 가지 일을 하게 만듭니다.
- 상태와 렌더링을 분리합니다.
- 기본은 `const`, 예외적으로 `let`, `var`는 쓰지 않습니다.
- 콜백 지옥은 `async/await`로 평탄화합니다.
- JavaScript는 쓰는 시간보다 읽는 시간이 더 길다는 전제로 설계합니다.

## 체크리스트

- [ ] `let`과 `const`의 차이를 설명할 수 있습니다.
- [ ] 화살표 함수를 작성할 수 있습니다.
- [ ] `map/filter/reduce`로 반복 로직을 표현할 수 있습니다.
- [ ] DOM을 읽고 수정할 수 있습니다.
- [ ] event delegation을 한 번 직접 사용해 봤습니다.

## 연습 문제

1. 위 todo 예제에 완료 표시 기능을 추가해 보세요.
2. `localStorage`를 사용해 새로고침 후에도 todo가 남도록 만들어 보세요.
3. `map/filter/reduce`만 사용해 평균 점수를 계산하는 코드를 작성해 보세요.

## 정리 및 다음 단계

순수 JavaScript만으로도 작은 애플리케이션을 만들 수 있습니다. 다만 화면이 커질수록 상태와 렌더링을 더 체계적으로 연결해 주는 도구가 필요해집니다.

다음 글에서는 그 연결을 담당하는 컴포넌트와 상태 모델을 살펴보겠습니다.


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

- **`let`과 `const`를 어떻게 구분해 쓰는 편이 좋을까요?**
  - 본문의 기준은 JavaScript 기본를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **함수와 화살표 함수는 어떤 기준으로 읽고 작성하면 될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`map`, `filter`, `reduce`는 왜 for문보다 자주 권장될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML과 CSS 기본](./02-html-and-css-basics.md)
- **JavaScript 기본 (현재 글)**
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
- [MDN: JavaScript guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [MDN: Introduction to the DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction)
- [MDN: Event bubbling](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling)

### 확인용 자료
- [JavaScript.info](https://javascript.info/)
- [TC39 proposals](https://github.com/tc39/proposals)

Tags: Frontend, JavaScript, DOM, Web, Beginner
