---
title: "Object-Oriented Programming 101 (10/10): 객체지향을 언제 피해야 할까?"
series: oop-101
episode: 10
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
  - Python
  - OOP
  - 함수형 프로그래밍
  - dataclass
  - 설계 판단
last_reviewed: '2026-05-17'
seo_description: 객체지향이 과한 상황과 함수, dataclass, 함수형 접근이 더 나은 경우를 설명합니다.
---

# Object-Oriented Programming 101 (10/10): 객체지향을 언제 피해야 할까?

가장 어려운 객체지향 결정은 종종 "어떤 클래스를 더 만들까?"가 아니라 "이걸 정말 클래스여야 하나?"입니다. 이 글은 OOP 101 시리즈의 마지막 글입니다.

Python이 함수, 모듈, `dataclass`, `NamedTuple`, `TypedDict`, 콜러블을 함께 주는 이유가 있습니다. 이번 글에서는 클래스가 과하게 많은 리포트 미니 앱을 단계적으로 단순화하고, 다시 클래스를 도입해야 하는 임계점까지 분명하게 잡아 보겠습니다.


![Object-Oriented Programming 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/10/10-01-concept-overview.ko.png)
*Object-Oriented Programming 101 10장 흐름 개요*

## 먼저 던지는 질문

- 어떤 신호가 보이면 클래스 기반 설계가 대부분 의식적인 장식에 가깝다고 판단할 수 있을까요?
- 어떤 종류의 클래스가 함수, `dataclass`, `NamedTuple`, `TypedDict`로 더 잘 바뀔까요?
- 전략 클래스 전체 대신 콜백 하나면 충분한 순간은 언제일까요?

## 핵심 개념 잡기

실무적인 질문은 단순합니다. 이 동작이 정말 상태와 수명주기 조정을 필요로 하는가, 아니면 대부분 데이터 변환 파이프라인인가? 후자라면 클래스는 종종 추가 무게일 뿐입니다.

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 다중 패러다임 | Python은 절차, 객체지향, 함수형 스타일을 함께 지원합니다 |
| 빈혈 클래스 | 데이터 보관이나 단일 메서드 래핑에 가까운 얇은 클래스입니다 |
| `dataclass` | 데이터 중심 구조를 간결하게 표현하는 기능입니다 |
| 고차 함수 | 다른 함수를 인자로 받거나 반환하는 함수입니다 |
| 재도입 임계점 | 상태, 검증, 수명주기 조정이 강해져 다시 클래스가 유리해지는 시점입니다 |

## 전후 비교

이번 글의 핵심은 "클래스는 나쁘다"가 아니라 "설계 의도를 지키는 가장 가벼운 도구를 먼저 쓰자"입니다.

```python
# before: 상태 없는 헬퍼와 단순 데이터도 모두 클래스로 감쌉니다
class TitleCleaner:
    def clean(self, title: str) -> str:
        return title.strip().title()

class ScoreFilter:
    def keep(self, score: int, minimum: int) -> bool:
        return score >= minimum
```

```python
# after: 함수와 데이터 구조가 같은 워크플로를 더 직접적으로 표현합니다
def clean_title(title: str) -> str:
    return title.strip().title()

def keep_score(score: int, minimum: int) -> bool:
    return score >= minimum
```

## 하나의 워크플로로 보는 클래스 줄이기

### 출발점: 너무 많은 작은 클래스

주간 캠페인 리포트를 만드는 팀이 모든 단계를 각각 클래스로 감쌌다고 가정해 보겠습니다.

```python
class TitleCleaner:
    def clean(self, title: str) -> str:
        return title.strip().title()

class ScoreFilter:
    def keep(self, score: int, minimum: int) -> bool:
        return score >= minimum

class CurrencyFormatter:
    def format(self, value: int) -> str:
        return f"${value:,.0f}"

class ReportRow:
    def __init__(self, title: str, score: int, spend: int) -> None:
        self.title = title
        self.score = score
        self.spend = spend

class ReportConfig:
    def __init__(self, minimum_score: int, currency: str) -> None:
        self.minimum_score = minimum_score
        self.currency = currency
```

각 클래스는 이해 가능하지만, 전체 설계는 문제에 비해 무겁습니다.

### 1단계: 상태 없는 헬퍼 클래스를 함수로 바꿉니다

인스턴스 상태도 없고 수명주기도 없는 코드는 모듈 함수가 더 분명한 경우가 많습니다.

