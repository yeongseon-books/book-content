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

이 글은 Testing 101 시리즈의 여섯 번째 글입니다.

테스트 더블을 배운 뒤에도 Mock과 Stub은 자주 뒤섞입니다. 둘 다 가짜 객체처럼 보이기 때문입니다. 그런데 목적은 꽤 다릅니다. 이 차이를 놓치면 결과를 검증해야 할 테스트를 호출 검증으로 가득 채우거나, 반대로 상호작용이 핵심인 테스트를 너무 느슨하게 만들게 됩니다.

좋은 테스트는 실패했을 때 무엇이 깨졌는지 한 줄로 말해 줍니다. Mock과 Stub을 구분하는 일은 그 한 줄을 선명하게 만드는 작업입니다.

이 글은 Testing 101 시리즈의 여섯 번째 글입니다. 여기서는 `unittest.mock` 예제를 바탕으로 Mock과 Stub의 목적 차이, 상태 검증과 상호작용 검증의 차이, 그리고 과한 Mock 사용이 보내는 설계 신호를 정리하겠습니다.


![Testing 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/06/06-01-diagram.ko.png)
*Testing 101 6장 흐름 개요*
> Stub은 응답을 제어하고, Mock은 호출 자체를 검증합니다.

## 먼저 던지는 질문

- Stub과 Mock은 정확히 무엇이 다를까요?
- 상태 검증과 상호작용 검증은 어떻게 구분할까요?
- `MagicMock`, `patch`, `side_effect`는 언제 쓰일까요?

## 왜 중요한가

Stub과 Mock을 섞어 쓰면 테스트가 구현 세부사항에 과하게 묶입니다. 예를 들어 실제로 확인하고 싶은 것은 사용자 생성 결과인데, 저장소 메서드가 몇 번 호출됐는지만 검사하면 리팩터링 때 테스트가 먼저 부서집니다.

반대로 상호작용 자체가 핵심인 경우도 있습니다. 메일 발송, 결제 호출, 알림 전송처럼 부작용이 의미의 중심인 기능은 호출 여부와 인자가 중요합니다. 그래서 도구를 구분해야 테스트 의도가 선명해집니다.

## 한눈에 보는 구조

Stub은 미리 정한 값을 돌려줘서 결과 검증을 돕습니다. Mock은 기대한 호출이 있었는지 확인해서 상호작용 검증을 돕습니다. 같은 `MagicMock` 객체로도 두 역할을 모두 흉내 낼 수 있지만, 테스트 목적은 분리해서 생각해야 합니다.

## 핵심 용어

- **상태 검증**: 최종 반환값이나 상태 변화가 기대와 맞는지 확인하는 방식입니다.
- **상호작용 검증**: 의존을 어떤 방식으로 호출했는지 확인하는 방식입니다.
- **MagicMock**: 속성과 메서드를 유연하게 흉내 낼 수 있는 객체입니다.
- **patch**: 기존 객체를 잠시 다른 객체로 바꿔 끼우는 도구입니다.
- **side_effect**: 호출마다 다른 값이나 예외를 일으키도록 설정하는 기능입니다.

## 바꾸기 전과 후

**바꾸기 전 — Mock에만 기대는 테스트**

```python
def test_creates_user(repo_mock):
    create_user("a@b.com", repo=repo_mock)
    repo_mock.add.assert_called_once()  # 호출 방식만 검증
```

**바꾼 뒤 — 결과를 확인하는 테스트**

```python
def test_creates_user_persists():
    repo = InMemoryUserRepo()
    create_user("a@b.com", repo=repo)
    assert repo.find_by_email("a@b.com") is not None
```

두 테스트 모두 의미가 있을 수 있지만, 질문이 다릅니다. 첫 번째는 호출이 일어났는지, 두 번째는 실제로 저장 결과가 남았는지를 묻습니다. 어떤 질문이 더 본질적인지 먼저 정해야 합니다.

## 다섯 단계로 유닛테스트 목 익히기

### 1단계 — 기본 Mock

