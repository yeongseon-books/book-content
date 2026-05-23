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

이 글은 Testing 101 시리즈의 네 번째 글입니다. 여기서는 E2E 테스트의 역할, Playwright로 첫 시나리오를 만드는 방법, 그리고 플래키(flaky)한 테스트를 줄이는 운영 원칙을 정리하겠습니다.

![Testing 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/04/04-01-diagram.ko.png)
*Testing 101 4장 흐름 개요*
> E2E 테스트는 현실적인 지만 느린 신호입니다. 따라서 시간 효율을 위해 주요 사용자 여정만 선택적으로 검증합니다.

## 먼저 던지는 질문

- E2E 테스트는 다른 테스트 계층과 어떻게 다를까요?
- 브라우저를 직접 띄우는 테스트는 무엇을 검증할까요?
- Playwright로 첫 시나리오를 어떻게 작성할까요?

## 왜 중요한가

E2E 테스트가 통과했다는 말은 프론트엔드, 백엔드, 데이터베이스가 함께 동작했다는 뜻입니다. 그래서 팀은 E2E 결과를 강한 신호로 받아들입니다. 다만 강한 신호인 만큼 값도 비쌉니다. 실행 시간이 길고, 환경 영향을 받기 쉬우며, 잘못 설계하면 금방 불안정해집니다.

그래서 E2E 테스트는 많을수록 좋은 계층이 아닙니다. 핵심 시나리오를 적게 두고 안정적으로 운영하는 편이 낫습니다. 로그인, 회원가입, 결제 같은 치명적인 경로를 보호하는 데 집중해야 합니다.

## 한눈에 보는 구조

브라우저에서 시작한 동작이 화면, API, 저장소까지 이어지는 전체 흐름을 검증합니다. 이 때문에 E2E 테스트는 개별 함수의 옳고 그름보다 사용자 시나리오의 성공 여부를 봅니다. 화면에서 실제로 쓸 수 있는지 확인하는 마지막 검증에 가깝습니다.

## 핵심 용어

- **E2E(end-to-end)**: 사용자의 시작 행동부터 최종 결과까지 이어지는 흐름입니다.
- **헤드리스 브라우저**: 화면을 띄우지 않고 실행되는 브라우저입니다. CI에서 자주 씁니다.
- **셀렉터(selector)**: 화면 요소를 찾는 표현입니다.
- **플래키 테스트**: 같은 코드인데도 어떤 날은 통과하고 어떤 날은 실패하는 불안정한 테스트입니다.
- **페이지 객체(page object)**: 화면별 동작을 객체로 감싼 재사용 패턴입니다.

## 바꾸기 전과 후

**바꾸기 전 — 수동 회귀 확인**

```text
- 배포 전마다 여러 사람이 한 시간씩 직접 클릭한다
- 그래도 결제 화면 버그가 운영에서 처음 드러난다
```

**바꾼 뒤 — 핵심 시나리오 자동화**

```text
- 회원가입, 로그인, 결제, 검색, 로그아웃 시나리오를 자동화한다
- CI에서 5분 안에 결과를 확인한다
```

사람이 반복해서 눌러 보는 작업은 결국 지칩니다. E2E 테스트는 이 반복을 코드로 바꿔 놓습니다. 다만 모든 화면을 다 올리려 하지 말고, 사용자 피해가 큰 흐름부터 고르는 편이 좋습니다.

## E2E 도구 비교

브라우저 자동화 도구는 여럿이 있고, 각기 다른 장단점을 가집니다. 팝은 도구는 아니지만, 팀에서 가장 자주 비교하는 세 가지를 정리했습니다.

| 기준 | Playwright | Selenium | Cypress |
|---|---|---|---|
| 언어 지원 | Python, JS, Java, .NET | Python, Java, C#, Ruby, JS | JavaScript/TypeScript 전용 |
| 설치 복잡도 | 낮음 (`playwright install`) | 높음 (WebDriver 별도 관리) | 중간 (`npm install`) |
| 실행 속도 | 빠름 | 느림 | 중간 |
| 헤드리스 | 기본 지원 | 지원 | 지원 |
| 자동 대기 | 기본 지원 | 수동 처리 | 일부 지원 |
| 병렬 실행 | 지원 | 제한적 | 유료 (Cypress Cloud) |
| 뷰포트 테스트 | 지원 (mobile emulation) | 제한적 | 지원 |
| 스크린샷 기록 | 지원 | 수동 처리 | 자동 |

