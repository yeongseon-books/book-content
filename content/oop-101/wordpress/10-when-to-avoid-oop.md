---
title: "바이브코딩을 위한 객체지향 기초 (10/10): 객체지향을 언제 피해야 할까?"
series: oop-101
episode: 10
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - Python
  - OOP
  - 함수형 프로그래밍
  - dataclass
  - 바이브코딩
  - 설계 판단
last_reviewed: '2026-06-18'
seo_description: AI가 만든 코드에서 클래스가 너무 많을 때 단순화하는 방법을 설명합니다. 함수, dataclass, callable로 대체하는 기준을 바이브코딩 관점에서 정리합니다.
---

# 바이브코딩을 위한 객체지향 기초 (10/10): 객체지향을 언제 피해야 할까?

이 글은 **바이브코딩을 위한 객체지향 기초** 시리즈의 마지막 글입니다.

---

AI에게 CSV 파일을 읽어서 리포트를 만들어 달라고 했더니 `CsvReader`, `RowNormalizer`, `ScoreFilter`, `CurrencyFormatter`, `ReportConfig`, `ReportRow` — 6개 클래스가 생겼습니다. 각 클래스는 이해할 수 있는데, 전체를 보면 코드 읽는 것보다 클래스를 추적하는 게 더 힘듭니다. 왜 이렇게 만들었을까요?

AI가 OOP 패턴에 익숙해져서 모든 것을 클래스로 감싸는 경향이 있습니다. 하지만 Python은 함수, `dataclass`, `NamedTuple`, `TypedDict`, 콜러블을 모두 지원합니다. 상태도 없고 수명주기도 없는 로직을 굳이 클래스로 감싸면 코드가 더 복잡해집니다.

AI가 클래스 계층을 만들어줬는데 왜 이렇게 짰는지 이해하려면 OOP를 알아야 합니다. 그리고 이 시리즈의 마지막 주제는 "OOP를 쓰지 말아야 할 때"입니다.

가장 어려운 설계 결정은 "어떤 클래스를 더 만들까?"가 아니라 "이걸 정말 클래스여야 하나?"입니다. AI가 만들어준 코드가 클래스 투성이여서 읽기 어렵다면, 어떤 것을 단순화해도 되는지 판단할 수 있어야 합니다.

> "OOP는 도구이지 종교가 아닙니다. '언제 안 써야 하는가'를 모르고 'OOP가 좋다'고 외우면, 모든 못이 망치로 보이기 시작합니다."

## 이 글에서 다룰 문제

- AI가 만든 코드에서 클래스가 너무 많다는 신호는 무엇인가요?
- 어떤 클래스가 함수, `dataclass`, `TypedDict`로 더 잘 바뀔까요?
- 전략 클래스 전체 대신 콜러블 하나면 충분한 순간은 언제일까요?
- 함수 파이프라인은 언제 다시 클래스로 되돌아가야 할까요?
- AI에게 어떻게 단순화를 요청할 수 있을까요?

## 핵심 개념 잡기

```text
클래스가 필요 없는 경우:
  - 인스턴스 상태가 없음 (모든 메서드가 인자만 사용)
  - 단일 메서드만 존재 (사실상 함수 포장)
  - 데이터만 저장 (검증, 비즈니스 로직 없음)

클래스가 필요한 경우:
  - 상태와 상태 전이가 있음 (open/suspend/close)
  - 불변식 검증이 있음 (잔액 >= 0)
  - 여러 협력 객체와 수명주기를 공유
```

| 용어 | 설명 |
|------|------|
| 빈혈 클래스 | 데이터 보관이나 단일 메서드 래핑에 가까운 얇은 클래스입니다 |
| `dataclass` | 데이터 중심 구조를 간결하게 표현하는 Python 기능입니다 |
| 콜러블 | 함수처럼 호출할 수 있는 객체나 함수 자체입니다 |
| 재도입 임계점 | 상태, 검증, 수명주기 조정이 커져 다시 클래스가 유리해지는 시점입니다 |

