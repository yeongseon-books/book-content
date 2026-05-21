---
series: frontend-development-101
episode: 10
title: "Frontend Development 101 (10/10): Building a Small Frontend App"
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
  - Project
  - Capstone
  - React
  - Web
seo_description: Pull the routing, components, API calls, forms, and styles from the previous nine posts into one small notes app and deploy it.
last_reviewed: '2026-05-04'
---

# Frontend Development 101 (10/10): Building a Small Frontend App

Knowing each concept in isolation is very different from tying those concepts into one app that someone can actually open and use. Routing, forms, API calls, styling, and build steps all look manageable on their own. The challenge appears when you have to decide where files live, how pieces connect, and what the deployment path looks like end to end.

This is the final post in the Frontend Development 101 series. Here we assemble a small notes app that pulls together the earlier chapters. The goal is not perfection. The goal is to turn separate concepts into one living product flow and ship it all the way to a public URL.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Building a Small Frontend App?
- Which signal should the example or diagram make visible for Building a Small Frontend App?
- What failure should be prevented first when Building a Small Frontend App reaches a real system?

## Big Picture

![frontend development 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/10/10-01-concept-at-a-glance.en.png)

*frontend development 101 chapter 10 flow overview*

This picture places Building a Small Frontend App inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- How to pick a *folder structure* for a small project
- How to *connect* the concepts from posts 1\~9
- The *full flow* of dev → build → deploy
- The next learning steps (testing, devops)

## Why It Matters

Knowledge becomes *yours* only when it is *bound into a project*. The nine posts gave you *bricks*. The final post builds the *house*.

> Polish does not have to be high. The experience of *shipping all the way to deployment* is *more powerful than any book*.

## Key Terms

- **Project structure**: a *folder layout split by role*.
- **Capstone**: the *closing project that ties what you learned*.
- **Deployment**: the act of putting build output *behind a public URL*.
- **Roadmap**: a path showing *what to learn next*.

## Before/After

**Before (you only know the concepts)**

```text
"I know routing, I know forms, I know APIs."
"But I have never combined them all to *build an app*."
```

**After (a small app is alive on the internet)**

```text
https://my-notes.netlify.app
- A user can *add/edit/delete* notes.
- The code is *on GitHub*.
- The next learner studies *on top of this code*.
```

## Hands-on: A Small Notes App in Five Steps

### Step 1 — Project structure

```text
my-notes/
├── src/
│   ├── components/   # NoteCard, NoteForm, ... (post 4)
│   ├── pages/        # NotesPage, NotePage (post 5)
│   ├── api/          # notes API client (post 6)
│   ├── hooks/        # useNotes, useForm (posts 4, 7)
│   ├── styles/       # tokens.css, layout.css (post 8)
│   └── App.tsx
├── vite.config.ts    # build config (post 9)
├── .env.production
└── package.json
```

### Step 2 — Routing and pages (review of post 5)

```typescript
// src/App.tsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import NotesPage from "./pages/NotesPage";
import NotePage from "./pages/NotePage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<NotesPage />} />
        <Route path="/notes/:id" element={<NotePage />} />
      </Routes>
    </BrowserRouter>
  );
}
```

### Step 3 — API client (review of post 6)

```typescript
// src/api/notes.ts
const BASE = import.meta.env.VITE_API_URL;

export async function listNotes() {
  const res = await fetch(`${BASE}/notes`);
  if (!res.ok) throw new Error("Failed to list notes");
  return res.json();
}

export async function createNote(body: { title: string }) {
  const res = await fetch(`${BASE}/notes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error("Failed to create note");
  return res.json();
}
```

### Step 4 — Form + component (review of posts 4 and 7)

```tsx
// src/components/NoteForm.tsx
import { useState } from "react";
import { createNote } from "../api/notes";

