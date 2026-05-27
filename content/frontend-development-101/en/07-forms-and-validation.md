---
series: frontend-development-101
episode: 7
title: "Frontend Development 101 (7/10): Forms and Validation"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Frontend
  - Forms
  - Validation
  - UX
  - React
seo_description: Controlled inputs, validation, error messages, and accessibility — handling user input safely and kindly.
last_reviewed: '2026-05-04'
---

# Frontend Development 101 (7/10): Forms and Validation

Forms are where products have their longest conversation with users. Sign-up, login, payment, search, and settings changes all pass through fields, buttons, and validation messages. When that conversation is awkward, users feel it immediately.

This is the 7th post in the Frontend Development 101 series. Here we treat a form as a guided interaction rather than as a bag of inputs. A good form helps while the user is typing, shows errors in plain language, and makes correction easier than failure.


![frontend development 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/frontend-development-101/07/07-01-concept-at-a-glance.en.png)
*frontend development 101 chapter 7 flow overview*

## Questions to Keep in Mind

- When should a form validate while the user types, and when should it wait until submit?
- How do accessibility signals such as labels, focus order, and `aria-invalid` belong inside form validation?
- Why must frontend validation and backend validation both exist in the same product flow?

## What You Will Learn

- Controlled vs uncontrolled inputs
- Three layers of validation (format, business rule, server)
- *Where and when* to show error messages
- Accessibility and keyboard usability
- The role of form libraries (React Hook Form, Zod)

## Why It Matters

Forms drive *conversion*. Sign-up, payment, search — all forms. *Slightly awkward* forms cause users to leave. Forms are the *UX exam* of the frontend.

> Great forms *ask less*, *catch typos early*, and *submit fast*.

## Key Terms

- **Controlled input**: value lives in *React state*.
- **Uncontrolled input**: value lives in the *DOM*.
- **Schema validation**: declarative validation with libraries like Zod or Yup.
- **Inline error**: an error shown *next to the field*.
- **`aria-invalid`**: ARIA attribute telling screen readers *the field is invalid*.

## From Last-Minute Validation to Guided Input

A form can either wait until submit and punish the user with a late error, or it can guide the user toward a valid answer while they type. The second style is not just nicer. It reduces retries, lowers abandonment, and makes accessibility easier to design deliberately.

**Validation appears only after submit**

```javascript
form.onsubmit = () => {
  if (email.value === "") alert("Please enter an email");
};
```

**Validation gives immediate, local feedback**

```jsx
{!isEmail(email) && <p className="error">That doesn't look like an email</p>}
```

The better pattern still needs restraint. Good forms do not scream on the first keystroke; they reveal feedback when it becomes useful and keep the correction path obvious.

## Hands-on: A Sign-up Form in Five Steps

### Step 1 — Controlled input

```jsx
function Signup() {
  const [email, setEmail] = useState("");
  return <input value={email} onChange={e => setEmail(e.target.value)} />;
}
```

### Step 2 — Format check

```jsx
const isValidEmail = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
```

### Step 3 — Inline error

```jsx
<input
  value={email}
  onChange={e => setEmail(e.target.value)}
  aria-invalid={!isValidEmail}
/>
{!isValidEmail && email && <p className="error">That doesn't look like an email</p>}
```

### Step 4 — Disable submit while invalid

```jsx
<button disabled={!isValidEmail || submitting}>
  {submitting ? "Submitting..." : "Sign up"}
</button>
```

### Step 5 — Schema with Zod

```jsx
import { z } from "zod";

const SignupSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

const result = SignupSchema.safeParse({ email, password });
if (!result.success) showErrors(result.error.format());
```

## Verification

- Type an invalid email and confirm that the inline error appears before submit; then type a valid one and verify that the submit button becomes usable.
- Tab through the form using only the keyboard and confirm that labels, focus order, and `aria-invalid` all communicate the same state.

## If It Fails, Check This First

- If errors never clear, check the controlled state update path and the exact timing of your format validation.
- If assistive feedback is weak, verify the `label`, `id`, and `aria-describedby` connections first.

## Practical Debug Loop

Good form debugging checks visual feedback, accessibility feedback, and submission behavior as one conversation.