## Before / After: AI가 과도하게 클래스를 쓰는 경우

```python
# Before: 상태 없는 헬퍼도 모두 클래스로 감쌈 — 인스턴스 생성 비용만 증가
class TitleCleaner:
    def clean(self, title: str) -> str:
        return title.strip().title()

class ScoreFilter:
    def keep(self, score: int, minimum: int) -> bool:
        return score >= minimum

class CurrencyFormatter:
    def format(self, value: int) -> str:
        return f"${value:,.0f}"

# 사용할 때마다 인스턴스를 만들어야 함
cleaner = TitleCleaner()
filt = ScoreFilter()
formatter = CurrencyFormatter()
print(cleaner.clean("  spring launch "))
print(filt.keep(82, 80))
print(formatter.format(12500))
```

```python
# After: 상태 없는 로직은 함수로 — 직접 호출, 조합이 쉬움
def clean_title(title: str) -> str:
    return title.strip().title()

def keep_score(score: int, minimum: int) -> bool:
    return score >= minimum

def format_currency(value: int) -> str:
    return f"${value:,.0f}"

# 인스턴스 생성 없이 바로 사용
print(clean_title("  spring launch "))  # Spring Launch
print(keep_score(82, 80))               # True
print(format_currency(12500))           # $12,500
```

상태가 없고 메서드가 하나뿐인 클래스는 함수 하나로 충분합니다. 클래스는 상태를 관리하고 불변식을 보호할 때 값어치를 합니다.

## 바이브코딩 관점: AI가 과잉 설계하는 패턴 4가지

AI가 코드를 생성할 때 클래스를 너무 많이 만드는 전형적인 패턴이 있습니다.

### 패턴 1: 데이터 보관용 수제 클래스 → `dataclass`로

```python
# AI가 만든 수제 클래스 — __init__, __repr__ 모두 직접 작성
class ReportRow:
    def __init__(self, title: str, score: int, spend: int) -> None:
        self.title = title
        self.score = score
        self.spend = spend

    def __repr__(self) -> str:
        return f"ReportRow(title={self.title!r}, score={self.score}, spend={self.spend})"

# AI에게 이렇게 요청하세요:
# "이 클래스를 @dataclass로 바꿔 줘"

from dataclasses import dataclass

@dataclass(frozen=True)
class ReportRow:
    title: str
    score: int
    spend: int

# ReportRow(title='Spring Launch', score=82, spend=12500)
row = ReportRow(title="Spring Launch", score=82, spend=12500)
print(row)
```

### 패턴 2: 설정 클래스 → `TypedDict`로

```python
# AI가 만든 설정 클래스 — 단순 보관인데 클래스 사용
class ReportConfig:
    def __init__(self, minimum_score: int, channel: str) -> None:
        self.minimum_score = minimum_score
        self.channel = channel

# AI에게 이렇게 요청하세요:
# "이 설정 클래스를 TypedDict로 바꿔 줘"

from typing import TypedDict

class ReportConfig(TypedDict):
    minimum_score: int
    channel: str

config: ReportConfig = {"minimum_score": 80, "channel": "email"}
print(config["channel"])  # email
```

### 패턴 3: 단일 메서드 전략 클래스 → 콜러블로

```python
# AI가 만든 전략 클래스 — 메서드 하나뿐
class CurrencyFormatter:
    def format(self, value: int) -> str:
        return f"${value:,.0f}"

class PointFormatter:
    def format(self, value: int) -> str:
        return f"{value} pts"

# AI에게 이렇게 요청하세요:
# "단일 메서드 전략 클래스를 콜러블로 바꿔 줘"

from collections.abc import Callable

def format_currency(value: int) -> str:
    return f"${value:,.0f}"

def format_points(value: int) -> str:
    return f"{value} pts"

def render_value(value: int, formatter: Callable[[int], str]) -> str:
    return formatter(value)

print(render_value(12500, format_currency))  # $12,500
print(render_value(82, format_points))       # 82 pts
```

