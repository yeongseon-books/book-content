---
series: testing-101
episode: 4
title: "Testing 101 (4/10): E2E 테스트"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Testing
  - E2E
  - Playwright
  - Browser
  - Automation
seo_description: 사용자 시나리오를 브라우저로 검증하는 E2E 테스트의 정의와 Playwright 실습 입문.
last_reviewed: '2026-05-12'
---

# Testing 101 (4/10): E2E 테스트

로그인 화면이 잘 보이고, 버튼도 눌리고, API도 정상이라고 각자 확인했는데 실제 사용자는 로그인조차 못 하는 상황이 생길 수 있습니다. 화면과 백엔드, 데이터베이스가 각각 정상이어도 끝에서 끝까지 이어지는 사용자 흐름은 다른 문제를 드러내기 때문입니다.

E2E 테스트는 그 흐름을 사용자의 시선에서 다시 확인합니다. 비용이 가장 큰 대신, 실제 사고와 가장 가까운 신호를 줍니다.

이 글은 Testing 101 시리즈의 네 번째 글입니다. 여기서는 E2E 테스트의 역할, Playwright로 첫 시나리오를 만드는 방법, 플래키 테스트를 줄이는 운영 원칙, 그리고 E2E 테스트를 언제 쓰지 말아야 하는지도 정리하겠습니다.

![Testing 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/04/04-01-diagram.ko.png)
*Testing 101 4장 흐름 개요*
> E2E 테스트는 현실에 가까운 신호를 줍니다. 따라서 핵심 사용자 여정만 선택적으로 검증합니다.

## 이 글에서 다룰 문제

- E2E 테스트는 다른 테스트 계층과 어떻게 다를까요?
- 브라우저를 직접 띄우는 테스트는 무엇을 검증할까요?
- Playwright로 첫 시나리오를 어떻게 작성할까요?
- 플래키 테스트를 줄이는 원칙은 무엇일까요?
- E2E를 쓰지 말아야 할 상황은 언제일까요?

E2E 테스트가 통과했다는 말은 프론트엔드, 백엔드, 데이터베이스가 함께 동작했다는 뜻입니다. 그래서 팀은 E2E 결과를 강한 신호로 받아들입니다. 다만 강한 신호인 만큼 값도 비쌉니다. 실행 시간이 길고, 환경 영향을 받기 쉬우며, 잘못 설계하면 금방 불안정해집니다.

그래서 E2E 테스트는 많을수록 좋은 계층이 아닙니다. 핵심 시나리오를 적게 두고 안정적으로 운영하는 편이 낫습니다.

## 한눈에 보는 구조

브라우저에서 시작한 동작이 화면, API, 저장소까지 이어지는 전체 흐름을 검증합니다. E2E 테스트는 개별 함수의 옳고 그름보다 사용자 시나리오의 성공 여부를 봅니다.

| 용어 | 의미 |
|------|------|
| E2E(end-to-end) | 사용자의 시작 행동부터 최종 결과까지 이어지는 흐름 |
| 헤드리스 브라우저 | 화면을 띄우지 않고 실행되는 브라우저. CI에서 자주 씁니다 |
| 셀렉터(selector) | 화면 요소를 찾는 표현 |
| 플래키 테스트 | 같은 코드인데도 어떤 날은 통과하고 어떤 날은 실패하는 불안정한 테스트 |
| 페이지 객체(page object) | 화면별 동작을 객체로 감싼 재사용 패턴 |

## 수동 회귀 확인 vs 핵심 시나리오 자동화

**수동 회귀 확인 중심**

```text
- 배포 전마다 여러 사람이 한 시간씩 직접 클릭한다
- 그래도 결제 화면 버그가 운영에서 처음 드러난다
- 재현 시도에 추가로 30분 소비
```

**핵심 시나리오 자동화 후**

```text
- 회원가입, 로그인, 결제, 검색, 로그아웃 시나리오를 자동화
- CI에서 8분 안에 결과를 확인
- 배포 전 결제 흐름 버그 차단
```

