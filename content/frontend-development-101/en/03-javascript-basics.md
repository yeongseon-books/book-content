---
series: frontend-development-101
episode: 3
title: "Frontend Development 101 (3/10): JavaScript Basics"
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
  - JavaScript
  - DOM
  - Web
  - Beginner
seo_description: Variables, functions, DOM manipulation, events — the twelve essentials of modern JavaScript in one post.
last_reviewed: '2026-05-04'
---

# Frontend Development 101 (3/10): JavaScript Basics

JavaScript feels endless when you first meet it. There are many array methods, multiple ways to declare functions, and a long list of DOM APIs that all look important. Many beginners lose momentum because they try to memorize the whole language before building anything real.

This is the 3rd post in the Frontend Development 101 series. Here we focus on the five slices that open most frontend work quickly: variables, functions, collection transforms, DOM access, and events. Once those pieces feel natural, framework code stops looking magical.


![frontend development 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/03/03-01-concept-at-a-glance.en.png)
*frontend development 101 chapter 3 flow overview*

## Questions to Keep in Mind

- Why do `const`, functions, and collection methods matter more than memorizing every JavaScript feature?
- How does data move from state into the DOM and back again through events?
- Which JavaScript habits keep a small script from turning into fragile frontend code?

## What You Will Learn

- `let`/`const` and *immutable thinking*

- Functions, arrow functions, and a *minimal grasp* of closures
- Array/object methods (`map`, `filter`, `reduce`)
- Reading and updating the DOM
- *The standard pattern* for event listeners

## Why It Matters

JavaScript stays the same *across frameworks*. Inside React components, inside Vue, inside Node.js — the *syntax is identical*. Time invested here makes *every framework faster to learn*.

> Good JavaScript is a sum of *small, separated functions*.

## Key Terms

- **`const`**: cannot be reassigned. Use it *by default*.
- **Arrow function**: `() => {}`, the short form.
- **Closure**: a function remembers *the environment in which it was created*.
- **`map/filter/reduce`**: standard tools to transform collections *without for-loops*.
- **Event delegation**: attach the listener *to the parent* and handle child events from there.

## From Loops and Mutation to Declarative JavaScript

Older frontend JavaScript often grows around mutable variables and hand-written loops. Modern JavaScript still does the same work, but it expresses intent more directly: transform the collection, then render the result. That difference matters because frontend code is usually read far more often than it is written.

**Loop-first code with mutable state**

```javascript
var arr = [1,2,3];
var doubled = [];
for (var i = 0; i < arr.length; i++) doubled.push(arr[i] * 2);
```

**Declarative collection transform**

```javascript
const arr = [1, 2, 3];
const doubled = arr.map(n => n * 2);
```

The newer version is not just shorter. It makes the transformation rule obvious, which is exactly what you want when event handlers, DOM updates, and async calls start piling into the same file.

## Hands-on: A Todo List in Five Steps

### Step 1 — HTML skeleton

```html
<input id="todo">
<button id="add">Add</button>
<ul id="list"></ul>
```

### Step 2 — State variable

```javascript
const todos = [];
```

### Step 3 — A render function

```javascript
function render() {
  const list = document.getElementById("list");
  list.innerHTML = todos.map(t => `<li>${t}</li>`).join("");
}
```

### Step 4 — Events

```javascript
document.getElementById("add").addEventListener("click", () => {
  const input = document.getElementById("todo");
  if (!input.value) return;
  todos.push(input.value);
  input.value = "";
  render();
});
```

### Step 5 — Delete via event delegation

```javascript
document.getElementById("list").addEventListener("click", (e) => {
  if (e.target.tagName === "LI") {
    const idx = [...e.target.parentNode.children].indexOf(e.target);
    todos.splice(idx, 1);
    render();
  }
});
```

## Verification

- Confirm that clicking Add appends an item without a reload and that clicking an item removes it through event delegation.
- Use DevTools Console to verify that the `todos` array stays in sync with what is rendered in the DOM.

## If It Fails, Check This First

