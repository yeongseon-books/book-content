---
series: backend-development-101
episode: 4
title: "Backend Development 101 (4/10): Service Layer"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Backend
  - Architecture
  - DesignPatterns
  - Python
  - DDD
seo_description: 서비스 레이어의 역할과 비즈니스 로직을 모으는 기준을 정리하고, 의존성 주입과 트랜잭션 경계 설계를 통해 테스트 가능성을 높입니다.
last_reviewed: '2026-05-15'
---

# Backend Development 101 (4/10): Service Layer

이 글은 Backend Development 101 시리즈의 4번째 글입니다.

controller에서 시작한 코드가 시간이 지나면서 gRPC 핸들러, CLI 커맨드, 배치 잡으로 퍼지면 "같은 규칙"이 세 군데에서 조금씩 다르게 실행되는 문제가 생깁니다. 운영 사고는 대개 여기서 시작합니다. 엔드포인트마다 validation 문구가 다르고, 한 경로에서는 트랜잭션이 묶이는데 다른 경로에서는 부분 커밋이 일어납니다. 서비스는 살아 있는데 규칙이 살아 있지 않은 상태입니다.

![Backend Development 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/04/04-01-concept-at-a-glance.ko.png)
*Backend Development 101 4장 흐름 개요*

## 먼저 던지는 질문

- 비즈니스 로직은 왜 controller도 repository도 아닌 service가 맡아야 할까요?
- controller, service, repository는 각각 어디까지 책임져야 할까요?
- 트랜잭션 경계는 어느 층에서 시작하는 편이 자연스러울까요?

## Service Layer를 두는 이유: 입구가 늘어나도 규칙은 하나여야 합니다

서비스를 오래 운영하면 "API를 잘 만들었는가"보다 "규칙의 단일 출처를 지켰는가"가 더 중요해집니다. REST, gRPC, CLI, 배치는 전달 방식만 다를 뿐 결국 같은 비즈니스 행위를 실행해야 합니다.

예를 들어 `주문 생성` 규칙이 다음처럼 분산되면 문제가 생깁니다.

- REST controller: 쿠폰 만료 검사 수행
- gRPC handler: 쿠폰 검사 누락
- 배치 재처리: 포인트 차감 순서가 반대
- 운영 스크립트(CLI): 재고 잠금 없이 주문 생성

코드는 모두 "주문 생성"이라고 적혀 있지만, 실제 동작은 네 가지입니다. 이때 필요한 계층이 service입니다. service는 인터페이스 기술(HTTP, protobuf, argparse)이 아니라 비즈니스 행위 자체를 소유합니다.

> 같은 규칙을 여러 입구에서 사용해야 한다면, 규칙은 반드시 service에 있어야 합니다.

## 책임 경계: Controller vs Service vs Repository

경계는 계층 이름이 아니라 "무엇을 알고 무엇을 몰라야 하는가"로 나눕니다. 아래 표는 실무에서 가장 자주 사용하는 판단 기준입니다.

| 구분 | Controller | Service | Repository |
| --- | --- | --- | --- |
| 주된 책임 | 요청/응답 변환, 인증 컨텍스트 진입, 예외 매핑 | 유스케이스 실행, 비즈니스 규칙, 트랜잭션 경계 | 저장소 접근, 조회/저장 쿼리 캡슐화 |
| 알아야 할 것 | HTTP status, header, path/query/body 파싱 | 도메인 규칙, 실행 순서, 외부 의존 조합 | 테이블/인덱스/쿼리 최적화 |
| 몰라야 할 것 | SQL 상세, 멀티 리포지토리 orchestration | Request 객체, HTTPException, 프레임워크 response 타입 | HTTP, 인증 토큰, 유스케이스 전체 맥락 |
| 입력/출력 형태 | transport DTO | use case input/output 모델 | 도메인 엔티티 또는 persistence 모델 |
| 실패 처리 | 도메인 예외를 HTTP/gRPC 에러로 번역 | 도메인 예외 정의/발생 | DB 예외를 의미 있는 저장소 예외로 래핑 |
| 테스트 초점 | 라우팅, status code, serialization | 규칙 정확성, 트랜잭션, 협력 객체 호출 순서 | 쿼리 정확성, 매핑, 성능 |

경계가 헷갈릴 때는 질문을 한 번만 던지면 됩니다. "이 로직이 HTTP 없이도 같은 의미를 가져야 하는가?" 답이 예이면 service 영역입니다.

## 운영 시나리오 1: 같은 validation이 컨트롤러 3곳에 흩어진 경우

