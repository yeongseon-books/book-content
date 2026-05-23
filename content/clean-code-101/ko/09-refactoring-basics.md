---
series: clean-code-101
episode: 9
title: "Clean Code 101 (9/10): 리팩토링 기초"
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
  - Refactoring
  - Patterns
  - LegacyCode
  - Quality
seo_description: 안전한 리팩토링을 위한 특성화 테스트 활용법과 마틴 파울러의 핵심 기법을 통해 레거시 코드를 점진적으로 개선하는 절차를 설명합니다.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (9/10): 리팩토링 기초

리팩토링은 코드를 다시 쓰는 작업처럼 보이기 쉽지만, 실제로는 훨씬 더 작은 단위의 개선을 반복하는 일입니다.

여기서는 리팩토링이 무엇이고 무엇이 아닌지, 그리고 레거시 코드에서도 안전하게 적용하는 절차를 정리하겠습니다.

![Clean Code 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/09/09-01-concept-at-a-glance.ko.png)
*Clean Code 101 9장 흐름 개요*
> 금달 컔단 동스른 동스른 동스른 동스른 동스른 동스른 동스른—.

## 먼저 던지는 질문

- 리팩토링은 정확히 무엇이고, 재작성과 무엇이 다를까요?
- Fowler 카탈로그의 핵심 기법은 무엇일까요?
- 특성화 테스트는 왜 레거시 코드에서 중요할까요?

## 왜 중요한가

리팩토링의 핵심은 외부 동작을 바꾸지 않고 내부 구조를 개선하는 데 있습니다. 그래서 기능 추가와 섞어 버리면 리뷰도 어려워지고, 어디서 버그가 생겼는지도 구분하기 힘들어집니다.

특히 레거시 코드에서는 "이해한 뒤 고친다"보다 "현재 동작을 먼저 고정한 뒤 조금씩 바꾼다"가 더 현실적인 접근입니다. 리팩토링은 한 번의 큰 점프보다, 초록 테스트와 초록 테스트 사이의 작은 이동을 반복하는 기술입니다.

## 한눈에 보는 개념

작은 초록 상태에서 다음 초록 상태로 옮겨 가는 것이 리팩토링의 기본 리듬입니다.

## 핵심 용어

- **Refactoring**: 외부 동작을 바꾸지 않는 내부 구조 개선입니다.
- **Characterization test**: 현재 동작을 우선 고정하는 테스트입니다.
- **Code smell**: 긴 함수, 큰 클래스, 데이터 덩어리처럼 개선 필요를 알리는 신호입니다.
- **Two hats**: 기능 추가와 구조 개선을 같은 변경에 섞지 않는 원칙입니다.
- **Mikado method**: 큰 변경을 작은 의존 그래프로 쪼개는 접근입니다.

## 전/후 비교

**Before**

```python
def order_total(o):
    s = 0
    for it in o.items:
        s += it.price * it.qty
    if o.coupon: s -= 10
    if o.member: s = s * 0.9
    return s
```

**After**

```python
def subtotal(items): return sum(i.price * i.qty for i in items)
def with_coupon(s, coupon): return s - 10 if coupon else s
def with_member(s, member): return s * 0.9 if member else s

def order_total(o):
    s = subtotal(o.items)
    s = with_coupon(s, o.coupon)
    s = with_member(s, o.member)
    return s
```

좋은 리팩토링은 한 번에 모든 것을 바꾸지 않습니다. 의미 단위를 하나씩 분리하면서 이름과 구조를 함께 드러냅니다.

## 실전 적용: 안전한 리팩토링 다섯 단계

### 단계 1 — 특성 테스트를 안전망으로 활용
```python
# 1_characterize.py
def test_legacy_total():
    o = make_order(items=[(100, 2)], coupon=True, member=True)
    assert order_total(o) == 171  # capture current behavior as is
```

레거시 코드에서는 완전히 이해한 뒤 시작하려고 하면 너무 늦어집니다. 먼저 현재 동작을 고정하고, 그다음에 구조를 만지는 편이 훨씬 안전합니다.

### 단계 2 — 함수 추출
```python
# 2_extract.py
def subtotal(items): return sum(i.price * i.qty for i in items)
```

