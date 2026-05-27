---
series: frontend-development-101
episode: 2
title: "Frontend Development 101 (2/10): HTML and CSS Basics"
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
  - HTML
  - CSS
  - Web
  - Beginner
seo_description: Semantic HTML, the box model, Flexbox and Grid — the long-lived fundamentals that shape every page.
last_reviewed: '2026-05-04'
---

# Frontend Development 101 (2/10): HTML and CSS Basics

One lesson shows up quickly when you study frontend work: building a screen fast and building a screen that survives real product growth are not the same thing. You can ship something quickly with random tags and one-off styles, but maintenance gets expensive as soon as the layout changes, accessibility matters, or another teammate joins the codebase.

This is the 2nd post in the Frontend Development 101 series. Here we treat HTML as the page skeleton and CSS as the rule system layered on top of that skeleton. Keeping meaning in HTML and appearance in CSS is what makes layout, accessibility, and SEO improve together instead of fighting each other later.


![frontend development 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/02/02-01-concept-at-a-glance.en.png)
*frontend development 101 chapter 2 flow overview*

## Questions to Keep in Mind

- Why is semantic HTML a design decision, not just a style preference?
- Why does the box model explain so many CSS bugs faster than visual guessing?
- When should you reach for Flexbox, and when does Grid describe the layout more directly?

## What You Will Learn

- Building *meaningful structure* with semantic HTML
- The CSS box model
- *Where Flexbox shines and where Grid shines*

- A *minimal pattern* for responsive design
- The *starting point* for accessibility

## Why It Matters

HTML and CSS are *long-lived skills*. Frameworks rotate every five years, but *semantic tags and the box model* stay. Time spent here is the *highest-yield investment* in your frontend career.

> Semantic HTML is code that *search engines and screen readers can read together*.

## Key Terms

- **Semantic HTML**: tags like `<header>`, `<nav>`, `<article>` that *carry meaning*.
- **Box model**: every element is *content + padding + border + margin*.
- **Flexbox**: a *one-axis* layout system.
- **Grid**: a *two-axis* layout system that divides regions.
- **Media query**: syntax that applies *different styles* per screen size.

## From Presentational Markup to Meaningful Structure

Two pages can look almost identical in the browser and still have very different long-term quality. A page built from generic containers can be hard to navigate for assistive tools and hard to reason about for teammates. A page built from semantic elements carries its structure in the markup itself.

**Presentational markup**

```html
<div class="header">
  <div class="nav">...</div>
</div>
<div class="content">...</div>
```

**Semantic structure**

```html
<header><nav>...</nav></header>
<main>...</main>
<footer>...</footer>
```

The visible layout may be similar, but the second version communicates intent. Search engines, screen readers, and future maintainers can tell where navigation stops and main content begins. That is why semantic HTML belongs in the architecture discussion, not just the polishing phase.

## Hands-on: A Card Layout in Five Steps

### Step 1 — Semantic structure

```html
<main>
  <article class="card">
    <h2>Title</h2>
    <p>Body</p>
  </article>
</main>
```

### Step 2 — Apply the box model

```css
.card {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 1rem;
}
```

### Step 3 — Flexbox row

```css
main {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
.card { flex: 1 1 250px; }
```

### Step 4 — Grid regions

```css
main {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}
```

### Step 5 — Media query

```css
@media (max-width: 600px) {
  main { grid-template-columns: 1fr; }
}
```

## Verification

- Resize the browser under 600px and verify that the card layout collapses to a single column.
- Inspect the DOM in DevTools Elements to confirm that semantic tags such as `<main>` and `<article>` describe the page structure you intended.

## If It Fails, Check This First

- If the layout does not change, verify that the media query condition and selector names match the actual HTML.
- If spacing feels wrong, inspect `gap`, `padding`, and `margin` in the box model instead of guessing from the visual result.

## Practical Debug Loop

HTML/CSS bugs usually become easier once you stop looking at the page as a picture and start checking structure, box model, and layout rules separately.