```python
def clean_title(title: str) -> str:
    return title.strip().title()

def keep_score(score: int, minimum: int) -> bool:
    return score >= minimum

def format_currency(value: int) -> str:
    return f"${value:,.0f}"
```

#### 실행

```python
print(clean_title("  spring launch "))
print(keep_score(82, 80))
print(format_currency(12500))
```

예상 출력:

```text
Spring Launch
True
$12,500
```

#### 점검

바뀐 것: 인스턴스 생성이 사라졌습니다. 그대로인 것: 각 변환은 여전히 이름이 분명하고 역할이 하나입니다.

### 2단계: 데이터 보관용 boilerplate를 `dataclass`와 `TypedDict`로 바꿉니다

원래 `ReportRow`, `ReportConfig`는 대부분 필드 저장만 하고 있었습니다. 이때는 가벼운 데이터 구조가 더 적합합니다.

```python
from dataclasses import dataclass
from typing import TypedDict

@dataclass(frozen=True)
class ReportRow:
    title: str
    score: int
    spend: int

class ReportConfig(TypedDict):
    minimum_score: int
    channel: str

config: ReportConfig = {"minimum_score": 80, "channel": "email"}
row = ReportRow(title="Spring Launch", score=82, spend=12500)

print(row)
print(config["channel"])
```

예상 출력:

```text
ReportRow(title='Spring Launch', score=82, spend=12500)
email
```

#### 점검

바뀐 것: 생성자와 표현용 boilerplate가 사라졌습니다. 그대로인 것: 워크플로는 여전히 이름 있는 행 타입과 명시적 설정 키를 가집니다.

#### 실패 경로

`config["chnanel"]`처럼 dict 키를 잘못 쓰면 런타임에 늦게 실패합니다. 얕고 단순한 설정에서는 감수할 수 있지만, 나중에 더 풍부한 객체가 필요해지는 첫 신호이기도 합니다.

### 3단계: 사소한 전략 클래스를 콜러블로 바꿉니다

많은 전략 클래스는 사실상 이름 붙은 포매팅 함수 하나에 가깝습니다.

```python
from collections.abc import Callable

def format_currency(value: int) -> str:
    return f"${value:,.0f}"

def format_points(value: int) -> str:
    return f"{value} pts"

def render_value(value: int, formatter: Callable[[int], str]) -> str:
    return formatter(value)

print(render_value(12500, format_currency))
print(render_value(82, format_points))
```

예상 출력:

```text
$12,500
82 pts
```

#### 점검

바뀐 것: 전략 추상이 호출자가 실제로 필요한 것, 즉 콜러블 하나로 줄었습니다. 그대로인 것: 포매팅 교체는 여전히 자연스럽습니다.

#### 실패 경로

각 포매터가 나중에 공통 설정, 캐시, 보조 메서드를 필요로 하기 시작하면 콜백만으로는 관련 동작이 흩어집니다. 그 순간이 클래스를 다시 고려할 한 기준입니다.

### 4단계: 리포트를 함수 파이프라인으로 조립합니다

이제 미니 앱은 작은 껍데기 클래스 모음 대신 읽기 쉬운 파이프라인이 될 수 있습니다.

```python
from dataclasses import dataclass
from collections.abc import Callable
from typing import TypedDict

@dataclass(frozen=True)
class ReportRow:
    title: str
    score: int
    spend: int

class ReportConfig(TypedDict):
    minimum_score: int
    channel: str

def clean_title(title: str) -> str:
    return title.strip().title()

def format_currency(value: int) -> str:
    return f"${value:,.0f}"

def normalize_rows(rows: list[dict]) -> list[ReportRow]:
    return [
        ReportRow(
            title=clean_title(row["title"]),
            score=row["score"],
            spend=row["spend"],
        )
        for row in rows
    ]

def filter_rows(rows: list[ReportRow], minimum_score: int) -> list[ReportRow]:
    return [row for row in rows if row.score >= minimum_score]

def sort_rows(rows: list[ReportRow]) -> list[ReportRow]:
    return sorted(rows, key=lambda row: row.score, reverse=True)

def render_report(rows: list[ReportRow], money: Callable[[int], str]) -> list[str]:
    return [f"{row.title} | score={row.score} | spend={money(row.spend)}" for row in rows]

def build_report(raw_rows: list[dict], config: ReportConfig, money: Callable[[int], str]) -> list[str]:
    rows = normalize_rows(raw_rows)
    rows = filter_rows(rows, config["minimum_score"])
    rows = sort_rows(rows)
    return render_report(rows, money)

raw_rows = [
    {"title": "  spring launch ", "score": 82, "spend": 12500},
    {"title": "retargeting", "score": 76, "spend": 4000},
    {"title": "summer promo", "score": 91, "spend": 18000},
]
config: ReportConfig = {"minimum_score": 80, "channel": "email"}

for line in build_report(raw_rows, config, format_currency):
    print(line)
```

