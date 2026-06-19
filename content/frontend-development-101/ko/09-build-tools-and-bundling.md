---
series: frontend-development-101
episode: 9
title: "Frontend Development 101 (9/10): 빌드 도구와 번들링"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/221"
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
  - Build
  - Vite
  - Bundling
  - Performance
seo_description: Vite와 번들링 최적화 전략을 익힙니다. Tree shaking, 코드 분할, 번들 분석 등 실무 성능 최적화 계층의 핵심 개념을 정리합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (9/10): 빌드 도구와 번들링

소스 코드는 그대로 배포되지 않습니다. 모듈 해석, 변환, 번들링을 거쳐 브라우저가 이해할 수 있는 최종 산출물로 바뀝니다.

이 글은 Frontend Development 101 시리즈의 아홉 번째 글입니다. 여기서는 빌드 도구를 단순한 개발 편의 기능이 아니라 사용자 경험을 결정하는 성능 계층으로 설명합니다. 번들의 모양은 사용자가 첫 화면을 얼마나 빨리 보는지를 좌우합니다.

![Frontend Development 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/09/09-01-diagram.ko.png)
*Frontend Development 101 9장 흐름 개요*

> Webpack·Vite·esbuild는 결국 한 가지 일을 합니다 — 'JS/TS/CSS/asset 그래프를 브라우저가 빠르게 받을 수 있는 형태로 변환하기.' bundle splitting·tree shaking·dev server HMR이 모두 이 한 문장의 변주라는 걸 알면 도구 비교가 단순해집니다.

## 이 글에서 다룰 문제

- 번들러는 import 그래프를 따라 어떤 일을 할까요?
- Vite와 esbuild는 왜 빠르다고 평가될까요?
- tree shaking과 dead code elimination은 어떤 비용을 줄여 줄까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 개념 한눈에 보기

| 용어 | 뜻 | 실무에서 왜 중요한가 |
|---|---|---|
| Module bundler | import 그래프를 따라 파일을 모으고 합치는 도구입니다. | 소스 코드가 어떤 산출물로 바뀌는지 이해하는 출발점이 됩니다. |
| Tree shaking | 사용하지 않는 export를 제거하는 최적화입니다. | 번들 크기를 줄이고 초기 로딩 성능을 직접 개선합니다. |
| Code splitting | 하나의 큰 번들을 여러 청크로 나누는 방식입니다. | 첫 화면에 꼭 필요한 코드만 먼저 보내는 전략의 핵심입니다. |
| Source map | 빌드된 코드와 원본 코드의 대응 관계를 담은 정보입니다. | 디버깅에는 유용하지만, 배포 설정을 잘못하면 코드 노출 위험이 생깁니다. |
| HMR | 전체 새로고침 없이 개발 중 변경분만 반영하는 기능입니다. | 개발 속도를 높이지만, 개발 환경과 운영 환경을 구분해서 보게 해 줍니다. |

## 번들러가 하는 일

**Before (수십 개 `<script>` 태그)**

```html
<!-- 의존성 순서를 사람이 직접 관리 -->
<script src="vendor/lodash.js"></script>
<script src="vendor/react.js"></script>
<script src="src/utils.js"></script>
<script src="src/components/Button.js"></script>
<script src="src/app.js"></script>
<!-- 하나라도 순서가 틀리면 오류 -->
```

**After (`<script>` 하나 + 자동 분할)**

```html
<!-- 번들러가 의존성 그래프를 분석해 최적화 -->
<script type="module" src="/dist/vendor-[hash].js"></script>
<script type="module" src="/dist/index-[hash].js"></script>
<!-- 파일명에 해시가 붙어 캐시 가능 -->
```

번들러가 실제로 하는 일:
```
1. import/require 문을 따라 의존성 그래프 구성
2. TypeScript/JSX → JavaScript 변환
3. 사용하지 않는 코드 제거 (tree shaking)
4. 여러 파일을 하나 또는 여러 청크로 합치기
5. 파일명에 내용 해시 추가 (캐시 버스팅)
6. CSS, 이미지 등 자산 처리
```

## 실습: 개발 빌드 도구를 5단계로 익히기

### 1단계 — Create the project

