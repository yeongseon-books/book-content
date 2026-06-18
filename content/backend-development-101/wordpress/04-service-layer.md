---
series: backend-development-101
episode: 4
title: "바이브코딩을 위한 백엔드 개발 기초 (4/10): Service Layer"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - Backend
  - Architecture
  - DesignPatterns
  - Python
  - DDD
seo_description: AI가 만든 코드에서 비즈니스 로직이 흩어지는 문제를 해결하는 Service Layer 패턴을 바이브코딩 관점에서 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 백엔드 개발 기초 (4/10): Service Layer

이 글은 **바이브코딩을 위한 백엔드 개발 기초** 시리즈의 4번째 글입니다. AI에게 코드를 맡기기 전에 백엔드가 어떻게 동작하는지 이해해야 원하는 결과를 얻을 수 있습니다.

---

AI로 API를 만들면 처음에는 controller에서 시작한 코드가 잘 동작합니다. 시간이 지나면서 같은 비즈니스 규칙이 REST 핸들러, CLI 스크립트, 배치 잡에서 각각 조금씩 다르게 구현됩니다. 운영 사고는 대개 여기서 시작합니다. "주문 생성"이라고 적혀 있는데 경로마다 쿠폰 검사 여부가 다릅니다. AI에게 수정을 요청해도 하나를 고치면 다른 경로에서 같은 버그가 재발합니다.

> 같은 규칙을 여러 입구에서 사용해야 한다면, 규칙은 반드시 service에 있어야 합니다.

## 이 글에서 다룰 문제

- 비즈니스 로직은 왜 controller도 repository도 아닌 service가 맡아야 할까요?
- controller, service, repository는 각각 어디까지 책임져야 할까요?
- 트랜잭션 경계는 어느 층에서 시작하는 편이 자연스러울까요?
- AI가 만든 코드에서 service가 없으면 어떤 문제가 생길까요?
- 바이브코딩에서 service layer를 언제, 어떻게 AI에게 요청해야 할까요?

## 바이브코딩과 Service Layer: AI가 흔히 만드는 문제

AI에게 "주문 생성 API"를 요청하면 대부분 controller 함수에 비즈니스 로직이 직접 들어갑니다. 이후 "관리자 API에서도 주문 생성이 필요해"라고 요청하면 같은 로직이 다른 핸들러에 복사됩니다. 세 번째 요청(CLI 재처리)이 오면 세 번째 복사본이 생깁니다.

이 패턴의 결과:

- 에러 메시지/코드 불일치로 클라이언트 처리 분기 증가
- 일부 경로에서만 사전 검증이 동작해 데이터 정합성 깨짐
- 버그 수정 시 세 파일이 아니라 세 시스템을 동시에 수정해야 함

## 책임 경계: Controller vs Service vs Repository

경계는 계층 이름이 아니라 "무엇을 알고 무엇을 몰라야 하는가"로 나눕니다.

| 구분 | Controller | Service | Repository |
| --- | --- | --- | --- |
| 주된 책임 | 요청/응답 변환, 인증 컨텍스트 진입, 예외 매핑 | 유스케이스 실행, 비즈니스 규칙, 트랜잭션 경계 | 저장소 접근, 조회/저장 쿼리 캡슐화 |
| 알아야 할 것 | HTTP status, header, path/query/body 파싱 | 도메인 규칙, 실행 순서, 외부 의존 조합 | 테이블/인덱스/쿼리 최적화 |
| 몰라야 할 것 | SQL 상세, 멀티 리포지토리 orchestration | Request 객체, HTTPException, 프레임워크 response 타입 | HTTP, 인증 토큰, 유스케이스 전체 맥락 |

경계가 헷갈릴 때는 질문을 한 번만 던지면 됩니다. "이 로직이 HTTP 없이도 같은 의미를 가져야 하는가?" 답이 예이면 service 영역입니다.

## 의존성 주입: service가 직접 생성하지 않게 만듭니다

AI가 만든 service 코드에서 흔한 문제는 service 내부에서 DB 세션이나 외부 클라이언트를 직접 생성하는 것입니다. 이렇게 하면 테스트를 실제 DB 없이 실행할 수 없습니다.

