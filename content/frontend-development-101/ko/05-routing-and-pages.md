---
series: frontend-development-101
episode: 5
title: "Frontend Development 101 (5/10): 라우팅과 페이지"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/217"
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
  - Routing
  - SPA
  - React
  - Web
seo_description: SPA 라우팅과 URL 매핑의 핵심 원리를 프론트엔드 관점에서 정리합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (5/10): 라우팅과 페이지

결국 라우팅은 URL 패턴을 해석해 컴포넌트 트리를 고르는 일입니다. 이 모델만 잡혀도 정적 경로, 동적 경로, 중첩 경로를 같은 방식으로 읽을 수 있습니다.

이 글은 Frontend Development 101 시리즈의 다섯 번째 글입니다. 여기서는 SPA가 여러 화면을 어떻게 표현하는지 URL 중심으로 설명합니다. URL은 단순한 주소가 아니라 현재 화면을 설명하는 상태이며, 라우터는 그 상태를 읽어 어떤 컴포넌트를 그릴지 결정하는 계층입니다.

![Frontend Development 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/05/05-01-diagram.ko.png)
*Frontend Development 101 5장 흐름 개요*

> 라우팅은 'URL과 컴포넌트 트리를 매핑하는 일'입니다 — SPA / MPA / SSR / SSG 차이는 '이 매핑을 누가 언제 수행하는가(브라우저인가, 서버인가, 빌드 타임인가)'라는 한 가지 축으로 정리됩니다.

## 이 글에서 다룰 문제

- 단일 페이지 앱이 여러 화면을 보여 주는 원리는 무엇일까요?
- 경로(path)는 컴포넌트와 어떤 식으로 매핑될까요?
- 중첩 라우트와 동적 파라미터는 왜 필요한가요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 개념 한눈에 보기

| 용어 | 뜻 | 실무에서 왜 중요한가 |
|---|---|---|
| Route | URL 패턴과 컴포넌트의 매핑입니다. | 어떤 화면이 어떤 주소에서 열리는지 설명하는 기본 단위입니다. |
| 중첩 라우트 | 다른 라우트 안에 들어가는 하위 라우트입니다. | 레이아웃과 하위 화면을 함께 묶는 구조를 만들 수 있습니다. |
| 동적 세그먼트 | `/users/:id`처럼 값이 들어갈 자리를 포함한 경로 패턴입니다. | 상세 페이지나 편집 화면처럼 개체별 URL을 자연스럽게 표현합니다. |
| 쿼리 문자열 | `?q=react&page=2`처럼 경로 밖에 붙는 추가 상태입니다. | 검색, 정렬, 필터처럼 공유 가능한 화면 상태를 보존합니다. |
| Lazy loading | 필요한 라우트 코드만 나중에 불러오는 방식입니다. | 초기 번들을 줄이고 첫 화면 응답 속도를 높이는 데 직접 연결됩니다. |

## History API: SPA 라우팅의 기반

브라우저의 `history.pushState()`가 SPA 라우팅의 핵심입니다.

```javascript
// 브라우저 History API 기본 원리
// 라우터 라이브러리 없이 직접 구현해 보면 원리가 보입니다.

const routes = {
  "/"        : HomePage,
  "/about"   : AboutPage,
  "/contact" : ContactPage,
};

function navigate(path) {
  // URL 변경 (전체 새로고침 없이)
  history.pushState({}, "", path);
  render(path);
}

function render(path) {
  const app = document.getElementById("app");
  const Page = routes[path] || NotFoundPage;
  app.innerHTML = "";
  app.appendChild(Page());
}

// 뒤로/앞으로 가기 처리
window.addEventListener("popstate", () => {
  render(location.pathname);
});

// 링크 클릭 처리
document.addEventListener("click", (e) => {
  const a = e.target.closest("a[href]");
  if (!a) return;
  const href = a.getAttribute("href");
  if (href.startsWith("/")) {
    e.preventDefault();
    navigate(href);
  }
});

// 초기 렌더링
render(location.pathname);
```

