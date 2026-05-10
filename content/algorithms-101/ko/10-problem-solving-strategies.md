---
series: algorithms-101
episode: 10
title: 알고리즘 문제 풀이 전략
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
  - 알고리즘
  - 문제 풀이
  - 패턴 인식
  - 면접
  - 실무
seo_description: 알고리즘 문제를 만났을 때 패턴을 인식하고 도구를 선택하는 사고 절차, 그리고 면접과 실무에서 알고리즘을 잘 다룬다는 것의 의미를 정리합니다.
last_reviewed: '2026-05-04'
---

# 알고리즘 문제 풀이 전략

> Algorithms 101 시리즈 (10/10)


## 이 글에서 다룰 문제

알고리즘 학습의 목표는 풀이를 외우는 것이 아니라 새 문제를 분해하는 능력을 갖추는 것입니다. 이는 면접뿐 아니라 실무 시스템 설계에도 직결됩니다. 도구함이 같아도 어떤 사고 절차로 도구를 선택하느냐가 결과의 질을 결정합니다.

> 좋은 풀이는 외운 결과가 아니라 일관된 사고 절차의 산물입니다.

## 개념 한눈에 보기

> 표준 절차는 다섯 단계로 정리할 수 있습니다. (1) 문제를 다시 진술한다. (2) 입력·출력·제약을 적는다. (3) 입력 크기로 허용 복잡도를 추정한다. (4) 패턴을 인식해 도구를 좁힌다. (5) 작은 예제로 검증한 뒤 코드로 옮긴다. 이 절차는 면접에서도 그대로 적용됩니다.

```text
입력 크기 → 허용 복잡도 (대략적인 상한)
    n ≤ 10            : 백트래킹, 모든 부분집합 (2^n)
    n ≤ 20            : 비트마스크 DP (2^n)
    n ≤ 100~500       : O(n^3) 까지 가능 (Floyd-Warshall, DP 3차)
    n ≤ 5,000         : O(n^2)
    n ≤ 10^5~10^6     : O(n log n)
    n ≥ 10^7          : O(n) 또는 O(log n)
```

## Before / After

**Before — 문제를 보자마자 코드부터:**

```text
"음, BFS로 풀면 될 것 같다."
→ 코딩 → 동작 → 일부 케이스 실패 → 디버깅의 늪
```

**After — 다섯 단계 절차:**

```text
1) 문제 진술 다시 쓰기
2) 입력/출력/제약 정리
3) n에서 허용 복잡도 추정
4) 패턴 인식으로 도구 후보 좁히기
5) 작은 예제로 검증 → 코드
```

## 실습: 단계별로 따라하기

### 1단계: 문제를 자신의 언어로 다시 진술

```text
원문: "Given an array, find the maximum sum of a contiguous subarray."

다시 쓰기: 정수 배열에서 연속된 구간의 합 중 가장 큰 값을 구한다.
경계: 빈 배열은 0인가 아니면 정의되지 않는가?
음수만 있을 때 답은 가장 작은 |음수|? 아니면 0?
```

원문 그대로 코딩하지 말고 자신의 언어로 다시 쓰는 것만으로 절반의 오류가 사라집니다.

### 2단계: 입력 크기로 허용 복잡도 추정

```text
n = 10^6, 시간 제한 1초
→ O(n²) 불가, O(n log n) 또는 O(n) 필요
→ "이 문제는 선형 또는 준선형 알고리즘"이라는 강한 힌트
```

입력 크기는 거의 항상 알고리즘 후보를 좁히는 가장 강력한 단서입니다.

### 3단계: 패턴 인식 신호 표

```python
signals = {
    "정렬된 배열에서 검색": "이진 탐색",
    "가장 가까운/큰/작은": "정렬 또는 heap",
    "구간 합/최소/최대": "prefix sum 또는 segment tree",
    "연속 부분 배열": "투 포인터 또는 슬라이딩 윈도우",
    "겹치는 부분 문제": "DP",
    "최단 경로 양의 가중치": "다익스트라",
    "위상 순서/의존성": "위상 정렬",
    "prefix가 핵심": "트라이",
    "패턴 매칭 큰 텍스트": "KMP/Aho-Corasick",
    "최적해 + 그리디 가능성": "교환 논증으로 증명 시도",
}
for k, v in signals.items():
    print(f"- {k:32s} → {v}")
```

