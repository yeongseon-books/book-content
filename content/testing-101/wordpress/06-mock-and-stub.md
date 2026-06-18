---
series: testing-101
episode: 6
title: "바이브코딩을 위한 테스팅 기초 (6/10): Mock과 Stub"
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
  - Mock
  - Stub
  - unittest.mock
  - Python
seo_description: AI가 만든 코드 테스트에서 Stub과 Mock을 언제 어떻게 쓰는지 구분하는 방법. unittest.mock 예제로 상태 검증과 상호작용 검증의 차이를 명확히 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 테스팅 기초 (6/10): Mock과 Stub

이 글은 **바이브코딩을 위한 테스팅 기초** 시리즈의 여섯 번째 글입니다. 바이브코딩 팀에서 가장 자주 혼동하는 Mock과 Stub의 차이를 `unittest.mock` 예제로 명확히 설명합니다.

---

AI에게 테스트를 만들어 달라고 하면 `MagicMock`이 가득한 코드가 나오는 경우가 많습니다. 그런데 Mock을 과하게 쓰면 AI가 코드를 리팩토링할 때마다 테스트가 먼저 깨집니다. 구현 세부사항에 테스트가 묶였기 때문입니다.

Stub과 Mock의 차이를 알면 AI 코드 테스트를 더 유연하게 만들 수 있습니다. 결과를 확인할지, 호출을 확인할지 먼저 정하면 어떤 도구를 써야 하는지도 분명해집니다.

> Stub은 응답을 제어하고, Mock은 호출 자체를 검증합니다.

## 이 글에서 다룰 문제

- Stub과 Mock은 정확히 무엇이 다를까요?
- 상태 검증과 상호작용 검증은 어떻게 구분할까요?
- `MagicMock`, `patch`, `side_effect`는 언제 쓰일까요?
- AI가 생성한 Mock 과잉 테스트의 문제는 무엇일까요?
- AI가 코드를 수정할 때 테스트가 불필요하게 깨지지 않으려면 어떻게 해야 할까요?

바이브코딩에서 AI는 코드를 자주 수정합니다. Mock에 과하게 의존하면 실제로 동작이 바뀌지 않았는데도 내부 호출 방식이 달라졌다는 이유로 테스트가 깨집니다. 반대로 Stub과 Fake로 결과를 검증하면 AI 리팩토링에 더 강한 테스트가 됩니다.

## 한눈에 보는 구조

Stub은 미리 정한 값을 돌려줘서 결과 검증을 돕습니다. Mock은 기대한 호출이 있었는지 확인해서 상호작용 검증을 돕습니다.

- **상태 검증**: 최종 반환값이나 상태 변화가 기대와 맞는지 확인하는 방식입니다.
- **상호작용 검증**: 의존을 어떤 방식으로 호출했는지 확인하는 방식입니다.
- **MagicMock**: 속성과 메서드를 유연하게 흉내 낼 수 있는 객체입니다.
- **patch**: 기존 객체를 잠시 다른 객체로 바꿔 끼우는 도구입니다.
- **side_effect**: 호출마다 다른 값이나 예외를 일으키도록 설정하는 기능입니다.

## Mock vs Stub 핵심 차이

| 구분 | Stub | Mock |
|---|---|---|
| 정의 | 미리 정해진 값을 반환하는 대체 객체 | 호출 여부와 방식을 검증하는 대체 객체 |
| 검증 대상 | 테스트 대상의 **결과** | 테스트 대상의 **상호작용** |
| AI 리팩토링 내성 | 강함 (결과만 보기 때문) | 약함 (호출 방식에 의존) |
| 적합한 상황 | 결과가 중요한 경우 | 호출 자체가 요구사항인 경우 (알림, 결제 등) |

## 바꾸기 전과 후

**바꾸기 전 — AI가 생성한 Mock 과잉 테스트**

