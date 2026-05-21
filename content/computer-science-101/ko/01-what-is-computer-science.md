---
series: computer-science-101
episode: 1
title: "Computer Science 101 (1/10): Computer Science란 무엇인가?"
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

# Computer Science 101 (1/10): Computer Science란 무엇인가?

처음 컴퓨터과학을 접하면 프로그래밍 문법을 더 많이 아는 일이 곧 CS를 잘하는 일처럼 보이기 쉽습니다. 하지만 실무에서 오래 버티는 엔지니어를 가르는 기준은 언어 숙련도보다, 계산을 어떻게 모델링하고 추상화하며 한계를 어디까지 읽어 내는지에 더 가깝습니다.

이 글은 Computer Science 101 시리즈의 첫 번째 글입니다.

여기서는 컴퓨터과학이 정확히 무엇을 다루는지, 왜 추상화가 이 분야의 공용 언어인지, 그리고 이후 글들이 어떤 지도를 따라 연결되는지 큰 그림부터 잡겠습니다.


![Computer Science 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/01/01-01-concept-at-a-glance.ko.png)
*Computer Science 101 1장 흐름 개요*

## 먼저 던지는 질문

- 컴퓨터과학은 프로그래밍과 어떻게 다르고, 정확히 무엇을 연구하는 학문일까요?
- 왜 추상화가 컴퓨터과학의 가장 중요한 도구로 반복해서 등장할까요?
- 알고리즘, 시스템, 응용 과목은 서로 어떤 계층 관계로 이어질까요?

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

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Computation | 정해진 규칙에 따라 입력을 출력으로 바꾸는 과정 |
| Abstraction | 세부 구현을 감추고 필요한 인터페이스만 드러내는 방식 |
| Algorithm | 문제를 해결하기 위한 유한한 절차 |
| Complexity | 알고리즘이 사용하는 시간과 공간의 증가율 |
| Turing machine | 무엇이 계산 가능한지 정의하는 이론 모델 |

## 적용 전후 비교
**Before — CS를 모를 때:**

```python
# 모든 쌍을 비교해 중복 찾기 — O(n^2)
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
# set을 사용해 O(n)으로 해결
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
# 가장 단순한 계산: input -> process -> output
def is_even(n: int) -> bool:
    """Return True if n is even."""
    return n % 2 == 0

print(is_even(4))   # True
print(is_even(7))   # False
```

계산의 본질은 "입력을 받아 규칙에 따라 출력을 만드는 것"입니다. 모든 프로그램은 이 구조를 따릅니다.

### 2단계: 추상화의 힘

```python
# 구현 세부사항은 숨기고 interface만 노출
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

# 사용자는 내부에 list가 있는지 알 필요 없음
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
# CS 주제의 계층 관계를 dictionary로 표현
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

## 추상화 계층을 실제 시스템에서 따라가기

추상화가 CS의 핵심 도구라는 이야기를 했습니다. 이를 실제 시스템에서 한 번 따라가 보겠습니다. 여러분이 웹 브라우저에서 버튼을 클릭하는 순간부터, 그 이벤트가 서버까지 도달하는 과정을 추상화 층별로 나누면 다음과 같습니다.

| 계층 | 하는 일 | 아래 계층에서 받는 서비스 |
| --- | --- | --- |
| 애플리케이션 | 사용자 입력 처리, UI 업데이트 | HTTP 요청/응답 |
| 프레임워크 | 라우팅, 상태 관리, 렌더링 | DOM API, fetch API |
| 런타임 | JavaScript 실행, 이벤트 루프 | OS 시스템 콜 |
| 운영체제 | 프로세스 관리, 소켓 통신 | 하드웨어 드라이버 |
| 네트워크 스택 | TCP/IP 패킷 전송 | NIC(네트워크 카드) |
| 하드웨어 | 전기 신호 전달 | 물리 매체(구리선, 광섬유) |

각 계층은 아래 계층의 세부 사항을 모릅니다. JavaScript 코드는 패킷이 어떻게 전송되는지 알 필요 없고, OS는 애플리케이션이 무슨 비즈니스 로직을 수행하는지 관심 없습니다. 이 분리 덕분에 각 계층을 독립적으로 개선하거나 교체할 수 있습니다.

### 추상화가 깨지는 순간

추상화는 만능이 아닙니다. Joel Spolsky가 말한 "Leaky Abstractions" â 추상화가 새는 순간 â 은 운영에서 반드시 만나게 됩니다. 대표적인 예시를 보겠습니다.

```python
# 추상화가 새는 예: ORM이 감춘 SQL의 비용
# Django ORM에서 간단해 보이는 쿼리가
# 실제로는 3중 JOIN을 생성할 수 있습니다