Python 백엔드 팀에서는 Playwright를 가장 많이 선택합니다. Selenium은 오래 썼지만 설정이 복잡하고, Cypress는 JavaScript 전용이기 때문에 백엔드 코드와 언어가 분리됩니다. Playwright는 빠르고, 설치가 간단하며, Python을 직접 지원하므로 백엔드 테스트와 같은 환경에서 돌릴 수 있습니다.

## 플레이라이트 파이썬 예시

Playwright는 pytest 플러그인으로 동작하므로, 백엔드 테스트와 동일한 패턴으로 작성할 수 있습니다.

```python
# tests/e2e/test_user_flow.py
def test_signup_and_first_login(page):
    # 회원가입
    page.goto("https://example.com/signup")
    page.get_by_label("Email").fill("new@user.com")
    page.get_by_label("Password").fill("securePass123")
    page.get_by_role("button", name="Sign up").click()
    page.wait_for_url"**/welcome")

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

하나의 테스트 안에 회원가입부터 로그인까지 전체 흐름을 넣었습니다. 이렇게 하면 화면 전환, 상태 관리, 인증 흐름을 한 번에 검증할 수 있습니다. 다만 지나치게 길면 실패 지점을 찾기 어려우므로, 경로당 테스트 하나를 원칙으로 삼는 편이 좋습니다.

## 플래키 테스트 관리

E2E 테스트는 네트워크, 렌더링 타이밍, 비동기 요청 등 여러 변수에 영향을 받아 불안정해지기 쉽습니다. 플래키 테스트는 신뢰를 깨고, 실패를 무시하게 만듭니다.

**1. 재시도 정책**

Playwright는 `--retries` 옵션으로 실패 시 자동 재시도를 지원합니다.

```bash
pytest tests/e2e --retries 2
```

다만 재시도는 불안정을 감추는 도구이지, 근본 해결책은 아닙니다. 재시도를 걸어도 계속 깨지면 셀렉터나 대기 조건을 먼저 고쳐야 합니다.

**2. 실패 시 스크린샷 기록**

```python
# pytest.ini 또는 conftest.py
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

실패 시 스크린샷을 남기면 디버깅 시간을 크게 줄일 수 있습니다. CI 로그만 보고 문제를 찾는 것보다, 실패 지점의 화면을 보는 편이 훨씬 빠릅니다.

**3. 네트워크 대기 전략**

```python
page.goto("https://example.com")
page.wait_for_load_state("networkidle")  # 모든 네트워크 요청 종료 대기
```

단, `networkidle`은 불필요하게 길어질 수 있으므로, 특정 요소가 나타나기를 기다리는 편이 더 안정적일 때가 많습니다.

## E2E를 쓰지 말아야 할 때

E2E 테스트는 강력하지만, 모든 경우에 적합하지는 않습니다. 다음 상황에서는 E2E보다 다른 계층을 선택하는 편이 낫습니다.

**1. 비즈니스 로직 검증**

할인율 계산, 포인트 적립, 재고 차감 같은 내부 로직은 단위 테스트나 통합 테스트로 검증해야 합니다. E2E로 검증하려면 화면을 여러 번 클릭해야 하고, 실패 원인을 찾기 어렵습니다.

**2. 에지 케이스 조합**

비밀번호 유효성 규칙 10가지, 이메일 형식 20가지를 모두 E2E로 테스트하면 200개의 브라우저 시나리오가 생깁니다. 이런 경우 입력 검증은 단위 테스트로, 화면 표시는 E2E 한 두 개로 커버하는 편이 현명합니다.

**3. 외부 시스템 통합**

결제 게이트웨이, SMS 발송, 이메일 발송처럼 비용이 발생하거나 부작용이 있는 외부 시스템은 E2E에서 목 서버로 교체해야 합니다. 실제로 호출하면 비용이 커지거나 테스트 계정이 차단됩니다.

