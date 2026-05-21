---
series: frontend-development-101
episode: 10
title: "Frontend Development 101 (10/10): 작은 프론트엔드 앱 만들기"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Frontend
  - Project
  - Capstone
  - React
  - Web
seo_description: 라우팅, API, 폼, 스타일링을 모아 실전 노트 앱을 제작하고 배포합니다. 프로젝트 구조 설계부터 빌드, 배포까지의 전체 흐름을 완주합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (10/10): 작은 프론트엔드 앱 만들기

개념을 따로따로 이해하는 것과 실제 앱으로 끝까지 묶는 것은 완전히 다른 경험입니다. 라우팅도 알고 폼도 알고 API 호출도 이해했는데, 막상 하나의 프로젝트로 합치려면 어디서부터 파일을 나누고 어떤 순서로 조립해야 할지 막막해지는 경우가 많습니다.

이 글은 Frontend Development 101 시리즈의 마지막 글입니다. 여기서는 지금까지 배운 내용을 작은 노트 앱으로 모아 봅니다. 완벽한 앱을 만드는 것이 목표가 아니라, 기초 개념을 하나의 살아 있는 제품 흐름으로 연결해 배포까지 끝내 보는 경험이 목표입니다.

## 먼저 던지는 질문

- 작은 프로젝트에서는 어떤 폴더 구조가 가장 읽기 쉬울까요?
- 앞선 1~9화 개념은 실제 앱 안에서 어떻게 이어질까요?
- 개발, 빌드, 배포 흐름은 어떤 순서로 정리되는 편이 좋을까요?

## 큰 그림

![Frontend Development 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/10/10-01-diagram.ko.png)

*Frontend Development 101 10장 흐름 개요*

## 왜 중요한가

지식은 프로젝트로 묶일 때 비로소 자기 것이 됩니다. 앞선 아홉 개 글이 벽돌이었다면, 마지막 글은 그 벽돌로 실제 집을 짓는 단계입니다. 화면만 그리는 것도 아니고, API 호출만 하는 것도 아니고, 배포만 하는 것도 아닌 전체 흐름이 한 번에 연결됩니다.

완성도가 아주 높지 않아도 괜찮습니다. 작은 앱을 실제 URL 뒤에 올려 보는 경험은 입문 단계에서 가장 강력한 학습 장치입니다.

## 개념 한눈에 보기

이 흐름은 시리즈 전체를 압축한 그림입니다. 사용자는 페이지를 보고, 페이지는 컴포넌트와 상태로 구성되고, 컴포넌트는 API와 스타일 계층을 사용하며, 마지막에는 빌드와 배포를 거쳐 외부에 공개됩니다.

## 핵심 용어

- **프로젝트 구조**: 역할별로 나눈 폴더 레이아웃입니다.
- **Capstone**: 앞에서 배운 내용을 하나로 묶는 마무리 프로젝트입니다.
- **배포(Deployment)**: 빌드 산출물을 공개 URL 뒤에 올리는 작업입니다.
- 로드맵: 다음에 무엇을 배울지 보여 주는 학습 경로입니다.

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

이 차이는 매우 큽니다. 개념만 아는 상태에서는 머릿속 연결이 약하지만, 한 번 앱을 배포하고 나면 라우팅과 폼과 API와 빌드가 하나의 흐름으로 묶입니다.

## 실습: 작은 노트 앱을 5단계로 만들기

### 1단계 — Project structure

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

### 2단계 — Routing and pages (review of post 5)

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

### 3단계 — API client (review of post 6)

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

### 4단계 — Form + component (review of posts 4 and 7)

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

### 5단계 — Build and deploy (post 9 + a new step)

```bash
npm run build
# Netlify CLI example
npm install -g netlify-cli
netlify deploy --dir=dist --prod
```

배포가 끝나면 공개 URL이 생깁니다. 이 URL을 다른 사람에게 공유하는 순간, 연습 프로젝트는 실제 제품 경험으로 한 단계 올라갑니다.

## 검증 포인트

