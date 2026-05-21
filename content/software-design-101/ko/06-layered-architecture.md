---
series: software-design-101
episode: 6
title: "Software Design 101 (6/10): 계층 아키텍처"
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
  - LayeredArchitecture
  - CleanArchitecture
  - Layers
  - Architecture
seo_description: 계층 아키텍처의 구성, 허용된 의존 방향, 부패 방지 계층을 정리합니다.
last_reviewed: '2026-05-15'
---

# Software Design 101 (6/10): 계층 아키텍처

라우터에서 요청을 받고, 그 안에서 바로 검증하고, 비즈니스 규칙을 처리하고, 데이터베이스까지 두드리는 코드는 처음에는 빠르게 완성됩니다. 하지만 채널이 하나 더 늘거나 저장 방식이 바뀌는 순간 책임이 한곳에 엉켜 있었다는 사실이 바로 드러납니다.

이 글은 Software Design 101 시리즈의 6번째 글입니다.

여기서는 계층 아키텍처를 왜 쓰는지, presentation·application·domain·infrastructure를 어떤 기준으로 나누는지, 허용되는 의존성 방향은 무엇인지, 외부 모델이 도메인으로 그대로 새지 않게 막는 부패 방지 계층은 어디에 필요한지 살펴봅니다.

## 먼저 던지는 질문

- 계층을 왜 나누고, 무엇을 기준으로 나눌까요?
- 각 계층은 어떤 책임을 가져야 할까요?
- 의존성은 어떤 방향으로만 흘러야 할까요?

## 큰 그림

![Software Design 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/software-design-101/06/06-01-concept-at-a-glance.ko.png)

*Software Design 101 6장 흐름 개요*

## 왜 중요한가

UI, 비즈니스 규칙, 인프라는 바뀌는 이유도 속도도 다릅니다. 웹 요청 형식은 자주 바뀔 수 있고, 외부 데이터베이스나 SaaS는 더 자주 흔들릴 수 있습니다. 반면 핵심 도메인 규칙은 상대적으로 천천히 변합니다.

이 셋을 한 계층에 섞으면 외부 변화가 내부 규칙까지 밀고 들어옵니다. 계층 아키텍처는 이 변동성 차이를 구조로 분리하는 방식입니다. 책임이 잘 나뉘면 웹 프레임워크를 바꾸더라도 도메인 규칙은 그대로 남기기 쉬워집니다.

## 전체 그림

계층 구조에서 먼저 기억할 점은 도메인이 가장 안정적인 중심이라는 사실입니다. 바깥 채널과 저장소는 도메인을 향해 붙지만, 도메인은 바깥 세부를 모르는 편이 좋습니다.

## 기본 용어

- <strong>표현 계층</strong>: HTTP, CLI, UI처럼 바깥과 만나는 접점입니다.
- <strong>애플리케이션 계층</strong>: 유스케이스 흐름을 조율하는 계층입니다.
- <strong>도메인 계층</strong>: 업무 규칙이 있는 가장 안정적인 계층입니다.
- <strong>인프라 계층</strong>: DB, 파일, 외부 SaaS 같은 변동이 큰 세부를 다룹니다.
- <strong>부패 방지 계층</strong>: 외부 모델이 도메인으로 그대로 스며드는 것을 막는 번역 계층입니다.

## 변경 전과 변경 후

**변경 전**

```python
# one function does HTTP, business, and DB
@app.route("/charge")
def charge():
    body = request.json
    if body["amount"] <= 0: return "bad", 400
    db.execute("UPDATE wallet ...")
    return "ok"
```

**변경 후**

```python
# presentation
@app.route("/charge")
def charge_view():
    return charge_use_case(request.json)

# application
def charge_use_case(payload):
    cmd = ChargeCommand.from_payload(payload)
    return charge_service.run(cmd)
```

두 번째 구조에서는 표현 계층이 얇고, 업무 흐름은 애플리케이션 계층으로 이동합니다. 각 계층이 자기 책임만 맡으므로 수정 범위도 더 예측하기 쉬워집니다.

