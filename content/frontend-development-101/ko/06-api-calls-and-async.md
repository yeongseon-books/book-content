---
series: frontend-development-101
episode: 6
title: API 호출과 비동기
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Frontend
  - API
  - Async
  - Fetch
  - JavaScript
seo_description: fetch, async/await, 로딩/에러 상태, 캐싱 — 프론트엔드의 비동기 데이터 흐름을 한 글로.
last_reviewed: '2026-05-04'
---

# API 호출과 비동기

> Frontend Development 101 시리즈 (6/10)


## 이 글에서 다룰 문제

비동기는 *프론트엔드 버그의 절반* 입니다. 빠른 네트워크에서는 잘 보이지 않다가, 사용자의 *느린 3G* 에서 갑자기 깨집니다. 명시적인 상태 관리가 *유일한* 해법입니다.

> 좋은 비동기 코드는 *항상 최악의 네트워크* 를 가정합니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Idle["idle"] --> Loading["loading"]
    Loading --> Success["success"]
    Loading --> Error["error"]
    Error --> Loading
```

## Before/After

**Before (콜백 지옥)**

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

## 실습: 사용자 목록 5단계

### 1단계 — 단순 fetch

```javascript
async function loadUsers() {
  const res = await fetch("/api/users");
  return res.json();
}
```

### 2단계 — React에서 사용

```jsx
function Users() {
  const [users, setUsers] = useState([]);
  useEffect(() => { loadUsers().then(setUsers); }, []);
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

### 3단계 — 로딩과 에러 상태

```jsx
function Users() {
  const [state, setState] = useState({ status: "idle" });
  useEffect(() => {
    setState({ status: "loading" });
    loadUsers()
      .then(data => setState({ status: "success", data }))
      .catch(err => setState({ status: "error", err }));
  }, []);

  if (state.status === "loading") return <p>로딩 중...</p>;
  if (state.status === "error")   return <p>에러: {state.err.message}</p>;
  return <ul>{state.data.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

### 4단계 — 취소

```jsx
useEffect(() => {
  const ctrl = new AbortController();
  fetch("/api/users", { signal: ctrl.signal })
    .then(r => r.json()).then(setUsers)
    .catch(e => e.name !== "AbortError" && console.error(e));
  return () => ctrl.abort();
}, []);
```

### 5단계 — React Query로 위 코드 압축

```jsx
import { useQuery } from "@tanstack/react-query";

function Users() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["users"],
    queryFn: loadUsers,
  });
  if (isLoading) return <p>로딩 중...</p>;
  if (error)     return <p>에러</p>;
  return <ul>{data.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

## 이 코드에서 주목할 점

- 상태가 `idle/loading/success/error` *네 가지로 명확* 합니다.
- 컴포넌트 unmount 시 요청을 *취소* 합니다.
- React Query가 캐싱, 재시도, race condition을 *모두* 해결해줍니다.

## 자주 하는 실수 5가지

1. **로딩 상태를 표시하지 않는다.** 사용자는 *앱이 죽었다* 고 생각합니다.
2. **에러를 `console.log` 만 한다.** 사용자에게는 *흰 화면* 입니다.
3. **race condition을 무시한다.** 빠른 검색 입력 시 *잘못된 결과* 가 표시됩니다.
4. **모든 컴포넌트가 *각자* fetch한다.** 같은 데이터를 N번 받습니다.
5. **캐시 무효화 전략이 없다.** 새 데이터가 들어와도 *오래된 화면* 이 보입니다.

## 실무에서는 이렇게 쓰입니다

대부분의 React 앱은 *React Query (TanStack Query)* 또는 *SWR* 을 표준으로 사용합니다. Vue는 *Pinia + composables*, Svelte는 내장 *load 함수* 가 있습니다. 손으로 fetch 상태를 관리하는 코드는 *점점 사라지고* 있습니다.

## 체크리스트

- [ ] `async/await` 로 fetch를 작성할 수 있다.
- [ ] 로딩/에러/성공 상태를 분리해서 표시한다.
- [ ] AbortController를 한 번 써봤다.
- [ ] React Query 또는 SWR을 시도해봤다.
- [ ] Slow 3G 모드에서 앱을 테스트해봤다.

## 정리 및 다음 단계

비동기는 *상태* 입니다. 다음 글에서는 *사용자 입력* 을 다루는 폼과 유효성 검사를 봅니다.

<!-- toc:begin -->
- [프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [HTML과 CSS 기본](./02-html-and-css-basics.md)
- [JavaScript 기본](./03-javascript-basics.md)
- [컴포넌트와 상태](./04-components-and-state.md)
- [라우팅과 페이지](./05-routing-and-pages.md)
- **API 호출과 비동기 (현재 글)**
- 폼과 유효성 검사 (예정)
- 스타일링과 디자인 시스템 (예정)
- 빌드 도구와 번들링 (예정)
- 작은 프론트엔드 앱 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [MDN Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [TanStack Query](https://tanstack.com/query/latest)
- [SWR docs](https://swr.vercel.app/)
- [MDN AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController)

Tags: Frontend, API, Async, Fetch, JavaScript
