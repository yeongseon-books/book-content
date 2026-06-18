---
title: "바이브코딩을 위한 Pytest 기초 (6/10): mock과 monkeypatch"
series: pytest-101
episode: 6
targets:
  wordpress: true
tags:
  - Python
  - pytest
  - mock
  - monkeypatch
  - 테스트 더블
  - 바이브코딩
---

# 바이브코딩을 위한 Pytest 기초 (6/10): mock과 monkeypatch

이 글은 **바이브코딩을 위한 Pytest 기초** 시리즈의 여섯 번째 글입니다. AI가 생성한 코드를 pytest로 검증하는 방법을 10편에 걸쳐 다룹니다.

---

AI가 생성한 코드는 외부 API, 데이터베이스, 환경변수에 의존하는 경우가 많습니다. 실제 외부 시스템을 호출하지 않고도 이 코드를 검증하려면 mock과 monkeypatch가 필요합니다. AI에게 "외부 의존성을 mock으로 격리한 테스트를 작성해 달라"고 요청하면 네트워크 없이도 안정적인 테스트를 만들 수 있습니다.

핵심은 실제 외부 시스템을 호출하지 않고도 코드의 동작 계약을 검증하는 것입니다. 어떤 값을 반환해야 하는지, 어떤 파라미터로 호출해야 하는지, 실패 상황에서 예외를 어떻게 처리해야 하는지를 테스트 안에서 통제할 수 있어야 합니다.

> "AI가 외부 API를 호출하는 코드를 생성했다면, 실제 API 없이 동작을 검증하는 mock 테스트를 요청하세요. CI에서도 네트워크 없이 안정적으로 실행됩니다."

---

## 이 글에서 다룰 문제

- mock과 monkeypatch는 무엇이 다를까요?
- `patch()`는 어디를 기준으로 적용해야 할까요?
- AI가 생성한 외부 API 호출 코드를 어떻게 격리할 수 있을까요?
- 외부 호출이 실패하는 상황은 어떻게 재현할 수 있을까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

---

## 왜 이 글이 중요한가

단위 테스트의 핵심은 대상 함수를 고립된 상태에서 검증하는 것입니다. AI가 생성한 코드가 DB, 네트워크, 파일 시스템에 직접 의존하면 테스트는 환경 영향을 크게 받습니다. 이때 mock과 monkeypatch는 외부 세계를 잘라내고 함수 자체의 계약만 검증하게 해 줍니다.

실무에서는 외부 서비스 장애 때문에 테스트가 깨지는 일을 줄이는 데도 이 패턴이 중요합니다. AI 코드에 테스트를 붙일 때 mock을 활용하면 CI에서 외부 서비스 없이도 빠르게 검증할 수 있습니다.

---

## 핵심 개념 잡기

> mock = 실제 객체 대신 가짜 객체를 넣어 테스트를 고립시키는 기법

```text
[프로덕션]                        [테스트]
함수 → DB 쿼리 → 결과              함수 → Mock(DB) → 가짜 결과
함수 → HTTP 호출 → 응답            함수 → Mock(HTTP) → 가짜 응답
```

---

## 주요 개념 정리

| 용어 | 설명 |
|------|------|
| mock | 실제 객체를 대체하는 가짜 객체입니다 |
| patch | 특정 import 경로의 객체를 mock으로 교체합니다 |
| monkeypatch | 속성, 함수, 환경변수를 테스트 범위 안에서 임시 변경하는 pytest fixture입니다 |
| MagicMock | 호출 기록과 속성 접근을 추적하는 mock 객체입니다 |
| side_effect | mock 호출 시 함수 실행 또는 예외 발생을 지정합니다 |

---

## Before / After: 실제 HTTP 호출 vs mock 기반 테스트

**Before: 실제 API를 호출하는 테스트**

```python
# AI 생성 코드
def get_user_name(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()["name"]

# 실제 API 호출 — 네트워크가 필요하고 느리며 불안정
def test_get_user_name():
    name = get_user_name(1)
    assert name == "Alice"
```

**After: mock으로 격리한 테스트**

```python
from unittest.mock import patch, MagicMock

def test_get_user_name():
    mock_response = MagicMock()
    mock_response.json.return_value = {"name": "Alice"}

    with patch("requests.get", return_value=mock_response):
        name = get_user_name(1)
    assert name == "Alice"
```

AI에게 "requests.get을 mock으로 격리한 테스트를 작성해 달라"고 요청하면 네트워크 없이 동작하는 테스트를 얻을 수 있습니다.

---

## 실습: mock과 monkeypatch

**단계 1: 외부 API mock**

```python
# weather.py (AI 생성)
import requests

def get_temperature(city: str) -> float:
    response = requests.get(
        f"https://api.weather.com/v1/current?city={city}"
    )
    return response.json()["temperature"]
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

**단계 2: monkeypatch로 환경변수 설정**

```python
# config.py (AI 생성)
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

**단계 3: side_effect로 예외 재현**

```python
import requests
from weather import get_temperature

def test_network_error():
    with patch("weather.requests.get", side_effect=requests.ConnectionError):
        with pytest.raises(requests.ConnectionError):
            get_temperature("Seoul")
```

**단계 4: 호출 검증**

```python
from unittest.mock import MagicMock, call

def process_items(items, handler):
    for item in items:
        handler(item)

def test_handler_called_for_each_item():
    mock_handler = MagicMock()
    process_items(["a", "b", "c"], mock_handler)
    assert mock_handler.call_count == 3
    mock_handler.assert_has_calls([call("a"), call("b"), call("c")])
```

---

## mock vs monkeypatch 비교

