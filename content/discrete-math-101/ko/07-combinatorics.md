---
series: discrete-math-101
episode: 7
title: 조합과 경우의 수
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
  - 조합론
  - 순열
  - 비둘기집 원리
  - 확률
seo_description: 순열, 조합, 이항정리, 비둘기집 원리, 포함-배제 원리를 통해 경우의 수와 확률 분석의 기초를 배웁니다.
last_reviewed: '2026-05-04'
---

# 조합과 경우의 수

> Discrete Math 101 시리즈 (7/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 해시 충돌은 왜 일어날 수밖에 없을까요? 비밀번호 후보를 모두 시도하려면 얼마나 걸릴까요?

> 조합론(combinatorics)은 "몇 가지 경우가 있는가"를 정확히 세는 수학입니다. 순열(permutation)·조합(combination)·이항정리·비둘기집 원리는 알고리즘의 입력 공간 크기, 암호의 키 공간, 해시 충돌 확률을 분석하는 도구입니다. 이 글에서는 기본 셈의 원리부터 비둘기집 원리, 포함-배제 원리까지 살펴보고 코드로 검증합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 곱의 법칙과 합의 법칙
- 순열과 조합의 차이
- 이항계수와 파스칼의 삼각형
- 비둘기집 원리와 포함-배제 원리

## 왜 중요한가

암호의 키 공간 크기, 무차별 대입 공격 시간, 생일 역설 — 모두 조합론입니다. 알고리즘이 가능한 모든 입력에 대해 어떻게 동작할지 분석할 때 입력 공간의 크기를 알아야 하고, 그 크기 계산이 조합론입니다.

> 조합론 = 가능성의 크기를 정확히 세는 도구

## 개념 한눈에 보기

> 셈의 두 법칙(곱·합)에서 출발하여 순열·조합·이항정리·비둘기집·포함-배제로 확장됩니다.

```text
   기본 법칙
  ┌─────────┐
  │ 곱의 법칙 │ — 독립 선택의 곱
  │ 합의 법칙 │ — 배타적 선택의 합
  └─────┬─────┘
        ↓
  ┌─────────┬─────────┐
  ↓         ↓         ↓
 순열 P    조합 C    이항정리
   │         │         │
   └────┬────┴─────────┘
        ↓
  비둘기집 / 포함-배제
```

## 핵심 용어 정리

| 용어 | 기호 | 설명 |
| --- | --- | --- |
| 순열 | P(n, r) = n!/(n-r)! | n개 중 r개 순서 있게 |
| 조합 | C(n, r) = n!/(r!(n-r)!) | n개 중 r개 순서 무관 |
| 이항계수 | (n choose r) | 조합과 동일 |
| 비둘기집 원리 | n+1개 → n개 | 적어도 한 칸에 2개 |
| 포함-배제 | |A∪B| = |A| + |B| - |A∩B| | 중복 제거 |

## Before / After

**Before — 셈 없이 무차별 시도:**

```python
# "모든 경우를 시도해보자" — 얼마나 걸릴지 모름
import itertools
for password in itertools.product("abc", repeat=4):
    pass  # 81가지 — 작아 보이지만...
```

**After — 공간 크기 분석:**

```python
# 4자리 영소문자: 26⁴ = 456,976
# 8자리 영숫자대소문자+특수: 94⁸ ≈ 6.1 × 10¹⁵
charset = 26
length = 4
print(f"공간 크기: {charset ** length:,}")
```

## 실습: 단계별로 따라하기

### 1단계: 곱의 법칙과 합의 법칙

```python
# 곱의 법칙: 독립적 선택의 경우는 곱한다
# 예: 셔츠 5종, 바지 3종 → 코디 5 × 3 = 15

shirts = ["흰", "검정", "회색", "남색", "베이지"]
pants = ["청", "면", "정장"]

outfits = [(s, p) for s in shirts for p in pants]
print(f"코디 가짓수: {len(outfits)} = {len(shirts)} × {len(pants)}")

# 합의 법칙: 배타적 선택은 더한다
# 예: 점심으로 한식 4가지 또는 일식 3가지 → 4 + 3 = 7
korean = 4; japanese = 3
print(f"점심 메뉴 가짓수: {korean + japanese}")
```

### 2단계: 순열과 조합

```python
from math import factorial


def permutation(n: int, r: int) -> int:
    """순서를 고려한 r개 선택"""
    return factorial(n) // factorial(n - r)


def combination(n: int, r: int) -> int:
    """순서를 고려하지 않는 r개 선택"""
    return factorial(n) // (factorial(r) * factorial(n - r))


# 5명 중 3명 줄세우기 (순서 중요)
print(f"P(5, 3) = {permutation(5, 3)}")
# 5명 중 3명 위원회 (순서 무관)
print(f"C(5, 3) = {combination(5, 3)}")

# Python 내장
from itertools import permutations, combinations
print(f"순열 수: {len(list(permutations(range(5), 3)))}")
print(f"조합 수: {len(list(combinations(range(5), 3)))}")
```

순서가 중요하면 순열, 무관하면 조합. 비밀번호는 순열, 카드 패는 조합입니다.

### 3단계: 이항정리와 파스칼 삼각형

```python
# 이항정리: (x + y)ⁿ = Σ C(n, k) xⁿ⁻ᵏ yᵏ
# 계수가 곧 조합의 수

def pascal_triangle(rows: int) -> list[list[int]]:
    triangle = [[1]]
    for i in range(1, rows):
        prev = triangle[-1]
        new_row = [1] + [prev[j] + prev[j + 1] for j in range(len(prev) - 1)] + [1]
        triangle.append(new_row)
    return triangle


for row in pascal_triangle(7):
    print(" ".join(str(x).rjust(3) for x in row).center(40))


# (x + y)⁴ 전개: 계수는 1, 4, 6, 4, 1
n = 4
print(f"(x+y)^{n} 계수: {[combination(n, k) for k in range(n + 1)]}")
```

### 4단계: 비둘기집 원리

```python
# 비둘기집 원리: n+1개를 n칸에 넣으면 적어도 한 칸에 2개
# 응용: 해시 충돌은 입력 공간이 출력 공간보다 크면 필연

def will_collide(input_space: int, hash_space: int) -> bool:
    return input_space > hash_space


# 32비트 해시는 출력 4 × 10⁹
# 100억 개의 ID를 32비트로 해시하면 충돌 보장
print(f"100억 → 32bit 충돌? {will_collide(10 ** 10, 2 ** 32)}")


# 생일 역설: 23명만 모여도 같은 생일 쌍이 50% 확률로 존재
def birthday_collision_prob(n: int, days: int = 365) -> float:
    no_collision = 1.0
    for i in range(n):
        no_collision *= (days - i) / days
    return 1 - no_collision


for n in [10, 23, 50, 100]:
    print(f"n={n}: 충돌 확률 = {birthday_collision_prob(n):.3f}")
```

비둘기집 원리는 단순하지만 강력합니다. 무손실 압축 알고리즘이 모든 입력을 줄일 수 없다는 사실도 이 원리의 직접적 결과입니다.

### 5단계: 포함-배제 원리

```python
# |A ∪ B| = |A| + |B| - |A ∩ B|
# |A ∪ B ∪ C| = |A| + |B| + |C| - |A∩B| - |A∩C| - |B∩C| + |A∩B∩C|


# 예: 100명 중 영어 학습자 60, 일어 40, 둘 다 20
def union_two(a: int, b: int, ab: int) -> int:
    return a + b - ab


print(f"적어도 하나 학습: {union_two(60, 40, 20)}명")

# 1~100 중 2 또는 3 또는 5의 배수 개수
def multiples_count(limit: int, n: int) -> int:
    return limit // n


limit = 100
m2, m3, m5 = multiples_count(limit, 2), multiples_count(limit, 3), multiples_count(limit, 5)
m6, m10, m15 = multiples_count(limit, 6), multiples_count(limit, 10), multiples_count(limit, 15)
m30 = multiples_count(limit, 30)

answer = m2 + m3 + m5 - m6 - m10 - m15 + m30
print(f"1~100 중 2,3,5의 배수: {answer}개")
```

포함-배제는 중복을 정확히 제거하는 도구입니다. 데이터베이스의 OR 쿼리 카디널리티 추정에도 쓰입니다.

## 이 코드에서 주목할 점

- 조합론은 입력 공간의 크기를 정확히 계산하는 도구
- 순열 = 순서 O, 조합 = 순서 X
- 비둘기집 원리는 충돌의 필연성을 설명
- 포함-배제는 OR 셈의 표준 기법

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 순열·조합 혼동 | 잘못된 경우의 수 | "순서가 의미 있나?" 질문 |
| 곱·합의 법칙 혼동 | 독립/배타 구분 실패 | "동시 발생인가, 둘 중 하나인가" |
| 중복 허용 여부 무시 | 같은 원소 재선택 가능성 | 중복 순열은 nʳ |
| 비둘기집 원리 약식 적용 | n+1이 아닌 경우 적용 | 정확한 조건 확인 |
| 포함-배제 부호 오류 | 짝수개 교집합 부호 +/- | 일반화된 공식 참조 |

## 실무에서는 이렇게 쓰입니다

- 비밀번호 정책 설계 (키 공간 크기 계산)
- 해시 함수 충돌 확률 분석 (생일 역설)
- A/B 테스트 표본 크기 산정
- 데이터베이스 쿼리 옵티마이저의 카디널리티 추정
- 분산 시스템의 ID 충돌 회피 (UUID, Snowflake)

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 "이 디자인이 충분한가?"를 정량적으로 판단합니다. UUID v4의 충돌 확률, 32비트 해시의 한계, 비밀번호 정책의 보안 수준 — 모두 조합론으로 즉답합니다. 또한 "최악의 경우 몇 가지 입력을 처리해야 하는가?"를 계산하여 알고리즘 선택의 근거로 삼습니다.

## 체크리스트

- [ ] 곱·합의 법칙을 구분할 수 있는가
- [ ] 순열과 조합의 차이를 안전하게 판단할 수 있는가
- [ ] 비둘기집 원리로 해시 충돌의 필연성을 설명할 수 있는가
- [ ] 포함-배제 원리로 OR 카디널리티를 계산할 수 있는가
- [ ] 생일 역설을 직관적으로 이해했는가

## 연습 문제

1. 8자리 비밀번호(영문 대소문자+숫자+8개 특수문자)의 키 공간 크기를 계산하고, 초당 10⁹회 시도 시 평균 크래킹 시간을 구하세요.

2. 1부터 1000 사이에서 7 또는 11 또는 13의 배수의 개수를 포함-배제 원리로 구하세요.

3. UUID v4의 충돌 확률을 생일 역설로 추정하세요. 1조 개를 생성하면 충돌 확률은 얼마인가요?

## 정리 및 다음 단계

조합론은 "가능성의 크기"를 정확히 세는 수학입니다. 곱·합의 법칙, 순열·조합, 이항정리, 비둘기집·포함-배제 원리는 보안·해시·확률 분석의 표준 도구입니다.

다음 글에서는 이산수학의 또 다른 큰 영역 — 그래프 이론의 기초 — 를 살펴봅니다.

<!-- toc:begin -->
- [이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- [명제와 논리](./02-propositions-and-logic.md)
- [집합과 함수](./03-sets-and-functions.md)
- [관계와 동치관계](./04-relations-and-equivalence.md)
- [증명 방법](./05-proof-techniques.md)
- [수열과 점화식](./06-sequences-and-recurrence.md)
- **조합과 경우의 수 (현재 글)**
- 그래프 이론 기초 (예정)
- 트리와 그래프 탐색 (예정)
- 알고리즘과 이산수학의 연결 (예정)
<!-- toc:end -->

## 참고 자료

- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 6](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Wikipedia — Combinatorics](https://en.wikipedia.org/wiki/Combinatorics)
- [Wikipedia — Pigeonhole Principle](https://en.wikipedia.org/wiki/Pigeonhole_principle)
- [Wikipedia — Birthday Problem](https://en.wikipedia.org/wiki/Birthday_problem)

Tags: Computer Science, 이산수학, 조합론, 순열, 비둘기집 원리, 확률
