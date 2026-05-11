---
series: pytest-101
episode: 6
title: mock과 monkeypatch
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - pytest
  - mock
  - monkeypatch
  - 테스트 더블
seo_description: mock과 monkeypatch로 외부 의존성을 격리하는 방법을 실습합니다.
last_reviewed: '2026-05-11'
---

# mock과 monkeypatch

> pytest 101 시리즈 (6/10)


## 이 글에서 다룰 문제

단위 테스트는 하나의 함수만 검증해야 합니다. 그런데 함수가 데이터베이스, 외부 API, 파일 시스템에 의존하면 테스트가 느리고, 불안정하고, 환경에 종속됩니다. mock으로 의존성을 제거하면 빠르고 안정적인 테스트가 됩니다.

> mock은 "이 함수가 외부 세계와 어떻게 상호작용하는지"를 검증합니다. 실제 API를 호출하지 않고도 "올바른 파라미터로 호출했는지"를 확인합니다.

실무에서 외부 서비스 장애 때문에 테스트가 실패하는 상황을 mock으로 예방합니다.

## 핵심 개념 잡기

> mock = 진짜 대신 가짜를 넣어서 테스트를 격리하는 기법

```text
[프로덕션]                    [테스트]
함수 → DB 쿼리 → 결과        함수 → Mock(DB) → 가짜 결과
함수 → HTTP 호출 → 응답      함수 → Mock(HTTP) → 가짜 응답
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| mock | 실제 객체를 대체하는 가짜 객체입니다 |
| patch | 특정 경로의 객체를 mock으로 교체합니다 |
| monkeypatch | pytest 내장 fixture로 속성, 환경변수를 임시 변경합니다 |
| MagicMock | 모든 속성과 메서드 호출을 기록하는 mock 객체입니다 |
| side_effect | mock 호출 시 실행할 함수나 발생할 예외를 지정합니다 |

## Before / After

실제 API를 호출하는 테스트와 mock으로 격리한 테스트를 비교합니다.

```python
# 이전 방식: 실제 HTTP 호출 — 느리고 외부 의존적입니다
import requests

