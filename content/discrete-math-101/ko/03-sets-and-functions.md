---
series: discrete-math-101
episode: 3
title: "Discrete Math 101 (3/10): 집합과 함수"
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
  - 집합론
  - 함수
  - 데이터베이스
  - 자료구조
seo_description: 집합 연산과 함수의 분류를 통해 자료구조와 데이터베이스의 수학적 기반을 설명합니다.
last_reviewed: '2026-05-12'
---

# Discrete Math 101 (3/10): 집합과 함수

이 글은 Discrete Math 101 시리즈의 3번째 글입니다.


![Discrete Math 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/03/03-01-big-picture.ko.png)
*Discrete Math 101 3장 흐름 개요*

## 먼저 던지는 질문

- 집합 표기와 기본 연산은 어떻게 읽어야 할까요?
- 합집합, 교집합, 차집합, 곱집합은 실무에서 어디에 쓰일까요?
- 함수의 정의역, 공역, 치역은 무엇이 다를까요?

## 왜 중요한가

데이터베이스의 한 행은 곱집합의 원소입니다. JOIN은 곱집합 위에서 술어를 평가합니다. 해시맵은 키 집합에서 값 집합으로 가는 부분 함수로 볼 수 있습니다. 함수형 프로그래밍의 `map` 역시 집합 사이에 함수를 적용하는 구조입니다. 집합과 함수를 모르면 이런 도구의 본질을 끝까지 설명하기 어렵습니다.

> 자료구조는 집합이나 함수를 효율적으로 구현한 결과물입니다.

## 한눈에 보는 개념

> 집합은 원소의 컬렉션이고, 함수는 집합 사이의 대응입니다. 둘을 함께 보면 거의 모든 데이터 구조가 설명됩니다.

```text
   Set A           Function f: A → B           Set B
  ┌─────┐                                    ┌─────┐
  │ a₁  │ ─────────── f(a₁) ─────────────── │ b₁  │
  │ a₂  │ ─────────── f(a₂) ─────────────── │ b₂  │
  │ a₃  │ ─────────── f(a₃) ─────────────── │ b₃  │
  └─────┘                                    └─────┘
   domain                                    codomain
                                              range
                                              ⊆ codomain
```

## 핵심 용어

| 용어 | 기호 | 의미 |
| --- | --- | --- |
| Element | a ∈ A | a가 집합 A의 원소 |
| Subset | A ⊆ B | A의 모든 원소가 B에 포함 |
| Cartesian product | A × B | 순서쌍 (a, b)의 집합 |
| Function | f: A → B | A의 각 원소를 B의 한 원소로 대응 |
| Injective | one-to-one | 서로 다른 입력이 서로 다른 출력으로 감 |

## 전후 비교

**Before — without set thinking:**

```python
# Manually deduplicate
result = []
for item in items:
    if item not in result:
        result.append(item)
```

**After — using sets:**

```python
# Leverage the set's intrinsic property
result = list(set(items))
```

## 단계별로 따라가기

### 1단계: 집합 표기

```python
# Roster notation: list elements
A = {1, 2, 3, 4, 5}

# Set-builder notation: state a condition
B = {x for x in range(1, 11) if x % 2 == 0}

# Power set: the set of all subsets
from itertools import chain, combinations

def power_set(s: set) -> list[set]:
    items = list(s)
    return [
        set(combo)
        for r in range(len(items) + 1)
        for combo in combinations(items, r)
    ]

print(f"A = {A}")
print(f"B = {B}")
print(f"|A| = {len(A)}, |P(A)| = {2 ** len(A)}")
print(f"P({{1,2}}) = {power_set({1, 2})}")
```

`|A| = n`이면 멱집합의 크기는 `2ⁿ`입니다. 부분집합의 수가 지수적으로 늘어난다는 사실은 알고리즘 복잡도가 왜 갑자기 폭발하는지를 설명하는 가장 기본적인 감각입니다.

### 2단계: 집합 연산

