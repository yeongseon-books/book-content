---
series: frontend-development-101
episode: 9
title: "Frontend Development 101 (9/10): 빌드 도구와 번들링"
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
  - Build
  - Vite
  - Bundling
  - Performance
seo_description: Vite와 번들링 최적화 전략을 익힙니다. Tree shaking, 코드 분할, 번들 분석 등 실무 성능 최적화 계층의 핵심 개념을 정리합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (9/10): 빌드 도구와 번들링

프론트엔드 코드는 개발할 때는 수십, 수백 개 파일로 흩어져 있습니다. 그런데 사용자의 브라우저는 그 모든 구조를 그대로 이해하지 않습니다. 결국 누군가는 import 그래프를 따라가고, 필요한 코드를 변환하고, 묶고, 쪼개고, 캐시 가능한 형태로 내보내야 합니다. 그 역할을 맡는 것이 빌드 도구입니다.

이 글은 Frontend Development 101 시리즈의 아홉 번째 글입니다. 여기서는 빌드 도구를 단순한 개발 편의 기능이 아니라 사용자 경험을 결정하는 성능 계층으로 설명합니다. 번들의 모양은 사용자가 첫 화면을 얼마나 빨리 보는지를 좌우합니다.

## 먼저 던지는 질문

- 번들러는 import 그래프를 따라 어떤 일을 할까요?
- Vite와 esbuild는 왜 빠르다고 평가될까요?
- tree shaking과 dead code elimination은 어떤 비용을 줄여 줄까요?

## 큰 그림

![Frontend Development 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/09/09-01-diagram.ko.png)

*Frontend Development 101 9장 흐름 개요*

## 왜 중요한가

번들 크기는 결국 사용자가 직접 지불합니다. 개발자 노트북에서는 가볍게 보이는 1MB JavaScript가 느린 네트워크 환경에서는 몇 초의 빈 화면이 될 수 있습니다. 빌드 도구를 이해하지 못하면 왜 제품이 점점 무거워지는지도 설명하기 어렵습니다.

좋은 번들은 작고, 캐시 가능하고, 적절히 분할되어 있습니다. 이 세 가지를 만족시키는 방향으로 빌드 파이프라인을 설계해야 합니다.

## 개념 한눈에 보기

소스 코드는 그대로 배포되지 않습니다. 모듈 해석, 변환, 번들링을 거쳐 브라우저가 이해할 수 있는 최종 산출물로 바뀝니다.

## 핵심 용어

- **Module bundler**: import 그래프를 따라 파일을 모으고 합치는 도구입니다.
- **Tree shaking**: 사용하지 않는 export를 제거하는 최적화입니다.
- **Code splitting**: 하나의 큰 번들을 여러 청크로 나누는 방식입니다.
- **Source map**: 빌드된 코드와 원본 코드의 대응 관계를 담은 정보입니다.
- **HMR(Hot Module Replacement)**: 전체 새로고침 없이 개발 중 변경분만 반영하는 기능입니다.

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

직접 스크립트 순서를 관리하던 시대와 달리, 현대 프론트엔드는 도구가 의존성을 계산하고 최적의 형태로 내보내는 방향으로 바뀌었습니다.

## 실습: Vite를 5단계로 익히기

### 1단계 — Create the project

```bash
npm create vite@latest my-app -- --template react-ts
cd my-app && npm install
```

### 2단계 — Dev server (HMR)

```bash
npm run dev
# Browser: http://localhost:5173
# The page updates *automatically* on code changes
```

### 3단계 — Production build

```bash
npm run build
# Static files appear in dist/
ls -lh dist/assets
```

### 4단계 — Bundle analysis

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

빌드가 끝나면 어떤 모듈이 큰지 시각적으로 확인합니다.

### 5단계 — Environment variables and modes

```bash
# .env.production
VITE_API_URL=https://api.example.com

# In code
const url = import.meta.env.VITE_API_URL;
```

실무에서는 3단계와 4단계가 특히 중요합니다. 개발 서버가 빠르다고 해서 프로덕션 번들도 좋다고 자동으로 보장되지는 않습니다. 결국 `dist/` 안에 무엇이 만들어졌는지 직접 보는 습관이 필요합니다.

## 검증 포인트

- `npm run build` 뒤에 `dist/assets`에 해시가 붙은 파일이 생성되는지 확인합니다.
- 번들 분석 도구에서 가장 큰 모듈을 확인하고, `VITE_API_URL`이 빌드 모드별로 다르게 들어가는지 확인합니다.

