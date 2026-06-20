---
series: software-design-101
episode: 9
title: "Software Design 101 (9/10): 설계 원칙 모음"
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
  - SOLID
  - KISS
  - YAGNI
  - Principles
seo_description: SOLID, KISS, YAGNI, DRY, 디미터 법칙을 한 자리에서 정리하고 언제 적용할지 보여줍니다.
last_reviewed: '2026-05-15'
---

# Software Design 101 (9/10): 설계 원칙 모음

코드 냄새를 먼저 보고, 어떤 원칙이 깨졌는지 짚은 뒤, 그 원칙에 맞춰 구조를 고치는 흐름이 실전 감각에 가깝습니다.

이 글은 Software Design 101 시리즈의 아홉 번째 글입니다.

SOLID, KISS, YAGNI 같은 원칙은 이름만 외우면 금방 추상적인 구호처럼 들립니다. 실제 설계에 도움이 되는 순간은 따로 있습니다. 코드가 커지고 냄새가 나기 시작할 때, 어떤 질문을 던져야 하는지 알려 주는 진단 도구로 쓸 때입니다.

여기서는 SOLID 다섯 원칙을 평이한 언어로 다시 정리하고, KISS·YAGNI·DRY·디미터 법칙이 어디에 붙는지 설명합니다. 중요한 것은 암기가 아니라 적용 시점입니다. 각 원칙이 어떤 냄새에 반응하는지 연결해서 보겠습니다.

![Software Design 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/software-design-101/09/09-01-concept-at-a-glance.ko.png)
*Software Design 101 9장 흐름 개요*

> SOLID·KISS·YAGNI·DRY는 외워야 하는 구호가 아니라 '코드에서 어떤 냄새가 날 때 어떤 질문을 던질지' 알려 주는 진단 도구입니다 — 모든 원칙을 항상 적용하는 것이 아니라, 지금 보이는 증상에 어떤 원칙이 반응하는지를 매칭하는 것이 실무 사용법입니다.

## 이 글에서 다룰 문제

- 설계 원칙은 외워야 하는 규칙일까요, 진단 도구일까요?
- SRP, OCP, LSP, ISP, DIP는 각각 어떤 냄새에 반응할까요?
- KISS와 YAGNI는 언제 구조를 단순하게 붙잡아 줄까요?
- 이 설계 원칙을 무시하면 코드베이스가 어떻게 변질될까요?
- 팀 규모가 커질 때 이 원칙의 중요성은 어떻게 달라질까요?

원칙은 명령문이 아니라 판단 보조도구입니다. 코드 냄새가 났을 때 "지금 책임이 섞인 건가?", "불필요한 분기가 늘어난 건가?", "하위 타입이 상위 계약을 깨는 건가?" 같은 질문을 던지게 해 줍니다.

팀 차원에서도 효과가 있습니다. 원칙이 공통 어휘가 되면 코드 리뷰에서 긴 설명 없이도 문제를 빠르게 공유할 수 있습니다. "이건 SRP 위반 같아요"라는 말 한마디에 모두가 비슷한 그림을 떠올릴 수 있습니다.

## 전체 그림

코드 냄새를 먼저 보고, 어떤 원칙이 깨졌는지 짚은 뒤, 그 원칙에 맞춰 구조를 고치는 흐름이 실전 감각에 가깝습니다.

```text
설계 원칙을 쓰는 흐름

코드 냄새 발견
    │
    ▼
냄새 → 원칙 매칭
    │
    ▼
원칙 → 수정 방향 도출
    │
    ▼
구조 개선

냄새와 원칙을 연결하는 것이 핵심입니다.
원칙 이름을 외우는 것이 아닙니다.
```

## 기본 용어

