---
series: algorithms-101
episode: 10
title: "Algorithms 101 (10/10): 알고리즘 문제 풀이 전략"
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
  - 알고리즘
  - 문제 풀이
  - 패턴 인식
  - 면접
  - 연습
seo_description: 알고리즘 문제를 읽고 제약을 해석하고 도구를 고르는 다섯 단계 사고 절차를 정리합니다.
last_reviewed: '2026-05-12'
---

# Algorithms 101 (10/10): 알고리즘 문제 풀이 전략

이 글은 Algorithms 101 시리즈의 10번째 글입니다.

알고리즘을 잘한다는 말은 많은 풀이를 외운다는 뜻일까요, 아니면 새로운 문제를 분해하는 절차를 갖고 있다는 뜻일까요? 여기서는 제약을 읽고, 도구를 고르고, 코딩 전에 접근을 검증하는 실전 절차로 시리즈를 마무리합니다.

![Algorithms 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/10/10-01-big-picture.ko.png)
*Algorithms 101 10장 흐름 개요*

## 먼저 던지는 질문

- 어떤 알고리즘 문제에도 적용할 수 있는 표준 사고 절차는 무엇일까요?
- 입력 크기만 보고 허용 복잡도를 어떻게 추정할까요?
- 어떤 신호가 어떤 도구를 떠올리게 할까요?

## 왜 중요한가

알고리즘을 공부하는 목적은 풀이 암기가 아니라 새로운 문제를 분해하는 능력을 얻는 것입니다. 이 능력은 면접에서만 중요하지 않습니다. 실무의 시스템 설계와 성능 문제에서도 똑같이 중요합니다. 같은 도구함을 가진 두 엔지니어도, 무엇을 어떻게 고르는지에 따라 전혀 다른 결과를 냅니다.

> 좋은 풀이는 외운 정답이 아니라 일관된 절차의 산물입니다.

## 한눈에 보는 개념

> 표준 절차는 다섯 단계입니다. (1) 문제를 자기 말로 다시 쓴다. (2) 입력, 출력, 제약을 적는다. (3) 입력 크기로 허용 복잡도를 추정한다. (4) 패턴을 인식해 후보 도구를 좁힌다. (5) 작은 예제로 손 검증한 뒤 코드로 옮긴다. 이 절차는 면접에서도 그대로 통합니다.

```text
Input size -> allowed complexity (rough upper bound)
    n <= 10            : backtracking, every subset (2^n)
    n <= 20            : bitmask DP (2^n)
    n <= 100..500      : up to O(n^3) (Floyd-Warshall, 3D DP)
    n <= 5,000         : O(n^2)
    n <= 10^5..10^6    : O(n log n)
    n >= 10^7          : O(n) or O(log n)
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| 재진술 | 문제를 자기 표현으로 다시 쓰는 것 |
| 허용 복잡도 | 시간 제한과 입력 크기에서 추정한 비용 상한 |
| 패턴 인식 | 입력 구조에서 적절한 도구를 떠올리는 능력 |
| 작은 예제 검증 | 코딩 전 손으로 한 번 따라가는 절차 |
| sanity test | 빈 입력, 경계값, 최대 입력 점검 |

## 개선 전 / 개선 후

**Before — 문제를 보자마자 코딩:**

```text
"Hmm, I think this is BFS."
-> code -> works -> some cases fail -> debugging spiral
```

**After — 다섯 단계 절차 적용:**

```text
1) Restate the problem
2) Write down inputs/outputs/constraints
3) Estimate allowed complexity from n
4) Use pattern recognition to narrow tool candidates
5) Verify on a small example, then code
```

## 단계별로 따라가기

### 1단계: 문제를 자기 말로 다시 쓰기

```text
Original: "Given an array, find the maximum sum of a contiguous subarray."

Restated: Among all contiguous segments of an integer array, find the one with the largest sum.
Edges: Is the answer for an empty array 0, or undefined?
If all values are negative, is the answer the largest single value, or 0?
```

문제를 자신의 말로 다시 써 보는 습관만으로도 많은 오해가 사라집니다.

### 2단계: 입력 크기로 허용 복잡도 추정

```text
n = 10^6, time limit 1 second
-> O(n^2) is out; you need O(n log n) or O(n)
-> Strong hint: "this problem wants a linear or near-linear algorithm"
```

입력 크기는 알고리즘 후보를 좁히는 가장 강한 단서입니다.

### 3단계: 패턴 인식 신호 표

```python
signals = {
    "search in a sorted array":          "binary search",
    "nearest / largest / smallest":      "sort or heap",
    "range sum / min / max":             "prefix sum or segment tree",
    "contiguous subarray":               "two pointers or sliding window",
    "overlapping subproblems":           "DP",
    "shortest path, non-negative":       "Dijkstra",
    "topological order / dependencies":  "topological sort",
    "prefix matters":                    "trie",
    "pattern matching, large text":      "KMP / Aho-Corasick",
    "optimum + greedy plausible":        "try an exchange argument",
}
for k, v in signals.items():
    print(f"- {k:36s} -> {v}")
