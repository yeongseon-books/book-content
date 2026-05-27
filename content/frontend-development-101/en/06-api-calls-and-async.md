---
series: frontend-development-101
episode: 6
title: "Frontend Development 101 (6/10): API Calls and Async"
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
  - API
  - Async
  - Fetch
  - JavaScript
seo_description: fetch, async/await, loading and error states, caching — the asynchronous data flow of a modern frontend.
last_reviewed: '2026-05-04'
---

# Frontend Development 101 (6/10): API Calls and Async

Frontend code almost always talks to a server. It loads a user list, fetches search results, and sends data when the user clicks Save. The hard part is not writing `fetch`. The hard part is that networks are slow, unreliable, and capable of returning responses in an order you did not expect.

This is the 6th post in the Frontend Development 101 series. Here we frame async work around explicit UI state. In practice, most async bugs get easier once you separate loading, success, and failure as first-class screen states instead of as afterthoughts.


![frontend development 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/06/06-01-concept-at-a-glance.en.png)
*frontend development 101 chapter 6 flow overview*

## Questions to Keep in Mind

- Why is async UI easier to reason about when loading, success, and failure are explicit screen states?
- What race conditions appear when requests overlap or a screen unmounts mid-request?
- Which checks turn a simple `fetch` demo into production-safe frontend behavior?

## What You Will Learn

- The *minimum usage* of `fetch` and `async/await`
- Handling loading/error states *explicitly*

- Cancellation and race conditions
- Caching and stale-while-revalidate
- *Why React Query / SWR* became standard

## Why It Matters

Async bugs make up *half of frontend defects*. They hide on a fast network and explode on a user's *slow 3G*. Explicit state management is *the only cure*.

> Good async code *assumes the worst network*.

## Key Terms

- **`fetch`**: the browser-built-in HTTP client.
- **Promise**: an object representing *a value to arrive in the future*.
- **`async/await`**: syntax to use Promises *as if they were synchronous*.
- **AbortController**: tool to *cancel a request mid-flight*.
- **Stale-while-revalidate**: *show cached data first*, refresh in the background.

## From Callback Chains to Explicit Async State

Async frontend work is not hard because `fetch` is complicated. It is hard because user-visible state has to stay coherent while the network is slow, reordered, canceled, or broken. Moving from callback-style control flow to explicit async state makes those failures much easier to reason about.

**Nested async flow that hides state changes**

```javascript
fetch(url, (res) => {
  parse(res, (data) => {
    render(data, (e) => { ... });
  });
});
```

**Linear async flow that exposes state transitions**

```javascript
const res = await fetch(url);
const data = await res.json();
render(data);
```

The improved style matters because it leaves room for the real production concerns: checking `res.ok`, rendering loading and error states, and canceling stale requests before they overwrite fresher data.

## Hands-on: A User List in Five Steps

### Step 1 — Plain fetch

```javascript
async function loadUsers() {
  const res = await fetch("/api/users");
  return res.json();
}
```

### Step 2 — Use it from React

