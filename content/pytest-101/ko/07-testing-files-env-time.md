---
series: pytest-101
episode: 7
title: 파일, 환경변수, 시간 테스트하기
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
  - tmp_path
  - freezegun
  - 시스템 리소스 테스트
seo_description: 파일, 환경변수, 시간 의존 코드를 pytest로 테스트하는 패턴을 실습합니다.
last_reviewed: '2026-05-04'
---

# 파일, 환경변수, 시간 테스트하기

> pytest 101 시리즈 (7/10)


## 이 글에서 다룰 문제

파일 I/O, 환경변수, 현재 시간은 테스트에서 가장 까다로운 외부 의존성입니다. 임시 디렉터리 없이 파일을 테스트하면 테스트 간 충돌이 발생하고, 시간에 의존하는 테스트는 자정이나 월말에 실패합니다.

> 시스템 리소스에 의존하는 테스트는 "오늘은 통과하고 내일은 실패하는" 유령 테스트(flaky test)의 주범입니다.

이 세 가지 패턴을 익히면 대부분의 시스템 의존성을 격리할 수 있습니다.

## 핵심 개념 잡기

> 시스템 리소스 격리 = 파일, 환경변수, 시간을 테스트 범위 안에서 통제

```
[격리 전]                      [격리 후]
파일 → 실제 경로 충돌          tmp_path → 자동 정리
환경변수 → 전역 오염           monkeypatch → 테스트 종료 시 복원
시간 → 실행 시점마다 다름      freezegun → 고정된 시간
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| tmp_path | pytest 내장 fixture로 테스트별 임시 디렉터리를 제공합니다 |
| tmp_path_factory | session scope로 여러 테스트가 공유하는 임시 디렉터리를 생성합니다 |
| monkeypatch.setenv | 테스트 범위 내에서 환경변수를 설정합니다 |
| freezegun | `datetime.now()`를 고정된 시간으로 대체하는 라이브러리입니다 |
| flaky test | 동일한 코드에서 때때로 실패하는 불안정한 테스트입니다 |

## Before / After

실제 파일 시스템을 사용하는 테스트와 tmp_path로 격리한 테스트를 비교합니다.

```python
# before: 실제 경로 사용 — 테스트 간 충돌 위험
import os

def test_write_file():
    with open("/tmp/test_output.txt", "w") as f:
        f.write("hello")
    with open("/tmp/test_output.txt") as f:
        assert f.read() == "hello"
    os.remove("/tmp/test_output.txt")  # 정리 누락 시 오염
```

```python
# after: tmp_path 사용 — 자동 격리, 자동 정리
def test_write_file(tmp_path):
    filepath = tmp_path / "test_output.txt"
    filepath.write_text("hello")
    assert filepath.read_text() == "hello"
    # 정리 불필요 — pytest가 자동 처리
```

## 단계별 실습

### Step 1: tmp_path로 파일 테스트

```python
# file_processor.py
from pathlib import Path
import json

def save_config(config: dict, filepath: Path) -> None:
    filepath.write_text(json.dumps(config, indent=2))

def load_config(filepath: Path) -> dict:
    if not filepath.exists():
        raise FileNotFoundError(f"{filepath}이(가) 존재하지 않습니다")
    return json.loads(filepath.read_text())
```

```python
# test_file_processor.py
import pytest
from pathlib import Path
from file_processor import save_config, load_config

def test_save_and_load(tmp_path):
    config = {"host": "localhost", "port": 8080}
    filepath = tmp_path / "config.json"

    save_config(config, filepath)
    loaded = load_config(filepath)

    assert loaded == config

def test_load_missing_file(tmp_path):
    filepath = tmp_path / "missing.json"
    with pytest.raises(FileNotFoundError):
        load_config(filepath)

def test_nested_directory(tmp_path):
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)
    filepath = nested / "deep.txt"
    filepath.write_text("deep content")
    assert filepath.read_text() == "deep content"
```

### Step 2: 여러 파일 처리 테스트

```python
# csv_processor.py
from pathlib import Path
import csv

