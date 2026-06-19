---
series: web-development-101
episode: 2
title: "Web Development 101 (2/10): HTML, CSS, JavaScript"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/204"
    published_at: '2026-05-26'
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - WebDevelopment
  - HTML
  - CSS
  - JavaScript
  - Frontend
seo_description: HTML, CSS, JavaScript가 구조, 스타일, 동작을 어떻게 나누는지 설명합니다.
last_reviewed: '2026-05-15'
---

# Web Development 101 (2/10): HTML, CSS, JavaScript

웹 페이지를 처음 만들 때는 세 언어가 왜 따로 존재하는지 잘 와닿지 않습니다. 화면 하나를 만들 뿐인데 구조용 언어, 스타일용 언어, 동작용 언어가 따로 있다는 사실이 오히려 번거롭게 보이기도 합니다. 하지만 규모가 조금만 커져도 이 분리가 왜 중요한지 금방 드러납니다.

이 글은 Web Development 101 시리즈의 2번째 글입니다.

여기서는 HTML, CSS, JavaScript가 각각 무엇을 맡고, 왜 세 층을 분리하는 편이 유지보수와 협업에 유리한지 정리하겠습니다.

![Web Development 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/02/02-01-concept-at-a-glance.ko.png)
*Web Development 101 2장 흐름 개요*

> HTML·CSS·JavaScript는 구조·표현·동작이라는 서로 다른 책임을 가진 세 층입니다 — 한 화면을 만들 때는 번거롭게 느껴지지만, 이 분리가 유지보수와 협업 비용을 좌우합니다.

## 이 글에서 다룰 문제

- 웹 페이지는 왜 세 가지 언어로 나뉠까요?
- HTML, CSS, JavaScript는 각각 무엇을 책임질까요?
- 세 언어가 함께 동작할 때 어떤 연결 지점이 생길까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 구분이 중요한가

세 언어가 한 파일 안에서 뒤엉키면 한 줄을 고칠 때마다 다른 영역이 흔들립니다. 디자인 수정이 동작 버그를 부르고, 스크립트 변경이 마크업 구조를 깨뜨리는 식입니다. 작은 예제에서는 버틸 수 있어도 팀 작업으로 넘어가면 금방 읽기 어려워집니다.

이 분리는 단지 미적인 취향이 아닙니다. 디자이너는 CSS를, 프론트엔드 엔지니어는 JavaScript를, 콘텐츠 담당자는 HTML을 주로 다룹니다. 역할이 나뉘어야 변경 범위가 좁아지고, 캐시 전략도 단순해지고, 코드 리뷰도 훨씬 쉬워집니다.

## 세 언어의 역할 구조

```
┌─────────────────────────────────────────────────────┐
│                  웹 페이지                           │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │    HTML     │  │    CSS      │  │ JavaScript  │ │
│  │  (구조)     │  │  (스타일)   │  │  (동작)     │ │
│  │             │  │             │  │             │ │
│  │ - 제목      │  │ - 색상      │  │ - 클릭      │ │
│  │ - 문단      │  │ - 폰트      │  │ - 폼 제출   │ │
│  │ - 링크      │  │ - 레이아웃  │  │ - API 호출  │ │
│  │ - 폼        │  │ - 여백      │  │ - DOM 수정  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
│         ↑                ↑                ↑         │
│    class, id       selector          querySelector  │
│    (연결 고리)                                       │
└─────────────────────────────────────────────────────┘
```

## 먼저 알아둘 용어

- **HTML**: 제목, 문단, 링크, 폼 같은 구조를 표현합니다.
- **CSS**: 색상, 폰트, 레이아웃처럼 보이는 스타일을 정의합니다.
- **JavaScript**: 클릭, 입력, 비동기 호출 같은 동작을 추가합니다.
- **Selector**: CSS가 어느 요소에 적용될지 고르는 규칙입니다.
- **Event**: 사용자 입력이나 브라우저 상태 변화를 JavaScript가 받을 수 있게 하는 신호입니다.
- **defer**: HTML 파싱이 끝난 뒤 스크립트를 실행하게 하는 속성입니다.

## 혼합 vs 분리 비교

### Before: 모든 것이 혼합된 코드

```html
<!-- 나쁜 예: HTML 안에 CSS와 JS가 뒤섞임 -->
<h1 style="color: red; font-size: 2rem;" onclick="alert('hi')">제목</h1>
<p style="color: gray; margin-top: 1rem;">설명 문구</p>
<button style="padding: 8px 16px; background: blue; color: white;"
        onclick="document.querySelector('p').style.display='none'">
  숨기기
</button>
```

