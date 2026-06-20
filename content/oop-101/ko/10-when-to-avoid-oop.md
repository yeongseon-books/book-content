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

가장 어려운 객체지향 결정은 종종 "어떤 클래스를 더 만들까?"가 아니라 "이걸 정말 클래스여야 하나?"입니다. 클래스가 있으면 더 전문적으로 보이는 것 같고, 함수로만 구성하면 구조가 없는 것처럼 느껴질 수 있습니다. 하지만 현업에서는 불필요한 클래스가 유지보수를 어렵게 만드는 경우가 적지 않습니다.

Python은 클래스와 함수를 모두 일급 시민으로 대우합니다. 어떤 로직에 클래스가 필요한지, 어떤 로직은 함수, `dataclass`, 함수형 접근이 더 나은지 판단하는 능력이 OOP 학습의 마지막 단계입니다.

이 글은 OOP 101 시리즈의 마지막 글입니다.

![Object-Oriented Programming 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/10/10-01-big-picture.ko.png)
*Object-Oriented Programming 101 10장 흐름 개요*

## 이 글에서 다룰 문제

- OOP가 과잉 설계가 되는 신호는 무엇인가요?
- 순수 함수와 함수형 스타일이 클래스보다 나은 상황은 언제인가요?
- `dataclass`와 `TypedDict`는 어떤 상황에서 클래스를 대체할 수 있나요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 이 글에서 배울 것

- OOP 과잉 설계의 신호를 인식합니다
- 순수 함수와 파이프라인으로 데이터 처리를 단순화합니다
- `dataclass`와 `TypedDict`의 올바른 사용 상황을 구분합니다
- callable 객체와 함수의 트레이드오프를 이해합니다
- 클래스 도입 타이밍 판단 기준을 갖춥니다

## 핵심 개념

| 접근 방식 | 적합한 상황 |
|----------|------------|
| 순수 함수 | 상태가 없고, 입력만으로 출력이 결정될 때 |
| `dataclass` | 데이터 컨테이너가 필요하고, 복잡한 메서드가 없을 때 |
| `TypedDict` | 딕셔너리 구조를 타입으로 문서화할 때 |
| callable 클래스 | 설정 상태가 필요한 함수가 필요할 때 |
| 일반 클래스(OOP) | 상태와 행위가 함께 변경되고, 수명주기가 명확할 때 |

## 전후 비교

캠페인 보고서 처리를 비교합니다.

```python
# before: 불필요한 클래스 — 상태 없이 메서드만 있음
class CampaignReportProcessor:
    def load(self, path: str) -> list[dict]:
        return []  # 파일 로드 시뮬레이션

    def filter_active(self, records: list[dict]) -> list[dict]:
        return [r for r in records if r.get("active")]

    def calculate_ctr(self, records: list[dict]) -> list[dict]:
        return [{**r, "ctr": r["clicks"] / r["impressions"]} for r in records if r["impressions"] > 0]

    def sort_by_ctr(self, records: list[dict]) -> list[dict]:
        return sorted(records, key=lambda r: r["ctr"], reverse=True)

    def process(self, path: str) -> list[dict]:
        records = self.load(path)
        records = self.filter_active(records)
        records = self.calculate_ctr(records)
        return self.sort_by_ctr(records)
```

```python
# after: 순수 함수 파이프라인 — 테스트와 조합이 쉬움
def filter_active(records: list[dict]) -> list[dict]:
    return [r for r in records if r.get("active")]

def calculate_ctr(records: list[dict]) -> list[dict]:
    return [
        {**r, "ctr": r["clicks"] / r["impressions"]}
        for r in records
        if r["impressions"] > 0
    ]

def sort_by_ctr(records: list[dict]) -> list[dict]:
    return sorted(records, key=lambda r: r["ctr"], reverse=True)

def process_campaign_report(records: list[dict]) -> list[dict]:
    return sort_by_ctr(calculate_ctr(filter_active(records)))
```

순수 함수 버전은 각 단계를 독립적으로 테스트할 수 있고, 파이프라인을 조합하거나 순서를 바꾸기도 쉽습니다.

## 단계별 실습

### 1단계: OOP 과잉 신호 인식

```python
# OOP 과잉 신호 1: 상태 없이 메서드만 있는 클래스
class StringUtils:
    @staticmethod
    def to_upper(s: str) -> str:
        return s.upper()

    @staticmethod
    def truncate(s: str, max_len: int) -> str:
        return s[:max_len]

# 더 나은 방법: 모듈 수준 함수
def to_upper(s: str) -> str:
    return s.upper()

def truncate(s: str, max_len: int) -> str:
    return s[:max_len]

# OOP 과잉 신호 2: 인스턴스화하자마자 바로 메서드 하나만 호출
class TaxCalculator:
    def calculate(self, amount: int, rate: float) -> int:
        return int(amount * rate)

result = TaxCalculator().calculate(10000, 0.1)  # 인스턴스 생성 후 바로 버림

# 더 나은 방법: 함수
def calculate_tax(amount: int, rate: float) -> int:
    return int(amount * rate)

result = calculate_tax(10000, 0.1)
```

