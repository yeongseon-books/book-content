---
series: testing-101
episode: 6
title: "Testing 101 (6/10): Mock과 Stub"
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
  - Mock
  - Stub
  - unittest.mock
  - Python
seo_description: Stub과 Mock의 차이를 unittest.mock 예제로 명확히 구분하고 적절히 사용하는 가이드.
last_reviewed: '2026-05-12'
---

# Testing 101 (6/10): Mock과 Stub

테스트 더블을 배운 뒤에도 Mock과 Stub은 자주 뒤섞입니다. 둘 다 가짜 객체처럼 보이기 때문입니다. 그런데 목적은 꽤 다릅니다. 이 차이를 놓치면 결과를 검증해야 할 테스트를 호출 검증으로 가득 채우거나, 반대로 상호작용이 핵심인 테스트를 너무 느슨하게 만들게 됩니다.

좋은 테스트는 실패했을 때 무엇이 깨졌는지 한 줄로 말해 줍니다. Mock과 Stub을 구분하는 일은 그 한 줄을 선명하게 만드는 작업입니다.

이 글은 Testing 101 시리즈의 여섯 번째 글입니다. 여기서는 `unittest.mock` 예제를 바탕으로 Mock과 Stub의 목적 차이, 상태 검증과 상호작용 검증의 차이, `MagicMock`, `patch`, `side_effect`의 실용 패턴, 그리고 과한 Mock 사용이 보내는 설계 신호를 정리하겠습니다.

![Testing 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/06/06-01-diagram.ko.png)
*Testing 101 6장 흐름 개요*
> Stub은 응답을 제어하고, Mock은 호출 자체를 검증합니다.

## 이 글에서 다룰 문제

- Stub과 Mock은 정확히 무엇이 다를까요?
- 상태 검증과 상호작용 검증은 어떻게 구분할까요?
- `MagicMock`, `patch`, `side_effect`는 언제 쓰일까요?
- Mock을 남용하면 어떤 문제가 생길까요?
- 런던 학파와 시카고 학파는 무엇이 다를까요?

Stub과 Mock을 섞어 쓰면 테스트가 구현 세부사항에 과하게 묶입니다. 예를 들어 실제로 확인하고 싶은 것은 사용자 생성 결과인데, 저장소 메서드가 몇 번 호출됐는지만 검사하면 리팩터링 때 테스트가 먼저 부서집니다.

반대로 상호작용 자체가 핵심인 경우도 있습니다. 메일 발송, 결제 호출, 알림 전송처럼 부작용이 의미의 중심인 기능은 호출 여부와 인자가 중요합니다.

## 핵심 차이

| 구분 | Stub | Mock |
|---|---|---|
| 정의 | 미리 정해진 값을 반환하는 대체 객체 | 호출 여부와 방식을 검증하는 대체 객체 |
| 검증 대상 | 테스트 대상의 **결과** | 테스트 대상의 **상호작용** |
| 실패 원인 | 최종 상태나 반환값이 기대와 다를 때 | 예상한 호출이 일어나지 않거나 잘못된 인자로 호출될 때 |
| 적합한 상황 | 외부 의존의 응답만 고정하고 실제 결과를 확인할 때 | 호출 자체가 요구사항인 경우 (알림, 로깅, 결제 등) |

## Mock에만 기대는 테스트 vs 결과를 확인하는 테스트

**나쁜 예 — Mock에만 기대는 테스트**

```python
def test_creates_user(repo_mock):
    create_user("a@b.com", repo=repo_mock)
    repo_mock.add.assert_called_once()  # 호출 방식만 검증
    # 실제로 저장되었는지는 알 수 없음
```

**좋은 예 — 결과를 확인하는 테스트**

```python
def test_creates_user_persists():
    repo = InMemoryUserRepo()
    create_user("a@b.com", repo=repo)
    assert repo.find_by_email("a@b.com") is not None
```

두 테스트 모두 의미가 있을 수 있지만, 질문이 다릅니다. 첫 번째는 호출이 일어났는지, 두 번째는 실제로 저장 결과가 남았는지를 묻습니다. 어떤 질문이 더 본질적인지 먼저 정해야 합니다.