가장 먼저 추출할 것은 계산이나 규칙처럼 의미 단위가 분명한 부분입니다. 작은 단위로 잘라야 다음 단계도 명확해집니다.

### 단계 3 — Rename

```python
# 3_rename.py
# 이름의 의도가 드러날 수 있도록 점진적으로 이름을 바꾸십시오.
def items_subtotal(items): ...
```

이름 변경은 리팩토링의 절반입니다. 구조를 바꿨는데 이름이 그대로면, 읽는 사람은 여전히 예전 정신 모델에 갇히게 됩니다.

### 단계 4 — 인라인 후 이동
```python
# 4_move.py
# 위치가 잘못된 함수를 올바른 모듈/클래스로 이동합니다.
class OrderPricing:
    def total(self, order): ...
```

응집도는 올리고, 잘못 놓인 코드는 제자리로 옮겨야 합니다. 때로는 추출보다 이동이 더 큰 가독성 개선을 만듭니다.

### 단계 5 — 두 역할 분리하기
```python
# 5_two_hats.py
# 하나의 PR에 기능 변경과 리팩토링을 혼합하지 마십시오.
# PR-1: 리팩터링(동작 유지)
# PR-2: 기능 추가(새 동작)
```

리팩토링 PR과 기능 PR을 분리해야 리뷰도 쉬워지고, 문제 발생 시 원인도 빨리 좁힐 수 있습니다.

## 검증 방법

```bash
python -m pytest -q tests/test_order_total.py
python -m pytest -q tests/test_legacy_characterization.py
```

**기대 결과**

- 현재 동작을 고정한 테스트가 먼저 초록이어야 합니다.
- 추출, 이름 변경, 이동 뒤에도 테스트 결과가 같아야 합니다.

## 실패하기 쉬운 지점

- 기능 변경이 리팩토링 커밋 안에 함께 섞입니다.
- 이름만 바꾸고 잘못 놓인 책임은 그대로 남아 있습니다.

## 이 코드에서 먼저 봐야 할 점

- 매 단계 뒤에 테스트가 계속 초록 상태를 유지합니다.
- 각 변경은 작고 되돌리기 쉽습니다.
- 이름이 의도를 더 잘 드러내는 방향으로 바뀝니다.

## 자주 하는 실수 5가지

1. **테스트 없이 시작하기.** 회귀가 우연이 됩니다.
2. **한 번에 너무 크게 바꾸기.** 되돌릴 방법이 사라집니다.
3. **기능과 섞어서 바꾸기.** 리뷰가 거의 불가능해집니다.
4. **구조는 바꿨는데 이름은 그대로 두기.** 가치의 절반을 잃습니다.
5. **미관만 위한 리팩토링 하기.** 다음 변경이 쉬워지지 않으면 목적을 놓친 것입니다.

## 실무에서는 이렇게 보입니다

좋은 팀은 기능 PR 전에 먼저 리팩토링 PR을 병합하기도 합니다. 그러면 기능 PR의 크기가 줄고, 리뷰어는 구조 변경과 기능 변경을 분리해서 판단할 수 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 다음 변경이 쉬워질 때만 리팩토링합니다.
- 빠른 테스트를 두고 작은 단계로 갑니다.
- 두 개의 모자, 즉 기능과 구조를 분리합니다.
- 레거시 코드는 특성화 테스트로 시작합니다.
- 큰 변경은 Mikado 그래프로 잘게 풉니다.

## 체크리스트

- [ ] 시작 전 테스트가 초록인가?
- [ ] 단계가 충분히 작은가?
- [ ] 기능 변경이 섞여 있지 않은가?
- [ ] 이름이 이제 의도를 드러내는가?
- [ ] 다음 변경이 실제로 더 쉬워졌는가?

## 연습 문제

1. 50줄이 넘는 함수 하나를 특성화 테스트로 고정하고 세 단계로 분해해 보세요.
2. 잘못 놓인 함수 하나를 더 적절한 모듈로 옮겨 보세요.
3. 구조만 바꾸는 리팩토링 전용 PR 하나를 열고 병합해 보세요.

## 정리 및 다음 단계