### 패턴 4: 클래스 조합 → 함수 파이프라인으로

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
        ReportRow(title=clean_title(row["title"]), score=row["score"], spend=row["spend"])
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
# Summer Promo | score=91 | spend=$18,000
# Spring Launch | score=82 | spend=$12,500
```

6개 클래스가 함수들과 경량 데이터 구조로 바뀌었습니다. 각 단계가 독립적으로 테스트 가능하고, 위에서 아래로 읽힙니다.

## 다시 클래스로 돌아가는 시점

함수 파이프라인도 한계가 있습니다. 다음 중 두 가지 이상이 보이면 클래스를 다시 도입할 때입니다.

| 신호 | 왜 클래스가 도움이 되는가 |
|------|--------------------------|
| 같은 필드 묶음이 함수 사이를 반복해서 이동 | 도메인 객체가 불변식과 동작을 한곳에 묶을 수 있습니다 |
| 검증 규칙과 상태 전이가 함께 반복됨 | 메서드와 캡슐화된 상태가 더 추론하기 쉬워집니다 |
| 포매터나 전략이 설정, 캐시 같은 지속 상태를 가짐 | 매번 인자를 늘리는 것보다 상태 객체가 분명해집니다 |
| 파이프라인이 재시도, 훅, 공유 협력 객체를 요구 | 조정자 객체가 횡단 관심사를 맡기 쉬워집니다 |

## 자주 하는 실수

| 실수 | 왜 문제인가 | 더 나은 선택 |
|------|------------|--------------|
| 모든 헬퍼를 클래스로 만듦 | 단순한 파이프라인이 객체 노이즈에 가려집니다 | 모듈 함수로 시작합니다 |
| 평범한 데이터에 수제 클래스를 사용 | boilerplate가 가치보다 빨리 늘어납니다 | `dataclass`, `NamedTuple`, `TypedDict`를 사용합니다 |
| 함수 하나 감싼 전략 클래스를 유지 | 상태 없는 간접 계층만 남습니다 | 콜러블을 직접 전달합니다 |
| 함수 중심 설계를 끝까지 고집 | 상태와 검증이 흩어집니다 | 불변식이 반복되면 클래스를 재도입합니다 |
| dict 기반 설정을 너무 오래 방치 | 오타와 기본값 누락이 늦게 드러납니다 | 설정 복잡도가 커지면 더 풍부한 객체로 올립니다 |

## AI 팁: 과잉 클래스 단순화 요청하기

AI가 만든 코드에서 클래스가 너무 많다고 느껴질 때 활용할 수 있는 요청 패턴입니다.

```python
# AI가 생성한 과잉 클래스 코드
class CsvReader:
    def run(self, path: str) -> list[dict]:
        ...

class RowNormalizer:
    def run(self, rows: list[dict]) -> list[dict]:
        ...

class InvalidFilter:
    def run(self, rows: list[dict]) -> list[dict]:
        ...

# AI에게 이렇게 요청하세요:
# "이 클래스들이 모두 상태가 없고 메서드가 하나야.
#  함수 파이프라인으로 단순화해 줘"

# AI가 만들어 줄 패턴
from collections.abc import Iterable

def read_csv(path: str) -> list[dict]:
    ...

def normalize_row(row: dict) -> dict:
    ...

def filter_invalid(rows: Iterable[dict]) -> list[dict]:
    return [r for r in rows if r.get("price", 0) > 0]

def pipeline(path: str) -> list[dict]:
    rows = read_csv(path)
    normalized = [normalize_row(r) for r in rows]
    return filter_invalid(normalized)
```

또한 AI에게 클래스가 필요한지 판단을 물어볼 수도 있습니다.

```python
# AI에게 이렇게 요청하세요:
# "이 클래스가 정말 클래스여야 하는지 판단해 줘.
#  상태가 없거나 메서드가 하나면 함수로 바꿔 줘"

