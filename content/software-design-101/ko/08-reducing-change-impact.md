---
series: software-design-101
episode: 8
title: "Software Design 101 (8/10): 변경 영향 줄이기"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - SoftwareDesign
  - ChangeImpact
  - OpenClosed
  - FeatureFlags
  - Refactoring
seo_description: 한 번의 변경이 시스템을 흔들지 않게 하는 설계 — 개방 폐쇄 원칙과 확장-수축 패턴을 정리합니다.
last_reviewed: '2026-05-15'
---

# Software Design 101 (8/10): 변경 영향 줄이기

카테고리 하나를 더 추가하려고 기존 가격 계산 함수에 `if-elif`를 계속 덧붙이다 보면 언젠가 작은 수정 하나가 전체 시스템을 긴장시키는 시점이 옵니다. 변경이 필요한 것은 한 줄인데, 검증 범위와 배포 불안은 그보다 훨씬 커집니다.

이 글은 Software Design 101 시리즈의 8번째 글입니다.

여기서는 변경의 폭발 반경을 어떻게 줄일지, OCP를 실무에서 어떻게 해석해야 할지, expand-contract 패턴과 feature flag를 어떻게 조합할지, 운영 중인 시스템에서 새 경로와 옛 경로를 병행하는 감각은 무엇인지 설명합니다.

## 먼저 던지는 질문

- 한 번의 변경이 얼마나 넓게 퍼지는지 어떻게 가늠할까요?
- OCP는 실제 코드에서 어떤 모습으로 나타날까요?
- 새 경로를 추가할 때 왜 기존 경로를 바로 지우지 않을까요?

## 큰 그림

![Software Design 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/software-design-101/08/08-01-concept-at-a-glance.ko.png)

*Software Design 101 8장 흐름 개요*

## 왜 중요한가

대부분의 시스템은 처음부터 완벽하지 않습니다. 실제로는 계속 바뀌면서 좋아집니다. 그래서 중요한 것은 “변경이 필요한가”가 아니라 “변경이 어디까지 흔드는가”입니다.

폭발 반경이 작은 시스템은 더 자주, 더 안전하게 진화할 수 있습니다. 새 기능을 넣더라도 기존 경로를 건드리지 않고 옆에 붙일 수 있고, 운영 중에도 비교 검증을 하면서 천천히 전환할 수 있기 때문입니다.

## 전체 그림

흐름은 보통 확장하고, 나란히 돌려 보고, 점진적으로 갈아탄 뒤, 마지막에 옛 경로를 정리하는 순서로 갑니다. 정리까지 끝나야 변경이 완료됩니다.

## 기본 용어

- <strong>폭발 반경</strong>: 한 번의 변경이 퍼질 수 있는 범위입니다.
- <strong>OCP</strong>: 확장에는 열려 있고 기존 코드 수정에는 닫혀 있는 구조를 지향하는 원칙입니다.
- <strong>expand-contract</strong>: 새 경로와 옛 경로를 함께 운영하며 점진적으로 이주하는 패턴입니다.
- <strong>feature flag</strong>: 코드 배포와 기능 활성화를 분리하는 스위치입니다.
- <strong>strangler fig</strong>: 레거시 바깥을 감싼 뒤 점진적으로 대체해 가는 전환 방식입니다.

## 변경 전과 변경 후

**변경 전**

```python
def price(item, kind):
    if kind == "book": return item.cost * 0.9
    elif kind == "food": return item.cost * 0.95
    elif kind == "lux": return item.cost * 1.1
    # adding a new category = editing this function
```

**변경 후**

```python
class PricingRule:
    def apply(self, item) -> float: ...

PRICING: dict[str, PricingRule] = {}

def price(item, kind):
    return PRICING[kind].apply(item)
```

두 번째 구조에서는 새 카테고리를 추가할 때 기존 분기문을 직접 수정하지 않아도 됩니다. 확장을 데이터 등록으로 표현하므로 파급 범위를 줄이기 쉽습니다.

## 변경 영향을 줄이는 다섯 단계

### 1단계 — 폭발 반경을 먼저 잰다

```bash
# 1_blast.sh
git grep -n "kind ==" | wc -l
# Has one variable's comparison spread across the system?
```