```python
from unittest.mock import MagicMock

def test_basic_mock():
    m = MagicMock()
    m.greet("hi")
    m.greet.assert_called_with("hi")
```

### 2단계 — `return_value`로 Stub처럼 쓰기

```python
def test_return_value():
    m = MagicMock()
    m.fetch.return_value = {"id": 1}
    assert m.fetch()["id"] == 1
```

### 3단계 — `side_effect`로 예외와 순서 다루기

```python
def test_side_effect_raises():
    m = MagicMock()
    m.fetch.side_effect = TimeoutError("slow")
    try:
        m.fetch()
    except TimeoutError as e:
        assert str(e) == "slow"
```

### 4단계 — 외부 함수를 `patch`로 교체하기

```python
from unittest.mock import patch

def test_patch_function():
    with patch("src.weather.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"temp": 20}
        from src.weather import current_temp
        assert current_temp() == 20
```

### 5단계 — 호출 여부 확인하기

```python
def test_not_called_when_disabled():
    mailer = MagicMock()
    notify("a@b.com", mailer=mailer, enabled=False)
    mailer.send.assert_not_called()
```

## 이 코드에서 먼저 볼 점

- `return_value`는 Stub 역할에 가깝고, `assert_called_*`는 Mock 역할에 가깝습니다.
- `patch`는 좁은 범위에서만 써야 다른 테스트에 영향을 남기지 않습니다.
- `side_effect`를 쓰면 정상 경로뿐 아니라 오류 경로도 쉽게 검증할 수 있습니다.

같은 도구를 써도 무엇을 검증하는지에 따라 테스트 성격이 달라집니다. 그래서 Mock 라이브러리를 잘 쓰는 것보다, 결과를 볼지 상호작용을 볼지 먼저 결정하는 감각이 더 중요합니다.

## 목과 스텁의 핵심 차이

Mock과 Stub을 간단히 정리하면 다음과 같습니다.

| 구분 | Stub | Mock |
|---|---|---|
| 정의 | 미리 정해진 값을 반환하는 대체 객체 | 호출 여부와 방식을 검증하는 대체 객체 |
| 검증 대상 | 테스트 대상의 **결과** | 테스트 대상의 **상호작용** |
| 실패 원인 | 최종 상태나 반환값이 기대와 다를 때 | 예상한 호출이 일어나지 않거나 잘못된 인자로 호출될 때 |
| 적합한 상황 | 외부 의존의 응답만 고정하고 실제 결과를 확인할 때 | 호출 자체가 요구사항인 경우 (알림, 로깅, 결제 등) |

이 차이를 코드로 보면 더 명확합니다.

**Stub 예시 — 결과 검증**

```python
def test_user_creation_with_stub():
    repo = MagicMock()
    repo.save.return_value = User(id=1, email="a@b.com")  # stub
    
    result = create_user("a@b.com", repo=repo)
    
    assert result.email == "a@b.com"  # 결과 검증
```

**Mock 예시 — 상호작용 검증**

```python
def test_user_creation_with_mock():
    repo = MagicMock()
    
    create_user("a@b.com", repo=repo)
    
    repo.save.assert_called_once_with(User(email="a@b.com"))  # 호출 검증
```

같은 `MagicMock` 객체를 써도, 첫 번째는 Stub처럼 반환값에 집중하고 두 번째는 Mock처럼 호출에 집중합니다. 테스트 의도가 다르면 검증 방식도 달라집니다.
## 어디서 자주 헷갈릴까요?

첫 번째 실수는 한 테스트 안에 결과 검증과 호출 검증을 과하게 섞는 일입니다. 의도가 두 개가 되면 실패 이유도 흐려집니다.

두 번째 실수는 `patch` 범위를 너무 넓게 잡는 일입니다. 함수 하나만 바꾸면 되는 상황에서 모듈 전체를 오래 바꾸면 다른 테스트까지 오염될 수 있습니다.

세 번째 실수는 모든 줄을 Mock으로 감싸 버리는 일입니다. 테스트 대상 코드보다 Mock 설정이 더 길어지는 순간, 테스트는 설계 검증보다 구현 복제에 가까워집니다.

