---
series: computer-science-101
episode: 1
title: Computer Science란 무엇인가?
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
  - 컴퓨터과학
  - CS 입문
  - 전공 개요
  - 계산 이론
  - 추상화
seo_description: 컴퓨터과학이 무엇을 연구하고 주요 과목이 어떻게 연결되는지 큰 그림을 잡습니다.
last_reviewed: '2026-05-12'
---

# Computer Science란 무엇인가?

처음 컴퓨터과학을 접하면 프로그래밍 문법을 더 많이 아는 일이 곧 CS를 잘하는 일처럼 보이기 쉽습니다. 하지만 실무에서 오래 버티는 엔지니어를 가르는 기준은 언어 숙련도보다, 계산을 어떻게 모델링하고 추상화하며 한계를 어디까지 읽어 내는지에 더 가깝습니다.

이 글은 Computer Science 101 시리즈의 첫 번째 글입니다.

여기서는 컴퓨터과학이 정확히 무엇을 다루는지, 왜 추상화가 이 분야의 공용 언어인지, 그리고 이후 글들이 어떤 지도를 따라 연결되는지 큰 그림부터 잡겠습니다.

## 이 글에서 다룰 문제

- 컴퓨터과학은 프로그래밍과 어떻게 다르고, 정확히 무엇을 연구하는 학문일까요?
- 왜 추상화가 컴퓨터과학의 가장 중요한 도구로 반복해서 등장할까요?
- 알고리즘, 시스템, 응용 과목은 서로 어떤 계층 관계로 이어질까요?
- 같은 문제라도 CS 관점으로 보면 해법이 왜 달라질까요?
- 이 시리즈를 어떤 순서와 관점으로 읽어야 전체 그림이 선명해질까요?

> 컴퓨터과학은 컴퓨터를 쓰는 요령이 아니라 계산을 설계하는 학문입니다. 이 관점을 잡으면 언어와 프레임워크가 바뀌어도 핵심 판단 기준은 흔들리지 않습니다.

## 이 글에서 배울 것

- 컴퓨터과학의 정의와 핵심 질문
- 추상화가 왜 이 분야의 중심 도구인지
- 주요 전공 과목이 어떤 구조로 연결되는지
- 시리즈 전체를 읽는 학습 로드맵

## 왜 중요한가

프로그래밍 언어를 배우는 것과 컴퓨터과학을 배우는 것은 다릅니다. 프로그래밍은 도구를 사용하는 기술이고, 컴퓨터과학은 도구가 작동하는 원리를 이해하는 학문입니다. 원리를 알면 새로운 도구를 빠르게 익히고, 문제를 근본적으로 해결할 수 있습니다.

> CS = 계산의 원리, 한계, 그리고 응용을 연구하는 학문

이 시리즈는 CS 전공의 주요 과목들을 한 편씩 살펴보며 전체 그림을 그립니다.

## 한눈에 보는 개념

> 컴퓨터과학은 계산 이론, 시스템, 응용의 세 축으로 구성됩니다. 모든 과목은 "추상화"라는 공통 도구로 연결됩니다.

![한눈에 보는 개념](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/01/01-01-concept-at-a-glance.ko.png)
*컴퓨터과학의 주요 층이 이론에서 시스템과 응용으로 이어지는 구조*

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Computation | 정해진 규칙에 따라 입력을 출력으로 바꾸는 과정 |
| Abstraction | 세부 구현을 감추고 필요한 인터페이스만 드러내는 방식 |
| Algorithm | 문제를 해결하기 위한 유한한 절차 |
| Complexity | 알고리즘이 사용하는 시간과 공간의 증가율 |
| Turing machine | 무엇이 계산 가능한지 정의하는 이론 모델 |

## Before / After

**Before — CS를 모를 때:**

```python
# Compare every pair to find duplicates — O(n^2)
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
# Use a set for an O(n) solution
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
```

## 단계별로 따라하기

### 1단계: 계산이란 무엇인가

```python
# The simplest computation: input -> process -> output
def is_even(n: int) -> bool:
    """Return True if n is even."""
    return n % 2 == 0

print(is_even(4))   # True
print(is_even(7))   # False
```

계산의 본질은 "입력을 받아 규칙에 따라 출력을 만드는 것"입니다. 모든 프로그램은 이 구조를 따릅니다.

### 2단계: 추상화의 힘

```python
# Hide implementation details, expose only the interface
class Stack:
    """An abstract stack — internals stay hidden."""

    def __init__(self) -> None:
        self._items: list[int] = []

    def push(self, item: int) -> None:
        self._items.append(item)

    def pop(self) -> int:
        return self._items.pop()

    def is_empty(self) -> bool:
        return len(self._items) == 0

# Users do not need to know there is a list inside
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
    """Sequential search — O(n)."""
    for i, item in enumerate(items):
        if item == target:
            return i
    return -1

def binary_search(items: list[int], target: int) -> int:
    """Binary search — O(log n), requires sorted input."""
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
print(f"Linear search: {time.time() - start:.4f}s")

start = time.time()
binary_search(data, 999_999)
print(f"Binary search: {time.time() - start:.6f}s")
```

