---
series: algorithms-101
episode: 1
title: "Algorithms 101 (1/10): 알고리즘이란 무엇인가?"
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
  - 기초
  - 문제 해결
  - 의사코드
  - 정확성
seo_description: 알고리즘이 무엇인지, 프로그램과 어떻게 다른지, 그리고 정확성·유한성·효율성이 왜 핵심 조건인지 정리합니다.
last_reviewed: '2026-05-12'
---

# Algorithms 101 (1/10): 알고리즘이란 무엇인가?

현대 하드웨어가 충분히 빠른데도 왜 여전히 좋은 알고리즘이 중요할까요? 여기서는 알고리즘이 무엇인지, 프로그램과 어떻게 다른지, 그리고 이후 시리즈 전체를 떠받치는 핵심 용어를 정리합니다.

이 글은 Algorithms 101 시리즈의 첫 번째 글입니다.

![Algorithms 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/01/01-01-big-picture.ko.png)
*Algorithms 101 1장 흐름 개요*

## 이 글에서 다룰 문제

- 알고리즘이 반드시 만족해야 하는 세 가지 조건은 무엇일까요?
- 알고리즘과 프로그램은 어떻게 다를까요?
- 왜 알고리즘 설계에서는 의사코드가 중요한 작업 언어가 될까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

운영에서 "시스템이 느리다"로 보이는 문제의 상당수는 사실 "알고리즘이 입력 크기에 맞게 확장되지 않는다"는 문제입니다. 테스트 데이터에서는 괜찮았던 선형 탐색 하나가, 실제로 수천만 건을 만나는 순간 병목이 되곤 합니다. 알고리즘의 언어를 익히는 것은 시스템이 현실적인 부하를 견딜지 미리 예측하는 첫걸음입니다.

> 알고리즘은 문제와 해법 사이의 계약입니다.

> 알고리즘은 세 가지 의무를 집니다. 모든 유효한 입력에 대해 올바른 출력을 내야 하고(정확성), 유한한 시간과 메모리 안에서 끝나야 하며(유한성), 입력이 커져도 감당 가능한 비용으로 동작해야 합니다(효율성). 프로그램은 여기에 구체적인 문법, 실행 환경, 부작용이 더해진 형태이고, 알고리즘은 그 뒤에 있는 추상적 절차입니다.

```text
Problem  →  Algorithm  →  Program  →  Execution
                  (correctness, finiteness, efficiency)
```

| 용어 | 설명 |
| --- | --- |
| 알고리즘 | 입력을 출력으로 바꾸는 유한하고 모호하지 않은 단계의 집합 |
| 정확성 | 모든 유효한 입력에 대해 올바른 출력을 만드는 성질 |
| 유한성 | 유한한 시간과 메모리 안에서 종료되는 성질 |
| 의사코드 | 특정 언어에 묶이지 않는 알고리즘 설계 표기법 |
| 효율성 | 입력 크기에 따라 비용이 어떻게 증가하는지 |

## 개선 전 / 개선 후

**Before — "내 컴퓨터에서는 된다" 수준의 코드:**

```python
def find(arr, x):
    for v in arr:
        if v == x:
            return True
    return False
# 100개 항목에서는 괜찮지만 10^8개 항목에서는 형편없습니다.
```

**After — 입력 크기에 맞는 알고리즘 선택:**

```python
def find(sorted_arr, x):
    import bisect
    i = bisect.bisect_left(sorted_arr, x)
    return i < len(sorted_arr) and sorted_arr[i] == x
# 정렬된 배열에서 O(log n)
```

같은 문제라도 어떤 알고리즘을 선택하느냐에 따라 비용 계층이 완전히 달라집니다.

## 단계별로 따라가기

### 1단계: 유한성 확인

```python
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

print(gcd(48, 36))   # 12
```

유클리드 알고리즘은 매 단계마다 `b`가 엄격하게 줄어들기 때문에 반드시 종료합니다. `a % b < b`이므로 b는 단조 감소합니다. 유한성은 우연이 아니라 한 문장으로 설명할 수 있어야 하는 성질입니다.

### 2단계: 경계 입력에서 정확성 확인

```python
assert gcd(0, 5) == 5
assert gcd(5, 0) == 5
assert gcd(7, 7) == 7
assert gcd(12, 8) == 4
assert gcd(100, 75) == 25
```

정확성은 빈값, 같은 값, 극단값처럼 대표적인 입력 부류를 놓고 확인해야 합니다. 테스트가 통과했다는 말은, 올바른 입력 부류를 테스트했을 때만 의미가 있습니다.

