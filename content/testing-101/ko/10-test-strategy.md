---
series: testing-101
episode: 10
title: "Testing 101 (10/10): 테스트 전략 세우기"
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
  - Strategy
  - Quality
  - Capstone
  - Engineering
seo_description: 테스트 피라미드와 ROI를 기준으로 팀에 맞는 테스트 전략을 세우는 방법.
last_reviewed: '2026-05-12'
---

# Testing 101 (10/10): 테스트 전략 세우기

테스트를 많이 쓰는 팀이 항상 잘 운영되는 것은 아닙니다. 모든 함수에 단위 테스트를 붙이고, 모든 화면에 E2E 테스트를 추가하면 겉보기에는 촘촘해 보일 수 있습니다. 그런데 CI가 30분씩 걸리고, 플래키 테스트가 늘고, PR 속도가 급격히 떨어지면 그 체계는 버그보다 느린 개발 속도를 더 많이 만들 수 있습니다.

그래서 마지막에는 수량보다 배치를 봐야 합니다. 어떤 계층에 얼마를 투자할지, 어디를 두껍게 보호할지, 무엇을 문서가 아니라 팀 습관으로 남길지를 결정하는 일이 전략입니다.

이 글은 Testing 101 시리즈의 마지막 글입니다. 여기서는 테스트 피라미드의 분포, 계층별 투자 대비 효과, 계약 테스트와 팀 운영 습관, 그리고 전략을 살아 있는 규칙으로 유지하는 방법을 정리하겠습니다.

![Testing 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/10/10-01-diagram.ko.png)
*Testing 101 10장 흐름 개요*
> 테스트 전략은 팀의 가치관과 위험도 평가로 결정됩니다. 정답은 없지만 의식적인 선택이 필요합니다.

## 이 글에서 다룰 문제

- 테스트 피라미드는 왜 분포가 중요할까요?
- 단위, 통합, E2E 계층에 어떤 비율로 투자해야 할까요?
- 중요한 사용자 경로는 어떻게 정할까요?
- 계약 테스트는 마이크로서비스에서 어떤 역할을 할까요?
- 전략을 살아 있는 문서로 유지하는 방법은 무엇일까요?

테스트는 공짜가 아닙니다. 작성 시간, 실행 시간, 유지 시간, 실패를 고치는 시간이 모두 듭니다. 전략 없이 늘리기만 하면 느리고 깨지기 쉬운 테스트 묶음이 됩니다.

반대로 분포를 잘 잡으면 적은 수의 E2E로 큰 사용자 사고를 막고, 많은 수의 단위 테스트로 빠른 피드백을 유지할 수 있습니다. 전략은 품질과 속도 사이의 균형을 잡는 일입니다.

## 한눈에 보는 구조

테스트 피라미드는 단순한 그림이 아니라 비용 구조를 보여 줍니다. 아래층일수록 빠르고 많아야 하고, 위층일수록 비싸고 적어야 합니다. 이 분포가 무너지면 피드백 속도와 신뢰가 함께 흔들립니다.

- **테스트 피라미드**: 단위 테스트는 많고, 통합 테스트는 그보다 적고, E2E 테스트는 더 적게 두는 분포 모델입니다.
- **ROI**: 투자한 비용 대비 얼마나 많은 버그를 잡는지 보는 관점입니다.
- **핵심 경로(critical path)**: 로그인, 결제처럼 사용자 피해가 큰 흐름입니다.
- **계약 테스트(contract test)**: 시스템 경계에서 입력과 출력 형식을 검증하는 테스트입니다.
- **플래키 예산(flaky budget)**: 허용 가능한 불안정 비율을 수치로 정한 기준입니다.

## 테스트 철학 비교 — 피라미드, 트로피, 다이아몬드

테스트 분포에 대한 접근 방식은 하나만 있는 것이 아닙니다.

| 모델 | 비율 (단위:통합:E2E) | 주장자 | 적합한 프로젝트 |
|---|---|---|---|
| 테스트 피라미드 | 70:20:10 | Mike Cohn, Martin Fowler | 백엔드 API, 도메인 로직 중심 시스템 |
| 테스트 트로피 | 50:30:20 (static 추가) | Kent C. Dodds | 프론트엔드 중심, 사용자 인터랙션 중요 |
| 테스트 다이아몬드 | 30:50:20 | 일부 팀 | 마이크로서비스, 경계 테스트 중심 |

