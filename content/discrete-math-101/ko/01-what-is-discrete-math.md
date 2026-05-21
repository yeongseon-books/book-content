---
series: discrete-math-101
episode: 1
title: "Discrete Math 101 (1/10): 이산수학이란 무엇인가?"
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
  - 수학 입문
  - 전공 개요
  - 논리
  - 집합
seo_description: 이산수학의 범위와 연속 수학과의 차이, 그리고 컴퓨터공학의 공용어인 이유를 정리합니다.
last_reviewed: '2026-05-12'
---

# Discrete Math 101 (1/10): 이산수학이란 무엇인가?

이 글은 Discrete Math 101 시리즈의 1번째 글입니다.

![Discrete Math 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/01/01-01-big-picture.ko.png)
*Discrete Math 101 1장 흐름 개요*

## 먼저 던지는 질문

- 이산수학과 연속 수학은 무엇이 다를까요?
- 이산수학의 다섯 축은 어떻게 연결될까요?
- 컴퓨터공학 커리큘럼에서 왜 이산수학이 필수일까요?

## 왜 중요한가

알고리즘을 분석하려면 점화식과 조합론이 필요합니다. 데이터베이스를 이해하려면 집합과 관계 이론이 필요합니다. 네트워크를 설계하려면 그래프 이론이 필요합니다. 이산수학은 그냥 하나의 수학 과목이 아니라, 컴퓨터공학 전반이 공유하는 사고의 문법입니다.

> 이산수학은 컴퓨터과학자가 생각을 구조화할 때 쓰는 언어입니다.

이 시리즈는 핵심 개념을 한 편씩 분리해서 설명하되, 매번 컴퓨터공학과의 연결을 함께 보여 줍니다.

## 한눈에 보는 개념

> 이산수학은 논리, 집합, 함수, 조합론, 그래프라는 다섯 축 위에 서 있고, 이 모두는 이산성이라는 공통 성질로 묶입니다.

```text
            Logic (propositions, proofs)
                |
        Sets / Functions / Relations
                |
        ┌───────┼───────┐
   Combinatorics  Sequences   Graphs
       (count)   (recurrence) (structure)
        └───────┼───────┘
                |
        Algorithms / Data structures
                |
        Computer science applications
```

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| Discrete | 분리된 단위로 셀 수 있는 성질 |
| Continuous | 끊김 없이 이어지는 성질 |
| Proposition | 참 또는 거짓이 분명한 문장 |
| Set | 서로 구별되는 원소들의 모임 |
| Graph | 정점과 간선으로 이루어진 구조 |

## 전후 비교

**Before — without discrete math:**

```python
# "왜 이게 O(log n)인가?"에 답하기 어려움
def binary_search(data, target):
    low, high = 0, len(data) - 1
    while low <= high:
        mid = (low + high) // 2
        if data[mid] == target:
            return mid
        elif data[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```

**After — with discrete math:**

```python
# 점화식 T(n) = T(n/2) + 1로 표현
# Master Theorem으로 O(log n)임을 증명
# "sorted array"가 total-order 전제임도 인식
def binary_search(data, target):
    """Precondition: data is sorted under a total order.
    Complexity: T(n) = T(n/2) + O(1) ⟹ O(log n)
    """
    low, high = 0, len(data) - 1
    while low <= high:
        mid = (low + high) // 2
        if data[mid] == target:
            return mid
        elif data[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```

## 단계별로 따라가기

### 1단계: 이산과 연속의 차이

```python
# 연속: [0, 1] 구간에 값이 무한히 많음
# 이산: {0, 1, 2, 3}은 명확히 셀 수 있음
import math

continuous_sample = [i * 0.0001 for i in range(10001)]  # an approximation
discrete_set = list(range(11))                          # exact

print(f"Continuous samples: {len(continuous_sample)}")
print(f"Discrete size: {len(discrete_set)}")
print(f"Continuous gap: {continuous_sample[1] - continuous_sample[0]}")
print(f"Discrete gap: {discrete_set[1] - discrete_set[0]}")
```

컴퓨터 메모리는 비트 단위로 나뉘어 있기 때문에 본질적으로 이산적입니다. 부동소수점 수는 실수를 표현하는 것이 아니라 근사합니다. 이 차이를 이해해야 왜 컴퓨터과학의 기초 수학이 미적분보다 이산수학에 더 가까운지 감이 잡힙니다.

### 2단계: 명제와 진리값

