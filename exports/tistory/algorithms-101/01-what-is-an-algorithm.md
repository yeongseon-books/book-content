
# 알고리즘이란 무엇인가?

> Algorithms 101 시리즈 (1/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 같은 문제를 푸는 코드가 둘 있는데 하나는 1초, 다른 하나는 1시간이 걸립니다. 무엇이 그 차이를 만드나요?

> 알고리즘은 "유한한 단계로 입력을 출력으로 바꾸는 명확한 절차"입니다. 단순히 코드를 작성하는 것과 알고리즘을 설계하는 것은 다른 활동입니다. 알고리즘 설계는 자료구조 위에서 어떤 절차로 문제를 풀지, 그 절차의 비용은 얼마인지, 동일한 문제를 더 좋은 방법으로 풀 수 있는지를 따집니다. 이 시리즈는 그 사고의 어휘와 패턴을 정리합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 알고리즘의 형식적 정의와 다섯 가지 조건
- 알고리즘과 자료구조의 관계
- "좋은 알고리즘"의 의미(정확성·효율성·단순성)
- 알고리즘적 사고가 코딩과 다른 점

## 왜 중요한가

같은 문제도 알고리즘 선택에 따라 성능 차이가 100배, 10000배가 됩니다. 인프라 확장으로 만회하기 어렵고, 한번 잘못 고르면 시스템의 상한선이 됩니다. 알고리즘적 사고는 코드를 짧게 만드는 기술이 아니라, 문제를 분해하고 해법의 비용을 미리 예측하는 기술입니다.

> 좋은 코드 ≠ 좋은 알고리즘. 알고리즘은 코드 이전의 결정입니다.

## 개념 한눈에 보기

> 알고리즘은 입력을 받아서 출력을 만들기 위한 일련의 단계입니다. 같은 문제를 풀더라도 단계의 구성에 따라 비용이 달라집니다. 자료구조가 "데이터를 어떻게 보관할지"를 결정한다면, 알고리즘은 "데이터로 무엇을 할지"를 결정합니다.

```text
입력 → [알고리즘: 단계의 나열] → 출력
        │
        ├─ 단계 수가 적으면 빠름
        ├─ 메모리를 적게 쓰면 가벼움
        └─ 잘못된 단계가 있으면 정답이 아님
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 입력(input) | 알고리즘이 받는 데이터 |
| 출력(output) | 알고리즘이 만드는 결과 |
| 유한성 | 항상 유한한 단계 안에 종료 |
| 명확성 | 각 단계가 모호함 없이 정의 |
| 효율성 | 시간과 공간을 가능한 적게 사용 |

## Before / After

**Before — 단순 반복으로 평균 구하기:**

```python
def average(nums):
    total = 0
    for n in nums:
        total += n
    return total / len(nums) if nums else 0
```

**After — 동일한 문제를 라이브러리로:**

```python
from statistics import fmean
average = lambda nums: fmean(nums) if nums else 0
```

같은 문제를 푸는 알고리즘이지만, "어떻게 푸는가"가 다릅니다. 알고리즘 설계는 늘 "더 나은 방법은 없는가"를 묻습니다.

## 실습: 단계별로 따라하기

### 1단계: 알고리즘의 다섯 조건 점검

```python
def find_max(nums):
    """최댓값 찾기 - 다섯 조건 모두 만족"""
    if not nums:
        return None              # 명확성: 빈 입력 처리 정의
    current_max = nums[0]        # 입력으로부터 시작
    for n in nums[1:]:           # 유한 단계
        if n > current_max:      # 명확한 비교
            current_max = n
    return current_max           # 출력 정의

print(find_max([3, 1, 4, 1, 5, 9, 2, 6]))   # 9
```

입력, 출력, 유한성, 명확성, 효율성 — 다섯 조건을 모두 만족해야 알고리즘입니다.

### 2단계: 같은 문제, 다른 알고리즘

```python
# 방법 1: 정렬 후 마지막 원소
def max_by_sort(nums):
    return sorted(nums)[-1]

# 방법 2: 한 번 순회
def max_by_scan(nums):
    m = nums[0]
    for n in nums[1:]:
        if n > m:
            m = n
    return m

# 방법 3: 재귀 분할 정복
def max_by_divide(nums):
    if len(nums) == 1:
        return nums[0]
    mid = len(nums) // 2
    left = max_by_divide(nums[:mid])
    right = max_by_divide(nums[mid:])
    return left if left > right else right

data = [3, 1, 4, 1, 5, 9, 2, 6]
print(max_by_sort(data), max_by_scan(data), max_by_divide(data))
```

세 알고리즘 모두 정답을 반환하지만 비용이 다릅니다. 정렬은 O(n log n), 순회는 O(n), 분할 정복은 O(n)이지만 호출 비용이 더 큽니다.

### 3단계: 정확성 검증

```python
import random

def reference(nums):
    return max(nums)

for _ in range(1000):
    data = [random.randint(-1000, 1000) for _ in range(random.randint(1, 100))]
    assert max_by_sort(data) == reference(data)
    assert max_by_scan(data) == reference(data)
    assert max_by_divide(data) == reference(data)

print("모든 알고리즘이 reference와 일치")
```

알고리즘이 빠르더라도 틀리면 의미가 없습니다. 정확성 검증은 효율성 분석보다 먼저입니다.

### 4단계: 비용 측정

```python
import time

def measure(fn, data, label):
    start = time.perf_counter()
    fn(data)
    print(f"{label:20s}: {(time.perf_counter() - start) * 1000:.2f} ms")

big = [random.randint(-10**6, 10**6) for _ in range(100_000)]
measure(max_by_sort, big, "sort")
measure(max_by_scan, big, "scan")
measure(max, big, "builtin max")
```

빅오뿐 아니라 실제 측정으로 알고리즘의 비용을 확인합니다. 표준 내장 함수가 거의 항상 가장 빠릅니다.

### 5단계: 알고리즘적 사고 적용

```python
# 문제: 정수 배열에서 두 수의 합이 target이 되는 인덱스 쌍
# 첫 번째 시도: 이중 루프 O(n^2)
def two_sum_naive(nums, target):
    for i, x in enumerate(nums):
        for j in range(i + 1, len(nums)):
            if x + nums[j] == target:
                return (i, j)
    return None

# 더 나은 방법: 해시 테이블 O(n)
def two_sum_hash(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        complement = target - x
        if complement in seen:
            return (seen[complement], i)
        seen[x] = i
    return None

print(two_sum_hash([2, 7, 11, 15], 9))   # (0, 1)
```

같은 문제에서 자료구조를 도입하면 시간 복잡도가 한 차원 떨어집니다. 알고리즘 설계와 자료구조 선택은 분리할 수 없습니다.

## 이 코드에서 주목할 점

- 알고리즘은 "무엇을"이 아니라 "어떻게"를 결정합니다
- 같은 문제도 여러 알고리즘이 존재하며 비용이 다릅니다
- 정확성 검증이 효율성 분석보다 먼저입니다
- 자료구조의 도움으로 알고리즘이 한 단계 빨라질 수 있습니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| "동작하면 끝" | 비효율로 시스템 한계 | 비용 분석 후 채택 |
| 빅오만 본다 | 상수 무시, 캐시 무시 | 측정으로 검증 |
| 자료구조 무시 | 같은 알고리즘이 한 차원 느림 | 자료구조와 같이 설계 |
| 라이브러리 무시 | 검증 안 된 직접 구현 | 표준 함수 우선 |
| 종료 조건 빠뜨림 | 무한 루프 | 유한성 직접 확인 |

## 실무에서는 이렇게 쓰입니다

- 검색 엔진 랭킹: 정렬·집합 연산·그래프 알고리즘의 결합
- 결제 시스템: 거래 매칭·중복 제거·우선순위 큐 알고리즘
- 추천 시스템: 행렬 분해·근접 이웃 탐색 알고리즘
- 라우팅: 다익스트라·A*·Bellman-Ford
- 컴파일러: 토큰화·파싱·최적화 알고리즘

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 코드를 작성하기 전에 "이건 알고리즘 문제인가?"를 묻습니다. 그렇다면 자료구조와 함께 비용을 먼저 추정하고, 가장 단순한 정답 알고리즘부터 시작합니다. 측정 후 병목이 보일 때만 더 정교한 알고리즘으로 교체합니다.

또한 시니어는 "정답성 → 가독성 → 효율성"의 우선순위를 지킵니다. 빠르지만 틀린 알고리즘이나 빠르지만 읽을 수 없는 알고리즘은 시스템을 망칩니다. 알고리즘은 결국 다른 사람이 읽고 유지보수할 코드입니다.

## 체크리스트

- [ ] 알고리즘의 다섯 조건을 말할 수 있는가
- [ ] 같은 문제에 여러 알고리즘이 있을 수 있음을 이해했는가
- [ ] 자료구조와 알고리즘이 함께 비용을 결정함을 알고 있는가
- [ ] 정확성 검증이 효율성 분석보다 먼저임을 동의하는가
- [ ] 표준 라이브러리부터 시작하는 습관을 갖고 있는가

## 연습 문제

1. 정수 배열에서 두 번째로 큰 값을 구하는 알고리즘을 두 가지 방법으로 작성하세요. 정렬 기반과 한 번 순회 기반. 각각의 시간 복잡도와 실제 측정값을 비교합니다.

2. 문자열에서 가장 자주 등장한 문자를 찾는 알고리즘을 작성하세요. (a) 이중 루프, (b) 카운터 dict 두 가지로 구현하고 시간 차이를 측정합니다.

3. 좋아하는 코드 한 편을 골라 그 안의 알고리즘을 한 줄로 요약해 보세요. "어떤 입력을 어떤 출력으로 어떤 절차로 바꾸는가"를 명시적으로 적습니다.

## 정리 및 다음 단계

알고리즘은 입력을 출력으로 바꾸는 명확한 절차이며, 자료구조 위에서 동작합니다. 같은 문제도 여러 알고리즘이 존재하고 그 비용이 다르므로, "동작하는가"가 아니라 "어떤 비용으로 동작하는가"를 함께 묻는 사고가 알고리즘 설계의 핵심입니다.

다음 글에서는 알고리즘의 비용을 정량적으로 분석하는 도구인 시간 복잡도와 공간 복잡도를 살펴봅니다. 빅오 표기법, 평균·최악·분할 상환의 차이, 그리고 이론과 측정을 함께 보는 법을 다룹니다.

- **알고리즘이란 무엇인가? (현재 글)**
- 시간 복잡도와 공간 복잡도 (예정)
- 탐색 알고리즘 (예정)
- 정렬 알고리즘 (예정)
- 재귀와 분할 정복 (예정)
- 동적 계획법 (예정)
- 그리디 알고리즘 (예정)
- 그래프 알고리즘 (예정)
- 문자열 알고리즘 기초 (예정)
- 알고리즘 문제 풀이 전략 (예정)
## 참고 자료

- [Wikipedia — Algorithm](https://en.wikipedia.org/wiki/Algorithm)
- [CLRS — Introduction to Algorithms (3rd ed.)](https://mitpress.mit.edu/9780262033848/introduction-to-algorithms/)
- [Sedgewick & Wayne — Algorithms 4ed](https://algs4.cs.princeton.edu/home/)
- [Open Data Structures](https://opendatastructures.org/)

Tags: Computer Science, 알고리즘, 문제 해결, 기초, 설계, 사고법

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
