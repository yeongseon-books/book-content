
# 증명 방법

> Discrete Math 101 시리즈 (5/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 알고리즘이 "항상" 올바르게 동작한다는 것을 어떻게 보장할 수 있을까요? 테스트 100개를 통과해도 입력 100,001번에서 실패할 수 있지 않을까요?

> 증명(proof)은 모든 가능한 경우에 대해 명제가 참임을 엄밀히 보이는 추론 과정입니다. 직접 증명, 대우 증명, 귀류법, 수학적 귀납법은 이산수학의 네 가지 핵심 증명 기법이며, 알고리즘의 정확성·종료성을 증명하는 도구이기도 합니다. 이 글에서는 각 증명 방법의 구조와 실제 코드 검증에의 응용을 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 직접 증명과 대우 증명
- 귀류법(proof by contradiction)
- 수학적 귀납법과 강한 귀납법
- 알고리즘의 정확성과 종료성 증명

## 왜 중요한가

테스트는 버그의 존재를 보일 뿐 부재를 증명하지 못합니다. 분산 합의 알고리즘, 암호 프로토콜, 컴파일러 최적화는 모두 형식적 증명으로 정확성을 보장합니다. 또한 재귀 함수의 정확성은 귀납법으로, 알고리즘 종료성은 well-founded 관계로 증명됩니다.

> 증명 = 모든 입력에 대한 보장

## 개념 한눈에 보기

> 증명 방법은 명제의 형태에 따라 선택됩니다. P → Q는 직접/대우, 부정형은 귀류, 모든 n에 대한 명제는 귀납.

```text
   증명할 명제
        │
   ┌────┼────────────┬─────────────┐
   ↓    ↓            ↓             ↓
  P→Q  P→Q          ¬P            ∀n: P(n)
  직접  대우 (¬Q→¬P)  귀류         귀납법
                                    │
                                    ↓
                              기저 + 귀납 단계
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 직접 증명 | P를 가정하고 Q를 유도 |
| 대우 증명 | ¬Q를 가정하고 ¬P를 유도 |
| 귀류법 | P의 부정을 가정하여 모순 유도 |
| 귀납법 | 기저 P(0) + P(k) → P(k+1) |
| 항진명제 | 모든 경우에 참인 명제 |

## Before / After

**Before — 증명 없이:**

```python
# "100번 테스트했으니 맞을 거야" — 모든 입력 보장 X
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a
```

**After — 정확성 증명 첨부:**

```python
def gcd(a: int, b: int) -> int:
    """유클리드 호제법.

    정확성: gcd(a, b) = gcd(b, a mod b) (수학적 정리)
    종료성: b는 매 반복마다 엄격히 감소(자연수) → well-founded
    """
    while b:
        a, b = b, a % b
    return a
```

## 실습: 단계별로 따라하기

### 1단계: 직접 증명

```python
# 명제: 짝수의 제곱은 짝수이다
# 증명: n = 2k라고 가정. n² = 4k² = 2(2k²). 따라서 짝수.

def verify_direct(limit: int = 1000) -> bool:
    """경험적 검증 (증명 자체는 수학으로 완료됨)"""
    for k in range(limit):
        n = 2 * k
        assert (n ** 2) % 2 == 0
    return True


print(f"검증: {verify_direct()}")
```

검증과 증명은 다릅니다. 검증은 일부 사례에서 참임을 보일 뿐이고, 증명은 모든 경우를 포괄합니다.

### 2단계: 대우 증명

```python
# 명제: n²이 짝수이면 n도 짝수이다
# 직접 증명은 어렵지만, 대우는 쉽다:
# 대우: n이 홀수이면 n²도 홀수이다
# n = 2k + 1 → n² = 4k² + 4k + 1 = 2(2k² + 2k) + 1 → 홀수

def contrapositive_check(limit: int = 1000) -> None:
    for n in range(limit):
        if n % 2 == 1:  # n 홀수
            assert (n ** 2) % 2 == 1  # n² 홀수


contrapositive_check()
print("대우 증명 사례 확인 완료")
```

대우 증명은 P → Q를 ¬Q → ¬P로 바꾸어 증명합니다. 진리값이 같다는 점을 활용합니다.

### 3단계: 귀류법

```python
# 명제: √2는 무리수이다
# 가정: √2 = p/q (서로소). 양변 제곱하면 2q² = p²
# → p²은 짝수 → p도 짝수 → p = 2k
# → 2q² = 4k² → q² = 2k² → q²도 짝수 → q도 짝수
# → p, q 둘 다 짝수 ⊥ "서로소"라는 가정과 모순

import math


def is_rational_approx(x: float, max_q: int = 10000) -> bool:
    """경험적: 분모가 max_q 이하에서 정확한 분수 표현이 있는지"""
    for q in range(1, max_q):
        p = round(x * q)
        if abs(x - p / q) < 1e-15:
            return True
    return False


print(f"√2가 분모 10000 이하 분수로 표현 가능?: {is_rational_approx(math.sqrt(2))}")
```

귀류법은 "결론의 부정"을 가정하고 모순을 유도합니다. 분산 시스템의 불가능성 증명(FLP, CAP)도 귀류법입니다.

### 4단계: 수학적 귀납법

```python
# 명제: 1 + 2 + ... + n = n(n+1)/2
# 기저 P(1): 1 = 1·2/2 = 1 ✓
# 귀납 단계: P(k) 가정 시 P(k+1) 증명
#   1 + 2 + ... + k + (k+1) = k(k+1)/2 + (k+1) = (k+1)(k+2)/2 ✓


def gauss_sum(n: int) -> int:
    return n * (n + 1) // 2


def actual_sum(n: int) -> int:
    return sum(range(1, n + 1))


for n in [1, 10, 100, 1000]:
    assert gauss_sum(n) == actual_sum(n)
    print(f"n={n}: 공식={gauss_sum(n)}, 실제={actual_sum(n)}")
```

귀납법은 두 단계로 구성됩니다: (1) 기저 — 가장 작은 경우, (2) 귀납 단계 — k에서 k+1로의 도출. 모든 자연수에 대한 명제는 이 두 단계로 증명됩니다.

### 5단계: 알고리즘 정확성 증명

```python
# 명제: 다음 함수는 정렬된 배열에서 target의 인덱스를 정확히 반환한다
# (없으면 -1)

def binary_search(arr: list, target: int) -> int:
    low, high = 0, len(arr) - 1
    while low <= high:
        # 불변 조건(invariant):
        # target이 arr에 있다면, 반드시 arr[low..high] 범위에 있다
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


# 종료성 증명: high - low가 매 반복마다 엄격히 감소
# 정확성 증명: 루프 불변 조건 + 종료 조건
# 귀납법으로 형식 증명 가능

for arr, target in [([1, 3, 5, 7, 9], 5), ([1, 3, 5, 7, 9], 4)]:
    print(f"binary_search({arr}, {target}) = {binary_search(arr, target)}")
```

루프 불변 조건은 알고리즘 정확성 증명의 핵심입니다. Hoare logic, Floyd-Hoare 검증이 이에 기반합니다.

## 이 코드에서 주목할 점

- 증명과 검증은 다르다 — 검증은 일부, 증명은 전체를 보장
- 대우 증명과 귀류법은 직접 증명이 어려울 때 유용
- 귀납법은 자연수·재귀 구조에 대한 표준 증명 기법
- 알고리즘 정확성은 루프 불변 조건으로 증명

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 검증을 증명으로 착각 | 일부 통과 = 모든 경우 보장 X | 형식적 증명 또는 형식 검증 사용 |
| 귀납법 기저 누락 | k → k+1만 증명, 시작점 없음 | 항상 P(0) 또는 P(1) 명시 |
| 귀류법에서 가정 혼동 | "P → Q를 부정"이 무엇인지 모호 | "P ∧ ¬Q"가 부정 |
| 대우와 역 혼동 | 역(Q → P)은 동치 아님 | 대우(¬Q → ¬P)만 동치 |
| 종료성 증명 빠뜨림 | 루프가 무한히 돌 가능성 | well-founded 측도로 감소 보임 |

## 실무에서는 이렇게 쓰입니다

- 분산 합의 알고리즘(Paxos, Raft)의 안전성·생존성 증명
- 암호 프로토콜의 보안성 증명 (BAN 논리, Tamarin)
- 컴파일러 최적화의 의미 보존 증명 (CompCert)
- TLA+, Coq, Lean 등 정형 검증 도구가 산업에 도입
- 코드 리뷰에서 "이게 항상 맞나? 엣지 케이스는?" 질문은 비공식 증명

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 코드를 읽을 때 머릿속으로 비공식 증명을 합니다. "이 루프의 불변 조건이 무엇인가? 매 반복마다 무엇이 줄어드는가? 종료 조건은 정말 도달 가능한가?" 형식 증명을 작성하지 않더라도, 증명의 사고 방식이 코드 정확성을 좌우합니다. 또한 분산 시스템처럼 테스트로 모든 경우를 커버할 수 없는 영역에서는 형식 모델과 증명에 의존합니다.

## 체크리스트

- [ ] 네 가지 증명 방법의 차이를 설명할 수 있는가
- [ ] 귀납법의 두 단계를 기억하는가
- [ ] 대우와 역의 차이를 알고 있는가
- [ ] 루프 불변 조건의 개념을 이해했는가
- [ ] 검증과 증명의 차이를 명확히 구분하는가

## 연습 문제

1. "n이 3의 배수이면 n²도 3의 배수이다"를 직접 증명하세요.

2. 1² + 2² + ... + n² = n(n+1)(2n+1)/6을 수학적 귀납법으로 증명하세요.

3. 자신이 작성한 while 루프 하나를 골라, 루프 불변 조건과 종료 측도를 명시적으로 작성해보세요.

## 정리 및 다음 단계

증명은 모든 가능한 경우에 대한 정확성 보장입니다. 직접·대우·귀류·귀납법의 네 도구로 이산수학의 거의 모든 명제를 증명할 수 있고, 같은 도구가 알고리즘 정확성 증명에도 쓰입니다. 시니어 엔지니어의 사고는 비공식 증명에 가깝습니다.

다음 글에서는 귀납법과 직결된 "수열과 점화식" — 알고리즘 분석의 필수 도구 — 를 살펴봅니다.

- [이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- [명제와 논리](./02-propositions-and-logic.md)
- [집합과 함수](./03-sets-and-functions.md)
- [관계와 동치관계](./04-relations-and-equivalence.md)
- **증명 방법 (현재 글)**
- 수열과 점화식 (예정)
- 조합과 경우의 수 (예정)
- 그래프 이론 기초 (예정)
- 트리와 그래프 탐색 (예정)
- 알고리즘과 이산수학의 연결 (예정)
## 참고 자료

- [Book of Proof — Richard Hammack (Free)](https://www.people.vcu.edu/~rhammack/BookOfProof/)
- [How to Prove It — Daniel Velleman](https://www.cambridge.org/core/books/how-to-prove-it/6D2965D6905658D704B782B9D67E2989)
- [Wikipedia — Mathematical Proof](https://en.wikipedia.org/wiki/Mathematical_proof)
- [MIT OCW — Mathematics for Computer Science, Lecture 2-5](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)

Tags: Computer Science, 이산수학, 수학적 증명, 귀납법, 귀류법, 알고리즘 정확성

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