- 노트 목록 화면에서 새 노트를 추가한 뒤 상세 화면으로 이동하고 다시 돌아오는 기본 흐름이 자연스러운지 확인합니다.
- `npm run build`가 성공하고, 배포 후 공개 URL에서 새로고침과 라우팅이 함께 동작하는지 확인합니다.

## 문제가 생기면 먼저 볼 것

- 배포 후 API 호출이 실패하면 `VITE_API_URL`과 CORS 설정, `fetch` 에러 처리를 먼저 확인합니다.
- 프로젝트를 다시 실행하기 어렵다면 README와 `.env.example`가 실제 현재 구조를 설명하는지 점검합니다.

## 이 코드에서 주목할 점

- 폴더 구조가 역할별로 나뉘어 있어 어디를 수정해야 할지 즉시 보입니다.
- API 클라이언트를 컴포넌트 밖으로 분리해 테스트와 재사용이 쉬워집니다.
- 환경 변수로 개발 백엔드와 프로덕션 백엔드를 분리합니다.

## 자주 하는 실수 5가지

1. **모든 코드를 `App.tsx`에 넣습니다.** 100줄을 넘기면 읽기가 급격히 어려워집니다.
2. **컴포넌트 안에서 API를 직접 호출합니다.** 테스트와 재사용이 모두 어려워집니다.
3. **README를 남기지 않습니다.** 한 달 뒤의 자신도 프로젝트를 다시 실행하기 어려워집니다.
4. **`localhost`에서만 확인하고 배포하지 않습니다.** 실제 배포는 언제나 새로운 문제를 드러냅니다.
5. **완벽해질 때까지 공개를 미룹니다.** 오늘 배포한 작은 앱이 배포하지 않은 완벽한 앱보다 훨씬 큰 학습을 줍니다.

## 실무에서는 이렇게 보입니다

실무 팀도 본질적으로 같은 패턴을 씁니다. `pages/`, `components/`, `api/`, `hooks/`, `styles/` 같은 구조는 수십 명이 함께 일하는 코드베이스에서도 기본 골격으로 자주 등장합니다. 달라지는 것은 규모와 추상화 수준이지, 형태 자체는 크게 다르지 않습니다.

그래서 입문 단계에서 작은 프로젝트를 제대로 나눠 보는 경험은 생각보다 오래갑니다. 나중에 큰 코드베이스를 만났을 때도 어디를 봐야 할지 훨씬 빨리 감이 옵니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 작게 만들고 자주 배포합니다.
- 폴더 구조는 비즈니스 도메인을 따라가게 둡니다.
- 항상 README와 `.env.example`를 함께 유지합니다.
- 배포 자동화는 가능한 한 초반부터 붙입니다.
- 첫 번째 사용자를 자기 자신으로 생각합니다.

## 체크리스트

- [ ] 폴더 구조를 설명할 수 있습니다.
- [ ] API 클라이언트를 컴포넌트 밖으로 분리했습니다.
- [ ] `npm run build`가 성공합니다.
- [ ] 앱이 공개 URL 뒤에서 동작합니다.
- [ ] README에 실행 방법을 적어 두었습니다.

## 연습 문제

1. 이 구조를 참고해 노트 앱을 만들고 Netlify나 Vercel에 배포해 보세요.
2. README에 실행 방법, 환경 변수, 배포 URL을 문서화해 보세요.
3. 빌드 산출물 크기를 측정하고 200KB 이하로 줄이는 연습을 해 보세요.

## 정리 및 다음 단계

여기까지 왔다면 프론트엔드 입문 과정은 한 번 완주한 셈입니다. 이제 개별 개념이 아니라 하나의 앱을 운영 가능한 형태로 묶는 감각이 생겼을 것입니다.

다음에 함께 보면 좋은 주제는 테스트, DevOps, 보안 코딩입니다. 컴포넌트와 API 호출을 어떻게 검증할지, 배포와 모니터링을 어떻게 자동화할지, 폼과 API를 어떤 식으로 방어할지 이어서 확장해 보세요.