테스트 피라미드는 단위 테스트를 가장 많이 두고 E2E를 최소화합니다. 테스트 트로피는 통합 테스트 비중을 높이고 정적 분석을 포함합니다. 테스트 다이아몬드는 시스템 경계에서 계약 테스트를 두껍게 유지하는 접근입니다.

팀은 자신의 아키텍처와 위험도에 따라 적합한 모델을 선택해야 합니다.

## 바꾸기 전과 후

**바꾸기 전 — 전략 없이 계층을 늘린 상태**

```text
- 모든 함수에 단위 테스트
- 모든 시나리오에 E2E 테스트
- CI 30분, PR 처리 속도 정체
- 팀이 CI 결과를 신뢰하지 않기 시작함
```

**바꾼 뒤 — 투자 위치를 조정한 상태**

```text
- 핵심 도메인 단위 테스트 2,000개 (70%)
- 통합 테스트 400개 (20%, DB와 외부 API 경계)
- E2E 200개 (10%, 결제, 로그인 같은 핵심 경로)
- CI 5분 이내 (단위+통합 병렬)
```

차이는 테스트 수보다 분포에 있습니다. 모든 계층을 같은 강도로 밀어붙이는 대신, 빠른 계층은 두껍게, 비싼 계층은 핵심만 남기는 방식입니다.

## 다섯 단계로 전략 만들기

### 1단계 — 현재 분포를 먼저 측정하기

전략은 현재 분포를 알아야 시작할 수 있습니다.

```bash
# 전체 테스트 수
pytest --collect-only -q | tail -1

# 계층별 파일 수
find tests/unit -name "*.py" | wc -l
find tests/integration -name "*.py" | wc -l
find tests/e2e -name "*.py" | wc -l

# 계층별 실행 시간 측정
time pytest tests/unit -q
time pytest tests/integration -q
time pytest tests/e2e -q
```

### 2단계 — 핵심 경로 정의하기

E2E로 반드시 보호해야 할 경로를 명시합니다. 모든 경로를 E2E로 덮으면 유지비가 급격히 늘어납니다.

```text
핵심 경로 (E2E 필수):
- 회원 가입 → 이메일 인증 → 첫 로그인
- 상품 선택 → 장바구니 → 결제 완료
- 비밀번호 분실 → 재설정 이메일 → 변경

보호 방법이 다른 경로:
- 관리자 설정 변경 → 통합 테스트 (API 레벨)
- 개별 계산 함수 → 단위 테스트
```

### 3단계 — 경계에 계약 테스트 추가하기

외부 API나 마이크로서비스와의 경계에서 스키마를 검증합니다.

```python
# tests/contracts/test_payment_api.py
import pytest
from src.payment_client import PaymentClient

def test_charge_response_has_required_fields():
    """결제 API 응답에 필수 필드가 포함되어야 합니다."""
    client = PaymentClient(base_url="http://localhost:8080")
    response = client.charge(amount=1000, currency="KRW")

    # 계약: 응답 스키마 검증
    assert "id" in response, "결제 ID가 없습니다"
    assert "status" in response, "결제 상태가 없습니다"
    assert "amount" in response, "결제 금액이 없습니다"
    assert response["status"] in ("pending", "completed", "failed")
    assert isinstance(response["amount"], (int, float))

def test_charge_idempotency_key_prevents_duplicates():
    """같은 idempotency key로 두 번 결제하면 동일한 결과를 반환해야 합니다."""
    client = PaymentClient(base_url="http://localhost:8080")
    key = "test-idem-key-001"
    res1 = client.charge(amount=1000, idempotency_key=key)
    res2 = client.charge(amount=1000, idempotency_key=key)
    assert res1["id"] == res2["id"]
```

### 4단계 — 팀 운영 습관 만들기

전략은 문서보다 반복되는 루틴으로 유지됩니다.

