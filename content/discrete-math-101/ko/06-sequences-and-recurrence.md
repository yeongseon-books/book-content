---
series: discrete-math-101
episode: 6
title: "Discrete Math 101 (6/10): 수열과 점화식"
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
  - 이산수학
  - 점화식
  - 수열
  - 마스터 정리
  - 알고리즘 분석
seo_description: 수열, 점화식, 마스터 정리로 재귀 알고리즘의 시간 복잡도를 푸는 방법을 설명합니다.
last_reviewed: '2026-05-12'
---

# Discrete Math 101 (6/10): 수열과 점화식

이 글은 Discrete Math 101 시리즈의 6번째 글입니다.

![Discrete Math 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/06/06-01-big-picture.ko.png)
*Discrete Math 101 6장 흐름 개요*

## 먼저 던지는 질문

- 수열과 닫힌 형식은 어떻게 연결될까요?
- 점화식은 어떤 수학적 표기인가요?
- 치환법과 재귀 트리법은 언제 유용할까요?

## 왜 중요한가

`mergesort(n) = 2·mergesort(n/2) + O(n)`은 점화식입니다. 이 식을 풀면 `O(n log n)`이 나옵니다. 분할 정복, 동적 계획법, 재귀 함수 분석은 모두 점화식을 푸는 문제로 귀결됩니다. 점화식을 모르면 재귀 코드는 쓸 수 있어도 그 비용은 설명하지 못합니다.

> 점화식은 재귀 알고리즘을 비추는 수학적 거울입니다.

## 한눈에 보는 개념

> `T(n) = aT(n/b) + f(n)`은 분할 정복의 표준형입니다. 마스터 정리는 이 식에서 닫힌 형식을 빠르게 읽어 내는 도구입니다.

```text
   recursive algorithm
            │
            ↓
     recurrence form
            │
   ┌────────┼────────────┐
   ↓        ↓            ↓
 substitution recursion  Master
            tree       Theorem
   │        │            │
   └────────┴──────┬─────┘
                   ↓
            closed form (Big-O)
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Sequence | `a₁, a₂, a₃, ...` 형태의 순서열 |
| Closed form | n으로부터 `aₙ`을 직접 계산하는 식 |
| Recurrence | 이전 항으로 다음 항을 정의하는 식 |
| Master Theorem | `T(n) = aT(n/b) + f(n)`의 표준 해법 |
| Geometric sequence | `aₙ = a₁·rⁿ⁻¹` 꼴의 등비수열 |

## 전후 비교

**Before — without analysis:**

```python
# "재귀는 느리다" — 정확한 복잡도를 모름
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

**After — analyzed via recurrence:**

```python
# T(n) = T(n-1) + T(n-2) + O(1)
# Solution: T(n) = O(φⁿ) ≈ O(1.618ⁿ) — exponential
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

# Memoized: T(n) = T(n-1) + O(1) → O(n)
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_fast(n):
    return n if n < 2 else fib_fast(n - 1) + fib_fast(n - 2)
```

## 단계별로 따라가기

### 1단계: 수열 표현하기

```python
# Arithmetic: aₙ = a₁ + (n-1)d
def arithmetic(a1: float, d: float, n: int) -> list:
    return [a1 + (i - 1) * d for i in range(1, n + 1)]

# Geometric: aₙ = a₁ · rⁿ⁻¹
def geometric(a1: float, r: float, n: int) -> list:
    return [a1 * (r ** (i - 1)) for i in range(1, n + 1)]

print(f"arithmetic (a=2, d=3, n=5): {arithmetic(2, 3, 5)}")
print(f"geometric  (a=1, r=2, n=8): {geometric(1, 2, 8)}")
```

등차수열과 등비수열은 닫힌 형식이 명확합니다. 어려운 점화식을 풀 때도 결국 이런 익숙한 형태로 바꿀 수 있는지가 핵심입니다.

### 2단계: 점화식을 직접 계산하기

