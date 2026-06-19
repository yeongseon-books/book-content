---
series: frontend-development-101
episode: 3
title: "Frontend Development 101 (3/10): JavaScript 기본"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/215"
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
  - JavaScript
  - DOM
  - Web
  - Beginner
seo_description: 변수, 함수, DOM, 이벤트 중심으로 JavaScript 핵심을 정리합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (3/10): JavaScript 기본

프론트엔드의 JavaScript는 대개 이 흐름으로 전개됩니다. 값을 만들고, 함수를 정의하고, 컬렉션을 변환하고, DOM에 반영하고, 이벤트로 다시 상태를 바꿉니다.

이 글은 Frontend Development 101 시리즈의 세 번째 글입니다. 여기서는 JavaScript를 완전한 언어 사전처럼 다루지 않고, 프론트엔드에서 가장 자주 쓰는 변수, 함수, 컬렉션 처리, DOM, 이벤트 다섯 축으로 정리합니다.

![Frontend Development 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/03/03-01-diagram.ko.png)
*Frontend Development 101 3장 흐름 개요*

> JavaScript의 진짜 모델은 '이벤트 루프 위에서 도는 단일 스레드 + 비동기 큐'입니다 — `setTimeout(fn, 0)`이 즉시 실행되지 않는 이유, `await`이 실제로 기다리는 것이 무엇인지가 모두 이 한 그림 위에서만 설명됩니다.

## 이 글에서 다룰 문제

- `let`과 `const`를 어떻게 구분해 쓰는 편이 좋을까요?
- 함수와 화살표 함수는 어떤 기준으로 읽고 작성하면 될까요?
- `map`, `filter`, `reduce`는 왜 for문보다 자주 권장될까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 개념 한눈에 보기

| 용어 | 뜻 | 실무에서 왜 중요한가 |
|---|---|---|
| `const` | 재할당할 수 없는 변수입니다. | 값이 어디서 바뀌는지 추적 범위를 줄여 실수를 줄여 줍니다. |
| 화살표 함수 | `() => {}` 형태의 간결한 함수 문법입니다. | 콜백과 이벤트 핸들러를 짧고 읽기 쉽게 유지하는 데 자주 쓰입니다. |
| 클로저 | 함수가 자신이 만들어질 당시의 환경을 기억하는 성질입니다. | 이벤트 핸들러와 팩토리 함수가 어떤 값을 붙잡고 있는지 이해하게 해 줍니다. |
| `map/filter/reduce` | 반복문 대신 컬렉션을 변환할 때 쓰는 표준 도구입니다. | 상태를 가공한 뒤 렌더링하는 코드의 의도를 더 직접적으로 드러냅니다. |
| 이벤트 위임 | 자식마다 리스너를 붙이지 않고 부모에 한 번만 리스너를 두는 방식입니다. | 리스트가 커져도 리스너 수를 억제하고 DOM 구조 변화를 더 쉽게 수용합니다. |

## 변수 선언: const, let, var

```javascript
// const: 재할당 불가 (객체 내부 변경은 가능)
const PI = 3.14159;
const user = { name: "Alice" };
user.name = "Bob";  // 가능: 객체 내부 변경
// user = {};       // 오류: 재할당 불가

// let: 재할당 가능, 블록 스코프
let count = 0;
count += 1;  // 가능

// var: 함수 스코프, 호이스팅 (사용 자제)
// 루프 안에서 var를 쓰면 의도하지 않은 결과가 생길 수 있음
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0);  // 3, 3, 3 출력됨 (버그)
}
for (let j = 0; j < 3; j++) {
  setTimeout(() => console.log(j), 0);  // 0, 1, 2 출력됨 (의도한 동작)
}
```

## 함수 표현 방식

