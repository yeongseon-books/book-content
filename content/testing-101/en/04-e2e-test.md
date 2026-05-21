---
series: testing-101
episode: 4
title: "Testing 101 (4/10): E2E Test"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Testing
  - E2E
  - Playwright
  - Browser
  - Automation
seo_description: Definition of end-to-end tests that verify user scenarios in a browser, plus a Playwright walkthrough for beginners.
last_reviewed: '2026-05-04'
---

# Testing 101 (4/10): E2E Test

It is entirely possible for the UI team to say the page renders, the backend team to say the API returns 200, and the database team to say persistence is healthy—while users still cannot log in. End-to-end tests exist for that exact gap between local confidence and real user success.

They are expensive because they run through the most surface area: browser, frontend, backend, and storage. That cost is precisely why they need to be selective and operationally disciplined.

This is post 4 in the Testing 101 series. Here we walk through the role of E2E tests, build a first Playwright scenario, and focus on the maintenance habits that keep browser tests from turning flaky and slow.

> E2E is the user’s final contract with your system. Treat it as a scarce but high-value signal.


![testing 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/04/04-01-concept-at-a-glance.en.png)
*testing 101 chapter 4 flow overview*
> E2E tests prove that the user can actually complete the flow, not just that the code says the flow should work.

## Questions to Keep in Mind

- What boundary should you inspect first when applying E2E Test?
- Which signal should the example or diagram make visible for E2E Test?
- What failure should be prevented first when E2E Test reaches a real system?

## What You Will Learn

- The definition of *E2E* and how it relates to other tests
- Writing *your first scenario* with Playwright
- Causes of *flaky* tests and how to fight them
- The *right number* of E2E tests
- Five common pitfalls

## Why It Matters

A passing E2E test means *frontend, backend, and DB work together*. It is the *most realistic* signal — and the *most expensive*. So you keep them *few and focused on the core*.

> E2E is the *user's point of view*.

## Concept at a Glance
An E2E test navigates a real browser through a complete user scenario—signing up, logging in, making a payment, or searching—and confirms that every screen, navigation path, and API interaction works end-to-end from the user's perspective.
## Key Terms

- **E2E (end-to-end)**: the full flow from *user start to result*.
- **Headless browser**: a browser that runs without a visible window (used in CI).
- **Selector**: an expression that *targets an element* (text, role, data-testid, ...).
- **Flaky test**: a test that breaks *intermittently*.
- **Page object**: an object that *encapsulates actions* per screen.

## Before/After

**Before (manual regression)**

```text
- Five people click for an hour before each release
- A *checkout bug* still ships and surfaces in production
```

**After (five E2E tests)**

```text
- Signup, login, payment, search, logout scenarios are automated
- Results in under five minutes from CI
```

## Hands-on: Playwright in Five Steps

### Step 1 — Install

```bash
pip install pytest-playwright
playwright install
```

### Step 2 — First scenario

```python
# tests/e2e/test_login.py
def test_login_flow(page):
    page.goto("https://example.com/login")
    page.get_by_label("Email").fill("a@b.com")
    page.get_by_label("Password").fill("secret")
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_url("**/dashboard")
    assert page.get_by_text("Welcome").is_visible()
```

### Step 3 — Stable selectors

```python
# Recommended: role + name
page.get_by_role("button", name="Sign in")
# Or data-testid
page.get_by_test_id("submit-login")
# Discouraged: volatile CSS classes
page.locator(".btn-primary-3xl")
```

### Step 4 — Waiting (no sleep)

```python
# Bad
import time; time.sleep(3)
# Good
page.wait_for_url("**/dashboard")
page.wait_for_selector("text=Welcome")
```

### Step 5 — Page object

```python
class LoginPage:
    def __init__(self, page):
        self.page = page
    def open(self):
        self.page.goto("https://example.com/login")
    def login(self, email, pw):
        self.page.get_by_label("Email").fill(email)
        self.page.get_by_label("Password").fill(pw)
        self.page.get_by_role("button", name="Sign in").click()

def test_login_with_page_object(page):
    LoginPage(page).open(); LoginPage(page).login("a@b.com", "secret")
    assert page.get_by_text("Welcome").is_visible()
```

## What to Notice in This Code

- *Role/text* selectors *survive design changes*.
- Conditional waits like `wait_for_url` *replace sleeps*.
- Page objects let you *reuse scenarios*.

## Five Common Mistakes

1. **Trying to cover *every screen* with E2E.** A 5-minute suite turns into *an hour*.
2. **Waiting with `time.sleep`.** Cause #1 of *flakiness*.
3. **Calling *real payments* in production.** Always use *staging/sandbox*.
4. **Using *CSS class* selectors.** They *break with every UI change*.
5. **Scenarios *depending on each other*.** Isolation is what enables *re-runs*.

## Verification Points

1. Run the same login scenario three times in a row. A scenario that passes once but fails on repeat is already telling you something about selector or wait instability.
2. Compare a `sleep`-based version with a `wait_for_url` or locator-based wait. The flakiness difference usually shows up immediately.
3. Confirm the scenario still makes sense with staging or sandbox credentials. If it depends on live production data, it is not safely repeatable.

**Expected output:** the core scenario should behave the same across repeated runs, and failures should tell you exactly which screen condition was never reached.

## Failure Signals and First Checks

- If CSS-class selectors break often, switch to role-based locators or `data-testid`.
- If scenarios share login state, reruns and parallel execution will become fragile fast.
- If PR feedback is too slow, keep only critical paths in the default E2E tier and move the heavier flows elsewhere.

## How This Shows Up in Production

Most teams keep only *5\~20 critical scenarios* as E2E. *Playwright/Cypress* are standard, and some add *visual regression* tests.

## How a Senior Engineer Thinks

- Keeps E2E *few, expensive, and stable*.
- Defaults to *role-based selectors*.
- *Quarantines flaky tests immediately*.
- Ships small PRs at the *scenario level*.
- Sees the value of E2E as preventing *"users can't use it"* incidents.

## Checklist

- [ ] You wrote *one Playwright scenario*.
- [ ] You used *role/text/test-id* selectors.
- [ ] You replaced `sleep` with *conditional waits*.
- [ ] Scenarios run *independently*.

## Practice Problems

1. Add a *failure scenario* (wrong password) for the login above.
2. Compare *three or more* selector types and note which is most stable.
3. Intentionally use `sleep` and observe *why it breaks*.

## Wrap-up and Next Steps

E2E is the *most realistic* signal. From the next post we cover *test doubles* for handling external dependencies.

## Answering the Opening Questions

- **What boundary should you inspect first when applying E2E Test?**
  - The article treats E2E Test as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for E2E Test?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when E2E Test reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Testing 101 (1/10): What Is Testing?](./01-what-is-testing.md)
- [Testing 101 (2/10): Unit Test](./02-unit-test.md)
- [Testing 101 (3/10): Integration Test](./03-integration-test.md)
- **E2E Test (current)**
- Test Double (upcoming)
- Mock and Stub (upcoming)
- Test Coverage (upcoming)
- Regression Test (upcoming)
- Running Tests in CI (upcoming)
- Building a Test Strategy (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [Playwright for Python](https://playwright.dev/python/)
- [Playwright locators guide](https://playwright.dev/python/docs/locators)
- [Playwright auto-waiting](https://playwright.dev/python/docs/actionability)

### Practical Reading
- [Martin Fowler — Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html)
- [Google Testing Blog — Flaky Tests](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)

Tags: Testing, E2E, Playwright, Browser, Automation
