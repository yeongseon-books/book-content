---
series: frontend-development-101
episode: 8
title: 스타일링과 디자인 시스템
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Frontend
  - CSS
  - DesignSystem
  - Tailwind
  - UX
seo_description: CSS Modules, Tailwind, design tokens — 스타일을 일관되게 유지하고 확장하는 디자인 시스템 입문.
last_reviewed: '2026-05-11'
---

# 스타일링과 디자인 시스템

> Frontend Development 101 시리즈 (8/10)


## 이 글에서 다룰 문제

코드가 일관되어도 디자인이 일관되지 않으면 사용자는 금방 어색함을 느낍니다. 같은 버튼이 페이지마다 다르면 제품이 정돈되지 않았다는 인상을 줍니다. 디자인 시스템은 팀 규모에서 일관성을 지키는 방법입니다.

> 좋은 디자인 시스템은 디자이너와 개발자가 같은 언어로 이야기하게 만듭니다.

## 전체 흐름
```mermaid
flowchart LR
    Tokens["Design tokens"] --> Comp["Components"]
    Comp --> Pages["Pages"]
    Tokens --> Theme["Light/Dark theme"]
    Theme --> Pages
```

## Before/After

**Before (페이지마다 다른 색)**

```css
.btn-a { background: #1d72ff; }   /* 페이지 A */
.btn-b { background: #1d70ff; }   /* 페이지 B (오타) */
```

**After (디자인 토큰)**

```css
:root { --color-primary: #1d72ff; }
.btn  { background: var(--color-primary); }
```

## Tailwind로 컴포넌트 5단계

### 1단계 — Tailwind 설치

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 2단계 — 토큰 정의

```javascript
// tailwind.config.js 파일
module.exports = {
  theme: {
    extend: {
      colors: { primary: "#1d72ff", surface: "#f8fafc" },
      spacing: { gutter: "1rem" },
    },
  },
};
```

### 3단계 — Button 컴포넌트

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

### 4단계 — 다크 모드

```jsx
// tailwind.config.js에서 { darkMode: "class" } 설정
<button className="bg-primary dark:bg-primary/80 text-white">
  눌러
</button>
```

### 5단계 — 일관성 강제

```bash
# eslint-plugin-tailwindcss 예시
# 임의의 클래스명, 잘못된 토큰을 lint로 잡습니다.
```

## 이 코드에서 주목할 점

- 모든 색이 `primary` 같은 이름으로 등장하므로 변경 지점이 한곳으로 모입니다.
- `Button` 같은 컴포넌트가 진실의 출처 역할을 합니다.
- 다크 모드는 별도 코드를 늘리기보다 토큰을 분리하는 방식으로 다루는 편이 좋습니다.

## 자주 하는 실수 5가지

1. **컴포넌트마다 색을 직접 적는다.** 디자이너가 색을 바꾸는 순간 수정 범위가 폭발합니다.
2. **버튼/입력의 변형을 문서 없이 만든다.** 디자이너와 합의되지 않은 컴포넌트가 계속 늘어납니다.
3. **다크 모드를 나중에 추가한다.** 색 토큰이 흩어진 뒤에는 거의 모든 컴포넌트를 손봐야 합니다.
4. **간격을 모두 px로 박는다.** 반응형과 접근성이 함께 깨집니다.
5. **컴포넌트 라이브러리에 비즈니스 로직을 넣는다.** 재사용이 어려워집니다.

## 실무에서는 이렇게 쓰입니다

대부분의 회사는 Storybook으로 컴포넌트 카탈로그를 만들고, Tailwind/CSS Modules + 디자인 토큰으로 스타일을 통일합니다. 규모가 큰 회사는 자체 디자인 시스템 패키지를 npm으로 배포해 여러 프로덕트가 같은 컴포넌트를 쓰게 합니다.

## 체크리스트

- [ ] 디자인 토큰의 의미를 안다.
- [ ] CSS Modules 또는 Tailwind로 컴포넌트를 스타일링했다.
- [ ] Storybook을 한 번 써봤다.
- [ ] 다크 모드를 한 번 적용해봤다.
- [ ] 임의의 색/간격이 lint로 잡히는지 확인한다.

## 정리 및 다음 단계

스타일도 공유된 어휘가 있어야 일관성이 생깁니다. 다음 글에서는 그 모든 코드를 브라우저가 읽을 수 있는 형태로 바꾸는 빌드 도구를 봅니다.

<!-- toc:begin -->
- [프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [HTML과 CSS 기본](./02-html-and-css-basics.md)
- [JavaScript 기본](./03-javascript-basics.md)
- [컴포넌트와 상태](./04-components-and-state.md)
- [라우팅과 페이지](./05-routing-and-pages.md)
- [API 호출과 비동기](./06-api-calls-and-async.md)
- [폼과 유효성 검사](./07-forms-and-validation.md)
- **스타일링과 디자인 시스템 (현재 글)**
- 빌드 도구와 번들링 (예정)
- 작은 프론트엔드 앱 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [Tailwind CSS docs](https://tailwindcss.com/)
- [Storybook](https://storybook.js.org/)
- [Design Tokens W3C draft](https://www.w3.org/community/design-tokens/)
- [Material Design](https://m3.material.io/)

Tags: Frontend, CSS, DesignSystem, Tailwind, UX
