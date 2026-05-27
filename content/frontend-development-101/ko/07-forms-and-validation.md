---
series: frontend-development-101
episode: 7
title: "Frontend Development 101 (7/10): 폼과 유효성 검사"
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
  - Forms
  - Validation
  - UX
  - React
seo_description: 폼 입력과 유효성 검사 전략을 익힙니다. 제어 컴포넌트, 실시간 피드백, Zod 검증, 접근성 고려 사항 등 실무 UX 패턴을 정리합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (7/10): 폼과 유효성 검사

이 글은 Frontend Development 101 시리즈의 일곱 번째 글입니다. 여기서는 폼을 단순한 입력 묶음이 아니라 사용자와의 대화 인터페이스로 설명합니다. 좋은 폼은 제출 후에만 검사하지 않고, 입력하는 동안 도와주며, 에러를 친절하고 구체적으로 보여 줍니다.

사용자는 폼을 통해 제품과 가장 길게 대화합니다. 회원가입, 로그인, 결제, 검색, 설정 변경까지 대부분의 중요한 순간이 폼에서 일어납니다. 그런데도 많은 폼은 제출 버튼을 누른 뒤에야 뒤늦게 오류를 보여 줍니다.

![Frontend Development 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/07/07-01-diagram.ko.png)
*Frontend Development 101 7장 흐름 개요*

> 폼은 '입력 받는 UI'가 아니라 '사용자 의도를 도메인 모델로 옮기는 좁은 통로'입니다 — controlled vs uncontrolled, 클라이언트 검증과 서버 검증의 역할 분리가 명확하지 않으면 보안·UX·접근성이 한꺼번에 무너집니다.

## 먼저 던지는 질문

- controlled input과 uncontrolled input은 어떤 차이가 있을까요?
- 유효성 검사는 형식, 비즈니스 규칙, 서버 검증으로 왜 나눠 생각해야 할까요?
- 에러 메시지는 어디에, 언제 보여 주는 편이 가장 친절할까요?

## 왜 중요한가

폼은 전환율을 직접 좌우합니다. 회원가입 한 칸이 어색하면 사용자는 떠나고, 결제 폼 하나가 불친절하면 매출이 줄어듭니다. 폼은 프론트엔드의 UX 시험지라고 봐도 과장이 아닙니다.

좋은 폼은 덜 묻고, 오타를 빨리 잡아 주고, 빠르게 제출됩니다. 결국 기술 구현보다도 사용자가 실수했을 때 얼마나 자연스럽게 복구하게 돕는지가 더 중요합니다.

## 개념 한눈에 보기

이 흐름을 보면 프론트엔드 검증이 서버 검증을 대체하는 것이 아님을 알 수 있습니다. 프론트엔드는 사용자 경험을 개선하고, 서버는 최종 보안을 책임집니다.

## 핵심 용어

- **Controlled input**: 입력값이 React state에 저장되는 방식입니다.
- **Uncontrolled input**: 입력값이 DOM 안에 남아 있는 방식입니다.
- **Schema validation**: Zod, Yup 같은 라이브러리로 선언적으로 검증하는 방식입니다.
- **Inline error**: 필드 옆이나 아래에 바로 보이는 에러 메시지입니다.
- **`aria-invalid`**: 스크린 리더에 현재 필드가 유효하지 않음을 알리는 ARIA 속성입니다.

## 전통 방식과 현대 방식 비교

**Before (제출 시에만 검증)**

```javascript
form.onsubmit = () => {
  if (email.value === "") alert("Please enter an email");
};
```

**After (실시간 인라인 검증 + 친절한 메시지)**

```jsx
{!isEmail(email) && <p className="error">That doesn't look like an email</p>}
```

둘의 차이는 단순한 구현 방식이 아닙니다. 전자는 사용자가 제출한 뒤에야 실패를 알게 되고, 후자는 입력 도중에 바로 수정할 수 있게 돕습니다.