```javascript
// 1. 함수 선언식: 호이스팅 되므로 선언 전에 사용 가능
function greet(name) {
  return `안녕하세요, ${name}님!`;
}

// 2. 화살표 함수: 간결하고 this 바인딩이 없음
const greetArrow = (name) => `안녕하세요, ${name}님!`;

// 3. 단일 표현식이면 중괄호와 return 생략
const double = (n) => n * 2;

// 4. 여러 줄이면 중괄호와 return 필요
const processUser = (user) => {
  const displayName = user.name.trim();
  return { ...user, displayName };
};

// 클로저 활용: 내부 함수가 외부 변수를 기억
function makeCounter(start = 0) {
  let count = start;
  return {
    increment: () => ++count,
    decrement: () => --count,
    value: () => count,
  };
}

const counter = makeCounter(10);
counter.increment(); // 11
counter.increment(); // 12
counter.value();     // 12
```

## 배열 메서드로 선언형 코드 작성

**Before (var와 for)**

```javascript
var users = [
  { name: "Alice", age: 30, active: true },
  { name: "Bob",   age: 25, active: false },
  { name: "Carol", age: 28, active: true },
];

var activeUsers = [];
for (var i = 0; i < users.length; i++) {
  if (users[i].active) activeUsers.push(users[i].name);
}
```

**After (모던 JS)**

```javascript
const users = [
  { name: "Alice", age: 30, active: true },
  { name: "Bob",   age: 25, active: false },
  { name: "Carol", age: 28, active: true },
];

// filter: 조건에 맞는 요소만 추출
const activeUsers = users.filter(u => u.active);
// [{ name: "Alice", ... }, { name: "Carol", ... }]

// map: 각 요소를 다른 값으로 변환
const names = users.map(u => u.name);
// ["Alice", "Bob", "Carol"]

// reduce: 누적 계산
const totalAge = users.reduce((sum, u) => sum + u.age, 0);
// 83

// 체이닝: 순서대로 변환
const activeNames = users
  .filter(u => u.active)
  .map(u => u.name)
  .sort();
// ["Alice", "Carol"]

// find: 첫 번째 일치 요소
const alice = users.find(u => u.name === "Alice");

// some / every
const hasInactive = users.some(u => !u.active);   // true
const allActive = users.every(u => u.active);      // false
```

## 실습: 할 일 목록을 5단계로 만들기

### 1단계 — HTML skeleton

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>Todo 앱</title>
  <style>
    body { font-family: system-ui; max-width: 500px; margin: 2rem auto; padding: 1rem; }
    #list li { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #e2e8f0; }
    .done { text-decoration: line-through; color: #94a3b8; }
    button { cursor: pointer; }
  </style>
</head>
<body>
  <h1>할 일 목록</h1>
  <form id="form">
    <input id="input" type="text" placeholder="새 할 일 입력..." required>
    <button type="submit">추가</button>
  </form>
  <ul id="list"></ul>
  <p id="summary"></p>
  <script src="todo.js"></script>
</body>
</html>
```

### 2단계 — State variable

```javascript
// todo.js
// 상태: 단일 진실의 원천
let todos = [];
let nextId = 1;
```

### 3단계 — A render function

```javascript
function render() {
  const listEl   = document.getElementById("list");
  const summaryEl = document.getElementById("summary");

  // innerHTML 대신 DOM 조작으로 XSS 방지
  listEl.innerHTML = "";
  todos.forEach(todo => {
    const li  = document.createElement("li");
    const span = document.createElement("span");
    span.textContent = todo.text;
    if (todo.done) span.classList.add("done");

    const toggleBtn = document.createElement("button");
    toggleBtn.textContent = todo.done ? "되돌리기" : "완료";
    toggleBtn.dataset.id = todo.id;
    toggleBtn.dataset.action = "toggle";

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "삭제";
    deleteBtn.dataset.id = todo.id;
    deleteBtn.dataset.action = "delete";

    li.append(span, toggleBtn, deleteBtn);
    listEl.appendChild(li);
  });

  const doneCount = todos.filter(t => t.done).length;
  summaryEl.textContent = `전체 ${todos.length}개 / 완료 ${doneCount}개`;
}
```

### 4단계 — Events

```javascript
document.getElementById("form").addEventListener("submit", (e) => {
  e.preventDefault();
  const input = document.getElementById("input");
  const text = input.value.trim();
  if (!text) return;

  todos.push({ id: nextId++, text, done: false });
  input.value = "";
  render();
});
```

### 5단계 — Delete via event delegation

```javascript
// 부모에 리스너 하나로 모든 버튼 처리
document.getElementById("list").addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-action]");
  if (!btn) return;

  const id = Number(btn.dataset.id);
  const action = btn.dataset.action;

  if (action === "delete") {
    todos = todos.filter(t => t.id !== id);
  } else if (action === "toggle") {
    todos = todos.map(t => t.id === id ? { ...t, done: !t.done } : t);
  }

  render();
});

