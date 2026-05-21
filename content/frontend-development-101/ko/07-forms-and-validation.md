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

사용자는 폼을 통해 제품과 가장 길게 대화합니다. 회원가입, 로그인, 결제, 검색, 설정 변경까지 대부분의 중요한 순간이 폼에서 일어납니다. 그런데도 많은 폼은 제출 버튼을 누른 뒤에야 뒤늦게 오류를 보여 줍니다.

이 글은 Frontend Development 101 시리즈의 일곱 번째 글입니다. 여기서는 폼을 단순한 입력 묶음이 아니라 사용자와의 대화 인터페이스로 설명합니다. 좋은 폼은 제출 후에만 검사하지 않고, 입력하는 동안 도와주며, 에러를 친절하고 구체적으로 보여 줍니다.

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

## Before/After

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

Tags: Frontend, Forms, Validation, UX, React
