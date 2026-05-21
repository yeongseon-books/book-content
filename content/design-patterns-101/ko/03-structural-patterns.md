---
series: design-patterns-101
episode: 3
title: "디자인 패턴 101 (3/10): 구조 패턴"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - DesignPatterns
  - Structural
  - Adapter
  - Decorator
  - Facade
seo_description: Structural 패턴으로 합성과 위임을 활용해 구조 변경 비용을 낮추는 방법을 설명합니다.
last_reviewed: '2026-05-15'
---

# 디자인 패턴 101 (3/10): 구조 패턴

생성 책임을 정리한 다음에는, 만들어진 객체들을 어떻게 엮을지가 다음 문제로 올라옵니다. 외부 라이브러리를 도메인에 바로 노출할지, 기존 객체에 기능을 덧씌울지, 복잡한 하위 시스템 앞에 단순한 입구를 둘지 같은 결정이 전부 구조의 문제입니다.

이 글은 Design Patterns 101 시리즈의 3번째 글입니다.

이번 글에서는 Structural 패턴을 “객체 합성의 이름표”로 보겠습니다. 핵심은 상속을 늘리는 대신 합성과 위임으로 구조를 조립해, 변경이 와도 전체 설계가 쉽게 굳어 버리지 않게 만드는 것입니다.

## 먼저 던지는 질문

- Structural 패턴은 어떤 구조적 문제를 풀까요?
- Adapter, Decorator, Facade는 각각 무엇을 단순화할까요?
- Proxy는 실제 객체 앞에서 어떤 책임을 대신 맡을까요?

## 큰 그림

![Design Patterns 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/03/03-01-concept-at-a-glance.ko.png)

*Design Patterns 101 3장 흐름 개요*

## 왜 중요한가

상속은 한번 뻗기 시작하면 구조를 빨리 굳혀 버립니다. 반면 합성은 같은 인터페이스를 유지한 채 구현을 감싸고, 바꾸고, 단순화하고, 트리로 엮을 수 있게 해 줍니다. 실무에서 구조 변경 비용을 낮추는 쪽은 대개 상속보다 합성입니다.

특히 외부 SDK, 미들웨어, 프록시 캐시, 하위 시스템 통합 같은 영역에서는 Structural 패턴이 거의 매일 등장합니다. 이름을 모르더라도 다들 이미 쓰고 있지만, 이름을 알고 보면 설계 의도를 훨씬 명확하게 설명할 수 있습니다.

## 한눈에 보는 개념

## 핵심 용어

- **Adapter**: 이미 있는 인터페이스를 우리가 원하는 모양으로 바꿉니다.
- **Decorator**: 객체를 감싸서 동적으로 책임을 추가합니다.
- **Facade**: 복잡한 하위 시스템 앞에 단순한 진입점을 둡니다.
- **Proxy**: 실제 객체를 대신해 접근 제어, 캐시, 지연 로딩을 맡습니다.
- **Composite**: 단일 객체와 객체 집합을 같은 방식으로 다룹니다.

## 변경 전후 비교

**Before**

```python
# external library calls leak into the domain
import boto3
s3 = boto3.client("s3")
s3.put_object(Bucket="b", Key="k", Body=data)
```

**After**

```python
# Adapter aligns the dependency to a domain interface
class FileStore:
    def put(self, key, data): ...

class S3FileStore(FileStore):
    def put(self, key, data): self._s3.put_object(...)
```

이후 도메인은 boto3를 몰라도 됩니다. 외부 의존성이 구조 경계 뒤로 숨었기 때문에 테스트와 교체가 쉬워집니다.

## 구조 패턴을 익히는 5단계

### 1단계 — 어댑터로 계약을 맞춥니다

```python
# 1_adapter.py
class LegacyPrinter:
    def write_line(self, s): ...

class NewPrinter:
    def print(self, s): ...

class PrinterAdapter(NewPrinter):
    def __init__(self, legacy): self.legacy = legacy
    def print(self, s): self.legacy.write_line(s)
```

예전 계약을 새 계약으로 번역해 주는 얇은 층입니다. 기존 코드를 대대적으로 바꾸지 않고도 호환성을 얻을 수 있습니다.

### 2단계 — 데코레이터로 기능을 덧씌웁니다

```python
# 2_decorator.py
class Logger:
    def __init__(self, inner): self.inner = inner
    def send(self, msg):
        print("LOG:", msg); self.inner.send(msg)

notifier = Logger(EmailNotifier())
```

