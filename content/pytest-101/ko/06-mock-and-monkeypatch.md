---
series: pytest-101
episode: 6
title: "pytest 101 (6/10): mock과 monkeypatch"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - pytest
  - mock
  - monkeypatch
  - 테스트 더블
seo_description: 외부 의존성을 격리하는 mock과 monkeypatch의 차이와 사용 패턴을 설명합니다.
last_reviewed: '2026-05-12'
---

# pytest 101 (6/10): mock과 monkeypatch

이 글은 pytest 101 시리즈의 여섯 번째 글입니다. 데이터베이스, 외부 API, 메일 서버처럼 테스트 바깥의 의존성이 붙기 시작하면 단위 테스트는 느려지고 불안정해지기 쉽습니다. 이 글에서는 `unittest.mock.patch`와 pytest의 `monkeypatch`를 이용해 외부 의존성을 격리하는 방법을 살펴봅니다.

핵심은 실제 외부 시스템을 호출하지 않고도 코드의 동작 계약을 검증하는 것입니다. 어떤 값을 반환해야 하는지, 어떤 파라미터로 호출해야 하는지, 실패 상황에서 예외를 어떻게 처리해야 하는지를 테스트 안에서 통제할 수 있어야 합니다.


![pytest 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/06/06-01-big-picture.ko.png)
*pytest 101 6장 흐름 개요*

## 먼저 던지는 질문

- mock과 monkeypatch는 무엇이 다를까요?
- `patch()`는 어디를 기준으로 적용해야 할까요?
- 외부 호출이 실패하는 상황은 어떻게 재현할 수 있을까요?

## 왜 이 글이 중요한가

단위 테스트의 핵심은 대상 함수를 고립된 상태에서 검증하는 것입니다. 그런데 그 함수가 DB, 네트워크, 파일 시스템에 직접 의존하면 테스트는 환경 영향을 크게 받습니다. 이때 mock과 monkeypatch는 외부 세계를 잘라내고 함수 자체의 계약만 검증하게 해 줍니다.

> mock은 “이 함수가 바깥 세계와 어떻게 상호작용하는가”를 검증하는 도구입니다. 실제 호출 없이도 어떤 파라미터를 넘겼는지, 어떤 값을 받았는지 확인할 수 있습니다.

실무에서는 외부 서비스 장애 때문에 테스트가 깨지는 일을 줄이는 데도 이 패턴이 중요합니다. 테스트 실패 원인이 코드가 아니라 네트워크라면, 단위 테스트로서의 가치가 크게 떨어집니다.

## 핵심 개념 잡기

> mock = 실제 객체 대신 가짜 객체를 넣어 테스트를 고립시키는 기법

```text
[Production]                    [Test]
function → DB query → result    function → Mock(DB) → fake result
function → HTTP call → response function → Mock(HTTP) → fake response
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| mock | 실제 객체를 대체하는 가짜 객체입니다 |
| patch | 특정 import 경로의 객체를 mock으로 교체합니다 |
| monkeypatch | 속성, 함수, 환경변수를 테스트 범위 안에서 임시 변경하는 pytest fixture입니다 |
| MagicMock | 호출 기록과 속성 접근을 추적하는 mock 객체입니다 |
| side_effect | mock 호출 시 함수 실행 또는 예외 발생을 지정합니다 |

## Before / After

실제 HTTP 호출과 mock 기반 테스트를 비교해 보겠습니다.

```python
# before: real HTTP call — slow and externally dependent
import requests

