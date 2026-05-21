---
series: frontend-development-101
episode: 6
title: "Frontend Development 101 (6/10): API 호출과 비동기"
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
  - API
  - Async
  - Fetch
  - JavaScript
seo_description: fetch와 async 흐름, 로딩과 에러 상태를 프론트엔드 관점에서 정리합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (6/10): API 호출과 비동기

프론트엔드는 거의 항상 서버와 대화합니다. 사용자 목록을 불러오고 검색 결과를 받고 저장 버튼을 누르면 데이터를 전송합니다. 문제는 이 모든 일이 즉시 끝나지 않는다는 점입니다. 네트워크는 느릴 수 있고 실패할 수 있으며 요청 순서가 뒤집힐 수도 있습니다.

이 글은 Frontend Development 101 시리즈의 여섯 번째 글입니다. 여기서는 프론트엔드의 비동기 흐름을 상태 중심으로 설명합니다. 비동기 코드는 결국 로딩, 성공, 실패라는 상태를 얼마나 명시적으로 다루느냐의 문제입니다.

## 먼저 던지는 질문

- `fetch`와 `async/await`는 어떤 최소 패턴으로 시작하면 될까요?
- 로딩 상태와 에러 상태를 왜 반드시 화면에 드러내야 할까요?
- 컴포넌트가 사라질 때 요청 취소가 왜 필요할까요?

## 큰 그림

![Frontend Development 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/06/06-01-diagram.ko.png)

*Frontend Development 101 6장 흐름 개요*

## 왜 중요한가

프론트엔드 버그의 큰 비중은 비동기 처리에서 나옵니다. 빠른 사내 와이파이에서는 잘 보이지 않다가 실제 사용자의 느린 네트워크에서만 터지는 경우가 많습니다. 그래서 비동기 로직은 낙관보다 명시적 상태 관리가 더 중요합니다.

좋은 비동기 코드는 최선의 네트워크가 아니라 최악의 네트워크를 기준으로 설계합니다. 느릴 때 무엇을 보여 줄지, 실패했을 때 어디까지 복구할지, 오래된 응답이 늦게 도착하면 어떻게 무시할지를 미리 정해야 합니다.

## 개념 한눈에 보기

이 네 가지 상태를 그려 놓고 시작하면 비동기 UI 설계가 훨씬 선명해집니다. 로딩 전, 로딩 중, 성공, 실패를 모두 다른 화면 상태로 다뤄야 합니다.

## 핵심 용어

- **`fetch`**: 브라우저에 기본 내장된 HTTP 클라이언트입니다.
- **Promise**: 미래에 도착할 값을 표현하는 객체입니다.
- **`async/await`**: Promise를 동기 코드처럼 읽게 해 주는 문법입니다.
- **AbortController**: 진행 중인 요청을 취소하는 도구입니다.
- **Stale-while-revalidate**: 캐시된 데이터를 먼저 보여 주고 뒤에서 새로 고치는 전략입니다.

## Before/After

**Before (callback hell)**

```javascript
fetch(url, (res) => {
  parse(res, (data) => {
    render(data, (e) => { ... });
  });
});
```

**After (async/await)**

```javascript
const res = await fetch(url);
const data = await res.json();
render(data);
```

문법이 단순해진 것만이 핵심은 아닙니다. `async/await`를 쓰면 흐름을 위에서 아래로 읽을 수 있어 예외 처리와 상태 분기가 훨씬 명확해집니다.

## 실습: 사용자 목록을 5단계로 만들기

### 1단계 — Plain fetch

```javascript
async function loadUsers() {
  const res = await fetch("/api/users");
  return res.json();
}
```

### 2단계 — Use it from React