**Expected output:** `Linear search`가 `Binary search`보다 훨씬 오래 걸리고, 입력 크기가 커질수록 차이가 급격히 벌어집니다.

같은 문제를 푸는 두 알고리즘의 성능 차이는 데이터가 커질수록 극적으로 벌어집니다.

### 4단계: 계층 구조로 이해하는 CS

```python
# Express the layered relationship of CS subjects as a dictionary
cs_layers = {
    "Applications": ["AI", "Data science", "Web", "Mobile"],
    "Software": ["Software engineering", "Programming languages"],
    "Systems": ["Operating systems", "Networks", "Databases"],
    "Hardware": ["Computer architecture", "Digital logic"],
    "Theory": ["Algorithms", "Complexity theory", "Computation theory"],
}

for layer, subjects in cs_layers.items():
    print(f"[{layer}] {', '.join(subjects)}")
```

CS는 이론 → 하드웨어 → 시스템 → 소프트웨어 → 응용의 계층으로 구성됩니다. 아래 계층이 위 계층의 기반이 됩니다.

### 5단계: 이 시리즈의 로드맵

```python
roadmap = [
    (1, "What Is Computer Science?", "the whole picture"),
    (2, "Computation and Programs", "models of computation, paradigms"),
    (3, "Data Representation", "binary, encoding, types"),
    (4, "Algorithms and Complexity", "Big-O, sorting, searching"),
    (5, "Computer Architecture", "CPU, memory, instructions"),
    (6, "Operating Systems", "processes, memory, file systems"),
    (7, "Networks", "TCP/IP, HTTP, the internet"),
    (8, "Databases", "relational model, SQL, transactions"),
    (9, "Software Engineering", "design, testing, collaboration"),
    (10, "From CS to AI and Data Science", "ML, statistics, applications"),
]

for num, title, keywords in roadmap:
    print(f"  {num:02d}. {title} — {keywords}")
```

## 이 코드에서 먼저 봐야 할 점

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

시니어 엔지니어는 새로운 기술이 나와도 먼저 원리를 찾습니다. 컨테이너는 운영체제 개념의 응용이고, 서버리스는 분산 시스템 추상화의 변형이며, NoSQL 역시 데이터베이스 이론의 다른 선택지라는 식으로 읽습니다.

그래서 기술 선택 질문을 받으면 제품명보다 계산 모델, 데이터 흐름, 복잡도, 운영 경계를 먼저 설명합니다. 도구 이름은 바뀌어도 판단 기준이 남기 때문입니다.

## 체크리스트

- [ ] 컴퓨터과학의 정의를 자신의 말로 설명할 수 있는가
- [ ] 추상화가 CS에서 왜 중요한지 이해했는가
- [ ] CS 주요 과목들의 계층 관계를 파악했는가
- [ ] 알고리즘 효율성이 왜 중요한지 체감했는가
- [ ] 이 시리즈의 전체 로드맵을 확인했는가

## 연습 문제

1. 일상에서 쓰는 알고리즘 세 가지를 골라 입력, 처리 절차, 출력을 각각 적어 보세요.
2. 스마트폰 한 대 안에 들어 있는 CS 분야를 떠올려 보고 운영체제, 네트워크, 데이터 표현처럼 층별로 분류해 보세요.
3. `linear_search`와 `binary_search`를 직접 실행하고, 입력 크기를 10배씩 키우며 실행 시간 차이를 기록해 보세요.

## 정리 및 다음 단계

컴퓨터과학은 계산의 원리, 한계, 응용을 연구하는 학문입니다. 추상화를 핵심 도구로 사용하며, 이론부터 응용까지 계층 구조로 연결됩니다. 프로그래밍은 CS의 도구이지 CS 자체가 아닙니다.

다음 글에서는 CS의 가장 기본적인 질문인 "계산이란 무엇인가"를 더 깊이 살펴보고, 프로그래밍 패러다임의 발전을 추적합니다.

<!-- toc:begin -->
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
<!-- toc:end -->

## 참고 자료

- [CS50 — Introduction to Computer Science (Harvard)](https://cs50.harvard.edu/)
- [ACM/IEEE-CS/AAAI — Computing Curricula 2020](https://www.acm.org/binaries/content/assets/education/curricula-recommendations/cc2020.pdf)
- [Structure and Interpretation of Computer Programs (MIT)](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book.html)
- [Computer Science Distilled — Wladston Ferreira Filho](https://code.energy/computer-science-distilled/)

Tags: Computer Science, 컴퓨터과학, CS 입문, 전공 개요, 계산 이론, 추상화