- <strong>SRP</strong>: 모듈은 하나의 이유로만 바뀌어야 한다는 원칙입니다.
- <strong>OCP</strong>: 확장에는 열려 있고 기존 코드 수정에는 닫혀 있어야 한다는 원칙입니다.
- <strong>LSP</strong>: 하위 타입은 상위 타입 자리에 자연스럽게 들어갈 수 있어야 한다는 원칙입니다.
- <strong>ISP</strong>: 호출자가 쓰지 않는 메서드에 의존하지 않게 하자는 원칙입니다.
- <strong>DIP</strong>: 구체 구현보다 추상에 의존하자는 원칙입니다.
- <strong>KISS / YAGNI / DRY / 디미터 법칙</strong>: 단순함을 유지하고, 미리 만들지 말고, 반복을 의심하되, 멀리 있는 객체와 과하게 대화하지 말자는 보조 원칙입니다.

## 변경 전과 변경 후

**변경 전 — 모든 책임이 하나의 클래스에 (SRP 위반)**

```python
class UserService:
    def signup(self, payload: dict) -> None:
        # 검증
        if not payload.get("email"):
            raise ValueError("email required")
        if len(payload["password"]) < 8:
            raise ValueError("password too short")
        # 저장
        user_id = db.execute("INSERT INTO users ...", ...)
        # 이메일 발송
        smtp = smtplib.SMTP("smtp.example.com")
        smtp.sendmail(...)
        # 애널리틱스
        analytics.track("signup", user_id=user_id)
        # 빌링
        billing.create_free_trial(user_id=user_id)
        # 로깅
        logger.info(f"User {user_id} signed up")
```

**변경 후 — 각 책임이 분리됨 (SRP 적용)**

```python
class SignupValidator:
    def validate(self, payload: dict) -> None:
        if not payload.get("email"):
            raise ValueError("email required")
        if len(payload.get("password", "")) < 8:
            raise ValueError("password too short")

class UserRepo:
    def create(self, email: str, password_hash: str) -> str: ...

class WelcomeMailer:
    def send(self, email: str) -> None: ...

class SignupService:
    def __init__(self, validator: SignupValidator, repo: UserRepo,
                 mailer: WelcomeMailer) -> None:
        self._validator = validator
        self._repo = repo
        self._mailer = mailer

    def run(self, payload: dict) -> str:
        self._validator.validate(payload)
        user_id = self._repo.create(
            email=payload["email"],
            password_hash=hash_password(payload["password"]),
        )
        self._mailer.send(payload["email"])
        return user_id
```

두 번째 구조는 SRP를 적용한 예입니다. 거대한 클래스 하나가 하던 일을 협력하는 작은 단위들로 나눠 변경 이유를 줄였습니다.

## 원칙을 꺼내는 다섯 가지 상황

### 1단계 — "이 클래스가 왜 이렇게 큰가?" → SRP

```python
# 1_srp.py
# 변경 이유가 둘 이상이면 → 분리하세요.
class OrderService:
    # 가격 정책 변경 시 수정 → 한 가지 이유
    # 알림 채널 변경 시 수정 → 또 다른 이유
    # 저장소 변경 시 수정 → 또 다른 이유
    # 세 가지 이유 → 세 가지 클래스로 분리
    pass
```

수정 이유가 여러 개 보이면 SRP를 먼저 떠올리면 됩니다. 저장 정책과 알림 정책이 같은 클래스에 있다면 분리 후보입니다.

### 2단계 — "또 if-elif 체인이 늘었다" → OCP

```python
# 2_ocp.py
# 분기를 polymorphism 또는 registry로 대체하세요.

# Before (OCP 위반)
def process(event_type: str) -> None:
    if event_type == "payment":   # 새 타입 추가 = 이 함수 수정
        ...
    elif event_type == "refund":
        ...

# After (OCP 적용)
class EventHandler(Protocol):
    def handle(self, event: dict) -> None: ...

HANDLERS: dict[str, EventHandler] = {
    "payment": PaymentHandler(),
    "refund": RefundHandler(),
    # 새 타입 추가 = 여기에만 등록
}
```

