---
series: frontend-development-101
episode: 2
title: "Frontend Development 101 (2/10): HTML과 CSS 기본"
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
  - HTML
  - CSS
  - Web
  - Beginner
seo_description: 시맨틱 HTML 구조 설계와 CSS 박스 모델, Flexbox, Grid 레이아웃 시스템을 익히고 반응형 웹과 접근성 기초를 정리합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (2/10): HTML과 CSS 기본

이 글은 Frontend Development 101 시리즈의 두 번째 글입니다. 여기서는 HTML을 페이지의 뼈대로, CSS를 그 뼈대 위에 입히는 규칙으로 설명합니다. HTML은 의미를 담고 CSS는 모양을 담아야 나중의 레이아웃, 접근성, SEO가 함께 정리됩니다.

프론트엔드를 조금만 공부해도 금방 느끼는 사실이 하나 있습니다. 화면을 빨리 만드는 일과 오래 유지되는 화면을 만드는 일은 전혀 다르다는 점입니다. 전자는 아무 태그나 놓고 색을 입혀도 되지만, 후자는 구조와 의미를 분리해야 합니다.

## 먼저 던지는 질문

- 시맨틱 HTML이 단순한 취향 문제가 아니라 기본 설계인 이유는 무엇일까요?
- 박스 모델은 CSS를 이해할 때 왜 가장 먼저 잡아야 할 개념일까요?
- Flexbox와 Grid는 각각 어떤 상황에서 더 적합할까요?

## 큰 그림

![Frontend Development 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/02/02-01-diagram.ko.png)

*Frontend Development 101 2장 흐름 개요*

## 왜 중요한가

HTML과 CSS는 프론트엔드에서 가장 오래 살아남는 기술입니다. 프레임워크는 몇 년마다 바뀌지만, 시맨틱 태그와 박스 모델과 레이아웃 원리는 계속 남습니다. 그래서 이 구간에 들인 시간은 거의 항상 수익률이 높습니다.

특히 시맨틱 HTML은 검색 엔진과 스크린 리더가 같은 문서를 읽을 수 있게 만드는 가장 값싼 투자입니다. 화면을 비슷하게 그리는 것만으로는 부족하고, 그 구조가 무엇을 의미하는지도 코드 안에 남아 있어야 합니다.

## 개념 한눈에 보기

대부분의 프론트엔드 레이아웃 문제는 결국 이 흐름 안에 들어 있습니다. 구조를 잡고, 박스를 이해하고, 배치를 결정하고, 화면 크기에 맞춰 조정한 뒤, 접근성까지 확인하는 순서입니다.

## 핵심 용어

- **시맨틱 HTML**: `<header>`, `<nav>`, `<article>`처럼 의미를 가진 태그입니다.
- **박스 모델**: 모든 요소를 content, padding, border, margin의 조합으로 보는 방식입니다.
- **Flexbox**: 한 축 중심으로 배치하는 레이아웃 시스템입니다.
- **Grid**: 행과 열 두 축을 함께 다루는 레이아웃 시스템입니다.
- **미디어 쿼리**: 화면 크기나 환경에 따라 다른 스타일을 적용하는 문법입니다.

## 전통 방식과 현대 방식 비교

**Before (의미 없는 div 더미)**

```html
<div class="header">
  <div class="nav">...</div>
</div>
<div class="content">...</div>
```

**After (semantic structure)**

```html
<header><nav>...</nav></header>
<main>...</main>
<footer>...</footer>
```

둘 다 화면은 비슷하게 만들 수 있습니다. 하지만 아래 예제처럼 시맨틱 태그를 쓰면 검색 엔진, 스크린 리더, 미래의 동료 개발자 모두가 구조를 더 쉽게 이해합니다.

## 실습: 카드 레이아웃을 5단계로 만들기

### 1단계 — Semantic structure

```html
<main>
  <article class="card">
    <h2>Title</h2>
    <p>Body</p>
  </article>
</main>
```

### 2단계 — Apply the box model

```css
.card {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 1rem;
}
```

### 3단계 — Flexbox row

```css
main {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
.card { flex: 1 1 250px; }
```

### 4단계 — Grid regions

```css
main {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}
```

### 5단계 — Media query

```css
@media (max-width: 600px) {
  main { grid-template-columns: 1fr; }
}
```

이 예제에서 중요한 것은 예쁜 카드가 아니라 레이아웃 사고방식입니다. 의미 있는 구조를 먼저 만들고, 박스 모델을 적용하고, Flexbox나 Grid로 배치하고, 마지막에 반응형 보정을 넣는 순서가 안정적입니다.

## 검증 포인트

- 브라우저 폭을 600px 아래로 줄였을 때 카드가 한 열로 접히는지 확인합니다.
- DevTools Elements 탭에서 `<main>`, `<article>` 같은 시맨틱 태그가 의도한 구조로 들어갔는지 확인합니다.

## 문제가 생기면 먼저 볼 것

- 레이아웃이 안 바뀌면 미디어 쿼리 조건과 선택자 이름이 실제 HTML과 일치하는지 확인합니다.
- 간격이 어색하면 `gap`, `padding`, `margin`이 어느 요소에 걸렸는지 박스 모델로 다시 봅니다.

## 이 코드에서 주목할 점

