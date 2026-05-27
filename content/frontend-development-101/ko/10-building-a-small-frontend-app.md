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

| 용어 | 뜻 | 실무에서 왜 중요한가 |
|---|---|---|
| 프로젝트 구조 | 역할별로 나눈 폴더 레이아웃입니다. | 어디에 무엇을 고쳐야 하는지 빠르게 찾게 해 주는 기본 지도입니다. |
| Capstone | 앞에서 배운 내용을 하나로 묶는 마무리 프로젝트입니다. | 개별 개념을 실제 제품 흐름으로 연결해 학습을 완성합니다. |
| 배포 | 빌드 산출물을 공개 URL 뒤에 올리는 작업입니다. | 로컬에서 보이지 않던 라우팅, 환경 변수, CORS 문제를 드러내는 최종 검증입니다. |
| 로드맵 | 다음에 무엇을 배울지 보여 주는 학습 경로입니다. | 한 번 만든 프로젝트를 다음 학습의 발판으로 바꾸는 기준점이 됩니다. |

## 개념 분리 학습에서 실제 앱 배포까지

시리즈 마지막 글의 핵심은 개별 개념을 아는 것과 실제 앱을 끝까지 연결해 보는 것 사이의 차이를 체감하는 데 있습니다. 프로젝트 구조, 라우팅, API, 폼, 스타일, 빌드가 한 저장소 안에서 만날 때 비로소 제품 흐름이 완성됩니다.

| 방식 | 학습 상태 | 실무 영향 |
|---|---|---|
| 개념을 따로만 아는 상태 | 각 주제는 이해했지만 서로의 연결이 약합니다. | 실제 프로젝트를 시작하면 파일 구조와 배포 흐름에서 막히기 쉽습니다. |
| 작은 앱을 끝까지 배포한 상태 | 화면, 상태, API, 빌드, 배포가 하나의 경험으로 묶입니다. | 다음 프로젝트를 시작할 때 재사용 가능한 기준과 자신감이 생깁니다. |

**Before (개념만 아는 상태)**

```text
"I know routing, I know forms, I know APIs."
"But I have never combined them all to build an app."
```

**After (작은 앱이 인터넷에서 동작)**

```text
https://my-notes.netlify.app
- A user can add/edit/delete notes.
- The code is on GitHub.
- The next learner studies on top of this code.
```

한 번이라도 실제로 앱을 배포해 보면, 앞선 아홉 글이 각각의 개념이 아니라 한 제품을 완성하는 연결 고리였다는 사실이 훨씬 선명해집니다.

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
curl -i "$VITE_API_URL/notes"
```

기대 결과는 앱이 빌드되고, 깊은 링크 새로고침이 안전하며, API와 연결되고, 다른 개발자도 문서만으로 환경을 재현할 수 있는 상태입니다. 그 수준이 되어야 비로소 "데모가 끝났다"가 아니라 "작게나마 출하됐다"고 말할 수 있습니다.

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

## 처음 질문으로 돌아가기

- **작은 프로젝트에서는 어떤 폴더 구조가 가장 읽기 쉬울까요?**
  - 이 글은 `components/`, `pages/`, `api/`, `hooks/`, `styles/`처럼 역할이 드러나는 구조를 기본 뼈대로 제안했습니다. `NoteCard`와 `NoteForm`은 컴포넌트에, `NotesPage`와 `NotePage`는 페이지에, `notes.ts`는 API 계층에 두면 어디를 수정해야 할지 바로 보여 읽기 비용이 크게 줄어듭니다.
- **앞선 1~9화 개념은 실제 앱 안에서 어떻게 이어질까요?**
  - 이 노트 앱은 4화의 컴포넌트 분리, 5화의 `/notes/:id` 라우팅, 6화의 `fetch` 기반 API 클라이언트, 7화의 `handleSubmit` 검증, 8화의 `tokens.css`, 9화의 `vite.config.ts`가 한 흐름으로 이어진 예시입니다. 그래서 시리즈 각 장이 따로 있는 지식이 아니라, 실제 제품 안에서 서로 맞물리는 층이었다는 점이 드러납니다.
- **개발, 빌드, 배포 흐름은 어떤 순서로 정리되는 편이 좋을까요?**
  - 먼저 로컬에서 라우팅, 폼, API 호출을 맞추고 `VITE_API_URL` 같은 환경 변수를 정리한 뒤, `npm run build`로 산출물을 확인하고 마지막에 `netlify deploy --dir=dist --prod`로 공개 URL까지 올리는 순서가 안정적입니다. 본문이 README와 `.env.example` 유지를 강조한 이유도, 배포 후 다시 실행하고 검증하는 흐름까지 프로젝트 일부로 보기 때문입니다.

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
