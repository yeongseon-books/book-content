---
series: backend-development-101
episode: 8
title: "Backend Development 101 (8/10): 백엔드 테스트"
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
  - Testing
  - Pytest
  - Python
  - QualityAssurance
seo_description: pytest와 TestClient로 안전한 백엔드 변경 환경을 만드는 방법입니다
last_reviewed: '2026-05-15'
---

# Backend Development 101 (8/10): 백엔드 테스트

기능을 빠르게 추가하는 팀과, 빠르게 추가하다가 자주 망가지는 팀의 차이는 구현 속도보다 검증 방식에서 갈립니다. 로컬에서 한 번 눌러 보고 끝내는 습관으로는 코드가 커질수록 실패 비용이 기하급수로 늘어납니다. 반대로 테스트가 설계되어 있으면 리팩터링, 의존성 교체, 버그 수정이 모두 예측 가능한 작업으로 바뀝니다.

이 글은 Backend Development 101 시리즈의 8번째 글입니다.

백엔드 테스트를 공부할 때 가장 먼저 부딪히는 문제는 기술이 아니라 경계입니다. 어디까지를 unit으로 보고, 어디서부터 integration으로 올리고, E2E는 몇 개만 두어야 유지 가능한지 기준이 흔들리기 쉽습니다. pytest 문법을 아는 것과 운영 가능한 테스트 세트를 설계하는 것은 다른 역량이기 때문입니다.

이 글에서는 테스트 피라미드의 경제성을 먼저 정리하고, FastAPI + pytest 환경에서 service 단위 테스트, TestClient 기반 통합 테스트, 테스트 데이터베이스 전략, 커버리지 해석, CI 연동까지 하나의 흐름으로 연결하겠습니다. 목표는 테스트 코드를 "작성"하는 수준이 아니라, 변경 안정성을 "운영"하는 기준을 잡는 것입니다.

![Backend Development 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/08/08-01-concept-at-a-glance.ko.png)
*Backend Development 101 8장 흐름 개요*

## 먼저 던지는 질문

- unit, integration, E2E 테스트는 각각 무엇을 검증할까요?
- pytest로 service를 어떻게 테스트할 수 있을까요?
- FastAPI `TestClient`는 endpoint를 어떻게 검증하게 해 줄까요?

## 테스트를 분류하는 기준: 피라미드가 먼저입니다

테스트를 단순히 "많이" 쓰면 품질이 올라간다고 생각하기 쉽습니다. 실제로는 비율이 더 중요합니다. 모든 검증을 E2E로 몰면 실패 원인 파악이 느려지고, 실행 시간이 길어져 개발 루프가 깨집니다. 반대로 unit만 많으면 시스템 경계에서 발생하는 계약 불일치를 놓칩니다.

테스트 피라미드는 이 균형을 비용 관점으로 설명합니다.

| 레벨 | 검증 대상 | 대표 도구 | 실행 속도 | 유지 비용 | 주로 잡는 결함 |
|---|---|---|---|---|---|
| Unit | 함수/클래스의 비즈니스 규칙 | pytest, mock | 매우 빠름 (ms) | 낮음 | 분기 로직 오류, 계산/검증 실수 |
| Integration | 모듈 간 협력, DB/HTTP 경계 | pytest, FastAPI TestClient | 보통 (수십~수백 ms) | 중간 | 직렬화 불일치, 상태 전이 오류, 의존성 연결 문제 |
| E2E | 사용자 시나리오 전체 경로 | Playwright, API smoke | 느림 (초~분) | 높음 | 배포/인증/인프라 경계 문제, 실제 흐름 단절 |

실무에서 안정적인 비율은 팀과 도메인에 따라 다르지만, 대체로 "많은 unit + 필요한 integration + 소수의 핵심 E2E"가 유지 비용 대비 효과가 가장 좋습니다. 결제, 인증, 권한 같은 고위험 경로는 integration과 E2E를 의도적으로 두껍게 가져가고, 단순 조회 API는 unit 중심으로 얇게 유지하는 방식이 현실적입니다.

## Unit 테스트: 서비스 판단을 고립해서 검증합니다

unit 테스트의 목적은 함수 호출 자체가 아니라 "판단"을 검증하는 것입니다. repository, 외부 API, 메시지 브로커 같은 의존성은 테스트 대상이 아니라 협력자이므로 mock이나 fake로 대체하고, 서비스 계층의 규칙만 확인합니다.