이 코드는 동작하지만 문제가 많습니다. 제목 색을 바꾸려면 HTML을 열어야 하고, 버튼 동작을 바꾸려면 HTML 태그 안을 뒤져야 합니다. CSS 캐시도 활용할 수 없습니다.

### After: 역할 분리

```html
<!-- index.html: 구조만 -->
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <title>역할 분리 예제</title>
    <link rel="stylesheet" href="style.css">
  </head>
  <body>
    <h1 class="page-title">제목</h1>
    <p class="description">설명 문구</p>
    <button id="hide-btn" class="btn">숨기기</button>
    <script src="app.js" defer></script>
  </body>
</html>
```

```css
/* style.css: 스타일만 */
.page-title {
  color: red;
  font-size: 2rem;
}

.description {
  color: gray;
  margin-top: 1rem;
}

.btn {
  padding: 8px 16px;
  background: blue;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn:hover {
  background: darkblue;
}
```

```js
// app.js: 동작만
document.getElementById("hide-btn").addEventListener("click", () => {
  const desc = document.querySelector(".description");
  desc.style.display = desc.style.display === "none" ? "" : "none";
});
```

이제 색상을 바꿀 때는 CSS 파일만, 클릭 동작을 바꿀 때는 JS 파일만 건드립니다.

## 완성도 높은 HTML 구조 예시

```html
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="페이지 설명">
    <title>페이지 제목</title>
    <link rel="stylesheet" href="style.css">
  </head>
  <body>
    <!-- semantic 태그 사용 -->
    <header>
      <nav>
        <a href="/">홈</a>
        <a href="/about">소개</a>
      </nav>
    </header>

    <main>
      <article>
        <h1>메인 제목</h1>
        <section>
          <h2>섹션 제목</h2>
          <p>본문 내용</p>
        </section>
      </article>

      <aside>
        <h3>사이드바</h3>
      </aside>
    </main>

    <footer>
      <p>저작권 정보</p>
    </footer>

    <!-- defer로 DOM 파싱 완료 후 실행 -->
    <script src="app.js" defer></script>
  </body>
</html>
```

`header`, `nav`, `main`, `article`, `section`, `aside`, `footer` 같은 시맨틱 태그는 접근성 도구와 검색 엔진이 페이지 구조를 이해하게 도와줍니다.

## CSS Cascade와 Specificity

```css
/* 우선순위 (낮음 → 높음) */
/* 1. 태그 선택자 */
p { color: gray; }

/* 2. 클래스 선택자 */
.highlight { color: blue; }

/* 3. ID 선택자 */
#special { color: red; }

/* 4. 인라인 스타일 (HTML style 속성) */
/* <p style="color: green"> → 더 높음 */

/* 5. !important (마지막 수단, 남용 금지) */
.override { color: purple !important; }
```

같은 요소에 여러 규칙이 적용되면 Specificity(구체성) 점수가 높은 규칙이 이깁니다. ID > class > tag 순서입니다.

## JavaScript DOM 연결

```js
// 선택
const title = document.querySelector(".page-title");
const allItems = document.querySelectorAll("li");
const byId = document.getElementById("main");

// 읽기
console.log(title.textContent);
console.log(title.className);

// 쓰기
title.textContent = "새 제목";
title.classList.add("active");
title.classList.toggle("hidden");

// 생성 및 추가
const newItem = document.createElement("li");
newItem.textContent = "새 항목";
document.querySelector("ul").appendChild(newItem);

// 이벤트
title.addEventListener("click", (event) => {
  console.log("클릭됨:", event.target.textContent);
});
```

`class`와 `id`는 HTML이 CSS와 JavaScript에 제공하는 연결 고리입니다. CSS는 선택자로 스타일을 붙이고, JavaScript는 API로 상태를 바꿉니다.

## defer와 async 비교

```html
<!-- 기본: HTML 파싱 중에 멈추고 즉시 실행 -->
<script src="app.js"></script>

<!-- defer: HTML 파싱 완료 후 실행, 순서 보장 -->
<script src="app.js" defer></script>

<!-- async: 다운로드 즉시 실행, 순서 보장 안 됨 -->
<script src="analytics.js" async></script>
```

