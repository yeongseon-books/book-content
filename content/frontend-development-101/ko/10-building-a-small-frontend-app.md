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

이 글은 Frontend Development 101 시리즈의 마지막 글입니다. 여기서는 지금까지 배운 내용을 작은 노트 앱으로 모아 봅니다. 완벽한 앱을 만드는 것이 목표가 아니라, 기초 개념을 하나의 살아 있는 제품 흐름으로 연결해 배포까지 끝내 보는 경험이 목표입니다.

개념을 따로따로 이해하는 것과 실제 앱으로 끝까지 묶는 것은 완전히 다른 경험입니다. 라우팅도 알고 폼도 알고 API 호출도 이해했는데, 막상 하나의 프로젝트로 합치려면 어디서부터 파일을 나누고 어떤 순서로 조립해야 할지 막막해지는 경우가 많습니다.


![Frontend Development 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/10/10-01-diagram.ko.png)
*Frontend Development 101 10장 흐름 개요*

## 먼저 던지는 질문

- 작은 프로젝트에서는 어떤 폴더 구조가 가장 읽기 쉬울까요?
- 앞선 1~9화 개념은 실제 앱 안에서 어떻게 이어질까요?
- 개발, 빌드, 배포 흐름은 어떤 순서로 정리되는 편이 좋을까요?

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

## 전통 방식과 현대 방식 비교

**Before (개념만 아는 상태)**

```text
"I know routing, I know forms, I know APIs."
"But I have never combined them all to *build an app*."
```

**After (작은 앱이 인터넷에서 동작)**

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


## 실전 구현 확장: 구조, 상태, 빌드, 운영 품질

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


## 실무 앵커 모음: 프레임워크, 레이아웃, 디버깅, 성능

이 절은 앞에서 배운 개념을 실제 구현 단위로 연결하기 위한 공통 앵커입니다. 핵심은 기술 이름을 외우는 것이 아니라, 같은 문제를 React와 Vue에서 어떻게 구조화하는지, CSS 레이아웃과 접근성 규칙을 어떻게 함께 적용하는지, 그리고 DevTools와 빌드 설정으로 성능 가설을 어떻게 검증하는지를 한 번에 보는 것입니다.

### React 컴포넌트 앵커: 상태와 접근성 속성 함께 설계하기

```tsx
import { useMemo, useState } from "react";

type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const seed: Todo[] = [
  { id: 1, title: "요구사항 정리", done: true },
  { id: 2, title: "UI 구성", done: false },
  { id: 3, title: "접근성 점검", done: false },
];

export default function TodoPanel() {
  const [items, setItems] = useState<Todo[]>(seed);
  const [keyword, setKeyword] = useState("");

  const filtered = useMemo(
    () => items.filter((item) => item.title.includes(keyword.trim())),
    [items, keyword],
  );

  function toggle(id: number) {
    setItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, done: !item.done } : item,
      ),
    );
  }

  return (
    <section aria-labelledby="todo-title">
      <h2 id="todo-title">작업 목록</h2>

      <label htmlFor="todo-filter">제목 필터</label>
      <input
        id="todo-filter"
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        placeholder="예: 접근성"
      />

      <ul>
        {filtered.map((item) => (
          <li key={item.id}>
            <button
              type="button"
              aria-pressed={item.done}
              onClick={() => toggle(item.id)}
            >
              {item.done ? "완료" : "진행"}: {item.title}
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
```

이 코드의 핵심은 세 가지입니다. 첫째, 상태 변경 지점을 `toggle` 하나로 모아 추적성을 높입니다. 둘째, `aria-pressed`로 토글 상태를 보조기술에 전달합니다. 셋째, 필터링 연산을 `useMemo`로 감싸 입력 반응성을 유지합니다. 입문 단계에서 이런 습관을 들이면 상태가 늘어나도 버그 위치를 빠르게 좁힐 수 있습니다.

### Vue 컴포넌트 앵커: 반응형 계산과 입력 검증 흐름

```vue
<script setup lang="ts">
import { computed, ref } from "vue";

type Member = {
  id: number;
  name: string;
  role: "dev" | "design" | "pm";
};

const members = ref<Member[]>([
  { id: 1, name: "민서", role: "dev" },
  { id: 2, name: "준호", role: "design" },
  { id: 3, name: "유진", role: "pm" },
]);

const role = ref<"all" | Member["role"]>("all");
const keyword = ref("");

const visibleMembers = computed(() => {
  return members.value.filter((member) => {
    const roleMatched = role.value === "all" || role.value === member.role;
    const keywordMatched = member.name.includes(keyword.value.trim());
    return roleMatched && keywordMatched;
  });
});
</script>

<template>
  <section aria-labelledby="member-title">
    <h2 id="member-title">팀 멤버</h2>

    <label for="role-select">역할</label>
    <select id="role-select" v-model="role">
      <option value="all">전체</option>
      <option value="dev">개발</option>
      <option value="design">디자인</option>
      <option value="pm">기획</option>
    </select>

    <label for="member-keyword">이름 검색</label>
    <input id="member-keyword" v-model="keyword" />

    <ul>
      <li v-for="member in visibleMembers" :key="member.id">
        {{ member.name }} / {{ member.role }}
      </li>
    </ul>
  </section>
</template>
```

Vue에서는 `computed`를 중심으로 파생 상태를 선언하면 템플릿이 읽기 쉬워지고 테스트 지점도 명확해집니다. 특히 폼 입력과 필터링이 결합된 화면에서 `v-model`과 계산 속성을 분리해 두면, 검증 규칙 추가나 API 연동 시 수정 범위가 작아집니다.

