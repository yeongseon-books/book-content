---
series: type-hints-python-101
episode: 10
title: 타입 힌트를 잘 쓰는 기준
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
  - Type Hints
  - 베스트 프랙티스
  - 점진적 타이핑
  - 코드 품질
  - 팀 가이드라인
seo_description: 점진적 타이핑 전략, 팀 가이드라인, 실무 패턴으로 타입 힌트를 효과적으로 도입하는 기준을 정리합니다.
last_reviewed: '2026-05-11'
---

# 타입 힌트를 잘 쓰는 기준

> Type Hints in Python 101 시리즈 (10/10)


## 이 글에서 다룰 문제

타입 힌트는 도구입니다. 도구는 올바르게 사용해야 효과가 있습니다. 무조건 strict 모드를 적용하면 기존 코드베이스와 마찰이 생기고, 느슨하게 사용하면 타입 시스템의 이점을 누리지 못합니다. 프로젝트의 규모, 팀의 숙련도, 코드의 수명을 고려한 균형 잡힌 전략이 필요합니다.

> 타입 힌트 = 코드의 계약서. 계약 범위는 상황에 따라 조절합니다.

점진적 타이핑은 Python 타입 시스템의 핵심 철학입니다.

## 전체 흐름
> 타입 힌트 적용은 "공개 API → 핵심 로직 → 내부 구현" 순으로 바깥에서 안쪽으로 진행합니다.

```text
공개 API (함수 시그니처)     ← 1순위
     │
핵심 비즈니스 로직           ← 2순위
     │
내부 유틸리티 / 헬퍼         ← 3순위
     │
테스트 코드                  ← 선택
     │
스크립트 / 일회성 코드       ← 불필요
```

## Before / After

**Before — 기준 없는 타입 힌트:**

```python
from typing import Any


def process(data: Any) -> Any:
    result: Any = data.get("value")
    items: list[Any] = result.split(",")
    count: int = len(items)
    return count
```

**After — 목적 있는 타입 힌트:**

```python
def process(data: dict[str, str]) -> int:
    result = data.get("value", "")
    items = result.split(",")
    return len(items)
```

함수 시그니처에 정확한 타입을 쓰고, 지역 변수는 추론에 맡깁니다.

## 단계별로 따라하기

### 1단계: 함수 시그니처부터 시작

```python
# 1순위: 공개 함수의 매개변수와 반환 타입
def calculate_total(prices: list[int], tax_rate: float) -> int:
    subtotal = sum(prices)  # 지역 변수는 추론에 맡깁니다
    tax = int(subtotal * tax_rate)
    return subtotal + tax


# 클래스의 공개 메서드도 동일합니다
class OrderService:
    def create_order(self, items: list[str], customer_id: int) -> dict[str, object]:
        ...

    def _validate_items(self, items):
        # 비공개 메서드는 후순위입니다
        ...
```

함수 시그니처의 타입 힌트가 가장 높은 투자 대비 효과를 보입니다. 호출자가 어떤 값을 넣고 어떤 값을 받는지 명확해집니다.

### 2단계: 반환 타입을 항상 명시

```python
# 좋은 예: 반환 타입이 명확합니다
def find_user(user_id: int) -> User | None:
    ...


# 나쁜 예: 반환 타입이 없으면 호출부에서 추측해야 합니다
def find_user(user_id: int):
    ...
```

반환 타입은 매개변수 타입보다 더 중요합니다. 매개변수는 호출자가 직접 넣으므로 알고 있지만, 반환값은 함수를 읽어야 알 수 있기 때문입니다.

### 3단계: Any 사용을 최소화

```python
from typing import Any

# 나쁜 예: Any가 전파되면 타입 검사 효과가 사라집니다
def get_config() -> Any:
    ...

value = get_config()  # value: Any → 이후 모든 코드가 Any


# 좋은 예: 구체적인 타입을 사용합니다
def get_config() -> dict[str, str | int | bool]:
    ...
```

Any는 "타입 검사를 포기한다"는 선언입니다. 불가피한 경우에만 사용하고, 가능하면 `object`나 구체 타입으로 대체합니다.

### 4단계: 타입 좁히기 패턴 활용

```python
def process_value(value: str | int | None) -> str:
    if value is None:
        return "default"

    if isinstance(value, int):
        return str(value)

    # 여기서 value는 str로 좁혀집니다
    return value.upper()
```

Union 타입을 받으면 if 문으로 타입을 좁혀야 합니다. mypy와 pyright는 이 패턴을 인식하여 각 분기에서 정확한 타입을 추론합니다.

### 5단계: 팀 가이드라인 수립

