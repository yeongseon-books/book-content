---
series: frontend-development-101
episode: 4
title: "Frontend Development 101 (4/10): Components and State"
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
  - React
  - Components
  - State
  - JavaScript
seo_description: Components, props, state, unidirectional data flow — the core mental model behind every modern frontend framework.
last_reviewed: '2026-05-04'
---

# Frontend Development 101 (4/10): Components and State

A small screen can survive on a few lines of JavaScript and direct DOM manipulation. As the screen grows, that approach collapses under its own weight. Logic piles into one file, every change feels risky, and reading the code becomes harder than writing the next feature.

This is the 4th post in the Frontend Development 101 series. Here we introduce components and state as the basic structure that keeps growing screens readable. The goal is simple: split the UI into small functions, and let each function own only the input and state it is responsible for.


![frontend development 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/04/04-01-concept-at-a-glance.en.png)
*frontend development 101 chapter 4 flow overview*

## Questions to Keep in Mind

- When should a growing screen be split into components instead of staying in one file?
- How do props and state divide responsibility inside a component tree?
- Why does one-way data flow make larger frontend screens easier to change?

## What You Will Learn

- The *component mindset*

- The *clear distinction* between props and state
- Unidirectional data flow
- *When to split* a component
- A minimal React example

## Why It Matters

The component mindset is not exclusive to React. The same pattern works in Vue, Svelte, Angular, and even *plain JS*. Once you internalize it, *every framework reads like a familiar language*.

> Well-split components exist for *readability*, not for *reuse*.

State flows *down*, events flow *up*.

## Key Terms

- **Component**: a function that draws *one slice* of the screen.
- **Props**: values *passed down* from parent. *Read-only*.
- **State**: a mutable value a component *holds itself*.
- **Unidirectional data flow**: data moves *only top-down*.
- **Lifting state up**: when two children share state, *move it up to the parent*.

## From One Big Script to Component Boundaries

A screen can work for a while as one large file of DOM manipulation, but that approach collapses once multiple people and multiple features touch the same view. Components are not just a framework preference. They are a way to give every part of the screen a small, readable job.

**One file owns everything**

```html
<script>
  // 1000 lines of DOM manipulation
</script>
```

**Components split responsibilities**

```jsx
function App()    { ... }
function Header() { ... }
function List()   { ... }
function Item()   { ... }
```

The point of the second structure is not beauty. It is changeability. Once each component owns one responsibility, props and state have somewhere clear to live, and refactoring stops feeling like surgery on the whole page.

## Hands-on: A React Counter in Five Steps

### Step 1 — Project

```bash
npm create vite@latest counter -- --template react
cd counter && npm install && npm run dev
```

### Step 2 — Define a component

```jsx
function Counter({ initial = 0 }) {
  return <button>{initial}</button>;
}
```

### Step 3 — Add state

```jsx
import { useState } from "react";

function Counter({ initial = 0 }) {
  const [count, setCount] = useState(initial);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

### Step 4 — Use it from the parent

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

### Step 5 — Lift state up

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

## Verification

- Render two counters and confirm that each instance increments independently before you try a lifted-state version.
- After lifting state up, verify that the shared total updates consistently everywhere the parent renders it.

## If It Fails, Check This First

- If state never changes, confirm the `useState` import and make sure the setter runs inside the click handler.
- If parent and child fall out of sync, re-check where the state lives and whether the prop names still match.

## Practical Debug Loop

Component bugs often look mysterious until you label them as either ownership bugs or rendering bugs.

1. **Props ownership** - verify which component should own the value before adding more state.
2. **Render trigger** - confirm that the state setter actually runs and that the new value reaches the child tree.
3. **Shared state** - if two widgets drift apart, move one level up and inspect whether the real source of truth already exists in the parent.

```jsx
useEffect(() => {
  console.log("count changed:", count);
}, [count]);
```

Expected outcome: you can answer three questions clearly - where the value lives, who is allowed to change it, and which render should happen after the change. That is the shortest route out of most component-state confusion.

## What to Notice in This Code

- `props` are *input*; `state` is *internal memory*.
- A child mutates parent state by receiving a *function* as a prop.
- The same component can live as *multiple instances*.

## Five Common Mistakes

1. **Mutating props inside the component.** Props are *read-only*.
2. **Putting all state at the top.** Unnecessary *globalization* hurts performance and readability.
3. **Letting a component grow past *a thousand lines*.** Past 200 lines is a *split signal*.
4. **Recreating event callbacks every render.** Causes needless child re-renders.
5. **Storing both state and derived values.** You end up with *two sources of truth*.

## How This Shows Up in Production

Most companies maintain a *design system* as a component library. New screens are built by *composing* base components like Button + Input + Card. A senior engineer's job is deciding *which components NOT to build*.

## How a Senior Engineer Thinks

- Components should be *small* — *only when they correspond to meaningful units*.
- Place state at the *closest common parent*.
- Two components that *look identical* deserve a second thought before merging.
- Cyclic data flow is a sign of *bad design*.
- *Readable* components beat *reusable* ones.

## Checklist

- [ ] You can define a component as a function.
- [ ] You distinguish props from state.
- [ ] You can bubble events from child to parent.
- [ ] You can place state in the *right* location.
- [ ] You can sketch unidirectional data flow.

## Practice Problems

1. Build a todo app split into `<TodoItem>`, `<TodoList>`, `<App>`.
2. Apply lifting state up so two counters share *the same total*.
3. Build a *pure presentational component* that only takes props, and write a unit test for it.

## Wrap-up and Next Steps

Components and state make screens *composable*. Next, we connect multiple screens via *URLs and routers*.

## Answering the Opening Questions

- **When should a growing screen be split into components instead of staying in one file?**
  - Split when one file starts mixing unrelated responsibilities such as layout, data fetching, input handling, and presentation details. A useful rule is that each component should represent one meaningful slice of the screen.
- **How do props and state divide responsibility inside a component tree?**
  - Props are read-only input coming from the parent, while state is the local memory a component owns itself. Once you keep that distinction sharp, it becomes much easier to reason about where each value should change.
- **Why does one-way data flow make larger frontend screens easier to change?**
  - One-way flow gives the team a predictable path: parents pass data down, children communicate back through events or callbacks. That predictability removes hidden side effects and makes debugging much faster.

<!-- toc:begin -->
## In this series

- [Frontend Development 101 (1/10): What Is Frontend Development?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML and CSS Basics](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript Basics](./03-javascript-basics.md)
- **Components and State (current)**
- Routing and Pages (upcoming)
- API Calls and Async (upcoming)
- Forms and Validation (upcoming)
- Styling and Design Systems (upcoming)
- Build Tools and Bundling (upcoming)
- Building a Small Frontend App (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [React: Thinking in React](https://react.dev/learn/thinking-in-react)
- [React: Sharing state between components](https://react.dev/learn/sharing-state-between-components)
- [Vue: Component basics](https://vuejs.org/guide/essentials/component-basics.html)

### Verification and Further Reading
- [Svelte tutorial](https://svelte.dev/tutorial)
- [React: State as a snapshot](https://react.dev/learn/state-as-a-snapshot)

Tags: Frontend, React, Components, State, JavaScript