사람이 반복해서 눌러 보는 작업은 결국 지칩니다. E2E 테스트는 이 반복을 코드로 바꿔 놓습니다. 다만 모든 화면을 다 올리려 하지 말고, 사용자 피해가 큰 흐름부터 고르는 편이 좋습니다.

## E2E 도구 비교

| 기준 | Playwright | Selenium | Cypress |
|---|---|---|---|
| 언어 지원 | Python, JS, Java, .NET | Python, Java, C#, Ruby, JS | JavaScript/TypeScript 전용 |
| 설치 복잡도 | 낮음 (`playwright install`) | 높음 (WebDriver 별도 관리) | 중간 (`npm install`) |
| 실행 속도 | 빠름 | 느림 | 중간 |
| 헤드리스 | 기본 지원 | 지원 | 지원 |
| 자동 대기 | 기본 지원 | 수동 처리 | 일부 지원 |
| 병렬 실행 | 지원 | 제한적 | 유료 (Cypress Cloud) |
| 스크린샷 기록 | 지원 | 수동 처리 | 자동 |

Python 백엔드 팀에서는 Playwright를 가장 많이 선택합니다. Playwright는 빠르고, 설치가 간단하며, Python을 직접 지원하므로 백엔드 테스트와 같은 환경에서 돌릴 수 있습니다.

## 다섯 단계로 Playwright 시작하기

### 1단계 — 설치

```bash
pip install pytest-playwright
playwright install chromium
```

### 2단계 — 첫 시나리오 작성

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

### 3단계 — 안정적인 셀렉터 선택

```python
# 권장: role + name (UI가 바뀌어도 버팀)
page.get_by_role("button", name="Sign in")
page.get_by_label("Email")

# 권장: data-testid (개발팀이 직접 지정)
page.get_by_test_id("submit-login")

# 비권장: 자주 바뀌는 CSS 클래스
page.locator(".btn-primary-3xl")
page.locator("#root > div > form > button:nth-child(2)")
```

### 4단계 — 시간 대기 대신 조건 대기

```python
# 나쁨: 고정 시간 대기 (플래키 원인)
import time
time.sleep(3)

# 좋음: 조건이 만족될 때까지 대기
page.wait_for_url("**/dashboard")
page.wait_for_selector("text=Welcome")
page.get_by_text("결제 완료").wait_for()
```

### 5단계 — 페이지 객체로 재사용성 높이기

```python
class LoginPage:
    def __init__(self, page):
        self.page = page

    def open(self):
        self.page.goto("https://example.com/login")
        return self

    def login(self, email: str, password: str):
        self.page.get_by_label("Email").fill(email)
        self.page.get_by_label("Password").fill(password)
        self.page.get_by_role("button", name="Sign in").click()
        return self

    def is_on_dashboard(self) -> bool:
        return "dashboard" in self.page.url

def test_login_with_page_object(page):
    login = LoginPage(page)
    login.open().login("a@b.com", "secret")
    assert login.is_on_dashboard()
```

## 회원가입부터 로그인까지 전체 흐름 테스트

```python
# tests/e2e/test_user_flow.py
def test_signup_and_first_login(page):
    # 회원가입
    page.goto("https://example.com/signup")
    page.get_by_label("Email").fill("new@user.com")
    page.get_by_label("Password").fill("securePass123")
    page.get_by_role("button", name="Sign up").click()
    page.wait_for_url("**/welcome")

    # 로그아웃 후 다시 로그인
    page.get_by_role("button", name="Log out").click()
    page.wait_for_url("**/login")
    page.get_by_label("Email").fill("new@user.com")
    page.get_by_label("Password").fill("securePass123")
    page.get_by_role("button", name="Sign in").click()

    # 대시보드 진입 확인
    page.wait_for_url("**/dashboard")
    assert page.get_by_text("new@user.com").is_visible()
```

하나의 테스트 안에 회원가입부터 로그인까지 전체 흐름을 넣었습니다. 화면 전환, 상태 관리, 인증 흐름을 한 번에 검증할 수 있습니다. 다만 지나치게 길면 실패 지점을 찾기 어려우므로, 경로당 테스트 하나를 원칙으로 삼는 편이 좋습니다.

## 플래키 테스트 관리