```text
PR 템플릿에 추가:
- [ ] 새 기능에 단위 테스트를 추가했습니다.
- [ ] 버그 수정에 회귀 테스트를 추가했습니다.
- [ ] 커버리지가 줄어들지 않았습니다.

주간 습관 (30분):
- 플래키 테스트 목록 확인 및 수정 계획

월간 습관:
- CI 평균 실행 시간 추세 확인
- 커버리지 절대값이 아닌 추세 확인

분기 습관:
- 전략 회고: 분포가 목표에 맞는지 점검
- 6개월간 의미 있게 실패하지 않은 E2E 재검토
```

### 5단계 — 분기마다 가지치기하기

```python
# 테스트 부채 시그널을 추적하는 conftest 훅
# tests/conftest.py
import pytest
import time

_slow_tests = []

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    start = time.monotonic()
    outcome = yield
    elapsed = time.monotonic() - start

    if call.when == "call" and elapsed > 5.0:
        _slow_tests.append((item.nodeid, elapsed))

def pytest_sessionfinish(session, exitstatus):
    if _slow_tests:
        print("\n[SLOW TESTS - 5초 초과]")
        for nodeid, elapsed in sorted(_slow_tests, key=lambda x: -x[1]):
            print(f"  {elapsed:.1f}s  {nodeid}")
```

## 예산 배분 예시와 이유

실제 팀에서는 테스트 분포를 예산 개념으로 접근할 수 있습니다. 다음은 중간 규모 백엔드 팀의 예산 배분 예시입니다.

| 계층 | 개수 | 비율 | 평균 실행 시간 | 총 시간 | 이유 |
|---|---|---|---|---|---|
| 단위 테스트 | 1400 | 70% | 10ms | 14초 | 도메인 로직, 변환 함수, 유효성 검사 |
| 통합 테스트 | 400 | 20% | 100ms | 40초 | DB, 외부 API, 메시지 큐 경계 |
| E2E 테스트 | 200 | 10% | 2초 | 400초 | 로그인, 결제, 주문 핵심 경로 |
| **합계** | **2000** | **100%** | — | **7분 30초** | — |

**배분 이유**

- 단위 테스트는 빠르고 결정적이므로 가장 많이 둡니다. 도메인 로직의 모든 분기를 촘촘히 덮습니다.
- 통합 테스트는 시스템 경계에서 입력과 출력 형식을 검증합니다. 외부 의존이 바뀌어도 빠르게 감지합니다.
- E2E 테스트는 사용자 영향이 큰 핵심 경로만 남깁니다. 모든 시나리오를 E2E로 덮으면 유지비가 급격히 늘어납니다.

이 예산은 팀마다 다를 수 있지만, 분포의 의도를 명시하는 것이 중요합니다.

## 프로젝트 유형별 전략

### API 서버

```text
분포: 단위 70% / 통합 25% / E2E 5%
단위: 비즈니스 규칙, 유효성 검사, 변환 함수
통합: DB 저장/조회, HTTP 요청-응답 스키마, 인증 미들웨어
E2E: 회원가입-로그인 흐름, 결제 흐름 (실제 브라우저 불필요)
```

### CLI 도구

```text
분포: 단위 60% / 통합 35% / E2E 5%
단위: 개별 명령 로직, 파서, 포맷터
통합: 실제 파일 입출력, 플래그 조합, 환경변수 처리
E2E: 전체 명령 체인 (subprocess 실행으로 충분)
```

### 데이터 파이프라인

```text
분포: 단위 50% / 통합 45% / E2E 5%
단위: 변환 함수, 스키마 검증, 필터 로직
통합: 실제 DB 읽기/쓰기, 객체 스토리지, 메시지 큐
E2E: 전체 파이프라인 실행 + 데이터 품질 검증
```

## 계약 테스트 — 마이크로서비스에서 경계 지키기

마이크로서비스 환경에서는 서비스 간 인터페이스가 깨지면 E2E에서만 발견되는 경우가 많습니다. 계약 테스트는 이 문제를 서비스 레벨에서 조기에 잡습니다.

**Consumer 측 (주문 서비스)**