다음과 같은 흐름은 흔합니다.

1. 웹 팀이 `POST /orders`에 금액 검증 추가
2. 파트너 연동 팀이 gRPC `CreateOrder` 구현
3. 운영팀이 재처리용 CLI `order-replay` 추가

각 팀이 일정에 맞춰 "자기 입구"에서 검증을 넣으면 처음에는 빨라 보입니다. 세 달 뒤에는 다음 문제가 생깁니다.

- 에러 메시지/코드 불일치로 클라이언트 처리 분기 증가
- 일부 경로에서만 사전 검증이 동작해 데이터 정합성 깨짐
- 버그 수정 시 세 파일이 아니라 세 시스템을 동시에 수정해야 함

해결은 단순합니다. validation을 service 메서드 첫 단계로 올리고, 모든 입구가 같은 메서드를 호출하게 만듭니다.

```python
from dataclasses import dataclass


class InvalidOrderAmountError(Exception):
    pass


@dataclass(frozen=True)
class CreateOrderInput:
    customer_id: str
    amount: int


class OrderService:
    def __init__(self, order_repo):
        self.order_repo = order_repo

    def create_order(self, data: CreateOrderInput):
        # 비즈니스 규칙: 주문 금액은 0보다 커야 합니다.
        if data.amount <= 0:
            raise InvalidOrderAmountError("주문 금액은 0보다 커야 합니다.")
        return self.order_repo.save(data)
```

이후 REST/gRPC/CLI는 입력 변환만 담당합니다. 규칙은 단일 출처가 됩니다.

## 의존성 주입: service가 직접 생성하지 않게 만듭니다

### 생성자 주입이 기본인 이유

service 내부에서 `SessionLocal()`이나 외부 클라이언트를 직접 생성하면 테스트 대체가 어려워집니다. 테스트는 "무엇을 호출했는가"보다 "어떤 규칙을 적용했는가"를 검증해야 하는데, 생성 책임이 service에 붙어 있으면 경계가 고정됩니다.

```python
class UserService:
    def __init__(self, user_repo, password_hasher, clock):
        self.user_repo = user_repo
        self.password_hasher = password_hasher
        self.clock = clock

    def register(self, email: str, raw_password: str):
        if self.user_repo.exists(email):
            raise ValueError("이미 존재하는 이메일입니다.")
        password_hash = self.password_hasher.hash(raw_password)
        return self.user_repo.create(email=email, password_hash=password_hash, created_at=self.clock.now())
```

구성은 바깥에서 하고, service는 규칙 실행만 합니다.

### FastAPI `Depends()`는 조립 지점입니다

FastAPI에서 `Depends()`는 service의 책임이 아니라 wiring 도구입니다. controller에서 조립하고 service로 전달합니다.

```python
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


def get_user_service(session=Depends(get_db_session)):
    repo = SqlAlchemyUserRepository(session)
    return UserService(user_repo=repo, password_hasher=BcryptHasher(), clock=SystemClock())


@router.post("/users")
def create_user(payload: CreateUserRequest, service: UserService = Depends(get_user_service)):
    try:
        user = service.register(payload.email, payload.password)
        return {"id": user.id, "email": user.email}
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
```

핵심은 `Depends()`를 service 안으로 끌어들이지 않는 것입니다. service는 프레임워크 비의존 상태를 유지해야 재사용 범위가 넓어집니다.

### 테스트 가능성 차이

- DI 적용 전: 서비스 테스트가 실제 DB 연결/네트워크에 묶임
- DI 적용 후: fake repository와 stub clock으로 규칙만 단위 검증 가능

"서비스가 자기 DB 연결을 만든다"는 문장은 대개 "서비스를 빠르게 테스트할 수 없다"와 같은 뜻입니다.

## 트랜잭션 경계: 왜 service가 소유해야 하는가

트랜잭션은 기술 기능이 아니라 비즈니스 약속입니다. "A와 B는 함께 성공하거나 함께 실패해야 한다"는 약속은 유스케이스 문장에 들어 있습니다. repository는 자기 저장 동작만 알 뿐, 유스케이스 전체를 알지 못합니다.

### 잘못된 경계에서 생기는 부분 커밋

송금 예시를 보겠습니다.

- `AccountRepository.debit()` 내부에서 commit
- `AccountRepository.credit()` 호출 중 예외 발생

결과: 출금은 반영, 입금은 실패. 계좌 총합이 깨집니다.

이 문제는 SQL 문법이 아니라 경계 소유권 문제입니다.

### SQLAlchemy 세션 패턴(서비스 경계)

