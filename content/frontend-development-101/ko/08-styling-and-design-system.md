---
series: frontend-development-101
episode: 8
title: "Frontend Development 101 (8/10): 스타일링과 디자인 시스템"
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
  - CSS
  - DesignSystem
  - Tailwind
  - UX
seo_description: 디자인 토큰과 컴포넌트 기반 스타일 일관성 전략을 익힙니다. Tailwind, 다크 모드 등 실무 스타일링 체계를 정리합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (8/10): 스타일링과 디자인 시스템

초기 프로젝트에서는 버튼 하나쯤 직접 색을 주고 간격을 맞춰도 큰 문제가 없어 보입니다. 하지만 화면이 늘어나고 팀원이 늘어나면 작은 차이가 금방 누적됩니다. 페이지마다 파란색이 조금씩 다르고, 간격 기준이 섞이고, 다크 모드는 나중에 붙이려다 전체를 다시 만지게 됩니다.

이 글은 Frontend Development 101 시리즈의 여덟 번째 글입니다. 여기서는 스타일링을 단순한 CSS 작성이 아니라 일관성을 운영하는 체계로 설명합니다. 색, 간격, 타이포그래피 같은 시각 규칙은 개별 컴포넌트 안에 흩어져 있으면 안 되고 토큰과 공용 컴포넌트 계층으로 모여 있어야 합니다.

## 먼저 던지는 질문

- 글로벌 CSS, CSS Modules, CSS-in-JS, Tailwind는 어떤 차이를 가질까요?
- 디자인 토큰은 왜 프로젝트가 커질수록 더 중요해질까요?
- 컴포넌트 라이브러리는 어떤 구조로 운영되는 편이 좋을까요?

## 큰 그림

![Frontend Development 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/08/08-01-diagram.ko.png)

*Frontend Development 101 8장 흐름 개요*

이 그림에서는 스타일링과 디자인 시스템를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 스타일링과 디자인 시스템의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

코드가 일관되어도 디자인이 일관되지 않으면 사용자는 제품을 미완성으로 느낍니다. 페이지마다 버튼 느낌이 다르면 기술적 품질과 별개로 신뢰가 떨어집니다. 디자인 시스템은 팀 규모에서의 일관성이라고 볼 수 있습니다.

좋은 디자인 시스템은 디자이너와 엔지니어가 같은 언어를 쓰게 만듭니다. “이 버튼은 primary인가 secondary인가”, “spacing token은 어느 단계인가” 같은 대화가 가능해지면 변경도 훨씬 빨라집니다.

## 개념 한눈에 보기

디자인 토큰이 가장 아래의 공통 규칙이고, 컴포넌트는 그 규칙을 구현하며, 페이지는 그 컴포넌트를 조합합니다. 다크 모드도 대개 구조 자체를 바꾸는 것이 아니라 토큰 값을 바꾸는 문제로 다뤄야 합니다.

## 핵심 용어

- **디자인 토큰**: 색, 간격, 타이포그래피 같은 원자 단위 규칙입니다.
- **CSS Modules**: 클래스 이름 충돌을 자동으로 줄여 주는 방식입니다.
- **CSS-in-JS**: 컴포넌트 함수 안에서 스타일을 정의하는 접근입니다.
- **Utility-first CSS**: 작은 클래스를 조합해 스타일을 만드는 방식입니다.
- **컴포넌트 라이브러리**: 디자인 시스템을 구현한 재사용 가능한 컴포넌트 모음입니다.

## Before/After

**Before (different colors per page)**

```css
.btn-a { background: #1d72ff; }   /* page A */
.btn-b { background: #1d70ff; }   /* page B (typo) */
```

**After (design token)**

```css
:root { --color-primary: #1d72ff; }
.btn  { background: var(--color-primary); }
```

겉으로 보면 작은 차이 같지만, 실제 운영에서는 이런 차이가 계속 쌓입니다. 토큰이 없으면 색상 변경 하나가 프로젝트 전체의 수작업이 됩니다.

## 실습: Tailwind 기반 컴포넌트를 5단계로 만들기

### 1단계 — Install Tailwind

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 2단계 — Define tokens

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: { primary: "#1d72ff", surface: "#f8fafc" },
      spacing: { gutter: "1rem" },
    },
  },
};
```

### 3단계 — Button component

```jsx
function Button({ children, variant = "primary" }) {
  const base = "px-4 py-2 rounded font-medium transition";
  const variants = {
    primary:   "bg-primary text-white hover:opacity-90",
    secondary: "bg-surface text-gray-900 border border-gray-200",
  };
  return <button className={`${base} ${variants[variant]}`}>{children}</button>;
}
```

### 4단계 — Dark mode

```jsx
// tailwind.config.js: { darkMode: "class" }
<button className="bg-primary dark:bg-primary/80 text-white">
  Click
