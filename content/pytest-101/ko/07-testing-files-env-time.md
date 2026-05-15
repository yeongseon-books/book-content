---
series: pytest-101
episode: 7
title: 파일, 환경변수, 시간 테스트하기
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
  - tmp_path
  - freezegun
  - 시스템 리소스 테스트
seo_description: tmp_path, monkeypatch, freezegun으로 파일·환경변수·시간 의존 코드를 테스트하는 방법을 설명합니다.
last_reviewed: '2026-05-12'
---

# 파일, 환경변수, 시간 테스트하기

이 글은 pytest 101 시리즈의 일곱 번째 글입니다. 파일 I/O, 환경변수, 현재 시간은 테스트를 불안정하게 만드는 대표적인 외부 의존성입니다. 이 글에서는 `tmp_path`, `monkeypatch`, `freezegun`을 이용해 시스템 리소스를 테스트 범위 안에서 통제하는 방법을 설명합니다.

이 영역이 어려운 이유는 코드 자체보다 실행 환경이 결과를 바꿔 버리기 때문입니다. 같은 코드인데도 오늘은 통과하고 내일은 실패하는 테스트가 생긴다면, 대개 파일 경로 충돌, 전역 환경변수 오염, 현재 시각 의존성이 원인입니다.

---

## 이 글에서 다룰 문제

- 파일 테스트에서 왜 실제 경로 대신 `tmp_path`를 써야 할까요?
- 환경변수는 왜 테스트마다 격리해야 할까요?
- 현재 시간을 기준으로 동작하는 로직은 어떻게 안정적으로 검증할 수 있을까요?
- 시스템 리소스 테스트를 flaky하지 않게 유지하려면 무엇을 조심해야 할까요?

## 왜 이 글이 중요한가

파일, 환경변수, 시간은 애플리케이션 밖의 세계와 직접 연결됩니다. 이 세계를 통제하지 않으면 테스트 결과가 코드가 아니라 환경에 의해 결정됩니다.

> 시스템 리소스에 의존하는 테스트는 “오늘은 통과하고 내일은 실패하는” flaky test의 가장 흔한 원인입니다.

이 세 가지를 제대로 다루기 시작하면, 파일 저장·설정 로딩·만료일 계산·배치 스케줄링처럼 실무에서 자주 만나는 코드를 훨씬 더 안정적으로 검증할 수 있습니다.

## 핵심 개념 잡기

> system resource isolation = 파일, 환경변수, 시간을 테스트 범위 안에서 통제하는 것

```text
[Before Isolation]                [After Isolation]
files → real path collisions      tmp_path → auto-cleanup
env vars → global pollution       monkeypatch → restored after test
time → varies per execution       freezegun → fixed time
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| tmp_path | 테스트별 임시 디렉터리를 제공하는 pytest 내장 fixture입니다 |
| tmp_path_factory | 여러 테스트가 공유할 임시 디렉터리를 만드는 session-scope fixture입니다 |
| monkeypatch.setenv | 테스트 범위 안에서 환경변수를 설정합니다 |
| freezegun | `datetime.now()`를 고정된 시각으로 대체하는 라이브러리입니다 |
| flaky test | 같은 코드에서도 간헐적으로 실패하는 테스트입니다 |

## Before / After

실제 경로를 쓰는 테스트와 `tmp_path` 기반 테스트를 비교해 보겠습니다.

```python
# before: real paths — risk of collisions between tests
import os

def test_write_file():
    with open("/tmp/test_output.txt", "w") as f:
        f.write("hello")
    with open("/tmp/test_output.txt") as f:
        assert f.read() == "hello"
    os.remove("/tmp/test_output.txt")  # leaked if forgotten
```

```python
# after: tmp_path — automatic isolation and cleanup
def test_write_file(tmp_path):
    filepath = tmp_path / "test_output.txt"
    filepath.write_text("hello")
    assert filepath.read_text() == "hello"
    # no cleanup needed — pytest handles it
```

## 단계별 실습

### Step 1: File Testing with tmp_path

```python
# file_processor.py
from pathlib import Path
import json

def save_config(config: dict, filepath: Path) -> None:
    filepath.write_text(json.dumps(config, indent=2))

def load_config(filepath: Path) -> dict:
    if not filepath.exists():
        raise FileNotFoundError(f"{filepath} does not exist")
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