```python
# Recurrence: T(n) = T(n-1) + n, T(0) = 0
# 의미: 각 단계에서 n만큼 작업 수행
def T(n: int) -> int:
    if n == 0:
        return 0
    return T(n - 1) + n

# Closed form: T(n) = n(n+1)/2
def T_closed(n: int) -> int:
    return n * (n + 1) // 2

for n in [1, 5, 10, 100]:
    assert T(n) == T_closed(n)
    print(f"T({n}) = {T(n)} (closed: {T_closed(n)})")
```

점화식의 의미를 코드로 계산해 보면 왜 닫힌 형식이 필요한지 감이 옵니다. 값을 하나씩 누적하는 방식은 개념을 보여 주지만, 복잡도 자체를 설명해 주지는 못합니다.

### 3단계: 치환법으로 풀기

```python
# Recurrence: T(n) = 2T(n/2) + n, T(1) = 1
# Substitute repeatedly:
# T(n) = 2T(n/2) + n
#      = 2[2T(n/4) + n/2] + n = 4T(n/4) + 2n
#      = 4[2T(n/8) + n/4] + 2n = 8T(n/8) + 3n
#      ...
#      = 2^k T(n/2^k) + kn
# n/2^k = 1 → k = log n
# T(n) = n·T(1) + n log n = O(n log n)

def merge_sort_count(arr: list) -> tuple:
    """Merge sort that also returns the comparison count."""
    if len(arr) <= 1:
        return arr, 0
    mid = len(arr) // 2
    left, lc = merge_sort_count(arr[:mid])
    right, rc = merge_sort_count(arr[mid:])
    merged, mc = merge_count(left, right)
    return merged, lc + rc + mc

def merge_count(a: list, b: list) -> tuple:
    result = []
    i = j = c = 0
    while i < len(a) and j < len(b):
        c += 1
        if a[i] <= b[j]:
            result.append(a[i]); i += 1
        else:
            result.append(b[j]); j += 1
    result.extend(a[i:]); result.extend(b[j:])
    return result, c

import math

for n in [16, 64, 256]:
    arr = list(range(n, 0, -1))
    _, count = merge_sort_count(arr)
    print(f"n={n}: {count} comparisons, n log n = {n * int(math.log2(n))}")
```

치환법은 점화식의 구조를 손으로 펼쳐 보는 방식입니다. 병합 정렬이 왜 `n log n`인지 이해할 때 가장 교육적인 방법이기도 합니다.

### 4단계: 마스터 정리

```python
# Master Theorem 형태: T(n) = aT(n/b) + f(n)
# n^(log_b a)와 f(n) 비교 — 세 가지 경우:
# 1. f(n) = O(n^(log_b a - ε))           → T(n) = Θ(n^(log_b a))
# 2. f(n) = Θ(n^(log_b a))                → T(n) = Θ(n^(log_b a) · log n) 케이스
# 3. f(n) = Ω(n^(log_b a + ε)) (regular)  → T(n) = Θ(f(n))

import math

def master_theorem(a: int, b: int, f_exponent: float) -> str:
    """Estimate the closed form of T(n) = aT(n/b) + n^f_exponent."""
    critical = math.log(a, b)
    if f_exponent < critical:
        return f"Θ(n^{critical:.2f})"
    elif abs(f_exponent - critical) < 1e-9:
        return f"Θ(n^{critical:.2f} · log n)"
    else:
        return f"Θ(n^{f_exponent})"

# Merge sort: T(n) = 2T(n/2) + n  → a=2, b=2, f(n)=n¹
print(f"merge sort:        {master_theorem(2, 2, 1)}")
# Binary search: T(n) = T(n/2) + 1
print(f"binary search:     {master_theorem(1, 2, 0)}")
# Strassen: T(n) = 7T(n/2) + n²
print(f"Strassen multiply: {master_theorem(7, 2, 2)}")
```

마스터 정리는 분할 정복 알고리즘을 빠르게 분류하는 표준 도구입니다. 다만 아무 점화식에나 붙일 수 있는 만능 공식은 아니라는 점을 함께 기억해야 합니다.

### 5단계: 피보나치의 닫힌 형식