리팩토링은 다음 변경의 비용을 낮추는 투자입니다. 마지막 글에서는 이 시리즈 전체를 한 번에 점검하는 좋은 코드 리뷰 기준으로 마무리합니다.

## 리팩토링 카탈로그를 실무에 매핑하기

리팩토링은 이름을 아는 것보다 순서가 중요합니다. 아래 표는 자주 쓰는 기법과 적용 목적을 정리한 카탈로그입니다.

| 기법 | 목적 | 시작 신호 | 기대 효과 |
| --- | --- | --- | --- |
| Extract Method | 긴 함수 분해 | 주석 블록이 많음 | 가독성/테스트 향상 |
| Move Field | 잘못된 책임 이동 | 데이터를 다른 객체가 더 많이 사용 | 응집도 향상 |
| Introduce Parameter Object | 인자 다발 정리 | 인자 4개 이상 반복 | 호출 소음 감소 |
| Replace Temp with Query | 임시 변수 정리 | 중간 값 의미가 불명확 | 의도 명확화 |
| Inline Function | 과도 추상화 축소 | 호출자가 1~2개뿐, 인자 과다 | 단순성 회복 |

카탈로그를 팀 공통 언어로 쓰면 리뷰 대화가 빨라집니다. "여기 Move Field가 필요하다"처럼 짧고 정확하게 의도를 전달할 수 있습니다.

## 메서드 추출 / 필드 이동 Python 예시

```python
# before
class OrderService:
    def __init__(self, order):
        self.order = order
        self.tax_rate = 0.1

    def total(self):
        subtotal = 0
        for line_item in self.order.line_items:
            subtotal += line_item.price * line_item.quantity
        return int(subtotal * (1 + self.tax_rate))
```

```python
# after
class Order:
    def __init__(self, line_items, tax_rate: float):
        self.line_items = line_items
        self.tax_rate = tax_rate

    def subtotal(self) -> int:
        return sum(line_item.price * line_item.quantity for line_item in self.line_items)

    def total_with_tax(self) -> int:
        return int(self.subtotal() * (1 + self.tax_rate))

class OrderService:
    def __init__(self, order: Order):
        self.order = order

    def total(self) -> int:
        return self.order.total_with_tax()
```

위 변경에는 두 가지 핵심이 있습니다. `subtotal` 추출로 계산 의도가 드러났고, `tax_rate` 책임이 `Order`로 이동해 응집도가 높아졌습니다.

## 점진적 리팩토링 절차

1. 특성화 테스트로 현재 동작 고정
2. 작은 리팩토링 1개 적용
3. 테스트 실행
4. 커밋
5. 다음 리팩토링 진행

```python
from dataclasses import dataclass

@dataclass
class RefactorStep:
    name: str
    done: bool = False

def next_refactor_step(steps: list[RefactorStep]) -> str | None:
    for step in steps:
        if not step.done:
            return step.name
    return None
```

이런 방식으로 리팩토링 계획을 명시하면, 큰 변경도 안전하게 작게 나눌 수 있습니다. 결국 리팩토링의 품질은 기법 지식보다 단계 관리에서 결정됩니다.

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

## 리팩토링 카탈로그: 작은 변경을 안전하게 누적하기

리팩토링은 대규모 재작성보다 작은 단위의 안전한 누적이 효과적입니다. 아래 카탈로그는 우선순위를 잡는 기본 틀입니다.

| 기법 | 적용 신호 | 선행 조건 |
| --- | --- | --- |
| 이름 변경 | 의미 불명확, 오해성 호출 | 참조 검색, 테스트 통과 |
| 함수 추출 | 한 함수의 책임 다중화 | 동작 고정 테스트 |
| 함수 이동 | 모듈 경계 위반 | 의존 방향 확인 |
| 인라인 | 과도한 추상화 | 호출부 단순화 검토 |
| 파라미터 객체 | 인자 목록 과다 | 데이터 응집도 확인 |

## 전/후 데모: 단계적 리팩토링