## 계층을 도입하는 다섯 단계

### 1단계 — 도메인을 먼저 분리한다

```python
# 1_domain.py
class Wallet:
    def debit(self, amount: int) -> None:
        if amount <= 0: raise ValueError
        self.balance -= amount
```

가장 먼저 분리할 것은 업무 규칙입니다. 금액이 0보다 커야 한다는 규칙은 웹 프레임워크나 DB 종류와 무관하게 살아남아야 합니다.

### 2단계 — 흐름을 유스케이스로 묶는다

```python
# 2_usecase.py
def charge(repo, user_id, amount):
    w = repo.get(user_id); w.debit(amount); repo.save(w)
```

유스케이스는 “무엇을 하는가”의 흐름을 담당합니다. 도메인 객체를 조합해 작업을 완료하지만, 표현 세부나 저장 구현은 직접 품지 않습니다.

### 3단계 — 표현 계층을 얇게 유지한다

```python
# 3_presentation.py
@app.route("/charge")
def view():
    return charge(repo, request.json["user"], request.json["amount"])
```

표현 계층은 입력을 받고 출력을 돌려주는 일에 집중해야 합니다. 라우터 안에서 업무 규칙이 커지기 시작하면 계층이 다시 흐려집니다.

### 4단계 — 인프라 어댑터를 둔다

```python
# 4_infra.py
class SqlWalletRepo:
    def get(self, uid): ...
    def save(self, w): ...
```

인프라는 도메인이 필요로 하는 모양을 구현합니다. 데이터베이스를 PostgreSQL에서 Redis로 바꿔도 도메인 규칙 자체는 그대로 남길 수 있어야 합니다.

### 5단계 — 부패 방지 계층으로 번역한다

```python
# 5_acl.py
def to_domain_user(external_json):
    return User(id=external_json["uid"], name=external_json["nm"])
```

외부 API 응답을 도메인 모델로 바로 쓰기 시작하면 외부 스키마가 도메인 내부 어휘를 오염시킵니다. 번역 계층을 두면 외부 변경 충격을 그 지점에서 흡수할 수 있습니다.

## 빠르게 검증해 보기

라우터 하나를 열고 HTTP 처리, 유스케이스 흐름, 도메인 규칙, 저장소 접근이 몇 줄씩 섞여 있는지 세어 보세요. 계층이 무너진 코드는 이 네 종류가 한 함수 안에 모여 있는 경우가 많습니다.

```text
router lines: input parsing, status code, JSON response
use-case lines: orchestration, transaction boundary
domain lines: validation, policy, invariant
infra lines: ORM call, SQL, SDK
```

**Expected output:** 표현 계층에는 HTTP 입출력만, 도메인에는 규칙만 남겨야 한다는 정리 포인트가 분명해집니다.

작은 프로젝트라면 네 계층을 모두 강제할 필요는 없습니다. 다만 서로 다른 이유로 바뀌는 코드를 한 함수에 쌓아 두는 상태는 피해야 합니다.

## 실패 신호와 먼저 볼 것

| 실패 신호 | 먼저 볼 것 |
| --- | --- |
| 라우터 함수가 길고 테스트도 어렵다 | 업무 흐름이 표현 계층에 남아 있는지 봅니다 |
| 도메인 모델에 ORM 세부가 많다 | 인프라가 도메인 안으로 새는지 확인합니다 |
| 외부 SaaS 응답 필드명이 도메인 곳곳에 보인다 | 부패 방지 계층이 필요한지 점검합니다 |

계층의 목적은 파일 구조를 예쁘게 만드는 것이 아니라, 바깥 변화가 안쪽 규칙을 직접 흔들지 못하게 막는 데 있습니다.

## 이 코드에서 먼저 볼 점

- 의존성은 도메인을 향하도록 정리됩니다.
- 표현 계층이 얇을수록 채널 교체 비용이 낮아집니다.
- 외부 모델은 번역을 거친 뒤 도메인으로 들어갑니다.