```python
# 나쁜 패턴: service가 직접 생성
class BadInvoiceService:
    def issue(self, order_id: str):
        session = SessionLocal()  # 직접 생성
        repo = InvoiceRepository(session)
        return repo.create_from_order(order_id)

# 좋은 패턴: 외부에서 주입
class InvoiceService:
    def __init__(self, invoice_repo):
        self.invoice_repo = invoice_repo  # 주입받음

    def issue(self, order_id: str):
        return self.invoice_repo.create_from_order(order_id)
```

의존성 주입을 사용하면 테스트에서 fake repository로 대체할 수 있고, 실패 케이스를 정교하게 주입할 수 있습니다.

## 트랜잭션 경계: 왜 service가 소유해야 하는가

트랜잭션은 기술 기능이 아니라 비즈니스 약속입니다. "A와 B는 함께 성공하거나 함께 실패해야 한다"는 약속은 유스케이스 문장에 들어 있습니다. AI에게 이를 명시하지 않으면 repository가 각자 commit하는 코드가 생성됩니다.

송금 예시에서 문제가 됩니다:
- `AccountRepository.debit()` 내부에서 commit
- `AccountRepository.credit()` 호출 중 예외 발생
- 결과: 출금은 반영, 입금은 실패

service가 트랜잭션을 소유하면 이 문제를 해결할 수 있습니다:

```python
class TransferService:
    def __init__(self, account_repo, session_factory):
        self.account_repo = account_repo
        self.session_factory = session_factory

    def transfer(self, from_id: str, to_id: str, amount: int):
        if amount <= 0:
            raise ValueError("이체 금액은 0보다 커야 합니다.")

        with self.session_factory() as session:
            with session.begin():
                # service가 트랜잭션 경계를 소유합니다
                self.account_repo.debit(session, from_id, amount)
                self.account_repo.credit(session, to_id, amount)
```

## Before/After: 비즈니스 로직 분리

### Before: controller에 흩어진 로직

```python
@router.post("/orders")
def create_order(payload: dict):
    # 검증이 여기에
    if payload.get("amount", 0) <= 0:
        raise HTTPException(400, "주문 금액은 0보다 커야 합니다.")

    # 비즈니스 로직이 여기에
    conn = get_db()
    result = conn.execute("INSERT INTO orders ...")
    return result
```

### After: service로 분리