#### 실행

```bash
python report_pipeline.py
```

예상 출력:

```text
Summer Promo | score=91 | spend=$18,000
Spring Launch | score=82 | spend=$12,500
```

#### 점검

다음 세 가지를 확인합니다.

1. 정규화, 필터링, 정렬, 렌더링이 각각 독립 함수로 테스트되기 쉬운가
2. 데이터 보관 구조가 가볍지만 충분히 명시적인가
3. 리포트 파이프라인이 인스턴스 조정 노이즈 없이 위에서 아래로 읽히는가

#### 실패 경로: 함수만으로 두었더니 느슨해지는 순간

함수 파이프라인은 규칙과 공유 상태가 함께 움직이기 시작할 때부터 흔들립니다. 예를 들면 다음과 같습니다.

```python
config = {"minimum_score": 80, "chnanel": "email"}  # dict 키 오타가 숨어 있습니다
```

또는 각 포매터가 통화 기호 설정, 로케일 반올림 규칙, 환율 캐시 조회를 함께 필요로 한다고 해 보겠습니다. 그 시점에는 맨몸의 콜러블이 더 이상 가장 분명한 추상이 아닐 수 있습니다.

## 다시 클래스를 도입할지 판단하는 기준

다음 항목 중 두 개 이상이 동시에 보이면 클래스 쪽으로 되돌아갈 이유가 생깁니다.

| 신호 | 왜 클래스가 도움이 되기 시작하는가 |
|------|----------------------------------|
| 같은 필드 묶음이 여러 함수 사이를 반복해서 같이 이동 | 더 풍부한 도메인 객체가 불변식과 동작을 한곳에 묶을 수 있습니다 |
| 검증 규칙과 상태 전이가 함께 반복 | 메서드와 캡슐화된 상태가 더 추론하기 쉬워집니다 |
| 포매터나 전략이 설정, 캐시 같은 지속 상태를 가짐 | 매번 인자를 늘리는 것보다 상태 객체가 분명해집니다 |
| 파이프라인이 재시도, 훅, 공유 협력 객체를 요구 | 조정자 객체가 횡단 관심사를 맡기 쉬워집니다 |

목표는 "순수 함수형"을 지키는 것이 아닙니다. 더 무거운 구조가 자기 값을 벌어들일 때까지 미루는 것입니다.

## 이 워크플로에서 주목할 점

- 상태 없는 변환 로직은 메서드 하나짜리 클래스보다 함수가 더 읽기 쉬운 경우가 많습니다.
- `dataclass`와 `TypedDict`는 이름 있는 구조를 유지하면서도 객체 ceremony를 줄여 줍니다.
- 단순한 교체 가능 동작은 콜러블 하나로 충분한 경우가 많습니다.
- 함수 파이프라인은 상태, 불변식, 수명주기 조정이 반복되기 전까지 강력합니다.

## 자주 하는 실수 5가지

| 실수 | 왜 아픈가 | 더 나은 선택 |
|------|----------|--------------|
| 모든 헬퍼를 클래스화 | 단순한 파이프라인이 객체 노이즈에 가려집니다 | 모듈 함수로 시작합니다 |
| 평범한 데이터에 수제 클래스를 사용 | boilerplate가 가치보다 빨리 늘어납니다 | `dataclass`, `NamedTuple`, `TypedDict`를 봅니다 |
| 함수 하나 감싼 전략 클래스를 유지 | 상태 없는 간접 계층만 남습니다 | 콜러블을 전달합니다 |
| 함수 중심 설계를 이념처럼 밀어붙임 | 상태와 검증이 흩어집니다 | 불변식이 반복되면 클래스를 재도입합니다 |
| dict 기반 설정을 너무 오래 방치 | 오타와 기본값 누락이 늦게 드러납니다 | 설정 복잡도가 커지면 더 풍부한 객체로 올립니다 |

## 실무에서 이렇게 쓰입니다