**Before (서버 라우팅, 전체 새로고침)**

```html
<a href="/about">About</a>
<!-- 클릭하면 서버에 새 HTML 문서 요청 → 전체 페이지 재로딩 -->
```

**After (SPA routing, smooth transition)**

```jsx
import { Link } from "react-router-dom";
<Link to="/about">About</Link>
{/* 클릭해도 JS만 실행 → 화면 일부만 교체 */}
```

## 실습: 리액트 라우터를 5단계로 적용하기

### 1단계 — Install

```bash
npm install react-router-dom
```

### 2단계 — Define routes

```jsx
// src/main.jsx
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "./App";
import Home from "./pages/Home";
import About from "./pages/About";
import UserDetail from "./pages/UserDetail";
import NotFound from "./pages/NotFound";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,       // 레이아웃 컴포넌트
    children: [
      { index: true,         element: <Home /> },
      { path: "about",       element: <About /> },
      { path: "users/:id",   element: <UserDetail /> },
      { path: "*",           element: <NotFound /> },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")).render(
  <RouterProvider router={router} />
);
```

### 3단계 — Layout with Outlet

```jsx
// src/App.jsx
import { Link, NavLink, Outlet } from "react-router-dom";

function App() {
  return (
    <div>
      <header>
        <nav>
          {/* NavLink는 현재 경로일 때 active 클래스 자동 추가 */}
          <NavLink to="/"     className={({ isActive }) => isActive ? "active" : ""}>홈</NavLink>
          <NavLink to="/about" className={({ isActive }) => isActive ? "active" : ""}>소개</NavLink>
        </nav>
      </header>
      <main>
        {/* 현재 라우트의 컴포넌트가 여기에 렌더링됨 */}
        <Outlet />
      </main>
    </div>
  );
}
```

### 4단계 — Dynamic parameters

```jsx
// src/pages/UserDetail.jsx
import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

function UserDetail() {
  const { id } = useParams();                  // URL의 :id 값
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch(`https://jsonplaceholder.typicode.com/users/${id}`)
      .then(r => r.json())
      .then(setUser);
  }, [id]);

  if (!user) return <p>로딩 중...</p>;

  return (
    <article>
      <h1>{user.name}</h1>
      <p>이메일: {user.email}</p>
      <p>도시: {user.address.city}</p>
      <button onClick={() => navigate(-1)}>뒤로 가기</button>
    </article>
  );
}
```

### 5단계 — Lazy loading

```jsx
// src/main.jsx
import { lazy, Suspense } from "react";

// 초기 번들에 포함하지 않고 필요할 때 로딩
const Settings = lazy(() => import("./pages/Settings"));
const Dashboard = lazy(() => import("./pages/Dashboard"));

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <Home /> },
      {
        path: "settings",
        element: (
          <Suspense fallback={<p>설정 페이지 로딩 중...</p>}>
            <Settings />
          </Suspense>
        ),
      },
      {
        path: "dashboard",
        element: (
          <Suspense fallback={<p>대시보드 로딩 중...</p>}>
            <Dashboard />
          </Suspense>
        ),
      },
    ],
  },
]);
```

## 검색과 필터를 쿼리 문자열로 관리

```jsx
// src/pages/Search.jsx
import { useSearchParams } from "react-router-dom";

function Search() {
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get("q") || "";
  const page  = Number(searchParams.get("page") || 1);

  function handleSearch(e) {
    e.preventDefault();
    const q = e.target.elements.q.value;
    // URL이 바뀌면 링크 공유 시 같은 화면이 열림
    setSearchParams({ q, page: 1 });
  }

  return (
    <div>
      <form onSubmit={handleSearch}>
        <input name="q" defaultValue={query} placeholder="검색어 입력..." />
        <button type="submit">검색</button>
      </form>
      <p>검색어: "{query}", 페이지: {page}</p>
      {/* 현재 URL 예: /search?q=react&page=1 */}
    </div>
  );
}
```

## 인증이 필요한 라우트 보호

```jsx
// src/components/PrivateRoute.jsx
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