## 문제가 생기면 먼저 볼 것

- 환경 변수가 비어 있으면 `VITE_` 접두사와 `.env.production` 위치를 먼저 확인합니다.
- 번들이 예상보다 크면 전체 라이브러리 import, 큰 이미지, source map 노출 여부를 점검합니다.

## 이 코드에서 주목할 점

- 개발 서버는 ESM을 직접 서빙하므로 초기 부팅이 빠릅니다.
- 빌드 산출물 파일명에는 해시가 붙어 장기 캐시에 유리합니다.
- 번들 분석은 최적화 출발점이지 마지막 단계가 아닙니다.

## 자주 하는 실수 5가지

1. **`import * as _ from "lodash"`처럼 전체 라이브러리를 가져옵니다.** 필요한 함수만 import해야 번들이 가벼워집니다.
2. **개발 서버와 프로덕션 빌드가 같다고 가정합니다.** HMR 코드와 source map은 프로덕션에 그대로 가면 부담이 됩니다.
3. **번들 분석을 한 번도 하지 않습니다.** 어떤 라이브러리가 4MB를 차지하는지 모른 채 배포하게 됩니다.
4. **프로덕션에 source map을 그대로 노출합니다.** 원본 코드가 지나치게 쉽게 읽힐 수 있습니다.
5. **최적화되지 않은 이미지를 함께 번들링합니다.** 1MB 이미지는 그대로 사용자에게 전달됩니다.

## 실무에서는 이렇게 보입니다

새 프로젝트는 대체로 Vite, esbuild, SWC 계열 스택을 채택합니다. 더 큰 모노레포는 Turbopack이나 Rspack 같은 차세대 번들러로 이동하는 흐름도 보입니다. Webpack은 여전히 널리 남아 있지만, 새 프로젝트의 기본 선택지에서는 조금씩 멀어지고 있습니다.

중요한 것은 도구 이름이 아니라 운영 습관입니다. 번들 크기를 예산처럼 관리하고, 라이브러리를 추가하기 전에 비용을 확인하고, 이미지와 폰트도 별도 최적화 파이프라인으로 보는 감각이 필요합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 번들 크기를 예산처럼 다룹니다.
- 주기적으로 번들 분석 결과를 확인합니다.
- 라이브러리를 추가하기 전에 크기를 먼저 봅니다.
- 이미지와 폰트는 별도 최적화 파이프라인으로 다룹니다.
- 가장 느린 사용자를 기준으로 성능을 판단합니다.

## 체크리스트

- [ ] Vite 프로젝트를 만들 수 있습니다.
- [ ] HMR이 동작하는 것을 확인했습니다.
- [ ] `dist/` 안의 산출물을 직접 살펴봤습니다.
- [ ] 번들 분석 도구를 한 번 실행해 봤습니다.
- [ ] 환경 변수로 개발과 프로덕션을 분리할 수 있습니다.

## 연습 문제

1. Vite로 React 프로젝트를 만들고 `npm run build` 후 `dist` 폴더를 살펴보세요.
2. 번들 분석 도구를 적용해 가장 큰 모듈이 무엇인지 적어 보세요.
3. lodash 전체 import와 함수 단위 import를 비교해 번들 크기 차이를 측정해 보세요.

## 정리 및 다음 단계

빌드 도구는 사용자가 보는 첫 화면이 얼마나 빨리 상호작용 가능해지는지를 결정합니다. 프론트엔드의 마지막 퍼즐은 지금까지 배운 내용을 하나의 앱으로 묶는 일입니다.

다음 글에서는 지금까지의 개념을 모두 모아 작은 프론트엔드 앱을 직접 구성하고 배포해 보겠습니다.


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

- **번들러는 import 그래프를 따라 어떤 일을 할까요?**
  - 본문의 기준은 빌드 도구와 번들링를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Vite와 esbuild는 왜 빠르다고 평가될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **tree shaking과 dead code elimination은 어떤 비용을 줄여 줄까요?**
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
- **빌드 도구와 번들링 (현재 글)**
- 작은 프론트엔드 앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Vite guide](https://vite.dev/guide/)
- [esbuild documentation](https://esbuild.github.io/)
- [web.dev: Tree shaking and code splitting](https://web.dev/reduce-javascript-payloads-with-tree-shaking/)

### 확인용 자료
- [Bundlephobia](https://bundlephobia.com/)
- [rollup-plugin-visualizer](https://github.com/btd/rollup-plugin-visualizer)

Tags: Frontend, Build, Vite, Bundling, Performance