## 실습: 가입 폼을 5단계로 만들기

### 1단계 — Controlled input

```jsx
function Signup() {
  const [email, setEmail] = useState("");
  return <input value={email} onChange={e => setEmail(e.target.value)} />;
}
```

### 2단계 — Format check

```jsx
const isValidEmail = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
```

### 3단계 — Inline error

```jsx
<input
  value={email}
  onChange={e => setEmail(e.target.value)}
  aria-invalid={!isValidEmail}
/>
{!isValidEmail && email && <p className="error">That doesn't look like an email</p>}
```

### 4단계 — Disable submit while invalid

```jsx
<button disabled={!isValidEmail || submitting}>
  {submitting ? "Submitting..." : "Sign up"}
</button>
```

### 5단계 — Schema with Zod

```jsx
import { z } from "zod";

const SignupSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

const result = SignupSchema.safeParse({ email, password });
if (!result.success) showErrors(result.error.format());
```

이 예제에서 핵심은 3단계와 5단계입니다. 입력 중 피드백을 주는 UX와, 프론트와 백엔드에서 같은 스키마 개념을 공유하는 구조가 결합되면 폼은 훨씬 일관되고 안전해집니다.

## 검증 포인트

- 잘못된 이메일 형식에서는 inline 에러가 보이고, 올바른 값에서는 제출 버튼이 활성화되는지 확인합니다.
- 키보드만으로 필드 이동과 제출이 가능하고, 에러 필드에 `aria-invalid`가 붙는지 확인합니다.

## 문제가 생기면 먼저 볼 것

- 에러가 안 사라지면 controlled state 업데이트와 정규식 검사 시점을 확인합니다.
- 스크린 리더 정보가 비면 `label`, `id`, `aria-describedby` 연결을 먼저 확인합니다.

## 이 코드에서 주목할 점

- 사용자가 입력하는 동안 검사가 진행됩니다.
- `aria-invalid`로 같은 정보를 스크린 리더 사용자에게도 전달합니다.
- Zod 스키마 하나로 프론트엔드와 백엔드 검증 기준을 맞출 수 있습니다.

## 자주 하는 실수 5가지

1. **비밀번호를 한 번만 입력받습니다.** 단순 오타가 가입 실패로 이어질 수 있습니다.
2. **에러를 제출 후에만 보여 줍니다.** 사용자는 모든 필드를 다시 훑어야 합니다.
3. **기술적인 에러 문구를 그대로 노출합니다.** “Schema validation failed”는 사용자에게 아무 의미가 없습니다.
4. **`<label>`을 빼먹습니다.** 스크린 리더는 이 입력이 무엇인지 정확히 알기 어렵습니다.
5. **모바일 키보드 힌트를 주지 않습니다.** 이메일 입력인데 일반 키보드가 뜨면 UX가 나빠집니다.

## 실무에서는 이렇게 보입니다

대부분의 React 앱은 React Hook Form과 Zod 조합을 사용합니다. 상태 관리, 검증, 제출, 에러 표시를 선언적으로 묶을 수 있기 때문입니다. `useState`만으로 모든 폼을 직접 다루는 방식은 학습 단계 이후 점점 줄어드는 편입니다.

하지만 도구보다 먼저 잡아야 하는 것은 원칙입니다. 에러는 친절해야 하고, 키보드만으로도 폼 전체를 쓸 수 있어야 하며, 프론트 검증과 서버 검증은 역할이 다르다는 점을 분명히 해야 합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 폼은 대화이므로 매 단계마다 피드백을 줍니다.
- 프론트엔드는 UX를 위해, 백엔드는 보안을 위해 각각 검증합니다.
- 에러 메시지는 친절하고 행동 가능해야 합니다.
- 전체 폼은 키보드만으로도 완주 가능해야 합니다.
- 자동완성과 모바일 키보드 타입은 옵션이 아니라 기본값입니다.