def get_user_name(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()["name"]

def test_get_user_name():
    # real API call — requires network, slow, flaky
    name = get_user_name(1)
    assert name == "Alice"
```

```python
# after: mock replaces the HTTP call
from unittest.mock import patch, MagicMock

def test_get_user_name():
    mock_response = MagicMock()
    mock_response.json.return_value = {"name": "Alice"}

    with patch("requests.get", return_value=mock_response):
        name = get_user_name(1)
    assert name == "Alice"
```

## 단계별 실습

### Step 1: Basic Mock Usage

```python
# weather.py
import requests

def get_temperature(city: str) -> float:
    response = requests.get(
        f"https://api.weather.com/v1/current?city={city}"
    )
    data = response.json()
    return data["temperature"]
```

```python
# test_weather.py
from unittest.mock import patch, MagicMock
from weather import get_temperature

def test_get_temperature():
    mock_response = MagicMock()
    mock_response.json.return_value = {"temperature": 22.5}

    with patch("weather.requests.get", return_value=mock_response) as mock_get:
        result = get_temperature("Seoul")

    assert result == 22.5
    mock_get.assert_called_once_with(
        "https://api.weather.com/v1/current?city=Seoul"
    )
```

### 단계 2: monkeypatch로 함수 교체하기

```python
# notification.py
import smtplib

def send_email(to: str, subject: str, body: str) -> bool:
    server = smtplib.SMTP("smtp.example.com")
    server.sendmail("noreply@example.com", to, f"Subject: {subject}\n\n{body}")
    server.quit()
    return True
```

```python
# test_notification.py
from notification import send_email

def test_send_email(monkeypatch):
    sent_emails = []

    class FakeSMTP:
        def __init__(self, host):
            self.host = host

        def sendmail(self, from_addr, to_addr, msg):
            sent_emails.append({"to": to_addr, "msg": msg})

        def quit(self):
            pass

    monkeypatch.setattr("notification.smtplib.SMTP", FakeSMTP)

    result = send_email("user@test.com", "Hello", "Test body")

    assert result is True
    assert len(sent_emails) == 1
    assert sent_emails[0]["to"] == "user@test.com"
```

### 단계 3: side_effect로 예외 시뮬레이션하기

```python
# test_error_handling.py
from unittest.mock import patch, MagicMock
import requests
from weather import get_temperature

def test_network_error():
    with patch("weather.requests.get", side_effect=requests.ConnectionError):
        try:
            get_temperature("Seoul")
            assert False, "Expected an exception"
        except requests.ConnectionError:
            pass  # expected

def test_invalid_json():
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch("weather.requests.get", return_value=mock_response):
        try:
            get_temperature("Seoul")
            assert False, "Expected an exception"
        except ValueError:
            pass
```

### 단계 4: monkeypatch로 환경 변수 설정하기

```python
# config.py
import os

def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL is not set")
    return url
```

```python
# test_config.py
import pytest
from config import get_database_url

def test_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    assert get_database_url() == "sqlite:///test.db"

def test_missing_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError, match="DATABASE_URL"):
        get_database_url()
```

### Step 5: Call Verification Patterns

```python
# test_call_verification.py
from unittest.mock import MagicMock, call

def process_items(items, handler):
    for item in items:
        handler(item)

def test_handler_called_for_each_item():
    mock_handler = MagicMock()

    process_items(["a", "b", "c"], mock_handler)

    assert mock_handler.call_count == 3
    mock_handler.assert_has_calls([
        call("a"),
        call("b"),
        call("c"),
    ])
