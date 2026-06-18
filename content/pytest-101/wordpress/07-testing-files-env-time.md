---
title: "바이브코딩을 위한 pytest 기초 (7/10): 파일, 환경변수, 시간 테스트"
series: pytest-101
episode: 7
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - pytest
  - Testing
  - Fixtures
  - Monkeypatch
---

# 바이브코딩을 위한 pytest 기초 (7/10): 파일, 환경변수, 시간 테스트

이 글은 "바이브코딩을 위한 pytest 기초" 시리즈의 7번째 글입니다.

---

바이브코딩에서 AI는 파일을 읽고 쓰는 코드, 환경변수로 동작을 바꾸는 코드, `datetime.now()`로 현재 시각을 쓰는 코드를 빠르게 만들어 줍니다. 그런데 이런 코드를 테스트하려면 세 가지 문제가 생깁니다.

첫째, 파일 테스트는 실제 디스크를 건드리면 테스트 간 간섭이 생깁니다. 한 테스트가 만든 파일이 다음 테스트에 남아 있으면 결과가 달라집니다. 둘째, 환경변수 테스트는 한 테스트에서 `os.environ`을 바꾸면 다른 테스트에도 영향이 갑니다. 셋째, 시간 테스트는 `datetime.now()`가 실행마다 달라지기 때문에 "만료 여부 확인" 같은 로직을 고정된 기준 없이 테스트할 수 없습니다.

pytest는 이 세 가지 문제를 각각 `tmp_path`, `monkeypatch`, `freezegun`으로 해결합니다. `tmp_path`는 테스트마다 새 임시 디렉터리를 만들고 테스트가 끝나면 자동으로 지웁니다. `monkeypatch`는 환경변수나 함수를 테스트 범위 안에서만 바꾸고 테스트가 끝나면 원래대로 돌려놓습니다. `freezegun`은 `datetime.now()`를 원하는 시각으로 고정합니다.

AI가 만든 코드에서 파일 경로를 하드코딩하거나, 환경변수를 직접 설정하거나, 현재 시각에 의존하는 로직이 있다면 이 세 도구로 격리된 테스트를 작성할 수 있습니다.

> **핵심 인사이트:** `tmp_path`는 테스트가 끝나면 자동으로 정리되고, `monkeypatch`는 테스트 범위를 벗어나면 원래 값으로 복원됩니다. 두 픽스처 모두 테스트 격리를 자동으로 처리해 줍니다. `freezegun`으로 시각을 고정하면 만료, 스케줄, 타임스탬프 로직을 결정론적으로 테스트할 수 있습니다.

## 이 글에서 다룰 문제

- `tmp_path` 픽스처는 파일 테스트에서 어떤 문제를 해결할까요?
- `monkeypatch.setenv`는 환경변수 테스트를 어떻게 격리할까요?
- `freezegun`은 시간 의존 로직을 어떻게 테스트 가능하게 만들까요?
- 파일 경로를 하드코딩한 코드는 어떻게 테스트할 수 있을까요?
- AI가 만든 시간 의존 코드에서 확인해야 할 것은 무엇인가요?

## 파일, 환경변수, 시간 테스트 핵심 패턴

```python
# tmp_path: 테스트마다 격리된 임시 디렉터리
def test_save_and_load(tmp_path):
    data_file = tmp_path / "data.txt"
    data_file.write_text("hello")
    assert data_file.read_text() == "hello"
    # 테스트 종료 후 tmp_path 전체가 자동 삭제됨

def test_write_file(tmp_path):
    output = tmp_path / "output.json"
    save_result({"score": 0.9}, output)   # 실제 코드 호출
    assert output.exists()
    assert json.loads(output.read_text())["score"] == 0.9
```

```python
# monkeypatch: 환경변수를 테스트 범위 안에서만 변경
def test_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    url = get_database_url()               # os.environ["DATABASE_URL"] 읽는 함수
    assert url == "sqlite:///:memory:"
    # 테스트 종료 후 DATABASE_URL 원래 값으로 자동 복원

def test_missing_env(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    with pytest.raises(EnvironmentError):
        connect_api()
```

```python
# freezegun: datetime.now()를 고정된 시각으로 대체
from freezegun import freeze_time

@freeze_time("2024-01-15 12:00:00")
def test_token_expiry():
    token = create_token(expires_in=3600)  # 1시간 후 만료
    assert not is_expired(token)           # 12:00:00 기준 아직 유효

@freeze_time("2024-01-15 13:01:00")
def test_token_expired():
    token = create_token(expires_in=3600)
    assert is_expired(token)               # 13:01:00 기준 만료됨
```

## 변경 전후 비교

**Before: 격리 없는 테스트**
```python
# 실제 파일에 쓰고 지우지 않음 → 테스트 간 간섭
def test_save():
    save_result(data, "/tmp/result.json")
    assert os.path.exists("/tmp/result.json")

# 전역 환경변수 변경 → 다른 테스트에 영향
def test_env():
    os.environ["API_KEY"] = "test-key"
    assert get_key() == "test-key"

# 실제 시각에 의존 → 내일 실행하면 다른 결과
def test_expiry():
    token = create_token(expires_in=1)
    time.sleep(2)
    assert is_expired(token)
```