## 런던 학파와 시카고 학파

Mock과 Stub을 바라보는 관점은 테스트 철학에서도 갈립니다. 전통적으로 두 학파가 있습니다.

**London school (Mockist)**

- 객체 간 상호작용을 중심으로 테스트합니다.
- 모든 협력자를 Mock으로 교체하고 호출 계약을 검증합니다.
- 설계 의도가 명확하게 드러나지만, 리팩터링 때 테스트가 쉽게 깨질 수 있습니다.

**Chicago school (Classicist)**

- 최종 결과를 중심으로 테스트합니다.
- 가능한 한 실제 객체를 쓰고, 느리거나 제어 불가능한 것만 Stub/Fake로 바꿉니다.
- 리팩터링에 강하지만, 실패 지점이 덜 명확할 수 있습니다.

대부분의 실무 팀은 둘 사이 어딘가에 있습니다. 핵심 도메인 로직은 Chicago 방식, 외부 API나 메시징은 London 방식을 섞어 씁니다. 중요한 것은 교조적으로 한쪽만 따르기보다, 각 테스트에서 무엇을 묻고 싶은지 먼저 정하는 일입니다.
## 현업 확장 노트: 계층별 검증을 연결하는 방법

이 장의 핵심 개념을 팀 운영에 연결하려면, 테스트를 단독 문서가 아니라 저장소 규약으로 관리해야 합니다. 가장 많이 쓰는 방식은 테스트 디렉터리를 계층으로 분리하고, 각 계층의 실행 시점과 실패 기준을 명시하는 것입니다.

```text
tests/
├─ unit/
├─ integration/
├─ e2e/
└─ contracts/
```

이 구조를 도입하면 PR 단계에서는 unit과 일부 integration만 빠르게 실행하고, 병합 전이나 야간 빌드에서는 더 넓은 범위를 실행하는 운영이 가능합니다. "모든 테스트를 매번 전부"보다 "위험에 맞게 계층별로"가 훨씬 현실적입니다.

```yaml
name: test-pipeline
on:
  pull_request:
  schedule:
    - cron: '0 17 * * *'

jobs:
  fast-feedback:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements-dev.txt
      - run: pytest tests/unit tests/integration -q --maxfail=1

  nightly-full:
    if: github.event_name == 'schedule'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements-dev.txt
      - run: pytest -q
```

또한 `unittest.mock`과 fixture를 함께 쓰면 테스트 의도를 더 분명히 드러낼 수 있습니다. fixture는 "무엇을 준비했는가"를, mock 검증은 "어떤 상호작용이 일어났는가"를 표현합니다.

```python
import pytest
from unittest.mock import Mock

@pytest.fixture
def notifier_mock():
    return Mock()

def test_notify_on_success(notifier_mock):
    service = JobService(notifier=notifier_mock)
    service.run(job_id='job-1')
    notifier_mock.send.assert_called_once()
```

마지막으로 커버리지는 목표치 자체보다 누락 영역의 성격을 함께 봐야 합니다. 예를 들어 유틸리티 파일 60%보다 결제 도메인 82%가 더 위험할 수 있습니다. 따라서 커버리지 리포트를 읽을 때는 반드시 "이 파일이 실패하면 비즈니스 영향이 큰가"를 함께 판단해야 합니다.

```bash
pytest --cov=src --cov-report=term-missing
```

```text
Name                        Stmts   Miss  Cover
-----------------------------------------------
src/domain/payment.py          96     14    85%
src/domain/refund.py           64      4    94%
src/utils/text.py              21      5    76%
-----------------------------------------------
TOTAL                          181    23    87%
```

이런 리포트에서는 `payment.py`의 누락 분기를 먼저 메우는 것이 합리적입니다. 테스트는 숫자를 맞추는 운동이 아니라, 고장 났을 때 손실이 큰 경로를 먼저 보호하는 엔지니어링 작업이기 때문입니다.

## 직접 검증해 볼 것

