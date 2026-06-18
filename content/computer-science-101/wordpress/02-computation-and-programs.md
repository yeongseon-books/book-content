---
series: computer-science-101
episode: 2
title: "바이브코딩을 위한 컴퓨터 과학 기초 (2/10): 계산과 프로그램"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Computer Science
  - 계산 모델
  - 튜링 기계
  - 프로그래밍 패러다임
  - AI 코딩
seo_description: 계산의 정의, 튜링 기계, 프로그래밍 패러다임을 바이브코딩 관점에서 이해합니다. AI에게 어떤 패러다임으로 코드를 요청할지 결정하는 기초입니다.
language: ko
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 컴퓨터 과학 기초 (2/10): 계산과 프로그램

> 이 글은 **바이브코딩을 위한 컴퓨터 과학 기초** 시리즈의 두 번째 글입니다. AI에게 코드를 시키려면 컴퓨터가 어떻게 동작하는지 기본은 알아야 합니다.

---

AI에게 "함수형으로 짜줘"라고 하면 어떤 코드가 나올지 예상할 수 있나요? "명령형으로 짜줘"는요? 패러다임을 모르면 AI가 내놓은 코드를 보고도 "이게 맞는 방향인지" 판단하기 어렵습니다.

"프로그램으로 풀 수 있는 문제"라는 말은 익숙하지만, 어디까지가 계산 가능한 범위인지 정확히 묻기 시작하면 이야기가 달라집니다. 계산 가능성의 경계와 코드를 조직하는 방식은 생각보다 가까이 붙어 있습니다.

여기서는 계산의 이론적 정의, 계산할 수 없는 문제, 그리고 프로그래밍 패러다임이 AI 코딩 요청에서 어떻게 쓰이는지 함께 봅니다.

> **바이브코딩 관점:** 패러다임을 알면 AI에게 "어떤 방식으로" 코드를 만들어달라고 구체적으로 요청할 수 있습니다. 명령형, 함수형, 객체지향 중 문제에 맞는 패러다임을 선택하는 것이 좋은 AI 코드를 받는 첫 번째 기술입니다.

---

## 이 글에서 다룰 문제

- 무엇을 두고 계산 가능하다고 말할 수 있을까요?
- 튜링 기계는 왜 오늘날의 컴퓨터를 설명하는 기준 모델로 남아 있을까요?
- 정지 문제처럼 원리적으로 풀 수 없는 문제는 AI에게도 풀 수 없는 것일까요?
- 명령형, 함수형, 객체지향 패러다임은 AI 코딩에서 어떻게 활용할까요?
- 바이브코더가 패러다임을 모를 때 어떤 문제가 생길까요?

---

## 핵심 개념 한 줄 정리

> **계산 이론 = CS의 헌법. 패러다임 = 코드를 조직하는 철학.**

계산은 입력을 규칙에 따라 변환하는 과정입니다. 튜링 기계는 이 과정의 가장 기본적인 모델이며, 프로그래밍 언어는 이를 인간이 읽을 수 있게 표현합니다.

| 용어 | 설명 |
| --- | --- |
| Turing machine | 계산 가능성을 정의하는 이론적 계산 모델 |
| Halting problem | 프로그램이 끝나는지 일반적으로 판정할 수 없는 문제 |
| Compiler | 소스 코드를 다른 저수준 코드로 번역하는 프로그램 |
| Interpreter | 소스 코드를 실행하면서 해석하는 프로그램 |
| Paradigm | 코드를 조직하는 방식과 사고 체계 |

---

## Before / After: 패러다임을 알기 전과 후

**Before — 패러다임을 모를 때:**

```python
# 모든 로직을 하나의 절차적 함수에 몰아넣은 형태
def process_orders(orders):
    total = 0
    for order in orders:
        if order["status"] == "paid":
            price = order["price"] * order["quantity"]
            if order["discount"]:
                price = price * 0.9
            total += price
    return total
```

AI에게 "주문 처리 함수 만들어줘"라고 하면 이런 코드가 나올 수 있습니다. 조건이 늘어날수록 함수가 비대해집니다.

