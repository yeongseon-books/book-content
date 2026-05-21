---
series: frontend-development-101
episode: 5
title: "Frontend Development 101 (5/10): 라우팅과 페이지"
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
  - Routing
  - SPA
  - React
  - Web
seo_description: SPA 라우팅과 URL 매핑의 핵심 원리를 프론트엔드 관점에서 정리합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (5/10): 라우팅과 페이지

이 글은 Frontend Development 101 시리즈의 다섯 번째 글입니다. 여기서는 SPA가 여러 화면을 어떻게 표현하는지 URL 중심으로 설명합니다. URL은 단순한 주소가 아니라 현재 화면을 설명하는 상태이며, 라우터는 그 상태를 읽어 어떤 컴포넌트를 그릴지 결정하는 계층입니다.

한 화면짜리 앱은 비교적 단순합니다. 하지만 제품이 커지면 홈, 상세, 설정, 검색 결과처럼 여러 화면이 생기고, 사용자는 뒤로 가기와 새로고침과 링크 공유가 모두 자연스럽게 되기를 기대합니다. 이 기대를 만족시키는 핵심이 라우팅입니다.

![Frontend Development 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/05/05-01-diagram.ko.png)
*Frontend Development 101 5장 흐름 개요*

## 먼저 던지는 질문

- 단일 페이지 앱이 여러 화면을 보여 주는 원리는 무엇일까요?
- 경로(path)는 컴포넌트와 어떤 식으로 매핑될까요?
- 중첩 라우트와 동적 파라미터는 왜 필요한가요?

## 왜 중요한가

라우팅은 새로고침해도 같은 화면이 다시 열리고, 링크를 복사해 다른 사람과 공유할 수 있으며, 뒤로 가기 버튼이 자연스럽게 동작하게 만듭니다. 이 기본기가 무너지면 사용자는 제품 전체를 불안정하게 느낍니다.

좋은 라우팅은 URL만 보고도 현재 화면을 어느 정도 짐작할 수 있게 만듭니다. 반대로 URL이 화면 상태를 설명하지 못하면 검색, 필터, 상세 페이지 같은 기능이 곧바로 불편해집니다.

## 개념 한눈에 보기

결국 라우팅은 URL 패턴을 해석해 컴포넌트 트리를 고르는 일입니다. 이 모델만 잡혀도 정적 경로, 동적 경로, 중첩 경로를 같은 방식으로 읽을 수 있습니다.

## 핵심 용어

- **Route**: URL 패턴과 컴포넌트의 매핑입니다.
- **중첩 라우트**: 다른 라우트 안에 들어가는 하위 라우트입니다.
- **동적 세그먼트**: `/users/:id`처럼 값이 들어갈 자리를 포함한 경로 패턴입니다.
- **쿼리 문자열**: `?q=react&page=2`처럼 경로 밖에 붙는 추가 상태입니다.
- **Lazy loading**: 필요한 라우트 코드만 나중에 불러오는 방식입니다.

## 전통 방식과 현대 방식 비교

**Before (서버 라우팅, 전체 새로고침)**

```html
<a href="/about">About</a>
```

**After (SPA routing, smooth transition)**

```jsx
<Link to="/about">About</Link>
```

둘 다 화면 이동처럼 보이지만 동작은 다릅니다. `<a>`는 브라우저가 전체 문서를 다시 요청하게 만들고, `<Link>`는 애플리케이션 내부 상태만 바꿔 더 자연스러운 전환을 제공합니다.

## 실습: 리액트 라우터를 5단계로 적용하기

### 1단계 — Install

```bash
npm install react-router-dom
```

### 2단계 — Define routes

```jsx
import { createBrowserRouter, RouterProvider } from "react-router-dom";

const router = createBrowserRouter([
  { path: "/", element: <Home /> },
  { path: "/about", element: <About /> },
]);

<RouterProvider router={router} />
```

### 3단계 — Use Link

```jsx
import { Link } from "react-router-dom";

<nav>
  <Link to="/">Home</Link>
  <Link to="/about">About</Link>
</nav>
```

### 4단계 — Dynamic parameters

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

이 흐름을 보면 라우팅이 단순한 링크 모음이 아니라는 점이 드러납니다. 설치와 경로 정의, 링크 연결, 파라미터 읽기, 코드 분할까지 이어져야 실제 제품에서 쓸 수 있는 라우팅이 됩니다.

## 검증 포인트

