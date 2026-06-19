---
series: frontend-development-101
episode: 4
title: "Frontend Development 101 (4/10): 컴포넌트와 상태"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/216"
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
  - React
  - Components
  - State
  - JavaScript
seo_description: 컴포넌트, props, state로 현대 프론트엔드의 핵심 구조를 설명합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (4/10): 컴포넌트와 상태

상태는 위에서 아래로 흐르고, 이벤트는 아래에서 위로 올라옵니다. 이 단순한 규칙 하나만 제대로 잡아도 복잡한 화면의 절반은 정리됩니다.

이 글은 Frontend Development 101 시리즈의 네 번째 글입니다. 여기서는 이 복잡도를 줄이는 가장 기본적인 모델인 컴포넌트와 상태를 설명합니다. 화면은 작은 함수 단위로 나누고, 각 함수는 자신에게 들어오는 값과 자신이 들고 있는 상태만 책임져야 구조가 오래 버팁니다.

![Frontend Development 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/04/04-01-diagram.ko.png)
*Frontend Development 101 4장 흐름 개요*

> 컴포넌트는 'UI 조각'이 아니라 '상태(props/state)를 받아 화면을 돌려주는 함수'입니다 — 이 함수형 모델이 잡히면 prop drilling·lifting state up·전역 상태 라이브러리 선택이 모두 같은 문제(상태를 어디에 둘 것인가)의 답으로 정리됩니다.

## 이 글에서 다룰 문제

- 컴포넌트 사고방식은 단순히 React 문법을 넘어서 무엇을 바꿔 줄까요?
- props와 state는 어떤 기준으로 구분해야 할까요?
- 단방향 데이터 흐름은 왜 대부분의 현대 프론트엔드 프레임워크의 기본 전제일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 개념 한눈에 보기

| 용어 | 뜻 | 실무에서 왜 중요한가 |
|---|---|---|
| 컴포넌트 | 화면의 한 조각을 그리는 함수입니다. | 역할별 경계를 만들기 시작하는 가장 기본 단위입니다. |
| Props | 부모가 자식에게 내려주는 읽기 전용 값입니다. | 데이터가 어느 방향으로 흐르는지 추적하기 쉽게 만듭니다. |
| State | 컴포넌트가 내부에 유지하는 변경 가능한 값입니다. | 어떤 값이 화면을 다시 그리게 만드는지 명확히 보여 줍니다. |
| 단방향 데이터 흐름 | 데이터가 위에서 아래로만 흐르는 구조입니다. | 화면이 커져도 사이드 이펙트를 추적하기 쉬운 이유가 됩니다. |
| 상태 끌어올리기 | 여러 자식이 공유해야 할 상태를 부모로 옮기는 방식입니다. | 서로 다른 컴포넌트가 같은 값을 볼 때 어디에 상태를 둬야 할지 판단하게 해 줍니다. |

## 컴포넌트를 나누는 기준

컴포넌트 분리는 재사용보다 책임의 명확화가 먼저입니다.

**Before (모든 것이 한 파일에)**

```html
<script>
  // 1000줄의 DOM 조작이 한 파일에
  // 어디를 고쳐야 할지 파일 전체를 읽어야 함
</script>
```

**After (컴포넌트로 분리)**

```jsx
// 각 컴포넌트는 한 가지 책임만
function App()      { return <><Header /><NoteList /></>; }
function Header()   { return <header><h1>노트 앱</h1></header>; }
function NoteList() { return <ul>{notes.map(n => <NoteItem key={n.id} note={n} />)}</ul>; }
function NoteItem({ note }) { return <li>{note.title}</li>; }
```

컴포넌트 분리를 판단하는 기준:
- 200줄이 넘기 시작했다면 분리 신호
- 같은 UI 조각이 두 군데 이상 나타난다면 분리 검토
- 역할이 명확히 다른 두 가지 일을 한 컴포넌트가 동시에 한다면 분리