```bash
npm create vite@latest my-app -- --template react-ts
cd my-app && npm install
```

Vite가 빠른 이유:
- 개발 서버: 네이티브 ESM으로 서빙 (번들링 없음, 파일 단위 변경 반영)
- 프로덕션 빌드: Rollup 사용 (성숙한 tree shaking, code splitting)
- 변환: esbuild 사용 (Go로 작성되어 Babel보다 10~100배 빠름)

### 2단계 — Dev server (HMR)

```bash
npm run dev
# Browser: http://localhost:5173
# 코드 변경 시 페이지 전체 새로고침 없이 해당 모듈만 교체
```

```javascript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // API 프록시: CORS 없이 백엔드 API 호출
    proxy: {
      "/api": {
        target: "http://localhost:3000",
        changeOrigin: true,
      },
    },
  },
});
```

### 3단계 — Production build

```bash
npm run build
# TypeScript 체크 → Rollup 번들링 → 파일 생성

ls -lh dist/assets
# index-[hash].js     크기 확인
# vendor-[hash].js    vendor 청크 (React, react-dom 등)
# index-[hash].css    스타일
```

```javascript
// vite.config.ts - 프로덕션 최적화
export default defineConfig({
  build: {
    // 청크 분리 전략
    rollupOptions: {
      output: {
        manualChunks: {
          // React 관련을 vendor 청크로 분리 (캐시 효율 향상)
          "react-vendor": ["react", "react-dom"],
          // 라우터 분리
          "router": ["react-router-dom"],
        },
      },
    },
    // 청크 크기 경고 기준 (kB)
    chunkSizeWarningLimit: 500,
  },
});
```

### 4단계 — Bundle analysis

```bash
npm install -D rollup-plugin-visualizer
```

```javascript
// vite.config.ts
import { visualizer } from "rollup-plugin-visualizer";

export default defineConfig({
  plugins: [
    react(),
    // 빌드 완료 후 브라우저에서 번들 시각화 열기
    visualizer({
      open: true,
      gzipSize: true,
      brotliSize: true,
      filename: "dist/stats.html",
    }),
  ],
});
```

번들 분석 시 확인할 것:
```
- 가장 큰 모듈이 무엇인가? (lodash 전체를 가져오지 않았는가?)
- vendor 청크와 앱 청크가 적절히 분리됐는가?
- 라우트별 lazy loading이 실제 별도 파일을 만들었는가?
- 이미지나 폰트가 불필요하게 번들에 포함됐는가?
```

### 5단계 — Environment variables and modes

```bash
# .env                  모든 환경 기본값
# .env.development      개발 환경 (npm run dev)
# .env.production       프로덕션 환경 (npm run build)
# .env.staging          스테이징 환경

# .env.production
VITE_API_URL=https://api.example.com
VITE_ANALYTICS_ID=GA-XXXXXXXXX
```

```typescript
// src/config.ts
// VITE_ 접두사가 있어야 클라이언트에 노출됨
const config = {
  apiUrl:      import.meta.env.VITE_API_URL      ?? "http://localhost:3000",
  analyticsId: import.meta.env.VITE_ANALYTICS_ID ?? "",
  isDev:       import.meta.env.DEV,
  isProd:      import.meta.env.PROD,
};

export default config;
```

## Tree Shaking 이해하기

```javascript
// utils.js - 모든 함수를 named export로 제공
export function formatDate(date) { ... }     // 사용함
export function formatCurrency(n) { ... }   // 사용함
export function formatPhoneNumber(s) { ... } // 미사용

// app.js
import { formatDate, formatCurrency } from "./utils";
// 번들러가 formatPhoneNumber는 사용 안 됨을 감지 → 제거

// 잘못된 패턴: 전체 import
import * as utils from "./utils";   // 모든 함수가 번들에 포함됨
import _ from "lodash";              // lodash 전체 (70KB+)

// 올바른 패턴: named import
import { formatDate } from "./utils";
import { debounce } from "lodash-es"; // ES Module 버전 lodash
```

## 코드 분할 패턴

