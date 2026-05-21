---
series: discrete-math-101
episode: 2
title: "Discrete Math 101 (2/10): 명제와 논리"
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
  - 명제 논리
  - 추론
  - 진리표
  - 술어 논리
seo_description: 명제, 진리값, 논리 연산자, 진리표, 술어와 양화사로 컴퓨터 추론의 기초를 정리합니다.
last_reviewed: '2026-05-12'
---

# Discrete Math 101 (2/10): 명제와 논리

이 글은 Discrete Math 101 시리즈의 2번째 글입니다.

![Discrete Math 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/02/02-01-big-picture.ko.png)
*Discrete Math 101 2장 흐름 개요*

## 먼저 던지는 질문

- 명제와 비명제는 어떻게 구분할까요?
- 다섯 가지 기본 논리 연산자는 어떻게 동작할까요?
- 진리표로 논리적 동치를 어떻게 확인할까요?

## 왜 중요한가

모든 `if` 문은 명제의 평가입니다. 모든 데이터베이스 질의는 어떤 술어가 만족되는지 묻습니다. 모든 디지털 회로 게이트는 논리 연산입니다. 명제 논리를 이해하지 못하면 복잡한 조건문을 줄이거나, 조건의 의미를 엄밀하게 검증하거나, 엣지 케이스를 자신 있게 다룰 수 없습니다.

> 명제 논리는 정확한 추론을 위한 기호 체계입니다.

이 글에서 세운 논리의 기초는 다음 글의 집합 이론으로 자연스럽게 이어집니다.

## 한눈에 보는 개념

> 명제는 진리값을 가지고, 논리 연산자는 그 진리값을 결합합니다. 연산의 의미는 모두 진리표로 정의됩니다.

```text
  Props P, Q  ──→  Operators  ──→  Compound prop.
                 ┌──────────┐
                 │ ¬ (NOT)  │
                 │ ∧ (AND)  │
                 │ ∨ (OR)   │
                 │ → (impl) │
                 │ ↔ (iff)  │
                 └──────────┘
                       ↓
                  Truth tables
                       ↓
                Logical equivalence
```

## 핵심 용어

| 용어 | 기호 | 의미 |
| --- | --- | --- |
| Negation | ¬P | P가 거짓일 때 참 |
| Conjunction | P ∧ Q | 둘 다 참일 때만 참 |
| Disjunction | P ∨ Q | 하나 이상 참이면 참 |
| Implication | P → Q | P 참, Q 거짓일 때만 거짓 |
| Biconditional | P ↔ Q | 두 진리값이 같을 때 참 |

## 전후 비교

**변경 전:**

```python
# 중첩 조건문, 단순화 없음
if not (x > 0 and y > 0):
    if not (x > 0):
        handle_x()
    if not (y > 0):
        handle_y()
```

**변경 후:**

```python
# ¬(P ∧ Q) ≡ ¬P ∨ ¬Q
if x <= 0 or y <= 0:
    if x <= 0:
        handle_x()
    if y <= 0:
        handle_y()
```

## 단계별로 따라가기

### 1단계: 명제와 진리값

```python
# 명제는 참/거짓이 명확함
# 질문문은 명제가 아님

propositions = {
    "2 is even": True,
    "Paris is the capital of the United States": False,
    "100 is prime": False,
    "1 + 1 = 2": True,
}

for statement, truth in propositions.items():
    print(f"{statement}: {truth}")
```

명제는 참이나 거짓이 분명해야 합니다. 질문, 명령, 감탄처럼 진리값이 정해지지 않는 문장은 명제가 아닙니다. 이 구분이 흐려지면 이후의 모든 논리식도 애매해집니다.

### 2단계: 기본 연산자

```python
def NOT(p: bool) -> bool:
    return not p

def AND(p: bool, q: bool) -> bool:
    return p and q

def OR(p: bool, q: bool) -> bool:
    return p or q

def IMPLIES(p: bool, q: bool) -> bool:
    """P → Q: false only when P true and Q false"""
    return (not p) or q

def IFF(p: bool, q: bool) -> bool:
    """P ↔ Q: true when both have the same value"""
    return p == q

print(IMPLIES(True, False))  # False
print(IMPLIES(False, True))  # True (false premise → always true)
print(IFF(True, True))       # True
```