1. **Keyboard path** - complete the form with `Tab`, `Shift+Tab`, and `Enter` only.
2. **Error clarity** - trigger one invalid state and confirm the message appears next to the right field, not only at the top of the form.
3. **Submission contract** - verify that disabled buttons, loading text, and server-error handling all match the same state transition.

```html
<input aria-invalid="true" aria-describedby="email-error" />
<p id="email-error">That doesn't look like an email.</p>
```

Expected outcome: a keyboard-only user, a screen-reader user, and a mouse user all receive the same validation signal at the same point in the flow. If those experiences diverge, the form is not truly finished yet.

## What to Notice in This Code

- Validation happens *while the user types*.
- `aria-invalid` carries *the same information* to screen reader users.
- One Zod schema unifies *frontend and backend* validation.

## Five Common Mistakes

1. **Asking for the password *only once*.** A typo causes the entire signup to fail.
2. **Showing errors *only after submit*.** Users must re-scan *every field*.
3. **Technical error text.** "Schema validation failed" means *nothing* to the user.
4. **Missing `<label>`.** Screen readers don't know *which input* this is.
5. **No mobile keyboard hint.** An email field opens the *letters keyboard*.

## How This Shows Up in Production

Most React apps use *React Hook Form + Zod*. State, validation, submission, and error display are bundled *declaratively*. Hand-rolled `useState` forms vanish *after the learning phase*.

## How a Senior Engineer Thinks

- A form is *a conversation* — give *feedback* at every step.
- Validate on *both* frontend (UX) and backend (security).
- Errors must be *friendly and actionable*.
- The *whole form* must be reachable by *keyboard alone*.
- Autocomplete and mobile keyboard `type` are *defaults*, not optional.

## Checklist

- [ ] You can use a controlled input.
- [ ] You display inline errors.
- [ ] You attach `<label>` and `for` to every input.
- [ ] You know `aria-invalid` and `aria-describedby`.
- [ ] You have used a schema validator like Zod or Yup.

## Practice Problems

1. Build a signup form with email, password, and password-confirm fields.
2. Add inline validation and friendly error messages to every field.
3. Verify the form can be filled and submitted using *only the keyboard*.

## Wrap-up and Next Steps

Forms are *the longest conversation with the user*. Next, we look at how the form — and the rest of the screen — gets *its appearance* via styling and design systems.

## Answering the Opening Questions

- **When should a form validate while the user types, and when should it wait until submit?**
  - Format-level checks such as email shape or password length usually help while typing, because they let the user recover early. Final business-rule or server validation still belongs at submit time because only the server knows the full truth.
- **How do accessibility signals such as labels, focus order, and `aria-invalid` belong inside form validation?**
  - Validation is not complete unless keyboard users and screen-reader users receive the same signal as sighted mouse users. Labels, focus movement, and ARIA attributes are part of the validation experience, not extra polish.
- **Why must frontend validation and backend validation both exist in the same product flow?**
  - Frontend validation protects the user experience by catching mistakes early, while backend validation protects correctness and security. Removing either one leaves a real gap in the system.

<!-- toc:begin -->
## In this series

- [Frontend Development 101 (1/10): What Is Frontend Development?](./01-what-is-frontend-development.md)
- [Frontend Development 101 (2/10): HTML and CSS Basics](./02-html-and-css-basics.md)
- [Frontend Development 101 (3/10): JavaScript Basics](./03-javascript-basics.md)
- [Frontend Development 101 (4/10): Components and State](./04-components-and-state.md)
- [Frontend Development 101 (5/10): Routing and Pages](./05-routing-and-pages.md)
- [Frontend Development 101 (6/10): API Calls and Async](./06-api-calls-and-async.md)
- **Forms and Validation (current)**
- Styling and Design Systems (upcoming)
- Build Tools and Bundling (upcoming)
- Building a Small Frontend App (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [React Hook Form documentation](https://react-hook-form.com/)
- [Zod documentation](https://zod.dev/)
- [MDN: Client-side form validation](https://developer.mozilla.org/en-US/docs/Learn/Forms/Form_validation)

### Verification and Further Reading
- [WAI: Forms tutorial](https://www.w3.org/WAI/tutorials/forms/)
- [MDN: ARIA aria-invalid](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-invalid)

Tags: Frontend, Forms, Validation, UX, React