> 한 번에 모든 것을 배우려 하지 말고, 지금 만든 앱에 한 가지씩 더해 가는 방식으로 확장해 보세요.


## 실전 구현 확장: HTML/CSS/JS, 컴포넌트, 빌드 설정

프론트엔드 글을 읽고 바로 실무에 연결하려면 이론 설명 뒤에 실행 가능한 구조를 붙여 보는 연습이 필요합니다. 핵심은 화면을 "보이는 결과"로만 다루지 않고, HTML 구조, CSS 토큰, JavaScript 상태, 컴포넌트 경계, 빌드 산출물까지 한 흐름으로 연결하는 것입니다. 이 흐름이 잡히면 기능 추가와 디버깅이 훨씬 예측 가능해집니다.

### HTML 구조를 의미 단위로 나누기

처음부터 시맨틱 태그를 사용하면 접근성과 유지보수 비용이 함께 좋아집니다.

```html
<main class="layout">
  <header class="hero">
    <h1>주문 대시보드</h1>
    <p>오늘 처리 상태를 빠르게 확인합니다.</p>
  </header>

  <section aria-labelledby="summary-title" class="card">
    <h2 id="summary-title">요약</h2>
    <ul id="summary-list"></ul>
  </section>

  <section aria-labelledby="queue-title" class="card">
    <h2 id="queue-title">대기 주문</h2>
    <div id="queue-root"></div>
  </section>
</main>
```

`div`만으로도 화면은 만들 수 있지만, `header`, `section`, `h1~h2` 계층을 쓰면 스크린 리더 탐색과 테스트 선택자가 안정됩니다. 구조가 명확하면 팀 내 협업에서도 컴포넌트 경계가 자연스럽게 정리됩니다.

### CSS를 토큰 중심으로 설계하기

디자인 시스템이 작더라도 색상, 간격, 타이포그래피 토큰을 먼저 선언하면 변경 비용을 크게 줄일 수 있습니다.

```css
:root {
  --bg: #f7f8fa;
  --surface: #ffffff;
  --text: #1f2937;
  --muted: #6b7280;
  --accent: #0f766e;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --radius-md: 12px;
}

body {
  margin: 0;
  background: linear-gradient(180deg, #eef4ff 0%, var(--bg) 35%);
  color: var(--text);
  font-family: "Noto Sans KR", sans-serif;
}

.card {
  background: var(--surface);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}
```

토큰 방식의 장점은 테마 변경, 브랜드 컬러 교체, 다크 테마 실험 시 영향 범위를 빠르게 파악할 수 있다는 점입니다. 임의 값 하드코딩이 늘어나면 작은 수정도 전체 회귀 테스트가 필요해집니다.

### JavaScript 상태 흐름을 단방향으로 유지하기

입문 단계부터 상태 갱신 규칙을 일정하게 가져가면 복잡한 프레임워크로 넘어가도 사고 비용이 낮습니다.

```javascript
const state = {
  orders: [],
  loading: false,
  error: null,
};

async function loadOrders() {
  setState({ loading: true, error: null });
  try {
    const res = await fetch("/api/orders?status=pending");
    const data = await res.json();
    setState({ orders: data.items, loading: false });
  } catch (err) {
    setState({ error: "주문 목록을 불러오지 못했습니다.", loading: false });
  }
}

function setState(patch) {
  Object.assign(state, patch);
  render();
}
```

`setState -> render` 규칙을 명시하면 상태 변경 지점을 추적하기 쉬워지고, 비동기 오류 처리도 일관되게 유지됩니다.

### 컴포넌트 패턴: Presentational vs Container

작은 프로젝트에서도 데이터 책임과 표현 책임을 분리해 두면 재사용성이 올라갑니다.

```javascript
function OrderList({ items }) {
  return `
    <ul>
      ${items.map((o) => `<li>${o.id} - ${o.customer}</li>`).join("")}
    </ul>
  `;
}

async function OrderListContainer(root) {
  root.innerHTML = "<p>불러오는 중...</p>";
  const res = await fetch("/api/orders");
  const data = await res.json();
  root.innerHTML = OrderList({ items: data.items });
}
```