새 기능이 들어올 때마다 기존 함수 분기를 수정해야 한다면 OCP를 의심해 볼 수 있습니다. 등록표나 다형성으로 확장 경로를 열 수 있는지 살펴봅니다.

### 3단계 — "하위 클래스가 예외를 던진다" → LSP

```python
# 3_lsp.py
# Before (LSP 위반)
class Shape:
    def area(self) -> float: ...
    def volume(self) -> float: ...   # 2D 도형에는 없는 개념

class Circle(Shape):
    def volume(self) -> float:
        raise NotImplementedError("원에는 부피가 없음")

# After (LSP 적용)
class Shape2D:
    def area(self) -> float: ...

class Shape3D:
    def area(self) -> float: ...
    def volume(self) -> float: ...
```

하위 타입이 상위 타입 자리에 들어갔을 때 호출자가 깨진다면, 상속 계층 자체가 잘못 설계됐을 수 있습니다.

### 4단계 — "쓰지도 않는 메서드를 왜 구현해야 하지?" → ISP

```python
# 4_isp.py
# Before (ISP 위반)
class Repository(Protocol):
    def read(self, id: str) -> dict: ...
    def write(self, data: dict) -> str: ...
    def delete(self, id: str) -> None: ...
    def bulk_import(self, data: list) -> None: ...  # 대부분의 구현체에 필요 없음

# After (ISP 적용)
class Readable(Protocol):
    def read(self, id: str) -> dict: ...

class Writable(Protocol):
    def write(self, data: dict) -> str: ...

class BulkImportable(Protocol):
    def bulk_import(self, data: list) -> None: ...
```

읽기만 필요한 구현체가 쓰기 메서드까지 억지로 품고 있다면 인터페이스가 너무 큽니다. 호출자 관점에서 쪼개는 편이 낫습니다.

### 5단계 — "도메인이 DB를 직접 안다" → DIP

```python
# 5_dip.py
# Before (DIP 위반)
from sqlalchemy.orm import Session  # 도메인이 ORM을 직접 import

class OrderDomain:
    def __init__(self, db: Session) -> None:  # 구체 구현에 의존
        self._db = db

# After (DIP 적용)
class OrderRepo(Protocol):  # 추상에 의존
    def get(self, order_id: str) -> Order: ...
    def save(self, order: Order) -> None: ...

class OrderDomain:
    def __init__(self, repo: OrderRepo) -> None:  # 추상에 의존
        self._repo = repo
```

핵심 규칙이 구체 저장소나 외부 SDK에 매달려 있으면 DIP를 떠올리면 됩니다. 추상을 도메인 쪽으로 끌어와 방향을 다시 잡습니다.

## 냄새와 원칙 매핑표

| 코드 냄새 | 관련 원칙 | 수정 방향 |
| --- | --- | --- |
| 클래스가 너무 크고 변경 이유가 많음 | SRP | 변경 이유별로 클래스 분리 |
| 새 기능 추가 시 기존 함수 계속 수정 | OCP | 다형성이나 등록 패턴으로 확장 지점 열기 |
| 하위 클래스가 `NotImplementedError` 던짐 | LSP | 상속 계층 재설계 또는 조합으로 변경 |
| 구현체가 쓰지 않는 메서드 구현 강요 | ISP | 인터페이스를 역할별로 분리 |
| 도메인 테스트에 DB·HTTP 연결 필요 | DIP | 포트를 도메인에 두고 어댑터 분리 |
| 비슷한 코드 여러 곳에 복사 | DRY | 단, 변경 이유가 같은 경우에만 통합 |
| 사용하지 않을 추상화 미리 추가 | YAGNI | 실제 필요할 때 추가 |
| 체이닝이 길어 `a.b.c.d.e()` 형태 | 디미터 법칙 | 직접 대화하는 객체 수를 줄이기 |

## 빠르게 검증해 보기

원칙을 암기하고 있는지보다, 냄새를 봤을 때 어떤 질문이 떠오르는지가 더 중요합니다. 최근 리뷰에서 봤던 코드를 하나 떠올리고 아래처럼 연결해 보세요.