```python
A = {1, 2, 3, 4, 5}
B = {4, 5, 6, 7, 8}
U = set(range(1, 11))  # universal set

print(f"A ∪ B = {A | B}")        # union
print(f"A ∩ B = {A & B}")        # intersection
print(f"A - B = {A - B}")        # difference
print(f"A △ B = {A ^ B}")        # symmetric difference
print(f"A^c (∈ U) = {U - A}")     # complement
print(f"|A ∪ B| = |A| + |B| - |A ∩ B| = {len(A) + len(B) - len(A & B)}")
```

마지막 식은 포함-배제 원리의 가장 단순한 형태입니다. 조합론 장으로 넘어가면 이 아이디어가 훨씬 큰 계산으로 확장됩니다.

### 3단계: 곱집합과 관계

```python
from itertools import product

A = {1, 2, 3}
B = {"x", "y"}

# A × B = {(a, b) | a ∈ A, b ∈ B}
cartesian = set(product(A, B))
print(f"A × B = {cartesian}")
print(f"|A × B| = |A| × |B| = {len(cartesian)}")

# A database row is an element of a Cartesian product
users = {"alice", "bob"}
roles = {"admin", "user"}
permissions = set(product(users, roles))
print(f"Possible (user, role) pairs: {permissions}")
```

데이터베이스 테이블 스키마는 그 자체로 곱집합입니다. `CROSS JOIN`은 말 그대로 그 곱집합을 계산합니다.

### 4단계: 함수의 종류

```python
def is_injective(f: dict) -> bool:
    """Injective: distinct inputs map to distinct outputs"""
    return len(set(f.values())) == len(f)

def is_surjective(f: dict, codomain: set) -> bool:
    """Surjective: every codomain element is hit"""
    return set(f.values()) == codomain

def is_bijective(f: dict, codomain: set) -> bool:
    """Bijective: both injective and surjective"""
    return is_injective(f) and is_surjective(f, codomain)

f1 = {1: "a", 2: "b", 3: "c"}     # injective; surjectivity depends on codomain
f2 = {1: "a", 2: "a", 3: "b"}     # not injective
codomain = {"a", "b", "c"}

print(f"f1 injective: {is_injective(f1)}")
print(f"f1 surjective onto {codomain}: {is_surjective(f1, codomain)}")
print(f"f1 bijective: {is_bijective(f1, codomain)}")
print(f"f2 injective: {is_injective(f2)}")
```

해시 충돌은 함수가 단사가 아니라는 뜻입니다. 좋은 해시 함수는 완전한 단사는 아니어도 실무적으로 충분히 “거의 단사처럼” 행동하도록 설계됩니다.

### 5단계: 합성과 역함수

```python
def compose(g, f):
    """(g ∘ f)(x) = g(f(x))"""
    return lambda x: g(f(x))

def inverse(f: dict) -> dict:
    """Inverse exists only when f is injective"""
    if not is_injective(f):
        raise ValueError("non-injective functions have no inverse")
    return {v: k for k, v in f.items()}

f = lambda x: x + 1
g = lambda x: x * 2

h = compose(g, f)  # h(x) = 2(x + 1)
print(f"h(3) = {h(3)}")  # 8

mapping = {1: "a", 2: "b", 3: "c"}
inv = inverse(mapping)
print(f"Inverse: {inv}")
```

함수 합성은 함수형 프로그래밍의 핵심이고, 역함수는 암호학과 데이터 변환에서 빠지지 않는 개념입니다. 파이프라인 설계를 수학적으로 읽는 기본 도구라고 보면 됩니다.

## 주목할 점

- 멱집합의 크기는 `2ⁿ`이므로 모든 부분집합을 다 보는 탐색은 지수 시간입니다.
- 곱집합은 데이터베이스 테이블의 수학적 모델입니다.
- 단사성과 전사성은 해시, 암호, 매핑 설계의 기준이 됩니다.
- 합성과 역함수는 변환 파이프라인을 이해하는 핵심 도구입니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 집합과 리스트를 섞어 생각한다 | 순서와 중복 가정이 깨진다 | 집합은 무순서, 중복 없음임을 명확히 둔다 |
| 공역과 치역을 혼동한다 | 전사 판정이 틀린다 | 공역은 선언, 치역은 실제 출력이다 |
| 부분 함수와 전함수를 구분하지 않는다 | 누락 입력에서 오류가 난다 | `dict` 같은 구현은 미정의 입력을 따로 처리한다 |
| 합성 순서를 바꾼다 | `(g ∘ f)(x)`를 반대로 읽는다 | 오른쪽에서 왼쪽으로 적용한다 |
| 역함수가 항상 있다고 가정한다 | 비단사 함수에서 정의가 깨진다 | 먼저 단사 여부를 확인한다 |

