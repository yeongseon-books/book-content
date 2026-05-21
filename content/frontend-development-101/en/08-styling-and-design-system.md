---
series: frontend-development-101
episode: 8
title: "Frontend Development 101 (8/10): Styling and Design Systems"
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
  - CSS
  - DesignSystem
  - Tailwind
  - UX
seo_description: CSS Modules, Tailwind, design tokens — keep styling consistent and scalable as projects grow.
last_reviewed: '2026-05-04'
---

# Frontend Development 101 (8/10): Styling and Design Systems

At the start of a project, it feels harmless to hand-pick one color for one button and one spacing value for one card. That convenience disappears as the project and the team grow. Tiny inconsistencies accumulate, dark mode becomes expensive, and the interface starts to feel unfinished even when the logic works.

This is post 8 in the Frontend Development 101 series. Here we look at styling as a system for operating consistency rather than as ad hoc CSS. Colors, spacing, and typography need shared tokens and shared components if the UI is going to stay coherent over time.


![frontend development 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/08/08-01-concept-at-a-glance.en.png)
*frontend development 101 chapter 8 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Styling and Design Systems?
- Which signal should the example or diagram make visible for Styling and Design Systems?
- What failure should be prevented first when Styling and Design Systems reaches a real system?

## What You Will Learn

- A *comparison* of styling approaches (global CSS, CSS Modules, CSS-in-JS, Tailwind)
- The role of *design tokens* (color, spacing, typography)
- The internal structure of a *component library*

- Dark mode and theming
- *Automatically enforcing* consistency

## Why It Matters

Even with consistent code, *inconsistent design* makes users *uneasy*. Buttons that differ per page make a product feel *unfinished*. A design system is *consistency at team scale*.

> A great design system gets *designers and engineers speaking the same language*.

## Key Terms

- **Design token**: an *atomic unit* of color/spacing/typography (e.g., `color.primary.500`).
- **CSS Modules**: makes class names *uniquely scoped automatically*.
- **CSS-in-JS**: write CSS *inside the component function*.
- **Utility-first CSS**: small, composable classes (Tailwind).
- **Component library**: a *reusable set of components* implementing the design system.

## Before/After

**Before (different colors per page)**

```css
.btn-a { background: #1d72ff; }   /* page A */
.btn-b { background: #1d70ff; }   /* page B (typo) */
```

**After (design token)**

```css
:root { --color-primary: #1d72ff; }
.btn  { background: var(--color-primary); }
```

## Hands-on: A Component With Tailwind in Five Steps

### Step 1 — Install Tailwind

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Step 2 — Define tokens

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: { primary: "#1d72ff", surface: "#f8fafc" },
      spacing: { gutter: "1rem" },
    },
  },
};
```

### Step 3 — Button component

```jsx
function Button({ children, variant = "primary" }) {
  const base = "px-4 py-2 rounded font-medium transition";
  const variants = {
    primary:   "bg-primary text-white hover:opacity-90",
    secondary: "bg-surface text-gray-900 border border-gray-200",
  };
  return <button className={`${base} ${variants[variant]}`}>{children}</button>;
}
```

### Step 4 — Dark mode

```jsx
// tailwind.config.js: { darkMode: "class" }
<button className="bg-primary dark:bg-primary/80 text-white">
  Click
</button>
```

### Step 5 — Enforce consistency

```bash
# eslint-plugin-tailwindcss
# Catches arbitrary class names and bad token usage at lint time.
```

## Verification

- Change one token value and confirm that the button and surface styles update together rather than one component at a time.
- Turn on dark mode and verify that contrast and state styles move with the theme instead of remaining hard-coded.

## If It Fails, Check This First

- If only part of the UI changes, search for hard-coded colors or spacing values that bypass the token layer.
- If dark mode does not apply, check the `darkMode` configuration and where the theme class is attached.

## What to Notice in This Code

- All colors appear by *name* (like `primary`) — change in *one place*.
- A component like `Button` is *the single source of truth*.
- Dark mode is *not extra code* — it's *extra tokens*.

## Five Common Mistakes

1. **Hardcoding colors per component.** Designer changes color → *hell*.
2. **Adding button/input variants *without docs*.** Components diverge from *agreed designs*.
3. **Adding dark mode *later*.** Scattered colors mean *every component* needs touching.
4. **Hardcoding *all spacing in px*.** Responsive and accessibility break.
5. **Putting *business logic* in the component library.** Reuse becomes impossible.

## How This Shows Up in Production

Most teams catalog components in *Storybook* and unify styling with *Tailwind/CSS Modules + design tokens*. Big companies publish their *design system as an npm package* so multiple products share the *same components*.

## How a Senior Engineer Thinks

- *Color without a token* gets caught in code review.
- Build the design system *with designers*, not for them.
- New components must answer: *why doesn't an existing one work?*

- Storybook is *unit testing for components*.
- Dark mode should be solved *purely by tokens*.

## Checklist

- [ ] You understand what design tokens mean.
- [ ] You have styled a component with CSS Modules or Tailwind.
- [ ] You have used Storybook once.
- [ ] You have applied dark mode once.
- [ ] You have lint rules to catch arbitrary colors/spacing.

## Practice Problems

1. Define your own `primary` color in Tailwind tokens and apply it to a Button.
2. Install Storybook and catalog two Button variants.
3. Apply dark mode using `prefers-color-scheme` or a class-based switch.

## Wrap-up and Next Steps

Even styling needs *shared vocabulary*. Next, we look at the build tools that turn your code into something *the browser can read*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Styling and Design Systems?**
  - The article treats Styling and Design Systems as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Styling and Design Systems?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Styling and Design Systems reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Frontend Development 101 (1/10): What Is Frontend Development?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML and CSS Basics](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript Basics](./03-javascript-basics.md)
- [Frontend Development 101 (4/10): Components and State](./04-components-and-state.md)
- [Frontend Development 101 (5/10): Routing and Pages](./05-routing-and-pages.md)
- [Frontend Development 101 (6/10): API Calls and Async](./06-api-calls-and-async.md)
- [Frontend Development 101 (7/10): Forms and Validation](./07-forms-and-validation.md)
- **Styling and Design Systems (current)**
- Build Tools and Bundling (upcoming)
- Building a Small Frontend App (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [Tailwind CSS documentation](https://tailwindcss.com/docs/installation)
- [Storybook documentation](https://storybook.js.org/docs)
- [W3C Design Tokens Community Group](https://www.w3.org/community/design-tokens/)

### Verification and Further Reading
- [Material Design 3](https://m3.material.io/)
- [MDN: prefers-color-scheme](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme)

Tags: Frontend, CSS, DesignSystem, Tailwind, UX