아래 예시는 `OrderService`가 할인 정책과 재고 정책을 어떻게 적용하는지 고립해서 검증합니다.

```python
from dataclasses import dataclass
from unittest.mock import Mock

@dataclass
class CreateOrderCommand:
    user_id: int
    sku: str
    quantity: int

class InsufficientStockError(Exception):
    pass

class OrderService:
    def __init__(self, inventory_repo, order_repo, discount_policy):
        self.inventory_repo = inventory_repo
        self.order_repo = order_repo
        self.discount_policy = discount_policy

    def create(self, cmd: CreateOrderCommand):
        stock = self.inventory_repo.get_stock(cmd.sku)
        if stock < cmd.quantity:
            raise InsufficientStockError("재고가 부족합니다")

        discount_rate = self.discount_policy.for_user(cmd.user_id)
        subtotal = 10000 * cmd.quantity
        total = int(subtotal * (1 - discount_rate))

        return self.order_repo.insert(
            {
                "user_id": cmd.user_id,
                "sku": cmd.sku,
                "quantity": cmd.quantity,
                "total_price": total,
            }
        )

def test_create_applies_discount_and_persists_order():
    inventory_repo = Mock()
    order_repo = Mock()
    discount_policy = Mock()

    inventory_repo.get_stock.return_value = 20
    discount_policy.for_user.return_value = 0.1
    order_repo.insert.return_value = {"id": 101, "total_price": 18000}

    service = OrderService(inventory_repo, order_repo, discount_policy)
    result = service.create(CreateOrderCommand(user_id=7, sku="A-100", quantity=2))

    order_repo.insert.assert_called_once()
    payload = order_repo.insert.call_args.args[0]
    assert payload["total_price"] == 18000
    assert result["id"] == 101

def test_create_raises_when_stock_is_insufficient():
    inventory_repo = Mock()
    order_repo = Mock()
    discount_policy = Mock()

    inventory_repo.get_stock.return_value = 1
    service = OrderService(inventory_repo, order_repo, discount_policy)

    try:
        service.create(CreateOrderCommand(user_id=7, sku="A-100", quantity=2))
        assert False, "예외가 발생해야 합니다"
    except InsufficientStockError:
        pass

    order_repo.insert.assert_not_called()
```

핵심은 두 가지입니다. 첫째, 외부 시스템의 성공/실패를 서비스 테스트에 끌어들이지 않습니다. 둘째, 내부 구현 세부사항이 아니라 입력 대비 결과와 부작용 여부를 봅니다. `for_user`를 몇 번 호출했는지보다 "재고 부족이면 저장하지 않는다" 같은 비즈니스 계약이 더 중요합니다.

## Integration 테스트: 실제 HTTP 계약을 검증합니다

integration 테스트에서는 FastAPI `TestClient`로 라우터, 의존성 주입, 검증기, 직렬화까지 실제 요청 경로를 통과시킵니다. 서버 프로세스를 별도 기동하지 않아도 HTTP 레벨의 계약을 확인할 수 있기 때문에, API 백엔드에서는 비용 대비 효과가 매우 큽니다.

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
    errors = response.json()["detail"]
    assert any(item["loc"][-1] == "email" for item in errors)
```

여기서 확인하는 대상은 "HTTP 계약"입니다.

- 요청이 유효하면 상태 코드가 201인지
- 응답 JSON의 스키마가 약속과 일치하는지
- 유효성 실패 시 422와 오류 구조가 일관적인지

integration 테스트가 부족하면 실제 클라이언트가 보는 실패를 놓치기 쉽습니다. unit 테스트에서는 모두 통과했는데 모바일 앱에서만 깨지는 문제 대부분이 이 계층의 공백에서 나옵니다.

## 데이터베이스 테스트: 격리 전략을 설계해야 유지됩니다

DB가 포함되는 순간 테스트가 느려지고 불안정해진다는 인식이 있습니다. 원인은 "DB를 쓴다"가 아니라 "격리를 설계하지 않는다"에 가깝습니다. 테스트마다 상태를 독립시키고, 종료 시 원복되는 구조를 만들면 신뢰도와 속도를 함께 가져갈 수 있습니다.

### 1) 테스트 데이터베이스 분리

운영 DB와 완전히 분리된 URL을 사용해야 합니다. `.env.test` 또는 CI 환경 변수에서 명시적으로 설정합니다.

```python
# settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "dev"
    database_url: str

