---
series: clean-code-101
episode: 5
title: "Clean Code 101 (5/10): 중복 제거"
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
  - CleanCode
  - DRY
  - Duplication
  - Refactoring
  - Abstraction
seo_description: DRY 원칙의 의미와 중복 제거 기준을 배웁니다. 우연한 유사성과 본질적 중복을 구분하고 지식의 출처를 하나로 관리하는 법을 배웁니다.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (5/10): 중복 제거

중복은 보이면 바로 없애야 할 것처럼 느껴지지만, 실제로는 그렇게 단순하지 않습니다.

이 글은 Clean Code 101 시리즈의 5번째 글입니다.

여기서는 DRY가 정말 뜻하는 것이 무엇인지, 그리고 어떤 중복은 남겨 두고 어떤 중복만 제거해야 하는지 분명하게 정리하겠습니다.

## 먼저 던지는 질문

- DRY의 진짜 의미는 무엇일까요?
- 우연히 닮은 중복과 본질적인 중복은 어떻게 구분할까요?
- 추출과 매개변수화는 어떤 순서로 적용해야 할까요?

## 큰 그림

![Clean Code 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/05/05-01-concept-at-a-glance.ko.png)

*Clean Code 101 5장 흐름 개요*

이 그림은 중복 제거의 동스턴 동스턴 동스턴 동스턴 동스턴 동스턴
중복 제거의 동스턴 동스턴 동스턴 동스턴 동스턴 동스턴 동스턴 동스턴 동스턴 동스턴 동스턴 동스턴 동스턴 동스턴 동스턴 동스턴
중복 단순히 같은 이윤으로 바뀌는 나머지는 버망 처럼 처기 이위로 스도록 한다. 한 곳을 고친고 다른 곳을 놓친는 순간, 시스템에는 서로 다른 진실이 생깁니다.

> 같은 이유로 바뀌는 중복만 추출해야 하나의 진실한 출처가 생깁니다.

## 왜 중요한가

중복은 버그를 복제합니다. 한 곳을 고치고 다른 곳을 놓치는 순간, 시스템에는 서로 다른 진실이 생깁니다. 그래서 DRY는 코드 줄 수를 줄이라는 조언이 아니라, 지식의 출처를 하나로 유지하라는 원칙에 가깝습니다.

다만 겉모양이 비슷하다고 해서 모두 합치면 안 됩니다. 변경 이유가 다른 코드를 억지로 묶으면, 중복 제거 대신 잘못된 결합만 커집니다. 핵심은 “왜 함께 바뀌는가”를 먼저 보는 일입니다.

## 한눈에 보는 개념

같은 이유로 바뀌는 중복만 추출해야, 하나의 진실한 출처가 생깁니다.

## 핵심 용어

- **DRY**: 지식의 출처를 하나로 유지하라는 원칙입니다.
- **Coincidental duplication**: 우연히 비슷하게 보일 뿐, 바뀌는 이유는 다른 중복입니다.
- **Extract Function/Class**: 공통 부분을 함수나 클래스로 올리는 방식입니다.
- **Parameterize**: 달라지는 부분을 인자로 표현하는 방식입니다.
- **Premature abstraction**: 너무 일찍 추상화해서 생기는 불필요한 결합입니다.

## Before/After

**Before**

```python
def email_admin(msg):
    print(f"[admin] {msg}")
def email_user(msg):
    print(f"[user] {msg}")
def email_guest(msg):
    print(f"[guest] {msg}")
```

**After**

```python
def email(role, msg):
    print(f"[{role}] {msg}")
```

차이는 역할 이름뿐이고, 변경 이유도 같습니다. 이런 경우에는 공통 부분을 하나로 올리는 편이 맞습니다.

## 실전 적용: 안전하게 중복 없애기

### Step 1 — Wait for the third occurrence

