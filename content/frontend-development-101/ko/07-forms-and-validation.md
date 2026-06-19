---
series: frontend-development-101
episode: 7
title: "Frontend Development 101 (7/10): 폼과 유효성 검사"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/219"
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
  - Forms
  - Validation
  - UX
  - React
seo_description: 폼 입력과 유효성 검사 전략을 익힙니다. 제어 컴포넌트, 실시간 피드백, Zod 검증, 접근성 고려 사항 등 실무 UX 패턴을 정리합니다.
last_reviewed: '2026-05-12'
---

# Frontend Development 101 (7/10): 폼과 유효성 검사

이 흐름을 보면 프론트엔드 검증이 서버 검증을 대체하는 것이 아님을 알 수 있습니다. 프론트엔드는 사용자 경험을 개선하고, 서버는 최종 보안을 책임집니다.

이 글은 Frontend Development 101 시리즈의 일곱 번째 글입니다. 여기서는 폼을 단순한 입력 묶음이 아니라 사용자와의 대화 인터페이스로 설명합니다. 좋은 폼은 제출 후에만 검사하지 않고, 입력하는 동안 도와주며, 에러를 친절하고 구체적으로 보여 줍니다.

![Frontend Development 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/07/07-01-diagram.ko.png)
*Frontend Development 101 7장 흐름 개요*

> 폼은 '입력 받는 UI'가 아니라 '사용자 의도를 도메인 모델로 옮기는 좁은 통로'입니다 — controlled vs uncontrolled, 클라이언트 검증과 서버 검증의 역할 분리가 명확하지 않으면 보안·UX·접근성이 한꺼번에 무너집니다.

## 이 글에서 다룰 문제

- controlled input과 uncontrolled input은 어떤 차이가 있을까요?
- 유효성 검사는 형식, 비즈니스 규칙, 서버 검증으로 왜 나눠 생각해야 할까요?
- 에러 메시지는 어디에, 언제 보여 주는 편이 가장 친절할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 개념 한눈에 보기

| 용어 | 뜻 | 실무에서 왜 중요한가 |
|---|---|---|
| Controlled input | 입력값이 React state에 저장되는 방식입니다. | 입력값과 검증 상태를 한 모델에서 추적하기 쉽습니다. |
| Uncontrolled input | 입력값이 DOM 안에 남아 있는 방식입니다. | 단순한 폼이나 레거시 통합에서는 가볍지만, 상태 추적은 더 어렵습니다. |
| Schema validation | Zod, Yup 같은 라이브러리로 선언적으로 검증하는 방식입니다. | 프론트엔드와 백엔드의 검증 규칙을 더 쉽게 맞출 수 있습니다. |
| Inline error | 필드 옆이나 아래에 바로 보이는 에러 메시지입니다. | 사용자가 제출 후 되돌아가는 비용을 줄여 줍니다. |
| `aria-invalid` | 스크린 리더에 현재 필드가 유효하지 않음을 알리는 ARIA 속성입니다. | 시각적 에러 상태를 보조 기술 사용자에게도 동일하게 전달합니다. |

## 제출 후 에러 vs 입력 중 피드백

**Before (제출 시에만 검증)**

```javascript
form.addEventListener("submit", (e) => {
  e.preventDefault();
  if (!emailInput.value) {
    alert("이메일을 입력해 주세요");  // 이미 모든 필드를 입력한 후
  }
  if (!passwordInput.value) {
    alert("비밀번호를 입력해 주세요");
  }
});
```

**After (실시간 인라인 검증 + 친절한 메시지)**

```jsx
// 필드를 벗어날 때 검증 + 해당 필드 바로 아래 에러 표시
{touched.email && errors.email && (
  <p id="email-error" className="field-error" role="alert">
    {errors.email}
  </p>
)}
```

## 실습: 가입 폼을 5단계로 만들기

### 1단계 — Controlled input

```jsx
// src/components/SignupForm.jsx
import { useState } from "react";

function SignupForm() {
  const [values, setValues] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    name: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
  };

  return (
    <form>
      <input
        name="email"
        type="email"
        value={values.email}
        onChange={handleChange}
        placeholder="이메일"
      />
    </form>
  );
}
```

### 2단계 — Format check

