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

알고리즘을 잘한다는 말은 많은 풀이를 외운다는 뜻일까요, 아니면 새로운 문제를 분해하는 절차를 갖고 있다는 뜻일까요? 여기서는 제약을 읽고, 도구를 고르고, 코딩 전에 접근을 검증하는 실전 절차로 시리즈를 마무리합니다.

이 글은 Algorithms 101 시리즈의 마지막 글입니다.

![Algorithms 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/10/10-01-big-picture.ko.png)
*Algorithms 101 10장 흐름 개요*

## 이 글에서 다룰 문제

- 어떤 알고리즘 문제에도 적용할 수 있는 표준 사고 절차는 무엇일까요?
- 입력 크기만 보고 허용 복잡도를 어떻게 추정할까요?
- 어떤 신호가 어떤 도구를 떠올리게 할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

알고리즘을 공부하는 목적은 풀이 암기가 아니라 새로운 문제를 분해하는 능력을 얻는 것입니다. 이 능력은 면접에서만 중요하지 않습니다. 실무의 시스템 설계와 성능 문제에서도 똑같이 중요합니다. 같은 도구함을 가진 두 엔지니어도, 무엇을 어떻게 고르는지에 따라 전혀 다른 결과를 냅니다.

> 좋은 풀이는 외운 정답이 아니라 일관된 절차의 산물입니다.

> 표준 절차는 다섯 단계입니다. (1) 문제를 자기 말로 다시 쓴다. (2) 입력, 출력, 제약을 적는다. (3) 입력 크기로 허용 복잡도를 추정한다. (4) 패턴을 인식해 후보 도구를 좁힌다. (5) 작은 예제로 손 검증한 뒤 코드로 옮긴다. 이 절차는 면접에서도 그대로 통합니다.

```text
Input size → allowed complexity (rough upper bound)
    n ≤ 10             : O(n!) backtracking, every permutation
    n ≤ 20             : O(2^n) bitmask DP
    n ≤ 100..500       : O(n^3) Floyd-Warshall, 3D DP
    n ≤ 5,000          : O(n^2)
    n ≤ 10^5..10^6     : O(n log n)
    n ≥ 10^7           : O(n) or O(log n)
```

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
→ code → works → edge cases fail → long debugging spiral
→ submission fail → restart
```

**After — 다섯 단계 절차 적용:**

```text
1) 재진술: 연속 부분 배열 중 합이 가장 큰 것을 찾는다
2) 제약: 배열 길이 n ≤ 10^5, 원소 범위 -10^4 ~ 10^4, 빈 배열 처리?
3) 복잡도: n=10^5 → O(n log n) 이하 필요, O(n)이면 더 좋음
4) 패턴: 연속 부분 배열 → sliding window 또는 DP (Kadane's)
5) 손 검증: [-2,1,-3,4,-1,2,1,-5,4] → cur=4,3,5,6,1,5 → 6
→ 코드 작성
```

## 단계별로 따라가기

### 1단계: 문제를 자기 말로 다시 쓰기

```text
원문: "Given an array, find the maximum sum of a contiguous subarray."

재진술: 정수 배열에서 인접한 원소들로 이루어진 구간 중 합이 가장 큰 구간의 합을 반환한다.

경계 케이스 질문:
- 빈 배열이면 0을 반환? 아니면 에러?
- 모든 원소가 음수면 가장 큰 음수를 반환? 아니면 0?
- 단일 원소 배열도 유효한 부분 배열?
```

문제를 자신의 말로 다시 써 보는 습관만으로도 많은 오해가 사라집니다.

### 2단계: 입력 크기로 허용 복잡도 추정

```python
def estimate_complexity(n, time_limit_sec=1.0):
    """입력 크기로 허용 알고리즘 계층 추정."""
    ops_per_second = 10**8   # 보통적인 추정
    budget = ops_per_second * time_limit_sec

    import math
    estimates = {
        "O(log n)": math.log2(n) if n > 0 else 0,
        "O(n)": n,
        "O(n log n)": n * math.log2(n) if n > 0 else 0,
        "O(n^2)": n ** 2,
        "O(2^n)": 2 ** n if n <= 60 else float('inf'),
    }
    feasible = [k for k, v in estimates.items() if v <= budget]
    return feasible

for n in [10, 100, 1000, 10**5, 10**6]:
    feasible = estimate_complexity(n)
    print(f"n={n:8d}: {', '.join(feasible)}")