```python
# 1_rule_of_three.py
# Extract only after the same pattern shows up three times.
def calc_a(x): return x * 1.1
def calc_b(x): return x * 1.2
# When the third arrives, decide whether to unify.
```

첫 번째, 두 번째 중복에서는 아직 섣불리 추상화하지 않는 편이 좋습니다. 세 번째가 나타날 때쯤이면 정말 같은 문제인지 더 분명하게 보입니다.

### Step 2 — Extract function

```python
# 2_extract.py
def with_tax(price, rate): return int(price * (1 + rate))
def krw(price): return with_tax(price, 0.1)
def jpy(price): return with_tax(price, 0.08)
```

달라지는 부분이 분명할 때만 인자로 뽑아야 합니다. 공통과 차이를 구분하지 못한 추상화는 오래 버티지 못합니다.

### Step 3 — Parameterize

```python
# 3_param.py
def greet(name, lang="en"):
    msgs = {"en": "Hello", "ko": "안녕하세요"}
    return f"{msgs[lang]}, {name}"
```

분기 대신 조회로 바꿀 수 있다면 구조는 더 단순해집니다. 매개변수화는 중복 제거와 조건문 제거를 동시에 돕기도 합니다.

### Step 4 — Remove data duplication

```python
# 4_data.py
PLANS = {
    "free": {"price": 0,  "limit": 100},
    "pro":  {"price": 10, "limit": 1000},
    "team": {"price": 30, "limit": 10000},
}
def quota(plan): return PLANS[plan]["limit"]
```

데이터 중복은 코드 중복보다 더 위험할 때가 많습니다. 정책을 여러 함수에 흩뿌리지 말고 하나의 데이터 구조로 모으는 편이 안전합니다.

### Step 5 — Undo a wrong extraction

```python
# 5_unfold.py
# A function shared by only two callers but with six arguments
# is usually better inlined back into two simple functions
# (Inline Function).
```

한 번 추출했다고 끝이 아닙니다. 추상화가 이득보다 부담을 더 만든다면 다시 되돌리는 것도 좋은 리팩토링입니다.

## 검증 방법

```bash
python -m pytest -q tests/test_pricing_rules.py
ruff check app/
```

**기대 결과**

- 추출 전후 호출 결과가 그대로 유지됩니다.
- 데이터 구조로 옮긴 정책이 새 케이스 추가에 더 단순해야 합니다.

## 실패하기 쉬운 지점

- 공통 함수가 인자 여섯 개짜리 미니 프레임워크가 됩니다.
- 우연한 유사성을 억지로 합쳐 서로 다른 변경 이유가 묶입니다.

## 이 코드에서 먼저 봐야 할 점

- 달라지는 부분만 인자로 올려야 합니다.
- 데이터 구조가 분기와 중복을 흡수할 수 있습니다.
- 추상화는 필요가 분명할 때만 생겨야 합니다.

## 자주 하는 실수 5가지

1. **첫 번째 중복에서 바로 추출하기.** 우연한 유사성일 가능성이 큽니다.
2. **비슷해 보인다는 이유로 합치기.** 의미가 다른 코드가 억지로 묶입니다.
3. **인자가 다섯 개를 넘는 추출 만들기.** 실패한 추상화 신호일 수 있습니다.
4. **테스트 없이 합치기.** 회귀 위험이 커집니다.
5. **데이터 중복을 무시하기.** 코드 중복보다 더 오래 숨어 있을 수 있습니다.

## 실무에서는 이렇게 보입니다

API 정책, 폼 검증 규칙, 요금제 정보처럼 사실상 데이터인 영역은 구조체나 테이블로 올릴수록 변경이 쉬워집니다. 새 정책을 추가할 때 기존 if 체인을 계속 건드리지 않아도 되기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 겉모양보다 변경 이유를 먼저 봅니다.
- 세 번째 반복이 나타날 때까지 기다립니다.
- 추상화의 비용, 즉 결합을 항상 함께 계산합니다.
- 데이터 중복을 먼저 제거합니다.
- 잘못된 추출은 자존심 없이 되돌립니다.