```toml
# pyproject.toml — 팀 표준 설정
[tool.mypy]
python_version = "3.11"

# 새 코드 기준
disallow_untyped_defs = true
warn_return_any = true
warn_unused_ignores = true

# 레거시 코드 허용
[[tool.mypy.overrides]]
module = "legacy.*"
ignore_errors = true

# 테스트 코드 완화
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

팀 가이드라인의 핵심 원칙입니다.

- 새 코드에는 타입 힌트를 필수로 적용합니다
- 기존 코드는 수정할 때 타입 힌트를 추가합니다
- 테스트 코드는 느슨한 규칙을 적용합니다
- `type: ignore`는 PR 리뷰에서 사유를 설명합니다

## 이 코드에서 주목할 점

- 함수 시그니처(매개변수 + 반환 타입)에 우선 적용합니다
- 지역 변수는 타입 추론에 맡기고 명시하지 않습니다
- Any는 타입 검사를 무력화하므로 최소한으로 사용합니다
- 팀 설정은 pyproject.toml에서 모듈별로 차등 적용합니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 지역 변수에 모두 타입 명시 | 코드가 장황해지고 가독성이 떨어집니다 | 추론 가능한 변수는 생략합니다 |
| Any로 빠르게 해결 | 타입 검사 효과가 전파적으로 사라집니다 | 구체 타입이나 object를 사용합니다 |
| 타입 힌트 없이 대규모 리팩터링 | 호출부 영향을 파악할 수 없습니다 | 리팩터링 전에 시그니처부터 타입을 추가합니다 |
| 일괄 strict 적용 | 수백 개 오류에 팀이 좌절합니다 | 모듈 단위로 점진 도입합니다 |
| 타입 힌트를 문서 대신 사용 | 타입만으로 의도를 전달할 수 없습니다 | 타입 힌트와 docstring을 병행합니다 |

## 실무에서는 이렇게 쓰입니다

- 새 프로젝트에서 첫날부터 mypy strict 모드를 CI에 설정
- 레거시 프로젝트에서 "boy scout rule"로 수정하는 파일마다 타입 추가
- API 경계(FastAPI 엔드포인트, gRPC 서비스)에 Pydantic 모델로 계약 명시
- 라이브러리 공개 API에는 py.typed 마커와 함께 완전한 타입 힌트 제공
- 코드 리뷰에서 타입 힌트 누락을 체크리스트 항목으로 관리

## 체크리스트

- [ ] 공개 함수의 매개변수와 반환 타입에 힌트를 추가했는가
- [ ] Any 사용을 최소화했는가
- [ ] 지역 변수의 불필요한 타입 명시를 제거했는가
- [ ] 팀 mypy/pyright 설정을 pyproject.toml에 정의했는가
- [ ] 점진적 도입 계획을 수립했는가

## 정리 및 다음 단계

타입 힌트는 코드의 안전성과 가독성을 높이는 강력한 도구입니다. 함수 시그니처에 우선 적용하고, Any를 최소화하며, 팀 설정으로 일관성을 유지하는 것이 핵심입니다. 점진적 타이핑 전략으로 기존 프로젝트에도 무리 없이 도입할 수 있습니다.

이 시리즈에서 기본 타입부터 Generic, mypy, Pydantic까지 Python 타입 힌트의 전체 그림을 살펴보았습니다. 타입 힌트를 도입하면 코드 리뷰가 빨라지고, 리팩터링이 안전해지며, 팀의 생산성이 향상됩니다.

<!-- toc:begin -->
- [Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- [기본 타입과 collection 타입](./02-basic-and-collection-types.md)
- [Optional과 Union](./03-optional-and-union.md)
- [함수 타입 힌트](./04-function-type-hints.md)
- [TypedDict와 dataclass](./05-typeddict-and-dataclass.md)
- [Protocol과 structural typing](./06-protocol-and-structural-typing.md)
- [Generic 이해하기](./07-generic.md)
- [mypy와 pyright 사용하기](./08-mypy-and-pyright.md)
- [Pydantic과 타입 힌트](./09-pydantic-and-type-hints.md)
- **타입 힌트를 잘 쓰는 기준 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — typing](https://docs.python.org/3/library/typing.html)
- [mypy 문서 — Using mypy with an existing codebase](https://mypy.readthedocs.io/en/stable/existing_code.html)
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)
- [Google Python Style Guide — Type Annotations](https://google.github.io/styleguide/pyguide.html#3192-line-length)

Tags: Python, Type Hints, 베스트 프랙티스, 점진적 타이핑, 코드 품질, 팀 가이드라인