```
기본:    HTML 파싱... [멈춤] JS 다운+실행 → HTML 파싱 재개
defer:   HTML 파싱......... [완료] → JS 실행
async:   HTML 파싱... [JS 다운 완료 즉시 멈추고 JS 실행] → 재개
```

대부분의 경우 `defer`가 안전합니다. DOM이 완성된 뒤 실행되므로 `document.querySelector`가 `null`을 반환하는 문제를 방지합니다.

## CSS 박스 모델과 레이아웃 기초

모든 HTML 요소는 사각형 박스입니다. 박스 모델을 이해하면 배치 버그의 70%가 해결됩니다.

```
┌─────────────────────────────────┐
│            margin               │
│   ┌─────────────────────────┐   │
│   │         border          │   │
│   │   ┌─────────────────┐   │   │
│   │   │     padding     │   │   │
│   │   │  ┌───────────┐  │   │   │
│   │   │  │  content  │  │   │   │
│   │   │  └───────────┘  │   │   │
│   │   └─────────────────┘   │   │
│   └─────────────────────────┘   │
└─────────────────────────────────┘
```

기본적으로 브라우저는 `box-sizing: content-box`를 사용합니다. 이 경우 `width`는 content 영역만 포함하고 padding과 border가 그 위에 추가됩니다. 거의 모든 프로젝트에서 다음 리셋을 사용합니다.

```css
/* 모든 요소에 border-box 적용 */
*, *::before, *::after {
  box-sizing: border-box;
}
```

`border-box`로 설정하면 `width: 300px`이 padding, border를 포함한 300px이 됩니다. 계산이 훨씬 직관적입니다.

### Flexbox: 1차원 레이아웃

행 또는 열 방향으로 아이템을 정렬할 때 사용합니다.

```css
.container {
  display: flex;
  flex-direction: row;       /* 기본값: 가로 방향 */
  justify-content: space-between; /* 주축 정렬 */
  align-items: center;       /* 교차축 정렬 */
  gap: 16px;
}

.item {
  flex: 1;                   /* 남은 공간을 균등 배분 */
}

.item.featured {
  flex: 2;                   /* 2배 넓이 */
}
```

```html
<!-- 네비게이션 바: 로고 왼쪽, 메뉴 오른쪽 -->
<nav style="display:flex; justify-content:space-between; align-items:center; padding:0 16px;">
  <a href="/" class="logo">MyApp</a>
  <ul style="display:flex; gap:24px; list-style:none;">
    <li><a href="/about">소개</a></li>
    <li><a href="/docs">문서</a></li>
    <li><a href="/contact">연락</a></li>
  </ul>
</nav>
```

### CSS Grid: 2차원 레이아웃

행과 열을 동시에 제어할 때 사용합니다.

```css
.grid-layout {
  display: grid;
  grid-template-columns: 200px 1fr 1fr; /* 고정 사이드바 + 유동 2열 */
  grid-template-rows: auto 1fr auto;    /* 헤더, 메인, 푸터 */
  grid-template-areas:
    "header header header"
    "sidebar main  aside"
    "footer footer footer";
  min-height: 100vh;
  gap: 16px;
}

header  { grid-area: header; }
.sidebar { grid-area: sidebar; }
main    { grid-area: main; }
aside   { grid-area: aside; }
footer  { grid-area: footer; }
```

### CSS 사용자 정의 속성 (변수)

반복되는 값을 한 곳에서 관리합니다.

