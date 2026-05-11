---
series: discrete-math-101
episode: 1
title: 이산수학이란 무엇인가?
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
  - 이산수학
  - 수학 입문
  - 전공 개요
  - 논리
  - 집합
seo_description: 이산수학이 무엇을 다루는 학문인지, 컴퓨터공학에서 왜 필수인지 전체 그림을 그립니다.
last_reviewed: '2026-05-04'
---

# 이산수학이란 무엇인가?

> Discrete Math 101 시리즈 (1/10)


## 이 글에서 다룰 문제

알고리즘을 분석하려면 점화식과 조합론이 필요합니다. 데이터베이스를 이해하려면 집합과 관계 이론이 필요합니다. 네트워크를 설계하려면 그래프 이론이 필요합니다. 이산수학은 단순한 수학 과목이 아니라 컴퓨터공학 전 분야의 공용어입니다.

> 이산수학 = 컴퓨터과학자가 생각을 정리하기 위해 사용하는 언어

이 시리즈는 이산수학의 핵심 개념을 한 편씩 살펴보며 컴퓨터공학과의 연결고리를 보여줍니다.

## 전체 흐름
> 이산수학은 논리, 집합, 함수, 조합, 그래프의 다섯 축으로 구성됩니다. 모든 영역은 "이산성(discreteness)"이라는 공통 성질로 연결됩니다.

```text
            논리 (명제, 증명)
                |
        집합 / 함수 / 관계
                |
        ┌───────┼───────┐
      조합론   수열      그래프
       (셈)   (점화식)   (구조)
        └───────┼───────┘
                |
        알고리즘 / 자료구조
                |
          컴퓨터과학 응용
```

## Before / After

**Before — 이산수학을 모를 때:**

```python
# "왜 이 알고리즘이 O(log n)인가?"라는 질문에 답하기 어렵습니다
def binary_search(data, target):
    low, high = 0, len(data) - 1
    while low <= high:
        mid = (low + high) // 2
        if data[mid] == target:
            return mid
        elif data[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```

**After — 이산수학을 알 때:**

```python
# 점화식 T(n) = T(n/2) + 1로 표현하고
# 마스터 정리로 O(log n)임을 증명할 수 있습니다
# 또한 정렬된 배열이라는 "전순서 관계"가 전제임을 인지합니다
def binary_search(data, target):
    """전제: data는 전순서(total order)로 정렬되어 있다.
    복잡도: T(n) = T(n/2) + O(1) ⟹ O(log n)
    """
    low, high = 0, len(data) - 1
    while low <= high:
        mid = (low + high) // 2
        if data[mid] == target:
            return mid
        elif data[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```

## 단계별로 따라하기

### 1단계: 이산과 연속의 차이

```python
# 연속: 실수 구간 [0, 1] 사이에는 무한히 많은 값이 존재
# 이산: 정수 집합 {0, 1, 2, 3}은 명확히 셀 수 있다
import math

continuous_sample = [i * 0.0001 for i in range(10001)]  # 근사일 뿐
discrete_set = list(range(11))  # 정확한 표현

print(f"연속 근사 개수: {len(continuous_sample)}")
print(f"이산 집합 크기: {len(discrete_set)}")
print(f"연속의 원소 사이 거리: {continuous_sample[1] - continuous_sample[0]}")
print(f"이산의 원소 사이 거리: {discrete_set[1] - discrete_set[0]}")
```

컴퓨터의 메모리는 비트 단위로 끊어져 있으므로 본질적으로 이산적입니다. 부동소수점은 실수를 "근사"할 뿐 진짜 연속이 아닙니다.

### 2단계: 명제와 진리값

```python
# 명제: 참 또는 거짓이 명확한 문장
def is_prime(n: int) -> bool:
    """n이 소수인지 판정합니다."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


# "7은 소수이다"는 참인 명제
# "9는 소수이다"는 거짓인 명제
print(f"7은 소수: {is_prime(7)}")  # True
print(f"9는 소수: {is_prime(9)}")  # False
```

명제 논리는 모든 컴퓨터 추론의 기초입니다. if 문, while 문, 데이터베이스 쿼리의 WHERE 절은 모두 명제의 참/거짓 평가입니다.

### 3단계: 집합 연산

```python
# 집합은 가장 기본적인 이산 구조입니다
A = {1, 2, 3, 4, 5}
B = {3, 4, 5, 6, 7}

print(f"합집합 A ∪ B: {A | B}")
print(f"교집합 A ∩ B: {A & B}")
print(f"차집합 A - B: {A - B}")
print(f"대칭차 A △ B: {A ^ B}")
print(f"부분집합 A ⊆ {A | B}: {A <= (A | B)}")
```

데이터베이스의 SQL JOIN은 집합 연산의 직접적 응용입니다. UNION, INTERSECT, EXCEPT 모두 위 연산과 일대일 대응됩니다.