현재 구조에서 같은 분기가 몇 군데로 퍼져 있는지부터 봐야 합니다. 어디까지 번져 있는지 모르면 줄일 수도 없습니다.

### 2단계 — 새 경로를 옆에 확장한다

```python
# 2_expand.py
# Add the new path only; leave the old one intact.
def price_v2(item, kind): ...
```

새 구현을 추가할 때 기존 경로를 바로 뜯어고치지 않는 편이 좋습니다. 운영 중인 시스템이라면 특히 비교 기준을 남겨 둬야 합니다.

### 3단계 — 기능 플래그로 점진 전환한다

```python
# 3_migrate.py
def price(item, kind):
    if FF.use_v2: return price_v2(item, kind)
    return price_v1(item, kind)
```

배포와 활성화를 분리하면 새 코드를 미리 올려 두고도 천천히 사용자 일부부터 전환할 수 있습니다. 변경을 작은 단계로 나누는 효과가 있습니다.

### 4단계 — 병렬 비교로 검증한다

```python
# 4_compare.py
def price(item, kind):
    a, b = price_v1(item, kind), price_v2(item, kind)
    if a != b: log.warn("price drift", a, b)
    return a if not FF.use_v2 else b
```

옛 경로와 새 경로를 나란히 돌려 보면 잠복 회귀를 빨리 잡을 수 있습니다. 운영 중인 데이터를 기준으로 비교할 수 있다는 점이 큽니다.

### 5단계 — 마지막에 수축하고 정리한다

```python
# 5_contract.py
# Once everyone is on v2, remove v1 and the flag.
```

새 경로가 안정화되면 옛 코드와 플래그를 지워야 합니다. 정리를 미루면 운영 부채가 쌓입니다.

## 빠르게 검증해 보기

운영 중 코드라면 새 경로를 넣기 전에 비교 기준부터 적어 두는 편이 좋습니다. 아래처럼 옛 경로와 새 경로를 어떤 값으로 비교할지 정리해 보세요.

```text
비교 대상: 가격 계산 결과
비교 시점: 요청 처리 직후
허용 오차: 0
전환 기준: 불일치 로그 0건, 회귀 테스트 통과
```

**Expected output:** 새 구현을 켜기 전에 어떤 신호가 안전한 전환 근거가 되는지 문장으로 설명할 수 있습니다.

이 단계가 있으면 기능 플래그는 단순 스위치가 아니라 검증 계획의 일부가 됩니다.

## 실패 신호와 먼저 볼 것

| 실패 신호 | 먼저 볼 것 |
| --- | --- |
| 새 구현을 켠 뒤 결과 차이를 뒤늦게 발견한다 | 병렬 비교 로그가 있었는지 확인합니다 |
| 기능 플래그가 몇 달째 남아 있다 | 만료일과 제거 계획이 있는지 봅니다 |
| 작은 변경에도 expand-contract를 강제한다 | 정말 운영 위험이 큰 변경인지 다시 판단합니다 |

변경 영향 줄이기의 핵심은 패턴을 많이 쓰는 것이 아니라, 필요한 변화만 작은 단계로 나누어 안전하게 넘기는 데 있습니다.

## 이 코드에서 먼저 볼 점

- 새 경로가 기존 경로를 바로 덮어쓰지 않습니다.
- 변경이 분기 증가보다 데이터와 설정으로 표현됩니다.
- 비교 검증이 구조 안에 자연스럽게 들어옵니다.

## 어디서 많이 헷갈릴까

개방 폐쇄 원칙을 “기존 코드는 절대 수정하면 안 된다”로 받아들이면 곤란합니다. 실제 의미는 새 기능 추가가 기존 구조 전체를 흔들지 않도록 설계하자는 쪽에 가깝습니다. 작은 버그 수정까지 모두 거대한 확장 패턴으로 처리할 필요는 없습니다.

또 하나 큰 함정은 expand만 하고 contract를 하지 않는 일입니다. 플래그와 구버전 코드가 계속 남아 있으면 한때 안전장치였던 것이 나중에는 운영 부담이 됩니다. 변경의 마지막 단계는 청소까지 포함합니다.

## 실무에서는 이렇게 본다

