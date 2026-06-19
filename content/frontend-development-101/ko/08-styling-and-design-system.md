---
series: frontend-development-101
episode: 8
title: "Frontend Development 101 (8/10): 스타일링과 디자인 시스템"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/220"
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
  - CSS
  - DesignSystem
  - Tailwind
  - UX
seo_description: 디자인 토큰과 컴포넌트 기반 스타일 일관성 전략을 익힙니다. Tailwind, 다크 모드 등 실무 스타일링 체계를 정리합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (8/10): 스타일링과 디자인 시스템

디자인 토큰이 가장 아래의 공통 규칙이고, 컴포넌트는 그 규칙을 구현하며, 페이지는 그 컴포넌트를 조합합니다. 다크 모드도 대개 구조 자체를 바꾸는 것이 아니라 토큰 값을 바꾸는 문제로 다뤄야 합니다.

이 글은 Frontend Development 101 시리즈의 여덟 번째 글입니다. 여기서는 스타일링을 단순한 CSS 작성이 아니라 일관성을 운영하는 체계로 설명합니다. 색, 간격, 타이포그래피 같은 시각 규칙은 개별 컴포넌트 안에 흩어져 있으면 안 되고 토큰과 공용 컴포넌트 계층으로 모여 있어야 합니다.

![Frontend Development 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/08/08-01-diagram.ko.png)
*Frontend Development 101 8장 흐름 개요*

> 스타일링의 핵심 질문은 '문법 선택'이 아니라 '스타일의 범위(scope)와 결합도를 어떻게 통제할 것인가'입니다 — BEM·CSS Modules·Tailwind·CSS-in-JS는 같은 문제(전역 cascading)에 대한 서로 다른 답입니다.

## 이 글에서 다룰 문제

- 글로벌 CSS, CSS Modules, CSS-in-JS, Tailwind는 어떤 차이를 가질까요?
- 디자인 토큰은 왜 프로젝트가 커질수록 더 중요해질까요?
- 컴포넌트 라이브러리는 어떤 구조로 운영되는 편이 좋을까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 개념 한눈에 보기

| 용어 | 뜻 | 실무에서 왜 중요한가 |
|---|---|---|
| 디자인 토큰 | 색, 간격, 타이포그래피 같은 원자 단위 규칙입니다. | 브랜드 변경, 다크 모드, 컴포넌트 통일성을 한곳에서 제어하게 해 줍니다. |
| CSS Modules | 클래스 이름 충돌을 자동으로 줄여 주는 방식입니다. | 중간 규모 프로젝트에서 예측 가능한 범위의 스타일 격리를 제공합니다. |
| CSS-in-JS | 컴포넌트 함수 안에서 스타일을 정의하는 접근입니다. | 상태 기반 스타일링이 편하지만 런타임 비용과 도구 선택이 따라옵니다. |
| Utility-first CSS | 작은 클래스를 조합해 스타일을 만드는 방식입니다. | 화면을 빠르게 만들 수 있지만, 토큰 규칙이 없으면 난잡해지기 쉽습니다. |
| 컴포넌트 라이브러리 | 디자인 시스템을 구현한 재사용 가능한 컴포넌트 모음입니다. | 팀이 같은 버튼, 입력창, 카드 규칙을 공유하게 만드는 운영 기반입니다. |

## 스타일링 방식 비교

```css
/* 1. 전역 CSS */
/* button.css */
.btn-primary {
  background: #1d72ff;  /* 값이 흩어짐 → 변경 시 전체 검색 필요 */
  color: white;
  padding: 8px 16px;
}
```

```css
/* 2. CSS Modules */
/* Button.module.css */
.button {
  background: var(--color-primary);  /* 토큰 참조 */
  color: white;
  padding: var(--spacing-2) var(--spacing-4);
}

/* 빌드 후 클래스명이 자동으로 고유해짐: .Button_button__3xNvj */
```

```jsx
/* 3. CSS-in-JS (예: vanilla-extract, Emotion) */
const buttonStyle = css({
  background: vars.color.primary,
  color: "white",
  padding: `${vars.spacing[2]} ${vars.spacing[4]}`,
  ":hover": { opacity: 0.9 },
});
```

```jsx
/* 4. Tailwind CSS */
<button className="bg-primary text-white px-4 py-2 rounded hover:opacity-90">
  클릭
</button>
```

**Before (페이지마다 다른 색상)**

```css
.btn-a { background: #1d72ff; }   /* page A */
.btn-b { background: #1d70ff; }   /* page B (오타) */
.btn-c { background: #1D72FF; }   /* page C (대소문자) */
```

**After (디자인 토큰)**