### CSS 레이아웃 앵커: Grid와 Flex를 역할별로 구분하기

```css
:root {
  --surface: #ffffff;
  --border: #e5e7eb;
  --text: #111827;
  --muted: #6b7280;
  --gap-3: 12px;
  --gap-4: 16px;
  --radius: 14px;
}

.dashboard {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: var(--gap-4);
  min-height: 100dvh;
  padding: var(--gap-4);
  background:
    radial-gradient(circle at 10% 0%, #e0f2fe 0%, transparent 35%),
    #f8fafc;
  color: var(--text);
}

.sidebar,
.content-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--gap-3);
  align-items: center;
  justify-content: space-between;
}

@media (max-width: 960px) {
  .dashboard {
    grid-template-columns: 1fr;
  }
}
```

권장 기준은 단순합니다. 페이지 뼈대는 Grid, 같은 축의 정렬은 Flex로 나눕니다. 이렇게 역할을 분리하면 반응형 변경 시 어디를 수정해야 하는지 즉시 보입니다. 또한 `minmax(0, 1fr)`를 사용해 긴 텍스트가 그리드를 깨뜨리는 문제를 예방할 수 있습니다.

### DevTools 워크플로: 가설부터 검증까지

브라우저 DevTools는 "문제가 있다"는 느낌을 "어느 계층이 원인인지"로 바꾸는 도구입니다. 실무에서 반복 가능한 순서는 아래와 같습니다.

1. **Network 탭**에서 느린 요청을 정렬하고 `TTFB`, `Content Download`를 분리해 확인합니다.
2. **Performance 탭**에서 사용자 시나리오를 기록한 뒤 Long Task(50ms+) 구간을 찾습니다.
3. **Coverage 탭**으로 사용되지 않는 CSS/JS 비율을 확인해 코드 스플리팅 후보를 뽑습니다.
4. **Lighthouse**에서 접근성 경고(`label`, `color contrast`, `heading order`)를 우선 정리합니다.
5. **Memory 탭**에서 화면 전환을 5회 반복 기록해 누수 패턴(Detached DOM tree)을 찾습니다.

이 흐름의 장점은 도구를 많이 쓰는 데 있지 않습니다. 같은 문제를 팀원 누구나 같은 순서로 재현하고 같은 숫자로 대화할 수 있다는 점이 핵심입니다.

### 빌드 설정 앵커: 개발/운영 차이를 명시적으로 관리하기

```ts
import { defineConfig } from "vite";

export default defineConfig({
  build: {
    target: "es2020",
    sourcemap: true,
    cssCodeSplit: true,
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks: {
          framework: ["react", "react-dom"],
          vendor: ["lodash-es", "dayjs"],
        },
      },
    },
  },
  server: {
    port: 5173,
    strictPort: true,
  },
});
```

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "analyze": "vite build --mode analyze",
    "check": "npm run build && npm run test && npm run lint"
  }
}
```

중요한 포인트는 `manualChunks` 같은 최적화 옵션을 "속도 향상 마법"으로 보지 않는 것입니다. 먼저 측정 지표를 정하고, 변경 전후 번들 크기와 초기 렌더링 시간을 숫자로 비교해야 합니다. 그래야 회귀가 생겨도 원인을 빠르게 되짚을 수 있습니다.

### 접근성 패턴 앵커: 키보드와 스크린 리더를 기본값으로

```html
<form aria-labelledby="signup-title" novalidate>
  <h2 id="signup-title">뉴스레터 신청</h2>

  <label for="email">이메일</label>
  <input
    id="email"
    name="email"
    type="email"
    autocomplete="email"
    aria-describedby="email-help email-error"
    required
  />
  <p id="email-help">업무용 이메일을 권장합니다.</p>
  <p id="email-error" role="alert" hidden>올바른 이메일 형식이 아닙니다.</p>

  <button type="submit">신청</button>
</form>
```

접근성은 별도 기능이 아니라 입력과 오류 흐름의 기본 계약입니다. `label` 연결, 오류 메시지의 `role="alert"`, 키보드 포커스 순서 같은 규칙은 초기에 넣어야 비용이 가장 낮습니다. 나중에 화면이 커진 뒤 보강하려면 컴포넌트 API부터 다시 설계해야 하는 경우가 많습니다.

### 성능 예산 앵커: 감이 아니라 수치로 운영하기

다음은 입문 팀에서도 바로 적용 가능한 예시 예산입니다.

- 초기 JavaScript 번들(압축 후): **220KB 이하**
- 최초 콘텐츠 표시(FCP): **1.8초 이하**
- 상호작용 가능 시점(TTI): **3.0초 이하**
- 이미지 총 전송량(첫 화면): **500KB 이하**
- 장기 작업(Long Task): **페이지당 2회 이하**

예산은 목표가 아니라 경계선입니다. 기능을 추가할 때 이 수치를 함께 검토하면 "동작은 하지만 체감은 나빠진" 상태를 초기에 차단할 수 있습니다. 특히 프론트엔드는 기능 품질과 성능 품질이 분리되지 않으므로, 정의 단계부터 성능 기준을 요구사항에 포함하는 편이 안전합니다.

### 운영 관점 마무리

프론트엔드는 도구보다 구조화 원칙이 오래갑니다. 컴포넌트 경계, 상태 흐름, 접근성 계약, 성능 예산, 검증 루프를 팀의 기본 언어로 고정하면 기술 스택이 바뀌어도 품질이 쉽게 무너지지 않습니다.


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

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/frontend-development-101/ko)

Tags: Frontend, Project, Capstone, React, Web
