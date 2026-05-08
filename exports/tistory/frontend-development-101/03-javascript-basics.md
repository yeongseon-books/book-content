
# JavaScript 기본

> Frontend Development 101 시리즈 (3/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 자바스크립트는 *어디서부터* 익히면 가장 효율적일까요?

> 모든 기능을 다 외우지 마세요. *변수, 함수, 배열/객체, DOM, 이벤트* 다섯 가지가 자바스크립트의 *80%* 입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- `let`/`const` 와 *immutable 사고방식*
- 함수, arrow function, 클로저의 *최소 이해*
- 배열/객체 메서드 (`map`, `filter`, `reduce`)
- DOM 조회와 수정
- 이벤트 리스너의 *기본 패턴*

## 왜 중요한가

JS는 framework가 *바뀌어도* 똑같이 쓰입니다. React 컴포넌트 안에서도, Vue 안에서도, Node.js 백엔드에서도 *같은 문법* 입니다. 여기에 시간을 쓰면 *모든 framework가 빨라집니다.*

> 좋은 자바스크립트는 *작고 분리된 함수* 의 합입니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Var["let/const"] --> Fn["Functions"]
    Fn --> Coll["Array/Object methods"]
    Coll --> DOM["DOM"]
    DOM --> Evt["Events"]
```

## 핵심 용어 정리

- **`const`**: 재할당 불가. *기본값으로* 쓰세요.
- **Arrow function**: `() => {}` 짧은 함수 표기.
- **Closure**: 함수가 *자기가 만들어진 환경* 을 기억하는 것.
- **`map/filter/reduce`**: *for문 없이* 컬렉션을 변환하는 표준 도구.
- **Event delegation**: 부모 요소 *하나에* 리스너를 달아 자식 이벤트를 처리.

## Before/After

**Before (var와 for문)**

```javascript
var arr = [1,2,3];
var doubled = [];
for (var i = 0; i < arr.length; i++) doubled.push(arr[i] * 2);
```

**After (modern JS)**

```javascript
const arr = [1, 2, 3];
const doubled = arr.map(n => n * 2);
```

## 실습: 할 일 목록 5단계

### 1단계 — HTML 골격

```html
<input id="todo">
<button id="add">추가</button>
<ul id="list"></ul>
```

### 2단계 — 상태 변수

```javascript
const todos = [];
```

### 3단계 — 함수로 분리

```javascript
function render() {
  const list = document.getElementById("list");
  list.innerHTML = todos.map(t => `<li>${t}</li>`).join("");
}
```

### 4단계 — 이벤트

```javascript
document.getElementById("add").addEventListener("click", () => {
  const input = document.getElementById("todo");
  if (!input.value) return;
  todos.push(input.value);
  input.value = "";
  render();
});
```

### 5단계 — Event delegation으로 삭제

```javascript
document.getElementById("list").addEventListener("click", (e) => {
  if (e.target.tagName === "LI") {
    const idx = [...e.target.parentNode.children].indexOf(e.target);
    todos.splice(idx, 1);
    render();
  }
});
```

## 이 코드에서 주목할 점

- 상태(`todos`)와 렌더링(`render`)이 *분리* 되어 있습니다.
- 모든 변경은 *상태 → 렌더링* 순서로 흐릅니다. (React 패러다임의 *맛보기*)
- 이벤트 리스너는 *부모에 하나* 만 달면 효율적입니다.

## 자주 하는 실수 5가지

1. **`var` 를 사용한다.** 스코프가 *함수 단위* 라 버그가 생깁니다. `const/let` 만 쓰세요.
2. **`==` 를 쓴다.** 타입 변환이 들어가 *예측 불가능* 합니다. `===` 만 쓰세요.
3. **상태와 DOM을 동시에 갱신한다.** 어떤 것이 *진짜 상태* 인지 알 수 없게 됩니다.
4. **모든 요소에 리스너를 단다.** 메모리와 성능 *낭비* 입니다.
5. **`async` 안에서 에러를 처리하지 않는다.** *조용히 실패* 하는 버그가 생깁니다.

## 실무에서는 이렇게 쓰입니다

대부분의 회사는 *TypeScript* + *ESLint* + *Prettier* 조합을 표준으로 사용합니다. JS의 자유로움이 팀 규모에서는 *위험* 이 되기 때문에 타입과 lint로 *경계* 를 만듭니다. 그러나 그 모든 도구도 *순수 JS 위에서* 돕니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 함수는 *하나의 일* 만 한다.
- 상태와 렌더링은 *분리* 한다.
- `const` 가 기본, `let` 은 예외, `var` 는 금지.
- 콜백 지옥이 보이면 `async/await` 로 평탄화한다.
- 자바스크립트는 *읽는 시간이 더 길다.*

## 체크리스트

- [ ] `let/const` 의 차이를 안다.
- [ ] arrow function을 쓸 수 있다.
- [ ] `map/filter/reduce` 로 for문을 대체한다.
- [ ] DOM을 조회/수정할 수 있다.
- [ ] event delegation을 한 번 써봤다.

## 연습 문제

1. 위 todo 코드에 *완료 표시 (체크)* 기능을 추가하세요.
2. `localStorage` 를 사용해 새로고침 후에도 todo가 유지되게 하세요.
3. `map/filter/reduce` 만으로 평균 점수를 구하는 함수를 작성하세요.

## 정리 및 다음 단계

순수 JS만으로도 작은 앱이 만들어집니다. 그러나 화면이 커지면 *상태와 렌더링* 을 자동으로 묶어주는 도구가 필요합니다. 다음 글에서 *컴포넌트와 상태* 라는 개념을 다룹니다.

- [프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [HTML과 CSS 기본](./02-html-and-css-basics.md)
- **JavaScript 기본 (현재 글)**
- 컴포넌트와 상태 (예정)
- 라우팅과 페이지 (예정)
- API 호출과 비동기 (예정)
- 폼과 유효성 검사 (예정)
- 스타일링과 디자인 시스템 (예정)
- 빌드 도구와 번들링 (예정)
- 작은 프론트엔드 앱 만들기 (예정)
## 참고 자료

- [MDN JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [JavaScript.info](https://javascript.info/)
- [Eloquent JavaScript](https://eloquentjavascript.net/)
- [TC39 Proposals](https://github.com/tc39/proposals)

Tags: Frontend, JavaScript, DOM, Web, Beginner

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
