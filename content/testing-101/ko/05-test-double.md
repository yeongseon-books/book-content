---
series: testing-101
episode: 5
title: "Testing 101 (5/10): 테스트 더블"
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
  - Test Double
  - Fake
  - Stub
  - Spy
seo_description: Stub, Fake, Spy, Mock, Dummy를 한 번에 정리하고 언제 무엇을 쓸지 결정하는 가이드.
last_reviewed: '2026-05-12'
---

# Testing 101 (5/10): 테스트 더블

단위 테스트를 쓰다 보면 곧 외부 의존과 마주칩니다. 메일 전송, 결제 API, 현재 시간, 데이터베이스처럼 실제로 호출하면 느리거나 비싸거나 불안정한 대상들입니다. 이런 의존을 매번 진짜로 호출하면 테스트가 느려지고, 실패 원인도 코드가 아니라 외부 환경으로 번집니다.

그래서 테스트에서는 실제 의존 대신 대역을 씁니다. 다만 대역도 하나로 뭉뚱그리면 금방 헷갈립니다. 반환값만 흉내 내는 경우와 호출 자체를 기록하는 경우는 목적이 다르기 때문입니다.

이 글은 Testing 101 시리즈의 다섯 번째 글입니다. 여기서는 테스트 더블의 다섯 종류를 구분하고, 언제 무엇을 써야 하는지, 그리고 왜 과한 목 사용이 문제를 만드는지 정리하겠습니다.

![Testing 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/05/05-01-diagram.ko.png)
*Testing 101 5장 흐름 개요*
> 테스트 더블은 외부 의존을 제어함으로써 빠르고 반복 가능한 테스트를 만듭니다.

## 먼저 던지는 질문

- 테스트 더블은 무엇을 대체하는 장치일까요?
- Dummy, Stub, Spy, Mock, Fake는 어떻게 다를까요?
- 어떤 상황에서 어떤 종류를 골라야 할까요?

## 왜 중요한가

테스트는 빠르고 결정적이어야 합니다. 실제 결제 API나 SMTP 서버를 부르면 속도도 느려지고 실패 원인도 외부로 번집니다. 테스트 더블은 이런 의존을 통제 가능한 대역으로 바꿔 테스트를 짧고 안정적으로 만듭니다.

문제는 대역을 쓰는 순간 거짓 확신도 함께 들어올 수 있다는 사실입니다. 실제 계약과 너무 다른 Fake를 만들거나, 호출 횟수만 지나치게 검증하면 테스트는 초록색인데 설계는 오히려 경직될 수 있습니다. 그래서 종류를 구분하는 일이 중요합니다.

## 한눈에 보는 구조

테스트 대상 시스템은 실제 의존 대신 테스트 더블을 바라봅니다. 여기서 핵심은 대체 자체보다 대체 목적입니다. 값을 돌려주기 위해 바꾸는지, 호출 기록을 남기기 위해 바꾸는지, 간단한 실제 구현처럼 동작하게 만들려는지에 따라 선택이 달라집니다.

## 핵심 용어

- **Dummy**: 자리를 채우기만 하는 객체입니다.
- **Stub**: 미리 정한 값을 돌려주는 대역입니다.
- **Spy**: 값을 돌려주면서 호출 기록도 남기는 대역입니다.
- **Mock**: 미리 기대를 심어 두고 그 호출이 일어났는지 검증하는 대역입니다.
- **Fake**: 실제와 비슷하게 동작하지만 단순하고 빠른 구현입니다.

## 테스트 더블 종류 비교표

| 종류 | 목적 | 반환값 | 호출 기록 | 구현 복잡도 | 사용 예시 |
|---|---|---|---|---|---|
| Dummy | 자리 채우기 | 없음 | 없음 | 매우 낮음 | 사용하지 않는 인자 |
| Stub | 결과 제어 | 고정값 | 없음 | 낮음 | 시간, 난수, 외부 API 응답 |
| Spy | 결과 + 추적 | 고정값 | 기록 | 중간 | 메일 전송 기록, 로그 호출 추적 |
| Mock | 상호작용 검증 | 설정 가능 | 검증 | 중간 | 메서드 호출 여부/인자 확인 |
| Fake | 실제 동작 흉내 | 동적 | 선택 | 높음 | 인메모리 DB, 로컬 파일 시스템 |

각 종류는 테스트 목적에 따라 선택됩니다. Dummy는 컴파일을 통과하기 위해 쓰고, Stub은 결과 검증을 위해, Spy는 호출 추적과 결과 검증을 함께 하려 할 때, Mock은 상호작용 자체가 핵심일 때, Fake는 복잡한 로직을 가볍게 흉내 내야 할 때 씁니다.
## 바꾸기 전과 후

