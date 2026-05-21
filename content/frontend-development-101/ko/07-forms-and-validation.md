---
series: frontend-development-101
episode: 7
title: "Frontend Development 101 (7/10): 폼과 유효성 검사"
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
  - Forms
  - Validation
  - UX
  - React
seo_description: 폼 입력과 유효성 검사 전략을 익힙니다. 제어 컴포넌트, 실시간 피드백, Zod 검증, 접근성 고려 사항 등 실무 UX 패턴을 정리합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (7/10): 폼과 유효성 검사

이 글은 Frontend Development 101 시리즈의 일곱 번째 글입니다. 여기서는 폼을 단순한 입력 묶음이 아니라 사용자와의 대화 인터페이스로 설명합니다. 좋은 폼은 제출 후에만 검사하지 않고, 입력하는 동안 도와주며, 에러를 친절하고 구체적으로 보여 줍니다.

사용자는 폼을 통해 제품과 가장 길게 대화합니다. 회원가입, 로그인, 결제, 검색, 설정 변경까지 대부분의 중요한 순간이 폼에서 일어납니다. 그런데도 많은 폼은 제출 버튼을 누른 뒤에야 뒤늦게 오류를 보여 줍니다.

## 먼저 던지는 질문

- controlled input과 uncontrolled input은 어떤 차이가 있을까요?
- 유효성 검사는 형식, 비즈니스 규칙, 서버 검증으로 왜 나눠 생각해야 할까요?
- 에러 메시지는 어디에, 언제 보여 주는 편이 가장 친절할까요?

## 큰 그림

![Frontend Development 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/07/07-01-diagram.ko.png)

*Frontend Development 101 7장 흐름 개요*

## 왜 중요한가

폼은 전환율을 직접 좌우합니다. 회원가입 한 칸이 어색하면 사용자는 떠나고, 결제 폼 하나가 불친절하면 매출이 줄어듭니다. 폼은 프론트엔드의 UX 시험지라고 봐도 과장이 아닙니다.

좋은 폼은 덜 묻고, 오타를 빨리 잡아 주고, 빠르게 제출됩니다. 결국 기술 구현보다도 사용자가 실수했을 때 얼마나 자연스럽게 복구하게 돕는지가 더 중요합니다.

## 개념 한눈에 보기

이 흐름을 보면 프론트엔드 검증이 서버 검증을 대체하는 것이 아님을 알 수 있습니다. 프론트엔드는 사용자 경험을 개선하고, 서버는 최종 보안을 책임집니다.

## 핵심 용어

- **Controlled input**: 입력값이 React state에 저장되는 방식입니다.
- **Uncontrolled input**: 입력값이 DOM 안에 남아 있는 방식입니다.
- **Schema validation**: Zod, Yup 같은 라이브러리로 선언적으로 검증하는 방식입니다.
- **Inline error**: 필드 옆이나 아래에 바로 보이는 에러 메시지입니다.
- **`aria-invalid`**: 스크린 리더에 현재 필드가 유효하지 않음을 알리는 ARIA 속성입니다.

## 전통 방식과 현대 방식 비교

**Before (validate only on submit)**

```javascript
form.onsubmit = () => {
  if (email.value === "") alert("Please enter an email");
};
```

**After (real-time inline check + friendly message)**

```jsx
{!isEmail(email) && <p className="error">That doesn't look like an email</p>}
```

둘의 차이는 단순한 구현 방식이 아닙니다. 전자는 사용자가 제출한 뒤에야 실패를 알게 되고, 후자는 입력 도중에 바로 수정할 수 있게 돕습니다.

## 실습: 가입 폼을 5단계로 만들기

### 1단계 — Controlled input

```jsx
function Signup() {
  const [email, setEmail] = useState("");
  return <input value={email} onChange={e => setEmail(e.target.value)} />;
}
```

### 2단계 — Format check

```jsx
const isValidEmail = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
```

### 3단계 — Inline error

```jsx
<input
  value={email}
  onChange={e => setEmail(e.target.value)}
  aria-invalid={!isValidEmail}
/>
{!isValidEmail && email && <p className="error">That doesn't look like an email</p>}
```

### 4단계 — Disable submit while invalid

```jsx
<button disabled={!isValidEmail || submitting}>
  {submitting ? "Submitting..." : "Sign up"}
</button>
```

### 5단계 — Schema with Zod

```jsx
import { z } from "zod";

const SignupSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

const result = SignupSchema.safeParse({ email, password });
if (!result.success) showErrors(result.error.format());
```

이 예제에서 핵심은 3단계와 5단계입니다. 입력 중 피드백을 주는 UX와, 프론트와 백엔드에서 같은 스키마 개념을 공유하는 구조가 결합되면 폼은 훨씬 일관되고 안전해집니다.

## 검증 포인트

- 잘못된 이메일 형식에서는 inline 에러가 보이고, 올바른 값에서는 제출 버튼이 활성화되는지 확인합니다.
- 키보드만으로 필드 이동과 제출이 가능하고, 에러 필드에 `aria-invalid`가 붙는지 확인합니다.