기존 객체를 수정하지 않고도 로깅 같은 횡단 기능을 추가할 수 있습니다. 인터페이스를 유지한 채 감싼다는 점이 중요합니다.

### 3단계 — 퍼사드로 복잡한 흐름을 단순화합니다

```python
# 3_facade.py
class CheckoutFacade:
    def buy(self, user, item):
        cart.add(user, item); pay.charge(user); ship.send(user, item)
```

하위 시스템이 여러 개라도 호출자는 단일 진입점만 보면 됩니다. 복잡한 흐름을 숨기되, 새로운 기능을 무작정 떠안는 만능 객체가 되어서는 안 됩니다.

### 4단계 — 프록시로 실제 객체 앞에 책임을 둡니다

```python
# 4_proxy.py
class CachedRepo:
    def __init__(self, real): self.real = real; self.cache = {}
    def get(self, k):
        if k not in self.cache: self.cache[k] = self.real.get(k)
        return self.cache[k]
```

실제 객체를 대신해 캐시, 접근 제어, 지연 로딩을 붙일 때 유용합니다. 호출자 입장에서는 같은 계약처럼 보여야 합니다.

### 5단계 — 컴포지트로 트리 구조를 통일합니다

```python
# 5_composite.py
class Node:
    def total(self): ...

class File(Node):
    def __init__(self, size): self.size = size
    def total(self): return self.size

class Folder(Node):
    def __init__(self, children): self.children = children
    def total(self): return sum(c.total() for c in self.children)
```

파일과 폴더처럼 단일 항목과 집합을 같은 연산으로 다뤄야 할 때 Composite가 자연스럽습니다. 실제 데이터가 트리가 아닐 때는 오히려 어색해집니다.

## 이 코드에서 주목할 점

- 다섯 패턴 모두 핵심 도구는 상속보다 합성입니다.
- 인터페이스는 안정적으로 유지하고 구현만 교체합니다.
- 상속 트리를 키우지 않고도 책임을 조립할 수 있습니다.

## 자주 하는 실수 5가지

1. **Adapter 안에 비즈니스 로직을 넣는 경우**: 번역과 정책이 뒤엉킵니다.
2. **Decorator를 너무 깊게 겹치는 경우**: 디버깅이 급격히 어려워집니다.
3. **Facade가 만능 객체로 커지는 경우**: 단순화가 아니라 책임 폭발이 됩니다.
4. **Proxy의 시그니처가 실제 객체와 달라지는 경우**: 호출자가 깨집니다.
5. **트리가 아닌 곳에 Composite를 억지로 맞추는 경우**: 모델이 부자연스러워집니다.

## 실무에서는 이렇게 드러납니다

Flask 미들웨어 체인은 Decorator 모양이고, `requests.Session`은 Facade처럼 읽히며, ORM의 지연 로딩 객체는 Proxy의 성격을 띱니다. 외부 서비스 SDK를 도메인 인터페이스 뒤로 숨기는 순간에는 Adapter가 등장합니다. Structural 패턴은 조용하지만 거의 모든 라이브러리 안에 들어 있습니다.

## 빠르게 검증해 보기

Structural 패턴을 넣기 전에 아래를 점검해 보세요.

- 지금 어려운 점이 외부 경계, 래핑, 하위 시스템 단순화, 캐시/대리 책임 중 어디에 있는지 먼저 적습니다.
- 새 구조가 호출자 계약을 더 단순하게 만드는지 확인합니다.
- 합성이 실제로 호출자의 지식을 줄이는지, 아니면 복잡성을 옆으로 옮기기만 하는지 비교합니다.

**기대 결과:** 리팩터링 뒤에는 호출자가 더 안정적인 인터페이스만 보고, 구현 세부는 구조 경계 뒤에 남아 있어야 합니다.

## 시니어 엔지니어는 이렇게 판단합니다

- 합성을 기본값으로 둡니다.
- Adapter는 외부 경계에만 둡니다.
- Decorator는 같은 인터페이스 위에서만 겹칩니다.
- Facade의 목적을 기능 추가가 아니라 단순화로 제한합니다.
- Composite는 데이터가 진짜 트리일 때만 도입합니다.

## 체크리스트