```text
거대한 클래스 -> SRP
분기 체인 증가 -> OCP
하위 타입 예외 -> LSP
읽기 전용 구현이 write를 구현 -> ISP
도메인이 DB import -> DIP
```

**Expected output:** 냄새와 원칙, 다음 수정 방향이 한 줄로 이어지면 원칙이 실제 도구로 작동하고 있다는 뜻입니다.

이 연습이 잘 되면 코드 리뷰에서 "이건 이상하다"가 아니라 "이건 SRP 관점에서 분리 후보다"처럼 더 구체적으로 말할 수 있습니다.

## 실패 신호와 먼저 볼 것

| 실패 신호 | 먼저 볼 것 |
| --- | --- |
| 원칙 이름은 아는데 수정 방향이 안 보인다 | 냄새와 원칙을 먼저 짝지어 봅니다 |
| DRY를 적용할수록 결합이 커진다 | 반복보다 변경 이유가 같은지 확인합니다 |
| 작은 스크립트가 지나치게 무거워진다 | YAGNI와 KISS 강도를 다시 조정합니다 |

원칙은 만능 규칙이 아니라, 문제를 본 뒤 어떤 질문을 꺼낼지 정하는 진단 카드에 가깝습니다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 올바른 접근 |
| --- | --- | --- |
| DRY를 코드 중복 제거로만 이해 | 우연한 중복을 합치면 불필요한 결합 발생 | 변경 이유가 같을 때만 추출 |
| YAGNI를 무시하고 미래 대비 추상화 | 지금 필요 없는 복잡성이 생산성 저해 | 실제 두 번째 사용처가 생길 때 추상화 |
| 모든 원칙을 동시에 강제 | 설계가 과도하게 무거워짐 | 현재 코드에서 가장 문제 있는 부분에 먼저 적용 |
| SOLID를 작은 스크립트에 강제 | 5계층 아키텍처를 10줄 스크립트에 적용 | 시스템 크기에 맞게 원칙 강도 조절 |
| 원칙 이름을 근거로만 설명 | "SRP 위반이에요"로 끝내면 수정 방향 불명확 | 구체적인 냄새와 수정 방향을 함께 설명 |

## 이 코드에서 먼저 볼 점

- 각 원칙은 서로 다른 냄새를 겨냥합니다.
- 원칙은 코드를 판단만 하는 것이 아니라 수정 방향까지 제시합니다.
- 한 번에 하나씩 적용해야 가독성과 균형을 잃지 않습니다.

## 어디서 많이 헷갈릴까

DRY는 특히 자주 오해됩니다. 비슷해 보이는 코드를 너무 빨리 합치면 우연한 공통점 때문에 결합이 커질 수 있습니다. 반복 자체보다 변화의 이유가 같은지를 먼저 보는 편이 낫습니다.

YAGNI도 마찬가지입니다. 미래를 대비한다는 명분으로 아직 필요하지 않은 추상화를 미리 넣으면 현재 구조만 무거워집니다. 작은 시스템이라면 작은 원칙 강도로 시작하는 편이 대개 더 낫습니다.

## 실무에서는 이렇게 본다

코드 리뷰에서 원칙은 공통 언어가 됩니다. SRP 위반, OCP가 필요한 분기, LSP를 깨는 타입 계층 같은 표현이 팀 내에서 바로 이해되면 설계 논의가 훨씬 빨라집니다.

좋은 시니어 엔지니어는 원칙을 만능 규칙으로 들이대지 않습니다. 시스템 크기와 변경 압력을 보고 강도를 조절합니다. 작은 스크립트에 다섯 계층을 강요하지 않고, 큰 시스템에서는 필요한 경계를 더 분명히 세웁니다.