```python
class TransferService:
    def __init__(self, account_repo, ledger_repo, session_factory):
        self.account_repo = account_repo
        self.ledger_repo = ledger_repo
        self.session_factory = session_factory

    def transfer(self, from_id: str, to_id: str, amount: int):
        if amount <= 0:
            raise ValueError("이체 금액은 0보다 커야 합니다.")

        with self.session_factory() as session:
            # 서비스가 트랜잭션 경계를 소유합니다.
            with session.begin():
                self.account_repo.debit(session, from_id, amount)
                self.account_repo.credit(session, to_id, amount)
                self.ledger_repo.append_transfer_log(session, from_id, to_id, amount)
```

`session`을 repository에 넘겨 같은 트랜잭션 컨텍스트를 강제하면 멀티 리포지토리 작업이 원자적으로 묶입니다.

### 실무 규칙

- 서비스 메서드 하나가 유스케이스 트랜잭션 하나를 기본으로 가집니다.
- repository 메서드는 commit/rollback을 호출하지 않습니다.
- 외부 API 호출이 포함되면 로컬 트랜잭션과 분리 전략(outbox, saga, 재시도 정책)을 명시합니다.

## 에러 처리 경계: 도메인 예외와 HTTP 예외를 분리합니다

service가 `HTTPException`을 직접 던지기 시작하면 두 문제가 동시에 생깁니다.

- 도메인 규칙이 transport 프로토콜에 종속됨
- 동일 service를 gRPC/CLI에서 재사용할 때 예외 해석이 꼬임

권장 패턴은 service에서 도메인 예외를 던지고 controller에서 번역하는 방식입니다.

```python
class OrderNotFoundError(Exception):
    pass


class OrderAlreadyCanceledError(Exception):
    pass


class CancelOrderService:
    def __init__(self, repo):
        self.repo = repo

    def cancel(self, order_id: str):
        order = self.repo.find(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        if order.status == "canceled":
            raise OrderAlreadyCanceledError(order_id)
        order.cancel()
        self.repo.save(order)
        return order
```

```python
@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: str, service: CancelOrderService = Depends(get_cancel_order_service)):
    try:
        order = service.cancel(order_id)
        return {"id": order.id, "status": order.status}
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")
    except OrderAlreadyCanceledError:
        raise HTTPException(status_code=409, detail="이미 취소된 주문입니다.")
```

이 분리는 테스트에서도 이점을 줍니다. service 테스트는 HTTP status를 몰라도 되고, controller 테스트는 번역 매핑만 확인하면 됩니다.

## 서비스 조합: 직접 호출 vs 이벤트

유스케이스가 늘면 "서비스가 다른 서비스를 불러도 되는가"가 쟁점이 됩니다. 답은 상황에 따라 다르지만 기준은 분명합니다.

| 선택지 | 적합한 상황 | 주의점 |
| --- | --- | --- |
| Service A가 Service B를 직접 호출 | 같은 트랜잭션 안에서 강결합된 순차 실행이 필요할 때 | 순환 의존, 과도한 결합 감시 필요 |
| 도메인 이벤트 발행 후 구독 처리 | 비동기 후속 작업, 느슨한 결합, 독립 배포가 필요할 때 | 최종 일관성, 중복 처리(idempotency) 설계 필요 |

### 순환 의존을 피하는 구조

- `OrderService -> PaymentService` 호출은 가능
- `PaymentService -> OrderService` 역호출이 추가되면 경고 신호
- 공통 정책은 별도 policy/domain service로 추출
- 상태 전파는 이벤트로 전환

"일단 import"로 시작한 결합은 대개 테스트 fixture 폭발과 배포 순서 리스크로 돌아옵니다.

## 안티패턴 테이블: 현장에서 바로 식별하는 기준

| 안티패턴 | 증상 | 왜 문제인가 | 교정 방법 |
| --- | --- | --- | --- |
| God Service | `UserService`가 회원가입, 결제, 알림, 통계까지 처리 | 변경 영향 범위가 폭발하고 책임이 흐려짐 | 유스케이스 단위로 분리, 파일/클래스 경량화 |
| Anemic Service | service가 repository passthrough만 수행 | 규칙이 controller/repository로 다시 흩어짐 | validation/정책/오케스트레이션을 service에 복원 |
| Service가 HTTP 직접 호출 | `requests.post()`를 service 내부에서 즉시 실행 | 실패 정책, 타임아웃, 재시도, 관측성이 중복 | gateway/client 인터페이스 주입, resilience 정책 중앙화 |
| Service가 Request 객체 import | `from fastapi import Request` 후 직접 참조 | 프레임워크 종속으로 재사용성과 테스트성 하락 | 입력 DTO로 변환 후 service 호출 |
| Repository가 트랜잭션 소유 | repo 메서드마다 commit 수행 | 멀티 리포지토리 유스케이스에서 부분 커밋 발생 | 트랜잭션 경계를 service로 상향 |