```css
:root {
  /* 기본 토큰 */
  --color-primary-500: #1d72ff;
  --color-primary-600: #1b65e6;

  /* 시맨틱 토큰 */
  --color-action-default:  var(--color-primary-500);
  --color-action-hover:    var(--color-primary-600);

  --spacing-1: 0.25rem;
  --spacing-2: 0.5rem;
  --spacing-4: 1rem;

  --radius-sm: 4px;
  --radius-md: 8px;

  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
}

.btn {
  background: var(--color-action-default);
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--radius-md);
}
.btn:hover {
  background: var(--color-action-hover);
}
```

## 실습: 유틸리티 스타일 기반 컴포넌트를 5단계로 만들기

### 1단계 — Install Tailwind

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 2단계 — Define tokens

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#1d72ff",
          hover:   "#1b65e6",
          light:   "#e8f0fe",
        },
        surface: {
          DEFAULT: "#ffffff",
          muted:   "#f8fafc",
        },
        text: {
          primary:   "#1e293b",
          secondary: "#64748b",
          disabled:  "#94a3b8",
        },
      },
      spacing: {
        "gutter-sm": "1rem",
        "gutter-md": "1.5rem",
        "gutter-lg": "2rem",
      },
      borderRadius: {
        DEFAULT: "8px",
        lg: "12px",
      },
    },
  },
};
```

### 3단계 — Button component

```jsx
// src/components/ui/Button.jsx
const buttonVariants = {
  primary:   "bg-primary text-white hover:bg-primary-hover focus-visible:ring-primary",
  secondary: "bg-surface text-text-primary border border-slate-200 hover:bg-surface-muted",
  danger:    "bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-500",
  ghost:     "text-text-primary hover:bg-surface-muted",
};

const buttonSizes = {
  sm: "px-3 py-1.5 text-sm rounded",
  md: "px-4 py-2   text-base rounded",
  lg: "px-6 py-3   text-lg rounded-lg",
};

export function Button({
  children,
  variant = "primary",
  size = "md",
  disabled = false,
  loading = false,
  onClick,
  type = "button",
  className = "",
}) {
  const base = [
    "inline-flex items-center justify-center gap-2",
    "font-medium transition-all duration-150",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
    "disabled:opacity-50 disabled:cursor-not-allowed",
    buttonVariants[variant],
    buttonSizes[size],
    className,
  ].join(" ");

  return (
    <button
      type={type}
      className={base}
      disabled={disabled || loading}
      onClick={onClick}
      aria-busy={loading}
    >
      {loading && (
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
      )}
      {children}
    </button>
  );
}

// 사용 예시
<Button variant="primary" size="lg">저장하기</Button>
<Button variant="secondary">취소</Button>
<Button variant="danger" loading={isDeleting}>삭제</Button>
```

### 4단계 — Dark mode

```jsx
// src/components/ThemeToggle.jsx
import { useState, useEffect } from "react";

export function ThemeToggle() {
  const [isDark, setIsDark] = useState(
    () => window.matchMedia("(prefers-color-scheme: dark)").matches
  );

  useEffect(() => {
    // class 기반 다크 모드: html 태그에 'dark' 클래스 토글
    document.documentElement.classList.toggle("dark", isDark);
    localStorage.setItem("theme", isDark ? "dark" : "light");
  }, [isDark]);

  return (
    <button
      onClick={() => setIsDark(d => !d)}
      aria-label={isDark ? "라이트 모드로 전환" : "다크 모드로 전환"}
      className="p-2 rounded-md text-text-secondary hover:bg-surface-muted"
    >
      {isDark ? "☀️" : "🌙"}
    </button>
  );
}

// Tailwind 다크 모드 클래스 사용
// tailwind.config.js: darkMode: "class"
<div className="bg-white dark:bg-slate-900 text-text-primary dark:text-slate-100">
  <Button className="bg-primary dark:bg-primary/80">
    다크 모드 버튼
  </Button>
</div>
```

### 5단계 — Enforce consistency

```bash
# eslint-plugin-tailwindcss 설치
npm install -D eslint-plugin-tailwindcss

# .eslintrc.js
{
  "plugins": ["tailwindcss"],
  "rules": {
    "tailwindcss/classnames-order": "warn",      // 클래스 정렬
    "tailwindcss/no-custom-classname": "error",  // 임의 클래스 금지
  }
}

# 하드코딩된 값 검색
grep -rn "color\s*:\s*#\|background\s*:\s*#" src/ --include="*.css"
```

## Card 컴포넌트 패턴

```jsx
// src/components/ui/Card.jsx
// 합성 패턴으로 유연한 카드 컴포넌트