```python
# 원칙 체크리스트를 코드 리뷰 템플릿으로 사용하는 예
"""
코드 리뷰 설계 체크리스트

SRP: 이 클래스/함수의 변경 이유가 하나인가?
OCP: 새 기능 추가 시 기존 코드를 크게 수정하지 않아도 되는가?
LSP: 하위 타입이 상위 타입의 계약을 완전히 지키는가?
ISP: 호출자가 쓰지 않는 메서드에 의존하지 않는가?
DIP: 도메인이 구체 구현보다 추상에 기대는가?
KISS: 지금 이 복잡성이 정말 필요한가?
YAGNI: 아직 필요하지 않은 기능이 미리 들어가 있지 않은가?
DRY: 반복된 코드가 같은 이유로 함께 변경되는가?
"""
```

## SOLID 원칙 적용 전후 전체 예시

한 개의 주문 서비스를 SOLID 원칙 관점에서 개선하는 과정을 단계별로 보겠습니다.

```python
# ── 개선 전: 모든 원칙 위반 ────────────────────────

class OrderService:
    def process(self, order_data: dict) -> None:
        # SRP 위반: 검증, 가격, 저장, 알림, 로깅이 모두 여기에
        if not order_data.get("item_id"):
            raise ValueError("item_id required")

        # OCP 위반: 새 할인 타입 추가 = 이 함수 수정
        if order_data["discount_type"] == "vip":
            price = order_data["price"] * 0.8
        elif order_data["discount_type"] == "coupon":
            price = order_data["price"] * 0.9

        # DIP 위반: 구체 구현에 직접 의존
        import psycopg2
        conn = psycopg2.connect("postgresql://...")
        conn.execute("INSERT INTO orders ...", ...)

        # ISP 위반: 알림 인터페이스가 너무 큼
        notifier = BigNotifier()
        notifier.send_email(order_data["user_id"], "주문 완료")
        notifier.send_sms(order_data["user_id"], "주문 완료")
        notifier.log_to_analytics(order_data["user_id"], "order")


# ── 개선 후: 각 원칙 적용 ────────────────────────

# SRP: 각 클래스가 한 가지 책임
class OrderValidator:
    def validate(self, data: dict) -> None:
        if not data.get("item_id"):
            raise ValueError("item_id required")

# OCP: 새 할인 타입 추가 = 새 클래스, 기존 코드 수정 없음
class DiscountStrategy(Protocol):
    def apply(self, price: int) -> int: ...

class VipDiscount:
    def apply(self, price: int) -> int: return int(price * 0.8)

class CouponDiscount:
    def apply(self, price: int) -> int: return int(price * 0.9)

DISCOUNTS: dict[str, DiscountStrategy] = {
    "vip": VipDiscount(),
    "coupon": CouponDiscount(),
}

# DIP: 도메인이 추상에 의존
class OrderRepo(Protocol):
    def save(self, order: dict) -> None: ...

# ISP: 알림 인터페이스를 역할별로 분리
class EmailNotifier(Protocol):
    def send_email(self, user_id: str, msg: str) -> None: ...

class SmsNotifier(Protocol):
    def send_sms(self, user_id: str, msg: str) -> None: ...

# LSP: EmailNotifier를 구현하는 모든 클래스는 계약을 지킴
class SmtpEmailNotifier:
    def send_email(self, user_id: str, msg: str) -> None:
        email = user_repo.get_email(user_id)
        smtp.send(to=email, body=msg)

class OrderService:
    def __init__(self, validator: OrderValidator,
                 repo: OrderRepo,
                 email_notifier: EmailNotifier) -> None:
        self._validator = validator
        self._repo = repo
        self._email = email_notifier

    def process(self, order_data: dict) -> None:
        self._validator.validate(order_data)
        discount = DISCOUNTS.get(order_data.get("discount_type", ""), None)
        price = discount.apply(order_data["price"]) if discount else order_data["price"]
        self._repo.save({**order_data, "price": price})
        self._email.send_email(order_data["user_id"], "주문 완료")
```

