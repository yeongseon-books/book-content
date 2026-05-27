---
series: frontend-development-101
episode: 4
title: "Frontend Development 101 (4/10): 컴포넌트와 상태"
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
  - React
  - Components
  - State
  - JavaScript
seo_description: 컴포넌트, props, state로 현대 프론트엔드의 핵심 구조를 설명합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (4/10): 컴포넌트와 상태

이 글은 Frontend Development 101 시리즈의 네 번째 글입니다. 여기서는 이 복잡도를 줄이는 가장 기본적인 모델인 컴포넌트와 상태를 설명합니다. 화면은 작은 함수 단위로 나누고, 각 함수는 자신에게 들어오는 값과 자신이 들고 있는 상태만 책임져야 구조가 오래 버팁니다.

화면이 작을 때는 JavaScript 몇 줄과 DOM 조작만으로도 충분합니다. 하지만 화면이 커지고 기능이 늘어나면 금방 한 파일에 모든 로직이 몰립니다. 그 순간부터는 코드를 실행하는 것보다 읽는 일이 더 힘들어집니다.

![Frontend Development 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/04/04-01-diagram.ko.png)
*Frontend Development 101 4장 흐름 개요*

> 컴포넌트는 'UI 조각'이 아니라 '상태(props/state)를 받아 화면을 돌려주는 함수'입니다 — 이 함수형 모델이 잡히면 prop drilling·lifting state up·전역 상태 라이브러리 선택이 모두 같은 문제(상태를 어디에 둘 것인가)의 답으로 정리됩니다.

## 먼저 던지는 질문

- 컴포넌트 사고방식은 단순히 React 문법을 넘어서 무엇을 바꿔 줄까요?
- props와 state는 어떤 기준으로 구분해야 할까요?
- 단방향 데이터 흐름은 왜 대부분의 현대 프론트엔드 프레임워크의 기본 전제일까요?

## 왜 중요한가

컴포넌트 사고방식은 React에만 한정되지 않습니다. Vue, Svelte, Angular는 물론이고 순수 JavaScript로도 같은 패턴을 적용할 수 있습니다. 한 번 이 감각을 익히면 프레임워크가 달라져도 코드가 훨씬 빠르게 읽힙니다.

또 중요한 점은 컴포넌트 분리가 재사용성만을 위한 작업이 아니라는 사실입니다. 잘 쪼개진 컴포넌트는 무엇보다도 읽기 쉽습니다. 시니어 엔지니어는 “나중에 어디서 재사용할 수 있을까”보다 “지금 이 화면이 읽히는가”를 먼저 봅니다.

## 개념 한눈에 보기

상태는 위에서 아래로 흐르고, 이벤트는 아래에서 위로 올라옵니다. 이 단순한 규칙 하나만 제대로 잡아도 복잡한 화면의 절반은 정리됩니다.

## 핵심 용어

| 용어 | 뜻 | 실무에서 왜 중요한가 |
|---|---|---|
| 컴포넌트 | 화면의 한 조각을 그리는 함수입니다. | 역할별 경계를 만들기 시작하는 가장 기본 단위입니다. |
| Props | 부모가 자식에게 내려주는 읽기 전용 값입니다. | 데이터가 어느 방향으로 흐르는지 추적하기 쉽게 만듭니다. |
| State | 컴포넌트가 내부에 유지하는 변경 가능한 값입니다. | 어떤 값이 화면을 다시 그리게 만드는지 명확히 보여 줍니다. |
| 단방향 데이터 흐름 | 데이터가 위에서 아래로만 흐르는 구조입니다. | 화면이 커져도 사이드 이펙트를 추적하기 쉬운 이유가 됩니다. |
| 상태 끌어올리기 | 여러 자식이 공유해야 할 상태를 부모로 옮기는 방식입니다. | 서로 다른 컴포넌트가 같은 값을 볼 때 어디에 상태를 둬야 할지 판단하게 해 줍니다. |

## 거대한 스크립트에서 컴포넌트 경계로

컴포넌트는 재사용을 위해서만 존재하는 것이 아닙니다. 더 자주 필요한 이유는 화면이 커졌을 때 읽기와 변경의 단위를 줄여 주기 때문입니다. 아래 비교는 화면 구조를 어떻게 쪼개야 수정 비용이 내려가는지 보여 줍니다.

| 방식 | 구조 특징 | 실무 영향 |
|---|---|---|
| 한 파일에 모든 DOM 조작이 모임 | 책임 경계가 흐리고 수정 범위가 넓습니다. | 작은 변경도 파일 전체를 다시 읽어야 해서 속도가 떨어집니다. |
| 컴포넌트 단위로 역할 분리 | 입력, 출력, 상태가 작은 단위로 나뉩니다. | 테스트, 리팩터링, 팀 협업이 모두 쉬워집니다. |