```python
def test_creates_user(repo_mock):
    create_user("a@b.com", repo=repo_mock)
    repo_mock.add.assert_called_once()  # 호출 방식만 검증
    # AI가 내부 구현을 바꾸면 이 테스트가 깨짐
```

**바꾼 뒤 — 결과를 확인하는 테스트 (AI 리팩토링에 강함)**

```python
def test_creates_user_persists():
    repo = InMemoryUserRepo()
    create_user("a@b.com", repo=repo)
    assert repo.find_by_email("a@b.com") is not None
    # AI가 내부 구현을 바꿔도 결과가 맞으면 통과
```

## 다섯 단계로 unittest.mock 익히기

### 1단계 — 기본 Mock

```python
from unittest.mock import MagicMock

def test_basic_mock():
    m = MagicMock()
    m.greet("hi")
    m.greet.assert_called_with("hi")
```

### 2단계 — `return_value`로 Stub처럼 쓰기

```python
def test_return_value():
    m = MagicMock()
    m.fetch.return_value = {"id": 1, "email": "a@b.com"}
    result = m.fetch()
    assert result["email"] == "a@b.com"
```

### 3단계 — `side_effect`로 AI 코드의 오류 경로 테스트

```python
def test_side_effect_raises():
    m = MagicMock()
    m.fetch.side_effect = TimeoutError("connection timeout")
    try:
        m.fetch()
    except TimeoutError as e:
        assert "connection timeout" in str(e)
```

### 4단계 — `patch`로 외부 라이브러리 교체

```python
from unittest.mock import patch

def test_patch_function():
    with patch("src.weather.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"temp": 20}
        from src.weather import current_temp
        assert current_temp() == 20
```

### 5단계 — 비활성화 조건에서 호출 안 됨 검증

```python
def test_not_called_when_disabled():
    mailer = MagicMock()
    notify("a@b.com", mailer=mailer, enabled=False)
    mailer.send.assert_not_called()
```

## AI가 생성한 Mock 과잉 테스트 개선하기

AI가 만든 테스트에서 자주 보이는 패턴과 개선 방법입니다.

**AI가 생성한 과잉 Mock 테스트**

```python
def test_process_order_ai_generated():
    validator_mock = MagicMock()
    inventory_mock = MagicMock()
    payment_mock = MagicMock()
    mailer_mock = MagicMock()

    validator_mock.validate.return_value = True
    inventory_mock.reserve.return_value = True
    payment_mock.charge.return_value = {"status": "ok"}

    process_order(
        order_id=1,
        validator=validator_mock,
        inventory=inventory_mock,
        payment=payment_mock,
        mailer=mailer_mock
    )

    validator_mock.validate.assert_called_once()
    inventory_mock.reserve.assert_called_with(order_id=1)
    payment_mock.charge.assert_called_once()
    mailer_mock.send.assert_called()
    # AI가 내부 구조를 조금만 바꿔도 전부 깨짐
```

**개선된 버전 — Fake로 결과 검증, Mock은 핵심만**

```python
def test_process_order_focused():
    inventory = InMemoryInventory()
    inventory.add_stock(product_id=10, quantity=5)

    payment = FakePaymentGateway()
    mailer_mock = MagicMock()  # 메일 발송은 호출 자체가 요구사항

    result = process_order(
        order_id=1,
        inventory=inventory,
        payment=payment,
        mailer=mailer_mock
    )

    assert result.status == "confirmed"           # 결과 검증
    assert payment.last_charge()["amount"] == 100  # 결과 검증
    mailer_mock.send.assert_called_once()          # 부작용만 Mock
```

## 자주 하는 실수

첫 번째 실수는 한 테스트 안에 결과 검증과 호출 검증을 과하게 섞는 일입니다. AI가 만든 테스트에 이 패턴이 자주 나타납니다.

두 번째 실수는 `patch` 범위를 너무 넓게 잡는 일입니다. AI는 종종 모듈 전체를 patch하는 코드를 생성합니다. 다른 테스트까지 오염될 수 있습니다.