## 체크리스트

- [ ] controlled input을 사용할 수 있습니다.
- [ ] inline 에러 메시지를 보여 줄 수 있습니다.
- [ ] 모든 입력에 `<label>`과 적절한 연결을 추가할 수 있습니다.
- [ ] `aria-invalid`와 `aria-describedby`의 역할을 설명할 수 있습니다.
- [ ] Zod나 Yup 같은 스키마 검증기를 사용해 봤습니다.

## 연습 문제

1. 이메일, 비밀번호, 비밀번호 확인 필드를 가진 가입 폼을 만들어 보세요.
2. 모든 필드에 inline 검증과 친절한 에러 메시지를 추가해 보세요.
3. 키보드만으로 폼을 끝까지 작성하고 제출할 수 있는지 직접 확인해 보세요.

## 정리 및 다음 단계

폼은 사용자와 가장 길게 만나는 인터페이스입니다. 입력을 안전하게 받고 친절하게 안내하는 감각이 있어야 제품 전체가 안정적으로 느껴집니다.

다음 글에서는 이 폼과 화면 전체에 일관된 모양을 부여하는 스타일링과 디자인 시스템을 봅니다.

## 처음 질문으로 돌아가기

- **controlled input과 uncontrolled input은 어떤 차이가 있을까요?**
  - controlled input은 `value={email}`과 `onChange={e => setEmail(e.target.value)}`처럼 입력값을 React state가 직접 들고 있는 방식입니다. uncontrolled input은 값이 DOM 안에 남아 있어 즉시 읽기는 쉽지만, 이 글처럼 실시간 검증과 버튼 활성화 제어를 하려면 controlled 방식이 더 자연스럽습니다.
- **유효성 검사는 형식, 비즈니스 규칙, 서버 검증으로 왜 나눠 생각해야 할까요?**
  - 이메일 정규식처럼 입력 형식을 빠르게 잡는 검사는 프론트엔드 UX를 좋게 만들고, `password` 최소 길이 같은 규칙은 Zod 스키마로 명시적으로 공유할 수 있습니다. 하지만 최종 보안과 중복 검사 같은 판단은 서버가 다시 확인해야 하므로, 본문은 프론트엔드 검증이 서버 검증을 대체하지 않는다고 분명히 선을 그었습니다.
- **에러 메시지는 어디에, 언제 보여 주는 편이 가장 친절할까요?**
  - 본문은 제출 뒤 경고창보다 필드 가까이에 inline 에러를 두고, 사용자가 입력하는 동안 수정 가능하게 만드는 방식을 권했습니다. `aria-invalid`와 에러 문구를 함께 붙이면 시각 사용자와 스크린 리더 사용자 모두가 같은 시점에 같은 문제를 이해할 수 있어 더 친절합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML과 CSS 기본](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript 기본](./03-javascript-basics.md)
- [Frontend Development 101 (4/10): 컴포넌트와 상태](./04-components-and-state.md)
- [Frontend Development 101 (5/10): 라우팅과 페이지](./05-routing-and-pages.md)
- [Frontend Development 101 (6/10): API 호출과 비동기](./06-api-calls-and-async.md)
- **폼과 유효성 검사 (현재 글)**
- 스타일링과 디자인 시스템 (예정)
- 빌드 도구와 번들링 (예정)
- 작은 프론트엔드 앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [React Hook Form documentation](https://react-hook-form.com/)
- [Zod documentation](https://zod.dev/)
- [MDN: Client-side form validation](https://developer.mozilla.org/en-US/docs/Learn/Forms/Form_validation)

### 확인용 자료
- [WAI: Forms tutorial](https://www.w3.org/WAI/tutorials/forms/)
- [MDN: ARIA aria-invalid](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-invalid)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/frontend-development-101/ko)

Tags: Frontend, Forms, Validation, UX, React