## 체크리스트

- [ ] 이 중복은 같은 이유로 바뀌는가?
- [ ] 달라지는 부분이 분명한가?
- [ ] 인자 수가 과하지 않은가?
- [ ] 데이터 구조로 표현할 수 있는가?
- [ ] 합친 뒤 호출 지점이 더 단순해졌는가?

## 연습 문제

1. 우연한 중복 하나를 찾아 왜 그대로 두는지 적어 보세요.
2. 본질적인 중복 하나를 함수로 추출해 보세요.
3. if/elif 정책 체인 하나를 데이터 구조로 옮겨 보세요.

## 정리 및 다음 단계

DRY는 코드 줄 수가 아니라 변화의 출처를 하나로 유지하는 원칙입니다. 다음 글에서는 또 다른 부패 지점인 오류 처리를 정리합니다.


## 중복 제거 기법을 단계별로 적용하기

중복 제거는 "한 번에 크게 추상화"가 아니라, 변경 이유를 확인하면서 작은 단계로 진행해야 안전합니다. 아래 표는 대표 기법과 적용 타이밍입니다.

| 기법 | 언제 적용할까 | 기대 효과 | 실패 신호 |
| --- | --- | --- | --- |
| Extract Function | 로직이 동일하고 맥락도 유사할 때 | 재사용, 테스트 단순화 | 인자 폭증 |
| Parameterize | 차이가 소수 값으로 표현될 때 | 분기 감소 | 의미 없는 플래그 증가 |
| Template Method | 알고리즘 골격은 같고 일부 단계만 다를 때 | 공통 흐름 고정 | 상속 계층 비대화 |
| Strategy | 정책 교체가 자주 필요할 때 | 확장 용이 | 객체 수 과도 증가 |
| Data Table화 | 규칙이 사실상 데이터일 때 | 변경 리스크 감소 | 키 정합성 관리 실패 |

중복 제거의 핵심 질문은 항상 같습니다. "이 둘은 정말 같은 이유로 바뀌는가?"

## DRY 원칙 Python 코드 예시

```python
from dataclasses import dataclass

@dataclass
class PricingRule:
    name: str
    multiplier: float


PRICING_RULES = {
    "kr": PricingRule(name="kr", multiplier=1.10),
    "jp": PricingRule(name="jp", multiplier=1.08),
    "us": PricingRule(name="us", multiplier=1.07),
}


def apply_tax(base_price: int, country_code: str) -> int:
    rule = PRICING_RULES[country_code]
    return int(base_price * rule.multiplier)
```

세 나라 규칙을 함수 세 개로 복제하던 구조를 테이블 하나로 모으면, 정책 수정 위치가 단일화됩니다. 이때 검증도 쉬워집니다. 나라별 테스트는 입력 데이터만 바꿔 같은 함수를 검증하면 되기 때문입니다.

## 우연한 유사성과 본질 중복을 가르는 기준

1. 변경 이슈가 항상 같이 열리는가
2. 도메인 용어가 동일한가
3. 실패 시 영향 범위가 같은가
4. 배포 타이밍이 같이 움직이는가

```python
def is_essential_duplication(
    same_change_issue: bool,
    same_domain_term: bool,
    same_failure_impact: bool,
    same_release_timing: bool,
) -> bool:
    score = sum([same_change_issue, same_domain_term, same_failure_impact, same_release_timing])
    return score >= 3
```

위처럼 단순한 평가 함수를 팀 합의로 정해 두면, 중복 제거 여부를 빠르게 결정할 수 있습니다.

## 잘못된 추상화를 되돌리는 기준

추상화는 한 번 만들면 계속 유지해야 한다고 오해하기 쉽지만, 실제로는 되돌림도 중요한 리팩토링입니다. 아래 상황이면 Inline을 검토할 가치가 큽니다.