- If the UI does not update, check whether `render()` is called after each state change and whether `getElementById()` returned `null`.
- If deletion removes the wrong item, inspect the event target and confirm that the index calculation still matches the current DOM structure.

## Practical Debug Loop

Plain JavaScript starts to feel reliable when you can inspect data, render output, and event flow separately instead of treating them as one blur.

1. **State** - log the data structure before and after the user action.
2. **Render** - confirm that `render()` is called after each state mutation.
3. **Event path** - inspect `event.target` when clicks do not land where you expect.

```javascript
console.table(todos);
document.getElementById("list").addEventListener("click", (event) => {
  console.log("clicked:", event.target.tagName);
});
```

Expected outcome: you can explain whether the bug is a state bug, a render bug, or an event-target bug before you edit the code. That is the same discipline frameworks demand later; you are just practicing it without abstraction first.

## What to Notice in This Code

- State (`todos`) and rendering (`render`) are *separated*.
- Every change flows *state → render*. (A *taste* of the React paradigm.)
- A single listener on the parent is more efficient than one per child.

## Five Common Mistakes

1. **Using `var`.** Function-scoped behavior creates bugs. Use `const`/`let`.
2. **Using `==`.** Type coercion makes results *unpredictable*. Use `===`.
3. **Updating state and DOM in parallel.** You lose track of *the source of truth*.
4. **Attaching a listener to every element.** Wastes memory and CPU.
5. **Not handling errors inside `async`.** Bugs that *fail silently* appear.

## How This Shows Up in Production

Most teams standardize on *TypeScript*, *ESLint*, and *Prettier*. JavaScript's freedom becomes a *risk* at team scale, so types and lint rules draw the *boundaries*. Yet all of those tools *run on top of* plain JS.

## How a Senior Engineer Thinks

- A function does *one thing*.
- Separate state from rendering.
- `const` by default; `let` by exception; `var` never.
- Flatten callback hell with `async/await`.
- *Reading* JavaScript takes longer than writing it.

## Checklist

- [ ] You know the difference between `let` and `const`.
- [ ] You can write arrow functions.
- [ ] You replace for-loops with `map/filter/reduce`.
- [ ] You can read and modify the DOM.
- [ ] You have used event delegation at least once.

## Practice Problems

1. Add a *complete (check)* feature to the todo code above.
2. Persist todos across reloads using `localStorage`.
3. Compute an average grade using only `map/filter/reduce`.

## Wrap-up and Next Steps

Plain JavaScript can build small apps on its own. As the screen grows, you need a tool that *binds state to rendering* automatically. Next up: components and state.

## Answering the Opening Questions

- **Why do `const`, functions, and collection methods matter more than memorizing every JavaScript feature?**
  - Those tools cover the majority of day-to-day frontend work: storing values safely, packaging behavior into small functions, and transforming data before it reaches the UI. Once those feel natural, larger APIs stop feeling random.
- **How does data move from state into the DOM and back again through events?**
  - In the todo example, state lives in `todos`, `render()` turns that state into DOM, and click events mutate state before calling `render()` again. That state -> DOM -> event -> state loop is the core frontend rhythm.
- **Which JavaScript habits keep a small script from turning into fragile frontend code?**
  - Prefer `const`, isolate one responsibility per function, keep state separate from rendering, and use patterns such as event delegation when the DOM grows. Those habits make later framework code feel like an extension of the same mental model.

<!-- toc:begin -->
## In this series

- [Frontend Development 101 (1/10): What Is Frontend Development?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML and CSS Basics](./02-html-and-css-basics.md)
- **JavaScript Basics (current)**
- Components and State (upcoming)
- Routing and Pages (upcoming)
- API Calls and Async (upcoming)
- Forms and Validation (upcoming)
- Styling and Design Systems (upcoming)
- Build Tools and Bundling (upcoming)
- Building a Small Frontend App (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [MDN: JavaScript guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [MDN: Introduction to the DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction)
- [MDN: Event bubbling](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling)

### Verification and Further Reading
- [JavaScript.info](https://javascript.info/)
- [TC39 proposals](https://github.com/tc39/proposals)

Tags: Frontend, JavaScript, DOM, Web, Beginner
