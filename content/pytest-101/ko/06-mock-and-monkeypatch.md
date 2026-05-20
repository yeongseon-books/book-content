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

## 먼저 던지는 질문

- mock과 monkeypatch는 무엇이 다를까요?
- `patch()`는 어디를 기준으로 적용해야 할까요?
- 외부 호출이 실패하는 상황은 어떻게 재현할 수 있을까요?

## 큰 그림

![pytest 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/06/06-01-big-picture.ko.png)

*pytest 101 6장 흐름 개요*

이 그림에서는 mock과 monkeypatch를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> mock과 monkeypatch의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

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

### Step 2: Replacing a Function with monkeypatch

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

### Step 3: Simulating Exceptions with side_effect

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

### Step 4: Setting Environment Variables with monkeypatch

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

Tags: Python, pytest, mock, monkeypatch, 테스트 더블