```python
# Fibonacci: F(n) = F(n-1) + F(n-2), F(0)=0, F(1)=1
# Characteristic equation: x² = x + 1 → x = (1±√5)/2 = φ, ψ
# Closed form: F(n) = (φⁿ - ψⁿ) / √5

import math

PHI = (1 + math.sqrt(5)) / 2
PSI = (1 - math.sqrt(5)) / 2

def fib_closed(n: int) -> int:
    return round((PHI ** n - PSI ** n) / math.sqrt(5))

def fib_iter(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

for n in [10, 20, 30]:
    assert fib_closed(n) == fib_iter(n)
    print(f"F({n}) = {fib_closed(n)} (closed = iter)")
```

선형 점화식은 특성방정식으로 닫힌 형식을 얻을 수 있습니다. 피보나치에서 황금비가 나오는 것은 우연이 아니라 이 기법의 직접적인 결과입니다.

## 주목할 점

- 점화식은 재귀 알고리즘의 시간 복잡도를 수학적으로 표현합니다.
- 마스터 정리는 분할 정복 문제의 표준 도구입니다.
- 닫힌 형식을 얻으면 임의의 n에 대한 비용을 즉시 예측할 수 있습니다.
- 메모이제이션은 중복 부분문제를 제거해 지수 시간을 다항 시간으로 낮춥니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 마스터 정리 조건을 무시한다 | case 3의 정칙 조건 등을 놓친다 | 세 경우와 전제를 함께 확인한다 |
| 기저 조건을 빼먹는다 | 점화식만 있고 시작점이 없다 | T(1) 또는 T(0)을 명시한다 |
| 로그의 밑을 대충 본다 | 정확한 수치 해석이 흐려진다 | Big-O와 정확한 값 계산을 구분한다 |
| 비균등 분할에도 마스터 정리를 쓴다 | 적용 자체가 틀린다 | 직접 전개나 다른 방법을 쓴다 |
| 메모이제이션을 빠뜨린다 | 의도치 않게 지수 시간이 된다 | 중복 부분문제가 있으면 먼저 의심한다 |

## 실무에서는 이렇게 사용합니다

- 면접에서 병합 정렬, 퀵 정렬, 이진 탐색의 복잡도를 설명합니다.
- 배낭 문제, LIS, 편집 거리 같은 DP 문제의 점화식을 세웁니다.
- B-tree 인덱스의 탐색 깊이를 추정합니다.
- 분산 시스템의 메시지 비용을 계산합니다.
- 재시도 백오프나 캐시 갱신 간격도 수열로 설계할 수 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 새로운 알고리즘을 보면 먼저 “이 함수가 자기 자신을 몇 번, 어떤 크기로 호출하는가”를 묻습니다. 즉시 점화식을 세우고, 가능하면 마스터 정리나 전개법으로 비용을 읽어 냅니다. 이런 사고는 알고리즘 밖에서도 반복 간격, 캐시 압력 증가, 재시도 전략 설계에 그대로 적용됩니다.

## 체크리스트

- [ ] 등차수열과 등비수열의 닫힌 형식을 기억한다
- [ ] `T(n) = aT(n/b) + f(n)` 꼴을 알아볼 수 있다
- [ ] 마스터 정리의 세 경우를 구분할 수 있다
- [ ] 병합 정렬이 왜 `O(n log n)`인지 설명할 수 있다
- [ ] 메모이제이션이 복잡도를 낮추는 이유를 이해한다

## 연습 문제

1. 마스터 정리로 `T(n) = 3T(n/2) + n²`의 닫힌 형식을 구해 보세요.

2. 반복형 피보나치와 순진한 재귀 피보나치를 `n = 30, 35, 40`에서 비교해 보세요.

3. 자신이 작성한 재귀 함수 하나를 골라 점화식으로 바꾸고 시간 복잡도를 유도해 보세요.

## 정리 및 다음 단계

수열은 순서 있는 값의 나열이고, 점화식은 그 값을 재귀적으로 정의하는 방식입니다. 치환법, 재귀 트리, 마스터 정리는 점화식을 닫힌 형식이나 Big-O로 바꾸어 재귀 알고리즘의 비용을 읽게 해 줍니다.