// localStorage로 새로고침 후에도 유지
function saveTodos() {
  localStorage.setItem("todos", JSON.stringify(todos));
}

function loadTodos() {
  const saved = localStorage.getItem("todos");
  if (saved) {
    todos = JSON.parse(saved);
    nextId = Math.max(0, ...todos.map(t => t.id)) + 1;
  }
}

// 상태 변경 시마다 저장
["submit"].forEach(evt =>
  document.getElementById("form").addEventListener(evt, () => saveTodos())
);
document.getElementById("list").addEventListener("click", () => saveTodos());

loadTodos();
render();
```

## 디버깅 시나리오

### 시나리오 1: 삭제 후 인덱스가 꼬일 때

```javascript
// 잘못된 방법: splice는 원본을 변경하고 인덱스가 밀림
todos.splice(idx, 1);  // 다음 요소 인덱스가 변해 버그 발생 가능

// 올바른 방법: filter로 새 배열 반환
todos = todos.filter(t => t.id !== id);
```

### 시나리오 2: 이벤트가 여러 번 등록될 때

```javascript
// 잘못된 패턴: render() 안에서 이벤트 등록 → 호출마다 누적됨
function render() {
  button.addEventListener("click", handler);  // 매번 추가됨!
}

// 올바른 패턴: 이벤트는 한 번만 등록, render()는 화면만 업데이트
button.addEventListener("click", handler);  // 초기화 시 한 번만
function render() { /* DOM 업데이트만 */ }
```

### 시나리오 3: 디버깅 도구 사용

```javascript
// Console에서 상태 확인
console.table(todos);
// ┌─────┬────┬──────────────┬───────┐
// │index│ id │     text     │ done  │
// ├─────┼────┼──────────────┼───────┤
// │  0  │  1 │ "첫 번째 할 일" │ false │

// 이벤트 타깃 확인
document.getElementById("list").addEventListener("click", (e) => {
  console.log("clicked:", e.target.tagName, e.target.dataset);
});
```

## 실무 점검 루프

1. **상태를 확인합니다.** 사용자 행동 전후의 데이터 구조를 먼저 로그로 확인합니다.
2. **렌더링을 확인합니다.** 상태가 바뀐 뒤 `render()`가 실제로 호출되는지 확인합니다.
3. **이벤트 경로를 확인합니다.** 클릭 위치가 이상하면 `event.target`을 직접 확인합니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|---|---|---|
| `var` 계속 사용 | 함수 스코프 특성으로 루프 버그 발생 | `const`를 기본, 재할당 필요 시 `let` 사용 |
| `==` 사용 | 타입 강제 변환으로 예상 외 결과 | 항상 `===` 사용 |
| 상태와 DOM을 동시에 여러 곳에서 수정 | 진실의 출처가 사라져 디버깅 불가 | 상태는 한 곳에, 화면은 render() 함수 하나로 |
| 모든 요소에 리스너 개별 부착 | 메모리 낭비, 동적 추가 요소 처리 불가 | 이벤트 위임 패턴 사용 |
| innerHTML에 사용자 입력 직접 삽입 | XSS(크로스 사이트 스크립팅) 취약점 | `textContent` 또는 `createElement`로 DOM 조작 |
| `async` 내부 에러 미처리 | 실패가 조용히 묻혀 빈 화면만 보임 | try/catch와 사용자 피드백 함께 구현 |

## 실무에서는 이렇게 보입니다

대부분의 팀은 TypeScript, ESLint, Prettier를 함께 사용합니다. JavaScript의 자유로움이 팀 단위에서는 오히려 위험이 되기 때문에 타입과 규칙으로 경계를 세웁니다. 하지만 그 모든 도구도 결국 순수 JavaScript 위에서 동작합니다.

```typescript
// TypeScript로 같은 패턴을 더 안전하게
interface Todo {
  id: number;
  text: string;
  done: boolean;
}