## 어디서 많이 헷갈릴까

계층 이름을 붙이는 것만으로 계층 아키텍처가 되는 것은 아닙니다. router 폴더, service 폴더, repository 폴더가 있어도 서비스가 ORM 모델과 HTTP 요청을 동시에 들고 있다면 실질적인 분리는 거의 없습니다.

또 다른 흔한 오해는 네 계층을 모든 프로젝트에 똑같이 강제하는 일입니다. 작은 스크립트나 단일 배치 작업에는 과할 수 있습니다. 중요한 것은 계층 개수보다, 서로 다른 이유로 바뀌는 코드를 같은 상자에 넣지 않는 감각입니다.

## 실무에서는 이렇게 본다

대부분의 백엔드는 이미 어떤 형태로든 계층 구조를 가집니다. 흔한 구성은 router → service → repository → model입니다. 여기에 외부 SaaS 연동이 들어오면 ACL을 추가해 외부 스키마를 도메인 바깥에서 번역하는 식입니다.

도메인 모델에 ORM 데코레이터가 잔뜩 붙기 시작하거나, 라우터가 업무 규칙을 대부분 품고 있으면 경계가 무너지고 있다는 신호로 봐도 됩니다. 계층 구조는 이런 누수를 빨리 발견하게 해 줍니다.

## 체크리스트

- [ ] 도메인이 인프라 라이브러리를 직접 import하지 않는가?
- [ ] 유스케이스가 애플리케이션 계층에 모여 있는가?
- [ ] 표현 계층이 입력과 출력 처리에 집중하는가?
- [ ] 외부 경계에 부패 방지 계층이 필요한지 검토했는가?
- [ ] 계층 수가 시스템 크기에 비해 과하지 않은가?

## 연습 문제

1. 라우터 하나에서 업무 로직을 서비스로 끌어내려 보세요.
2. ORM 모델과 도메인 모델을 분리해 보세요.
3. 외부 SaaS 응답 하나에 ACL을 적용해 보세요.

## 정리

계층 아키텍처는 다른 속도로 바뀌는 코드를 분리해 변경 충격을 흡수하는 구조입니다. 도메인을 중심에 두고, 표현과 인프라는 가장자리에서 협력하게 만들면 수정 범위가 훨씬 예측 가능해집니다.

다음 글에서는 계층 사이를 오가는 데이터 자체를 어떻게 설계할지, 데이터 흐름 설계를 다룹니다.

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

- **계층을 왜 나누고, 무엇을 기준으로 나눌까요?**
  - 본문의 기준은 계층 아키텍처를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **각 계층은 어떤 책임을 가져야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **의존성은 어떤 방향으로만 흘러야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Software Design 101 (1/10): 소프트웨어 설계란 무엇인가?](./01-what-is-software-design.md)
- [Software Design 101 (2/10): 관심사 분리](./02-separation-of-concerns.md)
- [Software Design 101 (3/10): 모듈과 경계](./03-modules-and-boundaries.md)
- [Software Design 101 (4/10): 의존성 방향](./04-dependency-direction.md)
- [Software Design 101 (5/10): 인터페이스와 추상화](./05-interfaces-and-abstraction.md)
- **계층 아키텍처 (현재 글)**
- 데이터 흐름 설계 (예정)
- 변경 영향 줄이기 (예정)
- 설계 원칙 모음 (예정)
- 작은 프로젝트로 설계 연습 (예정)

<!-- toc:end -->

## 참고 자료

- [Clean Architecture (Uncle Bob)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design — Layered Architecture](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Patterns of Enterprise Application Architecture](https://martinfowler.com/eaaCatalog/)
- [Anti-Corruption Layer Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer)

### 실전 확인용 문서

- [Flask Quickstart](https://flask.palletsprojects.com/en/stable/quickstart/)
- [dataclasses — Data Classes](https://docs.python.org/3/library/dataclasses.html)

Tags: Computer Science, SoftwareDesign, LayeredArchitecture, CleanArchitecture, Layers, Architecture