**바꾸기 전 — 실제 의존 직접 호출**

```python
def test_send_welcome_email():
    user = create_user("a@b.com")
    send_welcome_email(user)   # 실제 SMTP 호출
```

**바꾼 뒤 — 대역으로 교체**

```python
class FakeMailer:
    def __init__(self): self.sent = []
    def send(self, to, body): self.sent.append((to, body))

def test_send_welcome_email():
    mailer = FakeMailer()
    send_welcome_email(User("a@b.com"), mailer=mailer)
    assert mailer.sent == [("a@b.com", "Welcome!")]
```

진짜 SMTP 대신 `FakeMailer`를 쓰면 네트워크와 무관하게 메일 전송 결과를 확인할 수 있습니다. 이처럼 테스트 더블은 외부 비용을 잘라 내고 검증 대상을 코드 안으로 끌고 옵니다.

## 다섯 단계로 대역 종류 익히기

### 1단계 — Dummy

```python
def test_dummy_passthrough():
    user = User(email="a@b.com", logger=None)  # logger는 사용하지 않음
    assert user.email == "a@b.com"
```

### 2단계 — Stub

```python
class StubClock:
    def now(self): return "2026-05-04"

def test_uses_stub_clock():
    assert greet(StubClock()) == "Hello, today is 2026-05-04"
```

### 3단계 — Spy

```python
class SpyMailer:
    def __init__(self): self.calls = []
    def send(self, to, body): self.calls.append((to, body))

def test_spy_records_calls():
    m = SpyMailer(); send_welcome("a@b.com", m)
    assert len(m.calls) == 1
```

### 4단계 — Mock

```python
from unittest.mock import MagicMock

def test_mock_with_expectation():
    repo = MagicMock()
    repo.find.return_value = User(email="a@b.com")
    assert get_user(1, repo).email == "a@b.com"
    repo.find.assert_called_once_with(1)
```

### 5단계 — Fake

```python
class InMemoryUserRepo:
    def __init__(self): self._db = {}
    def add(self, u): self._db[u.id] = u
    def find(self, id): return self._db.get(id)
```

## 파이썬 유닛테스트 목으로 보는 상세 예시

### Spy 상세 예시 — 호출 기록과 결과 검증

```python
class SpyMailer:
    def __init__(self):
        self.sent_messages = []
    
    def send(self, to: str, subject: str, body: str):
        self.sent_messages.append({
            "to": to,
            "subject": subject,
            "body": body
        })
        return True

def test_welcome_flow_spy():
    mailer = SpyMailer()
    user = register_user("test@example.com", mailer=mailer)
    
    # 결과 검증
    assert user.email == "test@example.com"
    
    # 호출 기록 검증
    assert len(mailer.sent_messages) == 1
    assert mailer.sent_messages[0]["to"] == "test@example.com"
    assert "Welcome" in mailer.sent_messages[0]["subject"]
```

### Mock 상세 예시 — unittest.mock로 상호작용 검증

```python
from unittest.mock import MagicMock

def test_payment_calls_gateway():
    gateway = MagicMock()
    gateway.charge.return_value = {"status": "success", "tx_id": "12345"}
    
    result = process_payment(amount=100, gateway=gateway)
    
    # 상호작용 검증
    gateway.charge.assert_called_once_with(amount=100, currency="USD")
    assert result["tx_id"] == "12345"
```

### Fake 상세 예시 — 인메모리 저장소

```python
class InMemoryUserRepository:
    def __init__(self):
        self._users = {}
        self._next_id = 1
    
    def add(self, email: str) -> int:
        user_id = self._next_id
        self._users[user_id] = {"id": user_id, "email": email}
        self._next_id += 1
        return user_id
    
    def find(self, user_id: int):
        return self._users.get(user_id)
    
    def find_by_email(self, email: str):
        for user in self._users.values():
            if user["email"] == email:
                return user
        return None

def test_user_registration_with_fake_repo():
    repo = InMemoryUserRepository()
    
    user_id = register_user("alice@example.com", repo=repo)
    
    found = repo.find(user_id)
    assert found["email"] == "alice@example.com"
```

## 이 코드에서 먼저 볼 점

- Dummy는 빈 자리를 채울 뿐입니다.
- Stub은 값을 돌려주고, Spy는 호출 기록까지 남기고, Mock은 기대한 호출을 검증합니다.
- Fake는 실제 구현과 비슷한 계약을 유지하면서도 빠르게 동작합니다.