### 3단계: 코딩 전에 효율성 추정

```text
n = 10^6, time budget = 1 second
→ O(n^2) is impossible     (10^12 operations)
→ O(n log n) or O(n) is required
→ O(n log n) ≈ 2 × 10^7 operations — feasible
```

입력 크기만 봐도 후보 알고리즘이 크게 좁혀집니다. 이 습관 하나가 대부분의 성능 사고를 미리 막아 줍니다.

### 4단계: 먼저 의사코드 작성

```text
Algorithm: find smallest in array
Input:  arr (non-empty list)
Output: minimum element

1. min ← arr[0]
2. for i in 1..len(arr)-1:
3.     if arr[i] < min:
4.         min ← arr[i]
5. return min

Invariant: after step i, min == minimum of arr[0..i]
```

의사코드는 논리에 집중하게 해 줍니다. 불변식(invariant)을 명시하면 정확성을 논증하기 훨씬 쉬워집니다. 단계가 명확해지면 Python으로 옮기는 일은 기계적 변환에 가까워집니다.

### 5단계: 의사코드를 Python으로 옮기기

```python
def find_minimum(arr):
    if not arr:
        raise ValueError("empty input")
    minimum = arr[0]
    for v in arr[1:]:
        if v < minimum:
            minimum = v
    return minimum

# 검증
assert find_minimum([3, 1, 4, 1, 5]) == 1
assert find_minimum([7]) == 7
assert find_minimum([-3, -1, -4]) == -4
```

### 6단계: 같은 문제를 두 알고리즘으로 비교

```python
import time, bisect

def measure(fn, *args, repeat=3):
    best = float('inf')
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn(*args)
        best = min(best, time.perf_counter() - t0)
    return best

n = 1_000_000
arr = list(range(n))
target = n - 1

t_linear = measure(lambda: arr.index(target))          # O(n)
t_binary = measure(lambda: bisect.bisect_left(arr, target))  # O(log n)

print(f"linear : {t_linear:.6f}s")
print(f"binary : {t_binary:.6f}s")
print(f"speedup: {t_linear / t_binary:.1f}x")
```

중요한 것은 절대 시간이 아니라 차수의 차이입니다. n=10^6에서 이진 탐색은 약 20번의 비교로 끝나지만 선형 탐색은 최대 백만 번 비교합니다.

## 알고리즘 접근법 Big-O 비교

| 접근 | 시간 복잡도 | 공간 복잡도 | 전제 조건 | 적합한 상황 |
| --- | --- | --- | --- | --- |
| 선형 탐색 | O(n) | O(1) | 없음 | 소규모, 비정렬 데이터 |
| 이진 탐색 | O(log n) | O(1) | 정렬된 배열 | 반복 조회, 정렬된 대규모 데이터 |
| 해시 기반 탐색 | O(1) 평균 | O(n) | 해시 가능 키 | 동등성 탐색, 빈도 계산 |
| 브루트포스 | O(n^2) 이상 | O(1)~O(n) | 없음 | n ≤ 1000인 프로토타입 |
| 분할 정복 | O(n log n) | O(log n) | 분해 가능 | 정렬, 거듭제곱, 대부분의 최적화 |

## 심화: 알고리즘 정확성 형식적으로 생각하기

알고리즘의 정확성을 주장하는 방법은 여러 가지입니다. 가장 실용적인 세 가지는 루프 불변식, 귀납적 증명, 반례 탐색입니다.

**루프 불변식 예시:**

```python
def insertion_sort(arr):
    """
    루프 불변식: 반복 i 직전에 arr[0..i-1]은 정렬되어 있다.
    초기화: i=1일 때 arr[0..0]은 길이 1이므로 자명하게 정렬됨.
    유지: 각 반복에서 arr[i]를 올바른 위치에 삽입해 arr[0..i]를 정렬 상태로 유지.
    종료: i=len(arr)에서 arr[0..n-1] 전체가 정렬됨.
    """
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

result = insertion_sort([5, 2, 4, 6, 1, 3])
assert result == [1, 2, 3, 4, 5, 6]
```

불변식을 적으면 버그 위치를 코드 전체가 아닌 불변식이 깨지는 구간으로 좁힐 수 있습니다.

**반례 탐색 패턴:**

