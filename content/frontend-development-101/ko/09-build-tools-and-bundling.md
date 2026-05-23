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

이 글은 Frontend Development 101 시리즈의 아홉 번째 글입니다. 여기서는 빌드 도구를 단순한 개발 편의 기능이 아니라 사용자 경험을 결정하는 성능 계층으로 설명합니다. 번들의 모양은 사용자가 첫 화면을 얼마나 빨리 보는지를 좌우합니다.

프론트엔드 코드는 개발할 때는 수십, 수백 개 파일로 흩어져 있습니다. 그런데 사용자의 브라우저는 그 모든 구조를 그대로 이해하지 않습니다. 결국 누군가는 import 그래프를 따라가고, 필요한 코드를 변환하고, 묶고, 쪼개고, 캐시 가능한 형태로 내보내야 합니다. 그 역할을 맡는 것이 빌드 도구입니다.

![Frontend Development 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/09/09-01-diagram.ko.png)
*Frontend Development 101 9장 흐름 개요*

## 먼저 던지는 질문

- 번들러는 import 그래프를 따라 어떤 일을 할까요?
- Vite와 esbuild는 왜 빠르다고 평가될까요?
- tree shaking과 dead code elimination은 어떤 비용을 줄여 줄까요?

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

## 전통 방식과 현대 방식 비교

**Before (수십 개 `<script>` 태그)**

```html
<script src="utils.js"></script>
<script src="auth.js"></script>
<script src="app.js"></script>
```

**After (`<script>` 하나 + 자동 분할)**

```html
<script type="module" src="/dist/index-[hash].js"></script>
```

직접 스크립트 순서를 관리하던 시대와 달리, 현대 프론트엔드는 도구가 의존성을 계산하고 최적의 형태로 내보내는 방향으로 바뀌었습니다.

## 실습: 개발 빌드 도구를 5단계로 익히기

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

## 처음 질문으로 돌아가기

- **번들러는 import 그래프를 따라 어떤 일을 할까요?**
  - 번들러는 흩어져 있는 모듈 import를 따라가며 의존성을 해석하고, 브라우저가 이해할 수 있는 정적 산출물로 묶어 냅니다. 이 과정에서 변환, 코드 합치기, 청크 분할, 해시 파일명 생성까지 함께 수행하므로 사용자가 받는 `dist/assets` 구조 자체를 결정합니다.
- **Vite와 esbuild는 왜 빠르다고 평가될까요?**
  - 본문 기준으로 Vite 개발 서버는 ESM을 직접 서빙해 초기 부팅을 가볍게 만들고, HMR로 바뀐 모듈만 빠르게 반영합니다. esbuild 계열 도구는 변환 속도가 매우 빨라 개발 피드백 루프를 줄여 주기 때문에, 큰 프로젝트에서도 저장 후 화면 반영까지의 체감 시간이 짧습니다.
- **tree shaking과 dead code elimination은 어떤 비용을 줄여 줄까요?**
  - 사용하지 않는 export와 도달 불가능한 코드를 제거하면 사용자가 내려받는 JavaScript 바이트 수와 파싱·실행 비용이 함께 줄어듭니다. 그래서 `import * as _ from "lodash"` 같은 전체 import를 피하고, 번들 분석으로 큰 모듈을 확인하는 습관이 첫 화면 성능과 장기 유지 비용을 동시에 낮춰 줍니다.

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

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/frontend-development-101/ko)

Tags: Frontend, Build, Vite, Bundling, Performance
