---
series: discrete-math-101
episode: 10
title: 알고리즘과 이산수학의 연결
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
  - 알고리즘
  - 복잡도
  - NP
  - 응용
seo_description: 명제, 집합, 증명, 점화식, 조합, 그래프 — 지금까지 배운 이산수학 개념이 알고리즘 분석과 실무에 어떻게 연결되는지 정리합니다.
last_reviewed: '2026-05-04'
---

# 알고리즘과 이산수학의 연결

> Discrete Math 101 시리즈 (10/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 명제, 집합, 증명, 점화식, 조합, 그래프 — 지금까지 배운 이산수학 개념은 실제 알고리즘과 코드에서 어떻게 쓰일까요?

> 이산수학은 알고리즘의 언어입니다. 점화식은 시간 복잡도 분석에, 조합론은 경우의 수 계산에, 그래프 이론은 라우팅과 의존성 해석에, 증명 기법은 알고리즘의 정당성 검증에 사용됩니다. 이 마지막 글에서는 시리즈 전체를 알고리즘 관점으로 다시 묶고, P/NP 같은 한 단계 위 개념까지 짧게 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 시간 복잡도와 빅오 표기 — 점화식과 마스터 정리
- 알고리즘 정당성 — 귀납법과 루프 불변식
- P, NP, NP-완전의 직관
- 시리즈 전체를 알고리즘 도구상자로 재구성

## 왜 중요한가

이산수학을 따로 배우면 추상적이지만, 알고리즘과 묶으면 즉시 실무 도구가 됩니다. 면접, 시스템 설계, 성능 최적화의 언어는 모두 이 글에서 정리하는 개념 위에 쌓여 있습니다.

> 이산수학을 모르면 알고리즘은 마법처럼 보이고, 알면 추론의 결과로 보입니다.

## 개념 한눈에 보기

> 알고리즘 분석의 3대 축: (1) 정확성 = 증명, (2) 효율성 = 복잡도, (3) 자원 사용 = 공간/시간 트레이드오프.

```text
이산수학 도구          알고리즘 응용
명제·논리       →      단정문, 단위 테스트, 형식 검증
집합·함수       →      해시 집합, 인덱싱, 함수형 프로그래밍
관계·동치       →      Union-Find, 그래프 분류
증명 기법       →      알고리즘 정당성, 루프 불변식
점화식          →      시간 복잡도 분석 (T(n) = 2T(n/2) + n)
조합            →      경우의 수, 확률, 백트래킹
그래프          →      네트워크, 의존성, 최단 경로
트리·탐색       →      BFS·DFS·MST·정렬
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 빅오 O(f) | 최악 시간 복잡도 상한 |
| 마스터 정리 | 분할 정복 점화식의 일반 해법 |
| 루프 불변식 | 반복문이 유지하는 명제 |
| P | 다항 시간에 풀리는 문제 |
| NP | 다항 시간에 검증되는 문제 |

## Before / After

**Before — 측정만 하는 성능 분석:**

```python
import time

start = time.time()
result = my_algorithm(big_input)
print(f"걸린 시간: {time.time() - start}")  # 입력 크기를 바꿔야 비교 가능
```

**After — 분석으로 미리 예측:**

```python
def analyze(n: int) -> str:
    """T(n) = 2T(n/2) + n → 마스터 정리에 의해 O(n log n)."""
    return f"입력 크기 {n}일 때 약 {n * (n.bit_length() - 1)}회 비교 예상"


print(analyze(1024))
```

이론으로 예측한 뒤, 측정으로 검증하는 흐름이 시니어의 작업 방식입니다.

## 실습: 단계별로 따라하기

### 1단계: 점화식과 시간 복잡도

```python
def merge_sort(arr: list) -> list:
    """T(n) = 2T(n/2) + n → O(n log n) (마스터 정리)"""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)