```python
# tests/contracts/test_payment_contract.py
import pytest
from unittest.mock import MagicMock

def test_order_service_calls_payment_with_correct_schema():
    """주문 서비스가 결제 서비스를 올바른 스키마로 호출합니다."""
    payment_client = MagicMock()
    payment_client.charge.return_value = {
        "id": "pay-001",
        "status": "completed",
        "amount": 50000
    }

    order_service = OrderService(payment_client=payment_client)
    order_service.complete_order(order_id="ord-001", amount=50000)

    # Consumer 계약: 이 스키마로 호출해야 합니다
    payment_client.charge.assert_called_once_with(
        amount=50000,
        currency="KRW",
        order_id="ord-001"
    )
```

**Provider 측 (결제 서비스)**

```python
# tests/contracts/test_payment_provider.py
def test_payment_api_fulfills_consumer_contract():
    """결제 서비스가 Consumer가 기대하는 응답 스키마를 반환합니다."""
    from fastapi.testclient import TestClient
    from src.payment_app import app

    client = TestClient(app)
    response = client.post("/charge", json={
        "amount": 50000,
        "currency": "KRW",
        "order_id": "ord-001"
    })

    assert response.status_code == 200
    body = response.json()
    # Provider 계약: 이 스키마를 보장해야 합니다
    assert "id" in body
    assert "status" in body
    assert "amount" in body
    assert body["amount"] == 50000
```

## 테스트 부채 관리

테스트는 코드와 마찬가지로 부채가 쌓입니다.

**테스트 부채의 신호**

- 플래키 테스트가 계속 늘어납니다.
- 테스트가 깨져도 팀이 수정 대신 비활성화를 선택합니다.
- 새 기능 추가 시 기존 테스트 수정 시간이 기능 개발 시간보다 깁니다.
- CI 실행 시간이 15분을 넘어 PR 피드백이 느려집니다.

**분기별 가지치기 기준**

```text
삭제 대상:
- 참조 기능이 완전히 삭제된 테스트
- 6개월간 한 번도 의미 있게 실패하지 않은 E2E

계층 이동 대상:
- E2E에 있지만 통합 테스트로도 충분히 검증 가능한 테스트
- 통합 테스트에 있지만 단위 테스트로 내릴 수 있는 테스트

리팩터링 신호:
- 같은 모듈에서 회귀 테스트가 계속 추가되는 경우
- 테스트 setup이 50줄 이상인 경우
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
|---|---|---|
| 모든 코드에 같은 강도로 테스트 요구 | 팀이 낮은 ROI 계층부터 우회 | 위험도 기반으로 테스트 강도 차등 적용 |
| E2E를 주력 계층으로 삼음 | CI 30분 이상, 플래키 급증 | E2E는 핵심 경로 10% 이내로 제한 |
| 커버리지 숫자만 추적 | 중요 코드가 덮이지 않아도 목표 달성 착각 | 어떤 코드가 덮이는지 + 추세를 함께 확인 |
| 전략 문서만 만들고 습관 없음 | 6개월 뒤 전략이 사라짐 | PR 템플릿, 주간 리뷰, 분기 회고로 루틴화 |
| 계약 테스트 없이 마이크로서비스 운영 | 서비스 간 인터페이스 오류를 E2E에서만 발견 | 서비스 경계마다 계약 테스트 추가 |
| 테스트 부채를 방치 | 팀이 테스트를 짐으로 느끼기 시작 | 분기마다 가지치기, 플래키 목록 리뷰 |

## 실무에서는 이렇게 생각합니다

성숙한 팀은 목표 분포와 플래키 예산을 아예 운영 기준으로 문서화합니다. 새 서비스가 생겨도 같은 기준으로 출발하고, 분기마다 CI 시간과 불안정 비율을 점검합니다.

경험 많은 엔지니어는 테스트 전략을 기술 선택이 아니라 의사결정 체계로 봅니다. 무엇을 E2E에 남길지, 무엇을 단위 테스트로 내릴지, 어떤 회귀는 반드시 PR에 포함할지 모두 팀 속도와 위험도를 함께 보고 정합니다.

테스트가 팀에게 부담이 아니라 신뢰를 주는 도구가 되려면, 테스트의 수를 늘리는 것보다 팀이 신뢰할 수 있는 테스트를 올바른 위치에 두는 것이 더 중요합니다.

## 테스트 전략 문서화

테스트 전략은 팀의 머릿속에만 있으면 인수인계가 어렵습니다. 다음은 효과적인 문서화 구조입니다.

```markdown
# Testing Strategy — [팀 이름]