- [ ] Adapter가 외부 경계에만 존재하는가?
- [ ] Decorator 체인이 과도하게 깊지 않은가?
- [ ] Facade가 호출을 단순화하는가?
- [ ] Proxy가 실제 객체와 같은 계약을 유지하는가?
- [ ] Composite가 실제 트리 구조를 반영하는가?

## 연습 문제

1. 외부 SaaS 호출 하나를 도메인 인터페이스 뒤에 Adapter로 감싸 봅니다.
2. 기존 Notifier에 Logger Decorator를 덧붙여 봅니다.
3. 폴더/파일 같은 트리 구조를 Composite로 모델링해 봅니다.

## 정리 및 다음 글

합성은 구조를 변경 가능하게 유지하는 가장 실용적인 기본값입니다. 다음 글에서는 구조에서 한 걸음 더 나아가, 객체들이 어떻게 협력하고 행동하는지를 다루는 Behavioral 패턴으로 넘어가겠습니다.

## 실전 보강: 패턴 선택을 코드와 표로 검증하기

디자인 패턴은 이름을 아는 것보다 **언제 적용하고 언제 버릴지**를 결정하는 능력이 더 중요합니다. 아래 보강 내용은 Python 코드, UML 유사 다이어그램, 선택 기준 표를 함께 사용해 판단 근거를 명확히 만드는 데 초점을 둡니다.

### 1) 전략 교체를 런타임으로 밀어내는 패턴

```python
from dataclasses import dataclass
from typing import Protocol

class DiscountPolicy(Protocol):
    def apply(self, price: int) -> int: ...

@dataclass
class NoDiscount:
    def apply(self, price: int) -> int:
        return price

@dataclass
class PercentDiscount:
    rate: float
    def apply(self, price: int) -> int:
        return int(price * (1 - self.rate))

@dataclass
class PriceCalculator:
    policy: DiscountPolicy

    def final_price(self, price: int) -> int:
        return self.policy.apply(price)
```

이 구조의 핵심은 `if/elif` 분기 증가를 객체 교체로 바꾸는 것입니다. 정책이 늘어도 기존 계산기 코드는 수정 없이 확장할 수 있습니다.

### 2) 유엠엘 유사 텍스트 다이어그램

```text
[Client] --> [PriceCalculator]
[PriceCalculator] --uses--> <<interface>> DiscountPolicy
[NoDiscount] ----implements----> DiscountPolicy
[PercentDiscount] -implements--> DiscountPolicy
```

다이어그램으로 보면 의존 방향이 분명해집니다. 구체 클래스가 아니라 추상 인터페이스로 향하면 테스트 더블 주입과 기능 확장이 쉬워집니다.

### 3) 패턴 도입 판단표

| 상황 | 도입 권장 패턴 | 기대 이점 | 과사용 신호 |
| --- | --- | --- | --- |
| 정책 분기가 자주 늘어남 | Strategy | 조건문 감소, 교체 용이 | 정책이 1개인데 인터페이스만 복잡 |
| 객체 생성 규칙이 다양함 | Factory | 생성 책임 분리 | 생성 규칙이 단순한데 팩토리 계층 과다 |
| 외부 라이브러리 인터페이스 상이 | Adapter | 호출부 안정화 | 어댑터가 비즈니스 규칙까지 흡수 |
| 이벤트 구독자가 동적으로 변함 | Observer | 결합도 완화 | 이벤트 흐름 추적 불가, 디버깅 난해 |

표를 사용하면 “패턴을 넣을지 말지”를 감각이 아니라 조건으로 설명할 수 있습니다.

### 4) 안티패턴 회피 예시

```python
# 과한 추상화 예시(피해야 함)
class AbstractFactoryProviderManager:
    def get_factory(self):
        ...

# 개선: 실제 문제에 맞춘 단순 함수

def build_storage(kind: str):
    if kind == "memory":
        return {}
    if kind == "sqlite":
        import sqlite3
        return sqlite3.connect("app.db")
    raise ValueError("unsupported storage")
```

패턴은 복잡성을 제거할 때만 가치가 있습니다. 불필요한 추상화 계층은 코드 탐색 비용만 늘립니다.

### 5) 테스트 가능성 기준으로 최종 판단