스키마 마이그레이션, API 버전 교체, 가격 계산 로직 개편, 외부 SaaS 전환처럼 운영 중 시스템을 바꾸는 작업에서 이 패턴은 특히 강합니다. 새 경로와 옛 경로를 함께 두고 관측하면서 옮길 수 있기 때문입니다.

강한 팀은 기능 플래그에도 만료일을 둡니다. 영구 플래그는 보통 숨은 부채입니다. 변경을 끝냈다면 안전하게 제거하는 계획까지 포함해야 합니다.

## 체크리스트

- [ ] 변경의 폭발 반경을 먼저 가늠했는가?
- [ ] 새 경로를 옛 경로 옆에 둘 수 있는가?
- [ ] 병렬 비교나 회귀 검증 수단이 있는가?
- [ ] 기능 플래그에 만료일이 있는가?
- [ ] 전환 뒤 옛 코드 정리 계획까지 세웠는가?

## 연습 문제

1. 현재 코드에서 분기가 가장 많은 함수를 골라 데이터 기반 분배로 바꿔 보세요.
2. API 하나를 v2로 옮기는 expand-contract 계획을 적어 보세요.
3. 만료일이 없는 기능 플래그 목록을 만들고 정리 우선순위를 매겨 보세요.

## 정리

좋은 설계는 변경 자체를 두려워하지 않게 만듭니다. 새 경로를 확장하고, 나란히 검증하고, 점진적으로 전환한 뒤, 마지막에 정리하는 흐름을 익히면 운영 중인 시스템도 훨씬 차분하게 바꿀 수 있습니다.

다음 글에서는 이런 판단을 압축해 설명하는 공통 언어, 설계 원칙 모음을 다룹니다.

## 설계 경계를 코드로 내리는 추가 예시

실무에서 설계 논의가 길어지는 이유는 "모듈 경계"가 문장으로만 남기 쉽기 때문입니다. 경계를 글로 합의한 뒤 코드로 고정하지 않으면 다음 기능을 붙이는 순간 경계가 다시 흐려집니다. 그래서 설계 문서와 함께, 경계를 강제하는 최소한의 구조를 코드에 먼저 두는 방식이 안전합니다.

### 모듈 경계 예시: 주문 결제 도메인

아래 구조는 결제 정책, 결제 수단 어댑터, 외부 API 호출을 분리합니다. 핵심은 도메인 모듈이 인프라 구현을 직접 모르고, 인터페이스를 통해서만 협력한다는 점입니다.

```text
order/
  domain/
    payment_policy.py
    ports.py
  application/
    checkout_service.py
  infrastructure/
    stripe_gateway.py
    kakao_gateway.py
```

```python
# domain/ports.py
from typing import Protocol

class PaymentGateway(Protocol):
    def authorize(self, order_id: str, amount: int) -> str: ...
    def capture(self, payment_id: str) -> None: ...

class RiskChecker(Protocol):
    def is_suspicious(self, user_id: str, amount: int) -> bool: ...
```

이렇게 포트를 먼저 정의하면 애플리케이션 계층은 "무엇을 요청하는가"만 알면 됩니다. Stripe, KakaoPay, 사내 결제 모듈처럼 구현체가 달라져도 애플리케이션 서비스의 제어 흐름은 유지됩니다. 변경 비용을 구현체 내부로 가두는 효과가 생깁니다.

### 의존성 주입(DI) 예시: 생성 시점에서 연결

```python
# application/checkout_service.py
from dataclasses import dataclass
from domain.ports import PaymentGateway, RiskChecker

@dataclass
class CheckoutService:
    gateway: PaymentGateway
    risk_checker: RiskChecker

    def checkout(self, order_id: str, user_id: str, amount: int) -> str:
        if self.risk_checker.is_suspicious(user_id, amount):
            raise ValueError("risk blocked")
        payment_id = self.gateway.authorize(order_id, amount)
        self.gateway.capture(payment_id)
        return payment_id
```

```python
# composition_root.py
from application.checkout_service import CheckoutService
from infrastructure.stripe_gateway import StripeGateway
from infrastructure.simple_risk_checker import SimpleRiskChecker

service = CheckoutService(
    gateway=StripeGateway(api_key="masked"),
    risk_checker=SimpleRiskChecker(),
)
```

