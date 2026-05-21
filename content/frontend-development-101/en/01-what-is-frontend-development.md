---
series: frontend-development-101
episode: 1
title: "Frontend Development 101 (1/10): What Is Frontend Development?"
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
  - Web
  - JavaScript
  - HTML
  - Beginner
seo_description: Browsers, rendering, and JavaScript — a complete picture of frontend development with a learning roadmap.
last_reviewed: '2026-05-04'
---

# Frontend Development 101 (1/10): What Is Frontend Development?

Most people enter frontend development through the visual door. They see buttons, colors, and layouts, so the work looks like "making screens pretty." That is part of the job, but it is not the whole job. In production, frontend work also includes understanding how the browser renders, how user input becomes state changes, and where the boundary with the backend actually lives.

This is the first post in the Frontend Development 101 series. In this chapter, we treat the frontend as the product layer that runs inside the browser rather than as a pile of UI tweaks. The key mental model is that the frontend draws what users see and directly shapes the speed, trust, and feedback they feel.

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Is Frontend Development??
- Which signal should the example or diagram make visible for What Is Frontend Development??
- What failure should be prevented first when What Is Frontend Development? reaches a real system?

## Big Picture

![frontend development 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/01/01-01-concept-at-a-glance.en.png)

*frontend development 101 chapter 1 flow overview*

This picture places What Is Frontend Development? inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- The *clear boundary* between frontend and backend
- *How a browser draws* a page
- The *distinct roles* of HTML, CSS, and JavaScript
- A bird's-eye view of *modern frontend tooling*

- A learning roadmap

## Why It Matters

*Everything users feel* passes through the frontend. A perfect backend with a slow frontend is *judged as a slow product*. The frontend is the *first and last impression* of your product.

> A great frontend is *invisible*: users just *use it* without thinking.

The browser *combines* the three languages to draw the screen.

## Key Terms

- **DOM**: the *tree structure* the browser builds from HTML.
- **Rendering**: the process of *turning HTML+CSS into pixels*.
- **Bundle**: the *single file* produced from many JS files.
- **SPA (Single Page Application)**: an app whose screen changes *via JS*, with no page reload.
- **Hydration**: the process of *attaching JS behavior* to server-rendered HTML.

## Before/After

**Before (static website, 1995)**

```html
<!-- Each page is its own .html file -->
<a href="/about.html">About</a>
```

**After (modern SPA, 2025)**

```javascript
// A router swaps the screen inside one page
<Link to="/about">About</Link>
```

## Hands-on: Your First Page in Five Steps

### Step 1 — index.html

```html
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Hi</title></head>
<body>
  <h1 id="t">Hello</h1>
  <button id="b">Click me</button>
  <script src="app.js"></script>
</body>
</html>
```

### Step 2 — style.css

```css
body { font-family: system-ui; padding: 2rem; }
button { padding: .5rem 1rem; cursor: pointer; }
```

### Step 3 — app.js

```javascript
document.getElementById("b").addEventListener("click", () => {
  document.getElementById("t").textContent = "Hello, frontend!";
});
```

### Step 4 — Local server

```bash
python3 -m http.server 8000
# Visit http://localhost:8000 in the browser
```

### Step 5 — Open DevTools

Press `F12` and inspect the Elements, Console, and Network tabs to see *what the browser actually received*.

## Verification

- Run `python3 -m http.server 8000`, open the page, and confirm that clicking the button changes the heading text to `Hello, frontend!`.
- Open DevTools Network and verify that the browser really downloads `index.html`, `app.js`, and the related static assets.

## If It Fails, Check This First

- If the button does nothing, check the `app.js` path first and confirm that `id="b"` and `id="t"` still match the DOM.
- If the page looks fine but the interaction fails, inspect the Console for syntax errors or `null` selector references.

## What to Notice in This Code

- HTML is *structure*, CSS is *appearance*, JS is *behavior*.
- The three are *separated*, so each can evolve independently.
- DevTools is the *single most powerful tool* in frontend work.

## Five Common Mistakes

1. **Inlining styles in HTML.** Maintenance becomes *exponentially harder*.
2. **Mixing business logic and DOM manipulation in JS.** Tests become impossible.
3. **Ignoring DevTools.** You debug *with your eyes half-closed*.
4. **Reaching for a framework everywhere.** *React for a simple page* is overkill.
5. **Treating mobile as an afterthought.** Mobile users are *more than half* of traffic.

## How This Shows Up in Production

Most teams use *React/Vue/Svelte* with *TypeScript* and *Vite/Next.js*. Don't try to learn every tool at once: build one page in *plain HTML/CSS/JS*, then move to a framework. That path is *much faster* in practice.

## How a Senior Engineer Thinks

- *Fundamentals* outlive frameworks by years.
- User experience is measured in *milliseconds*.
- If HTML/CSS alone solve it, *don't reach for JS*.
- Accessibility is *cheaper when designed in from day one*.
- *Most answers are inside DevTools*.

## Checklist

- [ ] You can distinguish the roles of HTML, CSS, and JS.
- [ ] You can serve a static page locally.
- [ ] You can open DevTools and use Elements/Console/Network.
- [ ] You can describe what the DOM is.
- [ ] You can explain an SPA in one sentence.

## Practice Problems

1. Build a self-introduction page using only HTML and CSS — no JavaScript.
2. Add a button that updates the text on click.
3. In the DevTools Network tab, count *how many files* are downloaded for one page load.

## Wrap-up and Next Steps

The frontend is *the layer where the product meets the user inside the browser*. Next, we dig into the *foundation* of that layer: HTML and CSS.

## Answering the Opening Questions

- **What boundary should you inspect first when applying What Is Frontend Development??**
  - The article treats What Is Frontend Development? as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for What Is Frontend Development??**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when What Is Frontend Development? reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- **What Is Frontend Development? (current)**
- HTML and CSS Basics (upcoming)
- JavaScript Basics (upcoming)
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
- [MDN: How browsers work](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Performance/How_browsers_work)
- [MDN: Client-side web APIs](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Client-side_web_APIs/Introduction)
- [web.dev: Learn HTML](https://web.dev/learn/html/)

### Verification and Further Reading
- [Chrome DevTools documentation](https://developer.chrome.com/docs/devtools/)
- [Frontend Developer Roadmap](https://roadmap.sh/frontend)

Tags: Frontend, Web, JavaScript, HTML, Beginner