def merge_csv_files(input_dir: Path, output_file: Path) -> int:
    rows = []
    for csv_file in sorted(input_dir.glob("*.csv")):
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            rows.extend(reader)

    if not rows:
        return 0

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
```

```python
# test_csv_processor.py
from csv_processor import merge_csv_files

def test_merge_csv(tmp_path):
    # 입력 파일 생성
    (tmp_path / "a.csv").write_text("name,age\nAlice,30\n")
    (tmp_path / "b.csv").write_text("name,age\nBob,25\n")

    output = tmp_path / "merged.csv"
    count = merge_csv_files(tmp_path, output)

    assert count == 2
    lines = output.read_text().strip().split("\n")
    assert len(lines) == 3  # 헤더 + 2행

def test_merge_empty_dir(tmp_path):
    output = tmp_path / "merged.csv"
    count = merge_csv_files(tmp_path, output)
    assert count == 0
```

### Step 3: 환경변수 테스트

```python
# app_config.py
import os

def get_config() -> dict:
    return {
        "debug": os.environ.get("DEBUG", "false").lower() == "true",
        "db_url": os.environ.get("DATABASE_URL", "sqlite:///default.db"),
        "log_level": os.environ.get("LOG_LEVEL", "INFO"),
    }
```

```python
# test_app_config.py
from app_config import get_config

def test_default_config(monkeypatch):
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    config = get_config()
    assert config["debug"] is False
    assert config["db_url"] == "sqlite:///default.db"
    assert config["log_level"] == "INFO"

def test_production_config(monkeypatch):
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql://prod:5432/app")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")

    config = get_config()
    assert config["debug"] is False
    assert "postgresql" in config["db_url"]
    assert config["log_level"] == "WARNING"

def test_debug_mode(monkeypatch):
    monkeypatch.setenv("DEBUG", "True")
    config = get_config()
    assert config["debug"] is True
```

### Step 4: 시간 고정 테스트

```python
# billing.py
from datetime import datetime

def is_billing_day() -> bool:
    return datetime.now().day == 1

def days_until_expiry(expiry_date: datetime) -> int:
    delta = expiry_date - datetime.now()
    return max(0, delta.days)

def format_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

```python
# test_billing.py
from datetime import datetime
from unittest.mock import patch
from billing import is_billing_day, days_until_expiry, format_timestamp

def test_is_billing_day_true():
    fixed_time = datetime(2025, 1, 1, 12, 0, 0)
    with patch("billing.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_time
        assert is_billing_day() is True

def test_is_billing_day_false():
    fixed_time = datetime(2025, 1, 15, 12, 0, 0)
    with patch("billing.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_time
        assert is_billing_day() is False

def test_days_until_expiry():
    now = datetime(2025, 1, 1, 12, 0, 0)
    expiry = datetime(2025, 1, 11, 12, 0, 0)
    with patch("billing.datetime") as mock_dt:
        mock_dt.now.return_value = now
        assert days_until_expiry(expiry) == 10

def test_format_timestamp():
    fixed_time = datetime(2025, 3, 15, 14, 30, 0)
    with patch("billing.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_time
        mock_dt.now.return_value.strftime = fixed_time.strftime
        result = format_timestamp()
    assert result == "2025-03-15 14:30:00"
```

### Step 5: freezegun 활용

```bash
pip install freezegun
```

```python
# test_billing_freezegun.py
from freezegun import freeze_time
from billing import is_billing_day, format_timestamp

@freeze_time("2025-01-01 12:00:00")
def test_billing_day_with_freezegun():
    assert is_billing_day() is True

@freeze_time("2025-03-15 14:30:00")
def test_format_with_freezegun():
    assert format_timestamp() == "2025-03-15 14:30:00"

@freeze_time("2025-01-15")
def test_not_billing_day():
    assert is_billing_day() is False
```

## 이 코드에서 주목할 점

