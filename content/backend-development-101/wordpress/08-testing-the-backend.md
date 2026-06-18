---
series: backend-development-101
episode: 8
title: "바이브코딩을 위한 백엔드 개발 기초 (8/10): 백엔드 테스트"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - Backend
  - Testing
  - Pytest
  - Python
  - QualityAssurance
seo_description: AI가 만든 백엔드 코드를 안전하게 수정하려면 테스트가 필요합니다. 바이브코딩 관점에서 pytest와 FastAPI TestClient로 테스트를 구축하는 방법을 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 백엔드 개발 기초 (8/10): 백엔드 테스트

이 글은 **바이브코딩을 위한 백엔드 개발 기초** 시리즈의 8번째 글입니다. AI에게 코드를 맡기기 전에 백엔드가 어떻게 동작하는지 이해해야 원하는 결과를 얻을 수 있습니다.

---

AI로 빠르게 기능을 추가하다가 자주 망가지는 팀과, 빠르게 추가해도 안정적인 팀의 차이는 구현 속도보다 검증 방식에서 갈립니다. 바이브코딩으로 코드를 생성하면 "로컬에서 한 번 눌러 보고" 배포하는 습관이 생기기 쉽습니다. 코드가 커질수록 실패 비용이 기하급수로 늘어납니다. 테스트가 있으면 AI에게 리팩터링을 요청할 때도, 기능을 추가할 때도 회귀 여부를 빠르게 확인할 수 있습니다.

> 백엔드 테스트의 핵심 질문은 '커버리지 몇 %인가'가 아니라 '배포 직전에 이 테스트를 통과했다는 사실로부터 무엇을 보장할 수 있는가'입니다.

## 이 글에서 다룰 문제

- unit, integration, E2E 테스트는 각각 무엇을 검증할까요?
- pytest로 service를 어떻게 테스트할 수 있을까요?
- FastAPI `TestClient`는 endpoint를 어떻게 검증하게 해 줄까요?
- AI에게 테스트 코드를 요청할 때 어떻게 해야 유용한 테스트가 나올까요?
- 바이브코딩 프로젝트에서 최소한으로 갖춰야 할 테스트는 무엇일까요?

## 바이브코딩과 테스트: AI가 만드는 테스트의 한계

AI에게 테스트를 요청하면 코드가 나옵니다. 하지만 종종 다음 문제가 있습니다:

- 성공 케이스만 검증하고 실패 케이스가 없음
- mock을 과다 사용해서 실제 계약 불일치를 놓침
- 모든 테스트를 E2E로 작성해서 느리고 원인 추적이 어려움
- 커버리지 숫자는 높지만 실제 고위험 분기는 검증 안 됨

테스트를 단순히 많이 쓰면 품질이 올라간다고 생각하기 쉽습니다. 실제로는 비율과 목적이 더 중요합니다.

## 테스트 피라미드: 비율이 중요합니다

| 레벨 | 검증 대상 | 실행 속도 | 주로 잡는 결함 |
|---|---|---|---|
| Unit | 함수/클래스의 비즈니스 규칙 | 매우 빠름 (ms) | 분기 로직 오류, 계산/검증 실수 |
| Integration | 모듈 간 협력, DB/HTTP 경계 | 보통 (수십~수백 ms) | 직렬화 불일치, 상태 전이 오류 |
| E2E | 사용자 시나리오 전체 경로 | 느림 (초~분) | 배포/인증/인프라 경계 문제 |

안정적인 비율: "많은 unit + 필요한 integration + 소수의 핵심 E2E"

## Unit 테스트: Service 비즈니스 규칙 검증

unit 테스트의 목적은 "판단"을 검증하는 것입니다. DB나 외부 API 없이 service의 비즈니스 규칙만 확인합니다.

