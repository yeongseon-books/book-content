---
series: testing-101
episode: 4
title: "바이브코딩을 위한 테스팅 기초 (4/10): E2E 테스트"
status: content-ready
targets:
  wordpress: true
  tistory: false
  medium: false
  hashnode: false
  mkdocs: false
  ebook: false
language: ko
tags:
  - 바이브코딩
  - Testing
  - E2E
  - Playwright
  - Browser
  - Automation
seo_description: AI가 만든 프론트엔드와 백엔드 코드가 사용자 관점에서 제대로 동작하는지 확인하는 E2E 테스트. Playwright로 핵심 시나리오를 자동화하는 방법.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 테스팅 기초 (4/10): E2E 테스트

이 글은 **바이브코딩을 위한 테스팅 기초** 시리즈의 네 번째 글입니다. AI가 만든 프론트엔드와 백엔드가 사용자 관점에서 실제로 동작하는지 확인하는 E2E 테스트를 설명합니다.

---

로그인 화면이 잘 보이고, 버튼도 눌리고, API도 정상이라고 각자 확인했는데 실제 사용자는 로그인조차 못 하는 상황이 생길 수 있습니다. 바이브코딩 환경에서는 이 상황이 더 자주 발생합니다. AI가 프론트엔드와 백엔드를 따로 만들었을 때 두 코드가 실제로 맞물리는지는 아무도 확인하지 않았기 때문입니다.

E2E 테스트는 그 흐름을 사용자의 시선에서 다시 확인합니다. AI가 만든 코드 전체를 하나의 사용자 경험으로 묶어서 검증합니다.

> E2E 테스트는 AI가 만든 시스템 전체가 사용자 관점에서 동작하는지 확인하는 마지막 안전망입니다.

## 이 글에서 다룰 문제

- E2E 테스트는 다른 테스트 계층과 어떻게 다를까요?
- AI가 만든 풀스택 코드에서 E2E 테스트가 잡는 버그는 어떤 것들일까요?
- Playwright로 첫 시나리오를 어떻게 작성할까요?
- E2E 테스트를 너무 많이 만들면 어떤 문제가 생길까요?
- 플래키(flaky)한 E2E 테스트를 줄이는 방법은 무엇일까요?

바이브코딩에서 E2E 테스트의 핵심 가치는 "AI가 각 부분을 따로 만들었을 때 전체가 맞는지"를 확인하는 것입니다. 프론트엔드 컴포넌트와 API 응답 형식이 다를 수도 있고, 인증 토큰 처리가 한쪽에서만 잘못될 수도 있습니다.

## 한눈에 보는 구조

브라우저에서 시작한 동작이 화면, API, 저장소까지 이어지는 전체 흐름을 검증합니다. AI가 만든 코드의 연결 지점 모두를 실제 사용자 행동으로 검증합니다.

- **E2E(end-to-end)**: 사용자의 시작 행동부터 최종 결과까지 이어지는 흐름입니다.
- **헤드리스 브라우저**: 화면을 띄우지 않고 실행되는 브라우저입니다. CI에서 씁니다.
- **셀렉터(selector)**: 화면 요소를 찾는 표현입니다.
- **플래키 테스트**: 같은 코드인데도 어떤 날은 통과하고 어떤 날은 실패하는 불안정한 테스트입니다.
- **페이지 객체(page object)**: 화면별 동작을 객체로 감싼 재사용 패턴입니다.

## E2E 도구 비교

| 기준 | Playwright | Selenium | Cypress |
|---|---|---|---|
| 언어 지원 | Python, JS, Java, .NET | Python, Java, C#, Ruby, JS | JavaScript/TypeScript 전용 |
| 설치 복잡도 | 낮음 | 높음 | 중간 |
| 실행 속도 | 빠름 | 느림 | 중간 |
| 자동 대기 | 기본 지원 | 수동 처리 | 일부 지원 |
| 바이브코딩 추천도 | 높음 | 낮음 | JS 프로젝트만 |

Python 백엔드 바이브코딩 팀에는 Playwright가 가장 적합합니다. 설치가 간단하고, Python을 직접 지원하며, 백엔드 테스트와 같은 환경에서 돌릴 수 있습니다.

## 바꾸기 전과 후

**바꾸기 전 — AI가 만든 풀스택 코드, 수동 회귀 확인**

```text
- AI로 프론트엔드, 백엔드 각각 생성
- 배포 전 여러 사람이 한 시간씩 직접 클릭
- 로그인은 되는데 결제 화면에서 오류 발생
- 운영에서 처음 발견
```

**바꾼 뒤 — 핵심 시나리오 자동화**

```text
- 회원가입, 로그인, 결제, 검색, 로그아웃을 자동화
- AI가 코드를 수정할 때마다 5분 안에 결과 확인
```

## 다섯 단계로 Playwright 시작하기

### 1단계 — 설치

```bash
pip install pytest-playwright
playwright install
```

### 2단계 — AI가 만든 로그인 흐름 테스트

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
# 권장: role + name (AI가 만든 HTML 변경에도 강함)
page.get_by_role("button", name="Sign in")
# 또는 data-testid
page.get_by_test_id("submit-login")
# 비권장: AI가 생성하는 CSS 클래스는 자주 바뀜
page.locator(".btn-primary-3xl")
```

### 4단계 — sleep 대신 조건부 대기

```python
# 나쁨: AI가 자주 추가하는 패턴
import time; time.sleep(3)
# 좋음: 실제 상태 변화를 기다림
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
    lp = LoginPage(page)
    lp.open()
    lp.login("a@b.com", "secret")
    assert page.get_by_text("Welcome").is_visible()
