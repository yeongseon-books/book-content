---
series: web-development-101
episode: 3
title: "Web Development 101 (3/10): The Browser and the DOM"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - WebDevelopment
  - Browser
  - DOM
  - JavaScript
  - Frontend
seo_description: How the browser turns HTML into a moving page — DOM tree, the rendering pipeline, and the event loop explained for new web developers.
last_reviewed: '2026-05-15'
---

# Web Development 101 (3/10): The Browser and the DOM

A browser does much more than print HTML on the screen. It parses text into a tree, calculates styles, decides layout, paints pixels, and keeps the page interactive through the event loop. If that pipeline feels vague, performance bugs and UI glitches are hard to reason about.

This is post 3 in the Web Development 101 series. Here we turn the browser into a concrete execution model so DOM updates, rendering costs, and event timing stop feeling magical and start feeling measurable.

## Questions to Keep in Mind

- What the DOM is and how it gets built?
- The stages of the rendering pipeline?
- How JavaScript manipulates the DOM?

## Big Picture

![web development 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/03/03-01-concept-at-a-glance.en.png)

*web development 101 chapter 3 flow overview*

This picture places The Browser and the DOM inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of The Browser and the DOM is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Why It Matters

Without a mental model of the DOM, you will never understand *why your page is slow*. Once the rendering pipeline is in your head, even React and Vue stop feeling like magic.

> The browser is *a machine for drawing the DOM*.

## Concept at a Glance

The browser does not jump from HTML text straight to pixels. It builds internal structures first, and DOM updates can force part of that pipeline to run again, which is why UI work and performance are tightly connected.

### What to verify yourself

- Inspect the DOM tree in the Elements tab and confirm it matches the input HTML structure.
- Record a short interaction in the Performance tab and look for layout or paint work after a DOM mutation.
- Run the `setTimeout(..., 0)` example and compare synchronous log order with callback order.

**Expected output:** DOM changes trigger visible rendering work, and the timeout callback runs after the synchronous logs complete.

**Failure mode to watch for:** Repeated DOM updates inside loops multiply layout cost. Injecting user content through `innerHTML` creates security problems before performance tuning even starts.

## Key Terms

- **DOM (Document Object Model)**: HTML represented as an object tree.
- **Render tree**: DOM plus computed styles.
- **Layout**: computing the position and size of every element.
- **Paint**: drawing pixels.
- **Event loop**: queue system that handles asynchronous work.

## Before/After

**Before (string-style HTML)**

```js
document.body.innerHTML += "<p>new item</p>";
```

**After (DOM API)**

```js
const p = document.createElement("p");
p.textContent = "new item";
document.body.appendChild(p);
```

The DOM API is *safer and faster* — and it blocks XSS by default.

## Hands-on: Working With the DOM in 5 Steps

### Step 1 — Look at the tree

```html
<!-- index.html -->
<ul id="list">
  <li>apple</li>
  <li>pear</li>
</ul>
<script src="app.js"></script>
```

### Step 2 — Select elements

```js
// app.js
const list = document.getElementById("list");
const items = list.querySelectorAll("li");
console.log(items.length);  // 2
```

### Step 3 — Add a new element

```js
const li = document.createElement("li");
li.textContent = "grape";
list.appendChild(li);
```

### Step 4 — Register an event

```js
list.addEventListener("click", (e) => {
  if (e.target.tagName === "LI") {
    console.log("clicked:", e.target.textContent);
  }
});
```

This is *event delegation* — one listener on the parent.

### Step 5 — Compare with async

```js
console.log("1");
setTimeout(() => console.log("2"), 0);
console.log("3");
// Output: 1, 3, 2 — the event loop runs the callback later.
```

## What to Notice in This Code

- DOM mutations are *expensive* (they trigger layout and paint).
- Event delegation saves both memory and time.
- Even `setTimeout(fn, 0)` does not run *immediately*.

## Five Common Mistakes

1. **Using `innerHTML` with user input.** XSS opens up.
2. **Adding DOM nodes one by one in a loop.** Layout fires every time.
3. **Attaching one listener per `<li>`.** No event delegation.
4. **Not knowing *when* JS runs.** `defer` vs `async` vs inline matters.
5. **Assuming the DOM is *synchronous*.** Async callback order surprises you.

## How This Shows Up in Production

React and Vue use a *Virtual DOM* to batch real DOM calls into one update. Infinite scroll, chat apps, browser games — all of them ride on the DOM and the event loop. When something is slow, open Chrome DevTools' *Performance* tab to see layout and paint as flame charts.

## How a Senior Engineer Thinks

- *Batch* DOM calls into one update.
- Delegate events to parents.
- Measure first, then optimize (DevTools Performance).
- Use virtualization for long lists.
- Hunt down code that triggers repaints.

## Checklist

- [ ] You can list the five rendering stages.
- [ ] You can create and attach an element with the DOM API.
- [ ] You use event delegation.
- [ ] You can predict sync vs async order.
- [ ] You know the risks of `innerHTML`.

## Practice Problems

1. Compare adding 100 `<li>` items one by one vs adding them with a `DocumentFragment`. Time both.
2. Attach a single click listener to a parent `<ul>` and log the text of the clicked `<li>`.
3. Predict the output of `console.log("a"); Promise.resolve().then(() => console.log("b")); console.log("c");`.

## Wrap-up and Next Steps

The browser is *a machine for drawing the DOM*. Next, we look at the bridge between client and server: HTTP and APIs.

## Answering the Opening Questions

- **What the DOM is and how it gets built?**
  - The article treats The Browser and the DOM as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **The stages of the rendering pipeline?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How JavaScript manipulates the DOM?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Web Development 101 (1/10): How the Web Works](./01-how-the-web-works.md)
- [Web Development 101 (2/10): HTML, CSS, and JavaScript](./02-html-css-javascript.md)
- **The Browser and the DOM (current)**
- HTTP and APIs (upcoming)
- Frontend and Backend (upcoming)
- Authentication and Sessions (upcoming)
- Connecting to a Database (upcoming)
- Deployment (upcoming)
- Performance and Caching (upcoming)
- Building a Small Web App (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [Introduction to the DOM (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction)
- [Critical rendering path (MDN)](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Critical_rendering_path)
- [Event loop (MDN)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Event_loop)

### Practical Tools
- [Event bubbling and delegation (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling)
- [Performance panel overview (Chrome DevTools)](https://developer.chrome.com/docs/devtools/performance)

Tags: Computer Science, WebDevelopment, Browser, DOM, JavaScript, Frontend