let todos: Todo[] = [];

function toggleTodo(id: number): void {
  todos = todos.map(t =>
    t.id === id ? { ...t, done: !t.done } : t
  );
  render();
}
```

## 시니어 엔지니어는 이렇게 생각합니다

- 함수는 한 가지 일을 하게 만듭니다.
- 상태와 렌더링을 분리합니다.
- 기본은 `const`, 예외적으로 `let`, `var`는 쓰지 않습니다.
- 콜백 지옥은 `async/await`로 평탄화합니다.
- JavaScript는 쓰는 시간보다 읽는 시간이 더 길다는 전제로 설계합니다.

## 운영 체크리스트

- [ ] `let`과 `const`의 차이를 설명할 수 있습니다.
- [ ] 화살표 함수를 작성할 수 있습니다.
- [ ] `map/filter/reduce`로 반복 로직을 표현할 수 있습니다.
- [ ] DOM을 읽고 수정할 수 있습니다.
- [ ] event delegation을 한 번 직접 사용해 봤습니다.
- [ ] `localStorage`로 상태를 유지해 봤습니다.

## 연습 문제

1. 위 todo 예제에 완료 표시 기능을 추가해 보세요.
2. `localStorage`를 사용해 새로고침 후에도 todo가 남도록 만들어 보세요.
3. `map/filter/reduce`만 사용해 평균 점수를 계산하는 코드를 작성해 보세요.
4. 클로저를 활용해 `makeCounter`처럼 독립적인 상태를 갖는 함수를 직접 만들어 보세요.

## 정리 및 다음 단계

순수 JavaScript만으로도 작은 애플리케이션을 만들 수 있습니다. 다만 화면이 커질수록 상태와 렌더링을 더 체계적으로 연결해 주는 도구가 필요해집니다.

다음 글에서는 그 연결을 담당하는 컴포넌트와 상태 모델을 봅니다.

## 처음 질문으로 돌아가기

- **`let`과 `const`를 어떻게 구분해 쓰는 편이 좋을까요?**
  - 기본값은 `const`입니다. 재할당이 확실히 필요한 경우에만 `let`을 씁니다. `var`는 현대 코드에서 사용하지 않습니다.
- **함수와 화살표 함수는 어떤 기준으로 읽고 작성하면 될까요?**
  - 콜백과 짧은 변환 함수는 화살표 함수, 메서드나 생성자처럼 `this`가 필요한 곳은 일반 함수를 씁니다.
- **`map`, `filter`, `reduce`는 왜 for문보다 자주 권장될까요?**
  - 코드에서 의도를 직접 드러내기 때문입니다. `filter`만 봐도 "조건에 맞는 것만 남긴다"는 뜻이 보입니다. for문은 내부를 읽어야 의도를 알 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML과 CSS 기본](./02-html-and-css-basics.md)
- **Frontend Development 101 (3/10): JavaScript 기본 (현재 글)**
- [Frontend Development 101 (4/10): 컴포넌트와 상태](./04-components-and-state.md)
- [Frontend Development 101 (5/10): 라우팅과 페이지](./05-routing-and-pages.md)
- [Frontend Development 101 (6/10): API 호출과 비동기](./06-api-calls-and-async.md)
- [Frontend Development 101 (7/10): 폼과 유효성 검사](./07-forms-and-validation.md)
- [Frontend Development 101 (8/10): 스타일링과 디자인 시스템](./08-styling-and-design-system.md)
- [Frontend Development 101 (9/10): 빌드 도구와 번들링](./09-build-tools-and-bundling.md)
- [작은 프론트엔드 앱 만들기](./10-building-a-small-frontend-app.md)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [MDN: JavaScript guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [MDN: Introduction to the DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction)
- [MDN: Event bubbling](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling)

### 확인용 자료
- [JavaScript.info](https://javascript.info/)
- [TC39 proposals](https://github.com/tc39/proposals)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/frontend-development-101/ko)

Tags: Frontend, JavaScript, DOM, Web, Beginner