## 운영 시나리오 2: 트랜잭션 경계가 잘못돼 부분 커밋이 난 사고

실제 사고는 화려하지 않습니다. 대개 다음과 같은 짧은 체인으로 발생합니다.

1. `create_order()`가 주문 row를 먼저 commit
2. 재고 차감 단계에서 deadlock 또는 timeout
3. 재시도 배치가 이미 생성된 주문을 또 읽어 중복 처리

장애 지표는 "주문 성공률"보다 "주문-재고 불일치"로 나타납니다. 서비스와 DB는 살아 있지만 데이터는 틀립니다.

예방 질문은 단 하나입니다. "이 유스케이스에서 반드시 같이 성공해야 하는 상태 변경은 무엇인가?" 답이 둘 이상이면 같은 service 트랜잭션에 묶어야 합니다.

## 운영 시나리오 3: 서비스가 DB 연결을 직접 만들어 테스트가 막힌 경우

다음 구조는 흔한 초기 구현입니다.

```python
class BadInvoiceService:
    def issue(self, order_id: str):
        # 서비스가 인프라를 직접 생성합니다.
        session = SessionLocal()
        repo = InvoiceRepository(session)
        return repo.create_from_order(order_id)
```

문제는 세 가지입니다.

- 테스트가 DB 준비/정리에 묶여 실행 속도가 급격히 느려짐
- 실패 케이스를 정교하게 주입하기 어려워 경계 검증 누락
- 연결/세션 수명 관리가 분산되어 운영에서 누수 가능성 증가

개선은 조립 위치를 바꾸는 것입니다.

```python
class InvoiceService:
    def __init__(self, invoice_repo):
        self.invoice_repo = invoice_repo

    def issue(self, order_id: str):
        return self.invoice_repo.create_from_order(order_id)
```

이제 테스트는 fake repository로 10ms 내에 끝나고, 실패 주입도 메서드 단위로 명확해집니다.

## 프로덕션 구조: services/ 디렉터리는 유스케이스 지도를 담습니다

서비스 파일 구조는 팀의 사고방식을 드러냅니다. 아래처럼 도메인별 하위 디렉터리를 두고, 유스케이스 중심으로 파일을 나누면 변경 영향 분석이 빨라집니다.

```text
app/
  controllers/
    orders.py
    users.py
  services/
    orders/
      create_order.py
      cancel_order.py
      refund_order.py
    payments/
      capture_payment.py
      reverse_payment.py
    users/
      register_user.py
  repositories/
    order_repository.py
    payment_repository.py
    user_repository.py
```

"한 파일에 서비스 클래스 하나"보다 "한 파일에 유스케이스 하나"가 운영 추적에 유리한 경우가 많습니다. 장애 보고서가 "취소 로직"을 가리킬 때 바로 해당 파일을 열 수 있기 때문입니다.

## 유스케이스 메서드 설계: input → validate → execute → side-effects → return

시니어가 서비스 메서드를 읽을 때 보는 것은 문법이 아니라 흐름입니다. 아래 순서를 고정하면 팀 내 일관성이 올라갑니다.

1. input 정규화
2. validate(도메인 규칙)
3. execute(상태 변경)
4. side-effects(이벤트/알림/감사 로그)
5. return(명시적 결과)

```python
class PlaceOrderService:
    def __init__(self, order_repo, inventory_repo, event_bus, session_factory):
        self.order_repo = order_repo
        self.inventory_repo = inventory_repo
        self.event_bus = event_bus
        self.session_factory = session_factory

    def execute(self, cmd: PlaceOrderCommand) -> PlaceOrderResult:
        # 1) input
        customer_id = cmd.customer_id.strip()

        # 2) validate
        if cmd.total_amount <= 0:
            raise InvalidOrderAmountError("주문 금액은 0보다 커야 합니다.")

        with self.session_factory() as session:
            with session.begin():
                # 3) execute
                self.inventory_repo.reserve(session, cmd.items)
                order = self.order_repo.create(session, customer_id, cmd.items, cmd.total_amount)

                # 4) side-effects
                self.event_bus.publish("OrderPlaced", {"order_id": order.id})

        # 5) return
        return PlaceOrderResult(order_id=order.id, status=order.status)
```