1. 같은 시나리오를 `return_value` 기반 결과 검증과 `assert_called_with` 기반 상호작용 검증으로 각각 작성해 봅니다. 어떤 질문을 던지는 테스트인지 차이가 분명하게 보여야 합니다.
2. `patch` 범위를 함수 하나로 좁혔을 때와 모듈 전체로 넓혔을 때 다른 테스트에 미치는 영향을 비교합니다.
3. `side_effect`로 예외를 일으킨 뒤, 실패 메시지가 외부 의존 장애를 충분히 설명하는지 확인합니다.

**예상 결과:** 결과를 검증할 때는 Fake/Stub 버전이 더 읽기 쉽고, 호출 자체가 요구사항일 때만 Mock 검증이 핵심으로 남아야 합니다.

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

회귀 버그를 줄이려면 버그 티켓이 닫힐 때 반드시 재현 테스트를 남겨야 합니다. 수정 코드만 머지하면 같은 원인의 버그가 다른 경로에서 재발합니다. 반대로 재현 테스트를 함께 남기면 팀 지식이 실행 가능한 형태로 축적됩니다.

커버리지 리포트는 주간 회고에서 매우 유용합니다. 숫자만 보는 대신 누락 라인이 핵심 도메인인지 확인하고, 다음 스프린트에서 보강할 테스트를 합의하면 테스트 투자가 산발적으로 흩어지지 않습니다.

CI에서는 실패를 빠르게 보여 주는 순서가 중요합니다. 일반적으로 단위 테스트를 먼저 실행하고, 그 다음 통합 테스트, 마지막으로 느린 E2E를 배치하면 평균 피드백 시간이 줄어듭니다. 파이프라인 설계도 테스트 전략의 일부로 다루어야 합니다.

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

- 하나의 테스트가 결과 검증과 호출 검증을 모두 과하게 담으면 실패 이유가 흐려집니다.
- `patch`가 함수 밖까지 오래 살아 있으면 다른 테스트 오염으로 이어질 수 있습니다.
- Mock 설정이 테스트 대상 코드보다 길어지면 설계나 테스트 계층 선택을 다시 봐야 합니다.

## 실무에서는 이렇게 생각합니다

대부분의 새 테스트는 Stub이나 Fake에서 출발합니다. 실제 결과를 확인할 수 있으면 그 편이 읽기 쉽고 리팩터링에도 강합니다. Mock은 상호작용 그 자체가 요구사항일 때만 꺼내는 편이 좋습니다.

경험 많은 엔지니어는 Mock 수가 많아지는 상황을 설계 신호로 봅니다. 지나친 Mock은 보통 의존이 세분되지 않았거나 함수 책임이 과한 경우가 많습니다. 테스트가 불편하다면 테스트 코드를 고치기 전에 설계를 먼저 살펴보는 편이 낫습니다.

## 목 객체를 남용하면 생기는 문제

Mock은 강력하지만 과하게 쓰면 테스트가 설계를 따라가지 못하고 구현을 복제하는 문서가 됩니다.

**문제 상황**

```python
def test_process_order_too_many_mocks():
    validator_mock = MagicMock()
    inventory_mock = MagicMock()
    payment_mock = MagicMock()
    mailer_mock = MagicMock()
    logger_mock = MagicMock()
    
    # 10줄 넘는 mock 설정
    validator_mock.validate.return_value = True
    inventory_mock.reserve.return_value = True
    payment_mock.charge.return_value = {"status": "ok"}
    
    process_order(
        order_id=1,
        validator=validator_mock,
        inventory=inventory_mock,
        payment=payment_mock,
        mailer=mailer_mock,
        logger=logger_mock
    )
    
    # 5줄 넘는 호출 검증
    validator_mock.validate.assert_called_once()
    inventory_mock.reserve.assert_called_with(order_id=1)
    payment_mock.charge.assert_called_once()
    mailer_mock.send.assert_called_with("order_confirmed", to="user@example.com")
    logger_mock.info.assert_called()
```

이 테스트는 세 가지 문제가 있습니다.