## 문제가 생기면 먼저 볼 것

- 에러가 안 사라지면 controlled state 업데이트와 정규식 검사 시점을 확인합니다.
- 스크린 리더 정보가 비면 `label`, `id`, `aria-describedby` 연결을 먼저 확인합니다.

## 이 코드에서 주목할 점

- 사용자가 입력하는 동안 검사가 진행됩니다.
- `aria-invalid`로 같은 정보를 스크린 리더 사용자에게도 전달합니다.
- Zod 스키마 하나로 프론트엔드와 백엔드 검증 기준을 맞출 수 있습니다.

## 자주 하는 실수 5가지

1. **비밀번호를 한 번만 입력받습니다.** 단순 오타가 가입 실패로 이어질 수 있습니다.
2. **에러를 제출 후에만 보여 줍니다.** 사용자는 모든 필드를 다시 훑어야 합니다.
3. **기술적인 에러 문구를 그대로 노출합니다.** “Schema validation failed”는 사용자에게 아무 의미가 없습니다.
4. **`<label>`을 빼먹습니다.** 스크린 리더는 이 입력이 무엇인지 정확히 알기 어렵습니다.
5. **모바일 키보드 힌트를 주지 않습니다.** 이메일 입력인데 일반 키보드가 뜨면 UX가 나빠집니다.

## 실무에서는 이렇게 보입니다

대부분의 React 앱은 React Hook Form과 Zod 조합을 사용합니다. 상태 관리, 검증, 제출, 에러 표시를 선언적으로 묶을 수 있기 때문입니다. `useState`만으로 모든 폼을 직접 다루는 방식은 학습 단계 이후 점점 줄어드는 편입니다.

하지만 도구보다 먼저 잡아야 하는 것은 원칙입니다. 에러는 친절해야 하고, 키보드만으로도 폼 전체를 쓸 수 있어야 하며, 프론트 검증과 서버 검증은 역할이 다르다는 점을 분명히 해야 합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 폼은 대화이므로 매 단계마다 피드백을 줍니다.
- 프론트엔드는 UX를 위해, 백엔드는 보안을 위해 각각 검증합니다.
- 에러 메시지는 친절하고 행동 가능해야 합니다.
- 전체 폼은 키보드만으로도 완주 가능해야 합니다.
- 자동완성과 모바일 키보드 타입은 옵션이 아니라 기본값입니다.

## 체크리스트

- [ ] controlled input을 사용할 수 있습니다.
- [ ] inline 에러 메시지를 보여 줄 수 있습니다.
- [ ] 모든 입력에 `<label>`과 적절한 연결을 추가할 수 있습니다.
- [ ] `aria-invalid`와 `aria-describedby`의 역할을 설명할 수 있습니다.
- [ ] Zod나 Yup 같은 스키마 검증기를 사용해 봤습니다.

## 연습 문제

1. 이메일, 비밀번호, 비밀번호 확인 필드를 가진 가입 폼을 만들어 보세요.
2. 모든 필드에 inline 검증과 친절한 에러 메시지를 추가해 보세요.
3. 키보드만으로 폼을 끝까지 작성하고 제출할 수 있는지 직접 확인해 보세요.

## 정리 및 다음 단계

폼은 사용자와 가장 길게 만나는 인터페이스입니다. 입력을 안전하게 받고 친절하게 안내하는 감각이 있어야 제품 전체가 안정적으로 느껴집니다.

다음 글에서는 이 폼과 화면 전체에 일관된 모양을 부여하는 스타일링과 디자인 시스템을 살펴보겠습니다.


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

- **controlled input과 uncontrolled input은 어떤 차이가 있을까요?**
  - 본문의 기준은 폼과 유효성 검사를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **유효성 검사는 형식, 비즈니스 규칙, 서버 검증으로 왜 나눠 생각해야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **에러 메시지는 어디에, 언제 보여 주는 편이 가장 친절할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML과 CSS 기본](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript 기본](./03-javascript-basics.md)
- [Frontend Development 101 (4/10): 컴포넌트와 상태](./04-components-and-state.md)
- [Frontend Development 101 (5/10): 라우팅과 페이지](./05-routing-and-pages.md)
- [Frontend Development 101 (6/10): API 호출과 비동기](./06-api-calls-and-async.md)
- **폼과 유효성 검사 (현재 글)**
- 스타일링과 디자인 시스템 (예정)
- 빌드 도구와 번들링 (예정)
- 작은 프론트엔드 앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [React Hook Form documentation](https://react-hook-form.com/)
- [Zod documentation](https://zod.dev/)
- [MDN: Client-side form validation](https://developer.mozilla.org/en-US/docs/Learn/Forms/Form_validation)

### 확인용 자료
- [WAI: Forms tutorial](https://www.w3.org/WAI/tutorials/forms/)
- [MDN: ARIA aria-invalid](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-invalid)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/frontend-development-101/ko)

Tags: Frontend, Forms, Validation, UX, React