초보자가 가장 많이 놀라는 부분은 함의입니다. `P → Q`는 P가 거짓이면 참이 됩니다. “비가 오면 우산을 챙긴다”는 약속은 비가 오지 않은 날 위반되지 않는다고 생각하면 직관이 맞춰집니다.

### 3단계: 진리표 생성

```python
from itertools import product

def truth_table(variables: list[str], expr) -> None:
    """Print the truth table for a given expression."""
    header = " | ".join(variables) + " | result"
    print(header)
    print("-" * len(header))
    for values in product([False, True], repeat=len(variables)):
        env = dict(zip(variables, values))
        result = expr(**env)
        row = " | ".join(str(v)[0] for v in values) + f" | {str(result)[0]}"
        print(row)

# (P ∧ Q) → P 진리표
truth_table(["P", "Q"], lambda P, Q: IMPLIES(AND(P, Q), P))
```

진리표는 명제 논리의 실행 표와 같습니다. 입력 조합을 모두 열거하기 때문에 동치 여부를 가장 확실하게 확인할 수 있습니다.

### 4단계: 드모르간 법칙 검증

```python
# ¬(P ∧ Q) ≡ ¬P ∨ ¬Q
# ¬(P ∨ Q) ≡ ¬P ∧ ¬Q

def equivalent(expr1, expr2, variables: list[str]) -> bool:
    """Two expressions are equivalent if they agree on every input."""
    for values in product([False, True], repeat=len(variables)):
        env = dict(zip(variables, values))
        if expr1(**env) != expr2(**env):
            return False
    return True

lhs = lambda P, Q: NOT(AND(P, Q))
rhs = lambda P, Q: OR(NOT(P), NOT(Q))

print(f"De Morgan holds: {equivalent(lhs, rhs, ['P', 'Q'])}")
```

코드 리뷰에서 자주 쓰는 조건문 단순화는 대부분 이런 동치 변형입니다. 논리식이 짧아질수록 버그 표면적도 함께 줄어듭니다.

### 5단계: 술어와 양화사

```python
# 술어는 변수를 입력받아 명제를 반환하는 함수
def is_even(n: int) -> bool:
    return n % 2 == 0

# 전칭 ∀: "모든 n에 대해"
def for_all(domain, predicate) -> bool:
    return all(predicate(x) for x in domain)

# 존재 ∃: "어떤 n이 존재"
def there_exists(domain, predicate) -> bool:
    return any(predicate(x) for x in domain)

numbers = [2, 4, 6, 8, 10]

print(f"∀x ∈ {numbers}: x is even = {for_all(numbers, is_even)}")
print(f"∃x ∈ [1,2,3]: x is even = {there_exists([1, 2, 3], is_even)}")
```

양화사는 술어를 실제 명제로 닫아 주는 도구입니다. SQL의 `ALL`, `ANY`와 직접 이어진다고 보면 훨씬 실용적으로 이해할 수 있습니다.

## 주목할 점

- 모든 논리 연산자는 진리표로 정의됩니다.
- `P → Q`는 `¬P ∨ Q`와 논리적으로 같습니다.
- 드모르간 법칙은 부정이 분배되는 방식을 통제합니다.
- 양화사 ∀, ∃는 술어를 명제로 바꿉니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 함의를 직관적으로만 읽는다 | “거짓 전제면 참”이 계속 낯설다 | 정의를 진리표 기준으로 익힌다 |
| AND/OR 우선순위를 대충 처리한다 | 괄호가 빠져 버그가 생긴다 | 복합식은 항상 괄호를 명시한다 |
| 부정을 잘못 분배한다 | `¬(P ∧ Q)`를 잘못 바꾼다 | 드모르간 법칙을 확실히 익힌다 |
| ∀와 ∃의 순서를 바꾼다 | 전혀 다른 명제가 된다 | 양화사 순서를 그대로 유지한다 |
| 술어를 명제로 착각한다 | 자유변수가 남아 의미가 흐려진다 | 양화사로 닫아 준다 |

## 실무에서는 이렇게 사용합니다