| 질문 | Pass 기준 |
| --- | --- |
| 교체 가능한 인터페이스가 필요한가 | 런타임 정책 변경 요구가 있음 |
| 테스트 더블 주입이 실제로 유용한가 | 외부 의존성 분리가 테스트 속도를 높임 |
| 새 요구가 들어올 때 수정 범위가 줄어드는가 | 기존 클래스 수정 없이 신규 클래스 추가 가능 |
| 팀이 패턴을 공통 언어로 이해하는가 | 리뷰에서 동일 용어로 의사결정 가능 |

패턴의 목적은 미학이 아니라 변경 비용 절감입니다. 코드, 다이어그램, 표 세 가지를 함께 점검하면 과설계와 미설계를 동시에 줄일 수 있습니다.

### 추가 사례: 패턴 적용 전후 비교

```python
# Before: 조건문이 도메인 로직 곳곳에 흩어진 경우

def notify(channel: str, message: str) -> None:
    if channel == "email":
        send_email(message)
    elif channel == "slack":
        send_slack(message)
    elif channel == "sms":
        send_sms(message)
    else:
        raise ValueError("unsupported channel")
```

```python
# After: 전략 등록 방식
from typing import Callable

class Notifier:
    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[str], None]] = {}

    def register(self, channel: str, handler: Callable[[str], None]) -> None:
        self._handlers[channel] = handler

    def notify(self, channel: str, message: str) -> None:
        if channel not in self._handlers:
            raise ValueError("unsupported channel")
        self._handlers[channel](message)
```

이 전환의 장점은 기능 추가 시 기존 분기 로직을 수정하지 않아도 된다는 점입니다. 변경 충돌이 줄고 테스트 범위가 국소화됩니다.

| 평가 항목 | 분기 확장 방식 | 패턴 기반 방식 |
| --- | --- | --- |
| 신규 채널 추가 | 기존 함수 수정 필요 | 등록 코드 추가 |
| 회귀 위험 | 높음 | 낮음 |
| 테스트 범위 | 기존 케이스 재검증 범위 큼 | 신규 핸들러 중심 검증 |
| 리뷰 난이도 | 조건 중첩으로 상승 | 역할 분리로 하락 |

## 실무 심화: 구조 경계를 세워 변경 파급을 차단하기

Structural 패턴을 도입하는 이유는 기능 추가가 아니라 파급 범위 제어입니다. 외부 의존성, 횡단 관심사, 복잡한 하위 시스템이 그대로 노출되면 작은 요구 변경도 여러 계층을 동시에 건드리게 됩니다.

### 유엠엘 유사 다이어그램

```text
[View] --> [Application Service]
[Application Service] --> <<interface>> [FileStore]
[S3Adapter] --implements--> [FileStore]
[LoggingDecorator] --wraps--> [FileStore]
[CachedProxy] --wraps--> [FileStore]
```

호출자는 `FileStore`만 보고, 나머지 구조는 래핑 계층에서 해결합니다.

### 변경 전후 리팩터링

```python
# 변경 전: Flask 라우트가 외부 SDK 세부를 직접 호출
@app.post('/upload')
def upload():
    s3 = boto3.client('s3')
    s3.put_object(Bucket='app-bucket', Key='k', Body=request.data)
    return {'ok': True}
```

```python
# 변경 후: 어댑터 + 데코레이터
class FileStore:
    def put(self, key: str, data: bytes) -> None: ...

class S3FileStore(FileStore):
    def __init__(self, client, bucket: str) -> None:
        self.client = client
        self.bucket = bucket

    def put(self, key: str, data: bytes) -> None:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data)

class LoggingStore(FileStore):
    def __init__(self, inner: FileStore) -> None:
        self.inner = inner

    def put(self, key: str, data: bytes) -> None:
        print('upload', key, len(data))
        self.inner.put(key, data)
```

이 구조에서는 업로드 로직 변경 없이 로깅, 캐시, 권한 검사를 계층적으로 붙일 수 있습니다.

### 장고/플라스크 적용 포인트

- Django 스토리지 백엔드를 직접 모델/뷰에서 호출하지 않고 저장 인터페이스 뒤에 감추면 클라우드 전환이 쉬워집니다.
- Flask에서는 미들웨어와 데코레이터 체인이 Structural 패턴의 대표 사례입니다.

### 솔리드 매핑

| 원칙 | 구조 패턴 적용 효과 |
| --- | --- |
| OCP | 기존 호출부 변경 없이 래퍼 추가 가능 |
| ISP | 호출자가 필요한 최소 인터페이스만 의존 |
| DIP | 상위 계층이 구체 SDK 대신 추상 계약을 참조 |