세 번째 실수는 AI가 생성한 Mock 설정이 실제 코드보다 길어지도록 두는 일입니다. 이런 테스트는 유지비만 높아집니다.

## AI 팁: Mock/Stub 선택 프롬프트

```text
프롬프트 예시:
"create_user 함수의 테스트를 작성해 줘.
저장 결과가 올바른지 확인하려면 InMemoryUserRepo Fake를 사용해 줘.
메일 발송이 정확히 한 번 호출됐는지 확인하려면 Mock을 사용해 줘.
Mock 설정이 실제 테스트 코드보다 길어지지 않게 해 줘."

확인 포인트:
1. Mock은 호출 자체가 요구사항인 곳(알림, 결제)에만 사용하는지
2. 결과 검증에는 Fake나 Stub을 사용하는지
3. patch 범위가 함수 수준으로 좁은지
```

## 운영 체크리스트

- [ ] Stub과 Mock의 차이를 한 문장으로 설명할 수 있습니다.
- [ ] AI가 생성한 Mock 과잉 테스트를 개선했습니다.
- [ ] `patch` 범위를 함수 수준으로 좁게 유지했습니다.
- [ ] 가능하면 결과 검증을 먼저 선택했습니다.

## 처음 질문으로 돌아가기

- **Stub과 Mock은 정확히 무엇이 다를까요?**
  Stub은 결과를 제어하고, Mock은 호출을 검증합니다. 동일한 `MagicMock` 객체로도 두 역할을 할 수 있지만 목적을 분리해야 합니다.

- **AI가 코드를 수정할 때 테스트가 불필요하게 깨지지 않으려면?**
  Mock 대신 Fake나 Stub으로 결과를 검증하면 AI가 내부 구현을 바꿔도 동작이 같으면 테스트가 통과합니다.

- **AI가 생성한 Mock 과잉 테스트의 문제는 무엇일까요?**
  내부 호출 방식에 묶여 AI가 코드를 개선할 때마다 테스트가 깨지고, Mock 설정 코드가 실제 테스트보다 길어져 가독성이 떨어집니다.

## 정리

Mock과 Stub은 목표가 다릅니다. AI 코드 테스트에서는 결과를 먼저 확인하는 Stub/Fake를 기본으로 하고, 호출 자체가 요구사항인 곳에만 Mock을 씁니다. 다음 글에서는 AI가 만든 코드의 어느 부분이 테스트로 덮였는지 확인하는 커버리지를 다루겠습니다.

## 참고 자료

- 실습 예제 저장소: https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko
- [unittest.mock docs](https://docs.python.org/3/library/unittest.mock.html)
- [Martin Fowler — Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html)
- [pytest-mock](https://pytest-mock.readthedocs.io/)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 테스팅 기초 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [바이브코딩을 위한 테스팅 기초 (2/10): 단위 테스트](./02-unit-test.md)
- [바이브코딩을 위한 테스팅 기초 (3/10): 통합 테스트](./03-integration-test.md)
- [바이브코딩을 위한 테스팅 기초 (4/10): E2E 테스트](./04-e2e-test.md)
- [바이브코딩을 위한 테스팅 기초 (5/10): 테스트 더블](./05-test-double.md)
- **바이브코딩을 위한 테스팅 기초 (6/10): Mock과 Stub (현재 글)**
- [바이브코딩을 위한 테스팅 기초 (7/10): 테스트 커버리지](./07-test-coverage.md)
- [바이브코딩을 위한 테스팅 기초 (8/10): 회귀 테스트](./08-regression-test.md)
- [바이브코딩을 위한 테스팅 기초 (9/10): CI에서 테스트 실행하기](./09-tests-in-ci.md)
- [바이브코딩을 위한 테스팅 기초 (10/10): 테스트 전략 세우기](./10-test-strategy.md)

<!-- toc:end -->

Tags: 바이브코딩, Testing, Mock, Stub, unittest.mock, Python