```

입력 크기는 알고리즘 후보를 좁히는 가장 강한 단서입니다.

### 3단계: 패턴 인식 신호 표

```python
PATTERN_SIGNALS = {
    # 탐색
    "정렬된 배열에서 탐색":          "이진 탐색",
    "답이 단조롭게 증감":            "Parametric search",
    # 정렬
    "k번째 원소":                    "quickselect 또는 힙",
    "병합 또는 구간 처리":           "정렬 후 처리",
    # 부분 문제
    "연속 부분 배열/구간":           "투 포인터 또는 슬라이딩 윈도우",
    "최장 부분 수열":                "DP (LIS, LCS)",
    "최소 비용 경로":                "DP 또는 다익스트라",
    # 그래프
    "최단 거리 (무가중치)":          "BFS",
    "최단 거리 (양수 가중치)":       "다익스트라",
    "최단 거리 (음수 가중치)":       "Bellman-Ford",
    "의존성 순서":                   "위상 정렬",
    "최소 연결 비용":                "MST (Kruskal/Prim)",
    "연결 컴포넌트":                 "Union-Find 또는 DFS/BFS",
    # 문자열
    "prefix 공유":                   "트라이",
    "패턴 매칭 (대규모)":            "KMP 또는 Aho-Corasick",
    # 최적화
    "탐욕 선택 속성 + 최적 부분 구조": "그리디",
    "중복 부분 문제 + 최적 부분 구조": "동적 계획법",
    # 완전 탐색
    "모든 조합/순열":                "백트래킹",
    "부분 집합 최적화":              "비트마스크 DP",
}

for signal, tool in PATTERN_SIGNALS.items():
    print(f"  [{signal}] → {tool}")