### Step 2: Multi-File Processing Test

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
    (tmp_path / "a.csv").write_text("name,age\nAlice,30\n")
    (tmp_path / "b.csv").write_text("name,age\nBob,25\n")

    output = tmp_path / "merged.csv"
    count = merge_csv_files(tmp_path, output)

    assert count == 2
    lines = output.read_text().strip().split("\n")
    assert len(lines) == 3  # header + 2 rows

def test_merge_empty_dir(tmp_path):
    output = tmp_path / "merged.csv"
    count = merge_csv_files(tmp_path, output)
    assert count == 0
```

### Step 3: Environment Variable Testing

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

### Step 4: Freezing Time

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
```

### Step 5: Using freezegun

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

- `tmp_path`는 `pathlib.Path` 객체를 반환하므로 `/` 연산자로 경로를 조합합니다.
- `monkeypatch.delenv`는 “환경변수가 없는 상황”을 명시적으로 검증하게 해 줍니다.
- `freeze_time`은 수동 patch보다 간결하게 시간을 고정합니다.
- 각 테스트가 독립적으로 자원을 갖기 때문에 상태 오염이 줄어듭니다.

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 절대 경로에 파일을 만듦 | 환경마다 실패하거나 테스트끼리 충돌합니다 | 항상 `tmp_path`를 사용합니다 |
| `os.environ`을 직접 수정함 | 원복하지 않으면 다른 테스트에 영향을 줍니다 | `monkeypatch.setenv/delenv`를 사용합니다 |
| `datetime.now()`를 그대로 비교함 | 실행 시점에 따라 결과가 달라집니다 | 시간을 주입하거나 `freezegun`을 사용합니다 |
| tmp_path를 수동 정리함 | pytest가 이미 정리합니다 | 불필요한 cleanup 코드를 제거합니다 |
| timezone을 무시함 | UTC와 로컬 시간 차이로 실패할 수 있습니다 | 시간대 정책을 명확히 정합니다 |

## 실무에서 이렇게 쓰입니다

- 로그 파일을 `tmp_path`에 만들고 포맷을 검증합니다.
- 여러 환경변수 조합을 parametrize와 `monkeypatch`로 한꺼번에 검증합니다.
- 만료일, 과금일, 배치 스케줄링 로직을 고정된 시간으로 테스트합니다.
- CI 환경에서 파일 권한 차이를 줄이기 위해 임시 디렉터리를 표준화합니다.
- 시스템 자원 테스트를 순수 함수 테스트와 분리해 디버깅을 단순화합니다.

## 현업 개발자는 이렇게 생각합니다

파일, 환경변수, 시간은 “코드 바깥의 세계”입니다. 테스트가 이 세계를 통제하지 못하면 테스트는 코드 검증이 아니라 환경 관찰에 가까워집니다.

특히 `tmp_path`는 pytest에서 가장 실용적인 내장 fixture 중 하나입니다. 파일 I/O 테스트를 시작할 때 가장 먼저 떠올릴 기본 도구라고 생각해도 좋습니다.

## 체크리스트

- [ ] `tmp_path`로 임시 파일을 만들고 테스트했다
- [ ] `monkeypatch.setenv/delenv`로 환경변수를 격리했다
- [ ] `patch` 또는 `freezegun`으로 시간을 고정했다
- [ ] 누락 파일 같은 오류 경로를 테스트했다
- [ ] 테스트 사이에 상태 오염이 없는지 확인했다

## 연습 문제

1. `tmp_path`에 YAML 설정 파일을 만들고 이를 파싱하는 테스트를 작성해 보세요.
2. `LOG_FORMAT` 환경변수에 따라 JSON 또는 텍스트 로그를 출력하는 함수를 테스트해 보세요.
3. `freeze_time`과 parametrize를 조합해 매달 1일, 15일, 말일 로직을 검증해 보세요.

## 정리 및 다음 글 안내

`tmp_path`, `monkeypatch`, `freezegun`을 익히면 시스템 리소스에 의존하는 코드도 충분히 안정적으로 테스트할 수 있습니다. 다음 글에서는 이제 테스트가 실제로 어디까지 코드를 실행하는지, coverage를 통해 객관적으로 확인해 보겠습니다.

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