**After — 패러다임을 알 때:**

```python
from dataclasses import dataclass

@dataclass
class Order:
    price: int
    quantity: int
    status: str
    discount: bool

    def total_price(self) -> int:
        base = self.price * self.quantity
        return int(base * 0.9) if self.discount else base

def process_orders(orders: list[Order]) -> int:
    return sum(o.total_price() for o in orders if o.status == "paid")
```

AI에게 "dataclass로 Order 모델을 만들고 함수형 스타일로 주문 처리 로직 짜줘"라고 요청하면 이런 코드를 받을 수 있습니다.

---

## 핵심 내용: 바이브코딩 관점에서 보는 계산과 패러다임

### 계산할 수 없는 문제가 있다

정지 문제는 CS의 가장 유명한 불가능성 결과입니다. 어떤 프로그램이 끝날지 끝나지 않을지를 자동으로 판정하는 프로그램은 원리적으로 존재할 수 없습니다. 이는 AI도 마찬가지입니다. AI가 코드를 생성해도 그 코드가 항상 올바르게 종료하는지 AI 스스로 보장할 수 없습니다.

```python
def halts(program, input_data):
    """이 함수는 구현할 수 없습니다."""
    raise NotImplementedError("The halting problem is undecidable")

# 실용적인 우회 방법: timeout 사용
import signal

def run_with_timeout(func, timeout_sec: int = 5):
    signal.alarm(timeout_sec)
    try:
        return func()
    except Exception:
        return None
```

### 세 가지 패러다임 비교

같은 문제를 세 가지 패러다임으로 풀어보면 AI에게 어떻게 요청할지 감이 잡힙니다.

```python
words = ["cat", "elephant", "dog", "butterfly", "ant", "whale"]

# 명령형: 어떻게(how) 하는지 단계별로 지시
result_imperative = []
for word in words:
    if len(word) >= 4:
        result_imperative.append(word.upper())
print(f"명령형: {result_imperative}")

# 함수형: 무엇을(what) 원하는지 선언
result_functional = list(map(str.upper, filter(lambda w: len(w) >= 4, words)))
print(f"함수형: {result_functional}")

# 리스트 내포 (Python 고유의 선언적 스타일)
result_comprehension = [w.upper() for w in words if len(w) >= 4]
print(f"내포식: {result_comprehension}")
```

| 패러다임 | 장점 | AI 요청 키워드 |
| --- | --- | --- |
| 명령형 | 실행 흐름이 명확, 디버깅 쉬움 | "단계별로", "반복문으로" |
| 함수형 | 부수효과 없음, 조합성 높음 | "함수형으로", "map/filter로" |
| 객체지향 | 상태와 행동을 캡슐화 | "클래스로", "OOP로" |

### 컴파일과 인터프리트

Python은 인터프리터 언어이지만 내부적으로 바이트코드로 컴파일됩니다. 이 사실이 AI 코드 성능 최적화와 연결됩니다.

```python
import dis

def add(a: int, b: int) -> int:
    return a + b

# Python bytecode 확인
dis.dis(add)
# LOAD_FAST    0 (a)
# LOAD_FAST    1 (b)
# BINARY_OP
# RETURN_VALUE
```

---

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 모든 문제가 AI로 풀린다고 가정 | 계산 불가능한 문제가 존재합니다 | 정지 문제와 계산 이론을 이해합니다 |
| AI에게 패러다임 지정 없이 요청 | 일관성 없는 코드가 나옵니다 | 명령형/함수형/OOP 중 선택해서 요청합니다 |
| 컴파일러와 인터프리터를 혼동 | 언어 특성을 잘못 이해합니다 | 실행 방식의 차이를 명확히 구분합니다 |
| 고급 언어만 사용하며 저수준을 무시 | AI 코드의 성능 문제를 이해 못함 | 기계어와 메모리 구조를 기본 수준에서 파악합니다 |
| 이론을 실무와 무관하다고 무시 | AI 코드의 근본적 한계를 모릅니다 | 이론이 실무에 미치는 영향을 파악합니다 |