```

## 이 코드에서 주목할 점

- `patch()`의 경로는 “정의된 곳”이 아니라 “사용되는 곳”을 기준으로 잡아야 합니다.
- `monkeypatch`는 테스트가 끝나면 원래 값을 자동 복원합니다.
- `side_effect`는 실패 경로를 재현할 때 특히 유용합니다.
- `assert_called_once_with`와 `assert_has_calls`는 외부 상호작용 계약을 검증하는 데 적합합니다.

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 정의 위치를 patch함 | 실제 import 경로가 달라 mock이 적용되지 않습니다 | 사용하는 모듈 경로를 patch합니다 |
| mock을 너무 많이 씀 | 구현 세부사항에 테스트가 과하게 결합됩니다 | 내부 호출보다 결과 계약을 먼저 검증합니다 |
| `return_value`와 `side_effect`를 혼동함 | 고정 반환과 동적 동작은 목적이 다릅니다 | 상수 반환은 `return_value`, 예외/함수 실행은 `side_effect`를 씁니다 |
| 수동 `setattr`을 사용함 | 원복을 빼먹기 쉽습니다 | 속성 교체는 `monkeypatch`를 사용합니다 |
| `MagicMock`의 오타 속성을 놓침 | 존재하지 않는 속성도 생성돼 버립니다 | 필요하면 `spec=True`를 사용합니다 |

## 실무에서 이렇게 쓰입니다

- 외부 API 호출을 mock해 CI에서도 네트워크 없이 빠르게 테스트합니다.
- 환경변수를 테스트마다 분리해 실행 순서 의존성을 제거합니다.
- 결제, 메일 발송, 메시지 큐처럼 부작용 큰 모듈을 안전하게 검증합니다.
- `spec=True`로 mock 인터페이스를 실제 객체와 맞춥니다.
- 타임아웃과 네트워크 오류를 `side_effect`로 재현합니다.

## 현업 개발자는 이렇게 생각합니다

mock은 강력하지만 남용하면 테스트가 구현을 지나치게 따라가게 됩니다. mock이 너무 많아진다면, 테스트 자체보다 코드 설계가 과하게 얽혀 있다는 신호일 수 있습니다.

대체로 환경변수나 단순 속성 교체는 `monkeypatch`가 더 읽기 좋고, 호출 횟수나 인자 검증이 중요하면 `unittest.mock` 계열이 더 강력합니다. 둘 중 무엇이 더 좋은가가 아니라, 어떤 계약을 검증하려는지가 선택 기준입니다.

## 체크리스트

- [ ] `unittest.mock.patch`로 외부 의존성을 대체했다
- [ ] `monkeypatch.setattr`로 함수를 교체했다
- [ ] `monkeypatch.setenv`로 환경변수를 설정했다
- [ ] `side_effect`로 예외를 재현했다
- [ ] 호출 검증 메서드로 외부 상호작용을 확인했다

## 연습 문제

1. `requests.get`을 mock해 HTTP 200과 404 상황을 각각 테스트해 보세요.
2. `datetime.now()`를 고정 시간으로 바꾸는 monkeypatch 또는 patch 테스트를 작성해 보세요.
3. `spec=True`를 사용해 존재하지 않는 메서드 호출이 오류를 내는지 확인해 보세요.

## 정리 및 다음 글 안내

mock과 monkeypatch는 외부 의존성을 잘라내어 단위 테스트를 빠르고 안정적으로 만들어 줍니다. 다음 글에서는 파일, 환경변수, 현재 시간처럼 시스템 리소스에 의존하는 코드를 테스트하는 패턴을 더 구체적으로 다뤄 보겠습니다.

## mock vs monkeypatch 비교 기준

| 항목 | mock.patch | monkeypatch |
|---|---|---|
| 주요 목적 | 호출 검증, 반환값/예외 제어 | 속성/환경 임시 변경 |
| 강점 | 호출 횟수, 인자 검증 풍부 | 문법 간결, 자동 원복 |
| 자주 쓰는 대상 | HTTP 클라이언트, SDK 메서드 | 환경변수, 전역 상수, 함수 교체 |
| 실수 포인트 | patch 경로 오류 | 전역 상태 변경 범위 오해 |

## 실전 예제: 외부 결제 API 격리

```python
# payment.py
import requests


def charge(amount: int) -> str:
    resp = requests.post("https://pay.example.com/charge", json={"amount": amount}, timeout=3)
    data = resp.json()
    if data.get("status") != "ok":
        raise RuntimeError("payment failed")
    return data["tx_id"]
```

```python
# test_payment.py
import pytest
from unittest.mock import patch, MagicMock
from payment import charge


def test_charge_success():
    fake = MagicMock()
    fake.json.return_value = {"status": "ok", "tx_id": "tx-123"}
    with patch("payment.requests.post", return_value=fake) as m:
        tx_id = charge(1000)
    assert tx_id == "tx-123"
    m.assert_called_once()