1. **Mock 설정이 테스트보다 깁니다.** 실제 검증 의도보다 준비 코드가 더 많습니다.
2. **리팩터링에 취약합니다.** 함수 내부에서 호출 순서가 바뀌거나 새 협력자가 추가되면 테스트가 즉시 깨집니다.
3. **무엇이 중요한지 흐려집니다.** 다섯 개의 `assert_called`가 있지만, 그중 어떤 것이 핵심 요구사항인지 알기 어렵습니다.

**개선 방향**

대부분의 협력자를 Fake나 In-Memory 구현으로 바꾸고, 부작용이 핵심인 것만 Mock으로 남깁니다.

```python
def test_process_order_focused():
    inventory = InMemoryInventory()
    inventory.add_stock(product_id=10, quantity=5)
    
    payment = FakePaymentGateway()
    mailer_mock = MagicMock()  # 메일 발송만 Mock
    
    result = process_order(
        order_id=1,
        inventory=inventory,
        payment=payment,
        mailer=mailer_mock
    )
    
    assert result.status == "confirmed"
    assert inventory.reserved(product_id=10) == 1
    assert payment.last_charge()["amount"] == 100
    mailer_mock.send.assert_called_once_with("order_confirmed", to="user@example.com")
```

이제 테스트는 최종 상태를 먼저 확인하고, 메일 발송처럼 외부 부작용만 Mock으로 검증합니다. Mock이 줄어들수록 테스트는 더 읽기 쉬워지고 리팩터링에 강해집니다.
## 체크리스트

- [ ] Stub과 Mock의 차이를 한 문장으로 설명할 수 있습니다.
- [ ] `return_value`, `side_effect`, `assert_called_with`를 직접 사용했습니다.
- [ ] `patch` 범위를 함수 수준으로 좁게 유지했습니다.
- [ ] 가능하면 결과 검증을 먼저 선택했습니다.

## 연습 문제

1. 외부 API를 호출하는 함수를 만들고 Stub 방식과 Mock 방식으로 모두 테스트해 보세요.
2. 세 번에 한 번 실패하는 호출을 `side_effect`로 흉내 내 보세요.
3. 같은 시나리오를 Fake로도 테스트하고 무엇이 더 읽기 쉬운지 비교해 보세요.

## 정리

Mock과 Stub은 비슷해 보이지만 목표가 다릅니다. 결과를 확인할지, 호출을 확인할지 먼저 정하면 어떤 도구를 써야 하는지도 분명해집니다. 다음 글에서는 테스트가 코드의 어느 범위까지 닿았는지 보여 주는 테스트 커버리지를 다루겠습니다.

## 처음 질문으로 돌아가기

- **Stub과 Mock은 정확히 무엇이 다를까요?**
  - Stub은 외부 의존의 반환값을 고정하여 테스트에서 정해진 응답만 받을 수 있게 합니다.
- **상태 검증과 상호작용 검증은 어떻게 구분할까요?**
  - Mock은 함수가 정확히 예상된 방식으로 호출되었는지 검증하므로 호출 계약을 확인할 수 있습니다.
- **`MagicMock`, `patch`, `side_effect`는 언제 쓰일까요?**
  - 상황에 따라 stub만 필요할 수도 있고 mock까지 필요할 수도 있으므로 테스트 의도에 맞게 선택합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Testing 101 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [Testing 101 (2/10): 단위 테스트](./02-unit-test.md)
- [Testing 101 (3/10): 통합 테스트](./03-integration-test.md)
- [Testing 101 (4/10): E2E 테스트](./04-e2e-test.md)
- [Testing 101 (5/10): 테스트 더블](./05-test-double.md)
- **Mock과 Stub (현재 글)**
- 테스트 커버리지 (예정)
- 회귀 테스트 (예정)
- CI에서 테스트 실행하기 (예정)
- 테스트 전략 세우기 (예정)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소(book-examples): https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko
- [unittest.mock docs](https://docs.python.org/3/library/unittest.mock.html)
- [Martin Fowler — Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html)
- [pytest-mock](https://pytest-mock.readthedocs.io/)
- [Sandi Metz — POODR](https://www.poodr.com/)

Tags: Testing, Mock, Stub, unittest.mock, Python