## 다섯 단계로 unittest.mock 익히기

### 1단계 — 기본 Mock 생성과 검증

```python
from unittest.mock import MagicMock

def test_basic_mock_call_verification():
    mailer = MagicMock()
    notify_user("a@b.com", mailer=mailer)

    mailer.send.assert_called_once_with(
        to="a@b.com",
        subject="알림",
    )
```

### 2단계 — `return_value`로 Stub처럼 쓰기

```python
def test_user_lookup_with_stub():
    repo = MagicMock()
    repo.find.return_value = User(id=1, email="a@b.com")

    result = get_user(user_id=1, repo=repo)

    assert result.email == "a@b.com"
    # 호출 검증은 선택 사항
    repo.find.assert_called_once_with(1)
```

### 3단계 — `side_effect`로 예외와 순서 다루기

```python
def test_retry_on_timeout():
    client = MagicMock()
    # 첫 호출은 TimeoutError, 두 번째 호출은 성공
    client.charge.side_effect = [TimeoutError("slow"), {"status": "ok"}]

    result = pay_with_retry(amount=100, client=client)

    assert result["status"] == "ok"
    assert client.charge.call_count == 2
```

### 4단계 — 외부 함수를 `patch`로 교체하기

```python
from unittest.mock import patch

def test_weather_api_with_patch():
    with patch("src.weather.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"temp": 20, "city": "Seoul"}
        from src.weather import current_temp
        assert current_temp("Seoul") == 20

def test_payment_service_with_patch():
    with patch("src.payment.client.charge") as charge:
        charge.return_value = {"status": "ok", "tx_id": "abc123"}
        service = PaymentService()
        result = service.pay(amount=10000)

    assert result["status"] == "ok"
    charge.assert_called_once_with(amount=10000, currency="KRW")
```

### 5단계 — 호출하지 않음을 검증하기

```python
def test_notification_skipped_when_disabled():
    mailer = MagicMock()
    send_notification("a@b.com", mailer=mailer, enabled=False)
    mailer.send.assert_not_called()

def test_audit_log_written_only_for_admin():
    audit = MagicMock()
    process_action(user_role="member", audit=audit)
    audit.log.assert_not_called()

    process_action(user_role="admin", audit=audit)
    audit.log.assert_called_once()
```

## Stub vs Mock 코드 비교

같은 `MagicMock`으로 두 역할을 모두 수행할 수 있지만, 테스트 의도가 명확해야 합니다.

**Stub 방식 — 결과 검증**

```python
def test_user_creation_with_stub():
    repo = MagicMock()
    repo.save.return_value = User(id=1, email="a@b.com")  # stub: 반환값 고정

    result = create_user("a@b.com", repo=repo)

    assert result.email == "a@b.com"  # 결과만 검증
```

**Mock 방식 — 상호작용 검증**

```python
def test_user_creation_calls_save():
    repo = MagicMock()

    create_user("a@b.com", repo=repo)

    repo.save.assert_called_once()  # 호출 자체를 검증
    call_args = repo.save.call_args[0][0]
    assert call_args.email == "a@b.com"
```

**혼합 방식 — 결과와 부작용 모두 검증**

```python
def test_order_creates_and_notifies():
    repo = InMemoryOrderRepo()      # Fake로 결과 검증
    mailer = MagicMock()            # Mock으로 메일 발송 검증

    order = create_order(user_id=1, amount=10000, repo=repo, mailer=mailer)

    # 결과 검증
    assert repo.find(order.id) is not None
    assert order.status == "pending"

    # 부작용 검증
    mailer.send.assert_called_once_with(
        to="user-1@example.com",
        subject="주문이 접수되었습니다",
    )
```

이 패턴이 가장 실용적입니다. 상태는 Fake로, 부작용만 Mock으로 검증하면 리팩터링에 강하면서도 중요한 부작용을 놓치지 않습니다.

## `patch` 사용 범위 관리

`patch`는 좁은 범위에서만 써야 다른 테스트에 영향을 남기지 않습니다.