```python
# 명제: 참/거짓이 명확한 문장
def is_prime(n: int) -> bool:
    """Return True if n is prime."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

# "7 is prime"은 참인 명제
# "9 is prime"은 거짓인 명제
print(f"7 is prime: {is_prime(7)}")  # True
print(f"9 is prime: {is_prime(9)}")  # False
```

명제 논리는 모든 컴퓨터 추론의 출발점입니다. `if`, `while`, SQL의 `WHERE` 절은 모두 결국 명제의 진리값을 평가합니다.

### 3단계: 집합 연산

```python
# 집합은 가장 기본적인 이산 구조
A = {1, 2, 3, 4, 5}
B = {3, 4, 5, 6, 7}

print(f"Union A ∪ B: {A | B}")
print(f"Intersection A ∩ B: {A & B}")
print(f"Difference A - B: {A - B}")
print(f"Symmetric difference A △ B: {A ^ B}")
print(f"Subset A ⊆ {A | B}: {A <= (A | B)}")
```

SQL `JOIN`, `UNION`, `INTERSECT`, `EXCEPT`는 모두 집합 연산의 직접적인 응용입니다. 집합을 이해하면 데이터베이스 연산이 갑자기 훨씬 덜 임의적으로 보입니다.

### 4단계: 그래프로 관계 모델링하기

```python
# 그래프는 정점과 간선으로 구성
graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C", "E"],
    "E": ["D"],
}

def neighbors(g: dict, node: str) -> list:
    """Return neighbors of the given vertex."""
    return g.get(node, [])

for node in graph:
    print(f"{node} neighbors: {neighbors(graph, node)}")
```

소셜 네트워크, 도로망, 의존성 트리, 인터넷 라우팅처럼 관계가 있는 거의 모든 구조는 그래프로 표현됩니다. 이산수학의 넓은 응용 범위를 가장 선명하게 보여 주는 분야가 바로 그래프 이론입니다.

### 5단계: 시리즈 로드맵

```python
roadmap = [
    (1, "What Is Discrete Mathematics?", "the big picture"),
    (2, "Propositions and Logic", "truth values, operators, inference"),
    (3, "Sets and Functions", "set ops, domain, range"),
    (4, "Relations and Equivalence", "properties, classes, partitions"),
    (5, "Proof Techniques", "direct, contradiction, induction"),
    (6, "Sequences and Recurrence", "recursion, Master Theorem"),
    (7, "Combinatorics", "permutations, combinations, pigeonhole"),
    (8, "Graph Theory Basics", "vertices, edges, paths, connectivity"),
    (9, "Trees and Graph Traversal", "BFS, DFS, spanning trees"),
    (10, "Discrete Math and Algorithms", "complexity, NP, applications"),
]

for num, title, keywords in roadmap:
    print(f"  {num:02d}. {title} — {keywords}")
```

## 주목할 점

- 이산 구조는 컴퓨터가 정확하게 표현할 수 있는 거의 유일한 대상입니다.
- 명제, 집합, 그래프는 서로 다른 추상화처럼 보이지만 모두 이산성을 공유합니다.
- 알고리즘 분석은 점화식과 조합론에 기대고 있습니다.
- SQL, 라우팅, 의존성 관리 같은 실무 도구는 이산수학 개념을 거의 그대로 사용합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 이산수학을 순수한 추상 수학으로만 본다 | 알고리즘 분석에서 바로 막힌다 | 모든 개념을 코드와 함께 연결한다 |
| 증명을 암기만 한다 | 새 문제에 적용하지 못한다 | 구조와 동기를 이해한다 |
| 그래프를 그림으로만 이해한다 | 큰 입력에서 다룰 수 없다 | 인접 리스트와 행렬 표현을 함께 익힌다 |
| 조합과 순열을 자주 섞는다 | 경우의 수를 잘못 센다 | 순서가 중요한지 먼저 묻는다 |
| 명제와 술어를 혼동한다 | 형식 논리에서 막힌다 | ∀, ∃ 양화사까지 함께 익힌다 |

## 실무에서는 이렇게 사용합니다

- 데이터베이스 쿼리 최적화는 집합 이론과 관계대수를 사용합니다.
- 의존성 관리 도구(npm, pip)는 그래프 위상 정렬에 의존합니다.
- 분산 합의 알고리즘은 명제 논리와 일관성 증명을 사용합니다.
- 추천 시스템은 그래프 이론 위에 서 있습니다.
- 컴파일러 최적화는 데이터 흐름 그래프를 분석합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 새로운 알고리즘을 볼 때 먼저 그 문제를 이산수학의 언어로 다시 표현합니다. “이건 그래프 탐색 문제다”, “이건 집합 분할 문제다”, “이건 점화식으로 풀 수 있다”처럼 구조를 먼저 이름 붙입니다. 문제의 구조를 정확히 부르는 순간 풀이의 절반은 이미 시작된 셈입니다.