def get_settings() -> Settings:
    return Settings()
```

테스트 실행 시 `APP_ENV=test`, `DATABASE_URL=postgresql://.../app_test`처럼 주입합니다. 코드에서 환경별 URL을 분기하는 하드코딩보다 환경 변수를 강제하는 편이 안전합니다.

### 2) fixture + 트랜잭션 롤백

아래 패턴은 테스트마다 트랜잭션을 열고 종료 시 롤백해 상태를 격리합니다.

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base

@pytest.fixture(scope="session")
def engine():
    # 테스트 환경에서는 인메모리 sqlite를 예시로 사용합니다.
    # 프로젝트에 따라 dockerized postgres를 쓰는 편이 더 현실적일 수 있습니다.
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

테스트 간 데이터 누수가 사라지면 순서 의존 테스트가 줄고, CI 재현성이 크게 올라갑니다.

### 3) factory_boy 패턴으로 테스트 데이터 표현력 높이기

하드코딩된 dict를 매 테스트마다 복붙하면 의미가 사라집니다. `factory_boy`를 쓰면 "무엇을 준비했는지"가 도메인 언어로 드러납니다.

```python
import factory
from app.models import User

class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    name = "Tester"
    is_active = True
```

`UserFactory(is_active=False)`처럼 의도를 직접 표현할 수 있어 테스트 가독성과 수정 비용이 동시에 좋아집니다.

## pytest 패턴: 반복을 구조로 바꾸는 기술

pytest를 잘 쓰는 팀은 테스트 개수를 늘리는 대신 중복을 구조화합니다. 가장 효과가 큰 네 가지 패턴은 fixture, parametrize, `conftest.py`, marker입니다.

### fixture

fixture는 준비/정리 코드를 공유합니다. 특히 API 클라이언트, DB 세션, 인증 토큰, 샘플 데이터 같은 반복 자원에서 효과가 큽니다.

### parametrize

동일한 로직을 다양한 입력으로 검증할 때 테스트를 복제하지 않고 케이스를 선언합니다.

```python
import pytest

@pytest.mark.parametrize(
    "email,expected",
    [
        ("alice@example.com", True),
        ("bob@example", False),
        ("", False),
    ],
)
def test_email_validator(email, expected):
    assert is_valid_email(email) is expected
```

### conftest.py

공통 fixture를 테스트 패키지 루트의 `conftest.py`에 두면 import 없이 자동 공유됩니다. 프로젝트가 커질수록 계층별 `conftest.py`로 범위를 나누는 편이 관리에 유리합니다.

### marker

느린 테스트, DB 의존 테스트, 외부 API 테스트를 marker로 구분하면 실행 정책을 세밀하게 조절할 수 있습니다.

```python
import pytest

@pytest.mark.integration
def test_get_order_history(client):
    response = client.get("/orders/history")
    assert response.status_code == 200
```

`pytest -m "not integration"`처럼 빠른 피드백 루프를 분리할 수 있습니다.

## 무엇을 테스트하고, 무엇을 테스트하지 않을지

테스트 설계의 성숙도는 "무엇을 뺄지"에서 드러납니다. 모든 라인을 검증하겠다는 접근은 대부분 유지 불가능합니다.

테스트할 대상은 다음 우선순위가 좋습니다.

- 비즈니스 규칙: 가격 계산, 권한 판정, 상태 전이
- 계약: HTTP 상태 코드, 응답 스키마, 에러 포맷
- 경계 동작: 트랜잭션, 재시도, 타임아웃, 롤백
- 회귀 위험이 큰 버그 경로

반대로 구현 세부사항에 과도하게 묶인 검증은 피하는 편이 좋습니다.

- private 메서드 호출 횟수
- ORM 내부 쿼리 빌더 조합 자체
- 리팩터링 시 바뀔 수밖에 없는 내부 함수 분해 방식

좋은 질문은 "이 구현이 맞나"가 아니라 "이 동작 약속이 유지되나"입니다. API를 쓰는 클라이언트는 내부 클래스를 모르고, 오직 계약만 신뢰합니다.

## 커버리지 숫자 해석: 80%의 의미와 100%의 함정

커버리지는 의사결정 보조지표입니다. 목표 그 자체가 아닙니다.

- `라인 커버리지 80%`는 최소한의 안전망이 형성되었는지 보는 기준으로 유용합니다.
- `브랜치 커버리지`는 `if/else`, 예외 분기, 조기 반환 같은 경로를 실제로 탔는지 보여 줍니다.