## 실습: 리액트 카운터를 5단계로 만들기

### 1단계 — Project

```bash
npm create vite@latest counter -- --template react
cd counter && npm install && npm run dev
```

### 2단계 — Define a component

```jsx
// src/components/Counter.jsx
// props만 받는 순수 표현 컴포넌트 (프레젠테이션 컴포넌트)
function Counter({ count, onIncrement, onDecrement }) {
  return (
    <div className="counter">
      <button onClick={onDecrement} aria-label="감소">-</button>
      <span className="counter__value">{count}</span>
      <button onClick={onIncrement} aria-label="증가">+</button>
    </div>
  );
}
```

### 3단계 — Add state

```jsx
// src/components/CounterContainer.jsx
// 상태를 가진 컨테이너 컴포넌트
import { useState } from "react";
import Counter from "./Counter";

function CounterContainer({ initial = 0, label = "카운터" }) {
  const [count, setCount] = useState(initial);

  return (
    <div>
      <p>{label}</p>
      <Counter
        count={count}
        onIncrement={() => setCount(c => c + 1)}
        onDecrement={() => setCount(c => c - 1)}
      />
    </div>
  );
}
```

### 4단계 — Use it from the parent

```jsx
// src/App.jsx
function App() {
  return (
    <main>
      <h1>카운터 앱</h1>
      {/* 같은 컴포넌트, 독립적인 상태 */}
      <CounterContainer initial={0}  label="첫 번째" />
      <CounterContainer initial={10} label="두 번째" />
    </main>
  );
}
```

### 5단계 — Lift state up (상태 끌어올리기)

```jsx
// 두 카운터가 같은 합계를 보여줘야 할 때
// 상태를 공통 부모로 올립니다.
function App() {
  const [countA, setCountA] = useState(0);
  const [countB, setCountB] = useState(0);
  const total = countA + countB;

  return (
    <main>
      <h1>합계: {total}</h1>
      <Counter
        count={countA}
        onIncrement={() => setCountA(c => c + 1)}
        onDecrement={() => setCountA(c => c - 1)}
      />
      <Counter
        count={countB}
        onIncrement={() => setCountB(c => c + 1)}
        onDecrement={() => setCountB(c => c - 1)}
      />
    </main>
  );
}
```

## useEffect 사용 패턴

```jsx
import { useState, useEffect } from "react";

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // userId가 바뀔 때마다 실행
    setLoading(true);
    fetch(`/api/users/${userId}`)
      .then(r => r.json())
      .then(data => {
        setUser(data);
        setLoading(false);
      });

    // 클린업: 컴포넌트가 사라지거나 userId가 바뀌기 전에 실행
    return () => {
      // 진행 중인 요청 취소 등
    };
  }, [userId]); // 의존성 배열: userId가 바뀔 때만 재실행

  if (loading) return <p>로딩 중...</p>;
  if (!user)   return <p>사용자를 찾을 수 없습니다.</p>;

  return <div>{user.name}</div>;
}
```

## 컴포넌트 패턴: 합성(Composition)

```jsx
// 나쁜 패턴: 모든 변형을 props로 제어
function Card({ title, body, hasFooter, footerText, variant, imageUrl }) {
  // props가 10개 넘으면 API가 복잡해짐
}

// 좋은 패턴: 합성으로 유연하게
function Card({ children }) {
  return <div className="card">{children}</div>;
}

function CardHeader({ children }) {
  return <div className="card__header">{children}</div>;
}

function CardBody({ children }) {
  return <div className="card__body">{children}</div>;
}

// 사용할 때 필요한 조각만 조합
function ProductCard({ product }) {
  return (
    <Card>
      <CardHeader>
        <img src={product.image} alt={product.name} />
      </CardHeader>
      <CardBody>
        <h2>{product.name}</h2>
        <p>{product.price}원</p>
      </CardBody>
    </Card>
  );
}
```

## 디버깅 시나리오

