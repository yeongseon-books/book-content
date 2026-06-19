---
series: frontend-development-101
episode: 6
title: "Frontend Development 101 (6/10): API 호출과 비동기"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/218"
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
  - API
  - Async
  - Fetch
  - JavaScript
seo_description: fetch와 async 흐름, 로딩과 에러 상태를 프론트엔드 관점에서 정리합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (6/10): API 호출과 비동기

이 네 가지 상태를 그려 놓고 시작하면 비동기 UI 설계가 훨씬 선명해집니다. 로딩 전, 로딩 중, 성공, 실패를 모두 다른 화면 상태로 다뤄야 합니다.

이 글은 Frontend Development 101 시리즈의 여섯 번째 글입니다. 여기서는 프론트엔드의 비동기 흐름을 상태 중심으로 설명합니다. 비동기 코드는 결국 로딩, 성공, 실패라는 상태를 얼마나 명시적으로 다루느냐의 문제입니다.

![Frontend Development 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/06/06-01-diagram.ko.png)
*Frontend Development 101 6장 흐름 개요*

> 프론트의 비동기 코드는 거의 항상 세 가지 상태를 동시에 관리합니다 — loading / data / error. 이 셋을 명시적으로 모델링하지 않으면 'fetch 한 번 했는데 UI가 깜빡거리는 / 실패가 안 보이는' 버그가 끝없이 재생산됩니다.

## 이 글에서 다룰 문제

- `fetch`와 `async/await`는 어떤 최소 패턴으로 시작하면 될까요?
- 로딩 상태와 에러 상태를 왜 반드시 화면에 드러내야 할까요?
- 컴포넌트가 사라질 때 요청 취소가 왜 필요할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 개념 한눈에 보기

| 용어 | 뜻 | 실무에서 왜 중요한가 |
|---|---|---|
| `fetch` | 브라우저에 기본 내장된 HTTP 클라이언트입니다. | 프론트엔드가 서버와 대화하는 최소 단위가 됩니다. |
| Promise | 미래에 도착할 값을 표현하는 객체입니다. | 비동기 흐름이 어느 시점에 완료되는지 모델링하게 해 줍니다. |
| `async/await` | Promise를 동기 코드처럼 읽게 해 주는 문법입니다. | 로딩, 성공, 실패 경로를 위에서 아래로 읽기 쉽게 만듭니다. |
| AbortController | 진행 중인 요청을 취소하는 도구입니다. | 화면 전환이나 빠른 입력에서 오래된 요청이 덮어쓰는 문제를 막습니다. |
| Stale-while-revalidate | 캐시된 데이터를 먼저 보여 주고 뒤에서 새로 고치는 전략입니다. | 체감 속도를 높이면서도 최신 데이터를 다시 받아오는 균형점을 제공합니다. |

## fetch 기본 패턴

**Before (콜백 지옥)**

```javascript
fetch("/api/users")
  .then(function(res) {
    return res.json();
  })
  .then(function(data) {
    renderUsers(data);
  })
  .catch(function(err) {
    console.error(err); // 사용자는 여전히 빈 화면
  });
```

**After (async/await + 명시적 에러 처리)**

```javascript
async function loadUsers() {
  const res = await fetch("/api/users");

  // fetch는 4xx/5xx에서 reject하지 않음 → 직접 확인 필요
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  }

  return res.json();
}
```

## 비동기 상태 모델: 4가지 상태

```javascript
// 비동기 UI는 항상 4가지 상태를 가집니다.
const states = {
  idle:    { status: "idle"    },
  loading: { status: "loading" },
  success: { status: "success", data: null },
  error:   { status: "error",   error: null },
};

// 상태 기계로 생각하면 전이가 명확해집니다.
// idle → loading → success
//              ↘ error
```

## 실습: 사용자 목록을 5단계로 만들기

### 1단계 — Plain fetch