### 운영 체크리스트

1. 어댑터 클래스에 도메인 정책이 섞이지 않았는지 확인합니다.
2. 데코레이터 체인은 2~3단계 이내로 유지해 디버깅 난이도를 통제합니다.
3. 프록시 캐시 도입 시 무효화 규칙을 코드와 문서에 함께 남깁니다.

Structural 패턴은 "클래스를 예쁘게 배치하는 기술"이 아니라 "변경 충격을 격리하는 기술"입니다.


## 심화 워크숍: 패턴 적용을 운영 가능한 설계로 바꾸는 절차

패턴을 도입한 뒤 품질이 안정되는 팀과 그렇지 않은 팀의 차이는 구현 문법이 아니라 검증 절차입니다. 아래 절차는 패턴 적용을 코드 예제 수준에서 끝내지 않고, 리뷰/테스트/운영까지 연결하는 실무형 워크플로를 정리한 것입니다.

### 1단계: 요구사항을 변화 축으로 분해합니다

요구사항을 기능 단위로만 보면 패턴이 과하거나 부족해집니다. 먼저 "무엇이 자주 바뀌는지"를 분리해야 합니다. 예를 들어 결제 수단, 알림 채널, 저장소 구현, 권한 규칙은 변화 주기가 서로 다릅니다. 변화 주기가 다르면 클래스 경계도 달라져야 합니다.

```text
[요구사항]
  |- 자주 바뀜: 채널/정책/외부 API 계약
  |- 가끔 바뀜: 도메인 규칙
  |- 거의 안 바뀜: 엔터티 핵심 필드
```

이 분해를 먼저 하면 패턴 적용 대상이 명확해집니다.

### 2단계: 변경 전후를 코드로 고정합니다

```python
# 변경 전: 분기와 생성이 한 함수에 결합

def dispatch(kind: str, payload: dict) -> None:
    if kind == "email":
        client = SmtpClient(host="...")
        client.send(payload["to"], payload["body"])
    elif kind == "slack":
        client = SlackClient(webhook="...")
        client.push(payload["body"])
    else:
        raise ValueError("unsupported kind")
```

```python
# 변경 후: 생성과 실행을 분리
from typing import Protocol

class Sender(Protocol):
    def send(self, payload: dict) -> None: ...

class SenderFactory:
    def __init__(self, config: dict) -> None:
        self.config = config

    def create(self, kind: str) -> Sender:
        if kind == "email":
            return EmailSender(self.config["smtp_host"])
        if kind == "slack":
            return SlackSender(self.config["slack_webhook"])
        raise ValueError("unsupported kind")

class DispatchService:
    def __init__(self, factory: SenderFactory) -> None:
        self.factory = factory

    def dispatch(self, kind: str, payload: dict) -> None:
        self.factory.create(kind).send(payload)
```

변경 후 코드에서는 테스트 범위를 계층별로 나눌 수 있고, 새 채널 추가 시 수정 지점을 예측하기 쉬워집니다.

### 3단계: 유엠엘 유사 다이어그램으로 의존 방향을 검증합니다

```text
[Controller] --> [DispatchService]
[DispatchService] --> [SenderFactory]
[SenderFactory] --creates--> <<interface>> [Sender]
[EmailSender] --implements--> [Sender]
[SlackSender] --implements--> [Sender]
```

의존 방향이 위에서 아래로 한 번만 흐르면 코드 탐색 비용이 줄어듭니다.

### 4단계: 장고/플라스크 적용 지점을 분리합니다

- Django: `apps.py` 또는 설정 초기화 지점에서 팩토리/전략 조립을 끝내고, 뷰는 서비스 인터페이스만 호출합니다.
- Flask: `create_app()`에서 의존성 조립을 수행하고 블루프린트는 도메인 서비스에만 의존합니다.
- 공통 규칙: 프레임워크 객체(`request`, ORM 세션, 외부 SDK 클라이언트)를 도메인 모델 안으로 직접 흘려보내지 않습니다.

### 5단계: 솔리드 매핑으로 설계 품질을 점검합니다