- CLI 유틸리티는 함수 중심 모듈이 가장 잘 맞는 경우가 많습니다.
- 데이터 정리와 변환 코드는 파이프라인 형태가 자연스럽습니다.
- `dataclass`는 내부 DTO나 불변 페이로드에 특히 적합합니다.
- 반대로 상태가 있는 API 클라이언트나 캐시 서비스는 클래스를 다시 정당화합니다.

## 현업 개발자는 이렇게 생각합니다

현업 개발자는 클래스가 나빠서 클래스를 피하지 않습니다. 상태와 계층 구조의 무게가 실제로는 데이터 변환 문제에 불필요하게 올라타고 있기 때문에 피합니다. 좋은 질문은 "가장 싸면서도 워크플로를 보호하는 추상이 무엇인가?"입니다.

그래서 많은 Python 코드베이스는 함수로 시작하고, 상태·불변식·조정 책임이 쌓이는 지점만 클래스로 올립니다. 절제가 설계 능력의 일부입니다.

## 체크리스트

- [ ] 상태 없는 헬퍼 함수를 얇게 감싼 클래스를 식별할 수 있다
- [ ] boilerplate 데이터 보관 클래스를 `dataclass`나 `TypedDict`로 바꿀 수 있다
- [ ] 사소한 전략 클래스 대신 콜러블을 사용할 수 있다
- [ ] 변환 중심 코드를 읽기 쉬운 함수 파이프라인으로 만들 수 있다
- [ ] 상태와 불변식이 커질 때 클래스를 다시 도입해야 하는 이유를 설명할 수 있다

## 정리 및 다음 글 안내

객체지향을 피해야 하는 순간은 클래스가 보호보다 의식을 더 많이 늘릴 때입니다. 이번 리포트 워크플로에서는 상태 없는 헬퍼를 함수로, 데이터 보관용 클래스를 가벼운 구조로, 사소한 전략을 콜러블로 바꾸면서 전체를 직접적인 파이프라인으로 만들었습니다. 동시에 상태와 불변식이 함께 움직이기 시작하면 다시 클래스로 올라가야 하는 기준도 얻었습니다.

## 객체지향을 피해야 하는 신호를 구조로 정리

객체지향을 피해야 하는 상황은 반객체지향이 아니라, 문제 형태와 해법이 맞지 않는 경우입니다.

```text
입력 변환 파이프라인
[read_csv] -> [normalize_row] -> [filter_invalid] -> [aggregate] -> [write_report]

도메인 상태 모델
[Account]
  + open()
  + suspend()
  + close()
```

첫 번째 형태는 함수 조합이 자연스럽고, 두 번째 형태는 상태 모델 객체가 자연스럽습니다.

## 적용 전후: 과도한 클래스화에서 함수 중심으로

```python
# before
class CsvReader:
    def run(self, path: str) -> list[dict]:
        ...

class RowNormalizer:
    def run(self, rows: list[dict]) -> list[dict]:
        ...

class InvalidFilter:
    def run(self, rows: list[dict]) -> list[dict]:
        ...
```

```python
# after
from collections.abc import Iterable


def read_csv(path: str) -> list[dict]:
    ...


def normalize_row(row: dict) -> dict:
    ...


def filter_invalid(rows: Iterable[dict]) -> list[dict]:
    return [r for r in rows if r.get('price', 0) > 0]


def pipeline(path: str) -> list[dict]:
    rows = read_csv(path)
    normalized = [normalize_row(r) for r in rows]
    return filter_invalid(normalized)
```

## 원칙 위반 관점

| 위반 | 증상 | 수정 |
|---|---|---|
| 클래스가 데이터 없이 정적 메서드만 가짐 | 사실상 네임스페이스 포장 | 함수 모듈로 단순화 |
| 생성자 의존성만 8개 이상 | 조립 비용 과다 | use case 분리 또는 함수 파이프라인 |
| 작은 변환 로직도 객체 1개씩 생성 | 인지 부하 증가 | 순수 함수로 전환 |

## 비교표: 함수형 접근과 객체지향 접근

| 질문 | 함수형 접근 유리 | 객체지향 접근 유리 |
|---|---|---|
| 상태 전이가 핵심인가 | 아니오 | 예 |
| 입력→출력 변환이 반복되는가 | 예 | 아니오 |
| 규칙이 객체 생명주기에 묶이는가 | 아니오 | 예 |
| 테스트를 데이터 중심으로 작성하는가 | 예 | 상황별 |

## 혼합 전략

