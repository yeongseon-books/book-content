---
title: "바이브코딩을 위한 객체지향 기초 (6/10): 추상화"
series: oop-101
episode: 6
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - Python
  - OOP
  - 추상화
  - 바이브코딩
  - ABC
  - 인터페이스
last_reviewed: '2026-06-18'
seo_description: AI가 ABC와 abstractmethod를 사용하는 이유를 설명합니다. 바이브코딩에서 추상 클래스와 Protocol을 구분하는 기준을 정리합니다.
---

# 바이브코딩을 위한 객체지향 기초 (6/10): 추상화

이 글은 **바이브코딩을 위한 객체지향 기초** 시리즈의 여섯 번째 글입니다.

---

AI에게 데이터 파이프라인을 만들어 달라고 하면 `from abc import ABC, abstractmethod`가 나오고, 직접 인스턴스화할 수 없는 기묘한 클래스가 등장합니다. `FeedSource(ABC)`를 상속받은 구현체를 만들지 않으면 `TypeError`가 납니다. 왜 이렇게 만들었을까요?

AI가 ABC를 쓰는 이유는 **팀 계약을 강제하기 위해서**입니다. 구현체가 여러 개로 늘어날 때, 각자 다른 메서드 이름을 쓰면 호출부가 구현체마다 다른 코드를 알아야 합니다. ABC는 "이 메서드는 반드시 구현해야 한다"는 계약을 코드 레벨에서 강제합니다.

AI가 클래스 계층을 만들어줬는데 왜 이렇게 짰는지 이해하려면 OOP를 알아야 합니다.

> "추상화는 복잡한 걸 숨기는 일이 아니라, 필요한 결정만 남기고 나머지를 보이지 않게 옮기는 일입니다."

## 이 글에서 다룰 문제

- 덕 타이핑 관례만으로는 언제부터 부족해질까요?
- ABC와 `@abstractmethod`는 어떤 상황에서 필요할까요?
- 템플릿 메서드 패턴은 어떻게 공통 흐름을 부모에 두게 할까요?
- ABC와 Protocol 중 어떤 것을 선택해야 할까요?
- AI가 만든 추상 클래스를 어떻게 확장해야 할까요?

## 핵심 개념 잡기

```text
덕 타이핑만으로 충분한 경우:
  - 메서드 이름이 자연스럽게 통일됨
  - 팀원이 적고 코드베이스가 단순함

ABC가 필요한 경우:
  - 여러 팀원이 다른 메서드 이름을 쓰기 시작함
  - 미완성 구현체가 배포되면 안 됨
  - 공통 흐름은 부모에 두고 구현만 다르게 하고 싶음
```

| 용어 | 설명 |
|------|------|
| 추상 클래스 | 직접 인스턴스화할 수 없고 하위 클래스에 구현을 강제하는 클래스입니다 |
| `@abstractmethod` | 하위 클래스가 반드시 구현해야 하는 메서드를 표시합니다 |
| ABC | `abc` 모듈이 제공하는 명시적 계약 메커니즘입니다 |
| 템플릿 메서드 패턴 | 부모가 워크플로 골격을 가지고, 자식이 가변 단계를 채우는 패턴입니다 |

## Before / After: AI가 ABC를 도입하는 이유

```python
# Before: 구현체마다 다른 메서드 이름 — 호출부가 구현 상세를 알아야 함
class CsvFeed:
    def read_file(self, path: str) -> list[dict]:  # read_file
        return [{"email": "alice@example.com"}]

class WarehouseFeed:
    def fetch_rows(self, table: str) -> list[dict]:  # fetch_rows — 이름이 다름
        return [{"email": "bob@example.com"}]

def ingest(source):
    return source.fetch_records()  # 어떤 메서드를 불러야 할지 모름
    # AttributeError: 'CsvFeed' object has no attribute 'fetch_records'
```