## 1. 목표 분포
- Unit: 70%
- Integration: 20%
- E2E: 10%

## 2. 핵심 경로 (E2E 필수)
- 회원 가입 → 이메일 인증 → 로그인
- 결제 흐름 (상품 선택 → 결제 완료)
- 비밀번호 재설정

## 3. 품질 지표
- PR CI 시간: 5분 이내
- 플래키 비율: 전체 테스트의 3% 미만
- 커버리지: 도메인 코드 80% 이상 (추세 유지)

## 4. 팀 운영 습관
- PR 템플릿: 회귀 테스트 추가 여부 체크
- 주간 30분: 플래키 테스트 리뷰
- 분기 1시간: 전략 회고 및 분포 점검

## 5. 가지치기 기준
- 6개월간 실패하지 않은 E2E: 재검토
- 회귀 3회 이상 발생 모듈: 리팩터링 신호
```

## 운영 체크리스트

- [ ] 팀의 현재 테스트 분포를 알고 있습니다.
- [ ] 핵심 경로(E2E 필수)가 문서화되어 있습니다.
- [ ] PR 템플릿에 테스트 추가 확인 항목이 있습니다.
- [ ] 플래키 비율 또는 CI 시간을 정기적으로 측정합니다.
- [ ] 분기마다 전략 회고를 진행합니다.
- [ ] 계약 테스트로 서비스 경계를 보호합니다.

## 연습 문제

1. 현재 저장소의 단위/통합/E2E 테스트 수와 각 계층의 실행 시간을 표로 정리해 보세요.
2. 로그인, 결제, 비밀번호 재설정처럼 사용자 피해가 큰 핵심 경로를 세 개 골라 현재 어떤 계층이 보호하는지 표시해 보세요.
3. 지난 분기 플래키 테스트 목록과 CI 평균 시간을 같이 놓고, 어떤 계층을 줄이거나 옮겨야 하는지 회고해 보세요.
4. 팀 전략 문서를 위 형식을 참고해 작성하고 저장소에 추가해 보세요.

## 정리

테스트 전략은 기법 목록이 아니라 투자 판단입니다. 빠른 테스트를 두껍게 쌓고, 비싼 테스트는 핵심에만 두고, 그 기준을 팀 습관으로 굳혀야 합니다. 이렇게 하면 Testing 101에서 본 단위 테스트, 통합 테스트, E2E 테스트, 회귀 테스트, CI가 하나의 운영 모델로 연결됩니다.

테스트가 많다고 좋은 것이 아닙니다. 팀이 신뢰할 수 있고, 빠르게 실행되고, 유지 가능한 테스트를 올바른 위치에 두는 것이 전략의 목표입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Testing 101 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [Testing 101 (2/10): 단위 테스트](./02-unit-test.md)
- [Testing 101 (3/10): 통합 테스트](./03-integration-test.md)
- [Testing 101 (4/10): E2E 테스트](./04-e2e-test.md)
- [Testing 101 (5/10): 테스트 더블](./05-test-double.md)
- [Testing 101 (6/10): Mock과 Stub](./06-mock-and-stub.md)
- [Testing 101 (7/10): 테스트 커버리지](./07-test-coverage.md)
- [Testing 101 (8/10): 회귀 테스트](./08-regression-test.md)
- [Testing 101 (9/10): CI에서 테스트 실행하기](./09-tests-in-ci.md)
- **테스트 전략 세우기 (현재 글)**

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소(book-examples): https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko

### 공식 문서

- [GitHub documentation for pull request templates](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-issue-and-pull-request-templates)
- [Pact contract testing guides](https://docs.pact.io/)

### 실무 참고

- [Martin Fowler — The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Accelerate (Forsgren, Humble, Kim)](https://itrevolution.com/product/accelerate/)
- [ThoughtWorks — Test Strategy](https://www.thoughtworks.com/insights/blog/testing-strategy)

Tags: Testing, Strategy, Quality, Capstone, Engineering
