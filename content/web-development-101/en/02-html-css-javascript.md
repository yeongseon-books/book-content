---
series: web-development-101
episode: 2
title: "Web Development 101 (2/10): HTML, CSS, and JavaScript"
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
  - HTML
  - CSS
  - JavaScript
  - Frontend
seo_description: The three pillars of every web page — structure, style, and behavior — explained side by side with runnable examples for new web developers.
last_reviewed: '2026-05-15'
---

# Web Development 101 (2/10): HTML, CSS, and JavaScript

At first glance, splitting one page across three languages can feel like unnecessary ceremony. In practice, though, every production frontend becomes easier to debug once you can answer three separate questions: what is the structure, what controls the visual result, and what changes behavior after the page loads.

This is the 2nd post in the Web Development 101 series. Here we separate structure, style, and behavior on purpose so you can see why maintainable frontend code starts with clear responsibility boundaries rather than clever framework tricks.


![web development 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/02/02-01-concept-at-a-glance.en.png)
*web development 101 chapter 2 flow overview*

## Questions to Keep in Mind

- The *structure* HTML draws?
- The *style* CSS applies?
- The *behavior* JavaScript adds?

## Why It Matters

When all three live in one file, fixing one line breaks another. *Separation* is the starting point of teamwork and maintenance — designers touch CSS, frontend engineers touch JS, content owners touch HTML.

> Good web code keeps roles separate.

The point of this figure is not that three files are trendy. It is that one visible page is easier to change when structure, visual rules, and runtime behavior can move independently.

### What to verify yourself

- Open an HTML file without CSS or JS and confirm that the structure still exists.
- Attach the stylesheet and verify that only presentation changes.
- Attach the JavaScript file and confirm that behavior changes without rewriting the markup.

**Expected output:** HTML defines the page skeleton, CSS changes appearance, and JavaScript changes behavior without needing the other layers to absorb every edit.

**Failure mode to watch for:** If style and behavior are embedded directly into the markup, even a small change becomes harder to review, cache, and debug.

## Key Terms

- **HTML**: meaningful *structure* (headings, paragraphs, links, forms).
- **CSS**: visible *style* (colors, fonts, layout).
- **JavaScript**: dynamic *behavior* (clicks, input, async calls).
- **Selector**: rule that picks where CSS applies.
- **Event**: signal that lets JS react to user input.

## Before/After

**Before (everything mixed)**

```html
<h1 style="color:red" onclick="alert('hi')">Title</h1>
```

**After (roles separated)**

```html
<h1 class="title">Title</h1>
```

```css
.title { color: red; }
```

```js
document.querySelector(".title").addEventListener("click", () => alert("hi"));
```

Same result, *much easier to change*.

## Hands-on: Build a Separated Page in 5 Steps

### Step 1 — Basic HTML structure

```html
<!-- index.html -->
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Hello</title>
    <link rel="stylesheet" href="style.css">
  </head>
  <body>
    <h1 class="title">Hello there</h1>
    <button id="say">Greet</button>
    <script src="app.js" defer></script>
  </body>
</html>
```

### Step 2 — Add style with CSS

```css
/* style.css */
body { font-family: system-ui; }
.title { color: steelblue; }
button { padding: 8px 16px; }
```

### Step 3 — Add behavior with JS

```js
// app.js
document.getElementById("say").addEventListener("click", () => {
  alert("Nice to meet you");
});
```

### Step 4 — Open in a browser

```bash
python3 -m http.server 8000
# Open http://localhost:8000
```

### Step 5 — Inspect the tree

```text
F12 → Elements tab → see DOM tree and applied styles
```

## What to Notice in This Code

- HTML `class` and `id` are the *hooks* CSS and JS use.
- `defer` makes JS run after HTML parsing finishes.
- CSS *cascades* — multiple rules merge by priority.

## Five Common Mistakes

1. **Overusing `style="..."` inline.** The CSS file becomes pointless.
2. **Big `<script>` blocks inside HTML.** Hurts readability and caching.
3. **Reusing the same `id` on many elements.** An `id` must be unique on a page.
4. **Ignoring CSS specificity.** Reaching for `!important` to win the fight.
5. **Manipulating styles only with JS.** Toggling a CSS class is simpler.

## How This Shows Up in Production

Even huge sites reduce to these three languages. React and Vue are tools that ultimately produce *HTML, CSS, and JS* for the browser. Understanding the separation principle keeps you grounded in any framework.

## How a Senior Engineer Thinks

- Write *meaningful* HTML first (semantic tags).
- Style with *reusable* classes.
- Keep JS responsible for *behavior only*.
- Consider accessibility from the start.
- Design so a single change happens in one place.

## Checklist

- [ ] You can name each language's responsibility in one sentence.
- [ ] You know the difference between inline and external CSS.
- [ ] You can read the DOM tree and CSS rules in DevTools.
- [ ] You know the difference between `defer` and `async`.
- [ ] You can refactor mixed code into separated files.

## Practice Problems

1. Take an HTML file full of inline styles and move them into a CSS file.
2. Build five buttons that toggle background color via a CSS class.
3. Pick a favorite site and find five *semantic tags* in its HTML.

## Wrap-up and Next Steps

Three languages model the principle of *separation of concerns*. Next, we look at how the browser turns HTML into a tree (the DOM).

## Answering the Opening Questions

- **The *structure* HTML draws?**
  - The article treats HTML, CSS, and JavaScript as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **The *style* CSS applies?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **The *behavior* JavaScript adds?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Web Development 101 (1/10): How the Web Works](./01-how-the-web-works.md)
- **HTML, CSS, and JavaScript (current)**
- The Browser and the DOM (upcoming)
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
- [HTML basics (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Your_first_website/Creating_the_content)
- [CSS basics (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Your_first_website/Styling_the_content)
- [JavaScript basics (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Your_first_website/Adding_interactivity)

### Deepen the Model
- [Semantic HTML (MDN)](https://developer.mozilla.org/en-US/docs/Glossary/Semantics)
- [The `script` element: `defer` and `async` (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/script)

Tags: Computer Science, WebDevelopment, HTML, CSS, JavaScript, Frontend