**4. API 수준 계약 검증**

프론트엔드가 없거나, API만 제공하는 백엔드 서비스는 E2E가 필요 없습니다. 통합 테스트로 HTTP 계약을 검증하는 편이 빠르고 안정적입니다.

E2E는 사용자가 직접 마주하는 화면에서 발생하는 사고를 막는 데 집중해야 합니다. 내부 로직, 에지 케이스, 외부 시스템, API 계약은 다른 계층에 맡기는 것이 최선입니다.

## 다섯 단계로 플레이라이트 시작하기

### 1단계 — 설치

```bash
pip install pytest-playwright
playwright install
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
# 권장: role + name
page.get_by_role("button", name="Sign in")
# 또는 data-testid
page.get_by_test_id("submit-login")
# 비권장: 자주 바뀌는 CSS 클래스
page.locator(".btn-primary-3xl")
```

### 4단계 — 기다림은 조건으로 처리

```python
# 나쁨
import time; time.sleep(3)
# 좋음
page.wait_for_url("**/dashboard")
page.wait_for_selector("text=Welcome")
```

### 5단계 — 페이지 객체로 재사용성 높이기

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

## 이 코드에서 먼저 볼 점

- 역할 기반 셀렉터와 텍스트 기반 셀렉터는 UI 디자인이 바뀌어도 비교적 오래 버팁니다.
- `sleep` 대신 조건부 대기를 써야 플래키함을 줄일 수 있습니다.
- 페이지 객체를 쓰면 같은 화면 동작을 여러 시나리오에서 재사용하기 쉽습니다.

E2E 테스트는 작성보다 유지가 더 어렵습니다. 그래서 처음부터 안정적인 셀렉터와 조건부 대기를 고르는 습관이 중요합니다. 작은 선택이 나중의 유지비를 크게 바꿉니다.

## 어디서 자주 헷갈릴까요?

가장 흔한 실수는 모든 화면을 E2E로 덮으려는 시도입니다. 시간이 지나면 5분짜리 테스트 묶음이 한 시간짜리 묶음으로 커지고, 누구도 자주 돌리지 않게 됩니다.

또 하나는 `time.sleep`으로 문제를 덮는 방식입니다. 잠깐은 통과할 수 있어도, 네트워크 상태나 렌더링 타이밍이 흔들리면 금방 다시 깨집니다. 기다림은 시간으로 처리하는 것이 아니라 조건으로 처리해야 합니다.

실제 결제나 실제 운영 계정을 E2E에서 호출하는 문제도 자주 생깁니다. 비용과 위험이 너무 큽니다. E2E는 스테이징이나 샌드박스 환경에서 돌리는 것이 기본입니다.

## 직접 검증해 볼 것

1. 같은 로그인 시나리오를 세 번 연속 실행해 봅니다. 한 번만 통과하고 다시 깨진다면 셀렉터나 대기 조건이 불안정한 것입니다.
2. `sleep`을 넣은 버전과 `wait_for_url`을 쓴 버전의 성공률과 실행 시간을 비교해 봅니다. 플래키 테스트는 보통 여기서 차이가 바로 드러납니다.
3. 실제 운영 계정 대신 스테이징 계정이나 샌드박스 계정을 써도 시나리오 의미가 유지되는지 확인합니다. 운영 데이터에 의존하면 재현성과 안전성이 함께 무너집니다.

**예상 결과:** 핵심 시나리오는 반복 실행에서도 같은 결과를 내고, 실패 시에는 어느 화면 요소를 기다리다 멈췄는지 로그에서 바로 읽혀야 합니다.

## 심화 실습: 운영 관점 테스트 점검

실무에서 테스트를 확장할 때 가장 먼저 해야 할 일은 실패 원인을 사람이 추측하지 않도록 로그와 단언문을 정리하는 것입니다. 테스트 실패 메시지에는 입력값, 기대값, 실제값이 함께 남아야 하며, 그래야 CI 로그만으로도 원인을 좁힐 수 있습니다.

