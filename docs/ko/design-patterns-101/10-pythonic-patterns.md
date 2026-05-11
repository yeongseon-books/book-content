---
series: design-patterns-101
episode: 10
title: Python에 어울리는 패턴
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - DesignPatterns
  - Python
  - Idioms
  - Protocols
  - Decorators
seo_description: 모듈, 일급 함수, Protocol, 데코레이터로 GoF 패턴을 다시 푸는 Pythonic 패턴 — Python다운 설계 사고를 정리합니다.
last_reviewed: '2026-05-04'
---

# Python에 어울리는 패턴

> Design Patterns 101 시리즈 (10/10)


## 이 글에서 다룰 문제

Python의 기본 도구 — 모듈, 함수, Protocol — 가 이미 많은 패턴의 *런타임 지원*입니다. 같은 문제를 *더 적은 코드*로 풀 수 있습니다.

> 언어가 주는 도구를 먼저 본 다음, 그래도 부족하면 패턴을 꺼낸다.

## 전체 흐름
```mermaid
flowchart LR
    GoF["GoF 형식"] --> Trans["Pythonic 변환"]
    Trans --> Mod["모듈 = Singleton"]
    Trans --> Fn["함수 = Strategy / Command"]
    Trans --> Proto["Protocol = 인터페이스"]
    Trans --> Deco["@decorator = Decorator"]
    Trans --> DC["@dataclass = Value Object"]
```

같은 패턴, 더 가벼운 표현.

## Before/After

**Before (GoF 그대로)**

```python
class SingletonConfig:
    _inst = None
    def __new__(cls):
        if cls._inst is None:
            cls._inst = super().__new__(cls)
        return cls._inst
```

**After (Pythonic)**

```python
# config.py
DEBUG = True
DB_URL = "postgres://..."
# 어디서든 from config import DEBUG, DB_URL
```

모듈이 이미 Singleton입니다.

## Pythonic 패턴 5단계

### 1단계 — 모듈 = Singleton

```python
# 1_module_singleton.py
# settings.py
import os
ENV = os.getenv("ENV", "dev")
SECRET = os.getenv("SECRET", "x")
```

import 하면 어디서나 같은 값.

### 2단계 — 함수 = Strategy / Command

```python
# 2_function_strategy.py
def asc(d): return sorted(d)
def desc(d): return sorted(d, reverse=True)

def run(strategy, data): return strategy(data)
print(run(desc, [3, 1, 2]))
```

클래스 없이도 충분히 명료합니다.

### 3단계 — Protocol = 인터페이스

```python
# 3_protocol.py
from typing import Protocol

class Mailer(Protocol):
    def send(self, to: str, body: str) -> None: ...

class SmtpMailer:
    def send(self, to, body): ...   # ABC 상속 없이 만족
```

덕 타이핑 + 정적 검사의 균형.

### 4단계 — `@dataclass` = Value Object

```python
# 4_dataclass.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str
```

동등성, 표현, 불변성이 한 줄로.

### 5단계 — 데코레이터 = Decorator 패턴

```python
# 5_decorator.py
import time, functools

def timed(fn):
    @functools.wraps(fn)
    def wrap(*a, **k):
        t = time.time()
        try: return fn(*a, **k)
        finally: print(fn.__name__, time.time()-t)
    return wrap

@timed
def work(): time.sleep(0.1)
```

`@`로 자연스럽게 책임을 *덧씌웁니다*.

## 이 코드에서 주목할 점

- 클래스 계층이 거의 없습니다.
- 표준 도구만으로 패턴이 *드러납니다*.
- 같은 의도를 더 *적은 줄* 로 표현.

## 자주 하는 실수 5가지

1. **자바식 GoF를 그대로 이식.** Python에 어울리지 않는 무게.
2. **모듈 대신 Singleton 클래스.** 두 번째 인스턴스가 가능해 위험.
3. **ABC 강요.** Protocol이면 충분한 경우가 많다.
4. **데코레이터 남용으로 호출 흐름 불명확.** `functools.wraps` 누락도 흔함.
5. **dataclass 대신 손-말이 클래스.** `__eq__`/`__repr__` 빠진 채 사용.

## 실무에서는 이렇게 쓰입니다

`logging` = 모듈 Singleton, `sorted(key=...)` = 함수 Strategy, `typing.Protocol` = 인터페이스, `@app.route(...)` = Decorator. 표준 라이브러리와 인기 프레임워크가 이미 Pythonic 패턴을 *살아 있는 예제* 로 보여 줍니다.

## 체크리스트

- [ ] 모듈로 풀 수 있는 자리에 Singleton을 만들지 않았는가?
- [ ] 함수로 풀 수 있는 자리에 Strategy 클래스를 만들지 않았는가?
- [ ] Protocol로 충분한 자리에 ABC를 강요하지 않았는가?
- [ ] 값 객체에 dataclass를 썼는가?
- [ ] 데코레이터에 `functools.wraps`를 빠뜨리지 않았는가?

## 정리 및 다음 단계

GoF는 *어휘집*이지 *교본*이 아닙니다. Python의 도구를 먼저 보고, 부족한 곳에서만 패턴 이름을 꺼내 쓰세요. 디자인 패턴 101 시리즈는 여기서 마칩니다 — 도구가 아니라 *생각의 단위*로 이 어휘들을 사용하시기 바랍니다.

<!-- toc:begin -->
- [디자인 패턴이란 무엇인가?](./01-what-are-design-patterns.md)
- [Creational 패턴](./02-creational-patterns.md)
- [Structural 패턴](./03-structural-patterns.md)
- [Behavioral 패턴](./04-behavioral-patterns.md)
- [Strategy 패턴](./05-strategy-pattern.md)
- [Adapter 패턴](./06-adapter-pattern.md)
- [Observer 패턴](./07-observer-pattern.md)
- [Factory와 의존성 주입](./08-factory-and-di.md)
- [패턴을 남용하지 않는 법](./09-avoiding-pattern-overuse.md)
- **Python에 어울리는 패턴 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)
- [dataclasses (Python docs)](https://docs.python.org/3/library/dataclasses.html)
- [functools.wraps (Python docs)](https://docs.python.org/3/library/functools.html#functools.wraps)
- [Python 3 Patterns, Recipes and Idioms (Bruce Eckel)](https://python-3-patterns-idioms-test.readthedocs.io/)