### 2단계: dataclass로 데이터 컨테이너 표현

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class CampaignReport:
    """순수 데이터 컨테이너 — 메서드 최소화"""
    campaign_id: str
    name: str
    impressions: int
    clicks: int
    spend: int
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def ctr(self) -> float:
        """계산 속성만 허용 — 비즈니스 로직은 외부 함수에"""
        if self.impressions == 0:
            return 0.0
        return self.clicks / self.impressions

    @property
    def cpc(self) -> float:
        """비용 per 클릭"""
        if self.clicks == 0:
            return 0.0
        return self.spend / self.clicks

# 분리된 처리 함수
def filter_profitable(reports: list[CampaignReport], max_cpc: float) -> list[CampaignReport]:
    return [r for r in reports if r.active and r.cpc <= max_cpc]

def summarize(reports: list[CampaignReport]) -> dict:
    total_spend = sum(r.spend for r in reports)
    total_clicks = sum(r.clicks for r in reports)
    return {
        "campaign_count": len(reports),
        "total_spend": total_spend,
        "total_clicks": total_clicks,
        "avg_cpc": total_spend / total_clicks if total_clicks else 0,
    }

reports = [
    CampaignReport("C1", "Summer Sale", 100000, 3000, 150000),
    CampaignReport("C2", "Spring Ad", 50000, 500, 80000),
]
profitable = filter_profitable(reports, max_cpc=60)
print(summarize(profitable))
```

### 3단계: TypedDict로 딕셔너리 구조화

```python
from typing import TypedDict, NotRequired

class UserRecord(TypedDict):
    id: str
    name: str
    email: str
    role: str
    age: NotRequired[int]  # 선택 필드

def create_user_record(id: str, name: str, email: str) -> UserRecord:
    return {"id": id, "name": name, "email": email, "role": "viewer"}

def promote_user(user: UserRecord, new_role: str) -> UserRecord:
    return {**user, "role": new_role}

user = create_user_record("u1", "Alice", "alice@example.com")
admin = promote_user(user, "admin")
print(admin)  # {'id': 'u1', 'name': 'Alice', 'email': 'alice@example.com', 'role': 'admin'}
```

`TypedDict`는 딕셔너리 구조를 타입으로 문서화하지만 메서드를 추가할 수 없습니다. API 응답 파싱이나 JSON 처리처럼 데이터를 그대로 전달할 때 적합합니다.

### 4단계: callable 객체 — 상태 있는 함수

```python
from typing import Callable