function PrivateRoute({ children }) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    // 로그인 후 원래 페이지로 돌아오도록 현재 위치 저장
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

// 사용
{ path: "dashboard", element: <PrivateRoute><Dashboard /></PrivateRoute> }
```

## 디버깅 시나리오

### 시나리오 1: 배포 후 새로고침 시 404

```
문제: 브라우저에서 /users/42 에서 새로고침 → 404 오류

원인: 서버는 /users/42 라는 실제 파일이 없음
      브라우저는 SPA인지 몰라서 그냥 서버에 파일 요청

해결 (Nginx):
  location / {
    try_files $uri $uri/ /index.html;
  }

해결 (Netlify): _redirects 파일 생성
  /* /index.html 200

해결 (Vite preview):
  npx serve -s dist   # -s 플래그가 SPA fallback 활성화
```

### 시나리오 2: 뒤로 가기가 이상하게 동작할 때

```jsx
// navigate(-1)은 히스토리 스택에서 뒤로 이동
// 히스토리에 아무것도 없으면 아무 일도 안 일어남

// replace: 현재 히스토리 항목을 교체 (뒤로 가기로 돌아올 수 없음)
navigate("/login", { replace: true });

// push (기본): 새 히스토리 항목 추가 (뒤로 가기 가능)
navigate("/dashboard");
```

### 시나리오 3: useParams 값이 undefined일 때

```jsx
// 라우트 정의와 useParams 키가 일치해야 함
{ path: "users/:userId" }   // ← :userId 정의

const { id } = useParams();       // id는 undefined!
const { userId } = useParams();   // userId 올바름
```

## 실무 점검 루프

1. **링크 동작을 봅니다.** 화면 이동 시 Network 탭에 전체 문서 재요청이 없는지 확인합니다.
2. **라우트 매칭을 봅니다.** `useParams()` 값이 경로 패턴과 정확히 맞는지 로그로 확인합니다.
3. **호스팅 fallback을 봅니다.** `/users/42` 같은 깊은 URL을 직접 열고 새로고침했을 때 `index.html`이 반환되는지 확인합니다.

```bash
# 운영과 비슷한 정적 호스팅 확인
npm run build
npx serve -s dist
# 그다음 /users/42를 열고 새로고침
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|---|---|---|
| `<a>`와 `<Link>` 혼용 | `<a>`는 전체 새로고침, SPA 장점 사라짐 | SPA 내부 이동에는 반드시 `<Link>` 사용 |
| 인증 없이 보호 라우트 방치 | URL 직접 입력으로 우회 접근 가능 | `PrivateRoute`로 모든 보호 경로 감쌈 |
| lazy loading 없이 라우트 다수 | 초기 번들이 비대해져 첫 화면 느림 | 큰 페이지 컴포넌트는 `lazy()` 적용 |
| 쿼리 문자열과 화면 상태 미동기화 | 새로고침 시 필터/검색 상태 초기화 | `useSearchParams`로 URL에 상태 보존 |
| 404 페이지 미구현 | 잘못된 URL에서 빈 화면 또는 오류 | `path: "*"` 라우트에 404 컴포넌트 연결 |
| 배포 시 SPA fallback 미설정 | 깊은 URL 새로고침 시 404 오류 | 호스팅 서버에 fallback 설정 필수 |

## 실무에서는 이렇게 보입니다

최근에는 Next.js, Remix, Nuxt처럼 파일 기반 라우팅을 제공하는 프레임워크가 널리 쓰입니다.

```
# Next.js App Router 파일 구조
app/
├── page.tsx          → /
├── about/
│   └── page.tsx      → /about
├── users/
│   ├── page.tsx      → /users
│   └── [id]/
│       └── page.tsx  → /users/:id
└── not-found.tsx     → 404 페이지
```

파일 구조가 곧 라우트 정의가 됩니다. React Router처럼 배열로 경로를 선언하지 않아도 됩니다. 하지만 내부적으로 같은 원리로 동작합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- URL은 공유 가능한 상태입니다.
- 인증과 권한 경계는 라우팅 설계 초반부터 반영합니다.
- 라우트가 많아질수록 코드 스플리팅은 선택이 아니라 기본입니다.
- 검색과 필터 상태는 쿼리 문자열에 넣어 공유 가능하게 만듭니다.
- 404 화면도 친절해야 하며 돌아갈 길을 제공해야 합니다.

## 운영 체크리스트

- [ ] 정적 라우트와 동적 라우트를 구분할 수 있습니다.
- [ ] `<Link>`와 `<a>`의 차이를 설명할 수 있습니다.
- [ ] `useParams`로 파라미터를 읽을 수 있습니다.
- [ ] lazy loading을 한 번 설정해 봤습니다.
- [ ] 404 페이지를 만들 수 있습니다.
- [ ] 배포 환경에서 SPA fallback을 설정할 수 있습니다.

## 연습 문제

1. `/`, `/about`, `/users/:id`, `/*`(404) 네 개의 라우트를 만들어 보세요.
2. `/users/:id` 화면에서 `useParams`로 값을 표시해 보세요.
3. `/settings` 라우트를 lazy loading으로 분리하고 Network 탭에서 별도 청크를 확인해 보세요.
4. 검색 페이지에서 `useSearchParams`로 쿼리를 URL에 저장하고 새로고침 후에도 유지되는지 확인해 보세요.

## 정리 및 다음 단계

라우팅은 사용자가 무엇을 보는지 결정하는 URL 기반 상태 관리입니다. 이 흐름이 잡히면 이제 화면이 서버 데이터와 어떻게 연결되는지도 자연스럽게 이어집니다.

다음 글에서는 프론트엔드가 서버에서 데이터를 가져오는 비동기 흐름을 봅니다.

## 처음 질문으로 돌아가기

- **단일 페이지 앱이 여러 화면을 보여 주는 원리는 무엇일까요?**
  - `history.pushState()`로 URL을 바꾸고, URL에 매핑된 컴포넌트를 DOM에 교체하는 방식입니다. 전체 새로고침 없이 브라우저 주소만 바뀝니다.
- **경로(path)는 컴포넌트와 어떤 식으로 매핑될까요?**
  - 라우터가 현재 URL을 정규식 패턴과 비교해 일치하는 컴포넌트를 찾아 렌더링합니다. `/users/:id`에서 `:id`는 실제 URL 세그먼트와 매칭됩니다.
- **중첩 라우트와 동적 파라미터는 왜 필요한가요?**
  - 중첩 라우트는 공통 레이아웃을 재사용하기 위해, 동적 파라미터는 같은 화면 구조를 다른 데이터로 보여주기 위해 필요합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML과 CSS 기본](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript 기본](./03-javascript-basics.md)
- [Frontend Development 101 (4/10): 컴포넌트와 상태](./04-components-and-state.md)
- **Frontend Development 101 (5/10): 라우팅과 페이지 (현재 글)**
- [Frontend Development 101 (6/10): API 호출과 비동기](./06-api-calls-and-async.md)
- [Frontend Development 101 (7/10): 폼과 유효성 검사](./07-forms-and-validation.md)
- [Frontend Development 101 (8/10): 스타일링과 디자인 시스템](./08-styling-and-design-system.md)
- [Frontend Development 101 (9/10): 빌드 도구와 번들링](./09-build-tools-and-bundling.md)
- [작은 프론트엔드 앱 만들기](./10-building-a-small-frontend-app.md)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [React Router documentation](https://reactrouter.com/home)
- [Next.js routing](https://nextjs.org/docs/app/building-your-application/routing)
- [MDN: History API](https://developer.mozilla.org/en-US/docs/Web/API/History_API)

### 확인용 자료
- [URL Standard](https://url.spec.whatwg.org/)
- [Vite guide: Deploying a static site](https://vite.dev/guide/static-deploy.html)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/frontend-development-101/ko)

Tags: Frontend, Routing, SPA, React, Web