### 시나리오 1: 상태가 바뀌어도 화면이 안 바뀔 때

```jsx
// 잘못된 방법: 객체/배열 직접 변경 (React가 감지 못함)
const [items, setItems] = useState([]);
items.push(newItem);  // React가 변경을 감지하지 못함
setItems(items);       // 같은 참조이므로 리렌더링 안 됨

// 올바른 방법: 새 배열/객체 생성
setItems([...items, newItem]);         // 배열 추가
setItems(items.filter(i => i.id !== id)); // 배열 삭제
setItems(items.map(i => i.id === id ? {...i, done: true} : i)); // 배열 수정
```

### 시나리오 2: 무한 렌더링이 발생할 때

```jsx
// 잘못된 패턴: 의존성 배열 없이 setState 호출
useEffect(() => {
  setData(fetch(url)); // 리렌더링 → useEffect 재실행 → 무한 루프
}); // 의존성 배열 없음!

// 올바른 패턴: 의존성 배열 명시
useEffect(() => {
  fetchData(url).then(setData);
}, [url]); // url이 바뀔 때만 실행
```

### 시나리오 3: 상태 변경 후 값 확인

```jsx
// setState는 비동기 → 바로 다음 줄에서 읽으면 이전 값
setCount(count + 1);
console.log(count); // 여전히 이전 값!

// 해결: useEffect로 변경 후 실행
useEffect(() => {
  console.log("count changed:", count);
}, [count]);
```

## 실무 점검 루프

1. **값의 소유권을 확인합니다.** 상태를 더 추가하기 전에 그 값이 어느 컴포넌트에 살아야 하는지 먼저 정합니다.
2. **렌더 트리거를 확인합니다.** 상태 setter가 실제로 실행되고, 바뀐 값이 자식 트리까지 내려가는지 봅니다.
3. **공유 상태를 확인합니다.** 두 위젯이 엇갈리면 부모에 이미 진짜 source of truth가 있어야 하는지 다시 봅니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|---|---|---|
| `props`를 컴포넌트 안에서 직접 변경 | 단방향 흐름이 깨져 예측 불가 | props는 읽기 전용, 변경은 콜백 함수를 통해 부모에서 |
| 모든 상태를 최상단에 집중 | 관계없는 컴포넌트도 리렌더링 | 상태는 사용하는 컴포넌트와 가장 가까운 공통 조상에 |
| 컴포넌트 크기가 1000줄 이상 | 어떤 props가 어디에 영향을 주는지 파악 불가 | 200줄 전후에서 분리 검토 |
| 배열/객체를 직접 변경 후 setState | 화면이 업데이트 안 됨 | 항상 새 참조를 만들어서 setState |
| 원본 상태와 파생 값을 함께 저장 | 동기화 문제로 버그 발생 | 파생 값은 렌더 중에 계산 |
| useEffect 의존성 배열 누락 | 무한 루프 또는 오래된 값 사용 | 린터 경고를 무시하지 않습니다 |

## 실무에서는 이렇게 보입니다

대부분의 회사는 디자인 시스템을 컴포넌트 라이브러리 형태로 운영합니다. 새로운 화면은 Button, Input, Card 같은 기본 컴포넌트를 조합해 만들어집니다.

```jsx
// 실무 팀의 컴포넌트 계층 예시
// atoms: 가장 작은 단위
function Button({ variant, children, onClick }) { ... }
function Input({ label, error, ...props }) { ... }

// molecules: atom 조합
function SearchBar({ onSearch }) {
  const [query, setQuery] = useState("");
  return (
    <div className="search-bar">
      <Input value={query} onChange={e => setQuery(e.target.value)} />
      <Button onClick={() => onSearch(query)}>검색</Button>
    </div>
  );
}

// organisms: 비즈니스 로직 포함
function ProductSearch() {
  const [results, setResults] = useState([]);
  const handleSearch = async (q) => {
    const data = await searchProducts(q);
    setResults(data);
  };
  return (
    <>
      <SearchBar onSearch={handleSearch} />
      <ProductGrid items={results} />
    </>
  );
}
```