이 매핑은 외워두면 새 문제에서 즉시 작동하는 일종의 인덱스입니다.

### 4단계: 작은 예제로 알고리즘 검증

```text
문제: 배열에서 연속 부분합의 최대값 (Kadane's algorithm)

손 추적
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
답: 6
```

손으로 한 번 추적하고 나면 코딩은 거의 옮겨 적기에 가까워집니다.

### 5단계: 코드로 옮기고 경계 테스트

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

핵심 케이스 외에 빈 입력, 단일 원소, 모두 음수, 모두 양수의 네 가지 경계는 항상 점검합니다.

## 이 코드에서 주목할 점

- 다섯 단계 절차는 모든 문제에 동일하게 적용됨
- 입력 크기 → 허용 복잡도 추정이 가장 강력한 단서
- 패턴 인식 매핑은 일종의 인덱스
- 손으로 한 번 추적한 풀이가 가장 신뢰할 수 있음

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 문제를 끝까지 안 읽고 코딩 | 잘못된 풀이 | 자신의 언어로 다시 쓰기 |
| 복잡도 추정 없이 시작 | 시간 초과 | n으로 상한 추정 먼저 |
| 패턴 인식 없이 휴리스틱 | 헤매기 | 신호 → 도구 매핑 활용 |
| 경계 케이스 무시 | 일부 실패 | 빈/단일/극단을 항상 점검 |
| 풀이 외우기에만 의존 | 새 문제에 약함 | 절차에 따라 다시 분해 |

## 실무에서는 이렇게 쓰입니다

- 시스템 설계: 입력 크기로 데이터 구조 선택을 먼저 좁힘
- 성능 튜닝: 병목을 알고리즘 복잡도 관점에서 분석
- 코드 리뷰: 다른 사람의 풀이를 절차로 검증
- 면접: 후보의 사고 절차 일관성으로 평가
- 학습: 새 문제를 절차에 따라 분해하며 도구함 확장

## 체크리스트

- [ ] 다섯 단계 절차를 외우고 있는가
- [ ] 입력 크기로 허용 복잡도를 추정하는가
- [ ] 신호 → 도구 매핑을 머릿속에 가지고 있는가
- [ ] 경계 케이스를 자동으로 점검하는 습관이 있는가
- [ ] 새 문제에 대해 동일한 절차로 분해할 수 있는가

## 정리 및 다음 단계

알고리즘 학습의 본질은 풀이의 양이 아니라 사고 절차의 일관성입니다. 입력 크기로 복잡도를 추정하고, 신호로 도구를 좁히고, 작은 예제로 검증한 뒤 코드로 옮긴다는 다섯 단계 절차는 면접·실무 모두에서 그대로 작동합니다.

이로써 Algorithms 101 시리즈를 마칩니다. 다음 학습으로는 자료구조 심화(트리·힙·해시의 변형), 그래프 심화(흐름·매칭·SCC), 또는 분야별 응용(검색 엔진·추천 시스템·컴파일러)으로 확장하면 자연스럽게 이어집니다. 이 시리즈에서 익힌 사고 절차는 그 모든 학습에 그대로 쓰입니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [탐색 알고리즘](./03-search-algorithms.md)
- [정렬 알고리즘](./04-sorting-algorithms.md)
- [재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [동적 계획법](./06-dynamic-programming.md)
- [그리디 알고리즘](./07-greedy-algorithms.md)
- [그래프 알고리즘](./08-graph-algorithms.md)
- [문자열 알고리즘 기초](./09-string-algorithms.md)
- **알고리즘 문제 풀이 전략 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Competitive Programmer's Handbook (Antti Laaksonen)](https://cses.fi/book/book.pdf)
- [LeetCode — Patterns and study plans](https://leetcode.com/explore/)
- [CLRS — Introduction to Algorithms](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)
- [Sedgewick & Wayne — Algorithms 4ed](https://algs4.cs.princeton.edu/home/)

Tags: Computer Science, 알고리즘, 문제 풀이, 패턴 인식, 면접, 실무