def merge(a: list, b: list) -> list:
    result, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i]); i += 1
        else:
            result.append(b[j]); j += 1
    result.extend(a[i:]); result.extend(b[j:])
    return result


print(merge_sort([5, 2, 8, 1, 9, 3]))
```

마스터 정리: T(n) = aT(n/b) + f(n) 형태에서 a, b, f(n)의 관계로 즉시 복잡도를 결정.

### 2단계: 귀납법과 루프 불변식

```python
def sum_of_first_n(n: int) -> int:
    """반환값은 항상 1 + 2 + ... + n과 같다 — 귀납법으로 증명 가능."""
    total = 0
    for i in range(1, n + 1):
        # 루프 불변식: total == i*(i-1)/2 (반복 시작 시점 기준)
        total += i
    # 종료 시: total == n*(n+1)/2
    return total


assert sum_of_first_n(10) == 55
```

루프 불변식은 반복문이 유지하는 명제이며, 귀납법으로 증명합니다. 알고리즘이 정답을 내는 이유를 설명합니다.

### 3단계: 조합과 백트래킹

```python
def subsets(nums: list) -> list:
    """크기 n인 집합의 부분집합 — 2^n개."""
    result = [[]]
    for x in nums:
        result.extend([s + [x] for s in result])
    return result


def permutations(nums: list) -> list:
    """크기 n인 순열 — n!개. 백트래킹."""
    if not nums:
        return [[]]
    out = []
    for i, x in enumerate(nums):
        for rest in permutations(nums[:i] + nums[i + 1:]):
            out.append([x] + rest)
    return out


print(f"부분집합 수: {len(subsets([1, 2, 3]))}")
print(f"순열 수: {len(permutations([1, 2, 3]))}")
```

조합론으로 미리 경우의 수를 알면 무리한 알고리즘을 시도하지 않게 됩니다 — 입력이 20을 넘으면 순열 전체 탐색은 불가능하다는 즉각적 판단이 가능합니다.

### 4단계: 그래프 알고리즘과 응용

```python
from collections import defaultdict, deque


def topological_sort(graph: dict) -> list:
    """DAG의 위상 정렬 — Kahn 알고리즘 (BFS 기반)."""
    in_deg = defaultdict(int)
    for u in graph:
        for v in graph[u]:
            in_deg[v] += 1
    queue = deque([u for u in graph if in_deg[u] == 0])
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph[u]:
            in_deg[v] -= 1
            if in_deg[v] == 0:
                queue.append(v)
    return order


deps = {
    "compile": ["link"],
    "lex": ["parse"],
    "parse": ["compile"],
    "link": [],
}
print(f"빌드 순서: {topological_sort(deps)}")
```

위상 정렬은 의존성 해석의 핵심이며, 빌드 시스템·패키지 매니저·태스크 스케줄러의 기본 알고리즘입니다.

### 5단계: P, NP, NP-완전의 직관

```python
def subset_sum(nums: list, target: int) -> bool:
    """부분집합 합 문제 — NP-완전. n까지는 O(2^n) 완전 탐색."""
    n = len(nums)
    for mask in range(1 << n):
        s = sum(nums[i] for i in range(n) if mask & (1 << i))
        if s == target:
            return True
    return False