## 실무에서는 이렇게 사용합니다

- Python `set`과 `dict`는 집합과 함수의 직접 구현입니다.
- SQL JOIN은 곱집합 위에서 술어로 필터링하는 과정입니다.
- 해시맵은 키에서 값으로 가는 부분 함수입니다.
- 데이터 마이그레이션은 스키마 사이의 함수로 읽을 수 있습니다.
- ORM은 객체 도메인과 관계형 도메인 사이의 대응입니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 자료구조를 고를 때 “이건 집합인가, 멀티셋인가, 순서가 필요한가”부터 묻습니다. 또한 함수가 단사인지, 역함수를 만들 수 있는지, 동일 입력에 대해 항상 동일 출력이 보장되는지 확인합니다. 이런 감각이 결국 멱등성, 캐시 키 설계, 스키마 변환 안정성으로 이어집니다.

## 체크리스트

- [ ] 집합과 리스트의 차이를 설명할 수 있다
- [ ] `|P(A)| = 2ⁿ` 공식을 기억한다
- [ ] 단사, 전사, 전단사를 구분할 수 있다
- [ ] 함수 합성의 순서를 이해한다
- [ ] 역함수가 존재하는 조건을 안다

## 연습 문제

1. `{a, b, c}`의 멱집합을 모두 나열하고 원소 수가 `2³ = 8`인지 확인해 보세요.

2. `f(x) = x²`가 실수 전체에서는 단사가 아니지만 `[0, ∞)`에서는 단사인 이유를 설명해 보세요.

3. 자신이 다루는 데이터베이스 테이블 하나를 골라, 어떤 곱집합의 부분집합으로 볼 수 있는지 적어 보세요.

## 정리 및 다음 단계

집합은 데이터를 담는 그릇이고, 함수는 집합 사이의 명확한 대응입니다. 멱집합, 곱집합, 합성, 역함수까지 이해하면 자료구조와 데이터베이스를 훨씬 더 본질적으로 읽을 수 있습니다.

다음 글에서는 집합 위에 정의되는 가장 중요한 구조인 관계와 동치관계를 살펴보겠습니다.

## 실전 보강: 증명, 집합 연산, 그래프 알고리즘을 연결해서 보기

이산수학은 정의를 외우는 과목이 아니라, 명제를 세우고 검증하는 절차를 훈련하는 과목입니다. 아래 내용은 증명 예시, 집합 연산표, 그래프 알고리즘을 하나의 흐름으로 연결합니다.

### 1) 짧은 직접 증명 예시

명제: 임의의 정수 `n`에 대해 `n`이 짝수이면 `n^2`도 짝수입니다.

증명: `n`이 짝수이므로 어떤 정수 `k`가 존재하여 `n = 2k`입니다. 그러면
`n^2 = (2k)^2 = 4k^2 = 2(2k^2)` 이고, `2k^2`는 정수이므로 `n^2`는 짝수입니다.
따라서 명제가 성립합니다.

핵심은 결론을 먼저 믿는 것이 아니라, 정의(짝수의 정의)를 대입해 식을 변형하는 것입니다.

### 2) 집합 연산표로 규칙 확인

전체집합 `U = {1,2,3,4,5,6}`, `A = {1,2,3,4}`, `B = {3,4,5}`일 때:

| 연산 | 결과 |
| --- | --- |
| `A ∪ B` | `{1,2,3,4,5}` |
| `A ∩ B` | `{3,4}` |
| `A \ B` | `{1,2}` |
| `B \ A` | `{5}` |
| `A^c` (in U) | `{5,6}` |

이 표는 드모르간 법칙 검증에도 바로 사용됩니다.
`(A ∪ B)^c = A^c ∩ B^c`를 실제 원소로 계산해 양변이 같음을 확인할 수 있습니다.