또한 정확성에 집착합니다. “거의 맞다”는 말은 엔지니어링에서도 위험합니다. 이산수학이 참과 거짓의 세계라면, 시니어 엔지니어의 설계 감각도 그 기준을 그대로 가져옵니다.

## 체크리스트

- [ ] 이산과 연속의 차이를 자신의 말로 설명할 수 있다
- [ ] 논리, 집합, 함수, 조합론, 그래프의 다섯 축을 말할 수 있다
- [ ] 컴퓨터공학이 왜 이산수학을 필요로 하는지 이해했다
- [ ] SQL JOIN과 집합 연산의 연결을 설명할 수 있다
- [ ] 시리즈 전체 로드맵을 확인했다

## 연습 문제

1. 일상에서 볼 수 있는 이산적 대상 다섯 가지와 연속적 대상 다섯 가지를 찾아 보세요. 그중 컴퓨터가 정확하게 표현할 수 있는 것은 무엇인가요?

2. `binary_search`가 잘못된 값을 반환하는 정렬되지 않은 배열을 하나 만들어 보세요. 어떤 전제가 깨졌나요?

3. 자신의 소셜 네트워크를 그래프로 그려 보세요. 정점은 무엇이고, 간선은 무엇을 뜻하나요?

## 정리 및 다음 단계

이산수학은 셀 수 있는 대상을 다루는 수학이며, 컴퓨터과학의 공용어입니다. 논리, 집합, 함수, 조합론, 그래프라는 다섯 축은 알고리즘, 데이터베이스, 네트워크를 비롯한 거의 모든 핵심 분야와 직접 연결됩니다.

다음 글에서는 이산수학의 가장 작은 단위인 명제와, 모든 컴퓨터 추론을 움직이는 논리 연산자를 살펴보겠습니다.

## 실전 확장: 이산 모델링을 문제에 적용하는 절차

이산수학을 실제 문제에 적용할 때는 "정의-모델-검증" 세 단계를 분리해서 진행하는 것이 안전합니다. 먼저 대상의 상태를 집합과 관계로 정의하고, 다음으로 연산 규칙을 명제로 표현하며, 마지막으로 반례와 경계값으로 검증합니다.

### 모델링 예시: 회원 상태 전이

회원 상태를 `신규`, `활성`, `휴면`, `탈퇴` 네 가지로 두고 전이 관계를 정의합니다.

| 현재 상태 | 다음 상태 | 허용 여부 | 근거 |
| --- | --- | --- | --- |
| 신규 | 활성 | 허용 | 본인 인증 완료 |
| 활성 | 휴면 | 허용 | 1년 미접속 |
| 휴면 | 활성 | 허용 | 재인증 성공 |
| 탈퇴 | 활성 | 금지 | 정책상 복구 불가 |

관계로 쓰면 `R = {(신규,활성), (활성,휴면), (휴면,활성)}`입니다. 탈퇴 복구가 금지라는 사실은 관계에 쌍이 없다는 형태로 명시됩니다. 이 방식은 정책 문서와 코드의 불일치를 줄입니다.

### 진리표 기반 정책 점검

`P: 약관 동의`, `Q: 본인 인증`, `R: 계정 생성 허용`이라 두고 `R = P ∧ Q`를 사용한다고 가정합니다.

| P | Q | P ∧ Q | R |
| --- | --- | --- | --- |
| T | T | T | T |
| T | F | F | F |
| F | T | F | F |
| F | F | F | F |

여기서 정책 변경으로 "소셜 로그인은 인증 생략"이 추가되면 식이 `R = P ∧ (Q ∨ S)`로 바뀝니다. 변경 전후 진리표를 나란히 두면 어떤 입력 조합이 새롭게 허용되는지 바로 확인할 수 있습니다.

### 집합 연산 코드 앵커

