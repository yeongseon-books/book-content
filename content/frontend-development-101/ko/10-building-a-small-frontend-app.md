---
series: frontend-development-101
episode: 10
title: "Frontend Development 101 (10/10): 작은 프론트엔드 앱 만들기"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/222"
    published_at: '2026-05-27'
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

이 흐름은 시리즈 전체를 압축한 그림입니다. 사용자는 페이지를 보고, 페이지는 컴포넌트와 상태로 구성되고, 컴포넌트는 API와 스타일 계층을 사용하며, 마지막에는 빌드와 배포를 거쳐 외부에 공개됩니다.

이 글은 Frontend Development 101 시리즈의 마지막 글입니다. 여기서는 지금까지 배운 내용을 작은 노트 앱으로 모아 봅니다. 완벽한 앱을 만드는 것이 목표가 아니라, 기초 개념을 하나의 살아 있는 제품 흐름으로 연결해 배포까지 끝내 보는 경험이 목표입니다.

![Frontend Development 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/10/10-01-diagram.ko.png)
*Frontend Development 101 10장 흐름 개요*

## 이 글에서 다룰 문제

- 작은 프로젝트에서는 어떤 폴더 구조가 가장 읽기 쉬울까요?
- 앞선 1~9화 개념은 실제 앱 안에서 어떻게 이어질까요?
- 개발, 빌드, 배포 흐름은 어떤 순서로 정리되는 편이 좋을까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 개념 한눈에 보기

| 용어 | 뜻 | 실무에서 왜 중요한가 |
|---|---|---|
| 프로젝트 구조 | 역할별로 나눈 폴더 레이아웃입니다. | 어디에 무엇을 고쳐야 하는지 빠르게 찾게 해 주는 기본 지도입니다. |
| Capstone | 앞에서 배운 내용을 하나로 묶는 마무리 프로젝트입니다. | 개별 개념을 실제 제품 흐름으로 연결해 학습을 완성합니다. |
| 배포 | 빌드 산출물을 공개 URL 뒤에 올리는 작업입니다. | 로컬에서 보이지 않던 라우팅, 환경 변수, CORS 문제를 드러내는 최종 검증입니다. |
| 로드맵 | 다음에 무엇을 배울지 보여 주는 학습 경로입니다. | 한 번 만든 프로젝트를 다음 학습의 발판으로 바꾸는 기준점이 됩니다. |

## 프로젝트 구조 설계

```
my-notes/
├── src/
│   ├── api/                # API 클라이언트 (6화)
│   │   ├── client.ts       # 기본 fetch 래퍼
│   │   └── notes.ts        # 노트 API 함수
│   ├── components/         # 재사용 컴포넌트 (4화)
│   │   ├── ui/             # 순수 UI 컴포넌트
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Card.tsx
│   │   └── notes/          # 노트 도메인 컴포넌트
│   │       ├── NoteCard.tsx
│   │       └── NoteForm.tsx
│   ├── hooks/              # 커스텀 훅 (4, 6화)
│   │   ├── useNotes.ts     # 노트 CRUD + 상태
│   │   └── useForm.ts      # 폼 상태 관리
│   ├── pages/              # 라우트 컴포넌트 (5화)
│   │   ├── NotesPage.tsx
│   │   ├── NotePage.tsx
│   │   └── NotFoundPage.tsx
│   ├── styles/             # 전역 스타일 (8화)
│   │   ├── tokens.css
│   │   └── global.css
│   ├── types/              # TypeScript 타입
│   │   └── index.ts
│   └── App.tsx             # 라우터 + 레이아웃
├── .env.example            # 환경 변수 예시
├── .env.development
├── .env.production
├── vite.config.ts          # 빌드 설정 (9화)
├── tailwind.config.js      # 스타일 토큰 (8화)
└── package.json
```

## 실습: 작은 노트 앱을 5단계로 만들기

### 1단계 — Project structure

```bash
# 프로젝트 생성
npm create vite@latest my-notes -- --template react-ts
cd my-notes
npm install react-router-dom @tanstack/react-query zod
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 폴더 생성
mkdir -p src/{api,components/ui,components/notes,hooks,pages,styles,types}
```

```typescript
// src/types/index.ts
export interface Note {
  id:        number;
  title:     string;
  content:   string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateNoteInput {
  title:   string;
  content: string;
}

export type AsyncState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error";   error: Error };
```

### 2단계 — API client (6화 리뷰)

```typescript
// src/api/client.ts
const BASE_URL = import.meta.env.VITE_API_URL ?? "https://jsonplaceholder.typicode.com";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${text || res.statusText}`);
  }
  return res.json();
}