```jsx
function Users() {
  const [users, setUsers] = useState([]);
  useEffect(() => { loadUsers().then(setUsers); }, []);
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

### Step 3 — Loading and error states

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

### Step 4 — Cancel on unmount

```jsx
useEffect(() => {
  const ctrl = new AbortController();
  fetch("/api/users", { signal: ctrl.signal })
    .then(r => r.json()).then(setUsers)
    .catch(e => e.name !== "AbortError" && console.error(e));
  return () => ctrl.abort();
}, []);
```

### Step 5 — Compress all of it with React Query

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

## Verification

- With a working API, verify that the UI shows loading first and then renders the user list; with a broken endpoint, verify that a user-facing error appears.
- Switch DevTools to Slow 3G and confirm that requests can be canceled cleanly when the component unmounts or the screen changes.

## If It Fails, Check This First

- If errors disappear into the console, make sure `res.ok` is checked and the `catch` path updates visible UI state.

```javascript
const res = await fetch("/api/users");
if (!res.ok) throw new Error(`HTTP ${res.status}`);
```
- If older responses overwrite newer ones, inspect your `AbortController` cleanup or the logic that decides which response is still current.

## Practical Debug Loop

Async frontend bugs almost always reveal themselves when you watch the request lifecycle and the UI state machine side by side.

1. **Request result** - inspect the Network panel and confirm status code, response body, and timing before changing UI logic.
2. **Visible state** - make sure loading, success, and error each render a different screen state.
3. **Race safety** - type quickly or navigate away mid-request and confirm stale responses do not overwrite newer ones.

```bash
curl -i https://jsonplaceholder.typicode.com/users
```

```javascript
const res = await fetch("/api/users");
if (!res.ok) throw new Error(`HTTP ${res.status}`);
```

Expected outcome: you can name the exact failed stage - transport, response validation, state update, or cancellation - instead of filing all async issues under "fetch is broken."

## What to Notice in This Code

- The state is *explicit*: `idle/loading/success/error`.
- The request is *canceled* on unmount.
- React Query handles caching, retry, and race conditions *for you*.

## Five Common Mistakes

1. **Skipping the loading state.** Users assume the *app is dead*.
2. **Logging errors only to the console.** Users see *a white screen*.
3. **Ignoring race conditions.** Fast typing in search shows *the wrong result*.
4. **Each component fetches the *same* data separately.** N copies of one resource.
5. **No cache invalidation strategy.** Stale screens stay even after fresh data exists.

## How This Shows Up in Production

Most React apps standardize on *React Query (TanStack Query)* or *SWR*. Vue uses *Pinia + composables*; Svelte ships with built-in *load functions*. Hand-rolled fetch state code is *fading out*.

## How a Senior Engineer Thinks

- Async is *a state machine* — draw all four states.
- Every fetch should be *cancellable*.
- Caching is *the default*; live refresh is the exception.
- User-facing errors must be *friendly and actionable*.
- Test on the DevTools *Slow 3G* throttle once in a while.

## Checklist

- [ ] You can write fetch with `async/await`.
- [ ] You render loading, error, and success states distinctly.
- [ ] You have used `AbortController` once.
- [ ] You have tried React Query or SWR.
- [ ] You have tested under Slow 3G.

## Practice Problems

1. Call `https://jsonplaceholder.typicode.com/users` and render the user list.
2. Add explicit loading and error states.
3. Add a search box; ensure that fast typing only renders *the latest input's result*.

## Wrap-up and Next Steps

Async is *state*. Next, we look at handling *user input* via forms and validation.

## Answering the Opening Questions

- **Why is async UI easier to reason about when loading, success, and failure are explicit screen states?**
  - Once each state has a visible UI, the user never has to guess whether the app is waiting, broken, or finished. It also gives the developer a much cleaner mental model than sprinkling `setState` calls through promise chains.
- **What race conditions appear when requests overlap or a screen unmounts mid-request?**
  - Older responses can overwrite newer input, and unmounted components can still try to update state if the request is not canceled. That is why `AbortController` and request ownership rules matter even in small apps.
- **Which checks turn a simple `fetch` demo into production-safe frontend behavior?**
  - Check `res.ok`, render an error state the user can see, cancel stale requests, and test under throttled network conditions. Those four checks catch many of the failures that stay invisible on a fast local machine.

<!-- toc:begin -->
## In this series

- [Frontend Development 101 (1/10): What Is Frontend Development?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML and CSS Basics](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript Basics](./03-javascript-basics.md)
- [Frontend Development 101 (4/10): Components and State](./04-components-and-state.md)
- [Frontend Development 101 (5/10): Routing and Pages](./05-routing-and-pages.md)
- **API Calls and Async (current)**
- Forms and Validation (upcoming)
- Styling and Design Systems (upcoming)
- Build Tools and Bundling (upcoming)
- Building a Small Frontend App (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [MDN: Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [MDN: AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController)
- [TanStack Query docs](https://tanstack.com/query/latest)

### Verification and Further Reading
- [SWR documentation](https://swr.vercel.app/)
- [web.dev: Fetch API error handling](https://web.dev/articles/fetch-api-error-handling)

Tags: Frontend, API, Async, Fetch, JavaScript