## 시니어 엔지니어는 이렇게 생각합니다

- 컴포넌트는 작아야 하지만, 의미 있는 단위일 때만 쪼갭니다.
- 상태는 가장 가까운 공통 부모에 둡니다.
- 겉모습이 비슷하다고 바로 합치지 않습니다.
- 순환하는 데이터 흐름은 설계가 잘못됐다는 신호로 봅니다.
- 재사용성보다 가독성을 먼저 지킵니다.

## 운영 체크리스트

- [ ] 컴포넌트를 함수로 정의할 수 있습니다.
- [ ] props와 state를 구분할 수 있습니다.
- [ ] 자식에서 부모로 이벤트를 올릴 수 있습니다.
- [ ] 상태를 적절한 위치에 둘 수 있습니다.
- [ ] 단방향 데이터 흐름을 그림으로 설명할 수 있습니다.
- [ ] `useEffect`의 의존성 배열을 올바르게 사용할 수 있습니다.

## 연습 문제

1. `<TodoItem>`, `<TodoList>`, `<App>`으로 나눈 todo 앱을 만들어 보세요.
2. 두 카운터가 같은 총합을 공유하도록 상태 끌어올리기를 적용해 보세요.
3. props만 받는 순수 프레젠테이션 컴포넌트를 만들고 다양한 props로 테스트해 보세요.
4. 합성 패턴으로 Card 컴포넌트를 만들어 ProductCard와 UserCard 두 가지 용도로 사용해 보세요.

## 정리 및 다음 단계

컴포넌트와 상태는 화면을 조합 가능한 구조로 바꿔 줍니다. 이 관점이 잡히면 여러 화면을 연결하는 문제도 훨씬 자연스럽게 이해됩니다.

다음 글에서는 URL과 라우터를 사용해 여러 페이지를 연결하는 방법을 봅니다.

## 처음 질문으로 돌아가기

- **컴포넌트 사고방식은 단순히 React 문법을 넘어서 무엇을 바꿔 줄까요?**
  - 화면을 "상태를 받아 그림을 돌려주는 함수의 조합"으로 보는 시각을 줍니다. 이 모델이 있으면 Vue, Svelte, 심지어 순수 JS로도 같은 방식으로 생각할 수 있습니다.
- **props와 state는 어떤 기준으로 구분해야 할까요?**
  - 외부에서 받은 값은 props, 자신이 관리하고 바꿀 수 있는 값은 state입니다. "이 값이 어디서 오는가"가 구분 기준입니다.
- **단방향 데이터 흐름은 왜 대부분의 현대 프론트엔드 프레임워크의 기본 전제일까요?**
  - 데이터가 흐르는 방향이 하나면 어떤 변경이 어떤 화면에 영향을 주는지 추적하기 쉽기 때문입니다. 양방향 바인딩은 편리하지만 화면이 커질수록 디버깅이 어려워집니다.

<!-- toc:begin -->
## 시리즈 목차

- [Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML과 CSS 기본](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript 기본](./03-javascript-basics.md)
- **Frontend Development 101 (4/10): 컴포넌트와 상태 (현재 글)**
- [Frontend Development 101 (5/10): 라우팅과 페이지](./05-routing-and-pages.md)
- [Frontend Development 101 (6/10): API 호출과 비동기](./06-api-calls-and-async.md)
- [Frontend Development 101 (7/10): 폼과 유효성 검사](./07-forms-and-validation.md)
- [Frontend Development 101 (8/10): 스타일링과 디자인 시스템](./08-styling-and-design-system.md)
- [Frontend Development 101 (9/10): 빌드 도구와 번들링](./09-build-tools-and-bundling.md)
- [작은 프론트엔드 앱 만들기](./10-building-a-small-frontend-app.md)

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