```python
# 좁은 범위 — with 블록 안에서만 적용
def test_specific_function():
    with patch("src.module.external_call") as mock_call:
        mock_call.return_value = "mocked"
        result = function_under_test()
    assert result == "processed mocked"

# 데코레이터로 테스트 함수 범위 제한
@patch("src.module.external_call")
def test_with_decorator(mock_call):
    mock_call.return_value = "mocked"
    result = function_under_test()
    assert result == "processed mocked"

# 넓은 범위 — 피해야 할 패턴
class TestSomething:
    def setup_method(self):
        # 모든 테스트에 영향을 줄 수 있음
        self.patcher = patch("src.module.external_call")
        self.mock_call = self.patcher.start()

    def teardown_method(self):
        self.patcher.stop()  # 반드시 정리 필요
```

## 런던 학파와 시카고 학파

Mock과 Stub을 바라보는 관점은 테스트 철학에서도 갈립니다.

**London school (Mockist)**

- 객체 간 상호작용을 중심으로 테스트합니다.
- 모든 협력자를 Mock으로 교체하고 호출 계약을 검증합니다.
- 설계 의도가 명확하게 드러나지만, 리팩터링 때 테스트가 쉽게 깨질 수 있습니다.

**Chicago school (Classicist)**

- 최종 결과를 중심으로 테스트합니다.
- 가능한 한 실제 객체를 쓰고, 느리거나 제어 불가능한 것만 Stub/Fake로 바꿉니다.
- 리팩터링에 강하지만, 실패 지점이 덜 명확할 수 있습니다.

대부분의 실무 팀은 둘 사이 어딘가에 있습니다. 핵심 도메인 로직은 Chicago 방식, 외부 API나 메시징은 London 방식을 섞어 씁니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
|------|------|------------|
| 한 테스트에 결과 + 호출 검증 과하게 섞음 | 실패 이유가 흐려지고 테스트 의도 불분명 | 하나의 테스트는 하나의 목적으로 제한 |
| `patch` 범위를 모듈 전체로 넓게 잡음 | 다른 테스트 오염, 격리 실패 | 함수 수준 또는 with 블록으로 좁게 제한 |
| 모든 줄을 Mock으로 감쌈 | 테스트 대상 코드보다 Mock 설정이 더 길어짐 | Fake/Stub으로 대체 가능한 부분은 실제 구현 사용 |
| Mock의 반환 타입이 실제 코드와 다름 | 통합 환경에서만 발견되는 타입 오류 | 반환 타입 일치 확인, 또는 TypedDict/dataclass 사용 |
| `assert_called_once` 대신 `assert_called` 사용 | 여러 번 호출되어도 통과 | 의도에 맞는 검증 메서드 선택 |
| `side_effect`로 예외를 설정했지만 검증 누락 | 예외 처리 코드가 제대로 작동하는지 확인 불가 | `pytest.raises`와 함께 예외 처리 결과 검증 |

## Mock 남용이 만드는 문제

```python
# 문제 상황 — Mock 설정이 테스트보다 길어짐
def test_process_order_too_many_mocks():
    validator_mock = MagicMock()
    inventory_mock = MagicMock()
    payment_mock = MagicMock()
    mailer_mock = MagicMock()
    logger_mock = MagicMock()

    validator_mock.validate.return_value = True
    inventory_mock.reserve.return_value = True
    payment_mock.charge.return_value = {"status": "ok"}

    process_order(
        order_id=1,
        validator=validator_mock,
        inventory=inventory_mock,
        payment=payment_mock,
        mailer=mailer_mock,
        logger=logger_mock,
    )

    validator_mock.validate.assert_called_once()
    inventory_mock.reserve.assert_called_with(order_id=1)
    payment_mock.charge.assert_called_once()
    mailer_mock.send.assert_called_with("order_confirmed", to="user@example.com")
    logger_mock.info.assert_called()
```

이 테스트는 세 가지 문제가 있습니다.

1. Mock 설정이 테스트보다 깁니다.
2. 리팩터링에 취약합니다. 함수 내부에서 호출 순서가 바뀌면 즉시 깨집니다.
3. 무엇이 핵심 요구사항인지 흐려집니다.