- SQL `WHERE` 최적화는 논리적 동치 변형을 활용합니다.
- 코드 리뷰에서는 복잡한 조건문을 드모르간 법칙으로 정리합니다.
- 디지털 회로 설계는 AND, OR, NOT, NAND, NOR 게이트 위에 서 있습니다.
- 형식 검증은 시스템 속성을 명제로 표현합니다.
- 검색 엔진의 불리언 질의는 그대로 명제 논리입니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 복잡한 `if` 문을 보면 먼저 “이걸 더 단순하게 만들 수 있는가”를 묻습니다. 머릿속에서 진리표를 그리거나 동치 변형을 적용해 조건을 절반 이하로 줄이는 경우가 흔합니다. 또한 “이 조건은 항상 성립하는가, 가끔만 성립하는가”라는 양화사의 감각으로 엣지 케이스를 점검합니다.

## 체크리스트

- [ ] 다섯 가지 기본 연산자의 진리표를 그릴 수 있다
- [ ] 함의의 의미를 직관적으로 설명할 수 있다
- [ ] 드모르간 법칙을 실제 코드에 적용할 수 있다
- [ ] ∀와 ∃를 SQL 예시로 설명할 수 있다
- [ ] 술어와 명제의 차이를 구분할 수 있다

## 연습 문제

1. `(P → Q) ∧ (Q → R) → (P → R)`의 진리표를 만들어 항진명제인지 확인해 보세요.

2. 자신이 작성한 중첩 `if` 문 하나를 골라 드모르간 법칙으로 단순화해 보세요.

3. 정수 전체에서 `∀x ∃y: x + y = 0`과 `∃y ∀x: x + y = 0`의 참·거짓을 각각 판단하고 이유를 설명해 보세요.

## 정리 및 다음 단계

명제 논리는 모든 컴퓨터 추론의 기초입니다. 다섯 가지 논리 연산자, 진리표, 동치 법칙을 이해하면 복잡한 조건도 정밀하게 조작할 수 있습니다. 여기에 양화사가 더해지면 표현력은 술어 논리로 확장됩니다.

다음 글에서는 논리와 함께 이산수학의 또 다른 기초인 집합과 함수를 살펴보겠습니다.

## 실전 확장: 진리표와 양화사를 운영 규칙으로 번역하기

명제 논리는 형식적이지만, 운영 정책을 설계할 때 바로 쓸 수 있습니다. 핵심은 조건문을 자연어로 쓰지 말고, 변수와 술어를 먼저 고정한 뒤 진리표로 검증하는 것입니다.

### 복합 조건 진리표 예시

`P: 사용자 로그인`, `Q: 결제 수단 등록`, `R: 2차 인증 완료`일 때 배포 승인 조건을 `A = P ∧ Q ∧ R`로 둡니다.

| P | Q | R | A |
| --- | --- | --- | --- |
| T | T | T | T |
| T | T | F | F |
| T | F | T | F |
| F | T | T | F |
| T | F | F | F |
| F | T | F | F |
| F | F | T | F |
| F | F | F | F |

조건 하나라도 누락되면 보안 경계가 무너집니다. 따라서 진리표는 "문장이 맞아 보이는지"가 아니라 "모든 입력 조합에서 의도대로 동작하는지"를 확인하는 장치입니다.

### 동치 변환으로 코드 단순화

`not (is_admin and is_verified)`는 드모르간 법칙으로 `not is_admin or not is_verified`와 동치입니다.

```python
def blocked(is_admin: bool, is_verified: bool) -> bool:
    return (not is_admin) or (not is_verified)

cases = [(True, True), (True, False), (False, True), (False, False)]
for a, v in cases:
    left = not (a and v)
    right = blocked(a, v)
    print((a, v), left, right, left == right)
```

동치 변환을 적용하면 분기 구조가 얕아지고 테스트 케이스가 줄어듭니다.

### 양화사 해석 훈련

- `∀x User(x) → HasEmail(x)`: 모든 사용자에게 이메일이 있어야 한다.
- `∃x User(x) ∧ IsDormant(x)`: 휴면 사용자가 한 명 이상 존재한다.

양화사 순서는 중요합니다.

- `∀x ∃y owns(x, y)`는 "모든 사용자가 적어도 하나의 자원을 가진다"입니다.
- `∃y ∀x owns(x, y)`는 "모든 사용자가 같은 하나의 자원을 공유한다"입니다.