```javascript
// api/users.js - API 클라이언트를 컴포넌트 밖으로 분리
const BASE_URL = "https://jsonplaceholder.typicode.com";

export async function fetchUsers() {
  const res = await fetch(`${BASE_URL}/users`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function fetchUser(id) {
  const res = await fetch(`${BASE_URL}/users/${id}`);
  if (!res.ok) throw new Error(`사용자 ${id}를 찾을 수 없습니다`);
  return res.json();
}
```

### 2단계 — Use it from React

```jsx
// 최소 버전: 에러/로딩 미처리
function Users() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetchUsers().then(setUsers);
  }, []);

  return (
    <ul>
      {users.map(u => <li key={u.id}>{u.name}</li>)}
    </ul>
  );
}
```

### 3단계 — Loading and error states

```jsx
// 상태 기계 패턴으로 4가지 상태 명시적 처리
function Users() {
  const [state, setState] = useState({ status: "idle" });

  useEffect(() => {
    setState({ status: "loading" });

    fetchUsers()
      .then(data => setState({ status: "success", data }))
      .catch(err  => setState({ status: "error",   error: err }));
  }, []);

  // 상태에 따라 다른 UI 반환
  if (state.status === "loading") {
    return (
      <div role="status" aria-live="polite">
        <p>사용자 목록 로딩 중...</p>
      </div>
    );
  }

  if (state.status === "error") {
    return (
      <div role="alert">
        <p>오류가 발생했습니다: {state.error.message}</p>
        <button onClick={() => setState({ status: "idle" })}>다시 시도</button>
      </div>
    );
  }

  if (state.status !== "success") return null;

  return (
    <ul>
      {state.data.map(u => (
        <li key={u.id}>
          <strong>{u.name}</strong> — {u.email}
        </li>
      ))}
    </ul>
  );
}
```

### 4단계 — Cancel on unmount

```jsx
function Users() {
  const [state, setState] = useState({ status: "loading" });

  useEffect(() => {
    const ctrl = new AbortController();

    fetch("https://jsonplaceholder.typicode.com/users", {
      signal: ctrl.signal,
    })
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(data => setState({ status: "success", data }))
      .catch(err => {
        // AbortError는 컴포넌트 언마운트로 인한 의도적 취소
        if (err.name !== "AbortError") {
          setState({ status: "error", error: err });
        }
      });

    // 클린업: 컴포넌트가 사라지면 요청 취소
    return () => ctrl.abort();
  }, []);

  // 렌더링 로직...
}
```

### 5단계 — Compress all of it with React Query

```jsx
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

function Users() {
  const queryClient = useQueryClient();

  // 자동 캐싱, 재시도, 백그라운드 갱신
  const { data: users, isLoading, error, refetch } = useQuery({
    queryKey: ["users"],
    queryFn: fetchUsers,
    staleTime: 5 * 60 * 1000,  // 5분간 신선한 데이터로 취급
    retry: 2,                   // 실패 시 2번 재시도
  });

  // 뮤테이션: 데이터 변경 후 자동 캐시 무효화
  const deleteUser = useMutation({
    mutationFn: (id) => fetch(`/api/users/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  if (isLoading) return <p>로딩 중...</p>;
  if (error)     return <p>오류: {error.message} <button onClick={refetch}>재시도</button></p>;

  return (
    <ul>
      {users.map(u => (
        <li key={u.id}>
          {u.name}
          <button onClick={() => deleteUser.mutate(u.id)}>삭제</button>
        </li>
      ))}
    </ul>
  );
}
```

## Race Condition 처리

```jsx
// 문제: 검색어를 빠르게 입력하면 이전 요청 결과가 나중에 도착해
//       최신 검색어와 다른 결과를 보여줄 수 있음
function Search() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  useEffect(() => {
    if (!query) {
      setResults([]);
      return;
    }

    const ctrl = new AbortController();
    let isActive = true;

    fetchSearch(query, ctrl.signal)
      .then(data => {
        // 이 요청이 아직 최신인지 확인
        if (isActive) setResults(data);
      })
      .catch(err => {
        if (err.name !== "AbortError" && isActive) {
          console.error("검색 오류:", err);
        }
      });

    return () => {
      isActive = false;  // 이전 요청 결과 무시
      ctrl.abort();       // 진행 중인 요청 취소
    };
  }, [query]);

  return (
    <div>
      <input
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="검색어..."
      />
      <ul>
        {results.map(r => <li key={r.id}>{r.title}</li>)}
      </ul>
    </div>
  );
}
```

## 디버깅 시나리오

### 시나리오 1: 에러가 화면에 안 보일 때

```javascript
// 잘못된 패턴: fetch의 4xx/5xx를 자동으로 catch하지 않음
try {
  const res = await fetch("/api/users");
  const data = await res.json();
  setUsers(data);
} catch (err) {
  console.error(err); // 네트워크 오류만 여기에 옴
}

