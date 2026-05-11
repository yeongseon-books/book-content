---
series: discrete-math-101
episode: 2
title: 명제와 논리
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
  - 명제 논리
  - 추론
  - 진리표
  - 술어 논리
seo_description: 명제, 진리값, 논리 연산자, 진리표, 술어와 양화사를 통해 모든 컴퓨터 추론의 기초를 배웁니다.
last_reviewed: '2026-05-04'
---

# 명제와 논리

> Discrete Math 101 시리즈 (2/10)


## 이 글에서 다룰 문제

코드의 모든 if 문은 명제의 평가입니다. 데이터베이스의 모든 쿼리는 술어의 충족 여부를 묻습니다. 회로 설계의 모든 게이트는 논리 연산입니다. 명제 논리를 모르면 복잡한 조건문을 단순화할 수도, 정확히 디버깅할 수도 없습니다.

> 명제 논리 = 정확한 사고를 위한 기호 체계

이 글에서는 논리의 기초를 다지고 다음 글의 집합 이론으로 연결합니다.

## 전체 흐름
> 명제는 진리값(참/거짓)을 가지며, 논리 연산자로 결합됩니다. 모든 결합은 진리표로 정의됩니다.

```text
  명제 P, Q  ──→  연산자  ──→  복합 명제
                 ┌──────────┐
                 │ ¬ (NOT)  │
                 │ ∧ (AND)  │
                 │ ∨ (OR)   │
                 │ → (함의) │
                 │ ↔ (동치) │
                 └──────────┘
                       ↓
                    진리표
                       ↓
                  논리적 동치
```

## Before / After

**Before — 논리를 모를 때:**

```python
# 중첩된 조건문, 단순화 불가
if not (x > 0 and y > 0):
    if not (x > 0):
        handle_x()
    if not (y > 0):
        handle_y()
```

**After — 드모르간 법칙으로 단순화:**

```python
# ¬(P ∧ Q) ≡ ¬P ∨ ¬Q
if x <= 0 or y <= 0:
    if x <= 0:
        handle_x()
    if y <= 0:
        handle_y()
```

## 단계별로 따라하기

### 1단계: 명제와 진리값

```python
# 명제: 참 또는 거짓이 명확한 문장
# 비명제: "오늘 날씨 어때?"는 의문문이라 명제가 아님

propositions = {
    "2는 짝수이다": True,
    "파리는 미국의 수도이다": False,
    "100은 소수이다": False,
    "1 + 1 = 2": True,
}

for statement, truth in propositions.items():
    print(f"{statement}: {truth}")
```

### 2단계: 기본 논리 연산자

```python
def NOT(p: bool) -> bool:
    return not p


def AND(p: bool, q: bool) -> bool:
    return p and q


def OR(p: bool, q: bool) -> bool:
    return p or q


def IMPLIES(p: bool, q: bool) -> bool:
    """P → Q: P가 참이고 Q가 거짓일 때만 거짓"""
    return (not p) or q


def IFF(p: bool, q: bool) -> bool:
    """P ↔ Q: 진리값이 같을 때만 참"""
    return p == q


print(IMPLIES(True, False))  # False
print(IMPLIES(False, True))  # True (전제가 거짓이면 항상 참)
print(IFF(True, True))       # True
```

함의 P → Q에서 "P가 거짓이면 항상 참"이라는 점이 직관에 반할 수 있습니다. "비가 오면 우산을 챙긴다"는 약속은 비가 오지 않은 날에는 깨지지 않습니다.

### 3단계: 진리표 자동 생성

```python
from itertools import product


def truth_table(variables: list[str], expr) -> None:
    """주어진 변수와 표현식의 진리표를 출력합니다."""
    header = " | ".join(variables) + " | result"
    print(header)
    print("-" * len(header))
    for values in product([False, True], repeat=len(variables)):
        env = dict(zip(variables, values))
        result = expr(**env)
        row = " | ".join(str(v)[0] for v in values) + f" | {str(result)[0]}"
        print(row)


# (P ∧ Q) → P 의 진리표
truth_table(["P", "Q"], lambda P, Q: IMPLIES(AND(P, Q), P))
```

진리표는 명제 논리의 "실행"입니다. 모든 변수 조합에 대해 결과를 나열하므로 동치 검증이 항상 가능합니다.

### 4단계: 드모르간 법칙 검증