E2E 테스트는 네트워크, 렌더링 타이밍, 비동기 요청 등 여러 변수에 영향을 받아 불안정해지기 쉽습니다. 플래키 테스트는 신뢰를 깨고, 실패를 무시하게 만듭니다.

**재시도 정책**

```bash
# pytest-rerunfailures 사용
pip install pytest-rerunfailures
pytest tests/e2e --reruns 2 --reruns-delay 1
```

재시도는 불안정을 감추는 임시 조치입니다. 재시도를 걸어도 계속 깨지면 셀렉터나 대기 조건을 먼저 고쳐야 합니다.

**실패 시 스크린샷 기록**

```python
# tests/conftest.py
import pytest

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            page.screenshot(path=f"screenshots/{item.name}.png")
```

실패 시 스크린샷을 남기면 CI 로그만으로 원인을 찾는 것보다 훨씬 빠르게 디버깅할 수 있습니다.

**네트워크 대기 전략**

```python
# 모든 네트워크 요청이 끝날 때까지 대기 (조심해서 사용)
page.goto("https://example.com", wait_until="networkidle")

# 특정 요소가 나타날 때까지 대기 (더 안정적)
page.get_by_role("heading", name="Dashboard").wait_for()
```

`networkidle`은 긴 폴링이 있는 경우 타임아웃이 발생할 수 있습니다. 특정 요소를 기다리는 편이 더 안정적입니다.

## E2E를 쓰지 말아야 할 때

E2E 테스트는 강력하지만, 모든 경우에 적합하지는 않습니다.

**비즈니스 로직 검증에는 단위 테스트를 쓰세요**

할인율 계산, 포인트 적립, 재고 차감 같은 내부 로직을 E2E로 검증하려면 화면을 여러 번 클릭해야 하고, 실패 원인을 찾기 어렵습니다.

**에지 케이스 조합에는 단위 테스트를 쓰세요**

비밀번호 유효성 규칙 10가지를 모두 E2E로 테스트하면 10개의 브라우저 시나리오가 생깁니다. 입력 검증은 단위 테스트로, 화면 표시만 E2E 한 두 개로 커버하는 편이 현명합니다.

**외부 시스템 통합은 목 서버로 대체하세요**

결제 게이트웨이, SMS 발송처럼 비용이 발생하거나 부작용이 있는 외부 시스템은 E2E에서 목 서버로 교체해야 합니다.

**API만 제공하는 백엔드는 통합 테스트로 충분합니다**

프론트엔드가 없는 API 서비스는 E2E가 필요 없습니다. HTTP 계약을 통합 테스트로 검증하면 빠르고 안정적입니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
|------|------|------------|
| 모든 화면을 E2E로 덮으려 함 | CI 30분 이상, 팀이 테스트를 건너뜀 | 핵심 경로 5~20개만 E2E로 유지 |
| `time.sleep`으로 타이밍 문제를 해결 | 네트워크 속도에 따라 간헐적 실패 | 조건부 대기(`wait_for_url`, `wait_for_selector`) 사용 |
| CSS 클래스로 셀렉터를 만듦 | UI 개편 때마다 테스트 전면 수정 | role, label, test-id 기반 셀렉터 사용 |
| 시나리오 간 로그인 상태 공유 | 병렬 실행이나 재실행 시 순서 의존 오류 | 각 시나리오를 독립적으로 격리 |
| 운영 계정과 실제 결제 API 사용 | 테스트 비용 발생, 실제 이메일 발송 | 스테이징 환경 또는 샌드박스 계정 사용 |
| 플래키 테스트를 방치 | 실패를 무시하는 문화, 경고 신호 손실 | 플래키 테스트 목록 추적, 분기마다 정리 |

## 직접 검증해 볼 것

1. 같은 로그인 시나리오를 세 번 연속 실행해 봅니다. 한 번만 통과하고 다시 깨진다면 셀렉터나 대기 조건이 불안정한 것입니다.
2. `sleep`을 넣은 버전과 `wait_for_url`을 쓴 버전의 성공률과 실행 시간을 비교해 봅니다.
3. 실제 운영 계정 대신 스테이징 계정이나 샌드박스 계정을 써도 시나리오 의미가 유지되는지 확인합니다.