```python
def brute_force_check(algorithm, oracle, inputs):
    """
    작은 입력에 대해 알고리즘 결과와 정답(oracle)을 비교해 반례를 탐색합니다.
    """
    for inp in inputs:
        got = algorithm(inp)
        expected = oracle(inp)
        if got != expected:
            print(f"반례: input={inp}, algorithm={got}, oracle={expected}")
            return inp
    print("테스트 범위에서 반례 없음")
    return None

# 예시: find_minimum 검증
import random
random.seed(42)
test_inputs = [[random.randint(-100, 100) for _ in range(random.randint(1, 20))]
               for _ in range(1000)]
brute_force_check(find_minimum, min, test_inputs)
```

1000개의 무작위 입력에 대해 정답(`min`)과 비교하는 방식은 알고리즘 초안을 빠르게 검증하는 실용적인 방법입니다.

## 알고리즘 설계 흐름 요약

```text
1. 문제 정의       : 입력 / 출력 / 제약 조건 명시
2. 효율성 추정     : 입력 크기 → 허용 복잡도 결정
3. 의사코드        : 언어 독립적 절차 기술 + 불변식 명시
4. 정확성 논증     : 루프 불변식 또는 귀납법
5. 구현            : 의사코드 → Python
6. 검증            : 경계 입력 + 무작위 테스트
7. 측정            : 예측한 복잡도와 실측 데이터 비교
```

이 흐름을 머릿속에 갖고 있으면, 막막한 문제도 단계별로 쪼개서 접근할 수 있습니다.

## 이 글에서 먼저 가져갈 점

- 같은 문제에도 비용이 전혀 다른 여러 알고리즘이 존재합니다.
- 의사코드는 "무엇을 할지"와 "어떻게 구현할지"를 분리해 줍니다.
- 정확성은 테스트 몇 개가 아니라 논증의 대상입니다.
- 유한성도 당연하게 가정하지 말고 검증해야 합니다.
- 불변식을 명시하는 습관이 버그를 예방합니다.

## 자주 하는 실수

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 비용을 추정하지 않고 바로 코딩 | 운영에서 시간 초과 | 입력 크기부터 보고 복잡도를 추정합니다 |
| 경계 입력 없이 "테스트는 통과함"이라고 판단 | 드문 입력에서 실패 | 빈 입력, 단일 입력, 극단값, 중복값을 포함합니다 |
| 빠른 언어가 나쁜 알고리즘을 덮어 줄 것이라 기대 | O(n²)는 결국 무너짐 | 언어보다 알고리즘 선택을 먼저 봅니다 |
| 코드를 복사해 놓고 알고리즘은 읽지 않음 | 숨은 가정 누락 | 먼저 의사코드로 절차를 이해합니다 |
| 한 입력에서 성공한 것을 정확성으로 착각 | 잠복 버그 | 대표 입력 부류 전체로 검증합니다 |
| 불변식을 명시하지 않음 | 디버깅 어려움 | 루프마다 유지되는 조건을 한 문장으로 적습니다 |

## 실무에서는 이렇게 쓰입니다

- API 성능 리뷰는 언어보다 알고리즘부터 봅니다.
- 데이터베이스의 sort, hash join, index scan도 결국 알고리즘입니다.
- 컴파일러 최적화는 한 알고리즘을 더 빠른 동등 알고리즘으로 바꾸는 일입니다.
- 머신러닝 학습 비용도 바닥에 있는 알고리즘 비용이 지배합니다.
- 느린 시스템을 디버깅하는 일은 종종 알고리즘 교체로 이어집니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 "버그가 무엇인가"보다 먼저 "여기서 쓰는 알고리즘이 무엇인가"를 묻습니다. 시스템이 느릴 때도 구현 미세 조정보다 입력 크기에 맞는 접근인지부터 확인합니다.

또한 어려운 로직일수록 코드보다 먼저 의사코드를 적습니다. 몇 분 동안 절차를 분명히 하는 일이, 나중에 한 시간짜리 디버깅을 없애 주기 때문입니다. 코드는 비교적 싼 작업이고, 진짜 설계는 알고리즘 단계에서 일어납니다.

불변식을 유지하는 코드는 변경에도 강합니다. "이 시점에서 `min`은 arr[0..i]의 최솟값"이라는 문장이 있으면, 코드를 수정할 때도 이 불변식을 보존하는지 확인하면 됩니다.

## 운영 체크리스트

- [ ] 이 알고리즘의 정확성 조건을 한 문장으로 말할 수 있는가
- [ ] 유한성을 한 문장으로 설명할 수 있는가
- [ ] 코딩 전에 복잡도를 추정했는가
- [ ] 루프 불변식을 명시했는가
- [ ] 같은 문제의 두 알고리즘을 같은 입력에서 비교할 수 있는가
- [ ] 특정 언어에 기대지 않고 의사코드를 쓸 수 있는가