DI의 핵심은 프레임워크 사용 여부가 아니라 "조립 위치"를 분리하는 것입니다. 비즈니스 로직 내부에서 구현체를 `new` 하지 않으면 테스트에서 대체 객체를 넣기 쉬워지고, 운영에서 구현체 교체 시 영향 범위가 줄어듭니다.

### 인터페이스 패턴: 정책 객체 분리

가격 계산이나 할인 규칙은 가장 자주 바뀌는 영역입니다. 이 규칙을 서비스 코드 안에 `if` 체인으로 붙이면 기능은 빠르게 나오지만 변경 지점이 폭발합니다. 아래처럼 정책 인터페이스를 두면 규칙 추가를 클래스 추가로 제한할 수 있습니다.

```python
from typing import Protocol

class DiscountPolicy(Protocol):
    def discount(self, amount: int) -> int: ...

class RatePolicy:
    def __init__(self, rate: float) -> None:
        self.rate = rate

    def discount(self, amount: int) -> int:
        return int(amount * self.rate)

class FixedPolicy:
    def __init__(self, fixed: int) -> None:
        self.fixed = fixed

    def discount(self, amount: int) -> int:
        return min(self.fixed, amount)
```

정책 인터페이스를 쓰면 런타임 선택도 단순해집니다. 신규 캠페인 규칙은 기존 서비스 코드를 수정하기보다 새 정책 클래스를 추가하고 조립부에서 연결하면 끝납니다. 이 방식은 OCP를 실무적으로 지키는 가장 단순한 패턴입니다.

### 경계 품질을 확인하는 운영 체크

- 모듈 경계를 넘는 import가 늘어나는지 주간으로 확인합니다.
- 애플리케이션 계층에서 인프라 타입을 직접 참조하는지 검사합니다.
- 변경 요청 하나당 수정 파일 수를 기록해 경계 누수를 추적합니다.
- 구현체 교체(예: 결제 게이트웨이 변경) 리허설을 분기마다 1회 실행합니다.

설계는 문서에서 시작하지만, 유지보수성은 경계 강제 구조와 조립 규칙에서 결정됩니다. 경계를 합의한 다음 즉시 포트, 조립부, 테스트 대역을 갖춘 최소 코드를 두면 다음 변경에서 체감되는 비용 차이가 명확하게 나타납니다.

## 처음 질문으로 돌아가기

- **한 번의 변경이 얼마나 넓게 퍼지는지 어떻게 가늠할까요?**
  - 본문의 기준은 변경 영향 줄이기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **OCP는 실제 코드에서 어떤 모습으로 나타날까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **새 경로를 추가할 때 왜 기존 경로를 바로 지우지 않을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Software Design 101 (1/10): 소프트웨어 설계란 무엇인가?](./01-what-is-software-design.md)
- [Software Design 101 (2/10): 관심사 분리](./02-separation-of-concerns.md)
- [Software Design 101 (3/10): 모듈과 경계](./03-modules-and-boundaries.md)
- [Software Design 101 (4/10): 의존성 방향](./04-dependency-direction.md)
- [Software Design 101 (5/10): 인터페이스와 추상화](./05-interfaces-and-abstraction.md)
- [Software Design 101 (6/10): 계층 아키텍처](./06-layered-architecture.md)
- [Software Design 101 (7/10): 데이터 흐름 설계](./07-data-flow-design.md)
- **변경 영향 줄이기 (현재 글)**
- 설계 원칙 모음 (예정)
- 작은 프로젝트로 설계 연습 (예정)

<!-- toc:end -->

## 참고 자료

- [Open/Closed Principle (Robert C. Martin)](https://web.archive.org/web/20060822033314/http://www.objectmentor.com/resources/articles/ocp.pdf)
- [ParallelChange (Expand-Contract) — Danilo Sato](https://martinfowler.com/bliki/ParallelChange.html)
- [Feature Toggles — Pete Hodgson](https://martinfowler.com/articles/feature-toggles.html)
- [Strangler Fig Application — Martin Fowler](https://martinfowler.com/bliki/StranglerFigApplication.html)

### 실전 확인용 문서

- [logging — Logging facility for Python](https://docs.python.org/3/library/logging.html)
- [enum — Support for enumerations](https://docs.python.org/3/library/enum.html)

Tags: Computer Science, SoftwareDesign, ChangeImpact, OpenClosed, FeatureFlags, Refactoring