// 올바른 패턴
try {
  const res = await fetch("/api/users");
  if (!res.ok) throw new Error(`HTTP ${res.status}`); // 4xx/5xx 직접 throw
  const data = await res.json();
  setUsers(data);
} catch (err) {
  setError(err); // 화면에 표시
}
```

### 시나리오 2: 이전 응답이 최신 상태를 덮어쓸 때

```bash
# DevTools → Network → 요청 목록에서 순서 확인
# 빠른 검색 입력 시 느린 요청이 나중에 완료되는지 확인
# → AbortController로 이전 요청 취소 구현 필요
```

### 시나리오 3: Slow 3G에서 테스트

```
DevTools → Network 탭
→ 우측 상단 "No throttling" 드롭다운
→ Slow 3G 선택
→ 로딩 상태가 제대로 보이는지 확인
→ 오류 상태를 보려면 "Offline" 선택
```

## 실무 점검 루프

1. **요청 결과를 봅니다.** UI를 고치기 전에 Network 탭에서 상태 코드, 응답 본문, 지연 시간을 먼저 확인합니다.
2. **가시 상태를 봅니다.** 로딩, 성공, 실패가 모두 서로 다른 화면 상태로 렌더링되는지 확인합니다.
3. **경쟁 상태를 봅니다.** 빠르게 타이핑하거나 화면을 떠날 때 오래된 응답이 최신 상태를 덮어쓰지 않는지 확인합니다.

```bash
# API 직접 테스트
curl -i https://jsonplaceholder.typicode.com/users
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|---|---|---|
| 로딩 상태 생략 | 사용자가 앱이 멈췄다고 느낌 | `status: "loading"` 상태 항상 구현 |
| 에러를 콘솔에만 기록 | 이유 없는 빈 화면, 사용자는 원인 모름 | 에러 상태를 화면에 친절하게 표시 |
| Race condition 무시 | 빠른 검색에서 오래된 결과가 마지막에 덮어씀 | AbortController + isActive 패턴 적용 |
| 같은 데이터를 여러 컴포넌트가 각각 요청 | 동일 리소스를 중복 요청 | React Query/SWR 캐싱 활용 |
| `res.ok` 검사 없이 `res.json()` 호출 | 4xx/5xx 응답이 에러로 처리 안 됨 | `if (!res.ok) throw new Error(...)` |
| 캐시 무효화 전략 없음 | 오래된 데이터가 계속 화면에 남음 | 뮤테이션 후 `invalidateQueries` 호출 |

## 실무에서는 이렇게 보입니다

현대 React 앱은 대부분 TanStack Query나 SWR을 표준처럼 사용합니다.