또한 테스트는 코드와 함께 진화해야 합니다. 기능이 바뀌었는데 테스트가 그대로라면 테스트는 안전장치가 아니라 오경보 장치가 됩니다. 그래서 팀에서는 요구사항 변경 PR에 테스트 변경이 함께 포함되는지를 리뷰 기준으로 두는 편이 좋습니다.

fixture는 단순 편의 기능이 아니라 설계 도구입니다. 어떤 객체를 기본 상태로 두는지, 어떤 상태 변형을 허용하는지 fixture 레이어에서 명확히 정의하면 테스트 의도가 깔끔해집니다. 특히 도메인 객체가 복잡할수록 fixture 설계 품질이 테스트 유지보수 비용을 좌우합니다.

회귀 버그를 줄이려면 버그 티켓이 닫힐 때 반드시 재현 테스트를 남겨야 합니다. 수정 코드만 머지하면 같은 원인의 버그가 다른 경로에서 재발합니다. 반대로 재현 테스트를 함께 남기면 팀 지식이 실행 가능한 형태로 축적됩니다.

커버리지 리포트는 주간 회고에서 매우 유용합니다. 숫자만 보는 대신 누락 라인이 핵심 도메인인지 확인하고, 다음 스프린트에서 보강할 테스트를 합의하면 테스트 투자가 산발적으로 흩어지지 않습니다.

CI에서는 실패를 빠르게 보여 주는 순서가 중요합니다. 일반적으로 단위 테스트를 먼저 실행하고, 그 다음 통합 테스트, 마지막으로 느린 E2E를 배치하면 평균 피드백 시간이 줄어듭니다. 파이프라인 설계도 테스트 전략의 일부로 다루어야 합니다.

실무에서 테스트를 확장할 때 가장 먼저 해야 할 일은 실패 원인을 사람이 추측하지 않도록 로그와 단언문을 정리하는 것입니다. 테스트 실패 메시지에는 입력값, 기대값, 실제값이 함께 남아야 하며, 그래야 CI 로그만으로도 원인을 좁힐 수 있습니다.

또한 테스트는 코드와 함께 진화해야 합니다. 기능이 바뀌었는데 테스트가 그대로라면 테스트는 안전장치가 아니라 오경보 장치가 됩니다. 그래서 팀에서는 요구사항 변경 PR에 테스트 변경이 함께 포함되는지를 리뷰 기준으로 두는 편이 좋습니다.

fixture는 단순 편의 기능이 아니라 설계 도구입니다. 어떤 객체를 기본 상태로 두는지, 어떤 상태 변형을 허용하는지 fixture 레이어에서 명확히 정의하면 테스트 의도가 깔끔해집니다. 특히 도메인 객체가 복잡할수록 fixture 설계 품질이 테스트 유지보수 비용을 좌우합니다.

회귀 버그를 줄이려면 버그 티켓이 닫힐 때 반드시 재현 테스트를 남겨야 합니다. 수정 코드만 머지하면 같은 원인의 버그가 다른 경로에서 재발합니다. 반대로 재현 테스트를 함께 남기면 팀 지식이 실행 가능한 형태로 축적됩니다.

커버리지 리포트는 주간 회고에서 매우 유용합니다. 숫자만 보는 대신 누락 라인이 핵심 도메인인지 확인하고, 다음 스프린트에서 보강할 테스트를 합의하면 테스트 투자가 산발적으로 흩어지지 않습니다.

CI에서는 실패를 빠르게 보여 주는 순서가 중요합니다. 일반적으로 단위 테스트를 먼저 실행하고, 그 다음 통합 테스트, 마지막으로 느린 E2E를 배치하면 평균 피드백 시간이 줄어듭니다. 파이프라인 설계도 테스트 전략의 일부로 다루어야 합니다.

실무에서 테스트를 확장할 때 가장 먼저 해야 할 일은 실패 원인을 사람이 추측하지 않도록 로그와 단언문을 정리하는 것입니다. 테스트 실패 메시지에는 입력값, 기대값, 실제값이 함께 남아야 하며, 그래야 CI 로그만으로도 원인을 좁힐 수 있습니다.