</button>
```

### 5단계 — Enforce consistency

```bash
# eslint-plugin-tailwindcss
# Catches arbitrary class names and bad token usage at lint time.
```

이 예제에서 핵심은 스타일이 컴포넌트 내부에 흩어져 있지 않다는 점입니다. 이름 있는 토큰을 기준으로 버튼 변형을 정의하고, 다크 모드도 새 코드를 많이 추가하는 대신 토큰 조합으로 해결합니다.

## 검증 포인트

- 토큰 값 하나를 바꿨을 때 버튼과 표면색이 한 번에 바뀌는지 확인합니다.
- 다크 모드 클래스를 켰을 때 대비와 상태 스타일이 모두 같이 바뀌는지 확인합니다.

## 문제가 생기면 먼저 볼 것

- 색이 일부만 바뀌면 하드코딩 색상이 남아 있는지 확인합니다.
- 다크 모드가 안 먹으면 `darkMode` 설정과 실제 클래스 부착 위치를 먼저 봅니다.

## 이 코드에서 주목할 점

- 모든 색이 `primary` 같은 이름으로 표현되어 변경 지점이 한곳으로 모입니다.
- `Button` 컴포넌트가 스타일의 진실의 출처 역할을 합니다.
- 다크 모드는 별도 기능이 아니라 토큰 체계를 확장하는 문제로 다루는 편이 좋습니다.

## 자주 하는 실수 5가지

1. **컴포넌트마다 색을 직접 하드코딩합니다.** 디자이너가 색을 바꾸면 고통이 시작됩니다.
2. **문서 없이 variant를 계속 늘립니다.** 합의된 디자인과 실제 코드가 금방 어긋납니다.
3. **다크 모드를 나중 일로 미룹니다.** 색이 흩어져 있을수록 전체 컴포넌트를 다시 만져야 합니다.
4. **간격을 모두 `px`로 박아 둡니다.** 반응형과 접근성 대응이 어려워집니다.
5. **컴포넌트 라이브러리에 비즈니스 로직을 넣습니다.** 재사용성이 빠르게 무너집니다.

## 실무에서는 이렇게 보입니다

대부분의 팀은 Storybook으로 컴포넌트를 카탈로그화하고, Tailwind나 CSS Modules와 디자인 토큰을 조합해 일관성을 유지합니다. 큰 조직은 디자인 시스템 자체를 npm 패키지로 배포해 여러 제품이 같은 컴포넌트를 공유하기도 합니다.

이때 중요한 기준은 새 컴포넌트를 만들기 전에 기존 컴포넌트가 왜 충분하지 않은지 설명할 수 있는가입니다. 디자인 시스템은 무한히 늘리는 저장소가 아니라 선택과 제약의 체계여야 합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 토큰 없는 색상은 코드 리뷰에서 잡혀야 합니다.
- 디자인 시스템은 디자이너와 함께 만드는 것입니다.
- 새 컴포넌트는 왜 기존 것을 못 쓰는지 먼저 설명해야 합니다.
- Storybook은 컴포넌트에 대한 단위 테스트 같은 역할을 합니다.
- 다크 모드는 토큰 수준에서 해결해야 유지 비용이 낮습니다.

## 체크리스트

- [ ] 디자인 토큰의 의미를 설명할 수 있습니다.
- [ ] CSS Modules나 Tailwind로 컴포넌트를 스타일링해 봤습니다.
- [ ] Storybook을 한 번 사용해 봤습니다.
- [ ] 다크 모드를 한 번 적용해 봤습니다.
- [ ] 임의의 색상과 간격을 잡아내는 lint 규칙의 필요성을 이해합니다.

## 연습 문제

1. Tailwind 토큰에 `primary` 색을 정의하고 Button에 적용해 보세요.
2. Storybook을 설치하고 Button 변형 두 가지를 문서화해 보세요.
3. `prefers-color-scheme` 또는 class 기반 스위치로 다크 모드를 적용해 보세요.

## 정리 및 다음 단계

스타일링도 결국 공통 언어가 있어야 규모를 버팁니다. 디자인 토큰과 컴포넌트 체계가 잡혀야 팀이 커져도 화면 품질이 흔들리지 않습니다.

다음 글에서는 이 코드와 스타일을 브라우저가 읽을 수 있는 산출물로 바꾸는 빌드 도구와 번들링을 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **글로벌 CSS, CSS Modules, CSS-in-JS, Tailwind는 어떤 차이를 가질까요?**
  - 본문의 기준은 스타일링과 디자인 시스템를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **디자인 토큰은 왜 프로젝트가 커질수록 더 중요해질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **컴포넌트 라이브러리는 어떤 구조로 운영되는 편이 좋을까요?**
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
- **스타일링과 디자인 시스템 (현재 글)**
- 빌드 도구와 번들링 (예정)
- 작은 프론트엔드 앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Tailwind CSS documentation](https://tailwindcss.com/docs/installation)
- [Storybook documentation](https://storybook.js.org/docs)
- [W3C Design Tokens Community Group](https://www.w3.org/community/design-tokens/)

### 확인용 자료
- [Material Design 3](https://m3.material.io/)
- [MDN: prefers-color-scheme](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme)

Tags: Frontend, CSS, DesignSystem, Tailwind, UX