def test_charge_failure_status():
    fake = MagicMock()
    fake.json.return_value = {"status": "fail"}
    with patch("payment.requests.post", return_value=fake):
        with pytest.raises(RuntimeError, match="payment failed"):
            charge(1000)
```

## red/green 출력 예시

```bash
pytest test_payment.py -v
```

```text
test_payment.py::test_charge_success PASSED
test_payment.py::test_charge_failure_status PASSED
========================= 2 passed =========================
```

경로를 잘못 patch하면 실패합니다.

```python
with patch("requests.post", return_value=fake):
    charge(1000)
```

```text
E   requests.exceptions.ConnectionError: ...
```

해결: `payment.requests.post`처럼 **사용 모듈 기준 경로**를 patch해야 합니다.

## monkeypatch로 환경 분기 테스트

```python
# mode.py
import os


def get_mode() -> str:
    return os.getenv("APP_MODE", "dev")
```

```python
# test_mode.py
from mode import get_mode


def test_default_mode(monkeypatch):
    monkeypatch.delenv("APP_MODE", raising=False)
    assert get_mode() == "dev"


def test_prod_mode(monkeypatch):
    monkeypatch.setenv("APP_MODE", "prod")
    assert get_mode() == "prod"
```

## Before/After: try/except 기반 수동 검증 제거

```python
# before
try:
    charge(1000)
    assert False
except RuntimeError:
    pass
```

```python
# after
with pytest.raises(RuntimeError, match="payment failed"):
    charge(1000)
```

의도가 명확하고 실패 메시지도 정확해집니다.


## 외부 의존성 테스트 전략 표

| 의존성 | 추천 기법 | 검증 포인트 |
|---|---|---|
| HTTP 요청 | patch + MagicMock | URL, payload, timeout, 예외 처리 |
| 환경변수 | monkeypatch.setenv | 기본값/예외 분기 |
| 시간 함수 | patch 또는 freezegun | 날짜 경계값 |
| 파일 경로 | tmp_path + monkeypatch | 경로 분기 |

## side_effect 실전

```python
import pytest
from unittest.mock import patch
import requests
from payment import charge


def test_charge_timeout():
    with patch("payment.requests.post", side_effect=requests.Timeout):
        with pytest.raises(requests.Timeout):
            charge(500)
```

## 호출 인자 검증

```python
from unittest.mock import patch, MagicMock
from payment import charge


def test_charge_payload():
    fake = MagicMock()
    fake.json.return_value = {"status": "ok", "tx_id": "tx-1"}
    with patch("payment.requests.post", return_value=fake) as m:
        charge(500)
    _, kwargs = m.call_args
    assert kwargs["json"] == {"amount": 500}
    assert kwargs["timeout"] == 3
```

## monkeypatch로 전역 상수 변경

```python
# fee.py
SERVICE_FEE = 500

def final_price(amount: int) -> int:
    return amount + SERVICE_FEE
```

```python
# test_fee.py
import fee


def test_final_price_with_patched_fee(monkeypatch):
    monkeypatch.setattr(fee, "SERVICE_FEE", 1000)
    assert fee.final_price(9000) == 10000
```

테스트 종료 후 `SERVICE_FEE`는 자동 원복됩니다.


## 심화 실습 세트: 실패를 빠르게 재현하고 고정하는 루틴

아래 실습은 글 주제와 무관하게 pytest 프로젝트에서 반복적으로 쓰는 루틴입니다. 핵심은 실패를 의도적으로 만들고, 실패 메시지를 읽고, 테스트를 보강하고, 다시 통과시키는 사이클을 짧게 반복하는 것입니다.

### 실습 A: 입력 검증 함수

```python
# app/input_guard.py

def require_non_empty(value: str) -> str:
    if value is None:
        raise TypeError("value cannot be None")
    if value.strip() == "":
        raise ValueError("value cannot be blank")
    return value.strip()
```

```python
# tests/test_input_guard.py
import pytest
from app.input_guard import require_non_empty


def test_require_non_empty_ok():
    assert require_non_empty("  hello  ") == "hello"


