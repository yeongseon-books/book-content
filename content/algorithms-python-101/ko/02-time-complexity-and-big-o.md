---
series: algorithms-python-101
episode: 2
title: "Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - Algorithms
  - Time Complexity
  - Big-O
  - Performance
seo_description: 시간 복잡도와 Big-O 표기법으로 알고리즘 성능을 객관적으로 분석합니다. 입력 증가에 따른 시간 변화를 파이썬 예제로 비교하는 법을 배웁니다.
last_reviewed: '2026-05-12'
---

# Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O

내 노트북에서 몇 초가 걸렸는지만으로 알고리즘을 평가하는 것은 위험합니다. 하드웨어도 바뀌고, 런타임도 바뀌고, 테스트 데이터도 바뀌지만, 입력이 커질 때 실행 시간이 얼마나 빨리 증가하는지는 그대로 남기 때문입니다.

이 글은 Algorithms with Python 101 시리즈의 두 번째 글입니다. 여기서는 시간 복잡도에 대한 감을 잡고, Big-O 표기법으로 알고리즘을 더 엄밀하게 비교해 보겠습니다.

Big-O는 코드를 실서비스에 넣기 전이나 코딩 테스트 화이트보드 앞에 서기 전에도 성장 패턴을 비교할 수 있게 해 주는 실용적인 언어입니다.


![Algorithms with Python 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/02/02-01-big-picture.ko.png)
*Algorithms with Python 101 2장 흐름 개요*

## 먼저 던지는 질문

- 시간 복잡도는 무엇이며, 실제 실행 시간만으로는 왜 부족할까요?
- Big-O 표기법은 어떻게 읽고 써야 할까요?
- `O(1)`부터 `O(n!)`까지의 대표 복잡도는 어떻게 구분할까요?

## 왜 중요한가

"이 코드는 느립니다"라는 말만으로는 부족합니다. Big-O는 하드웨어와 무관하게 알고리즘의 확장성을 설명하는 정밀한 언어입니다. `O(n)` 알고리즘은 1천만 개의 데이터도 감당할 수 있지만, `O(n^2)` 알고리즘은 10만 개만 되어도 급격히 버거워집니다.

> Big-O 표기법은 입력 크기가 무한히 커질 때 알고리즘 실행 시간의 최악 성장률을, 상수항과 낮은 차수항을 무시하고 표현합니다.

시간 복잡도를 이해하는 일은 코딩 테스트, 코드 리뷰, 시스템 설계에서 이루어지는 거의 모든 알고리즘 대화의 출발점입니다.

## 개념 한눈에 보기

> Big-O = 알고리즘 실행 시간 증가율의 상한

```text
Input Size vs Operations (approximate):
n=1,000  | O(1): 1       | O(log n): 10    | O(n): 1,000
         | O(n log n): 10,000 | O(n^2): 1,000,000 | O(2^n): ∞
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Time complexity | 입력 크기에 따라 실행 시간이 얼마나 늘어나는지를 나타냅니다 |
| Big-O notation | 최악의 성장률을 표현하는 상한 표기입니다 |
| O(1) — constant | 입력 크기와 무관하게 시간이 거의 일정합니다 |
| O(n) — linear | 실행 시간이 입력 크기에 비례해 증가합니다 |
| O(n^2) — quadratic | 실행 시간이 입력 크기의 제곱에 비례해 증가합니다 |

## Before / After

컬렉션 안에 값이 있는지 확인하는 두 가지 방법입니다.

```python
# before: linear search in a list — O(n)
def contains(data: list, target) -> bool:
    for item in data:
        if item == target:
            return True
    return False
```

```python
# after: lookup in a set — O(1) average
def contains(data: set, target) -> bool:
    return target in data
```

## 단계별 실습

### Step 1: O(1) — Constant Time

```python
def get_first(data: list) -> int:
    """Access the first element — O(1)."""
    return data[0]

def get_by_key(data: dict, key: str):
    """Dictionary lookup — O(1) average."""
    return data.get(key)

numbers = list(range(1_000_000))
print(get_first(numbers))  # 0

lookup = {"name": "Alice", "age": 30}
print(get_by_key(lookup, "name"))  # Alice
```

배열의 첫 원소 접근이나 해시 기반 딕셔너리 조회처럼, 입력이 커져도 비용이 거의 늘지 않는 연산이 `O(1)`입니다.

### Step 2: O(n) — Linear Time

```python
def linear_sum(data: list[int]) -> int:
    """Sum all elements — O(n)."""
    total = 0
    for x in data:
        total += x
    return total