```

이 매핑을 외워 두면 새로운 문제가 들어왔을 때 도구 후보가 훨씬 빨리 좁혀집니다.

### 4단계: 작은 예제로 손 검증

```text
Problem: maximum contiguous subarray sum (Kadane's algorithm)

Hand trace
arr = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
cur, best = 0, -inf
i=0  cur = max(-2, -2)        = -2,  best = -2
i=1  cur = max(1, -2+1)       = 1,   best = 1
i=2  cur = max(-3, 1-3)       = -2,  best = 1
i=3  cur = max(4, -2+4)       = 4,   best = 4
i=4  cur = max(-1, 4-1)       = 3,   best = 4
i=5  cur = max(2, 3+2)        = 5,   best = 5
i=6  cur = max(1, 5+1)        = 6,   best = 6
i=7  cur = max(-5, 6-5)       = 1,   best = 6
i=8  cur = max(4, 1+4)        = 5,   best = 6
Answer: 6
```

한 번 손으로 따라가 본 알고리즘은 구현할 때 훨씬 덜 흔들립니다.

### 5단계: 코드로 옮기고 경계를 테스트

```python
def max_subarray(arr):
    if not arr:
        return 0
    cur = best = arr[0]
    for x in arr[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best

assert max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
assert max_subarray([-1]) == -1
assert max_subarray([1]) == 1
assert max_subarray([]) == 0
```

핵심 케이스 외에도 빈 입력, 단일 원소, 전부 음수, 전부 양수는 자동으로 확인하는 습관이 필요합니다.

## 이 글에서 먼저 가져갈 점

- 다섯 단계 절차는 문제 종류와 상관없이 반복해서 쓸 수 있습니다.
- 입력 크기에서 허용 복잡도를 읽는 일이 가장 강한 신호입니다.
- 패턴 인식 표는 머릿속 색인 역할을 합니다.
- 손으로 한 번 추적한 해법이 가장 믿을 만합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 문제를 끝까지 안 읽고 바로 코딩 | 잘못된 풀이 | 자기 말로 다시 씁니다 |
| 복잡도 추정 생략 | 시간 초과 | n부터 보고 상한을 잡습니다 |
| 패턴 인식 없이 감으로 접근 | 헤맴 | 신호-도구 매핑을 적극 활용합니다 |
| 경계 케이스 무시 | 간헐적 실패 | 빈값, 단일값, 극단값을 항상 봅니다 |
| 외운 풀이에만 의존 | 처음 보는 문제에 약함 | 절차로 다시 분해합니다 |

## 실무에서는 이렇게 쓰입니다

- 시스템 설계에서 입력 크기로 자료구조 선택을 좁힙니다.
- 성능 튜닝에서 병목을 알고리즘 복잡도로 읽습니다.
- 코드 리뷰에서 다른 사람의 풀이를 절차로 검증합니다.
- 면접에서는 사고 절차의 안정성을 평가합니다.
- 학습에서는 이 절차로 새 문제를 분해하며 도구함을 넓힙니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 새로운 문제를 보자마자 타이핑하지 않습니다. 먼저 크기와 구조를 읽고, 도구 후보를 좁히고, 작은 예제로 검증한 뒤에야 코드를 작성합니다. 이 절차는 면접뿐 아니라 프로덕션 의사결정에도 그대로 적용됩니다.

또한 실력을 "얼마나 많은 정답을 외웠는가"로 측정하지 않습니다. 진짜 실력은 처음 보는 문제도 같은 절차로 안정적으로 분해할 수 있는 자신감에서 나옵니다. 도구함은 점점 넓어지겠지만, 그 도구를 고르는 절차가 더 중요합니다.

## 체크리스트

- [ ] 다섯 단계 절차를 기억하고 있는가
- [ ] 입력 크기로 허용 복잡도를 추정하는가
- [ ] 신호-도구 매핑을 머릿속에 갖고 있는가
- [ ] 경계 케이스를 자동으로 확인하는가
- [ ] 새로운 문제도 같은 절차로 분해할 수 있는가

## 연습 문제

1. 이 시리즈에서 다룬 알고리즘 도구를 한 표로 정리해 보세요. 평균/최악 복잡도, 적용 신호, 한계까지 한 줄씩 적어 보면 강한 학습 자료가 됩니다.

2. 외부 알고리즘 문제 하나를 골라 다섯 단계 절차를 글로 먼저 쓰고, 그다음 풀이를 구현해 보세요. 어느 단계가 가장 어려웠는지도 적어 보세요.

3. "어떤 신호가 나오면 그래프 알고리즘을 떠올리는가"를 5분 동안 다른 사람에게 설명하거나 혼자 말로 정리해 보세요. 설명할 수 있어야 자기 도구가 됩니다.

## 정리 및 다음 단계

알고리즘 학습의 본질은 풀이의 양보다 절차의 일관성에 있습니다. 입력 크기에서 복잡도를 추정하고, 신호에서 도구를 좁히고, 작은 예제로 검증한 뒤 코드로 옮기는 다섯 단계 루프는 면접과 실무에서 똑같이 작동합니다.

이로써 Algorithms 101 시리즈를 마칩니다. 다음 단계로는 자료구조 심화, 그래프 고급 주제, 혹은 검색 엔진·추천 시스템·컴파일러 같은 도메인 응용으로 확장할 수 있습니다. 여기서 만든 사고 절차는 그 모든 학습으로 그대로 이전됩니다.

## 실전 확장 워크북

이 절은 문제 풀이 전략 루프를 실제 문제 풀이와 운영 감각으로 연결하기 위한 보강 파트입니다. 개념을 암기하는 대신, 입력 크기·자료 구조·검증 순서를 함께 다루어 같은 유형의 문제를 반복적으로 안정적으로 풀 수 있게 만드는 데 목적이 있습니다. 핵심은 "정답 코드 한 번"이 아니라 "다음 문제에서도 재사용 가능한 판단 프레임"을 확보하는 것입니다.

### 1) 시간 복잡도와 입력 제약을 먼저 맞추기

| 입력 조건 | 우선 배제할 접근 | 현실적인 후보 | 확인 포인트 |
| --- | --- | --- | --- |
| n <= 10^3 | 없음(학습 목적 실험 가능) | 브루트포스, 정렬, 해시 | 구현 명확성 |
| n <= 10^5 | O(n^2) 대부분 배제 | O(n log n), O(n), BFS/DFS | 경계값 테스트 |
| n <= 10^6 이상 | O(n log n)도 부담 가능 | 단일 패스, 압축, 스트리밍 | 메모리 상한 |

복잡도 판단은 코드 스타일 논쟁보다 우선합니다. 같은 팀에서 코드 품질 기준이 달라도, 입력 제약과 차수를 맞추는 원칙은 공통으로 적용됩니다. 이 단계를 건너뛰면 구현이 아무리 깔끔해도 제출 실패나 운영 지연으로 이어집니다.

### 2) 단계별 추적 표로 경계 버그를 조기에 찾기

| 단계 | 관찰 값 | 기대 신호 | 실패 신호 |
| --- | --- | --- | --- |
| 초기화 | 포인터/상태/큐/테이블 | 문제 정의와 일치 | 초기값 누락 |
| 1회 반복 | 상태 전이 | 단조 증가 또는 감소 | 제자리 반복 |
| 종료 직전 | 반환 후보 | 문제 요구와 직접 연결 | 보조값 반환 |

경계 버그는 대부분 "한 줄"에서 발생하지만, 원인은 상태 전이 설계에 있습니다. 그래서 디버깅할 때는 출력값 하나만 보지 말고, 전이 로그를 함께 봐야 합니다. 특히 인덱스 기반 문제는 `lo, mid, hi`, DP 문제는 `state, transition`, 그래프 문제는 `queue size, visited count`를 같이 기록하면 원인 분리가 훨씬 빨라집니다.

### 3) Python 구현 앵커

```python
def solve_with_checklist(n, constraints):
    if n <= 10**5 and constraints.get('ordered'):
        return '이진 탐색/투포인터 후보'
    if constraints.get('graph') and constraints.get('weighted'):
        return '다익스트라 또는 벨만-포드 후보'
    if constraints.get('subproblem_repeat'):
        return 'DP 후보'
    return '브루트포스 축소 또는 그리디 검토'
```

코드는 짧아도 충분합니다. 중요한 점은 구현 전에 불변식(invariant)을 문장으로 먼저 고정하는 것입니다. 예를 들어 "현재 단계가 끝나면 최소 비용이 보장된다" 같은 문장이 없으면, 코드가 돌아가도 왜 맞는지 설명할 수 없고, 변형 문제에서 무너지기 쉽습니다.

### 4) LeetCode 스타일 매핑

| 문제 | 핵심 패턴 | 첫 시도에서 자주 틀리는 지점 |
| --- | --- | --- |
| 1 Two Sum | 제약을 통한 후보 축소 | 입력 조건을 늦게 반영 |
| 15 3Sum | 상태/포인터 유지 | 경계 인덱스 처리 |
| 300 Longest Increasing Subsequence | 자료구조 선택 | 복잡도 목표 미달 |

문제 매핑의 목적은 정답 암기가 아닙니다. 같은 구조를 빠르게 인식하고, "왜 이 패턴을 쓰는가"를 재현하는 데 있습니다. 시리즈 전체를 관통하는 실력 차이는 여기서 발생합니다.

### 5) 비교 벤치마크를 읽는 기준

| 비교 항목 | A 접근 | B 접근 | 의사결정 기준 |
| --- | --- | --- | --- |
| 시간 | 평균적으로 빠름 | 최악 케이스 안정적 | 입력 분포가 고정인지 |
| 메모리 | 추가 배열 필요 | 제자리 처리 가능 | 메모리 제한 강도 |
| 구현 난이도 | 짧음 | 디버깅 난이도 높음 | 팀 유지보수 역량 |

벤치마크 숫자는 환경에 따라 달라집니다. 하지만 차수와 메모리 계층에서 발생하는 방향성은 반복됩니다. 그래서 한 번 측정한 결과를 절대값으로 외우기보다, 어떤 조건에서 우위가 바뀌는지(입력 크기, 정렬 여부, 중복 비율)를 함께 기록해야 다음 의사결정에 도움이 됩니다.

### 6) 제출/배포 전 점검 루틴

1. 문제 제약을 한 줄로 요약하고 불가능한 차수를 먼저 제거합니다.
2. 핵심 자료구조 선택 이유를 "삽입/조회/삭제 비용" 기준으로 적습니다.
3. 경계 입력 3종(빈값, 최소값, 중복/극단값) 테스트를 고정합니다.
4. 시간·공간 복잡도를 코드 옆에 기록하고, 실제 측정값을 짧게 남깁니다.
5. 같은 패턴의 변형 문제를 1개 더 풀어 일반화 여부를 확인합니다.

이 루틴을 꾸준히 적용하면 "이번 문제를 맞춤"에서 끝나지 않고 "같은 유형을 안정적으로 재현"하는 상태로 넘어갈 수 있습니다. 알고리즘 학습은 지식 축적이 아니라 판단 체계 구축이라는 점을 계속 기억하는 것이 중요합니다.

## 처음 질문으로 돌아가기

- **어떤 알고리즘 문제에도 적용할 수 있는 표준 사고 절차는 무엇일까요?**
  - 이 글의 답은 문제 재진술, 입력·출력·제약 정리, 허용 복잡도 추정, 신호-도구 매핑, 작은 예제 손검증의 다섯 단계입니다. `Kadane` 손추적 예시가 보여 주듯 코딩 전에 한 번 따라가 보는 절차가 실제 오답을 크게 줄여 줍니다.
- **입력 크기만 보고 허용 복잡도를 어떻게 추정할까요?**
  - `n = 10^6`이면 O(n^2)는 바로 버리고 O(n log n)이나 O(n)을 찾아야 한다는 식으로, 본문 표를 상한선으로 쓰면 됩니다. 입력 크기는 감이 아니라 알고리즘 후보를 잘라 내는 가장 강한 제약입니다.
- **어떤 신호가 어떤 도구를 떠올리게 할까요?**
  - 정렬된 배열이면 binary search, contiguous subarray면 two pointers나 Kadane, overlapping subproblems면 DP, non-negative shortest path면 Dijkstra를 떠올리라는 것이 본문의 `signals` 딕셔너리였습니다. 결국 문제 풀이 실력은 정답 암기보다 이런 신호-도구 연결을 빠르게 꺼내는 능력에 가깝습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms 101 (1/10): 알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [Algorithms 101 (2/10): 시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [Algorithms 101 (3/10): 탐색 알고리즘](./03-search-algorithms.md)
- [Algorithms 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [Algorithms 101 (6/10): 동적 계획법](./06-dynamic-programming.md)
- [Algorithms 101 (7/10): 그리디 알고리즘](./07-greedy-algorithms.md)
- [Algorithms 101 (8/10): 그래프 알고리즘](./08-graph-algorithms.md)
- [Algorithms 101 (9/10): 문자열 알고리즘 기초](./09-string-algorithms.md)
- **알고리즘 문제 풀이 전략 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [book-examples — algorithms-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-101/ko)
- [Competitive Programmer's Handbook (Antti Laaksonen)](https://cses.fi/book/book.pdf)
- [LeetCode — Patterns and study plans](https://leetcode.com/explore/)
- [CLRS — Introduction to Algorithms](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)
- [Sedgewick & Wayne — Algorithms 4ed](https://algs4.cs.princeton.edu/home/)

Tags: Computer Science, 알고리즘, 문제 풀이, 패턴 인식, 면접, 연습