def get_user_name(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()["name"]

def test_get_user_name():
    # 실제 API를 호출합니다 — 네트워크가 필요하고 느리며 불안정합니다
    name = get_user_name(1)
    assert name == "Alice"
```

```python
# 개선 방식: mock으로 HTTP 호출을 대체합니다
from unittest.mock import patch, MagicMock

def test_get_user_name():
    mock_response = MagicMock()
    mock_response.json.return_value = {"name": "Alice"}

    with patch("requests.get", return_value=mock_response):
        name = get_user_name(1)
    assert name == "Alice"
```

## 단계별 실습

### Step 1: 기본 mock 사용

```python
# weather.py 파일
import requests

def get_temperature(city: str) -> float:
    response = requests.get(
        f"https://api.weather.com/v1/current?city={city}"
    )
    data = response.json()
    return data["temperature"]
```

```python
# test_weather.py 파일
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

### Step 2: monkeypatch로 함수 교체

```python
# notification.py 파일
import smtplib

def send_email(to: str, subject: str, body: str) -> bool:
    server = smtplib.SMTP("smtp.example.com")
    server.sendmail("noreply@example.com", to, f"Subject: {subject}\n\n{body}")
    server.quit()
    return True
```

```python
# test_notification.py 파일
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

### Step 3: side_effect로 예외 시뮬레이션

```python
# test_error_handling.py 파일
from unittest.mock import patch
import requests
from weather import get_temperature

def test_network_error():
    with patch("weather.requests.get", side_effect=requests.ConnectionError):
        try:
            get_temperature("Seoul")
            assert False, "예외가 발생해야 합니다"
        except requests.ConnectionError:
            pass  # 기대한 예외 발생

def test_invalid_json():
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("잘못된 JSON")

    with patch("weather.requests.get", return_value=mock_response):
        try:
            get_temperature("Seoul")
            assert False, "예외가 발생해야 합니다"
        except ValueError:
            pass
```

### Step 4: monkeypatch로 환경변수 설정

```python
# config.py 파일
import os

def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL이 설정되지 않았습니다")
    return url
```

```python
# test_config.py 파일
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

### Step 5: 호출 검증 패턴

```python
# test_call_verification.py 파일
from unittest.mock import patch, call

def process_items(items, handler):
    for item in items:
        handler(item)

def test_handler_called_for_each_item():
    from unittest.mock import MagicMock
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

- `patch`의 첫 번째 인자는 "mock 대상이 사용되는 위치"입니다 — 정의된 위치가 아닙니다
- `monkeypatch`는 fixture이므로 테스트 종료 시 자동으로 원래 값을 복원합니다
- `side_effect`로 예외를 발생시켜 에러 핸들링을 테스트합니다
- `assert_called_once_with`로 정확한 파라미터를 검증합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| patch 경로를 정의 위치로 지정 | 실제 import 경로와 달라서 mock이 적용되지 않습니다 | mock 대상이 import되는 경로를 사용합니다 |
| mock을 너무 많이 사용 | 구현 세부사항에 결합되어 리팩터링이 어려워집니다 | 행위가 아닌 결과를 검증합니다 |
| return_value와 side_effect 혼동 | 고정 값 반환과 함수 실행은 다릅니다 | 고정 값은 return_value, 동적 동작은 side_effect입니다 |
| monkeypatch로 내장 함수 교체 후 복원 누락 | pytest가 자동 복원하지만, 수동 setattr은 복원이 필요합니다 | 항상 monkeypatch fixture를 사용합니다 |
| mock 객체의 오타 속성 접근 | MagicMock은 모든 속성을 자동 생성하여 오타를 숨깁니다 | `spec=True`로 실제 객체의 인터페이스를 강제합니다 |

## 실무에서 이렇게 쓰입니다

- 외부 API 호출을 mock하여 CI에서 네트워크 없이 테스트합니다
- monkeypatch로 환경변수를 테스트별로 격리합니다
- 결제 모듈 같은 부작용이 큰 코드를 mock으로 안전하게 테스트합니다
- `spec=True`로 mock 객체의 인터페이스를 실제 객체와 동기화합니다
- 타임아웃, 네트워크 에러 같은 실패 시나리오를 side_effect로 시뮬레이션합니다

## 현업 개발자는 이렇게 생각합니다

mock은 강력한 도구이지만, 남용하면 "테스트가 구현을 테스트하는" 상황이 됩니다. mock이 5개 이상 필요하다면, 코드의 의존성이 너무 많다는 신호입니다.

monkeypatch는 환경변수, 설정값 같은 단순한 대체에 적합하고, unittest.mock은 복잡한 호출 검증에 적합합니다. 상황에 맞는 도구를 선택합니다.

## 체크리스트

- [ ] `unittest.mock.patch`로 외부 의존성을 mock했다
- [ ] `monkeypatch.setattr`로 함수를 교체했다
- [ ] `monkeypatch.setenv`로 환경변수를 설정했다
- [ ] `side_effect`로 예외를 시뮬레이션했다
- [ ] `assert_called_once_with`로 호출을 검증했다

## 정리 및 다음 글 안내

mock과 monkeypatch는 외부 의존성을 제거하여 테스트를 빠르고 안정적으로 만드는 도구입니다. 다음 글에서는 파일, 환경변수, 시간 같은 시스템 리소스를 테스트하는 구체적 패턴을 배웁니다.

<!-- toc:begin -->
- [왜 테스트를 작성해야 할까?](./01-why-write-tests.md)
- [첫 번째 pytest 테스트 작성하기](./02-first-pytest-test.md)
- [assert와 예외 테스트](./03-assert-and-exceptions.md)
- [fixture 이해하기](./04-fixtures.md)
- [parametrization으로 테스트 케이스 늘리기](./05-parametrization.md)
- **mock과 monkeypatch (현재 글)**
- 파일, 환경변수, 시간 테스트하기 (예정)
- coverage와 테스트 품질 보기 (예정)
- GitHub Actions에서 테스트 자동화하기 (예정)
- 테스트하기 쉬운 코드 구조 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [pytest — monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- [unittest.mock — Python 공식 문서](https://docs.python.org/3/library/unittest.mock.html)
- [Real Python — Understanding the Python Mock Object Library](https://realpython.com/python-mock-library/)
- [pytest-mock — 플러그인 문서](https://pytest-mock.readthedocs.io/)

Tags: Python, pytest, mock, monkeypatch, 테스트 더블
