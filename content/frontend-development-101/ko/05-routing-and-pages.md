---
series: frontend-development-101
episode: 5
title: 라우팅과 페이지
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
  - Routing
  - SPA
  - React
  - Web
seo_description: SPA 라우팅, URL 매핑, nested routes, lazy loading — 여러 화면을 URL로 연결하는 기본기를 정리합니다.
last_reviewed: '2026-05-11'
---

# 라우팅과 페이지

> Frontend Development 101 시리즈 (5/10)


## 이 글에서 다룰 문제

라우팅은 사용자가 새로고침해도 같은 화면을 보게 만들고, 공유 링크를 만들고, 뒤로 가기 동작을 자연스럽게 유지해 줍니다. 라우팅이 깨지면 제품 전체의 신뢰가 흔들립니다.

> 좋은 라우팅은 URL만 봐도 어떤 화면인지 짐작이 갑니다.

## 전체 흐름
```mermaid
flowchart LR
    URL["/users/42"] --> Router["Router"]
    Router --> Match["Match path"]
    Match --> Comp["UserDetail({id: 42})"]
```

## Before/After

**Before (서버 라우팅, 새로고침 발생)**

```html
<a href="/about">About</a>
```

**After (SPA 라우팅, 부드러운 전환)**

```jsx
<Link to="/about">About</Link>
```

## React Router 5단계

### 1단계 — 설치

```bash
npm install react-router-dom
```

### 2단계 — 라우트 정의

```jsx
import { createBrowserRouter, RouterProvider } from "react-router-dom";

const router = createBrowserRouter([
  { path: "/", element: <Home /> },
  { path: "/about", element: <About /> },
]);

<RouterProvider router={router} />
```

### 3단계 — Link 사용

```jsx
import { Link } from "react-router-dom";

<nav>
  <Link to="/">홈</Link>
  <Link to="/about">소개</Link>
</nav>
```

### 4단계 — 동적 파라미터

```jsx
{ path: "/users/:id", element: <UserDetail /> }

import { useParams } from "react-router-dom";
function UserDetail() {
  const { id } = useParams();
  return <p>user {id}</p>;
}
```

### 5단계 — Lazy loading

```jsx
import { lazy } from "react";
const Settings = lazy(() => import("./Settings"));

{ path: "/settings", element: <Suspense><Settings /></Suspense> }
```

## 이 코드에서 주목할 점

- `<Link>` 는 페이지 새로고침 없이 라우터 상태만 바꿉니다.
- `useParams` 는 동적 segment를 실제 값으로 꺼내줍니다.
- Lazy loading을 적용하면 초기 번들 크기를 줄일 수 있습니다.

## 자주 하는 실수 5가지

1. **`<a>` 와 `<Link>` 를 혼용한다.** `<a>` 는 새로고침을 일으켜 SPA의 장점을 없애 버립니다.
2. **인증이 필요한 라우트를 보호하지 않는다.** URL을 직접 입력하면 우회될 수 있습니다.
3. **라우트가 수십 개인데 lazy loading을 안 한다.** 첫 로드가 눈에 띄게 느려집니다.
4. **query string을 상태와 동기화하지 않는다.** 새로고침하면 검색 결과가 사라집니다.
5. **404 페이지를 만들지 않는다.** 잘못된 URL에서 흰 화면만 보이게 됩니다.

## 실무에서는 이렇게 쓰입니다

대부분의 회사는 Next.js, Remix, Nuxt 같은 프레임워크가 제공하는 파일 기반 라우팅을 사용합니다. `pages/users/[id].tsx` 가 자동으로 `/users/:id` 라우트가 됩니다. 손으로 라우트를 길게 나열하는 일은 점점 줄어드는 추세입니다.

## 체크리스트

- [ ] 정적 라우트와 동적 라우트를 구분한다.
- [ ] `<Link>` 와 `<a>` 의 차이를 안다.
- [ ] `useParams` 로 동적 값을 꺼낼 수 있다.
- [ ] lazy loading을 한 번 설정해봤다.
- [ ] 404 페이지가 있다.

## 정리 및 다음 단계

URL이 화면을 결정합니다. 다음 글에서는 그 화면이 서버에서 데이터를 가져오는 비동기 흐름을 다룹니다.

<!-- toc:begin -->
- [프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [HTML과 CSS 기본](./02-html-and-css-basics.md)
- [JavaScript 기본](./03-javascript-basics.md)
- [컴포넌트와 상태](./04-components-and-state.md)
- **라우팅과 페이지 (현재 글)**
- API 호출과 비동기 (예정)
- 폼과 유효성 검사 (예정)
- 스타일링과 디자인 시스템 (예정)
- 빌드 도구와 번들링 (예정)
- 작은 프론트엔드 앱 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [React Router docs](https://reactrouter.com/)
- [Next.js routing](https://nextjs.org/docs/app/building-your-application/routing)
- [URL Living Standard](https://url.spec.whatwg.org/)
- [MDN History API](https://developer.mozilla.org/en-US/docs/Web/API/History_API)

Tags: Frontend, Routing, SPA, React, Web