import sqlite3

conn = sqlite3.connect(":memory:")
cur = conn.cursor()
cur.execute("CREATE TABLE posts (id INTEGER PRIMARY KEY, author_id INTEGER, title TEXT)")
cur.execute("CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT)")
cur.execute("CREATE TABLE followers (id INTEGER PRIMARY KEY, target_id INTEGER)")

# 인덱스 없이 조인하면 풀 스캔이 발생합니다
for row in cur.execute(
    "EXPLAIN QUERY PLAN SELECT p.title FROM posts p JOIN authors a ON p.author_id = a.id"
):
    print(row)
# 추상화를 믿되, EXPLAIN으로 검증합니다
```

이 예시가 보여주는 교훈은 명확합니다. ORM은 SQL을 추상화하지만, 그 추상화 아래의 실행 비용은 여전히 존재합니다. 추상화를 사용하되, 성능 문제가 생기면 한 단계 아래를 들여다볼 준비가 되어 있어야 합니다.

### 추상화 수준을 오가는 사고 훈련

CS를 잘하는 사람은 하나의 계층에만 머물지 않습니다. 문제가 생기면 아래 계층으로 내려가 원인을 찾고, 해결한 뒤 다시 올라와 인터페이스를 정리합니다. 이 능력을 키우는 가장 좋은 방법은 같은 문제를 여러 추상화 수준에서 표현해 보는 것입니다.

```python
# 같은 "정렬" 작업을 세 가지 추상화 수준으로 표현

# 수준 1: 가장 높은 추상화 - 한 줄
data = [5, 2, 8, 1, 9, 3]
result = sorted(data)
print(f"수준 1 (내장 함수): {result}")

# 수준 2: 알고리즘 수준 - 삽입 정렬 직접 구현
def insertion_sort(arr: list[int]) -> list[int]:
    arr = arr[:]
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

print(f"수준 2 (알고리즘):  {insertion_sort(data)}")

# 수준 3: 비교 연산 수준 - 비교 횟수를 세며 정렬
def counted_sort(arr: list[int]) -> tuple[list[int], int]:
    arr = arr[:]
    comparisons = 0
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            else:
                break
        arr[j + 1] = key
    return arr, comparisons

sorted_data, count = counted_sort(data)
print(f"수준 3 (비교 추적): {sorted_data}, 비교 {count}회")
```

수준 1은 "무엇을" 하는지만 말합니다. 수준 2는 "어떻게" 하는지를 보여줍니다. 수준 3은 "얼마나 비싼지"를 측정합니다. CS 전공 과목은 이 세 수준을 자유롭게 오가는 능력을 기릅니다.

## 진수 변환으로 보는 계산의 본질

컴퓨터과학이 "계산"을 연구한다고 했습니다. 가장 기본적인 계산 예시로 진수 변환을 살펴보겠습니다. 이 과정은 단순하지만, 입력을 규칙에 따라 출력으로 바꾸는 계산의 본질을 그대로 보여줍니다.

```python
# 10진수를 임의 진법으로 변환하는 범용 함수
def convert_base(n: int, base: int) -> str:
    if n == 0:
        return "0"
    digits = "0123456789ABCDEF"
    result = []
    while n > 0:
        result.append(digits[n % base])
        n //= base
    return "".join(reversed(result))

# 변환 예시 테이블
print(f"{'10진수':>8} {'2진수':>12} {'8진수':>8} {'16진수':>6}")
print("-" * 40)
for num in [0, 7, 10, 15, 16, 42, 127, 255, 256, 1024]:
    print(f"{num:>8} {convert_base(num, 2):>12} {convert_base(num, 8):>8} {convert_base(num, 16):>6}")