- `tmp_path`는 `pathlib.Path` 객체이므로 `/` 연산자로 경로를 조합합니다
- `monkeypatch.delenv`로 환경변수가 없는 상황을 명시적으로 테스트합니다
- `freeze_time`은 데코레이터 하나로 시간을 고정하여 mock보다 간결합니다
- 각 테스트가 독립적으로 실행되므로 환경 오염이 없습니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 절대 경로로 파일을 생성 | 다른 환경에서 실패하고 테스트 간 충돌합니다 | `tmp_path`를 항상 사용합니다 |
| 환경변수를 `os.environ`에 직접 설정 | 테스트 종료 후 복원하지 않으면 다른 테스트에 영향을 줍니다 | `monkeypatch.setenv`를 사용합니다 |
| `datetime.now()`를 직접 비교 | 실행 시점에 따라 결과가 달라집니다 | 시간을 주입하거나 freezegun을 사용합니다 |
| tmp_path 내용을 수동으로 정리 | pytest가 자동으로 정리하므로 불필요합니다 | 정리 코드를 제거합니다 |
| 시간대(timezone) 미고려 | UTC와 로컬 시간 차이로 테스트가 실패합니다 | 항상 UTC를 명시하거나 timezone-aware datetime을 사용합니다 |

## 실무에서 이렇게 쓰입니다

- 로그 파일을 `tmp_path`에 생성하여 로그 포맷을 검증합니다
- 12개월 환경변수 조합을 parametrize와 monkeypatch로 일괄 테스트합니다
- 만료일 검증 로직을 freezegun으로 과거, 현재, 미래 시점에서 테스트합니다
- CI 환경에서 `tmp_path`를 사용하여 파일 권한 차이를 회피합니다
- 배치 잡의 스케줄 로직을 고정 시간으로 테스트합니다

## 현업 개발자는 이렇게 생각합니다

파일, 환경변수, 시간은 "코드 바깥의 세계"입니다. 테스트에서 이 세계를 통제하지 않으면, 테스트 결과가 코드가 아닌 환경에 의해 결정됩니다.

tmp_path는 pytest의 가장 유용한 내장 fixture 중 하나입니다. 모든 파일 I/O 테스트의 출발점으로 삼으면 됩니다.

## 체크리스트

- [ ] `tmp_path`로 임시 파일을 생성하고 테스트에 사용했다
- [ ] `monkeypatch.setenv/delenv`로 환경변수를 격리했다
- [ ] `unittest.mock.patch` 또는 `freezegun`으로 시간을 고정했다
- [ ] 파일이 없는 경우의 에러 처리를 테스트했다
- [ ] 테스트 간 상태 오염이 없는지 확인했다

## 정리 및 다음 글 안내

tmp_path, monkeypatch, freezegun으로 시스템 리소스를 격리하면 안정적이고 재현 가능한 테스트를 작성할 수 있습니다. 다음 글에서는 coverage를 측정하고 테스트 품질을 평가하는 방법을 배웁니다.

<!-- toc:begin -->
- [왜 테스트를 작성해야 할까?](./01-why-write-tests.md)
- [첫 번째 pytest 테스트 작성하기](./02-first-pytest-test.md)
- [assert와 예외 테스트](./03-assert-and-exceptions.md)
- [fixture 이해하기](./04-fixtures.md)
- [parametrization으로 테스트 케이스 늘리기](./05-parametrization.md)
- [mock과 monkeypatch](./06-mock-and-monkeypatch.md)
- **파일, 환경변수, 시간 테스트하기 (현재 글)**
- coverage와 테스트 품질 보기 (예정)
- GitHub Actions에서 테스트 자동화하기 (예정)
- 테스트하기 쉬운 코드 구조 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [pytest — tmp_path](https://docs.pytest.org/en/stable/how-to/tmp_path.html)
- [pytest — monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- [freezegun — GitHub](https://github.com/spulec/freezegun)
- [Real Python — Testing with tmp_path](https://realpython.com/pytest-python-testing/#tmp-path)

Tags: Python, pytest, tmp_path, freezegun, 시스템 리소스 테스트