```

## 바이브코딩에서 E2E가 잡는 버그 유형

AI가 프론트엔드와 백엔드를 따로 만들 때 자주 발생하는 E2E 수준의 버그들입니다.

```text
버그 유형 1: API 응답 필드명 불일치
- 백엔드: {"user_name": "홍길동"}
- 프론트엔드: response.data.userName 접근 (camelCase 가정)
- 단위/통합 테스트: 각자 통과
- E2E: 이름 표시 안 됨

버그 유형 2: 인증 토큰 처리 누락
- AI가 API 엔드포인트를 만들 때 토큰 갱신 로직 빠뜨림
- 30분 후 자동 로그아웃
- E2E 시나리오 실행 중 발견 가능

버그 유형 3: 리디렉션 URL 불일치
- 로그인 성공 후 /dashboard 대신 /home으로 이동
- 백엔드 테스트: 200 응답 확인
- E2E: 페이지 전환 후 올바른 화면인지 확인
```

## E2E를 쓰지 말아야 할 때

바이브코딩 팀이 E2E 테스트를 남용하면 CI가 수십 분씩 걸려 개발 속도가 떨어집니다.

| 검증 대상 | 권장 계층 |
|---|---|
| 할인 계산 로직 | 단위 테스트 |
| API 응답 스키마 | 통합 테스트 |
| 이메일 형식 유효성 20가지 | 단위 테스트 |
| 로그인 → 결제 핵심 흐름 | E2E |
| 실제 결제 API 호출 | 목(mock) 서버로 대체 |

## 자주 하는 실수

가장 흔한 실수는 모든 화면을 E2E로 덮으려는 시도입니다. 바이브코딩 팀에서는 AI가 빠르게 화면을 만드는 만큼 E2E도 빠르게 늘어나는 경향이 있습니다. 하지만 E2E 20개를 넘어가면 CI가 느려지고 플래키 테스트가 증가합니다.

`time.sleep`으로 문제를 덮는 방식도 자주 보입니다. AI가 만든 E2E 테스트에는 `sleep`이 자주 포함되어 있으므로 반드시 조건부 대기로 교체해야 합니다.

## AI 팁: E2E 테스트 프롬프트

```text
프롬프트 예시:
"로그인 E2E 테스트를 Playwright Python으로 작성해 줘.
role 기반 셀렉터를 사용하고, sleep 대신 wait_for_url을 사용해 줘.
정상 로그인과 잘못된 비밀번호 실패 케이스를 포함해 줘."

확인 포인트:
1. sleep 없이 조건부 대기를 사용하는지
2. CSS 클래스가 아닌 role/text/testid 셀렉터를 사용하는지
3. 시나리오끼리 독립적으로 실행되는지
```

## 운영 체크리스트

- [ ] Playwright로 핵심 시나리오 하나 이상을 작성했습니다.
- [ ] role, text, test-id 기반 셀렉터를 사용했습니다.
- [ ] `sleep` 대신 조건부 대기를 썼습니다.
- [ ] AI가 만든 E2E 테스트의 sleep을 제거했습니다.
- [ ] E2E 테스트 수를 20개 이내로 유지합니다.

## 처음 질문으로 돌아가기

- **E2E 테스트는 다른 테스트 계층과 어떻게 다를까요?**
  단위/통합 테스트가 각 부품을 검증한다면, E2E는 사용자가 실제로 경험하는 전체 흐름을 검증합니다. AI가 따로 만든 부품들이 사용자 관점에서 맞물리는지 확인합니다.

- **E2E 테스트를 너무 많이 만들면 어떤 문제가 생길까요?**
  CI 실행 시간이 급격히 늘고, 플래키 테스트가 증가하며, 팀이 테스트를 무시하기 시작합니다. 핵심 경로 20개 이내로 제한하세요.

- **플래키한 E2E 테스트를 줄이는 방법은 무엇일까요?**
  `sleep` 제거, role 기반 셀렉터 사용, `wait_for_url` 같은 조건부 대기 사용입니다. AI가 생성한 테스트에는 이 패턴이 빠진 경우가 많습니다.

## 정리

E2E 테스트는 AI가 만든 시스템 전체가 사용자 관점에서 동작하는지 확인하는 마지막 안전망입니다. 하지만 비용이 비싸므로 핵심 경로만 선택해서 안정적으로 운영해야 합니다. 다음 글에서는 외부 의존을 다룰 때 자주 쓰는 테스트 더블을 봅니다.

## 참고 자료

- 실습 예제 저장소: https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko
- [Playwright for Python](https://playwright.dev/python/)
- [Playwright locators guide](https://playwright.dev/python/docs/locators)
- [Google Testing Blog — Flaky Tests](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 테스팅 기초 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [바이브코딩을 위한 테스팅 기초 (2/10): 단위 테스트](./02-unit-test.md)
- [바이브코딩을 위한 테스팅 기초 (3/10): 통합 테스트](./03-integration-test.md)
- **바이브코딩을 위한 테스팅 기초 (4/10): E2E 테스트 (현재 글)**
- [바이브코딩을 위한 테스팅 기초 (5/10): 테스트 더블](./05-test-double.md)
- [바이브코딩을 위한 테스팅 기초 (6/10): Mock과 Stub](./06-mock-and-stub.md)
- [바이브코딩을 위한 테스팅 기초 (7/10): 테스트 커버리지](./07-test-coverage.md)
- [바이브코딩을 위한 테스팅 기초 (8/10): 회귀 테스트](./08-regression-test.md)
- [바이브코딩을 위한 테스팅 기초 (9/10): CI에서 테스트 실행하기](./09-tests-in-ci.md)
- [바이브코딩을 위한 테스팅 기초 (10/10): 테스트 전략 세우기](./10-test-strategy.md)

<!-- toc:end -->

Tags: 바이브코딩, Testing, E2E, Playwright, Browser, Automation