```python
# before
def make_report(users):
    result = []
    for u in users:
        if u["active"] and u["last_login_days"] < 30:
            result.append({"id": u["id"], "segment": "engaged"})
    return result

# after
def make_report(users):
    return [to_engaged_entry(user) for user in users if is_recent_active_user(user)]

def is_recent_active_user(user: dict) -> bool:
    return user["active"] and user["last_login_days"] < 30

def to_engaged_entry(user: dict) -> dict:
    return {"id": user["id"], "segment": "engaged"}
```

## SOLID 샘플: 개방-폐쇄와 의존 역전 적용

```python
from typing import Protocol

class SegmentPolicy(Protocol):
    def matches(self, user: dict) -> bool: ...

def filter_users(users: list[dict], policy: SegmentPolicy) -> list[dict]:
    return [user for user in users if policy.matches(user)]
```

정책 객체를 주입하면 규칙 추가 시 기존 함수 수정량이 줄어듭니다. 이 구조는 리팩토링과 기능 확장을 동시에 안전하게 지원합니다.

## 린터/품질 게이트 예시

```toml
[tool.ruff.lint]
select = ["E", "F", "B", "C90", "N", "I"]
```

```bash
pytest -q
ruff check app/ tests/
```

리팩토링 PR은 기능 PR과 분리하고, 검증 로그를 PR 본문에 남겨야 추적 가능성이 올라갑니다. 이 규칙이 장기 유지보수 비용을 결정합니다.

## 심화 실습: 레거시 모듈 점진 개선 계획

레거시 모듈은 "한 번에 교체"보다 "행동 고정 후 점진 개선"이 안전합니다. 먼저 Characterization Test로 현재 동작을 고정하고, 작은 리팩토링을 반복합니다.

| 단계 | 목표 | 완료 기준 |
| --- | --- | --- |
| 1 | 현재 동작 고정 | 핵심 시나리오 테스트 통과 |
| 2 | 이름 정리 | 주요 함수/변수 오해성 제거 |
| 3 | 구조 분리 | 계산/검증/저장 경계 분리 |
| 4 | 확장점 도입 | 정책 추가 시 수정 범위 축소 |

```python
def migrate_refactor_step(step_name: str, is_verified: bool) -> str:
    if not is_verified:
        return f"{step_name}:blocked"
    return f"{step_name}:done"
```

리팩토링은 속도보다 신뢰가 먼저입니다. 각 단계마다 검증 로그를 남기면 다음 변경의 출발 비용이 줄어듭니다.

### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.

### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.

### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.

### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.

### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.

### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.

### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.

## 처음 질문으로 돌아가기

- **리팩토링은 정확히 무엇이고, 재작성과 무엇이 다를까요?**
  - 본문의 기준은 리팩토링 기초를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Fowler 카탈로그의 핵심 기법은 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **특성화 테스트는 왜 레거시 코드에서 중요할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Clean Code 101 (1/10): Clean Code란 무엇인가?](./01-what-is-clean-code.md)
- [Clean Code 101 (2/10): 이름 짓기](./02-naming.md)
- [Clean Code 101 (3/10): 함수 작게 만들기](./03-small-functions.md)
- [Clean Code 101 (4/10): 조건문 줄이기](./04-simplifying-conditionals.md)
- [Clean Code 101 (5/10): 중복 제거](./05-removing-duplication.md)
- [Clean Code 101 (6/10): 오류 처리](./06-error-handling.md)
- [Clean Code 101 (7/10): 주석과 문서화](./07-comments-and-docs.md)
- [Clean Code 101 (8/10): 테스트 가능한 코드](./08-testable-code.md)
- **리팩토링 기초 (현재 글)**
- 좋은 코드 리뷰 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Refactoring (Martin Fowler)](https://martinfowler.com/books/refactoring.html)
- [Refactoring Catalog](https://refactoring.com/catalog/)
- [Working Effectively with Legacy Code (M. Feathers)](https://www.oreilly.com/library/view/working-effectively-with/0131177052/)
- [The Mikado Method](https://mikadomethod.info/)
- [Refactoring catalog](https://refactoring.com/catalog/)
- [Working Effectively with Legacy Code](https://www.oreilly.com/library/view/working-effectively-with/0131177052/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/clean-code-101/ko)
Tags: Computer Science, CleanCode, Refactoring, Patterns, LegacyCode, Quality