```jsx
// TanStack Query로 구현한 완전한 CRUD 예시
function NotesPage() {
  const queryClient = useQueryClient();

  const { data: notes = [], isLoading } = useQuery({
    queryKey: ["notes"],
    queryFn: () => fetch("/api/notes").then(r => r.json()),
  });

  const createNote = useMutation({
    mutationFn: (title) =>
      fetch("/api/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title }),
      }).then(r => r.json()),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notes"] }),
  });

  const deleteNote = useMutation({
    mutationFn: (id) => fetch(`/api/notes/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notes"] }),
  });

  if (isLoading) return <p>로딩 중...</p>;

  return (
    <div>
      <button onClick={() => createNote.mutate("새 노트")}>노트 추가</button>
      <ul>
        {notes.map(n => (
          <li key={n.id}>
            {n.title}
            <button onClick={() => deleteNote.mutate(n.id)}>삭제</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## 시니어 엔지니어는 이렇게 생각합니다

- 비동기는 상태 기계이므로 상태 전이를 먼저 그립니다.
- 모든 fetch는 취소 가능해야 한다고 가정합니다.
- 캐싱을 기본값으로 두고 실시간 갱신을 예외로 다룹니다.
- 사용자에게 보이는 에러는 친절하고 행동 가능해야 합니다.
- 가끔은 DevTools의 Slow 3G로 실제 체감을 확인합니다.

## 운영 체크리스트

- [ ] `fetch`를 `async/await`와 함께 작성할 수 있습니다.
- [ ] 로딩, 에러, 성공 상태를 각각 따로 렌더링할 수 있습니다.
- [ ] `AbortController`를 한 번 사용해 봤습니다.
- [ ] React Query나 SWR을 직접 써 봤습니다.
- [ ] Slow 3G 환경에서 동작을 점검해 봤습니다.
- [ ] `res.ok` 검사를 항상 추가하고 있습니다.

## 연습 문제

1. `https://jsonplaceholder.typicode.com/users`를 호출해 사용자 목록을 렌더링해 보세요.
2. 로딩 상태와 에러 상태를 명시적으로 추가해 보세요.
3. 검색 입력창을 붙이고, 빠르게 입력해도 가장 최근 입력 결과만 보이도록 race condition을 제어해 보세요.
4. React Query를 설치하고 위 예제를 마이그레이션해 보세요. 코드가 얼마나 줄어드는지 비교해 보세요.

## 정리 및 다음 단계

비동기는 결국 상태입니다. 이 관점이 잡히면 이제 사용자 입력을 받는 폼도 같은 방식으로 더 명확하게 읽을 수 있습니다.

다음 글에서는 폼과 유효성 검사를 통해 사용자 입력을 안전하고 친절하게 다루는 방법을 봅니다.

## 처음 질문으로 돌아가기

- **`fetch`와 `async/await`는 어떤 최소 패턴으로 시작하면 될까요?**
  - `async` 함수 안에서 `await fetch(url)` → `if (!res.ok) throw` → `await res.json()` 순서입니다. 이 세 줄이 안전한 최소 패턴입니다.
- **로딩 상태와 에러 상태를 왜 반드시 화면에 드러내야 할까요?**
  - 프론트엔드 버그의 많은 비중이 비동기 처리에서 나옵니다. 빠른 사내 와이파이에서는 잘 보이지 않다가 실제 사용자의 느린 네트워크에서만 터지는 경우가 많습니다.
- **컴포넌트가 사라질 때 요청 취소가 왜 필요할까요?**
  - 취소 없이 컴포넌트가 언마운트되면 응답이 돌아왔을 때 이미 사라진 컴포넌트의 상태를 업데이트하려는 오류가 발생합니다. AbortController로 이를 방지합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML과 CSS 기본](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript 기본](./03-javascript-basics.md)
- [Frontend Development 101 (4/10): 컴포넌트와 상태](./04-components-and-state.md)
- [Frontend Development 101 (5/10): 라우팅과 페이지](./05-routing-and-pages.md)
- **Frontend Development 101 (6/10): API 호출과 비동기 (현재 글)**
- [Frontend Development 101 (7/10): 폼과 유효성 검사](./07-forms-and-validation.md)
- [Frontend Development 101 (8/10): 스타일링과 디자인 시스템](./08-styling-and-design-system.md)
- [Frontend Development 101 (9/10): 빌드 도구와 번들링](./09-build-tools-and-bundling.md)
- [작은 프론트엔드 앱 만들기](./10-building-a-small-frontend-app.md)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [MDN: Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [MDN: AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController)
- [TanStack Query docs](https://tanstack.com/query/latest)

### 확인용 자료
- [SWR documentation](https://swr.vercel.app/)
- [web.dev: Fetch API error handling](https://web.dev/articles/fetch-api-error-handling)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/frontend-development-101/ko)

Tags: Frontend, API, Async, Fetch, JavaScript