```python
from unittest.mock import Mock

def test_create_applies_discount_and_persists_order():
    inventory_repo = Mock()
    order_repo = Mock()
    discount_policy = Mock()

    inventory_repo.get_stock.return_value = 20
    discount_policy.for_user.return_value = 0.1  # 10% 할인
    order_repo.insert.return_value = {"id": 101, "total_price": 18000}

    service = OrderService(inventory_repo, order_repo, discount_policy)
    result = service.create(CreateOrderCommand(user_id=7, sku="A-100", quantity=2))

    order_repo.insert.assert_called_once()
    payload = order_repo.insert.call_args.args[0]
    assert payload["total_price"] == 18000  # 20000 * 0.9
    assert result["id"] == 101

def test_create_raises_when_stock_is_insufficient():
    inventory_repo = Mock()
    order_repo = Mock()
    discount_policy = Mock()

    inventory_repo.get_stock.return_value = 1  # 재고 1개

    service = OrderService(inventory_repo, order_repo, discount_policy)

    try:
        service.create(CreateOrderCommand(user_id=7, sku="A-100", quantity=2))  # 2개 주문
        assert False, "예외가 발생해야 합니다"
    except InsufficientStockError:
        pass

    order_repo.insert.assert_not_called()  # 저장이 일어나지 않아야 함
```

핵심: "재고 부족이면 저장하지 않는다" 같은 비즈니스 계약을 빠르게 검증합니다.

## Integration 테스트: FastAPI TestClient로 HTTP 계약 검증