# AI가 판단 기준으로 사용하는 신호:
# - self.xxx 필드를 저장하고 나중에 읽는가? → 클래스 유지
# - 메서드가 인자만 사용하는가? → 함수로 변환
# - 여러 메서드가 같은 self.xxx를 공유하는가? → 클래스 유지
```

## 체크리스트

- [ ] 상태 없는 헬퍼 클래스를 함수로 식별하고 바꿀 수 있다
- [ ] 데이터 보관 클래스를 `@dataclass`나 `TypedDict`로 변환할 수 있다
- [ ] 단일 메서드 전략 클래스 대신 콜러블을 사용할 수 있다
- [ ] 변환 중심 코드를 읽기 쉬운 함수 파이프라인으로 만들 수 있다
- [ ] 상태와 불변식이 커질 때 클래스를 다시 도입해야 하는 이유를 설명할 수 있다

## 처음 질문으로 돌아가기

- **AI가 만든 코드에서 클래스가 너무 많다는 신호는 무엇인가요?**
  인스턴스 상태가 없고, 메서드가 하나뿐이거나, 생성자에서 필드만 저장하는 클래스가 여러 개라면 과잉 클래스화의 신호입니다. AI에게 "상태 없는 클래스를 함수로 바꿔 줘"라고 요청하면 됩니다.

- **어떤 클래스가 함수, `dataclass`, `TypedDict`로 더 잘 바뀔까요?**
  상태 없는 헬퍼 클래스는 함수로, `__init__`에서 필드만 저장하는 클래스는 `@dataclass`로, 설정을 담는 클래스는 `TypedDict`로 바꾸면 코드가 훨씬 가벼워집니다.

- **함수 파이프라인은 언제 다시 클래스로 되돌아가야 할까요?**
  같은 상태가 여러 함수 사이를 반복해서 이동하거나, 검증 규칙이 여러 곳에 흩어지기 시작하면 클래스로 묶을 때입니다. 절제가 설계 능력의 일부입니다.

## 정리

OOP는 도구입니다. 상태, 불변식, 수명주기 조정이 필요할 때는 클래스가 최선입니다. 하지만 상태도 없고 메서드도 하나뿐인 클래스는 함수로, 데이터만 담는 클래스는 `@dataclass`로, 설정은 `TypedDict`로, 단일 동작은 콜러블로 대체하면 코드가 더 직접적으로 읽힙니다. AI가 클래스를 너무 많이 만들었다면, 이제 어디를 단순화해야 하는지 판단할 수 있습니다.

## 참고 자료

- [Python 공식 문서 — dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Python 공식 문서 — typing.NamedTuple / TypedDict / Callable](https://docs.python.org/3/library/typing.html)
- [Stop Writing Classes — PyCon Talk by Jack Diederich](https://www.youtube.com/watch?v=o9pEzgHorH0)
- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 객체지향 기초 (1/10): 객체지향이란 무엇인가?
- 바이브코딩을 위한 객체지향 기초 (2/10): 클래스와 인스턴스
- 바이브코딩을 위한 객체지향 기초 (3/10): 캡슐화
- 바이브코딩을 위한 객체지향 기초 (4/10): 상속
- 바이브코딩을 위한 객체지향 기초 (5/10): 다형성
- 바이브코딩을 위한 객체지향 기초 (6/10): 추상화
- 바이브코딩을 위한 객체지향 기초 (7/10): 합성과 상속
- 바이브코딩을 위한 객체지향 기초 (8/10): SOLID 원칙 기초
- 바이브코딩을 위한 객체지향 기초 (9/10): 객체지향 설계 예제
- **바이브코딩을 위한 객체지향 기초 (10/10): 객체지향을 언제 피해야 할까? (현재 글)**

<!-- toc:end -->

Tags: Python, OOP, 함수형 프로그래밍, dataclass, 바이브코딩, 설계 판단