print(subset_sum([3, 7, 1, 8, 5], 13))
```

P = 다항 시간에 풀리는 문제. NP = 답을 받으면 다항 시간에 검증되는 문제. NP-완전 = NP에서 가장 어려운 부류. P = NP인지는 컴퓨터 과학 최대 미해결 문제입니다. 실무적으로는 "이 문제가 NP-완전이라면 완벽한 해 대신 근사·휴리스틱으로 우회한다"는 판단이 중요합니다.

## 이 코드에서 주목할 점

- 점화식은 알고리즘의 비용 모형이며, 마스터 정리는 분할 정복의 표준 분석 도구
- 귀납법은 단순 수학을 넘어 알고리즘 정당성 증명의 도구
- 조합론은 입력 크기에 대한 직관을 만드는 핵심
- NP-완전 판단은 "완벽한 해를 포기할 시점"을 알려주는 신호

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 평균/최악 혼동 | 빅오는 최악 상한 | 분포 모르면 최악 가정 |
| 마스터 정리 무리 적용 | 형식이 안 맞는 점화식 | 직접 전개나 트리 방법 사용 |
| 입력 크기 과소평가 | n=30이면 2^n도 가능 | 항상 n의 범위를 먼저 본다 |
| NP라서 불가능 단정 | 작은 n에서는 충분히 풀림 | 입력 크기와 시간 제약 함께 본다 |
| 정확성 증명 생략 | 코드는 동작하나 가끔 틀림 | 루프 불변식과 단위 테스트 병행 |

## 실무에서는 이렇게 쓰입니다

- 시스템 설계 면접 — 점화식과 빅오로 후보 알고리즘 비교
- 데이터 파이프라인 최적화 — 조인 순서를 그래프 탐색으로 결정
- 패키지 매니저·빌드 시스템 — 위상 정렬과 사이클 검출
- 추천·검색 — 그래프 임베딩과 행렬 분해
- 컴파일러 최적화 — 데이터 흐름 분석은 격자 이론과 그래프

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 코드를 쓰기 전에 입력 크기, 시간 복잡도, 메모리 한계를 먼저 추정합니다. 이는 측정이 아니라 이산수학으로 미리 추론하는 작업입니다. 또한 NP-완전을 만나면 즉시 근사 알고리즘이나 휴리스틱으로 전략을 바꿉니다 — "정답을 포기하는 결정"도 분석의 결과입니다.

## 체크리스트

- [ ] 빅오 표기와 점화식의 관계를 설명할 수 있다
- [ ] 마스터 정리의 적용 조건을 안다
- [ ] 루프 불변식으로 알고리즘 정당성을 검증할 수 있다
- [ ] P와 NP의 차이를 설명할 수 있다
- [ ] 시리즈 전체 개념을 알고리즘 도구로 매핑할 수 있다

## 연습 문제

1. T(n) = 3T(n/2) + n²의 시간 복잡도를 마스터 정리로 구하세요.

2. 이진 탐색의 정확성을 루프 불변식과 귀납법으로 증명하세요.

3. 자신의 프로젝트에서 NP-완전 또는 그에 준하는 어려운 문제를 하나 찾고, 어떻게 우회했는지(또는 우회할지) 설명하세요.

## 정리 및 다음 단계

이산수학은 알고리즘의 언어입니다. 명제·집합·증명·점화식·조합·그래프 — 모든 개념이 시간 복잡도, 정확성, 자료 구조 선택, 시스템 설계 결정에 직접 사용됩니다.

이 시리즈를 마쳤다면 다음 단계는 (1) 자료 구조와 알고리즘 시리즈로 깊이 들어가기, (2) 시스템 설계에서 이산수학 도구가 어떻게 결합되는지 관찰하기, (3) 실제 코드에서 점화식·증명·복잡도 분석을 습관화하기입니다.

<!-- toc:begin -->
- [이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- [명제와 논리](./02-propositions-and-logic.md)
- [집합과 함수](./03-sets-and-functions.md)
- [관계와 동치관계](./04-relations-and-equivalence.md)
- [증명 방법](./05-proof-techniques.md)
- [수열과 점화식](./06-sequences-and-recurrence.md)
- [조합과 경우의 수](./07-combinatorics.md)
- [그래프 이론 기초](./08-graph-theory-basics.md)
- [트리와 그래프 탐색](./09-trees-and-graph-traversal.md)
- **알고리즘과 이산수학의 연결 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Introduction to Algorithms — Cormen et al.](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Discrete Mathematics and Its Applications — Kenneth Rosen](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Wikipedia — Master Theorem](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Wikipedia — P versus NP problem](https://en.wikipedia.org/wiki/P_versus_NP_problem)