def find_value(data: list[int], target: int) -> int:
    """Linear search — O(n)."""
    for i, val in enumerate(data):
        if val == target:
            return i
    return -1

data = list(range(100))
print(linear_sum(data))       # 4950
print(find_value(data, 42))   # 42
```

데이터를 처음부터 끝까지 한 번 훑어야 하면 보통 `O(n)`입니다. 입력이 두 배가 되면 대체로 실행 시간도 두 배 가까이 늘어납니다.

### Step 3: O(n^2) — Quadratic Time

```python
def bubble_sort(data: list[int]) -> list[int]:
    """Bubble sort — O(n^2)."""
    arr = data[:]
    n = len(arr)
    for i in range(n):
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def all_pairs(data: list) -> int:
    """Count all pairs — O(n^2)."""
    count = 0
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            count += 1
    return count

print(bubble_sort([5, 3, 8, 1, 2]))  # [1, 2, 3, 5, 8]
print(all_pairs(list(range(100))))    # 4950
```

중첩 반복문이 들어가면 가장 먼저 `O(n^2)` 가능성을 의심해야 합니다. 입력이 커질수록 선형 알고리즘과의 차이가 매우 빠르게 벌어집니다.

### Step 4: O(log n) and O(n log n)

```python
def binary_search(sorted_data: list[int], target: int) -> int:
    """Binary search — O(log n)."""
    left, right = 0, len(sorted_data) - 1
    while left <= right:
        mid = (left + right) // 2
        if sorted_data[mid] == target:
            return mid
        elif sorted_data[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

data = list(range(1_000_000))
print(binary_search(data, 999_999))  # 999999

# Python's built-in sort is O(n log n) — Timsort
import random
random_data = [random.randint(0, 1000) for _ in range(1000)]
sorted_data = sorted(random_data)  # O(n log n)
print(sorted_data[:5])
```

이진 탐색처럼 문제 공간을 절반씩 줄이는 알고리즘은 `O(log n)`입니다. 정렬처럼 분할과 병합이 결합된 많은 알고리즘은 `O(n log n)`에 속합니다.

### Step 5: Empirical Measurement

```python
import time

def measure(func, *args) -> float:
    start = time.perf_counter()
    func(*args)
    return time.perf_counter() - start

sizes = [1_000, 5_000, 10_000]
for n in sizes:
    data = list(range(n))
    t_linear = measure(linear_sum, data)
    t_quadratic = measure(all_pairs, data)
    ratio = t_quadratic / t_linear if t_linear > 0 else 0
    print(f"n={n:>6}: linear={t_linear:.5f}s  quadratic={t_quadratic:.5f}s  ratio={ratio:.0f}x")
```

실측 시간은 환경 영향을 받지만, 입력이 커질수록 어떤 알고리즘의 증가율이 훨씬 가파른지는 분명하게 드러납니다. 그래서 이론과 실측을 함께 보는 연습이 중요합니다.

## 이 코드에서 먼저 봐야 할 점

- 딕셔너리 조회 같은 `O(1)` 연산은 데이터가 커져도 비용이 거의 일정합니다.
- `O(n)`과 `O(n^2)`는 작은 입력에서는 비슷해 보여도, `n=10,000` 수준만 가도 차이가 압도적으로 커집니다.
- 이진 탐색은 `O(log n)`의 대표 예시입니다. 100만 개 데이터도 비교 횟수는 대략 20번 수준입니다.
- Python의 `sorted()`는 `O(n log n)`인 Timsort를 사용합니다.

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| `O(n)`과 `O(1)`을 혼동함 | 리스트와 집합의 조회 비용은 다릅니다 | 자료구조별 연산 복잡도를 익힙니다 |
| 중첩 반복문을 놓침 | 내부 루프 때문에 전체가 `O(n^2)`가 됩니다 | 중첩 깊이를 세어 봅니다 |
| 숨은 비용을 무시함 | 리스트에서 `in`은 `O(n)`입니다 | 자료구조의 복잡도 표를 확인합니다 |
| 너무 이른 미세 최적화 | 큰 병목은 놔두고 작은 부분만 손봅니다 | 먼저 가장 큰 병목을 찾습니다 |
| 최선/평균/최악을 섞어 말함 | Big-O 관례와 설명이 어긋납니다 | 어떤 경우를 말하는지 명확히 합니다 |

## 실무에서는 이렇게 연결됩니다

- 데이터베이스 쿼리 플래너는 시간 복잡도 관점에서 인덱스를 선택합니다.
- 검색 엔진은 역색인 조회에 해시 기반 `O(1)` 접근을 활용합니다.
- 추천 순위 계산에서는 `O(n log n)` 정렬이 자주 등장합니다.
- 네트워크 라우터는 포워딩 테이블 탐색에 로그 시간 구조를 사용합니다.
- 머신러닝 학습 시간도 결국 알고리즘 복잡도의 영향을 받습니다.

## 현업에서는 이렇게 생각합니다

모든 복잡도 계열을 외우는 것이 목적은 아닙니다. 더 중요한 것은 감을 만드는 일입니다. 입력을 두 배로 늘렸을 때 실행 시간이 두 배인지, 네 배인지, 거의 안 늘어나는지를 떠올릴 수 있어야 합니다.

코드 리뷰에서 숙련된 엔지니어는 큰 데이터 위의 중첩 루프를 보면 바로 복잡도를 묻습니다. 이 습관 하나가 많은 성능 문제를 배포 전에 막아 줍니다.

## 체크리스트

- [ ] Big-O 표기법이 무엇을 표현하는지 설명할 수 있습니다
- [ ] 간단한 Python 코드의 시간 복잡도를 식별할 수 있습니다
- [ ] 대표 복잡도 계열을 빠른 순서대로 비교할 수 있습니다
- [ ] 중첩 루프에서 `O(n)`과 `O(n^2)`를 구분할 수 있습니다
- [ ] 알고리즘 성능을 실측하고 비교할 수 있습니다

## 연습 문제

1. Python의 `list.index()`와 `dict.__getitem__()`의 시간 복잡도를 분석해 보세요.
2. 리스트에서 중복을 찾는 `O(n)` 알고리즘을 작성해 보세요. 힌트는 `set`입니다.
3. `n=10,000`에서 1초가 걸리는 `O(n^2)` 알고리즘이 `n=100,000`에서는 얼마나 걸릴지 예측해 보세요.

## 정리와 다음 글

시간 복잡도와 Big-O 표기법은 알고리즘 성능을 비교하는 공통 언어입니다. 특히 기억해야 할 계열은 `O(1)`, `O(log n)`, `O(n)`, `O(n log n)`, `O(n^2)`입니다. 다음 글에서는 가장 대표적인 두 탐색 알고리즘인 선형 탐색과 이진 탐색을 구현하고 비교합니다.

## 실전 패턴 추가: 정렬과 탐색 구현을 문제 유형별로 선택하기

알고리즘 문제에서는 코드 길이보다 선택 기준이 더 중요합니다. 입력 크기, 데이터 분포, 정렬 여부에 따라 정렬/탐색 전략이 달라집니다. 아래 예시는 같은 정수 배열을 다루더라도 어떤 조건에서 어떤 구현을 고르는지 보여 줍니다.

```python
def binary_search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def merge_sort(nums: list[int]) -> list[int]:
    if len(nums) <= 1:
        return nums
    mid = len(nums) // 2
    left = merge_sort(nums[:mid])
    right = merge_sort(nums[mid:])

    merged: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quick_sort(nums: list[int]) -> list[int]:
    if len(nums) <= 1:
        return nums
    pivot = nums[len(nums) // 2]
    less = [x for x in nums if x < pivot]
    equal = [x for x in nums if x == pivot]
    greater = [x for x in nums if x > pivot]
    return quick_sort(less) + equal + quick_sort(greater)
```

실무 판단은 보통 이렇게 정리됩니다. 이미 정렬된 리스트에서 존재 여부를 반복 조회하면 이진 탐색이 기본 선택입니다. 입력이 계속 바뀌고 안정 정렬이 필요하면 병합 정렬 계열이 유리하고, 평균 성능과 구현 단순성을 우선하면 퀵 정렬 계열이 자주 선택됩니다. 코딩 테스트에서는 Python 내장 `sort()`가 Timsort 기반이라 거의 항상 가장 실용적인 기본값이지만, 원리를 직접 구현해 보면 경계 조건과 복잡도 해석 능력이 크게 좋아집니다.

## 심화 실전 노트: Big-O를 문제 선택 도구로 쓰는 법

### 구현 앵커: 연산 카운터로 성장률 관찰하기

```python
def count_linear_ops(n: int) -> int:
    ops = 0
    data = list(range(n))
    for _ in data:
        ops += 1
    return ops


def count_quadratic_ops(n: int) -> int:
    ops = 0
    for i in range(n):
        for j in range(i + 1, n):
            ops += 1
    return ops


for n in [100, 500, 1_000]:
    linear = count_linear_ops(n)
    quadratic = count_quadratic_ops(n)
    print(f"n={n:>5} | linear_ops={linear:>8} | quadratic_ops={quadratic:>10}")
```

실행 시간은 환경 영향을 받지만, 연산 카운트는 성장 패턴을 직관적으로 보여 줍니다.

### 시각 추적: 입력 증가에 따른 기울기

```text
n=100   -> O(n)=100,     O(n^2)=4,950
n=500   -> O(n)=500,     O(n^2)=124,750
n=1000  -> O(n)=1,000,   O(n^2)=499,500
```

입력을 10배 늘렸을 때 선형은 10배, 제곱은 100배로 늘어납니다. Big-O의 핵심은 절대 시간보다 기울기입니다.

### 복잡도 선택표: 제약으로 알고리즘 거르기

| 최대 입력 `N` | 우선 검토 복잡도 | 회피해야 할 복잡도 |
|---------------|------------------|--------------------|
| 1,000 | `O(n^2)` 가능 | `O(2^n)` |
| 100,000 | `O(n log n)` 이하 | `O(n^2)` |
| 1,000,000 | `O(n)` 중심 | `O(n log n)`도 상수 비용 점검 필요 |

### 인터뷰형 설명 템플릿

- "현재 접근은 중첩 루프 때문에 `O(n^2)`입니다."
- "제약이 `n=200,000`이므로 `O(n^2)`는 탈락입니다."
- "정렬 + 단일 순회로 `O(n log n)`까지 낮추겠습니다."
- "가능하면 해시로 `O(n)`도 검토하겠습니다."

면접에서는 수학 공식보다 이런 결정을 빠르게 말하는 능력이 더 중요합니다.

### 간단 증명: `n log n`이 `n^2`보다 유리한 이유

`n >= 2`에서 `log2 n < n`이므로 `n log n < n^2`가 성립합니다. 따라서 입력이 커질수록 `O(n log n)` 접근이 `O(n^2)`보다 확실히 유리합니다. 이는 정렬 기반 풀이가 대규모 입력에서 여전히 실용적인 이유를 설명합니다.

### 실수-수정 페어

| 실수 | 결과 | 수정 |
|------|------|------|
| 리스트 조회를 `O(1)`로 착각 | 시간 초과 | 자료구조별 복잡도 표 확인 |
| 평균 복잡도와 최악 복잡도 혼동 | 설명 불일치 | 어떤 기준인지 먼저 선언 |
| 상수 최적화에 과몰입 | 큰 병목 방치 | 복잡도 차수를 먼저 낮춤 |

## 실전 검증 부록: 성능 측정과 반례 설계

알고리즘 학습에서 구현 자체보다 오래 남는 자산은 검증 습관입니다. 아래 체크는 주제와 무관하게 거의 모든 문제에서 공통으로 적용됩니다.

### 1) 마이크로 벤치마크 규칙

```python
import time


def benchmark(func, *args, repeat: int = 5) -> float:
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        func(*args)
        best = min(best, time.perf_counter() - start)
    return best
```

- 단일 실행 시간은 노이즈가 큽니다.
- 최소/중앙값 기준으로 비교하는 편이 안정적입니다.
- 입력 크기를 여러 단계로 늘려 증가 추세를 기록해야 합니다.

### 2) 반례 세트 템플릿

```text
A. 최소 입력: 빈 배열, 원소 1개
B. 중복 입력: 같은 값 다수
C. 정렬/역정렬 입력: 경계 인덱스 오류 탐지
D. 음수/0 포함 입력: 비교식 방향 오류 탐지
E. 해답 없음 케이스: 종료 조건 검증
```

테스트를 통과했는지보다, 어떤 종류의 실패를 막았는지 기록하는 편이 품질에 더 직접적입니다.

### 3) 복잡도-메모리 트레이드오프 표

| 개선 전략 | 시간 영향 | 공간 영향 | 적용 판단 |
|-----------|-----------|-----------|-----------|
| 캐시/메모이제이션 | 감소 | 증가 | 중복 계산이 명확할 때 |
| 정렬 후 탐색 | 대체로 감소 | 동일/약간 증가 | 질의가 여러 번일 때 |
| 해시 사용 | 평균 감소 | 증가 | 순서보다 조회가 중요할 때 |
| 힙 사용 | 상위/최소 유지에 유리 | 증가 | 우선순위 선택이 핵심일 때 |

### 4) 인터뷰 답변 스크립트

- "먼저 입력 제약을 보고 가능한 복잡도 상한을 정하겠습니다."
- "현재 접근의 시간/공간 복잡도를 계산해 보겠습니다."
- "경계 입력 다섯 가지로 검증 계획을 먼저 제시하겠습니다."
- "필요하면 정답 유지 조건을 짧게 증명하겠습니다."

이 스크립트를 반복하면 설명의 밀도가 올라가고, 구현 중 길을 잃는 빈도가 줄어듭니다.

## 케이스 스터디 확장: 입력 규모가 커질 때의 판단

### 시나리오 1: 제약 기반 의사결정 로그

문제를 처음 읽을 때 정답 코드보다 먼저 남겨야 하는 기록은 입력 크기, 허용 복잡도, 실패 가능성이 큰 경계 조건입니다. 이 기록이 있으면 구현 도중 방향이 흔들려도 빠르게 복구할 수 있습니다.

| 항목 | 기록 예시 | 확인 이유 |
|------|-----------|-----------|
| 입력 상한 | `N=200000` | 중첩 루프 배제 판단 |
| 목표 복잡도 | `O(n log n)` 이하 | 시간 초과 예방 |
| 경계 조건 | 빈 입력/중복/음수 | 런타임 오류 예방 |

```python
def decision_log(n_max: int) -> str:
    if n_max <= 5_000:
        return "O(n^2)까지 검토"
    if n_max <= 200_000:
        return "O(n log n) 중심"
    return "O(n) 우선"

print(decision_log(200_000))
```

작은 보조 함수를 두면 문제별 판단 근거를 팀 문서와 코드 리뷰에 같은 형태로 남길 수 있습니다. 코딩 테스트 연습에서도 같은 틀을 반복하면 풀이 속도와 정확도가 함께 올라갑니다.

### 시나리오 2: 제약 기반 의사결정 로그

문제를 처음 읽을 때 정답 코드보다 먼저 남겨야 하는 기록은 입력 크기, 허용 복잡도, 실패 가능성이 큰 경계 조건입니다. 이 기록이 있으면 구현 도중 방향이 흔들려도 빠르게 복구할 수 있습니다.

| 항목 | 기록 예시 | 확인 이유 |
|------|-----------|-----------|
| 입력 상한 | `N=200000` | 중첩 루프 배제 판단 |
| 목표 복잡도 | `O(n log n)` 이하 | 시간 초과 예방 |
| 경계 조건 | 빈 입력/중복/음수 | 런타임 오류 예방 |

```python
def decision_log(n_max: int) -> str:
    if n_max <= 5_000:
        return "O(n^2)까지 검토"
    if n_max <= 200_000:
        return "O(n log n) 중심"
    return "O(n) 우선"

print(decision_log(200_000))
```

작은 보조 함수를 두면 문제별 판단 근거를 팀 문서와 코드 리뷰에 같은 형태로 남길 수 있습니다. 코딩 테스트 연습에서도 같은 틀을 반복하면 풀이 속도와 정확도가 함께 올라갑니다.

### 시나리오 3: 제약 기반 의사결정 로그

문제를 처음 읽을 때 정답 코드보다 먼저 남겨야 하는 기록은 입력 크기, 허용 복잡도, 실패 가능성이 큰 경계 조건입니다. 이 기록이 있으면 구현 도중 방향이 흔들려도 빠르게 복구할 수 있습니다.

| 항목 | 기록 예시 | 확인 이유 |
|------|-----------|-----------|
| 입력 상한 | `N=200000` | 중첩 루프 배제 판단 |
| 목표 복잡도 | `O(n log n)` 이하 | 시간 초과 예방 |
| 경계 조건 | 빈 입력/중복/음수 | 런타임 오류 예방 |

```python
def decision_log(n_max: int) -> str:
    if n_max <= 5_000:
        return "O(n^2)까지 검토"
    if n_max <= 200_000:
        return "O(n log n) 중심"
    return "O(n) 우선"

print(decision_log(200_000))
```

작은 보조 함수를 두면 문제별 판단 근거를 팀 문서와 코드 리뷰에 같은 형태로 남길 수 있습니다. 코딩 테스트 연습에서도 같은 틀을 반복하면 풀이 속도와 정확도가 함께 올라갑니다.

### 시나리오 4: 제약 기반 의사결정 로그

문제를 처음 읽을 때 정답 코드보다 먼저 남겨야 하는 기록은 입력 크기, 허용 복잡도, 실패 가능성이 큰 경계 조건입니다. 이 기록이 있으면 구현 도중 방향이 흔들려도 빠르게 복구할 수 있습니다.

| 항목 | 기록 예시 | 확인 이유 |
|------|-----------|-----------|
| 입력 상한 | `N=200000` | 중첩 루프 배제 판단 |
| 목표 복잡도 | `O(n log n)` 이하 | 시간 초과 예방 |
| 경계 조건 | 빈 입력/중복/음수 | 런타임 오류 예방 |

```python
def decision_log(n_max: int) -> str:
    if n_max <= 5_000:
        return "O(n^2)까지 검토"
    if n_max <= 200_000:
        return "O(n log n) 중심"
    return "O(n) 우선"

print(decision_log(200_000))
```

작은 보조 함수를 두면 문제별 판단 근거를 팀 문서와 코드 리뷰에 같은 형태로 남길 수 있습니다. 코딩 테스트 연습에서도 같은 틀을 반복하면 풀이 속도와 정확도가 함께 올라갑니다.

### 시나리오 5: 제약 기반 의사결정 로그

문제를 처음 읽을 때 정답 코드보다 먼저 남겨야 하는 기록은 입력 크기, 허용 복잡도, 실패 가능성이 큰 경계 조건입니다. 이 기록이 있으면 구현 도중 방향이 흔들려도 빠르게 복구할 수 있습니다.

| 항목 | 기록 예시 | 확인 이유 |
|------|-----------|-----------|
| 입력 상한 | `N=200000` | 중첩 루프 배제 판단 |
| 목표 복잡도 | `O(n log n)` 이하 | 시간 초과 예방 |
| 경계 조건 | 빈 입력/중복/음수 | 런타임 오류 예방 |

```python
def decision_log(n_max: int) -> str:
    if n_max <= 5_000:
        return "O(n^2)까지 검토"
    if n_max <= 200_000:
        return "O(n log n) 중심"
    return "O(n) 우선"

print(decision_log(200_000))
```

작은 보조 함수를 두면 문제별 판단 근거를 팀 문서와 코드 리뷰에 같은 형태로 남길 수 있습니다. 코딩 테스트 연습에서도 같은 틀을 반복하면 풀이 속도와 정확도가 함께 올라갑니다.

## 처음 질문으로 돌아가기

- **시간 복잡도는 무엇이며, 실제 실행 시간만으로는 왜 부족할까요?**
  - 본문의 기준은 시간 복잡도와 Big-O를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Big-O 표기법은 어떻게 읽고 써야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`O(1)`부터 `O(n!)`까지의 대표 복잡도는 어떻게 구분할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- **시간 복잡도와 Big-O (현재 글)**
- 선형 탐색과 이진 탐색 (예정)
- 정렬 알고리즘 (예정)
- 재귀와 분할 정복 (예정)
- 동적 계획법 기초 (예정)
- 그래프 탐색 — BFS와 DFS (예정)
- 최단 경로 기초 (예정)
- 그리디 알고리즘 (예정)
- 코딩 테스트 문제 접근법 (예정)

<!-- toc:end -->

## 참고 자료

- [Python Documentation — Time Complexity](https://wiki.python.org/moin/TimeComplexity)
- [Real Python — Big O Notation in Python](https://realpython.com/sorting-algorithms-python/)
- [GeeksforGeeks — Analysis of Algorithms | Big-O Analysis](https://www.geeksforgeeks.org/analysis-algorithms-big-o-analysis/)
- [Khan Academy — Asymptotic Notation](https://www.khanacademy.org/computing/computer-science/algorithms/asymptotic-notation)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-python-101/ko/02-time-complexity-and-big-o)

Tags: Python, Algorithms, Time Complexity, Big-O, Performance