**Before (모든 것이 한 파일에)**

```html
<script>
  // 1000 lines of DOM manipulation
</script>
```

**After (컴포넌트로 분리)**

```jsx
function App()    { ... }
function Header() { ... }
function List()   { ... }
function Item()   { ... }
```

핵심은 파일 수를 늘리는 것이 아니라 책임을 줄이는 것입니다. 그렇게 해야 props와 state를 어디에 둘지 판단하는 기준도 함께 선명해집니다.

## 실습: 리액트 카운터를 5단계로 만들기

### 1단계 — Project

```bash
npm create vite@latest counter -- --template react
cd counter && npm install && npm run dev
```

### 2단계 — Define a component

```jsx
function Counter({ initial = 0 }) {
  return <button>{initial}</button>;
}
```

### 3단계 — Add state

```jsx
import { useState } from "react";

function Counter({ initial = 0 }) {
  const [count, setCount] = useState(initial);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

### 4단계 — Use it from the parent

```jsx
function App() {
  return (
    <>
      <Counter initial={0} />
      <Counter initial={10} />
    </>
  );
}
```

### 5단계 — Lift state up

```jsx
function App() {
  const [total, setTotal] = useState(0);
  return (
    <>
      <p>Total: {total}</p>
      <button onClick={() => setTotal(total + 1)}>+1</button>
    </>
  );
}
```

이 예제는 작지만 중요한 차이를 보여 줍니다. `props`는 외부에서 들어오고, `state`는 내부에서 바뀌며, 같은 컴포넌트도 여러 인스턴스로 독립 동작합니다. 그리고 여러 조각이 같은 상태를 봐야 할 때는 상태를 공통 부모로 끌어올립니다.

## 검증 포인트

- 카운터 두 개를 렌더링했을 때 각 버튼이 서로 독립적으로 증가하는지 확인합니다.
- 상태 끌어올리기 버전에서는 공통 부모가 가진 값이 화면 여러 곳에서 동시에 갱신되는지 확인합니다.

## 문제가 생기면 먼저 볼 것

- 상태가 안 바뀌면 `useState` import와 `setCount` 호출 위치를 먼저 확인합니다.
- 부모-자식 동기화가 꼬이면 상태를 어디에 두었는지, props 이름이 일치하는지 다시 봅니다.

## 실무 점검 루프

컴포넌트 문제는 대부분 소유권 문제인지, 렌더링 문제인지 구분하는 순간 절반이 풀립니다.

1. **값의 소유권을 확인합니다.** 상태를 더 추가하기 전에 그 값이 어느 컴포넌트에 살아야 하는지 먼저 정합니다.
2. **렌더 트리거를 확인합니다.** 상태 setter가 실제로 실행되고, 바뀐 값이 자식 트리까지 내려가는지 봅니다.
3. **공유 상태를 확인합니다.** 두 위젯이 엇갈리면 부모에 이미 진짜 source of truth가 있어야 하는지 다시 봅니다.

```jsx
useEffect(() => {
  console.log("count changed:", count);
}, [count]);
```

기대 결과는 세 가지 질문에 답할 수 있는 상태입니다. 값이 어디에 살고, 누가 바꿀 수 있으며, 변경 후 어떤 렌더가 일어나야 하는가. 이 세 가지가 명확해지면 컴포넌트 설계가 훨씬 덜 흔들립니다.

## 이 코드에서 주목할 점

- `props`는 입력이고 `state`는 내부 기억입니다.
- 자식이 부모 상태를 바꾸려면 함수를 props로 전달받는 구조를 사용합니다.
- 같은 컴포넌트가 여러 인스턴스로 독립 동작할 수 있습니다.

## 자주 하는 실수 5가지

1. **컴포넌트 안에서 props를 직접 바꿉니다.** props는 읽기 전용이어야 합니다.
2. **모든 상태를 최상단에 몰아둡니다.** 불필요한 전역화는 성능과 가독성을 함께 해칩니다.
3. **컴포넌트가 1000줄 가까이 커지는데도 쪼개지 않습니다.** 보통 200줄 전후부터는 분리 신호를 의심해 볼 만합니다.
4. **매 렌더마다 이벤트 콜백을 무분별하게 새로 만듭니다.** 자식 리렌더링이 불필요하게 늘어날 수 있습니다.
5. **원본 상태와 파생 값을 함께 저장합니다.** 진실의 출처가 둘이 되어 버그가 생깁니다.

## 실무에서는 이렇게 보입니다

대부분의 회사는 디자인 시스템을 컴포넌트 라이브러리 형태로 운영합니다. 새로운 화면은 Button, Input, Card 같은 기본 컴포넌트를 조합해 만들어집니다. 그래서 실무에서 중요한 역량은 무엇을 만들 것인가 못지않게 무엇을 새로 만들지 않을 것인가를 판단하는 일입니다.

결국 좋은 컴포넌트 구조는 재사용보다 읽기와 변경 비용을 먼저 줄입니다. 화면이 커질수록 이 차이는 더 크게 드러납니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 컴포넌트는 작아야 하지만, 의미 있는 단위일 때만 쪼갭니다.
- 상태는 가장 가까운 공통 부모에 둡니다.
- 겉모습이 비슷하다고 바로 합치지 않습니다.
- 순환하는 데이터 흐름은 설계가 잘못됐다는 신호로 봅니다.
- 재사용성보다 가독성을 먼저 지킵니다.

## 체크리스트

- [ ] 컴포넌트를 함수로 정의할 수 있습니다.
- [ ] props와 state를 구분할 수 있습니다.
- [ ] 자식에서 부모로 이벤트를 올릴 수 있습니다.
- [ ] 상태를 적절한 위치에 둘 수 있습니다.
- [ ] 단방향 데이터 흐름을 그림으로 설명할 수 있습니다.

## 연습 문제

1. `<TodoItem>`, `<TodoList>`, `<App>`으로 나눈 todo 앱을 만들어 보세요.
2. 두 카운터가 같은 총합을 공유하도록 상태 끌어올리기를 적용해 보세요.
3. props만 받는 순수 프레젠테이션 컴포넌트를 만들고 단위 테스트를 작성해 보세요.

## 정리 및 다음 단계

컴포넌트와 상태는 화면을 조합 가능한 구조로 바꿔 줍니다. 이 관점이 잡히면 여러 화면을 연결하는 문제도 훨씬 자연스럽게 이해됩니다.

다음 글에서는 URL과 라우터를 사용해 여러 페이지를 연결하는 방법을 봅니다.

## 처음 질문으로 돌아가기

- **컴포넌트 사고방식은 단순히 React 문법을 넘어서 무엇을 바꿔 줄까요?**
  - 이 글에서 컴포넌트는 화면을 그리는 작은 함수 단위이며, `App`, `Header`, `List`, `Item`처럼 역할 경계를 분명하게 만듭니다. 그래서 한 파일에 DOM 조작을 몰아넣던 방식보다 읽기와 수정이 쉬워지고, 같은 사고방식을 Vue나 Svelte 같은 다른 프레임워크에도 그대로 옮길 수 있습니다.
- **props와 state는 어떤 기준으로 구분해야 할까요?**
  - `initial`처럼 부모가 내려주는 값은 props이고, `useState(initial)`로 컴포넌트 내부에서 기억하며 바뀌는 `count`는 state입니다. 본문 예제에서 같은 `Counter`를 두 번 렌더링해도 각 버튼이 독립적으로 증가하는 이유는 입력인 props와 내부 기억인 state가 분리되어 있기 때문입니다.
- **단방향 데이터 흐름은 왜 대부분의 현대 프론트엔드 프레임워크의 기본 전제일까요?**
  - 데이터가 부모에서 자식으로 내려가고, 자식은 이벤트나 콜백으로 변경 요청만 올리는 구조여야 어디서 값이 바뀌는지 추적하기 쉽습니다. `total`을 공통 부모로 끌어올리는 예제도 이 규칙을 따르기 때문에 여러 화면 조각이 같은 상태를 보더라도 흐름이 순환하지 않고 예측 가능하게 유지됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML과 CSS 기본](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript 기본](./03-javascript-basics.md)
- **컴포넌트와 상태 (현재 글)**
- 라우팅과 페이지 (예정)
- API 호출과 비동기 (예정)
- 폼과 유효성 검사 (예정)
- 스타일링과 디자인 시스템 (예정)
- 빌드 도구와 번들링 (예정)
- 작은 프론트엔드 앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [React: Thinking in React](https://react.dev/learn/thinking-in-react)
- [React: Sharing state between components](https://react.dev/learn/sharing-state-between-components)
- [Vue: Component basics](https://vuejs.org/guide/essentials/component-basics.html)

### 확인용 자료
- [Svelte tutorial](https://svelte.dev/tutorial)
- [React: State as a snapshot](https://react.dev/learn/state-as-a-snapshot)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/frontend-development-101/ko)

Tags: Frontend, React, Components, State, JavaScript