```python
# After: ABC로 팀 계약 고정 — 모든 구현체가 같은 메서드를 가짐
from abc import ABC, abstractmethod

class FeedSource(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str: ...  # 반드시 구현

    @abstractmethod
    def fetch_records(self) -> list[dict]: ...  # 반드시 구현

class CsvFeed(FeedSource):
    @property
    def source_name(self) -> str:
        return "csv"

    def fetch_records(self) -> list[dict]:
        return [{"email": "alice@example.com"}]

class WarehouseFeed(FeedSource):
    @property
    def source_name(self) -> str:
        return "warehouse"

    def fetch_records(self) -> list[dict]:
        return [{"email": "bob@example.com"}]

def ingest(source: FeedSource) -> list[dict]:
    return source.fetch_records()  # 어떤 구현체든 fetch_records() 보장
```

ABC를 상속받은 클래스가 `fetch_records()`를 구현하지 않으면 인스턴스 생성 시점에 `TypeError`가 납니다. 미완성 구현체가 배포되는 것을 원천 차단합니다.

## 바이브코딩 관점: 템플릿 메서드 패턴

AI가 더 복잡한 파이프라인을 만들 때 나오는 패턴입니다. 부모가 실행 흐름을 잡고, 자식은 달라지는 부분만 구현합니다.

```python
from abc import ABC, abstractmethod

class IngestionPipeline(ABC):
    def run(self) -> list[dict]:
        """공통 흐름: 부모가 순서를 정의"""
        raw = self.fetch_records()           # 자식마다 다름
        normalized = [self._normalize(row) for row in raw]
        valid = [row for row in normalized if self._is_valid(row)]
        self.store(valid)                    # 자식마다 다름
        print(f"[{self.source_name}] {len(valid)}개 로드")
        return valid

    @property
    @abstractmethod
    def source_name(self) -> str: ...

    @abstractmethod
    def fetch_records(self) -> list[dict]: ...

    def _normalize(self, row: dict) -> dict:
        """공통 정규화 로직: 부모에서 기본 구현 제공"""
        return {"email": row["email"].strip().lower()}

    def _is_valid(self, row: dict) -> bool:
        return "@" in row["email"]

    @abstractmethod
    def store(self, rows: list[dict]) -> None: ...

class CsvPipeline(IngestionPipeline):
    @property
    def source_name(self) -> str:
        return "csv"

    def fetch_records(self) -> list[dict]:
        return [{"email": " Alice@example.com "}]

    def store(self, rows: list[dict]) -> None:
        for row in rows:
            print(f"저장: {row}")

# 실행 순서는 부모가 정의, 구현은 자식이 제공
pipeline = CsvPipeline()
pipeline.run()
# 저장: {'email': 'alice@example.com'}
# [csv] 1개 로드
```

이 패턴을 보면 AI는 "공통 흐름은 한 곳에서 관리하고, 달라지는 부분만 각 구현체가 담당하도록" 설계한 것입니다.

## ABC vs Protocol: 언제 무엇을 선택하는가?

| 질문 | 예라면 | 더 적합한 선택 |
|------|--------|----------------|
| 구현체를 우리가 대부분 소유하는가 | 예 | ABC |
| 공통 기본 동작이 필요한가 | 예 | ABC |
| 상속 없이 모양 호환만 필요한가 | 예 | Protocol |
| 외부 라이브러리 구현체인가 | 예 | Protocol 또는 `register()` |

## 자주 하는 실수

| 실수 | 왜 문제인가 | 더 나은 선택 |
|------|------------|--------------|
| 모든 인터페이스를 ABC로 만듦 | 외부 통합까지 불필요한 상속을 강제합니다 | 모양 호환이면 Protocol을 사용합니다 |
| 부모 클래스에 로직을 너무 많이 넣음 | 추상 클래스가 거대해집니다 | 진짜 공통 단계만 부모에 둡니다 |
| 추상 멤버 없는 ABC 사용 | 계약이 실제로 아무것도 강제하지 않습니다 | 최소 하나의 필수 메서드나 프로퍼티를 둡니다 |
| 자식마다 같은 책임의 메서드 이름을 바꿈 | 호출부가 구현 상세에 분기합니다 | 먼저 공통 어휘를 고정합니다 |
| ABC 미완성 구현을 테스트로 사용 | TypeError가 납니다 | 테스트용 최소 구현 클래스를 만듭니다 |