```python
# ¬(P ∧ Q) ≡ ¬P ∨ ¬Q
# ¬(P ∨ Q) ≡ ¬P ∧ ¬Q

def equivalent(expr1, expr2, variables: list[str]) -> bool:
    """두 표현식이 모든 입력에서 같은 결과를 내는지 확인합니다."""
    for values in product([False, True], repeat=len(variables)):
        env = dict(zip(variables, values))
        if expr1(**env) != expr2(**env):
            return False
    return True


lhs = lambda P, Q: NOT(AND(P, Q))
rhs = lambda P, Q: OR(NOT(P), NOT(Q))

print(f"드모르간 법칙 성립: {equivalent(lhs, rhs, ['P', 'Q'])}")
```

### 5단계: 술어와 양화사

```python
# 술어(predicate): 변수에 따라 진리값이 결정되는 명제 함수
def is_even(n: int) -> bool:
    return n % 2 == 0


# 전칭 양화 ∀: "모든 n에 대해"
def for_all(domain, predicate) -> bool:
    return all(predicate(x) for x in domain)


# 존재 양화 ∃: "어떤 n이 존재하여"
def there_exists(domain, predicate) -> bool:
    return any(predicate(x) for x in domain)


numbers = [2, 4, 6, 8, 10]

print(f"∀x ∈ {numbers}: x는 짝수 = {for_all(numbers, is_even)}")
print(f"∃x ∈ [1,2,3]: x는 짝수 = {there_exists([1, 2, 3], is_even)}")
```

양화사는 SQL의 ALL, ANY와 동일한 개념입니다. `WHERE x > ALL(SELECT ...)`은 전칭 양화입니다.

## 이 코드에서 주목할 점

- 모든 논리 연산자는 진리표로 정의됩니다
- 함의 P → Q는 ¬P ∨ Q와 동치입니다
- 드모르간 법칙은 부정의 분배를 제어합니다
- 양화사 ∀, ∃는 술어를 명제로 변환합니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 함의의 진리값 오해 | "전제가 거짓이면 참" 직관에 반함 | "거짓에서 무엇이든 도출"을 기억 |
| AND/OR 우선순위 혼동 | 괄호 누락으로 버그 | 항상 명시적으로 괄호 사용 |
| 부정의 잘못된 분배 | ¬(P ∧ Q) = ¬P ∧ ¬Q로 오인 | 드모르간 법칙 암기 |
| ∀와 ∃ 순서 바꿈 | "모든 x에 어떤 y" vs "어떤 y가 모든 x에" 다름 | 양화사 순서 엄격히 유지 |
| 술어와 명제 혼동 | 변수가 있는 P(x)는 명제가 아님 | 양화사로 닫아야 명제가 됨 |

## 실무에서는 이렇게 쓰입니다

- SQL `WHERE` 절 최적화 시 논리적 동치 변환
- 코드 리뷰에서 복잡한 조건문을 드모르간 법칙으로 단순화
- 회로 설계의 논리 게이트(AND, OR, NOT, NAND, NOR)
- 정형 검증(formal verification)에서 시스템 속성을 명제로 표현
- 검색 엔진의 불리언 쿼리(`apple AND NOT pie`)

## 체크리스트

- [ ] 다섯 가지 논리 연산자의 진리표를 그릴 수 있는가
- [ ] 함의 P → Q의 의미를 직관적으로 설명할 수 있는가
- [ ] 드모르간 법칙을 코드에 적용할 수 있는가
- [ ] ∀와 ∃의 차이를 SQL 예시로 설명할 수 있는가
- [ ] 술어와 명제의 차이를 이해했는가

## 정리 및 다음 단계

명제 논리는 모든 컴퓨터 추론의 기초입니다. 다섯 가지 연산자, 진리표, 동치 법칙을 도구로 사용하면 복잡한 조건문도 정확히 다룰 수 있습니다. 양화사를 통해 명제는 술어로 확장되고, 더 풍부한 표현이 가능해집니다.

다음 글에서는 명제 논리와 함께 이산수학의 양대 기초인 "집합과 함수"를 살펴봅니다.

<!-- toc:begin -->
- [이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- **명제와 논리 (현재 글)**
- 집합과 함수 (예정)
- 관계와 동치관계 (예정)
- 증명 방법 (예정)
- 수열과 점화식 (예정)
- 조합과 경우의 수 (예정)
- 그래프 이론 기초 (예정)
- 트리와 그래프 탐색 (예정)
- 알고리즘과 이산수학의 연결 (예정)
<!-- toc:end -->

## 참고 자료

- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 1](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Stanford Encyclopedia of Philosophy — Propositional Logic](https://plato.stanford.edu/entries/logic-propositional/)
- [Wikipedia — De Morgan's Laws](https://en.wikipedia.org/wiki/De_Morgan%27s_laws)
- [MIT OCW — Mathematics for Computer Science, Lecture 1-3](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)

Tags: Computer Science, 이산수학, 명제 논리, 추론, 진리표, 술어 논리