다음 글에서는 경우의 수를 세는 수학, 조합론으로 넘어가겠습니다.

## 실전 확장: 점화식을 닫힌형으로 전개하는 훈련

점화식은 알고리즘 비용을 시간 축으로 기록한 형태입니다. 전개, 추측, 귀납 검증의 세 단계를 반복하면 닫힌형을 안정적으로 얻을 수 있습니다.

### 워크드 예시 1: 선형 점화식

`T(n)=T(n-1)+2n`, `T(0)=0`.

전개하면
`T(n)=2(1+2+...+n)=n(n+1)`.

귀납 검증:
- 기저 `n=0`: `0=0`.
- 가정 `T(k)=k(k+1)`.
- `T(k+1)=T(k)+2(k+1)=k(k+1)+2k+2=(k+1)(k+2)`.

### 워크드 예시 2: 분할정복 점화식

`T(n)=2T(n/2)+n`, `T(1)=1`.

레벨 `i`에서 부분문제 수는 `2^i`, 각 비용은 `n/2^i`라서 레벨 합은 항상 `n`입니다. 깊이는 `log2 n`이므로 총비용은 `n log n + n = Θ(n log n)`입니다.

### 워크드 예시 3: 특성방정식

`a_n = 3a_{n-1} - 2a_{n-2}`, `a_0=2`, `a_1=3`.

특성방정식 `r^2-3r+2=0`의 근은 `1,2`. 따라서
`a_n = c1*1^n + c2*2^n = c1 + c2*2^n`.
초기값 대입:
- `n=0`: `c1+c2=2`
- `n=1`: `c1+2c2=3`
`c2=1`, `c1=1`이므로 `a_n = 1 + 2^n`.

### 구현 앵커: 메모이제이션과 반복

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo(n: int) -> int:
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)