| 항목 | mock.patch | monkeypatch |
|---|---|---|
| 주요 목적 | 호출 검증, 반환값/예외 제어 | 속성/환경 임시 변경 |
| 강점 | 호출 횟수, 인자 검증 풍부 | 문법 간결, 자동 원복 |
| 자주 쓰는 대상 | HTTP 클라이언트, SDK 메서드 | 환경변수, 전역 상수, 함수 교체 |
| 실수 포인트 | patch 경로 오류 | 전역 상태 변경 범위 오해 |

---

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 정의 위치를 patch함 | 실제 import 경로가 달라 mock이 적용되지 않습니다 | 사용하는 모듈 경로를 patch합니다 |
| AI가 `patch("requests.get")`으로 생성함 | 다른 모듈에서 import한 경우 적용되지 않습니다 | `patch("weather.requests.get")`처럼 사용 모듈 기준으로 수정합니다 |
| `return_value`와 `side_effect`를 혼동함 | 고정 반환과 동적 동작은 목적이 다릅니다 | 상수 반환은 `return_value`, 예외는 `side_effect`를 씁니다 |
| 수동 `setattr`을 사용함 | 원복을 빼먹기 쉽습니다 | 속성 교체는 `monkeypatch`를 사용합니다 |
| mock을 너무 많이 씀 | 구현 세부사항에 테스트가 과하게 결합됩니다 | 결과 계약을 먼저 검증하고 mock은 최소화합니다 |

---

## AI 코딩 팁

AI가 외부 의존성을 포함한 코드를 생성할 때 테스트 요청 예시입니다.

```text
"아래 코드에서 requests.post 호출을 mock으로 격리한 pytest 테스트를 작성해 주세요.
- 정상 응답 케이스
- API 실패 응답 케이스 (status: 'fail')
- 네트워크 타임아웃 케이스 (requests.Timeout)
patch 경로는 사용하는 모듈 기준으로 지정해 주세요."
```

patch 경로 오류는 AI 생성 테스트에서 가장 흔한 실수입니다.

```python
# AI가 잘못 생성하는 경우
with patch("requests.post", return_value=fake):
    charge(1000)  # mock이 적용되지 않음

# 올바른 방법
with patch("payment.requests.post", return_value=fake):
    charge(1000)  # payment 모듈에서 사용하는 requests.post를 교체
```

---

## 체크리스트

- [ ] `unittest.mock.patch`로 외부 의존성을 대체했다
- [ ] `monkeypatch.setattr`로 함수를 교체했다
- [ ] `monkeypatch.setenv`로 환경변수를 설정했다
- [ ] `side_effect`로 예외를 재현했다
- [ ] patch 경로를 사용 모듈 기준으로 지정했다
- [ ] AI 생성 테스트에서 patch 경로가 올바른지 확인했다

---

## 처음 질문으로 돌아가기

- **mock과 monkeypatch는 무엇이 다를까요?**
  - mock은 호출 횟수·인자 검증이 필요할 때, monkeypatch는 환경변수·전역 상수처럼 임시 변경이 목적일 때 더 적합합니다. AI에게 용도에 맞게 선택하도록 명시하세요.
- **`patch()`는 어디를 기준으로 적용해야 할까요?**
  - 정의된 곳이 아니라 사용되는 모듈 경로를 기준으로 합니다. AI가 `requests.get`으로 생성하면 `weather.requests.get`으로 수정해야 합니다.
- **AI가 생성한 외부 API 호출 코드를 어떻게 격리할 수 있을까요?**
  - AI에게 "외부 호출을 mock으로 대체하고, 정상/실패/타임아웃 케이스를 각각 테스트해 달라"고 요청합니다.

---

## 정리

mock과 monkeypatch는 외부 의존성을 잘라내어 단위 테스트를 빠르고 안정적으로 만들어 줍니다. AI가 생성한 외부 API 호출 코드를 검증할 때 가장 먼저 익혀야 할 도구입니다. 다음 글에서는 파일, 환경변수, 현재 시간처럼 시스템 리소스에 의존하는 코드를 테스트하는 패턴을 더 구체적으로 다룹니다.

---

## 참고 자료

- [pytest — monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- [unittest.mock — Python Docs](https://docs.python.org/3/library/unittest.mock.html)
- [Real Python — Understanding the Python Mock Object Library](https://realpython.com/python-mock-library/)
- [pytest-mock — Plugin Documentation](https://pytest-mock.readthedocs.io/)
- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Pytest 기초 (1/10): 왜 테스트를 작성해야 할까?
- 바이브코딩을 위한 Pytest 기초 (2/10): 첫 번째 pytest 테스트 작성하기
- 바이브코딩을 위한 Pytest 기초 (3/10): assert와 예외 테스트
- 바이브코딩을 위한 Pytest 기초 (4/10): fixture 이해하기
- 바이브코딩을 위한 Pytest 기초 (5/10): parametrization으로 테스트 케이스 늘리기
- **바이브코딩을 위한 Pytest 기초 (6/10): mock과 monkeypatch (현재 글)**
- 바이브코딩을 위한 Pytest 기초 (7/10): 파일, 환경변수, 시간 테스트하기
- 바이브코딩을 위한 Pytest 기초 (8/10): coverage와 테스트 품질 보기
- 바이브코딩을 위한 Pytest 기초 (9/10): GitHub Actions에서 테스트 자동화하기
- 바이브코딩을 위한 Pytest 기초 (10/10): 테스트하기 쉬운 코드 구조 만들기
<!-- toc:end -->

Tags: Python, pytest, mock, monkeypatch, 테스트 더블, 바이브코딩