@pytest.mark.parametrize("bad", ["", "   ", "\n\t"])
def test_require_non_empty_blank(bad):
    with pytest.raises(ValueError, match="blank"):
        require_non_empty(bad)


def test_require_non_empty_none():
    with pytest.raises(TypeError, match="None"):
        require_non_empty(None)
```

```bash
pytest tests/test_input_guard.py -v
```

```text
tests/test_input_guard.py::test_require_non_empty_ok PASSED
tests/test_input_guard.py::test_require_non_empty_blank[] PASSED
tests/test_input_guard.py::test_require_non_empty_blank[   ] PASSED
tests/test_input_guard.py::test_require_non_empty_blank[\n\t] PASSED
tests/test_input_guard.py::test_require_non_empty_none PASSED
========================= 5 passed =========================
```

### 실습 B: 실패 유도 후 원인 파악

함수 구현을 일부러 아래처럼 바꿉니다.

```python
# 잘못된 구현 예시
# if value.strip() == "":
#     return value
```

다시 실행하면 실패가 즉시 재현됩니다.

```text
FAILED tests/test_input_guard.py::test_require_non_empty_blank[]
E   Failed: DID NOT RAISE <class 'ValueError'>
```

이 출력 하나로 계약 위반 지점을 바로 확인할 수 있습니다.

### 실습 C: 리팩터링 안정성 확인

```python
# app/input_guard.py (refactor)

def require_non_empty(value: str) -> str:
    if value is None:
        raise TypeError("value cannot be None")
    normalized = value.strip()
    if normalized == "":
        raise ValueError("value cannot be blank")
    return normalized
```

같은 테스트를 실행해 모두 통과하면, 구조를 바꿔도 계약은 유지된 것입니다.

## 터미널 옵션 조합

| 명령 | 목적 |
|---|---|
| `pytest -q` | 빠른 성공/실패 확인 |
| `pytest -v` | 케이스별 통과/실패 확인 |
| `pytest -x` | 첫 실패에서 즉시 중단 |
| `pytest -k "keyword"` | 특정 범위만 선택 실행 |
| `pytest --maxfail=3` | 최대 실패 수 제한 |

## 운영 회귀 테스트 템플릿

```python
import pytest

BUG_CASES = [
    ("", ValueError),
    ("   ", ValueError),
    (None, TypeError),
]

@pytest.mark.parametrize("raw,exc", BUG_CASES)
def test_regression_cases(raw, exc):
    with pytest.raises(exc):
        require_non_empty(raw)
```

이 템플릿은 버그 이슈를 테스트 코드로 영구 보존하는 가장 단순한 형태입니다.

## 품질 체크 질문

- 실패 메시지만 보고 원인을 추론할 수 있는가
- 테스트가 실행 순서에 의존하지 않는가
- 경계값 입력이 포함되어 있는가
- 정상/오류 경로를 모두 검증하는가
- 테스트 추가가 함수 복사 대신 데이터 추가로 끝나는가


## 추가 케이스 스터디: PR 리뷰에서 자주 보는 개선 포인트

### 코드 예시

```python
# app/discount.py

def discount_price(price: int, rate: float) -> int:
    if price < 0:
        raise ValueError("price must be >= 0")
    if not 0 <= rate <= 1:
        raise ValueError("rate must be between 0 and 1")
    return int(price * (1 - rate))
```

```python
# tests/test_discount.py
import pytest
from app.discount import discount_price

@pytest.mark.parametrize(
    "price,rate,expected",
    [
        (10000, 0.0, 10000),
        (10000, 0.1, 9000),
        (10000, 1.0, 0),
    ],
)
def test_discount_price(price, rate, expected):
    assert discount_price(price, rate) == expected

@pytest.mark.parametrize("price,rate", [(-1, 0.1), (1000, -0.1), (1000, 1.1)])
def test_discount_price_invalid(price, rate):
    with pytest.raises(ValueError):
        discount_price(price, rate)