def fib_iter(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
```

두 구현은 같은 점화식을 사용하지만 복잡도와 메모리 패턴이 다릅니다. 이 차이를 분석하는 언어가 점화식입니다.

### 검증 체크리스트

- 기저 조건이 실제로 종료를 보장하는가
- 점화식의 인자가 단조 감소하는가
- 닫힌형을 대입했을 때 원식이 복원되는가
- 입력 제약(예: `n`이 2의 거듭제곱)이 필요한가

## 심화 워크숍: 점화식 해법 비교와 선택 기준

### 반복 대입 vs 마스터 정리

`T(n)=aT(n/b)+f(n)` 꼴이면 먼저 마스터 정리를 시도하고, 조건이 맞지 않으면 반복 대입이나 재귀 트리로 전환합니다. 도구 선택을 빠르게 하면 계산 실수를 줄일 수 있습니다.

### 워크드 예시 4: 로그 항이 섞인 경우

`T(n)=2T(n/2)+n log n`.

재귀 트리에서 깊이 `i`의 레벨 합은 `n(log n - i)`가 됩니다. 이를 `i=0`부터 `log n-1`까지 더하면 `Θ(n log^2 n)`을 얻습니다.

### 워크드 예시 5: 비동차 선형 점화식

`a_n = 2a_{n-1} + 3`, `a_0=1`.

상수해 `c`를 가정하면 `c=2c+3`에서 `c=-3`. `b_n=a_n+3`이라 두면 `b_n=2b_{n-1}`, `b_0=4`. 따라서 `b_n=4*2^n`, 결국 `a_n=4*2^n-3`.

### 구현 앵커: 점화식 값 테이블링

```python
def recurrence_table(n: int) -> list[int]:
    # a_n = 2a_{n-1} + 3, a_0 = 1
    arr = [0] * (n + 1)
    arr[0] = 1
    for i in range(1, n + 1):
        arr[i] = 2 * arr[i - 1] + 3
    return arr
```

테이블링은 계산 경로를 명시하므로 디버깅과 검증에 유리합니다.

## 부록: 검증 가능한 실습 패턴 모음

아래 패턴은 각 장의 개념을 실습으로 고정하기 위한 공통 템플릿입니다. 핵심은 계산 결과를 맞히는 것보다, 어떤 정의를 적용했는지 문장으로 남기는 것입니다.

### 패턴 1: 정의를 먼저 쓰고 계산하기

1. 문제에서 사용하는 대상 집합을 명시합니다.
2. 관계 또는 함수를 기호로 정의합니다.
3. 계산을 수행하고, 결과가 정의를 만족하는지 다시 확인합니다.

이 순서를 지키면 중간에 식이 길어져도 논리의 출발점을 잃지 않습니다.

### 패턴 2: 반례를 의도적으로 만들기

정리나 가설을 세웠다면, 반례 후보를 최소 3개 만듭니다.

- 경계값 입력(0, 1, 최대값)
- 중복/충돌 입력
- 공집합 또는 단일 원소 입력

반례가 발견되면 결론을 버리는 것이 아니라, 가정과 정의를 수정합니다. 이 절차가 수학적 엄밀성과 엔지니어링 실용성을 동시에 만족시킵니다.

### 패턴 3: 표와 코드 출력을 함께 남기기

진리표, 집합 연산표, 점화식 전개표 중 하나를 반드시 포함합니다. 그리고 같은 내용을 계산하는 짧은 코드를 붙여 결과를 재현합니다.

```python
def verify_identity(left: set[int], right: set[int]) -> bool:
    return left == right
```

작은 검증 함수 하나라도 문서에 남기면 팀원 간 해석 차이를 줄일 수 있습니다.

### 패턴 4: 증명 구조를 고정하기

증명은 다음 네 문장 구조를 기본으로 씁니다.

- 가정: 무엇을 참이라고 두는가
- 전개: 어떤 정의/정리를 사용해 변형하는가
- 핵심 전환: 결론으로 넘어가는 결정적 단계는 무엇인가
- 결론: 원래 명제가 왜 성립하는가

이 구조는 직접 증명, 대우 증명, 귀류법, 귀납법 모두에 적용됩니다.

### 패턴 5: 알고리즘과 수학 근거 연결하기

알고리즘 설명에는 다음 항목을 최소로 넣습니다.

- 불변식 1개 이상
- 종료 조건 1개
- 복잡도 식 1개
- 반례 테스트 1개

이 네 항목이 있으면 코드가 바뀌어도 정확성 근거를 유지할 수 있습니다.

### 미니 문제 세트

1. 두 집합 `A`, `B`를 임의로 만들고 `A∩B`, `A∪B`, `A\B`를 계산한 뒤 포함관계를 설명하세요.
2. 명제식 `(P→Q) ∧ (Q→R) → (P→R)`의 진리표를 작성하고 항진명제 여부를 확인하세요.
3. 점화식 `T(n)=T(n-1)+n`의 닫힌형을 추측한 다음 귀납법으로 검증하세요.
4. 인접 리스트 그래프 하나를 만든 뒤 BFS/DFS 방문 순서를 비교하세요.
5. `nCk = nC(n-k)`를 식과 의미 해석(선택 vs 비선택) 두 방식으로 설명하세요.

### 마무리

각 장의 주제가 달라 보여도 훈련 루프는 같습니다. 정의를 선언하고, 계산을 수행하고, 반례로 검증하고, 증명 또는 불변식으로 고정하면 됩니다. 이 루프를 반복하면 새로운 문제에서도 같은 품질로 사고할 수 있습니다.

## 추가 심화: 오류 사례와 교정 로그

실무에서 이산수학 개념이 흔들리는 지점은 대부분 "정의 생략"에서 시작합니다. 아래는 자주 나오는 오류와 교정 방식입니다.

### 오류 사례 1: 조건 누락

- 증상: 코드가 특정 입력에서만 실패합니다.
- 원인: 명제식에서 한 항을 자연어로만 설명하고 코드에 반영하지 않았습니다.
- 교정: 조건을 변수화해 논리식으로 명시하고, 진리표의 위험 조합을 테스트로 고정합니다.

### 오류 사례 2: 집합 경계 불일치

- 증상: 제외되어야 할 원소가 결과에 섞입니다.
- 원인: 전체집합 `U`를 정의하지 않아 여집합 계산이 흔들립니다.
- 교정: `U`를 먼저 확정하고 `A^c = U \ A`를 코드와 문서에 동시에 기록합니다.

### 오류 사례 3: 그래프 방향성 오해

- 증상: 탐색 결과가 기대보다 과도하거나 부족합니다.
- 원인: 유향/무향 그래프를 혼동해 간선을 양방향으로 추가했습니다.
- 교정: 입력 스키마 단계에서 방향성을 필드로 분리하고, 예제 그래프를 최소 1개 유지합니다.

### 오류 사례 4: 점화식 기저 조건 누락

- 증상: 재귀가 종료되지 않거나 값이 어긋납니다.
- 원인: `n=0`, `n=1`에서의 정의를 생략했습니다.
- 교정: 기저 조건을 본문과 코드 첫 줄에 병기하고, 단위 테스트를 별도로 둡니다.

### 교정 루프

1. 정의를 다시 선언합니다.
2. 최소 반례를 구성합니다.
3. 식과 코드를 동시에 수정합니다.
4. 표/출력으로 재검증합니다.

이 루프를 문서화하면 팀 단위 품질이 안정됩니다.

## 처음 질문으로 돌아가기

- **수열과 닫힌 형식은 어떻게 연결될까요?**
  - 수열은 값을 순서대로 나열한 것이고, 닫힌 형식은 `a_n`을 이전 항을 거치지 않고 바로 계산하는 식입니다. 본문에서 `T(n)=T(n-1)+n`을 재귀로 계산한 뒤 `T_closed(n)=n(n+1)/2`와 비교한 예시가 이 연결을 가장 직접적으로 보여 줍니다.
- **점화식은 어떤 수학적 표기인가요?**
  - 점화식은 현재 값이나 비용을 더 작은 입력의 값으로 정의하는 표기이며, 알고리즘에서는 재귀 호출 구조를 수식으로 옮긴 형태입니다. 그래서 `fib(n)`의 `T(n)=T(n-1)+T(n-2)+O(1)`이나 병합 정렬의 `T(n)=2T(n/2)+n`처럼 코드의 성능 구조를 직접 읽어 낼 수 있습니다.
- **치환법과 재귀 트리법은 언제 유용할까요?**
  - 치환법은 `T(n)=2T(n/2)+n`을 `4T(n/4)+2n`, `8T(n/8)+3n`처럼 손으로 펼치며 패턴을 찾을 때 유용합니다. 재귀 트리법은 각 레벨 비용을 합쳐 전체 성장 모양을 볼 때 강해서, 본문처럼 병합 정렬이 왜 `Θ(n log n)`이 되는지 직관적으로 설명하기 좋습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Discrete Math 101 (1/10): 이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- [Discrete Math 101 (2/10): 명제와 논리](./02-propositions-and-logic.md)
- [Discrete Math 101 (3/10): 집합과 함수](./03-sets-and-functions.md)
- [Discrete Math 101 (4/10): 관계와 동치관계](./04-relations-and-equivalence.md)
- [Discrete Math 101 (5/10): 증명 방법](./05-proof-techniques.md)
- **수열과 점화식 (현재 글)**
- 조합과 경우의 수 (예정)
- 그래프 이론 기초 (예정)
- 트리와 그래프 탐색 (예정)
- 알고리즘과 이산수학의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [book-examples: discrete-math-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/discrete-math-101/ko)
- [Introduction to Algorithms — CLRS, Chapter 4 (Master Theorem)](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Wikipedia — Master Theorem](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Wikipedia — Recurrence Relation](https://en.wikipedia.org/wiki/Recurrence_relation)
- [MIT OCW — Mathematics for Computer Science, Lecture 19-21](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)

Tags: Computer Science, 이산수학, 점화식, 수열, 마스터 정리, 알고리즘 분석