```python
# service.py
class OrderService:
    def __init__(self, order_repo):
        self.order_repo = order_repo

    def create_order(self, data: CreateOrderInput):
        if data.amount <= 0:
            raise InvalidOrderAmountError("주문 금액은 0보다 커야 합니다.")
        return self.order_repo.save(data)

# router.py
@router.post("/orders")
def create_order(payload: CreateOrderRequest, service: OrderService = Depends(get_order_service)):
    try:
        order = service.create_order(CreateOrderInput(**payload.dict()))
        return order
    except InvalidOrderAmountError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

service는 HTTP를 모릅니다. 동일한 service를 REST, CLI, 배치에서 모두 재사용할 수 있습니다.

## AI가 만든 Service 코드에서 자주 하는 실수

| 안티패턴 | 증상 | 왜 문제인가 | AI에게 수정 요청 방법 |
| --- | --- | --- | --- |
| God Service | `UserService`가 회원가입, 결제, 알림, 통계까지 처리 | 변경 영향 범위가 폭발 | "유스케이스 단위로 service를 분리해줘" |
| Anemic Service | service가 repository passthrough만 수행 | 규칙이 controller/repository로 다시 흩어짐 | "비즈니스 검증 로직을 service에 추가해줘" |
| Service가 HTTP 직접 호출 | `requests.post()`를 service 내부에서 즉시 실행 | 실패 정책, 재시도, 관측성이 중복 | "외부 API 호출을 gateway 클래스로 분리해줘" |
| Service가 Request 객체 import | `from fastapi import Request` 후 직접 참조 | 프레임워크 종속으로 재사용성 하락 | "service는 FastAPI에 의존하지 않게 작성해줘" |
| Repository가 트랜잭션 소유 | repo 메서드마다 commit 수행 | 멀티 리포지토리 유스케이스에서 부분 커밋 발생 | "트랜잭션 경계를 service에서 관리하도록 수정해줘" |

## AI 팁: Service Layer를 AI에게 요청하는 방법

**레이어 분리 명시**: "비즈니스 로직을 service 클래스로 분리해줘. service는 FastAPI Request 객체를 직접 사용하지 않도록 해줘."

**트랜잭션 경계**: "주문 생성과 재고 차감을 하나의 트랜잭션으로 묶어줘. 트랜잭션 경계는 service에서 관리해줘."

**의존성 주입**: "service는 생성자로 repository를 주입받도록 작성해줘. 이렇게 하면 테스트에서 fake repository로 대체할 수 있어."

## 체크리스트

- [ ] 서비스 레이어의 역할을 설명할 수 있습니다.
- [ ] controller와 service의 책임 차이를 말할 수 있습니다.
- [ ] 트랜잭션 경계를 service에서 관리해야 하는 이유를 설명할 수 있습니다.
- [ ] AI가 만든 코드에서 비즈니스 로직이 controller에 있는지 확인할 수 있습니다.
- [ ] 의존성 주입 패턴을 사용해 테스트 가능한 service를 만들 수 있습니다.

## 처음 질문으로 돌아가기

- **비즈니스 로직은 왜 controller도 repository도 아닌 service가 맡아야 할까요?**
  - 같은 비즈니스 규칙을 REST, gRPC, CLI, 배치 등 여러 입구에서 재사용할 수 있기 때문입니다. controller나 repository에 두면 입구마다 규칙이 달라지는 사고가 생깁니다.
- **controller, service, repository는 각각 어디까지 책임져야 할까요?**
  - controller는 HTTP 변환, service는 비즈니스 규칙과 트랜잭션, repository는 데이터 접근만 담당합니다. 각 레이어는 다른 레이어의 세부 구현을 알지 못해야 합니다.
- **트랜잭션 경계는 어느 층에서 시작하는 편이 자연스러울까요?**
  - 유스케이스 문장("주문 생성과 재고 차감은 같이 성공해야 한다")이 service에 있으므로, 트랜잭션 경계도 service가 소유하는 것이 자연스럽습니다.

## 정리

Service Layer는 컨트롤러를 얇게 만들기 위한 미적 추상이 아닙니다. AI에게 여러 기능을 반복적으로 요청할 때, 비즈니스 규칙이 한 곳에 모여 있어야 각 요청이 일관된 결과를 냅니다. "service를 분리해줘", "service는 FastAPI에 의존하지 않게 해줘", "트랜잭션은 service에서 관리해줘"를 AI에게 명시하면 훨씬 안정적인 코드를 얻을 수 있습니다.

## 참고 자료

### 공식 문서

- [FastAPI dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)
- [Service Layer pattern (Martin Fowler)](https://martinfowler.com/eaaCatalog/serviceLayer.html)
- [Architecture Patterns with Python](https://www.cosmicpython.com/)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 백엔드 개발 기초 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [바이브코딩을 위한 백엔드 개발 기초 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- [바이브코딩을 위한 백엔드 개발 기초 (3/10): Routing과 Controller](./03-routing-and-controllers.md)
- **바이브코딩을 위한 백엔드 개발 기초 (4/10): Service Layer (현재 글)**
- [바이브코딩을 위한 백엔드 개발 기초 (5/10): Database Layer](./05-database-layer.md)
- [바이브코딩을 위한 백엔드 개발 기초 (6/10): 인증과 권한](./06-auth-and-authorization.md)
- [바이브코딩을 위한 백엔드 개발 기초 (7/10): Logging과 Error Handling](./07-logging-and-error-handling.md)
- [바이브코딩을 위한 백엔드 개발 기초 (8/10): 백엔드 테스트](./08-testing-the-backend.md)
- [바이브코딩을 위한 백엔드 개발 기초 (9/10): 백엔드 배포](./09-deploying-the-backend.md)
- [바이브코딩을 위한 백엔드 개발 기초 (10/10): 운영 가능한 백엔드 구조](./10-production-ready-backend.md)

<!-- toc:end -->

Tags: 바이브코딩, Backend, Architecture, DesignPatterns, Python, DDD
