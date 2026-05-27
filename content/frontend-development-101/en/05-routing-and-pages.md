---
series: frontend-development-101
episode: 5
title: "Frontend Development 101 (5/10): Routing and Pages"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Frontend
  - Routing
  - SPA
  - React
  - Web
seo_description: SPA routing, URL-to-component mapping, nested routes, and lazy loading — connect screens through URLs cleanly.
last_reviewed: '2026-05-04'
---

# Frontend Development 101 (5/10): Routing and Pages

A one-screen app is easy to reason about. Real products are not. As soon as you add a home page, detail page, settings, and search results, users expect refresh, back navigation, and shareable links to work as if those screens were always separate places. Routing is the layer that makes that expectation feel natural.

This is the 5th post in the Frontend Development 101 series. Here we explain SPA navigation through the lens of URLs. The important idea is that a URL is not only an address. It is the portable description of the current screen state, and the router is the layer that maps that state to the component tree.


![frontend development 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/05/05-01-concept-at-a-glance.en.png)
*frontend development 101 chapter 5 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Routing and Pages?
- Which signal should the example or diagram make visible for Routing and Pages?
- What failure should be prevented first when Routing and Pages reaches a real system?

## What You Will Learn

- The *principle* behind SPA routing
- Mapping paths to components
- Nested routes
- Dynamic parameters and query strings
- Code splitting and lazy loading

## Why It Matters

Routing makes *refresh-safe screens*, *shareable links*, and *back-button behavior* work correctly. Broken routing breaks *product trust*.

> Good routing makes the screen *guessable from the URL alone*.

## Key Terms

- **Route**: a *mapping* from URL pattern to component.
- **Nested route**: a route *inside another route*.
- **Dynamic segment**: a pattern with a *variable slot* like `/users/:id`.
- **Query string**: extra info *outside the route*, like `?q=react&page=2`.
- **Lazy loading**: *splitting code per route* so it loads only when needed.

## Before/After

**Before (server routing, full reload)**

```html
<a href="/about">About</a>
```

**After (SPA routing, smooth transition)**

```jsx
<Link to="/about">About</Link>
```

## Hands-on: React Router in Five Steps

### Step 1 — Install

```bash
npm install react-router-dom
```

### Step 2 — Define routes

```jsx
import { createBrowserRouter, RouterProvider } from "react-router-dom";

const router = createBrowserRouter([
  { path: "/", element: <Home /> },
  { path: "/about", element: <About /> },
]);

<RouterProvider router={router} />
```

### Step 3 — Use Link

```jsx
import { Link } from "react-router-dom";

<nav>
  <Link to="/">Home</Link>
  <Link to="/about">About</Link>
</nav>
```

### Step 4 — Dynamic parameters

```jsx
{ path: "/users/:id", element: <UserDetail /> }

import { useParams } from "react-router-dom";
function UserDetail() {
  const { id } = useParams();
  return <p>user {id}</p>;
}
```

### Step 5 — Lazy loading

```jsx
import { lazy } from "react";
const Settings = lazy(() => import("./Settings"));

{ path: "/settings", element: <Suspense><Settings /></Suspense> }
```

## Verification

- Navigate between `/`, `/about`, and `/users/42` and confirm that the screen changes without a full reload while the param value renders correctly.
- In the Network tab, confirm that the lazy-loaded route downloads as a separate chunk rather than inflating the initial bundle.

## If It Fails, Check This First

- If the detail page is empty, check that the route pattern `/users/:id` matches the `useParams()` lookup exactly.
- If refresh fails after deployment, verify whether your host needs SPA history-fallback configuration.

## What to Notice in This Code

- `<Link>` updates router state *without a full page reload*.
- `useParams` exposes dynamic segments as *values*.
- Lazy loading shrinks the *initial bundle*.

## Five Common Mistakes

1. **Mixing `<a>` and `<Link>`.** `<a>` triggers *full reload*, defeating SPA gains.
2. **Not protecting auth-gated routes.** Direct URL entry *bypasses* checks.
3. **Skipping lazy loading with *dozens* of routes.** Initial load becomes *brutally slow*.
4. **Not syncing query string with state.** Search results *vanish on refresh*.
5. **No 404 page.** A bad URL shows *a white screen*.

## How This Shows Up in Production

Most teams use *file-based routing* via Next.js, Remix, or Nuxt. `pages/users/[id].tsx` automatically becomes the `/users/:id` route. Hand-listing routes is becoming *less common*.

## How a Senior Engineer Thinks

- A URL is *shareable state*.
- Auth/permission route guards are *designed in from day one*.
- Lots of routes ⇒ code splitting is *mandatory*.
- Search/filter belongs in the *query string* so links stay *shareable*.
- 404 must be *friendly* and offer a *way back*.

## Checklist

- [ ] You distinguish static and dynamic routes.
- [ ] You know the difference between `<Link>` and `<a>`.
- [ ] You can read params with `useParams`.
- [ ] You have set up lazy loading at least once.
- [ ] You have a 404 page.

## Practice Problems

1. Build four routes: `/`, `/about`, `/users/:id`, `/*` (404).
2. Show the param in `/users/:id` via `useParams`.
3. Lazy-load `/settings` and verify a separate chunk in the Network tab.

## Wrap-up and Next Steps

URLs decide what users see. Next, we look at how those screens *fetch data from a server*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Routing and Pages?**
  - The article treats Routing and Pages as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Routing and Pages?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Routing and Pages reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Frontend Development 101 (1/10): What Is Frontend Development?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML and CSS Basics](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript Basics](./03-javascript-basics.md)
- [Frontend Development 101 (4/10): Components and State](./04-components-and-state.md)
- **Routing and Pages (current)**
- API Calls and Async (upcoming)
- Forms and Validation (upcoming)
- Styling and Design Systems (upcoming)
- Build Tools and Bundling (upcoming)
- Building a Small Frontend App (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [React Router documentation](https://reactrouter.com/home)
- [Next.js routing](https://nextjs.org/docs/app/building-your-application/routing)
- [MDN: History API](https://developer.mozilla.org/en-US/docs/Web/API/History_API)

### Verification and Further Reading
- [URL Standard](https://url.spec.whatwg.org/)
- [Vite guide: Deploying a static site](https://vite.dev/guide/static-deploy.html)

Tags: Frontend, Routing, SPA, React, Web