- `/`, `/about`, `/users/42`로 이동했을 때 새로고침 없이 화면이 바뀌고 파라미터가 올바르게 보이는지 확인합니다.
- Network 탭에서 lazy loading한 라우트가 별도 청크로 내려오는지 확인합니다.

## 문제가 생기면 먼저 볼 것

- 상세 페이지가 비면 `useParams()` 결과와 라우트 패턴 `/users/:id`가 일치하는지 확인합니다.
- 배포 후 새로고침 404가 나면 호스팅 환경에 SPA history fallback 설정이 필요한지 봅니다.

## 이 코드에서 주목할 점

- `<Link>`는 전체 새로고침 없이 라우터 상태만 바꿉니다.
- `useParams`는 동적 세그먼트를 실제 값으로 꺼내 줍니다.
- Lazy loading은 초기 번들 크기를 줄여 첫 화면 성능을 지켜 줍니다.

## 자주 하는 실수 5가지

1. **`<a>`와 `<Link>`를 섞어 씁니다.** 전체 새로고침이 발생해 SPA의 장점이 사라집니다.
2. **인증이 필요한 경로를 보호하지 않습니다.** URL을 직접 입력하면 우회 접근이 생길 수 있습니다.
3. **라우트가 많은데 lazy loading을 건너뜁니다.** 초기 로딩이 매우 무거워집니다.
4. **쿼리 문자열과 화면 상태를 동기화하지 않습니다.** 검색 결과나 필터 상태가 새로고침에서 사라집니다.
5. **404 페이지가 없습니다.** 잘못된 URL에서 사용자가 하얀 화면을 만나게 됩니다.

## 실무에서는 이렇게 보입니다

최근에는 Next.js, Remix, Nuxt처럼 파일 기반 라우팅을 제공하는 프레임워크가 널리 쓰입니다. `pages/users/[id].tsx` 같은 파일 구조가 곧 라우트 정의가 됩니다. 직접 배열로 경로를 하나씩 나열하는 방식은 점점 줄어드는 추세입니다.

하지만 형식이 무엇이든 핵심은 같습니다. URL이 상태를 설명해야 하고, 인증과 권한과 404 처리와 코드 분할까지 함께 설계해야 합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- URL은 공유 가능한 상태입니다.
- 인증과 권한 경계는 라우팅 설계 초반부터 반영합니다.
- 라우트가 많아질수록 코드 스플리팅은 선택이 아니라 기본입니다.
- 검색과 필터 상태는 쿼리 문자열에 넣어 공유 가능하게 만듭니다.
- 404 화면도 친절해야 하며 돌아갈 길을 제공해야 합니다.

## 체크리스트

- [ ] 정적 라우트와 동적 라우트를 구분할 수 있습니다.
- [ ] `<Link>`와 `<a>`의 차이를 설명할 수 있습니다.
- [ ] `useParams`로 파라미터를 읽을 수 있습니다.
- [ ] lazy loading을 한 번 설정해 봤습니다.
- [ ] 404 페이지를 만들 수 있습니다.

## 연습 문제

1. `/`, `/about`, `/users/:id`, `/*`(404) 네 개의 라우트를 만들어 보세요.
2. `/users/:id` 화면에서 `useParams`로 값을 표시해 보세요.
3. `/settings` 라우트를 lazy loading으로 분리하고 Network 탭에서 별도 청크를 확인해 보세요.

## 정리 및 다음 단계

라우팅은 사용자가 무엇을 보는지 결정하는 URL 기반 상태 관리입니다. 이 흐름이 잡히면 이제 화면이 서버 데이터와 어떻게 연결되는지도 자연스럽게 이어집니다.

다음 글에서는 프론트엔드가 서버에서 데이터를 가져오는 비동기 흐름을 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **단일 페이지 앱이 여러 화면을 보여 주는 원리는 무엇일까요?**
  - 본문의 기준은 라우팅과 페이지를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **경로(path)는 컴포넌트와 어떤 식으로 매핑될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **중첩 라우트와 동적 파라미터는 왜 필요한가요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML과 CSS 기본](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript 기본](./03-javascript-basics.md)
- [Frontend Development 101 (4/10): 컴포넌트와 상태](./04-components-and-state.md)
- **라우팅과 페이지 (현재 글)**
- API 호출과 비동기 (예정)
- 폼과 유효성 검사 (예정)
- 스타일링과 디자인 시스템 (예정)
- 빌드 도구와 번들링 (예정)
- 작은 프론트엔드 앱 만들기 (예정)

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