TestClient로 실제 HTTP 계약을 검증합니다. 서버를 별도로 실행할 필요 없습니다.

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user_returns_201_and_shape():
    payload = {
        "email": "alice@example.com",
        "name": "Alice",
        "password": "Secret123!",
    }

    response = client.post("/users", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert set(body.keys()) == {"id", "email", "name", "created_at"}
    assert body["email"] == payload["email"]
    assert isinstance(body["id"], int)

def test_create_user_rejects_invalid_email():
    response = client.post(
        "/users",
        json={"email": "not-an-email", "name": "Alice", "password": "Secret123!"},
    )

    assert response.status_code == 422
```

검증 대상: HTTP 상태 코드, 응답 JSON 스키마, 에러 구조의 일관성.

## Before/After: 테스트 개선

### Before: AI가 자주 만드는 성공 케이스만 검증

```python
def test_create_order():
    response = client.post("/orders", json={"item_id": 1, "quantity": 2})
    assert response.status_code == 200  # 201이어야 할 수도 있음
    # 실패 케이스 없음
```

### After: 성공과 실패 케이스 모두 검증

```python
def test_create_order_success():
    response = client.post("/orders", json={"item_id": 1, "quantity": 2})
    assert response.status_code == 201
    body = response.json()
    assert "id" in body
    assert body["quantity"] == 2

def test_create_order_rejects_zero_quantity():
    response = client.post("/orders", json={"item_id": 1, "quantity": 0})
    assert response.status_code == 400
    assert "error" in response.json()

def test_create_order_requires_auth():
    # 인증 없이 요청
    response = client.post("/orders", json={"item_id": 1, "quantity": 1})
    assert response.status_code == 401
```

## AI가 만든 테스트 코드에서 자주 하는 실수

| 실수 | 왜 위험한가 | AI에게 수정 요청 방법 |
| --- | --- | --- |
| E2E 중심으로만 테스트 작성 | 느려서 자주 못 돌리고 원인 추적이 어려움 | "unit과 integration 테스트를 분리해줘" |
| mock 과다 사용 | 실제 계약 불일치가 숨어도 통과 | "API 계약은 TestClient로 integration 테스트를 작성해줘" |
| 성공 경로만 검증 | 장애 시 500/타임아웃 경로 무방비 | "실패 케이스도 성공 케이스와 같은 비중으로 작성해줘" |
| 커버리지 숫자 집착 | 의미 없는 테스트 양산 | "인증 실패, 결제 취소, 권한 우회 같은 고위험 분기를 먼저 검증해줘" |

## AI 팁: 테스트를 AI에게 요청하는 방법

**테스트 분리 요청**: "service 비즈니스 규칙을 검증하는 unit 테스트와, API HTTP 계약을 검증하는 integration 테스트를 분리해서 작성해줘."

**실패 케이스 명시**: "성공 케이스뿐만 아니라 인증 실패, 권한 부족, 입력 검증 실패, 재고 부족 케이스도 테스트해줘."

**CI 연동**: "pytest를 GitHub Actions에서 자동 실행하도록 설정해줘. E2E 테스트는 별도 job으로 분리해줘."

## 체크리스트

- [ ] unit, integration, E2E 테스트의 차이를 설명할 수 있습니다.
- [ ] pytest로 service 비즈니스 규칙을 Mock을 사용해 검증할 수 있습니다.
- [ ] FastAPI TestClient로 HTTP 상태 코드와 응답 스키마를 검증할 수 있습니다.
- [ ] 성공 케이스와 실패 케이스를 모두 작성해야 하는 이유를 말할 수 있습니다.
- [ ] AI가 만든 테스트 코드에서 성공 케이스만 있는 경우를 발견할 수 있습니다.

## 처음 질문으로 돌아가기

- **unit, integration, E2E 테스트는 각각 무엇을 검증할까요?**
  - unit은 비즈니스 규칙(빠름), integration은 레이어 간 협력과 HTTP 계약(중간), E2E는 사용자 시나리오 전체(느림)를 검증합니다. 각각 다른 종류의 버그를 잡습니다.
- **pytest로 service를 어떻게 테스트할 수 있을까요?**
  - Mock으로 repository와 외부 의존성을 대체하고, service의 비즈니스 규칙만 고립해서 검증합니다. DB 없이 밀리초 단위로 실행됩니다.
- **FastAPI `TestClient`는 endpoint를 어떻게 검증하게 해 줄까요?**
  - 실제 서버를 실행하지 않고 HTTP 요청을 시뮬레이션합니다. 상태 코드, 응답 스키마, 에러 포맷을 검증할 수 있습니다.

## 정리

바이브코딩으로 빠르게 만든 코드도 테스트가 있으면 안전하게 수정할 수 있습니다. AI에게 "service unit 테스트와 API integration 테스트를 분리해줘", "성공과 실패 케이스를 모두 작성해줘", "CI에서 자동 실행되도록 설정해줘"를 요청하면 변경 안정성을 확보할 수 있습니다.

## 참고 자료

### 공식 문서

- [pytest documentation](https://docs.pytest.org/en/stable/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)
- [Testing pyramid (Martin Fowler)](https://martinfowler.com/articles/practical-test-pyramid.html)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 백엔드 개발 기초 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [바이브코딩을 위한 백엔드 개발 기초 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- [바이브코딩을 위한 백엔드 개발 기초 (3/10): Routing과 Controller](./03-routing-and-controllers.md)
- [바이브코딩을 위한 백엔드 개발 기초 (4/10): Service Layer](./04-service-layer.md)
- [바이브코딩을 위한 백엔드 개발 기초 (5/10): Database Layer](./05-database-layer.md)
- [바이브코딩을 위한 백엔드 개발 기초 (6/10): 인증과 권한](./06-auth-and-authorization.md)
- [바이브코딩을 위한 백엔드 개발 기초 (7/10): Logging과 Error Handling](./07-logging-and-error-handling.md)
- **바이브코딩을 위한 백엔드 개발 기초 (8/10): 백엔드 테스트 (현재 글)**
- [바이브코딩을 위한 백엔드 개발 기초 (9/10): 백엔드 배포](./09-deploying-the-backend.md)
- [바이브코딩을 위한 백엔드 개발 기초 (10/10): 운영 가능한 백엔드 구조](./10-production-ready-backend.md)

<!-- toc:end -->

Tags: 바이브코딩, Backend, Testing, Pytest, Python, QualityAssurance