```jsx
// src/App.tsx - 라우트별 lazy loading
import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";

// 각 페이지가 별도 청크로 분리됨
const Dashboard  = lazy(() => import("./pages/Dashboard"));
const Settings   = lazy(() => import("./pages/Settings"));
const Analytics  = lazy(() => import("./pages/Analytics"));

// 공통 로딩 컴포넌트
function PageLoader() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route
        path="/dashboard"
        element={
          <Suspense fallback={<PageLoader />}>
            <Dashboard />
          </Suspense>
        }
      />
      <Route
        path="/settings"
        element={
          <Suspense fallback={<PageLoader />}>
            <Settings />
          </Suspense>
        }
      />
    </Routes>
  );
}
```

## 디버깅 시나리오

### 시나리오 1: 번들이 예상보다 클 때

```bash
# 1. 번들 분석 실행
npm run build
# vite.config.ts에 visualizer 플러그인 있다면 자동으로 stats.html 열림

# 2. 가장 큰 모듈 찾기
npx source-map-explorer "dist/assets/*.js"

# 3. 의심 모듈 크기 확인
npx bundlephobia moment     # moment.js: 67.9KB (gzip)
npx bundlephobia dayjs      # dayjs:      2.2KB (gzip) ← 대안
```

### 시나리오 2: 환경 변수가 undefined일 때

```typescript
// 잘못된 접근
process.env.VITE_API_URL  // undefined! (Vite는 process.env 미지원)

// 올바른 접근
import.meta.env.VITE_API_URL  // Vite 전용 환경 변수

// TypeScript 타입 선언
// src/vite-env.d.ts
interface ImportMetaEnv {
  readonly VITE_API_URL:      string;
  readonly VITE_ANALYTICS_ID: string;
}
interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

### 시나리오 3: 개발 서버와 프로덕션 동작이 다를 때

```bash
# 개발 서버는 ESM 직접 서빙, 프로덕션은 번들된 파일
# 반드시 빌드 후 로컬에서 확인

npm run build
npx serve -s dist  # -s: SPA fallback 활성화

# 또는 Vite preview
npm run preview    # dist/ 폴더를 정적 서버로 서빙
```

## 실무 점검 루프

1. **프로덕션 빌드를 봅니다.** 개발 서버를 믿지 말고 실제 `dist` 산출물을 먼저 확인합니다.
2. **가장 큰 자산을 찾습니다.** 소스 코드를 고치기 전에 어떤 파일이 실제로 무거운지부터 확인합니다.
3. **청크 의도를 확인합니다.** 라우트 단위 lazy loading이 정말 별도 파일을 만들었는지 봅니다.

```bash
npm run build && ls -lh dist/assets
# 더 깊게 보고 싶다면
npx source-map-explorer "dist/assets/*.js"
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|---|---|---|
| `import * as _ from "lodash"` | lodash 전체(70KB+)가 번들에 포함 | `import { debounce } from "lodash-es"`로 named import |
| 개발 서버 = 프로덕션 가정 | 빌드 시 오류 또는 동작 차이 | 반드시 `npm run build` 후 `npm run preview`로 확인 |
| 번들 분석 미실시 | 어떤 라이브러리가 4MB 차지하는지 모름 | 첫 배포 전 반드시 visualizer 또는 source-map-explorer 실행 |
| 프로덕션에 source map 노출 | 원본 코드가 브라우저에서 보임 | `build.sourcemap: false` 또는 서버에서 .map 파일 접근 차단 |
| 이미지 최적화 없이 번들 | 1MB 이미지가 그대로 사용자에게 전달 | vite-imagetools 또는 별도 CDN으로 이미지 처리 |
| VITE_ 접두사 없이 환경 변수 | 브라우저에서 `undefined` | 클라이언트 환경 변수는 반드시 `VITE_` 접두사 |

## 실무에서는 이렇게 보입니다

새 프로젝트는 대체로 Vite, esbuild, SWC 계열 스택을 채택합니다.

```bash
# 번들 크기를 예산처럼 관리하는 CI 설정 예시
# package.json
{
  "scripts": {
    "build": "vite build",
    "size-check": "bundlesize"
  },
  "bundlesize": [
    {
      "path": "./dist/assets/index-*.js",
      "maxSize": "150 kB"  // 초과 시 CI 실패
    },
    {
      "path": "./dist/assets/vendor-*.js",
      "maxSize": "300 kB"
    }
  ]
}
```