두 문장은 완전히 다른 정책입니다.

### 간단한 증명 앵커

명제: `(P → Q) ∧ P`이면 `Q`입니다.

증명: `P → Q`가 참이고 `P`도 참이라고 가정합니다. 함의의 정의에 따라 `P`가 참일 때 `Q`가 거짓이면 `P → Q`는 거짓이 됩니다. 하지만 가정에서 `P → Q`는 참이므로 모순입니다. 따라서 `Q`는 참입니다.

이 논리는 코드 리뷰에서 "사전 조건이 참이면 사후 조건도 참"을 보장하는 근거가 됩니다.

## 심화 워크숍: 논리 규칙을 코드 리뷰 기준으로 전환하기

### 조건 명세 템플릿

복잡한 승인 로직은 먼저 논리식으로 명세합니다.

`ALLOW = (M ∧ V) ∧ (A ∨ E) ∧ ¬B`

- `M`: 멤버십 유효
- `V`: 본인 인증 완료
- `A`: 관리자 권한
- `E`: 예외 승인 토큰
- `B`: 제재 상태

이 식을 기준으로 리뷰하면 "조건이 많다"가 아니라 "어떤 항이 빠졌는가"를 논의할 수 있습니다.

### 진리표 축소 기법

전체 조합이 큰 경우에도 위험 조합을 먼저 점검합니다.

| M | V | A | E | B | ALLOW |
| --- | --- | --- | --- | --- | --- |
| T | T | F | F | F | F |
| T | T | T | F | F | T |
| T | T | F | T | F | T |
| T | T | T | T | T | F |

`B`가 참이면 항상 거부되어야 한다는 성질이 즉시 보입니다.

### 논리 동치로 코드 정리

```python
def allow(m: bool, v: bool, a: bool, e: bool, banned: bool) -> bool:
    return (m and v) and (a or e) and (not banned)

# 부정 형태가 필요할 때
# 허용하지 않음 == (not m) or (not v) or ((not a) and (not e)) or banned
```

동치 변환을 이용하면 "거부 사유"를 분해해 로그 메시지와 알림 규칙을 만들 수 있습니다.

### 양화사와 데이터 품질 규칙

- `∀u User(u) → HasPhone(u)`는 필수 필드 규칙입니다.
- `∃u Fraud(u)`는 이상 사용자 탐지 신호입니다.

실무에서는 전칭 조건을 배치 검증 쿼리로, 존재 조건을 알람 쿼리로 구현합니다.

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

## 보강 메모: 손으로 계산해 보는 검증 절차

아래 절차를 한 번 손으로 수행하면 개념이 빠르게 고정됩니다.

- 진리표 문제: 입력 조합을 빠짐없이 나열하고, 각 행의 결론을 식에 따라 계산합니다.
- 집합 문제: 원소를 실제로 써서 합집합/교집합/차집합을 구한 뒤 식과 일치하는지 확인합니다.
- 그래프 문제: 정점 방문 순서를 한 줄 로그로 기록해 BFS/DFS 차이를 비교합니다.
- 점화식 문제: `n=1..6`까지 값을 적어 패턴을 추측한 뒤 귀납법으로 검증합니다.

이 과정을 문서 마지막에 남기면 다음 글을 읽을 때도 같은 기준으로 사고를 이어갈 수 있습니다.

## 처음 질문으로 돌아가기

- **명제와 비명제는 어떻게 구분할까요?**
  - 본문의 기준은 명제와 논리를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **다섯 가지 기본 논리 연산자는 어떻게 동작할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **진리표로 논리적 동치를 어떻게 확인할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Discrete Math 101 (1/10): 이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
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

- [book-examples: discrete-math-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/discrete-math-101/ko)
- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 1](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Stanford Encyclopedia of Philosophy — Propositional Logic](https://plato.stanford.edu/entries/logic-propositional/)
- [Wikipedia — De Morgan's Laws](https://en.wikipedia.org/wiki/De_Morgan%27s_laws)
- [MIT OCW — Mathematics for Computer Science, Lecture 1-3](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)

Tags: Computer Science, 이산수학, 명제 논리, 추론, 진리표, 술어 논리