```

이 함수는 단 10줄이지만, CS의 핵심 아이디어 여러 가지를 담고 있습니다.

| 관찰 포인트 | CS 개념 |
| --- | --- |
| `n % base`로 나머지를 구한다 | 나눗셈 알고리즘 - 모든 진법 변환의 기초 |
| `while n > 0` 반복 | 종료 조건이 보장된 유한 루프 - 알고리즘의 정의 |
| `reversed(result)` | 스택 구조 - 마지막에 넣은 것을 먼저 꺼냄 |
| `digits` 테이블 참조 | 룩업 테이블 - 조건문 대신 데이터로 분기 |

### 16진수와 실무

16진수는 프로그래밍에서 매우 자주 등장합니다. 색상 코드(`#FF5733`), 메모리 주소(`0x7fff5fbff8ac`), 네트워크 MAC 주소(`AA:BB:CC:DD:EE:FF`), UUID 모두 16진수를 사용합니다.

```python
# 16진수가 실무에서 쓰이는 예시
color = 0xFF5733
r = (color >> 16) & 0xFF   # 상위 8비트
g = (color >> 8) & 0xFF    # 중간 8비트
b = color & 0xFF           # 하위 8비트
print(f"RGB({r}, {g}, {b})")  # RGB(255, 87, 51)

# 메모리 주소 출력
data = [1, 2, 3]
print(f"리스트 객체의 id: {hex(id(data))}")

# 바이트열을 16진수로 표시
message = "Hello".encode("utf-8")
hex_dump = " ".join(f"{byte:02X}" for byte in message)
print(f"Hello의 16진 덤프: {hex_dump}")
```

## CS 과목 간 의존 관계 상세

시리즈의 각 과목이 단독으로 존재하는 것이 아니라 서로 의존한다고 했습니다. 이 의존 관계를 좀 더 구체적으로 보겠습니다.

| 선행 과목 | 후행 과목 | 연결 고리 |
| --- | --- | --- |
| 데이터 표현 | 알고리즘 | 정수/실수 표현이 정렬/비교 연산의 기초 |
| 데이터 표현 | 네트워크 | 바이트 순서(엔디안), 직렬화 형식 |
| 알고리즘 | 데이터베이스 | B-Tree 인덱스, 해시 조인, 정렬 병합 |
| 알고리즘 | 운영체제 | 스케줄링 알고리즘, 페이지 교체 정책 |
| 컴퓨터 구조 | 운영체제 | 인터럽트, 가상 메모리, 캐시 일관성 |
| 운영체제 | 네트워크 | 소켓 API, 파일 디스크립터, epoll |
| 네트워크 | 데이터베이스 | 클라이언트-서버 프로토콜, 복제 |
| 데이터베이스 | 소프트웨어 엔지니어링 | 마이그레이션, 스키마 설계, 테스트 |
| 소프트웨어 엔지니어링 | AI/DS | MLOps, 실험 재현성, 코드 품질 |

이 표가 말해주는 핵심은 하나입니다. **어느 하나를 건너뛰면 나중에 반드시 돌아오게 됩니다.** 네트워크를 이해하려면 운영체제의 소켓이 필요하고, 소켓을 이해하려면 파일 디스크립터가 필요합니다. 데이터베이스 인덱스를 이해하려면 B-Tree 자료구조가 필요합니다.

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


## 학습 설계 지도: 이 글을 커리큘럼에 연결하기

컴퓨터 과학 입문을 빠르게 끝내는 접근보다, 서로 연결된 개념을 축적하는 접근이 이후 학습 효율을 높입니다. 이 글의 핵심 개념은 단독 지식이 아니라 운영체제, 네트워크, 데이터베이스, 소프트웨어 공학으로 이어지는 선행 지식입니다. 따라서 한 주 단위 학습에서 이 글을 기준점으로 삼고, 다음과 같은 연결 훈련을 함께 수행하는 것이 좋습니다.

| 학습 축 | 이 글에서 확인할 포인트 | 다음 과목 연결 |
| --- | --- | --- |
| 계산 모델 | 입력, 상태, 출력의 관계를 명확히 정의 | 알고리즘 설계, 분산 시스템 모델링 |
| 추상화 | 세부 구현을 숨기고 인터페이스를 구분 | API 설계, 모듈 경계 설계 |
| 자원 제약 | 시간·메모리·I/O 비용을 동시에 고려 | 성능 튜닝, 인프라 비용 최적화 |
| 검증 가능성 | 주장 대신 측정과 반례로 판단 | 테스트 전략, 실험 설계 |