이 구분을 익히면 테스트 목적이 훨씬 선명해집니다. 결과를 확인하려는지, 상호작용을 확인하려는지, 아니면 실제 저장소 대신 가벼운 구현이 필요한지를 분리해 생각할 수 있습니다.

## 언제 어떤 더블을 쓸까? — 의사결정 흐름

```text
외부 의존 발견
    ↓
의존이 사용되는가?
    → NO → Dummy (null, 빈 객체)
    ↓ YES
고정된 결과만 필요한가?
    → YES → Stub (canned return)
    ↓ NO
호출 자체가 핵심 검증 대상인가?
    → YES → Mock (assert_called_*)
    ↓ NO
호출 기록 + 결과 둘 다 확인하는가?
    → YES → Spy (기록 + 반환)
    ↓ NO
복잡한 내부 상태와 로직이 필요한가?
    → YES → Fake (in-memory impl)
```

이 흐름은 절대적인 규칙이 아니라 출발점입니다. 실제로는 테스트 계층, 팀 관습, 언어 도구에 따라 조합해서 씁니다.

## 어디서 자주 헷갈릴까요?

가장 흔한 실수는 모든 곳에 Mock부터 꺼내는 일입니다. 그러면 구현 세부사항에 테스트가 과하게 묶여 리팩터링이 어려워집니다.

또 다른 문제는 Fake가 실제 계약과 너무 멀어지는 경우입니다. 테스트에서는 통과하지만 운영에서는 다른 방식으로 깨질 수 있습니다. Fake는 단순해야 하지만, 최소한 같은 입력과 출력 계약은 지켜야 합니다.

Spy를 쓸 때 호출 횟수만 보고 실제 결과를 확인하지 않는 문제도 자주 보입니다. 상호작용만 맞고 최종 결과가 틀릴 수 있으므로, 가능하면 결과 검증도 함께 고려해야 합니다.

## 과한 목 객체 사용이 보내는 신호

Mock은 강력하지만 남용하면 테스트가 구현에 과하게 결합됩니다. 다음 징후가 보이면 Mock 사용을 재검토해야 합니다.

### 신호 1 — Mock 설정이 테스트보다 길어짐

```python
def test_order_creation():
    # Mock 설정 20줄
    user_repo = MagicMock()
    product_repo = MagicMock()
    payment_gateway = MagicMock()
    email_service = MagicMock()
    logger = MagicMock()
    # ...
    
    # 실제 테스트 3줄
    order = create_order(user_id=1, product_id=10, ...)
    assert order.status == "pending"
```

Mock 설정이 이렇게 길어지면 의존이 너무 많거나 함수 책임이 과한 경우가 많습니다. 리팩터링 신호입니다.

### 신호 2 — 리팩터링 때마다 테스트가 깨짐

```python
# 내부 구조를 바꿨을 뿐인데 테스트 실패
repo.find.assert_called_with(user_id=1)  # 호출 순서나 횟수 변경에 취약
```

상호작용을 과하게 검증하면 내부 리팩터링이 어려워집니다. 결과 검증으로 대체할 수 있는지 먼저 고려해야 합니다.

### 신호 3 — Mock이 실제 계약과 달라짐

```python
# Mock은 통과
mock_repo.find.return_value = {"id": 1}

# 실제 저장소는 다른 형태 반환
real_repo.find(1)  # User 객체 반환, dict 아님
```

Mock과 실제 구현의 계약이 달라지면 통합 환경에서만 문제가 발견됩니다. Fake나 Contract Test로 보완해야 합니다.
## 직접 검증해 볼 것

1. `FakeMailer`가 실제 메일러와 같은 입력 계약을 지키는지 확인합니다. 메서드 이름이나 인자 모양이 다르면 테스트에서만 통과하는 가짜 안정감이 생깁니다.
2. 같은 시나리오를 Stub/Fake와 Mock 두 방식으로 각각 써 보고, 어떤 버전이 결과를 더 명확하게 설명하는지 비교합니다.
3. Spy나 Mock을 쓸 때는 호출 횟수만 보지 말고 최종 결과도 함께 점검합니다. 상호작용만 맞고 상태가 틀리는 경우가 실제로 자주 나옵니다.

**예상 결과:** 대역을 써도 테스트 목적이 더 또렷해지고, 실제 의존을 붙였을 때보다 실행 시간이 눈에 띄게 짧아져야 합니다.

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

fixture는 단순 편의 기능이 아니라 설계 도구입니다. 어떤 객체를 기본 상태로 두는지, 어떤 상태 변형을 허용하는지 fixture 레이어에서 명확히 정의하면 테스트 의도가 깔끔해집니다. 특히 도메인 객체가 복잡할수록 fixture 설계 품질이 테스트 유지보수 비용을 좌우합니다.

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