**After: 격리된 테스트**
```python
# tmp_path: 자동 생성·삭제
def test_save(tmp_path):
    save_result(data, tmp_path / "result.json")
    assert (tmp_path / "result.json").exists()

# monkeypatch: 테스트 후 자동 복원
def test_env(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    assert get_key() == "test-key"

# freezegun: 결정론적 시각
@freeze_time("2024-01-15 12:00:00")
def test_expiry():
    token = create_token(expires_in=3600)
    assert not is_expired(token)
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 하드코딩된 경로 `/tmp/test.txt` | 테스트 간 파일 충돌 | `tmp_path` 픽스처 사용 |
| `os.environ` 직접 수정 | 다른 테스트에 환경변수 오염 | `monkeypatch.setenv` 사용 |
| `time.sleep()`으로 시간 테스트 | 테스트가 느려지고 불안정 | `freezegun`으로 시각 고정 |
| 실제 DB/API에 의존하는 파일 경로 | CI 환경에서 실패 | `tmp_path`로 격리 |
| `monkeypatch` 없이 환경변수 삭제 | teardown 없으면 복원 안 됨 | 항상 `monkeypatch.delenv` 사용 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"파일을 읽고 쓰는 함수 save_result()와 load_result()에
pytest 테스트를 작성해줘.
tmp_path 픽스처로 파일을 격리하고,
환경변수 OUTPUT_DIR도 monkeypatch로 테스트해줘"

# AI 결과물 검증 체크포인트:
# - tmp_path를 사용하는가? (하드코딩 경로 없는가?)
# - monkeypatch.setenv/delenv를 사용하는가?
# - freezegun이 필요한 시간 로직이 있는가?
# - 각 테스트가 서로 독립적으로 실행될 수 있는가?
# - 테스트 후 정리가 자동으로 되는가?
```

## 운영 체크리스트

- [ ] 파일을 읽고 쓰는 모든 테스트에 `tmp_path`를 사용한다
- [ ] 환경변수 변경은 `monkeypatch.setenv`로만 한다
- [ ] `datetime.now()`에 의존하는 로직은 `freezegun`으로 테스트한다
- [ ] 테스트가 순서와 관계없이 독립적으로 통과한다
- [ ] 테스트 실행 후 `/tmp`나 프로젝트 디렉터리에 잔여 파일이 없다

## 처음 질문으로 돌아가기

- **`tmp_path`가 필요한 이유는?** 테스트마다 고유한 임시 디렉터리를 제공해 파일 충돌을 막습니다. 테스트가 끝나면 pytest가 자동으로 삭제하므로 teardown 코드가 필요 없습니다.
- **`monkeypatch`와 직접 `os.environ` 수정의 차이는?** `monkeypatch.setenv`는 테스트가 끝나면 자동으로 원래 값으로 복원합니다. 직접 수정하면 teardown을 잊었을 때 다른 테스트가 오염됩니다.
- **`freezegun` 없이 시간 테스트를 하면 어떤 문제가 생기는가?** 테스트가 실행되는 시각에 따라 결과가 달라집니다. `time.sleep()`으로 대기하면 테스트가 느려지고 CI에서 타임아웃이 발생할 수 있습니다.

## 정리

바이브코딩에서 AI가 만들어 준 코드에서 파일 경로가 하드코딩되어 있거나, 환경변수를 직접 읽거나, `datetime.now()`를 사용한다면 `tmp_path`, `monkeypatch`, `freezegun`으로 격리된 테스트를 작성하세요. 세 픽스처 모두 테스트 후 자동으로 정리되어 테스트 간 간섭을 막습니다. 다음 글에서는 커버리지 측정을 다룹니다.

## 참고 자료

- [pytest — tmp_path fixture](https://docs.pytest.org/en/stable/how-to/tmp_path.html)
- [pytest — monkeypatch fixture](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- [freezegun — GitHub](https://github.com/spulec/freezegun)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 pytest 기초 (1/10): pytest란 무엇인가?
- 바이브코딩을 위한 pytest 기초 (2/10): 첫 번째 테스트 작성
- 바이브코딩을 위한 pytest 기초 (3/10): assert와 예외 테스트
- 바이브코딩을 위한 pytest 기초 (4/10): 픽스처
- 바이브코딩을 위한 pytest 기초 (5/10): 파라미터화 테스트
- 바이브코딩을 위한 pytest 기초 (6/10): Mock과 패치
- **바이브코딩을 위한 pytest 기초 (7/10): 파일, 환경변수, 시간 테스트 (현재 글)**
- 바이브코딩을 위한 pytest 기초 (8/10): 커버리지
- 바이브코딩을 위한 pytest 기초 (9/10): CI와 GitHub Actions
- 바이브코딩을 위한 pytest 기초 (10/10): 테스트하기 좋은 코드
<!-- toc:end -->

Tags: 바이브코딩, pytest, Testing, Fixtures, Monkeypatch
