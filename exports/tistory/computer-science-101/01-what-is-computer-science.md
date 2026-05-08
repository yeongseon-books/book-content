
# Computer Science란 무엇인가?

> Computer Science 101 시리즈 (1/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 컴퓨터과학은 "컴퓨터를 잘 쓰는 법"을 배우는 학문일까요?

> 컴퓨터과학은 컴퓨터 자체보다 "계산(computation)"을 연구하는 학문입니다. 어떤 문제를 계산으로 풀 수 있는지, 얼마나 효율적으로 풀 수 있는지, 그리고 그 과정을 어떻게 체계적으로 설계할 수 있는지를 다룹니다. 이 글에서는 컴퓨터과학의 정의, 핵심 질문, 그리고 전공 과목들이 서로 어떻게 연결되는지 전체 지도를 그립니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 컴퓨터과학의 정의와 핵심 연구 질문
- 추상화(abstraction)가 CS의 중심 도구인 이유
- 전공 과목 간의 연결 관계
- CS 학습의 전체 로드맵

## 왜 중요한가

프로그래밍 언어를 배우는 것과 컴퓨터과학을 배우는 것은 다릅니다. 프로그래밍은 도구를 사용하는 기술이고, 컴퓨터과학은 도구가 작동하는 원리를 이해하는 학문입니다. 원리를 알면 새로운 도구를 빠르게 익히고, 문제를 근본적으로 해결할 수 있습니다.

> CS = 계산의 원리, 한계, 그리고 응용을 연구하는 학문

이 시리즈는 CS 전공의 주요 과목들을 한 편씩 살펴보며 전체 그림을 그립니다.

## 개념 한눈에 보기

> 컴퓨터과학은 계산 이론, 시스템, 응용의 세 축으로 구성됩니다. 모든 과목은 "추상화"라는 공통 도구로 연결됩니다.

```text
         계산 이론
        /        \
  알고리즘    복잡도 이론
       \      /
      데이터 구조
          |
    ┌─────┼─────┐
  컴퓨터   OS   네트워크
  구조          |
    └─────┼─────┘
          |
     소프트웨어
     엔지니어링
          |
    AI / 데이터사이언스
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 계산(computation) | 입력을 규칙에 따라 처리하여 출력을 만드는 과정 |
| 추상화(abstraction) | 복잡한 시스템의 핵심만 남기고 세부를 숨기는 기법 |
| 알고리즘(algorithm) | 문제를 해결하는 단계별 절차 |
| 복잡도(complexity) | 알고리즘이 소비하는 시간과 공간의 양 |
| 튜링 기계(Turing machine) | 계산 가능성의 이론적 모델 |

## Before / After

**Before — CS를 모를 때:**

```python
# 모든 쌍을 비교하여 중복을 찾습니다 — O(n^2)
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates
```

**After — CS를 알 때:**

```python
# 집합을 활용하여 O(n)으로 해결합니다
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
```

## 실습: 단계별로 따라하기

### 1단계: 계산이란 무엇인가

```python
# 가장 단순한 계산: 입력 → 처리 → 출력
def is_even(n: int) -> bool:
    """n이 짝수인지 판별합니다."""
    return n % 2 == 0


print(is_even(4))   # True
print(is_even(7))   # False
```

계산의 본질은 "입력을 받아 규칙에 따라 출력을 만드는 것"입니다. 모든 프로그램은 이 구조를 따릅니다.

### 2단계: 추상화의 힘

```python
# 세부 구현을 숨기고 인터페이스만 노출합니다
class Stack:
    """스택 추상 자료형 — 내부 구현은 감춥니다."""

    def __init__(self) -> None:
        self._items: list[int] = []

    def push(self, item: int) -> None:
        self._items.append(item)

    def pop(self) -> int:
        return self._items.pop()

    def is_empty(self) -> bool:
        return len(self._items) == 0


# 사용자는 리스트를 몰라도 스택을 사용할 수 있습니다
stack = Stack()
stack.push(1)
stack.push(2)
print(stack.pop())  # 2
```

추상화는 CS의 가장 중요한 도구입니다. 운영체제는 하드웨어를, 프로그래밍 언어는 기계어를, 함수는 구현 세부를 추상화합니다.

### 3단계: 알고리즘과 효율성

```python
import time


def linear_search(items: list[int], target: int) -> int:
    """순차 탐색 — O(n)"""
    for i, item in enumerate(items):
        if item == target:
            return i
    return -1


def binary_search(items: list[int], target: int) -> int:
    """이진 탐색 — O(log n), 정렬된 리스트 필요"""
    low, high = 0, len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


data = list(range(1_000_000))

start = time.time()
linear_search(data, 999_999)
print(f"순차 탐색: {time.time() - start:.4f}초")

start = time.time()
binary_search(data, 999_999)
print(f"이진 탐색: {time.time() - start:.6f}초")
```

같은 문제를 푸는 두 알고리즘의 성능 차이는 데이터가 커질수록 극적으로 벌어집니다.

### 4단계: 계층 구조로 이해하는 CS

```python
# CS 과목들의 계층 관계를 딕셔너리로 표현합니다
cs_layers = {
    "응용": ["AI", "데이터사이언스", "웹", "모바일"],
    "소프트웨어": ["소프트웨어 엔지니어링", "프로그래밍 언어"],
    "시스템": ["운영체제", "네트워크", "데이터베이스"],
    "하드웨어": ["컴퓨터 구조", "디지털 논리"],
    "이론": ["알고리즘", "복잡도 이론", "계산 이론"],
}

for layer, subjects in cs_layers.items():
    print(f"[{layer}] {', '.join(subjects)}")
```

CS는 이론 → 하드웨어 → 시스템 → 소프트웨어 → 응용의 계층으로 구성됩니다. 아래 계층이 위 계층의 기반이 됩니다.

### 5단계: 이 시리즈의 로드맵

```python
roadmap = [
    (1, "Computer Science란 무엇인가?", "전체 그림"),
    (2, "계산과 프로그램", "계산 모델, 프로그래밍 패러다임"),
    (3, "데이터 표현", "이진수, 문자 인코딩, 자료형"),
    (4, "알고리즘과 복잡도", "Big-O, 정렬, 탐색"),
    (5, "컴퓨터 구조", "CPU, 메모리, 명령어"),
    (6, "운영체제", "프로세스, 메모리 관리, 파일 시스템"),
    (7, "네트워크", "TCP/IP, HTTP, 인터넷"),
    (8, "데이터베이스", "관계형 모델, SQL, 트랜잭션"),
    (9, "소프트웨어 엔지니어링", "설계, 테스트, 협업"),
    (10, "AI와 데이터사이언스까지의 연결", "ML, 통계, 응용"),
]

for num, title, keywords in roadmap:
    print(f"  {num:02d}. {title} — {keywords}")
```

## 이 코드에서 주목할 점

- 계산의 본질은 "입력 → 처리 → 출력"이라는 단순한 구조입니다
- 추상화를 통해 복잡한 시스템을 관리 가능한 단위로 분할합니다
- 알고리즘 선택에 따라 같은 문제의 성능이 극적으로 달라집니다
- CS의 모든 과목은 계층 구조로 연결되어 있습니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| CS = 프로그래밍이라고 생각 | 도구 사용과 원리 이해를 혼동합니다 | CS는 계산의 원리를 연구하는 학문입니다 |
| 이론 과목을 건너뜀 | 응용에서 벽에 부딪힙니다 | 알고리즘과 자료구조는 모든 과목의 기초입니다 |
| 한 과목만 깊이 파고듦 | 전체 그림을 놓칩니다 | 먼저 넓게 보고 필요한 곳을 깊이 학습합니다 |
| 수학을 완전히 회피 | 이론 이해에 한계가 생깁니다 | 이산수학과 확률은 CS의 필수 도구입니다 |
| 실습 없이 이론만 학습 | 이해가 피상적입니다 | 코드로 구현하며 개념을 확인합니다 |

## 실무에서는 이렇게 쓰입니다

- 시스템 설계 면접에서 CS 기초가 핵심 평가 항목으로 등장
- 대규모 데이터 처리 시 알고리즘 복잡도 분석이 성능 결정
- 운영체제 개념이 컨테이너(Docker)와 클라우드 인프라의 기반
- 네트워크 이해가 분산 시스템과 마이크로서비스 설계에 필수
- 데이터베이스 이론이 스키마 설계와 쿼리 최적화에 직결

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 새로운 기술이 등장해도 당황하지 않습니다. 기술은 바뀌지만 CS의 기본 원리는 변하지 않기 때문입니다. 컨테이너는 운영체제 개념의 응용이고, NoSQL은 데이터베이스 이론의 변형이며, 서버리스는 분산 시스템의 새로운 추상화입니다.

CS 기초가 탄탄한 엔지니어는 문제를 근본적으로 이해하고, 적절한 추상화 수준에서 해결책을 설계합니다. "왜 이 기술을 선택했는가"라는 질문에 원리에 기반한 답을 할 수 있습니다.

## 체크리스트

- [ ] 컴퓨터과학의 정의를 자신의 말로 설명할 수 있는가
- [ ] 추상화가 CS에서 왜 중요한지 이해했는가
- [ ] CS 주요 과목들의 계층 관계를 파악했는가
- [ ] 알고리즘 효율성이 왜 중요한지 체감했는가
- [ ] 이 시리즈의 전체 로드맵을 확인했는가

## 연습 문제

1. 일상생활에서 "알고리즘"에 해당하는 예시를 3가지 찾아보세요. 각각의 입력, 처리 과정, 출력을 정리합니다.

2. 스마트폰 하나에 CS의 어떤 분야들이 적용되어 있는지 목록을 작성하세요. (예: 운영체제 → iOS/Android)

3. `linear_search`와 `binary_search`를 직접 실행하고, 데이터 크기를 10배씩 늘리며 실행 시간 차이를 측정하세요.

## 정리 및 다음 단계

컴퓨터과학은 계산의 원리, 한계, 응용을 연구하는 학문입니다. 추상화를 핵심 도구로 사용하며, 이론부터 응용까지 계층 구조로 연결됩니다. 프로그래밍은 CS의 도구이지 CS 자체가 아닙니다.

다음 글에서는 CS의 가장 기본적인 질문인 "계산이란 무엇인가"를 더 깊이 살펴보고, 프로그래밍 패러다임의 발전을 추적합니다.

- **Computer Science란 무엇인가? (현재 글)**
- [계산과 프로그램](./02-computation-and-programs.md)
- [데이터 표현](./03-data-representation.md)
- [알고리즘과 복잡도](./04-algorithms-and-complexity.md)
- [컴퓨터 구조](./05-computer-architecture.md)
- [운영체제](./06-operating-systems.md)
- [네트워크](./07-networks.md)
- [데이터베이스](./08-databases.md)
- [소프트웨어 엔지니어링](./09-software-engineering.md)
- [AI와 데이터사이언스까지의 연결](./10-ai-and-data-science.md)
## 참고 자료

- [CS50 — Introduction to Computer Science (Harvard)](https://cs50.harvard.edu/)
- [Wikipedia — Computer Science](https://en.wikipedia.org/wiki/Computer_science)
- [Structure and Interpretation of Computer Programs (MIT)](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book.html)
- [Computer Science Distilled — Wladston Ferreira Filho](https://code.energy/computer-science-distilled/)

Tags: Computer Science, 컴퓨터과학, CS 입문, 전공 개요, 계산 이론, 추상화

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