class RateLimiter:
    """상태(호출 횟수)가 필요한 함수 — callable 클래스 적합"""
    def __init__(self, max_calls: int) -> None:
        self.max_calls = max_calls
        self._calls = 0

    def __call__(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            if self._calls >= self.max_calls:
                raise RuntimeError("Rate limit exceeded")
            self._calls += 1
            return func(*args, **kwargs)
        return wrapper

class ExponentialBackoff:
    """재시도 간격을 누적하는 callable"""
    def __init__(self, base: float = 1.0, factor: float = 2.0) -> None:
        self.base = base
        self.factor = factor
        self._attempt = 0

    def __call__(self) -> float:
        delay = self.base * (self.factor ** self._attempt)
        self._attempt += 1
        return delay

backoff = ExponentialBackoff(base=0.5)
for _ in range(4):
    print(f"Wait: {backoff():.1f}s")  # 0.5, 1.0, 2.0, 4.0
```

callable 클래스는 함수처럼 호출하지만 내부 상태를 유지합니다. 상태 없이 같은 기능만 제공한다면 일반 함수가 더 단순합니다.

### 5단계: functools로 함수형 파이프라인

```python
from functools import reduce
from typing import Callable

Pipeline = Callable[[list], list]

def compose(*funcs: Pipeline) -> Pipeline:
    """여러 변환 함수를 하나의 파이프라인으로 조합"""
    def pipeline(data: list) -> list:
        return reduce(lambda acc, f: f(acc), funcs, data)
    return pipeline

# 각 단계를 독립된 순수 함수로 정의
def remove_nulls(records: list) -> list:
    return [r for r in records if r is not None]

def normalize_emails(records: list[dict]) -> list[dict]:
    return [{**r, "email": r["email"].lower().strip()} for r in records if "email" in r]

def add_rank(records: list[dict]) -> list[dict]:
    return [{**r, "rank": i + 1} for i, r in enumerate(records)]

# 파이프라인 조합
process = compose(remove_nulls, normalize_emails, add_rank)

data = [
    {"name": "Alice", "email": "ALICE@EXAMPLE.COM"},
    None,
    {"name": "Bob", "email": "  BOB@EXAMPLE.COM  "},
]
result = process(data)
for r in result:
    print(r)
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 유틸리티 함수를 클래스로 감쌈 | 불필요한 인스턴스화가 필요합니다 | 모듈 수준 함수로 충분합니다 |
| 데이터만 있는 클래스에 메서드를 억지로 추가 | 응집도가 낮아집니다 | `dataclass`나 `TypedDict`를 사용합니다 |
| 상태 없는 로직에 클래스를 도입 | 테스트가 복잡해집니다 | 순수 함수가 더 간단합니다 |
| `TypedDict`에 메서드 추가 시도 | `TypedDict`는 딕셔너리 타입 힌트만 제공합니다 | 메서드가 필요하면 `dataclass`로 전환합니다 |
| 함수형과 OOP를 무조건 분리 | 두 방식은 보완 관계입니다 | 상태 관리는 OOP, 데이터 변환은 함수형을 조합합니다 |

## 실무에서 이렇게 쓰입니다

데이터 처리 파이프라인에서는 함수형 접근이 더 자연스럽습니다.

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class SalesRecord:
    region: str
    product: str
    amount: int
    is_refund: bool = False

# 각 변환을 순수 함수로 정의
def exclude_refunds(records: list[SalesRecord]) -> list[SalesRecord]:
    return [r for r in records if not r.is_refund]

def group_by_region(records: list[SalesRecord]) -> dict[str, int]:
    result: dict[str, int] = {}
    for r in records:
        result[r.region] = result.get(r.region, 0) + r.amount
    return result

def top_regions(grouped: dict[str, int], n: int = 3) -> list[tuple[str, int]]:
    return sorted(grouped.items(), key=lambda x: x[1], reverse=True)[:n]

# 데이터는 dataclass, 처리는 함수형
records = [
    SalesRecord("Seoul", "Book A", 50000),
    SalesRecord("Seoul", "Book B", 30000),
    SalesRecord("Busan", "Book A", 70000),
    SalesRecord("Seoul", "Book C", 20000, is_refund=True),
]

valid = exclude_refunds(records)
grouped = group_by_region(valid)
print(top_regions(grouped))  # [('Busan', 70000), ('Seoul', 80000)]
```

## 현업 개발자는 이렇게 생각합니다

OOP의 목적은 클래스를 많이 만드는 게 아니라, 변경 비용을 낮추는 것입니다. 상태와 행위가 함께 변경되는 경우에는 클래스가 강력합니다. 하지만 데이터를 읽어서 변환하고 반환하는 파이프라인에서는 순수 함수가 더 단순하고 테스트하기 쉽습니다.

"클래스를 써야 하나?"를 자문할 때 가장 좋은 기준은 다음입니다. 이 코드에 수명주기가 있는가? 생성과 소멸 사이에 상태가 유의미하게 변화하는가? 그렇다면 클래스입니다. 입력을 받아 출력을 반환하는 변환이라면 함수로 충분합니다.

## 운영 체크리스트

- [ ] OOP 과잉 설계의 신호를 인식할 수 있다
- [ ] 순수 함수로 데이터 처리 파이프라인을 구성할 수 있다
- [ ] `dataclass`와 `TypedDict`를 상황에 맞게 선택할 수 있다
- [ ] callable 클래스를 적절하게 활용할 수 있다
- [ ] OOP와 함수형을 상황에 맞게 조합할 수 있다

## 연습 문제

1. 파일 처리 유틸리티가 모두 정적 메서드만 있는 클래스로 구현되어 있습니다. 모듈 수준 함수로 리팩터링하고, 차이를 설명하세요.
2. 사용자 데이터 변환 파이프라인을 `compose` 함수로 구성하세요. 빈 이름 제거, 이메일 소문자화, 나이 검증 세 단계를 순수 함수로 만들고 조합합니다.
3. `EventCounter` callable 클래스를 만드세요. `max_per_window`와 `window_seconds` 설정으로 시간 창 안의 이벤트 수를 제한합니다.

## 정리 및 다음 단계

OOP는 도구입니다. 상태와 행위가 함께 변경되는 곳에서 클래스가 빛을 발합니다. 데이터 변환, 유틸리티 함수, 단순 컨테이너에서는 함수형 접근과 `dataclass`가 더 단순하고 테스트하기 쉽습니다.

이 시리즈를 통해 배운 OOP 원칙들은 클래스를 쓸 때 더 잘 쓰기 위한 기초입니다. 다음 단계로는 Python의 함수형 프로그래밍 패턴, 디자인 패턴, 또는 Domain-Driven Design을 공부하면 이 기초가 더 풍부해집니다.

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
- **Object-Oriented Programming 101 (10/10): 객체지향을 언제 피해야 할까? (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Python dataclasses 공식 문서](https://docs.python.org/3/library/dataclasses.html)
- [Python typing 공식 문서](https://docs.python.org/3/library/typing.html)
- [Python functools 공식 문서](https://docs.python.org/3/library/functools.html)
- [PyCon 2012 — Stop Writing Classes (Jack Diederich)](https://www.youtube.com/watch?v=o9pEzgHorH0)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)
Tags: Python, OOP, 함수형 프로그래밍, dataclass, 설계 판단