실무에서는 둘 중 하나만 고집하지 않습니다. 도메인 상태는 객체로 모델링하고, 데이터 변환은 순수 함수로 처리하는 혼합 전략이 유지보수 비용을 가장 낮추는 경우가 많습니다.

## 실전 시나리오: 요구사항 변경을 견디는 구조로 바꾸기

현업에서는 기능 추가보다 규칙 변경이 더 자주 발생합니다. 따라서 클래스 구조를 평가할 때는 "지금 동작하는가"보다 "다음 변경을 어디까지 건드려야 하는가"를 기준으로 보는 편이 안전합니다.

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass
class LineItem:
    name: str
    quantity: int
    unit_price: int

    def subtotal(self) -> int:
        return self.quantity * self.unit_price


class DiscountPolicy(Protocol):
    def apply(self, amount: int) -> int:
        ...


class NoDiscount:
    def apply(self, amount: int) -> int:
        return amount


class PercentDiscount:
    def __init__(self, percent: int) -> None:
        if not 0 <= percent <= 100:
            raise ValueError('percent must be 0..100')
        self.percent = percent

    def apply(self, amount: int) -> int:
        return int(amount * (100 - self.percent) / 100)


class Invoice:
    def __init__(self, items: list[LineItem], policy: DiscountPolicy) -> None:
        self.items = items
        self.policy = policy

    def total(self) -> int:
        base = sum(i.subtotal() for i in self.items)
        return self.policy.apply(base)
```

이 코드는 할인 규칙이 바뀌어도 `Invoice.total()`을 수정할 필요가 없습니다. 확장은 구현 클래스 추가로 닫히고, 핵심 흐름은 안정적으로 유지됩니다.

## UML 스타일로 보는 협력 관계

```text
[Invoice]
  - items: list[LineItem]
  - policy: DiscountPolicy
  + total()

[LineItem]
  + subtotal()

[DiscountPolicy] <<interface>>
  + apply(amount)
      ^
      +-- [NoDiscount]
      +-- [PercentDiscount]
```

협력 구조를 이렇게 텍스트로 적어 두면 코드 리뷰에서 "어디가 정책 축이고 어디가 도메인 축인가"를 빠르게 맞출 수 있습니다.

## 안티패턴과 교정 절차

| 안티패턴 | 발견 신호 | 교정 순서 |
|---|---|---|
| 거대 클래스(God Object) | 메서드가 20개 이상, 변경 이력이 분산됨 | 책임 축 분해 → 협력 인터페이스 도출 |
| 데이터만 가진 빈 클래스 | 메서드 없이 getter/setter만 존재 | 규칙 메서드 이동 또는 dataclass로 단순화 |
| 상속 트리 우회 분기 | 하위 클래스 타입 체크 분기 존재 | 다형성 계약 재정의 |
| 인프라 타입 누수 | 도메인 계층이 SDK 응답 객체 의존 | DTO 변환 계층 추가 |

## 전후 비교: 테스트 유지비

| 항목 | 리팩터링 전 | 리팩터링 후 |
|---|---|---|
| 테스트 준비 | 전역 상태 초기화 필요 | 객체 단위 상태 생성 |
| 실패 원인 추적 | 함수 체인 전체 역추적 | 클래스 메서드 단위 추적 |
| 회귀 범위 | 넓고 불명확 | 좁고 예측 가능 |

## 팀 적용 체크리스트

- 도메인 용어와 클래스 이름이 일치하는지 확인합니다.
- 인스턴스 생성 시점에 불변식이 완성되는지 확인합니다.
- 정책 변경이 기존 코드 수정이 아닌 구현 추가로 가능한지 점검합니다.
- 코드 리뷰에서 UML 텍스트 10줄로 협력 구조를 먼저 합의합니다.
- 테스트 이름이 메서드명보다 비즈니스 규칙을 설명하는지 확인합니다.

## 미니 케이스 스터디: 규칙 추가 한 번으로 검증하기

아래 예시는 정책 확장을 기존 코드 수정 없이 추가하는 최소 단위입니다.

```python
class WeekendPolicy:
    def apply(self, amount: int, is_weekend: bool) -> int:
        if is_weekend:
            return int(amount * 0.95)
        return amount


def estimate(amount: int, is_weekend: bool) -> int:
    policy = WeekendPolicy()
    return policy.apply(amount, is_weekend)