export function Card({ children, className = "" }) {
  return (
    <article
      className={`bg-surface rounded-lg border border-slate-200 overflow-hidden shadow-sm dark:bg-slate-800 dark:border-slate-700 ${className}`}
    >
      {children}
    </article>
  );
}

export function CardHeader({ children }) {
  return (
    <div className="px-gutter-md py-4 border-b border-slate-200 dark:border-slate-700">
      {children}
    </div>
  );
}

export function CardBody({ children }) {
  return <div className="px-gutter-md py-gutter-sm">{children}</div>;
}

export function CardFooter({ children }) {
  return (
    <div className="px-gutter-md py-4 bg-surface-muted dark:bg-slate-900 flex justify-end gap-2">
      {children}
    </div>
  );
}

// 사용: 조각을 원하는 대로 조합
function ProductCard({ product }) {
  return (
    <Card>
      <CardHeader>
        <img src={product.image} alt={product.name} className="w-full h-48 object-cover" />
      </CardHeader>
      <CardBody>
        <h2 className="text-lg font-semibold text-text-primary">{product.name}</h2>
        <p className="text-text-secondary">{product.price.toLocaleString()}원</p>
      </CardBody>
      <CardFooter>
        <Button variant="secondary">담기</Button>
        <Button>구매하기</Button>
      </CardFooter>
    </Card>
  );
}
```

## 디버깅 시나리오

### 시나리오 1: 색이 일부만 바뀔 때

```bash
# 하드코딩된 색상 찾기
grep -rn "#1d72ff\|bg-blue-600\|color: blue" src/

# 발견된 파일에서 토큰으로 교체
# background: #1d72ff; → background: var(--color-action-default);
# bg-blue-600 → bg-primary (Tailwind 토큰)
```

### 시나리오 2: 다크 모드가 일부 컴포넌트에서 안 될 때

```jsx
// 문제: 하드코딩된 색상은 다크 모드 토글에 반응 안 함
<div style={{ background: "#ffffff" }}>  // 안 바뀜

// 해결: 토큰 또는 Tailwind 다크 클래스 사용
<div className="bg-white dark:bg-slate-900">  // 바뀜
```

### 시나리오 3: 간격이 일관되지 않을 때

```css
/* 문제: 임의의 px 값 혼용 */
.card { padding: 13px; }
.modal { padding: 15px; }

/* 해결: spacing 토큰만 사용 */
.card  { padding: var(--spacing-4); }   /* 1rem = 16px */
.modal { padding: var(--spacing-4); }   /* 동일 */
```

## 실무 점검 루프

1. **토큰 사용 여부를 봅니다.** 컴포넌트를 고치기 전에 하드코딩된 색상과 간격 값이 숨어 있지 않은지 찾습니다.
2. **컴포넌트 경계를 봅니다.** 시각 변경이 공유 컴포넌트에 속하는지, 특정 페이지 레이아웃에만 속하는지 구분합니다.
3. **테마 검증을 봅니다.** 기본 화면만 보지 말고 dark mode에서 hover, focus, disabled 상태까지 같이 비교합니다.

```bash
grep -R "#[0-9a-fA-F]\{3,6\}\|margin:\s*[0-9]px\|padding:\s*[0-9]px" src/ || true
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|---|---|---|
| 컴포넌트마다 색을 직접 하드코딩 | 브랜드 색 변경 시 전체 검색·수정 필요 | 모든 색을 토큰으로 참조 |
| 문서 없이 variant를 계속 추가 | 합의된 디자인과 코드가 어긋남 | 새 variant마다 디자인 팀과 합의 후 추가 |
| 다크 모드를 나중 일로 미룸 | 색이 흩어져 있을수록 전체를 다시 수정해야 함 | 처음부터 `dark:` 클래스 함께 작성 |
| 간격을 `px`로 직접 지정 | 반응형·접근성 대응이 어려워짐 | `rem` 기반 spacing 토큰 사용 |
| 컴포넌트 라이브러리에 비즈니스 로직 포함 | 재사용성 저하, 라이브러리 교체 어려움 | UI 컴포넌트는 순수하게, 로직은 훅으로 분리 |
| Storybook 없이 컴포넌트 개발 | 다양한 상태(hover, disabled, dark) 검증 어려움 | Storybook으로 모든 variant 문서화 |

## 실무에서는 이렇게 보입니다

대부분의 팀은 Storybook으로 컴포넌트를 카탈로그화하고, Tailwind나 CSS Modules와 디자인 토큰을 조합해 일관성을 유지합니다.