```jsx
function Users() {
  const [users, setUsers] = useState([]);
  useEffect(() => { loadUsers().then(setUsers); }, []);
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

### 3단계 — Loading and error states

```jsx
function Users() {
  const [state, setState] = useState({ status: "idle" });
  useEffect(() => {
    setState({ status: "loading" });
    loadUsers()
      .then(data => setState({ status: "success", data }))
      .catch(err => setState({ status: "error", err }));
  }, []);

  if (state.status === "loading") return <p>Loading...</p>;
  if (state.status === "error")   return <p>Error: {state.err.message}</p>;
  return <ul>{state.data.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

### 4단계 — Cancel on unmount

```jsx
useEffect(() => {
  const ctrl = new AbortController();
  fetch("/api/users", { signal: ctrl.signal })
    .then(r => r.json()).then(setUsers)
    .catch(e => e.name !== "AbortError" && console.error(e));
  return () => ctrl.abort();
}, []);
```

### 5단계 — Compress all of it with React Query

```jsx
import { useQuery } from "@tanstack/react-query";

function Users() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["users"],
    queryFn: loadUsers,
  });
  if (isLoading) return <p>Loading...</p>;
  if (error)     return <p>Error</p>;
  return <ul>{data.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

실무에서 중요한 포인트는 3단계와 4단계입니다. 데이터를 받아오는 코드 자체보다 로딩과 실패를 어떻게 보여 주는지, 그리고 컴포넌트가 사라질 때 오래된 요청이 남지 않게 처리하는지가 안정성을 좌우합니다.

## 검증 포인트

- 정상 API에서는 로딩 메시지 뒤에 목록이 나오고, 잘못된 엔드포인트에서는 사용자에게 에러가 보이는지 확인합니다.
- Slow 3G로 바꾼 뒤에도 로딩 상태가 비어 있지 않고, 화면 이동 시 오래된 요청이 정리되는지 확인합니다.

## 문제가 생기면 먼저 볼 것

- 에러가 화면에 안 보이면 `res.ok` 검사와 `catch` 분기가 실제 렌더링으로 이어지는지 확인합니다.
- 이전 응답이 덮어쓰면 `AbortController` cleanup이나 최신 요청만 반영하는 분기가 있는지 봅니다.

## 이 코드에서 주목할 점

- 상태가 `idle/loading/success/error`로 명확히 드러납니다.
- 컴포넌트가 unmount될 때 요청을 취소합니다.
- React Query는 캐싱, 재시도, race condition 대응까지 한 번에 맡아줍니다.

## 자주 하는 실수 5가지

1. **로딩 상태를 생략합니다.** 사용자는 앱이 멈췄다고 느낍니다.
2. **에러를 콘솔에만 남깁니다.** 사용자 입장에서는 이유 없는 빈 화면만 보게 됩니다.
3. **race condition을 무시합니다.** 빠르게 입력한 검색에서 오래된 결과가 마지막에 덮어쓸 수 있습니다.
4. **같은 데이터를 여러 컴포넌트가 각각 다시 불러옵니다.** 한 리소스를 여러 번 중복 요청하게 됩니다.
5. **캐시 무효화 전략이 없습니다.** 새 데이터가 있어도 오래된 화면이 계속 남습니다.

## 실무에서는 이렇게 보입니다

현대 React 앱은 대부분 TanStack Query나 SWR을 표준처럼 사용합니다. Vue는 composable과 상태 관리 조합을 쓰고, Svelte는 내장 load 함수로 이 문제를 단순화합니다. 손으로 일일이 fetch 상태를 관리하는 코드는 학습 단계 이후 점점 줄어드는 편입니다.

그렇더라도 기본 원리는 사라지지 않습니다. 도구를 쓰든 직접 쓰든 비동기 UI는 상태 기계로 이해해야 합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 비동기는 상태 기계이므로 상태 전이를 먼저 그립니다.
- 모든 fetch는 취소 가능해야 한다고 가정합니다.
- 캐싱을 기본값으로 두고 실시간 갱신을 예외로 다룹니다.
- 사용자에게 보이는 에러는 친절하고 행동 가능해야 합니다.
- 가끔은 DevTools의 Slow 3G로 실제 체감을 확인합니다.

## 체크리스트

- [ ] `fetch`를 `async/await`와 함께 작성할 수 있습니다.
- [ ] 로딩, 에러, 성공 상태를 각각 따로 렌더링할 수 있습니다.
- [ ] `AbortController`를 한 번 사용해 봤습니다.
- [ ] React Query나 SWR을 직접 써 봤습니다.
- [ ] Slow 3G 환경에서 동작을 점검해 봤습니다.

## 연습 문제

1. `https://jsonplaceholder.typicode.com/users`를 호출해 사용자 목록을 렌더링해 보세요.
2. 로딩 상태와 에러 상태를 명시적으로 추가해 보세요.
3. 검색 입력창을 붙이고, 빠르게 입력해도 가장 최근 입력 결과만 보이도록 race condition을 제어해 보세요.

## 정리 및 다음 단계

비동기는 결국 상태입니다. 이 관점이 잡히면 이제 사용자 입력을 받는 폼도 같은 방식으로 더 명확하게 읽을 수 있습니다.

다음 글에서는 폼과 유효성 검사를 통해 사용자 입력을 안전하고 친절하게 다루는 방법을 살펴보겠습니다.


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

- **`fetch`와 `async/await`는 어떤 최소 패턴으로 시작하면 될까요?**
  - 본문의 기준은 API 호출과 비동기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **로딩 상태와 에러 상태를 왜 반드시 화면에 드러내야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **컴포넌트가 사라질 때 요청 취소가 왜 필요할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML과 CSS 기본](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript 기본](./03-javascript-basics.md)
- [Frontend Development 101 (4/10): 컴포넌트와 상태](./04-components-and-state.md)
- [Frontend Development 101 (5/10): 라우팅과 페이지](./05-routing-and-pages.md)
- **API 호출과 비동기 (현재 글)**
- 폼과 유효성 검사 (예정)
- 스타일링과 디자인 시스템 (예정)
- 빌드 도구와 번들링 (예정)
- 작은 프론트엔드 앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [MDN: Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [MDN: AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController)
- [TanStack Query docs](https://tanstack.com/query/latest)

### 확인용 자료
- [SWR documentation](https://swr.vercel.app/)
- [web.dev: Fetch API error handling](https://web.dev/articles/fetch-api-error-handling)

Tags: Frontend, API, Async, Fetch, JavaScript