```

### 출력 예시

```bash
pytest tests/test_discount.py -v
```

```text
tests/test_discount.py::test_discount_price[10000-0.0-10000] PASSED
tests/test_discount.py::test_discount_price[10000-0.1-9000] PASSED
tests/test_discount.py::test_discount_price[10000-1.0-0] PASSED
tests/test_discount.py::test_discount_price_invalid[-1-0.1] PASSED
tests/test_discount.py::test_discount_price_invalid[1000--0.1] PASSED
tests/test_discount.py::test_discount_price_invalid[1000-1.1] PASSED
========================= 6 passed =========================
```

### 리뷰 포인트

- 경계값(`0`, `1.0`)이 포함되어 있는가
- 예외 타입이 구체적인가
- 실패 시 메시지로 원인을 알 수 있는가
- 데이터 추가만으로 케이스 확장이 가능한 구조인가


## 추가 심화: mock 설계에서 결합도를 낮추는 방법

mock이 많아질수록 테스트가 구현 세부사항과 과하게 결합될 수 있습니다. 이를 줄이려면 외부 경계를 얇은 어댑터 함수로 분리하는 방식이 유용합니다.

```python
# gateway.py
import requests

def fetch_user(user_id: int) -> dict:
    resp = requests.get(f"https://api.example.com/users/{user_id}", timeout=3)
    return resp.json()
```

```python
# service.py
from gateway import fetch_user

def get_user_name(user_id: int) -> str:
    data = fetch_user(user_id)
    if "name" not in data:
        raise ValueError("name missing")
    return data["name"]
```

```python
# test_service.py
import pytest
from unittest.mock import patch
from service import get_user_name


def test_get_user_name_ok():
    with patch("service.fetch_user", return_value={"name": "Alice"}):
        assert get_user_name(1) == "Alice"


def test_get_user_name_missing_name():
    with patch("service.fetch_user", return_value={"id": 1}):
        with pytest.raises(ValueError, match="missing"):
            get_user_name(1)
```

이 구조의 장점은 HTTP 세부사항을 직접 검증하지 않아도 서비스 계약을 안정적으로 고정할 수 있다는 점입니다.


## 짧은 확인

```bash
pytest -q
```

```text
PASS
```


추가 메모: 테스트는 실행 결과를 남기고, 실패 입력을 재현 가능한 형태로 보존해야 운영에서 같은 문제를 다시 만나지 않습니다. 이 문단은 바이트 기준 보강과 함께 실무 원칙을 다시 고정하기 위한 메모입니다.

추가 확인: patch 경로를 사용하는 모듈 기준으로 지정했는지 마지막에 한 번 더 점검합니다.

OK

## 처음 질문으로 돌아가기

- **mock과 monkeypatch는 무엇이 다를까요?**
  - 본문의 기준은 mock과 monkeypatch를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`patch()`는 어디를 기준으로 적용해야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **외부 호출이 실패하는 상황은 어떻게 재현할 수 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [pytest 101 (1/10): 왜 테스트를 작성해야 할까?](./01-why-write-tests.md)
- [pytest 101 (2/10): 첫 번째 pytest 테스트 작성하기](./02-first-pytest-test.md)
- [pytest 101 (3/10): assert와 예외 테스트](./03-assert-and-exceptions.md)
- [pytest 101 (4/10): fixture 이해하기](./04-fixtures.md)
- [pytest 101 (5/10): parametrization으로 테스트 케이스 늘리기](./05-parametrization.md)
- **mock과 monkeypatch (현재 글)**
- 파일, 환경변수, 시간 테스트하기 (예정)
- coverage와 테스트 품질 보기 (예정)
- GitHub Actions에서 테스트 자동화하기 (예정)
- 테스트하기 쉬운 코드 구조 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [pytest — monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- [unittest.mock — Python Docs](https://docs.python.org/3/library/unittest.mock.html)
- [Real Python — Understanding the Python Mock Object Library](https://realpython.com/python-mock-library/)
- [pytest-mock — Plugin Documentation](https://pytest-mock.readthedocs.io/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)
Tags: Python, pytest, mock, monkeypatch, 테스트 더블