export function NoteForm({ onCreated }: { onCreated: () => void }) {
  const [title, setTitle] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (title.trim().length < 2) {
      setError("Title must be at least 2 characters.");
      return;
    }
    await createNote({ title });
    setTitle("");
    setError(null);
    onCreated();
  }

  return (
    <form onSubmit={handleSubmit}>
      <input value={title} onChange={(e) => setTitle(e.target.value)} />
      {error && <p role="alert">{error}</p>}
      <button>Add</button>
    </form>
  );
}
```

### Step 5 — Build and deploy (post 9 + a new step)

```bash
npm run build
# Netlify CLI example
npm install -g netlify-cli
netlify deploy --dir=dist --prod
```

When the deploy finishes you have a *public URL*. Share that URL *with the next person*.

## Verification

- Create a note, return to the list, and confirm that routing, form handling, and API updates all work together as one product flow.
- Run `npm run build`, deploy the result, and verify that the public URL still supports refresh and client-side routing.

## If It Fails, Check This First

- If the deployed app cannot reach the API, check `VITE_API_URL`, CORS configuration, and the visible fetch error path first.
- If another person cannot rerun the project quickly, treat the README and `.env.example` as broken parts of the product, not as optional extras.

## What to Notice in This Code

- The folder layout is split *by role*, so you instantly know *where to edit*.
- The API client is *separated from components*, which makes *testing easy*.
- Environment variables split *dev and prod backends*.

## Five Common Mistakes

1. **Putting all code into `App.tsx`.** Past 100 lines it becomes *unreadable*.
2. **Calling APIs *directly inside components*.** Tests and reuse become *hard*.
3. **Having *no README*.** Future you *cannot run the project* a month later.
4. **Looking only at `localhost` and *never deploying*.** Deployment *always surfaces new issues*.
5. **Waiting *for perfection*.** A small app *deployed today* beats *a perfect undeployed one*.

## How This Shows Up in Production

Production teams use *the same pattern*. Folder structures like `pages/`, `components/`, `api/`, `hooks/`, `styles/` are also the basic skeleton of *codebases shared by dozens of engineers*. The difference is only *scale and abstraction*; *the shape is the same*.

## How a Senior Engineer Thinks

- Builds *small* and ships *often*.
- Lets folder structure *follow the business domain*.
- Always keeps a *README and .env.example*.
- Automates deployment *from day one*.
- Treats the first user as *themselves*.

## Checklist

- [ ] You can sketch the folder structure.
- [ ] You moved API clients *outside components*.
- [ ] `npm run build` succeeds.
- [ ] Your app is live behind a *public URL*.
- [ ] Your README explains *how to run it*.

## Practice Problems

1. Build a *notes app* with this structure and deploy it to Netlify or Vercel.
2. In the README, document *how to run, environment variables, and the deploy URL*.
3. Measure your build output size and *bring it under 200KB*.

## Wrap-up and Next Steps

If you made it here, *frontend onboarding is done*. Good companion series to read next:

- *Testing 101*: how to *test* components and API calls.
- *DevOps 101*: how to *automate deployment* and add monitoring.
- *Secure Coding 101*: how to *block attacks* in forms and APIs.

> Do not try to learn everything at once. *Add one thing at a time* to the app you just built.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Building a Small Frontend App?**
  - The article treats Building a Small Frontend App as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Building a Small Frontend App?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Building a Small Frontend App reaches a real system?**
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
- [Frontend Development 101 (8/10): Styling and Design Systems](./08-styling-and-design-system.md)
- [Frontend Development 101 (9/10): Build Tools and Bundling](./09-build-tools-and-bundling.md)
- **Building a Small Frontend App (current)**

<!-- toc:end -->

## References

### Official Docs
- [Vite guide](https://vite.dev/guide/)
- [React Router documentation](https://reactrouter.com/home)
- [Netlify deploy docs](https://docs.netlify.com/site-deploys/create-deploys/)

### Verification and Further Reading
- [Vercel framework guides](https://vercel.com/docs/frameworks)
- [Create React App alternatives on react.dev](https://react.dev/learn/start-a-new-react-project)

Tags: Frontend, Project, Capstone, React, Web