```jsx
// src/components/ui/Button.stories.jsx
export default {
  title: "UI/Button",
  component: Button,
  argTypes: {
    variant: { control: "select", options: ["primary", "secondary", "danger", "ghost"] },
    size:    { control: "select", options: ["sm", "md", "lg"] },
  },
};

export const Primary   = { args: { children: "기본 버튼", variant: "primary" } };
export const Secondary = { args: { children: "보조 버튼", variant: "secondary" } };
export const Loading   = { args: { children: "저장 중...", loading: true } };
export const Disabled  = { args: { children: "비활성", disabled: true } };
```

## 시니어 엔지니어는 이렇게 생각합니다

- 토큰 없는 색상은 코드 리뷰에서 잡혀야 합니다.
- 디자인 시스템은 디자이너와 함께 만드는 것입니다.
- 새 컴포넌트는 왜 기존 것을 못 쓰는지 먼저 설명해야 합니다.
- Storybook은 컴포넌트에 대한 단위 테스트 같은 역할을 합니다.
- 다크 모드는 토큰 수준에서 해결해야 유지 비용이 낮습니다.

## 운영 체크리스트

- [ ] 디자인 토큰의 의미를 설명할 수 있습니다.
- [ ] CSS Modules나 Tailwind로 컴포넌트를 스타일링해 봤습니다.
- [ ] Storybook을 한 번 사용해 봤습니다.
- [ ] 다크 모드를 한 번 적용해 봤습니다.
- [ ] 임의의 색상과 간격을 잡아내는 lint 규칙의 필요성을 이해합니다.
- [ ] Button 컴포넌트의 모든 variant를 한 곳에서 관리할 수 있습니다.

## 연습 문제

1. Tailwind 토큰에 `primary` 색을 정의하고 Button에 적용해 보세요.
2. Storybook을 설치하고 Button 변형 두 가지를 문서화해 보세요.
3. `prefers-color-scheme` 또는 class 기반 스위치로 다크 모드를 적용해 보세요.
4. `eslint-plugin-tailwindcss`로 하드코딩된 클래스를 자동 감지하는 환경을 만들어 보세요.

## 정리 및 다음 단계

스타일링도 결국 공통 언어가 있어야 규모를 버팁니다. 디자인 토큰과 컴포넌트 체계가 잡혀야 팀이 커져도 화면 품질이 흔들리지 않습니다.

다음 글에서는 이 코드와 스타일을 브라우저가 읽을 수 있는 산출물로 바꾸는 빌드 도구와 번들링을 봅니다.

## 처음 질문으로 돌아가기

- **글로벌 CSS, CSS Modules, CSS-in-JS, Tailwind는 어떤 차이를 가질까요?**
  - 모두 전역 cascading 문제를 다르게 풉니다. 글로벌 CSS는 전역 그대로, CSS Modules는 파일 범위로 격리, CSS-in-JS는 컴포넌트 범위로 격리, Tailwind는 클래스 단위 유틸리티로 cascading 자체를 최소화합니다.
- **디자인 토큰은 왜 프로젝트가 커질수록 더 중요해질까요?**
  - 파일이 많아질수록 색상이나 간격 값이 흩어지고, 한 번 변경 시 전체를 검색해야 합니다. 토큰이 있으면 한 곳만 바꿔도 전체가 반영됩니다.
- **컴포넌트 라이브러리는 어떤 구조로 운영되는 편이 좋을까요?**
  - 원자(색, 타이포그래피) → 컴포넌트(Button, Input) → 패턴(Form, Card) 순서로 계층을 두고, 각 컴포넌트는 비즈니스 로직 없이 순수하게 유지합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML과 CSS 기본](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript 기본](./03-javascript-basics.md)
- [Frontend Development 101 (4/10): 컴포넌트와 상태](./04-components-and-state.md)
- [Frontend Development 101 (5/10): 라우팅과 페이지](./05-routing-and-pages.md)
- [Frontend Development 101 (6/10): API 호출과 비동기](./06-api-calls-and-async.md)
- [Frontend Development 101 (7/10): 폼과 유효성 검사](./07-forms-and-validation.md)
- **Frontend Development 101 (8/10): 스타일링과 디자인 시스템 (현재 글)**
- [Frontend Development 101 (9/10): 빌드 도구와 번들링](./09-build-tools-and-bundling.md)
- [작은 프론트엔드 앱 만들기](./10-building-a-small-frontend-app.md)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Tailwind CSS documentation](https://tailwindcss.com/docs/installation)
- [Storybook documentation](https://storybook.js.org/docs)
- [W3C Design Tokens Community Group](https://www.w3.org/community/design-tokens/)

### 확인용 자료
- [Material Design 3](https://m3.material.io/)
- [MDN: prefers-color-scheme](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/frontend-development-101/ko)

Tags: Frontend, CSS, DesignSystem, Tailwind, UX