## 연습 문제

1. 유클리드 알고리즘을 의사코드로 작성하고, 왜 반드시 종료하는지 한 문장으로 설명해 보세요. 그다음 Python으로 옮겨 세 가지 경계 입력으로 검증해 보세요.

2. 배열의 최댓값을 찾는 두 알고리즘, 즉 선형 탐색과 분할 정복 재귀를 각각 구현해 보세요. 입력 크기 10^4, 10^5, 10^6에서 측정하고, 둘 다 O(n)인데도 시간이 왜 달라지는지 설명해 보세요.

3. 최근에 작성한 작은 작업 하나를 골라 특정 언어 문법 없이 의사코드로 다시 써 보세요. 그 과정에서 어떤 가정을 명시적으로 드러내야 했는지 적어 보세요.

4. 아래 두 함수 중 어느 쪽이 입력 크기 n = 10^7에서 더 빠를지 복잡도 분석만으로 먼저 예측하고, 실제 측정으로 검증해 보세요.

```python
def approach_a(n):
    result = 0
    for i in range(n):
        result += i
    return result

def approach_b(n):
    return n * (n - 1) // 2
```

## 정리 및 다음 단계

알고리즘은 정확성, 유한성, 효율성으로 정의됩니다. 알고리즘은 모든 프로그램 뒤에 있는 추상적 절차이며, 시스템이 부하를 견딜 수 있는지를 결정하는 핵심입니다. 의사코드는 설계 언어이고, 구체적인 코드는 구현 세부사항입니다.

다음 글에서는 시간 복잡도와 공간 복잡도를 다룹니다. Big-O, Big-Omega, Big-Theta라는 공통 언어를 익히면 이후 시리즈 전체를 같은 기준으로 비교할 수 있습니다.

## 처음 질문으로 돌아가기

- **알고리즘이 반드시 만족해야 하는 세 가지 조건은 무엇일까요?**
  - 정확성(모든 유효한 입력에 대해 올바른 출력), 유한성(유한한 시간과 메모리 안에서 종료), 효율성(입력 크기에 따라 비용이 감당 가능하게 증가)입니다. 유클리드 알고리즘은 매 단계마다 `b`가 엄격하게 줄어들기 때문에 유한성이 보장됩니다.
- **알고리즘과 프로그램은 어떻게 다를까요?**
  - 알고리즘은 입력을 출력으로 바꾸는 추상적 절차이고, 프로그램은 그 절차를 특정 언어와 실행 환경에 맞게 구현한 결과입니다. 같은 알고리즘이 여러 언어로 구현될 수 있고, 같은 언어로 작성된 두 프로그램이 전혀 다른 알고리즘을 구현할 수 있습니다.
- **왜 알고리즘 설계에서는 의사코드가 중요한 작업 언어가 될까요?**
  - 의사코드는 언어 문법에서 해방되어 논리 구조와 불변식에 집중하게 해 줍니다. 몇 분 동안 의사코드로 절차를 명확히 하면, 나중에 발생할 수 있는 구현 버그를 구조적으로 예방할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- **Algorithms 101 (1/10): 알고리즘이란 무엇인가? (현재 글)**
- [Algorithms 101 (2/10): 시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [Algorithms 101 (3/10): 탐색 알고리즘](./03-search-algorithms.md)
- [Algorithms 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [Algorithms 101 (6/10): 동적 계획법](./06-dynamic-programming.md)
- [Algorithms 101 (7/10): 그리디 알고리즘](./07-greedy-algorithms.md)
- [Algorithms 101 (8/10): 그래프 알고리즘](./08-graph-algorithms.md)
- [Algorithms 101 (9/10): 문자열 알고리즘 기초](./09-string-algorithms.md)
- [알고리즘 문제 풀이 전략](./10-problem-solving-strategies.md)

<!-- toc:end -->

## 참고 자료

- [book-examples — algorithms-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-101/ko)
- [Wikipedia — Algorithm](https://en.wikipedia.org/wiki/Algorithm)
- [Donald Knuth — The Art of Computer Programming](https://www-cs-faculty.stanford.edu/~knuth/taocp.html)
- [CLRS — Introduction to Algorithms](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)
- [Sedgewick & Wayne — Algorithms 4ed](https://algs4.cs.princeton.edu/home/)

Tags: Computer Science, 알고리즘, 기초, 문제 해결, 의사코드, 정확성