## AI 팁: ABC 구현체 작성하기

AI가 만든 ABC를 보면 어떻게 확장해야 할지 알 수 있습니다.

```python
# AI가 만든 ABC
class FeedSource(ABC):
    @abstractmethod
    def fetch_records(self) -> list[dict]: ...

# AI에게 이렇게 요청하세요:
# "FeedSource를 상속받아 JSON 파일을 읽는 구현체를 만들어 줘"

# AI가 만들어 줄 구현체 패턴
class JsonFeed(FeedSource):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def fetch_records(self) -> list[dict]:
        import json
        with open(self.file_path) as f:
            return json.load(f)

# 추상 메서드를 빠뜨리면 즉시 오류가 납니다
# class BrokenFeed(FeedSource):
#     pass  # TypeError: Can't instantiate abstract class
```

## 체크리스트

- [ ] ABC와 `@abstractmethod`의 역할을 설명할 수 있다
- [ ] 템플릿 메서드 패턴으로 공통 흐름을 부모에 둘 수 있다
- [ ] ABC와 Protocol 중 언제 무엇을 선택할지 판단할 수 있다
- [ ] AI가 만든 ABC를 상속받아 구현체를 작성할 수 있다
- [ ] 추상 메서드를 빠뜨렸을 때 발생하는 오류를 이해한다

## 처음 질문으로 돌아가기

- **덕 타이핑만으로는 언제부터 부족해질까요?**
  구현체가 여러 명이 만드는 상황이 되면 메서드 이름이 제각각이 됩니다. AI가 ABC를 만들 때는 "이 계약을 모든 구현체가 지켜야 한다"는 의도입니다.

- **ABC는 어떤 메서드를 강제해야 할까요?**
  "모든 구현체가 반드시 달라야 하는 부분"을 `@abstractmethod`로 표시합니다. "모든 구현체가 같은 방식으로 처리해도 되는 부분"은 부모에서 기본 구현을 제공합니다.

- **ABC와 Protocol 중 어떤 것을 선택해야 할까요?**
  내부에서 소유하고 공통 동작이 필요하면 ABC, 외부 라이브러리나 모양 호환만 필요하면 Protocol입니다. AI가 둘 중 하나를 선택한 이유를 이해하면 코드를 수정할 때 실수를 줄일 수 있습니다.

## 정리

추상화는 여러 구현체가 공통 계약을 지키도록 강제합니다. AI가 ABC를 쓸 때는 "이 인터페이스는 반드시 구현해야 한다"는 팀 계약을 코드로 표현한 것입니다. 다음 글에서는 합성과 상속을 비교하고, AI가 언제 상속 대신 합성을 선택하는지 알아봅니다.

## 참고 자료

- [Python 공식 문서 — abc 모듈](https://docs.python.org/3/library/abc.html)
- [PEP 544 — Protocols: Structural Subtyping](https://peps.python.org/pep-0544/)
- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 객체지향 기초 (1/10): 객체지향이란 무엇인가?
- 바이브코딩을 위한 객체지향 기초 (2/10): 클래스와 인스턴스
- 바이브코딩을 위한 객체지향 기초 (3/10): 캡슐화
- 바이브코딩을 위한 객체지향 기초 (4/10): 상속
- 바이브코딩을 위한 객체지향 기초 (5/10): 다형성
- **바이브코딩을 위한 객체지향 기초 (6/10): 추상화 (현재 글)**
- 바이브코딩을 위한 객체지향 기초 (7/10): 합성과 상속
- 바이브코딩을 위한 객체지향 기초 (8/10): SOLID 원칙 기초
- 바이브코딩을 위한 객체지향 기초 (9/10): 객체지향 설계 예제
- 바이브코딩을 위한 객체지향 기초 (10/10): 객체지향을 언제 피해야 할까?

<!-- toc:end -->

Tags: Python, OOP, 추상화, 바이브코딩, ABC, 인터페이스