```jsx
// 검증 규칙을 함수로 분리
function validateForm(values) {
  const errors = {};

  // 이메일 형식 검사
  const emailRegex = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
  if (!values.email) {
    errors.email = "이메일을 입력해 주세요.";
  } else if (!emailRegex.test(values.email)) {
    errors.email = "올바른 이메일 형식이 아닙니다. (예: user@example.com)";
  }

  // 비밀번호 강도 검사
  if (!values.password) {
    errors.password = "비밀번호를 입력해 주세요.";
  } else if (values.password.length < 8) {
    errors.password = "비밀번호는 8자 이상이어야 합니다.";
  } else if (!/[A-Z]/.test(values.password)) {
    errors.password = "비밀번호에 대문자를 포함해 주세요.";
  }

  // 비밀번호 확인
  if (values.password !== values.confirmPassword) {
    errors.confirmPassword = "비밀번호가 일치하지 않습니다.";
  }

  // 이름 검사
  if (!values.name.trim()) {
    errors.name = "이름을 입력해 주세요.";
  } else if (values.name.trim().length < 2) {
    errors.name = "이름은 2자 이상이어야 합니다.";
  }

  return errors;
}
```

### 3단계 — Inline error

```jsx
function SignupForm() {
  const [values, setValues]   = useState({ email: "", password: "", confirmPassword: "", name: "" });
  const [touched, setTouched] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const errors = validateForm(values);
  const hasErrors = Object.keys(errors).length > 0;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
  };

  // 필드를 벗어날 때 touched 표시 (아직 안 건든 필드는 에러 숨김)
  const handleBlur = (e) => {
    setTouched(prev => ({ ...prev, [e.target.name]: true }));
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="field">
        <label htmlFor="email">이메일</label>
        <input
          id="email"
          name="email"
          type="email"
          value={values.email}
          onChange={handleChange}
          onBlur={handleBlur}
          aria-invalid={!!(touched.email && errors.email)}
          aria-describedby={touched.email && errors.email ? "email-error" : undefined}
          autoComplete="email"
        />
        {touched.email && errors.email && (
          <p id="email-error" className="field-error" role="alert">
            {errors.email}
          </p>
        )}
      </div>

      <div className="field">
        <label htmlFor="password">비밀번호</label>
        <input
          id="password"
          name="password"
          type="password"
          value={values.password}
          onChange={handleChange}
          onBlur={handleBlur}
          aria-invalid={!!(touched.password && errors.password)}
          aria-describedby={touched.password && errors.password ? "password-error" : undefined}
          autoComplete="new-password"
        />
        {touched.password && errors.password && (
          <p id="password-error" className="field-error" role="alert">
            {errors.password}
          </p>
        )}
      </div>
    </form>
  );
}
```

### 4단계 — Disable submit while invalid

```jsx
async function handleSubmit(e) {
  e.preventDefault();

  // 모든 필드를 touched로 표시해서 에러 전부 표시
  const allTouched = Object.keys(values).reduce(
    (acc, key) => ({ ...acc, [key]: true }), {}
  );
  setTouched(allTouched);

  if (hasErrors) return;

  setSubmitting(true);
  try {
    await submitSignup(values);
    // 성공 처리
  } catch (err) {
    setServerError(err.message);
  } finally {
    setSubmitting(false);
  }
}

// 버튼 상태
<button
  type="submit"
  disabled={submitting}
  aria-busy={submitting}
>
  {submitting ? "가입 중..." : "가입하기"}
</button>
```

### 5단계 — Schema with Zod

```jsx
import { z } from "zod";

// 스키마 선언: 프론트엔드와 백엔드가 같은 규칙 공유 가능
const SignupSchema = z.object({
  email: z
    .string()
    .email("올바른 이메일 형식이 아닙니다.")
    .min(1, "이메일을 입력해 주세요."),
  password: z
    .string()
    .min(8, "비밀번호는 8자 이상이어야 합니다.")
    .regex(/[A-Z]/, "대문자를 포함해 주세요."),
  confirmPassword: z.string(),
  name: z
    .string()
    .min(2, "이름은 2자 이상이어야 합니다.")
    .max(50, "이름은 50자 이하여야 합니다."),
}).refine(
  data => data.password === data.confirmPassword,
  { message: "비밀번호가 일치하지 않습니다.", path: ["confirmPassword"] }
);

// 검증 실행
function validateWithZod(values) {
  const result = SignupSchema.safeParse(values);
  if (result.success) return {};

  // Zod 오류를 { field: message } 형태로 변환
  return result.error.issues.reduce((acc, issue) => {
    const field = issue.path[0];
    if (!acc[field]) acc[field] = issue.message;
    return acc;
  }, {});
}
```

## React Hook Form + Zod 조합 (실무 패턴)

```jsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  email: z.string().email("올바른 이메일을 입력해 주세요."),
  password: z.string().min(8, "8자 이상 입력해 주세요."),
});

function LoginForm({ onSuccess }) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm({ resolver: zodResolver(schema) });

  const onSubmit = async (data) => {
    try {
      await login(data);
      onSuccess();
    } catch (err) {
      // 서버 에러를 특정 필드에 표시
      if (err.code === "INVALID_CREDENTIALS") {
        setError("email", { message: "이메일 또는 비밀번호가 올바르지 않습니다." });
      }
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label htmlFor="email">이메일</label>
        <input
          id="email"
          type="email"
          {...register("email")}
          aria-invalid={!!errors.email}
        />
        {errors.email && <p role="alert">{errors.email.message}</p>}
      </div>

      <div>
        <label htmlFor="password">비밀번호</label>
        <input
          id="password"
          type="password"
          {...register("password")}
          aria-invalid={!!errors.password}
        />
        {errors.password && <p role="alert">{errors.password.message}</p>}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "로그인 중..." : "로그인"}
      </button>
    </form>
  );
}
```

## 디버깅 시나리오

### 시나리오 1: 에러가 안 사라질 때

```jsx
// 문제: onChange에서 touched 상태를 업데이트하지 않음
// 에러가 입력해도 사라지지 않음

// 수정: 값이 바뀌면 에러도 다시 계산
const handleChange = (e) => {
  const { name, value } = e.target;
  setValues(prev => ({ ...prev, [name]: value }));
  // touched는 유지하되 에러는 새 값으로 다시 계산됨
};
```

### 시나리오 2: 스크린 리더가 에러를 읽지 않을 때

```html
<!-- 잘못된 패턴: 에러와 입력창의 연결이 없음 -->
<input id="email" type="email" />
<p class="error">이메일 형식이 잘못됐습니다.</p>

<!-- 올바른 패턴: aria-describedby로 연결 -->
<input
  id="email"
  type="email"
  aria-invalid="true"
  aria-describedby="email-error"
/>
<p id="email-error" role="alert">이메일 형식이 잘못됐습니다.</p>
```

### 시나리오 3: 모바일 키보드가 엉뚱하게 뜰 때

```html
<!-- type 속성이 모바일 키보드를 결정합니다 -->
<input type="email"  inputmode="email" />    <!-- @ 포함 이메일 키보드 -->
<input type="tel"   inputmode="numeric" />  <!-- 숫자 키보드 -->
<input type="url"   inputmode="url" />      <!-- URL 키보드 -->
<input type="search" />                     <!-- 검색 키보드 (Enter = 검색) -->
```

## 실무 점검 루프

1. **키보드 경로를 점검합니다.** `Tab`, `Shift+Tab`, `Enter`만으로 폼을 끝까지 완료해 봅니다.
2. **에러 위치를 점검합니다.** 잘못된 값을 넣었을 때 메시지가 폼 맨 위가 아니라 해당 필드 옆에 바로 붙는지 확인합니다.
3. **제출 상태를 점검합니다.** 비활성 버튼, 로딩 텍스트, 서버 에러 표시가 같은 상태 전환을 반영하는지 봅니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|---|---|---|
| 비밀번호를 한 번만 입력받음 | 오타로 인한 가입 실패, 사용자가 원인 모름 | 비밀번호 확인 필드 항상 추가 |
| 에러를 제출 후에만 표시 | 모든 필드를 다시 훑어야 함 | `onBlur`마다 touched 업데이트, 실시간 검증 |
| 기술적 에러 메시지 그대로 노출 | "Schema validation failed"는 사용자에게 무의미 | 사람이 이해할 수 있는 친절한 메시지로 변환 |
| `<label>` 없이 `placeholder`만 사용 | 스크린 리더가 필드 목적 파악 불가 | 모든 입력에 연결된 `<label>` 필수 |
| 모바일 `type` 속성 미지정 | 이메일 필드에 일반 키보드 → UX 저하 | `type="email"`, `type="tel"` 등 적절한 타입 지정 |
| 서버 에러를 화면에 표시 안 함 | 폼 제출 후 아무 반응 없음, 사용자 혼란 | 서버 오류도 사용자 수준 메시지로 표시 |

## 실무에서는 이렇게 보입니다

대부분의 React 앱은 React Hook Form과 Zod 조합을 사용합니다. 상태 관리, 검증, 제출, 에러 표시를 선언적으로 묶을 수 있기 때문입니다.