### 3) 귀납법 예시

명제: `1 + 2 + ... + n = n(n+1)/2`.

- 기저 단계: `n=1`에서 좌변 `1`, 우변 `1(2)/2 = 1`로 성립.
- 귀납 가정: `n=k`에서 성립한다고 가정.
- 귀납 단계:
  `1+...+k+(k+1) = k(k+1)/2 + (k+1)`
  `= (k+1)(k+2)/2`.

따라서 모든 자연수 `n`에 대해 성립합니다.

귀납법의 핵심은 “k에서 참이면 k+1도 참”이라는 연결 고리를 명시하는 것입니다.

### 4) 그래프 알고리즘: BFS 거리 계산

```python
from collections import deque

def bfs_distance(graph: dict[int, list[int]], start: int) -> dict[int, int]:
    dist = {start: 0}
    q = deque([start])
    while q:
        v = q.popleft()
        for nxt in graph.get(v, []):
            if nxt not in dist:
                dist[nxt] = dist[v] + 1
                q.append(nxt)
    return dist

G = {
    1: [2, 3],
    2: [4],
    3: [4, 5],
    4: [6],
    5: [],
    6: [],
}
print(bfs_distance(G, 1))
```

BFS는 간선 가중치가 동일할 때 최단 거리 계층을 계산합니다. 증명 관점에서는 “큐에서 먼저 나온 정점의 거리는 이미 최단”이라는 불변식을 유지하는 것이 핵심입니다.

### 5) DFS와 BFS 선택 기준

| 기준 | BFS | DFS |
| --- | --- | --- |
| 주 용도 | 최단 거리(무가중치) | 경로 존재성, 사이클 탐지 |
| 자료구조 | Queue | Stack(또는 재귀) |
| 메모리 특성 | 폭이 넓으면 증가 | 깊이가 깊으면 증가 |
| 직관 | 레벨 단위 탐색 | 한 경로 끝까지 탐색 |

문제의 요구가 “최소 단계”인지 “탐색 가능성”인지 먼저 구분하면 알고리즘 선택이 쉬워집니다.

### 6) 이산수학에서 알고리즘으로 넘어갈 때 체크 포인트

- 명제를 자연어로 쓴 뒤 기호화할 수 있는가
- 필요한 정의(짝수, 함수, 관계, 연결성)를 정확히 호출했는가
- 반례 하나로 거짓을 보일 수 있는 문제인지 확인했는가
- 증명 불변식을 코드 루프 불변식으로 옮길 수 있는가

이산수학의 강점은 계산 자체보다 **판단 근거를 명시하는 습관**입니다. 이 습관이 자료구조, 알고리즘, 시스템 설계까지 그대로 이어집니다.

## 실전 확장: 집합 연산과 함수 성질을 코드로 고정하기

집합과 함수는 데이터 정합성 규칙을 쓰는 언어입니다. 규칙을 한국어 문장으로만 두면 해석이 갈리므로, 집합 기호와 테스트 코드로 동시에 고정해야 합니다.

### 집합 연산 워크드 예시

`U={1..12}`, `A=짝수 집합`, `B=3의 배수 집합`일 때:

| 연산 | 결과 |
| --- | --- |
| `A ∩ B` | `{6, 12}` |
| `A ∪ B` | `{2,3,4,6,8,9,10,12}` |
| `A \ B` | `{2,4,8,10}` |
| `B \ A` | `{3,9}` |

```python
U = set(range(1, 13))
A = {x for x in U if x % 2 == 0}
B = {x for x in U if x % 3 == 0}
print("A∩B", A & B)
print("A∪B", A | B)
print("A\B", A - B)
print("B\A", B - A)
```

수식과 출력이 일치하면 모델링 오류 가능성이 크게 줄어듭니다.

### 함수의 단사/전사/전단사 점검

함수 `f: A→B`에 대해:

- 단사: 서로 다른 입력이 같은 출력으로 가지 않는다.
- 전사: 공역의 모든 원소가 적어도 한 번 출력된다.
- 전단사: 단사이면서 전사이다.