```css
:root {
  --color-primary: #2563eb;
  --color-text: #1f2937;
  --color-bg: #f9fafb;
  --spacing-unit: 8px;
  --border-radius: 6px;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
  padding: calc(var(--spacing-unit) * 1.5) calc(var(--spacing-unit) * 3);
  border-radius: var(--border-radius);
  border: none;
  cursor: pointer;
}

/* 다크 모드: 변수만 바꾸면 모든 컴포넌트에 적용 */
@media (prefers-color-scheme: dark) {
  :root {
    --color-primary: #3b82f6;
    --color-text: #f3f4f6;
    --color-bg: #111827;
  }
}
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|------|------|-------------|
| `style="..."` 남용 | CSS 파일 효과 무력화, 캐시 불가 | 외부 CSS 파일에 클래스로 정의 |
| `<script>`를 `<head>` 안에 넣기 | DOM 준비 전 실행으로 `null` 오류 | `defer` 사용 또는 `</body>` 직전 |
| 같은 `id`를 여러 요소에 사용 | `getElementById`가 첫 번째만 반환 | `id`는 문서 내 유일, 여러 개는 `class` 사용 |
| `!important` 남용 | 규칙 우선순위 추적 불가 | Specificity 계층 이해 후 선택자 조정 |
| 스타일 변경을 JS로만 처리 | 애니메이션 성능 저하, 유지보수 어려움 | CSS 클래스 추가/제거로 처리 |
| 시맨틱 태그 대신 `<div>` 남용 | 접근성 저하, SEO 불리 | `header`, `main`, `article` 등 사용 |

## 직접 검증해 볼 포인트

```bash
# 간단한 정적 서버 실행
python3 -m http.server 8000
# http://localhost:8000 에서 확인
```

```
F12 → Elements 탭
- HTML 구조가 DOM 트리로 표시됨
- 오른쪽 Styles 패널에서 적용된 CSS 규칙 확인 가능
- 요소 클릭 후 실시간으로 CSS 수정 가능 (임시)
```

**기대 결과:** HTML 없이 CSS나 JavaScript만으로는 페이지 골격이 생기지 않고, 각 파일을 따로 수정할 때 영향 범위도 분리됩니다.

**실패 모드:** 모든 스타일과 동작을 HTML 안에 섞어 넣으면 작은 변경에도 파일 전체를 다시 읽어야 하고, 캐시 이점도 크게 줄어듭니다.

## 운영에서는 이렇게 보입니다

React나 Vue 같은 프레임워크를 써도 브라우저가 받는 것은 HTML, CSS, JavaScript입니다. 프레임워크는 이 세 언어를 더 잘 관리하게 도와주는 도구일 뿐입니다. 이 원칙을 알고 있으면 새로운 도구를 배울 때도 중심을 잃지 않습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 먼저 의미 있는 HTML을 씁니다. 가능하면 semantic tag를 사용합니다.
- CSS는 재사용 가능한 클래스 중심으로 설계합니다.
- JavaScript는 동작에만 집중하게 둡니다.
- 접근성은 나중이 아니라 처음부터 함께 봅니다.
- 변경이 한 곳에서 끝나도록 구조를 짭니다.

## 운영 체크리스트

- [ ] 세 언어의 책임을 각각 한 문장으로 설명할 수 있습니다.
- [ ] inline CSS와 external CSS의 차이를 알고 있습니다.
- [ ] DevTools에서 DOM 트리와 CSS 규칙을 읽을 수 있습니다.
- [ ] `defer`와 `async`의 차이를 알고 있습니다.
- [ ] 뒤섞인 코드를 분리된 파일 구조로 옮길 수 있습니다.

## 연습 문제

1. inline style이 많은 HTML 파일 하나를 골라 CSS 파일로 분리해 보세요.
2. 버튼 다섯 개를 만들고 CSS 클래스를 토글해 배경색이 바뀌게 해 보세요.
3. 자주 가는 사이트의 HTML에서 semantic tag 다섯 개를 찾아보세요.

## 정리와 다음 글

HTML, CSS, JavaScript는 관심사를 분리하는 가장 기본적인 훈련입니다. 구조, 스타일, 동작을 나눠 생각할 수 있어야 브라우저가 화면을 어떻게 그리는지도 자연스럽게 이해됩니다. 다음 글에서는 브라우저가 HTML을 DOM 트리로 바꾸는 과정을 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Web Development 101 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- **Web Development 101 (2/10): HTML, CSS, JavaScript (현재 글)**
- [Web Development 101 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [Web Development 101 (4/10): HTTP와 API](./04-http-and-api.md)
- [Web Development 101 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- [Web Development 101 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- [Web Development 101 (7/10): 데이터베이스 연결](./07-connecting-to-database.md)
- [Web Development 101 (8/10): 배포](./08-deployment.md)
- [Web Development 101 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- [작은 웹앱 만들기](./10-building-a-small-web-app.md)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [HTML basics (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Your_first_website/Creating_the_content)
- [CSS basics (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Your_first_website/Styling_the_content)
- [JavaScript basics (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Your_first_website/Adding_interactivity)

### 개념 보강
- [Semantic HTML (MDN)](https://developer.mozilla.org/en-US/docs/Glossary/Semantics)
- [script 요소와 defer/async (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/script)

- [web-development-101 예제 코드 저장소 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/web-development-101/ko)

Tags: Computer Science, WebDevelopment, HTML, CSS, JavaScript, Frontend