```python
def policy_sets(total_users: set[int], agreed: set[int], verified: set[int]) -> dict[str, set[int]]:
    eligible = agreed & verified
    blocked = total_users - eligible
    only_agreed = agreed - verified
    only_verified = verified - agreed
    return {
        "eligible": eligible,
        "blocked": blocked,
        "only_agreed": only_agreed,
        "only_verified": only_verified,
    }

U = set(range(1, 11))
A = {1, 2, 3, 4, 7, 9}
V = {2, 3, 5, 7, 8}
print(policy_sets(U, A, V))
```

위 코드는 수식 `A ∩ V`, `U \ (A ∩ V)`를 그대로 구현합니다. 도메인 언어와 코드가 1:1로 대응되면 테스트 설계도 쉬워집니다.

### 간단한 그래프 모델과 탐색

실행 경로를 그래프로 보면 장애 분석이 빨라집니다.

```python
from collections import deque

def reachable(graph: dict[str, list[str]], start: str) -> set[str]:
    seen = {start}
    q = deque([start])
    while q:
        cur = q.popleft()
        for nxt in graph.get(cur, []):
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return seen

flow = {
    "login": ["token"],
    "token": ["profile", "home"],
    "profile": ["home"],
    "home": [],
}
print(reachable(flow, "login"))
```

도달 가능 집합이 기대와 다르면 전이 규칙 자체가 잘못되었을 수 있습니다. 이처럼 그래프는 프로그램 구조의 논리적 완전성을 확인하는 데 유용합니다.

## 심화 워크숍: 정의에서 검증까지 한 번에 연결하기

### 시나리오: 추천 시스템의 후보 필터링

추천 후보 집합 `C`에서 실제 노출 집합 `S`를 만들 때, 보통 다음 조건을 적용합니다.

- 재고가 있어야 한다.
- 사용자 차단 목록에 없어야 한다.
- 연령 제한을 만족해야 한다.

이를 집합으로 쓰면 `S = (C ∩ I ∩ A) \ B`입니다. 여기서 `I`는 재고 가능 집합, `A`는 연령 적합 집합, `B`는 차단 집합입니다. 기호로 적어 두면 정책 변경의 영향 범위를 좁힐 수 있습니다.

```python
def exposed(candidates: set[int], in_stock: set[int], age_ok: set[int], blocked: set[int]) -> set[int]:
    return (candidates & in_stock & age_ok) - blocked
```

### 반례 기반 검증

모델이 맞는지 빠르게 검증하려면 반례를 먼저 구성합니다.

1. `blocked`가 공집합일 때 노출이 과도하게 늘어나는가
2. `in_stock`이 공집합일 때 결과가 반드시 공집합인가
3. `age_ok`가 누락되면 정책 위반 아이템이 포함되는가

반례를 명시하면 "왜 틀렸는지"가 아니라 "어떤 정의가 빠졌는지"를 정확히 찾을 수 있습니다.

### 논리식과 테스트 케이스 대응표

| 논리식 | 테스트 이름 | 기대 결과 |
| --- | --- | --- |
| `x ∈ C ∧ x ∈ I ∧ x ∈ A ∧ x ∉ B` | `eligible_item_is_exposed` | 포함 |
| `x ∈ B` | `blocked_item_not_exposed` | 제외 |
| `x ∉ I` | `out_of_stock_not_exposed` | 제외 |
| `x ∉ A` | `age_restricted_not_exposed` | 제외 |

이 표가 있으면 요구사항-테스트-코드 간 연결이 끊기지 않습니다.

### 요약

이산수학의 기본 도구는 거창한 이론이 아니라, 변경 가능한 시스템을 안정적으로 다루는 작업 언어입니다. 정의를 기호로 고정하고, 반례를 통해 검증하고, 코드와 테스트를 1:1로 맞추는 습관이 핵심입니다.

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

## 처음 질문으로 돌아가기

- **이산수학과 연속 수학은 무엇이 다를까요?**
  - 본문의 기준은 이산수학이란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **이산수학의 다섯 축은 어떻게 연결될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **컴퓨터공학 커리큘럼에서 왜 이산수학이 필수일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **이산수학이란 무엇인가? (현재 글)**
- 명제와 논리 (예정)
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

- [book-examples: discrete-math-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/discrete-math-101/ko)
- [Discrete Mathematics and Its Applications — Kenneth Rosen](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [MIT OCW — Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
- [Wikipedia — Discrete Mathematics](https://en.wikipedia.org/wiki/Discrete_mathematics)
- [Book of Proof — Richard Hammack](https://www.people.vcu.edu/~rhammack/BookOfProof/)

Tags: Computer Science, 이산수학, 수학 입문, 전공 개요, 논리, 집합