```javascript
// 실무 vite.config.ts 전체 예시
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { visualizer } from "rollup-plugin-visualizer";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [
      react(),
      mode === "analyze" && visualizer({ open: true, gzipSize: true }),
    ].filter(Boolean),

    build: {
      sourcemap: mode !== "production",  // 프로덕션에서 source map 비활성화
      rollupOptions: {
        output: {
          manualChunks: {
            "react-vendor": ["react", "react-dom"],
            "router":       ["react-router-dom"],
            "query":        ["@tanstack/react-query"],
          },
        },
      },
    },

    server: {
      proxy: {
        "/api": { target: env.BACKEND_URL, changeOrigin: true },
      },
    },
  };
});
```

## 시니어 엔지니어는 이렇게 생각합니다

- 번들 크기를 예산처럼 다룹니다.
- 주기적으로 번들 분석 결과를 확인합니다.
- 라이브러리를 추가하기 전에 크기를 먼저 봅니다.
- 이미지와 폰트는 별도 최적화 파이프라인으로 다룹니다.
- 가장 느린 사용자를 기준으로 성능을 판단합니다.

## 운영 체크리스트

- [ ] Vite 프로젝트를 만들 수 있습니다.
- [ ] HMR이 동작하는 것을 확인했습니다.
- [ ] `dist/` 안의 산출물을 직접 살펴봤습니다.
- [ ] 번들 분석 도구를 한 번 실행해 봤습니다.
- [ ] 환경 변수로 개발과 프로덕션을 분리할 수 있습니다.
- [ ] tree shaking과 named import의 관계를 이해합니다.

## 연습 문제

1. Vite로 React 프로젝트를 만들고 `npm run build` 후 `dist` 폴더를 살펴보세요.
2. 번들 분석 도구를 적용해 가장 큰 모듈이 무엇인지 적어 보세요.
3. lodash 전체 import와 함수 단위 import를 비교해 번들 크기 차이를 측정해 보세요.
4. 라우트 두 개를 lazy loading으로 분리하고, Network 탭에서 별도 청크 파일로 내려오는지 확인해 보세요.

## 정리 및 다음 단계

빌드 도구는 사용자가 보는 첫 화면이 얼마나 빨리 상호작용 가능해지는지를 결정합니다. 프론트엔드의 마지막 퍼즐은 지금까지 배운 내용을 하나의 앱으로 묶는 일입니다.

다음 글에서는 지금까지의 개념을 모두 모아 작은 프론트엔드 앱을 직접 구성하고 배포해 보겠습니다.

## 처음 질문으로 돌아가기

- **번들러는 import 그래프를 따라 어떤 일을 할까요?**
  - 엔트리 파일부터 import를 재귀적으로 따라가며 의존성 그래프를 구성하고, 변환·최적화·분할 과정을 거쳐 브라우저가 이해할 수 있는 파일로 출력합니다.
- **Vite와 esbuild는 왜 빠르다고 평가될까요?**
  - Vite 개발 서버는 번들링 없이 네이티브 ESM으로 파일을 직접 서빙하고, esbuild는 Go로 작성돼 JavaScript 기반 툴보다 10~100배 빠른 변환을 제공합니다.
- **tree shaking과 dead code elimination은 어떤 비용을 줄여 줄까요?**
  - 실제로 사용하지 않는 코드를 번들에서 제거해 초기 로딩 시간을 줄입니다. lodash 전체를 가져오면 70KB+지만 필요한 함수만 가져오면 수 KB로 줄어들 수 있습니다.

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
- **Frontend Development 101 (9/10): 빌드 도구와 번들링 (현재 글)**
- [작은 프론트엔드 앱 만들기](./10-building-a-small-frontend-app.md)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Vite guide](https://vite.dev/guide/)
- [esbuild documentation](https://esbuild.github.io/)
- [web.dev: Tree shaking and code splitting](https://web.dev/reduce-javascript-payloads-with-tree-shaking/)

### 확인용 자료
- [Bundlephobia](https://bundlephobia.com/)
- [rollup-plugin-visualizer](https://github.com/btd/rollup-plugin-visualizer)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/frontend-development-101/ko)

Tags: Frontend, Build, Vite, Bundling, Performance