메서드 길이를 줄이기 위해 흐름을 숨기면 오히려 유지보수성이 내려갑니다. 읽는 사람이 "어디서 검증했고 어디서 커밋했는지"를 10초 안에 찾을 수 있어야 합니다.

## 흔한 실수와 WHY: 시니어가 바로 잡는 관점

| 실수 | 팀이 자주 하는 변명 | 실제 위험 | 시니어 관점의 교정 |
| --- | --- | --- | --- |
| 컨트롤러에서 규칙 처리 | "엔드포인트 하나라서 빠릅니다" | 입구가 늘 때 규칙이 분기 | 처음부터 service 메서드 호출로 고정 |
| 서비스에서 HTTPException 발생 | "에러코드 맞추기 편합니다" | transport 종속, 재사용성 붕괴 | 도메인 예외로 통일 후 경계 번역 |
| 서비스가 DB 세션 생성 | "DI 설정이 번거롭습니다" | 테스트 비용 폭증, 수명 관리 분산 | composition root에서 주입 |
| 리포지토리에서 commit | "쿼리랑 같이 닫는 게 안전합니다" | 멀티 작업 원자성 깨짐 | 유스케이스 기준 트랜잭션 상향 |
| 서비스 간 양방향 호출 | "기능을 재사용하고 싶습니다" | 순환 의존, 배포 리스크 | 단방향 호출 또는 이벤트 전환 |

## 코드 리뷰에서 바로 쓰는 체크리스트

- 이 규칙이 REST/gRPC/CLI 어디서 호출돼도 동일하게 동작하는가?
- service가 `Request`, `HTTPException`, framework response를 import하는가?
- 트랜잭션 시작/종료가 service에서 보이는가?
- repository가 commit/rollback을 소유하고 있지 않은가?
- 서비스 테스트가 실제 DB 없이 핵심 규칙을 검증할 수 있는가?

체크리스트는 문서가 아니라 품질 게이트입니다. PR에서 한 항목이라도 "아니오"면 다음 장애의 씨앗일 가능성이 높습니다.

## 정리

Service Layer는 컨트롤러를 얇게 만들기 위한 미적 추상이 아닙니다. 여러 인터페이스가 같은 비즈니스 규칙을 공유하게 만드는 운영 안전장치입니다. DI는 테스트와 교체 가능성을 열고, 트랜잭션 경계를 service가 소유해야 멀티 저장소 유스케이스에서 원자성을 지킬 수 있습니다. 도메인 예외를 경계에서 번역하면 transport가 바뀌어도 규칙 코드는 흔들리지 않습니다.

## 처음 질문으로 돌아가기

- **비즈니스 로직은 왜 controller도 repository도 아닌 service가 맡아야 할까요?**
  - REST, gRPC, CLI, 배치처럼 입구가 늘어도 같은 유스케이스 규칙을 한 곳에서 실행해야 단일 출처가 유지됩니다. controller에 두면 인터페이스마다 규칙이 분기되고, repository에 두면 저장 기술 세부와 비즈니스 판단이 섞여 변경 비용이 급격히 커집니다.
- **controller, service, repository는 각각 어디까지 책임져야 할까요?**
  - controller는 요청/응답 번역, service는 규칙과 실행 순서 및 트랜잭션, repository는 영속성 접근을 담당해야 합니다. "HTTP 없이도 의미가 같아야 하는 로직인가"라는 기준으로 service 책임을 판별하면 경계가 안정됩니다.
- **트랜잭션 경계는 어느 층에서 시작하는 편이 자연스러울까요?**
  - 유스케이스 전체 성공/실패를 결정하는 층인 service가 시작점이 되어야 합니다. 그래야 멀티 repository 작업을 원자적으로 묶고 부분 커밋 사고를 막을 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Backend Development 101 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [Backend Development 101 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- [Backend Development 101 (3/10): Routing과 Controller](./03-routing-and-controllers.md)
- **Service Layer (현재 글)**
- Database Layer (예정)
- 인증과 권한 (예정)
- Logging과 Error Handling (예정)
- 백엔드 테스트 (예정)
- 백엔드 배포 (예정)
- 운영 가능한 백엔드 구조 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [FastAPI dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)

- [Service Layer pattern (Martin Fowler)](https://martinfowler.com/eaaCatalog/serviceLayer.html)
- [DDD reference (Eric Evans)](https://www.domainlanguage.com/ddd/reference/)
- [Architecture Patterns with Python](https://www.cosmicpython.com/)

Tags: Backend, Architecture, DesignPatterns, Python, DDD
