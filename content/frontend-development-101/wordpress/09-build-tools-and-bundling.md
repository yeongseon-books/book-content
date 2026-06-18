---
series: frontend-development-101
episode: 9
title: "바이브코딩을 위한 프론트엔드 개발 기초 (9/10): 빌드 도구와 번들링"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - Frontend
  - Build
  - Vite
  - Bundling
  - Performance
seo_description: Vite와 번들링 최적화 전략을 익힙니다. 바이브코딩으로 만든 프론트엔드 앱을 배포 가능한 산출물로 만드는 빌드 파이프라인 핵심 개념을 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 프론트엔드 개발 기초 (9/10): 빌드 도구와 번들링

이 글은 **바이브코딩을 위한 프론트엔드 개발 기초** 시리즈의 아홉 번째 글입니다. AI가 만들어 준 React 앱을 실제로 배포하려면 빌드 도구가 무엇을 하는지 알아야 번들 크기 문제, 환경 변수 오류, 배포 실패를 해결할 수 있습니다.

"AI야, Vite로 React 프로젝트 세팅해줘"라고 하면 설정 파일이 나옵니다. 그런데 `npm run build`가 왜 필요한지, `dist` 폴더 안에 무엇이 생기는지, 환경 변수는 어떻게 관리하는지 모르면 배포 단계에서 막힙니다. 빌드 도구의 역할을 이해해야 이 막힘을 스스로 해결할 수 있습니다.

> Webpack·Vite·esbuild는 결국 한 가지 일을 합니다 — 'JS/TS/CSS/asset 그래프를 브라우저가 빠르게 받을 수 있는 형태로 변환하기.' bundle splitting·tree shaking·dev server HMR이 모두 이 한 문장의 변주라는 걸 알면 도구 비교가 단순해집니다.

## 이 글에서 다룰 문제

- 번들러는 import 그래프를 따라 어떤 일을 할까요?
- Vite와 esbuild는 왜 빠르다고 평가될까요?
- tree shaking과 dead code elimination은 어떤 비용을 줄여 줄까요?
- AI가 설정한 빌드 도구에서 자주 발생하는 문제는 무엇일까요?
- 번들 크기를 줄이기 위해 AI에게 무엇을 요청해야 할까요?

## 바이브코딩 관점에서 시작하기

"AI야, 이 프로젝트를 배포하려면 어떻게 해?"라고 물으면 `npm run build`를 실행하라고 합니다. 그런데 번들이 너무 크거나, 환경 변수가 빌드에 포함되지 않거나, source map이 운영 환경에 노출되는 문제가 생길 수 있습니다. 빌드 도구가 무엇을 하는지 알면 이런 문제를 직접 진단하고 AI에게 올바른 수정을 요청할 수 있습니다.

## 개념 한눈에 보기

| 용어 | 뜻 | 바이브코딩에서 왜 중요한가 |
|---|---|---|
| Module bundler | import 그래프를 따라 파일을 모으고 합치는 도구입니다. | AI가 생성한 import 구조가 빌드 산출물에 어떤 영향을 미치는지 이해하는 기반입니다. |
| Tree shaking | 사용하지 않는 export를 제거하는 최적화입니다. | "전체 라이브러리 import를 함수 단위로 바꿔줘"라고 요청하는 근거가 됩니다. |
| Code splitting | 하나의 큰 번들을 여러 청크로 나누는 방식입니다. | "라우트별 lazy loading 적용해줘"라고 요청하는 기반이 됩니다. |
| Source map | 빌드된 코드와 원본 코드의 대응 관계를 담은 정보입니다. | AI에게 "운영 환경에서 source map 노출 방지 설정해줘"라고 요청해야 합니다. |
| HMR | 전체 새로고침 없이 개발 중 변경분만 반영하는 기능입니다. | 개발 서버와 프로덕션 빌드가 다르다는 것을 이해하는 핵심 개념입니다. |

## 수동 스크립트 관리에서 빌드 파이프라인으로

| 방식 | 파일 관리 방식 | 실무 영향 |
|---|---|---|
| 수동 `<script>` 관리 | 실행 순서와 의존성을 사람이 직접 맞춥니다. | 프로젝트가 커질수록 순서 오류와 중복 로딩 위험이 커집니다. |
| 번들러 기반 파이프라인 | import 그래프를 읽어 빌드와 분할을 자동화합니다. | 캐시, 코드 분할, 환경별 빌드 같은 운영 성능 전략을 적용하기 쉽습니다. |

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

AI가 Vite나 webpack으로 설정한 프로젝트는 두 번째 방식을 사용합니다. `dist` 폴더에 해시가 붙은 파일들이 생기는 이유를 알면 캐시 전략도 이해할 수 있습니다.

## AI 팁: 빌드 최적화 요청

- **번들 분석 설정 요청**: "rollup-plugin-visualizer 또는 webpack-bundle-analyzer로 번들 분석 환경 설정해줘"를 요청하세요.
- **Tree shaking 확인 요청**: "lodash 전체 import 대신 필요한 함수만 import하도록 바꿔줘"를 명시하세요.
- **환경 변수 설정 요청**: ".env.development와 .env.production을 분리해서 관리하는 방법 알려줘"를 요청하세요.
- **Source map 보안 요청**: "프로덕션 빌드에서 source map을 숨기는 설정 추가해줘"를 명시하세요.
- **Lazy loading 연동 요청**: "각 라우트를 React.lazy로 분리해서 별도 청크로 나눠줘"를 요청하면 초기 번들이 작아집니다.