- `card`처럼 역할 기반 이름을 쓰고 `red`처럼 표현 중심 이름은 피하는 편이 좋습니다.
- `gap`은 margin 충돌을 줄여 레이아웃을 더 단순하게 만듭니다.
- `minmax(250px, 1fr)`는 반응형 Grid에서 매우 자주 쓰이는 기본 패턴입니다.

## 자주 하는 실수 5가지

1. **모든 것을 `<div>`로만 작성합니다.** 구조의 의미가 사라져 검색 엔진과 스크린 리더 모두 불리해집니다.
2. **`!important`를 남발합니다.** 우선순위 체계가 무너져 CSS가 금방 혼란스러워집니다.
3. **고정 `px`만 사용합니다.** `rem`, `%`, `fr`을 섞어야 반응형 흐름이 살아납니다.
4. **색만으로 정보를 전달합니다.** 색각 이상 사용자에게는 중요한 신호가 사라질 수 있습니다.
5. **이미지 alt를 비워 둡니다.** 의미 있는 이미지는 반드시 대체 텍스트가 필요합니다.

## 실무에서는 이렇게 보입니다

대부분의 팀은 Tailwind, Material UI, 자체 토큰 시스템 같은 디자인 시스템을 도입합니다. 하지만 그 시스템도 내부적으로는 시맨틱 HTML과 Flexbox/Grid 위에 서 있습니다. 기초가 약하면 디자인 시스템을 써도 디버깅이 어려워집니다.

결국 실무에서도 질문은 같습니다. 이 레이아웃이 어떤 의미 구조를 갖는가, 이 문제는 Flexbox로 풀 문제인가 Grid로 풀 문제인가, 이 화면이 모바일에서 자연스럽게 줄어드는가를 계속 묻게 됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 시맨틱 태그는 가장 저렴한 SEO·접근성 투자입니다.
- 많은 레이아웃 문제는 Flexbox와 Grid 중 무엇을 고를지로 정리됩니다.
- 모바일 우선으로 설계하고 큰 화면으로 확장합니다.
- 색은 유일한 신호가 되면 안 됩니다.
- 습관적으로 “왜 이 요소가 div인가”를 다시 묻습니다.

## 체크리스트

- [ ] `<header>`, `<main>`, `<footer>`를 적절히 사용할 수 있습니다.
- [ ] 박스 모델을 직접 그릴 수 있습니다.
- [ ] Flexbox와 Grid의 차이를 한 문장으로 설명할 수 있습니다.
- [ ] 미디어 쿼리로 반응형 레이아웃을 만들 수 있습니다.
- [ ] 모든 의미 있는 이미지에 적절한 `alt`를 작성할 수 있습니다.

## 연습 문제

1. 시맨틱 HTML과 CSS로 명함 형태의 작은 페이지를 만들어 보세요.
2. 카드 세 개를 Flexbox와 Grid로 각각 한 번씩 배치하고 차이를 정리해 보세요.
3. 600px 이하에서 한 열로 접히는 미디어 쿼리를 직접 추가해 보세요.

## 정리 및 다음 단계

HTML은 뼈대이고 CSS는 그 위에 입는 옷입니다. 두 역할이 분리되어 있어야 이후에 JavaScript가 자연스럽게 끼어들 수 있습니다.

다음 글에서는 이 구조 위에 동작을 붙이는 JavaScript 기본기를 살펴보겠습니다.


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

프론트엔드는 빠르게 변하는 생태계처럼 보이지만, 실제로 오래가는 것은 구조화 원칙입니다. 컴포넌트 경계, 상태 흐름, 접근성 계약, 성능 예산, 검증 루프를 팀의 기본 언어로 고정하면 도구가 React에서 Vue로, Vite에서 다른 번들러로 바뀌어도 품질이 쉽게 무너지지 않습니다. 이 글의 나머지 내용을 읽을 때도 "무엇을 썼는가"보다 "왜 이 구조로 검증 가능한가"를 기준으로 보면 실무 전환 속도가 훨씬 빨라집니다.


## 처음 질문으로 돌아가기

- **시맨틱 HTML이 단순한 취향 문제가 아니라 기본 설계인 이유는 무엇일까요?**
  - 본문의 기준은 HTML과 CSS 기본를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **박스 모델은 CSS를 이해할 때 왜 가장 먼저 잡아야 할 개념일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Flexbox와 Grid는 각각 어떤 상황에서 더 적합할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- **HTML과 CSS 기본 (현재 글)**
- JavaScript 기본 (예정)
- 컴포넌트와 상태 (예정)
- 라우팅과 페이지 (예정)
- API 호출과 비동기 (예정)
- 폼과 유효성 검사 (예정)
- 스타일링과 디자인 시스템 (예정)
- 빌드 도구와 번들링 (예정)
- 작은 프론트엔드 앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [MDN: HTML elements reference](https://developer.mozilla.org/en-US/docs/Web/HTML/Element)
- [MDN: CSS box model](https://developer.mozilla.org/en-US/docs/Learn/CSS/Building_blocks/The_box_model)
- [MDN: Basic concepts of flexbox](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_flexible_box_layout/Basic_concepts_of_flexbox)
- [MDN: CSS grid layout](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout)

### 확인용 자료
- [web.dev: Responsive web design basics](https://web.dev/articles/responsive-web-design-basics)
- [WAI: Images and alt decisions](https://www.w3.org/WAI/tutorials/images/)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/frontend-development-101/ko)

Tags: Frontend, HTML, CSS, Web, Beginner