**개선 방향**

```python
def test_process_order_focused():
    inventory = InMemoryInventory()
    inventory.add_stock(product_id=10, quantity=5)

    payment = FakePaymentGateway()
    mailer_mock = MagicMock()  # 메일 발송만 Mock으로 검증

    result = process_order(
        order_id=1,
        inventory=inventory,
        payment=payment,
        mailer=mailer_mock,
    )

    # 상태 검증
    assert result.status == "confirmed"
    assert inventory.reserved(product_id=10) == 1

    # 부작용 검증 (핵심 비즈니스 요구사항)
    mailer_mock.send.assert_called_once_with(
        "order_confirmed",
        to="user@example.com",
    )
```

## 직접 검증해 볼 것

1. 같은 시나리오를 `return_value` 기반 결과 검증과 `assert_called_with` 기반 상호작용 검증으로 각각 작성해 봅니다. 어떤 질문을 던지는 테스트인지 차이가 분명하게 보여야 합니다.
2. `patch` 범위를 함수 하나로 좁혔을 때와 모듈 전체로 넓혔을 때 다른 테스트에 미치는 영향을 비교합니다.
3. `side_effect`로 예외를 일으킨 뒤, 실패 메시지가 외부 의존 장애를 충분히 설명하는지 확인합니다.

**예상 결과:** 결과를 검증할 때는 Fake/Stub 버전이 더 읽기 쉽고, 호출 자체가 요구사항일 때만 Mock 검증이 핵심으로 남아야 합니다.

## 운영 체크리스트

- [ ] Stub과 Mock의 차이를 한 문장으로 설명할 수 있습니다.
- [ ] `return_value`, `side_effect`, `assert_called_with`를 직접 사용했습니다.
- [ ] `patch` 범위를 함수 수준으로 좁게 유지했습니다.
- [ ] 가능하면 결과 검증을 먼저 선택했습니다.
- [ ] Mock이 실제 계약과 동일한 타입을 반환하는지 확인했습니다.

## 연습 문제

1. 외부 날씨 API를 호출하는 함수를 만들고 Stub 방식과 Mock 방식으로 모두 테스트해 보세요.
2. 세 번에 한 번 실패하는 호출을 `side_effect`로 흉내 내 보세요.
3. 같은 시나리오를 Fake로도 테스트하고 무엇이 더 읽기 쉬운지 비교해 보세요.
4. Mock 설정이 10줄을 넘는 테스트를 발견하면 Fake로 교체해 보고 테스트가 얼마나 단순해지는지 확인하세요.

## 정리

Mock과 Stub은 비슷해 보이지만 목표가 다릅니다. 결과를 확인할지, 호출을 확인할지 먼저 정하면 어떤 도구를 써야 하는지도 분명해집니다. 다음 글에서는 테스트가 코드의 어느 범위까지 닿았는지 보여 주는 테스트 커버리지를 다루겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Testing 101 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [Testing 101 (2/10): 단위 테스트](./02-unit-test.md)
- [Testing 101 (3/10): 통합 테스트](./03-integration-test.md)
- [Testing 101 (4/10): E2E 테스트](./04-e2e-test.md)
- [Testing 101 (5/10): 테스트 더블](./05-test-double.md)
- **Testing 101 (6/10): Mock과 Stub (현재 글)**
- [Testing 101 (7/10): 테스트 커버리지](./07-test-coverage.md)
- [Testing 101 (8/10): 회귀 테스트](./08-regression-test.md)
- [Testing 101 (9/10): CI에서 테스트 실행하기](./09-tests-in-ci.md)
- [테스트 전략 세우기](./10-test-strategy.md)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소(book-examples): https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko
- [unittest.mock docs](https://docs.python.org/3/library/unittest.mock.html)
- [Martin Fowler — Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html)
- [pytest-mock](https://pytest-mock.readthedocs.io/)
- [Sandi Metz — POODR](https://www.poodr.com/)

Tags: Testing, Mock, Stub, unittest.mock, Python