## 실수 유형과 바이브코딩 대처법

| 실수 유형 | 증상 | 바이브코딩 대처 |
|---|---|---|
| 전체 라이브러리 import | 번들 크기 과다 | "import * 대신 필요한 함수만 named import로 바꿔줘" 요청 |
| 개발/프로덕션 빌드 동일하게 가정 | HMR 코드와 source map이 배포에 포함됨 | "프로덕션 빌드 전용 설정 최적화해줘" 요청 |
| 번들 분석 미실시 | 어떤 라이브러리가 번들을 키우는지 모름 | "번들 분석 도구 설정하고 결과 해석 도와줘" 요청 |
| 프로덕션에 source map 노출 | 원본 코드가 쉽게 읽힘 | "vite.config에서 build.sourcemap을 false로 설정해줘" 요청 |
| 이미지 최적화 없음 | 대용량 이미지가 그대로 배포됨 | "이미지를 WebP로 변환하고 크기를 최적화하는 방법 알려줘" 요청 |

## 체크리스트

- [ ] Vite 프로젝트를 만들 수 있습니다.
- [ ] HMR이 동작하는 것을 확인했습니다.
- [ ] `dist/` 안의 산출물을 직접 살펴봤습니다.
- [ ] 번들 분석 도구를 한 번 실행해 봤습니다.
- [ ] 환경 변수로 개발과 프로덕션을 분리할 수 있습니다.
- [ ] AI가 생성한 import 문에서 번들 크기를 키우는 패턴을 발견할 수 있습니다.

## 처음 질문으로 돌아가기

- **번들러는 import 그래프를 따라 어떤 일을 할까요?**
  진입점(main.tsx)에서 시작해 모든 `import` 경로를 따라가며 파일을 모읍니다. JSX·TypeScript를 JavaScript로 변환하고, 사용하지 않는 코드를 제거(tree shaking)하고, 파일들을 하나 또는 여러 청크로 합쳐 최종 `dist` 파일을 만듭니다.

- **Vite와 esbuild는 왜 빠르다고 평가될까요?**
  Vite 개발 서버는 파일을 미리 번들하지 않고 브라우저의 ESM을 직접 활용합니다. esbuild는 Go로 작성되어 JavaScript 번들러보다 수십 배 빠릅니다. 두 도구 모두 "전체 재번들 대신 변경된 부분만 빠르게 처리"하는 전략을 씁니다.

- **tree shaking과 dead code elimination은 어떤 비용을 줄여 줄까요?**
  사용하지 않는 코드를 번들에서 제거해 파일 크기를 줄입니다. `import { debounce } from 'lodash'` 대신 `import debounce from 'lodash/debounce'`처럼 필요한 것만 가져오면 번들 크기가 크게 줄어듭니다.

## 정리

빌드 도구는 사용자가 보는 첫 화면이 얼마나 빨리 상호작용 가능해지는지를 결정합니다. 바이브코딩으로 만든 앱을 배포할 때도 번들 분석, tree shaking, 환경 변수 분리를 처음부터 요청하면 운영 품질이 크게 올라갑니다.

다음 글에서는 지금까지의 개념을 모두 모아 작은 프론트엔드 앱을 직접 구성하고 배포해 봅니다.

## 참고 자료

### 공식 문서
- [Vite guide](https://vite.dev/guide/)
- [esbuild documentation](https://esbuild.github.io/)
- [web.dev: Tree shaking and code splitting](https://web.dev/reduce-javascript-payloads-with-tree-shaking/)

### 확인용 자료
- [Bundlephobia](https://bundlephobia.com/)
- [rollup-plugin-visualizer](https://github.com/btd/rollup-plugin-visualizer)
- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/frontend-development-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 프론트엔드 개발 기초 (1/10): 프론트엔드 개발이란 무엇인가?
- 바이브코딩을 위한 프론트엔드 개발 기초 (2/10): HTML과 CSS 기본
- 바이브코딩을 위한 프론트엔드 개발 기초 (3/10): JavaScript 기본
- 바이브코딩을 위한 프론트엔드 개발 기초 (4/10): 컴포넌트와 상태
- 바이브코딩을 위한 프론트엔드 개발 기초 (5/10): 라우팅과 페이지
- 바이브코딩을 위한 프론트엔드 개발 기초 (6/10): API 호출과 비동기
- 바이브코딩을 위한 프론트엔드 개발 기초 (7/10): 폼과 유효성 검사
- 바이브코딩을 위한 프론트엔드 개발 기초 (8/10): 스타일링과 디자인 시스템
- **바이브코딩을 위한 프론트엔드 개발 기초 (9/10): 빌드 도구와 번들링 (현재 글)**
- 바이브코딩을 위한 프론트엔드 개발 기초 (10/10): 작은 프론트엔드 앱 만들기

<!-- toc:end -->

Tags: 바이브코딩, Frontend, Build, Vite, Bundling, Performance