---

## AI 코딩 팁

1. **패러다임을 명시하세요.** "함수형으로, 부수효과 없이, map과 filter 사용해서 짜줘"처럼 구체적으로 요청하면 원하는 스타일의 코드를 받을 수 있습니다.
2. **정지 문제를 인식하세요.** AI가 생성한 코드에 무한루프 가능성이 있는지 타임아웃을 걸지 직접 판단해야 합니다.
3. **바이트코드를 이해하면 성능을 물어볼 수 있습니다.** "이 코드를 더 효율적인 바이트코드를 생성하도록 최적화해줘"라는 요청이 가능해집니다.

---

## 체크리스트

- [ ] 튜링 기계의 개념을 설명할 수 있는가
- [ ] 정지 문제가 왜 풀 수 없는지 이해했는가
- [ ] 명령형, 함수형, 객체지향의 차이를 구분할 수 있는가
- [ ] 컴파일러와 인터프리터의 차이를 이해했는가
- [ ] AI에게 패러다임을 명시해서 코드를 요청해 봤는가

---

## 처음 질문으로 돌아가기

- **무엇을 두고 계산 가능하다고 말할 수 있을까요?**
  튜링 기계로 표현할 수 있는 알고리즘이 존재하면 계산 가능합니다. AI도 이 범위 안에서 동작합니다.

- **정지 문제처럼 원리적으로 풀 수 없는 문제는 AI에게도 풀 수 없나요?**
  그렇습니다. AI가 코드를 생성해도 그 코드가 항상 올바르게 종료하는지 AI가 보장할 수 없는 이유가 여기에 있습니다.

- **패러다임은 AI 코딩에서 어떻게 활용할까요?**
  문제의 성격에 맞는 패러다임을 AI 요청에 명시하면 더 깨끗하고 유지보수하기 쉬운 코드를 받을 수 있습니다.

---

## 정리

계산은 입력을 규칙에 따라 변환하는 과정이며, 튜링 기계가 그 이론적 모델입니다. 모든 문제가 계산으로 풀리는 것은 아닙니다. 프로그래밍 패러다임은 코드를 조직하는 철학이며, AI에게 코드를 요청할 때 패러다임을 명시하면 더 일관된 코드를 받을 수 있습니다.

다음 글에서는 컴퓨터가 데이터를 어떻게 표현하는지, 그리고 이것이 AI 코드의 버그와 어떻게 연결되는지 봅니다.

---

## 참고 자료

- [Alan Turing — On Computable Numbers (1936)](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf)
- [SICP — Structure and Interpretation of Computer Programs](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book.html)
- [Programming Paradigms for Dummies (Peter Van Roy)](https://www.info.ucl.ac.be/~pvr/VanRoyChapter.pdf)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 컴퓨터 과학 기초 (1/10): Computer Science란 무엇인가?
- **바이브코딩을 위한 컴퓨터 과학 기초 (2/10): 계산과 프로그램 (현재 글)**
- 바이브코딩을 위한 컴퓨터 과학 기초 (3/10): 데이터 표현
- 바이브코딩을 위한 컴퓨터 과학 기초 (4/10): 알고리즘과 복잡도
- 바이브코딩을 위한 컴퓨터 과학 기초 (5/10): 컴퓨터 구조
- 바이브코딩을 위한 컴퓨터 과학 기초 (6/10): 운영체제
- 바이브코딩을 위한 컴퓨터 과학 기초 (7/10): 네트워크
- 바이브코딩을 위한 컴퓨터 과학 기초 (8/10): 데이터베이스
- 바이브코딩을 위한 컴퓨터 과학 기초 (9/10): 소프트웨어 엔지니어링
- 바이브코딩을 위한 컴퓨터 과학 기초 (10/10): AI와 데이터사이언스까지의 연결
<!-- toc:end -->

Tags: 바이브코딩, Computer Science, 계산 모델, 튜링 기계, 프로그래밍 패러다임, AI 코딩