연결 학습을 할 때는 "개념 정의 1회 + 사례 적용 2회 + 반례 점검 1회" 구조를 반복합니다. 예를 들어 시간 복잡도를 배웠다면, 단순히 O 표기법을 외우지 않고 입력 크기 변화에 따른 실행 시간 그래프를 직접 기록합니다. 그래프가 기대와 다를 때 원인을 추정하고, 캐시 지역성이나 상수항의 영향을 설명해 보는 과정이 필요합니다. 이 연습이 쌓이면 글에서 다룬 개념이 시험 대비 지식이 아니라 실무 의사결정 기준으로 바뀝니다.

또한 과목 간 언어를 통일해 두는 것이 중요합니다. 같은 현상을 운영체제에서는 스케줄링, 네트워크에서는 큐잉, 데이터베이스에서는 트랜잭션 대기라고 부를 수 있습니다. 이름은 달라도 "경합 상태에서 자원을 배분한다"는 본질은 동일합니다. 학습 노트에 용어 사전을 만들어 개념 동치 관계를 표시해 두면, 새로운 분야를 배울 때 기존 이해를 재사용하기 쉬워집니다.

마지막으로 주간 복습은 요약보다 질문 중심으로 구성합니다. "왜 이 추상화가 필요한가", "어떤 조건에서 깨지는가", "대안의 비용은 무엇인가"를 각각 한 문장으로 답하면 학습 깊이가 빠르게 올라갑니다. 이렇게 축적한 질문-답변 세트는 면접, 설계 리뷰, 코드 리뷰에서 그대로 활용 가능한 사고 프레임이 됩니다.

추가로 이 글은 분야 지형도를 잡는 출발점이므로, 수학적 사고(논리·이산수학)와 시스템 사고(추상화 계층)를 병행해 학습해야 균형이 맞습니다.


## 처음 질문으로 돌아가기

- **컴퓨터과학은 프로그래밍과 어떻게 다르고, 정확히 무엇을 연구하는 학문일까요?**
  - 프로그래밍은 도구를 사용하는 기술이고, 컴퓨터과학은 그 도구가 작동하는 원리를 연구하는 학문입니다. CS는 "계산의 원리, 한계, 응용"을 다루며, 무엇이 계산 가능한지(이론), 어떻게 효율적으로 계산하는지(알고리즘), 어떤 구조 위에서 실행하는지(시스템)를 포함합니다.
- **왜 추상화가 컴퓨터과학의 가장 중요한 도구로 반복해서 등장할까요?**
  - 복잡한 시스템을 한 번에 이해하는 것은 불가능합니다. 추상화는 각 계층이 아래 계층의 세부를 숨기고 인터페이스만 드러내는 방식으로, 인간이 유한한 인지 능력으로도 거대한 시스템을 설계하고 운영할 수 있게 합니다. Stack 예제에서 내부 list를 감춘 것처럼, OS는 하드웨어를, 프레임워크는 OS를, 애플리케이션은 프레임워크를 추상화합니다.
- **알고리즘, 시스템, 응용 과목은 서로 어떤 계층 관계로 이어질까요?**
  - 이론(알고리즘, 복잡도)이 기초를 제공하고, 시스템(하드웨어, OS, 네트워크, DB)이 실행 환경을 만들며, 응용(AI, 웹, 모바일)이 사용자에게 가치를 전달합니다. 아래 계층의 제약을 알아야 위 계층의 설계가 현실적이 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- **Computer Science란 무엇인가? (현재 글)**
- 계산과 프로그램 (예정)
- 데이터 표현 (예정)
- 알고리즘과 복잡도 (예정)
- 컴퓨터 구조 (예정)
- 운영체제 (예정)
- 네트워크 (예정)
- 데이터베이스 (예정)
- 소프트웨어 엔지니어링 (예정)
- AI와 데이터사이언스까지의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [CS50 — Introduction to Computer Science (Harvard)](https://cs50.harvard.edu/)
- [ACM/IEEE-CS/AAAI — Computing Curricula 2020](https://www.acm.org/binaries/content/assets/education/curricula-recommendations/cc2020.pdf)
- [Structure and Interpretation of Computer Programs (MIT)](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book.html)
- [Computer Science Distilled — Wladston Ferreira Filho](https://code.energy/computer-science-distilled/)

Tags: Computer Science, 컴퓨터과학, CS 입문, 전공 개요, 계산 이론, 추상화