또한 테스트는 코드와 함께 진화해야 합니다. 기능이 바뀌었는데 테스트가 그대로라면 테스트는 안전장치가 아니라 오경보 장치가 됩니다. 그래서 팀에서는 요구사항 변경 PR에 테스트 변경이 함께 포함되는지를 리뷰 기준으로 두는 편이 좋습니다.

```python
from unittest.mock import patch

def test_payment_service_retries_once_on_timeout():
    service = PaymentService()
    with patch('src.payment.client.charge') as charge:
        charge.side_effect = [TimeoutError(), {'status': 'ok'}]
        result = service.pay(user_id='u-1', amount=10000)

    assert result['status'] == 'ok'
    assert charge.call_count == 2
```

```bash
pytest -q --maxfail=1 --disable-warnings
pytest --cov=src --cov-report=term-missing
```

## 실패 신호와 첫 점검

- CSS 클래스 셀렉터가 자주 깨지면 역할 기반 셀렉터나 `data-testid`로 바꾸는 편이 낫습니다.
- 시나리오끼리 로그인 상태를 공유하면 재실행이나 병렬 실행에서 금방 흔들립니다.
- E2E가 PR마다 너무 오래 걸리면 핵심 경로만 남기고 무거운 흐름은 야간 잡으로 분리해야 합니다.

## 실무에서는 이렇게 생각합니다

대부분의 팀은 E2E 테스트를 5개에서 20개 사이의 핵심 시나리오로 제한합니다. 로그인, 회원가입, 결제, 검색처럼 서비스 가치가 직접 걸린 경로만 남기고 나머지는 단위 테스트나 통합 테스트로 내려 보냅니다.

경험 많은 엔지니어는 E2E의 역할을 분명히 압니다. E2E는 모든 것을 설명하는 계층이 아니라, 사용자가 실제로 못 쓰게 되는 사고를 막는 마지막 신호입니다. 그래서 비싸고 드문 계층이어야 합니다.

## 체크리스트

- [ ] Playwright로 시나리오 하나를 작성했습니다.
- [ ] role, text, test-id 기반 셀렉터를 사용했습니다.
- [ ] `sleep` 대신 조건부 대기를 썼습니다.
- [ ] 각 시나리오가 서로 독립적으로 실행됩니다.

## 연습 문제

1. 로그인 실패 시나리오를 하나 추가해 보세요.
2. 셀렉터 세 종류를 비교하고 무엇이 가장 안정적인지 기록해 보세요.
3. `sleep`을 일부러 넣고 왜 불안정해지는지 관찰해 보세요.

## 정리

E2E 테스트는 가장 현실에 가까운 품질 신호입니다. 다만 현실에 가까운 만큼 유지비도 큽니다. 적게 두고, 핵심 경로에 집중하고, 안정적으로 운영하는 것이 좋습니다. 다음 글에서는 외부 의존을 다룰 때 자주 쓰는 테스트 더블을 봅니다.

## 처음 질문으로 돌아가기

- **E2E 테스트는 다른 테스트 계층과 어떻게 다를까요?**
  - E2E 테스트는 브라우저를 포함한 전체 스택을 테스트하므로 가장 현실적인 사용자 흐름을 검증합니다.
- **브라우저를 직접 띄우는 테스트는 무엇을 검증할까요?**
  - 통합 테스트로 놓칠 수 있는 UI 버그, JavaScript 오류, 비동기 경쟁 상태 같은 문제를 실제 환경에서 잡습니다.
- **Playwright로 첫 시나리오를 어떻게 작성할까요?**
  - 느린 실행 속도 때문에 모든 기능을 E2E로 검증하지 않고, 사용자 가치가 높은 경로에 집중합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Testing 101 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [Testing 101 (2/10): 단위 테스트](./02-unit-test.md)
- [Testing 101 (3/10): 통합 테스트](./03-integration-test.md)
- **E2E 테스트 (현재 글)**
- 테스트 더블 (예정)
- Mock과 Stub (예정)
- 테스트 커버리지 (예정)
- 회귀 테스트 (예정)
- CI에서 테스트 실행하기 (예정)
- 테스트 전략 세우기 (예정)

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