```python
def classify_function(mapping: dict[int, int], codomain: set[int]) -> tuple[bool, bool, bool]:
    values = list(mapping.values())
    injective = len(values) == len(set(values))
    surjective = set(values) == codomain
    bijective = injective and surjective
    return injective, surjective, bijective

f = {1: 10, 2: 20, 3: 30}
print(classify_function(f, {10, 20, 30}))
```

서비스에서 ID 변환 함수가 전단사인지 확인하면 역조회 가능성과 충돌 가능성을 동시에 판단할 수 있습니다.

### 관계형 데이터와 데카르트 곱

주문 테이블을 `User × Product × Time`의 부분집합으로 보면, 누락 제약을 엄밀하게 표현할 수 있습니다. 예를 들어 `User`가 비어 있지 않은 주문만 허용한다면 조건은 `∀o ∈ Orders, o.user_id ∈ Users`입니다.

### 짧은 증명 앵커

명제: 유한집합 `A`, `B`에 대해 `|A ∪ B| = |A| + |B| - |A ∩ B|`.

증명 아이디어: `A`와 `B`를 단순 합하면 교집합 원소를 두 번 셉니다. 중복된 `|A∩B|`를 한 번 빼면 정확한 합집합 크기가 됩니다.

## 심화 워크숍: 함수 설계와 데이터 변환 검증

### 함수 합성과 파이프라인 안정성

함수 `f: Raw -> Clean`, `g: Clean -> Feature`가 있을 때 파이프라인은 `g∘f`입니다. 이때 `f`의 공역이 `g`의 정의역을 벗어나면 런타임 오류가 납니다. 타입 검증과 계약 테스트는 이 경계를 확인하는 작업입니다.

### 이미지 처리 예시를 집합으로 해석

원본 집합 `R`에서 유효 확장자 집합 `E`, 크기 제한 집합 `S`, 바이러스 스캔 통과 집합 `V`를 두면 최종 허용은 `H = R ∩ E ∩ S ∩ V`입니다.

```python
def accepted(raw: set[str], ext_ok: set[str], size_ok: set[str], scan_ok: set[str]) -> set[str]:
    return raw & ext_ok & size_ok & scan_ok
```

### 역함수 가능성 점검

주문 번호 인코딩 함수가 전단사면 역함수가 존재해 복구가 쉽습니다. 단사가 아니면 충돌이 발생하고, 전사가 아니면 사용되지 않는 코드 공간이 남습니다.

| 성질 | 운영 영향 |
| --- | --- |
| 단사 아님 | 서로 다른 입력이 같은 키로 충돌 |
| 전사 아님 | 키 공간 낭비, 불필요한 제약 |
| 전단사 | 역변환 가능, 추적 용이 |

### 짧은 증명 앵커

명제: `f`, `g`가 단사이면 `g∘f`도 단사입니다.

증명: `(g∘f)(x1)=(g∘f)(x2)`라 하자. `g`가 단사이므로 `f(x1)=f(x2)`, 다시 `f`가 단사이므로 `x1=x2`입니다.

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

- **집합 표기와 기본 연산은 어떻게 읽어야 할까요?**
  - 본문의 기준은 집합과 함수를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **합집합, 교집합, 차집합, 곱집합은 실무에서 어디에 쓰일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **함수의 정의역, 공역, 치역은 무엇이 다를까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Discrete Math 101 (1/10): 이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- [Discrete Math 101 (2/10): 명제와 논리](./02-propositions-and-logic.md)
- **집합과 함수 (현재 글)**
- 관계와 동치관계 (예정)
- 증명 방법 (예정)
- 수열과 점화식 (예정)
- 조합과 경우의 수 (예정)
- 그래프 이론 기초 (예정)
- 트리와 그래프 탐색 (예정)
- 알고리즘과 이산수학의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [book-examples: discrete-math-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/discrete-math-101/ko)
- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 2](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Wikipedia — Set Theory](https://en.wikipedia.org/wiki/Set_theory)
- [Wikipedia — Function (mathematics)](https://en.wikipedia.org/wiki/Function_(mathematics))
- [Python Documentation — set, dict](https://docs.python.org/3/tutorial/datastructures.html#sets)

Tags: Computer Science, 이산수학, 집합론, 함수, 데이터베이스, 자료구조