**예상 결과:** 핵심 시나리오는 반복 실행에서도 같은 결과를 내고, 실패 시에는 어느 화면 요소를 기다리다 멈췄는지 로그에서 바로 읽혀야 합니다.

## CI에서 E2E 테스트 실행하기

```yaml
name: e2e-test
on:
  push:
    branches: [main]   # PR이 아닌 main 머지 후 실행

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
      - run: pip install -r requirements-dev.txt
      - run: playwright install --with-deps chromium
      - name: Run E2E tests
        run: pytest tests/e2e -q --reruns 1
        env:
          BASE_URL: https://staging.example.com
      - name: Upload screenshots on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: e2e-screenshots
          path: screenshots/
```

E2E 테스트는 PR마다 실행하지 않고 main 브랜치 머지 후 또는 야간 배치로 실행하는 팀이 많습니다.

## 운영 관점에서 생각하기

대부분의 팀은 E2E 테스트를 5개에서 20개 사이의 핵심 시나리오로 제한합니다. 로그인, 회원가입, 결제, 검색처럼 서비스 가치가 직접 걸린 경로만 남기고 나머지는 단위 테스트나 통합 테스트로 내려 보냅니다.

경험 많은 엔지니어는 E2E의 역할을 분명히 압니다. E2E는 모든 것을 설명하는 계층이 아니라, 사용자가 실제로 못 쓰게 되는 사고를 막는 마지막 신호입니다. 그래서 비싸고 드문 계층이어야 합니다.

## 운영 체크리스트

- [ ] Playwright로 시나리오 하나를 작성했습니다.
- [ ] role, text, test-id 기반 셀렉터를 사용했습니다.
- [ ] `sleep` 대신 조건부 대기를 썼습니다.
- [ ] 각 시나리오가 서로 독립적으로 실행됩니다.
- [ ] 실패 시 스크린샷이 저장됩니다.
- [ ] 스테이징 또는 샌드박스 환경에서 실행합니다.

## 연습 문제

1. 로그인 실패 시나리오(잘못된 비밀번호)를 하나 추가해 보세요.
2. 셀렉터 세 종류(CSS 클래스, role, test-id)를 비교하고 무엇이 가장 안정적인지 기록해 보세요.
3. `sleep`을 일부러 넣고 왜 불안정해지는지 관찰해 보세요.
4. `LoginPage` 페이지 객체를 만들고 두 개의 시나리오에서 재사용해 보세요.

## 정리

E2E 테스트는 가장 현실에 가까운 품질 신호입니다. 다만 현실에 가까운 만큼 유지비도 큽니다. 적게 두고, 핵심 경로에 집중하고, 안정적으로 운영하는 것이 좋습니다. 다음 글에서는 외부 의존을 다룰 때 자주 쓰는 테스트 더블을 봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Testing 101 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [Testing 101 (2/10): 단위 테스트](./02-unit-test.md)
- [Testing 101 (3/10): 통합 테스트](./03-integration-test.md)
- **Testing 101 (4/10): E2E 테스트 (현재 글)**
- [Testing 101 (5/10): 테스트 더블](./05-test-double.md)
- [Testing 101 (6/10): Mock과 Stub](./06-mock-and-stub.md)
- [Testing 101 (7/10): 테스트 커버리지](./07-test-coverage.md)
- [Testing 101 (8/10): 회귀 테스트](./08-regression-test.md)
- [Testing 101 (9/10): CI에서 테스트 실행하기](./09-tests-in-ci.md)
- [테스트 전략 세우기](./10-test-strategy.md)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소(book-examples): https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko
### 공식 문서
- [Playwright for Python](https://playwright.dev/python/)
- [Playwright locators guide](https://playwright.dev/python/docs/locators)
- [Playwright auto-waiting](https://playwright.dev/python/docs/actionability)

### 실무 참고
- [Martin Fowler — Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html)
- [Google Testing Blog — Flaky Tests](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)

Tags: Testing, E2E, Playwright, Browser, Automation