- 공통 함수 인자가 5개 이상으로 증가함
- 호출자 대부분이 더미 값을 넘김
- 공통 로직보다 분기 처리 코드가 더 많아짐
- 새 요구사항이 들어올 때마다 예외 플래그가 늘어남

잘못된 추상화를 되돌리면 코드가 잠시 중복돼 보일 수 있지만, 변경 이유가 분리되면서 장기 비용은 오히려 내려갑니다.


## 실무 적용 메모

아래 메모는 팀 내 합의 문서에 그대로 옮겨 적어도 되는 수준의 운영 규칙입니다.

1. 리뷰는 코드 스타일보다 변경 위험을 먼저 다룹니다.
2. 규칙 위반은 사람 지적보다 자동화 전환을 우선합니다.
3. 반복되는 설계 결함은 교육 과제가 아니라 구조 개선 과제로 등록합니다.
4. 모든 개선은 테스트와 함께 진행하며, 동작 변경 여부를 PR 설명에 명시합니다.
5. 다음 분기 목표에는 "새 기능 수"와 함께 "변경 비용 감소 지표"를 반드시 포함합니다.

```python
from dataclasses import dataclass

@dataclass
class QualityGate:
    has_tests: bool
    has_clear_names: bool
    has_boundary_error_handling: bool
    has_small_functions: bool
    has_review_notes: bool


def evaluate_gate(gate: QualityGate) -> tuple[bool, list[str]]:
    missing = []
    if not gate.has_tests:
        missing.append("tests")
    if not gate.has_clear_names:
        missing.append("naming")
    if not gate.has_boundary_error_handling:
        missing.append("error-boundary")
    if not gate.has_small_functions:
        missing.append("function-size")
    if not gate.has_review_notes:
        missing.append("review-notes")
    return len(missing) == 0, missing
```

이 체크 함수는 단순하지만, 품질 기준을 코드로 표현하는 출발점이 됩니다. 팀이 기준을 말로만 합의하면 시간이 지나며 흐려집니다. 반대로 코드와 템플릿과 자동화 규칙으로 남기면 신규 멤버가 들어와도 동일한 기준이 유지됩니다.

또한 개선 활동은 단발성 이벤트가 아니라 루프여야 합니다. 한 번의 대청소보다 매 PR마다 작은 개선을 추가하는 편이 장기적으로 더 강합니다. 이름 하나, 함수 하나, 분기 하나를 매번 더 낫게 만드는 습관이 쌓이면 코드베이스의 평균 품질이 올라가고, 장애 대응 속도도 실제로 빨라집니다.

## 처음 질문으로 돌아가기

- **DRY의 진짜 의미는 무엇일까요?**
  - 본문의 기준은 중복 제거를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **우연히 닮은 중복과 본질적인 중복은 어떻게 구분할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **추출과 매개변수화는 어떤 순서로 적용해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Clean Code 101 (1/10): Clean Code란 무엇인가?](./01-what-is-clean-code.md)
- [Clean Code 101 (2/10): 이름 짓기](./02-naming.md)
- [Clean Code 101 (3/10): 함수 작게 만들기](./03-small-functions.md)
- [Clean Code 101 (4/10): 조건문 줄이기](./04-simplifying-conditionals.md)
- **중복 제거 (현재 글)**
- 오류 처리 (예정)
- 주석과 문서화 (예정)
- 테스트 가능한 코드 (예정)
- 리팩토링 기초 (예정)
- 좋은 코드 리뷰 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [The Pragmatic Programmer — DRY](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/)
- [Sandi Metz — The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction)
- [Refactoring — Extract Function](https://refactoring.com/catalog/extractFunction.html)
- [Refactoring — Inline Function](https://refactoring.com/catalog/inlineFunction.html)
- [The wrong abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction)
Tags: Computer Science, CleanCode, DRY, Duplication, Refactoring, Abstraction