```

이 매핑을 익혀 두면 새로운 문제가 들어왔을 때 도구 후보가 훨씬 빨리 좁혀집니다.

### 4단계: 작은 예제로 손 검증 (Kadane's Algorithm)

```text
문제: 최대 연속 부분 배열 합 (Kadane's Algorithm)

손 추적:
arr = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
cur = arr[0] = -2, best = -2

i=1: cur = max(1, -2+1) = max(1,-1) = 1,  best = 1
i=2: cur = max(-3,1-3) = max(-3,-2) = -2, best = 1
i=3: cur = max(4,-2+4) = max(4,2) = 4,    best = 4
i=4: cur = max(-1,4-1) = max(-1,3) = 3,   best = 4
i=5: cur = max(2,3+2) = max(2,5) = 5,     best = 5
i=6: cur = max(1,5+1) = max(1,6) = 6,     best = 6
i=7: cur = max(-5,6-5) = max(-5,1) = 1,   best = 6
i=8: cur = max(4,1+4) = max(4,5) = 5,     best = 6

답: 6 (구간 [4,-1,2,1])
```

한 번 손으로 따라가 본 알고리즘은 구현할 때 훨씬 덜 흔들립니다.

### 5단계: 코드로 옮기고 경계를 테스트

```python
def max_subarray(arr):
    """Kadane's Algorithm: O(n) 시간, O(1) 공간."""
    if not arr:
        return 0
    cur = best = arr[0]
    for x in arr[1:]:
        cur = max(x, cur + x)   # 이전 합이 음수면 현재 원소부터 다시 시작
        best = max(best, cur)
    return best

# 핵심 케이스
assert max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
assert max_subarray([-1]) == -1          # 음수만 있는 경우
assert max_subarray([1]) == 1            # 단일 원소
assert max_subarray([]) == 0             # 빈 배열
assert max_subarray([-1, -2, -3]) == -1  # 모두 음수 → 가장 큰 음수
assert max_subarray([1, 2, 3]) == 6      # 모두 양수
print("모든 케이스 통과")
```

### 6단계: 시리즈 도구함 정리

```python
# 이 시리즈에서 배운 도구함 요약
TOOLBOX = {
    "알고리즘 설계": {
        "정확성/유한성/효율성 삼각형": "모든 알고리즘의 기본 계약",
        "의사코드 우선 작성": "구현 전 논리를 명확히",
        "불변식 명시": "정확성 논증의 근거",
    },
    "복잡도 분석": {
        "Big-O 6계층": "O(1), O(log n), O(n), O(n log n), O(n²), O(2^n)",
        "입력 크기 표": "n에서 허용 복잡도를 역산",
        "분할 상환": "시퀀스 전체의 평균 비용",
    },
    "탐색": {
        "이진 탐색": "정렬된 배열에서 O(log n)",
        "bisect": "Python 표준, lower/upper bound",
        "Parametric search": "단조 조건 함수의 답을 이진 탐색",
    },
    "정렬": {
        "Timsort": "Python 표준, 안정+적응형",
        "Mergesort": "안정 정렬 O(n log n) 보장",
        "Quicksort": "제자리 정렬 평균 O(n log n)",
    },
    "재귀/분할 정복": {
        "3가지 규칙": "베이스 케이스, 입력 감소, 자기 호출",
        "점화식": "T(n) = a·T(n/b) + f(n)",
        "메모이제이션": "반복 부분 문제의 O(2^n) → O(n)",
    },
    "동적 계획법": {
        "두 조건": "중복 부분 문제 + 최적 부분 구조",
        "상태 정의": "dp[...] = ... 를 한 문장으로",
        "top-down vs bottom-up": "직관 vs 성능",
    },
    "그리디": {
        "두 조건": "그리디 선택 속성 + 최적 부분 구조",
        "교환 논증": "정당화의 표준 도구",
        "함정": "DP가 필요한 문제를 그리디로 오해",
    },
    "그래프": {
        "BFS": "무가중치 최단 거리 O(V+E)",
        "DFS": "연결성, 위상 정렬 O(V+E)",
        "다익스트라": "양수 가중치 최단 경로 O((V+E)log V)",
        "Kruskal/Prim": "MST O(E log E)",
        "Union-Find": "연결성 O(α(n)) per op",
    },
    "문자열": {
        "KMP": "단일 패턴 O(n+m)",
        "트라이": "prefix 탐색 O(m)",
        "Aho-Corasick": "다중 패턴 O(n + matches)",
        "ReDoS 주의": "백트래킹 정규식 = 지수 위험",
    },
}

for category, tools in TOOLBOX.items():
    print(f"\n{category}:")
    for tool, desc in tools.items():
        print(f"  {tool}: {desc}")
```

## 문제 유형별 도구 선택 가이드

| 문제 신호 | 첫 번째 후보 | 복잡도 | 주의사항 |
| --- | --- | --- | --- |
| 정렬된 배열, 값 찾기 | 이진 탐색 | O(log n) | 정렬 전제 확인 |
| 배열, k번째 원소 | 퀵셀렉트 또는 힙 | O(n) 평균 / O(n log k) | 전체 정렬 불필요 |
| 연속 부분 배열 최적 | 슬라이딩 윈도우 또는 Kadane's | O(n) | 조건 단조성 확인 |
| 최적 배분/선택 | 그리디 (교환 논증 후) 또는 DP | O(n log n) ~ O(n²) | 분할 가능 여부 |
| 경로 수 / 방법 수 | 동적 계획법 | O(n²) ~ O(n·W) | 상태 설계가 핵심 |
| 최단 거리 (무가중치) | BFS | O(V+E) | deque 사용 |
| 최단 거리 (양수 가중치) | 다익스트라 | O((V+E)log V) | 음수 가중치 불가 |
| 의존성 처리, 순서 | 위상 정렬 | O(V+E) | 사이클 탐지 |
| 집합 연결성 | Union-Find | O(α(n)) | 경로 압축 필수 |
| 문자열 패턴 매칭 | KMP 또는 표준 라이브러리 | O(n+m) | 단일 vs 다중 패턴 |
| prefix 자동완성 | 트라이 | O(m) | 메모리 vs 시간 트레이드오프 |
| 완전 탐색, n≤20 | 백트래킹 또는 bitmask DP | O(2^n) | 가지 치기 필수 |

## 이 글에서 먼저 가져갈 점

- 다섯 단계 절차는 문제 종류와 상관없이 반복해서 쓸 수 있습니다.
- 입력 크기에서 허용 복잡도를 읽는 일이 가장 강한 신호입니다.
- 패턴 인식 표는 머릿속 색인 역할을 합니다.
- 손으로 한 번 추적한 해법이 가장 믿을 만합니다.
- 경계 케이스를 자동으로 확인하는 습관이 실패를 막습니다.

## 자주 하는 실수

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 문제를 끝까지 안 읽고 바로 코딩 | 잘못된 풀이 | 자기 말로 다시 씁니다 |
| 복잡도 추정 생략 | 시간 초과 | n부터 보고 상한을 잡습니다 |
| 패턴 인식 없이 감으로 접근 | 헤맴 | 신호-도구 매핑을 적극 활용합니다 |
| 경계 케이스 무시 | 간헐적 실패 | 빈값, 단일값, 극단값을 항상 봅니다 |
| 외운 풀이에만 의존 | 처음 보는 문제에 약함 | 절차로 다시 분해합니다 |
| 첫 번째 접근이 틀렸을 때 디버깅에 집착 | 시간 낭비 | 복잡도가 틀렸으면 접근 자체를 바꿉니다 |

## 실무에서는 이렇게 쓰입니다

- 시스템 설계에서 입력 크기로 자료구조 선택을 좁힙니다.
- 성능 튜닝에서 병목을 알고리즘 복잡도로 읽습니다.
- 코드 리뷰에서 다른 사람의 풀이를 절차로 검증합니다.
- 면접에서는 사고 절차의 안정성을 평가합니다.
- 학습에서는 이 절차로 새 문제를 분해하며 도구함을 넓힙니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 새로운 문제를 보자마자 타이핑하지 않습니다. 먼저 크기와 구조를 읽고, 도구 후보를 좁히고, 작은 예제로 검증한 뒤에야 코드를 작성합니다. 이 절차는 면접뿐 아니라 프로덕션 의사결정에도 그대로 적용됩니다.

또한 실력을 "얼마나 많은 정답을 외웠는가"로 측정하지 않습니다. 진짜 실력은 처음 보는 문제도 같은 절차로 안정적으로 분해할 수 있는 자신감에서 나옵니다. 도구함은 점점 넓어지겠지만, 그 도구를 고르는 절차가 더 중요합니다.

## 운영 체크리스트

- [ ] 다섯 단계 절차를 기억하고 있는가
- [ ] 입력 크기로 허용 복잡도를 추정하는가
- [ ] 신호-도구 매핑을 머릿속에 갖고 있는가
- [ ] 경계 케이스를 자동으로 확인하는가
- [ ] 새로운 문제도 같은 절차로 분해할 수 있는가
- [ ] 접근이 틀렸을 때 빠르게 피벗할 수 있는가

## 연습 문제

1. 이 시리즈에서 다룬 알고리즘 도구를 한 표로 정리해 보세요. 평균/최악 복잡도, 적용 신호, 한계까지 한 줄씩 적어 보면 강한 학습 자료가 됩니다.

2. 외부 알고리즘 문제 하나를 골라 다섯 단계 절차를 글로 먼저 쓰고, 그다음 풀이를 구현해 보세요. 어느 단계가 가장 어려웠는지도 적어 보세요.

3. "어떤 신호가 나오면 그래프 알고리즘을 떠올리는가"를 5분 동안 다른 사람에게 설명하거나 혼자 말로 정리해 보세요. 설명할 수 있어야 자기 도구가 됩니다.

4. 이 시리즈의 각 글에서 하나씩 문제를 골라 총 10개의 문제 세트를 만들고, 다섯 단계 절차를 적용해 풀어 보세요. 각 문제에서 어떤 신호가 도구 선택을 이끌었는지 기록하세요.

## 정리 및 다음 단계

알고리즘 학습의 본질은 풀이의 양보다 절차의 일관성에 있습니다. 입력 크기에서 복잡도를 추정하고, 신호에서 도구를 좁히고, 작은 예제로 검증한 뒤 코드로 옮기는 다섯 단계 루프는 면접과 실무에서 똑같이 작동합니다.

이로써 Algorithms 101 시리즈를 마칩니다. 다음 단계로는 자료구조 심화, 그래프 고급 주제, 혹은 검색 엔진·추천 시스템·컴파일러 같은 도메인 응용으로 확장할 수 있습니다. 여기서 만든 사고 절차는 그 모든 학습으로 그대로 이전됩니다.

## 처음 질문으로 돌아가기

- **어떤 알고리즘 문제에도 적용할 수 있는 표준 사고 절차는 무엇일까요?**
  - 다섯 단계입니다. (1) 문제를 자기 말로 재진술하고 경계 케이스를 정리합니다. (2) 입력, 출력, 제약을 명시합니다. (3) 입력 크기 n에서 허용 복잡도를 추정합니다. (4) 문제의 신호(정렬됨, 연속 구간, 의존성 등)에서 도구 후보를 좁힙니다. (5) 작은 예제로 손 추적 후 코드로 옮깁니다. 이 절차를 반복할수록 새 문제에서의 시간이 줄어듭니다.
- **입력 크기만 보고 허용 복잡도를 어떻게 추정할까요?**
  - 1초에 약 10^8번 연산이 가능하다고 가정합니다. n=10^5이면 O(n log n) ≈ 1.7×10^6으로 여유 있고, O(n²)=10^10으로 불가능합니다. n=10^6이면 O(n log n) ≈ 2×10^7로 가능하고, O(n²)=10^12로 절대 불가능합니다. 이 감각이 있으면 후보 알고리즘을 절반 이상 제거할 수 있습니다.
- **어떤 신호가 어떤 도구를 떠올리게 할까요?**
  - 정렬된 배열이면 이진 탐색, 최단 거리면 BFS/다익스트라, 의존성 순서면 위상 정렬, 부분 집합 최적이면 DP, 그리디 선택 속성이 있으면 그리디, prefix 공유면 트라이, 패턴 매칭이면 KMP, 연결성이면 Union-Find를 가장 먼저 떠올립니다. 이 매핑을 체화하는 것이 알고리즘 실력의 핵심입니다.

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