- Presentational 컴포넌트는 입력 props를 받아 화면만 렌더링합니다.
- Container 컴포넌트는 데이터 조회, 예외 처리, 로딩 상태를 담당합니다.

이 분리는 테스트 단위를 명확히 만들어 줍니다. 화면 렌더링 테스트와 API 실패 테스트를 별도로 설계할 수 있기 때문입니다.

### 빌드 설정 예시: Vite 기반 최소 구성

빌드 도구는 복잡해 보이지만 기본 설정은 단순합니다. 중요한 것은 개발 서버와 운영 번들의 차이를 이해하는 것입니다.

```ts
// vite.config.ts
import { defineConfig } from "vite";

export default defineConfig({
  server: {
    port: 5173,
  },
  build: {
    sourcemap: true,
    target: "es2020",
    outDir: "dist",
  },
});
```

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "check": "npm run build && npm run test"
  }
}
```

운영 이슈를 빠르게 추적하려면 `sourcemap` 유지 전략, 캐시 무효화 파일명(hash), 환경변수 주입 규칙(`import.meta.env`)을 함께 문서화해야 합니다.

### 프런트엔드 품질을 좌우하는 검증 항목

- 접근성: 버튼/입력 요소의 label과 키보드 포커스 경로 확인
- 성능: 첫 렌더링 크기, 이미지 최적화, 코드 스플리팅 여부 확인
- 안정성: 네트워크 실패 시 로딩/오류/재시도 UI 동작 확인
- 유지보수: 컴포넌트 props 계약과 상태 변경 규칙 일관성 확인

이 항목을 PR 체크리스트로 고정하면 "기능은 동작하지만 운영 품질이 낮은 화면"을 사전에 걸러낼 수 있습니다.

### 실무 연결 포인트

프론트엔드는 더 이상 단순 화면 기술이 아닙니다. API 계약, 번들 최적화, 브라우저 성능, 접근성, 운영 관측이 모두 만나는 실행 계층입니다. 따라서 작은 예제라도 HTML/CSS/JS 코드, 컴포넌트 패턴, 빌드 설정을 한 번에 다뤄 보는 연습이 필요합니다. 이 연습을 반복하면 도구가 바뀌어도 구조를 잃지 않고, 신규 기능을 추가할 때도 안정적으로 확장할 수 있습니다.


## 처음 질문으로 돌아가기

- **작은 프로젝트에서는 어떤 폴더 구조가 가장 읽기 쉬울까요?**
  - 본문의 기준은 작은 프론트엔드 앱 만들기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **앞선 1~9화 개념은 실제 앱 안에서 어떻게 이어질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **개발, 빌드, 배포 흐름은 어떤 순서로 정리되는 편이 좋을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML과 CSS 기본](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript 기본](./03-javascript-basics.md)
- [Frontend Development 101 (4/10): 컴포넌트와 상태](./04-components-and-state.md)
- [Frontend Development 101 (5/10): 라우팅과 페이지](./05-routing-and-pages.md)
- [Frontend Development 101 (6/10): API 호출과 비동기](./06-api-calls-and-async.md)
- [Frontend Development 101 (7/10): 폼과 유효성 검사](./07-forms-and-validation.md)
- [Frontend Development 101 (8/10): 스타일링과 디자인 시스템](./08-styling-and-design-system.md)
- [Frontend Development 101 (9/10): 빌드 도구와 번들링](./09-build-tools-and-bundling.md)
- **작은 프론트엔드 앱 만들기 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Vite guide](https://vite.dev/guide/)
- [React Router documentation](https://reactrouter.com/home)
- [Netlify deploy docs](https://docs.netlify.com/site-deploys/create-deploys/)

### 확인용 자료
- [Vercel framework guides](https://vercel.com/docs/frameworks)
- [Create React App alternatives on react.dev](https://react.dev/learn/start-a-new-react-project)

Tags: Frontend, Project, Capstone, React, Web