### 4단계: 그래프로 관계 표현

```python
# 그래프는 정점(vertex)과 간선(edge)으로 구성됩니다
graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C", "E"],
    "E": ["D"],
}


def neighbors(g: dict, node: str) -> list:
    """주어진 정점의 이웃을 반환합니다."""
    return g.get(node, [])


for node in graph:
    print(f"{node}의 이웃: {neighbors(graph, node)}")
```

소셜 네트워크, 도로망, 의존성 트리, 인터넷 라우팅 — 컴퓨터과학에서 다루는 거의 모든 관계는 그래프로 모델링됩니다.

### 5단계: 이 시리즈의 로드맵

```python
roadmap = [
    (1, "이산수학이란 무엇인가?", "전체 그림"),
    (2, "명제와 논리", "진리값, 논리 연산, 추론"),
    (3, "집합과 함수", "집합 연산, 함수의 정의역과 치역"),
    (4, "관계와 동치관계", "관계의 성질, 동치류, 분할"),
    (5, "증명 방법", "직접·귀류·귀납"),
    (6, "수열과 점화식", "재귀적 정의, 마스터 정리"),
    (7, "조합과 경우의 수", "순열, 조합, 비둘기집"),
    (8, "그래프 이론 기초", "정점, 간선, 경로, 연결성"),
    (9, "트리와 그래프 탐색", "BFS, DFS, 신장 트리"),
    (10, "알고리즘과 이산수학의 연결", "복잡도, NP, 응용"),
]

for num, title, keywords in roadmap:
    print(f"  {num:02d}. {title} — {keywords}")
```

## 이 코드에서 주목할 점

- 이산 구조는 컴퓨터가 정확하게 표현할 수 있는 유일한 대상입니다
- 명제, 집합, 그래프는 서로 다른 추상화이지만 모두 "이산성"을 공유합니다
- 알고리즘 분석은 점화식과 조합론에 의존합니다
- 이산수학의 도구는 SQL, 라우팅, 의존성 관리 등 실무에 직접 적용됩니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 이산수학 = 추상 수학으로 회피 | 알고리즘 분석에서 막힙니다 | 코드와 함께 학습하면 직관적입니다 |
| 증명을 외우기만 함 | 새로운 문제에 적용 불가 | 증명의 구조와 동기를 이해합니다 |
| 그래프를 시각적으로만 이해 | 큰 그래프에서 한계 | 인접 리스트·행렬 표현에 익숙해집니다 |
| 조합과 순열 혼동 | 경우의 수 계산 오류 | 순서 유무로 구분합니다 |
| 명제와 술어 구분 못 함 | 형식 논리에서 막힙니다 | 양화사 ∀, ∃의 의미를 명확히 합니다 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스 쿼리 최적화 시 집합 이론과 관계대수 적용
- 의존성 관리 도구(npm, pip)는 그래프의 위상 정렬 사용
- 분산 시스템의 합의 알고리즘은 명제 논리와 일관성 증명
- 추천 시스템의 그래프 임베딩은 그래프 이론의 응용
- 컴파일러 최적화는 데이터 흐름 그래프 분석에 의존

## 체크리스트

- [ ] 이산과 연속의 차이를 자신의 말로 설명할 수 있는가
- [ ] 이산수학의 다섯 영역(논리·집합·함수·조합·그래프)을 나열할 수 있는가
- [ ] 컴퓨터과학에서 이산수학이 필요한 이유를 이해했는가
- [ ] SQL JOIN과 집합 연산의 대응을 파악했는가
- [ ] 이 시리즈의 전체 로드맵을 확인했는가

## 정리 및 다음 단계

이산수학은 셀 수 있는 대상을 다루는 수학이며, 컴퓨터과학의 공용어입니다. 논리·집합·함수·조합·그래프의 다섯 영역으로 구성되며, 각 영역은 알고리즘·데이터베이스·네트워크 등 실무 분야와 직결됩니다.

다음 글에서는 이산수학의 가장 기본 단위인 "명제"와 논리 연산을 자세히 살펴봅니다. 모든 추론의 출발점입니다.

<!-- toc:begin -->
- **이산수학이란 무엇인가? (현재 글)**
- 명제와 논리 (예정)
- 집합과 함수 (예정)
- 관계와 동치관계 (예정)
- 증명 방법 (예정)
- 수열과 점화식 (예정)
- 조합과 경우의 수 (예정)
- 그래프 이론 기초 (예정)
- 트리와 그래프 탐색 (예정)
- 알고리즘과 이산수학의 연결 (예정)
<!-- toc:end -->

## 참고 자료

- [Discrete Mathematics and Its Applications — Kenneth Rosen](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [MIT OCW — Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
- [Wikipedia — Discrete Mathematics](https://en.wikipedia.org/wiki/Discrete_mathematics)
- [Book of Proof — Richard Hammack](https://www.people.vcu.edu/~rhammack/BookOfProof/)