```jsx
// 실무 팀의 재사용 가능한 폼 필드 컴포넌트
function FormField({ label, name, register, error, type = "text", ...props }) {
  return (
    <div className="form-field">
      <label htmlFor={name}>{label}</label>
      <input
        id={name}
        type={type}
        {...register(name)}
        aria-invalid={!!error}
        aria-describedby={error ? `${name}-error` : undefined}
        {...props}
      />
      {error && (
        <p id={`${name}-error`} className="form-field__error" role="alert">
          {error.message}
        </p>
      )}
    </div>
  );
}

// 사용
<FormField
  label="이메일"
  name="email"
  type="email"
  register={register}
  error={errors.email}
  autoComplete="email"
/>
```

## 시니어 엔지니어는 이렇게 생각합니다

- 폼은 대화이므로 매 단계마다 피드백을 줍니다.
- 프론트엔드는 UX를 위해, 백엔드는 보안을 위해 각각 검증합니다.
- 에러 메시지는 친절하고 행동 가능해야 합니다.
- 전체 폼은 키보드만으로도 완주 가능해야 합니다.
- 자동완성과 모바일 키보드 타입은 옵션이 아니라 기본값입니다.

## 운영 체크리스트

- [ ] controlled input을 사용할 수 있습니다.
- [ ] inline 에러 메시지를 보여 줄 수 있습니다.
- [ ] 모든 입력에 `<label>`과 적절한 연결을 추가할 수 있습니다.
- [ ] `aria-invalid`와 `aria-describedby`의 역할을 설명할 수 있습니다.
- [ ] Zod나 Yup 같은 스키마 검증기를 사용해 봤습니다.
- [ ] 키보드만으로 폼 전체를 완료할 수 있는지 확인했습니다.

## 연습 문제

1. 이메일, 비밀번호, 비밀번호 확인 필드를 가진 가입 폼을 만들어 보세요.
2. 모든 필드에 inline 검증과 친절한 에러 메시지를 추가해 보세요.
3. 키보드만으로 폼을 끝까지 작성하고 제출할 수 있는지 직접 확인해 보세요.
4. React Hook Form과 Zod로 같은 폼을 리팩터링하고 코드 줄 수를 비교해 보세요.

## 정리 및 다음 단계

폼은 사용자와 가장 길게 만나는 인터페이스입니다. 입력을 안전하게 받고 친절하게 안내하는 감각이 있어야 제품 전체가 안정적으로 느껴집니다.

다음 글에서는 이 폼과 화면 전체에 일관된 모양을 부여하는 스타일링과 디자인 시스템을 봅니다.

## 처음 질문으로 돌아가기

- **controlled input과 uncontrolled input은 어떤 차이가 있을까요?**
  - controlled는 React state가 입력값을 관리합니다. uncontrolled는 DOM이 관리하고 필요할 때 `ref`로 읽습니다. 검증과 실시간 피드백이 필요하면 controlled가 훨씬 다루기 쉽습니다.
- **유효성 검사는 형식, 비즈니스 규칙, 서버 검증으로 왜 나눠 생각해야 할까요?**
  - 이메일 형식은 프론트에서 즉시 검사, 중복 이메일 여부는 서버에서만 알 수 있기 때문입니다. 층위를 구분해야 각 검증이 적절한 위치에 구현됩니다.
- **에러 메시지는 어디에, 언제 보여 주는 편이 가장 친절할까요?**
  - 해당 필드 바로 아래에, 필드를 벗어나거나(`onBlur`) 입력을 시작한 후에 보여 주는 것이 가장 자연스럽습니다. 아직 건드리지 않은 필드에 에러를 미리 보여 주면 사용자가 부담을 느낍니다.

<!-- toc:begin -->
## 시리즈 목차

- [Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML과 CSS 기본](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript 기본](./03-javascript-basics.md)
- [Frontend Development 101 (4/10): 컴포넌트와 상태](./04-components-and-state.md)
- [Frontend Development 101 (5/10): 라우팅과 페이지](./05-routing-and-pages.md)
- [Frontend Development 101 (6/10): API 호출과 비동기](./06-api-calls-and-async.md)
- **Frontend Development 101 (7/10): 폼과 유효성 검사 (현재 글)**
- [Frontend Development 101 (8/10): 스타일링과 디자인 시스템](./08-styling-and-design-system.md)
- [Frontend Development 101 (9/10): 빌드 도구와 번들링](./09-build-tools-and-bundling.md)
- [작은 프론트엔드 앱 만들기](./10-building-a-small-frontend-app.md)

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