개선 후에는 새 할인 타입을 추가해도 `OrderService`를 건드리지 않고, 도메인 테스트에 DB가 필요 없으며, 각 클래스를 독립적으로 교체할 수 있습니다.

## 원칙 적용 우선순위

모든 원칙을 동시에 적용하기 어렵다면 아래 순서로 시작하는 것이 실용적입니다.

```text
1순위: SRP
   이유: 가장 직접적으로 변경 비용을 낮춤
   언제: 클래스가 커지기 시작할 때

2순위: DIP
   이유: 테스트 가능성을 즉시 개선
   언제: 도메인 테스트에 DB가 필요할 때

3순위: OCP
   이유: 분기가 늘어나기 시작할 때
   언제: if-elif 체인이 3개 이상일 때

4순위: ISP
   이유: 인터페이스가 커지기 시작할 때
   언제: 구현체가 메서드를 비워두거나 예외 던질 때

5순위: LSP
   이유: 상속 계층이 생길 때
   언제: 하위 클래스가 상위 동작을 깰 때
```

## 운영 체크리스트

- [ ] 이 모듈은 하나의 이유로만 바뀌는가? (SRP)
- [ ] 새 기능을 넣을 때 기존 코드를 크게 수정하지 않아도 되는가? (OCP)
- [ ] 하위 타입이 상위 계약을 자연스럽게 지키는가? (LSP)
- [ ] 인터페이스가 실제 호출자 크기에 맞는가? (ISP)
- [ ] 도메인이 구체 구현보다 추상에 기대는가? (DIP)

## 연습 문제

1. 가장 큰 클래스 하나를 골라 SRP 위반 지점을 찾아 분리해 보세요.
2. `if-elif` 체인 하나를 OCP 관점에서 다시 설계해 보세요.
3. 지난해 만든 추상화 가운데 YAGNI에 어긋났던 사례를 하나 적어 보세요.

## 현업 적용 관점에서 다시 정리

원칙은 교과서 문장이 아니라 설계 결정의 필터입니다. SRP, OCP, DIP 같은 원칙은 "지금 무엇을 분리하고 무엇을 유지할지"를 선택하게 도와줍니다.

## 정리

SOLID·KISS·YAGNI·DRY는 외워야 하는 구호가 아니라 '코드에서 어떤 냄새가 날 때 어떤 질문을 던질지' 알려 주는 진단 도구입니다 — 모든 원칙을 항상 적용하는 것이 아니라, 지금 보이는 증상에 어떤 원칙이 반응하는지를 매칭하는 것이 실무 사용법입니다. 이 글에서는 전체 그림부터 현업 적용 관점에서 다시 정리까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **설계 원칙은 외워야 하는 규칙일까요, 진단 도구일까요?**
  - 진단 도구입니다. 원칙 이름을 외우는 것보다 "어떤 냄새가 어떤 원칙에 반응하는가"를 연결하는 것이 훨씬 더 실용적입니다. 원칙은 만능 규칙이 아니라, 문제를 본 뒤 어떤 질문을 꺼낼지 정하는 진단 카드에 가깝습니다.
- **SRP, OCP, LSP, ISP, DIP는 각각 어떤 냄새에 반응할까요?**
  - SRP: 클래스가 너무 크고 변경 이유가 많음. OCP: 새 기능마다 기존 함수를 수정. LSP: 하위 클래스가 예외를 던짐. ISP: 쓰지 않는 메서드를 구현해야 함. DIP: 도메인 테스트에 DB가 필요함.
- **KISS와 YAGNI는 언제 구조를 단순하게 붙잡아 줄까요?**
  - 필요하지 않은 추상화를 미리 추가하거나, 단순한 문제를 과하게 일반화할 때 YAGNI와 KISS가 제동을 겁니다. 코드 냄새를 먼저 보고, 어떤 원칙이 깨졌는지 짚은 뒤, 그 원칙에 맞춰 구조를 고치는 흐름이 실전 감각에 가깝습니다.