export const api = {
  get:    <T>(path: string)                      => request<T>(path),
  post:   <T>(path: string, body: unknown)       => request<T>(path, { method: "POST",   body: JSON.stringify(body) }),
  put:    <T>(path: string, body: unknown)       => request<T>(path, { method: "PUT",    body: JSON.stringify(body) }),
  delete: <T>(path: string)                      => request<T>(path, { method: "DELETE" }),
};
```

```typescript
// src/api/notes.ts
import { api } from "./client";
import type { Note, CreateNoteInput } from "../types";

export const notesApi = {
  list:   ()                          => api.get<Note[]>("/posts"),
  get:    (id: number)                => api.get<Note>(`/posts/${id}`),
  create: (input: CreateNoteInput)    => api.post<Note>("/posts", input),
  update: (id: number, input: Partial<CreateNoteInput>) =>
    api.put<Note>(`/posts/${id}`, input),
  delete: (id: number)                => api.delete<void>(`/posts/${id}`),
};
```

### 3단계 — Custom hooks (4화 + 6화 리뷰)

```typescript
// src/hooks/useNotes.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notesApi } from "../api/notes";
import type { CreateNoteInput } from "../types";

export function useNotes() {
  return useQuery({
    queryKey: ["notes"],
    queryFn:  notesApi.list,
  });
}

export function useNote(id: number) {
  return useQuery({
    queryKey: ["notes", id],
    queryFn:  () => notesApi.get(id),
    enabled:  !!id,
  });
}

export function useCreateNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateNoteInput) => notesApi.create(input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notes"] }),
  });
}

export function useDeleteNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => notesApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notes"] }),
  });
}
```

### 4단계 — Form + component (4화 + 7화 리뷰)

```tsx
// src/components/notes/NoteForm.tsx
import { useState } from "react";
import { z } from "zod";
import { useCreateNote } from "../../hooks/useNotes";

const NoteSchema = z.object({
  title:   z.string().min(2, "제목은 2자 이상이어야 합니다.").max(100, "제목은 100자 이하여야 합니다."),
  content: z.string().min(10, "내용은 10자 이상이어야 합니다."),
});

interface NoteFormProps {
  onSuccess?: () => void;
}