```bash
pytest --cov=app --cov-report=term-missing --cov-branch
```

100%를 절대 목표로 두면 생기는 부작용이 있습니다.

1. 의미 없는 assertion으로 숫자를 채우게 됩니다.
2. 리팩터링 저항이 커집니다. 내부 구조를 바꾸기만 해도 테스트가 과도하게 깨집니다.
3. 고위험 경로보다 저위험 보일러플레이트에 시간이 새어 나갑니다.

시니어 엔지니어는 "몇 퍼센트인가"보다 "무엇이 비어 있는가"를 봅니다. 인증 실패, 결제 취소, 권한 우회 같은 실패 비용 높은 분기가 빠져 있으면 90%도 안전하지 않습니다.

## 운영 시나리오로 보는 테스트 실패 패턴

### 1) 로컬에서는 통과하는데 CI에서 실패합니다

원인은 대체로 환경 의존입니다. 로컬 타임존, OS 파일 경로, 누락된 환경 변수, 외부 서비스 접근 권한 차이가 대표적입니다. 해결은 "로컬을 CI처럼" 만드는 것입니다.

- `.env.test`를 명시적으로 사용합니다.
- 시간/랜덤/UUID를 fixture로 고정합니다.
- 네트워크 의존 테스트를 격리하고 mock 또는 sandbox로 대체합니다.

### 2) 테스트가 느립니다

원인은 대부분 불필요한 실제 I/O입니다. 모든 테스트에서 실제 DB를 매번 마이그레이션하거나, 외부 API를 실호출하면 분 단위로 느려집니다.

- unit은 I/O 없이 실행되도록 경계를 분리합니다.
- integration은 트랜잭션 롤백과 seed 최소화로 최적화합니다.
- E2E는 핵심 사용자 경로만 남기고 개수를 통제합니다.

### 3) 리팩터링했는데 테스트는 통과하고 서비스는 깨졌습니다

테스트가 구현 결합형이면 이런 일이 생깁니다. mock 기반 unit만 많고 계약 기반 integration이 적으면 내부 협력 오류를 놓칩니다.

- 주요 endpoint마다 상태 코드 + 응답 스키마 검증을 둡니다.
- "호출했다"보다 "무엇을 보장했는지"를 테스트 이름에 명시합니다.

### 4) 에러 경로 테스트가 없어 운영에서 500이 납니다

성공 경로만 검증하면 실제 장애는 대부분 미검증 분기에서 터집니다.

- 예외 매핑(예: `DomainError -> 400`)을 통합 테스트로 고정합니다.
- 외부 의존성 실패(타임아웃, 503) 시 대체 응답을 검증합니다.

## 테스트 코드 조직: 소스 구조를 거울처럼 반영합니다

테스트 폴더는 소스 구조를 따라가야 탐색과 유지가 쉽습니다.

```text
app/
  api/
  services/
  repositories/
tests/
  unit/
    services/
      test_order_service.py
  integration/
    api/
      test_users_api.py
  e2e/
    test_checkout_flow.py
  conftest.py
```

네이밍 규칙도 일관되게 가져갑니다.

- 파일: `test_<대상>.py`
- 함수: `test_<조건>_<기대결과>`
- fixture: 목적이 드러나는 명사형 이름 (`authorized_client`, `db_session`)

이 규칙의 효과는 새 팀원이 들어왔을 때 즉시 체감됩니다. "어디에 어떤 테스트를 추가해야 하는가"가 구조에서 바로 보이기 때문입니다.

## CI에 연결해야 테스트가 자산이 됩니다

로컬에서만 도는 테스트는 습관에 의존합니다. CI에 연결된 테스트만 조직의 안전망이 됩니다.

핵심 원칙은 세 가지입니다.

1. **push/PR마다 자동 실행**: 최소한 unit + integration은 항상 돌립니다.
2. **fail fast**: lint/type/test를 병렬로 실행하되, 실패 시 즉시 피드백을 줍니다.
3. **병렬화**: `pytest-xdist` 등으로 테스트 셋을 분산해 대기 시간을 줄입니다.

```bash
pytest -m "not e2e" -n auto --maxfail=1
```

`--maxfail=1`은 첫 실패를 빠르게 드러내고, `-n auto`는 코어 수에 맞춰 실행 시간을 단축합니다. E2E는 별도 job이나 야간 파이프라인으로 분리해도 좋습니다.