- Fake가 실제 계약과 다르면 운영에서만 재현되는 버그를 놓치기 쉽습니다.
- 테스트마다 Mock 설정이 너무 길어지면 구현 세부사항에 과하게 묶였는지 점검해야 합니다.
- Dummy로 충분한 자리에 Spy나 Mock을 끼우면 읽기 비용만 커집니다.

## 실무에서는 이렇게 생각합니다

대부분의 단위 테스트는 Stub과 Fake만으로도 충분합니다. Mock은 상호작용 자체가 중요한 경우, 예를 들어 메일 전송이나 결제 호출처럼 부작용이 핵심인 지점에서만 제한적으로 쓰는 편이 좋습니다.

경험 많은 엔지니어는 테스트 더블의 수가 많아질수록 설계 신호를 봅니다. 대역이 지나치게 많다면 의존이 과하게 퍼져 있거나 인터페이스가 불분명할 가능성이 큽니다. 테스트 더블은 문제를 숨기는 도구가 아니라 구조를 드러내는 도구이기도 합니다.

## 실무에서의 판단 기준

테스트 더블 선택은 단순 분류보다 실용적 질문에서 출발합니다.

### 질문 1 — 외부 의존 비용이 얼마나 큰가?

- 네트워크 호출: 높음 → Stub/Mock 우선
- 파일 I/O: 중간 → 상황에 따라 실제 또는 Fake
- 계산 로직: 낮음 → 실제 구현 우선

### 질문 2 — 검증 대상이 무엇인가?

- 최종 결과: Stub/Fake
- 호출 여부/인자: Mock
- 호출 기록 + 결과: Spy

### 질문 3 — 설계를 개선할 여지가 있는가?

Mock이 과하게 필요하면 의존성 주입, 인터페이스 분리, 책임 분산을 먼저 검토합니다. 테스트 문제가 아니라 설계 문제일 수 있습니다.
## 체크리스트

- [ ] 다섯 종류를 각 한 줄로 구분해 설명할 수 있습니다.
- [ ] Stub과 Fake를 직접 사용해 테스트를 작성했습니다.
- [ ] Mock은 상호작용 검증이 필요한 곳에만 사용했습니다.
- [ ] 외부 의존을 인터페이스 뒤로 분리했습니다.

## 연습 문제

1. `send_welcome` 함수를 만들고 Stub과 Mock 두 방식으로 테스트해 보세요.
2. 각 방식이 어떤 종류의 버그를 잘 잡는지 비교해 보세요.
3. 메모리 기반 저장소 Fake를 만들고 그 위에서 비즈니스 로직을 테스트해 보세요.

## 정리

테스트 더블은 외부 의존을 통제 가능한 대역으로 바꿔 테스트를 짧고 안정적으로 만듭니다. 다만 대역은 한 종류가 아니며, 목적에 맞게 골라야 합니다. 다음 글에서는 가장 자주 함께 언급되는 Mock과 Stub의 차이를 더 깊게 보겠습니다.

## 처음 질문으로 돌아가기

- **테스트 더블은 무엇을 대체하는 장치일까요?**
  - 테스트 더블은 외부 의존을 대체하여 테스트를 빠르고 격리된 상태로 유지합니다.
- **Dummy, Stub, Spy, Mock, Fake는 어떻게 다를까요?**
  - 더블의 종류(더미, 스텁, 스파이, 목)를 상황에 맞게 선택하면 불필요한 의존 호출 없이 로직만 검증할 수 있습니다.
- **어떤 상황에서 어떤 종류를 골라야 할까요?**
  - 테스트 더블을 과도하게 사용하면 실제 의존과의 계약 변화를 감지하지 못할 수 있으므로 균형이 필요합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Testing 101 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [Testing 101 (2/10): 단위 테스트](./02-unit-test.md)
- [Testing 101 (3/10): 통합 테스트](./03-integration-test.md)
- [Testing 101 (4/10): E2E 테스트](./04-e2e-test.md)
- **테스트 더블 (현재 글)**
- Mock과 Stub (예정)
- 테스트 커버리지 (예정)
- 회귀 테스트 (예정)
- CI에서 테스트 실행하기 (예정)
- 테스트 전략 세우기 (예정)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소(book-examples): https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko
- [Martin Fowler — Test Double](https://martinfowler.com/bliki/TestDouble.html)
- [Meszaros — xUnit Test Patterns](http://xunitpatterns.com/Test%20Double.html)
- [unittest.mock docs](https://docs.python.org/3/library/unittest.mock.html)
- [Martin Fowler — Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html)

Tags: Testing, Test Double, Fake, Stub, Spy
