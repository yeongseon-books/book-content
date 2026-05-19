---
series: frontend-development-101
episode: 9
title: Build Tools and Bundling
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
  - Build
  - Vite
  - Bundling
  - Performance
seo_description: Vite, esbuild, tree shaking, and bundle analysis — an introduction to how modern frontend build tools work and how to keep output small.
last_reviewed: '2026-05-04'
---

# Build Tools and Bundling

During development, frontend code lives as dozens or hundreds of separate files. Browsers do not consume that source tree directly. Something has to resolve the import graph, transform the syntax, split the output, and emit files that are fast to download and easy to cache. That "something" is the build toolchain.

This is post 9 in the Frontend Development 101 series. Here we treat build tools as a performance layer, not just as developer convenience. The shape of the bundle is one of the clearest predictors of how quickly a user sees and uses the first screen.

## What You Will Learn

- The *role* of a bundler (module graph, transform, split)
- *Why* Vite and esbuild are fast
- Tree shaking and dead code elimination
- Finding *large modules* with bundle analysis
- Building per environment and basic optimization

## Why It Matters

Bundle size is paid *directly* by your users. A 1MB bundle is *eight seconds of white screen* on a 3G connection. If you do not understand the build tool, you will not understand *why your product gets heavy*.

> A good bundle is *small, cacheable, and split*.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/09/09-01-concept-at-a-glance.en.png)

*How source files move through resolve, transform, bundle, and output stages*

## Key Terms

- **Module bundler**: a tool that *follows the import graph* and merges files.
- **Tree shaking**: an optimization that *drops* unused exports.
- **Code splitting**: cutting one bundle into *multiple chunks*.
- **Source map**: the mapping that lets you debug built code *as the original*.
- **HMR (Hot Module Replacement)**: applying changes during development *without a full page reload*.

## Before/After

**Before (dozens of `<script>` tags)**

```html
<script src="utils.js"></script>
<script src="auth.js"></script>
<script src="app.js"></script>
```

**After (one `<script>` plus automatic split)**

```html
<script type="module" src="/dist/index-[hash].js"></script>
```

## Hands-on: Vite in Five Steps

### Step 1 — Create the project

```bash
npm create vite@latest my-app -- --template react-ts
cd my-app && npm install
```

### Step 2 — Dev server (HMR)

```bash
npm run dev
# Browser: http://localhost:5173
# The page updates *automatically* on code changes
```

### Step 3 — Production build

```bash
npm run build
# Static files appear in dist/
ls -lh dist/assets
```

### Step 4 — Bundle analysis

```bash
npm install -D rollup-plugin-visualizer
```

```javascript
// vite.config.ts
import { visualizer } from "rollup-plugin-visualizer";
export default {
  plugins: [visualizer({ open: true })],
};
```

After the build, *see which modules are large* visually.

### Step 5 — Environment variables and modes

```bash
# .env.production
VITE_API_URL=https://api.example.com

# In code
const url = import.meta.env.VITE_API_URL;
```

## Verification

- Run `npm run build` and confirm that `dist/assets` contains hashed output files rather than raw source names.
- Run the bundle analyzer and identify the largest module so you have a concrete optimization target before tuning anything else.

## If It Fails, Check This First

- If `import.meta.env` is undefined, confirm the `VITE_` prefix and the location of `.env.production`.
- If the bundle is unexpectedly large, inspect full-library imports, large images, and source-map exposure before chasing smaller details.

## What to Notice in This Code

- The dev server serves *ESM directly*, so *startup is fast*.
- Build output filenames carry a *hash*, so they are *cacheable forever*.
- Bundle analysis is *the starting point of optimization*.

## Five Common Mistakes

1. **Doing `import * as _ from "lodash"`.** All of lodash lands in the bundle. Use `import debounce from "lodash/debounce"` for *per-function imports*.
2. **Assuming dev server and production build behave the *same*.** HMR code and source maps are heavy *if they reach production*.
3. **Never *analyzing the bundle*.** You will not know which library takes *4MB*.
4. **Exposing *source maps in production*.** Original code becomes *fully readable*.
5. **Bundling *unoptimized images*.** A 1MB image goes *as is* to the user.

## How This Shows Up in Production

Most new projects use a *Vite + esbuild + SWC* stack. Larger monorepos are gradually moving to next-gen bundlers like *Turbopack/Rspack*. *Webpack* is still common but is slowly disappearing from *the default choice* for new projects.

## How a Senior Engineer Thinks

- Treats bundle size as a *budget* (for example, main < 200KB).
- Looks at *bundle analysis weekly*.
- Checks *the size of a library* before adding it.
- Sends images and fonts through a separate *optimization pipeline*.
- Uses the *slowest user as the reference*.

## Checklist

- [ ] You can scaffold a Vite project.
- [ ] You confirmed HMR works.
- [ ] You inspected the files inside `dist/`.
- [ ] You ran a bundle analyzer at least once.
- [ ] You can split dev and prod through environment variables.

## Practice Problems

1. Scaffold a React project with Vite, run `npm run build`, and inspect the `dist` folder.
2. Use a bundle analyzer and write down which module is largest.
3. Compare lodash with a *full import* versus *per-function import* and measure the bundle size difference.

## Wrap-up and Next Steps

Build tools decide *how fast the first screen the user sees becomes interactive*. In the final post we will pull every concept so far into *a small frontend app*.

<!-- toc:begin -->
- [What Is Frontend Development?](./01-what-is-frontend-development.md)
- [HTML and CSS Basics](./02-html-and-css-basics.md)
- [JavaScript Basics](./03-javascript-basics.md)
- [Components and State](./04-components-and-state.md)
- [Routing and Pages](./05-routing-and-pages.md)
- [API Calls and Async](./06-api-calls-and-async.md)
- [Forms and Validation](./07-forms-and-validation.md)
- [Styling and Design Systems](./08-styling-and-design-system.md)
- **Build Tools and Bundling (current)**

- Building a Small Frontend App (upcoming)
<!-- toc:end -->

## References

### Official Docs
- [Vite guide](https://vite.dev/guide/)
- [esbuild documentation](https://esbuild.github.io/)
- [web.dev: Tree shaking and code splitting](https://web.dev/reduce-javascript-payloads-with-tree-shaking/)

### Verification and Further Reading
- [Bundlephobia](https://bundlephobia.com/)
- [rollup-plugin-visualizer](https://github.com/btd/rollup-plugin-visualizer)

Tags: Frontend, Build, Vite, Bundling, Performance