## 자주 하는 실수와 왜 위험한지

| 실수 | 왜 발생하는가 | 왜 위험한가 | 권장 대응 |
|---|---|---|---|
| E2E 중심으로만 테스트 작성 | "실제와 가까우면 더 좋다"는 직관 | 느려서 자주 못 돌리고 원인 추적이 어려움 | unit/integration 비중 확대, E2E는 핵심 흐름만 유지 |
| mock 과다 사용 | 외부 의존 분리를 과도하게 해석 | 실제 계약 불일치가 숨어도 통과 | 경계 밖만 mock, API 계약은 integration으로 보강 |
| 성공 경로만 검증 | 데모 중심 개발 습관 | 장애 시 500/타임아웃 경로 무방비 | 실패 케이스를 성공 케이스와 같은 비중으로 작성 |
| 전역 상태 공유 fixture | 초기 설정 단순화 욕심 | 테스트 간 순서 의존/flake 증가 | 함수 스코프 기본, 필요한 경우만 scope 확장 |
| 커버리지 숫자 집착 | KPI 압박 | 의미 없는 테스트 양산, 리팩터링 저항 증가 | 고위험 분기 기준으로 공백 점검 |

시니어 관점의 핵심은 "테스트가 미래 변경 비용을 줄이는가"입니다. 작성 당시 기분 좋은 통과보다, 3개월 뒤 기능 추가 시 깨지는 위치를 빨리 알려 주는 설계가 더 가치 있습니다.

## 실무 체크리스트

- 테스트 피라미드 비율(unit/integration/E2E)을 팀 차원에서 합의했습니다.
- 핵심 서비스 규칙은 unit 테스트로 빠르게 보호합니다.
- 주요 API 계약(상태 코드, 응답 스키마, 에러 포맷)은 integration으로 고정합니다.
- 테스트 DB 격리, 롤백, fixture 수명 주기를 문서화했습니다.
- marker와 CI 분리 전략으로 빠른 피드백 루프를 유지합니다.
- 커버리지는 숫자보다 고위험 분기 공백 중심으로 해석합니다.

## 처음 질문으로 돌아가기

- **unit, integration, E2E 테스트는 각각 무엇을 검증할까요?**
  - unit은 서비스 계층의 판단 규칙을 고립해 검증하고, integration은 실제 HTTP와 의존성 연결에서 계약이 맞는지 검증하며, E2E는 배포된 시스템에서 사용자 핵심 흐름이 끝까지 이어지는지를 검증합니다. 세 레벨은 대체 관계가 아니라 비용과 신뢰도를 분담하는 보완 관계입니다.
- **pytest로 service를 어떻게 테스트할 수 있을까요?**
  - repository나 외부 API를 mock/fake로 분리하고, 입력 대비 출력과 부작용(저장/롤백/예외)만 검증하면 됩니다. fixture로 반복 준비를 구조화하고, parametrize로 경계값과 실패 케이스를 선언적으로 추가하면 서비스 규칙을 빠르고 안정적으로 보호할 수 있습니다.
- **FastAPI `TestClient`는 endpoint를 어떻게 검증하게 해 줄까요?**
  - 서버를 따로 띄우지 않고도 실제 요청-응답 경로를 통과시켜 상태 코드, 응답 shape, 유효성 실패 포맷, 예외 매핑까지 검증할 수 있습니다. 이 계층을 갖추면 "unit은 통과했는데 클라이언트에서 깨진다"는 종류의 회귀를 배포 전에 차단할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Backend Development 101 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [Backend Development 101 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- [Backend Development 101 (3/10): Routing과 Controller](./03-routing-and-controllers.md)
- [Backend Development 101 (4/10): Service Layer](./04-service-layer.md)
- [Backend Development 101 (5/10): Database Layer](./05-database-layer.md)
- [Backend Development 101 (6/10): 인증과 권한](./06-auth-and-authorization.md)
- [Backend Development 101 (7/10): Logging과 Error Handling](./07-logging-and-error-handling.md)
- **백엔드 테스트 (현재 글)**
- 백엔드 배포 (예정)
- 운영 가능한 백엔드 구조 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [pytest documentation](https://docs.pytest.org/en/stable/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)

- [Testing pyramid (Martin Fowler)](https://martinfowler.com/articles/practical-test-pyramid.html)

Tags: Backend, Testing, Pytest, Python, QualityAssurance