```

핵심은 새로운 정책이 호출 경로를 깨지 않고 들어온다는 사실입니다. 변경 이력이 정책 클래스에만 남도록 경계를 유지하면 회귀 위험이 줄어듭니다.

| 확인 질문 | Pass 기준 |
|---|---|
| 새 정책 추가 시 기존 함수 수정이 필요한가 | 아니오 |
| 예외 정책이 기존 계약과 같은가 | 예 |
| 테스트가 정책별로 분리되어 있는가 | 예 |

## 검증 노트: 객체 설계 품질을 점검하는 질문

아래 질문은 구현 이후 리뷰에서 반복적으로 사용하는 기준입니다.

- 이 메서드가 실패할 때 예외 타입과 메시지가 호출자 계약과 일치하는가.
- 같은 규칙이 다른 클래스나 함수에 중복되어 있지 않은가.
- 상태 변경이 메서드 한 경로로만 이루어지는가.
- 외부 의존성 없이 단위 테스트가 가능한가.

```python
def review_signal(duplicate_rules: int, mutable_paths: int) -> str:
    if duplicate_rules > 0:
        return '중복 규칙 제거 필요'
    if mutable_paths > 1:
        return '상태 변경 경로 통합 필요'
    return '구조 안정'
```

이런 체크를 글 단위 예제에도 적용하면, 객체지향을 문법이 아니라 유지보수 전략으로 이해하는 데 도움이 됩니다.

## 처음 질문으로 돌아가기

- **어떤 신호가 보이면 클래스 기반 설계가 대부분 의식적인 장식에 가깝다고 판단할 수 있을까요?**
  - `TitleCleaner`, `ScoreFilter`, `CurrencyFormatter`처럼 인스턴스 상태 없이 메서드 하나만 감싼 클래스가 계속 늘어나고, 생성자 의존성만 많아진다면 이 글이 말하는 과한 객체지향 신호에 가깝습니다. 여기에 리포트 앱이 사실상 `read_csv → normalize_row → filter_invalid → aggregate` 같은 변환 파이프라인으로 읽히기 시작하면, 클래스보다 함수가 더 직접적인 표현이 됩니다.
- **어떤 종류의 클래스가 함수, `dataclass`, `NamedTuple`, `TypedDict`로 더 잘 바뀔까요?**
  - `ReportRow`처럼 필드 저장이 주된 역할인 클래스는 `@dataclass(frozen=True)`로 줄이는 편이 낫고, `ReportConfig`처럼 얕은 설정 묶음은 `TypedDict`가 더 가볍습니다. 반대로 제목 정리나 점수 필터링처럼 상태 없는 헬퍼는 함수로 바꾸는 것이 자연스럽고, 본문은 이렇게 클래스 종류별로 더 적합한 대체 수단을 구체적으로 나눴습니다.
- **전략 클래스 전체 대신 콜백 하나면 충분한 순간은 언제일까요?**
  - `render_value(value, formatter)`와 `build_report(..., money)` 예제처럼 호출자가 정말 필요한 것이 `int -> str` 변환 하나뿐이라면 `format_currency`나 `format_points` 같은 콜러블만 넘겨도 충분합니다. 다만 글 후반에서 짚었듯이 포매터가 로케일, 캐시, 공통 설정을 함께 들기 시작하면 콜백만으로는 흩어지므로, 그때가 다시 클래스를 도입할 임계점입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): 클래스와 인스턴스](./02-classes-and-instances.md)
- [Object-Oriented Programming 101 (3/10): 캡슐화](./03-encapsulation.md)
- [Object-Oriented Programming 101 (4/10): 상속](./04-inheritance.md)
- [Object-Oriented Programming 101 (5/10): 다형성](./05-polymorphism.md)
- [Object-Oriented Programming 101 (6/10): 추상화](./06-abstraction.md)
- [Object-Oriented Programming 101 (7/10): 합성과 상속](./07-composition-vs-inheritance.md)
- [Object-Oriented Programming 101 (8/10): SOLID 원칙 기초](./08-solid-principles.md)
- [Object-Oriented Programming 101 (9/10): 객체지향 설계 예제](./09-oop-design-example.md)
- **객체지향을 언제 피해야 할까? (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Python 공식 문서 — typing.NamedTuple / TypedDict / Callable](https://docs.python.org/3/library/typing.html)
- [Python 공식 문서 — functools](https://docs.python.org/3/library/functools.html)
- [Stop Writing Classes — PyCon Talk by Jack Diederich](https://www.youtube.com/watch?v=o9pEzgHorH0)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)
Tags: Python, OOP, 함수형 프로그래밍, dataclass, 설계 판단