export function NoteForm({ onSuccess }: NoteFormProps) {
  const [values,  setValues]  = useState({ title: "", content: "" });
  const [touched, setTouched] = useState({ title: false, content: false });

  const createNote = useCreateNote();

  const validation = NoteSchema.safeParse(values);
  const errors = validation.success ? {} : validation.error.issues.reduce<Record<string, string>>(
    (acc, issue) => ({ ...acc, [String(issue.path[0])]: issue.message }),
    {}
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setValues(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleBlur = (e: React.FocusEvent) => {
    setTouched(prev => ({ ...prev, [e.target.name]: true }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setTouched({ title: true, content: true });
    if (!validation.success) return;

    await createNote.mutateAsync(values);
    setValues({ title: "", content: "" });
    setTouched({ title: false, content: false });
    onSuccess?.();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          제목
        </label>
        <input
          id="title"
          name="title"
          type="text"
          value={values.title}
          onChange={handleChange}
          onBlur={handleBlur}
          aria-invalid={!!(touched.title && errors.title)}
          aria-describedby={touched.title && errors.title ? "title-error" : undefined}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="노트 제목을 입력하세요"
        />
        {touched.title && errors.title && (
          <p id="title-error" className="mt-1 text-sm text-red-600" role="alert">
            {errors.title}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-1">
          내용
        </label>
        <textarea
          id="content"
          name="content"
          value={values.content}
          onChange={handleChange}
          onBlur={handleBlur}
          aria-invalid={!!(touched.content && errors.content)}
          aria-describedby={touched.content && errors.content ? "content-error" : undefined}
          rows={4}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          placeholder="내용을 입력하세요..."
        />
        {touched.content && errors.content && (
          <p id="content-error" className="mt-1 text-sm text-red-600" role="alert">
            {errors.content}
          </p>
        )}
      </div>

      {createNote.isError && (
        <p className="text-sm text-red-600" role="alert">
          저장 중 오류가 발생했습니다. 다시 시도해 주세요.
        </p>
      )}

      <button
        type="submit"
        disabled={createNote.isPending}
        aria-busy={createNote.isPending}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {createNote.isPending ? "저장 중..." : "노트 저장"}
      </button>
    </form>
  );
}
```

### 5단계 — Build and deploy

```tsx
// src/App.tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { lazy, Suspense } from "react";

const NotesPage  = lazy(() => import("./pages/NotesPage"));
const NotePage   = lazy(() => import("./pages/NotePage"));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage"));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime:  5 * 60 * 1000,
      retry:      1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50">
          <header className="bg-white border-b border-gray-200 px-4 py-3">
            <h1 className="text-xl font-bold text-gray-900">My Notes</h1>
          </header>
          <main className="max-w-4xl mx-auto px-4 py-6">
            <Suspense fallback={<div className="text-center py-8">로딩 중...</div>}>
              <Routes>
                <Route path="/"          element={<NotesPage />} />
                <Route path="/notes/:id" element={<NotePage />} />
                <Route path="*"          element={<NotFoundPage />} />
              </Routes>
            </Suspense>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
```

```bash
# 빌드 및 배포
npm run build

# Netlify CLI
npm install -g netlify-cli
netlify deploy --dir=dist --prod

# 또는 Vercel CLI
npm install -g vercel
vercel --prod

# 배포 후 확인
# 1. 공개 URL에서 기본 동작 확인
# 2. /notes/1 에서 새로고침 → 404인지 확인 (SPA fallback 설정 필요 시 조치)
# 3. DevTools Network 탭에서 lazy loading 청크 확인
```

## 출하 준비 점검표

작은 프론트엔드 앱도 로컬 데모를 넘어 실제로 빌드, 새로고침, 데이터 흐름, 실행 문서를 견뎌야 비로소 완성이라고 부를 수 있습니다.

1. **빌드 계약을 점검합니다.** `npm run build` 후 `dist`를 정적 서버처럼 띄워 실제 배포와 비슷하게 확인합니다.
2. **라우팅 계약을 점검합니다.** `/notes/1` 같은 깊은 URL을 직접 열고 새로고침해도 404 대신 앱이 다시 열리는지 확인합니다.
3. **데이터 계약을 점검합니다.** 노트를 만든 뒤 목록을 다시 불러와서, 결과가 메모리 착시가 아니라 API 응답으로 유지되는지 봅니다.
4. **인수인계 계약을 점검합니다.** README와 `.env.example`만으로 다른 사람이 프로젝트를 재실행할 수 있는지 확인합니다.

```bash
npm run build
npx serve -s dist
# 그다음 http://localhost:3000/notes/1 을 열고 새로고침
```

```bash
curl -i "$VITE_API_URL/posts"
```

```markdown
# .env.example
VITE_API_URL=https://api.example.com

# README.md 필수 섹션
## 실행 방법
1. `cp .env.example .env.development`
2. `.env.development` 에서 API URL 설정
3. `npm install`
4. `npm run dev` → http://localhost:5173

## 배포 URL
https://my-notes.netlify.app

## 환경 변수
- `VITE_API_URL`: 백엔드 API 기본 URL
```

## 디버깅 시나리오

### 시나리오 1: 배포 후 API 호출 실패

```
문제: 로컬에서는 되는데 배포 후 API 오류

확인 순서:
1. DevTools Network 탭에서 실제 요청 URL 확인
2. VITE_API_URL이 프로덕션 환경에 올바르게 설정됐는지 확인
3. 백엔드 서버의 CORS 설정에 배포 도메인 포함 여부 확인
4. API 서버가 HTTPS인지 확인 (HTTP API → HTTPS 앱에서 Mixed Content 오류)
```

### 시나리오 2: 빌드 오류

```bash
# TypeScript 오류 먼저 확인
npx tsc --noEmit

# 타입 오류가 없는데 빌드 실패 시
npm run build 2>&1 | head -50
# 오류 메시지 읽고 해당 파일/라인 수정
```

### 시나리오 3: 성능이 느릴 때

```bash
# Lighthouse 실행 (Chrome DevTools → Lighthouse 탭)
# Performance 점수와 개선 제안 확인

# 번들 분석
npm run analyze  # vite.config.ts에 visualizer 설정 후

# 큰 모듈 발견 시 대체 라이브러리 찾기
npx bundlephobia [package-name]
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|---|---|---|
| 모든 코드를 `App.tsx`에 | 100줄 넘으면 읽기 급격히 어려워짐 | `pages/`, `components/`, `api/`, `hooks/`로 처음부터 분리 |
| 컴포넌트 안에서 API 직접 호출 | 테스트와 재사용 모두 어려움 | API는 `api/` 폴더로, 상태는 커스텀 훅으로 분리 |
| README 미작성 | 한 달 뒤 자신도 프로젝트 재실행 불가 | `npm run dev`부터 배포 URL까지 단계별로 문서화 |
| localhost에서만 확인 | 배포 시 라우팅·환경변수·CORS 오류 발견 | 반드시 `npm run build && npx serve -s dist`로 배포 환경 시뮬레이션 |
| 완벽해질 때까지 배포 미룸 | 실제 사용 경험 없이 로컬 개발만 반복 | 최소 기능으로 빠르게 배포, 이후 개선 반복 |
| `.env` 파일을 git에 커밋 | API 키, 비밀 값 노출 위험 | `.gitignore`에 `.env*` 추가, `.env.example`만 커밋 |

## 실무에서는 이렇게 보입니다

실무 팀도 본질적으로 같은 패턴을 씁니다. `pages/`, `components/`, `api/`, `hooks/`, `styles/` 같은 구조는 수십 명이 함께 일하는 코드베이스에서도 기본 골격으로 자주 등장합니다.

```
실무 팀의 추가 요소 (입문 이후 확장 학습)
├── __tests__/           # Vitest 단위 테스트
├── e2e/                 # Playwright E2E 테스트
├── .github/workflows/   # CI/CD (GitHub Actions)
├── monitoring/          # Sentry 에러 트래킹
└── storybook/           # 컴포넌트 문서

다음에 배울 주제
├── 테스트: Vitest + React Testing Library
├── 접근성: axe-core, 스크린 리더 테스트
├── 성능: Web Vitals, Lighthouse CI
├── 보안: CSP, XSS 방어, 의존성 감사
└── DevOps: CI/CD 파이프라인, 무중단 배포
```

## 시니어 엔지니어는 이렇게 생각합니다

- 작게 만들고 자주 배포합니다.
- 폴더 구조는 비즈니스 도메인을 따라가게 둡니다.
- 항상 README와 `.env.example`를 함께 유지합니다.
- 배포 자동화는 가능한 한 초반부터 붙입니다.
- 첫 번째 사용자를 자기 자신으로 생각합니다.

## 운영 체크리스트

- [ ] 폴더 구조를 설명할 수 있습니다.
- [ ] API 클라이언트를 컴포넌트 밖으로 분리했습니다.
- [ ] `npm run build`가 성공합니다.
- [ ] 앱이 공개 URL 뒤에서 동작합니다.
- [ ] README에 실행 방법을 적어 두었습니다.
- [ ] `.env.example`이 있고 `.env`는 `.gitignore`에 포함됩니다.

## 연습 문제

1. 이 구조를 참고해 노트 앱을 만들고 Netlify나 Vercel에 배포해 보세요.
2. README에 실행 방법, 환경 변수, 배포 URL을 문서화해 보세요.
3. 빌드 산출물 크기를 측정하고 200KB 이하로 줄이는 연습을 해 보세요.
4. GitHub Actions로 `main` 브랜치에 푸시할 때 자동으로 Netlify에 배포되도록 CI/CD를 설정해 보세요.

## 정리 및 다음 단계

여기까지 왔다면 프론트엔드 입문 과정은 한 번 완주한 셈입니다. 이제 개별 개념이 아니라 하나의 앱을 운영 가능한 형태로 묶는 감각이 생겼을 것입니다.

다음에 함께 보면 좋은 주제는 테스트, DevOps, 보안 코딩입니다. 컴포넌트와 API 호출을 어떻게 검증할지, 배포와 모니터링을 어떻게 자동화할지, 폼과 API를 어떤 식으로 방어할지 이어서 확장해 보세요.

> 한 번에 모든 것을 배우려 하지 말고, 지금 만든 앱에 한 가지씩 더해 가는 방식으로 확장해 보세요.

## 처음 질문으로 돌아가기

- **작은 프로젝트에서는 어떤 폴더 구조가 가장 읽기 쉬울까요?**
  - 역할별로 나누는 것이 가장 단순하고 팀이 커져도 적용됩니다. `api/`, `components/`, `hooks/`, `pages/`, `styles/` 다섯 폴더로 시작하면 대부분의 입문 프로젝트를 커버할 수 있습니다.
- **앞선 1~9화 개념은 실제 앱 안에서 어떻게 이어질까요?**
  - HTML/CSS(2화)로 구조를 만들고, 컴포넌트/상태(4화)로 조각을 나누고, 라우터(5화)로 페이지를 연결하고, API(6화)로 서버와 대화하고, 폼(7화)으로 입력을 받고, 스타일 시스템(8화)으로 일관성을 유지하고, 빌드 도구(9화)로 배포 가능한 산출물을 만듭니다.
- **개발, 빌드, 배포 흐름은 어떤 순서로 정리되는 편이 좋을까요?**
  - `npm run dev`로 개발 → `npm run build`로 프로덕션 번들 생성 → `npx serve -s dist`로 로컬 배포 시뮬레이션 → Netlify/Vercel CLI로 실제 배포 순서입니다.

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