| 원칙 | 적용 전 리스크 | 적용 후 기대 효과 |
| --- | --- | --- |
| SRP | 한 클래스가 정책/생성/실행을 동시에 담당 | 책임 분리로 변경 파급 축소 |
| OCP | 새 기능마다 기존 분기 수정 | 확장 지점 추가 중심으로 전환 |
| LSP | 대체 구현이 계약을 깨뜨림 | 인터페이스 테스트로 대체 가능성 보장 |
| ISP | 거대한 인터페이스 강요 | 용도별 작은 인터페이스 유지 |
| DIP | 상위 계층이 구체 SDK에 결합 | 추상 계약 의존으로 테스트 용이 |

### 6단계: 운영 로그와 알람 포인트를 함께 정의합니다

패턴을 적용해도 관측이 없으면 운영에서 효과를 확인할 수 없습니다. 다음 항목을 로그에 남겨야 합니다.

1. 선택된 전략/어댑터/팩토리 구현 이름
2. 처리 시간과 실패 원인(예외 타입)
3. 재시도 횟수와 최종 상태

이 로그가 있어야 "패턴 도입 이후 장애 회복 시간이 줄었는가"를 측정할 수 있습니다.

### 7단계: 테스트를 세 계층으로 분리합니다

```python
# 단위 테스트: 전략/어댑터 계약 테스트

def test_email_sender_contract():
    sender = FakeEmailSender()
    sender.send({"to": "a@example.com", "body": "hello"})
    assert sender.sent_count == 1
```

```python
# 통합 테스트: 팩토리 조립 + 서비스 실행

def test_dispatch_service_with_memory_config():
    cfg = {"smtp_host": "localhost", "slack_webhook": "http://localhost"}
    service = DispatchService(SenderFactory(cfg))
    service.dispatch("email", {"to": "a@example.com", "body": "x"})
```

```python
# 회귀 테스트: 새 구현 추가 시 기존 계약 보존

def test_new_sender_does_not_break_existing_contract():
    for sender in [FakeEmailSender(), FakeSlackSender()]:
        sender.send({"body": "ok"})
```

계층 분리를 하면 실패 원인을 더 빨리 좁힐 수 있습니다.

### 8단계: 패턴 남용 방지 규칙을 명시합니다

- 클래스 수가 늘어도 변경 지점 수가 줄지 않으면 과설계입니다.
- 인터페이스를 만들었는데 구현이 1개로 6개월 이상 유지되면 단순화 후보입니다.
- 패턴 이름을 설명해도 비즈니스 이득을 말할 수 없다면 적용 근거가 약합니다.

### 9단계: 문서화 템플릿

다음 템플릿을 ADR에 기록하면 팀 합의가 빨라집니다.

```text
문제: 어떤 변화가 반복되는가?
제약: 성능/보안/테스트/팀 숙련도 제약은 무엇인가?
선택: 어떤 패턴을 적용했는가?
대안: 왜 다른 패턴은 선택하지 않았는가?
결과: 얻는 이점과 추가 비용은 무엇인가?
```

### 10단계: 릴리스 후 회고 질문

1. 새 요구 추가 시 PR 수정 파일 수가 줄었는가?
2. 장애 발생 시 원인 계층(생성/구조/행위)을 빠르게 특정했는가?
3. 테스트 실행 시간이 합리적 수준으로 유지되는가?

이 회고를 반복하면 패턴은 지식이 아니라 조직 역량으로 축적됩니다.


## 처음 질문으로 돌아가기

- **Structural 패턴은 어떤 구조적 문제를 풀까요?**
  - 본문의 기준은 Structural 패턴를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Adapter, Decorator, Facade는 각각 무엇을 단순화할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Proxy는 실제 객체 앞에서 어떤 책임을 대신 맡을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Design Patterns 101 (1/10): 디자인 패턴이란 무엇인가?](./01-what-are-design-patterns.md)
- [Design Patterns 101 (2/10): Creational 패턴](./02-creational-patterns.md)
- **Structural 패턴 (현재 글)**
- Behavioral 패턴 (예정)
- Strategy 패턴 (예정)
- Adapter 패턴 (예정)
- Observer 패턴 (예정)
- Factory와 의존성 주입 (예정)
- 패턴을 남용하지 않는 법 (예정)
- Python에 어울리는 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Adapter Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/adapter)
- [Decorator Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/decorator)
- [Facade Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/facade)
- [Composite Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/composite)

### 실무 확장 읽을거리

- [The Python Tutorial — Classes (Python docs)](https://docs.python.org/3/tutorial/classes.html)

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: Computer Science, DesignPatterns, Structural, Adapter, Decorator, Facade