1. **Structure** - in the Elements panel, verify that the semantic tag you expect really wraps the correct content.
2. **Spacing** - inspect the box model to see whether the extra gap comes from `margin`, `padding`, or an inherited `display` rule.
3. **Layout system** - confirm whether the container is actually using `display: flex` or `display: grid` before changing child styles.

```css
/* Temporary debugging rule */
* { outline: 1px solid rgba(255, 0, 0, 0.2); }
```

Expected outcome: you can point to the exact element whose box is wrong and explain whether the bug comes from semantics, spacing, or layout mode. That discipline prevents the classic "change five CSS rules and hope" debugging style.

## What to Notice in This Code

- Use *role-based class names* like `card`, not `red`.
- `gap` removes *margin collision* problems.
- `minmax(250px, 1fr)` is the *responsive magic*.

## Five Common Mistakes

1. **Using only `<div>`.** Search engines and screen readers *cannot read structure*.
2. **Spamming `!important`.** CSS specificity becomes *chaos*.
3. **Using only fixed `px`.** Mix `rem`, `%`, `fr` to keep responsive flow.
4. **Carrying information in color alone.** *Color-blind* users miss it.
5. **Leaving alt text empty.** Meaningful images *need alt*.

## How This Shows Up in Production

Most companies adopt a *design system* (Tailwind, Material UI, custom tokens) for reuse. But every design system *runs on* semantic HTML and Flexbox/Grid underneath. Skipping fundamentals makes design systems *un-debuggable*.

## How a Senior Engineer Thinks

- *Semantic tags* are the cheapest SEO/accessibility investment.
- Most layout problems reduce to *Flexbox vs Grid*.
- Design *mobile-first*, then scale up.
- Color must *not be the only* signal.
- Always ask: "*Why* did I make this a div?"

## Checklist

- [ ] You use `<header>`, `<main>`, `<footer>` correctly.
- [ ] You can sketch the box model.
- [ ] You can describe Flexbox vs Grid in one sentence.
- [ ] You can add a media query for responsiveness.
- [ ] All images have meaningful `alt`.

## Practice Problems

1. Build a business card with semantic HTML and CSS.
2. Lay out three cards once with Flexbox, once with Grid. Note the difference.
3. Add a media query so the layout collapses to one column under 600 px.

## Wrap-up and Next Steps

HTML is *the skeleton*; CSS is *the clothes*. With the two clearly separated, behavior — JavaScript — slots in cleanly. We tackle JavaScript fundamentals next.

## Answering the Opening Questions

- **Why is semantic HTML a design decision, not just a style preference?**
  - Semantic tags such as `<header>`, `<main>`, and `<article>` make the structure of the page explicit. That improves accessibility, helps search engines understand the document, and gives the team a cleaner foundation than a tree of anonymous `<div>` elements.
- **Why does the box model explain so many CSS bugs faster than visual guessing?**
  - Most spacing and alignment problems come from misunderstanding which part of the box is growing: content, padding, border, or margin. When you inspect the box model in DevTools, you can stop guessing and identify whether the issue is inner spacing, outer spacing, or layout flow.
- **When should you reach for Flexbox, and when does Grid describe the layout more directly?**
  - Flexbox is usually the clearest choice when content flows mainly along one axis, such as rows of cards or navigation items. Grid becomes clearer when you need to control rows and columns together, especially for dashboard-like layouts or responsive card matrices.

<!-- toc:begin -->
## In this series

- [Frontend Development 101 (1/10): What Is Frontend Development?](./01-what-is-frontend-development.md)
- **HTML and CSS Basics (current)**
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
- [MDN: HTML elements reference](https://developer.mozilla.org/en-US/docs/Web/HTML/Element)
- [MDN: CSS box model](https://developer.mozilla.org/en-US/docs/Learn/CSS/Building_blocks/The_box_model)
- [MDN: Basic concepts of flexbox](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_flexible_box_layout/Basic_concepts_of_flexbox)
- [MDN: CSS grid layout](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout)

### Verification and Further Reading
- [web.dev: Responsive web design basics](https://web.dev/articles/responsive-web-design-basics)
- [WAI: Images and alt decisions](https://www.w3.org/WAI/tutorials/images/)

Tags: Frontend, HTML, CSS, Web, Beginner
